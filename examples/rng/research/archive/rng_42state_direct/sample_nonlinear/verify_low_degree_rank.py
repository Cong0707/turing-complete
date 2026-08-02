#!/usr/bin/env python3
"""Compute ANF evaluation ranks of the fixed RNG trajectory sample.

If all square-free monomials through degree d have independent evaluations,
then no nonzero Boolean polynomial of algebraic degree <= d vanishes on the
sample.  Consequently, agreement between two degree-d functions on the live
sample implies a global Boolean identity rather than sample specialization.

This is a deterministic, low-memory research calculation.  It does not read
or write player saves and does not start the game.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import struct


MASK32 = (1 << 32) - 1
MASK64 = (1 << 64) - 1
SCRIPT_RANDOM_MODULUS = 0xFFFFFFFE
XORSHIFT64_STAR_MULTIPLIER = 0x2545F4914F6CDD1


def xorshift64_star(value: int) -> int:
    value &= MASK64
    value ^= (value << 12) & MASK64
    value ^= value >> 25
    value ^= value >> 27
    return (value * XORSHIFT64_STAR_MULTIPLIER) & MASK64


def initial_seed(test_id: int) -> int:
    return 1 + xorshift64_star(test_id + 1) % SCRIPT_RANDOM_MODULUS


def xorshift32(value: int) -> int:
    value &= MASK32
    value ^= value >> 13
    value ^= (value << 17) & MASK32
    value ^= value >> 5
    return value & MASK32


def trajectory(rounds: int) -> list[int]:
    states: list[int] = []
    for test_id in range(256):
        value = initial_seed(test_id)
        for _ in range(rounds):
            states.append(value)
            value = xorshift32(value)
    return states


def variable_signatures(states: list[int]) -> list[int]:
    result = [0] * 32
    for row, state in enumerate(states):
        value = state
        while value:
            low = value & -value
            result[low.bit_length() - 1] |= 1 << row
            value ^= low
    return result


def anf_rank(
    states: list[int], maximum_degree: int
) -> tuple[int, int, list[int], int | None]:
    variables = variable_signatures(states)
    basis: dict[int, int] = {}
    cumulative: list[int] = []
    monomial_count = 0
    row_full_at: int | None = None

    for degree in range(maximum_degree + 1):
        choices = [()] if degree == 0 else combinations(range(32), degree)
        for indices in choices:
            vector = (1 << len(states)) - 1
            for index in indices:
                vector &= variables[index]
            monomial_count += 1
            while vector:
                pivot = vector.bit_length() - 1
                previous = basis.get(pivot)
                if previous is None:
                    basis[pivot] = vector
                    break
                vector ^= previous
            if len(basis) == len(states):
                row_full_at = monomial_count
                break
        cumulative.append(len(basis))
        if row_full_at is not None:
            break
    return monomial_count, len(basis), cumulative, row_full_at


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rounds", type=int, default=65)
    parser.add_argument("--degree", type=int, default=3)
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("low_degree_rank_certificate.json"))
    args = parser.parse_args()
    states = trajectory(args.rounds)
    processed, rank, cumulative, row_full_at = anf_rank(states, args.degree)
    state_blob = b"".join(struct.pack("<I", value) for value in states)
    expected_counts = [sum(1 for _ in combinations(range(32), degree)) for degree in range(args.degree + 1)]
    result = {
        "schema": 1,
        "state_definition": f"256 seeds times xorshift states A^0(s)..A^{args.rounds - 1}(s)",
        "state_count": len(states),
        "unique_state_count": len(set(states)),
        "state_vector_sha256": sha256(state_blob).hexdigest(),
        "maximum_anf_degree": args.degree,
        "monomial_counts_by_exact_degree": expected_counts,
        "monomial_count": sum(expected_counts),
        "monomials_processed": processed,
        "rank_after_each_degree": cumulative,
        "rank": rank,
        "full_column_rank": row_full_at is None and rank == sum(expected_counts),
        "full_row_rank": rank == len(states),
        "full_row_rank_first_reached_at_monomial": row_full_at,
        "consequence": (
            f"no nonzero square-free Boolean polynomial of degree <= {args.degree} "
            "vanishes on this sample"
            if row_full_at is None and rank == sum(expected_counts)
            else "degree-bounded ANF evaluations span every Boolean function on this sample"
            if rank == len(states)
            else "evaluation map is neither full-column-rank nor full-row-rank"
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
