"""Reproduce and identify the x60 pair-cover searches that hit the old cap.

This is intentionally an offline audit tool.  It reconstructs the exact radius-four
basis traversal used by ``search_basis_dualmode.py`` and records every basis whose
pair-cover DFS reaches ``state_limit``.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys


BITS = 32


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def matrix_hex(rows):
    return [f"{row:08x}" for row in rows]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state-limit", type=int, default=250_000)
    parser.add_argument("--solution-limit", type=int, default=10_000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    repo = Path(__file__).resolve().parents[3]
    dual = load_module(
        "finish_x60_dual", repo / ".research/rng_cost387/search_basis_dualmode.py"
    )
    init = load_module(
        "finish_x60_init", repo / ".research/rng_init_reuse/verify_init_reuse.py"
    )
    basis = load_module(
        "finish_x60_basis", repo / ".research/rng_joint_search_resume/search.py"
    )

    start = (tuple(init.T), tuple(init.B), tuple(init.C))
    seen = {start[0]: (start[1], start[2], ())}
    frontier = [start[0]]
    attempted = 0
    total_states = 0
    total_covers = 0
    truncated = []
    largest = []

    for depth in range(5):
        for index, t_rows in enumerate(frontier):
            b_rows, c_rows, operations = seen[t_rows]
            greedy = basis.depth_two_cost((*b_rows, *c_rows))
            if not greedy.feasible or greedy.greedy_upper_bound is None:
                continue
            if greedy.greedy_upper_bound > 60:
                continue
            finals = frozenset(
                row for row in (*b_rows, *c_rows) if row.bit_count() in (3, 4)
            )
            attempted += 1
            covers, states, hit_cap = dual.enumerate_pair_covers(
                (*b_rows, *c_rows),
                60 - len(finals),
                state_limit=args.state_limit,
                solution_limit=args.solution_limit,
            )
            total_states += states
            total_covers += len(covers)
            largest.append(
                {
                    "depth": depth,
                    "frontier_index": index,
                    "basis_row_shears": [list(item) for item in operations],
                    "greedy_xor": greedy.greedy_upper_bound,
                    "final_count": len(finals),
                    "pair_budget": 60 - len(finals),
                    "visited_states": states,
                    "covers_returned": len(covers),
                    "truncated": hit_cap,
                }
            )
            if hit_cap:
                record = {
                    "depth": depth,
                    "frontier_index": index,
                    "basis_row_shears": [list(item) for item in operations],
                    "T": matrix_hex(t_rows),
                    "B": matrix_hex(b_rows),
                    "C": matrix_hex(c_rows),
                    "greedy_xor": greedy.greedy_upper_bound,
                    "final_count": len(finals),
                    "pair_budget": 60 - len(finals),
                    "required_pair_count": sum(
                        row.bit_count() == 2 for row in frozenset((*b_rows, *c_rows))
                    ),
                    "visited_states": states,
                    "covers_returned": len(covers),
                    "hit_state_limit": states >= args.state_limit,
                    "hit_solution_limit": len(covers) >= args.solution_limit,
                }
                truncated.append(record)
                print(
                    f"truncated #{len(truncated)} depth={depth} index={index} "
                    f"greedy={greedy.greedy_upper_bound} finals={len(finals)} "
                    f"states={states} covers={len(covers)}",
                    flush=True,
                )

        if depth == 4:
            break
        next_frontier = []
        for t_rows in frontier:
            b0, c0, operations = seen[t_rows]
            for dst in range(BITS):
                for src in range(BITS):
                    if dst == src:
                        continue
                    t_new, b_new, c_new = list(t_rows), list(b0), list(c0)
                    basis.mutate(t_new, b_new, c_new, dst, src)
                    if max(row.bit_count() for row in (*t_new, *b_new, *c_new)) > 4:
                        continue
                    key = tuple(t_new)
                    if key in seen:
                        continue
                    seen[key] = (
                        tuple(b_new),
                        tuple(c_new),
                        operations + ((dst, src),),
                    )
                    next_frontier.append(key)
        frontier = next_frontier

    document = {
        "state_limit": args.state_limit,
        "solution_limit": args.solution_limit,
        "basis_count": len(seen),
        "cover_searches_attempted": attempted,
        "enumerated_pair_cover_states": total_states,
        "enumerated_pair_cover_count": total_covers,
        "truncated_pair_cover_searches": len(truncated),
        "largest_searches": sorted(
            largest, key=lambda item: item["visited_states"], reverse=True
        )[:20],
        "truncated": truncated,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(document, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
