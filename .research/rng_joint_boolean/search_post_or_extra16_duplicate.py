#!/usr/bin/env python3
"""Audit x62 extra16 pair covers plus one duplicated physical pair node."""

from __future__ import annotations

import argparse
from collections import Counter
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
from tc_save_lab.rng_encoded_asic import B, GATE_BY_OUTPUT  # noqa: E402


X62_RESULT = HERE / "post-or-x62-b42.json"


def enumerate_cases():
    document = json.loads(X62_RESULT.read_text(encoding="utf-8"))
    cases = []
    topology_count = 0
    for source in document["cases"]:
        if source["family"] != "extra16-pair-cover":
            continue
        topology_count += 1
        selected = frozenset(int(value, 16) for value in source["selected_pairs"])
        overrides = {
            int(row, 16): tuple(int(value, 16) for value in values)
            for row, values in source["B_fanins"].items()
        }
        users = Counter()
        for steady in B:
            if steady in overrides:
                fanins = overrides[steady]
            elif steady in selected:
                fanins = (steady,)
            elif steady.bit_count() == 1:
                fanins = ()
            else:
                gate = GATE_BY_OUTPUT[steady]
                fanins = (gate.left, gate.right)
            users.update(fanin for fanin in fanins if fanin in selected)
        # A single-consumer copy can be merged back into the original node
        # without changing its label or any OR atom, so only fanout>=2 matters.
        useful = tuple(sorted(pair for pair, count in users.items() if count >= 2))
        if max(users.values(), default=0) != 2:
            raise AssertionError("extra16 useful-pair fanout changed")
        for duplicate_pair in useful:
            cases.append({
                "source_case": source["index"],
                "selected": selected,
                "overrides": overrides,
                "duplicate_pair": duplicate_pair,
            })
    if topology_count != 102:
        raise AssertionError(f"extra16 topology count changed: {topology_count}")
    if len(cases) != 1418:
        raise AssertionError(f"extra16 duplicate case count changed: {len(cases)}")
    return cases


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--or-bound", type=int, default=39)
    parser.add_argument("--timeout-per-case", type=float, default=90.0)
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--stop", type=int)
    parser.add_argument(
        "--output", type=Path, default=HERE / "post-or-extra16-duplicate-b39.json"
    )
    args = parser.parse_args()
    topology_cases = enumerate_cases()
    stop = len(topology_cases) if args.stop is None else min(args.stop, len(topology_cases))
    if not 0 <= args.start <= stop:
        raise ValueError("invalid --start/--stop range")

    started = time.monotonic()
    cases = []
    winner = None
    for index in range(args.start, stop):
        case = topology_cases[index]
        duplicate_pair = case["duplicate_pair"]
        result = solve_duplicates(
            frozenset((duplicate_pair,)),
            args.or_bound,
            args.timeout_per_case,
            args.solver,
            pairs_override=case["selected"],
            b_fanins_override=case["overrides"],
            fixed_xor_override=63,
        )
        cases.append({
            "index": index,
            "source_case": case["source_case"],
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
        "scope": "all x62 extra16 pair/B topologies plus one useful pair duplicate",
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
        "case_count": len(topology_cases),
        "statuses": statuses,
        "winner_gate": (
            winner.get("certificate", {}).get("total_gate")
            if isinstance(winner, dict) else None
        ),
        "elapsed_seconds": document["elapsed_seconds"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
