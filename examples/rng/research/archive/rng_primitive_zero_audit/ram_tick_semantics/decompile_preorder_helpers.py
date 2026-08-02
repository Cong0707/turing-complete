"""Export the small preorder helpers used to prove component emission order."""

from __future__ import annotations

from pathlib import Path

import ida_auto
import ida_funcs
import ida_hexrays
import ida_kernwin
import ida_lines
import idc


OUT = Path(
    r"D:\Develop\Other\turing-complete\.research\rng_primitive_zero_audit"
    r"\ram_tick_semantics"
)

TARGETS = {
    "add_wire_pins": 0x1402B9EE2,
    "connect": 0x1402BCAA9,
    "is_ready": 0x1402BD1A4,
    "input_size": 0x1402BDEB9,
    "preorder_pop": 0x1402BD791,
    "preorder_add": 0x14003CB4A,
    "preorder_sort": 0x140098543,
    "seq_concat": 0x14003FE94,
}


def decompile_one(label: str, address: int) -> str:
    fn = ida_funcs.get_func(address)
    if fn is None:
        return f"no function at {address:#x}\n"
    pseudocode = ida_hexrays.decompile(fn)
    if pseudocode is None:
        return f"decompile returned None for {label} at {address:#x}\n"
    return "\n".join(
        ida_lines.tag_remove(line.line) for line in pseudocode.get_pseudocode()
    ) + "\n"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    ida_auto.auto_wait()
    if not ida_hexrays.init_hexrays_plugin():
        raise RuntimeError("Hex-Rays decompiler is unavailable")
    for label, address in TARGETS.items():
        (OUT / f"{label}.c").write_text(
            decompile_one(label, address), encoding="utf-8"
        )
    idc.qexit(0)


try:
    main()
except Exception as exc:
    (OUT / "decompile_preorder_helpers.error.txt").write_text(
        repr(exc), encoding="utf-8"
    )
    ida_kernwin.warning(str(exc))
    idc.qexit(1)
