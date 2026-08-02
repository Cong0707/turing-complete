"""Export direct callers of native word-width helpers from the existing IDB."""

from __future__ import annotations

from pathlib import Path

import ida_auto
import ida_funcs
import ida_hexrays
import ida_name
import idautils
import idc


OUTPUT = Path(
    r"D:\Develop\Other\turing-complete\.research\rng_u64_pins_audit\width_callers.c"
)

TARGETS = {
    "get_output_word_size": 0x1402367C6,
    "get_clamped_word_size": 0x140236B33,
    "proto_word_size": 0x1402378B1,
}


def main() -> None:
    ida_auto.auto_wait()
    ida_hexrays.init_hexrays_plugin()
    chunks: list[str] = []
    seen: set[int] = set()
    for target_name, target in TARGETS.items():
        chunks.append(f"/* XREFS TO {target_name} @ 0x{target:016x} */")
        for xref in idautils.XrefsTo(target, 0):
            caller = ida_funcs.get_func(xref.frm)
            if caller is None:
                chunks.append(f"/* data/non-function xref from 0x{xref.frm:016x} */")
                continue
            chunks.append(
                f"/* call 0x{xref.frm:016x}, caller {ida_name.get_name(caller.start_ea)} "
                f"@ 0x{caller.start_ea:016x} */"
            )
            if caller.start_ea in seen:
                continue
            seen.add(caller.start_ea)
            try:
                chunks.append(str(ida_hexrays.decompile(caller.start_ea)))
            except Exception as exc:
                chunks.append(f"/* decompile failed: {exc!r} */")
    OUTPUT.write_text("\n\n".join(chunks) + "\n", encoding="utf-8")
    idc.qexit(0)


try:
    main()
except Exception as exc:
    print(f"DECOMPILE_ERROR: {exc}")
    idc.qexit(1)
