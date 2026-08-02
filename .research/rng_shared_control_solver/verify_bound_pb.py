"""Independent stratified-MaxSAT verifier for the free-control lower bound.

This verifier rebuilds the universe without importing the primary solver.  It
uses pairwise exactly-one clauses instead of a sequential counter and runs
RC2Stratified instead of RC2.  The independent CNF construction and a second
SAT backend provide a reproducibility check for the reported optimum.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import dataclass
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import sys
import time
from typing import Iterable


BITS = 32
MASK = (1 << BITS) - 1
EXPECTED_MATRIX_SHA256 = "b05c6d821814fb084ee2ade6d742a4b91f9a9f749dcb313836469be43bd7e97f"


def xorshift32(value: int) -> int:
    value ^= value >> 13
    value &= MASK
    value ^= (value << 17) & MASK
    value &= MASK
    value ^= value >> 5
    return value & MASK


def rows() -> tuple[int, ...]:
    columns = tuple(xorshift32(1 << bit) for bit in range(BITS))
    return tuple(
        sum(((columns[source] >> output) & 1) << source for source in range(BITS))
        for output in range(BITS)
    )


def singleton_masks(value: int) -> tuple[int, ...]:
    return tuple(1 << bit for bit in range(BITS) if value >> bit & 1)


def partitions(items: tuple[int, ...], count: int) -> Iterable[tuple[int, ...]]:
    blocks: list[list[int]] = []

    def visit(index: int) -> Iterable[tuple[int, ...]]:
        if index == len(items):
            if len(blocks) == count and all(1 <= len(block) <= 3 for block in blocks):
                yield tuple(sorted(sum(block) for block in blocks))
            return
        item = items[index]
        for block in blocks:
            if len(block) < 3:
                block.append(item)
                yield from visit(index + 1)
                block.pop()
        if len(blocks) < count:
            blocks.append([item])
            yield from visit(index + 1)
            blocks.pop()

    yield from visit(0)


@dataclass(frozen=True)
class Choice:
    arity: int
    sources: tuple[int, ...]

    @property
    def forms(self) -> tuple[int, ...]:
        return tuple(source for source in self.sources if source.bit_count() > 1)


def choices(target: int) -> tuple[Choice, ...]:
    result: set[Choice] = set()
    if target.bit_count() in {1, 2, 3}:
        result.add(Choice(0, (target,)))
    for arity in (2, 3):
        for sources in partitions(singleton_masks(target), arity):
            if all(source.bit_count() <= 3 for source in sources):
                result.add(Choice(arity, sources))
    return tuple(sorted(result, key=lambda item: (item.arity, item.sources)))


def cost(arity: int) -> int:
    return 3 if arity == 2 else 8 if arity == 3 else 0


def optimize(solver_name: str) -> dict[str, object]:
    from pysat.examples.rc2 import RC2Stratified
    from pysat.formula import IDPool, WCNF

    started = time.perf_counter()
    matrix = rows()
    all_choices = tuple(choices(row) for row in matrix)
    forms = tuple(sorted({form for options in all_choices for option in options for form in option.forms}))
    pool = IDPool()
    y = {
        (output, index): pool.id(f"verify_y{output}_{index}")
        for output, options in enumerate(all_choices)
        for index in range(len(options))
    }
    f = {form: pool.id(f"verify_f_{form:08x}") for form in forms}
    formula = WCNF()
    users: dict[int, list[int]] = defaultdict(list)

    for output, options in enumerate(all_choices):
        variables = [y[output, index] for index in range(len(options))]
        formula.append(variables)
        for left, right in combinations(variables, 2):
            formula.append([-left, -right])
        for index, option in enumerate(options):
            active = y[output, index]
            for form in option.forms:
                formula.append([-active, f[form]])
                users[form].append(active)
            option_cost = cost(option.arity)
            if option_cost:
                formula.append([-active], weight=option_cost)
    for form in forms:
        formula.append([-f[form], *users[form]])
        formula.append([-f[form]], weight=cost(form.bit_count()))
    encoded = time.perf_counter()
    with RC2Stratified(
        formula,
        solver=solver_name,
        adapt=True,
        exhaust=True,
        incr=True,
        verbose=0,
    ) as solver:
        model = solver.compute()
        optimum = solver.cost
    finished = time.perf_counter()
    if model is None:
        raise RuntimeError("independent hard constraints are unexpectedly UNSAT")
    return {
        "status": "optimal",
        "optimum": optimum,
        "variables": pool.top,
        "hard_clauses": len(formula.hard),
        "soft_clauses": len(formula.soft),
        "forms": len(forms),
        "options": sum(map(len, all_choices)),
        "encode_seconds": encoded - started,
        "solve_seconds": finished - encoded,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "certificate",
        type=Path,
        nargs="?",
        default=Path(__file__).with_name("shared_control_bound233.json"),
    )
    parser.add_argument("--solver", default="g3")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("pb_verification.json"),
    )
    args = parser.parse_args()

    payload = json.loads(args.certificate.read_text(encoding="utf-8"))
    matrix = rows()
    matrix_hash = sha256(b"".join(row.to_bytes(4, "little") for row in matrix)).hexdigest()
    if matrix_hash != EXPECTED_MATRIX_SHA256 or payload["matrix_sha256"] != matrix_hash:
        raise AssertionError("matrix hash mismatch")
    optimum = int(payload["free_control_lower_bound"]["optimum"])
    independent = optimize(args.solver)
    if independent["optimum"] != optimum:
        raise AssertionError(
            f"independent MaxSAT optimum {independent['optimum']} != reported {optimum}"
        )
    requested = int(payload["requested_bound"])
    if requested < optimum and payload["status"] != "unsat-within-model":
        raise AssertionError("certificate status contradicts the verified lower bound")

    result = {
        "schema_version": 1,
        "status": "verified",
        "method": "independent pairwise-CNF RC2Stratified optimization",
        "solver": args.solver,
        "matrix_sha256": matrix_hash,
        "reported_optimum": optimum,
        "requested_bound": requested,
        "independent_optimization": independent,
        "scope": "cancellation-free depth-4 partition family with free controls",
    }
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
