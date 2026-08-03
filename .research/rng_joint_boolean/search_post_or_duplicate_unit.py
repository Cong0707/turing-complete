#!/usr/bin/env python3
"""Audit one duplicated pair plus one unit-final XOR in the fixed RNG DAG."""

from __future__ import annotations

import argparse
from itertools import product
import json
from pathlib import Path
import sys
import time


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for path in (HERE, ROOT / "src"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from search_post_or_duplicate_pair import solve_duplicates  # noqa: E402
from tc_save_lab.rng_encoded_asic import B, FIRST_LAYER  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--or-bound", type=int, default=39)
    parser.add_argument("--timeout-per-case", type=float, default=90.0)
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--stop", type=int)
    parser.add_argument(
        "--output", type=Path, default=HERE / "post-or-duplicate-unit-b39.json"
    )
    args = parser.parse_args()

    unit_rows = tuple(row for row in B if row.bit_count() == 1)
    unit_options = tuple(
        (unit, pair)
        for unit in unit_rows
        for pair in sorted(FIRST_LAYER)
        if pair & unit and (pair ^ unit).bit_count() == 1
    )
    if len(unit_options) != 5:
        raise AssertionError(f"unit-final option count changed: {len(unit_options)}")
    topology_cases = tuple(product(unit_options, sorted(FIRST_LAYER)))
    if len(topology_cases) != 135:
        raise AssertionError(f"mixed duplicate/unit case count changed: {len(topology_cases)}")
    stop = len(topology_cases) if args.stop is None else min(args.stop, len(topology_cases))
    if not 0 <= args.start <= stop:
        raise ValueError("invalid --start/--stop range")

    started = time.monotonic()
    cases = []
    winner = None
    for index in range(args.start, stop):
        (unit, unit_pair), duplicate_pair = topology_cases[index]
        result = solve_duplicates(
            frozenset((duplicate_pair,)),
            args.or_bound,
            args.timeout_per_case,
            args.solver,
            b_fanins_override={unit: (unit_pair, unit ^ unit_pair)},
            fixed_xor_override=63,
        )
        cases.append({
            "index": index,
            "unit": f"{unit:08x}",
            "unit_pair": f"{unit_pair:08x}",
            "duplicate_pair": f"{duplicate_pair:08x}",
            "status": result["status"],
            "elapsed_seconds": result["elapsed_seconds"],
            "peak_rss_bytes": result["peak_rss_bytes"],
            "clause_sha256": result["clause_sha256"],
        })
        if result["status"] == "sat":
            winner = result
            break
    statuses = {
        status: sum(case["status"] == status for case in cases)
        for status in ("sat", "unsat", "unknown")
    }
    document = {
        "schema": 1,
        "scope": "fixed x61 DAG plus one pair duplicate and one unit-final XOR",
        "or_bound": args.or_bound,
        "target_total_gate": 172 + 63 * 3 + args.or_bound,
        "range": [args.start, stop],
        "case_count": len(topology_cases),
        "statuses": statuses,
        "cases": cases,
        "winner": winner,
        "elapsed_seconds": time.monotonic() - started,
    }
    args.output.write_text(
        json.dumps(document, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "range": document["range"],
        "statuses": statuses,
        "winner_gate": (
            winner.get("certificate", {}).get("total_gate")
            if isinstance(winner, dict) else None
        ),
        "elapsed_seconds": document["elapsed_seconds"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
