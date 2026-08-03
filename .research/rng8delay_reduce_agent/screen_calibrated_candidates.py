#!/usr/bin/env python3
"""Independently screen one-shot d8 basis candidates before exact synthesis."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


BITS = 32
MASK = (1 << BITS) - 1


def xorshift32(value: int) -> int:
    value ^= value >> 13
    value ^= (value << 17) & MASK
    value ^= value >> 5
    return value & MASK


def xorshift_matrix() -> list[int]:
    rows = [0] * BITS
    for source in range(BITS):
        output = xorshift32(1 << source)
        for target in range(BITS):
            rows[target] |= ((output >> target) & 1) << source
    return rows


def multiply(left: list[int], right: list[int]) -> list[int]:
    result: list[int] = []
    for row in left:
        value = 0
        remaining = row
        while remaining:
            bit = (remaining & -remaining).bit_length() - 1
            value ^= right[bit]
            remaining &= remaining - 1
        result.append(value)
    return result


def parse_matrix(record: dict[str, object], name: str) -> list[int]:
    raw = record.get(name)
    if not isinstance(raw, list) or len(raw) != BITS:
        raise ValueError(f"{name} must contain 32 rows")
    rows = [int(value, 16) for value in raw]
    if any(value < 0 or value > MASK for value in rows):
        raise ValueError(f"{name} row outside U32")
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    args = parser.parse_args()

    transform = xorshift_matrix()
    accepted: list[tuple[tuple[float, int, int], str]] = []
    rejected = {"parse": 0, "algebra": 0, "structure": 0, "timing": 0}
    seen: set[tuple[int, ...]] = set()
    total = 0

    for raw_line in args.source.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip():
            continue
        total += 1
        try:
            record = json.loads(raw_line)
            target = parse_matrix(record, "T")
            steady = parse_matrix(record, "B")
            output = parse_matrix(record, "C")
        except (ValueError, TypeError, json.JSONDecodeError):
            rejected["parse"] += 1
            continue
        target_key = tuple(target)
        if target_key in seen:
            continue
        seen.add(target_key)
        if multiply(output, target) != transform or multiply(target, output) != steady:
            rejected["algebra"] += 1
            continue
        if any(not 1 <= row.bit_count() <= 4 for matrix in (target, steady, output) for row in matrix):
            rejected["structure"] += 1
            continue
        violations = sum(
            steady_row.bit_count() >= 3 and target_row.bit_count() > 2
            for target_row, steady_row in zip(target, steady, strict=True)
        )
        if violations:
            rejected["timing"] += 1
            continue
        lower = record.get("lower", {})
        if not isinstance(lower, dict):
            lower = {}
        key = (
            float(record.get("surrogate", 1e30)),
            int(lower.get("proxy_logic", 1000)),
            int(lower.get("strict_logic", 1000)),
        )
        accepted.append((key, json.dumps(record, separators=(",", ":"))))

    accepted.sort(key=lambda item: item[0])
    output_text = "".join(line + "\n" for _, line in accepted)
    args.output.write_text(output_text, encoding="utf-8")
    source_digest = hashlib.sha256(args.source.read_bytes()).hexdigest()
    output_digest = hashlib.sha256(args.output.read_bytes()).hexdigest()
    summary = {
        "schema": 1,
        "source": str(args.source),
        "source_sha256": source_digest,
        "records": total,
        "unique_T": len(seen),
        "accepted": len(accepted),
        "rejected": rejected,
        "output": str(args.output),
        "output_sha256": output_digest,
        "necessary_condition": "weight(B[i]) >= 3 => weight(T[i]) <= 2",
    }
    args.summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
