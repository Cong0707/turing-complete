"""Prototype an exact factorized CNF for one mixed two-driver BUS class.

The production enumerator currently materializes one ``Recipe`` for every
dependency-minimal pair of driver forms.  This prototype retains the earlier
factorization instead:

``producer -> compatible coverage pair -> one form per coverage -> dependencies``

All alternatives have the same cost (four Switches) and step delay (one), so
the factorization is equisatisfiable with the flat recipe antichain.  It is a
standalone sizing/validation module; it does not change the production solver.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

import search_hub79_global_function_map as gm


Driver = tuple[int, int]


@dataclass(frozen=True)
class FactorizedBusTarget:
    target: int
    base_by_coverage: tuple[tuple[int, tuple[Driver, ...]], ...]
    mixed_by_coverage: tuple[tuple[int, tuple[Driver, ...]], ...]
    compatible_coverage_pairs: tuple[tuple[int, int], ...]

    @property
    def base_form_count(self) -> int:
        return sum(len(forms) for _coverage, forms in self.base_by_coverage)

    @property
    def mixed_form_count(self) -> int:
        return sum(len(forms) for _coverage, forms in self.mixed_by_coverage)

    @property
    def coverage_count(self) -> int:
        return len(self.base_by_coverage) + len(self.mixed_by_coverage)

    @property
    def coverage_pair_count(self) -> int:
        return len(self.compatible_coverage_pairs)

    def is_feasible(self, available: set[int]) -> bool:
        base = dict(self.base_by_coverage)
        mixed = dict(self.mixed_by_coverage)
        for base_coverage, mixed_coverage in self.compatible_coverage_pairs:
            if not any(set(driver) <= available for driver in base[base_coverage]):
                continue
            if any(set(driver) <= available for driver in mixed[mixed_coverage]):
                return True
        return False

    def retained_dependency_sets(self) -> tuple[tuple[int, ...], ...]:
        """Expand only for validation against the existing flat enumerator."""

        base = dict(self.base_by_coverage)
        mixed = dict(self.mixed_by_coverage)
        records: dict[
            frozenset[int], tuple[tuple[int, int], tuple[int, int]]
        ] = {}
        for base_coverage, mixed_coverage in self.compatible_coverage_pairs:
            for base_driver in base[base_coverage]:
                for mixed_driver in mixed[mixed_coverage]:
                    deps = frozenset((*base_driver, *mixed_driver))
                    drivers = tuple(sorted((base_driver, mixed_driver)))
                    old = records.get(deps)
                    if old is None or drivers < old:
                        records[deps] = drivers
        return tuple(
            tuple(sorted(deps))
            for deps, _drivers in gm.minimal_dependency_sets(records)
        )


def build_source1_data_factorization(
    base_universe: Iterable[int],
    expanded_enables: Iterable[int],
    expanded_data: Iterable[int],
    target: int,
) -> FactorizedBusTarget:
    """Build the untruncated factor graph using exact full truth conditions."""

    base = sorted(set(base_universe))
    base_set = set(base)
    enables = sorted(set(expanded_enables) - base_set)
    data_rows = sorted(set(expanded_data) - base_set)

    base_by_coverage: dict[int, list[Driver]] = {}
    if target:
        for enable in base:
            if enable == target:
                continue
            for data in base:
                if data == target or enable & (data ^ target):
                    continue
                coverage = enable & data
                if coverage:
                    base_by_coverage.setdefault(coverage, []).append((enable, data))

    mixed_by_coverage: dict[int, list[Driver]] = {}
    if base_by_coverage:
        for enable in enables:
            if enable == target:
                continue
            coverage = enable & target
            if not coverage:
                continue
            for data in data_rows:
                if data == target or enable & (data ^ target):
                    continue
                if enable & data != coverage:
                    raise RuntimeError("source1-data mixed coverage identity failed")
                mixed_by_coverage.setdefault(coverage, []).append((enable, data))

    minimized_base = {
        coverage: tuple(gm.minimal_driver_forms(forms))
        for coverage, forms in base_by_coverage.items()
    }
    minimized_mixed = {
        coverage: tuple(gm.minimal_driver_forms(forms))
        for coverage, forms in mixed_by_coverage.items()
    }
    compatible = tuple(
        (base_coverage, mixed_coverage)
        for mixed_coverage in sorted(minimized_mixed)
        for base_coverage in sorted(minimized_base)
        if not ((target & ~mixed_coverage) & ~base_coverage)
    )
    return FactorizedBusTarget(
        target=target,
        base_by_coverage=tuple(sorted(minimized_base.items())),
        mixed_by_coverage=tuple(sorted(minimized_mixed.items())),
        compatible_coverage_pairs=compatible,
    )


def factorized_incremental_shape(
    graph: FactorizedBusTarget, arrival_depth_count: int
) -> dict[str, int]:
    """Count the prototype variables/clauses beyond existing arrival variables."""

    if arrival_depth_count < 0:
        raise ValueError("arrival_depth_count must be non-negative")
    pair_count = graph.coverage_pair_count
    if not pair_count:
        return {
            "producer_class_variables": 0,
            "coverage_pair_variables": 0,
            "coverage_variables": 0,
            "driver_form_variables": 0,
            "incremental_variables": 0,
            "producer_to_pair_clauses": 0,
            "pair_to_coverage_clauses": 0,
            "coverage_to_form_clauses": 0,
            "driver_dependency_clauses": 0,
            "incremental_clauses": 0,
        }

    forms = [
        driver
        for _coverage, rows in (
            *graph.base_by_coverage,
            *graph.mixed_by_coverage,
        )
        for driver in rows
    ]
    dependency_count = sum(len(set(driver)) for driver in forms)
    producer_to_pair = 1
    pair_to_coverage = 2 * pair_count
    coverage_to_form = graph.coverage_count
    dependency_clauses = arrival_depth_count * dependency_count
    variables = 1 + pair_count + graph.coverage_count + len(forms)
    clauses = (
        producer_to_pair
        + pair_to_coverage
        + coverage_to_form
        + dependency_clauses
    )
    return {
        "producer_class_variables": 1,
        "coverage_pair_variables": pair_count,
        "coverage_variables": graph.coverage_count,
        "driver_form_variables": len(forms),
        "incremental_variables": variables,
        "producer_to_pair_clauses": producer_to_pair,
        "pair_to_coverage_clauses": pair_to_coverage,
        "coverage_to_form_clauses": coverage_to_form,
        "driver_dependency_clauses": dependency_clauses,
        "incremental_clauses": clauses,
    }


def encode_factorized_target(
    graph: FactorizedBusTarget,
    arrival_ready_slices: list[tuple[int, dict[int, int]]],
    new_variable: Callable[[tuple[object, ...]], int],
) -> tuple[int | None, list[list[int]]]:
    """Emit the exact existential path encoding used by the design.

    Each slice consists of the target-arrival literal and one ready-by-deadline
    literal per possible dependency.  The caller supplies the surrounding
    producer/arrival exclusivity and cost constraints.
    """

    if not graph.compatible_coverage_pairs:
        return None, []

    clauses: list[list[int]] = []
    producer = new_variable(("factor_bus", graph.target))
    pair_vars = {
        pair: new_variable(("factor_pair", graph.target, *pair))
        for pair in graph.compatible_coverage_pairs
    }
    base_coverage_vars = {
        coverage: new_variable(("factor_base_coverage", graph.target, coverage))
        for coverage, _forms in graph.base_by_coverage
    }
    mixed_coverage_vars = {
        coverage: new_variable(("factor_mixed_coverage", graph.target, coverage))
        for coverage, _forms in graph.mixed_by_coverage
    }
    base_form_vars = {
        (coverage, index): new_variable(
            ("factor_base_form", graph.target, coverage, index)
        )
        for coverage, forms in graph.base_by_coverage
        for index in range(len(forms))
    }
    mixed_form_vars = {
        (coverage, index): new_variable(
            ("factor_mixed_form", graph.target, coverage, index)
        )
        for coverage, forms in graph.mixed_by_coverage
        for index in range(len(forms))
    }

    clauses.append([-producer, *pair_vars.values()])
    for (base_coverage, mixed_coverage), pair_var in pair_vars.items():
        clauses.append([-pair_var, base_coverage_vars[base_coverage]])
        clauses.append([-pair_var, mixed_coverage_vars[mixed_coverage]])

    for coverage, forms in graph.base_by_coverage:
        form_vars = [base_form_vars[(coverage, index)] for index in range(len(forms))]
        clauses.append([-base_coverage_vars[coverage], *form_vars])
        for index, driver in enumerate(forms):
            form_var = base_form_vars[(coverage, index)]
            for arrival_literal, ready in arrival_ready_slices:
                for dependency in set(driver):
                    clauses.append(
                        [-form_var, -arrival_literal, ready[dependency]]
                    )

    for coverage, forms in graph.mixed_by_coverage:
        form_vars = [mixed_form_vars[(coverage, index)] for index in range(len(forms))]
        clauses.append([-mixed_coverage_vars[coverage], *form_vars])
        for index, driver in enumerate(forms):
            form_var = mixed_form_vars[(coverage, index)]
            for arrival_literal, ready in arrival_ready_slices:
                for dependency in set(driver):
                    clauses.append(
                        [-form_var, -arrival_literal, ready[dependency]]
                    )
    return producer, clauses
