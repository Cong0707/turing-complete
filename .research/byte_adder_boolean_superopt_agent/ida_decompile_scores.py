"""只读导出 model/scores 的成本函数伪代码与调用关系。"""

from __future__ import annotations

from pathlib import Path

import ida_auto
import ida_funcs
import ida_hexrays
import ida_lines
import ida_name
import idaapi
import idautils
import idc


OUT = Path(r"D:\Develop\Other\turing-complete\.research\byte_adder_boolean_superopt_agent\score_functions.txt")
PREFIXES = (
    "is_free_component_type__modelZscores",
    "get_gate_cost__modelZscores",
    "get_delay_cost__modelZscores",
    "get_cost__modelZscores",
    "insert_cost__modelZscores",
    "add_cost__modelZscores",
    "import_costs__modelZscores",
    "get_all_costs__modelZscores",
)


def clean(value: object) -> str:
    return ida_lines.tag_remove(str(value))


def function_block(ea: int, name: str) -> list[str]:
    result = ["=" * 88, f"{name} @ {ea:#018x}"]
    callers = []
    for xref in idautils.XrefsTo(ea):
        caller = ida_funcs.get_func(xref.frm)
        callers.append(
            f"{xref.frm:#018x} {ida_name.get_name(caller.start_ea) if caller else ''}"
        )
    result.append("CALLERS " + " | ".join(callers))
    try:
        result.append(clean(ida_hexrays.decompile(ea)))
    except Exception as exc:
        result.append(f"DECOMPILE_ERROR {exc}")
        function = ida_funcs.get_func(ea)
        if function:
            for insn_ea in idautils.FuncItems(function.start_ea):
                result.append(f"{insn_ea:#018x} {idc.generate_disasm_line(insn_ea, 0)}")
    return result


ida_auto.auto_wait()
lines: list[str] = []
for ea, name in idautils.Names():
    if any(name.startswith(prefix) for prefix in PREFIXES):
        lines.extend(function_block(ea, name))
OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
idc.qexit(0)
