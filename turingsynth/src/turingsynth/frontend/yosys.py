"""Deterministic Yosys synthesis and JSON normalization."""

from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

from turingsynth.config import ProjectConfig
from turingsynth.ir.logical import (
    Bit,
    Cell,
    CellPort,
    CustomCell,
    LogicNetlist,
    Port,
)
from turingsynth.library import CustomModule


CELL_TYPES = {
    "$_NOT_": ("NOT", ("A",), "Y"),
    "$_AND_": ("AND", ("A", "B"), "Y"),
    "$_NAND_": ("NAND", ("A", "B"), "Y"),
    "$_OR_": ("OR", ("A", "B"), "Y"),
    "$_NOR_": ("NOR", ("A", "B"), "Y"),
    "$_XOR_": ("XOR", ("A", "B"), "Y"),
}


def find_yosys() -> str:
    explicit = os.environ.get("TURINGSYNTH_YOSYS")
    candidates = [explicit] if explicit else []
    executable_dir = Path(sys.executable).resolve().parent
    candidates.extend(
        [
            str(executable_dir / "yowasp-yosys.exe"),
            str(executable_dir / "yowasp-yosys"),
            str(executable_dir / "yosys.exe"),
            str(executable_dir / "yosys"),
        ]
    )
    candidates.extend(["yowasp-yosys", "yowasp-yosys.exe", "yosys", "yosys.exe"])
    for candidate in candidates:
        if candidate and (Path(candidate).is_file() or shutil.which(candidate)):
            return candidate
    raise RuntimeError(
        "Yosys was not found. Install requirements.txt or set TURINGSYNTH_YOSYS."
    )


def _yosys_quote(path: Path) -> str:
    value = str(path.resolve()).replace("\\", "/")
    return '"' + value.replace('"', '\\"') + '"'


def _identifier(value: str) -> str:
    if value and (value[0].isalpha() or value[0] == "_") and all(
        character.isalnum() or character in "_$" for character in value
    ):
        return value
    return "\\" + value + " "


def _read_commands(
    config: ProjectConfig,
    *,
    include_dirs: tuple[Path, ...] | None = None,
) -> str:
    include_dirs = config.include_dirs if include_dirs is None else include_dirs
    options = ["-sv"]
    options.extend(f"-I{path.as_posix()}" for path in include_dirs)
    options.extend(f"-D{value}" for value in config.defines)
    prefix = " ".join(options)
    return "\n".join(
        f"read_verilog {prefix} {_yosys_quote(path)}" for path in config.sources
    )


def _staged_read_commands(
    config: ProjectConfig,
    stage_dir: Path,
    namespace: str,
) -> str:
    staged = []
    for index, source in enumerate(config.include_dirs):
        destination = stage_dir / "includes" / namespace / f"{index:03d}"
        shutil.copytree(source, destination)
        staged.append(destination.relative_to(stage_dir))
    return _read_commands(config, include_dirs=tuple(staged))


def _blackbox_stubs(custom_modules: dict[str, CustomModule]) -> str:
    lines = []
    for module_name, module in sorted(custom_modules.items()):
        ports = ", ".join(_identifier(port.name) for port in module.ports)
        lines.append(f"(* blackbox *) module {_identifier(module_name)}({ports});")
        for port in module.ports:
            vector = "" if len(port.bits) == 1 else f"[{len(port.bits) - 1}:0] "
            signed = "signed " if port.signed else ""
            lines.append(
                f"  {port.direction} wire {signed}{vector}{_identifier(port.name)};"
            )
        lines.append("endmodule")
    return "\n".join(lines) + ("\n" if lines else "")


def _script(
    config: ProjectConfig,
    json_path: Path,
    *,
    custom_modules: dict[str, CustomModule],
    reads: str | None = None,
) -> str:
    reads = _read_commands(config) if reads is None else reads
    stub_read = (
        'read_verilog -sv -lib "custom-stubs.sv"\n' if custom_modules else ""
    )
    parameters = "\n".join(
        f"chparam -set {_identifier(name)} {value} {_identifier(config.top)}"
        for name, value in config.parameters
    )
    return f"""{stub_read}{reads}
{parameters}
hierarchy -check -top {_identifier(config.top)}
proc
flatten
tribuf -logic
deminout
memory_map
opt -full
techmap
opt -full
abc -g AND,OR,XOR,NAND,NOR
clean -purge
check -assert
write_json {json_path.as_posix()}
"""


def _normalize_bit(value: object) -> Bit:
    if isinstance(value, int):
        return value
    text = str(value).lower()
    if text in {"0", "1"}:
        return text
    raise ValueError(f"unsupported Yosys constant/state {value!r}; x/z are forbidden")


def normalize_yosys_json(
    raw: dict[str, object],
    config: ProjectConfig,
    custom_modules: dict[str, CustomModule] | None = None,
) -> LogicNetlist:
    custom_modules = custom_modules or {}
    modules = raw.get("modules")
    if not isinstance(modules, dict) or config.top not in modules:
        raise ValueError(f"Yosys JSON does not contain top module {config.top!r}")
    module = modules[config.top]
    if not isinstance(module, dict):
        raise ValueError("malformed Yosys module")
    ports_raw = module.get("ports", {})
    cells_raw = module.get("cells", {})
    top_ports = []
    for name, item in ports_raw.items():
        if not isinstance(item, dict):
            raise ValueError(f"malformed port {name!r}")
        direction = str(item.get("direction"))
        if direction not in {"input", "output"}:
            raise ValueError(f"inout port {name!r} is not supported")
        top_ports.append(
            Port(
                name=str(name),
                direction=direction,
                bits=tuple(_normalize_bit(bit) for bit in item.get("bits", ())),
                signed=bool(item.get("signed", False)),
            )
        )
    cells = []
    custom_cells = []
    unsupported: dict[str, int] = {}
    for name, item in cells_raw.items():
        if not isinstance(item, dict):
            raise ValueError(f"malformed cell {name!r}")
        cell_type = str(item.get("type"))
        spec = CELL_TYPES.get(cell_type)
        custom_module = custom_modules.get(cell_type)
        if spec is None and custom_module is None:
            unsupported[cell_type] = unsupported.get(cell_type, 0) + 1
            continue
        connections = item.get("connections")
        if not isinstance(connections, dict):
            raise ValueError(f"cell {name!r} has no connections")
        attributes = item.get("attributes", {})
        normalized_attributes = (
            tuple(sorted((str(key), str(value)) for key, value in attributes.items()))
            if isinstance(attributes, dict)
            else ()
        )
        if custom_module is not None:
            custom_ports = []
            for port in custom_module.ports:
                values = connections.get(port.name)
                if not isinstance(values, list) or len(values) != len(port.bits):
                    raise ValueError(
                        f"custom cell {name!r} port {port.name!r} width differs "
                        f"from component {custom_module.name!r}"
                    )
                custom_ports.append(
                    CellPort(
                        name=port.name,
                        direction=port.direction,
                        bits=tuple(_normalize_bit(bit) for bit in values),
                    )
                )
            custom_cells.append(
                CustomCell(
                    name=str(name),
                    module=cell_type,
                    ports=tuple(custom_ports),
                    attributes=normalized_attributes,
                )
            )
            continue
        assert spec is not None
        op, input_names, output_name = spec
        inputs = tuple(
            _normalize_bit(connections[pin][0])
            for pin in input_names
            if isinstance(connections.get(pin), list) and len(connections[pin]) == 1
        )
        output_values = connections.get(output_name)
        if len(inputs) != len(input_names) or not isinstance(output_values, list) or len(output_values) != 1:
            raise ValueError(f"cell {name!r} is not a scalar standard cell")
        output = _normalize_bit(output_values[0])
        if not isinstance(output, int):
            raise ValueError(f"cell {name!r} drives a constant")
        cells.append(
            Cell(
                name=str(name),
                op=op,
                inputs=inputs,
                output=output,
                attributes=normalized_attributes,
            )
        )
    if unsupported:
        raise ValueError(
            "Yosys emitted unsupported cells; sequential logic and black boxes must "
            f"use an explicit future technology profile: {unsupported!r}"
        )
    result = LogicNetlist(
        top=config.top,
        ports=tuple(top_ports),
        cells=tuple(cells),
        source_files=tuple(str(path) for path in config.sources),
        custom_cells=tuple(custom_cells),
    )
    result.validate()
    return result


def synthesize(
    config: ProjectConfig,
    stage_dir: Path,
    *,
    custom_modules: dict[str, CustomModule] | None = None,
) -> tuple[LogicNetlist, dict[str, object]]:
    custom_modules = custom_modules or {}
    stage_dir.mkdir(parents=True, exist_ok=True)
    json_path = stage_dir / "netlist.json"
    script_path = stage_dir / "synth.ys"
    log_path = stage_dir / "yosys.log"
    if custom_modules:
        (stage_dir / "custom-stubs.sv").write_text(
            _blackbox_stubs(custom_modules), encoding="utf-8"
        )
    reads = _staged_read_commands(config, stage_dir, "project")
    script = _script(
        config,
        Path("netlist.json"),
        custom_modules=custom_modules,
        reads=reads,
    )
    script_path.write_text(script, encoding="utf-8")
    command = [find_yosys(), "-q", "-l", log_path.name, "-s", script_path.name]
    completed = subprocess.run(
        command,
        cwd=stage_dir,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode:
        raise RuntimeError(
            f"Yosys failed with exit code {completed.returncode}:\n"
            f"{completed.stderr[-4000:]}"
        )
    raw_bytes = json_path.read_bytes()
    raw = json.loads(raw_bytes)
    netlist = normalize_yosys_json(raw, config, custom_modules)
    normalized_path = stage_dir / "normalized.json"
    normalized_path.write_text(
        json.dumps(netlist.to_dict(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    report = {
        "schema": "turingsynth-yosys-stage-v1",
        "executable": command[0],
        "command": command,
        "source_sha256": {
            str(path): sha256(path.read_bytes()).hexdigest() for path in config.sources
        },
        "script_sha256": sha256(script.encode()).hexdigest(),
        "yosys_json_sha256": sha256(raw_bytes).hexdigest(),
        "port_count": len(netlist.ports),
        "cell_count": len(netlist.cells),
        "custom_cell_count": len(netlist.custom_cells),
        "custom_modules": sorted(custom_modules),
    }
    (stage_dir / "report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return netlist, report
