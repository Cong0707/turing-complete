"""Read-only IDA export for native tristate bus and RAM-load helpers."""

from pathlib import Path

import ida_auto
import ida_funcs
import ida_hexrays
import ida_kernwin
import ida_lines
import idautils
import idc


OUT = Path(r"D:\Develop\Other\turing-complete\.research\rng_tristate_bus\native")
TARGETS = {
    "input_static": 0x140433BA5,
    "store_output": 0x140437079,
    "input_dynamic": 0x14043DE0D,
    "add_circuit_code": 0x140441388,
}


def decompile(address: int) -> str:
    function = ida_funcs.get_func(address)
    if function is None:
        return f"no function at {address:#x}\n"
    cfunc = ida_hexrays.decompile(function)
    if cfunc is None:
        return f"decompile returned None at {address:#x}\n"
    return "\n".join(
        ida_lines.tag_remove(line.line) for line in cfunc.get_pseudocode()
    ) + "\n"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    ida_auto.auto_wait()
    if not ida_hexrays.init_hexrays_plugin():
        raise RuntimeError("Hex-Rays unavailable")
    for label, address in TARGETS.items():
        (OUT / f"{label}.c").write_text(decompile(address), encoding="utf-8")
    rows = ["target\tcallsite\tcaller"]
    for label, target in TARGETS.items():
        for callsite in idautils.CodeRefsTo(target, False):
            caller = ida_funcs.get_func(callsite)
            rows.append(
                f"{label}\t{callsite:#x}\t"
                f"{ida_funcs.get_func_name(caller.start_ea) if caller else ''}"
            )
    (OUT / "xrefs.tsv").write_text("\n".join(rows) + "\n", encoding="utf-8")
    idc.qexit(0)


try:
    main()
except Exception as exc:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "error.txt").write_text(repr(exc), encoding="utf-8")
    ida_kernwin.warning(str(exc))
    idc.qexit(1)
