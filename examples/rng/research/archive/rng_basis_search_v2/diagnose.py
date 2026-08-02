"""Classify radius-search tick-zero failures and expose every search cap.

This is an offline-only companion to ``audit.py``.  It recomputes pair covers,
enumerates every B-row decomposition assignment, and reports whether a failed
labeling is structural or depends on the bounded label beam.
"""

from __future__ import annotations

import argparse
from collections import Counter
from functools import reduce
import importlib.util
import json
from operator import mul
from pathlib import Path
import random
import sys
import time


BITS = 32
BEAM_DEPENDENT = {"beam_missing_all_seed_coverage", "global_beam_empty"}


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def matrix(record: dict[str, object], name: str) -> tuple[int, ...]:
    values = record[name]
    if not isinstance(values, list) or len(values) != BITS:
        raise ValueError(f"{name} is not a 32-row matrix")
    return tuple(int(str(value), 16) for value in values)


def load_records(paths: list[Path]) -> list[dict[str, object]]:
    by_basis: dict[tuple[int, ...], dict[str, object]] = {}
    for path in paths:
        with path.open(encoding="utf-8-sig") as stream:
            for line_number, line in enumerate(stream, start=1):
                if not line.strip():
                    continue
                record = json.loads(line)
                record["source_path"] = str(path)
                record["source_line"] = line_number
                by_basis.setdefault(matrix(record, "T"), record)
    return list(by_basis.values())


def decomposition_count(dual, pairs, finals, b_rows) -> int:
    covered = {
        row: tuple(
            option for option in dual.pair_partitions(row) if set(option) <= pairs
        )
        for row in finals
    }
    if any(not options for options in covered.values()):
        return 0
    active = tuple(
        row
        for row in dict.fromkeys(b_rows)
        if row in covered and len(covered[row]) > 1
    )
    return reduce(mul, (len(covered[row]) for row in active), 1)


def run(args) -> dict[str, object]:
    root = Path(__file__).resolve().parents[2]
    init = load_module(
        "rng_basis_diag_init", root / ".research/rng_init_reuse/verify_init_reuse.py"
    )
    cover_module = load_module(
        "rng_basis_diag_cover", root / ".research/rng_joint_search_resume/search.py"
    )
    dual = load_module(
        "rng_basis_diag_dual", root / ".research/rng_cost387/search_basis_dualmode.py"
    )
    diagnosis = load_module(
        "rng_basis_diag_labels",
        root / ".research/rng_cost387/agent_finish_x60/diagnose_labels.py",
    )

    records = [
        record
        for record in load_records(args.inputs)
        if args.min_xor
        <= int(record.get("cover", {}).get("greedy_xor", 1000))
        <= args.max_xor
    ]
    records.sort(
        key=lambda record: (
            int(record.get("cover", {}).get("greedy_xor", 1000)),
            int(record.get("mode", {}).get("penalty", 1000)),
            int(record.get("step", 0)),
        )
    )

    started = time.perf_counter()
    counts: Counter[str] = Counter()
    xor_counts: Counter[int] = Counter()
    cover_count = 0
    cover_states = 0
    truncated_covers = 0
    variant_count = 0
    maximum_assignments = 0
    identity_failures = 0
    beam_cases: list[dict[str, object]] = []

    for record_index, record in enumerate(records):
        T = matrix(record, "T")
        B = matrix(record, "B")
        C = matrix(record, "C")
        if init.compose(C, T) != init.A or init.compose(T, C) != B:
            identity_failures += 1
            continue
        finals = frozenset(row for row in (*B, *C) if row.bit_count() in (3, 4))
        pair_budget = args.max_xor - len(finals)
        if pair_budget < 0:
            continue

        greedy = cover_module.depth_two_cost((*B, *C))
        covers: list[frozenset[int]] = []
        if greedy.greedy_upper_bound is not None and greedy.greedy_upper_bound <= args.max_xor:
            covers.append(frozenset(greedy.selected_pair_gates))
        enumerated, visited, truncated = dual.enumerate_pair_covers(
            (*B, *C),
            pair_budget,
            state_limit=args.cover_state_limit,
            solution_limit=args.cover_solution_limit,
        )
        cover_states += visited
        truncated_covers += int(truncated)
        covers.extend(enumerated)
        covers = list(
            dict.fromkeys(sorted(covers, key=lambda item: (len(item), tuple(sorted(item)))))
        )

        for cover_index, pairs in enumerate(covers):
            xor_count = len(pairs) + len(finals)
            if xor_count > args.max_xor:
                continue
            cover_count += 1
            xor_counts[xor_count] += 1
            expected = decomposition_count(dual, pairs, finals, B)
            maximum_assignments = max(maximum_assignments, expected)
            variants = dual.decomposition_variants(
                pairs,
                finals,
                B,
                max(1, expected),
                random.Random(args.seed ^ int(record.get("step", 0)) ^ cover_index),
            )
            if len(variants) != expected:
                raise AssertionError(
                    f"expected {expected} exhaustive decompositions, got {len(variants)}"
                )
            for variant_index, decompositions in enumerate(variants):
                variant_count += 1
                status, detail = diagnosis.diagnose(
                    dual,
                    T,
                    B,
                    pairs,
                    decompositions,
                    args.component_limit,
                    args.global_beam,
                )
                counts[status] += 1
                if status in BEAM_DEPENDENT or status == "feasible":
                    beam_cases.append(
                        {
                            "source_path": record["source_path"],
                            "source_line": record["source_line"],
                            "step": record.get("step"),
                            "xor": xor_count,
                            "cover_index": cover_index,
                            "variant_index": variant_index,
                            "status": status,
                            "detail": detail,
                        }
                    )

        if not (record_index + 1) % 100:
            print(
                f"diagnosed records={record_index + 1} covers={cover_count} "
                f"variants={variant_count}",
                flush=True,
            )

    exact = (
        identity_failures == 0
        and truncated_covers == 0
        and not beam_cases
    )
    return {
        "scope": "all emitted bases in the requested greedy-XOR interval",
        "status": "structurally_closed" if exact else "needs_followup",
        "input_record_count": len(load_records(args.inputs)),
        "selected_record_count": len(records),
        "identity_failure_count": identity_failures,
        "pair_cover_count": cover_count,
        "pair_cover_states": cover_states,
        "truncated_pair_cover_search_count": truncated_covers,
        "decomposition_variant_count": variant_count,
        "maximum_decomposition_assignments_per_cover": maximum_assignments,
        "cover_count_by_xor": {str(key): value for key, value in sorted(xor_counts.items())},
        "failure_counts": dict(sorted(counts.items())),
        "beam_or_feasible_cases": beam_cases,
        "limits": {
            "min_xor": args.min_xor,
            "max_xor": args.max_xor,
            "cover_state_limit": args.cover_state_limit,
            "cover_solution_limit": args.cover_solution_limit,
            "component_limit": args.component_limit,
            "global_beam": args.global_beam,
        },
        "elapsed_seconds": round(time.perf_counter() - started, 6),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", type=Path, nargs="+")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--min-xor", type=int, default=0)
    parser.add_argument("--max-xor", type=int, default=60)
    parser.add_argument("--cover-state-limit", type=int, default=250_000)
    parser.add_argument("--cover-solution-limit", type=int, default=2_000)
    parser.add_argument("--component-limit", type=int, default=512)
    parser.add_argument("--global-beam", type=int, default=4096)
    parser.add_argument("--seed", type=lambda value: int(value, 0), default=0x387)
    args = parser.parse_args()
    document = run(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in document.items() if key != "beam_or_feasible_cases"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
