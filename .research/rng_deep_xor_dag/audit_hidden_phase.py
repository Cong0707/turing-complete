"""Audit every hidden exact-x56 state against the physical phase model.

This is an adapter around the already reviewed RC2/CNF model in
``rng_switch_bdd_cover``.  It removes the old assumption that the greedy pair
cover is exact, enumerates every minimum cover at the newly certified exact
XOR count, and asks whether at most 33 phase-repair gates suffice.
"""

from __future__ import annotations

import argparse
from collections import Counter
import importlib.util
import json
from pathlib import Path
import sys
import time
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PHASE_DIR = ROOT / ".research" / "rng_switch_bdd_cover"
SHELL_GATE = 230
TARGET_GATE = 431
XOR_GATE_PER_BIT = 3
XOR_DELAY = 2


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


batch = load_module("hidden_cover_batch_phase", PHASE_DIR / "batch_phase_audit.py")
phase = load_module("hidden_cover_phase_maxsat", PHASE_DIR / "phase_maxsat.py")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as source:
        return [json.loads(line) for line in source if line.strip()]


def decomposition_variants(
    cover: frozenset[int], finals: frozenset[int], b_rows: tuple[int, ...]
) -> tuple[dict[int, tuple[int, ...]], ...]:
    options = {
        row: tuple(
            option for option in batch.pair_partitions(row) if set(option) <= cover
        )
        for row in finals
    }
    if any(not choices for choices in options.values()):
        return ()
    active = tuple(
        row for row in dict.fromkeys(b_rows) if row in options and len(options[row]) > 1
    )
    total = 1
    for row in active:
        total *= len(options[row])
    return batch.decomposition_variants(cover, finals, b_rows, total, 0x431)


def make_certificate(
    record: dict[str, Any],
    record_index: int,
    cover_index: int,
    variant_index: int,
    cover: frozenset[int],
    decomposition: dict[int, tuple[int, ...]],
    result: Any,
) -> dict[str, Any]:
    xor_count = int(record["exact_xor"])
    correction = int(result.correction_cost)
    return {
        "record_index": record_index,
        "source": record["source"],
        "source_line": record["source_line"],
        "t_sha256": record["t_sha256"],
        "cover_index": cover_index,
        "variant_index": variant_index,
        "xor_count": xor_count,
        "xor_gate": XOR_GATE_PER_BIT * xor_count,
        "correction_cost": correction,
        "total_gate": SHELL_GATE + XOR_GATE_PER_BIT * xor_count + correction,
        "delay": 9,
        "cycles": 66,
        "T": record["T"],
        "B": record["B"],
        "C": record["C"],
        "selected_pairs": [f"{row:08x}" for row in sorted(cover)],
        "decompositions": {
            f"{row:08x}": [f"{fanin:08x}" for fanin in fanins]
            for row, fanins in sorted(decomposition.items())
        },
        "direct_pairs": [[seed, f"{node:08x}"] for seed, node in result.direct_pairs],
        "late_pairs": [[seed, f"{node:08x}"] for seed, node in result.late_pairs],
        "late_seeds": list(result.late_seeds),
        "masked_late_seeds": list(result.masked_late_seeds),
        "direct_occurrences": [list(item) for item in result.direct_occurrences],
        "late_occurrences": [list(item) for item in result.late_occurrences],
        "variables": result.variable_count,
        "clauses": result.clause_count,
        "solve_seconds": result.elapsed_seconds,
    }


def audit(args: argparse.Namespace) -> dict[str, Any]:
    records = read_jsonl(args.input)
    if args.max_records is not None:
        records = records[: args.max_records]
    started = time.perf_counter()
    statuses: Counter[str] = Counter()
    cover_histogram: Counter[int] = Counter()
    solve_count = cover_count = cover_states = 0
    record_results: list[dict[str, Any]] = []
    best: dict[str, Any] | None = None

    for record_index, record in enumerate(records):
        T, B, C = (batch.matrix(record, name) for name in ("T", "B", "C"))
        batch.verify_matrix_identities(T, B, C)
        exact_xor = int(record["exact_xor"])
        _greedy, finals = batch.greedy_pair_cover((*B, *C))
        witness = frozenset(int(value, 16) for value in record["exact_pairs"])
        if len(witness) + len(finals) != exact_xor:
            raise AssertionError(f"stored exact witness has wrong size at record {record_index}")
        if args.witness_only:
            covers = (witness,)
            visited = 0
        else:
            covers, visited, truncated = batch.enumerate_pair_covers(
                (*B, *C),
                exact_xor,
                state_limit=args.cover_state_limit,
                solution_limit=args.cover_solution_limit,
            )
            cover_states += visited
            if truncated:
                raise RuntimeError(f"cover enumeration truncated for record {record_index}")
            minimum = min((len(cover) + len(finals) for cover in covers), default=10_000)
            if minimum != exact_xor:
                raise AssertionError(
                    f"exact cover mismatch at record {record_index}: {minimum} != {exact_xor}"
                )
            covers = tuple(cover for cover in covers if len(cover) + len(finals) == minimum)
            if witness not in covers:
                raise AssertionError(f"stored exact witness missing at record {record_index}")

        candidate_status: Counter[str] = Counter()
        candidate_best: dict[str, Any] | None = None
        candidate_solves = 0
        correction_bound = TARGET_GATE - SHELL_GATE - XOR_GATE_PER_BIT * exact_xor
        if args.cover_only:
            variant_counts = [len(decomposition_variants(cover, finals, B)) for cover in covers]
            cover_count += len(covers)
            cover_histogram[exact_xor] += len(covers)
            record_results.append(
                {
                    "record_index": record_index,
                    "t_sha256": record["t_sha256"],
                    "cover_count": len(covers),
                    "cover_search_states": visited,
                    "variant_counts": variant_counts,
                    "variant_count": sum(variant_counts),
                    "solve_count": 0,
                    "statuses": {},
                    "best": None,
                }
            )
            print(
                f"record={record_index + 1}/{len(records)} covers={len(covers)} "
                f"variants={sum(variant_counts)} cover-only",
                flush=True,
            )
            continue
        for cover_index, cover in enumerate(covers):
            cover_count += 1
            cover_histogram[len(cover) + len(finals)] += 1
            variants = decomposition_variants(cover, finals, B)
            if args.variant_limit is not None:
                variants = variants[: args.variant_limit]
            for variant_index, decomposition in enumerate(variants):
                solve_count += 1
                candidate_solves += 1
                result = phase.solve_phase_maxsat(
                    T,
                    B,
                    decomposition,
                    correction_bound=correction_bound,
                    solver_name=args.solver,
                    timeout_seconds=args.solve_timeout,
                    conflict_budget=args.conflict_budget,
                )
                statuses[result.status] += 1
                candidate_status[result.status] += 1
                if result.status != "sat" or result.correction_cost is None:
                    continue
                item = make_certificate(
                    record,
                    record_index,
                    cover_index,
                    variant_index,
                    cover,
                    decomposition,
                    result,
                )
                if candidate_best is None or (
                    item["total_gate"], item["correction_cost"]
                ) < (candidate_best["total_gate"], candidate_best["correction_cost"]):
                    candidate_best = item
                if best is None or (item["total_gate"], item["t_sha256"]) < (
                    best["total_gate"], best["t_sha256"]
                ):
                    best = item
                    args.certificate.write_text(
                        json.dumps(best, indent=2) + "\n", encoding="utf-8"
                    )
                    print(
                        f"SAT record={record_index} gate={item['total_gate']} "
                        f"repair={item['correction_cost']}",
                        flush=True,
                    )
        record_results.append(
            {
                "record_index": record_index,
                "t_sha256": record["t_sha256"],
                "cover_count": len(covers),
                "cover_search_states": visited,
                "solve_count": candidate_solves,
                "statuses": dict(candidate_status),
                "best": candidate_best,
            }
        )
        print(
            f"record={record_index + 1}/{len(records)} covers={len(covers)} "
            f"solves={candidate_solves} statuses={dict(candidate_status)}",
            flush=True,
        )

    return {
        "schema": 1,
        "model": "exact hidden-x56 cover plus physical U32-Switch phase CNF",
        "cost_model": {
            "ordinary_xor": [3, XOR_DELAY],
            "u1_xor": [3, XOR_DELAY],
            "width_w_xor": ["3*w", XOR_DELAY],
            "fixed_shell_gate": SHELL_GATE,
            "target": [TARGET_GATE, 9, 66],
        },
        "input": str(args.input),
        "witness_only": args.witness_only,
        "variant_limit": args.variant_limit,
        "cover_only": args.cover_only,
        "record_count": len(records),
        "cover_count": cover_count,
        "cover_search_states": cover_states,
        "solve_count": solve_count,
        "cover_xor_histogram": dict(sorted(cover_histogram.items())),
        "statuses": dict(statuses),
        "elapsed_seconds": time.perf_counter() - started,
        "best": best,
        "records": record_results,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=HERE / "radius10-15-hidden-x56.jsonl")
    parser.add_argument("--output", type=Path, default=HERE / "hidden-x56-phase.json")
    parser.add_argument("--certificate", type=Path, default=HERE / "hidden-x56-sat.json")
    parser.add_argument("--cover-state-limit", type=int, default=2_000_000)
    parser.add_argument("--cover-solution-limit", type=int, default=200_000)
    parser.add_argument("--solver", default="g4")
    parser.add_argument("--solve-timeout", type=float, default=None)
    parser.add_argument("--conflict-budget", type=int, default=None)
    parser.add_argument("--witness-only", action="store_true")
    parser.add_argument("--cover-only", action="store_true")
    parser.add_argument("--variant-limit", type=int, default=None)
    parser.add_argument("--max-records", type=int, default=None)
    args = parser.parse_args()
    result = audit(args)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "records"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
