from __future__ import annotations

import random
import unittest

import search_hub79_global_function_map as gm
import search_phase_high_global_map as phase


def independent_minimal_forms(
    rows: list[tuple[int, int]],
) -> list[tuple[int, int]]:
    by_deps: dict[frozenset[int], tuple[int, int]] = {}
    for row in set(rows):
        deps = frozenset(row)
        old = by_deps.get(deps)
        if old is None or row < old:
            by_deps[deps] = row
    ordered = sorted(
        by_deps.items(),
        key=lambda item: (len(item[0]), sorted(item[0]), item[1]),
    )
    result: list[tuple[int, int]] = []
    result_deps: list[frozenset[int]] = []
    for deps, row in ordered:
        if any(old <= deps for old in result_deps):
            continue
        result_deps.append(deps)
        result.append(row)
    return result


def independent_minimal_records(
    records: dict[
        frozenset[int], tuple[tuple[int, int], tuple[int, int]]
    ],
) -> list[tuple[frozenset[int], tuple[tuple[int, int], tuple[int, int]]]]:
    ordered = sorted(records.items(), key=lambda item: (len(item[0]), sorted(item[0])))
    result: list[
        tuple[frozenset[int], tuple[tuple[int, int], tuple[int, int]]]
    ] = []
    for deps, drivers in ordered:
        if any(old_deps <= deps for old_deps, _old_drivers in result):
            continue
        result.append((deps, drivers))
    return result


def brute_force_source1_data_recipes(
    base_universe: list[int],
    expanded_enables: list[int],
    expanded_data: list[int],
    targets: list[int],
) -> set[tuple[int, tuple[int, ...], tuple[tuple[int, int], tuple[int, int]]]]:
    base = sorted(set(base_universe))
    base_set = set(base)
    enables = sorted(set(expanded_enables) - base_set)
    data_rows = sorted(set(expanded_data) - base_set)
    result: set[
        tuple[int, tuple[int, ...], tuple[tuple[int, int], tuple[int, int]]]
    ] = set()

    for target in sorted(set(targets)):
        if target == 0:
            continue
        base_by_coverage: dict[int, list[tuple[int, int]]] = {}
        for enable in base:
            if enable == target:
                continue
            for data in base:
                if data == target or enable & (data ^ target):
                    continue
                coverage = enable & data
                if coverage:
                    base_by_coverage.setdefault(coverage, []).append((enable, data))
        base_by_coverage = {
            coverage: independent_minimal_forms(rows)
            for coverage, rows in base_by_coverage.items()
        }

        mixed_by_coverage: dict[int, list[tuple[int, int]]] = {}
        for enable in enables:
            if enable == target:
                continue
            for data in data_rows:
                if data == target or enable & (data ^ target):
                    continue
                coverage = enable & data
                if coverage:
                    mixed_by_coverage.setdefault(coverage, []).append((enable, data))
        mixed_by_coverage = {
            coverage: independent_minimal_forms(rows)
            for coverage, rows in mixed_by_coverage.items()
        }

        records: dict[
            frozenset[int], tuple[tuple[int, int], tuple[int, int]]
        ] = {}
        for mixed_coverage, mixed_drivers in mixed_by_coverage.items():
            missing = target & ~mixed_coverage
            for base_coverage, base_drivers in base_by_coverage.items():
                if missing & ~base_coverage:
                    continue
                for base_driver in base_drivers:
                    for mixed_driver in mixed_drivers:
                        if base_driver == mixed_driver:
                            continue
                        deps = frozenset((*base_driver, *mixed_driver))
                        if target in deps:
                            continue
                        drivers = tuple(sorted((base_driver, mixed_driver)))
                        old = records.get(deps)
                        if old is None or drivers < old:
                            records[deps] = drivers

        for deps, drivers in independent_minimal_records(records):
            result.add((target, tuple(sorted(deps)), drivers))
    return result


def generated_case(
    rng: random.Random,
) -> tuple[list[int], list[int], list[int], list[int], int]:
    row_count = rng.choice((8, 16))
    all_mask = (1 << row_count) - 1
    while True:
        target = rng.randrange(1, all_mask)
        one_rows = [bit for bit in range(row_count) if target & (1 << bit)]
        if len(one_rows) >= 2:
            break

    rng.shuffle(one_rows)
    split = rng.randrange(1, len(one_rows))
    left_coverage = sum(1 << bit for bit in one_rows[:split])
    right_coverage = target & ~left_coverage

    base = {0, all_mask, target, left_coverage}
    while len(base) < rng.randrange(6, 10):
        base.add(rng.randrange(all_mask + 1))

    expanded = {right_coverage}
    while len(expanded) < rng.randrange(5, 10):
        truth = rng.randrange(all_mask + 1)
        if truth not in base:
            expanded.add(truth)
    # Keep a second independently chosen data universe in some cases.  Both are
    # still strictly disjoint from base, matching the production class rules.
    data = set(expanded)
    while len(data) < rng.randrange(len(expanded), 11):
        truth = rng.randrange(all_mask + 1)
        if truth not in base:
            data.add(truth)
    return sorted(base), sorted(expanded), sorted(data), [target], all_mask


class Source1DataMixedTests(unittest.TestCase):
    def test_seqcounter_closed_form_matches_pysat_matrix(self) -> None:
        from pysat.card import CardEnc, EncType
        from pysat.formula import IDPool

        for literal_count in range(101):
            for bound in range(literal_count + 2):
                pool = IDPool()
                literals = [pool.id(("x", index)) for index in range(literal_count)]
                before = pool.top
                encoded = CardEnc.atmost(
                    lits=literals,
                    bound=bound,
                    vpool=pool,
                    encoding=EncType.seqcounter,
                )
                self.assertEqual(
                    (pool.top - before, len(encoded.clauses)),
                    phase.seqcounter_atmost_shape(literal_count, bound),
                    (literal_count, bound),
                )

    def test_200_random_cnf_estimators_match_constructed_pysat(self) -> None:
        from pysat.card import CardEnc, EncType
        from pysat.formula import IDPool

        def constructed_reference(
            recipes,
            active,
            producers,
            earliest,
            sources,
            outputs,
            delay_bound,
            gate_bound,
        ):
            pool = IDPool()
            xvars = {index: pool.id(("x", index)) for index in active}
            avars = {
                (truth, depth): pool.id(("a", truth, depth))
                for truth in producers
                for depth in range(max(1, earliest[truth]), delay_bound + 1)
            }
            arrival_counts = {
                truth: delay_bound - max(1, earliest[truth]) + 1
                for truth in producers
            }
            explicit_base = pool.top
            clauses = 0
            for truth, recipe_rows in producers.items():
                selected = [xvars[index] for index in recipe_rows]
                arrivals = [
                    avars[(truth, depth)]
                    for depth in range(max(1, earliest[truth]), delay_bound + 1)
                ]
                for literals in (selected, arrivals):
                    if len(literals) > 1:
                        encoded = CardEnc.atmost(
                            lits=literals,
                            bound=1,
                            vpool=pool,
                            encoding=EncType.seqcounter,
                        )
                        clauses += len(encoded.clauses)
                clauses += len(recipe_rows) + arrival_counts[truth]
            producer_aux = pool.top - explicit_base

            dependency_clauses = 0
            for index in active:
                recipe = recipes[index]
                for target_depth in range(
                    max(1, earliest[recipe.target]), delay_bound + 1
                ):
                    deadline = target_depth - recipe.step_delay
                    for dep in recipe.deps:
                        if dep in sources and sources[dep] <= deadline:
                            continue
                        dependency_clauses += 1
            clauses += dependency_clauses + len(outputs)

            cost_literals = []
            cost_groups = 0
            cost_link_clauses = 0
            for truth, recipe_rows in producers.items():
                arrival_count = arrival_counts[truth]
                cost_literals.append(pool.id(("cost_target", truth)))
                cost_groups += 1
                cost_link_clauses += arrival_count + 1
                maximum_cost = max(recipes[index].cost for index in recipe_rows)
                for tier in range(2, maximum_cost + 1):
                    eligible = [
                        xvars[index]
                        for index in recipe_rows
                        if recipes[index].cost >= tier
                    ]
                    if not eligible:
                        continue
                    cost_literals.append(pool.id(("cost_tier", truth, tier)))
                    cost_groups += 1
                    cost_link_clauses += len(eligible) + 1
            clauses += cost_link_clauses
            before_cost = pool.top
            bounded = CardEnc.atmost(
                lits=cost_literals,
                bound=gate_bound,
                vpool=pool,
                encoding=EncType.seqcounter,
            )
            cost_aux = pool.top - before_cost
            clauses += len(bounded.clauses)
            return {
                "active_recipe_variables": len(active),
                "arrival_variables": sum(arrival_counts.values()),
                "auxiliary_variables": producer_aux + cost_aux,
                "producer_cardinality_auxiliary_variables": producer_aux,
                "cost_cardinality_auxiliary_variables": cost_aux,
                "cost_group_variables": cost_groups,
                "cost_literal_count": len(cost_literals),
                "dependency_clause_count": dependency_clauses,
                "cost_link_clause_count": cost_link_clauses,
                "cnf_variables": pool.top,
                "cnf_clauses": clauses,
            }

        rng = random.Random(0xC0F5A9E)
        for case_index in range(200):
            delay_bound = rng.randrange(1, 7)
            sources = {0: 0, 1: 0}
            recipes = []
            producers = {}
            earliest = {}
            truth_rows = list(range(2, 2 + rng.randrange(1, 12)))
            for truth in truth_rows:
                earliest[truth] = rng.randrange(1, delay_bound + 1)
                for _row in range(rng.randrange(1, 12)):
                    index = len(recipes)
                    dependency_pool = [*sources, *truth_rows]
                    deps = tuple(
                        sorted(
                            rng.sample(
                                dependency_pool,
                                rng.randrange(min(4, len(dependency_pool)) + 1),
                            )
                        )
                    )
                    recipes.append(
                        gm.Recipe(
                            truth,
                            "TEST",
                            deps,
                            rng.choice((1, 2, 4)),
                            rng.choice((1, 2)),
                        )
                    )
                    producers.setdefault(truth, []).append(index)
            active = list(range(len(recipes)))
            outputs = [(f"o{index}", truth) for index, truth in enumerate(truth_rows[:3])]
            gate_bound = rng.randrange(0, 20)
            expected = constructed_reference(
                recipes,
                active,
                producers,
                earliest,
                sources,
                outputs,
                delay_bound,
                gate_bound,
            )
            actual = phase.estimate_producer_tiered_cnf_shape(
                recipes,
                active,
                producers,
                earliest,
                sources,
                outputs,
                delay_bound=delay_bound,
                gate_bound=gate_bound,
            )
            self.assertEqual(
                expected,
                {key: actual[key] for key in expected},
                f"CNF estimator case {case_index}",
            )

    def test_direct_subset_antichain_matches_quadratic_reference(self) -> None:
        rng = random.Random(0xA471C)
        for case_index in range(500):
            records: dict[
                frozenset[int], tuple[tuple[int, int], tuple[int, int]]
            ] = {}
            for _row in range(rng.randrange(1, 80)):
                deps = frozenset(rng.sample(range(12), rng.randrange(5)))
                records[deps] = ((1, 2), (3, 4))
            expected = independent_minimal_records(records)
            self.assertEqual(
                expected,
                gm.minimal_dependency_sets(records),
                f"antichain case {case_index}",
            )

    def test_500_driver_form_antichains_match_quadratic_reference(self) -> None:
        rng = random.Random(0xD21A3)
        for case_index in range(500):
            rows = [
                (rng.randrange(20), rng.randrange(20))
                for _row in range(rng.randrange(1, 200))
            ]
            self.assertEqual(
                independent_minimal_forms(rows),
                gm.minimal_driver_forms(rows),
                f"driver form case {case_index}",
            )

    def test_250_random_small_domains_match_independent_bruteforce(self) -> None:
        rng = random.Random(0x5A17D4A)
        for case_index in range(250):
            base, enables, data, targets, all_mask = generated_case(rng)
            row_count = all_mask.bit_length()
            expected = brute_force_source1_data_recipes(
                base, enables, data, targets
            )
            actual_rows, stats = (
                gm.new_targeted_source1_data_mixed_two_switch_recipes(
                    base,
                    enables,
                    data,
                    targets,
                    all_mask,
                    max_per_coverage=256,
                    probe_row_count=rng.randrange(row_count + 1),
                    exact_verification_threshold=rng.randrange(4),
                )
            )
            actual = {
                (recipe.target, recipe.deps, recipe.detail)
                for recipe in actual_rows
            }
            self.assertEqual(expected, actual, f"random case {case_index}")
            self.assertTrue(
                stats["mixed_source1_data_bus2_probe_filter_conservative"]
            )
            self.assertTrue(
                stats["mixed_source1_data_bus2_enumeration_complete"]
            )

            for recipe in actual_rows:
                ones = 0
                zeros = 0
                for enable, data_truth in recipe.detail:
                    ones |= enable & data_truth
                    zeros |= enable & (~data_truth & all_mask)
                self.assertFalse(ones & zeros)
                self.assertEqual(recipe.target, ones)

    def test_250_indexed_base_data_cases_match_full_scan(self) -> None:
        rng = random.Random(0xBA5EDA7A)
        stable_stat_keys = (
            "mixed_bus2_targets_with_recipe",
            "mixed_bus2_raw_dependency_sets",
            "mixed_bus2_retained_recipes",
            "mixed_bus2_base_coverage_count",
            "mixed_bus2_coverage_count",
            "mixed_bus2_candidate_expanded_enable_count",
            "mixed_bus2_valid_driver_count",
            "mixed_bus2_max_base_forms_in_any_coverage",
            "mixed_bus2_max_expanded_forms_in_any_coverage",
            "mixed_bus2_truncated_base_coverage_count",
            "mixed_bus2_truncated_expanded_coverage_count",
            "mixed_bus2_enumeration_complete",
        )
        for case_index in range(250):
            base, enables, _data, targets, all_mask = generated_case(rng)
            expected_rows, expected_stats = gm.new_targeted_mixed_two_switch_recipes(
                base,
                enables,
                targets,
                max_per_coverage=256,
            )
            actual_rows, actual_stats = gm.new_targeted_mixed_two_switch_recipes(
                base,
                enables,
                targets,
                max_per_coverage=256,
                all_mask=all_mask,
                probe_row_count=rng.randrange(all_mask.bit_length() + 1),
                exact_verification_threshold=rng.randrange(4),
            )
            self.assertEqual(expected_rows, actual_rows, f"base-data case {case_index}")
            self.assertEqual(
                {key: expected_stats[key] for key in stable_stat_keys},
                {key: actual_stats[key] for key in stable_stat_keys},
                f"base-data stats {case_index}",
            )


if __name__ == "__main__":
    unittest.main()
