"""Export switch-case mappings from the current giant simulation code generator."""

from __future__ import annotations

import json
import os

import ida_auto
import ida_bytes
import ida_funcs
import ida_nalt
import ida_xref
import idautils
import idc


OUTPUT = os.environ.get("TC_IDA_OUTPUT")
FUNCTION_EA = 0x1404432F8


def main() -> None:
    if not OUTPUT:
        raise RuntimeError("TC_IDA_OUTPUT is required")
    ida_auto.auto_wait()
    func = ida_funcs.get_func(FUNCTION_EA)
    if func is None:
        raise RuntimeError("cannot resolve add_circuit_code")
    switches = []
    for ea in idautils.Heads(func.start_ea, func.end_ea):
        if not ida_bytes.is_code(ida_bytes.get_flags(ea)):
            continue
        info = ida_nalt.get_switch_info(ea)
        if info is None:
            continue
        result = ida_xref.calc_switch_cases(ea, info)
        rows = []
        if result is not None:
            for index in range(len(result.cases)):
                cases = [int(result.cases[index][i]) for i in range(len(result.cases[index]))]
                rows.append(
                    {
                        "cases": cases,
                        "target": f"0x{int(result.targets[index]):016x}",
                    }
                )
        switches.append(
            {
                "address": f"0x{ea:016x}",
                "instruction": idc.generate_disasm_line(ea, 0),
                "ncases": int(info.ncases),
                "jtable_size": int(info.get_jtable_size()),
                "lowcase": int(info.get_lowcase()),
                "default": f"0x{int(info.defjump):016x}",
                "rows": rows,
            }
        )
    with open(OUTPUT, "w", encoding="utf-8") as handle:
        json.dump(
            {
                "schema": 1,
                "function": idc.get_func_name(func.start_ea),
                "function_address": f"0x{func.start_ea:016x}",
                "function_end": f"0x{func.end_ea:016x}",
                "switches": switches,
            },
            handle,
            ensure_ascii=False,
            indent=2,
        )
        handle.write("\n")
    idc.qexit(0)


try:
    main()
except Exception as exc:
    print(f"CODEGEN_SWITCH_ERROR: {type(exc).__name__}: {exc}")
    idc.qexit(1)
