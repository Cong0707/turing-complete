"""Bound the row-deduplicated fixed-two-shear family against gate score 387.

The proof is combinatorial and uses less than a few hundred megabytes. It
extends the exact 61-XOR audit to the only neighboring XOR counts that could
possibly score at most 387: 62 and 63.
"""

from __future__ import annotations

import argparse
import importlib.util
from itertools import combinations, product
import json
from pathlib import Path
import sys
from typing import Iterable, Sequence


BITS = 32
SOURCE = Path(".research/rng_joint_sat/agent_joint/fixed-two-shear.json")
FIXED_CERTIFICATE = Path(".research/rng_joint_sat/agent_joint/fixed-BC-exact.json")
HELPER = Path(".research/rng_cost387/agent_paircover/enumerate_and_optimize.py")


def load_helper(path: Path):
    spec = importlib.util.spec_from_file_location("rng_paircover_helper", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_rows(document: dict[str, object], name: str) -> tuple[int, ...]:
    values = document[name]
    if not isinstance(values, list):
        raise TypeError(f"matrix {name!r} is not a list")
    return tuple(int(value, 16) if isinstance(value, str) else int(value) for value in values)


def exact_extra_sets(helper, option_extras, universe: frozenset[int], budget: int):
    search = helper.CoverSearch(option_extras, budget, set(), set())
    search.run()
    exact: set[frozenset[int]] = set()
    for solution in search.solutions:
        missing = budget - len(solution)
        if missing < 0:
            continue
        for padding in combinations(sorted(universe - solution), missing):
            exact.add(solution | frozenset(padding))
    return search, frozenset(exact)


def choices_for_rows(helper, rows: Sequence[int], selected: frozenset[int]):
    return tuple(
        tuple(
            option
            for option in helper.pair_partitions(row)
            if set(option) <= selected
        )
        for row in rows
    )


def build_mode_components(
    helper,
    t_rows: Sequence[int],
    b_rows: Sequence[int],
    heavy_decompositions: dict[int, tuple[int, ...]],
    unit_finals: dict[int, int],
):
    adjacency: dict[int, list[tuple[int, int]]] = {}
    exact_labels: dict[int, int] = {}
    residuals: list[tuple[int, int, int]] = []
    fixed_mappings: set[tuple[int, int]] = set()

    def touch(pair: int) -> None:
        adjacency.setdefault(pair, [])

    def add_edge(left: int, right: int, label: int) -> None:
        touch(left)
        touch(right)
        adjacency[left].append((right, label))
        adjacency[right].append((left, label))

    for target, steady in zip(t_rows, b_rows):
        weight = steady.bit_count()
        if weight == 1:
            if steady not in unit_finals:
                fixed_mappings.add((helper.bits(target)[0], helper.bits(steady)[0]))
                continue
            pair = unit_finals[steady]
            direct = steady ^ pair
            if direct.bit_count() != 1:
                return None
            touch(pair)
            residuals.append((pair, target, helper.bits(direct)[0]))
        elif weight == 2:
            touch(steady)
            previous = exact_labels.setdefault(steady, target)
            if previous != target:
                return None
        elif weight == 3:
            pair = heavy_decompositions[steady][0]
            direct = steady ^ pair
            if direct.bit_count() != 1:
                return None
            touch(pair)
            residuals.append((pair, target, helper.bits(direct)[0]))
        elif weight == 4:
            left, right = heavy_decompositions[steady]
            add_edge(left, right, target)
        else:
            raise AssertionError(f"unsupported B row weight {weight}")

    active = set(adjacency) | set(exact_labels) | {node for node, _, _ in residuals}
    visited: set[int] = set()
    offsets_list: list[dict[int, int]] = []
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
                        return None
                else:
                    offsets[neighbor] = expected
                    stack.append(neighbor)
        offsets_list.append(offsets)

    try:
        components = tuple(
            helper.enumerate_component(offsets, exact_labels, residuals)
            for offsets in offsets_list
        )
    except AssertionError:
        return None
    return frozenset(fixed_mappings), components


def component_union_lower_bound(fixed, components) -> int:
    minimum_sum = len(fixed)
    possible_users: dict[tuple[int, int], int] = {}
    for component in components:
        minimum_sum += min(len(option.mappings - fixed) for option in component.options)
        possible = frozenset().union(
            *(option.mappings - fixed for option in component.options)
        )
        for mapping in possible:
            possible_users[mapping] = possible_users.get(mapping, 0) + 1
    overlap_capacity = sum(max(0, users - 1) for users in possible_users.values())
    return minimum_sum - overlap_capacity


def option_as_function(option, fixed):
    mapping = dict(fixed)
    for seed, state in option.mappings:
        previous = mapping.setdefault(seed, state)
        if previous != state:
            return None
    return tuple(sorted(mapping.items()))


def has_or_32(fixed, components) -> bool:
    """OR=32 iff every seed bit uses exactly one state coordinate."""

    domains: list[list[dict[int, int]]] = []
    for component in components:
        functions = {
            option_as_function(option, fixed)
            for option in component.options
        }
        functions.discard(None)
        if not functions:
            return False
        domains.append([dict(function) for function in functions])
    domains.sort(key=len)

    assigned = dict(fixed)

    def visit(index: int) -> bool:
        if index == len(domains):
            return len(assigned) == BITS
        for option in domains[index]:
            if any(seed in assigned and assigned[seed] != state for seed, state in option.items()):
                continue
            added = [seed for seed in option if seed not in assigned]
            for seed in added:
                assigned[seed] = option[seed]
            if visit(index + 1):
                return True
            for seed in added:
                del assigned[seed]
        return False

    return visit(0)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--fixed-certificate", type=Path, default=FIXED_CERTIFICATE)
    parser.add_argument("--helper", type=Path, default=HELPER)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    helper = load_helper(args.helper)
    source = json.loads(args.source.read_text(encoding="utf-8"))
    fixed_certificate = json.loads(args.fixed_certificate.read_text(encoding="utf-8"))
    t_rows = load_rows(source, "T")
    b_rows = load_rows(source, "B")
    c_rows = load_rows(source, "C")
    targets = frozenset(b_rows + c_rows)
    required_pairs = frozenset(row for row in targets if row.bit_count() == 2)
    final_rows = tuple(sorted(row for row in targets if row.bit_count() in (3, 4)))
    b_final_rows = tuple(row for row in b_rows if row.bit_count() in (3, 4))
    b_unit_rows = tuple(row for row in b_rows if row.bit_count() == 1)
    option_extras = {
        row: tuple(
            frozenset(option) - required_pairs
            for option in helper.pair_partitions(row)
        )
        for row in final_rows
    }
    heavy_extra_universe = frozenset(
        pair
        for row_options in option_extras.values()
        for option in row_options
        for pair in option
    )
    all_pairs = frozenset(
        (1 << left) | (1 << right)
        for left, right in combinations(range(BITS), 2)
    )

    searches = {}
    exact_sets = {}
    for budget in (15, 16, 17):
        searches[budget], exact_sets[budget] = exact_extra_sets(
            helper,
            option_extras,
            heavy_extra_universe,
            budget,
        )
    if tuple(len(exact_sets[budget]) for budget in (15, 16, 17)) != (1, 92, 4198):
        raise AssertionError("exact extra-set frontier changed")

    base_pairs = frozenset(
        int(value, 16) for value in fixed_certificate["selected_pair_gates"]
    )
    base_extra = base_pairs - required_pairs
    if exact_sets[15] != frozenset((base_extra,)):
        raise AssertionError("15-extra cover differs from the fixed certificate")
    base_decompositions = {
        int(row, 16): tuple(int(pair, 16) for pair in option)
        for row, option in fixed_certificate["decompositions"].items()
    }

    # Audit canonicalization for 61..63 XOR. Every heavy decomposition still
    # consumes every pair-valued target, so no target pair can be moved to a
    # depth-two pair-XOR-pair output in these budgets.
    heavy_combo_counts = {}
    missing_required_counts = {}
    b_topologies_by_budget: dict[int, set[tuple[tuple[int, ...], ...]]] = {}
    for budget in (15, 16, 17):
        combo_count = 0
        missing_count = 0
        b_topologies: set[tuple[tuple[int, ...], ...]] = set()
        for extra in exact_sets[budget]:
            selected = required_pairs | extra
            all_choices = choices_for_rows(helper, final_rows, selected)
            b_choices = choices_for_rows(helper, b_final_rows, selected)
            for decomposition_tuple in product(*all_choices):
                combo_count += 1
                used = set().union(*(set(option) for option in decomposition_tuple))
                if required_pairs - used:
                    missing_count += 1
            for decomposition_tuple in product(*b_choices):
                b_topologies.add(decomposition_tuple)
        heavy_combo_counts[budget] = combo_count
        missing_required_counts[budget] = missing_count
        b_topologies_by_budget[budget] = b_topologies
    if any(missing_required_counts.values()):
        raise AssertionError("a pair-valued target can be omitted in the 61..63 XOR frontier")

    # 61 XOR: imported exact result.
    exact_61 = json.loads(
        Path(".research/rng_cost387/agent_paircover/result.json").read_text(encoding="utf-8")
    )
    if exact_61["tick_zero_optimization"]["exact_minimum_or"] != 47:
        raise AssertionError("61-XOR OR optimum changed")

    # 62 XOR has two accounting cases: 16 extra pairs, or 15 extras plus one
    # unit output deliberately moved to layer two.
    lower_bounds_62 = []
    feasible_topologies_62 = 0
    for topology in b_topologies_by_budget[16]:
        decompositions = dict(base_decompositions)
        decompositions.update(zip(b_final_rows, topology))
        built = build_mode_components(helper, t_rows, b_rows, decompositions, {})
        if built is None:
            continue
        feasible_topologies_62 += 1
        lower_bounds_62.append(component_union_lower_bound(*built))
    if not lower_bounds_62 or min(lower_bounds_62) <= 35:
        raise AssertionError(
            "62-XOR component lower bound no longer excludes OR<=35: "
            + repr(sorted(lower_bounds_62))
        )

    base_selected = required_pairs | base_extra
    unit_cases_62 = 0
    unit_label_feasible_62 = 0
    for unit in b_unit_rows:
        for pair in base_selected:
            if not pair & unit:
                continue
            unit_cases_62 += 1
            built = build_mode_components(
                helper,
                t_rows,
                b_rows,
                base_decompositions,
                {unit: pair},
            )
            unit_label_feasible_62 += built is not None
    if unit_label_feasible_62:
        raise AssertionError("15-extra plus one unit-final topology became label-feasible")

    # 63 XOR, case A: 15 extras plus two unit finals.
    unit_pair_choices = {
        unit: tuple(pair for pair in base_selected if pair & unit)
        for unit in b_unit_rows
    }
    unit_cases_63_e15 = 0
    unit_label_feasible_63_e15 = 0
    for units in combinations(b_unit_rows, 2):
        for pairs in product(*(unit_pair_choices[unit] for unit in units)):
            unit_cases_63_e15 += 1
            built = build_mode_components(
                helper,
                t_rows,
                b_rows,
                base_decompositions,
                dict(zip(units, pairs)),
            )
            unit_label_feasible_63_e15 += built is not None
    if unit_label_feasible_63_e15:
        raise AssertionError("15-extra plus two unit-final topology became label-feasible")

    # 63 XOR, case B: 16 extras plus one unit final. The added non-target pair
    # may be any of the 496 possible pairs, not only a heavy-row candidate.
    unit_topologies_63: set[tuple[tuple[tuple[int, ...], ...], int, int]] = set()
    for added in sorted(all_pairs - required_pairs - base_selected):
        selected = base_selected | frozenset((added,))
        b_choices = choices_for_rows(helper, b_final_rows, selected)
        for topology in product(*b_choices):
            for unit in b_unit_rows:
                for pair in selected:
                    if pair & unit:
                        unit_topologies_63.add((topology, unit, pair))
    unit_label_feasible_63 = 0
    unit_or32_63 = 0
    for topology, unit, pair in unit_topologies_63:
        decompositions = dict(base_decompositions)
        decompositions.update(zip(b_final_rows, topology))
        built = build_mode_components(
            helper,
            t_rows,
            b_rows,
            decompositions,
            {unit: pair},
        )
        if built is None:
            continue
        unit_label_feasible_63 += 1
        unit_or32_63 += has_or_32(*built)
    if unit_or32_63:
        raise AssertionError("63-XOR one-unit-final case reached the 32-OR lower bound")

    # 63 XOR, case C: 17 extras and direct unit outputs.
    direct_label_feasible_63 = 0
    direct_or32_63 = 0
    for topology in b_topologies_by_budget[17]:
        decompositions = dict(base_decompositions)
        decompositions.update(zip(b_final_rows, topology))
        built = build_mode_components(helper, t_rows, b_rows, decompositions, {})
        if built is None:
            continue
        direct_label_feasible_63 += 1
        direct_or32_63 += has_or_32(*built)
    if direct_or32_63:
        raise AssertionError("63-XOR direct-unit case reached the 32-OR lower bound")

    result = {
        "scope": (
            "fixed two-shear T; row-deduplicated depth-2 XOR2 B/C networks; "
            "dual-mode OR leaves"
        ),
        "cover_frontier": {
            str(budget): {
                "visited_partial_sets": len(searches[budget].visited),
                "terminal_cover_sets": len(searches[budget].solutions),
                "exact_extra_sets_over_heavy_candidate_universe": len(exact_sets[budget]),
                "heavy_decomposition_combinations": heavy_combo_counts[budget],
                "heavy_combinations_missing_any_pair_target": missing_required_counts[budget],
                "distinct_B_topologies": len(b_topologies_by_budget[budget]),
            }
            for budget in (15, 16, 17)
        },
        "bounds": {
            "xor_minimum": 61,
            "or_rank_minimum": 32,
            "xor_61": {
                "required_or_for_gate_387": 38,
                "exact_or_minimum": 47,
                "best_gate": 396,
            },
            "xor_62": {
                "required_or_for_gate_387": 35,
                "extra16_B_topologies": len(b_topologies_by_budget[16]),
                "label_feasible_extra16_B_topologies": feasible_topologies_62,
                "minimum_proved_or_lower_bound": min(lower_bounds_62),
                "extra15_plus_unit_cases": unit_cases_62,
                "extra15_plus_unit_label_feasible": unit_label_feasible_62,
            },
            "xor_63": {
                "required_or_for_gate_387": 32,
                "extra15_plus_two_units_cases": unit_cases_63_e15,
                "extra15_plus_two_units_label_feasible": unit_label_feasible_63_e15,
                "extra16_plus_unit_topologies": len(unit_topologies_63),
                "extra16_plus_unit_label_feasible": unit_label_feasible_63,
                "extra16_plus_unit_or32": unit_or32_63,
                "extra17_B_topologies": len(b_topologies_by_budget[17]),
                "extra17_label_feasible_B_topologies": direct_label_feasible_63,
                "extra17_or32": direct_or32_63,
            },
            "xor_64_or_more": {
                "best_possible_gate_using_or_rank_minimum": 160 + 3 * 64 + 32 + 6,
            },
        },
        "gate_387_reachable_in_scoped_family": False,
        "excluded_from_scope": (
            "At 62/63 XOR, duplicate physical gates with the same steady-state row but "
            "different tick-zero labels may use the extra gate budget. The steady-row "
            "pair-cover model intentionally deduplicates them. At the exact 61-XOR "
            "minimum such duplicates are impossible, because merging one would produce "
            "a forbidden <=60-XOR steady network."
        ),
        "best_verified_tuple": "396/9/66",
        "proof_summary": (
            "XOR<61 is excluded by the exhaustive 15-extra-pair cover bound. "
            "At 61 XOR the exact OR minimum is 47. At 62 XOR every feasible B topology "
            "has a component-union lower bound above 35, while the unit-final trade "
            "is label-infeasible. At 63 XOR exhaustive partial-function compatibility finds "
            "no 32-OR topology in either unit-final accounting case. At 64 XOR, the rank "
            "minimum of 32 OR already gives gate 390."
        ),
    }
    encoded = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
    print("extra-set frontier:", [len(exact_sets[value]) for value in (15, 16, 17)])
    print("heavy combos missing a target pair:", list(missing_required_counts.values()))
    print("62-XOR minimum OR lower bound:", min(lower_bounds_62))
    print("63-XOR OR=32 hits:", unit_or32_63 + direct_or32_63)
    print("row-deduplicated fixed-T gate<=387:", False)
    if args.output:
        print("wrote:", args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
