"""Z3 models for XOR3 substitution and exact synchronous retiming.

There are two deliberately separate models:

* ``cycle_mean`` only constrains the average delay of state-dependency cycles.
  It is a necessary relaxation and gives 9 / 17 substitutions for P=6 / P=5.
* ``exact_retiming`` builds every conditional edge of the transformed gate
  DAG.  Integer retiming labels and arrival times constrain every zero-register
  path.  It gives the real relaxed-I/O retiming minima 11 / 17.

The exact model leaves primary-output phase unconstrained.  This is favorable
to the proposed construction: adding strict per-tick I/O anchors can only make
the feasible set smaller, so the reported gate minima remain valid lower
bounds for the RNG task.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import argparse
import json
from pathlib import Path
from typing import Iterable

from z3 import (
    And,
    AtMost,
    Bool,
    BoolVal,
    If,
    Implies,
    Int,
    Not,
    Optimize,
    Or,
    Solver,
    Sum,
    is_true,
    sat,
)

from verify_certificate import GATES, OUTPUTS, physical_paths, verify as verify_cycle_certificate


XOR2_GATE = 3
XOR3_GATE = 12
DELAY_BIT_GATE = 5
STATE_BITS = 32
# 32 steady-state seed ORs + ready Delay Bit + ready NOT.
FIXED_GATE = 32 + 5 + 1

CANDIDATES = tuple(
    (child, parent)
    for child, inputs in GATES.items()
    for parent in inputs
    if parent in GATES
)
CANDIDATES_BY_CHILD: defaultdict[str, list[str]] = defaultdict(list)
for child, parent in CANDIDATES:
    CANDIDATES_BY_CHILD[child].append(parent)


# Exact-retiming witnesses.  A child occurs at most once; the same parent may
# be expanded at several consumers, which means several physically distinct
# XOR3 gates and is implementable.
P6_WITNESS = frozenset(
    {
        ("b18", "a18"),
        ("b19", "a2"),
        ("b21", "a4"),
        ("b22", "a5"),
        ("b24", "a7"),
        ("b26", "a9"),
        ("b27", "a10"),
        ("b29", "a12"),
        ("y12", "b17"),
        ("y17", "b17"),
        ("y25", "b30"),
    }
)
P5_WITNESS = frozenset(
    {
        ("b19", "a2"),
        ("b20", "a3"),
        ("b21", "a4"),
        ("b22", "a5"),
        ("b23", "a6"),
        ("b24", "a7"),
        ("b25", "a8"),
        ("b26", "a9"),
        ("b27", "a10"),
        ("b29", "a12"),
        ("y12", "b17"),
        ("y13", "b18"),
        ("y17", "b17"),
        ("y18", "b18"),
        ("y23", "b28"),
        ("y25", "b30"),
        ("y26", "b31"),
    }
)


def transformed_inputs(
    substitutions: frozenset[tuple[str, str]],
) -> dict[str, tuple[str, ...]]:
    by_child: defaultdict[str, list[str]] = defaultdict(list)
    for child, parent in substitutions:
        assert (child, parent) in CANDIDATES
        by_child[child].append(parent)
    assert all(len(parents) <= 1 for parents in by_child.values())

    result: dict[str, tuple[str, ...]] = {}
    for child, original in GATES.items():
        if child not in by_child:
            result[child] = original
            continue
        parent = by_child[child][0]
        other = original[1] if original[0] == parent else original[0]
        expanded = (*GATES[parent], other)
        assert len(set(expanded)) == 3
        result[child] = expanded
    return result


def reachable_gates(inputs: dict[str, tuple[str, ...]]) -> frozenset[str]:
    reachable: set[str] = set()
    stack = list(OUTPUTS)
    while stack:
        node = stack.pop()
        if node not in GATES or node in reachable:
            continue
        reachable.add(node)
        stack.extend(inputs[node])
    return frozenset(reachable)


def form(node: str, inputs: dict[str, tuple[str, ...]], memo: dict[str, int]) -> int:
    if node.startswith("x"):
        return 1 << int(node[1:])
    if node not in memo:
        value = 0
        for source in inputs[node]:
            value ^= form(source, inputs, memo)
        memo[node] = value
    return memo[node]


def verify_transformation(substitutions: frozenset[tuple[str, str]]) -> dict[str, object]:
    inputs = transformed_inputs(substitutions)
    reachable = reachable_gates(inputs)
    original_rows = tuple(form(output, GATES, {}) for output in OUTPUTS)
    transformed_rows = tuple(form(output, inputs, {}) for output in OUTPUTS)
    assert transformed_rows == original_rows
    active_substitutions = frozenset(
        pair for pair in substitutions if pair[0] in reachable
    )
    assert active_substitutions == substitutions
    original_consumers: defaultdict[str, list[str]] = defaultdict(list)
    for child, sources in GATES.items():
        for source in sources:
            original_consumers[source].append(child)
    for bit, output in enumerate(OUTPUTS):
        original_consumers[output].append(f"OUT{bit}")

    replacement_audit = []
    for child, parent in sorted(substitutions):
        parent_alive = parent in reachable
        fanout = len(original_consumers[parent])
        if not parent_alive and fanout == 1:
            category = "single_fanout_parent_deleted_net_plus_6"
        elif parent_alive:
            category = "parent_retained_bypass_net_plus_9"
        else:
            category = "shared_parent_deleted_collectively"
        replacement_audit.append(
            {
                "child": child,
                "parent": parent,
                "parent_original_consumers": sorted(original_consumers[parent]),
                "parent_alive_after_rewrite": parent_alive,
                "category": category,
            }
        )

    dead = sorted(set(GATES) - reachable)
    assert all(any(parent == gate for _, parent in substitutions) for gate in dead)
    xor_cost = sum(
        XOR3_GATE
        if any(child == gate for child, _ in substitutions)
        else XOR2_GATE
        for gate in reachable
    )
    assert xor_cost == len(GATES) * XOR2_GATE + 9 * len(substitutions) - 3 * len(dead)
    return {
        "substitutions": [list(pair) for pair in sorted(substitutions)],
        "substitution_count": len(substitutions),
        "active_xor_gate_count": len(reachable),
        "dead_xor_gates": dead,
        "xor_gate_cost": xor_cost,
        "xor_cost_identity": "183 + 9*XOR3 - 3*dead_parent",
        "replacement_cost_audit": replacement_audit,
        "all_transformed_gates_have_two_or_three_distinct_inputs": all(
            len(inputs[gate]) in (2, 3) and len(set(inputs[gate])) == len(inputs[gate])
            for gate in reachable
        ),
        "gf2_outputs_equal_canonical": True,
    }


def cycle_mean_minimum(period: int) -> tuple[int, list[tuple[str, str]]]:
    """Solve the necessary state-cycle relaxation."""

    optimizer = Optimize()
    selected = {
        pair: Bool(f"cm_{period}_{pair[0]}_{pair[1]}") for pair in CANDIDATES
    }
    for child, parents in CANDIDATES_BY_CHILD.items():
        optimizer.add(AtMost(*(selected[child, parent] for parent in parents), 1))

    potential = [Int(f"cm_h_{period}_{bit}") for bit in range(STATE_BITS)]
    optimizer.add(potential[0] == 0)
    candidate_set = set(CANDIDATES)
    for target, output in enumerate(OUTPUTS):
        for source, chain in physical_paths(output):
            shortening = [
                selected[child, parent]
                for child, parent in zip(chain[1:], chain[:-1])
                if (child, parent) in candidate_set
            ]
            hit = Or(*shortening) if shortening else BoolVal(False)
            path_delay = 1 + 2 * len(chain)
            optimizer.add(
                potential[target]
                >= potential[source] + path_delay - period - If(hit, 2, 0)
            )

    count = Sum(*(If(variable, 1, 0) for variable in selected.values()))
    handle = optimizer.minimize(count)
    assert optimizer.check() == sat
    model = optimizer.model()
    minimum = optimizer.lower(handle).as_long()
    witness = [pair for pair, variable in selected.items() if is_true(model[variable])]
    assert len(witness) == minimum
    return minimum, sorted(witness)


@dataclass(frozen=True)
class ConditionalRetiming:
    optimizer: Optimize
    selected: dict[tuple[str, str], object]
    selection_count: object
    objective_handle: object


def exact_retiming_optimizer(period: int) -> ConditionalRetiming:
    """Build the complete conditional-edge retiming feasibility model."""

    optimizer = Optimize()
    selected = {
        pair: Bool(f"rt_{period}_{pair[0]}_{pair[1]}") for pair in CANDIDATES
    }
    for child, parents in CANDIDATES_BY_CHILD.items():
        optimizer.add(AtMost(*(selected[child, parent] for parent in parents), 1))

    delays: dict[str, int] = {}
    edges: list[tuple[str, str, int, object]] = []
    for bit in range(STATE_BITS):
        delays[f"x{bit}"] = 0
    for child, inputs in GATES.items():
        operation = f"op_{child}"
        delays[operation] = 2
        delays[child] = 0
        for source in inputs:
            if source not in GATES:
                edges.append((source, operation, 0, BoolVal(True)))
                continue
            edges.append((source, operation, 0, Not(selected[child, source])))
            for grandparent in GATES[source]:
                edges.append((grandparent, operation, 0, selected[child, source]))
        edges.append((operation, child, 0, BoolVal(True)))

    for bit, output in enumerate(OUTPUTS):
        operation = f"op_or{bit}"
        signal = f"or{bit}"
        delays[operation] = 1
        delays[signal] = 0
        edges.extend(
            (
                (output, operation, 0, BoolVal(True)),
                (operation, signal, 0, BoolVal(True)),
                (signal, f"x{bit}", 1, BoolVal(True)),
            )
        )

    retiming = {node: Int(f"rt_r_{period}_{node}") for node in delays}
    arrival = {node: Int(f"rt_t_{period}_{node}") for node in delays}
    optimizer.add(retiming["x0"] == 0)
    for node, delay in delays.items():
        optimizer.add(arrival[node] >= delay, arrival[node] <= period)
    for source, target, registers, active in edges:
        retimed = registers + retiming[target] - retiming[source]
        optimizer.add(Implies(active, retimed >= 0))
        optimizer.add(
            Implies(
                And(active, retimed == 0),
                arrival[target] >= arrival[source] + delays[target],
            )
        )

    count = Sum(*(If(variable, 1, 0) for variable in selected.values()))
    handle = optimizer.minimize(count)
    return ConditionalRetiming(optimizer, selected, count, handle)


def exact_retiming_minimum(period: int) -> tuple[int, list[tuple[str, str]]]:
    problem = exact_retiming_optimizer(period)
    assert problem.optimizer.check() == sat
    model = problem.optimizer.model()
    minimum = problem.optimizer.lower(problem.objective_handle).as_long()
    witness = [
        pair
        for pair, variable in problem.selected.items()
        if is_true(model[variable])
    ]
    assert len(witness) == minimum
    return minimum, sorted(witness)


def fixed_retiming(
    period: int, substitutions: frozenset[tuple[str, str]]
) -> dict[str, object]:
    """Minimize physical registers for one concrete transformed netlist."""

    inputs = transformed_inputs(substitutions)
    reachable = reachable_gates(inputs)
    delays: dict[str, int] = {f"x{bit}": 0 for bit in range(STATE_BITS)}
    edges: list[tuple[str, str, int]] = []
    for gate in reachable:
        operation = f"op_{gate}"
        delays[operation] = 2
        delays[gate] = 0
        edges.extend((source, operation, 0) for source in inputs[gate])
        edges.append((operation, gate, 0))
    for bit, output in enumerate(OUTPUTS):
        operation = f"op_or{bit}"
        signal = f"or{bit}"
        delays[operation] = 1
        delays[signal] = 0
        edges.extend(
            (
                (output, operation, 0),
                (operation, signal, 0),
                (signal, f"x{bit}", 1),
            )
        )

    optimizer = Optimize()
    retiming = {node: Int(f"fix_r_{period}_{node}") for node in delays}
    arrival = {node: Int(f"fix_t_{period}_{node}") for node in delays}
    optimizer.add(retiming["x0"] == 0)
    for node, delay in delays.items():
        optimizer.add(arrival[node] >= delay, arrival[node] <= period)
    retimed_edges = []
    for source, target, registers in edges:
        retimed = registers + retiming[target] - retiming[source]
        optimizer.add(retimed >= 0)
        optimizer.add(
            Implies(
                retimed == 0,
                arrival[target] >= arrival[source] + delays[target],
            )
        )
        retimed_edges.append(retimed)
    register_count = Sum(*retimed_edges)
    optimizer.minimize(register_count)
    assert optimizer.check() == sat
    model = optimizer.model()
    count = model.eval(register_count).as_long()
    placements = [
        {"source": source, "target": target, "count": value}
        for (source, target, _), expression in zip(edges, retimed_edges)
        if (value := model.eval(expression).as_long())
    ]
    return {
        "minimum_retimed_state_registers": count,
        "register_placements": placements,
    }


def gate_lower_bound(period: int, minimum_substitutions: int, extra_registers: int) -> dict[str, int]:
    # A live XOR3 costs +9 over its child XOR2.  One substitution can make at
    # most its direct parent dead, saving at most 3, hence net >= +6 each.
    xor_lower_bound = len(GATES) * XOR2_GATE + 6 * minimum_substitutions
    state_register_lower_bound = STATE_BITS + extra_registers
    return {
        "xor_network_gate_lower_bound": xor_lower_bound,
        "state_register_lower_bound": state_register_lower_bound,
        "fixed_control_and_or_gate": FIXED_GATE,
        "total_gate_lower_bound": (
            xor_lower_bound
            + state_register_lower_bound * DELAY_BIT_GATE
            + FIXED_GATE
        ),
        "score_delay_if_delay_bit_is_4": 4 + period,
    }


def solve(run_exact_p6_optimization: bool) -> dict[str, object]:
    certificate = verify_cycle_certificate()
    cycle_minimum_6, cycle_witness_6 = cycle_mean_minimum(6)
    cycle_minimum_5, cycle_witness_5 = cycle_mean_minimum(5)
    assert (cycle_minimum_6, cycle_minimum_5) == (9, 17)

    if run_exact_p6_optimization:
        exact_minimum_6, exact_solver_witness_6 = exact_retiming_minimum(6)
        assert exact_minimum_6 == 11
        verify_transformation(frozenset(exact_solver_witness_6))
    else:
        exact_minimum_6 = 11
        exact_solver_witness_6 = sorted(P6_WITNESS)

    # The disjoint-cycle certificate proves >=17, and this concrete exact
    # retiming witness proves <=17; no second long Optimize call is needed.
    exact_minimum_5 = certificate["xor3_lower_bound_for_period_5"]
    assert exact_minimum_5 == 17

    witness_results = {}
    for period, substitutions in ((6, P6_WITNESS), (5, P5_WITNESS)):
        structure = verify_transformation(substitutions)
        retiming = fixed_retiming(period, substitutions)
        physical_gate = (
            structure["xor_gate_cost"]
            + retiming["minimum_retimed_state_registers"] * DELAY_BIT_GATE
            + FIXED_GATE
        )
        witness_results[str(period)] = {
            **structure,
            **retiming,
            "physical_gate_in_relaxed_io_retiming_model": physical_gate,
        }

    lower_bounds = {
        "period_6_unrestricted_register_count": gate_lower_bound(6, 11, 0),
        "period_5_unrestricted_register_count": gate_lower_bound(5, 17, 0),
        "period_6_with_two_extra_delay_bits": gate_lower_bound(6, 11, 2),
        "period_5_with_four_extra_delay_bits": gate_lower_bound(5, 17, 4),
    }
    assert lower_bounds["period_6_unrestricted_register_count"]["total_gate_lower_bound"] == 447
    assert lower_bounds["period_5_unrestricted_register_count"]["total_gate_lower_bound"] == 483
    assert lower_bounds["period_6_with_two_extra_delay_bits"]["total_gate_lower_bound"] == 457
    assert lower_bounds["period_5_with_four_extra_delay_bits"]["total_gate_lower_bound"] == 503

    return {
        "canonical_model": {
            "xor2_count": len(GATES),
            "xor2_gate_delay": [XOR2_GATE, 2],
            "xor3_gate_delay": [XOR3_GATE, 2],
            "delay_bit_gate_delay": [DELAY_BIT_GATE, 4],
            "steady_state_or_gate_delay": [1, 1],
            "state_bits": STATE_BITS,
            "fixed_gate_outside_xor_and_state": FIXED_GATE,
        },
        "cycle_mean_relaxation": {
            "period_6_minimum_xor3": cycle_minimum_6,
            "period_6_witness": [list(pair) for pair in cycle_witness_6],
            "period_5_minimum_xor3": cycle_minimum_5,
            "period_5_witness": [list(pair) for pair in cycle_witness_5],
            "warning": "necessary cycle-average condition, not full retiming",
        },
        "exact_conditional_edge_retiming": {
            "period_6_minimum_xor3": exact_minimum_6,
            "period_6_solver_witness": [list(pair) for pair in exact_solver_witness_6],
            "period_6_optimize_proof_rerun": run_exact_p6_optimization,
            "period_5_minimum_xor3": exact_minimum_5,
            "period_5_lower_bound_source": "seven disjoint cycle groups",
            "io_phase_constraint": "relaxed (favorable lower-bound model)",
        },
        "implementable_witnesses": witness_results,
        "gate_lower_bounds": lower_bounds,
        "target_421_period_6_possible": False,
        "target_431_period_5_possible": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--prove-p6-minimum",
        action="store_true",
        help="run the ~50 second Optimize proof that exact P6 needs 11 XOR3",
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = solve(args.prove_p6_minimum)
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
