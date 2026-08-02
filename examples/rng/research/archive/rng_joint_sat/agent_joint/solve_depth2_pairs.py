"""Exact minimum-gate synthesis for shared depth-two XOR output matrices.

Rows are GF(2) masks over primary inputs.  The canonical network has selected
input-pair gates in layer one and one final gate for every distinct target of
weight three or four.  Targets of weight two are forced layer-one pair gates.

This research-only script reads a JSON certificate containing matrix arrays
such as ``B`` and ``C``.  It does not import or write any game-save code.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from itertools import combinations
from pathlib import Path
from typing import Iterable, Sequence

from z3 import And, Bool, If, Or, Solver, Sum, is_true, sat, unsat


@dataclass(frozen=True)
class Problem:
    targets: frozenset[int]
    units: frozenset[int]
    required_pairs: frozenset[int]
    finals: frozenset[int]
    options: dict[int, tuple[tuple[int, ...], ...]]
    candidates: frozenset[int]


def pair_partitions(row: int) -> tuple[tuple[int, ...], ...]:
    """Return canonical layer-one pair requirements for a weight-3/4 row."""

    bits = tuple(1 << index for index in range(row.bit_length()) if row >> index & 1)
    if len(bits) == 3:
        return tuple((row ^ unit,) for unit in bits)
    if len(bits) == 4:
        result = {
            tuple(sorted((left, row ^ left)))
            for left in (a | b for a, b in combinations(bits, 2))
        }
        return tuple(sorted(result))
    raise ValueError(f"row 0x{row:x} has weight {len(bits)}, expected 3 or 4")


def build_problem(rows: Iterable[int]) -> Problem:
    targets = frozenset(rows)
    if 0 in targets:
        raise ValueError("zero target requires an explicit constant convention")
    heavy = sorted(row for row in targets if row.bit_count() > 4)
    if heavy:
        raise ValueError(
            "depth <= 2 is impossible for rows heavier than four: "
            + ", ".join(f"0x{row:x}" for row in heavy)
        )

    units = frozenset(row for row in targets if row.bit_count() == 1)
    required_pairs = frozenset(row for row in targets if row.bit_count() == 2)
    finals = frozenset(row for row in targets if row.bit_count() in (3, 4))
    options = {row: pair_partitions(row) for row in finals}
    candidates = required_pairs | frozenset(
        pair for row_options in options.values() for option in row_options for pair in option
    )
    return Problem(targets, units, required_pairs, finals, options, candidates)


def make_solver(problem: Problem, pair_budget: int | None = None):
    variables = {pair: Bool(f"p_{pair:08x}") for pair in sorted(problem.candidates)}
    solver = Solver()
    for pair in problem.required_pairs:
        solver.add(variables[pair])
    for row, row_options in problem.options.items():
        solver.add(
            Or(
                *(And(*(variables[pair] for pair in option)) for option in row_options)
            )
        )
    if pair_budget is not None:
        solver.add(Sum(*(If(variable, 1, 0) for variable in variables.values())) <= pair_budget)
    return solver, variables


def solve_exact(problem: Problem) -> tuple[frozenset[int], int, int]:
    """Binary-search the pair budget and prove optimum-1 unsatisfiable."""

    low = len(problem.required_pairs)
    high = len(problem.candidates)
    best_model = None
    best_variables = None
    checks = 0
    while low < high:
        middle = (low + high) // 2
        solver, variables = make_solver(problem, middle)
        checks += 1
        if solver.check() == sat:
            high = middle
            best_model = solver.model()
            best_variables = variables
        else:
            low = middle + 1

    solver, variables = make_solver(problem, low)
    checks += 1
    if solver.check() != sat:
        raise AssertionError("the canonical depth-two problem is unexpectedly unsatisfiable")
    best_model = solver.model()
    best_variables = variables

    if low:
        below, _ = make_solver(problem, low - 1)
        checks += 1
        if below.check() != unsat:
            raise AssertionError("optimum-1 was not proved unsatisfiable")

    selected = frozenset(
        pair
        for pair, variable in best_variables.items()
        if is_true(best_model.eval(variable, model_completion=True))
    )
    # Models at an at-most budget may omit unused variables, but never exceed
    # the proved optimum.  A smaller selection would contradict optimum-1.
    if len(selected) != low:
        raise AssertionError(f"model selected {len(selected)} pairs, optimum is {low}")
    return selected, low, checks


def choose_decompositions(
    problem: Problem, selected: frozenset[int]
) -> dict[int, tuple[int, ...]]:
    result = {}
    for row, row_options in problem.options.items():
        result[row] = next(option for option in row_options if set(option) <= selected)
    return result


def load_rows(path: Path, matrix_names: Sequence[str]) -> tuple[int, ...]:
    document = json.loads(path.read_text(encoding="utf-8"))
    rows = []
    for name in matrix_names:
        values = document[name]
        rows.extend(int(value, 16) if isinstance(value, str) else int(value) for value in values)
    return tuple(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("json", type=Path)
    parser.add_argument("matrices", nargs="+", help="matrix keys to synthesize jointly")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    problem = build_problem(load_rows(args.json, args.matrices))
    selected, pair_optimum, checks = solve_exact(problem)
    decompositions = choose_decompositions(problem, selected)
    extra_pairs = selected - problem.required_pairs
    gate_optimum = pair_optimum + len(problem.finals)

    result = {
        "source": str(args.json),
        "matrices": args.matrices,
        "distinct_targets": len(problem.targets),
        "unit_targets": len(problem.units),
        "required_pair_targets": len(problem.required_pairs),
        "final_targets": len(problem.finals),
        "candidate_pairs": len(problem.candidates),
        "selected_pair_gates": [f"{pair:08x}" for pair in sorted(selected)],
        "extra_pair_gates": [f"{pair:08x}" for pair in sorted(extra_pairs)],
        "selected_pair_count": pair_optimum,
        "extra_pair_count": len(extra_pairs),
        "minimum_xor_gates": gate_optimum,
        "formula": "selected_pair_count + final_targets",
        "equivalent_formula": "distinct_non_unit_targets + extra_pair_count",
        "solver_checks": checks,
        "proved_unsat_pair_budget": pair_optimum - 1,
        "decompositions": {
            f"{row:08x}": [f"{pair:08x}" for pair in option]
            for row, option in sorted(decompositions.items())
        },
    }
    encoded = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
