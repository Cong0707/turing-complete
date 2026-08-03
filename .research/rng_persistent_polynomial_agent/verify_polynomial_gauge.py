#!/usr/bin/env python3
"""Verify the persistent-seed polynomial family and its gauge equivalence.

This is an offline GF(2) proof tool.  It does not import the save writer and
does not read or write the live Turing Complete save.

For every invertible polynomial P(A) commuting with A and every invertible T,
the proposed family is

    B = T A T^-1
    D = T P
    C = (A + I) P^-1 T^-1

Putting U = T P gives exactly the P=I family

    B = U A U^-1, D = U, C = (A + I) U^-1.

The equality is algebraic; the executable checks below are certificates
against implementation mistakes, not the reason the theorem is true.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path
from typing import Iterable, Sequence


N = 32
MASK = (1 << N) - 1
IDENTITY = tuple(1 << bit for bit in range(N))


def xorshift32(value: int) -> int:
    value &= MASK
    value ^= value >> 13
    value ^= (value << 17) & MASK
    value ^= value >> 5
    return value & MASK


def matrix_from_function(function) -> tuple[int, ...]:
    columns = tuple(function(1 << source) for source in range(N))
    return tuple(
        sum(((columns[source] >> target) & 1) << source for source in range(N))
        for target in range(N)
    )


def apply_row(row: int, matrix: Sequence[int]) -> int:
    result = 0
    while row:
        bit = row & -row
        result ^= matrix[bit.bit_length() - 1]
        row ^= bit
    return result


def multiply(left: Sequence[int], right: Sequence[int]) -> tuple[int, ...]:
    return tuple(apply_row(row, right) for row in left)


def add(left: Sequence[int], right: Sequence[int]) -> tuple[int, ...]:
    return tuple(a ^ b for a, b in zip(left, right, strict=True))


def inverse(matrix: Sequence[int]) -> tuple[int, ...]:
    rows = [int(matrix[row]) | (1 << (N + row)) for row in range(N)]
    for column in range(N):
        pivot = next(
            (row for row in range(column, N) if rows[row] >> column & 1),
            None,
        )
        if pivot is None:
            raise ValueError("singular matrix")
        rows[column], rows[pivot] = rows[pivot], rows[column]
        for row in range(N):
            if row != column and rows[row] >> column & 1:
                rows[row] ^= rows[column]
    return tuple((row >> N) & MASK for row in rows)


def apply_matrix(matrix: Sequence[int], value: int) -> int:
    return sum(
        (((row & value).bit_count() & 1) << bit)
        for bit, row in enumerate(matrix)
    )


def polynomial_of_a(coefficients: int, a: Sequence[int]) -> tuple[int, ...]:
    """Evaluate sum(coeff[k] * A**k), for a 32-bit coefficient mask."""

    result = (0,) * N
    power = IDENTITY
    for degree in range(N):
        if coefficients >> degree & 1:
            result = add(result, power)
        power = multiply(power, a)
    return result


def random_encoding(generator: random.Random, shears: int) -> tuple[int, ...]:
    rows = list(IDENTITY)
    for _ in range(shears):
        destination = generator.randrange(N)
        source = generator.randrange(N - 1)
        if source >= destination:
            source += 1
        rows[destination] ^= rows[source]
        if generator.randrange(8) == 0:
            other = generator.randrange(N)
            rows[destination], rows[other] = rows[other], rows[destination]
    return tuple(rows)


def hex_rows(matrix: Sequence[int]) -> list[str]:
    return [f"{row:08x}" for row in matrix]


def sha256_matrices(matrices: Iterable[Sequence[int]]) -> str:
    digest = hashlib.sha256()
    for matrix in matrices:
        for row in matrix:
            digest.update(int(row).to_bytes(4, "little"))
    return digest.hexdigest()


def protocol_all_space(
    b: Sequence[int], d: Sequence[int], c: Sequence[int], a: Sequence[int]
) -> None:
    """Prove every seed by comparing the complete seed-to-output matrices."""

    state_map = (0,) * N
    expected = IDENTITY
    for tick in range(1, 66):
        state_map = add(multiply(b, state_map), d)
        output_map = add(multiply(c, state_map), IDENTITY)
        expected = multiply(a, expected)
        if output_map != expected:
            raise AssertionError(f"all-space protocol mismatch at tick {tick}")


def protocol_values(
    b: Sequence[int],
    d: Sequence[int],
    c: Sequence[int],
    seeds: Sequence[int],
) -> None:
    for seed in seeds:
        state = 0
        expected = seed
        for tick in range(1, 66):
            state = apply_matrix(b, state) ^ apply_matrix(d, seed)
            output = apply_matrix(c, state) ^ seed
            expected = xorshift32(expected)
            if output != expected:
                raise AssertionError(
                    f"value replay mismatch seed={seed:08x} tick={tick}: "
                    f"{output:08x} != {expected:08x}"
                )


def verify_case(
    *,
    label: str,
    t: Sequence[int],
    p: Sequence[int],
    a: Sequence[int],
    seeds: Sequence[int],
) -> dict[str, object]:
    ti = inverse(t)
    pi = inverse(p)
    a_plus_i = add(a, IDENTITY)

    original_b = multiply(multiply(t, a), ti)
    original_d = multiply(t, p)
    original_c = multiply(multiply(a_plus_i, pi), ti)

    u = original_d
    ui = inverse(u)
    normalized_b = multiply(multiply(u, a), ui)
    normalized_d = u
    normalized_c = multiply(a_plus_i, ui)

    if original_b != normalized_b:
        raise AssertionError(f"{label}: B gauge equality failed")
    if original_d != normalized_d:
        raise AssertionError(f"{label}: D gauge equality failed")
    if original_c != normalized_c:
        raise AssertionError(f"{label}: C gauge equality failed")
    if multiply(p, a) != multiply(a, p):
        raise AssertionError(f"{label}: P does not commute with A")
    if multiply(u, normalized_c) != add(normalized_b, IDENTITY):
        raise AssertionError(f"{label}: U*C != B+I")

    protocol_all_space(original_b, original_d, original_c, a)
    protocol_values(original_b, original_d, original_c, seeds)
    return {
        "label": label,
        "matrix_sha256": sha256_matrices(
            (t, p, u, original_b, original_d, original_c)
        ),
        "T": hex_rows(t),
        "P": hex_rows(p),
        "U": hex_rows(u),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--random-polynomials", type=int, default=64)
    parser.add_argument("--random-seeds", type=int, default=256)
    parser.add_argument("--seed", type=lambda value: int(value, 0), default=0x6608_2026)
    args = parser.parse_args()

    generator = random.Random(args.seed)
    a = matrix_from_function(xorshift32)
    a_plus_i = add(a, IDENTITY)
    inverse(a_plus_i)  # The named endpoint must satisfy the hypothesis.

    coefficient_masks = [1, 0b11]
    attempts = 0
    while len(coefficient_masks) < args.random_polynomials + 2:
        attempts += 1
        coefficients = generator.randrange(1, 1 << N)
        if coefficients in coefficient_masks:
            continue
        p = polynomial_of_a(coefficients, a)
        try:
            inverse(p)
        except ValueError:
            continue
        coefficient_masks.append(coefficients)

    seeds = [1 << bit for bit in range(N)]
    seeds.extend(generator.randrange(1 << N) for _ in range(args.random_seeds))
    cases = []
    for index, coefficients in enumerate(coefficient_masks):
        p = polynomial_of_a(coefficients, a)
        t = random_encoding(generator, 64 + index % 97)
        label = (
            "P=I" if coefficients == 1 else
            "P=A+I" if coefficients == 0b11 else
            f"P-mask-{coefficients:08x}"
        )
        cases.append(verify_case(label=label, t=t, p=p, a=a, seeds=seeds))

    certificate = {
        "schema": 1,
        "status": "verified",
        "theorem": "invertible commuting P is gauge-equivalent to P=I via U=T*P",
        "symbolic_identities": [
            "U=T*P",
            "T*A*T^-1=U*A*U^-1 because P*A=A*P",
            "T*P=U",
            "(A+I)*P^-1*T^-1=(A+I)*U^-1",
            "U*C=B+I",
            "q'=q+U*y where y=C*q+seed",
        ],
        "protocol": {
            "state": "q'=B*q+D*seed",
            "output": "y=C*q+seed",
            "initial_state": 0,
            "checked_ticks": [1, 65],
            "full_space_proof": "seed-to-output matrix equals A^tick for every tick",
        },
        "verification": {
            "polynomial_cases": len(cases),
            "random_polynomial_cases": args.random_polynomials,
            "coefficient_draw_attempts": attempts,
            "unit_seeds_per_case": N,
            "random_seeds_per_case": args.random_seeds,
            "value_replays": len(cases) * (N + args.random_seeds) * 65,
            "all_2^32_seeds": True,
            "prng_seed": f"0x{args.seed:x}",
        },
        "A_sha256": sha256_matrices((a,)),
        "cases": cases,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(certificate, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": certificate["status"],
                "polynomial_cases": len(cases),
                "value_replays": certificate["verification"]["value_replays"],
                "output": str(args.output),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
