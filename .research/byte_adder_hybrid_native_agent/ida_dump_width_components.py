"""Export native prototypes needed to materialize mixed-width adders."""

from __future__ import annotations

import json
import os
from pathlib import Path

import ida_auto
import ida_bytes
import ida_nalt
import ida_name
import idaapi
import idc


OUT = Path(os.environ.get(
    "BYTE_ADDER_WIDTH_PROTOTYPES_OUT",
    r"D:\Develop\Other\turing-complete\.research\byte_adder_hybrid_native_agent"
    r"\width_component_prototypes.json",
))
TABLE_NAME = "TM__wUqL1Kpuf69c1ieeyVFJbBQ_3391"
SELECTED = {16, 17, 30, 47, 48, 78, 79, 81, 97, 98, 99, 100, 101, 102,
            103, 109, 110, 111, 112, 113, 114, 115, 116}
SLOT_STRIDE = 1464
KEY_OFFSET = 16
VALUE_OFFSET = 24
PIN_SIZE = 56


def qword(ea: int) -> int:
    return ida_bytes.get_qword(ea)


def mapped(ea: int, size: int = 1) -> bool:
    return ea != idaapi.BADADDR and all(ida_bytes.is_loaded(ea + i) for i in range(size))


def text_at(pointer: int, length: int) -> str | None:
    if not (0 < length <= 256 and mapped(pointer + 8, length)):
        return None
    raw = ida_bytes.get_bytes(pointer + 8, length)
    if raw is None:
        return None
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return None


def signed16(ea: int) -> int:
    value = ida_bytes.get_word(ea)
    return value - 0x10000 if value & 0x8000 else value


def pins(record: int, offset: int) -> list[dict[str, object]]:
    length, pointer = qword(record + offset), qword(record + offset + 8)
    if not (0 <= length <= 32 and mapped(pointer)):
        return []
    result = []
    for index in range(length):
        pin = pointer + 8 + PIN_SIZE * index
        labels = []
        for label_offset in range(0, 48, 8):
            value = text_at(qword(pin + label_offset + 8), qword(pin + label_offset))
            if value:
                labels.append(value)
        result.append({
            "direction_code": ida_bytes.get_word(pin),
            "offset": [signed16(pin + 2), signed16(pin + 4)],
            "word_size_token": qword(pin + 8),
            "labels": labels,
            "raw_hex": ida_bytes.get_bytes(pin, PIN_SIZE).hex(),
        })
    return result


def main() -> None:
    ida_auto.auto_wait()
    table = ida_name.get_name_ea(idaapi.BADADDR, TABLE_NAME)
    records = {}
    for slot in range(256):
        base = table + SLOT_STRIDE * slot
        kind = ida_bytes.get_byte(base + KEY_OFFSET)
        if kind not in SELECTED:
            continue
        record = base + VALUE_OFFSET
        records[str(kind)] = {
            "slot": slot,
            "name": text_at(qword(record + 24), qword(record + 16)),
            "inputs": pins(record, 96),
            "bidirectional": pins(record, 112),
            "outputs": pins(record, 128),
        }
    digest = ida_nalt.retrieve_input_file_sha256()
    OUT.write_text(json.dumps({
        "input_sha256": digest.hex() if digest else None,
        "records": records,
        "missing": sorted(SELECTED - {int(x) for x in records}),
    }, indent=2, ensure_ascii=True) + "\n", encoding="ascii")
    idc.qexit(0)


try:
    main()
except Exception as exc:
    print(f"DUMP_ERROR: {type(exc).__name__}: {exc}")
    idc.qexit(1)
