#!/usr/bin/env python3
"""Exact post-OR audit of the x63 two-unit-final frontier."""

from __future__ import annotations

import argparse
from itertools import combinations, product
import json
from pathlib import Path
import sys
import time


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for path in (HERE, ROOT / "src"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from search_post_or_fixed import solve  # noqa: E402
from tc_save_lab.rng_encoded_asic import B, FIRST_LAYER  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--or-bound", type=int, default=39)
    parser.add_argument("--timeout-per-case", type=float, default=30.0)
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument(
        "--output", type=Path, default=HERE / "post-or-x63-unit2-b39.json"
    )
    args = parser.parse_args()
    started = time.monotonic()

    unit_rows = tuple(row for row in B if row.bit_count() == 1)
    options = {
        row: tuple(
            (pair, row ^ pair)
            for pair in sorted(FIRST_LAYER)
            if (row ^ pair).bit_count() == 1
        )
        for row in unit_rows
    }
    cases = []
    winner = None
    for rows in combinations(unit_rows, 2):
        for fanin_pair in product(*(options[row] for row in rows)):
            overrides = dict(zip(rows, fanin_pair))
            result = solve(
                args.or_bound,
                args.timeout_per_case,
                args.solver,
                pairs_override=frozenset(FIRST_LAYER),
                b_fanins_override=overrides,
                fixed_xor_override=63,
                scope_suffix=f"x63 two-unit-final case {len(cases)}",
            )
            cases.append({
                "index": len(cases),
                "status": result["status"],
                "elapsed_seconds": result["elapsed_seconds"],
                "peak_rss_bytes": result["peak_rss_bytes"],
                "overrides": {
                    f"{row:08x}": [f"{fanin:08x}" for fanin in fanins]
                    for row, fanins in sorted(overrides.items())
                },
                "clause_sha256": result["clause_sha256"],
            })
            if result["status"] == "sat":
                winner = result
                break
        if winner is not None:
            break
    if len(cases) != 10 and winner is None:
        raise AssertionError(f"two-unit-final topology count changed: {len(cases)}")
    statuses = {
        status: sum(case["status"] == status for case in cases)
        for status in ("sat", "unsat", "unknown")
    }
    document = {
        "schema": 1,
        "scope": "fixed T/x61 pair cover plus two unit-final XORs; complete pre/post OR model",
        "or_bound": args.or_bound,
        "target_total_gate": 172 + 63 * 3 + args.or_bound,
        "cases": cases,
        "statuses": statuses,
        "winner": winner,
        "elapsed_seconds": time.monotonic() - started,
    }
    args.output.write_text(
        json.dumps(document, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "cases": len(cases),
        "statuses": statuses,
        "winner_gate": (
            winner.get("certificate", {}).get("total_gate")
            if isinstance(winner, dict) else None
        ),
        "elapsed_seconds": document["elapsed_seconds"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
