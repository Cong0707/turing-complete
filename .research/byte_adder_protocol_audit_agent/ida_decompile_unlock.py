"""只读导出少量解锁相关函数的伪代码与调用者。"""

from __future__ import annotations

import json
from pathlib import Path

import ida_auto
import ida_funcs
import ida_hexrays
import ida_name
import idaapi
import idautils


OUTPUT = Path(
    r"D:\Develop\Other\turing-complete\.research\byte_adder_protocol_audit_agent\ida_decompile_unlock.json"
)
TARGETS = (
    "is_score_unlocked__modelZboardZschematics_u1782",
    "is_unlocked__modelZcampaigns_u16787",
    "get_level_unlockable_components__presenterZutilitiesZhelper95functions_u1522",
)


def main() -> None:
    ida_auto.auto_wait()
    result: list[dict[str, object]] = []
    for name in TARGETS:
        address = ida_name.get_name_ea(idaapi.BADADDR, name)
        callers = []
        for reference in idautils.CodeRefsTo(address, False):
            function = ida_funcs.get_func(reference)
            callers.append(
                {
                    "reference": f"0x{reference:016x}",
                    "function": "" if function is None else ida_name.get_name(function.start_ea),
                }
            )
        try:
            pseudocode = str(ida_hexrays.decompile(address))
        except Exception as error:
            pseudocode = f"{type(error).__name__}: {error}"
        result.append(
            {
                "name": name,
                "address": f"0x{address:016x}",
                "callers": callers,
                "pseudocode": pseudocode,
            }
        )
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    idaapi.qexit(0)


main()
