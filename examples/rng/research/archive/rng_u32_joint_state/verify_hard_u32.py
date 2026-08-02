"""Verify the single-U32 RNG state-encoding boundary.

This research script is self-contained.  It does not import save-writing code,
open the game, or inspect player state.  The proof covers a 32-bit linear state
machine with no additional first-output phase state:

* tick 0 loads the raw U32 seed into the only 32-bit state register;
* every later tick uses the same linear feedback and output maps;
* a proposed steady encoding is q = T*x for invertible T.

Under those assumptions the raw-seed initialization map and encoded steady
map force T = I.  The remaining natural xorshift32 map has rows of weight up
to seven, so an XOR2-only network needs at least three XOR levels (delay 6).
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
from typing import Callable, Iterable, Sequence


BITS = 32
MASK = (1 << BITS) - 1
IDENTITY = tuple(1 << bit for bit in range(BITS))
DEFAULT_OUTPUT = Path(__file__).with_name("hard_u32_certificate.json")
TEST_SCRIPT_SHA256 = "B396A9D5BBA76BEC2CEB123478DADC4616B6057894F17775982ED097C62FD50C"


def xorshift32(value: int) -> int:
    value ^= value >> 13
    value &= MASK
    value ^= (value << 17) & MASK
    value &= MASK
    value ^= value >> 5
    return value & MASK


def matrix_from_function(function: Callable[[int], int]) -> tuple[int, ...]:
    columns = tuple(function(1 << source) for source in range(BITS))
    return tuple(
        sum(((columns[source] >> target) & 1) << source for source in range(BITS))
        for target in range(BITS)
    )


def apply_row(row: int, matrix: Sequence[int]) -> int:
    result = 0
    while row:
        bit = (row & -row).bit_length() - 1
        result ^= matrix[bit]
        row &= row - 1
    return result


def compose(left: Sequence[int], right: Sequence[int]) -> tuple[int, ...]:
    return tuple(apply_row(row, right) for row in left)


def invert(matrix: Sequence[int]) -> tuple[int, ...]:
    rows = [matrix[index] | ((1 << index) << BITS) for index in range(BITS)]
    for column in range(BITS):
        pivot = next(
            (index for index in range(column, BITS) if (rows[index] >> column) & 1),
            None,
        )
        if pivot is None:
            raise AssertionError("matrix is singular")
        rows[column], rows[pivot] = rows[pivot], rows[column]
        for index in range(BITS):
            if index != column and ((rows[index] >> column) & 1):
                rows[index] ^= rows[column]
    return tuple((row >> BITS) & MASK for row in rows)


INVERSE_TOKEN = {"A": "a", "a": "A", "T": "t", "t": "T"}


def inverse_word(word: Iterable[str]) -> tuple[str, ...]:
    return tuple(INVERSE_TOKEN[token] for token in reversed(tuple(word)))


def reduce_word(word: Iterable[str]) -> tuple[str, ...]:
    stack: list[str] = []
    for token in word:
        if stack and INVERSE_TOKEN[token] == stack[-1]:
            stack.pop()
        else:
            stack.append(token)
    return tuple(stack)


def xor_levels_for_weight(weight: int) -> int:
    levels = 0
    capacity = 1
    while capacity < weight:
        capacity *= 2
        levels += 1
    return levels


def build_certificate() -> dict[str, object]:
    matrix_a = matrix_from_function(xorshift32)
    weights = [row.bit_count() for row in matrix_a]
    heavy = [index for index, weight in enumerate(weights) if weight > 4]
    min_levels = [xor_levels_for_weight(weight) for weight in weights]

    # Mechanical free-group cancellation for
    #   T*A = T*A*T^-1.
    # Left multiplying both sides by (T*A)^-1 reduces the left side to I and
    # the right side to T^-1, hence T=I.
    ta = ("T", "A")
    steady = ("T", "A", "t")
    cancellation_prefix = inverse_word(ta)
    reduced_left = reduce_word((*cancellation_prefix, *ta))
    reduced_right = reduce_word((*cancellation_prefix, *steady))

    return {
        "schema": 1,
        "scope": {
            "architecture_input_count": 1,
            "architecture_input_width": 32,
            "architecture_output_count": 1,
            "architecture_output_width": 32,
            "input_drive_ticks": [0],
            "feedback_merge": "U32 before any splitter",
            "state_bits": 32,
            "extra_first_output_phase_state": False,
            "network_class": "time-invariant linear feedback/output maps",
        },
        "challenge_evidence": {
            "seed_expression": "1 + random(0xfffffffe)",
            "seed_domain_contains_all_basis_vectors": True,
            "test_script_sha256": TEST_SCRIPT_SHA256,
        },
        "encoding_theorem": {
            "initial_feedback_map": "T*A",
            "steady_feedback_map": "T*A*T^-1",
            "why_maps_are_equal": (
                "the same time-invariant feedback map is evaluated first on every "
                "basis seed and later on an invertible image of that basis"
            ),
            "left_cancel_word": list(cancellation_prefix),
            "reduced_initial_side": list(reduced_left),
            "reduced_steady_side": list(reduced_right),
            "conclusion": "T=I",
        },
        "natural_matrix": {
            "rows": [f"{row:08x}" for row in matrix_a],
            "invertible": True,
            "row_weights": weights,
            "weight_histogram": {
                str(weight): count for weight, count in sorted(Counter(weights).items())
            },
            "rows_above_depth2_xor2_support": heavy,
            "row_min_xor_levels": min_levels,
        },
        "cost_model": {
            "xor2_gate": 3,
            "xor2_delay": 2,
            "xor3_gate": 12,
            "xor3_delay": 2,
            "combination_budget": 201,
            "combination_delay_limit": 4,
            "fixed_state_delay_gate": 160,
            "fixed_word_switch_gate": 64,
            "fixed_ready_control_gate": 6,
        },
        "strict_xor2_bound": {
            "max_support_at_two_levels": 4,
            "rows_requiring_three_levels": len(heavy),
            "minimum_combination_delay": max(min_levels) * 2,
            "result": "UNSAT for XOR2-only delay<=4, regardless of gate budget",
        },
        "mixed_primitive_status": (
            "XOR3 can support up to nine leaves in two levels; a separate exact "
            "XOR2/XOR3 cost-cover search is required for the 201 budget"
        ),
    }


def verify_certificate(certificate: dict[str, object]) -> None:
    if certificate.get("schema") != 1:
        raise AssertionError("unsupported schema")
    scope = certificate["scope"]
    expected_scope = {
        "architecture_input_count": 1,
        "architecture_input_width": 32,
        "architecture_output_count": 1,
        "architecture_output_width": 32,
        "input_drive_ticks": [0],
        "feedback_merge": "U32 before any splitter",
        "state_bits": 32,
        "extra_first_output_phase_state": False,
        "network_class": "time-invariant linear feedback/output maps",
    }
    if scope != expected_scope:
        raise AssertionError("hard architecture scope changed")

    evidence = certificate["challenge_evidence"]
    if evidence["seed_expression"] != "1 + random(0xfffffffe)":
        raise AssertionError("seed expression changed")
    if evidence["test_script_sha256"] != TEST_SCRIPT_SHA256:
        raise AssertionError("test script hash changed")
    if not all(1 <= 1 << bit <= MASK for bit in range(BITS)):
        raise AssertionError("seed domain does not contain the GF(2) basis")

    theorem = certificate["encoding_theorem"]
    ta = ("T", "A")
    steady = ("T", "A", "t")
    prefix = inverse_word(ta)
    if theorem["left_cancel_word"] != list(prefix):
        raise AssertionError("cancellation prefix changed")
    if reduce_word((*prefix, *ta)):
        raise AssertionError("initial side did not cancel to identity")
    if reduce_word((*prefix, *steady)) != ("t",):
        raise AssertionError("steady side did not reduce to T^-1")
    if theorem["conclusion"] != "T=I":
        raise AssertionError("encoding conclusion changed")

    matrix_a = matrix_from_function(xorshift32)
    if compose(matrix_a, invert(matrix_a)) != IDENTITY:
        raise AssertionError("natural xorshift matrix is not invertible")
    natural = certificate["natural_matrix"]
    if natural["rows"] != [f"{row:08x}" for row in matrix_a]:
        raise AssertionError("natural matrix rows changed")
    weights = [row.bit_count() for row in matrix_a]
    if natural["row_weights"] != weights:
        raise AssertionError("row weights changed")
    histogram = {str(k): v for k, v in sorted(Counter(weights).items())}
    if natural["weight_histogram"] != histogram:
        raise AssertionError("weight histogram changed")
    heavy = [index for index, weight in enumerate(weights) if weight > 4]
    if natural["rows_above_depth2_xor2_support"] != heavy:
        raise AssertionError("heavy-row list changed")
    if len(heavy) != 15:
        raise AssertionError("expected 15 rows with support above four")
    levels = [xor_levels_for_weight(weight) for weight in weights]
    if max(levels) != 3:
        raise AssertionError("natural map XOR depth bound changed")
    bound = certificate["strict_xor2_bound"]
    if bound["max_support_at_two_levels"] != 4:
        raise AssertionError("depth-two support bound changed")
    if bound["rows_requiring_three_levels"] != len(heavy):
        raise AssertionError("three-level row count changed")
    if bound["minimum_combination_delay"] != 6:
        raise AssertionError("minimum XOR2 combination delay changed")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--verify-existing", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.verify_existing is not None:
        certificate = json.loads(args.verify_existing.read_text(encoding="utf-8"))
        verify_certificate(certificate)
        print(f"verified {args.verify_existing}")
        return

    certificate = build_certificate()
    verify_certificate(certificate)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(certificate, indent=2) + "\n", encoding="utf-8")
    heavy = certificate["strict_xor2_bound"]["rows_requiring_three_levels"]
    print("single-U32 theorem: T=I")
    print(f"natural A: {heavy} rows require >=3 XOR2 levels")
    print("XOR2-only delay<=4: UNSAT")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
