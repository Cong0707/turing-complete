"""Exclude the minimum-output-support 42-state direct-lift family.

The model is O=[I|X], H_top=A*O+X*D, H_hidden=D.  This verifier covers
the narrow family where X is zero on every natural xorshift output row whose
support is already at most four.  Consequently exactly the 15 heavy natural
rows must use hidden coordinates.  It is a useful exact boundary, not a
global exclusion of arbitrary X.
"""

from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
from itertools import combinations, product
import json
from math import comb
from pathlib import Path


BITS = 32
HEAVY = tuple(range(12, 27))
FULL_LIGHT = tuple(range(12))
TAIL_LIGHT = tuple(range(27, 32))


def xorshift32(value: int) -> int:
    value ^= value >> 13
    value &= 0xFFFFFFFF
    value ^= (value << 17) & 0xFFFFFFFF
    value &= 0xFFFFFFFF
    value ^= value >> 5
    return value & 0xFFFFFFFF


def transition_rows() -> tuple[int, ...]:
    rows = [0] * BITS
    for source in range(BITS):
        value = xorshift32(1 << source)
        for target in range(BITS):
            if value >> target & 1:
                rows[target] |= 1 << source
    return tuple(rows)


def restricted_row(row: int) -> int:
    return sum(((row >> source) & 1) << local for local, source in enumerate(HEAVY))


def sparse_dictionary_obstruction(rows: tuple[int, ...], indices: tuple[int, ...]) -> dict:
    checked = 0
    feasible = 0
    maximum_histogram: Counter[int] = Counter()
    best: tuple[int, int, int, int, int] | None = None
    for weight in range(5):
        for selected in combinations(range(BITS), weight):
            dictionary_row = sum(1 << bit for bit in selected)
            weights = tuple((rows[index] ^ dictionary_row).bit_count() for index in indices)
            key = (
                max(weights),
                sum(max(0, value - 4) for value in weights),
                sum(weights),
                weight,
                dictionary_row,
            )
            checked += 1
            maximum_histogram[key[0]] += 1
            feasible += key[0] <= 4
            if best is None or key < best:
                best = key
    assert best is not None
    assert checked == sum(comb(BITS, weight) for weight in range(5))
    return {
        "indices": list(indices),
        "natural_rows_hex": [f"{rows[index]:08x}" for index in indices],
        "dictionary_candidates_checked": checked,
        "feasible_candidates": feasible,
        "best_maximum_weight": best[0],
        "best_support_excess": best[1],
        "best_total_weight": best[2],
        "best_dictionary_weight": best[3],
        "best_dictionary_hex": f"{best[4]:08x}",
        "maximum_weight_histogram": {
            str(weight): count for weight, count in sorted(maximum_histogram.items())
        },
    }


def build_certificate() -> dict:
    rows = transition_rows()
    assert [row.bit_count() for row in rows] == [4] * 12 + [6, 6, 5, 5, 5, 7, 7] + [6] * 8 + [3] * 5

    restricted = {index: restricted_row(rows[index]) for index in (*FULL_LIGHT, *TAIL_LIGHT)}
    null_patterns = tuple(
        pattern
        for pattern in range(1 << len(HEAVY))
        if all((restricted[index] & pattern).bit_count() % 2 == 0 for index in FULL_LIGHT)
    )
    assert null_patterns == (0, 0x1FFF, 0x2001, 0x3FFE, 0x494B, 0x56B4, 0x694A, 0x76B5)

    nonzero = null_patterns[1:]
    feasible_multisets = []
    for counts in product(range(4), repeat=len(nonzero)):
        if not 1 <= sum(counts) <= 10:
            continue
        heavy_counts = tuple(
            sum(count * ((pattern >> bit) & 1) for count, pattern in zip(counts, nonzero))
            for bit in range(len(HEAVY))
        )
        if min(heavy_counts) == 0 or max(heavy_counts) > 3:
            continue
        tail_counts = tuple(
            sum(
                count * ((restricted[index] & pattern).bit_count() % 2)
                for count, pattern in zip(counts, nonzero)
            )
            for index in TAIL_LIGHT
        )
        if max(tail_counts) > 1:
            continue
        feasible_multisets.append(
            {
                "counts": list(counts),
                "column_count": sum(counts),
                "heavy_row_counts": list(heavy_counts),
                "tail_hidden_weights": list(tail_counts),
            }
        )

    # Every surviving multiset contains exactly one Q-family column and one
    # R-family column.  These core rows see only that shared hidden D row.
    q_positions = (3, 5)  # 0x494b or 0x694a in nonzero[]
    r_positions = (4, 6)  # 0x56b4 or 0x76b5 in nonzero[]
    assert len(feasible_multisets) == 8
    for item in feasible_multisets:
        counts = item["counts"]
        assert sum(counts[position] for position in q_positions) == 1
        assert sum(counts[position] for position in r_positions) == 1

    q_core = (13, 15, 18, 20, 23)
    r_core = (14, 16, 17, 19, 21, 22, 24)
    q_obstruction = sparse_dictionary_obstruction(rows, q_core)
    r_obstruction = sparse_dictionary_obstruction(rows, r_core)
    assert q_obstruction["feasible_candidates"] == 0
    assert r_obstruction["feasible_candidates"] == 0

    matrix_payload = b"".join(row.to_bytes(4, "little") for row in rows)
    return {
        "schema": 1,
        "scope": (
            "42-state O=[I|X] direct lift; X=0 on natural rows of weight<=4; "
            "X row weight<=3; D row weight<=4; H row weight<=4"
        ),
        "status": "unsat_in_scoped_family",
        "transition_sha256": sha256(matrix_payload).hexdigest(),
        "heavy_rows": list(HEAVY),
        "full_light_rows": list(FULL_LIGHT),
        "tail_light_rows": list(TAIL_LIGHT),
        "nullspace": {
            "dimension": 3,
            "patterns_hex": [f"{pattern:04x}" for pattern in null_patterns],
            "nonzero_pattern_order_hex": [f"{pattern:04x}" for pattern in nonzero],
            "feasible_column_multisets": feasible_multisets,
        },
        "q_core_obstruction": q_obstruction,
        "r_core_obstruction": r_obstruction,
        "reason": (
            "each feasible hidden-column multiset has one Q-family column; rows "
            "13,15,18,20,23 therefore share its single D row, but all 41,449 "
            "D low halves of weight<=4 leave at least one row at weight>=7"
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    result = build_certificate()
    encoded = json.dumps(result, indent=2) + "\n"
    if args.verify:
        assert json.loads(args.verify.read_text(encoding="utf-8")) == result
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")


if __name__ == "__main__":
    main()
