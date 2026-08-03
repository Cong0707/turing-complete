#!/usr/bin/env python3
"""Prove that low-degree RNG features have no short global wire cycle.

The proof uses the exterior-power representation of the degree filtration of
the Boolean ring.  It is exact and does not access the game or player save.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
from itertools import combinations
import json
from math import gcd
from pathlib import Path
import struct
import sys


HERE = Path(__file__).resolve().parent
ROOT = next(parent for parent in HERE.parents if (parent / "pyproject.toml").exists())
sys.path.insert(0, str(ROOT))

from src.tc_save_lab.rng_encoded_asic import (  # noqa: E402
    A,
    B,
    IDENTITY,
    T,
    T_INVERSE,
    apply_matrix,
    compose,
)


BITS = 32
SINGER_ORDER = (1 << BITS) - 1
ORDER_PRIME_FACTORS = (3, 5, 17, 257, 65537)


def matrix_power(matrix: tuple[int, ...], exponent: int) -> tuple[int, ...]:
    result = IDENTITY
    factor = matrix
    while exponent:
        if exponent & 1:
            result = compose(factor, result)
        factor = compose(factor, factor)
        exponent >>= 1
    return result


def gf2_rank(vectors: list[int]) -> int:
    basis: dict[int, int] = {}
    for original in vectors:
        vector = original
        while vector:
            pivot = vector.bit_length() - 1
            previous = basis.get(pivot)
            if previous is None:
                basis[pivot] = vector
                break
            vector ^= previous
    return len(basis)


def coordinates_in_basis(vectors: list[int], target: int) -> int:
    basis: dict[int, tuple[int, int]] = {}
    for index, original in enumerate(vectors):
        vector = original
        coordinates = 1 << index
        while vector:
            pivot = vector.bit_length() - 1
            previous = basis.get(pivot)
            if previous is None:
                basis[pivot] = (vector, coordinates)
                break
            vector ^= previous[0]
            coordinates ^= previous[1]
    result = 0
    while target:
        pivot = target.bit_length() - 1
        previous = basis.get(pivot)
        if previous is None:
            raise AssertionError("target is outside the Krylov basis")
        target ^= previous[0]
        result ^= previous[1]
    return result


def krylov_certificate() -> dict[str, object]:
    vector = 1
    orbit: list[int] = []
    for _ in range(BITS):
        orbit.append(vector)
        vector = apply_matrix(A, vector)
    rank = gf2_rank(orbit)
    if rank != BITS:
        raise AssertionError("the chosen xorshift cyclic vector lost full rank")
    recurrence = coordinates_in_basis(orbit, vector)
    characteristic_polynomial = (1 << BITS) | recurrence
    blob = b"".join(struct.pack("<I", value) for value in orbit)
    return {
        "cyclic_vector_hex": "00000001",
        "krylov_rank": rank,
        "krylov_vectors_hex": [f"{value:08x}" for value in orbit],
        "next_vector_hex": f"{vector:08x}",
        "next_vector_krylov_coordinates_hex": f"{recurrence:08x}",
        "characteristic_polynomial_bits_hex": f"{characteristic_polynomial:09x}",
        "characteristic_polynomial_nonzero_degrees": [
            degree
            for degree in range(BITS + 1)
            if characteristic_polynomial >> degree & 1
        ],
        "krylov_vector_sha256": sha256(blob).hexdigest(),
    }


def exact_order_certificate() -> dict[str, object]:
    full_order_identity = matrix_power(A, SINGER_ORDER) == IDENTITY
    proper_factor_checks = {
        str(prime): matrix_power(A, SINGER_ORDER // prime) == IDENTITY
        for prime in ORDER_PRIME_FACTORS
    }
    if not full_order_identity or any(proper_factor_checks.values()):
        raise AssertionError("xorshift transition is no longer a Singer cycle")
    return {
        "claimed_order": SINGER_ORDER,
        "prime_factors": list(ORDER_PRIME_FACTORS),
        "power_at_claimed_order_is_identity": full_order_identity,
        "power_at_order_divided_by_prime_is_identity": proper_factor_checks,
        "exact_order_verified": True,
    }


def exponent_audit(maximum_degree: int, maximum_period: int) -> dict[str, object]:
    gcd_classes = sorted({gcd(period, SINGER_ORDER) for period in range(1, maximum_period + 1)})
    periods_by_class = {
        str(class_gcd): [
            period
            for period in range(1, maximum_period + 1)
            if gcd(period, SINGER_ORDER) == class_gcd
        ]
        for class_gcd in gcd_classes
    }

    enumeration_hash = sha256()
    counts_by_class = {
        class_gcd: [0] * (maximum_degree + 1)
        for class_gcd in gcd_classes
    }
    exponent_count = 0
    for degree in range(maximum_degree + 1):
        choices = [()] if degree == 0 else combinations(range(BITS), degree)
        for indices in choices:
            exponent = sum(1 << index for index in indices)
            flags = 0
            for class_index, class_gcd in enumerate(gcd_classes):
                if (class_gcd * exponent) % SINGER_ORDER == 0:
                    counts_by_class[class_gcd][degree] += 1
                    flags |= 1 << class_index
            enumeration_hash.update(struct.pack("<BII", degree, exponent, flags))
            exponent_count += 1

    class_records: list[dict[str, object]] = []
    for class_gcd in gcd_classes:
        step = SINGER_ORDER // class_gcd
        positive_multiples = [multiple * step for multiple in range(1, class_gcd)]
        minimum_weight = (
            min(value.bit_count() for value in positive_multiples)
            if positive_multiples
            else None
        )
        minimum_witnesses = (
            [f"{value:08x}" for value in positive_multiples if value.bit_count() == minimum_weight]
            if minimum_weight is not None
            else []
        )
        counts = counts_by_class[class_gcd]
        invariant_dimension = sum(counts)
        if invariant_dimension != 1 or counts[0] != 1:
            raise AssertionError(f"nonconstant low-degree invariant appeared for gcd {class_gcd}")
        class_records.append({
            "gcd_with_singer_order": class_gcd,
            "periods_at_most_bound": periods_by_class[str(class_gcd)],
            "generated_subgroup_order": SINGER_ORDER // class_gcd,
            "positive_fixed_exponent_step": step,
            "minimum_positive_fixed_exponent_hamming_weight": minimum_weight,
            "minimum_positive_fixed_exponent_witnesses_hex": minimum_witnesses,
            "fixed_exponent_count_by_exact_degree": counts,
            "invariant_dimension_through_maximum_degree": invariant_dimension,
        })

    return {
        "maximum_period": maximum_period,
        "gcd_classes": gcd_classes,
        "periods_by_gcd_class": periods_by_class,
        "maximum_anf_degree": maximum_degree,
        "low_weight_exponent_count": exponent_count,
        "low_weight_exponent_enumeration_sha256": enumeration_hash.hexdigest(),
        "classes": class_records,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--maximum-degree", type=int, default=4)
    parser.add_argument("--maximum-period", type=int, default=42)
    parser.add_argument(
        "--output",
        type=Path,
        default=HERE / "global_degree4_short_period_certificate.json",
    )
    args = parser.parse_args()
    if not 0 <= args.maximum_degree <= 8:
        raise SystemExit("maximum-degree must be in 0..8")
    if not 1 <= args.maximum_period < SINGER_ORDER:
        raise SystemExit("maximum-period must be in 1..2^32-2")
    if compose(T, compose(A, T_INVERSE)) != B:
        raise AssertionError("encoded-state conjugacy B=T*A*T^-1 changed")

    matrix_blob = b"".join(struct.pack("<I", row) for row in A)
    result = {
        "schema": 1,
        "scope": "all global Boolean ANF features through the requested degree",
        "natural_transition_rows_hex": [f"{row:08x}" for row in A],
        "natural_transition_sha256": sha256(matrix_blob).hexdigest(),
        "encoded_transition_is_linearly_conjugate": True,
        "krylov": krylov_certificate(),
        "order": exact_order_certificate(),
        "exterior_power_audit": exponent_audit(args.maximum_degree, args.maximum_period),
        "proof": (
            "The Boolean degree filtration has graded quotients exterior^d(V*). "
            "The generated subgroup has odd order, so Maschke splitting makes "
            "fixed-space dimensions additive across the filtration. A primitive "
            "degree-32 Singer cycle has eigenvalues alpha^(2^i); an exterior "
            "basis exponent s is fixed by A^L exactly when (2^32-1) divides L*s. "
            "The enumerated low-weight exponents leave only s=0, the constant."
        ),
        "conclusion": (
            f"every globally valid Boolean feature of ANF degree <= {args.maximum_degree} "
            f"with period <= {args.maximum_period} under A (and conjugate B) is constant"
        ),
        "limitations": (
            "does not exclude sample-only identities, degree above the bound, or cycles "
            "whose updates contain combinational gates"
        ),
        "script_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps({
        "exact_order_verified": result["order"]["exact_order_verified"],
        "gcd_classes": result["exterior_power_audit"]["gcd_classes"],
        "low_weight_exponent_count": result["exterior_power_audit"]["low_weight_exponent_count"],
        "invariant_dimensions": {
            str(record["gcd_with_singer_order"]): record["invariant_dimension_through_maximum_degree"]
            for record in result["exterior_power_audit"]["classes"]
        },
        "conclusion": result["conclusion"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
