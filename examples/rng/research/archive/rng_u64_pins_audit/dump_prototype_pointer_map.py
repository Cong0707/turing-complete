"""Describe every pointer-like qword in native kind-98/100 prototype records."""

from __future__ import annotations

import json
from pathlib import Path

import ida_auto
import ida_bytes
import ida_funcs
import ida_name
import ida_segment
import idc


OUTPUT = Path(
    r"D:\Develop\Other\turing-complete\.research\rng_u64_pins_audit\prototype_pointer_map.json"
)
RECORDS = {98: 0x1409BBB58, 100: 0x1409D7F20}
RECORD_SIZE = 1448


def describe(value: int) -> dict[str, object]:
    result: dict[str, object] = {"value": f"0x{value:016x}"}
    segment = ida_segment.getseg(value)
    if segment is None:
        return result
    result["segment"] = ida_segment.get_segm_name(segment)
    name = ida_name.get_name(value)
    if name:
        result["name"] = name
    func = ida_funcs.get_func(value)
    if func is not None:
        result["function_start"] = f"0x{func.start_ea:016x}"
        result["function_name"] = ida_name.get_name(func.start_ea)
    return result


def main() -> None:
    ida_auto.auto_wait()
    records: dict[str, object] = {}
    for kind, record in RECORDS.items():
        fields = []
        for offset in range(0, RECORD_SIZE - 7, 8):
            value = ida_bytes.get_qword(record + offset)
            item = {"offset": offset, **describe(value)}
            if len(item) > 2:
                fields.append(item)
        records[str(kind)] = {
            "record_va": f"0x{record:016x}",
            "mapped_qwords": fields,
        }
    OUTPUT.write_text(json.dumps({"records": records}, indent=2) + "\n", encoding="ascii")
    idc.qexit(0)


try:
    main()
except Exception as exc:
    print(f"DUMP_ERROR: {exc}")
    idc.qexit(1)
