"""Export the native critical-path helper for the RNG score audit."""

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
    r"\ram_tick_semantics\native_score_check"
)
TARGETS = {
    "is_critical": 0x1402C720D,
    "set_critical_path": 0x1402C76B5,
}


def decompile_one(label: str, address: int) -> str:
    function = ida_funcs.get_func(address)
    if function is None:
        raise RuntimeError(f"no function containing {address:#x}")
    pseudocode = ida_hexrays.decompile(function)
    if pseudocode is None:
        raise RuntimeError(f"failed to decompile {label} at {address:#x}")
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
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "decompile_native_score.error.txt").write_text(
        repr(exc), encoding="utf-8"
    )
    ida_kernwin.warning(str(exc))
    idc.qexit(1)
