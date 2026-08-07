"""Single-build-directory compiler and hierarchical package pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import shutil

from turingsynth.audit import audit_physical, verify_formal_equivalence
from turingsynth.config import ComponentConfig, ProjectConfig, load_project
from turingsynth.formats.emitter import emit_v15
from turingsynth.formats.package import (
    PackageDependency,
    PackageFile,
    SchematicPackage,
    decode_package,
    encode_package,
)
from turingsynth.formats.model import Circuit
from turingsynth.frontend import synthesize
from turingsynth.ir.logical import LogicNetlist
from turingsynth.layout import place
from turingsynth.library import CustomModule
from turingsynth.mapping.native import configure_custom_components
from turingsynth.mapping.packer import map_to_native
from turingsynth.render import render_svg
from turingsynth.routing import FanoutTrackCapacityError, route
from turingsynth.targets import build_target_context


@dataclass(frozen=True)
class _BuildArtifact:
    report: dict[str, object]
    logical: LogicNetlist
    circuit: Circuit
    payload: bytes


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


def _component_order(config: ProjectConfig) -> tuple[ComponentConfig, ...]:
    by_name = {component.name: component for component in config.components}
    pending = list(config.components)
    emitted: list[ComponentConfig] = []
    completed: set[str] = set()
    while pending:
        ready = [
            component
            for component in pending
            if set(component.dependencies) <= completed
        ]
        if not ready:
            cycle = [component.name for component in pending]
            raise ValueError(f"Custom component dependency graph contains a cycle: {cycle!r}")
        ready.sort(key=lambda component: list(by_name).index(component.name))
        for component in ready:
            emitted.append(component)
            completed.add(component.name)
            pending.remove(component)
    return tuple(emitted)


def _compile_design(
    config: ProjectConfig,
    stage_root: Path,
    custom_modules: dict[str, CustomModule],
) -> _BuildArtifact:
    stage_root.mkdir(parents=True, exist_ok=True)
    _write_json(
        stage_root / "project.json",
        {
            "schema": "turingsynth-build-unit-v2",
            "manifest": str(config.manifest),
            "name": config.name,
            "top": config.top,
            "target": config.target_kind,
            "sources": [str(path) for path in config.sources],
            "include_dirs": [str(path) for path in config.include_dirs],
            "defines": list(config.defines),
            "parameters": dict(config.parameters),
            "custom_modules": sorted(custom_modules),
        },
    )
    logical, yosys_report = synthesize(
        config,
        stage_root / "01-yosys",
        custom_modules=custom_modules,
    )
    definitions = {
        module.circuit.custom_id: module.circuit
        for module in custom_modules.values()
    }
    configure_custom_components(tuple(definitions.values()))
    target = build_target_context(config, logical)
    physical = map_to_native(
        config,
        logical,
        target,
        custom_modules=custom_modules,
    )
    _write_json(stage_root / "02-mapping" / "physical.json", physical.to_dict())
    mapping_report = {
        "schema": "turingsynth-native-mapping-v2",
        "gate": physical.gate,
        "delay": physical.delay,
        "energy": physical.gate * physical.delay,
        "component_count": len(physical.components),
        "custom_component_count": sum(
            component.kind == 78 for component in physical.components
        ),
        "logical_net_count": len(physical.nets),
        "zero_cost_pack_components": sum(
            component.role in {"maker", "splitter"}
            for component in physical.components
        ),
        "no_padding_lanes": True,
        "cost_or_delay_added_by_packaging": False,
    }
    _write_json(stage_root / "02-mapping" / "report.json", mapping_report)
    net_by_name = {net.name: net for net in physical.nets}
    channel_expansion: dict[int, int] = {}
    for _layout_attempt in range(32):
        placed, layout_report = place(
            physical,
            config,
            channel_expansion=channel_expansion,
        )
        _write_json(stage_root / "03-layout" / "placed.json", placed.to_dict())
        _write_json(stage_root / "03-layout" / "report.json", layout_report)
        try:
            routed = route(
                placed,
                conductor_hints={
                    str(network): int(x)
                    for network, x in dict(
                        layout_report.get("planned_conductor_spines", {})
                    ).items()
                },
            )
            break
        except FanoutTrackCapacityError as exc:
            net = net_by_name.get(exc.network)
            if net is None:
                raise
            source_rank = int(layout_report["ranks"][net.source.component])
            channel_expansion[source_rank] = channel_expansion.get(source_rank, 0) + 1
    else:
        raise RuntimeError(
            "layout could not provide enough legal fanout-track capacity "
            "after 32 targeted channel expansions"
        )
    _write_json(stage_root / "04-routing" / "report.json", routed.report)
    circuit, payload = emit_v15(
        placed,
        routed,
        target,
        description=config.description,
        custom_definitions=definitions,
    )
    output_dir = stage_root / "05-output"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "circuit.data").write_bytes(payload)
    _write_json(output_dir / "circuit.json", circuit.to_dict())
    render_svg(placed, routed, output_dir / "layout.svg")
    formal = verify_formal_equivalence(
        config,
        logical,
        stage_root / "06-audit" / "formal",
        custom_modules=custom_modules,
    )
    physical_audit = audit_physical(placed, routed, circuit)
    _write_json(stage_root / "06-audit" / "formal.json", formal)
    _write_json(stage_root / "06-audit" / "physical.json", physical_audit)
    report = {
        "schema": "turingsynth-build-unit-report-v2",
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
    _write_json(stage_root / "report.json", report)
    return _BuildArtifact(report, logical, circuit, payload)


def _package_project(
    config: ProjectConfig,
    build: Path,
    modules: tuple[CustomModule, ...],
    main: _BuildArtifact,
) -> dict[str, object]:
    output_dir = build / "05-output"
    dependencies = []
    dependency_records = []
    for module in modules:
        files = (PackageFile("circuit.data", module.payload),)
        dependencies.append(
            PackageDependency(path=module.config.display_path, files=files)
        )
        mirror = (
            output_dir
            / "dependencies"
            / Path(*module.config.display_path.split("/"))
            / "circuit.data"
        )
        mirror.parent.mkdir(parents=True, exist_ok=True)
        mirror.write_bytes(module.payload)
        dependency_records.append(
            {
                "name": module.name,
                "module": module.top,
                "path": module.config.display_path,
                "custom_id": module.circuit.custom_id,
                "gate": module.circuit.gate,
                "delay": module.circuit.delay,
                "sha256": sha256(module.payload).hexdigest(),
            }
        )
    package = SchematicPackage(
        level=config.package.level,
        dependencies=tuple(dependencies),
        main_files=(PackageFile("circuit.data", main.payload),),
    )
    payload = encode_package(package)
    decoded = decode_package(payload)
    if decoded != package:
        raise RuntimeError("schematic package round trip changed the project")
    package_path = output_dir / config.package.filename
    package_path.write_bytes(payload)
    package_report = {
        "schema": "turingsynth-package-report-v1",
        "status": "pass",
        "level": package.level,
        "filename": package_path.name,
        "bytes": len(payload),
        "sha256": sha256(payload).hexdigest(),
        "main_sha256": sha256(main.payload).hexdigest(),
        "dependencies": dependency_records,
        "round_trip_verified": True,
    }
    _write_json(output_dir / "package.json", package_report)
    return package_report


def build_project(compiler_root: Path, manifest: Path) -> dict[str, object]:
    compiler_root = Path(compiler_root).resolve()
    config = load_project(manifest)
    build = _reset_build(compiler_root)
    try:
        modules_by_name: dict[str, CustomModule] = {}
        ordered_modules = []
        for component in _component_order(config):
            dependencies = {
                modules_by_name[name].top: modules_by_name[name]
                for name in component.dependencies
            }
            artifact = _compile_design(
                config.for_component(component),
                build / "units" / component.name,
                dependencies,
            )
            module = CustomModule(
                config=component,
                logical=artifact.logical,
                circuit=artifact.circuit,
                payload=artifact.payload,
            )
            module.port_components()
            modules_by_name[component.name] = module
            ordered_modules.append(module)

        top_library = {module.top: module for module in ordered_modules}
        main = _compile_design(config, build, top_library)
        report = dict(main.report)
        report["schema"] = "turingsynth-build-report-v2"
        report["components"] = [
            {
                "name": module.name,
                "top": module.top,
                "display_path": module.config.display_path,
                "custom_id": module.circuit.custom_id,
                "gate": module.circuit.gate,
                "delay": module.circuit.delay,
                "direct_dependencies": list(module.config.dependencies),
            }
            for module in ordered_modules
        ]
        if config.package.enabled:
            package_report = _package_project(
                config,
                build,
                tuple(ordered_modules),
                main,
            )
            report["package"] = package_report
            report["artifacts"] = {
                **dict(report["artifacts"]),
                "package": f"05-output/{config.package.filename}",
                "package_report": "05-output/package.json",
            }
        report["build_directory_policy"] = (
            "single disposable compiler-root/build with nested unit stages"
        )
        _write_json(build / "report.json", report)
        return report
    except Exception as exc:
        (build / "FAILED.txt").write_text(
            f"{type(exc).__name__}: {exc}\n", encoding="utf-8"
        )
        raise
