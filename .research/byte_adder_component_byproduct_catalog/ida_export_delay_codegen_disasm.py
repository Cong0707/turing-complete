"""Export the current machine-code window that emits Delay Line code."""

from __future__ import annotations

import hashlib
import json
import os

import ida_auto
import ida_bytes
import ida_funcs
import ida_gdl
import ida_lines
import idaapi
import idautils
import idc


OUTPUT = os.environ.get("TC_IDA_OUTPUT")
FUNCTION_EA = 0x1404432F8
WINDOW_START = 0x14044C000
WINDOW_END = 0x14044CE50


def mapped(ea: int, size: int = 1) -> bool:
    return ea != idaapi.BADADDR and all(ida_bytes.is_loaded(ea + i) for i in range(size))


def static_text_pair(ea: int) -> str | None:
    """Decode a Nim (length, payload-object pointer) pair used by appendString."""
    if idc.print_insn_mnem(ea) != "mov":
        return None
    length_address = idc.get_operand_value(ea, 1)
    next_ea = idc.next_head(ea, WINDOW_END)
    if next_ea == idc.BADADDR or idc.print_insn_mnem(next_ea) != "mov":
        return None
    pointer_address = idc.get_operand_value(next_ea, 1)
    if not (mapped(length_address, 8) and mapped(pointer_address, 8)):
        return None
    length = ida_bytes.get_qword(length_address)
    pointer = ida_bytes.get_qword(pointer_address)
    if not (0 < length <= 4096 and mapped(pointer + 8, length)):
        return None
    raw = ida_bytes.get_bytes(pointer + 8, length)
    if raw is None:
        return None
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return None


def main() -> None:
    if not OUTPUT:
        raise RuntimeError("TC_IDA_OUTPUT is required")
    ida_auto.auto_wait()
    func = ida_funcs.get_func(FUNCTION_EA)
    if func is None:
        raise RuntimeError("cannot resolve add_circuit_code")
    instructions = []
    for ea in idautils.Heads(WINDOW_START, WINDOW_END):
        if not ida_bytes.is_code(ida_bytes.get_flags(ea)):
            continue
        size = idc.get_item_size(ea)
        raw = ida_bytes.get_bytes(ea, size) or b""
        instructions.append(
            {
                "address": f"0x{ea:016x}",
                "bytes": raw.hex(),
                "text": ida_lines.tag_remove(idc.generate_disasm_line(ea, 0) or ""),
                "static_text_pair": static_text_pair(ea),
            }
        )
    blocks = []
    for block in ida_gdl.FlowChart(func):
        if block.end_ea <= WINDOW_START or block.start_ea >= WINDOW_END:
            continue
        blocks.append(
            {
                "start": f"0x{block.start_ea:016x}",
                "end": f"0x{block.end_ea:016x}",
                "predecessors": [f"0x{pred.start_ea:016x}" for pred in block.preds()],
                "successors": [f"0x{succ.start_ea:016x}" for succ in block.succs()],
            }
        )
    raw_window = ida_bytes.get_bytes(WINDOW_START, WINDOW_END - WINDOW_START) or b""
    with open(OUTPUT, "w", encoding="utf-8") as handle:
        json.dump(
            {
                "schema": 1,
                "function": idc.get_func_name(FUNCTION_EA),
                "function_address": f"0x{func.start_ea:016x}",
                "window_start": f"0x{WINDOW_START:016x}",
                "window_end": f"0x{WINDOW_END:016x}",
                "window_machine_sha256": hashlib.sha256(raw_window).hexdigest(),
                "instructions": instructions,
                "blocks": blocks,
            },
            handle,
            ensure_ascii=False,
            indent=2,
        )
        handle.write("\n")
    idc.qexit(0)


try:
    main()
except Exception as exc:
    print(f"DELAY_DISASM_ERROR: {type(exc).__name__}: {exc}")
    idc.qexit(1)
