#!/usr/bin/env python3
"""Audit full-seed linear and phase-linear RNG implementations over GF(2).

This replaces the retracted fixed-sample DFA experiment.  It never reads a
player save and does not start the game.  Every functional identity is checked
on all 32 unit seeds, which is exhaustive for the linear maps involved.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
from typing import Iterable, Sequence


BITS = 32
OUTPUT_COUNT = 65
MASK = (1 << BITS) - 1
IDENTITY = tuple(1 << bit for bit in range(BITS))


def xorshift32(value: int) -> int:
    value &= MASK
    value ^= value >> 13
    value &= MASK
    value ^= (value << 17) & MASK
    value &= MASK
    value ^= value >> 5
    return value & MASK


def matrix_from_function() -> tuple[int, ...]:
    columns = tuple(xorshift32(1 << source) for source in range(BITS))
    return tuple(
        sum(((columns[source] >> output) & 1) << source for source in range(BITS))
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
    return sum(
        ((row & value).bit_count() & 1) << output
        for output, row in enumerate(matrix)
    )


def compose(left: Sequence[int], right: Sequence[int]) -> tuple[int, ...]:
    return tuple(apply_row(row, right) for row in left)


def flatten(matrix: Sequence[int]) -> int:
    return sum(row << (BITS * output) for output, row in enumerate(matrix))


def matrix_sha256(matrix: Sequence[int]) -> str:
    payload = b"".join(row.to_bytes(BITS // 8, "little") for row in matrix)
    return sha256(payload).hexdigest()


def gf2_rank(values: Iterable[int]) -> int:
    pivots: dict[int, int] = {}
    for original in values:
        value = original
        while value:
            pivot = value.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = value
                break
            value ^= pivots[pivot]
    return len(pivots)


def build_solver(basis: Sequence[int]) -> dict[int, tuple[int, int]]:
    pivots: dict[int, tuple[int, int]] = {}
    for index, original in enumerate(basis):
        value = original
        combination = 1 << index
        while value:
            pivot = value.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = (value, combination)
                break
            prior_value, prior_combination = pivots[pivot]
            value ^= prior_value
            combination ^= prior_combination
        if value == 0:
            raise ValueError("basis is linearly dependent")
    return pivots


def solve_span(
    pivots: dict[int, tuple[int, int]], target: int
) -> int:
    combination = 0
    value = target
    while value:
        pivot = value.bit_length() - 1
        if pivot not in pivots:
            raise ValueError("target is outside the supplied span")
        prior_value, prior_combination = pivots[pivot]
        value ^= prior_value
        combination ^= prior_combination
    return combination


def polynomial_mod(value: int, modulus: int) -> int:
    modulus_degree = modulus.bit_length() - 1
    while value and value.bit_length() - 1 >= modulus_degree:
        value ^= modulus << (value.bit_length() - 1 - modulus_degree)
    return value


def polynomial_gcd(left: int, right: int) -> int:
    while right:
        left, right = right, polynomial_mod(left, right)
    return left


def polynomial_multiply_mod(left: int, right: int, modulus: int) -> int:
    result = 0
    while right:
        if right & 1:
            result ^= left
        right >>= 1
        left <<= 1
    return polynomial_mod(result, modulus)


def polynomial_power_mod(value: int, exponent: int, modulus: int) -> int:
    result = 1
    while exponent:
        if exponent & 1:
            result = polynomial_multiply_mod(result, value, modulus)
        value = polynomial_multiply_mod(value, value, modulus)
        exponent >>= 1
    return result


def powers_of_a(a: Sequence[int]) -> tuple[tuple[int, ...], ...]:
    powers = [IDENTITY]
    for _ in range(OUTPUT_COUNT):
        powers.append(compose(a, powers[-1]))
    return tuple(powers)


def build_certificate() -> dict[str, object]:
    a = matrix_from_function()
    powers = powers_of_a(a)

    unit_checks = 0
    for exponent, matrix in enumerate(powers[1:], start=1):
        for source in range(BITS):
            expected = 1 << source
            for _ in range(exponent):
                expected = xorshift32(expected)
            actual = apply_matrix(matrix, 1 << source)
            if actual != expected:
                raise AssertionError(
                    f"A^{exponent} unit seed {source} mismatch: "
                    f"{actual:08x} != {expected:08x}"
                )
            unit_checks += 1

    plus_identity = []
    for exponent, matrix in enumerate(powers[1:], start=1):
        difference = tuple(
            row ^ IDENTITY[index] for index, row in enumerate(matrix)
        )
        plus_identity.append(
            {
                "p": exponent,
                "rank": gf2_rank(difference),
                "sha256": matrix_sha256(difference),
            }
        )
    if any(item["rank"] != BITS for item in plus_identity):
        raise AssertionError("an A^p + I matrix unexpectedly lost rank")

    krylov = [1]
    for _ in range(BITS):
        krylov.append(apply_matrix(a, krylov[-1]))
    krylov_solver = build_solver(krylov[:BITS])
    characteristic_coefficients = solve_span(krylov_solver, krylov[BITS])
    characteristic = (1 << BITS) | characteristic_coefficients
    for source in range(BITS):
        values = [1 << source]
        for _ in range(BITS):
            values.append(apply_matrix(a, values[-1]))
        annihilated = values[BITS]
        for exponent in range(BITS):
            if characteristic_coefficients >> exponent & 1:
                annihilated ^= values[exponent]
        if annihilated:
            raise AssertionError("characteristic relation failed on a unit seed")
    x = 0b10
    irreducible_checks = {
        "x_to_2^32_mod_p": polynomial_power_mod(x, 1 << BITS, characteristic),
        "gcd_p_x_to_2^16_plus_x": polynomial_gcd(
            characteristic,
            polynomial_power_mod(x, 1 << (BITS // 2), characteristic) ^ x,
        ),
    }
    if irreducible_checks != {
        "x_to_2^32_mod_p": x,
        "gcd_p_x_to_2^16_plus_x": 1,
    }:
        raise AssertionError("degree-32 characteristic polynomial is reducible")

    flattened = tuple(flatten(matrix) for matrix in powers[1:])
    slice_rank = gf2_rank(flattened)
    if slice_rank != BITS:
        raise AssertionError(f"unexpected power-slice rank {slice_rank}")

    basis = flattened[:BITS]
    if gf2_rank(basis) != BITS:
        raise AssertionError("A^1 through A^32 must be an independent basis")
    solver = build_solver(basis)
    coefficients = tuple(solve_span(solver, matrix) for matrix in flattened)
    for phase, coefficient in enumerate(coefficients):
        rebuilt = 0
        for index, matrix in enumerate(basis):
            if coefficient >> index & 1:
                rebuilt ^= matrix
        if rebuilt != flattened[phase]:
            raise AssertionError(f"power coefficient reconstruction failed at {phase}")

    phase_functions = tuple(
        sum(((coefficient >> basis_index) & 1) << phase
            for phase, coefficient in enumerate(coefficients))
        for basis_index in range(BITS)
    )
    if gf2_rank(phase_functions) != BITS:
        raise AssertionError("phase coefficient functions unexpectedly lost rank")

    protocol_periods = [
        item for item in plus_identity if int(item["p"]) < OUTPUT_COUNT
    ]
    return {
        "schema": 1,
        "scope": "all 2^32 seeds; linear identities certified on all 32 unit seeds",
        "transition": "x ^= x >> 13; x ^= (x << 17) & 0xffffffff; x ^= x >> 5",
        "matrix": {
            "A_sha256": matrix_sha256(a),
            "A_rank": gf2_rank(a),
            "A_rows_hex": [f"{row:08x}" for row in a],
            "unit_basis_power_checks": unit_checks,
            "characteristic_polynomial_hex": f"0x{characteristic:x}",
            "characteristic_polynomial_irreducible": True,
            "irreducibility_checks_hex": {
                key: f"0x{value:x}" for key, value in irreducible_checks.items()
            },
        },
        "arbitrary_boolean_one_time_input_bound": {
            "seed_domain_size": 1 << BITS,
            "data_state_bit_lower_bound": BITS,
            "proof": (
                "After the input closes, the first required output A*seed is a "
                "bijection. Therefore two seeds cannot share the same internal "
                "state before that output, independent of linearity."
            ),
            "including_pre_output_phase_state_count_lower_bound": (1 << BITS) + 1,
            "including_pre_output_phase_bit_lower_bound": BITS + 1,
            "phase_proof": (
                "A pre-output state with output disabled must differ from every "
                "loaded state when all controls are internal and seed is closed."
            ),
            "boundary": (
                "Persistent seed access invalidates this counting bound; a phase-"
                "specific combinational decoder may then use fewer data bits."
            ),
        },
        "periodic_linear_state_bound": {
            "algebra": "rank(A^p + I)",
            "all_algebraic_results_p_1_through_65": plus_identity,
            "protocol_applicable_periods": [1, OUTPUT_COUNT - 1],
            "protocol_applicable_all_full_rank": all(
                item["rank"] == BITS for item in protocol_periods
            ),
            "data_state_bit_lower_bound": BITS,
            "reason": (
                "At two required output ticks with the same phase, the direct "
                "seed term cancels. The output difference factors through the "
                "data-state difference, while A^t(A^p+I) has rank 32."
            ),
            "period_65_boundary": (
                "rank(A^65+I)=32 is an algebraic fact, but 65 required outputs "
                "contain no repeated phase for a 65-phase machine, so this "
                "finite protocol alone gives no p=65 data-state lower bound."
            ),
        },
        "phase_seed_linear_separation": {
            "tensor_flattening": "65 phases by 1024 output/seed matrix entries",
            "rank": slice_rank,
            "lower_bound_terms": slice_rank,
            "matching_basis": "A^1 through A^32",
            "power_coefficient_masks_hex": [
                f"{coefficient:08x}" for coefficient in coefficients
            ],
            "power_coefficient_weights": [
                coefficient.bit_count() for coefficient in coefficients
            ],
            "phase_function_masks_65bit_hex": [
                f"{function:017x}" for function in phase_functions
            ],
            "phase_function_weights": [
                function.bit_count() for function in phase_functions
            ],
            "interpretation": (
                "Any identity y(phase,seed)=XOR_i g_i(phase)*M_i(seed) with "
                "fixed word-linear M_i needs at least 32 nonzero gated terms."
            ),
            "physical_limit": (
                "This is a lower bound for the separated feed-forward family, "
                "not a global lower bound for arbitrary stateful tri-state circuits."
            ),
            "minimal_term_map_property": (
                "The power slices form the 32-dimensional field GF(2)[A]. "
                "Irreducibility makes every nonzero map in this slice space "
                "invertible. Hence every map in a minimal 32-term separated "
                "decomposition is a full-rank 32-bit transform."
            ),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = build_certificate()
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        print(encoded, end="")
    else:
        args.output.write_text(encoded, encoding="utf-8")
        print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
