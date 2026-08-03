"""只读导出当前 IDB 中与 Add/成本有关的符号和交叉引用。"""

from __future__ import annotations

from pathlib import Path

import ida_funcs
import ida_name
import idautils
import idc


OUT = Path(r"D:\Develop\Other\turing-complete\.research\byte_adder_boolean_superopt_agent\ida_add_query.txt")
KEYS = ("add", "cost", "gate", "delay", "component")


def interesting(name: str) -> bool:
    lower = name.casefold()
    return any(key in lower for key in KEYS)


lines: list[str] = []
for ea, name in idautils.Names():
    if not interesting(name):
        continue
    function = ida_funcs.get_func(ea)
    lines.append(
        f"NAME {ea:#018x} {name} func={function.start_ea:#018x}" if function else f"NAME {ea:#018x} {name}"
    )

for string in idautils.Strings():
    value = str(string)
    lower = value.casefold()
    if not any(key in lower for key in KEYS):
        continue
    if len(value) > 240:
        continue
    lines.append(f"STRING {string.ea:#018x} {value!r}")
    for xref in idautils.XrefsTo(string.ea):
        function = ida_funcs.get_func(xref.frm)
        fname = ida_name.get_name(function.start_ea) if function else ""
        lines.append(f"  XREF {xref.frm:#018x} function={fname}")

OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
idc.qexit(0)
