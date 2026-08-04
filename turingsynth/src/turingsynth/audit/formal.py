"""Emit a structural Verilog witness and prove it equivalent with Yosys."""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import re
import subprocess

from turingsynth.config import ProjectConfig
from turingsynth.frontend.yosys import find_yosys
from turingsynth.ir.logical import Bit, LogicNetlist


IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_$]*\Z")


def _identifier(value: str) -> str:
    return value if IDENTIFIER.fullmatch(value) else "\\" + value + " "


def _quoted(path: Path) -> str:
    return '"' + str(path.resolve()).replace("\\", "/").replace('"', '\\"') + '"'


def _mapped_verilog(logical: LogicNetlist) -> tuple[str, str]:
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
    pending = list(logical.cells)
    ordered = []
    while pending:
        ready = [cell for cell in pending if all(bit in expression for bit in cell.inputs)]
        if not ready:
            raise ValueError("cannot emit mapped Verilog from a cyclic logic netlist")
        ready.sort(key=lambda cell: cell.name)
        for cell in ready:
            wire = f"turingsynth_n_{cell.output}"
            lines.append(f"  wire {wire};")
            values = [expression[bit] for bit in cell.inputs]
            formulas = {
                "NOT": f"~({values[0]})",
                "AND": f"({values[0]}) & ({values[1]})",
                "NAND": f"~(({values[0]}) & ({values[1]}))",
                "OR": f"({values[0]}) | ({values[1]})",
                "NOR": f"~(({values[0]}) | ({values[1]}))",
                "XOR": f"({values[0]}) ^ ({values[1]})",
            }
            lines.append(f"  assign {wire} = {formulas[cell.op]};")
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
    config: ProjectConfig, logical: LogicNetlist, stage_dir: Path
) -> dict[str, object]:
    stage_dir.mkdir(parents=True, exist_ok=True)
    mapped_name, mapped = _mapped_verilog(logical)
    mapped_path = stage_dir / "mapped.v"
    script_path = stage_dir / "equiv.ys"
    log_path = stage_dir / "equiv.log"
    mapped_path.write_text(mapped, encoding="utf-8")
    reads = "\n".join(f"read_verilog -sv {_quoted(path)}" for path in config.sources)
    script = f"""{reads}
prep -top {config.top}
design -stash gold
read_verilog -sv {mapped_path.name}
prep -top {mapped_name}
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
        "mapped_cell_count": len(logical.cells),
    }
