"""Audit same-count noncanonical low-pair mediators for RNG basis candidates."""

from __future__ import annotations

import argparse
from functools import lru_cache
from itertools import product
import importlib.util
import json
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


def matrix(record: dict[str, object], key: str) -> tuple[int, ...]:
    values = record[key]
    if not isinstance(values, list) or len(values) != BITS:
        raise ValueError(f"{key} must contain 32 rows")
    return tuple(int(str(value), 16) for value in values)


def bits(mask: int) -> tuple[int, ...]:
    return tuple(bit for bit in range(BITS) if mask >> bit & 1)


@lru_cache(maxsize=131_072)
def hitting_number(family_key: tuple[int, ...]) -> int:
    family = list(dict.fromkeys(family_key))
    family = [
        candidate
        for candidate in family
        if not any(
            other != candidate and (other & candidate) == other for other in family
        )
    ]
    if not family:
        return 0

    @lru_cache(maxsize=None)
    def solve(remaining: tuple[int, ...]) -> int:
        if not remaining:
            return 0
        chosen = min(remaining, key=int.bit_count)
        best = BITS + 1
        for state in bits(chosen):
            reduced = tuple(mask for mask in remaining if not (mask >> state & 1))
            best = min(best, 1 + solve(reduced))
        return best

    return solve(tuple(sorted(family)))


def topology_or_lower_bound(
    T: tuple[int, ...],
    B: tuple[int, ...],
    mediated: dict[int, tuple[int, int]],
    mediated_units: dict[int, int],
) -> int:
    total = 0
    for seed in range(BITS):
        family = []
        for target, steady in zip(T, B):
            if target >> seed & 1:
                if steady in mediated:
                    left, right = mediated[steady]
                    family.append(left | right)
                elif steady in mediated_units:
                    family.append(mediated_units[steady])
                else:
                    family.append(steady)
        total += hitting_number(tuple(sorted(family)))
    return total


def optimize_labels(
    dual,
    T: tuple[int, ...],
    B: tuple[int, ...],
    selected_pairs: frozenset[int],
    decompositions: dict[int, tuple[int, ...]],
    mediated: dict[int, tuple[int, int]],
    mediated_units: dict[int, int],
    *,
    component_limit: int,
    global_beam: int,
):
    adjacency: dict[int, list[tuple[int, int]]] = {
        pair: [] for pair in selected_pairs
    }
    exact_labels: dict[int, int] = {}
    residuals: list[tuple[int, int, int]] = []
    fixed_mappings: set[tuple[int, int]] = set()

    for target, steady in zip(T, B):
        if steady in mediated:
            left, right = mediated[steady]
            adjacency[left].append((right, target))
            adjacency[right].append((left, target))
            continue
        if steady in mediated_units:
            pair = mediated_units[steady]
            direct = steady ^ pair
            if direct.bit_count() != 1:
                return None
            residuals.append((pair, target, bits(direct)[0]))
            continue
        weight = steady.bit_count()
        if weight == 1:
            if target.bit_count() != 1:
                return None
            fixed_mappings.add((bits(target)[0], bits(steady)[0]))
        elif weight == 2:
            if steady not in selected_pairs or target.bit_count() > 2:
                return None
            previous = exact_labels.setdefault(steady, target)
            if previous != target:
                return None
        elif weight == 3:
            pair = decompositions[steady][0]
            direct = steady ^ pair
            if direct.bit_count() != 1:
                return None
            residuals.append((pair, target, bits(direct)[0]))
        elif weight == 4:
            left, right = decompositions[steady]
            adjacency[left].append((right, target))
            adjacency[right].append((left, target))
        else:
            return None

    active = set(exact_labels) | {node for node, _, _ in residuals}
    active |= {node for node, edges in adjacency.items() if edges}
    components = []
    visited: set[int] = set()
    for root in sorted(active):
        if root in visited:
            continue
        offsets = {root: 0}
        stack = [root]
        consistent = True
        while stack and consistent:
            node = stack.pop()
            visited.add(node)
            for neighbor, edge_label in adjacency[node]:
                expected = offsets[node] ^ edge_label
                if neighbor in offsets:
                    consistent &= offsets[neighbor] == expected
                else:
                    offsets[neighbor] = expected
                    stack.append(neighbor)
        if not consistent:
            return None
        local_exact = {
            node: label for node, label in exact_labels.items() if node in offsets
        }
        local_residuals = tuple(item for item in residuals if item[0] in offsets)
        options = dual.component_options(
            offsets, local_exact, local_residuals, component_limit
        )
        if not options:
            return None
        components.append((offsets, options))

    components.sort(key=lambda item: (len(item[1]), len(item[0])))
    states: dict[frozenset[tuple[int, int]], tuple[object, ...]] = {
        frozenset(fixed_mappings): ()
    }
    for _, options in components:
        expanded: dict[frozenset[tuple[int, int]], tuple[object, ...]] = {}
        for mappings, choices in states.items():
            for option in options:
                merged = mappings | option.mappings
                expanded.setdefault(merged, choices + (option,))
        ordered = sorted(
            expanded.items(), key=lambda item: (len(item[0]), tuple(sorted(item[0])))
        )
        states = dict(ordered[:global_beam])
        if not states:
            return None

    mappings, choices = min(
        states.items(), key=lambda item: (len(item[0]), tuple(sorted(item[0])))
    )
    if len({seed for seed, _ in mappings}) != BITS:
        return None
    pair_labels = {pair: 0 for pair in selected_pairs}
    orientations = {pair: (None, None) for pair in selected_pairs}
    for option in choices:
        pair_labels.update(option.labels)
        orientations.update(
            (pair, (left, right)) for pair, left, right in option.orientations
        )
    return dual.DualResult(
        len(mappings), mappings, pair_labels, orientations, decompositions
    )


def verify_candidate(
    init,
    T: tuple[int, ...],
    B: tuple[int, ...],
    C: tuple[int, ...],
    selected_pairs: frozenset[int],
    decompositions: dict[int, tuple[int, ...]],
    mediated: dict[int, tuple[int, int]],
    mediated_units: dict[int, int],
    result,
) -> None:
    if init.compose(C, T) != init.A or init.compose(T, C) != B:
        raise AssertionError("matrix identity failed")
    for steady in frozenset((*B, *C)):
        weight = steady.bit_count()
        if steady in mediated:
            left, right = mediated[steady]
            if left not in selected_pairs or right not in selected_pairs or left ^ right != steady:
                raise AssertionError("invalid mediated steady target")
        elif steady in mediated_units:
            pair = mediated_units[steady]
            if pair not in selected_pairs or (pair ^ steady).bit_count() != 1:
                raise AssertionError("invalid mediated unit target")
        elif weight == 1:
            continue
        elif weight == 2:
            if steady not in selected_pairs:
                raise AssertionError("direct pair target is absent")
        else:
            option = decompositions[steady]
            if not set(option) <= selected_pairs:
                raise AssertionError("heavy decomposition is absent")
            actual = option[0] ^ (steady ^ option[0]) if len(option) == 1 else option[0] ^ option[1]
            if actual != steady:
                raise AssertionError("heavy decomposition is invalid")

    for pair, label in result.pair_labels.items():
        left_seed, right_seed = result.orientations[pair]
        left_state, right_state = bits(pair)
        actual = (0 if left_seed is None else 1 << left_seed) ^ (
            0 if right_seed is None else 1 << right_seed
        )
        if actual != label:
            raise AssertionError("pair tick-zero label is unrealized")
        if left_seed is not None and (left_seed, left_state) not in result.mappings:
            raise AssertionError("left mapping is absent")
        if right_seed is not None and (right_seed, right_state) not in result.mappings:
            raise AssertionError("right mapping is absent")

    for target, steady in zip(T, B):
        if steady in mediated:
            left, right = mediated[steady]
            actual = result.pair_labels[left] ^ result.pair_labels[right]
        elif steady in mediated_units:
            pair = mediated_units[steady]
            residual = target ^ result.pair_labels[pair]
            if residual.bit_count() > 1:
                raise AssertionError("mediated unit residual label is not a unit")
            state = bits(pair ^ steady)[0]
            if residual and (bits(residual)[0], state) not in result.mappings:
                raise AssertionError("mediated unit raw mapping is absent")
            actual = result.pair_labels[pair] ^ residual
        elif steady.bit_count() == 1:
            actual = target
            required = (bits(target)[0], bits(steady)[0])
            if required not in result.mappings:
                raise AssertionError("direct mapping is absent")
        elif steady.bit_count() == 2:
            actual = result.pair_labels[steady]
        elif steady.bit_count() == 3:
            pair = decompositions[steady][0]
            residual = target ^ result.pair_labels[pair]
            if residual.bit_count() > 1:
                raise AssertionError("raw residual is not a unit")
            if residual:
                state = bits(steady ^ pair)[0]
                if (bits(residual)[0], state) not in result.mappings:
                    raise AssertionError("raw residual mapping is absent")
            actual = result.pair_labels[pair] ^ residual
        else:
            left, right = decompositions[steady]
            actual = result.pair_labels[left] ^ result.pair_labels[right]
        if actual != target:
            raise AssertionError("tick-zero feedback label mismatch")

    seeds = [0, 1, 2, 0x12345678, 0xFFFFFFFF, 0x80000000]
    generator = random.Random(20260802)
    seeds.extend(generator.getrandbits(32) for _ in range(63))
    for seed in seeds:
        natural = seed
        encoded = init.apply_matrix(T, seed)
        for _ in range(65):
            natural = init.xorshift32(natural)
            if init.apply_matrix(C, encoded) != natural:
                raise AssertionError("visible sequence mismatch")
            encoded = init.apply_matrix(B, encoded)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--bounds", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--topology-limit", type=int, default=20_000)
    parser.add_argument("--component-limit", type=int, default=256)
    parser.add_argument("--global-beam", type=int, default=2048)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    init = load_module(
        "rng_or_mediated_init", root / ".research/rng_init_reuse/verify_init_reuse.py"
    )
    cover_module = load_module(
        "rng_or_mediated_cover", root / ".research/rng_joint_search_resume/search.py"
    )
    dual = load_module(
        "rng_or_mediated_dual", root / ".research/rng_cost387/search_basis_dualmode.py"
    )

    bounds = []
    with args.bounds.open(encoding="utf-8-sig") as stream:
        header = stream.readline().strip().split(",")
        for line in stream:
            values = line.strip().split(",")
            bounds.append(dict(zip(header, values)))

    records = [json.loads(line) for line in args.source.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    if len(records) != len(bounds):
        raise ValueError("candidate JSONL and bound CSV counts differ")

    started = time.perf_counter()
    topology_count = 0
    lower_bound_passes = 0
    label_feasible = 0
    truncated_records = 0
    best = None
    frontier = []

    for candidate_index, (record, bound) in enumerate(zip(records, bounds)):
        T, B, C = (matrix(record, key) for key in ("T", "B", "C"))
        if init.compose(C, T) != init.A or init.compose(T, C) != B:
            raise AssertionError("input matrix identity failed")
        cover = cover_module.depth_two_cost((*B, *C))
        selected0 = frozenset(cover.selected_pair_gates)
        heavy = tuple(
            row for row in dict.fromkeys((*B, *C)) if row.bit_count() in (3, 4)
        )
        heavy_options = {
            row: tuple(
                option for option in dual.pair_partitions(row) if set(option) <= selected0
            )
            for row in heavy
        }
        pair_targets = frozenset(
            row for row in (*B, *C) if row.bit_count() == 2
        )
        b_pair_targets = tuple(row for row in B if row.bit_count() == 2)
        b_unit_targets = tuple(row for row in B if row.bit_count() == 1)
        local_seen = set()
        local_topologies = 0
        local_passes = 0
        local_best = None

        for heavy_choices in product(*(heavy_options[row] for row in heavy)):
            heavy_decompositions = dict(zip(heavy, heavy_choices))
            heavy_used = frozenset(pair for option in heavy_choices for pair in option)
            mediation_options = {}
            for steady in b_pair_targets:
                left, right = bits(steady)
                alternatives = []
                for common in range(BITS):
                    if common in (left, right):
                        continue
                    first = (1 << left) | (1 << common)
                    second = (1 << right) | (1 << common)
                    if first in selected0 and second in selected0:
                        alternatives.append(tuple(sorted((first, second))))
                mediation_options[steady] = (None, *dict.fromkeys(alternatives))
            unit_mediation_options = {
                steady: (
                    None,
                    *(
                        pair
                        for pair in sorted(selected0)
                        if (pair & steady) and (pair ^ steady).bit_count() == 1
                    ),
                )
                for steady in b_unit_targets
            }

            for choices in product(*(mediation_options[row] for row in b_pair_targets)):
                mediated = {
                    row: choice
                    for row, choice in zip(b_pair_targets, choices)
                    if choice is not None
                }
                for unit_choices in product(
                    *(unit_mediation_options[row] for row in b_unit_targets)
                ):
                    mediated_units = {
                        row: choice
                        for row, choice in zip(b_unit_targets, unit_choices)
                        if choice is not None
                    }
                    required_pairs = set(heavy_used)
                    required_pairs.update(pair_targets - mediated.keys())
                    for option in mediated.values():
                        required_pairs.update(option)
                    required_pairs.update(mediated_units.values())
                    xor_count = (
                        len(required_pairs)
                        + len(heavy)
                        + len(mediated)
                        + len(mediated_units)
                    )
                    if xor_count > 63:
                        continue
                    topology_key = (
                        frozenset(required_pairs),
                        tuple(sorted(heavy_decompositions.items())),
                        tuple(sorted(mediated.items())),
                        tuple(sorted(mediated_units.items())),
                    )
                    if topology_key in local_seen:
                        continue
                    local_seen.add(topology_key)
                    topology_count += 1
                    local_topologies += 1
                    if local_topologies > args.topology_limit:
                        truncated_records += 1
                        break

                    or_target = TARGET - 3 * xor_count
                    lower = topology_or_lower_bound(
                        T, B, mediated, mediated_units
                    )
                    if lower > or_target:
                        continue
                    lower_bound_passes += 1
                    local_passes += 1
                    decompositions = dict(heavy_decompositions)
                    decompositions.update(mediated)
                    result = optimize_labels(
                        dual,
                        T,
                        B,
                        frozenset(required_pairs),
                        decompositions,
                        mediated,
                        mediated_units,
                        component_limit=args.component_limit,
                        global_beam=args.global_beam,
                    )
                    if result is None:
                        continue
                    verify_candidate(
                        init,
                        T,
                        B,
                        C,
                        frozenset(required_pairs),
                        decompositions,
                        mediated,
                        mediated_units,
                        result,
                    )
                    label_feasible += 1
                    metrics = {
                        "xor": xor_count,
                        "or": result.or_count,
                        "three_xor_plus_or": 3 * xor_count + result.or_count,
                        "gate": 166 + 3 * xor_count + result.or_count,
                        "delay": 10,
                        "cycles": 66,
                    }
                    certificate = {
                        "candidate_index": candidate_index,
                        "original_source_line": int(bound["line"]),
                        "T": [f"{row:08x}" for row in T],
                        "B": [f"{row:08x}" for row in B],
                        "C": [f"{row:08x}" for row in C],
                        "selected_pair_gates": [
                            f"{pair:08x}" for pair in sorted(required_pairs)
                        ],
                        "decompositions": {
                            f"{row:08x}": [f"{pair:08x}" for pair in option]
                            for row, option in sorted(decompositions.items())
                        },
                        "mediated_pair_targets": [
                            f"{row:08x}" for row in sorted(mediated)
                        ],
                        "mediated_unit_targets": {
                            f"{row:08x}": f"{pair:08x}"
                            for row, pair in sorted(mediated_units.items())
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
                    if local_best is None or metrics["three_xor_plus_or"] < local_best["metrics"]["three_xor_plus_or"]:
                        local_best = certificate
                    if best is None or metrics["three_xor_plus_or"] < best["metrics"]["three_xor_plus_or"]:
                        best = certificate
                        print(
                            f"best budget={metrics['three_xor_plus_or']} xor={xor_count} "
                            f"or={result.or_count} source={bound['line']}",
                            flush=True,
                        )
                    if metrics["three_xor_plus_or"] <= TARGET:
                        break
                if local_topologies > args.topology_limit or (
                    best is not None and best["metrics"]["three_xor_plus_or"] <= TARGET
                ):
                    break
            if local_topologies > args.topology_limit or (
                best is not None and best["metrics"]["three_xor_plus_or"] <= TARGET
            ):
                break

        frontier.append(
            {
                "candidate_index": candidate_index,
                "original_source_line": int(bound["line"]),
                "greedy_xor": cover.greedy_upper_bound,
                "topology_count": local_topologies,
                "lower_bound_pass_count": local_passes,
                "best_metrics": None if local_best is None else local_best["metrics"],
            }
        )
        if best is not None and best["metrics"]["three_xor_plus_or"] <= TARGET:
            break

    document = {
        "status": (
            "target_candidate"
            if best is not None and best["metrics"]["three_xor_plus_or"] <= TARGET
            else "frontier_only"
        ),
        "candidate_count": len(records),
        "topology_count": topology_count,
        "lower_bound_pass_count": lower_bound_passes,
        "label_feasible_count": label_feasible,
        "truncated_record_count": truncated_records,
        "limits": {
            "topology_limit": args.topology_limit,
            "component_limit": args.component_limit,
            "global_beam": args.global_beam,
        },
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
