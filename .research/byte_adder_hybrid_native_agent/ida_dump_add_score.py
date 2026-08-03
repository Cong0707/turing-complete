"""IDA batch helper: dump the native score functions and com_add branches."""

from __future__ import annotations

import os
from pathlib import Path

import ida_auto
import ida_bytes
import ida_funcs
import ida_lines
import ida_name
import idaapi
import idc


OUT = Path(os.environ.get(
    "BYTE_ADDER_SCORE_DISASM_OUT",
    r"D:\Develop\Other\turing-complete\.research\byte_adder_hybrid_native_agent"
    r"\native_add_score_disasm.txt",
))


def function_text(ea: int) -> str:
    func = ida_funcs.get_func(ea)
    if func is None:
        return f"no function at 0x{ea:x}\n"
    lines = [
        f"FUNCTION {ida_name.get_name(func.start_ea)} "
        f"0x{func.start_ea:x}..0x{func.end_ea:x}"
    ]
    cursor = func.start_ea
    while cursor < func.end_ea:
        rendered = idc.generate_disasm_line(cursor, 0) or ""
        lines.append(f"0x{cursor:016x}: {ida_lines.tag_remove(rendered)}")
        cursor = ida_bytes.next_head(cursor, func.end_ea)
    return "\n".join(lines) + "\n"


def main() -> None:
    ida_auto.auto_wait()
    targets = [
        "get_gate_cost__modelZscores_u2232",
        "get_delay_cost__modelZscores_u2270",
    ]
    chunks = []
    for name in targets:
        ea = ida_name.get_name_ea(idaapi.BADADDR, name)
        chunks.append(f"LOOKUP {name} = 0x{ea:x}\n")
        if ea != idaapi.BADADDR:
            chunks.append(function_text(ea))
    # Also include the previously identified com_add gate branch neighborhood.
    for ea in (0x1402762FF,):
        chunks.append(f"NEIGHBORHOOD 0x{ea:x}\n")
        cursor = ea - 0x60
        end = ea + 0x120
        while cursor < end:
            rendered = idc.generate_disasm_line(cursor, 0) or ""
            chunks.append(f"0x{cursor:016x}: {ida_lines.tag_remove(rendered)}\n")
            cursor = ida_bytes.next_head(cursor, end)
    OUT.write_text("".join(chunks), encoding="utf-8")
    idc.qexit(0)


try:
    main()
except Exception as exc:
    print(f"DUMP_ERROR: {type(exc).__name__}: {exc}")
    idc.qexit(1)
