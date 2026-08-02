#!/usr/bin/env python3
"""Audit a 12-bit affine-LFSR phase encoding for all-seed RNG synthesis.

The script never reads a save or starts the game.  It works on the exact 65
power slices of xorshift32 and verifies all linear identities on GF(2)
bit-vectors.  Degree-two phase interpolation is exhaustive because the feature
matrix has only 79 columns and a 14-dimensional nullspace.
"""

from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
from typing import Iterable, Sequence

from full_space_linear_audit import (
    BITS,
    OUTPUT_COUNT,
    build_solver,
    flatten,
    gf2_rank,
    matrix_from_function,
    powers_of_a,
    solve_span,
)


PHASE_BITS = 12
PHASE_MASK = (1 << PHASE_BITS) - 1
PRIMITIVE_POLYNOMIAL = 0x1053  # x^12 + x^6 + x^4 + x + 1
AFFINE_CONSTANT = 1
FEATURE_COUNT = 1 + PHASE_BITS + PHASE_BITS * (PHASE_BITS - 1) // 2


def polynomial_mod(value: int, modulus: int) -> int:
    degree = modulus.bit_length() - 1
    while value.bit_length() - 1 >= degree:
        value ^= modulus << (value.bit_length() - 1 - degree)
    return value


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


def lfsr_linear_step(state: int) -> int:
    carry = state >> (PHASE_BITS - 1)
    state = (state << 1) & PHASE_MASK
    if carry:
        state ^= PRIMITIVE_POLYNOMIAL & PHASE_MASK
    return state


def lfsr_affine_step(state: int) -> int:
    return lfsr_linear_step(state) ^ AFFINE_CONSTANT


def phase_trajectory(count: int) -> tuple[int, ...]:
    values = [0]
    for _ in range(count - 1):
        values.append(lfsr_affine_step(values[-1]))
    return tuple(values)


def feature_definitions() -> tuple[tuple[str, tuple[int, ...]], ...]:
    definitions: list[tuple[str, tuple[int, ...]]] = [("1", ())]
    definitions.extend((f"p{bit}", (bit,)) for bit in range(PHASE_BITS))
    definitions.extend(
        (f"p{left}*p{right}", (left, right))
        for left in range(PHASE_BITS)
        for right in range(left + 1, PHASE_BITS)
    )
    if len(definitions) != FEATURE_COUNT:
        raise AssertionError("feature count mismatch")
    return tuple(definitions)


def evaluate_feature(bits: tuple[int, ...], state: int) -> int:
    if not bits:
        return 1
    return int(all(state >> bit & 1 for bit in bits))


def feature_columns(
    trajectory: Sequence[int],
) -> tuple[tuple[str, tuple[int, ...], int], ...]:
    return tuple(
        (
            name,
            bits,
            sum(
                evaluate_feature(bits, state) << phase
                for phase, state in enumerate(trajectory)
            ),
        )
        for name, bits in feature_definitions()
    )


def build_full_column_solver(
    columns: Sequence[int],
) -> tuple[dict[int, tuple[int, int]], tuple[int, ...]]:
    pivots: dict[int, tuple[int, int]] = {}
    nullspace: list[int] = []
    for index, original in enumerate(columns):
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
        if not value:
            nullspace.append(combination)
    return pivots, tuple(nullspace)


def solve_columns(pivots: dict[int, tuple[int, int]], target: int) -> int:
    value = target
    combination = 0
    while value:
        pivot = value.bit_length() - 1
        if pivot not in pivots:
            raise ValueError("target is outside the feature span")
        prior_value, prior_combination = pivots[pivot]
        value ^= prior_value
        combination ^= prior_combination
    return combination


def xor_selected(columns: Sequence[int], selection: int) -> int:
    result = 0
    while selection:
        low = selection & -selection
        result ^= columns[low.bit_length() - 1]
        selection ^= low
    return result


def enumerate_coset(particular: int, nullspace: Sequence[int]) -> Iterable[int]:
    value = particular
    previous_gray = 0
    yield value
    for index in range(1, 1 << len(nullspace)):
        gray = index ^ (index >> 1)
        changed = gray ^ previous_gray
        value ^= nullspace[changed.bit_length() - 1]
        yield value
        previous_gray = gray


def balanced_arrival(selection: int, definitions: Sequence[tuple[int, ...]]) -> int:
    """Return the best naive XOR-tree arrival from registered phase bits.

    The constant com_on arrives at 0, Delay Bit outputs arrive at 4, and a
    quadratic monomial adds one AND delay.  Each U1 XOR adds two.  Combining
    the earliest pair first is optimal for equal-delay binary gates.
    """

    arrivals = []
    for index, bits in enumerate(definitions):
        if selection >> index & 1:
            arrivals.append(0 if not bits else 5 if len(bits) == 2 else 4)
    if not arrivals:
        return 0
    arrivals.sort()
    while len(arrivals) > 1:
        first = arrivals.pop(0)
        second = arrivals.pop(0)
        output = max(first, second) + 2
        insert = 0
        while insert < len(arrivals) and arrivals[insert] <= output:
            insert += 1
        arrivals.insert(insert, output)
    return arrivals[0]


def minimum_representations(
    particular: int,
    nullspace: Sequence[int],
    definitions: Sequence[tuple[int, ...]],
) -> tuple[dict[str, int], tuple[int, ...]]:
    best_weight = FEATURE_COUNT + 1
    best_quadratic = FEATURE_COUNT + 1
    best_arrival = 1 << 30
    best: list[int] = []
    quadratic_mask = sum(
        (len(bits) == 2) << index for index, bits in enumerate(definitions)
    )
    for selection in enumerate_coset(particular, nullspace):
        weight = selection.bit_count()
        quadratic = (selection & quadratic_mask).bit_count()
        arrival = balanced_arrival(selection, definitions)
        key = (weight, quadratic, arrival)
        current = (best_weight, best_quadratic, best_arrival)
        if key < current:
            best_weight, best_quadratic, best_arrival = key
            best = [selection]
        elif key == current:
            best.append(selection)
    return (
        {
            "term_count": best_weight,
            "quadratic_count": best_quadratic,
            "naive_xor_count": max(0, best_weight - 1),
            "naive_decoder_gate_count_excluding_shared_and": (
                3 * max(0, best_weight - 1)
            ),
            "naive_control_arrival_before_switch": best_arrival,
            "equally_optimal_count": len(best),
        },
        tuple(best),
    )


def phase_targets() -> tuple[int, ...]:
    powers = powers_of_a(matrix_from_function())
    flattened = tuple(flatten(matrix) for matrix in powers[1:])
    basis = flattened[:BITS]
    solver = build_solver(basis)
    coefficients = tuple(solve_span(solver, matrix) for matrix in flattened)
    return tuple(
        sum(
            ((coefficient >> basis_index) & 1) << phase
            for phase, coefficient in enumerate(coefficients)
        )
        for basis_index in range(BITS)
    )


def build_certificate() -> dict[str, object]:
    order = (1 << PHASE_BITS) - 1
    prime_divisors = (3, 5, 7, 13)
    primitive_checks = {
        "x_to_order": polynomial_power_mod(2, order, PRIMITIVE_POLYNOMIAL),
        **{
            f"x_to_order_over_{prime}": polynomial_power_mod(
                2, order // prime, PRIMITIVE_POLYNOMIAL
            )
            for prime in prime_divisors
        },
    }
    if primitive_checks["x_to_order"] != 1 or any(
        value == 1
        for key, value in primitive_checks.items()
        if key != "x_to_order"
    ):
        raise AssertionError("0x1053 is not primitive under this convention")

    full_trajectory = phase_trajectory(order + 1)
    if len(set(full_trajectory[:-1])) != order:
        raise AssertionError("affine phase trajectory is not maximal")
    if full_trajectory[-1] != 0:
        raise AssertionError("affine phase trajectory does not close at 4095")
    trajectory = full_trajectory[:OUTPUT_COUNT]
    if len(set(trajectory)) != OUTPUT_COUNT:
        raise AssertionError("the 65 protocol phases are not unique")

    features = feature_columns(trajectory)
    names = tuple(name for name, _, _ in features)
    definitions = tuple(bits for _, bits, _ in features)
    columns = tuple(column for _, _, column in features)
    pivots, nullspace = build_full_column_solver(columns)
    rank = len(pivots)
    if rank != OUTPUT_COUNT:
        raise AssertionError(f"degree-two phase feature rank is only {rank}")
    if len(nullspace) != FEATURE_COUNT - OUTPUT_COUNT:
        raise AssertionError("unexpected feature nullity")
    if any(xor_selected(columns, relation) for relation in nullspace):
        raise AssertionError("invalid feature nullspace relation")
    if gf2_rank(nullspace) != len(nullspace):
        raise AssertionError("feature nullspace relations are dependent")

    targets = phase_targets()
    if gf2_rank(targets) != BITS:
        raise AssertionError("target phase space lost rank")
    target_rows = []
    selected_representations = []
    for index, target in enumerate(targets):
        particular = solve_columns(pivots, target)
        if xor_selected(columns, particular) != target:
            raise AssertionError(f"target {index} particular solution failed")
        minimum, alternatives = minimum_representations(
            particular, nullspace, definitions
        )
        selection = min(alternatives)
        selected_representations.append(selection)
        target_rows.append(
            {
                "basis_index": index,
                "target_mask_65bit_hex": f"{target:017x}",
                **minimum,
                "selected_mask_79bit_hex": f"{selection:020x}",
                "selected_features": [
                    names[feature]
                    for feature in range(FEATURE_COUNT)
                    if selection >> feature & 1
                ],
            }
        )

    quadratic_indices = tuple(
        index for index, bits in enumerate(definitions) if len(bits) == 2
    )
    union = 0
    for selection in selected_representations:
        union |= selection
    shared_quadratic_count = sum(union >> index & 1 for index in quadratic_indices)
    naive_xors = sum(row["naive_xor_count"] for row in target_rows)
    naive_decoder_gate_count = shared_quadratic_count + 3 * naive_xors
    phase_state_gate_count = PHASE_BITS * 5
    phase_update_gate_count = 1 + 3 * 3  # NOT carry; three XOR taps

    feature_payload = b"".join(
        column.to_bytes((OUTPUT_COUNT + 7) // 8, "little") for column in columns
    )
    return {
        "schema": 1,
        "scope": "all 2^32 seeds; exact 65-phase GF(2) identities",
        "phase_generator": {
            "bits": PHASE_BITS,
            "primitive_polynomial_hex": f"0x{PRIMITIVE_POLYNOMIAL:x}",
            "affine_recurrence": "p' = (x*p mod polynomial) xor 1",
            "period": order,
            "first_65_unique": True,
            "first_65_states_hex": [f"{state:03x}" for state in trajectory],
            "primitive_checks_hex": {
                key: f"0x{value:x}" for key, value in primitive_checks.items()
            },
            "physical_update": {
                "delay_bits": PHASE_BITS,
                "delay_bit_gate_count": phase_state_gate_count,
                "not_count": 1,
                "u1_xor_count": 3,
                "combinational_gate_count": phase_update_gate_count,
                "total_gate_count": phase_state_gate_count
                + phase_update_gate_count,
                "maximum_feedback_arrival": 6,
            },
        },
        "degree_two_features": {
            "count": FEATURE_COUNT,
            "constant": 1,
            "linear": PHASE_BITS,
            "quadratic": len(quadratic_indices),
            "rank_on_65_phases": rank,
            "nullity": len(nullspace),
            "columns_sha256": sha256(feature_payload).hexdigest(),
            "nullspace_masks_79bit_hex": [
                f"{relation:020x}" for relation in nullspace
            ],
            "conclusion": (
                "Every Boolean function on these 65 exact phase points has a "
                "degree-at-most-two interpolation in the 12 registered bits."
            ),
        },
        "xorshift_power_phase_targets": {
            "rank": gf2_rank(targets),
            "targets": target_rows,
            "minimum_term_histogram": dict(
                sorted(Counter(row["term_count"] for row in target_rows).items())
            ),
            "selected_shared_quadratic_features": shared_quadratic_count,
            "selected_naive_u1_xor_count": naive_xors,
            "selected_naive_decoder_gate_count": naive_decoder_gate_count,
            "selected_maximum_control_arrival_before_switch": max(
                row["naive_control_arrival_before_switch"] for row in target_rows
            ),
        },
        "physical_interpretation": {
            "status": "mathematically expressive but physically noncompetitive in naive ANF form",
            "phase_shell_gate_count": phase_state_gate_count
            + phase_update_gate_count,
            "naive_phase_decoder_gate_count": naive_decoder_gate_count,
            "naive_shell_plus_decoder_gate_count": (
                phase_state_gate_count
                + phase_update_gate_count
                + naive_decoder_gate_count
            ),
            "omitted_costs": (
                "seed linear pre-processing, phase/seed products, output XOR "
                "network, I/O control, and layout"
            ),
            "boundary": (
                "This rejects only direct quadratic-ANF decoding. Shared "
                "multi-output DAGs, tri-state cancellation, or a different "
                "nonlinear sequential encoding remain open."
            ),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = build_certificate()
    encoded = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        print(encoded, end="")
    else:
        args.output.write_text(encoded, encoding="utf-8")
        print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
