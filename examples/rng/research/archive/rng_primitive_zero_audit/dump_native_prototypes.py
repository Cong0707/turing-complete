"""Dump selected native component prototype records from the existing IDB."""

from __future__ import annotations

import json
from pathlib import Path

import ida_auto
import ida_bytes
import ida_name
import idaapi
import idc


OUTPUT = Path(
    r"D:\Develop\Other\turing-complete\.research\rng_primitive_zero_audit\native_prototypes.json"
)
TABLE_NAME = "TM__wUqL1Kpuf69c1ieeyVFJbBQ_3391"
SELECTED = {41, 51, 54, 56, 58, 59, 60, 61, 62, 68, 69, 70, 77, 79, 80, 81,
            82, 83, 84, 85, 86, 87, 89, 90, 91, 92, 93, 94, 95, 96,
            97, 98, 99, 100, 101, 106, 117, 118}
SLOT_STRIDE = 1464
KEY_OFFSET = 16
VALUE_OFFSET = 24
VALUE_SIZE = 1448


def qword(ea: int) -> int:
    return ida_bytes.get_qword(ea)


def mapped(ea: int, size: int = 1) -> bool:
    return ea != idaapi.BADADDR and all(ida_bytes.is_loaded(ea + i) for i in range(size))


def payload_ascii(pointer: int, length: int) -> str | None:
    if not (0 < length <= 200 and mapped(pointer + 8, length)):
        return None
    raw = ida_bytes.get_bytes(pointer + 8, length)
    if raw is None:
        return None
    try:
        value = raw.decode("utf-8")
    except UnicodeDecodeError:
        return None
    if all(ch.isprintable() or ch in "\r\n\t" for ch in value):
        return value
    return None


def describe_pairs(record: int) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    for offset in range(0, VALUE_SIZE - 8, 8):
        length = qword(record + offset)
        pointer = qword(record + offset + 8)
        if length < 0 or length > 4096 or not mapped(pointer):
            continue
        item: dict[str, object] = {
            "offset": offset,
            "length": length,
            "pointer": f"0x{pointer:016x}",
        }
        text = payload_ascii(pointer, length)
        if text is not None:
            item["text"] = text
        result.append(item)
    return result


def describe_pin(pin: int) -> dict[str, object]:
    item: dict[str, object] = {
        "raw_hex": ida_bytes.get_bytes(pin, 56).hex(),
        "kind": ida_bytes.get_byte(pin),
    }
    pairs: list[dict[str, object]] = []
    for offset in range(0, 48, 8):
        length = qword(pin + offset)
        pointer = qword(pin + offset + 8)
        if length < 0 or length > 200 or not mapped(pointer):
            continue
        pair: dict[str, object] = {
            "offset": offset,
            "length": length,
            "pointer": f"0x{pointer:016x}",
        }
        value = payload_ascii(pointer, length)
        if value is not None:
            pair["text"] = value
        pairs.append(pair)
    item["candidate_length_pointer_pairs"] = pairs
    return item


def describe_pin_sequences(record: int) -> dict[str, object]:
    result: dict[str, object] = {}
    for offset in (96, 112, 128):
        length = qword(record + offset)
        pointer = qword(record + offset + 8)
        pins = []
        if 0 <= length <= 32 and mapped(pointer):
            pins = [describe_pin(pointer + 8 + 56 * index) for index in range(length)]
        result[str(offset)] = {
            "length": length,
            "pointer": f"0x{pointer:016x}",
            "pins": pins,
        }
    return result


def main() -> None:
    ida_auto.auto_wait()
    table = ida_name.get_name_ea(idaapi.BADADDR, TABLE_NAME)
    if table == idaapi.BADADDR:
        raise RuntimeError(f"cannot resolve {TABLE_NAME}")

    records: dict[str, object] = {}
    for slot in range(256):
        base = table + SLOT_STRIDE * slot
        kind = ida_bytes.get_byte(base + KEY_OFFSET)
        if kind not in SELECTED:
            continue
        record = base + VALUE_OFFSET
        records[str(kind)] = {
            "slot": slot,
            "record_va": f"0x{record:016x}",
            "first_256_hex": ida_bytes.get_bytes(record, 256).hex(),
            "candidate_length_pointer_pairs": describe_pairs(record),
            "pin_sequences": describe_pin_sequences(record),
        }

    result = {
        "table_name": TABLE_NAME,
        "table_va": f"0x{table:016x}",
        "slot_stride": SLOT_STRIDE,
        "key_offset": KEY_OFFSET,
        "value_offset": VALUE_OFFSET,
        "value_size": VALUE_SIZE,
        "records": records,
        "missing": sorted(SELECTED - {int(kind) for kind in records}),
    }
    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=True) + "\n", encoding="ascii")
    idc.qexit(0)


try:
    main()
except Exception as exc:
    print(f"DUMP_ERROR: {exc}")
    idc.qexit(1)
