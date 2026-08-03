"""只读定位 campaign 关卡记录关键字段偏移的所有代码访问。"""

from __future__ import annotations

import json
from pathlib import Path

import ida_auto
import ida_funcs
import ida_lines
import ida_name
import ida_ua
import idaapi
import idautils


OUTPUT = Path(
    r"D:\Develop\Other\turing-complete\.research\byte_adder_protocol_audit_agent\ida_campaign_field_offsets.json"
)

OFFSETS = (280, 288, 320, 360, 368, 384, 392)


def main() -> None:
    ida_auto.auto_wait()
    records: dict[str, list[dict[str, str]]] = {str(offset): [] for offset in OFFSETS}
    for function_ea in idautils.Functions():
        function = ida_funcs.get_func(function_ea)
        if function is None:
            continue
        function_name = ida_name.get_name(function.start_ea)
        for ea in idautils.FuncItems(function.start_ea):
            instruction = ida_ua.insn_t()
            if not ida_ua.decode_insn(instruction, ea):
                continue
            rendered = ida_lines.generate_disasm_line(ea, 0) or ""
            rendered = ida_lines.tag_remove(rendered)
            for operand in instruction.ops:
                if operand.type == ida_ua.o_void:
                    break
                if operand.type not in (ida_ua.o_displ, ida_ua.o_imm):
                    continue
                value = int(operand.addr if operand.type == ida_ua.o_displ else operand.value)
                if value not in OFFSETS:
                    continue
                records[str(value)].append(
                    {
                        "address": f"0x{ea:016x}",
                        "function": function_name,
                        "instruction": rendered,
                    }
                )
    OUTPUT.write_text(
        json.dumps(records, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    idaapi.qexit(0)


main()
