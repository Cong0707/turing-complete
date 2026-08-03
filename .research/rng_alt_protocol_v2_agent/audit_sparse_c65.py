#!/usr/bin/env python3
"""Independently audit persistent-seed 65-cycle search records."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Iterable


BITS = 32
MASK = (1 << BITS) - 1
LIMIT = 16
Matrix = tuple[int, ...]


def xorshift32(value: int) -> int:
    value ^= value >> 13
    value ^= (value << 17) & MASK
    value ^= value >> 5
    return value & MASK


def transition_rows() -> Matrix:
    columns = tuple(xorshift32(1 << source) for source in range(BITS))
    return tuple(
        sum(((columns[source] >> target) & 1) << source for source in range(BITS))
        for target in range(BITS)
    )


def identity() -> Matrix:
    return tuple(1 << bit for bit in range(BITS))


def matrix_xor(left: Matrix, right: Matrix) -> Matrix:
    return tuple(a ^ b for a, b in zip(left, right, strict=True))


def apply_row(row: int, matrix: Matrix) -> int:
    result = 0
    while row:
        bit = (row & -row).bit_length() - 1
        result ^= matrix[bit]
        row &= row - 1
    return result


def multiply(left: Matrix, right: Matrix) -> Matrix:
    return tuple(apply_row(row, right) for row in left)


def inverse(source: Matrix) -> Matrix:
    matrix = list(source)
    result = list(identity())
    for column in range(BITS):
        pivot = next(
            (row for row in range(column, BITS) if matrix[row] & (1 << column)),
            None,
        )
        if pivot is None:
            raise AssertionError("C is singular")
        matrix[column], matrix[pivot] = matrix[pivot], matrix[column]
        result[column], result[pivot] = result[pivot], result[column]
        for row in range(BITS):
            if row != column and matrix[row] & (1 << column):
                matrix[row] ^= matrix[column]
                result[row] ^= result[column]
    if tuple(matrix) != identity():
        raise AssertionError("inverse elimination did not reach identity")
    return tuple(result)


def parse_matrix(record: dict[str, object], name: str) -> Matrix:
    raw = record.get(name)
    if not isinstance(raw, list) or len(raw) != BITS:
        raise AssertionError(f"{name} must contain {BITS} rows")
    result = tuple(int(str(value), 16) for value in raw)
    if any(value < 0 or value > MASK for value in result):
        raise AssertionError(f"{name} has a row outside 32 bits")
    return result


def feedback_score(b: Matrix, d: Matrix, c: Matrix) -> dict[str, int]:
    metrics = [
        4 * left.bit_count() + right.bit_count()
        for left, right in zip(b, d, strict=True)
    ]
    violations = [max(0, metric - LIMIT) for metric in metrics]
    return {
        "over": sum(value > 0 for value in violations),
        "excess": sum(violations),
        "max": max(metrics),
        "quadratic": sum(value * value for value in violations),
        "combined_weight": sum(row.bit_count() for row in b + d),
        "B_weight": sum(row.bit_count() for row in b),
        "D_weight": sum(row.bit_count() for row in d),
        "C_weight": sum(row.bit_count() for row in c),
    }


def audit_record(record: dict[str, object]) -> dict[str, int]:
    a = transition_rows()
    a_plus_i = matrix_xor(a, identity())
    c = parse_matrix(record, "C")
    stored_t = parse_matrix(record, "T")
    stored_b = parse_matrix(record, "B")
    stored_d = parse_matrix(record, "D")

    p = inverse(c)
    if multiply(c, p) != identity() or multiply(p, c) != identity():
        raise AssertionError("C inverse identity failed")
    t = multiply(p, a)
    b = multiply(t, c)
    d = multiply(t, a_plus_i)
    if (stored_t, stored_b, stored_d) != (t, b, d):
        raise AssertionError("stored T/B/D does not match C parameterization")

    for row, (c_row, a_row) in enumerate(zip(c, a, strict=True)):
        cap = (LIMIT - a_row.bit_count()) // 4
        if not 1 <= c_row.bit_count() <= cap:
            raise AssertionError(f"output row {row} exceeds cap {cap}")
        if 4 * c_row.bit_count() + a_row.bit_count() > LIMIT:
            raise AssertionError(f"output row {row} exceeds mixed-Kraft limit")

    q = (0,) * BITS
    expected = a
    for tick in range(65):
        output = matrix_xor(multiply(c, q), a)
        if output != expected:
            raise AssertionError(f"output replay failed at tick {tick}")
        q = matrix_xor(multiply(b, q), d)
        expected = multiply(a, expected)

    calculated = feedback_score(b, d, c)
    stored_score = record.get("score")
    if not isinstance(stored_score, dict):
        raise AssertionError("record has no score object")
    for key, value in calculated.items():
        if key in stored_score and int(stored_score[key]) != value:
            raise AssertionError(
                f"score mismatch for {key}: {stored_score[key]} != {value}"
            )
    if int(record.get("delay", -1)) != 8 or int(record.get("cycles", -1)) != 65:
        raise AssertionError("record is not marked delay=8, cycles=65")
    return calculated


def records(paths: Iterable[Path]) -> Iterable[tuple[Path, int, dict[str, object]]]:
    for path in paths:
        for line_number, line in enumerate(
            path.read_text(encoding="ascii").splitlines(), start=1
        ):
            if line.strip():
                yield path, line_number, json.loads(line)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("records", nargs="+", type=Path)
    args = parser.parse_args()

    audited: list[dict[str, object]] = []
    for path, line_number, record in records(args.records):
        score = audit_record(record)
        audited.append(
            {"path": str(path), "line": line_number, "score": score}
        )
    if not audited:
        raise AssertionError("no records were audited")

    def best(keys: tuple[str, ...]) -> dict[str, object]:
        return min(
            audited,
            key=lambda item: tuple(item["score"][key] for key in keys),
        )

    report = {
        "schema": 1,
        "status": "verified",
        "records": len(audited),
        "files": [
            {"path": str(path), "sha256": sha256(path)} for path in args.records
        ],
        "lexicographic_best": best(
            ("over", "excess", "max", "combined_weight")
        ),
        "linear_best": best(("excess", "over", "max", "combined_weight")),
        "quadratic_best": best(
            ("quadratic", "excess", "over", "combined_weight")
        ),
        "feasible_records": sum(
            item["score"]["over"] == 0 for item in audited
        ),
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output is not None:
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
