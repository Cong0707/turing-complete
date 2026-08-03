#!/usr/bin/env python3
"""Prove that reachable tick-1 states do not cheapen cascade final XORs."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Callable, Sequence


N = 32
MASK = (1 << N) - 1
IDENTITY = tuple(1 << bit for bit in range(N))


def xorshift32(value: int) -> int:
    value ^= value >> 13
    value ^= (value << 17) & MASK
    value ^= value >> 5
    return value & MASK


def transition() -> tuple[int, ...]:
    columns = tuple(xorshift32(1 << source) for source in range(N))
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


def load_u(path: Path) -> tuple[int, ...]:
    document = json.loads(path.read_text(encoding="utf-8"))
    raw = document.get("targets")
    if not isinstance(raw, list) or len(raw) != 64:
        raise ValueError("certificate must contain 64 targets")
    targets = tuple(int(str(value), 16) for value in raw)
    return tuple(target >> 32 for target in targets[:N])


def pair_witnesses(left: int, right: int) -> dict[str, str]:
    if not left or not right or left == right:
        raise AssertionError("pair does not have rank two")
    witnesses: dict[str, str] = {}
    for first in range(N):
        for second in range(first + 1, N):
            candidates = (0, 1 << first, 1 << second, (1 << first) | (1 << second))
            observed = {
                f"{(left & seed).bit_count() & 1}{(right & seed).bit_count() & 1}": seed
                for seed in candidates
            }
            if len(observed) == 4:
                # The live test samples only nonzero seeds.  Rank two leaves a
                # 30-dimensional common kernel, so replace the trivial 00
                # witness with an explicit nonzero member of that kernel.
                columns: dict[int, int] = {}
                kernel = None
                for bit in range(N):
                    signature = ((left >> bit & 1) << 1) | (right >> bit & 1)
                    if signature == 0:
                        kernel = 1 << bit
                        break
                    if signature in columns:
                        kernel = (1 << columns[signature]) | (1 << bit)
                        break
                    columns[signature] = bit
                if kernel is None or not kernel:
                    raise AssertionError("rank-two pair has no nonzero kernel witness")
                observed["00"] = kernel
                result = {key: f"{observed[key]:08x}" for key in ("00", "01", "10", "11")}
                if any(int(value, 16) == 0 for value in result.values()):
                    raise AssertionError("live-domain witness unexpectedly used seed zero")
                return result
    raise AssertionError("rank-two pair has no two-coordinate witness")


def truth_table(function: Callable[[int, int], int]) -> int:
    return sum((function(a, b) & 1) << (2 * a + b) for a in range(2) for b in range(2))


def primitive_minimum() -> dict[str, object]:
    # Truth-table bit order is 00, 01, 10, 11.
    constants_and_inputs = {0b0000: "0", 0b1111: "1", 0b1100: "a", 0b1010: "b"}
    best = dict(constants_and_inputs)
    cost = {function: 0 for function in best}
    layers = [set(best)]

    def add(function: int, expression: str, gate_cost: int) -> None:
        if function not in cost or gate_cost < cost[function]:
            cost[function] = gate_cost
            best[function] = expression

    for budget in range(1, 4):
        snapshot = tuple(cost.items())
        for function, function_cost in snapshot:
            if function_cost + 1 == budget:
                add(function ^ 0b1111, f"NOT({best[function]})", budget)
        snapshot = tuple(cost.items())
        for left, left_cost in snapshot:
            for right, right_cost in snapshot:
                if left_cost + right_cost + 1 != budget:
                    continue
                add(left & right, f"AND({best[left]},{best[right]})", budget)
                add(left | right, f"OR({best[left]},{best[right]})", budget)
                add((left & right) ^ 0b1111, f"NAND({best[left]},{best[right]})", budget)
                add((left | right) ^ 0b1111, f"NOR({best[left]},{best[right]})", budget)
        layers.append({function for function, value in cost.items() if value == budget})

    xor = truth_table(lambda a, b: a ^ b)
    if xor != 0b0110 or cost.get(xor) != 3:
        raise AssertionError("primitive XOR minimum changed")
    return {
        "truth_table_order": ["00", "01", "10", "11"],
        "xor_table": f"{xor:04b}",
        "xor_minimum_without_native_xor": cost[xor],
        "witness_expression": best[xor],
        "functions_reachable_by_cost": [len(layer) for layer in layers],
        "single_switch_reading_z_as_zero": "data AND enable",
        "single_switch_cost": 2,
        "single_switch_can_compute_xor": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--certificate", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    a = transition()
    u = load_u(args.certificate)
    ua = multiply(u, a)
    a_plus_i = tuple(row ^ IDENTITY[index] for index, row in enumerate(a))

    output_pairs = []
    feedback_pairs = []
    for bit in range(N):
        # At tick 1: q=U*seed, z=C*q=(A+I)*seed, y=z XOR seed.
        output_pairs.append(
            {
                "bit": bit,
                "left_form": f"{a_plus_i[bit]:08x}",
                "right_form": f"{IDENTITY[bit]:08x}",
                "witness_seed": pair_witnesses(a_plus_i[bit], IDENTITY[bit]),
            }
        )
        # At tick 1: w=U*A*seed, q=U*seed, q'=w XOR q.
        feedback_pairs.append(
            {
                "bit": bit,
                "left_form": f"{ua[bit]:08x}",
                "right_form": f"{u[bit]:08x}",
                "witness_seed": pair_witnesses(ua[bit], u[bit]),
            }
        )

    payload = {
        "schema": 1,
        "status": "proved",
        "scope": "explicit cascade final pairs at reachable tick 1, all 2^32 seeds",
        "live_input_domain": "1..0xffffffff; every stored truth-combination witness is nonzero",
        "certificate": str(args.certificate),
        "certificate_sha256": hashlib.sha256(args.certificate.read_bytes()).hexdigest(),
        "argument": {
            "output": "z=(A+I)*seed and right=seed at tick 1",
            "feedback": "w=U*A*seed and right=q=U*seed at tick 1",
            "rank_two_test": "both forms nonzero and unequal over GF(2)",
            "consequence": "each pair projects onto all four Boolean assignments",
        },
        "primitive_cost": primitive_minimum(),
        "output_pair_count": len(output_pairs),
        "feedback_pair_count": len(feedback_pairs),
        "all_pairs_rank_two": True,
        "output_pairs": output_pairs,
        "feedback_pairs": feedback_pairs,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="ascii")
    print(
        json.dumps(
            {
                "status": payload["status"],
                "rank_two_pairs": len(output_pairs) + len(feedback_pairs),
                "primitive_xor_minimum": payload["primitive_cost"]["xor_minimum_without_native_xor"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
