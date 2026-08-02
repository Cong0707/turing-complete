"""Audit a 65-cycle, no-RAM dual-mode RNG initialization.

The first tick must do two different jobs through the shared XOR network:

* emit ``A * seed`` immediately;
* store ``T * A * seed`` so tick 1 emits ``A^2 * seed`` rather than repeating
  the first output.

Steady operation remains ``output=C*q`` and ``q_next=B*q``.  For a 10-delay
candidate to beat 431/9/66 its gate count must be at most 393, so the fixed
166-gate shell leaves ``3*XOR + OR <= 227``.  Every one-bit XOR is charged as
3 gates / 2 delay.  This script is offline-only and has no save/game imports.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import random
import sys
import time
from typing import Any, Sequence


BITS = 32
FIXED_SHELL = 166
TARGET_GATE = 393
TARGET_DELAY = 10
TARGET_CYCLES = 65


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def matrix(record: dict[str, Any], key: str) -> tuple[int, ...]:
    values = record[key]
    if not isinstance(values, list) or len(values) != BITS:
        raise ValueError(f"{key} must contain 32 rows")
    return tuple(int(str(value), 16) for value in values)


def matrix_hex(rows: Sequence[int]) -> list[str]:
    return [f"{row:08x}" for row in rows]


def label_of(
    steady: int,
    pair_labels: dict[int, int],
    decompositions: dict[int, tuple[int, ...]],
    mappings: frozenset[tuple[int, int]],
    target: int,
) -> int:
    weight = steady.bit_count()
    if weight == 1:
        state = (steady & -steady).bit_length() - 1
        if target.bit_count() != 1:
            raise AssertionError("unit steady row needs a unit load label")
        seed = (target & -target).bit_length() - 1
        if (seed, state) not in mappings:
            raise AssertionError("unit load mapping is absent")
        return target
    if weight == 2:
        return pair_labels[steady]
    if weight == 3:
        pair = decompositions[steady][0]
        direct = steady ^ pair
        residual = target ^ pair_labels[pair]
        if residual.bit_count() > 1:
            raise AssertionError("weight-3 residual is not a unit")
        if residual:
            state = (direct & -direct).bit_length() - 1
            seed = (residual & -residual).bit_length() - 1
            if (seed, state) not in mappings:
                raise AssertionError("weight-3 residual mapping is absent")
        return pair_labels[pair] ^ residual
    if weight == 4:
        left, right = decompositions[steady]
        return pair_labels[left] ^ pair_labels[right]
    raise AssertionError(f"unsupported steady row weight {weight}")


def verify_candidate(init, T, B, C, pairs, result) -> None:
    if init.compose(C, T) != init.A or init.compose(T, C) != B:
        raise AssertionError("matrix identity failed")
    load_state = init.compose(T, init.A)
    constraints = ((*load_state, *init.A), (*B, *C))
    for target, steady in zip(*constraints, strict=True):
        actual = label_of(
            steady,
            result.pair_labels,
            result.decompositions,
            result.mappings,
            target,
        )
        if actual != target:
            raise AssertionError("tick-zero dual label mismatch")

    seeds = [0, 1, 2, 0x12345678, 0xFFFFFFFF, 0x80000000]
    generator = random.Random(20260802)
    seeds.extend(generator.getrandbits(32) for _ in range(64))
    for seed in seeds:
        natural = init.xorshift32(seed)
        encoded = init.apply_matrix(load_state, seed)
        if init.apply_matrix(C, encoded) != init.xorshift32(natural):
            raise AssertionError("tick-one state starts at the wrong phase")
        for _ in range(1, TARGET_CYCLES):
            wanted = init.xorshift32(natural)
            actual = init.apply_matrix(C, encoded)
            if actual != wanted:
                raise AssertionError("65-cycle visible stream mismatch")
            natural = wanted
            encoded = init.apply_matrix(B, encoded)


def load_records(paths: Sequence[Path]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    seen: set[tuple[int, ...]] = set()
    for path in paths:
        for line_number, line in enumerate(
            path.read_text(encoding="utf-8-sig").splitlines(), 1
        ):
            if not line.strip():
                continue
            record = json.loads(line)
            key = matrix(record, "T")
            if key in seen:
                continue
            seen.add(key)
            record["source_path"] = str(path.resolve())
            record["source_line"] = line_number
            records.append(record)
    return records


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", type=Path, nargs="+")
    parser.add_argument("--xor", type=int, default=56)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--component-limit", type=int, default=16_384)
    parser.add_argument("--global-beam", type=int, default=100_000)
    parser.add_argument("--state-limit", type=int, default=2_000_000)
    parser.add_argument("--solution-limit", type=int, default=200_000)
    parser.add_argument("--first", type=int, default=1)
    parser.add_argument("--last", type=int)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    init = load_module(
        "rng_65_init", root / ".research/rng_init_reuse/verify_init_reuse.py"
    )
    dual = load_module(
        "rng_65_dual", root / ".research/rng_cost387/search_basis_dualmode.py"
    )
    cover_module = load_module(
        "rng_65_cover", root / ".research/rng_switch_bdd_cover/batch_phase_audit.py"
    )

    records = load_records(args.inputs)
    last = len(records) if args.last is None else min(args.last, len(records))
    selected_records = records[args.first - 1 : last]
    started = time.perf_counter()
    cover_count = 0
    truncated_count = 0
    label_sat_count = 0
    best = None
    frontier = []

    for local_index, record in enumerate(selected_records, args.first):
        T, B, C = (matrix(record, key) for key in ("T", "B", "C"))
        if init.compose(C, T) != init.A or init.compose(T, C) != B:
            raise AssertionError(f"matrix identity failed at record {local_index}")
        finals = frozenset(
            row for row in (*B, *C) if row.bit_count() in (3, 4)
        )
        covers, visited, truncated = cover_module.enumerate_pair_covers(
            (*B, *C),
            args.xor,
            state_limit=args.state_limit,
            solution_limit=args.solution_limit,
        )
        truncated_count += int(truncated)
        record_best = None
        for pairs in covers:
            if len(pairs) + len(finals) != args.xor:
                continue
            decompositions = {}
            for row in finals:
                options = tuple(
                    option
                    for option in dual.pair_partitions(row)
                    if set(option) <= pairs
                )
                if len(options) != 1:
                    raise AssertionError(
                        "audited x56 covers should have one decomposition per final"
                    )
                decompositions[row] = options[0]
            cover_count += 1
            load_state = init.compose(T, init.A)
            result = dual.optimize_labels(
                (*load_state, *init.A),
                (*B, *C),
                pairs,
                decompositions,
                component_limit=args.component_limit,
                global_beam=args.global_beam,
            )
            if result is None:
                continue
            label_sat_count += 1
            verify_candidate(init, T, B, C, pairs, result)
            gate = FIXED_SHELL + 3 * args.xor + result.or_count
            metrics = {
                "xor": args.xor,
                "or": result.or_count,
                "gate": gate,
                "delay": TARGET_DELAY,
                "cycles": TARGET_CYCLES,
                "energy": gate * TARGET_DELAY * TARGET_CYCLES,
            }
            candidate = {
                "source_path": record["source_path"],
                "source_line": record["source_line"],
                "T": matrix_hex(T),
                "B": matrix_hex(B),
                "C": matrix_hex(C),
                "load_state": matrix_hex(load_state),
                "selected_pair_gates": matrix_hex(sorted(pairs)),
                "decompositions": {
                    f"{row:08x}": matrix_hex(option)
                    for row, option in sorted(decompositions.items())
                },
                "pair_labels": {
                    f"{row:08x}": f"{label:08x}"
                    for row, label in sorted(result.pair_labels.items())
                },
                "pair_pin_seed_bits": {
                    f"{row:08x}": list(value)
                    for row, value in sorted(result.orientations.items())
                },
                "mode_pairs": [
                    {"seed": seed, "state": state}
                    for seed, state in sorted(result.mappings)
                ],
                "metrics": metrics,
            }
            if record_best is None or metrics["gate"] < record_best["metrics"]["gate"]:
                record_best = candidate
            if best is None or metrics["gate"] < best["metrics"]["gate"]:
                best = candidate
                print(
                    f"best gate={gate} xor={args.xor} or={result.or_count} "
                    f"record={local_index}",
                    flush=True,
                )
        frontier.append(
            {
                "record": local_index,
                "source_line": record["source_line"],
                "cover_search_visited": visited,
                "cover_search_truncated": truncated,
                "cover_count": len(covers),
                "best": None if record_best is None else record_best["metrics"],
            }
        )
        if best is not None and best["metrics"]["gate"] <= TARGET_GATE:
            break

    document = {
        "schema": 1,
        "status": (
            "target_candidate"
            if best is not None and best["metrics"]["gate"] <= TARGET_GATE
            else "frontier_only"
        ),
        "model": {
            "tick0_output": "A*seed",
            "tick0_state": "T*A*seed",
            "steady_output": "C*q",
            "steady_state": "B*q",
            "gate": "166 + 3*XOR + OR",
            "xor_cost": [3, 2],
            "target": [TARGET_GATE, TARGET_DELAY, TARGET_CYCLES],
        },
        "record_count": len(selected_records),
        "cover_count": cover_count,
        "truncated_cover_search_count": truncated_count,
        "label_sat_count": label_sat_count,
        "limits": {
            "component_limit": args.component_limit,
            "global_beam": args.global_beam,
            "state_limit": args.state_limit,
            "solution_limit": args.solution_limit,
        },
        "elapsed_seconds": round(time.perf_counter() - started, 6),
        "frontier": frontier,
    }
    if best is not None:
        document["best_candidate"] = best
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(document, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {key: value for key, value in document.items() if key != "frontier"},
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
