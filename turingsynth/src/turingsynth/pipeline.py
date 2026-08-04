"""Single-build-directory compiler pipeline."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import shutil

from turingsynth.audit import audit_physical, verify_formal_equivalence
from turingsynth.config import load_project
from turingsynth.formats.emitter import emit_v15
from turingsynth.frontend import synthesize
from turingsynth.layout import place
from turingsynth.mapping.packer import map_to_native
from turingsynth.render import render_svg
from turingsynth.routing import FanoutTrackCapacityError, route
from turingsynth.targets import build_target_context


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def _reset_build(root: Path) -> Path:
    build = (root / "build").resolve()
    if build.parent != root.resolve() or build.name != "build":
        raise RuntimeError("refusing to clean anything except compiler-root/build")
    if build.exists():
        shutil.rmtree(build)
    build.mkdir(parents=True)
    return build


def build_project(compiler_root: Path, manifest: Path) -> dict[str, object]:
    compiler_root = Path(compiler_root).resolve()
    config = load_project(manifest)
    build = _reset_build(compiler_root)
    try:
        _write_json(
            build / "project.json",
            {
                "schema": "turingsynth-build-project-v1",
                "manifest": str(config.manifest),
                "name": config.name,
                "top": config.top,
                "target": config.target_kind,
                "sources": [str(path) for path in config.sources],
                "build_directory_policy": "single disposable compiler-root/build",
            },
        )
        logical, yosys_report = synthesize(config, build / "01-yosys")
        target = build_target_context(config, logical)
        physical = map_to_native(config, logical, target)
        _write_json(build / "02-mapping" / "physical.json", physical.to_dict())
        mapping_report = {
            "schema": "turingsynth-native-mapping-v1",
            "gate": physical.gate,
            "delay": physical.delay,
            "energy": physical.gate * physical.delay,
            "component_count": len(physical.components),
            "logical_net_count": len(physical.nets),
            "zero_cost_pack_components": sum(
                component.role in {"maker", "splitter"}
                for component in physical.components
            ),
            "no_padding_lanes": True,
            "cost_or_delay_added_by_packaging": False,
        }
        _write_json(build / "02-mapping" / "report.json", mapping_report)
        net_by_name = {net.name: net for net in physical.nets}
        channel_expansion: dict[int, int] = {}
        for _layout_attempt in range(32):
            placed, layout_report = place(
                physical,
                config,
                channel_expansion=channel_expansion,
            )
            _write_json(build / "03-layout" / "placed.json", placed.to_dict())
            _write_json(build / "03-layout" / "report.json", layout_report)
            try:
                routed = route(placed)
                break
            except FanoutTrackCapacityError as exc:
                net = net_by_name.get(exc.network)
                if net is None:
                    raise
                source_rank = int(layout_report["ranks"][net.source.component])
                channel_expansion[source_rank] = (
                    channel_expansion.get(source_rank, 0) + 1
                )
        else:
            raise RuntimeError(
                "layout could not provide enough legal fanout-track capacity "
                "after 32 targeted channel expansions"
            )
        _write_json(build / "03-layout" / "placed.json", placed.to_dict())
        _write_json(build / "03-layout" / "report.json", layout_report)
        _write_json(build / "04-routing" / "report.json", routed.report)
        circuit, payload = emit_v15(
            placed,
            routed,
            target,
            description=config.description,
        )
        output_dir = build / "05-output"
        output_dir.mkdir(parents=True, exist_ok=True)
        circuit_path = output_dir / "circuit.data"
        circuit_path.write_bytes(payload)
        _write_json(output_dir / "circuit.json", circuit.to_dict())
        render_svg(placed, routed, output_dir / "layout.svg")
        formal = verify_formal_equivalence(config, logical, build / "06-audit" / "formal")
        physical_audit = audit_physical(placed, routed, circuit)
        _write_json(build / "06-audit" / "formal.json", formal)
        _write_json(build / "06-audit" / "physical.json", physical_audit)
        report = {
            "schema": "turingsynth-build-report-v1",
            "status": "pass",
            "project": config.name,
            "top": config.top,
            "target": config.target_kind,
            "score": {
                "gate": placed.gate,
                "delay": placed.delay,
                "energy": placed.gate * placed.delay,
            },
            "artifacts": {
                "circuit": "05-output/circuit.data",
                "preview": "05-output/layout.svg",
                "yosys_netlist": "01-yosys/netlist.json",
                "normalized_ir": "01-yosys/normalized.json",
                "mapped_ir": "02-mapping/physical.json",
                "placed_ir": "03-layout/placed.json",
                "routing_report": "04-routing/report.json",
                "formal_audit": "06-audit/formal.json",
                "physical_audit": "06-audit/physical.json",
            },
            "hashes": {
                "circuit_sha256": sha256(payload).hexdigest(),
                "source_sha256": yosys_report["source_sha256"],
            },
            "mapping": mapping_report,
            "layout": layout_report,
            "routing": routed.report,
            "formal": formal,
            "physical": physical_audit,
        }
        _write_json(build / "report.json", report)
        return report
    except Exception as exc:
        (build / "FAILED.txt").write_text(
            f"{type(exc).__name__}: {exc}\n", encoding="utf-8"
        )
        raise
