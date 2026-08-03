"""只读导出基础元件名称和 DEFAULT_COMPONENT_SCORES 原始表。"""

from __future__ import annotations

import json
from pathlib import Path

import ida_auto
import ida_bytes
import ida_name
import idaapi
import idc


OUT = Path(r"D:\Develop\Other\turing-complete\.research\byte_adder_boolean_superopt_agent\default_scores.json")
SCORES = "DEFAULT_COMPONENT_SCORES__modelZscores_u1605"
PROTOTYPES = "TM__wUqL1Kpuf69c1ieeyVFJbBQ_3391"
SLOT_STRIDE = 1464


def text_at(pointer: int, length: int) -> str | None:
    if not (0 < length <= 256 and ida_bytes.is_loaded(pointer + 8)):
        return None
    raw = ida_bytes.get_bytes(pointer + 8, length)
    if raw is None:
        return None
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return None


ida_auto.auto_wait()
score_ea = ida_name.get_name_ea(idaapi.BADADDR, SCORES)
proto_ea = ida_name.get_name_ea(idaapi.BADADDR, PROTOTYPES)
if score_ea == idaapi.BADADDR or proto_ea == idaapi.BADADDR:
    raise RuntimeError("required score/prototype symbol is missing")

names: dict[int, str | None] = {}
for slot in range(256):
    base = proto_ea + SLOT_STRIDE * slot
    kind = ida_bytes.get_byte(base + 16)
    record = base + 24
    name = text_at(ida_bytes.get_qword(record + 24), ida_bytes.get_qword(record + 16))
    if name is not None:
        names[kind] = name

score_length = ida_bytes.get_qword(score_ea)
score_pointer = ida_bytes.get_qword(score_ea + 8)
score_data = score_pointer + 8
by_kind: dict[int, dict[str, int]] = {}
for slot in range(score_length):
    entry = score_data + 32 * slot
    hash_code = ida_bytes.get_qword(entry)
    if hash_code == 0:
        continue
    kind = ida_bytes.get_byte(entry + 8)
    by_kind[kind] = {
        "slot": slot,
        "hash": hash_code,
        "gate": ida_bytes.get_qword(entry + 16),
        "delay": ida_bytes.get_qword(entry + 24),
    }
rows = [
    {"kind": kind, "name": names.get(kind), **by_kind[kind]}
    for kind in sorted(by_kind)
]
OUT.write_text(
    json.dumps(
        {
            "length": score_length,
            "pointer": f"0x{score_pointer:016x}",
            "rows": rows,
        },
        ensure_ascii=False,
        indent=2,
    )
    + "\n",
    encoding="utf-8",
)
idc.qexit(0)
