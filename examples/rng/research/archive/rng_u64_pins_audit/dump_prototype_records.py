"""Dump raw qwords and referenced bytes from the kind-98/100 prototypes."""

from __future__ import annotations

import json
from pathlib import Path

import ida_auto
import ida_bytes
import ida_name
import ida_segment
import idc


OUTPUT = Path(
    r"D:\Develop\Other\turing-complete\.research\rng_u64_pins_audit\prototype_records.json"
)
RECORDS = {98: 0x1409BBB58, 100: 0x1409D7F20}
RECORD_SIZE = 1448


def referenced_bytes(value: int) -> dict[str, object]:
    segment = ida_segment.getseg(value)
    if segment is None:
        return {}
    data = ida_bytes.get_bytes(value, 160) or b""
    return {
        "segment": ida_segment.get_segm_name(segment),
        "name": ida_name.get_name(value),
        "hex": data.hex(),
        "ascii": "".join(chr(byte) if 32 <= byte < 127 else "." for byte in data),
    }


def main() -> None:
    ida_auto.auto_wait()
    records: dict[str, object] = {}
    for kind, record in RECORDS.items():
        fields = []
        for offset in range(0, RECORD_SIZE - 7, 8):
            value = ida_bytes.get_qword(record + offset)
            item: dict[str, object] = {
                "offset": offset,
                "value": f"0x{value:016x}",
            }
            item.update(referenced_bytes(value))
            fields.append(item)
        records[str(kind)] = {"record_va": f"0x{record:016x}", "qwords": fields}
    OUTPUT.write_text(json.dumps({"records": records}, indent=2) + "\n", encoding="ascii")
    idc.qexit(0)


try:
    main()
except Exception as exc:
    print(f"DUMP_ERROR: {exc}")
    idc.qexit(1)
