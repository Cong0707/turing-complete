"""只读列出 ``unlocks_components`` 字符串的交叉引用。"""

from __future__ import annotations

import json
from pathlib import Path

import ida_auto
import ida_funcs
import ida_name
import idaapi
import idautils


OUTPUT = Path(
    r"D:\Develop\Other\turing-complete\.research\byte_adder_protocol_audit_agent\ida_unlock_xrefs.json"
)


def main() -> None:
    ida_auto.auto_wait()
    records: list[dict[str, object]] = []
    for string in idautils.Strings():
        text = str(string)
        if "unlock" not in text.lower():
            continue
        xrefs = []
        for delta in range(-32, 1, 8):
            for xref in idautils.XrefsTo(string.ea + delta):
                function = ida_funcs.get_func(xref.frm)
                start = function.start_ea if function else idaapi.BADADDR
                xrefs.append(
                    {
                        "target_delta": delta,
                        "from": f"0x{xref.frm:016x}",
                        "function": None if start == idaapi.BADADDR else f"0x{start:016x}",
                        "function_name": "" if start == idaapi.BADADDR else ida_name.get_name(start),
                    }
                )
        records.append(
            {
                "address": f"0x{string.ea:016x}",
                "text": text,
                "xrefs": xrefs,
            }
        )
    matching_names = [
        {"address": f"0x{ea:016x}", "name": name}
        for ea, name in idautils.Names()
        if "unlock" in name.lower()
    ]
    OUTPUT.write_text(
        json.dumps(
            {"strings": records, "matching_names": matching_names},
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    idaapi.qexit(0)


main()
