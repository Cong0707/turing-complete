"""只读导出 campaign 解析器关键 Nim 字符串常量。"""

from __future__ import annotations

import json
from pathlib import Path

import ida_auto
import ida_bytes
import ida_name
import idaapi


OUTPUT = Path(
    r"D:\Develop\Other\turing-complete\.research\byte_adder_protocol_audit_agent\ida_campaign_strings.json"
)

NAMES = tuple(
    f"TM__aJQQD8lFP9bFZ9bHTULcjigA_{index}"
    for index in (
        43, 44, 53, 54, 59, 60, 61, 62, 65, 66, 85, 86, 95,
        99, 100, 103, 104, 105, 106, 107, 108, 109, 110,
        117, 118, 119, 120,
    )
) + (
    "TM__JGc9b9bh2D3nTdUR7TGyq8aA_487",
    "TM__JGc9b9bh2D3nTdUR7TGyq8aA_488",
    "TM__JGc9b9bh2D3nTdUR7TGyq8aA_489",
    "TM__JGc9b9bh2D3nTdUR7TGyq8aA_490",
)


def record(name: str) -> dict[str, object]:
    ea = ida_name.get_name_ea(idaapi.BADADDR, name)
    if ea == idaapi.BADADDR:
        return {"name": name, "error": "missing"}
    raw = ida_bytes.get_bytes(ea, 160) or b""
    return {
        "name": name,
        "address": f"0x{ea:016x}",
        "qword": ida_bytes.get_qword(ea),
        "bytes_hex": raw.hex(),
        "ascii": "".join(chr(value) if 32 <= value < 127 else "." for value in raw),
    }


def main() -> None:
    ida_auto.auto_wait()
    OUTPUT.write_text(
        json.dumps([record(name) for name in NAMES], ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    idaapi.qexit(0)


main()
