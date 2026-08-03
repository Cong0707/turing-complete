#!/usr/bin/env python3
"""Exact post-OR audit of the x63 direct-unit extra17 frontier."""

from __future__ import annotations

import argparse
import importlib.util
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
from tc_save_lab.rng_encoded_asic import B, C  # noqa: E402


HELPER = (
    ROOT
    / ".research"
    / "rng_cost387"
    / "agent_paircover"
    / "enumerate_and_optimize.py"
)


def load_helper():
    spec = importlib.util.spec_from_file_location("rng_post_or_paircover", HELPER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {HELPER}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def exact_extra_sets(helper, option_extras, universe, budget):
    search = helper.CoverSearch(option_extras, budget, set(), set())
    search.run()
    exact = set()
    for solution in search.solutions:
        missing = budget - len(solution)
        if missing < 0:
            continue
        for padding in combinations(sorted(universe - solution), missing):
            exact.add(solution | frozenset(padding))
    return search, frozenset(exact)


def enumerate_topologies(helper):
    targets = frozenset((*B, *C))
    required_pairs = frozenset(row for row in targets if row.bit_count() == 2)
    final_rows = tuple(sorted(row for row in targets if row.bit_count() in (3, 4)))
    b_final_rows = tuple(row for row in B if row.bit_count() in (3, 4))
    option_extras = {
        row: tuple(
            frozenset(option) - required_pairs
            for option in helper.pair_partitions(row)
        )
        for row in final_rows
    }
    universe = frozenset(
        pair
        for options in option_extras.values()
        for option in options
        for pair in option
    )
    search, extra_sets = exact_extra_sets(helper, option_extras, universe, 17)
    if len(extra_sets) != 4198:
        raise AssertionError(f"extra17 cover count changed: {len(extra_sets)}")

    # C-only choices do not constrain seed labels.  Keep one selected-pair
    # representative for each distinct B-side decomposition.
    representatives = {}
    full_decompositions = 0
    for extra in extra_sets:
        selected = required_pairs | extra
        choices = tuple(
            tuple(
                option
                for option in helper.pair_partitions(row)
                if set(option) <= selected
            )
            for row in final_rows
        )
        for options in product(*choices):
            full_decompositions += 1
            decomposition = dict(zip(final_rows, options))
            topology = tuple(decomposition[row] for row in b_final_rows)
            representatives.setdefault(topology, selected)
    if full_decompositions != 6262:
        raise AssertionError(
            f"extra17 full decomposition count changed: {full_decompositions}"
        )
    if len(representatives) != 84:
        raise AssertionError(
            f"extra17 B topology count changed: {len(representatives)}"
        )
    return search, extra_sets, full_decompositions, b_final_rows, representatives


def fanins_for_topology(b_final_rows, topology):
    fanins = {}
    for row, option in zip(b_final_rows, topology, strict=True):
        if row.bit_count() == 3:
            fanins[row] = (option[0], row ^ option[0])
        else:
            fanins[row] = tuple(option)
    return fanins


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--or-bound", type=int, default=39)
    parser.add_argument("--timeout-per-case", type=float, default=30.0)
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--stop", type=int)
    parser.add_argument(
        "--output", type=Path, default=HERE / "post-or-x63-extra17-b39.json"
    )
    args = parser.parse_args()
    helper = load_helper()
    search, extra_sets, full_count, b_final_rows, representatives = (
        enumerate_topologies(helper)
    )
    ordered = sorted(
        representatives.items(),
        key=lambda item: (item[0], tuple(sorted(item[1]))),
    )
    stop = len(ordered) if args.stop is None else min(args.stop, len(ordered))
    if not 0 <= args.start <= stop:
        raise ValueError("invalid --start/--stop range")

    started = time.monotonic()
    cases = []
    winner = None
    for index in range(args.start, stop):
        topology, selected = ordered[index]
        fanins = fanins_for_topology(b_final_rows, topology)
        result = solve(
            args.or_bound,
            args.timeout_per_case,
            args.solver,
            pairs_override=selected,
            b_fanins_override=fanins,
            fixed_xor_override=63,
            scope_suffix=f"x63 direct-unit extra17 topology {index}",
        )
        cases.append({
            "index": index,
            "status": result["status"],
            "elapsed_seconds": result["elapsed_seconds"],
            "peak_rss_bytes": result["peak_rss_bytes"],
            "selected_pairs": [f"{value:08x}" for value in sorted(selected)],
            "B_fanins": {
                f"{row:08x}": [f"{fanin:08x}" for fanin in values]
                for row, values in sorted(fanins.items())
            },
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
        "scope": (
            "fixed T x63 direct-unit extra17 pair-cover frontier; complete "
            "pre/post OR model"
        ),
        "or_bound": args.or_bound,
        "target_total_gate": 172 + 63 * 3 + args.or_bound,
        "cover_frontier": {
            "visited_partial_sets": len(search.visited),
            "exact_extra17_sets": len(extra_sets),
            "full_decompositions": full_count,
            "deduplicated_B_topologies": len(ordered),
        },
        "range": [args.start, stop],
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
        "topology_count": len(ordered),
        "statuses": statuses,
        "winner_gate": (
            winner.get("certificate", {}).get("total_gate")
            if isinstance(winner, dict) else None
        ),
        "elapsed_seconds": document["elapsed_seconds"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
