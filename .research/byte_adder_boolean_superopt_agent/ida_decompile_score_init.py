"""只读导出默认成本表符号的所有引用函数。"""

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


OUT = Path(r"D:\Develop\Other\turing-complete\.research\byte_adder_boolean_superopt_agent\score_initializers.txt")
SYMBOLS = (
    "DEFAULT_COMPONENT_SCORES__modelZscores_u1605",
    "component_costs__modelZscores_u10",
    "component_cost_buffer__modelZscores_u12",
)


ida_auto.auto_wait()
functions: dict[int, list[str]] = {}
lines: list[str] = []
for symbol in SYMBOLS:
    ea = ida_name.get_name_ea(idaapi.BADADDR, symbol)
    lines.append(f"SYMBOL {symbol} {ea:#018x}")
    for xref in idautils.XrefsTo(ea):
        function = ida_funcs.get_func(xref.frm)
        lines.append(f"  XREF {xref.frm:#018x} {ida_name.get_name(function.start_ea) if function else ''}")
        if function:
            functions.setdefault(function.start_ea, []).append(symbol)

for ea, name in idautils.Names():
    if name == "X5BX5D___modelZscores_u1990" or (
        "modelZscores" in name and "Init" in name
    ):
        function = ida_funcs.get_func(ea)
        if function:
            functions.setdefault(function.start_ea, []).append("targeted-score-helper")

for ea, symbols in sorted(functions.items()):
    name = ida_name.get_name(ea)
    lines.extend(("=" * 88, f"{name} @ {ea:#018x} refs={','.join(symbols)}"))
    try:
        lines.append(ida_lines.tag_remove(str(ida_hexrays.decompile(ea))))
    except Exception as exc:
        lines.append(f"DECOMPILE_ERROR {exc}")
OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
idc.qexit(0)
