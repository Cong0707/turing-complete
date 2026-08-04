from __future__ import annotations

import random
import unittest

from pysat.formula import IDPool
from pysat.solvers import Solver

import factorized_mixed_bus_cnf as factor
import search_hub79_global_function_map as gm


def generated_case(
    rng: random.Random,
) -> tuple[list[int], list[int], list[int], int, int]:
    row_count = rng.choice((8, 16))
    all_mask = (1 << row_count) - 1
    while True:
        target = rng.randrange(1, all_mask)
        one_rows = [bit for bit in range(row_count) if target & (1 << bit)]
        if len(one_rows) >= 2:
            break
    rng.shuffle(one_rows)
    split = rng.randrange(1, len(one_rows))
    left = sum(1 << bit for bit in one_rows[:split])
    right = target & ~left

    base = {0, all_mask, target, left}
    while len(base) < rng.randrange(6, 10):
        base.add(rng.randrange(all_mask + 1))
    expanded = {right}
    while len(expanded) < rng.randrange(5, 10):
        value = rng.randrange(all_mask + 1)
        if value not in base:
            expanded.add(value)
    data = set(expanded)
    while len(data) < rng.randrange(len(expanded), 11):
        value = rng.randrange(all_mask + 1)
        if value not in base:
            data.add(value)
    return sorted(base), sorted(expanded), sorted(data), target, all_mask


class FactorizedMixedBusTests(unittest.TestCase):
    def test_250_graphs_expand_to_the_same_retained_dependency_antichain(self) -> None:
        rng = random.Random(0xFAC702)
        for case_index in range(250):
            base, enables, data, target, all_mask = generated_case(rng)
            graph = factor.build_source1_data_factorization(
                base, enables, data, target
            )
            recipes, stats = gm.new_targeted_source1_data_mixed_two_switch_recipes(
                base,
                enables,
                data,
                [target],
                all_mask,
                max_per_coverage=0,
                probe_row_count=rng.randrange(all_mask.bit_length() + 1),
                exact_verification_threshold=rng.randrange(4),
            )
            self.assertTrue(stats["mixed_source1_data_bus2_enumeration_complete"])
            self.assertEqual(
                tuple(sorted(recipe.deps for recipe in recipes)),
                tuple(sorted(graph.retained_dependency_sets())),
                f"dependency antichain case {case_index}",
            )

            universe = set(base) | set(enables) | set(data)
            for _sample in range(20):
                available = {
                    truth for truth in universe if rng.randrange(2)
                }
                flat_feasible = any(
                    set(recipe.deps) <= available for recipe in recipes
                )
                self.assertEqual(flat_feasible, graph.is_feasible(available))

    def test_200_emitted_cnfs_match_direct_graph_feasibility(self) -> None:
        rng = random.Random(0xC0A6F)
        for case_index in range(200):
            base, enables, data, target, _all_mask = generated_case(rng)
            graph = factor.build_source1_data_factorization(
                base, enables, data, target
            )
            dependencies = sorted(
                {
                    truth
                    for _coverage, forms in (
                        *graph.base_by_coverage,
                        *graph.mixed_by_coverage,
                    )
                    for driver in forms
                    for truth in driver
                }
            )
            available = {
                truth for truth in dependencies if rng.randrange(2)
            }
            pool = IDPool()
            arrival = pool.id(("arrival", target))
            ready = {truth: pool.id(("ready", truth)) for truth in dependencies}
            producer, clauses = factor.encode_factorized_target(
                graph,
                [(arrival, ready)],
                pool.id,
            )
            if producer is None:
                self.assertFalse(graph.is_feasible(available))
                continue
            clauses.extend([[arrival], [producer]])
            clauses.extend(
                [literal if truth in available else -literal]
                for truth, literal in ready.items()
            )
            with Solver(name="cadical195", bootstrap_with=clauses) as solver:
                self.assertEqual(
                    graph.is_feasible(available),
                    solver.solve(),
                    f"CNF case {case_index}",
                )

    def test_shape_matches_emitted_clause_and_variable_counts(self) -> None:
        base = [0, 0b0011, 0b1111]
        enables = [0b1100, 0b1110]
        data = [0b1100, 0b1101]
        graph = factor.build_source1_data_factorization(
            base, enables, data, 0b1111
        )
        dependencies = sorted(
            {
                truth
                for _coverage, forms in (
                    *graph.base_by_coverage,
                    *graph.mixed_by_coverage,
                )
                for driver in forms
                for truth in driver
            }
        )
        pool = IDPool()
        slices = []
        for depth in range(3):
            arrival = pool.id(("arrival", depth))
            ready = {
                truth: pool.id(("ready", truth, depth))
                for truth in dependencies
            }
            slices.append((arrival, ready))
        before = pool.top
        producer, clauses = factor.encode_factorized_target(graph, slices, pool.id)
        shape = factor.factorized_incremental_shape(graph, len(slices))
        self.assertIsNotNone(producer)
        self.assertEqual(shape["incremental_variables"], pool.top - before)
        self.assertEqual(shape["incremental_clauses"], len(clauses))


if __name__ == "__main__":
    unittest.main()
