"""Export the complete RAM-save code-generation branch with literal payloads."""

from __future__ import annotations

from pathlib import Path

import ida_auto
import ida_bytes
import ida_lines
import idautils
import idc


OUT = Path(__file__).with_name("ram_codegen_save_branch_452700_456b00.txt")
START = 0x140452700
END = 0x140456B00


def clean(ea: int) -> str:
    return ida_lines.tag_remove(idc.generate_disasm_line(ea, 0) or "")


def describe_ref(ref: int) -> str:
    facts = [f"{ref:#x} {idc.get_name(ref)}"]
    raw = idc.get_strlit_contents(ref, -1, idc.STRTYPE_C)
    if raw is not None:
        facts.append(f"direct={bytes(raw).decode('utf-8', 'backslashreplace')!r}")
    value = ida_bytes.get_qword(ref)
    facts.append(f"qword={value:#x}")
    payload = idc.get_strlit_contents(value + 8, -1, idc.STRTYPE_C)
    if payload is not None:
        facts.append(f"payload={bytes(payload).decode('utf-8', 'backslashreplace')!r}")
    return " ".join(facts)


def main() -> None:
    ida_auto.auto_wait()
    rows = []
    ea = ida_bytes.next_head(START - 1, END)
    while ea != idc.BADADDR and ea < END:
        refs = [describe_ref(ref) for ref in idautils.DataRefsFrom(ea)]
        suffix = " ; refs: " + ", ".join(refs) if refs else ""
        rows.append(f"{ea:#x}  {clean(ea)}{suffix}")
        ea = ida_bytes.next_head(ea, END)
    OUT.write_text("\n".join(rows) + "\n", encoding="utf-8")
    idc.qexit(0)


try:
    main()
except Exception as exc:
    OUT.with_suffix(".error.txt").write_text(repr(exc), encoding="utf-8")
    idc.qexit(1)
