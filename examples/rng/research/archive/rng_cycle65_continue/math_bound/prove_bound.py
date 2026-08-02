#!/usr/bin/env python3
"""Necessary bounds for the fixed two-shear constant-seed RNG.

Research only: this script constructs GF(2) matrices in memory.  It neither
imports save-writing code nor starts the game.

The fixed model is

    feedback = B*q xor D*seed
    output   = C*q xor A*seed

where q leaves arrive at 4, seed leaves at 0, XOR2 delay is 2, every target
must arrive by 9, and the proposed budget is at most 92 XOR2 gates.
"""

from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
from typing import Callable, Iterable, Sequence

from z3 import And, Bool, If, Or, Solver, Sum, unsat


BITS = 32
INPUTS = 64
MASK = (1 << BITS) - 1
IDENTITY = tuple(1 << bit for bit in range(BITS))
Q_ARRIVAL = 4
SEED_ARRIVAL = 0
XOR2_DELAY = 2
TARGET_DELAY = 9
XOR2_BUDGET = 92

# A deterministic 27-pair upper witness.  Exactness is established below by
# independently asking Z3 for UNSAT at budget 26.
PAIR_WITNESS = frozenset(
    int(value, 16)
    for value in (
        "00000021", "00000042", "00000084", "00000108", "00000210",
        "00000420", "00000840", "00001080", "00002100", "00004200",
        "00008008", "00010010", "00420000", "00840000", "01080000",
        "02100000", "04200000", "08008000", "08400000", "10010000",
        "10800000", "20000001", "21000000", "40000002", "42000000",
        "80000004", "84000000",
    )
)


def xorshift32(value: int) -> int:
    value ^= value >> 13
    value &= MASK
    value ^= (value << 17) & MASK
    value &= MASK
    value ^= value >> 5
    return value & MASK


def matrix_from_function(function: Callable[[int], int]) -> tuple[int, ...]:
    return tuple(
        sum(((function(1 << source) >> output) & 1) << source for source in range(BITS))
        for output in range(BITS)
    )


def apply_row(row: int, matrix: Sequence[int]) -> int:
    result = 0
    remaining = row
    while remaining:
        low = remaining & -remaining
        result ^= matrix[low.bit_length() - 1]
        remaining ^= low
    return result


def compose(left: Sequence[int], right: Sequence[int]) -> tuple[int, ...]:
    return tuple(apply_row(row, right) for row in left)


def add(left: Sequence[int], right: Sequence[int]) -> tuple[int, ...]:
    return tuple(a ^ b for a, b in zip(left, right))


def invert(matrix: Sequence[int]) -> tuple[int, ...]:
    rows = [matrix[index] | ((1 << index) << BITS) for index in range(BITS)]
    for column in range(BITS):
        pivot = next(
            (index for index in range(column, BITS) if rows[index] >> column & 1),
            None,
        )
        if pivot is None:
            raise AssertionError("singular matrix")
        rows[column], rows[pivot] = rows[pivot], rows[column]
        for index in range(BITS):
            if index != column and rows[index] >> column & 1:
                rows[index] ^= rows[column]
    return tuple((row >> BITS) & MASK for row in rows)


def right_shear(distance: int) -> tuple[int, ...]:
    return matrix_from_function(lambda value: (value ^ (value >> distance)) & MASK)


def gf2_rank(rows: Iterable[int]) -> int:
    basis: dict[int, int] = {}
    for original in rows:
        row = original
        while row:
            pivot = row.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = row
                break
            row ^= basis[pivot]
    return len(basis)


def digest(values: Iterable[int], width: int = 8) -> str:
    payload = b"".join(value.to_bytes(width, "little") for value in values)
    return sha256(payload).hexdigest()


def build_matrices() -> dict[str, tuple[int, ...]]:
    a = matrix_from_function(xorshift32)
    t = compose(right_shear(17), right_shear(13))
    t_inverse = invert(t)
    c = compose(a, t_inverse)
    b = compose(t, c)
    d = compose(t, add(a, IDENTITY))
    assert compose(c, t) == a
    assert compose(t, c) == b
    assert compose(t, t_inverse) == IDENTITY
    assert d == compose(t, add(a, IDENTITY))
    return {"A": a, "T": t, "T_inverse": t_inverse, "B": b, "C": c, "D": d}


def target_rows(matrices: dict[str, tuple[int, ...]]) -> tuple[tuple[str, int, int, int], ...]:
    result = []
    for branch, q_rows, seed_rows in (
        ("feedback", matrices["B"], matrices["D"]),
        ("output", matrices["C"], matrices["A"]),
    ):
        result.extend(
            (branch, index, q_row, seed_row)
            for index, (q_row, seed_row) in enumerate(zip(q_rows, seed_rows))
        )
    return tuple(result)


def pair_options(row: int) -> tuple[tuple[int, ...], ...]:
    """Layer-one q-pair requirements for a weight-three/four q row."""

    units = tuple(1 << bit for bit in range(BITS) if row >> bit & 1)
    if len(units) == 3:
        return tuple((row ^ unit,) for unit in units)
    if len(units) == 4:
        return tuple(
            sorted(
                {
                    tuple(sorted((left, row ^ left)))
                    for left in (a | b for a, b in combinations(units, 2))
                }
            )
        )
    raise AssertionError(f"expected q weight 3/4, got {len(units)}")


def pair_solver(
    options: dict[int, tuple[tuple[int, ...], ...]], budget: int | None
) -> tuple[Solver, dict[int, object]]:
    candidates = sorted(
        {pair for row_options in options.values() for option in row_options for pair in option}
    )
    variables = {pair: Bool(f"pair_{pair:08x}") for pair in candidates}
    solver = Solver()
    for row_options in options.values():
        solver.add(
            Or(*(And(*(variables[pair] for pair in option)) for option in row_options))
        )
    if budget is not None:
        solver.add(Sum(*(If(variable, 1, 0) for variable in variables.values())) <= budget)
    return solver, variables


def exact_pair_cover(q_rows: Iterable[int]) -> dict[str, object]:
    heavy = tuple(sorted({row for row in q_rows if row.bit_count() in (3, 4)}))
    options = {row: pair_options(row) for row in heavy}
    candidates = {
        pair for row_options in options.values() for option in row_options for pair in option
    }

    selected = PAIR_WITNESS
    if len(selected) != 27 or not selected <= candidates:
        raise AssertionError("fixed pair witness is malformed")
    decompositions = {
        row: next(
            (option for option in row_options if set(option) <= selected),
            None,
        )
        for row, row_options in options.items()
    }
    if any(option is None for option in decompositions.values()):
        raise AssertionError("fixed pair witness does not cover every heavy q row")

    optimum = len(selected)
    below, _ = pair_solver(options, optimum - 1)
    if below.check() != unsat:
        raise AssertionError("optimum-1 pair budget was not UNSAT")
    option_encoding = []
    for row, row_options in sorted(options.items()):
        option_encoding.append(row)
        for option in row_options:
            option_encoding.extend(option)
            option_encoding.append(0)
        option_encoding.append((1 << 32) - 1)

    return {
        "heavy_distinct_q_rows": len(heavy),
        "candidate_q_pairs": len(candidates),
        "minimum_selected_q_pairs": optimum,
        "proved_unsat_pair_budget": optimum - 1,
        "solver_checks": 1,
        "selected_q_pairs": [f"{pair:08x}" for pair in sorted(selected)],
        "decompositions": {
            f"{row:08x}": [f"{pair:08x}" for pair in option]
            for row, option in sorted(decompositions.items())
        },
        "problem_sha256": digest(option_encoding, width=4),
    }


def kraft_record(branch: str, index: int, q_row: int, seed_row: int) -> dict[str, object]:
    q_weight = q_row.bit_count()
    seed_weight = seed_row.bit_count()
    q_levels = (TARGET_DELAY - Q_ARRIVAL) // XOR2_DELAY
    seed_levels = (TARGET_DELAY - SEED_ARRIVAL) // XOR2_DELAY
    denominator = 1 << seed_levels
    numerator = q_weight * (1 << (seed_levels - q_levels)) + seed_weight
    return {
        "branch": branch,
        "index": index,
        "q_row": f"{q_row:08x}",
        "seed_row": f"{seed_row:08x}",
        "q_weight": q_weight,
        "seed_weight": seed_weight,
        "kraft_numerator": numerator,
        "kraft_denominator": denominator,
        "violates_delay_9": numerator > denominator,
    }


def make_certificate() -> dict[str, object]:
    matrices = build_matrices()
    targets = target_rows(matrices)
    full_rows = tuple(q_row | (seed_row << BITS) for _, _, q_row, seed_row in targets)
    records = tuple(kraft_record(*target) for target in targets)
    violations = tuple(record for record in records if record["violates_delay_9"])

    if len(full_rows) != 64 or len(set(full_rows)) != 64 or gf2_rank(full_rows) != 64:
        raise AssertionError("the 64 complete targets are not an independent basis")
    if min(row.bit_count() for row in full_rows) <= 1:
        raise AssertionError("a complete target is unexpectedly a raw input")
    if len(violations) != 32:
        raise AssertionError("fixed two-shear Kraft violation count changed")

    q_rows = matrices["B"] + matrices["C"]
    pair_cover = exact_pair_cover(q_rows)
    pair_count = int(pair_cover["minimum_selected_q_pairs"])

    # Each complete target needs a distinct XOR output: all 64 are non-input
    # and independent.  A q-pair parent of a heavy target must be one XOR
    # level from the q leaves; with a binary gate it is therefore the pure
    # XOR of two raw q inputs.  Every complete target has nonzero seed support,
    # so those pair gates are disjoint from the 64 target gates.
    target_gate_lower_bound = len(full_rows)
    xor_lower_bound = target_gate_lower_bound + pair_count

    matrix_payload = tuple(
        row
        for name in ("A", "T", "T_inverse", "B", "C", "D")
        for row in matrices[name]
    )
    return {
        "schema": 1,
        "scope": {
            "encoding": "fixed T=(I+R17)(I+R13)",
            "maps": ["B*q xor D*seed", "C*q xor A*seed"],
            "q_arrival": Q_ARRIVAL,
            "seed_arrival": SEED_ARRIVAL,
            "xor2_delay": XOR2_DELAY,
            "target_delay": TARGET_DELAY,
            "xor2_budget": XOR2_BUDGET,
        },
        "matrix_sha256": digest(matrix_payload, width=4),
        "target_uniqueness": {
            "complete_target_count": len(full_rows),
            "distinct_complete_targets": len(set(full_rows)),
            "complete_target_rank": gf2_rank(full_rows),
            "minimum_complete_target_weight": min(row.bit_count() for row in full_rows),
            "target_xor_gate_lower_bound": target_gate_lower_bound,
            "complete_targets_sha256": digest(sorted(full_rows)),
        },
        "projected_pair_cover": {
            **pair_cover,
            "scope_note": (
                "Exact arbitrary-fanout cover of all distinct q-weight-3/4 target "
                "projections by raw q singletons and first-level q-pair gates."
            ),
            "non_target_q_pair_gate_lower_bound": pair_count,
            "combined_xor_gate_lower_bound": xor_lower_bound,
        },
        "kraft": {
            "q_max_xor_levels": (TARGET_DELAY - Q_ARRIVAL) // XOR2_DELAY,
            "seed_max_xor_levels": (TARGET_DELAY - SEED_ARRIVAL) // XOR2_DELAY,
            "necessary_inequality": "q_weight/4 + seed_weight/16 <= 1",
            "integer_inequality": "4*q_weight + seed_weight <= 16",
            "feedback_violation_count": sum(
                record["branch"] == "feedback" for record in violations
            ),
            "output_violation_count": sum(record["branch"] == "output" for record in violations),
            "total_violation_count": len(violations),
            "maximum_kraft_numerator": max(int(record["kraft_numerator"]) for record in records),
            "certified_total_delay_lower_bound": 10,
            "conclusion": (
                "delay<=9 is impossible at every XOR2 gate budget; in particular "
                "the conjunction delay<=9 and XOR2<=92 is UNSAT"
            ),
        },
        "target_records": records,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify-existing", type=Path)
    args = parser.parse_args()

    certificate = make_certificate()
    if args.verify_existing:
        saved = json.loads(args.verify_existing.read_text(encoding="utf-8"))
        normalized = json.loads(json.dumps(certificate))
        if saved != normalized:
            raise AssertionError("saved certificate differs from clean recomputation")
        print(f"verified {args.verify_existing}")
        return 0

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(certificate, indent=2) + "\n", encoding="utf-8")
    print(
        "delay<=9 UNSAT: "
        f"Kraft violations={certificate['kraft']['total_violation_count']}; "
        f"supplementary XOR lower bound={certificate['projected_pair_cover']['combined_xor_gate_lower_bound']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
