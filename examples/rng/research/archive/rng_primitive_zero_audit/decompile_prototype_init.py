"""Export the native component prototype registry initializer from the game IDB."""

from pathlib import Path

import ida_auto
import ida_funcs
import ida_hexrays
import ida_idp
import ida_kernwin
import ida_lines
import idc


ADDRESS = 0x140237BFF
OUTPUT = Path(
    r"D:\Develop\Other\turing-complete\.research\rng_primitive_zero_audit\prototype_init.c"
)


def main() -> None:
    ida_auto.auto_wait()
    if not ida_hexrays.init_hexrays_plugin():
        raise RuntimeError("Hex-Rays decompiler is unavailable")
    ida_idp.process_config_directive("MAX_FUNCSIZE = 1024")

    function = ida_funcs.get_func(ADDRESS)
    if function is None:
        raise RuntimeError(f"no function containing {ADDRESS:#x}")
    print(
        f"PROTOTYPE_INIT_RANGE {function.start_ea:#x}..{function.end_ea:#x} "
        f"({function.end_ea - function.start_ea:#x} bytes)"
    )
    pseudocode = ida_hexrays.decompile(function)
    if pseudocode is None:
        raise RuntimeError(f"failed to decompile prototype initializer at {ADDRESS:#x}")
    lines = [ida_lines.tag_remove(line.line) for line in pseudocode.get_pseudocode()]
    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    idc.qexit(0)


try:
    main()
except Exception as exc:
    print(f"DECOMPILE_ERROR: {exc}")
    ida_kernwin.warning(str(exc))
    idc.qexit(1)
