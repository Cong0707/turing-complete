"""Find native uses of component-kind immediates 98 and 100 in add_circuit_code."""

from __future__ import annotations

from pathlib import Path

import ida_auto
import ida_funcs
import ida_ua
import idc


OUT = Path(
    r"D:\Develop\Other\turing-complete\.research\rng_u64_pins_audit"
    r"\native_independent\add_circuit_kind_immediates.txt"
)
ADD_CIRCUIT_CODE = 0x140441388
KINDS = {98, 100}


def line(ea: int) -> str:
    return f"{ea:016x}  {idc.generate_disasm_line(ea, 0) or ''}"


def main() -> None:
    ida_auto.auto_wait()
    func = ida_funcs.get_func(ADD_CIRCUIT_CODE)
    if func is None:
        raise RuntimeError(f"no function at 0x{ADD_CIRCUIT_CODE:x}")
    hits = []
    ea = func.start_ea
    while ea < func.end_ea:
        insn = ida_ua.insn_t()
        if ida_ua.decode_insn(insn, ea):
            immediates = {
                int(op.value)
                for op in insn.ops
                if op.type == ida_ua.o_imm and int(op.value) in KINDS
            }
            if immediates:
                hits.append((ea, sorted(immediates)))
        ea = idc.next_head(ea, func.end_ea)

    rows = [
        f"add_circuit_code=0x{func.start_ea:016x}-0x{func.end_ea:016x}",
        f"hit_count={len(hits)}",
    ]
    for hit, values in hits:
        rows.append(f"\n=== hit 0x{hit:016x} values={values} ===")
        window = []
        cur = hit
        for _ in range(20):
            prev = idc.prev_head(cur, func.start_ea)
            if prev == idc.BADADDR or prev >= cur:
                break
            window.append(prev)
            cur = prev
        for cur in reversed(window):
            rows.append("  " + line(cur))
        rows.append("> " + line(hit))
        cur = hit
        for _ in range(30):
            cur = idc.next_head(cur, func.end_ea)
            if cur == idc.BADADDR or cur >= func.end_ea:
                break
            rows.append("  " + line(cur))
    OUT.write_text("\n".join(rows) + "\n", encoding="utf-8")
    idc.qexit(0)


try:
    main()
except Exception as exc:
    print(f"SCAN_ERROR: {exc!r}")
    idc.qexit(1)
