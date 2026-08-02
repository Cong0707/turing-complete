"""Export focused static evidence for RAM code generation.

Run inside IDA against the existing Turing Complete database.  This script
does not execute the target program or modify target bytes.
"""

from __future__ import annotations

from pathlib import Path

import ida_auto
import ida_bytes
import ida_funcs
import ida_gdl
import ida_lines
import ida_nalt
import ida_segment
import ida_xref
import idautils
import idc


OUT = Path(
    r"D:\Develop\Other\turing-complete\.research\rng_primitive_zero_audit"
    r"\ram_tick_semantics"
)

TARGETS = {
    "get_ram_pipeline_depth": 0x14021A94F,
    "load_memory_word": 0x140434586,
    "store_bit": 0x14043DD1A,
    "store_word": 0x14043E4C0,
    "load_and_output": 0x14043CF90,
}


def clean_disasm(ea: int) -> str:
    return ida_lines.tag_remove(idc.generate_disasm_line(ea, 0) or "")


def source_loc(ea: int) -> str:
    path = ida_lines.get_sourcefile(ea) or ""
    line = ida_nalt.get_source_linnum(ea)
    return f"{path}:{line}" if path else ""


def containing_block(ea: int) -> tuple[int, int]:
    fn = ida_funcs.get_func(ea)
    if fn is None:
        return ea, ea + ida_bytes.get_item_size(ea)
    for block in ida_gdl.FlowChart(fn):
        if block.start_ea <= ea < block.end_ea:
            return block.start_ea, block.end_ea
    return ea, ea + ida_bytes.get_item_size(ea)


def dump_window(ea: int, before: int = 35, after: int = 45) -> list[str]:
    fn = ida_funcs.get_func(ea)
    lo = fn.start_ea if fn else ida_segment.getseg(ea).start_ea
    hi = fn.end_ea if fn else ida_segment.getseg(ea).end_ea
    start = ea
    for _ in range(before):
        prev = ida_bytes.prev_head(start, lo)
        if prev == idc.BADADDR or prev >= start:
            break
        start = prev
    lines: list[str] = []
    cur = start
    remaining = before + after + 1
    while cur != idc.BADADDR and cur < hi and remaining:
        mark = ">>" if cur == ea else "  "
        loc = source_loc(cur)
        suffix = f" ; {loc}" if loc else ""
        lines.append(f"{mark} {cur:#x}  {clean_disasm(cur)}{suffix}")
        cur = ida_bytes.next_head(cur, hi)
        remaining -= 1
    return lines


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    ida_auto.auto_wait()
    chunks: list[str] = []
    rows: list[str] = ["target\tcallee\tcallsite\tfunction\tblock_start\tblock_end\tsource"]
    for label, target in TARGETS.items():
        chunks.append(f"## {label} @ {target:#x}\n")
        for callsite in idautils.CodeRefsTo(target, False):
            fn = ida_funcs.get_func(callsite)
            fn_name = ida_funcs.get_func_name(fn.start_ea) if fn else ""
            block_start, block_end = containing_block(callsite)
            rows.append(
                "\t".join(
                    [
                        label,
                        f"{target:#x}",
                        f"{callsite:#x}",
                        f"{fn.start_ea:#x} {fn_name}" if fn else "",
                        f"{block_start:#x}",
                        f"{block_end:#x}",
                        source_loc(callsite),
                    ]
                )
            )
            chunks.append(
                f"### xref {callsite:#x} in "
                f"{fn.start_ea:#x} {fn_name}\n"
                f"block=[{block_start:#x},{block_end:#x}) "
                f"source={source_loc(callsite)}\n"
            )
            chunks.extend(dump_window(callsite))
            chunks.append("")
    (OUT / "ram_helper_xrefs.tsv").write_text("\n".join(rows) + "\n", encoding="utf-8")
    (OUT / "ram_helper_windows.txt").write_text("\n".join(chunks) + "\n", encoding="utf-8")
    idc.qexit(0)


try:
    main()
except Exception as exc:
    (OUT / "trace_ram_codegen.error.txt").write_text(repr(exc), encoding="utf-8")
    idc.qexit(1)
