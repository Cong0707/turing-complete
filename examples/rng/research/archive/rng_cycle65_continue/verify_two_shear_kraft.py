#!/usr/bin/env python3
"""Certify a delay lower bound for the fixed two-shear 65-cycle RNG.

The model has 32 state leaves q arriving at delay 4, 32 constant-seed leaves
arriving at delay 0, and XOR2 gates of delay 2.  It computes the 64 targets

    feedback = B*q xor D*s
    output   = C*q xor A*s

for T=(I+R17)(I+R13).  The script is research-only and does not import save
code or access the live game schematic.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import random
from typing import Callable, Sequence


BITS = 32
MASK = (1 << BITS) - 1
IDENTITY = tuple(1 << bit for bit in range(BITS))
Q_ARRIVAL = 4
SEED_ARRIVAL = 0
XOR2_DELAY = 2
TARGET_DELAY = 9


def xorshift32(value: int) -> int:
    value ^= value >> 13
    value &= MASK
    value ^= (value << 17) & MASK
    value &= MASK
    value ^= value >> 5
    return value & MASK


def matrix_from_function(function: Callable[[int], int]) -> tuple[int, ...]:
    return tuple(
        sum(((function(1 << source) >> output) & 1) << source for source in range(BITS))
        for output in range(BITS)
    )


def apply_row(row: int, matrix: Sequence[int]) -> int:
    result = 0
    while row:
        low = row & -row
        result ^= matrix[low.bit_length() - 1]
        row ^= low
    return result


def apply_matrix(matrix: Sequence[int], value: int) -> int:
    return sum(((row & value).bit_count() & 1) << bit for bit, row in enumerate(matrix))


def compose(left: Sequence[int], right: Sequence[int]) -> tuple[int, ...]:
    return tuple(apply_row(row, right) for row in left)


def add(left: Sequence[int], right: Sequence[int]) -> tuple[int, ...]:
    return tuple(a ^ b for a, b in zip(left, right))


def invert(matrix: Sequence[int]) -> tuple[int, ...]:
    rows = [matrix[index] | ((1 << index) << BITS) for index in range(BITS)]
    for column in range(BITS):
        pivot = next(index for index in range(column, BITS) if rows[index] >> column & 1)
        rows[column], rows[pivot] = rows[pivot], rows[column]
        for index in range(BITS):
            if index != column and rows[index] >> column & 1:
                rows[index] ^= rows[column]
    return tuple((row >> BITS) & MASK for row in rows)


def right_shear(distance: int) -> tuple[int, ...]:
    return matrix_from_function(lambda value: (value ^ (value >> distance)) & MASK)


def build_matrices() -> dict[str, tuple[int, ...]]:
    a = matrix_from_function(xorshift32)
    t = compose(right_shear(17), right_shear(13))
    t_inverse = invert(t)
    b = compose(t, compose(a, t_inverse))
    c = compose(a, t_inverse)
    d = compose(t, add(a, IDENTITY))
    if compose(c, t) != a:
        raise AssertionError("C*T != A")
    if compose(t, c) != b:
        raise AssertionError("T*C != B")
    if compose(t, t_inverse) != IDENTITY:
        raise AssertionError("T*T^-1 != I")
    if d != compose(t, add(a, IDENTITY)):
        raise AssertionError("D != T*(A+I)")
    return {"A": a, "T": t, "T_inverse": t_inverse, "B": b, "C": c, "D": d}


def verify_protocol(matrices: dict[str, tuple[int, ...]]) -> int:
    generator = random.Random(20260802)
    seeds = [0, 1, 2, 0x12345678, MASK]
    seeds.extend(generator.getrandbits(BITS) for _ in range(64))
    a, t, b, c, d = (matrices[name] for name in ("A", "T", "B", "C", "D"))
    for seed in seeds:
        q = 0
        expected = seed
        for tick in range(65):
            output = apply_matrix(c, q) ^ apply_matrix(a, seed)
            next_q = apply_matrix(b, q) ^ apply_matrix(d, seed)
            expected = xorshift32(expected)
            if output != expected:
                raise AssertionError(f"seed {seed:08x} tick {tick}: output mismatch")
            if next_q != apply_matrix(t, expected ^ seed):
                raise AssertionError(f"seed {seed:08x} tick {tick}: state mismatch")
            q = next_q
    return len(seeds)


def target_record(branch: str, index: int, q_row: int, seed_row: int) -> dict[str, object]:
    q_weight = q_row.bit_count()
    seed_weight = seed_row.bit_count()
    q_levels = (TARGET_DELAY - Q_ARRIVAL) // XOR2_DELAY
    seed_levels = (TARGET_DELAY - SEED_ARRIVAL) // XOR2_DELAY
    denominator = 1 << seed_levels
    q_numerator = 1 << (seed_levels - q_levels)
    numerator = q_weight * q_numerator + seed_weight
    return {
        "branch": branch,
        "index": index,
        "q_row": f"{q_row:08x}",
        "seed_row": f"{seed_row:08x}",
        "q_weight": q_weight,
        "seed_weight": seed_weight,
        "q_max_xor_levels": q_levels,
        "seed_max_xor_levels": seed_levels,
        "kraft_numerator": numerator,
        "kraft_denominator": denominator,
        "violates": numerator > denominator,
    }


def make_certificate() -> dict[str, object]:
    matrices = build_matrices()
    seed_count = verify_protocol(matrices)
    records = []
    for branch, q_rows, seed_rows in (
        ("feedback", matrices["B"], matrices["D"]),
        ("output", matrices["C"], matrices["A"]),
    ):
        records.extend(
            target_record(branch, index, q_row, seed_row)
            for index, (q_row, seed_row) in enumerate(zip(q_rows, seed_rows))
        )
    violations = [record for record in records if record["violates"]]
    if not violations:
        raise AssertionError("expected a delay-nine Kraft obstruction")

    matrix_payload = b"".join(
        row.to_bytes(4, "little")
        for name in ("A", "T", "T_inverse", "B", "C", "D")
        for row in matrices[name]
    )
    return {
        "schema": 1,
        "scope": "fixed T=(I+R17)(I+R13); XOR2 only; q arrival 4; seed arrival 0",
        "model": {
            "feedback": "B*q xor D*seed",
            "output": "C*q xor A*seed",
            "cycles": 65,
            "target_count": 64,
            "xor2_gate_budget": 92,
            "xor2_delay": XOR2_DELAY,
            "target_delay": TARGET_DELAY,
        },
        "matrix_sha256": sha256(matrix_payload).hexdigest(),
        "matrix_identities": {
            "C*T=A": True,
            "T*C=B": True,
            "T*T^-1=I": True,
            "D=T*(A+I)": True,
        },
        "protocol_verification": {
            "seed_count": seed_count,
            "outputs_per_seed": 65,
            "all_state_initial_values": 0,
        },
        "kraft_bound": {
            "argument": (
                "Unfold a target XOR DAG into a binary formula. Each required independent "
                "leaf occurs an odd, hence nonzero, number of times. q leaves have at most "
                "2 XOR levels and seed leaves at most 4, so Kraft requires "
                "q_weight/4 + seed_weight/16 <= 1. Sharing and cancellation only add "
                "leaf occurrences and cannot weaken this necessary condition."
            ),
            "integer_form": "4*q_weight + seed_weight <= 16",
            "feedback_violation_count": sum(
                record["violates"] and record["branch"] == "feedback" for record in records
            ),
            "output_violation_count": sum(
                record["violates"] and record["branch"] == "output" for record in records
            ),
            "maximum_numerator": max(int(record["kraft_numerator"]) for record in records),
            "certified_total_delay_lower_bound": 10,
            "conclusion": (
                "delay <= 9 is impossible for this fixed two-shear XOR2 model at every "
                "gate budget, including XOR2 <= 92"
            ),
        },
        "targets": records,
    }


def verify_certificate(certificate: dict[str, object]) -> None:
    expected = make_certificate()
    if certificate != expected:
        raise AssertionError("saved certificate differs from a clean recomputation")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify-existing", type=Path)
    args = parser.parse_args()
    if args.verify_existing:
        verify_certificate(json.loads(args.verify_existing.read_text(encoding="utf-8")))
        print(f"verified {args.verify_existing}")
        return 0
    certificate = make_certificate()
    encoded = json.dumps(certificate, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    print(
        "delay<=9 UNSAT by Kraft: "
        f"feedback violations={certificate['kraft_bound']['feedback_violation_count']}, "
        f"output violations={certificate['kraft_bound']['output_violation_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
