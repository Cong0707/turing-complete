#!/usr/bin/env python3
"""Exact post-OR audit of the x63 extra16-plus-unit frontier."""

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


FIXED_CERTIFICATE = (
    ROOT / ".research" / "rng_joint_sat" / "agent_joint" / "fixed-BC-exact.json"
)
HELPER = (
    ROOT
    / ".research"
    / "rng_cost387"
    / "agent_paircover"
    / "enumerate_and_optimize.py"
)
BITS = 32


def load_helper():
    spec = importlib.util.spec_from_file_location("rng_post_or_paircover", HELPER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {HELPER}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def choices_for_rows(helper, rows, selected):
    return tuple(
        tuple(
            option
            for option in helper.pair_partitions(row)
            if set(option) <= selected
        )
        for row in rows
    )


def enumerate_topologies(helper):
    certificate = json.loads(FIXED_CERTIFICATE.read_text(encoding="utf-8"))
    targets = frozenset((*B, *C))
    required_pairs = frozenset(row for row in targets if row.bit_count() == 2)
    base_selected = frozenset(
        int(value, 16) for value in certificate["selected_pair_gates"]
    )
    if not required_pairs <= base_selected:
        raise AssertionError("fixed certificate omits a required pair")

    b_final_rows = tuple(row for row in B if row.bit_count() in (3, 4))
    b_unit_rows = tuple(row for row in B if row.bit_count() == 1)
    all_pairs = frozenset(
        (1 << left) | (1 << right)
        for left, right in combinations(range(BITS), 2)
    )

    # Match the old proof's canonical key exactly.  Multiple unused padding
    # pairs describe the same physical B topology and are represented once.
    representatives = {}
    for added in sorted(all_pairs - base_selected):
        selected = base_selected | frozenset((added,))
        choices = choices_for_rows(helper, b_final_rows, selected)
        for topology in product(*choices):
            for unit in b_unit_rows:
                for pair in selected:
                    if pair & unit:
                        key = (topology, unit, pair)
                        representatives.setdefault(key, selected)
    if len(representatives) != 215:
        raise AssertionError(
            f"extra16-plus-unit topology count changed: {len(representatives)}"
        )
    return b_final_rows, representatives


def fanins_for_case(b_final_rows, topology, unit, pair):
    fanins = {}
    for row, option in zip(b_final_rows, topology, strict=True):
        if row.bit_count() == 3:
            fanins[row] = (option[0], row ^ option[0])
        else:
            fanins[row] = tuple(option)
    other = unit ^ pair
    if other.bit_count() != 1:
        raise AssertionError("unit-final pair does not leave a unit fanin")
    fanins[unit] = (pair, other)
    return fanins


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--or-bound", type=int, default=39)
    parser.add_argument("--timeout-per-case", type=float, default=30.0)
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--stop", type=int)
    parser.add_argument(
        "--output",
        type=Path,
        default=HERE / "post-or-x63-extra16-unit-b39.json",
    )
    args = parser.parse_args()
    helper = load_helper()
    b_final_rows, representatives = enumerate_topologies(helper)
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
        (topology, unit, pair), selected = ordered[index]
        fanins = fanins_for_case(b_final_rows, topology, unit, pair)
        result = solve(
            args.or_bound,
            args.timeout_per_case,
            args.solver,
            pairs_override=selected,
            b_fanins_override=fanins,
            fixed_xor_override=63,
            scope_suffix=f"x63 extra16-plus-unit topology {index}",
        )
        cases.append({
            "index": index,
            "status": result["status"],
            "elapsed_seconds": result["elapsed_seconds"],
            "peak_rss_bytes": result["peak_rss_bytes"],
            "selected_pairs": [f"{value:08x}" for value in sorted(selected)],
            "unit": f"{unit:08x}",
            "unit_pair": f"{pair:08x}",
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
            "fixed minimum pair cover plus one arbitrary pair and one unit-final "
            "XOR; complete pre/post OR model"
        ),
        "or_bound": args.or_bound,
        "target_total_gate": 172 + 63 * 3 + args.or_bound,
        "topology_count": len(ordered),
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
