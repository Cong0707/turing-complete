"""Exact SAT audit for four-gate S2/S4 root replacements in the 80/7 DAG.

The current S2 and S4 output roots each own a five-gate private cone.  A live
four-gate ordinary DAG over the retained local signals would therefore produce
a complete 79/7 candidate.  This script encodes all such four-gate DAGs,
including arbitrary internal fanout, instead of limiting the search to formula
trees.

Each synthesized gate is AND, NAND, OR, or NOR.  NOT is included without loss
by tying both inputs of NAND or NOR to the same source.  Source truth values are
projected from every one of the 2^17 Byte Adder assignments.  The projection is
checked to be target-preserving before SAT is invoked.  Structural liveness and
the seven-delay deadline are explicit CNF constraints.

This is an offline research audit and never accesses the formal game save.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any

from pysat.formula import CNF, IDPool
from pysat.solvers import Solver


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DEFAULT_DAG = HERE / "byte-adder-hybrid-phasefold-g80-d7.json"
MATERIALIZER = (
    ROOT / ".research" / "byte_adder_builder_layout_agent" / "materialize_factory_dag.py"
)

TARGET_POOLS = {
    81: (4, 5, 6, 7, 22, 23, 24, 25, 45, 50, 51, 52, 54, 55, 56, 76, 77),
    86: (8, 9, 10, 11, 28, 29, 30, 31, 32, 56, 57, 59, 60, 61, 62, 82, 83),
}
GATE_KINDS = ("AND", "NAND", "OR", "NOR")
DELAY_LIMIT = 7


def load_materializer():
    spec = importlib.util.spec_from_file_location("byte_adder_four_gate_materializer", MATERIALIZER)
    if spec is None or spec.loader is None:
        raise RuntimeError(MATERIALIZER)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def exactly_one(cnf: CNF, literals: list[int]) -> None:
    cnf.append(literals)
    for index, left in enumerate(literals):
        for right in literals[index + 1 :]:
            cnf.append([-left, -right])


def guarded_equivalence(cnf: CNF, guard: int, left: int, right: int) -> None:
    cnf.append([-guard, -left, right])
    cnf.append([-guard, left, -right])


def guarded_constant(cnf: CNF, guard: int, value_var: int, value: bool) -> None:
    cnf.append([-guard, value_var if value else -value_var])


def guarded_gate(
    cnf: CNF,
    guard: int,
    kind: str,
    left: int,
    right: int,
    output: int,
) -> None:
    prefix = [-guard]
    if kind == "AND":
        clauses = ([-left, -right, output], [left, -output], [right, -output])
    elif kind == "NAND":
        clauses = ([-left, -right, -output], [left, output], [right, output])
    elif kind == "OR":
        clauses = ([left, right, -output], [-left, output], [-right, output])
    elif kind == "NOR":
        clauses = ([left, right, output], [-left, -output], [-right, -output])
    else:
        raise ValueError(kind)
    for clause in clauses:
        cnf.append(prefix + clause)


def project(
    source_ids: tuple[int, ...],
    target: int,
    states: dict[int, dict[str, int]],
) -> tuple[list[list[bool]], list[bool]]:
    source_bits = tuple(int(states[node_id]["bits"]) for node_id in source_ids)
    target_bits = int(states[target]["bits"])
    classes: dict[int, bool] = {}
    for row in range(1 << 17):
        vector = 0
        for index, bits in enumerate(source_bits):
            vector |= ((bits >> row) & 1) << index
        value = bool((target_bits >> row) & 1)
        previous = classes.get(vector)
        if previous is not None and previous != value:
            raise RuntimeError(
                f"target {target} is not determined by source vector {vector}"
            )
        classes[vector] = value
    vectors = sorted(classes)
    source_rows = [
        [bool((vector >> index) & 1) for vector in vectors]
        for index in range(len(source_ids))
    ]
    target_row = [classes[vector] for vector in vectors]
    return source_rows, target_row


def build_problem(
    source_ids: tuple[int, ...],
    target: int,
    states: dict[int, dict[str, int]],
    gate_count: int,
) -> tuple[CNF, IDPool, dict[str, Any], list[list[bool]], list[bool]]:
    source_rows, target_row = project(source_ids, target, states)
    rows = len(target_row)
    pool = IDPool()
    cnf = CNF()

    kind_vars = [
        {kind: pool.id(("kind", gate, kind)) for kind in GATE_KINDS}
        for gate in range(gate_count)
    ]
    arrival_vars = [
        {arrival: pool.id(("arrival", gate, arrival)) for arrival in range(1, DELAY_LIMIT + 1)}
        for gate in range(gate_count)
    ]
    output_vars = [
        [pool.id(("output", gate, row)) for row in range(rows)]
        for gate in range(gate_count)
    ]
    input_vars = [
        {
            side: [pool.id(("input", gate, side, row)) for row in range(rows)]
            for side in (0, 1)
        }
        for gate in range(gate_count)
    ]
    selectors: list[dict[int, list[int]]] = []

    for gate in range(gate_count):
        exactly_one(cnf, list(kind_vars[gate].values()))
        exactly_one(cnf, list(arrival_vars[gate].values()))
        candidates = len(source_ids) + gate
        gate_selectors = {
            side: [pool.id(("select", gate, side, candidate)) for candidate in range(candidates)]
            for side in (0, 1)
        }
        selectors.append(gate_selectors)
        exactly_one(cnf, gate_selectors[0])
        exactly_one(cnf, gate_selectors[1])

        for side in (0, 1):
            for candidate, selector in enumerate(gate_selectors[side]):
                if candidate < len(source_ids):
                    source = source_rows[candidate]
                    for row, value in enumerate(source):
                        guarded_constant(cnf, selector, input_vars[gate][side][row], value)
                    source_arrival = int(states[source_ids[candidate]]["depth"])
                    for arrival in range(1, source_arrival + 1):
                        cnf.append([-selector, -arrival_vars[gate][arrival]])
                else:
                    previous_gate = candidate - len(source_ids)
                    for row in range(rows):
                        guarded_equivalence(
                            cnf,
                            selector,
                            input_vars[gate][side][row],
                            output_vars[previous_gate][row],
                        )
                    for previous_arrival in range(1, DELAY_LIMIT + 1):
                        for current_arrival in range(1, previous_arrival + 1):
                            cnf.append(
                                [
                                    -selector,
                                    -arrival_vars[previous_gate][previous_arrival],
                                    -arrival_vars[gate][current_arrival],
                                ]
                            )

        for row in range(rows):
            for kind, guard in kind_vars[gate].items():
                guarded_gate(
                    cnf,
                    guard,
                    kind,
                    input_vars[gate][0][row],
                    input_vars[gate][1][row],
                    output_vars[gate][row],
                )

    # Every non-root synthesized gate must feed at least one later gate.  In a
    # topological four-node graph this condition is equivalent to all nodes
    # belonging to the final gate's backward slice.
    for previous_gate in range(gate_count - 1):
        candidate = len(source_ids) + previous_gate
        uses = []
        for later_gate in range(previous_gate + 1, gate_count):
            uses.extend(
                [selectors[later_gate][0][candidate], selectors[later_gate][1][candidate]]
            )
        cnf.append(uses)

    for row, value in enumerate(target_row):
        cnf.append([output_vars[-1][row] if value else -output_vars[-1][row]])

    variables = {
        "kind": kind_vars,
        "arrival": arrival_vars,
        "selectors": selectors,
        "outputs": output_vars,
    }
    return cnf, pool, variables, source_rows, target_row


def apply_gate(kind: str, left: int, right: int, mask: int) -> int:
    if kind == "AND":
        return left & right
    if kind == "NAND":
        return ~(left & right) & mask
    if kind == "OR":
        return left | right
    if kind == "NOR":
        return ~(left | right) & mask
    raise ValueError(kind)


def solve_target(
    source_ids: tuple[int, ...],
    target: int,
    states: dict[int, dict[str, int]],
    gate_count: int,
    solver_name: str,
) -> dict[str, Any]:
    cnf, pool, variables, source_rows, target_row = build_problem(
        source_ids, target, states, gate_count
    )
    with Solver(name=solver_name, bootstrap_with=cnf.clauses) as solver:
        sat = solver.solve()
        model = set(literal for literal in (solver.get_model() or ()) if literal > 0)

    result: dict[str, Any] = {
        "target": target,
        "source_ids": list(source_ids),
        "compressed_truth_rows": len(target_row),
        "gate_count": gate_count,
        "delay_limit": DELAY_LIMIT,
        "cnf_variables": pool.top,
        "cnf_clauses": len(cnf.clauses),
        "solver": solver_name,
        "status": "sat" if sat else "unsat",
    }
    if not sat:
        return result

    decoded = []
    compact_mask = (1 << len(target_row)) - 1
    compact_values = [
        sum(int(value) << row for row, value in enumerate(source)) for source in source_rows
    ]
    full_values = [int(states[node_id]["bits"]) for node_id in source_ids]
    full_mask = (1 << (1 << 17)) - 1
    compact_gate_values = []
    full_gate_values = []
    actual_arrivals = []
    used_previous = set()
    for gate in range(gate_count):
        kind = next(
            kind for kind, variable in variables["kind"][gate].items() if variable in model
        )
        selected = []
        for side in (0, 1):
            selected.append(
                next(
                    candidate
                    for candidate, variable in enumerate(variables["selectors"][gate][side])
                    if variable in model
                )
            )
        source_count = len(source_ids)

        def value(candidate: int, compact: bool) -> int:
            if candidate < source_count:
                return (compact_values if compact else full_values)[candidate]
            previous = candidate - source_count
            used_previous.add(previous)
            return (compact_gate_values if compact else full_gate_values)[previous]

        compact_output = apply_gate(
            kind, value(selected[0], True), value(selected[1], True), compact_mask
        )
        full_output = apply_gate(
            kind, value(selected[0], False), value(selected[1], False), full_mask
        )
        compact_gate_values.append(compact_output)
        full_gate_values.append(full_output)

        def arrival(candidate: int) -> int:
            if candidate < source_count:
                return int(states[source_ids[candidate]]["depth"])
            return actual_arrivals[candidate - source_count]

        actual_arrival = max(arrival(selected[0]), arrival(selected[1])) + 1
        actual_arrivals.append(actual_arrival)
        decoded.append(
            {
                "gate": gate,
                "kind": kind,
                "inputs": [
                    f"n{source_ids[candidate]}"
                    if candidate < source_count
                    else f"g{candidate - source_count}"
                    for candidate in selected
                ],
                "actual_arrival": actual_arrival,
            }
        )

    compact_target = sum(int(value) << row for row, value in enumerate(target_row))
    if compact_gate_values[-1] != compact_target:
        raise RuntimeError("decoded compact witness does not match target")
    if full_gate_values[-1] != int(states[target]["bits"]):
        raise RuntimeError("decoded witness does not match all 131072 rows")
    if actual_arrivals[-1] > DELAY_LIMIT:
        raise RuntimeError("decoded witness violates delay limit")
    if used_previous != set(range(gate_count - 1)):
        raise RuntimeError("decoded witness has a dead synthesized gate")
    result["witness"] = decoded
    result["full_truth_rows_verified"] = 1 << 17
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dag", type=Path, default=DEFAULT_DAG)
    parser.add_argument("--output", type=Path, default=HERE / "four-gate-dag-sat-80d7.json")
    parser.add_argument("--solver", default="cadical195")
    args = parser.parse_args()

    materializer = load_materializer()
    payload = json.loads(args.dag.read_text(encoding="utf-8"))
    ordered_nodes = tuple(payload["factory_dag"]["nodes"])
    states = materializer.logical_states(ordered_nodes)
    results = []
    for target, source_ids in TARGET_POOLS.items():
        four_gate = solve_target(source_ids, target, states, 4, args.solver)
        five_gate = solve_target(source_ids, target, states, 5, args.solver)
        if five_gate["status"] != "sat" or five_gate.get("full_truth_rows_verified") != 1 << 17:
            raise RuntimeError(f"target {target} five-gate positive regression failed")
        results.append(
            {
                "target": target,
                "four_gate_audit": four_gate,
                "five_gate_positive_regression": five_gate,
            }
        )
    result = {
        "schema": "byte-adder-80d7-four-gate-root-dag-sat-v1",
        "source": str(args.dag.resolve()),
        "full_truth_rows": 1 << 17,
        "private_gate_cost": 5,
        "replacement_gate_cost": 4,
        "ordinary_kinds": ["AND", "NAND", "OR", "NOR", "NOT via tied NAND/NOR"],
        "targets": results,
        "status": (
            "sat"
            if any(item["four_gate_audit"]["status"] == "sat" for item in results)
            else "unsat-with-positive-regressions"
        ),
        "scope": (
            "all live four-gate ordinary DAGs over each explicit retained local source pool, "
            "with internal fanout and delay<=7"
        ),
        "limitations": [
            "does not include Switch or XOR mixtures",
            "does not change sources outside the explicit retained local pool",
            "not a global 79/7 lower bound",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
