"""Inventory Byte Adder circuits already downloaded from public GitHub saves.

This scanner is read-only and deliberately reports the format version so that
scores from old scoring systems are not compared with current v15 scores.
"""

from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import struct

from tc_save_lab.codec import decode_circuit
from tc_save_lab.snappy import decompress_raw


ROOT = Path(__file__).resolve().parents[2]
SOURCES = (
    ("https://github.com/chastitywhiterose/Turing-Complete", ".research/gh6", "GPL-3.0"),
    ("https://github.com/MizuchiKun/TuringComplete", ".research/gh9", "NOASSERTION"),
    ("https://github.com/CoccaGuo/Turing-Complete-Saves", ".research/public_saves_cocca", "NOASSERTION"),
    ("https://github.com/GeniusRyder/My-Turing-Complete-Save", ".research/public_saves_genius", "NOASSERTION"),
    ("https://github.com/MizuchiKun/TuringComplete", ".research/public_saves_mizuchi", "NOASSERTION"),
    ("https://github.com/magnitood/Turing-Complete", ".research/rng_public_search/magnitood_tc", "NOASSERTION"),
    ("https://github.com/NeiFeiTiii/Turing-Complete-Game-Save", ".research/rng_public_search/neifei_tc", "NOASSERTION"),
    ("https://github.com/zoickx/turing-complete", ".research/rng_public_search/zoickx_tc", "CC0-1.0"),
)


def header(payload: bytes) -> tuple[int, int]:
    raw = decompress_raw(payload[1:])
    if len(raw) < 28:
        raise ValueError("decompressed circuit is too short")
    return struct.unpack_from("<q", raw, 12)[0], struct.unpack_from("<q", raw, 20)[0]


def v6_kind_counts(payload: bytes) -> dict[str, int]:
    raw = decompress_raw(payload[1:])
    offset = 0

    def take(size: int) -> bytes:
        nonlocal offset
        result = raw[offset : offset + size]
        if len(result) != size:
            raise ValueError("truncated v6 circuit")
        offset += size
        return result

    def unpack(fmt: str) -> int:
        return struct.unpack(fmt, take(struct.calcsize(fmt)))[0]

    def skip_string() -> None:
        take(unpack("<H"))

    take(8 + 4 + 8 + 8 + 1 + 4)
    for _ in range(unpack("<H")):
        take(8)
    skip_string()
    take(4 + 1 + 1 + 2)
    take(unpack("<H"))
    skip_string()
    component_count = unpack("<q")
    kinds = []
    for _ in range(component_count):
        kind = unpack("<H")
        kinds.append(kind)
        take(4 + 1 + 8)
        skip_string()
        take(8 + 8 + 2)
        if kind == 78:
            take(8 + 4)
    return {str(key): value for key, value in sorted(Counter(kinds).items())}


def inspect(path: Path) -> dict[str, object]:
    payload = path.read_bytes()
    version = payload[0]
    gate, delay = header(payload)
    result: dict[str, object] = {
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "format_version": version,
        "declared_gate": gate,
        "declared_delay": delay,
        "declared_product": gate * delay,
    }
    if version == 6:
        result["component_kind_counts"] = v6_kind_counts(payload)
    elif version in {7, 13, 14, 15}:
        circuit = decode_circuit(payload)
        result["component_kind_counts"] = {
            str(key): value
            for key, value in sorted(Counter(component.kind for component in circuit.components).items())
        }
        result["component_count"] = len(circuit.components)
        result["wire_count"] = len(circuit.wires)
    return result


def main() -> None:
    records = []
    seen = set()
    for repository, relative_root, license_id in SOURCES:
        source_root = ROOT / relative_root
        if not source_root.exists():
            continue
        for path in source_root.rglob("circuit*.data"):
            normalized = path.as_posix().casefold()
            if "/byte_adder/" not in normalized:
                continue
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            key = (repository, digest)
            if key in seen:
                continue
            seen.add(key)
            record = inspect(path)
            record.update({"repository": repository, "license": license_id})
            records.append(record)
    records.sort(key=lambda item: (str(item["repository"]), str(item["path"])))
    output = Path(__file__).with_name("public-byte-adder-save-scan.json")
    output.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "scope": "working-tree public GitHub save files; no git history traversal",
                "records": records,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"records={len(records)}")
    for record in records:
        print(
            f"v{record['format_version']} {record['declared_gate']}/{record['declared_delay']} "
            f"{record['sha256'][:12]} {record['path']}"
        )


if __name__ == "__main__":
    main()
