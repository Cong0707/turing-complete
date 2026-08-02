"""Find RAM-related Nim global strings and every code reference to them."""

from __future__ import annotations

from pathlib import Path

import ida_auto
import ida_bytes
import ida_funcs
import ida_lines
import idautils
import idc


OUT = Path(
    r"D:\Develop\Other\turing-complete\.research\rng_primitive_zero_audit"
    r"\ram_tick_semantics"
)
NEEDLES = (
    "#DATA_",
    "#SIMULATION_STATE",
    "Output cache",
    "tick_p2_",
    "load(<U",
    "store(",
    "memory_clear",
)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    ida_auto.auto_wait()
    rows: list[str] = []
    for ea, name in idautils.Names():
        if not name.startswith("TM__"):
            continue
        length = ida_bytes.get_qword(ea)
        ptr = ida_bytes.get_qword(ea + 8)
        if not (0 < length < 4096):
            continue
        raw = ida_bytes.get_bytes(ptr + 8, length)
        if raw is None:
            continue
        text = raw.decode("utf-8", "backslashreplace")
        if not any(needle in text for needle in NEEDLES):
            continue
        refs = sorted(set(idautils.DataRefsTo(ea)) | set(idautils.DataRefsTo(ea + 8)))
        if refs:
            for ref in refs:
                fn = ida_funcs.get_func(ref)
                fn_name = ida_funcs.get_func_name(fn.start_ea) if fn else ""
                disasm = ida_lines.tag_remove(idc.generate_disasm_line(ref, 0) or "")
                rows.append(
                    f"{ea:#x}\t{name}\t{text!r}\t{ref:#x}\t"
                    f"{fn.start_ea:#x} {fn_name}\t{disasm}" if fn else
                    f"{ea:#x}\t{name}\t{text!r}\t{ref:#x}\t\t{disasm}"
                )
        else:
            rows.append(f"{ea:#x}\t{name}\t{text!r}\t\t\t")
    (OUT / "ram_codegen_literals.tsv").write_text(
        "literal_ea\tname\ttext\tref\tfunction\tdisasm\n" + "\n".join(rows) + "\n",
        encoding="utf-8",
    )
    idc.qexit(0)


try:
    main()
except Exception as exc:
    (OUT / "find_codegen_literals.error.txt").write_text(repr(exc), encoding="utf-8")
    idc.qexit(1)
