"""Full v15 import, placement, routing, audit, and lossless component emission."""

from __future__ import annotations

from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path

from turingsynth.audit import (
    audit_layout_readability,
    audit_physical,
    audit_relayout,
)
from turingsynth.config import ProjectConfig
from turingsynth.formats.v15 import decode_v15, encode_v15
from turingsynth.importers import import_v15
from turingsynth.layout import place
from turingsynth.pipeline import _reset_build
from turingsynth.render import render_svg
from turingsynth.routing import FanoutTrackCapacityError, route


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _channel_gap_for_failure(
    net,
    ranks: dict[str, int],
    channel_expansion: dict[int, int],
) -> int:
    """Choose a layer gap that actually separates the failed terminals."""

    source_rank = ranks[net.source.component]
    other_ranks = [
        ranks[pin.component]
        for pin in (*net.sinks, *net.additional_sources)
        if ranks[pin.component] != source_rank
    ]
    if not other_ranks:
        return source_rank
    if max(other_ranks) < source_rank:
        return source_rank - 1
    if min(other_ranks) > source_rank:
        return source_rank

    candidates = (source_rank - 1, source_rank)
    return min(
        candidates,
        key=lambda rank: (channel_expansion.get(rank, 0), rank),
    )


def relayout_v15(
    compiler_root: Path,
    source_path: Path,
) -> dict[str, object]:
    root = Path(compiler_root).resolve()
    source = Path(source_path).resolve()
    build = _reset_build(root)
    try:
        imported = import_v15(source)
        source_payload = source.read_bytes()
        _write_json(
            build / "01-import" / "report.json",
            {
                "schema": "turingsynth-v15-import-v1",
                "source": str(source),
                "source_sha256": sha256(source_payload).hexdigest(),
                "gate": imported.design.gate,
                "delay": imported.design.delay,
                "energy": imported.design.gate * imported.design.delay,
                "component_count": len(imported.design.components),
                "logical_network_count": imported.logical_network_count,
                "lossless_component_metadata": True,
            },
        )
        _write_json(
            build / "02-mapping" / "physical.json",
            imported.design.to_dict(),
        )
        config = ProjectConfig(
            manifest=source,
            name="v15 relayout",
            top="imported_v15",
            sources=(source,),
            target_kind="level",
            logical_key="relayout/imported-v15",
            description=imported.circuit.description,
            template=source,
            port_bindings={},
            pack_widths=(8, 4, 2),
            horizontal_clearance=5,
            vertical_clearance=3,
        )
        net_by_name = {net.name: net for net in imported.design.nets}
        channel_expansion: dict[int, int] = {}
        routing_attempts: list[dict[str, object]] = []
        for attempt in range(48):
            placed, layout_report = place(
                imported.design,
                config,
                channel_expansion=channel_expansion,
            )
            layout_report["readability"] = audit_layout_readability(
                placed,
                layout_report["ranks"],
            )
            _write_json(build / "03-layout" / "placed.json", placed.to_dict())
            _write_json(build / "03-layout" / "report.json", layout_report)
            try:
                routed = route(placed)
                break
            except FanoutTrackCapacityError as exc:
                failed_networks = tuple(
                    network
                    for network in exc.networks
                    if network in net_by_name
                )
                if not failed_networks:
                    raise
                gaps = {
                    _channel_gap_for_failure(
                        net_by_name[network],
                        layout_report["ranks"],
                        channel_expansion,
                    )
                    for network in failed_networks
                }
                routing_attempts.append(
                    {
                        "attempt": attempt,
                        "failed_networks": list(failed_networks),
                        "expanded_gaps": sorted(gaps),
                        "error": str(exc),
                    }
                )
                for gap in gaps:
                    channel_expansion[gap] = channel_expansion.get(gap, 0) + 1
        else:
            raise RuntimeError("v15 relayout exhausted targeted channel expansion")

        positions = {
            component.key: component.position for component in placed.components
        }
        relocated_components = []
        for index, original in enumerate(imported.circuit.components):
            position = positions[imported.component_key_by_index[index]]
            if position is None:
                raise RuntimeError("relayout omitted a component position")
            if original.immutable and position != original.position:
                raise RuntimeError("relayout moved an immutable campaign component")
            relocated_components.append(replace(original, position=position))
        circuit = replace(
            imported.circuit,
            components=tuple(relocated_components),
            wires=routed.wires,
        )
        payload = encode_v15(circuit)
        if decode_v15(payload) != circuit:
            raise RuntimeError("relayout v15 round trip changed the circuit")
        lossless = audit_relayout(imported.circuit, circuit)
        physical = audit_physical(placed, routed, circuit)
        output = build / "05-output"
        output.mkdir(parents=True, exist_ok=True)
        (output / "circuit.data").write_bytes(payload)
        _write_json(output / "circuit.json", circuit.to_dict())
        render_svg(placed, routed, output / "layout.svg")
        _write_json(build / "04-routing" / "report.json", routed.report)
        _write_json(build / "06-audit" / "physical.json", physical)
        _write_json(build / "06-audit" / "relayout.json", lossless)
        report = {
            "schema": "turingsynth-v15-relayout-report-v1",
            "status": "pass",
            "score": {
                "gate": circuit.gate,
                "delay": circuit.delay,
                "energy": circuit.energy,
            },
            "source": str(source),
            "component_count": len(circuit.components),
            "logical_network_count": imported.logical_network_count,
            "wire_count": len(circuit.wires),
            "immutable_component_positions_preserved": True,
            "all_component_fields_except_position_preserved": True,
            "hashes": {
                "source_sha256": sha256(source_payload).hexdigest(),
                "output_sha256": sha256(payload).hexdigest(),
            },
            "layout": layout_report,
            "routing": routed.report,
            "routing_attempts": routing_attempts,
            "physical": physical,
            "lossless_relayout": lossless,
            "artifacts": {
                "circuit": "05-output/circuit.data",
                "preview": "05-output/layout.svg",
            },
        }
        _write_json(build / "report.json", report)
        return report
    except Exception as exc:
        (build / "FAILED.txt").write_text(
            f"{type(exc).__name__}: {exc}\n",
            encoding="utf-8",
        )
        raise
