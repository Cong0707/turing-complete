"""Dump the static prototype-table entries used by preorder for RAM ports."""

from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path

import ida_auto
import ida_bytes
import idautils
import idc


OUT = Path(
    r"D:\Develop\Other\turing-complete\.research\rng_primitive_zero_audit"
    r"\ram_tick_semantics\ram_prototypes.json"
)
TABLE_NAME = "TM__wUqL1Kpuf69c1ieeyVFJbBQ_3391"
ENTRY_SIZE = 1464
PROTOTYPE_OFFSET = 24
PROTOTYPE_SIZE = 1448


def read_port_group(proto: int, offset: int) -> dict[str, object]:
    length = ida_bytes.get_qword(proto + offset)
    pointer = ida_bytes.get_qword(proto + offset + 8)
    ports: list[dict[str, int]] = []
    if pointer and 0 <= length < 100:
        for index in range(length):
            item = pointer + 8 + 56 * index
            ports.append(
                {
                    "index": index,
                    "kind_u8_at_0": ida_bytes.get_byte(item),
                    "u8_at_1": ida_bytes.get_byte(item + 1),
                    "u16_at_2": ida_bytes.get_word(item + 2),
                    "u32_at_4": ida_bytes.get_dword(item + 4),
                    "qword_at_8": ida_bytes.get_qword(item + 8),
                    "qword_at_16": ida_bytes.get_qword(item + 16),
                    "qword_at_24": ida_bytes.get_qword(item + 24),
                    "qword_at_32": ida_bytes.get_qword(item + 32),
                    "qword_at_40": ida_bytes.get_qword(item + 40),
                    "qword_at_48": ida_bytes.get_qword(item + 48),
                }
            )
    return {"length": length, "pointer": f"{pointer:#x}", "ports": ports}


def main() -> None:
    ida_auto.auto_wait()
    names = {name: ea for ea, name in idautils.Names()}
    table = names[TABLE_NAME]
    result: dict[str, object] = {"table": f"{table:#x}", "entries": {}}
    entries: dict[str, object] = result["entries"]  # type: ignore[assignment]
    wanted = {54, 56, 118}
    for slot in range(256):
        entry = table + ENTRY_SIZE * slot
        occupancy = ida_bytes.get_qword(entry + 8)
        stored_kind = ida_bytes.get_byte(entry + 16)
        if occupancy == 0 or stored_kind not in wanted:
            continue
        proto = entry + PROTOTYPE_OFFSET
        raw = ida_bytes.get_bytes(proto, PROTOTYPE_SIZE)
        entries[str(stored_kind)] = {
            "hash_slot": slot,
            "entry": f"{entry:#x}",
            "occupancy_qword": occupancy,
            "stored_kind_u8": stored_kind,
            "prototype_raw_hex": raw.hex() if raw is not None else None,
            "prototype_sha256": sha256(raw).hexdigest() if raw is not None else None,
            "word1_proto_qword8": ida_bytes.get_word(proto + 8 * 8 + 2),
            "word2_proto_qword8": ida_bytes.get_word(proto + 8 * 8 + 4),
            "group_at_96": read_port_group(proto, 96),
            "group_at_112": read_port_group(proto, 112),
            "group_at_128": read_port_group(proto, 128),
        }
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    idc.qexit(0)


try:
    main()
except Exception as exc:
    OUT.with_suffix(".error.txt").write_text(repr(exc), encoding="utf-8")
    idc.qexit(1)
