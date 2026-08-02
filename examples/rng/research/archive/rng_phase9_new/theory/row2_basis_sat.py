#!/usr/bin/env python3
"""Exact low-memory search for a row-weight-two RNG state basis.

The selected rows of T are unordered during solving.  They come from the 32
unit vectors and the 496 two-bit vectors.  If exactly 32 such vectors span all
32 rows of the invertible xorshift matrix A, they are automatically a basis.

For that basis, ``C = A*T^-1`` has row weight at most four exactly when every
row of A is the XOR of at most four selected vectors.  A selected unit e_u
produces the B row ``C_u``.  A selected edge e_u+e_v produces ``C_u+C_v``, so
the B constraint is exactly the same four-vector condition for ``A_u+A_v``.

This script is research-only.  It does not import save/game code or access a
live process.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
from typing import Iterable, Sequence

from z3 import And, Bool, Implies, Or, PbEq, Solver, is_true, sat, unknown


BITS = 32
MASK = (1 << BITS) - 1


def xorshift32(value: int) -> int:
    value ^= value >> 13
    value &= MASK
    value ^= (value << 17) & MASK
    value &= MASK
    value ^= value >> 5
    return value & MASK


def matrix_from_function(function) -> tuple[int, ...]:
    return tuple(
        sum(
            ((function(1 << source) >> output) & 1) << source
            for source in range(BITS)
        )
        for output in range(BITS)
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
    rows = [row | ((1 << index) << BITS) for index, row in enumerate(matrix)]
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


def rank(rows: Iterable[int]) -> int:
    pivots: dict[int, int] = {}
    for original in rows:
        row = original
        while row:
            bit = row.bit_length() - 1
            if bit not in pivots:
                pivots[bit] = row
                break
            row ^= pivots[bit]
    return len(pivots)


def xor_rows(rows: Iterable[int]) -> int:
    result = 0
    for row in rows:
        result ^= row
    return result


class DecompositionIndex:
    def __init__(self, candidates: Sequence[int]) -> None:
        self.candidates = tuple(candidates)
        self.by_mask = {mask: index for index, mask in enumerate(candidates)}
        self.pairs_by_xor: dict[int, list[tuple[int, int]]] = defaultdict(list)
        for left, left_mask in enumerate(candidates):
            for right in range(left + 1, len(candidates)):
                self.pairs_by_xor[left_mask ^ candidates[right]].append((left, right))
        self.cache: dict[int, tuple[tuple[int, ...], ...]] = {}

    def decompositions(self, target: int) -> tuple[tuple[int, ...], ...]:
        cached = self.cache.get(target)
        if cached is not None:
            return cached

        result: list[tuple[int, ...]] = []
        direct = self.by_mask.get(target)
        if direct is not None:
            result.append((direct,))
        result.extend(self.pairs_by_xor.get(target, ()))

        candidates = self.candidates
        for left, left_mask in enumerate(candidates):
            for middle in range(left + 1, len(candidates)):
                right = self.by_mask.get(target ^ left_mask ^ candidates[middle])
                if right is not None and right > middle:
                    result.append((left, middle, right))

        for left, left_mask in enumerate(candidates):
            for second in range(left + 1, len(candidates)):
                needed = target ^ left_mask ^ candidates[second]
                for third, fourth in self.pairs_by_xor.get(needed, ()):
                    if third > second:
                        result.append((left, second, third, fourth))

        answer = tuple(result)
        self.cache[target] = answer
        return answer


def row_histogram(matrix: Sequence[int]) -> dict[str, int]:
    return {
        str(weight): count
        for weight, count in sorted(Counter(row.bit_count() for row in matrix).items())
    }


def verify_selected(a: Sequence[int], selected: Sequence[int]) -> dict[str, object]:
    if len(selected) != BITS or len(set(selected)) != BITS:
        raise AssertionError("expected 32 distinct basis rows")
    if any(not 1 <= row.bit_count() <= 2 for row in selected):
        raise AssertionError("T row support exceeds two")
    if rank(selected) != BITS:
        raise AssertionError("selected rows are singular")
    inverse = invert(selected)
    c = compose(a, inverse)
    b = compose(selected, c)
    if compose(c, selected) != tuple(a):
        raise AssertionError("C*T != A")
    if max(row.bit_count() for row in c) > 4:
        raise AssertionError("C support bound failed")
    if max(row.bit_count() for row in b) > 4:
        raise AssertionError("B support bound failed")
    return {
        "T_rows_hex": [f"{row:08x}" for row in selected],
        "T_inverse_rows_hex": [f"{row:08x}" for row in inverse],
        "B_rows_hex": [f"{row:08x}" for row in b],
        "C_rows_hex": [f"{row:08x}" for row in c],
        "row_weight_histograms": {
            "T": row_histogram(selected),
            "B": row_histogram(b),
            "C": row_histogram(c),
        },
    }


def solve_pysat(
    *,
    a: Sequence[int],
    candidates: Sequence[int],
    allowed_edges: Sequence[tuple[int, int]],
    decompositions: DecompositionIndex,
    c_only: bool,
    solver_name: str,
    branch_weight7: bool,
    leaderboard_bound: bool,
    exact_pairs: int | None,
    min_unit_b: int | None,
    omit_unit_b: int | None,
) -> tuple[str, tuple[int, ...] | None, dict[str, object]]:
    try:
        from pysat.card import CardEnc, EncType
        from pysat.formula import CNF
        from pysat.solvers import Solver as PySatSolver
    except ImportError as error:  # pragma: no cover - optional research dependency
        raise SystemExit("--engine pysat requires `pip install python-sat`") from error

    selection_variables = tuple(range(1, len(candidates) + 1))
    # Covering the 32 independent A rows already implies at least 32 selected
    # vectors.  Encoding only <=32 is equivalent here and avoids a large,
    # unhelpful lower-cardinality search symmetry.
    cardinality = CardEnc.atmost(
        lits=list(selection_variables),
        bound=BITS,
        top_id=len(candidates),
        encoding=EncType.seqcounter,
    )
    cnf = CNF(from_clauses=cardinality.clauses)
    next_variable = cardinality.nv + 1

    if exact_pairs is not None:
        pair_cardinality = CardEnc.equals(
            lits=list(selection_variables[BITS:]),
            bound=exact_pairs,
            top_id=next_variable - 1,
            encoding=EncType.seqcounter,
        )
        cnf.extend(pair_cardinality.clauses)
        next_variable = pair_cardinality.nv + 1

    unit_variables: list[int] = []
    if leaderboard_bound:
        by_mask = {mask: index for index, mask in enumerate(candidates)}
        for offset, (left, right) in enumerate(allowed_edges, start=BITS):
            difference = a[left] ^ a[right]
            if difference.bit_count() != 2:
                continue
            companion = by_mask[difference]
            unit_variable = next_variable
            next_variable += 1
            unit_variables.append(unit_variable)
            edge_variable = selection_variables[offset]
            companion_variable = selection_variables[companion]
            cnf.append([-unit_variable, edge_variable])
            cnf.append([-unit_variable, companion_variable])
            cnf.append([unit_variable, -edge_variable, -companion_variable])

        # The physical target requires total XOR <=77.  If r is the number
        # of selected pair rows and u the number of unit B rows, the target
        # union gives the necessary bound 32+2*r-u <=77.  Encode the
        # equivalent 2*r+(8-u)<=53 with duplicate variables for weight two.
        weighted_literals: list[int] = []
        for edge_variable in selection_variables[BITS:]:
            copy_variable = next_variable
            next_variable += 1
            cnf.append([-copy_variable, edge_variable])
            cnf.append([copy_variable, -edge_variable])
            weighted_literals.extend((edge_variable, copy_variable))
        weighted_literals.extend(-variable for variable in unit_variables)
        leaderboard_cardinality = CardEnc.atmost(
            lits=weighted_literals,
            bound=53,
            top_id=next_variable - 1,
            encoding=EncType.seqcounter,
        )
        cnf.extend(leaderboard_cardinality.clauses)
        next_variable = leaderboard_cardinality.nv + 1

        if min_unit_b is not None:
            unit_cardinality = CardEnc.atleast(
                lits=unit_variables,
                bound=min_unit_b,
                top_id=next_variable - 1,
                encoding=EncType.seqcounter,
            )
            cnf.extend(unit_cardinality.clauses)
            next_variable = unit_cardinality.nv + 1
        if omit_unit_b is not None:
            if not 0 <= omit_unit_b < len(unit_variables):
                raise ValueError("--omit-unit-b is outside the special-unit range")
            for index, variable in enumerate(unit_variables):
                cnf.append([-variable] if index == omit_unit_b else [variable])
    elif min_unit_b is not None or omit_unit_b is not None:
        raise ValueError("unit-B constraints require --leaderboard-bound")

    branched_targets = {a[17], a[18]} if branch_weight7 else set()
    unconditional = set(a) - branched_targets
    conditions: dict[int, list[int]] = defaultdict(list)
    if not c_only:
        for offset, (left, right) in enumerate(allowed_edges, start=BITS):
            conditions[a[left] ^ a[right]].append(selection_variables[offset])

    targets = unconditional | set(conditions)
    decomposition_counts: dict[str, int] = {}
    auxiliary_count = 0
    for target in sorted(targets):
        options = decompositions.decompositions(target)
        decomposition_counts[f"{target:08x}"] = len(options)
        option_variables = []
        for option in options:
            option_variable = next_variable
            next_variable += 1
            auxiliary_count += 1
            option_variables.append(option_variable)
            for candidate_index in option:
                cnf.append([-option_variable, selection_variables[candidate_index]])
        if target in unconditional:
            cnf.append(option_variables)
        for condition in conditions.get(target, ()):
            cnf.append([-condition, *option_variables])

    branch_count = 0
    skipped_dependent_branches = 0
    with PySatSolver(name=solver_name, bootstrap_with=cnf.clauses) as solver:
        if branch_weight7:
            answer = False
            model = None
            first_options = decompositions.decompositions(a[17])
            second_options = decompositions.decompositions(a[18])
            for first in first_options:
                for second in second_options:
                    branch_count += 1
                    option = tuple(sorted(set((*first, *second))))
                    option_rows = tuple(candidates[index] for index in option)
                    if rank(option_rows) != len(option_rows):
                        skipped_dependent_branches += 1
                        continue
                    assumptions = [selection_variables[index] for index in option]
                    if solver.solve(assumptions=assumptions):
                        answer = True
                        model = solver.get_model()
                        break
                if answer:
                    break
        else:
            answer = solver.solve()
            model = solver.get_model() if answer else None

    basis = None
    if model is not None:
        truth = set(literal for literal in model if literal > 0)
        basis = tuple(
            candidate
            for candidate, variable in zip(candidates, selection_variables)
            if variable in truth
        )
    statistics = {
        "cnf_variable_count": next_variable - 1,
        "cnf_clause_count": len(cnf.clauses),
        "decomposition_target_count": len(decomposition_counts),
        "decomposition_option_count": sum(decomposition_counts.values()),
        "decomposition_auxiliary_count": auxiliary_count,
        "weight7_branching": branch_weight7,
        "weight7_branch_count": branch_count,
        "weight7_dependent_branches_skipped": skipped_dependent_branches,
        "leaderboard_xor_lower_bound_enabled": leaderboard_bound,
        "potential_unit_B_count": len(unit_variables),
        "exact_pair_count": exact_pairs,
        "minimum_unit_B_count": min_unit_b,
        "omitted_unit_B_index": omit_unit_b,
    }
    return ("sat" if answer else "unsat"), basis, statistics


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--c-only", action="store_true")
    parser.add_argument("--timeout-ms", type=int, default=120_000)
    parser.add_argument("--memory-mb", type=int, default=512)
    parser.add_argument("--engine", choices=("z3", "pysat"), default="z3")
    parser.add_argument("--pysat-solver", default="cadical195")
    parser.add_argument("--branch-weight7", action="store_true")
    parser.add_argument("--leaderboard-bound", action="store_true")
    parser.add_argument("--exact-pairs", type=int)
    parser.add_argument("--min-unit-b", type=int)
    parser.add_argument("--omit-unit-b", type=int)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    a = matrix_from_function(xorshift32)
    units = tuple(1 << bit for bit in range(BITS))

    # A selected edge (u,v) needs a B row representing A_u+A_v with at most
    # four basis rows of support <=2.  Natural support above eight is therefore
    # impossible before considering any particular basis.
    allowed_edges = tuple(
        (left, right)
        for left in range(BITS)
        for right in range(left + 1, BITS)
        if (a[left] ^ a[right]).bit_count() <= 8
    )
    candidates = units + tuple((1 << left) | (1 << right) for left, right in allowed_edges)
    decompositions = DecompositionIndex(candidates)

    basis = None
    extra_statistics: dict[str, object] = {}
    reason_unknown = None
    if args.engine == "pysat":
        result_text, basis, extra_statistics = solve_pysat(
            a=a,
            candidates=candidates,
            allowed_edges=allowed_edges,
            decompositions=decompositions,
            c_only=args.c_only,
            solver_name=args.pysat_solver,
            branch_weight7=args.branch_weight7,
            leaderboard_bound=args.leaderboard_bound,
            exact_pairs=args.exact_pairs,
            min_unit_b=args.min_unit_b,
            omit_unit_b=args.omit_unit_b,
        )
    else:
        solver = Solver()
        solver.set(timeout=args.timeout_ms, max_memory=args.memory_mb)
        selected = [Bool(f"selected_{index}") for index in range(len(candidates))]
        solver.add(PbEq([(variable, 1) for variable in selected], BITS))

        decomposition_counts: dict[str, int] = {}

        def require(target: int, condition=True) -> None:
            options = decompositions.decompositions(target)
            decomposition_counts[f"{target:08x}"] = len(options)
            formula = Or(*(And(*(selected[index] for index in option)) for option in options))
            solver.add(formula if condition is True else Implies(condition, formula))

        for row in a:
            require(row)

        if not args.c_only:
            for offset, (left, right) in enumerate(allowed_edges, start=BITS):
                require(a[left] ^ a[right], selected[offset])

        result = solver.check()
        result_text = str(result)
        extra_statistics = {
            "decomposition_target_count": len(decomposition_counts),
            "decomposition_option_count": sum(decomposition_counts.values()),
        }
        if result == sat:
            model = solver.model()
            basis = tuple(
                candidate
                for candidate, variable in zip(candidates, selected)
                if is_true(model.eval(variable))
            )
        elif result == unknown:
            reason_unknown = solver.reason_unknown()

    report: dict[str, object] = {
        "schema": 1,
        "scope": "exact row-weight<=2 basis search; research-only",
        "mode": "C-only" if args.c_only else "full B/C",
        "candidate_count": len(candidates),
        "unit_candidate_count": len(units),
        "edge_candidate_count": len(allowed_edges),
        "excluded_edge_count": BITS * (BITS - 1) // 2 - len(allowed_edges),
        **extra_statistics,
        "engine": args.engine,
        "timeout_ms": args.timeout_ms,
        "memory_mb": args.memory_mb,
        "solver_result": result_text,
    }
    if basis is not None:
        report["certificate"] = verify_selected(a, basis) if not args.c_only else {
            "T_rows_hex": [f"{row:08x}" for row in basis],
            "rank": rank(basis),
            "C_maximum_row_weight": max(
                row.bit_count() for row in compose(a, invert(basis))
            ),
        }
    elif reason_unknown is not None:
        report["reason_unknown"] = reason_unknown

    encoded = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="ascii")
    print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
