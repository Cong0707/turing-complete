"""Dump the native connect_to_ram function for static ordering audit."""

from __future__ import annotations

from pathlib import Path

import ida_auto
import ida_bytes
import ida_lines
import idautils
import idc


OUT = Path(__file__).with_name("connect_to_ram_2babfd_2bcaa9.txt")
START = 0x1402BABFD
END = 0x1402BCAA9


def main() -> None:
    ida_auto.auto_wait()
    rows: list[str] = []
    ea = ida_bytes.next_head(START - 1, END)
    while ea != idc.BADADDR and ea < END:
        text = ida_lines.tag_remove(idc.generate_disasm_line(ea, 0) or "")
        refs = [f"{ref:#x} {idc.get_name(ref)}" for ref in idautils.DataRefsFrom(ea)]
        suffix = " ; refs: " + ", ".join(refs) if refs else ""
        rows.append(f"{ea:#x}  {text}{suffix}")
        ea = ida_bytes.next_head(ea, END)
    OUT.write_text("\n".join(rows) + "\n", encoding="utf-8")
    idc.qexit(0)


try:
    main()
except Exception as exc:
    OUT.with_suffix(".error.txt").write_text(repr(exc), encoding="utf-8")
    idc.qexit(1)
