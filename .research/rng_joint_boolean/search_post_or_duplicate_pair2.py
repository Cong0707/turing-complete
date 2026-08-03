#!/usr/bin/env python3
"""Audit every two-pair duplication of the fixed 61-XOR RNG DAG."""

from __future__ import annotations

import argparse
from itertools import combinations
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
from tc_save_lab.rng_encoded_asic import FIRST_LAYER  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--or-bound", type=int, default=39)
    parser.add_argument("--timeout-per-case", type=float, default=90.0)
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--stop", type=int)
    parser.add_argument(
        "--output", type=Path, default=HERE / "post-or-duplicate-pair2-b39.json"
    )
    args = parser.parse_args()
    cases_to_run = tuple(combinations(sorted(FIRST_LAYER), 2))
    if len(cases_to_run) != 351:
        raise AssertionError(f"two-copy case count changed: {len(cases_to_run)}")
    stop = len(cases_to_run) if args.stop is None else min(args.stop, len(cases_to_run))
    if not 0 <= args.start <= stop:
        raise ValueError("invalid --start/--stop range")

    started = time.monotonic()
    cases = []
    winner = None
    for index in range(args.start, stop):
        duplicate_pairs = frozenset(cases_to_run[index])
        result = solve_duplicates(
            duplicate_pairs, args.or_bound, args.timeout_per_case, args.solver
        )
        cases.append({
            "index": index,
            "duplicate_pairs": result["duplicate_pairs"],
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
        "scope": "all two-pair physical duplications of the fixed x61 DAG",
        "or_bound": args.or_bound,
        "target_total_gate": 172 + 63 * 3 + args.or_bound,
        "range": [args.start, stop],
        "case_count": len(cases_to_run),
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
