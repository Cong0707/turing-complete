#!/usr/bin/env python3
"""Scan exact fixed-C neighbourhoods with a bounded number of extra free rows."""

from __future__ import annotations

import argparse
from itertools import combinations
import json
from pathlib import Path
import time

from pysat.solvers import Solver

from solve_three_c_rows_sat import (
    BITS,
    ThreeRowModel,
    load_center,
    parse_rows,
    transition_rows,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--center", type=Path, required=True)
    parser.add_argument("--support", type=int, default=9)
    parser.add_argument("--extra", type=int, default=2)
    parser.add_argument(
        "--optional-rows",
        type=lambda value: tuple(int(item) for item in value.split(",") if item),
        help="restrict extra-row combinations to this comma-separated set",
    )
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--count", type=int)
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--conflicts", type=int, default=100_000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    center = load_center(args.center)
    center_c = parse_rows(center, "C")
    center_b = parse_rows(center, "B")
    center_d = parse_rows(center, "D")
    a = transition_rows()
    mandatory = tuple(
        row
        for row in range(BITS)
        if center_c[row].bit_count() + a[row].bit_count() > args.support
    )
    optional = (
        tuple(row for row in range(BITS) if row not in mandatory)
        if args.optional_rows is None
        else tuple(dict.fromkeys(args.optional_rows))
    )
    if any(row < 0 or row >= BITS or row in mandatory for row in optional):
        parser.error("optional rows must be distinct non-mandatory rows in 0..31")
    trials = tuple(combinations(optional, args.extra))
    end = len(trials) if args.count is None else min(len(trials), args.start + args.count)
    selected = trials[args.start:end]
    args.output.parent.mkdir(parents=True, exist_ok=True)

    counts = {"sat": 0, "unsat": 0, "unknown": 0}
    started = time.monotonic()
    sat_record: dict[str, object] | None = None
    with args.output.open("a", encoding="ascii") as sink:
        for relative, extra_rows in enumerate(selected):
            trial_index = args.start + relative
            free_rows = (*mandatory, *extra_rows)
            built_at = time.monotonic()
            with Solver(name=args.solver) as solver:
                model = ThreeRowModel(solver, center_c, args.support, free_rows)
                build_seconds = time.monotonic() - built_at
                phase_hint_applied = False
                try:
                    solver.set_phases(model.phases(center_b, center_d))
                    phase_hint_applied = True
                except NotImplementedError:
                    pass
                solve_at = time.monotonic()
                if args.conflicts:
                    solver.conf_budget(args.conflicts)
                    answer = solver.solve_limited(expect_interrupt=True)
                else:
                    answer = solver.solve()
                solve_seconds = time.monotonic() - solve_at
                status = (
                    "sat" if answer is True else "unsat" if answer is False else "unknown"
                )
                counts[status] += 1
                record: dict[str, object] = {
                    "trial": trial_index,
                    "mandatory_rows": list(mandatory),
                    "extra_rows": list(extra_rows),
                    "free_rows": list(free_rows),
                    "status": status,
                    "variables": model.next_variable - 1,
                    "clauses": model.clause_count,
                    "build_seconds": build_seconds,
                    "solve_seconds": solve_seconds,
                    "phase_hint_applied": phase_hint_applied,
                }
                if answer is True:
                    record["solution"] = model.extract(solver.get_model())
                    sat_record = record
                sink.write(json.dumps(record, separators=(",", ":")) + "\n")
                sink.flush()
            if (relative + 1) % 10 == 0 or status != "unsat":
                print(
                    f"trial={trial_index + 1}/{len(trials)} extra={extra_rows} "
                    f"status={status} solve={solve_seconds:.3f}s counts={counts}",
                    flush=True,
                )
            if sat_record is not None:
                break

    checked = sum(counts.values())
    completed_range = sat_record is None and checked == len(selected)
    summary = {
        "schema": 1,
        "model": "persistent seed exact fixed-C neighbourhood scan",
        "support_limit": args.support,
        "center": str(args.center),
        "mandatory_rows": list(mandatory),
        "optional_rows": list(optional),
        "extra_free_row_count": args.extra,
        "total_combinations": len(trials),
        "range_start": args.start,
        "range_end": args.start + checked,
        "requested_range_end": end,
        "conflict_budget_per_trial": args.conflicts or None,
        "counts": counts,
        "elapsed_seconds": time.monotonic() - started,
        "status": (
            "sat"
            if sat_record is not None
            else "unknown_present"
            if counts["unknown"]
            else "unsat_checked_range"
            if completed_range
            else "incomplete"
        ),
        "scope": (
            "UNSAT is exact only for the scanned fixed-C neighbourhoods. "
            "SAT is support-feasible but still needs physical timed synthesis."
        ),
        "sat_trial": sat_record,
    }
    summary_path = args.output.with_suffix(args.output.suffix + ".summary.json")
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="ascii")
    print(json.dumps(summary, indent=2), flush=True)
    return 0 if sat_record is not None else 2


if __name__ == "__main__":
    raise SystemExit(main())
