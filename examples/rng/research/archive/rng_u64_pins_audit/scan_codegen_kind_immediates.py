"""Find native code-generation instructions that compare/dispatch kinds 98/100."""

from __future__ import annotations

from pathlib import Path

import ida_auto
import ida_funcs
import ida_ua
import idc


OUTPUT = Path(
    r"D:\Develop\Other\turing-complete\.research\rng_u64_pins_audit\codegen_kind_immediates.txt"
)
GENERATE_SOURCE = 0x14048B0BD
TARGET_VALUES = {98, 100}


def line(ea: int) -> str:
    return f"{ea:016x}  {idc.generate_disasm_line(ea, 0) or ''}"


def main() -> None:
    ida_auto.auto_wait()
    func = ida_funcs.get_func(GENERATE_SOURCE)
    if func is None:
        raise RuntimeError("generate_source function not found")
    hits: list[int] = []
    ea = func.start_ea
    while ea < func.end_ea:
        insn = ida_ua.insn_t()
        if ida_ua.decode_insn(insn, ea):
            values = {
                int(op.value)
                for op in insn.ops
                if op.type in (ida_ua.o_imm, ida_ua.o_displ, ida_ua.o_mem)
            }
            if values & TARGET_VALUES:
                hits.append(ea)
        ea = idc.next_head(ea, func.end_ea)

    rows = [
        f"generate_source=0x{func.start_ea:016x}-0x{func.end_ea:016x}",
        f"hit_count={len(hits)}",
    ]
    for hit in hits:
        start = hit
        for _ in range(16):
            previous = idc.prev_head(start, func.start_ea)
            if previous == idc.BADADDR:
                break
            start = previous
        rows.append(f"\n=== hit 0x{hit:016x} ===")
        ea = start
        for _ in range(40):
            if ea == idc.BADADDR or ea >= func.end_ea:
                break
            rows.append(("> " if ea == hit else "  ") + line(ea))
            ea = idc.next_head(ea, func.end_ea)
    OUTPUT.write_text("\n".join(rows) + "\n", encoding="utf-8")
    idc.qexit(0)


try:
    main()
except Exception as exc:
    print(f"SCAN_ERROR: {exc}")
    idc.qexit(1)
