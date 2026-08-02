"""Complete the five x60 pair-cover searches truncated at 100,000 states.

The five instances are identified by their deterministic row-shear paths from
the verified fixed basis.  For each instance this tool reruns the old cap and a
250,000-state cap, compares the exact returned cover sets, and records the
number of B-row decomposition assignments for every complete cover.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys


CASES = (
    ((17, 22), (18, 23), (22, 27), (23, 28)),
    ((17, 22), (18, 23), (23, 28)),
    ((17, 22), (18, 23), (22, 27)),
    ((17, 22), (18, 23), (19, 24), (24, 29)),
    ((17, 22), (18, 23), (18, 31), (23, 28)),
)


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


def cover_hex(cover):
    return [f"{pair:08x}" for pair in sorted(cover)]


def digest_covers(covers) -> str:
    payload = "\n".join(
        ",".join(f"{pair:08x}" for pair in sorted(cover)) for cover in covers
    ).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def decomposition_count(dual, cover, finals, b_rows) -> int:
    covered = {
        row: tuple(
            option
            for option in dual.pair_partitions(row)
            if set(option) <= cover
        )
        for row in finals
    }
    if any(not options for options in covered.values()):
        raise AssertionError("complete cover does not cover every final")
    active = tuple(
        row
        for row in dict.fromkeys(b_rows)
        if row in covered and len(covered[row]) > 1
    )
    count = 1
    for row in active:
        count *= len(covered[row])
    return count


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--old-limit", type=int, default=100_000)
    parser.add_argument("--complete-limit", type=int, default=250_000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    repo = Path(__file__).resolve().parents[3]
    dual = load_module(
        "finish_five_dual", repo / ".research/rng_cost387/search_basis_dualmode.py"
    )
    init = load_module(
        "finish_five_init", repo / ".research/rng_init_reuse/verify_init_reuse.py"
    )
    basis = load_module(
        "finish_five_basis", repo / ".research/rng_joint_search_resume/search.py"
    )

    records = []
    for case_index, operations in enumerate(CASES, 1):
        t_rows, b_rows, c_rows = map(list, (init.T, init.B, init.C))
        for dst, src in operations:
            basis.mutate(t_rows, b_rows, c_rows, dst, src)
        t_rows, b_rows, c_rows = map(tuple, (t_rows, b_rows, c_rows))
        if max(row.bit_count() for row in (*t_rows, *b_rows, *c_rows)) > 4:
            raise AssertionError("recorded path is not radius-four feasible")

        greedy = basis.depth_two_cost((*b_rows, *c_rows))
        finals = frozenset(
            row for row in (*b_rows, *c_rows) if row.bit_count() in (3, 4)
        )
        budget = 60 - len(finals)
        old_covers, old_states, old_truncated = dual.enumerate_pair_covers(
            (*b_rows, *c_rows),
            budget,
            state_limit=args.old_limit,
            solution_limit=10_000,
        )
        covers, states, truncated = dual.enumerate_pair_covers(
            (*b_rows, *c_rows),
            budget,
            state_limit=args.complete_limit,
            solution_limit=10_000,
        )
        old_set, complete_set = set(old_covers), set(covers)
        variants = [
            decomposition_count(dual, cover, finals, b_rows) for cover in covers
        ]
        record = {
            "case": case_index,
            "basis_row_shears": [list(item) for item in operations],
            "T": matrix_hex(t_rows),
            "B": matrix_hex(b_rows),
            "C": matrix_hex(c_rows),
            "greedy_xor": greedy.greedy_upper_bound,
            "final_count": len(finals),
            "pair_budget": budget,
            "old": {
                "state_limit": args.old_limit,
                "visited_states": old_states,
                "truncated": old_truncated,
                "cover_count": len(old_covers),
                "cover_digest_sha256": digest_covers(old_covers),
            },
            "complete": {
                "state_limit": args.complete_limit,
                "visited_states": states,
                "truncated": truncated,
                "cover_count": len(covers),
                "cover_digest_sha256": digest_covers(covers),
            },
            "new_cover_count": len(complete_set - old_set),
            "lost_cover_count": len(old_set - complete_set),
            "decomposition_assignment_counts": variants,
            "max_decomposition_assignments": max(variants, default=0),
            "covers": [cover_hex(cover) for cover in covers],
        }
        records.append(record)
        print(
            f"case={case_index} old={old_states}/{len(old_covers)} "
            f"complete={states}/{len(covers)} new={record['new_cover_count']} "
            f"max_variants={record['max_decomposition_assignments']}",
            flush=True,
        )

    document = {
        "scope": "the five x60 pair-cover searches truncated by the old 100k cap",
        "old_limit": args.old_limit,
        "complete_limit": args.complete_limit,
        "all_old_runs_truncated": all(item["old"]["truncated"] for item in records),
        "all_complete_runs_finished": all(
            not item["complete"]["truncated"] for item in records
        ),
        "old_total_states": sum(item["old"]["visited_states"] for item in records),
        "complete_total_states": sum(
            item["complete"]["visited_states"] for item in records
        ),
        "old_total_covers": sum(item["old"]["cover_count"] for item in records),
        "complete_total_covers": sum(
            item["complete"]["cover_count"] for item in records
        ),
        "new_cover_count": sum(item["new_cover_count"] for item in records),
        "cases": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in document.items() if key != "cases"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
