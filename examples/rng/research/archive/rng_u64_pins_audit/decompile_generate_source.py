"""Export the current native source generator for focused template analysis."""

from __future__ import annotations

from pathlib import Path

import ida_auto
import ida_hexrays
import ida_lines
import idc


OUTPUT = Path(
    r"D:\Develop\Other\turing-complete\.research\rng_u64_pins_audit\generate_source.c"
)
GENERATE_SOURCE = 0x14048B0BD


def main() -> None:
    ida_auto.auto_wait()
    if not ida_hexrays.init_hexrays_plugin():
        raise RuntimeError("Hex-Rays unavailable")
    code = ida_hexrays.decompile(GENERATE_SOURCE)
    if code is None:
        raise RuntimeError("decompilation failed")
    lines = [ida_lines.tag_remove(line.line) for line in code.get_pseudocode()]
    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    idc.qexit(0)


try:
    main()
except Exception as exc:
    print(f"DECOMPILE_ERROR: {exc}")
    idc.qexit(1)
