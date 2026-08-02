"""Rank lifted-state candidates with concrete cancellation-aware covers.

The exact PySAT model in ``rng_depth2_pysat/search.py`` permits arbitrary
overlap and cancellation at the final XOR2/Switch-XOR3 gate.  Rebuilding and
solving that model for every search candidate is too expensive, so this tool
reuses its reduced option enumeration and applies deterministic multi-start
coordinate descent to the shared first-level forms.

Every reported cover is a verified implementation in the same restricted
depth-two library.  It is an upper bound, not an optimum or UNSAT proof.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import random
import sys
import time
from typing import Iterable, Sequence


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

import optimize_pruned38 as lift  # noqa: E402
import proxy_v2_cost_eval as partition_proxy  # noqa: E402


@dataclass(frozen=True)
class CoverOption:
    final_units: int
    required: tuple[int, ...]
    sources: tuple[int, ...]


@dataclass(frozen=True)
class CandidateRecord:
    candidate: lift.Candidate
    sources: tuple[tuple[str, tuple[int, ...]], ...]
    targets: tuple[int, ...]
    active_hidden: tuple[int, ...]
    state_bits: int
    features: tuple[int, int, int, int]


@dataclass
class CoverResult:
    units: int
    choices: list[int]
    counts: Counter[int]
    restarts: int
    coordinate_moves: int


def load_backend():
    path = ROOT / ".research" / "rng_depth2_pysat" / "search.py"
    spec = importlib.util.spec_from_file_location("rng_cancellation_proxy_backend", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import backend {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module, path


def candidate_key(candidate: lift.Candidate) -> tuple[tuple[int, ...], tuple[int, ...]]:
    return candidate.x_rows, candidate.d_rows


def build_record(
    candidate: lift.Candidate,
    sources: tuple[tuple[str, tuple[int, ...]], ...],
) -> CandidateRecord:
    h_rows, o_rows, active_hidden = lift.build_pruned(
        candidate.x_rows, candidate.d_rows
    )
    targets = tuple(sorted({row for row in h_rows + o_rows if row.bit_count() >= 2}))
    weights = tuple(row.bit_count() for row in targets)
    features = (
        len(targets),
        sum(max(0, weight - 4) for weight in weights),
        sum(weights),
        max(weights, default=0),
    )
    return CandidateRecord(
        candidate=candidate,
        sources=sources,
        targets=targets,
        active_hidden=active_hidden,
        state_bits=len(h_rows),
        features=features,
    )


def load_records(
    paths: Sequence[Path],
    active: int | None,
    selection: str,
) -> list[CandidateRecord]:
    merged: dict[
        tuple[tuple[int, ...], tuple[int, ...]],
        tuple[lift.Candidate, list[tuple[str, tuple[int, ...]]]],
    ] = {}
    for path in paths:
        for candidate in lift.load_log_candidates(path, selection):
            key = candidate_key(candidate)
            if key not in merged:
                merged[key] = (candidate, [])
            merged[key][1].append((str(path.resolve()), candidate.source_lines))

    records = []
    target_seen: set[tuple[int, tuple[int, ...]]] = set()
    for candidate, sources in merged.values():
        record = build_record(candidate, tuple(sources))
        if active is not None and len(record.active_hidden) != active:
            continue
        semantic_key = record.state_bits, record.targets
        if semantic_key in target_seen:
            continue
        target_seen.add(semantic_key)
        records.append(record)
    return records


def diverse_selection(records: Sequence[CandidateRecord], limit: int) -> list[CandidateRecord]:
    if limit <= 0 or len(records) <= limit:
        return list(records)

    def key_for(record: CandidateRecord, mode: int) -> tuple[int, ...]:
        targets, excess, total, maximum = record.features
        if mode == 0:
            return targets, excess, total, maximum
        if mode == 1:
            return excess, targets, total, maximum
        if mode == 2:
            return total, targets, excess, maximum
        if mode == 3:
            return maximum, targets, excess, total
        weight = (1, 2, 4, 8, 12, 20)[mode - 4]
        return 3 * targets + weight * excess, targets, excess, total, maximum

    rankings = [sorted(records, key=lambda record, mode=mode: key_for(record, mode))
                for mode in range(10)]
    selected: list[CandidateRecord] = []
    selected_ids: set[int] = set()
    offset = 0
    while len(selected) < limit:
        progressed = False
        for ranking in rankings:
            if offset >= len(ranking):
                continue
            record = ranking[offset]
            marker = id(record)
            if marker not in selected_ids:
                selected.append(record)
                selected_ids.add(marker)
                progressed = True
                if len(selected) == limit:
                    break
        if not progressed and offset >= max(len(ranking) for ranking in rankings):
            break
        offset += 1
    return selected


def permute_mask(mask: int, coordinate_map: Sequence[int]) -> int:
    result = 0
    while mask:
        low = mask & -mask
        result |= 1 << coordinate_map[low.bit_length() - 1]
        mask ^= low
    return result


def canonical_templates(backend, width: int, weights: Iterable[int]):
    forms, costs = backend.all_forms(width)
    templates: dict[int, tuple[CoverOption, ...]] = {}
    for weight in sorted(set(weights)):
        target = (1 << weight) - 1
        reduced = backend.reduced_options(target, forms, costs)
        options = []
        for final_cost, choices in sorted(reduced.items()):
            for required, sources in choices.items():
                options.append(
                    CoverOption(final_cost // backend.SCALE, required, sources)
                )
        if not options:
            raise AssertionError(f"no canonical options for width={width} weight={weight}")
        templates[weight] = tuple(options)
        print(
            f"templates width={width} weight={weight} options={len(options)}",
            flush=True,
        )
    return templates


def target_options(
    target: int,
    width: int,
    templates: dict[int, tuple[CoverOption, ...]],
) -> tuple[CoverOption, ...]:
    support = tuple(bit for bit in range(width) if (target >> bit) & 1)
    outside = tuple(bit for bit in range(width) if not ((target >> bit) & 1))
    coordinate_map = support + outside
    result = []
    for option in templates[len(support)]:
        result.append(
            CoverOption(
                option.final_units,
                tuple(sorted(permute_mask(mask, coordinate_map) for mask in option.required)),
                tuple(permute_mask(mask, coordinate_map) for mask in option.sources),
            )
        )
    return tuple(result)


def primary_units(mask: int) -> int:
    weight = mask.bit_count()
    if weight == 2:
        return 1
    if weight == 3:
        return 4
    raise AssertionError(f"invalid first-level form weight {weight}")


def add_option(counts: Counter[int], option: CoverOption, direction: int) -> None:
    for form in option.required:
        counts[form] += direction
        if counts[form] == 0:
            del counts[form]


def marginal_units(counts: Counter[int], option: CoverOption) -> int:
    return option.final_units + sum(
        primary_units(form) for form in option.required if form not in counts
    )


def total_units(
    options: Sequence[Sequence[CoverOption]],
    choices: Sequence[int],
) -> tuple[int, Counter[int]]:
    counts: Counter[int] = Counter()
    final = 0
    for row_options, choice in zip(options, choices):
        option = row_options[choice]
        final += option.final_units
        counts.update(option.required)
    return final + sum(primary_units(form) for form in counts), counts


def initialize(
    options: Sequence[Sequence[CoverOption]],
    rng: random.Random,
    restart: int,
) -> tuple[list[int], Counter[int]]:
    choices = [-1] * len(options)
    counts: Counter[int] = Counter()
    order = list(range(len(options)))
    if restart:
        rng.shuffle(order)
    else:
        order.sort(key=lambda index: len(options[index]))
    pool_size = 1 if restart == 0 else 1 + restart % 8
    for index in order:
        scored = sorted(
            (
                marginal_units(counts, option),
                option.final_units + sum(primary_units(form) for form in option.required),
                rng.random(),
                option_index,
            )
            for option_index, option in enumerate(options[index])
        )
        pool = scored[: min(pool_size, len(scored))]
        choice = pool[rng.randrange(len(pool))][3]
        choices[index] = choice
        add_option(counts, options[index][choice], 1)
    return choices, counts


def coordinate_descent(
    options: Sequence[Sequence[CoverOption]],
    choices: list[int],
    counts: Counter[int],
    rng: random.Random,
    randomized: bool,
) -> int:
    moves = 0
    for _ in range(24):
        changed = 0
        order = list(range(len(options)))
        if randomized:
            rng.shuffle(order)
        for index in order:
            old_index = choices[index]
            add_option(counts, options[index][old_index], -1)
            best_index = min(
                range(len(options[index])),
                key=lambda option_index: (
                    marginal_units(counts, options[index][option_index]),
                    option_index,
                ),
            )
            choices[index] = best_index
            add_option(counts, options[index][best_index], 1)
            changed += best_index != old_index
        moves += changed
        if not changed:
            break
    return moves


def solve_cover(
    options: Sequence[Sequence[CoverOption]],
    targets: Sequence[int],
    width: int,
    restarts: int,
    partition_restarts: int,
    partition_pair_top_k: int,
    seed: int,
) -> CoverResult:
    rng = random.Random(seed)
    partition_options = [partition_proxy.make_options(target, width) for target in targets]
    partition_result = partition_proxy.solve_cover(
        partition_options,
        partition_restarts,
        seed ^ 0xC0DEC0DE,
        partition_pair_top_k,
    )
    seeded_choices = []
    for exact_options, coarse_options, coarse_choice in zip(
        options, partition_options, partition_result.choices
    ):
        coarse = coarse_options[coarse_choice]
        coarse_required = set(coarse.groups)
        seeded_choices.append(
            min(
                range(len(exact_options)),
                key=lambda index: (
                    exact_options[index].final_units
                    + sum(primary_units(form) for form in exact_options[index].required),
                    len(set(exact_options[index].required) - coarse_required),
                    index,
                )
                if (
                    exact_options[index].final_units <= coarse.final_units
                    and sum(
                        primary_units(form)
                        for form in exact_options[index].required
                        if form not in coarse_required
                    )
                    <= coarse.final_units - exact_options[index].final_units
                )
                else (10**9, 10**9, index),
            )
        )
    seeded_units, seeded_counts = total_units(options, seeded_choices)
    if seeded_units > partition_result.units:
        raise AssertionError(
            f"reduced cancellation seed {seeded_units} exceeds partition cover "
            f"{partition_result.units}"
        )
    seeded_moves = coordinate_descent(
        options, seeded_choices, seeded_counts, rng, False
    )
    seeded_units, rebuilt_counts = total_units(options, seeded_choices)
    if rebuilt_counts != seeded_counts:
        raise AssertionError("seeded cover usage counter drift")
    best: CoverResult | None = CoverResult(
        seeded_units, seeded_choices.copy(), seeded_counts.copy(), 0, seeded_moves
    )
    total_moves = 0
    for restart in range(restarts):
        choices, counts = initialize(options, rng, restart)
        moves = coordinate_descent(options, choices, counts, rng, bool(restart))
        total_moves += moves
        units, rebuilt_counts = total_units(options, choices)
        if rebuilt_counts != counts:
            raise AssertionError("cover usage counter drift")
        if best is None or units < best.units:
            best = CoverResult(units, choices.copy(), counts.copy(), restart + 1, total_moves)
    assert best is not None
    return best


def verify_cover(
    targets: Sequence[int],
    options: Sequence[Sequence[CoverOption]],
    result: CoverResult,
) -> None:
    rebuilt_units = sum(primary_units(form) for form in result.counts)
    for target, row_options, choice in zip(targets, options, result.choices):
        option = row_options[choice]
        if len(option.sources) not in (1, 2, 3):
            raise AssertionError("invalid final arity")
        rebuilt = 0
        for source in option.sources:
            rebuilt ^= source
            if source.bit_count() > 1 and source not in result.counts:
                raise AssertionError("final source is not implemented")
        if rebuilt != target:
            raise AssertionError(f"cover computes {rebuilt:x}, expected {target:x}")
        expected_final = {1: 0, 2: 1, 3: 4}[len(option.sources)]
        if option.final_units != expected_final:
            raise AssertionError("wrong final cost")
        rebuilt_units += option.final_units
    if rebuilt_units != result.units:
        raise AssertionError("cover cost mismatch")


def result_record(
    record: CandidateRecord,
    options: Sequence[Sequence[CoverOption]],
    result: CoverResult,
) -> dict[str, object]:
    width = record.state_bits
    hex_width = (width + 3) // 4
    fixed_gate = 198 + 5 * len(record.active_hidden)
    target_covers = []
    for target, row_options, choice in zip(record.targets, options, result.choices):
        option = row_options[choice]
        target_covers.append(
            {
                "target": f"{target:0{hex_width}x}",
                "mode": {1: "direct", 2: "xor2", 3: "xor3"}[len(option.sources)],
                "sources": [f"{source:0{hex_width}x}" for source in option.sources],
                "final_gate": 3 * option.final_units,
            }
        )
    return {
        "state_bits": width,
        "active_original_hidden_rows": list(record.active_hidden),
        "features": {
            "distinct_targets": record.features[0],
            "excess4": record.features[1],
            "total_weight": record.features[2],
            "maximum_weight": record.features[3],
        },
        "fixed_gate": fixed_gate,
        "cover": {
            "status": "verified-upper-bound",
            "logic_gate": 3 * result.units,
            "total_gate": fixed_gate + 3 * result.units,
            "delay": 9,
            "cycles": 66,
            "restarts_at_best": result.restarts,
            "coordinate_moves_through_best": result.coordinate_moves,
            "first_level": [
                {
                    "form": f"{form:0{hex_width}x}",
                    "mode": "xor2" if form.bit_count() == 2 else "xor3",
                    "inputs": [bit for bit in range(width) if (form >> bit) & 1],
                    "gate": 3 * primary_units(form),
                }
                for form in sorted(result.counts)
            ],
            "targets": target_covers,
        },
        "candidate": {
            "sources": [
                {"path": path, "lines": list(lines)} for path, lines in record.sources
            ],
            "reported": record.candidate.reported,
            "X_rows_hex": [f"{row:03x}" for row in record.candidate.x_rows],
            "D_rows_hex": [f"{row:011x}" for row in record.candidate.d_rows],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", type=Path, action="append", required=True)
    parser.add_argument("--active", type=int)
    parser.add_argument("--selection", choices=("last", "all"), default="all")
    parser.add_argument("--max-candidates", type=int, default=12)
    parser.add_argument("--restarts", type=int, default=12)
    parser.add_argument("--partition-restarts", type=int, default=96)
    parser.add_argument("--partition-pair-top-k", type=int, default=8)
    parser.add_argument("--seed", type=int, default=202608020501)
    parser.add_argument("--memory-mb", type=int, default=700)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.restarts <= 0 or args.partition_restarts <= 0:
        raise SystemExit("restart counts must be positive")

    started = time.perf_counter()
    records = load_records(args.log, args.active, args.selection)
    selected = diverse_selection(records, args.max_candidates)
    if not selected:
        raise SystemExit("no matching candidates")
    print(f"loaded semantic_candidates={len(records)} selected={len(selected)}", flush=True)

    backend, backend_path = load_backend()
    stop_watchdog, peak_working_set = backend.start_memory_watchdog(args.memory_mb)
    templates_by_width = {}
    for width in sorted({record.state_bits for record in selected}):
        weights = {
            target.bit_count()
            for record in selected if record.state_bits == width
            for target in record.targets
        }
        templates_by_width[width] = canonical_templates(backend, width, weights)

    results = []
    for index, record in enumerate(selected):
        row_options = [
            target_options(target, record.state_bits, templates_by_width[record.state_bits])
            for target in record.targets
        ]
        cover = solve_cover(
            row_options,
            record.targets,
            record.state_bits,
            args.restarts,
            args.partition_restarts,
            args.partition_pair_top_k,
            args.seed + index,
        )
        verify_cover(record.targets, row_options, cover)
        item = result_record(record, row_options, cover)
        results.append(item)
        print(
            f"candidate={index + 1}/{len(selected)} active={len(record.active_hidden)} "
            f"targets={len(record.targets)} logic={3 * cover.units} "
            f"total={item['cover']['total_gate']}",
            flush=True,
        )

    results.sort(key=lambda item: (item["cover"]["total_gate"], item["cover"]["logic_gate"]))
    peak_working_set[0] = max(
        peak_working_set[0], backend.working_set_bytes()
    )
    output = {
        "schema": 1,
        "scope": "cancellation-aware depth-two concrete-cover proxy",
        "status": "UPPER_BOUNDS",
        "warning": "heuristic covers are feasible upper bounds, not exact optima",
        "backend": str(backend_path),
        "source_logs": [str(path.resolve()) for path in args.log],
        "semantic_candidate_count": len(records),
        "evaluated_candidate_count": len(results),
        "restarts": args.restarts,
        "seed": args.seed,
        "elapsed_seconds": time.perf_counter() - started,
        "peak_working_set_mb": peak_working_set[0] / 1048576,
        "results": results,
    }
    encoded = (json.dumps(output, indent=2, sort_keys=True) + "\n").encode("ascii")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(encoded)
    stop_watchdog.set()
    print(
        json.dumps(
            {
                "best_total_gate": results[0]["cover"]["total_gate"],
                "best_logic_gate": results[0]["cover"]["logic_gate"],
                "sha256": sha256(encoded).hexdigest(),
            },
            indent=2,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
