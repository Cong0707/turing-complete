"""Strictly audit every B-decomposition of each greedy depth-two RNG cover.

This research-only script imports matrix/label helpers but no save writer.  It
checks C*T=A, T*C=B and 65 output steps before emitting a candidate.
"""

from __future__ import annotations

import argparse
from functools import reduce
import importlib.util
import json
from operator import mul
from pathlib import Path
import random
import sys
import time


BITS = 32
TARGET = 221


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def rows(record: dict[str, object], key: str) -> tuple[int, ...]:
    values = record[key]
    if not isinstance(values, list) or len(values) != BITS:
        raise ValueError(f"{key} must have 32 rows")
    return tuple(int(str(value), 16) for value in values)


def load_records(paths: list[Path]) -> list[dict[str, object]]:
    unique: dict[tuple[int, ...], dict[str, object]] = {}
    for path in paths:
        with path.open(encoding="utf-8-sig") as stream:
            for line_number, line in enumerate(stream, 1):
                if not line.strip():
                    continue
                record = json.loads(line)
                record["source_path"] = str(path)
                record["source_line"] = line_number
                unique.setdefault(rows(record, "T"), record)
    return list(unique.values())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--min-xor", type=int, default=61)
    parser.add_argument("--max-xor", type=int, default=63)
    parser.add_argument("--component-limit", type=int, default=512)
    parser.add_argument("--global-beam", type=int, default=4096)
    parser.add_argument("--decomposition-limit", type=int, default=1024)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    init = load_module(
        "rng_or_greedy_init", root / ".research/rng_init_reuse/verify_init_reuse.py"
    )
    cover_module = load_module(
        "rng_or_greedy_cover", root / ".research/rng_joint_search_resume/search.py"
    )
    dual = load_module(
        "rng_or_greedy_dual", root / ".research/rng_cost387/search_basis_dualmode.py"
    )
    diagnosis = load_module(
        "rng_or_greedy_diagnosis",
        root / ".research/rng_cost387/agent_finish_x60/diagnose_labels.py",
    )

    started = time.perf_counter()
    records = load_records(args.inputs)
    audited = 0
    variants = 0
    truncated_decomposition_records = 0
    identity_failures = 0
    statuses: dict[str, int] = {}
    frontier: list[dict[str, object]] = []
    best: dict[str, object] | None = None

    for record in records:
        T, B, C = (rows(record, key) for key in ("T", "B", "C"))
        if init.compose(C, T) != init.A or init.compose(T, C) != B:
            identity_failures += 1
            continue
        cover = cover_module.depth_two_cost((*B, *C))
        xor_count = cover.greedy_upper_bound
        if xor_count is None or not args.min_xor <= xor_count <= args.max_xor:
            continue
        audited += 1
        pairs = frozenset(cover.selected_pair_gates)
        finals = frozenset(row for row in (*B, *C) if row.bit_count() in (3, 4))
        available = {
            row: tuple(
                option for option in dual.pair_partitions(row) if set(option) <= pairs
            )
            for row in finals
        }
        active = tuple(
            row
            for row in dict.fromkeys(B)
            if row in available and len(available[row]) > 1
        )
        expected = reduce(mul, (len(available[row]) for row in active), 1)
        sample_limit = min(expected, args.decomposition_limit)
        decompositions = dual.decomposition_variants(
            pairs, finals, B, sample_limit, random.Random(0x387 ^ record["source_line"])
        )
        truncated_decomposition_records += int(expected > sample_limit)

        record_best: dict[str, object] | None = None
        for decomposition in decompositions:
            variants += 1
            status, _ = diagnosis.diagnose(
                dual,
                T,
                B,
                pairs,
                decomposition,
                args.component_limit,
                args.global_beam,
            )
            statuses[status] = statuses.get(status, 0) + 1
            if status != "feasible":
                continue
            result = dual.optimize_labels(
                T,
                B,
                pairs,
                decomposition,
                component_limit=args.component_limit,
                global_beam=args.global_beam,
            )
            if result is None:
                raise AssertionError("diagnosis said feasible but optimizer returned none")
            dual.verify_candidate(init, T, B, C, pairs, result)
            metrics = {
                "xor": xor_count,
                "or": result.or_count,
                "three_xor_plus_or": 3 * xor_count + result.or_count,
                "gate": 166 + 3 * xor_count + result.or_count,
                "delay": 10,
                "cycles": 66,
            }
            candidate = {
                "source_path": record["source_path"],
                "source_line": record["source_line"],
                "T": [f"{row:08x}" for row in T],
                "B": [f"{row:08x}" for row in B],
                "C": [f"{row:08x}" for row in C],
                "selected_pair_gates": [f"{pair:08x}" for pair in sorted(pairs)],
                "decompositions": {
                    f"{row:08x}": [f"{pair:08x}" for pair in option]
                    for row, option in sorted(result.decompositions.items())
                },
                "pair_labels": {
                    f"{pair:08x}": f"{label:08x}"
                    for pair, label in sorted(result.pair_labels.items())
                },
                "pair_pin_seed_bits": {
                    f"{pair:08x}": list(result.orientations[pair])
                    for pair in sorted(result.orientations)
                },
                "mode_pairs": [
                    {"seed": seed, "state": state}
                    for seed, state in sorted(result.mappings)
                ],
                "metrics": metrics,
            }
            if record_best is None or metrics["three_xor_plus_or"] < record_best["metrics"]["three_xor_plus_or"]:
                record_best = candidate
            if best is None or metrics["three_xor_plus_or"] < best["metrics"]["three_xor_plus_or"]:
                best = candidate

        frontier.append(
            {
                "source_path": record["source_path"],
                "source_line": record["source_line"],
                "xor": xor_count,
                "decomposition_count": expected,
                "best_or": None if record_best is None else record_best["metrics"]["or"],
            }
        )

    document: dict[str, object] = {
        "status": (
            "target_candidate"
            if best is not None and best["metrics"]["three_xor_plus_or"] <= TARGET
            else "frontier_only"
        ),
        "input_record_count": len(records),
        "audited_record_count": audited,
        "decomposition_variant_count": variants,
        "truncated_decomposition_record_count": truncated_decomposition_records,
        "identity_failure_count": identity_failures,
        "diagnosis_status_counts": dict(sorted(statuses.items())),
        "elapsed_seconds": round(time.perf_counter() - started, 6),
        "frontier": frontier,
    }
    if best is not None:
        document["best_candidate"] = best
    args.output.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in document.items() if key != "frontier"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
