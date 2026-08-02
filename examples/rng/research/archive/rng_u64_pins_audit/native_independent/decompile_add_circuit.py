"""Export the current native add_circuit_code pseudocode for focused auditing."""

from __future__ import annotations

from pathlib import Path

import ida_auto
import ida_funcs
import ida_hexrays
import ida_name
import idc


OUT = Path(
    r"D:\Develop\Other\turing-complete\.research\rng_u64_pins_audit"
    r"\native_independent\add_circuit_code.c"
)
EA = 0x140441388


def main() -> None:
    ida_auto.auto_wait()
    if not ida_hexrays.init_hexrays_plugin():
        raise RuntimeError("Hex-Rays unavailable")
    func = ida_funcs.get_func(EA)
    if func is None:
        raise RuntimeError(f"no function at 0x{EA:x}")
    cfunc = ida_hexrays.decompile(func.start_ea)
    header = (
        f"/* {ida_name.get_name(func.start_ea)} "
        f"@ 0x{func.start_ea:016x}-0x{func.end_ea:016x} */\n"
    )
    OUT.write_text(header + str(cfunc) + "\n", encoding="utf-8")
    idc.qexit(0)


try:
    main()
except Exception as exc:
    print(f"DECOMPILE_ADD_CIRCUIT_ERROR: {exc!r}")
    idc.qexit(1)
