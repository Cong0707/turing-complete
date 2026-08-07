"""Emit a structural Verilog witness and prove it equivalent with Yosys."""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import re
import subprocess

from turingsynth.config import ProjectConfig
from turingsynth.frontend.yosys import _staged_read_commands, find_yosys
from turingsynth.ir.logical import Bit, Cell, CustomCell, LogicNetlist
from turingsynth.library import CustomModule


IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_$]*\Z")


def _identifier(value: str) -> str:
    return value if IDENTIFIER.fullmatch(value) else "\\" + value + " "


def _quoted(path: Path) -> str:
    return '"' + str(path.resolve()).replace("\\", "/").replace('"', '\\"') + '"'


def _vector_expression(bits: tuple[Bit, ...], expression: dict[Bit, str]) -> str:
    values = [expression[bit] for bit in bits]
    return values[0] if len(values) == 1 else "{" + ", ".join(reversed(values)) + "}"


def _mapped_verilog(
    logical: LogicNetlist,
    custom_modules: dict[str, CustomModule] | None = None,
) -> tuple[str, str]:
    custom_modules = custom_modules or {}
    module_name = f"{logical.top}__turingsynth_mapped"
    port_names = ", ".join(_identifier(port.name) for port in logical.ports)
    lines = [f"module {_identifier(module_name)}({port_names});"]
    for port in logical.ports:
        width = len(port.bits)
        vector = "" if width == 1 else f"[{width - 1}:0] "
        lines.append(f"  {port.direction} wire {vector}{_identifier(port.name)};")
    expression: dict[Bit, str] = {"0": "1'b0", "1": "1'b1"}
    for port in logical.input_ports:
        for lane, bit in enumerate(port.bits):
            if isinstance(bit, int):
                expression[bit] = (
                    _identifier(port.name)
                    if len(port.bits) == 1
                    else f"{_identifier(port.name)}[{lane}]"
                )
    pending: list[Cell | CustomCell] = [*logical.cells, *logical.custom_cells]
    ordered = []
    while pending:
        ready = [
            cell
            for cell in pending
            if all(
                bit in expression
                for bit in (
                    cell.inputs if isinstance(cell, Cell) else cell.input_bits
                )
            )
        ]
        if not ready:
            raise ValueError("cannot emit mapped Verilog from a cyclic logic netlist")
        ready.sort(key=lambda cell: cell.name)
        for cell in ready:
            if isinstance(cell, CustomCell):
                if cell.module not in custom_modules:
                    raise ValueError(
                        f"mapped Verilog references unknown Custom module {cell.module!r}"
                    )
                connections = []
                for port in cell.ports:
                    if port.direction == "input":
                        value = _vector_expression(port.bits, expression)
                    else:
                        value = (
                            f"turingsynth_custom_{len(ordered)}_"
                            f"{re.sub(r'[^A-Za-z0-9_$]', '_', port.name)}"
                        )
                        vector = (
                            ""
                            if len(port.bits) == 1
                            else f"[{len(port.bits) - 1}:0] "
                        )
                        lines.append(f"  wire {vector}{value};")
                        for lane, bit in enumerate(port.bits):
                            assert isinstance(bit, int)
                            expression[bit] = (
                                value if len(port.bits) == 1 else f"{value}[{lane}]"
                            )
                    connections.append(f".{_identifier(port.name)}({value})")
                lines.append(
                    f"  {_identifier(cell.module)} {_identifier(cell.name)} "
                    f"({', '.join(connections)});"
                )
                ordered.append(cell)
                pending.remove(cell)
                continue
            wire = f"turingsynth_n_{cell.output}"
            lines.append(f"  wire {wire};")
            values = [expression[bit] for bit in cell.inputs]
            if cell.op == "NOT":
                formula = f"~({values[0]})"
            else:
                formulas = {
                    "AND": f"({values[0]}) & ({values[1]})",
                    "NAND": f"~(({values[0]}) & ({values[1]}))",
                    "OR": f"({values[0]}) | ({values[1]})",
                    "NOR": f"~(({values[0]}) | ({values[1]}))",
                    "XOR": f"({values[0]}) ^ ({values[1]})",
                }
                formula = formulas[cell.op]
            lines.append(f"  assign {wire} = {formula};")
            expression[cell.output] = wire
            ordered.append(cell)
            pending.remove(cell)
    for port in logical.output_ports:
        for lane, bit in enumerate(port.bits):
            destination = (
                _identifier(port.name)
                if len(port.bits) == 1
                else f"{_identifier(port.name)}[{lane}]"
            )
            lines.append(f"  assign {destination} = {expression[bit]};")
    lines.append("endmodule")
    return module_name, "\n".join(lines) + "\n"


def verify_formal_equivalence(
    config: ProjectConfig,
    logical: LogicNetlist,
    stage_dir: Path,
    *,
    custom_modules: dict[str, CustomModule] | None = None,
) -> dict[str, object]:
    custom_modules = custom_modules or {}
    stage_dir.mkdir(parents=True, exist_ok=True)
    mapped_name, mapped = _mapped_verilog(logical, custom_modules)
    mapped_path = stage_dir / "mapped.v"
    script_path = stage_dir / "equiv.ys"
    log_path = stage_dir / "equiv.log"
    mapped_path.write_text(mapped, encoding="utf-8")
    library_reads = "\n".join(
        _staged_read_commands(
            config.for_component(module.config),
            stage_dir,
            f"library-{index:03d}",
        )
        for index, (_name, module) in enumerate(sorted(custom_modules.items()))
    )
    reads = _staged_read_commands(config, stage_dir, "project")
    parameters = "\n".join(
        f"chparam -set {_identifier(name)} {value} {_identifier(config.top)}"
        for name, value in config.parameters
    )
    script = f"""{library_reads}
{reads}
{parameters}
prep -top {config.top} -flatten
design -stash gold
{library_reads}
read_verilog -sv {mapped_path.name}
prep -top {mapped_name} -flatten
design -stash gate
design -copy-from gold -as gold {config.top}
design -copy-from gate -as gate {mapped_name}
equiv_make gold gate equiv
prep -top equiv
equiv_simple
equiv_status -assert
"""
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
            f"formal equivalence failed with exit code {completed.returncode}:\n"
            f"{completed.stderr[-4000:]}"
        )
    return {
        "schema": "turingsynth-yosys-equivalence-v1",
        "status": "pass",
        "method": "Yosys equiv_make + equiv_simple + equiv_status -assert",
        "mapped_verilog_sha256": sha256(mapped.encode()).hexdigest(),
        "script_sha256": sha256(script.encode()).hexdigest(),
        "mapped_cell_count": len(logical.cells) + len(logical.custom_cells),
        "custom_cell_count": len(logical.custom_cells),
    }
