"""Read-only Hex-Rays export for U64 maker/splitter width and rotation helpers."""

from __future__ import annotations

from pathlib import Path

import ida_auto
import ida_bytes
import ida_funcs
import ida_hexrays
import ida_name
import idaapi
import idc


OUTPUT = Path(
    r"D:\Develop\Other\turing-complete\.research\rng_u64_pins_audit\helpers.c"
)

TARGETS = {
    # COFF symbol values in exe-symbols.txt are section-relative; .text starts
    # at RVA 0x1000, hence the extra 0x1000 in these absolute IDB addresses.
    "rotate_point": 0x140186C29,
    "rotate_then_translate": 0x14018B5A7,
    "get_output_word_size": 0x1402367C6,
    "get_clamped_word_size": 0x140236B33,
    "proto_word_size": 0x1402378B1,
}


def disassembly(start: int, end: int) -> str:
    rows: list[str] = []
    ea = start
    while ea < end:
        rows.append(f"{ea:016x}  {idc.generate_disasm_line(ea, 0) or ''}")
        ea = idc.next_head(ea, end)
    return "\n".join(rows)


def main() -> None:
    ida_auto.auto_wait()
    ida_hexrays.init_hexrays_plugin()
    chunks: list[str] = []
    for label, requested_ea in TARGETS.items():
        func = ida_funcs.get_func(requested_ea)
        if func is None:
            chunks.append(f"/* {label}: no function at 0x{requested_ea:x} */")
            continue
        name = ida_name.get_name(func.start_ea)
        chunks.append(
            f"/* {label}: {name} @ 0x{func.start_ea:016x}-0x{func.end_ea:016x} */"
        )
        try:
            chunks.append(str(ida_hexrays.decompile(func.start_ea)))
        except Exception as exc:
            chunks.append(f"/* decompile failed: {exc!r}\n{disassembly(func.start_ea, func.end_ea)}\n*/")
    OUTPUT.write_text("\n\n".join(chunks) + "\n", encoding="utf-8")
    idc.qexit(0)


try:
    main()
except Exception as exc:
    print(f"DECOMPILE_ERROR: {exc}")
    idc.qexit(1)
