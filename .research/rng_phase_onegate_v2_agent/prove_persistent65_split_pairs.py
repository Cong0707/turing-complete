#!/usr/bin/env python3
"""Prove that no 65-cycle final state/seed split is a cheap OR/Switch.

At reachable tick 1, every feedback and visible-output split consists of two
different nonzero linear forms of the seed.  Hence each split realizes all
four Boolean input combinations even when seed zero is excluded.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
from typing import Callable, Sequence


BITS = 32
MASK = (1 << BITS) - 1
IDENTITY = tuple(1 << bit for bit in range(BITS))


def xorshift32(value: int) -> int:
    value ^= value >> 13
    value ^= (value << 17) & MASK
    value ^= value >> 5
    return value & MASK


def transition() -> tuple[int, ...]:
    columns = tuple(xorshift32(1 << bit) for bit in range(BITS))
    return tuple(
        sum(((columns[source] >> target) & 1) << source for source in range(BITS))
        for target in range(BITS)
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


def rank(rows: Sequence[int]) -> int:
    basis = [0] * BITS
    result = 0
    for original in rows:
        row = original
        while row:
            pivot = row.bit_length() - 1
            if basis[pivot]:
                row ^= basis[pivot]
            else:
                basis[pivot] = row
                result += 1
                break
    return result


def pair_witnesses(left: int, right: int) -> dict[str, str]:
    if not left or not right or left == right:
        raise AssertionError("expected two independent GF(2) forms")
    signatures: dict[str, int] = {}
    for first in range(BITS):
        for second in range(first + 1, BITS):
            values = (1 << first, 1 << second, (1 << first) | (1 << second))
            observed = {
                f"{(left & seed).bit_count() & 1}{(right & seed).bit_count() & 1}": seed
                for seed in values
            }
            if all(key in observed for key in ("01", "10", "11")):
                signatures = observed
                break
        if signatures:
            break
    if not signatures:
        raise AssertionError("failed to find rank-two nonzero witnesses")

    # Rank two has a 30-dimensional common kernel.  Find an explicit nonzero
    # member so the certificate remains inside the live 1..0xffffffff domain.
    columns: dict[int, int] = {}
    kernel = 0
    for bit in range(BITS):
        signature = ((left >> bit & 1) << 1) | (right >> bit & 1)
        if signature == 0:
            kernel = 1 << bit
            break
        if signature in columns:
            kernel = (1 << columns[signature]) | (1 << bit)
            break
        columns[signature] = bit
    if not kernel:
        raise AssertionError("failed to construct a nonzero common-kernel witness")
    signatures["00"] = kernel
    result = {key: f"{signatures[key]:08x}" for key in ("00", "01", "10", "11")}
    for assignment, value in result.items():
        seed = int(value, 16)
        actual = f"{(left & seed).bit_count() & 1}{(right & seed).bit_count() & 1}"
        if seed == 0 or actual != assignment:
            raise AssertionError("stored witness failed replay")
    return result


def truth_table(function: Callable[[int, int], int]) -> int:
    return sum((function(a, b) & 1) << (2 * a + b) for a in range(2) for b in range(2))


def primitive_minimum() -> dict[str, object]:
    expressions = {0b0000: "0", 0b1111: "1", 0b1100: "a", 0b1010: "b"}
    costs = {function: 0 for function in expressions}

    def add(function: int, expression: str, cost: int) -> None:
        if function not in costs or cost < costs[function]:
            costs[function] = cost
            expressions[function] = expression

    for budget in range(1, 4):
        snapshot = tuple(costs.items())
        for function, cost in snapshot:
            if cost + 1 == budget:
                add(function ^ 0b1111, f"NOT({expressions[function]})", budget)
        snapshot = tuple(costs.items())
        for left, left_cost in snapshot:
            for right, right_cost in snapshot:
                if left_cost + right_cost + 1 != budget:
                    continue
                add(left & right, f"AND({expressions[left]},{expressions[right]})", budget)
                add(left | right, f"OR({expressions[left]},{expressions[right]})", budget)
                add((left & right) ^ 0b1111, f"NAND({expressions[left]},{expressions[right]})", budget)
                add((left | right) ^ 0b1111, f"NOR({expressions[left]},{expressions[right]})", budget)

    xor = truth_table(lambda left, right: left ^ right)
    if xor != 0b0110 or costs.get(xor) != 3:
        raise AssertionError("two-input XOR primitive minimum changed")
    return {
        "truth_table_order": ["00", "01", "10", "11"],
        "xor_table": f"{xor:04b}",
        "minimum_NOT_AND_OR_NAND_NOR_gate": costs[xor],
        "witness_expression": expressions[xor],
        "native_XOR": {"gate": 3, "delay": 2},
        "single_Bit_Switch": {"gate": 2, "delay": 1, "disabled_output": "Z"},
        "single_switch_is_not_active_binary_XOR": True,
        "two_switch_gate": 4,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    a = transition()
    a_plus_i = tuple(row ^ unit for row, unit in zip(a, IDENTITY, strict=True))
    a_squared = compose(a, a)
    identity_d = a_plus_i
    feedback_left = compose(identity_d, a)
    feedback_right = identity_d
    output_left = compose(a, a_plus_i)
    output_right = a

    if rank(a) != BITS or rank(a_plus_i) != BITS or rank(a_squared) != BITS:
        raise AssertionError("required xorshift matrix unexpectedly singular")

    feedback = []
    visible = []
    for bit in range(BITS):
        feedback.append({
            "bit": bit,
            "left": f"{feedback_left[bit]:08x}",
            "right": f"{feedback_right[bit]:08x}",
            "witness_seed": pair_witnesses(feedback_left[bit], feedback_right[bit]),
        })
        visible.append({
            "bit": bit,
            "left": f"{output_left[bit]:08x}",
            "right": f"{output_right[bit]:08x}",
            "witness_seed": pair_witnesses(output_left[bit], output_right[bit]),
        })

    payload = {
        "schema": 1,
        "status": "proved-local-split-bound",
        "model": "65-cycle persistent seed at reachable tick 1",
        "live_seed_domain": "1..0xffffffff",
        "global_argument": {
            "feedback_pair": "(D*A)_i and D_i",
            "feedback_difference": "(D*(A+I))_i",
            "output_pair": "(A*(A+I))_i and A_i",
            "output_difference": "(A^2)_i",
            "invertible_matrices": ["D", "A", "A+I", "A^2"],
            "consequence": (
                "For every invertible T and every bit, both forms are nonzero and unequal; "
                "over GF(2) they have rank two and realize all four assignments."
            ),
        },
        "representative": "T=I, D=A+I",
        "transition_sha256": sha256(
            b"".join(row.to_bytes(4, "little") for row in a)
        ).hexdigest(),
        "pair_count": len(feedback) + len(visible),
        "primitive_cost": primitive_minimum(),
        "feedback_pairs": feedback,
        "visible_pairs": visible,
        "scope": (
            "This excludes per-output replacement of the direct state/seed XOR by an OR, "
            "ordinary one/two-gate Boolean formula, or one isolated Bit Switch. It does not "
            "exclude a cross-output shared dual-rail or multi-driver Z network."
        ),
    }
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="ascii")
    print(json.dumps({
        "status": payload["status"],
        "rank_two_pairs": payload["pair_count"],
        "primitive_xor_minimum": payload["primitive_cost"]["minimum_NOT_AND_OR_NAND_NOR_gate"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
