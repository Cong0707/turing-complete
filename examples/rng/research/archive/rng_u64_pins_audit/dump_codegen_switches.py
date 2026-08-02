"""Dump IDA-recognized switch tables in generate_source, including kind 98/100 targets."""

from __future__ import annotations

from pathlib import Path

import ida_auto
import ida_funcs
import ida_nalt
import ida_xref
import idc


OUTPUT = Path(
    r"D:\Develop\Other\turing-complete\.research\rng_u64_pins_audit\codegen_switches.txt"
)
GENERATE_SOURCE = 0x14048B0BD


def main() -> None:
    ida_auto.auto_wait()
    func = ida_funcs.get_func(GENERATE_SOURCE)
    if func is None:
        raise RuntimeError("generate_source function not found")
    rows: list[str] = []
    ea = func.start_ea
    while ea < func.end_ea:
        switch = ida_nalt.get_switch_info(ea)
        if switch is not None:
            rows.append(
                f"switch @ 0x{ea:016x}: ncases={switch.ncases} lowcase={switch.lowcase} "
                f"jumps=0x{switch.jumps:016x} defjump=0x{switch.defjump:016x} "
                f"flags=0x{switch.flags:x}"
            )
            cases = ida_xref.calc_switch_cases(ea, switch)
            if cases is not None:
                for values, target in zip(cases.cases, cases.targets):
                    rendered = ",".join(str(value) for value in values)
                    marker = " *" if 98 in values or 100 in values else ""
                    rows.append(f"  {rendered} -> 0x{target:016x}{marker}")
        ea = idc.next_head(ea, func.end_ea)
    OUTPUT.write_text("\n".join(rows) + "\n", encoding="utf-8")
    idc.qexit(0)


try:
    main()
except Exception as exc:
    print(f"DUMP_ERROR: {exc}")
    idc.qexit(1)
