"""Export lightweight native xrefs around the Delay Bit helper path.

Run this script in IDA batch mode against the analysed v2.1.281 database.  It
does not decompile the large component dispatcher; it only records nearby
instructions for references to the two helpers and the literal "1".
"""

from __future__ import annotations

import json
from pathlib import Path

import ida_auto
import ida_funcs
import ida_lines
import ida_name
import idaapi
import idautils
import idc


OUT = Path(
    r"D:\Develop\Other\turing-complete\.research\rng_sample_dfa"
    r"\delay-native-audit\xrefs.json"
)

SYMBOLS = {
    "load_and_output": "load_and_output__modelZsimulationZcode95gen_u3940",
    "store_bit": "store_bit__modelZsimulationZcode95gen_u2179",
    "literal_one": "TM__THWBxVSaWN2Zh7OMooFH0w_934",
}


def instruction_window(address: int, before: int = 14, after: int = 14) -> list[dict[str, str]]:
    heads = [address]
    cursor = address
    for _ in range(before):
        cursor = idc.prev_head(cursor)
        if cursor == idaapi.BADADDR:
            break
        heads.append(cursor)
    heads.reverse()
    cursor = address
    for _ in range(after):
        cursor = idc.next_head(cursor)
        if cursor == idaapi.BADADDR:
            break
        heads.append(cursor)
    return [
        {
            "address": f"0x{head:016x}",
            "text": ida_lines.tag_remove(idc.generate_disasm_line(head, 0) or ""),
        }
        for head in heads
    ]


def xrefs(address: int) -> list[dict[str, object]]:
    rows = []
    for xref in idautils.XrefsTo(address, 0):
        function = ida_funcs.get_func(xref.frm)
        rows.append(
            {
                "from": f"0x{xref.frm:016x}",
                "type": int(xref.type),
                "function_start": (
                    f"0x{function.start_ea:016x}" if function is not None else None
                ),
                "function_name": (
                    ida_funcs.get_func_name(function.start_ea)
                    if function is not None
                    else None
                ),
                "window": instruction_window(xref.frm),
            }
        )
    return rows


def main() -> None:
    ida_auto.auto_wait()
    result: dict[str, object] = {
        "schema": 1,
        "input_file": idc.get_input_file_path(),
        "image_base": f"0x{idaapi.get_imagebase():016x}",
        "symbols": {},
    }
    for label, name in SYMBOLS.items():
        address = ida_name.get_name_ea(idaapi.BADADDR, name)
        if address == idaapi.BADADDR:
            raise RuntimeError(f"missing symbol {name}")
        result["symbols"][label] = {
            "name": name,
            "address": f"0x{address:016x}",
            "xrefs": xrefs(address),
        }
    OUT.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    idc.qexit(0)


try:
    main()
except Exception as exc:
    OUT.with_name("xrefs-error.txt").write_text(repr(exc) + "\n", encoding="utf-8")
    idc.qexit(1)
