"""Dump the isolated RAM branch of add_circuit_code with string operands."""

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
RANGES = (
    (0x14044EE00, 0x140452700, "ram_codegen_load_region_44ee00_452700.txt"),
    (0x140455000, 0x140456800, "ram_codegen_save_region_455000_456800.txt"),
)


def clean(ea: int) -> str:
    return ida_lines.tag_remove(idc.generate_disasm_line(ea, 0) or "")


def quote_data_ref(ref: int) -> str:
    raw = idc.get_strlit_contents(ref, -1, idc.STRTYPE_C)
    facts: list[str] = [f"{ref:#x} {idc.get_name(ref)}"]
    if raw is not None:
        if isinstance(raw, bytes):
            text = raw.decode("utf-8", "backslashreplace")
        else:
            text = str(raw)
        facts.append(f"direct={text!r}")
    value = ida_bytes.get_qword(ref)
    facts.append(f"qword={value:#x}")
    pointed = idc.get_strlit_contents(value, -1, idc.STRTYPE_C)
    if pointed is not None:
        if isinstance(pointed, bytes):
            text = pointed.decode("utf-8", "backslashreplace")
        else:
            text = str(pointed)
        facts.append(f"points={text!r}")
    payload = idc.get_strlit_contents(value + 8, -1, idc.STRTYPE_C)
    if payload is not None:
        if isinstance(payload, bytes):
            text = payload.decode("utf-8", "backslashreplace")
        else:
            text = str(payload)
        facts.append(f"payload={text!r}")
    return " ".join(facts)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    ida_auto.auto_wait()
    for start, end, filename in RANGES:
        rows: list[str] = []
        ea = ida_bytes.next_head(start - 1, end)
        while ea != idc.BADADDR and ea < end:
            refs = [quote_data_ref(ref) for ref in idautils.DataRefsFrom(ea)]
            refs = [ref for ref in refs if ref]
            suffix = " ; strings: " + ", ".join(refs) if refs else ""
            rows.append(f"{ea:#x}  {clean(ea)}{suffix}")
            ea = ida_bytes.next_head(ea, end)
        (OUT / filename).write_text("\n".join(rows) + "\n", encoding="utf-8")
    idc.qexit(0)


try:
    main()
except Exception as exc:
    (OUT / "dump_ram_codegen_region.error.txt").write_text(repr(exc), encoding="utf-8")
    idc.qexit(1)
