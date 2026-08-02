"""Low-memory neighborhood search for a cheaper dual-mode xorshift32 basis.

The search walks elementary row shears around the verified two-shear basis.
Only states for which every T/B/C row has weight at most four are retained.
For each promising greedy depth-two B/C pair cover, a component solver assigns
tick-zero labels to the physical pair nodes and minimizes the union of
``(seed_bit, state_bit)`` OR leaves with a bounded beam DP.

This is a candidate generator, not a global lower-bound proof.  Every emitted
certificate contains an explicit pair cover, decomposition, pair label, pin
orientation and OR set, then replays the GF(2) identities and 65 output ticks.
It never imports save-writing code or touches a game save.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import importlib.util
from itertools import combinations, islice, product
import json
from pathlib import Path
import random
import sys
import time
from typing import Iterable, Sequence


BITS = 32
IDENTITY = tuple(1 << bit for bit in range(BITS))
LABEL_UNIVERSE = (
    (0,)
    + tuple(1 << seed for seed in range(BITS))
    + tuple((1 << left) | (1 << right) for left, right in combinations(range(BITS), 2))
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def bits(value: int) -> tuple[int, ...]:
    return tuple(index for index in range(BITS) if value >> index & 1)


def pair_partitions(row: int) -> tuple[tuple[int, ...], ...]:
    support = tuple(1 << bit for bit in bits(row))
    if len(support) == 3:
        return tuple((row ^ unit,) for unit in support)
    if len(support) == 4:
        a, b, c, d = support
        return (
            tuple(sorted((a | b, c | d))),
            tuple(sorted((a | c, b | d))),
            tuple(sorted((a | d, b | c))),
        )
    raise ValueError(f"row {row:08x} has weight {len(support)}")


Atom = tuple[int, int]


@dataclass(frozen=True)
class LocalOption:
    mappings: frozenset[Atom]
    labels: tuple[tuple[int, int], ...]
    orientations: tuple[tuple[int, int | None, int | None], ...]


@dataclass(frozen=True)
class DualResult:
    or_count: int
    mappings: frozenset[Atom]
    pair_labels: dict[int, int]
    orientations: dict[int, tuple[int | None, int | None]]
    decompositions: dict[int, tuple[int, ...]]


@dataclass
class CoverEnumerator:
    options: dict[int, tuple[frozenset[int], ...]]
    budget: int
    state_limit: int
    solution_limit: int
    visited: set[frozenset[int]]
    solutions: set[frozenset[int]]
    truncated: bool = False

    def run(self) -> None:
        self._visit(frozenset())

    def _visit(self, selected: frozenset[int]) -> None:
        if self.truncated or selected in self.visited:
            return
        if len(self.visited) >= self.state_limit or len(self.solutions) >= self.solution_limit:
            self.truncated = True
            return
        self.visited.add(selected)
        uncovered = [
            options
            for options in self.options.values()
            if not any(option <= selected for option in options)
        ]
        if not uncovered:
            self.solutions.add(selected)
            return
        if len(selected) >= self.budget:
            return
        row_options = min(
            uncovered,
            key=lambda options: (
                len({option - selected for option in options}),
                -min(len(option - selected) for option in options),
            ),
        )
        additions = sorted(
            {option - selected for option in row_options},
            key=lambda option: (len(option), tuple(sorted(option))),
        )
        for addition in additions:
            extended = selected | addition
            if len(extended) <= self.budget:
                self._visit(extended)


def label_realizations(
    pair: int, label: int
) -> tuple[tuple[frozenset[Atom], tuple[int | None, int | None]], ...]:
    states = bits(pair)
    seeds = bits(label)
    if len(states) != 2 or len(seeds) > 2:
        return ()
    left_state, right_state = states
    if not seeds:
        return ((frozenset(), (None, None)),)
    if len(seeds) == 1:
        seed = seeds[0]
        return (
            (frozenset(((seed, left_state),)), (seed, None)),
            (frozenset(((seed, right_state),)), (None, seed)),
        )
    left_seed, right_seed = seeds
    return (
        (
            frozenset(((left_seed, left_state), (right_seed, right_state))),
            (left_seed, right_seed),
        ),
        (
            frozenset(((right_seed, left_state), (left_seed, right_state))),
            (right_seed, left_seed),
        ),
    )


def pareto_options(options: Iterable[LocalOption], limit: int) -> tuple[LocalOption, ...]:
    by_mapping: dict[frozenset[Atom], LocalOption] = {}
    for option in options:
        by_mapping.setdefault(option.mappings, option)
    result: list[LocalOption] = []
    for option in sorted(
        by_mapping.values(), key=lambda item: (len(item.mappings), tuple(sorted(item.mappings)))
    ):
        if any(existing.mappings <= option.mappings for existing in result):
            continue
        result.append(option)
        if len(result) >= limit:
            break
    return tuple(result)


def component_options(
    offsets: dict[int, int],
    exact_labels: dict[int, int],
    residuals: Sequence[tuple[int, int, int]],
    option_limit: int,
) -> tuple[LocalOption, ...]:
    all_options: list[LocalOption] = []
    for root_label in LABEL_UNIVERSE:
        labels = {node: root_label ^ offset for node, offset in offsets.items()}
        if any(label.bit_count() > 2 for label in labels.values()):
            continue
        if any(labels.get(node) != expected for node, expected in exact_labels.items()):
            continue

        raw_mappings: set[Atom] = set()
        feasible = True
        for node, target, state in residuals:
            if node not in labels:
                continue
            residual = target ^ labels[node]
            if residual.bit_count() > 1:
                feasible = False
                break
            if residual:
                raw_mappings.add((bits(residual)[0], state))
        if not feasible:
            continue

        partial = (
            LocalOption(
                frozenset(raw_mappings),
                tuple(sorted(labels.items())),
                (),
            ),
        )
        for node in sorted(labels):
            expanded: list[LocalOption] = []
            for current in partial:
                for mappings, orientation in label_realizations(node, labels[node]):
                    expanded.append(
                        LocalOption(
                            current.mappings | mappings,
                            current.labels,
                            current.orientations + ((node, orientation[0], orientation[1]),),
                        )
                    )
            partial = pareto_options(expanded, option_limit)
        all_options.extend(partial)
    return pareto_options(all_options, option_limit)


def decomposition_variants(
    selected_pairs: frozenset[int],
    finals: frozenset[int],
    b_rows: Sequence[int],
    sample_limit: int,
    rng: random.Random,
) -> tuple[dict[int, tuple[int, ...]], ...]:
    covered = {
        row: tuple(option for option in pair_partitions(row) if set(option) <= selected_pairs)
        for row in finals
    }
    if any(not options for options in covered.values()):
        return ()

    base = {row: options[0] for row, options in covered.items()}
    active_rows = tuple(
        row for row in dict.fromkeys(b_rows) if row in covered and len(covered[row]) > 1
    )
    if not active_rows:
        return (base,)

    counts = [len(covered[row]) for row in active_rows]
    total = 1
    for count in counts:
        total *= count

    variants: list[dict[int, tuple[int, ...]]] = []
    if total <= sample_limit:
        choices: Iterable[tuple[int, ...]] = product(*(range(count) for count in counts))
    else:
        deterministic = list(
            islice(product(*(range(count) for count in counts)), sample_limit // 2)
        )
        random_choices = {
            tuple(rng.randrange(count) for count in counts)
            for _ in range(sample_limit * 2)
        }
        choices = (*deterministic, *sorted(random_choices))

    seen: set[tuple[int, ...]] = set()
    for indexes in choices:
        if indexes in seen:
            continue
        seen.add(indexes)
        candidate = dict(base)
        for row, index in zip(active_rows, indexes):
            candidate[row] = covered[row][index]
        variants.append(candidate)
        if len(variants) >= sample_limit:
            break
    return tuple(variants)


def enumerate_pair_covers(
    rows: Sequence[int],
    pair_budget: int,
    *,
    state_limit: int,
    solution_limit: int,
) -> tuple[tuple[frozenset[int], ...], int, bool]:
    targets = frozenset(rows)
    required = frozenset(row for row in targets if row.bit_count() == 2)
    finals = frozenset(row for row in targets if row.bit_count() in (3, 4))
    extra_budget = pair_budget - len(required)
    if extra_budget < 0:
        return (), 0, False
    options = {
        row: tuple(frozenset(option) - required for option in pair_partitions(row))
        for row in finals
    }
    enumerator = CoverEnumerator(
        options,
        extra_budget,
        state_limit,
        solution_limit,
        set(),
        set(),
    )
    enumerator.run()
    covers = tuple(
        sorted(
            (required | extras for extras in enumerator.solutions),
            key=lambda cover: (len(cover), tuple(sorted(cover))),
        )
    )
    return covers, len(enumerator.visited), enumerator.truncated


def optimize_labels(
    T: Sequence[int],
    B: Sequence[int],
    selected_pairs: frozenset[int],
    decompositions: dict[int, tuple[int, ...]],
    *,
    component_limit: int,
    global_beam: int,
) -> DualResult | None:
    adjacency: dict[int, list[tuple[int, int]]] = {pair: [] for pair in selected_pairs}
    exact_labels: dict[int, int] = {}
    residuals: list[tuple[int, int, int]] = []
    fixed_mappings: set[Atom] = set()

    for target, steady in zip(T, B):
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
    components: list[tuple[dict[int, int], tuple[LocalOption, ...]]] = []
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
        local_exact = {node: label for node, label in exact_labels.items() if node in offsets}
        local_residuals = tuple(item for item in residuals if item[0] in offsets)
        options = component_options(
            offsets, local_exact, local_residuals, component_limit
        )
        if not options:
            return None
        components.append((offsets, options))

    # Components with fewer options first tighten the beam early.
    components.sort(key=lambda item: (len(item[1]), len(item[0])))
    states: dict[frozenset[Atom], tuple[LocalOption, ...]] = {
        frozenset(fixed_mappings): ()
    }
    for _, options in components:
        expanded: dict[frozenset[Atom], tuple[LocalOption, ...]] = {}
        for mappings, choices in states.items():
            for option in options:
                merged = mappings | option.mappings
                expanded.setdefault(merged, choices + (option,))
        ordered = sorted(expanded.items(), key=lambda item: (len(item[0]), tuple(sorted(item[0]))))
        states = dict(ordered[:global_beam])

    mappings, choices = min(states.items(), key=lambda item: (len(item[0]), tuple(sorted(item[0]))))
    pair_labels = {pair: 0 for pair in selected_pairs}
    orientations = {pair: (None, None) for pair in selected_pairs}
    for option in choices:
        pair_labels.update(option.labels)
        orientations.update(
            (pair, (left, right)) for pair, left, right in option.orientations
        )
    if len({seed for seed, _ in mappings}) != BITS:
        return None
    return DualResult(
        len(mappings), mappings, pair_labels, orientations, decompositions
    )


def verify_candidate(
    init_module,
    T: Sequence[int],
    B: Sequence[int],
    C: Sequence[int],
    selected_pairs: frozenset[int],
    result: DualResult,
) -> None:
    if init_module.compose(C, T) != init_module.A:
        raise AssertionError("C*T != A")
    if init_module.compose(T, C) != tuple(B):
        raise AssertionError("T*C != B")

    for row in frozenset((*B, *C)):
        if row.bit_count() == 1:
            continue
        if row.bit_count() == 2:
            if row not in selected_pairs:
                raise AssertionError("pair target is absent")
            continue
        option = result.decompositions[row]
        if not set(option) <= selected_pairs:
            raise AssertionError("final decomposition is absent")
        if row != (option[0] ^ (row ^ option[0]) if len(option) == 1 else option[0] ^ option[1]):
            raise AssertionError("invalid decomposition")

    for pair, label in result.pair_labels.items():
        left_seed, right_seed = result.orientations[pair]
        left_state, right_state = bits(pair)
        actual = (0 if left_seed is None else 1 << left_seed) ^ (
            0 if right_seed is None else 1 << right_seed
        )
        if actual != label:
            raise AssertionError("pair pin orientation has incorrect label")
        if left_seed is not None and (left_seed, left_state) not in result.mappings:
            raise AssertionError("left pin mode mapping is absent")
        if right_seed is not None and (right_seed, right_state) not in result.mappings:
            raise AssertionError("right pin mode mapping is absent")

    for target, steady in zip(T, B):
        if steady.bit_count() == 1:
            actual = target
            required = (bits(target)[0], bits(steady)[0])
            if required not in result.mappings:
                raise AssertionError("direct feedback mode mapping is absent")
        elif steady.bit_count() == 2:
            actual = result.pair_labels[steady]
        elif steady.bit_count() == 3:
            pair = result.decompositions[steady][0]
            residual = target ^ result.pair_labels[pair]
            if residual.bit_count() > 1:
                raise AssertionError("raw residual is not a unit")
            if residual:
                state = bits(steady ^ pair)[0]
                if (bits(residual)[0], state) not in result.mappings:
                    raise AssertionError("raw residual mode mapping is absent")
            actual = result.pair_labels[pair] ^ residual
        else:
            left, right = result.decompositions[steady]
            actual = result.pair_labels[left] ^ result.pair_labels[right]
        if actual != target:
            raise AssertionError("tick-zero feedback label mismatch")

    for seed in (0, 1, 2, 0x12345678, 0xFFFFFFFF, 0x80000000):
        natural = seed
        encoded = init_module.apply_matrix(T, seed)
        for _ in range(65):
            natural = init_module.xorshift32(natural)
            if init_module.apply_matrix(C, encoded) != natural:
                raise AssertionError("visible sequence mismatch")
            encoded = init_module.apply_matrix(B, encoded)


def matrix_hex(rows: Sequence[int]) -> list[str]:
    return [f"{row:08x}" for row in rows]


def search(args) -> dict[str, object]:
    root = Path(__file__).resolve().parents[2]
    init_module = load_module(
        "rng_cost387_init", root / ".research/rng_init_reuse/verify_init_reuse.py"
    )
    search_module = load_module(
        "rng_cost387_basis", root / ".research/rng_joint_search_resume/search.py"
    )

    start = (tuple(init_module.T), tuple(init_module.B), tuple(init_module.C))
    seen: dict[tuple[int, ...], tuple[tuple[int, ...], tuple[int, ...], tuple[tuple[int, int], ...]]] = {
        start[0]: (start[1], start[2], ())
    }
    frontier = [start[0]]
    best: tuple[int, int, int, tuple[int, ...], tuple[int, ...], tuple[int, ...], tuple[tuple[int, int], ...], frozenset[int], DualResult] | None = None
    evaluated = 0
    dual_basis_keys: set[tuple[int, ...]] = set()
    within_budget_keys: set[tuple[int, ...]] = set()
    dual_histogram: dict[int, int] = {}
    enumerated_cover_states = 0
    enumerated_cover_count = 0
    truncated_cover_searches = 0
    feasible_by_depth = [1]
    rng = random.Random(args.seed)
    started = time.perf_counter()

    for depth in range(args.radius + 1):
        for T_key in frontier:
            B, C, operations = seen[T_key]
            cover = search_module.depth_two_cost((*B, *C))
            if not cover.feasible or cover.greedy_upper_bound is None:
                continue
            xor_count = cover.greedy_upper_bound
            if xor_count > args.max_xor or 3 * xor_count + BITS > 221:
                continue
            finals = frozenset(row for row in (*B, *C) if row.bit_count() in (3, 4))
            greedy_pairs = frozenset(cover.selected_pair_gates)
            if xor_count != len(greedy_pairs) + len(finals):
                raise AssertionError("greedy pair accounting changed")
            covers = (greedy_pairs,)
            if xor_count <= args.enumerate_cover_xor:
                covers, cover_states, truncated = enumerate_pair_covers(
                    (*B, *C),
                    args.enumerate_cover_xor - len(finals),
                    state_limit=args.cover_state_limit,
                    solution_limit=args.cover_solution_limit,
                )
                enumerated_cover_states += cover_states
                enumerated_cover_count += len(covers)
                truncated_cover_searches += int(truncated)
                if not covers:
                    continue
            for selected_pairs in dict.fromkeys(covers):
                selected_xor = len(selected_pairs) + len(finals)
                if selected_xor > args.max_xor:
                    continue
                variants = decomposition_variants(
                    selected_pairs, finals, B, args.decomposition_samples, rng
                )
                for decompositions in variants:
                    evaluated += 1
                    dual = optimize_labels(
                        T_key,
                        B,
                        selected_pairs,
                        decompositions,
                        component_limit=args.component_limit,
                        global_beam=args.global_beam,
                    )
                    if dual is None:
                        continue
                    dual_basis_keys.add(T_key)
                    dual_histogram[selected_xor] = dual_histogram.get(selected_xor, 0) + 1
                    gate = 166 + 3 * selected_xor + dual.or_count
                    if gate <= 387:
                        within_budget_keys.add(T_key)
                    candidate = (
                        gate,
                        selected_xor,
                        dual.or_count,
                        T_key,
                        B,
                        C,
                        operations,
                        selected_pairs,
                        dual,
                    )
                    if best is None or candidate[:3] < best[:3]:
                        verify_candidate(init_module, T_key, B, C, selected_pairs, dual)
                        best = candidate
                        print(
                            f"best gate={gate} xor={selected_xor} or={dual.or_count} "
                            f"depth={depth} ops={len(operations)}",
                            flush=True,
                        )

        if depth == args.radius:
            break
        next_frontier: list[tuple[int, ...]] = []
        for T_key in frontier:
            B0, C0, operations = seen[T_key]
            for dst in range(BITS):
                for src in range(BITS):
                    if dst == src:
                        continue
                    T, B, C = list(T_key), list(B0), list(C0)
                    search_module.mutate(T, B, C, dst, src)
                    if max(row.bit_count() for row in (*T, *B, *C)) > 4:
                        continue
                    key = tuple(T)
                    if key in seen:
                        continue
                    seen[key] = (tuple(B), tuple(C), operations + ((dst, src),))
                    next_frontier.append(key)
        frontier = next_frontier
        feasible_by_depth.append(len(frontier))
        print(
            f"basis depth={depth + 1} new={len(frontier)} total={len(seen)}",
            flush=True,
        )

    elapsed = time.perf_counter() - started
    document: dict[str, object] = {
        "scope": "row-shear neighborhood of fixed two-shear T; greedy canonical depth-2 B/C cover",
        "radius": args.radius,
        "max_xor": args.max_xor,
        "feasible_basis_counts_by_depth": feasible_by_depth,
        "basis_count": len(seen),
        "decomposition_variants_evaluated": evaluated,
        "dual_feasible_basis_count": len(dual_basis_keys),
        "within_387_basis_count": len(within_budget_keys),
        "dual_feasible_variants_by_xor": {
            str(xor_count): count for xor_count, count in sorted(dual_histogram.items())
        },
        "enumerated_pair_cover_states": enumerated_cover_states,
        "enumerated_pair_cover_count": enumerated_cover_count,
        "truncated_pair_cover_searches": truncated_cover_searches,
        "component_option_limit": args.component_limit,
        "global_beam": args.global_beam,
        "elapsed_seconds": round(elapsed, 6),
        "memory_model": "deduplicated 32-row integer matrices plus bounded mapping beams",
    }
    if best is None:
        document["status"] = "no_dual_candidate"
        return document

    gate, xor_count, or_count, T, B, C, operations, selected_pairs, dual = best
    document["status"] = "candidate"
    document["candidate"] = {
        "T": matrix_hex(T),
        "B": matrix_hex(B),
        "C": matrix_hex(C),
        "basis_row_shears": [list(operation) for operation in operations],
        "selected_pair_gates": [f"{pair:08x}" for pair in sorted(selected_pairs)],
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
            "or": or_count,
            "gate": gate,
            "delay": 9,
            "cycles": 66,
            "energy": gate * 9 * 66,
            "budget_3xor_plus_or": 3 * xor_count + or_count,
            "within_387": gate <= 387,
        },
    }
    return document


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--radius", type=int, default=4)
    parser.add_argument("--max-xor", type=int, default=60)
    parser.add_argument("--component-limit", type=int, default=512)
    parser.add_argument("--global-beam", type=int, default=2048)
    parser.add_argument("--decomposition-samples", type=int, default=256)
    parser.add_argument("--enumerate-cover-xor", type=int, default=-1)
    parser.add_argument("--cover-state-limit", type=int, default=250_000)
    parser.add_argument("--cover-solution-limit", type=int, default=10_000)
    parser.add_argument("--seed", type=lambda value: int(value, 0), default=0x387)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    document = search(args)
    encoded = json.dumps(document, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
