#!/usr/bin/env python3
"""Construct and verify a sparse Galois form similar to xorshift32.

This is a research-only GF(2) calculation.  It does not import any save/game
module and only writes the optional JSON certificate selected by ``--output``.

Matrices are tuples of row masks and act on column vectors.  With

    P = [v, A*v, ..., A^31*v]

the encoded coordinate is q=P^-1*x and B=P^-1*A*P is the (column) companion,
also called the Galois LFSR form in this orientation.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import random
from typing import Callable, Sequence


BITS = 32
MASK = (1 << BITS) - 1
IDENTITY = tuple(1 << bit for bit in range(BITS))


def xorshift32(value: int) -> int:
    value ^= value >> 13
    value &= MASK
    value ^= (value << 17) & MASK
    value &= MASK
    value ^= value >> 5
    return value & MASK


def matrix_from_function(function: Callable[[int], int]) -> tuple[int, ...]:
    return tuple(
        sum(
            ((function(1 << source) >> target) & 1) << source
            for source in range(BITS)
        )
        for target in range(BITS)
    )


def rows_from_columns(columns: Sequence[int]) -> tuple[int, ...]:
    if len(columns) != BITS:
        raise ValueError(f"expected {BITS} columns")
    return tuple(
        sum(((columns[source] >> target) & 1) << source for source in range(BITS))
        for target in range(BITS)
    )


def apply_matrix(matrix: Sequence[int], value: int) -> int:
    return sum(
        ((row & value).bit_count() & 1) << target
        for target, row in enumerate(matrix)
    )


def apply_row(row: int, matrix: Sequence[int]) -> int:
    result = 0
    while row:
        low = row & -row
        result ^= matrix[low.bit_length() - 1]
        row ^= low
    return result


def compose(left: Sequence[int], right: Sequence[int]) -> tuple[int, ...]:
    return tuple(apply_row(row, right) for row in left)


def invert(matrix: Sequence[int]) -> tuple[int, ...]:
    rows = [matrix[index] | ((1 << index) << BITS) for index in range(BITS)]
    for column in range(BITS):
        pivot = next(
            (index for index in range(column, BITS) if rows[index] >> column & 1),
            None,
        )
        if pivot is None:
            raise ValueError("singular matrix")
        rows[column], rows[pivot] = rows[pivot], rows[column]
        for index in range(BITS):
            if index != column and rows[index] >> column & 1:
                rows[index] ^= rows[column]
    return tuple((row >> BITS) & MASK for row in rows)


def matrix_stats(matrix: Sequence[int]) -> dict[str, object]:
    weights = tuple(row.bit_count() for row in matrix)
    return {
        "ones": sum(weights),
        "row_weight_histogram": {
            str(weight): count for weight, count in sorted(Counter(weights).items())
        },
        "maximum_row_weight": max(weights),
        "independent_row_xor2_upper_bound": sum(max(0, weight - 1) for weight in weights),
    }


def digest(*matrices: Sequence[int]) -> str:
    data = b"".join(
        row.to_bytes(4, "little") for matrix in matrices for row in matrix
    )
    return hashlib.sha256(data).hexdigest()


def build_certificate() -> dict[str, object]:
    a = matrix_from_function(xorshift32)

    # e0 is a cyclic vector: Gaussian inversion below proves that these 32
    # Krylov columns are independent.
    krylov_columns: list[int] = []
    value = 1
    for _ in range(BITS):
        krylov_columns.append(value)
        value = xorshift32(value)
    p = rows_from_columns(krylov_columns)
    p_inverse = invert(p)

    # Express A^32*v in the Krylov basis.  This is the lower-coefficient
    # bitmask of the monic characteristic/minimal polynomial over GF(2).
    coefficients = apply_matrix(p_inverse, value)
    polynomial = (1 << BITS) | coefficients
    b = compose(compose(p_inverse, a), p)
    c = compose(a, p)
    tick0_feedback = compose(p_inverse, a)

    expected_columns = tuple(
        [*(1 << (index + 1) for index in range(BITS - 1)), coefficients]
    )
    expected_b = rows_from_columns(expected_columns)

    if compose(p, p_inverse) != IDENTITY or compose(p_inverse, p) != IDENTITY:
        raise AssertionError("P inverse check failed")
    if b != expected_b:
        raise AssertionError("similarity is not the expected Galois companion")
    if compose(p, b) != compose(a, p):
        raise AssertionError("A*P != P*B")

    # Cayley-Hamilton on every basis vector, evaluated by repeated A action.
    for source in range(BITS):
        powers = []
        state = 1 << source
        for _ in range(BITS + 1):
            powers.append(state)
            state = xorshift32(state)
        total = powers[BITS]
        for exponent in range(BITS):
            if coefficients >> exponent & 1:
                total ^= powers[exponent]
        if total:
            raise AssertionError(f"characteristic polynomial failed at e{source}")

    seeds = [0, 1, 2, 0x12345678, MASK]
    generator = random.Random(0xA5C65)
    seeds.extend(generator.getrandbits(BITS) for _ in range(64))
    for seed in seeds:
        q = apply_matrix(p_inverse, seed)
        natural = seed
        for _ in range(65):
            natural = xorshift32(natural)
            if apply_matrix(c, q) != natural:
                raise AssertionError("decoded output mismatch")
            q = apply_matrix(b, q)
            if apply_matrix(p, q) != natural:
                raise AssertionError("encoded-state invariant mismatch")

    taps = tuple(index for index in range(BITS) if coefficients >> index & 1)
    xor_rows = tuple(index for index in taps if index != 0)
    if coefficients & 1 != 1:
        raise AssertionError("invertible transition must have constant coefficient one")
    if any(row.bit_count() > 2 for row in b):
        raise AssertionError("Galois row-support bound failed")
    if sum(row.bit_count() == 2 for row in b) != len(xor_rows):
        raise AssertionError("tap/XOR count mismatch")

    return {
        "schema": 1,
        "scope": "read-only GF(2) sparse-similarity certificate for xorshift32",
        "convention": "column vectors; q=P^-1*x; B=P^-1*A*P; C=A*P",
        "cyclic_vector": "00000001",
        "krylov_rank": BITS,
        "characteristic_polynomial_hex": f"{polynomial:09x}",
        "characteristic_polynomial_terms": [
            exponent for exponent in range(BITS + 1) if polynomial >> exponent & 1
        ],
        "characteristic_polynomial_weight": polynomial.bit_count(),
        "galois_feedback_coefficient_hex": f"{coefficients:08x}",
        "galois_tap_rows": list(taps),
        "galois_xor_rows": list(xor_rows),
        "steady_transition": {
            **matrix_stats(b),
            "xor2_gate_count": len(xor_rows),
            "xor_layers": 1,
            "rows_hex": [f"{row:08x}" for row in b],
        },
        "basis_transform_context": {
            "P_natural_from_encoded": matrix_stats(p),
            "P_inverse_encoded_from_natural": matrix_stats(p_inverse),
            "C_equals_A_times_P": matrix_stats(c),
            "tick0_feedback_equals_P_inverse_times_A": matrix_stats(tick0_feedback),
            "note": "dense context maps are not included in the 9-XOR transition count",
        },
        "verified_sequences": {"seed_count": len(seeds), "outputs_per_seed": 65},
        "matrix_sha256": digest(a, p, p_inverse, b, c, tick0_feedback),
        "P_rows_hex": [f"{row:08x}" for row in p],
        "P_inverse_rows_hex": [f"{row:08x}" for row in p_inverse],
    }


def verify_certificate(saved: dict[str, object]) -> None:
    rebuilt = build_certificate()
    if saved != rebuilt:
        raise AssertionError("saved certificate differs from rebuilt result")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify-existing", type=Path)
    args = parser.parse_args()

    if args.verify_existing:
        saved = json.loads(args.verify_existing.read_text(encoding="utf-8"))
        verify_certificate(saved)
        print(f"verified {args.verify_existing}")
        return 0

    certificate = build_certificate()
    encoded = json.dumps(certificate, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="ascii")
    print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
