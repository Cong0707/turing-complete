"""Export Byte Adder-related native prototypes from the analyzed 2.1.281 IDB.

Run this script with IDA's ``idat64 -A -S...``.  It only reads the database and
writes a compact JSON certificate to ``BYTE_ADDER_PROTOTYPES_OUT``.
"""

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


OUTPUT = Path(
    os.environ.get(
        "BYTE_ADDER_PROTOTYPES_OUT",
        r"D:\Develop\Other\turing-complete\.research\byte_adder_component_costs_agent"
        r"\native_prototypes.json",
    )
)
TABLE_NAME = "TM__wUqL1Kpuf69c1ieeyVFJbBQ_3391"
SELECTED = {
    3,
    4,
    5,
    6,
    7,
    8,
    9,
    10,
    11,
    12,
    15,
    16,
    17,
    18,
    19,
    20,
    21,
    22,
    23,
    24,
    25,
    30,
    47,
    48,
    97,
    98,
    99,
    100,
    109,
    110,
    111,
    112,
    114,
    115,
    116,
}
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
        value = raw.decode("utf-8")
    except UnicodeDecodeError:
        return None
    return value if all(char.isprintable() or char in "\r\n\t" for char in value) else None


def signed16(ea: int) -> int:
    value = ida_bytes.get_word(ea)
    return value - 0x10000 if value & 0x8000 else value


def pin_record(pin: int) -> dict[str, object]:
    labels = []
    for offset in range(0, 48, 8):
        length = qword(pin + offset)
        pointer = qword(pin + offset + 8)
        value = text_at(pointer, length)
        if value is not None:
            labels.append({"offset": offset, "length": length, "text": value})
    direction_code = ida_bytes.get_word(pin)
    return {
        "direction_code": direction_code,
        "direction": {0: "input", 2: "output"}.get(direction_code, "other"),
        "offset": [signed16(pin + 2), signed16(pin + 4)],
        "word_size_token": qword(pin + 8),
        "labels": labels,
        "raw_hex": ida_bytes.get_bytes(pin, PIN_SIZE).hex(),
    }


def pin_sequence(record: int, offset: int) -> dict[str, object]:
    length = qword(record + offset)
    pointer = qword(record + offset + 8)
    pins = []
    if 0 <= length <= 32 and mapped(pointer):
        pins = [pin_record(pointer + 8 + PIN_SIZE * index) for index in range(length)]
    return {"length": length, "pins": pins}


def main() -> None:
    ida_auto.auto_wait()
    table = ida_name.get_name_ea(idaapi.BADADDR, TABLE_NAME)
    if table == idaapi.BADADDR:
        raise RuntimeError(f"cannot resolve prototype table {TABLE_NAME}")
    records = {}
    for slot in range(256):
        base = table + SLOT_STRIDE * slot
        kind = ida_bytes.get_byte(base + KEY_OFFSET)
        if kind not in SELECTED:
            continue
        record = base + VALUE_OFFSET
        records[str(kind)] = {
            "slot": slot,
            "record_va": f"0x{record:016x}",
            "name": text_at(qword(record + 24), qword(record + 16)),
            "pin_sequences": {
                "inputs": pin_sequence(record, 96),
                "bidirectional": pin_sequence(record, 112),
                "outputs": pin_sequence(record, 128),
            },
        }
    missing = sorted(SELECTED - {int(kind) for kind in records})
    digest = ida_nalt.retrieve_input_file_sha256()
    OUTPUT.write_text(
        json.dumps(
            {
                "schema": 1,
                "input_file": ida_nalt.get_root_filename(),
                "input_sha256": digest.hex() if digest else None,
                "image_base": f"0x{idaapi.get_imagebase():016x}",
                "prototype_table": TABLE_NAME,
                "selected_kinds": sorted(SELECTED),
                "missing_kinds": missing,
                "records": records,
            },
            indent=2,
            ensure_ascii=True,
        )
        + "\n",
        encoding="ascii",
    )
    idc.qexit(0 if not missing else 2)


try:
    main()
except Exception as exc:
    print(f"DUMP_ERROR: {type(exc).__name__}: {exc}")
    idc.qexit(1)
