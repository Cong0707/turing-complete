"""Audit RNG basis-walk JSONL records with the existing exact replay model.

The sampler's metrics are treated as hints only.  This script recomputes every
matrix identity and depth-two cover, enumerates alternate pair covers within a
bounded budget, solves tick-zero labels, and emits a standalone certificate
for the best verified candidate.  It never imports save-writing modules.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import random
import sys
import time
from typing import Iterable, Sequence


BITS = 32
TARGET_BUDGET = 221


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


def matrix_hex(rows: Sequence[int]) -> list[str]:
    return [f"{row:08x}" for row in rows]


def load_records(paths: Iterable[Path]) -> list[dict[str, object]]:
    by_basis: dict[tuple[int, ...], dict[str, object]] = {}
    for path in paths:
        with path.open(encoding="utf-8") as stream:
            for line_number, line in enumerate(stream, start=1):
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                    key = matrix(record, "T")
                except (json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
                    raise ValueError(f"{path}:{line_number}: {error}") from error
                record["source_path"] = str(path)
                record["source_line"] = line_number
                by_basis.setdefault(key, record)
    return list(by_basis.values())


def candidate_key(record: dict[str, object]) -> tuple[int, ...]:
    cover = record.get("cover", {})
    mode = record.get("mode", {})
    structural = record.get("structural", {})
    return (
        int(cover.get("greedy_xor", 1000)),
        int(mode.get("penalty", 1000)),
        int(cover.get("lower", 1000)),
        int(structural.get("weight", 1000)),
        int(record.get("step", 0)),
    )


def result_certificate(
    source: dict[str, object],
    T: Sequence[int],
    B: Sequence[int],
    C: Sequence[int],
    pairs: frozenset[int],
    dual,
    xor_count: int,
) -> dict[str, object]:
    gate = 166 + 3 * xor_count + dual.or_count
    return {
        "source_path": source["source_path"],
        "source_line": source["source_line"],
        "source_step": source.get("step"),
        "T": matrix_hex(T),
        "B": matrix_hex(B),
        "C": matrix_hex(C),
        "selected_pair_gates": [f"{pair:08x}" for pair in sorted(pairs)],
        "decompositions": {
            f"{row:08x}": [f"{pair:08x}" for pair in option]
            for row, option in sorted(dual.decompositions.items())
        },
        "pair_labels": {
            f"{pair:08x}": f"{label:08x}"
            for pair, label in sorted(dual.pair_labels.items())
        },
        "pair_pin_seed_bits": {
            f"{pair:08x}": list(dual.orientations[pair])
            for pair in sorted(dual.orientations)
        },
        "mode_pairs": [
            {"seed": seed, "state": state}
            for seed, state in sorted(dual.mappings)
        ],
        "metrics": {
            "xor": xor_count,
            "or": dual.or_count,
            "three_xor_plus_or": 3 * xor_count + dual.or_count,
            "gate": gate,
            "delay": 10,
            "cycles": 66,
            "energy": gate * 10 * 66,
            "beats_256014": gate * 10 * 66 < 256014,
        },
    }


def audit(args) -> dict[str, object]:
    root = Path(__file__).resolve().parents[2]
    init_module = load_module(
        "rng_basis_v2_init", root / ".research/rng_init_reuse/verify_init_reuse.py"
    )
    cover_module = load_module(
        "rng_basis_v2_cover", root / ".research/rng_joint_search_resume/search.py"
    )
    dual_module = load_module(
        "rng_basis_v2_dual", root / ".research/rng_cost387/search_basis_dualmode.py"
    )

    all_records = load_records(args.inputs)
    records = [
        record
        for record in all_records
        if args.min_xor
        <= int(record.get("cover", {}).get("greedy_xor", 1000))
        <= args.max_xor
    ]
    records.sort(key=candidate_key)
    selected = records[: args.candidate_limit]
    started = time.perf_counter()
    identity_failures = 0
    metric_mismatches = 0
    audited_cover_count = 0
    audited_decomposition_count = 0
    truncated_cover_searches = 0
    dual_feasible = 0
    frontier: list[dict[str, object]] = []
    best: dict[str, object] | None = None

    for record_index, record in enumerate(selected):
        T = matrix(record, "T")
        B = matrix(record, "B")
        C = matrix(record, "C")
        if (
            init_module.compose(C, T) != init_module.A
            or init_module.compose(T, C) != B
            or max(row.bit_count() for row in (*T, *B, *C)) > 4
        ):
            identity_failures += 1
            continue

        greedy = cover_module.depth_two_cost((*B, *C))
        reported_xor = int(record.get("cover", {}).get("greedy_xor", 1000))
        metric_mismatches += int(greedy.greedy_upper_bound != reported_xor)
        finals = frozenset(row for row in (*B, *C) if row.bit_count() in (3, 4))
        pair_budget = args.max_xor - len(finals)
        if pair_budget < 0:
            continue

        covers: list[frozenset[int]] = []
        if greedy.greedy_upper_bound is not None and greedy.greedy_upper_bound <= args.max_xor:
            covers.append(frozenset(greedy.selected_pair_gates))
        enumerated, visited, truncated = dual_module.enumerate_pair_covers(
            (*B, *C),
            pair_budget,
            state_limit=args.cover_state_limit,
            solution_limit=args.cover_solution_limit,
        )
        del visited
        truncated_cover_searches += int(truncated)
        covers.extend(enumerated)
        covers = list(
            dict.fromkeys(
                sorted(covers, key=lambda cover: (len(cover), tuple(sorted(cover))))
            )
        )

        record_best: tuple[int, int] | None = None
        failure = "no_pair_cover"
        for cover_index, pairs in enumerate(covers):
            xor_count = len(pairs) + len(finals)
            if xor_count > args.max_xor:
                continue
            audited_cover_count += 1
            variants = dual_module.decomposition_variants(
                pairs,
                finals,
                B,
                args.decomposition_samples,
                random.Random(args.seed ^ int(record.get("step", 0)) ^ cover_index),
            )
            for decompositions in variants:
                audited_decomposition_count += 1
                dual = dual_module.optimize_labels(
                    T,
                    B,
                    pairs,
                    decompositions,
                    component_limit=args.component_limit,
                    global_beam=args.global_beam,
                )
                if dual is None:
                    failure = "tick0_label_unsat"
                    continue
                dual_module.verify_candidate(init_module, T, B, C, pairs, dual)
                dual_feasible += 1
                metric = (3 * xor_count + dual.or_count, dual.or_count)
                if record_best is None or metric < record_best:
                    record_best = metric
                certificate = result_certificate(record, T, B, C, pairs, dual, xor_count)
                if best is None or (
                    certificate["metrics"]["three_xor_plus_or"],
                    certificate["metrics"]["xor"],
                    certificate["metrics"]["or"],
                ) < (
                    best["metrics"]["three_xor_plus_or"],
                    best["metrics"]["xor"],
                    best["metrics"]["or"],
                ):
                    best = certificate
                    print(
                        "best "
                        f"budget={certificate['metrics']['three_xor_plus_or']} "
                        f"xor={xor_count} or={dual.or_count} "
                        f"step={record.get('step')}",
                        flush=True,
                    )

        frontier.append(
            {
                "source_path": record["source_path"],
                "source_line": record["source_line"],
                "step": record.get("step"),
                "recomputed_greedy_xor": greedy.greedy_upper_bound,
                "lower_bound": greedy.lower_bound,
                "cover_count": len(covers),
                "cover_search_truncated": truncated,
                "best_three_xor_plus_or": None if record_best is None else record_best[0],
                "best_or": None if record_best is None else record_best[1],
                "status": "dual_feasible" if record_best is not None else failure,
            }
        )
        if best is not None and best["metrics"]["three_xor_plus_or"] <= TARGET_BUDGET:
            break
        if not (record_index + 1) % 25:
            print(
                f"audited records={record_index + 1} covers={audited_cover_count} "
                f"variants={audited_decomposition_count}",
                flush=True,
            )

    document: dict[str, object] = {
        "status": (
            "target_candidate"
            if best is not None and best["metrics"]["three_xor_plus_or"] <= TARGET_BUDGET
            else "frontier_only"
        ),
        "metric_model": {
            "gate": "166 + 3*XOR + OR",
            "delay": 10,
            "cycles": 66,
            "target_three_xor_plus_or": TARGET_BUDGET,
        },
        "input_record_count": len(all_records),
        "filtered_record_count": len(records),
        "selected_record_count": len(selected),
        "identity_failure_count": identity_failures,
        "sampler_metric_mismatch_count": metric_mismatches,
        "audited_pair_cover_count": audited_cover_count,
        "audited_decomposition_count": audited_decomposition_count,
        "truncated_pair_cover_search_count": truncated_cover_searches,
        "dual_feasible_variant_count": dual_feasible,
        "elapsed_seconds": round(time.perf_counter() - started, 6),
        "limits": {
            "candidate_limit": args.candidate_limit,
            "min_xor": args.min_xor,
            "max_xor": args.max_xor,
            "cover_state_limit": args.cover_state_limit,
            "cover_solution_limit": args.cover_solution_limit,
            "decomposition_samples": args.decomposition_samples,
            "component_limit": args.component_limit,
            "global_beam": args.global_beam,
        },
        "frontier": frontier,
    }
    if best is not None:
        document["best_candidate"] = best
    return document


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", type=Path, nargs="+")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--candidate-limit", type=int, default=250)
    parser.add_argument("--min-xor", type=int, default=0)
    parser.add_argument("--max-xor", type=int, default=61)
    parser.add_argument("--cover-state-limit", type=int, default=250_000)
    parser.add_argument("--cover-solution-limit", type=int, default=2_000)
    parser.add_argument("--decomposition-samples", type=int, default=512)
    parser.add_argument("--component-limit", type=int, default=512)
    parser.add_argument("--global-beam", type=int, default=4096)
    parser.add_argument("--seed", type=lambda value: int(value, 0), default=0x387)
    args = parser.parse_args()
    document = audit(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in document.items() if key != "frontier"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
