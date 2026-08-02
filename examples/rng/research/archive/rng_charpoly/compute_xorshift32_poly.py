#!/usr/bin/env python3
"""Compute the GF(2) polynomials of the live RNG xorshift32 map.

The transition is the one in ``campaign/rng/test.si``::

    x ^= x >> 13; x ^= (x << 17) & 0xffffffff; x ^= x >> 5

This file intentionally uses only the Python standard library.  It computes
the characteristic polynomial twice by independent routes: a cyclic Krylov
relation (which also gives the minimal polynomial), and a polynomial Bareiss
determinant of ``x I + A``.  It then runs irreducibility and primitivity
tests in GF(2)[x].  No save or game state is read or changed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Iterable


N = 32
MASK = (1 << N) - 1
X = 0b10  # polynomial x; polynomial bit i is the coefficient of x**i
LIVE_TEST_SHA256 = "b396a9d5bba76bec2ceb123478dadc4616b6057894f17775982ed097c62fd50c"


def xorshift32(value: int) -> int:
    """The exact U32 transition, with truncation after each shear."""

    value &= MASK
    value ^= value >> 13
    value &= MASK
    value ^= (value << 17) & MASK
    value &= MASK
    value ^= value >> 5
    return value & MASK


def matrix_columns() -> tuple[int, ...]:
    """Return A's columns as 32-bit words (source bit -> output word)."""

    return tuple(xorshift32(1 << source) for source in range(N))


def matrix_rows(columns: Iterable[int]) -> tuple[int, ...]:
    columns = tuple(columns)
    return tuple(
        sum(((columns[source] >> output) & 1) << source for source in range(N))
        for output in range(N)
    )


def degree(value: int) -> int:
    return value.bit_length() - 1


def poly_mul(left: int, right: int) -> int:
    result = 0
    while right:
        if right & 1:
            result ^= left
        right >>= 1
        left <<= 1
    return result


def poly_divmod(numerator: int, denominator: int) -> tuple[int, int]:
    if denominator == 0:
        raise ZeroDivisionError("polynomial division by zero")
    quotient = 0
    remainder = numerator
    denominator_degree = degree(denominator)
    while remainder and degree(remainder) >= denominator_degree:
        shift = degree(remainder) - denominator_degree
        quotient ^= 1 << shift
        remainder ^= denominator << shift
    return quotient, remainder


def poly_div_exact(numerator: int, denominator: int) -> int:
    quotient, remainder = poly_divmod(numerator, denominator)
    if remainder:
        raise AssertionError(
            f"non-exact GF(2) Bareiss division: {numerator:#x} / {denominator:#x}"
        )
    return quotient


def poly_mod(numerator: int, modulus: int) -> int:
    return poly_divmod(numerator, modulus)[1]


def poly_mul_mod(left: int, right: int, modulus: int) -> int:
    return poly_mod(poly_mul(left, right), modulus)


def poly_pow_mod(base: int, exponent: int, modulus: int) -> int:
    result = 1
    base = poly_mod(base, modulus)
    while exponent:
        if exponent & 1:
            result = poly_mul_mod(result, base, modulus)
        exponent >>= 1
        base = poly_mul_mod(base, base, modulus)
    return result


def poly_gcd(left: int, right: int) -> int:
    while right:
        left, right = right, poly_mod(left, right)
    return left


def gf2_rank(words: Iterable[int]) -> int:
    basis = [0] * N
    rank = 0
    for value in words:
        value &= MASK
        while value:
            pivot = value.bit_length() - 1
            if basis[pivot]:
                value ^= basis[pivot]
            else:
                basis[pivot] = value
                rank += 1
                break
    return rank


def krylov_minimal_polynomial(columns: tuple[int, ...]) -> tuple[int, int, int]:
    """Return (polynomial, cyclic-rank, first-cyclic-vector).

    The vector e_0 is used.  If e_0 is cyclic, expressing A**32 e_0 in the
    first 32 Krylov vectors gives the monic degree-32 annihilator.  Since the
    vectors form a basis, that annihilator is both the minimal and
    characteristic polynomial.
    """

    def apply(value: int) -> int:
        result = 0
        while value:
            low = value & -value
            result ^= columns[low.bit_length() - 1]
            value ^= low
        return result

    vectors = []
    value = 1
    for _ in range(N + 1):
        vectors.append(value)
        value = apply(value)
    rank = gf2_rank(vectors[:N])
    if rank != N:
        raise AssertionError(f"e0 is not cyclic (Krylov rank {rank})")

    # Solve [v0 ... v31] * coefficients = v32 over GF(2).
    rows = []
    for output_bit in range(N):
        row = sum(
            ((vectors[source] >> output_bit) & 1) << source
            for source in range(N)
        )
        row |= ((vectors[N] >> output_bit) & 1) << N
        rows.append(row)
    row_index = 0
    pivots: list[int] = []
    for column in range(N):
        pivot = next(
            (index for index in range(row_index, N) if (rows[index] >> column) & 1),
            None,
        )
        if pivot is None:
            continue
        rows[row_index], rows[pivot] = rows[pivot], rows[row_index]
        for index in range(N):
            if index != row_index and ((rows[index] >> column) & 1):
                rows[index] ^= rows[row_index]
        pivots.append(column)
        row_index += 1
    if row_index != N or pivots != list(range(N)):
        raise AssertionError(f"Krylov solve did not reach full rank: {pivots}")
    coefficients = sum(((rows[row] >> N) & 1) << pivots[row] for row in range(N))
    return (1 << N) | coefficients, rank, vectors[N]


def characteristic_bareiss(columns: tuple[int, ...]) -> int:
    """Compute det(xI+A) using fraction-free polynomial Bareiss elimination."""

    # In characteristic two, xI-A == xI+A, so this is det(xI-A).
    matrix = [
        [X if row == column else 0 for column in range(N)]
        for row in range(N)
    ]
    for row in range(N):
        for column in range(N):
            if (columns[column] >> row) & 1:
                matrix[row][column] ^= 1

    previous = 1
    for pivot_index in range(N - 1):
        pivot = next(
            (
                row
                for row in range(pivot_index, N)
                if matrix[row][pivot_index] != 0
            ),
            None,
        )
        if pivot is None:
            raise AssertionError(f"singular polynomial pivot at {pivot_index}")
        if pivot != pivot_index:
            matrix[pivot_index], matrix[pivot] = matrix[pivot], matrix[pivot_index]
        pivot_value = matrix[pivot_index][pivot_index]
        for row in range(pivot_index + 1, N):
            left = matrix[row][pivot_index]
            for column in range(pivot_index + 1, N):
                numerator = poly_mul(matrix[row][column], pivot_value)
                numerator ^= poly_mul(left, matrix[pivot_index][column])
                matrix[row][column] = poly_div_exact(numerator, previous)
            matrix[row][pivot_index] = 0
        previous = pivot_value
    return matrix[N - 1][N - 1]


def polynomial_terms(polynomial: int) -> str:
    terms = []
    for exponent in range(degree(polynomial), -1, -1):
        if not (polynomial >> exponent) & 1:
            continue
        if exponent == 0:
            terms.append("1")
        elif exponent == 1:
            terms.append("x")
        else:
            terms.append(f"x^{exponent}")
    return " + ".join(terms)


def source_evidence(path: Path | None) -> dict[str, object]:
    if path is None:
        return {"path": None, "checked": False}
    blob = path.read_bytes()
    observed = hashlib.sha256(blob).hexdigest()
    text = blob.decode("utf-8")
    required = (
        "var result = ((seed >> 13) ^ seed) & 0xffffffff",
        "result = ((result << 17) ^ result) & 0xffffffff",
        "result = ((result >> 5) ^ result) & 0xffffffff",
    )
    missing = [fragment for fragment in required if fragment not in text]
    if missing:
        raise AssertionError(f"live RNG script does not contain expected transform: {missing}")
    return {
        "path": str(path),
        "sha256": observed,
        "expected_sha256": LIVE_TEST_SHA256,
        "hash_matches_certificate": observed == LIVE_TEST_SHA256,
        "formula_fragments_present": True,
    }


def certificate(source_path: Path | None = None) -> dict[str, object]:
    columns = matrix_columns()
    rows = matrix_rows(columns)
    minimal, krylov_rank, target = krylov_minimal_polynomial(columns)
    characteristic = characteristic_bareiss(columns)
    if minimal != characteristic:
        raise AssertionError(
            f"Krylov and determinant polynomials differ: {minimal:#x} != {characteristic:#x}"
        )
    polynomial = characteristic

    # Rabin's irreducibility criterion.  Checking all i <= n/2 is redundant
    # but leaves explicit witnesses for every possible small factor degree.
    frobenius = X
    gcd_witnesses = []
    for i in range(1, N + 1):
        frobenius = poly_mul_mod(frobenius, frobenius, polynomial)
        if i <= N // 2:
            witness = poly_gcd(frobenius ^ X, polynomial)
            gcd_witnesses.append({"i": i, "gcd_hex": hex(witness)})
            if witness != 1:
                raise AssertionError(f"reducible polynomial; gcd at i={i}: {witness:#x}")
    if frobenius != X:
        raise AssertionError(f"x^(2^32) != x modulo p: {frobenius:#x}")

    order = (1 << N) - 1
    prime_factors = (3, 5, 17, 257, 65537)
    if order != 3 * 5 * 17 * 257 * 65537:
        raise AssertionError("incorrect factorization of 2^32-1")
    order_witnesses = {
        str(q): hex(poly_pow_mod(X, order // q, polynomial))
        for q in prime_factors
    }
    if any(int(value, 16) == 1 for value in order_witnesses.values()):
        raise AssertionError(f"x does not have full order: {order_witnesses}")
    full_order_residue = poly_pow_mod(X, order, polynomial)
    if full_order_residue != 1:
        raise AssertionError(f"x^({order}) != 1 modulo p: {full_order_residue:#x}")

    return {
        "transition": "x ^= x >> 13; x ^= (x << 17) & 0xffffffff; x ^= x >> 5",
        "matrix_convention": "A columns are xorshift32(1 << source_bit), bit 0 is LSB",
        "matrix_columns_hex": [f"{value:08x}" for value in columns],
        "matrix_rows_hex": [f"{value:08x}" for value in rows],
        "krylov": {
            "seed_vector_hex": "00000001",
            "rank": krylov_rank,
            "a32_seed_vector_hex": f"{target:08x}",
        },
        "polynomial_encoding": "bit i is coefficient of x^i over GF(2)",
        "characteristic_polynomial_hex": hex(characteristic),
        "minimal_polynomial_hex": hex(minimal),
        "polynomial": polynomial_terms(polynomial),
        "factorization": [{"factor": polynomial_terms(polynomial), "multiplicity": 1}],
        "irreducible": True,
        "rabin_gcd_witnesses": gcd_witnesses,
        "group_order": order,
        "group_order_prime_factors": list(prime_factors),
        "primitive": True,
        "order_witnesses_x_to_(2^32-1)/q": order_witnesses,
        "x_to_(2^32-1)_mod_p_hex": hex(full_order_residue),
        "source": source_evidence(source_path),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--test-script", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = certificate(args.test_script)
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        print(encoded, end="")
    else:
        args.output.write_text(encoded, encoding="utf-8")
        print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
