"""Exhaust the fixed-two-shear 61-XOR pair covers and tick-zero OR reuse.

This is a research-only, standard-library verifier. It neither imports save
generation code nor touches the game process.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from itertools import combinations
from math import prod
from pathlib import Path
from typing import Iterable, Sequence


BITS = 32
DEFAULT_SOURCE = Path(
    ".research/rng_joint_sat/agent_joint/fixed-two-shear.json"
)
DEFAULT_FIXED_CERTIFICATE = Path(
    ".research/rng_joint_sat/agent_joint/fixed-BC-exact.json"
)


def bits(value: int) -> tuple[int, ...]:
    return tuple(index for index in range(BITS) if value >> index & 1)


def pair_partitions(row: int) -> tuple[tuple[int, ...], ...]:
    support = tuple(1 << index for index in bits(row))
    if len(support) == 3:
        return tuple((row ^ unit,) for unit in support)
    if len(support) == 4:
        return tuple(
            sorted(
                {
                    tuple(sorted((left, row ^ left)))
                    for left in (
                        support[0] | support[1],
                        support[0] | support[2],
                        support[0] | support[3],
                    )
                }
            )
        )
    raise ValueError(f"row {row:08x} has weight {len(support)}")


def load_matrix(document: dict[str, object], name: str) -> tuple[int, ...]:
    values = document[name]
    if not isinstance(values, list):
        raise TypeError(f"matrix {name!r} is not a list")
    return tuple(int(value, 16) if isinstance(value, str) else int(value) for value in values)


@dataclass
class CoverSearch:
    options: dict[int, tuple[frozenset[int], ...]]
    budget: int
    visited: set[frozenset[int]]
    solutions: set[frozenset[int]]
    pruned_budget: int = 0

    def run(self) -> None:
        self._visit(frozenset())

    def _visit(self, selected: frozenset[int]) -> None:
        if selected in self.visited:
            return
        self.visited.add(selected)

        uncovered = [
            (row, row_options)
            for row, row_options in self.options.items()
            if not any(option <= selected for option in row_options)
        ]
        if not uncovered:
            self.solutions.add(selected)
            return
        if len(selected) >= self.budget:
            self.pruned_budget += 1
            return

        # Any completion must contain one option of the chosen uncovered row.
        # Selecting the row with the fewest distinct increments keeps the
        # exhaustive state graph small without changing completeness.
        _, row_options = min(
            uncovered,
            key=lambda item: (
                len({option - selected for option in item[1]}),
                -min(len(option - selected) for option in item[1]),
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
            else:
                self.pruned_budget += 1


Atom = tuple[int, int]


def atom(seed_bit: int, state_bit: int) -> Atom:
    return seed_bit, state_bit


def label_realizations(pair: int, label: int) -> tuple[tuple[frozenset[Atom], tuple[int | None, int | None]], ...]:
    state_bits = bits(pair)
    seed_bits = bits(label)
    if len(state_bits) != 2 or len(seed_bits) > 2:
        raise ValueError("a first-layer pair needs two state bits and a label of weight <= 2")
    left_state, right_state = state_bits
    if not seed_bits:
        return ((frozenset(), (None, None)),)
    if len(seed_bits) == 1:
        seed = seed_bits[0]
        return (
            (frozenset((atom(seed, left_state),)), (seed, None)),
            (frozenset((atom(seed, right_state),)), (None, seed)),
        )
    left_seed, right_seed = seed_bits
    return (
        (
            frozenset((atom(left_seed, left_state), atom(right_seed, right_state))),
            (left_seed, right_seed),
        ),
        (
            frozenset((atom(right_seed, left_state), atom(left_seed, right_state))),
            (right_seed, left_seed),
        ),
    )


@dataclass(frozen=True)
class ComponentOption:
    mappings: frozenset[Atom]
    leaf_seeds: tuple[tuple[int, int | None, int | None], ...]


@dataclass(frozen=True)
class ComponentResult:
    offsets: dict[int, int]
    root_labels: tuple[int, ...]
    labels: dict[int, int]
    options: tuple[ComponentOption, ...]


def enumerate_component(
    offsets: dict[int, int],
    exact_labels: dict[int, int],
    residuals: Sequence[tuple[int, int, int]],
) -> ComponentResult:
    label_universe = (
        (0,)
        + tuple(1 << seed for seed in range(BITS))
        + tuple((1 << left) | (1 << right) for left, right in combinations(range(BITS), 2))
    )
    roots: list[int] = []
    all_options: dict[frozenset[Atom], ComponentOption] = {}
    unique_labels: dict[int, int] | None = None

    for root_label in label_universe:
        labels = {node: root_label ^ offset for node, offset in offsets.items()}
        if any(label.bit_count() > 2 for label in labels.values()):
            continue
        if any(labels.get(node, expected) != expected for node, expected in exact_labels.items()):
            continue

        direct_mappings: set[Atom] = set()
        feasible = True
        for node, target, state_bit in residuals:
            if node not in labels:
                continue
            residual = target ^ labels[node]
            if residual.bit_count() > 1:
                feasible = False
                break
            if residual:
                direct_mappings.add(atom(bits(residual)[0], state_bit))
        if not feasible:
            continue

        roots.append(root_label)
        unique_labels = labels
        partial = [
            ComponentOption(
                frozenset(direct_mappings),
                (),
            )
        ]
        for node in sorted(labels):
            expanded: dict[frozenset[Atom], ComponentOption] = {}
            for current in partial:
                for mappings, pin_seeds in label_realizations(node, labels[node]):
                    merged = current.mappings | mappings
                    option = ComponentOption(
                        merged,
                        current.leaf_seeds + ((node, pin_seeds[0], pin_seeds[1]),),
                    )
                    expanded.setdefault(merged, option)
            partial = list(expanded.values())
        for option in partial:
            all_options.setdefault(option.mappings, option)

    if unique_labels is None:
        raise AssertionError("tick-zero label component is infeasible")
    return ComponentResult(
        offsets=offsets,
        root_labels=tuple(roots),
        labels=unique_labels,
        options=tuple(
            sorted(
                all_options.values(),
                key=lambda option: (
                    len(option.mappings),
                    tuple(sorted(option.mappings)),
                ),
            )
        ),
    )


def build_components(
    selected_pairs: frozenset[int],
    t_rows: Sequence[int],
    b_rows: Sequence[int],
    decompositions: dict[int, tuple[int, ...]],
) -> tuple[
    frozenset[Atom],
    dict[int, int],
    tuple[tuple[int, int, int], ...],
    tuple[dict[int, int], ...],
]:
    adjacency: dict[int, list[tuple[int, int]]] = {pair: [] for pair in selected_pairs}
    exact_labels: dict[int, int] = {}
    residuals: list[tuple[int, int, int]] = []
    fixed_mappings: set[Atom] = set()

    for target, steady in zip(t_rows, b_rows):
        weight = steady.bit_count()
        if weight == 1:
            target_bits = bits(target)
            state_bits = bits(steady)
            if len(target_bits) != 1 or len(state_bits) != 1:
                raise AssertionError("direct B output does not have a unit tick-zero label")
            fixed_mappings.add(atom(target_bits[0], state_bits[0]))
        elif weight == 2:
            if steady not in selected_pairs:
                raise AssertionError("a pair-valued B output is absent from layer one")
            previous = exact_labels.setdefault(steady, target)
            if previous != target:
                raise AssertionError("one physical pair node has conflicting exact labels")
        elif weight == 3:
            pair = decompositions[steady][0]
            direct = steady ^ pair
            if direct.bit_count() != 1:
                raise AssertionError("weight-three decomposition is not pair XOR unit")
            residuals.append((pair, target, bits(direct)[0]))
        elif weight == 4:
            left, right = decompositions[steady]
            adjacency[left].append((right, target))
            adjacency[right].append((left, target))
        else:
            raise AssertionError(f"unsupported B row weight {weight}")

    active = (
        set(exact_labels)
        | {node for node, _, _ in residuals}
        | {node for node, edges in adjacency.items() if edges}
    )
    if active != set(selected_pairs):
        missing = selected_pairs - active
        raise AssertionError(f"unconstrained first-layer pair nodes: {sorted(missing)}")

    components: list[dict[int, int]] = []
    visited: set[int] = set()
    for root in sorted(active):
        if root in visited:
            continue
        offsets = {root: 0}
        stack = [root]
        while stack:
            node = stack.pop()
            visited.add(node)
            for neighbor, edge_label in adjacency[node]:
                expected = offsets[node] ^ edge_label
                if neighbor in offsets:
                    if offsets[neighbor] != expected:
                        raise AssertionError("inconsistent XOR equation cycle")
                else:
                    offsets[neighbor] = expected
                    stack.append(neighbor)
        components.append(offsets)
    return (
        frozenset(fixed_mappings),
        exact_labels,
        tuple(residuals),
        tuple(components),
    )


def mask(value: int) -> str:
    return f"{value:08x}"


def atom_text(value: Atom) -> str:
    return f"s{value[0]}:q{value[1]}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--fixed-certificate", type=Path, default=DEFAULT_FIXED_CERTIFICATE)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    source = json.loads(args.source.read_text(encoding="utf-8"))
    fixed_certificate = json.loads(args.fixed_certificate.read_text(encoding="utf-8"))
    t_rows = load_matrix(source, "T")
    b_rows = load_matrix(source, "B")
    c_rows = load_matrix(source, "C")
    if not (len(t_rows) == len(b_rows) == len(c_rows) == BITS):
        raise AssertionError("T/B/C must each have 32 rows")

    targets = frozenset(b_rows + c_rows)
    required_pairs = frozenset(row for row in targets if row.bit_count() == 2)
    finals = frozenset(row for row in targets if row.bit_count() in (3, 4))
    option_extras = {
        row: tuple(
            frozenset(option) - required_pairs
            for option in pair_partitions(row)
        )
        for row in finals
    }

    extra_budget = 15
    cover_search = CoverSearch(option_extras, extra_budget, set(), set())
    cover_search.run()
    if not cover_search.solutions:
        raise AssertionError("no exact 61-XOR pair cover was found")
    minimum_extra = min(len(solution) for solution in cover_search.solutions)
    minimum_extra_solutions = tuple(
        sorted(
            (solution for solution in cover_search.solutions if len(solution) == minimum_extra),
            key=lambda solution: tuple(sorted(solution)),
        )
    )
    if minimum_extra != extra_budget:
        raise AssertionError(f"expected the exact extra-pair minimum 15, got {minimum_extra}")
    if len(minimum_extra_solutions) != 1:
        raise AssertionError(
            f"expected a unique exact pair set, got {len(minimum_extra_solutions)}"
        )

    selected_pairs = required_pairs | minimum_extra_solutions[0]
    certificate_pairs = frozenset(
        int(value, 16) for value in fixed_certificate["selected_pair_gates"]
    )
    if selected_pairs != certificate_pairs:
        raise AssertionError("exhaustive pair cover differs from fixed-BC certificate")

    covered_options = {
        row: tuple(
            option
            for option in pair_partitions(row)
            if set(option) <= selected_pairs
        )
        for row in finals
    }
    ambiguous = {row: options for row, options in covered_options.items() if len(options) != 1}
    if ambiguous:
        raise AssertionError(f"exact pair set has non-unique decompositions: {ambiguous}")
    decompositions = {row: options[0] for row, options in covered_options.items()}

    # Canonicalizing a pair-valued output replaces a depth-two
    # (pair XOR pair) gate with the direct target pair: remove one final gate,
    # add one first-layer gate. XOR count and the set of non-target pair gates
    # do not change. Thus every non-canonical 61-XOR network maps to a cover
    # enumerated above. In this instance the unique heavy-row decompositions
    # use every pair-valued target, so none can actually remain depth two.
    heavy_pair_use_count = {
        pair: sum(pair in option for option in decompositions.values())
        for pair in selected_pairs
    }
    required_pairs_unused_by_heavy = frozenset(
        pair for pair in required_pairs if not heavy_pair_use_count[pair]
    )
    if required_pairs_unused_by_heavy:
        raise AssertionError(
            "non-canonical pair outputs need a separate audit: "
            + repr(sorted(required_pairs_unused_by_heavy))
        )

    noncanonical_pair_mediators = {}
    for pair in sorted(required_pairs):
        left, right = bits(pair)
        alternatives = []
        for common in range(BITS):
            if common in (left, right):
                continue
            first = (1 << left) | (1 << common)
            second = (1 << right) | (1 << common)
            if first in selected_pairs and second in selected_pairs:
                alternatives.append((first, second))
        noncanonical_pair_mediators[pair] = tuple(alternatives)

    fixed_mappings, exact_labels, residuals, component_offsets = build_components(
        selected_pairs,
        t_rows,
        b_rows,
        decompositions,
    )
    components = tuple(
        enumerate_component(offsets, exact_labels, residuals)
        for offsets in component_offsets
    )
    if any(len(component.root_labels) != 1 for component in components):
        raise AssertionError("a pair-label component does not have a unique root label")

    possible_atoms = tuple(
        frozenset().union(*(option.mappings for option in component.options))
        for component in components
    )
    cross_component_overlaps = []
    for right in range(len(components)):
        for left in range(right):
            overlap = possible_atoms[left] & possible_atoms[right]
            if overlap:
                cross_component_overlaps.append((left, right, overlap))
    if cross_component_overlaps:
        raise AssertionError(
            "component independence assumption failed: "
            + repr(cross_component_overlaps)
        )

    chosen_options: list[ComponentOption] = []
    component_details = []
    optimal_component_option_counts: list[int] = []
    for index, component in enumerate(components):
        minimum_new = min(
            len(option.mappings - fixed_mappings)
            for option in component.options
        )
        optimal_options = tuple(
            option
            for option in component.options
            if len(option.mappings - fixed_mappings) == minimum_new
        )
        optimal_component_option_counts.append(len(optimal_options))
        chosen = min(
            optimal_options,
            key=lambda option: (
                tuple(sorted(option.mappings)),
            ),
        )
        chosen_options.append(chosen)
        component_details.append(
            {
                "index": index,
                "nodes": [mask(node) for node in sorted(component.labels)],
                "root_label": mask(component.root_labels[0]),
                "pair_labels": {
                    mask(node): mask(label)
                    for node, label in sorted(component.labels.items())
                },
                "orientation_options": len(component.options),
                "minimum_orientation_options": len(optimal_options),
                "local_mapping_count": len(chosen.mappings),
                "minimum_new_mappings_after_fixed": minimum_new,
                "possible_fixed_reuse": [
                    atom_text(value)
                    for value in sorted(possible_atoms[index] & fixed_mappings)
                ],
                "chosen_leaf_seeds": [
                    {
                        "pair": mask(node),
                        "left_seed": left_seed,
                        "right_seed": right_seed,
                    }
                    for node, left_seed, right_seed in chosen.leaf_seeds
                ],
                "chosen_mappings": [atom_text(value) for value in sorted(chosen.mappings)],
            }
        )

    mode_pairs = fixed_mappings | frozenset().union(
        *(option.mappings for option in chosen_options)
    )
    exact_minimum = len(fixed_mappings) + sum(
        min(len(option.mappings - fixed_mappings) for option in component.options)
        for component in components
    )
    if len(mode_pairs) != exact_minimum:
        raise AssertionError("chosen component options do not attain the exact OR minimum")
    if exact_minimum != 47:
        raise AssertionError(f"expected fixed-DAG OR minimum 47, got {exact_minimum}")

    pair_labels = {
        node: label
        for component in components
        for node, label in component.labels.items()
    }
    for target, steady in zip(t_rows, b_rows):
        weight = steady.bit_count()
        if weight == 1:
            actual = target
        elif weight == 2:
            actual = pair_labels[steady]
        elif weight == 3:
            pair = decompositions[steady][0]
            residual = target ^ pair_labels[pair]
            if residual.bit_count() > 1:
                raise AssertionError("chosen weight-three residual is not a raw leaf")
            actual = pair_labels[pair] ^ residual
        else:
            left, right = decompositions[steady]
            actual = pair_labels[left] ^ pair_labels[right]
        if actual != target:
            raise AssertionError(
                f"B output {steady:08x} has tick-zero label {actual:08x}, expected {target:08x}"
            )

    xor_count = len(selected_pairs) + len(finals)
    gate_score = BITS * 5 + xor_count * 3 + exact_minimum + 6
    result = {
        "scope": "fixed two-shear T; all useful depth-2 XOR2 B/C networks with exactly 61 XOR",
        "source": str(args.source),
        "fixed_certificate": str(args.fixed_certificate),
        "cover_enumeration": {
            "required_pair_count": len(required_pairs),
            "extra_pair_budget": extra_budget,
            "visited_selected_extra_sets": len(cover_search.visited),
            "budget_prunes": cover_search.pruned_budget,
            "solutions_at_or_below_budget": len(cover_search.solutions),
            "minimum_extra_pair_count": minimum_extra,
            "minimum_pair_set_count": len(minimum_extra_solutions),
            "selected_pair_count": len(selected_pairs),
            "selected_pairs": [mask(pair) for pair in sorted(selected_pairs)],
            "unique_decomposition_count": len(decompositions),
            "canonicalization_complete_for_all_61_xor_networks": True,
            "required_pairs_used_by_heavy_finals": {
                mask(pair): heavy_pair_use_count[pair]
                for pair in sorted(required_pairs)
            },
            "required_pairs_unused_by_heavy_finals": [],
            "noncanonical_pair_mediators_inside_unique_pair_set": {
                mask(pair): [
                    [mask(first), mask(second)]
                    for first, second in noncanonical_pair_mediators[pair]
                ]
                for pair in sorted(required_pairs)
            },
        },
        "tick_zero_optimization": {
            "fixed_direct_mapping_count": len(fixed_mappings),
            "fixed_direct_mappings": [atom_text(value) for value in sorted(fixed_mappings)],
            "pair_components": len(components),
            "component_sizes": [len(component.labels) for component in components],
            "unique_root_label_per_component": True,
            "cross_component_possible_mapping_overlaps": 0,
            "raw_mapping_count_before_fixed_reuse": len(fixed_mappings)
            + sum(len(option.mappings) for option in chosen_options),
            "fixed_mapping_reuse_count": len(fixed_mappings)
            + sum(len(option.mappings) for option in chosen_options)
            - len(mode_pairs),
            "exact_minimum_or": exact_minimum,
            "optimal_mode_pair_set_count": prod(optimal_component_option_counts),
            "target_or_le_38": False,
            "mode_pairs": [atom_text(value) for value in sorted(mode_pairs)],
            "components": component_details,
        },
        "metrics": {
            "xor": xor_count,
            "or": exact_minimum,
            "gate": gate_score,
            "delay": 9,
            "cycles": 66,
            "energy": gate_score * 9 * 66,
        },
        "proof_summary": (
            "Exhaustive cover DFS finds one 15-extra-pair set and one decomposition per final. "
            "Canonicalizing any depth-two pair output preserves XOR count and extra-pair count; "
            "the unique heavy-row cover uses every pair target, so no non-canonical 61-XOR "
            "topology remains. "
            "The induced B-label equations have one weight<=2 root label per component. "
            "Possible mapping atoms are disjoint across components, so independent local minima "
            "give a global lower bound and construction of 47 OR gates."
        ),
    }

    encoded = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
    print(
        "cover states:",
        len(cover_search.visited),
        "minimum covers:",
        len(minimum_extra_solutions),
    )
    print("selected pair set: unique; decompositions: unique")
    print("tick-zero label components:", len(components), "all roots unique")
    print("cross-component possible mapping overlaps: 0")
    print("exact OR minimum:", exact_minimum)
    print("optimal 47-OR mapping sets:", prod(optimal_component_option_counts))
    print(f"candidate tuple: {gate_score}/9/66")
    if args.output:
        print("wrote:", args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
