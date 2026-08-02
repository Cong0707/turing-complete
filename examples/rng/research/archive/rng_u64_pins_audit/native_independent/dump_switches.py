"""Dump all IDA-recognized switches in the current generate_source function."""

from __future__ import annotations

from pathlib import Path

import ida_auto
import ida_funcs
import ida_nalt
import ida_xref
import idc


OUT = Path(
    r"D:\Develop\Other\turing-complete\.research\rng_u64_pins_audit"
    r"\native_independent\switches.txt"
)
GENERATE_SOURCE = 0x14048B0BD


def main() -> None:
    ida_auto.auto_wait()
    func = ida_funcs.get_func(GENERATE_SOURCE)
    if func is None:
        raise RuntimeError(f"no function at 0x{GENERATE_SOURCE:x}")

    rows = [f"generate_source=0x{func.start_ea:016x}-0x{func.end_ea:016x}"]
    ea = func.start_ea
    count = 0
    while ea < func.end_ea:
        si = ida_nalt.get_switch_info(ea)
        if si is not None:
            count += 1
            rows.append(
                f"switch @ 0x{ea:016x}: ncases={si.ncases} "
                f"lowcase={si.lowcase} jumps=0x{si.jumps:016x} "
                f"defjump=0x{si.defjump:016x} flags=0x{si.flags:x}"
            )
            cases = ida_xref.calc_switch_cases(ea, si)
            if cases is None:
                rows.append("  <calc_switch_cases failed>")
            else:
                for values, target in zip(cases.cases, cases.targets):
                    vals = [int(value) for value in values]
                    marker = " *" if 98 in vals or 100 in vals else ""
                    rows.append(
                        f"  {','.join(map(str, vals))} -> 0x{target:016x}{marker}"
                    )
        ea = idc.next_head(ea, func.end_ea)
    rows.insert(1, f"switch_count={count}")
    OUT.write_text("\n".join(rows) + "\n", encoding="utf-8")
    idc.qexit(0)


try:
    main()
except Exception as exc:
    print(f"DUMP_SWITCHES_ERROR: {exc!r}")
    idc.qexit(1)
