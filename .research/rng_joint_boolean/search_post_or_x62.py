#!/usr/bin/env python3
"""Exhaust the fixed-T 62-XOR frontier with post-XOR seed ORs."""

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
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from search_post_or_fixed import solve  # noqa: E402
from tc_save_lab.rng_encoded_asic import B, C, FIRST_LAYER, T  # noqa: E402


def load_helper():
    path = ROOT / ".research" / "rng_cost387" / "agent_paircover" / "enumerate_and_optimize.py"
    spec = importlib.util.spec_from_file_location("rng_post_or_paircover", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def exact_extra_sets(helper, option_extras, universe: frozenset[int], budget: int):
    search = helper.CoverSearch(option_extras, budget, set(), set())
    search.run()
    exact: set[frozenset[int]] = set()
    for solution in search.solutions:
        missing = budget - len(solution)
        if missing < 0:
            continue
        for padding in combinations(sorted(universe - solution), missing):
            exact.add(solution | frozenset(padding))
    return search, frozenset(exact)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--or-bound", type=int, default=42)
    parser.add_argument("--timeout-per-case", type=float, default=30.0)
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument(
        "--output", type=Path, default=HERE / "post-or-x62-b42.json"
    )
    args = parser.parse_args()
    helper = load_helper()
    started = time.monotonic()

    targets = frozenset((*B, *C))
    required_pairs = frozenset(
        row for row in targets if row.bit_count() == 2
    )
    final_rows = tuple(sorted(
        row for row in targets if row.bit_count() in (3, 4)
    ))
    b_final_rows = tuple(
        row for row in B if row.bit_count() in (3, 4)
    )
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
    cover_search, extra_sets = exact_extra_sets(
        helper, option_extras, universe, 16
    )
    if len(extra_sets) != 92:
        raise AssertionError("16-extra cover frontier changed")

    # C-only choices do not constrain load labels.  Deduplicate the 112 full
    # decompositions by their selected pair set and B-side topology.
    topology_cases: dict[
        tuple[frozenset[int], tuple[tuple[int, tuple[int, ...]], ...]],
        dict[int, tuple[int, ...]],
    ] = {}
    full_decomposition_count = 0
    for extra in extra_sets:
        selected = required_pairs | extra
        choices = tuple(
            tuple(
                option for option in helper.pair_partitions(row)
                if set(option) <= selected
            )
            for row in final_rows
        )
        for selected_options in product(*choices):
            full_decomposition_count += 1
            all_decompositions = dict(zip(final_rows, selected_options))
            fanins = {}
            for row in b_final_rows:
                option = all_decompositions[row]
                fanins[row] = (
                    (option[0], row ^ option[0])
                    if row.bit_count() == 3 else option
                )
            key = (selected, tuple(sorted(fanins.items())))
            topology_cases.setdefault(key, fanins)
    if full_decomposition_count != 112:
        raise AssertionError("full 62-XOR decomposition count changed")

    cases: list[dict[str, object]] = []
    winner: dict[str, object] | None = None
    for case_index, ((selected, _), fanins) in enumerate(
        sorted(
            topology_cases.items(),
            key=lambda item: (
                tuple(sorted(item[0][0])), item[0][1]
            ),
        )
    ):
        result = solve(
            args.or_bound,
            args.timeout_per_case,
            args.solver,
            pairs_override=selected,
            b_fanins_override=fanins,
            fixed_xor_override=62,
            scope_suffix=f"x62 extra16 topology {case_index}",
        )
        cases.append({
            "family": "extra16-pair-cover",
            "index": case_index,
            "status": result["status"],
            "elapsed_seconds": result["elapsed_seconds"],
            "selected_pairs": [f"{pair:08x}" for pair in sorted(selected)],
            "B_fanins": {
                f"{row:08x}": [f"{fanin:08x}" for fanin in values]
                for row, values in sorted(fanins.items())
            },
            "clause_sha256": result["clause_sha256"],
        })
        if result["status"] == "sat":
            winner = result
            break

    # The other exact x62 accounting is the unique x61 pair cover plus one
    # direct unit output deliberately implemented as pair XOR unit.
    if winner is None:
        unit_index = 0
        for steady in (row for row in B if row.bit_count() == 1):
            for pair in sorted(FIRST_LAYER):
                other = steady ^ pair
                if other.bit_count() != 1:
                    continue
                result = solve(
                    args.or_bound,
                    args.timeout_per_case,
                    args.solver,
                    pairs_override=frozenset(FIRST_LAYER),
                    b_fanins_override={steady: (pair, other)},
                    fixed_xor_override=62,
                    scope_suffix=f"x62 unit-final topology {unit_index}",
                )
                cases.append({
                    "family": "unit-final",
                    "index": unit_index,
                    "status": result["status"],
                    "elapsed_seconds": result["elapsed_seconds"],
                    "steady": f"{steady:08x}",
                    "fanins": [f"{pair:08x}", f"{other:08x}"],
                    "clause_sha256": result["clause_sha256"],
                })
                unit_index += 1
                if result["status"] == "sat":
                    winner = result
                    break
            if winner is not None:
                break

    statuses = {
        name: sum(case["status"] == name for case in cases)
        for name in ("sat", "unsat", "unknown")
    }
    document = {
        "schema": 1,
        "scope": "fixed T; complete row-deduplicated x62 depth-two frontier plus unit-final accounting; pre/post seed OR model",
        "or_bound": args.or_bound,
        "target_total_gate": 172 + 62 * 3 + args.or_bound,
        "cover_frontier": {
            "visited_partial_sets": len(cover_search.visited),
            "exact_extra16_sets": len(extra_sets),
            "full_decompositions": full_decomposition_count,
            "deduplicated_pair_B_topologies": len(topology_cases),
        },
        "case_statuses": statuses,
        "cases": cases,
        "winner": winner,
        "elapsed_seconds": time.monotonic() - started,
        "scope_warning": "Duplicate pre-labelled XOR nodes with identical steady rows remain outside this row-deduplicated x62 pass; raw pair post-OR sharing is fully represented.",
    }
    args.output.write_text(
        json.dumps(document, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "or_bound": args.or_bound,
        "target_total_gate": document["target_total_gate"],
        "topologies": len(topology_cases),
        "statuses": statuses,
        "winner_gate": (
            winner.get("certificate", {}).get("total_gate")
            if isinstance(winner, dict) else None
        ),
        "elapsed_seconds": document["elapsed_seconds"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
