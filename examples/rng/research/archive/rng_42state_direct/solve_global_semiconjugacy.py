#!/usr/bin/env python3
"""Decide the unrestricted 42-state sparse semiconjugacy model.

It never fixes individual X/D rows; by default it is global, while
``--hamming-bound`` gives an explicitly recorded local run.  The JSON output
keeps a local UNSAT result from being mistaken for a global one.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import time

from z3 import And, Bool, BoolVal, Not, PbGe, PbLe, Solver, Xor, is_true


HERE = Path(__file__).resolve().parent
VISIBLE = 32
HIDDEN = 10
BITS = VISIBLE + HIDDEN
MASK32 = (1 << VISIBLE) - 1

CENTER_X = tuple(
    int(value, 16)
    for value in (
        "010,122,040,004,008,090,020,040,108,200,080,044,101,100,200,004,"
        "008,011,022,040,004,008,210,020,040,100,200,280,000,000,100,200"
    ).split(",")
)
CENTER_D = tuple(
    int(value, 16)
    for value in (
        "20040020001,10400004002,00800110008,00100220010,08200040020,"
        "04400080040,00401100080,0a000800400,20004002000,08008404000"
    ).split(",")
)


def xorshift32(value: int) -> int:
    value ^= value >> 13
    value ^= (value << 17) & MASK32
    value ^= value >> 5
    return value & MASK32


def transition_rows() -> tuple[int, ...]:
    return tuple(
        sum(((xorshift32(1 << source) >> target) & 1) << source for source in range(VISIBLE))
        for target in range(VISIBLE)
    )


A_ROWS = transition_rows()


def xor_all(terms: list[object], constant: bool = False) -> object:
    result = BoolVal(constant)
    for term in terms:
        result = Xor(result, term)
    return result


def build_model(solver: Solver) -> tuple[list[list[object]], list[list[object]], list[object]]:
    x = [[Bool(f"x_{row}_{aux}") for aux in range(HIDDEN)] for row in range(VISIBLE)]
    d = [[Bool(f"d_{aux}_{column}") for column in range(BITS)] for aux in range(HIDDEN)]
    for row in x:
        solver.add(PbLe([(value, 1) for value in row], 3))
    for row in d:
        solver.add(PbGe([(value, 1) for value in row], 1))
        solver.add(PbLe([(value, 1) for value in row], 4))

    for row in range(VISIBLE):
        top = []
        for column in range(BITS):
            terms = []
            constant = column < VISIBLE and bool((A_ROWS[row] >> column) & 1)
            if column >= VISIBLE:
                aux_column = column - VISIBLE
                terms.extend(
                    x[source][aux_column]
                    for source in range(VISIBLE)
                    if (A_ROWS[row] >> source) & 1
                )
            terms.extend(And(x[row][aux], d[aux][column]) for aux in range(HIDDEN))
            top.append(xor_all(terms, constant))
        solver.add(PbLe([(value, 1) for value in top], 4))

    hamming = []
    for row in range(VISIBLE):
        for aux in range(HIDDEN):
            variable = x[row][aux]
            hamming.append(variable if not ((CENTER_X[row] >> aux) & 1) else Not(variable))
    for aux in range(HIDDEN):
        for column in range(BITS):
            variable = d[aux][column]
            hamming.append(variable if not ((CENTER_D[aux] >> column) & 1) else Not(variable))
    return x, d, hamming


def extract_rows(model: object, variables: list[list[object]]) -> tuple[int, ...]:
    return tuple(
        sum(is_true(model.eval(value, model_completion=True)) << column for column, value in enumerate(row))
        for row in variables
    )


def apply_row(row: int, matrix: tuple[int, ...]) -> int:
    result = 0
    while row:
        low = row & -row
        result ^= matrix[low.bit_length() - 1]
        row ^= low
    return result


def verify_solution(x_rows: tuple[int, ...], d_rows: tuple[int, ...]) -> dict[str, object]:
    o_rows = tuple((1 << index) | (x_rows[index] << VISIBLE) for index in range(VISIBLE))
    h_top = tuple(
        apply_row(A_ROWS[index], o_rows) ^ apply_row(x_rows[index], d_rows)
        for index in range(VISIBLE)
    )
    h_rows = h_top + d_rows
    if max(row.bit_count() for row in o_rows + h_rows) > 4:
        raise AssertionError("SAT extraction violates row support")
    if tuple(apply_row(row, h_rows) for row in o_rows) != tuple(
        apply_row(row, o_rows) for row in A_ROWS
    ):
        raise AssertionError("SAT extraction violates O*H=A*O")
    return {
        "status": "support-feasible",
        "X_rows_hex": [f"{row:03x}" for row in x_rows],
        "D_rows_hex_42bit": [f"{row:011x}" for row in d_rows],
        "H_rows_hex_42bit": [f"{row:011x}" for row in h_rows],
        "O_rows_hex_42bit": [f"{row:011x}" for row in o_rows],
        "distinct_nontrivial_targets": len({row for row in o_rows + h_rows if row.bit_count() >= 2}),
        "warning": "support feasibility still requires exact pair-cover <=61",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout-ms", type=int, default=120_000)
    parser.add_argument("--max-memory-mb", type=int, default=768)
    parser.add_argument(
        "--hamming-bound",
        type=int,
        help="optional distance from the recorded excess-3 frontier",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=HERE / "global_semiconjugacy_result.json",
    )
    args = parser.parse_args()
    if args.timeout_ms <= 0 or not 64 <= args.max_memory_mb < 1024:
        parser.error("invalid timeout or memory cap")

    solver = Solver()
    solver.set(timeout=args.timeout_ms, max_memory=args.max_memory_mb)
    x, d, hamming = build_model(solver)
    if args.hamming_bound is not None:
        if args.hamming_bound < 0:
            parser.error("--hamming-bound must be nonnegative")
        solver.add(PbLe([(literal, 1) for literal in hamming], args.hamming_bound))

    started = time.monotonic()
    status = solver.check()
    elapsed = time.monotonic() - started
    result: dict[str, object] = {
        "schema": 1,
        "scope": (
            "unrestricted 42-state linear semiconjugacy: "
            "O=[I32|X], wt(O/H rows)<=4, O*H=A*O"
        ),
        "fixed_x_rows": [],
        "fixed_d_rows": [],
        "hamming_constraint": (
            None
            if args.hamming_bound is None
            else {
                "center": "embedded excess-3 frontier",
                "center_sha256": sha256(
                    json.dumps([CENTER_X, CENTER_D], separators=(",", ":")).encode("ascii")
                ).hexdigest(),
                "distance": "bitwise Hamming over all X and D entries",
                "at_most": args.hamming_bound,
            }
        ),
        "hidden_state_bits": HIDDEN,
        "timeout_ms": args.timeout_ms,
        "max_memory_mb": args.max_memory_mb,
        "status": str(status),
        "seconds": elapsed,
    }
    if str(status) == "unknown":
        result["reason"] = solver.reason_unknown()
    elif str(status) == "sat":
        model = solver.model()
        result["solution"] = verify_solution(extract_rows(model, x), extract_rows(model, d))

    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
