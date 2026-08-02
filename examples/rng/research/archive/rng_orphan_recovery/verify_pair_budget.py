"""Check whether the two orphan 42-state covers can beat gate 387.

This reproduces only the decisive budget boundary.  With 42 Delay Bits and
the ready Delay/NOT pair, the fixed cost is 42 * 5 + 6 = 216.  Even with no
OR gates, gate <= 387 therefore requires at most 57 XOR gates.
"""

from __future__ import annotations

from pathlib import Path
import time

from z3 import And, Bool, Or, PbLe, Solver, unsat


CASES = ((707, 17), (808, 19))
STATE_BITS = 42


def parse_rows(seed: int) -> set[int]:
    path = Path(f".research/rng_stage_basis_search/subspace-{seed}.log")
    lines = path.read_text(encoding="utf-8").splitlines()
    marker = max(
        index
        for index, line in enumerate(lines)
        if line.startswith("score heavy=0")
    )
    return {int(value, 16) for value in lines[marker + 13 : marker + 55]}


def pair_options(row: int) -> tuple[tuple[int, ...], ...]:
    units = tuple(1 << bit for bit in range(STATE_BITS) if row >> bit & 1)
    if len(units) == 3:
        return tuple((row ^ unit,) for unit in units)
    if len(units) == 4:
        a, b, c, d = units
        return (
            (a | b, c | d),
            (a | c, b | d),
            (a | d, b | c),
        )
    raise ValueError(f"unsupported final row weight {len(units)}")


def check(seed: int, pair_budget: int) -> None:
    rows = parse_rows(seed)
    required = {row for row in rows if row.bit_count() == 2}
    finals = {row for row in rows if row.bit_count() in (3, 4)}
    options = {row: pair_options(row) for row in finals}
    pairs = set(required)
    for row_options in options.values():
        for option in row_options:
            pairs.update(option)

    selected = {pair: Bool(f"selected_{seed}_{pair:x}") for pair in pairs}
    solver = Solver()
    solver.set(timeout=60_000, max_memory=256)
    for pair in required:
        solver.add(selected[pair])
    for row_options in options.values():
        solver.add(
            Or(*(And(*(selected[pair] for pair in option)) for option in row_options))
        )
    solver.add(PbLe([(variable, 1) for variable in selected.values()], pair_budget))

    started = time.perf_counter()
    result = solver.check()
    elapsed = time.perf_counter() - started
    xor_budget = pair_budget + len(finals)
    print(
        f"seed={seed} result={result} pair_budget={pair_budget} "
        f"finals={len(finals)} xor_budget={xor_budget} elapsed={elapsed:.3f}s"
    )
    if result != unsat:
        raise SystemExit(f"expected UNSAT, got {result}: {solver.reason_unknown()}")


def main() -> None:
    for seed, pair_budget in CASES:
        check(seed, pair_budget)


if __name__ == "__main__":
    main()
