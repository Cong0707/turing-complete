"""Exact depth-two XOR2/XOR3 cover model for natural-state xorshift32.

Research only.  The universe consists of the 32 input basis vectors and every
non-degenerate first-level XOR2/XOR3 form.  An output is a single XOR2 or
XOR3 gate whose inputs are drawn from that universe.  This permits arbitrary
overlap/cancellation between first-level forms, and sharing is represented by
one Boolean per first-level form.
"""

from __future__ import annotations

from collections import Counter
from itertools import combinations
import argparse
import sys
import time


BITS = 32
MASK = (1 << BITS) - 1


def xorshift32(value: int) -> int:
    value ^= value >> 13
    value &= MASK
    value ^= (value << 17) & MASK
    value &= MASK
    value ^= value >> 5
    return value & MASK


def target_rows() -> tuple[int, ...]:
    columns = tuple(xorshift32(1 << source) for source in range(BITS))
    return tuple(
        sum(((columns[source] >> output) & 1) << source for source in range(BITS))
        for output in range(BITS)
    )


def forms() -> tuple[tuple[int, ...], dict[int, int]]:
    basis = tuple(1 << bit for bit in range(BITS))
    level_one = tuple(
        sorted(
            (left ^ right for left, right in combinations(basis, 2)),
            key=lambda value: (value.bit_count(), value),
        )
    ) + tuple(
        sorted(
            (first ^ second ^ third for first, second, third in combinations(basis, 3)),
            key=lambda value: (value.bit_count(), value),
        )
    )
    costs = {value: 3 if value.bit_count() == 2 else 12 for value in level_one}
    # Numeric order is used as the canonical order for output source tuples.
    return tuple(sorted(basis + level_one)), costs


def enumerate_options(target: int, sources: tuple[int, ...], primary_cost: dict[int, int]):
    """Yield canonical (final_cost, required-first-level-form tuple) options.

    Duplicated sources are intentionally excluded: an XOR gate with repeated
    identical inputs algebraically reduces to a smaller gate and cannot lower
    either cost or depth.
    """
    source_set = set(sources)
    options: set[tuple[int, tuple[int, ...]]] = set()
    # An output may directly tap a first-level gate.  This matters for the
    # five weight-three rows: that gate can also be shared by another output.
    if target in primary_cost:
        options.add((0, (target,)))
    # XOR2: choose the lexicographically first source; the other is forced.
    for index, left in enumerate(sources):
        right = target ^ left
        if right in source_set and left < right:
            required = tuple(sorted(value for value in (left, right) if value in primary_cost))
            options.add((3, required))

    # XOR3: choose an ordered pair and derive the third source.  The numeric
    # ordering makes every unordered triple appear exactly once.
    for index, left in enumerate(sources):
        for right in sources[index + 1:]:
            third = target ^ left ^ right
            if third in source_set and right < third:
                required = tuple(sorted(value for value in (left, right, third) if value in primary_cost))
                options.add((12, required))
    return tuple(sorted(options, key=lambda option: (option[0] + sum(primary_cost[value] for value in option[1]), option)))


def minimal_requirements(options, final_cost: int) -> tuple[tuple[int, ...], ...]:
    """Remove DNF terms made redundant by a strict subset term."""
    raw = {required for cost, required in options if cost == final_cost}
    result = []
    for required in raw:
        redundant = any(
            subset != required and subset in raw
            for size in range(len(required))
            for subset in combinations(required, size)
        )
        if not redundant:
            result.append(required)
    return tuple(sorted(result, key=lambda required: (len(required), required)))


def remove_xor3_dominated_by_xor2(
    xor2: tuple[tuple[int, ...], ...],
    xor3: tuple[tuple[int, ...], ...],
    primary_cost: dict[int, int],
) -> tuple[tuple[int, ...], ...]:
    """Drop an XOR3 term if adding an XOR2 term costs at most its 9 premium.

    If R is selected and S is an XOR2 term, switching the output from XOR3
    to XOR2 changes total cost by ``cost(S - R) - 9``.  Hence this is an exact
    dominance reduction, not a heuristic, and it remains valid under sharing.
    """
    result = []
    for required in xor3:
        present = set(required)
        if any(
            sum(primary_cost[value] for value in alternative if value not in present) <= 9
            for alternative in xor2
        ):
            continue
        result.append(required)
    return tuple(result)


def solve(limit: int, timeout_ms: int) -> None:
    try:
        from z3 import And, Bool, If, Implies, Or, Solver, Sum, sat, unsat
    except ImportError as error:
        raise SystemExit("requires z3-solver") from error

    rows = target_rows()
    sources, primary_cost = forms()
    options_by_output = [enumerate_options(row, sources, primary_cost) for row in rows]
    minimal = [
        {cost: minimal_requirements(options, cost) for cost in (3, 12)}
        for options in options_by_output
    ]
    for entry in minimal:
        entry[12] = remove_xor3_dominated_by_xor2(
            entry[3], entry[12], primary_cost
        )
    # Cost-zero direct taps are only possible for an output whose linear form
    # is itself a legal first-level form.
    for output, options in enumerate(options_by_output):
        minimal[output][0] = minimal_requirements(options, 0)
    print("minimal DNF terms:", flush=True)
    for index, entry in enumerate(minimal):
        print(f"  y{index:02d}: direct={len(entry[0])} xor2={len(entry[3])} xor3={len(entry[12])}", flush=True)

    used_forms = sorted(
        {value for entry in minimal for choices in entry.values() for choice in choices for value in choice}
    )
    variables = {value: Bool(f"p_{value:08x}") for value in used_forms}
    is_xor3 = [Bool(f"y{index}_xor3") for index in range(BITS)]
    is_direct = [Bool(f"y{index}_direct") for index in range(BITS)]
    solver = Solver()
    solver.set(timeout=timeout_ms)
    for index, entry in enumerate(minimal):
        for cost, arity in ((3, False), (12, True), (0, None)):
            requirements = entry[cost]
            formula = Or(*(And(*(variables[value] for value in required)) for required in requirements))
            if arity is None:
                solver.add(Implies(is_direct[index], formula))
            else:
                solver.add(Implies((~is_direct[index]) & (is_xor3[index] == arity), formula))
        solver.add(Implies(is_direct[index], ~is_xor3[index]))
    total = Sum(
        *(If(variables[value], primary_cost[value], 0) for value in used_forms),
        *(If(is_direct[index], 0, If(is_xor3[index], 12, 3)) for index in range(BITS)),
    )
    solver.add(total <= limit)
    print(f"solver variables: first={len(variables)} output_arity={len(is_xor3)} limit={limit}", flush=True)
    started = time.perf_counter()
    result = solver.check()
    elapsed = time.perf_counter() - started
    print(f"result={result} elapsed_s={elapsed:.3f}", flush=True)
    if result == unsat:
        print("proved_unsat=true", flush=True)
        return
    if result != sat:
        print(f"reason_unknown={solver.reason_unknown()}", file=sys.stderr, flush=True)
        raise SystemExit(2)
    model = solver.model()
    selected = tuple(value for value in used_forms if bool(model.eval(variables[value], model_completion=True)))
    output_cost = sum(
        0 if bool(model.eval(is_direct[index], model_completion=True))
        else 12 if bool(model.eval(is_xor3[index], model_completion=True)) else 3
        for index in range(BITS)
    )
    first_cost = sum(primary_cost[value] for value in selected)
    print(f"model first_forms={len(selected)} first_cost={first_cost} output_cost={output_cost} total={first_cost+output_cost}")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--solve", type=int, metavar="LIMIT")
    parser.add_argument("--timeout-ms", type=int, default=30_000)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.solve is not None:
        solve(args.solve, args.timeout_ms)
        return
    rows = target_rows()
    sources, primary_cost = forms()
    print(f"sources={len(sources)} first_level={len(primary_cost)}")
    print("row weights:", dict(sorted(Counter(row.bit_count() for row in rows).items())))
    started = time.perf_counter()
    total = 0
    for output, row in enumerate(rows):
        options = enumerate_options(row, sources, primary_cost)
        by_arity = Counter(final_cost for final_cost, _ in options)
        max_required = max((len(required) for _, required in options), default=0)
        print(
            f"y{output:02d} weight={row.bit_count()} options={len(options)} "
            f"xor2={by_arity[3]} xor3={by_arity[12]} max_required={max_required}"
        )
        total += len(options)
    print(f"total_options={total} elapsed_s={time.perf_counter()-started:.3f}")


if __name__ == "__main__":
    main()
