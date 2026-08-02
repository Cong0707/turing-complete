"""Exact streaming-CNF bound for the natural depth-two XOR2/XOR3 model.

Unlike ``solve_mixed_bound.py``, this encoder does not rely on a native
cardinality solver.  It streams a one-way weighted sequential counter directly
into an ordinary SAT backend, avoiding a Python list of roughly a million CNF
clauses.  Costs use units of three game gates:

* XOR2 weight 1;
* reviewed Switch-XOR3 weight 4;
* gate bound 201 becomes weight bound 67.

The option universe is the complete cancellation-aware reduced DNF from
``solve_mixed_rc2.py``.  Every output selects exactly one decomposition.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from hashlib import sha256
import itertools
import json
from pathlib import Path
import sys
import time
from typing import Any, Callable, Iterable


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import search_depth2_mixed as mixed  # noqa: E402
from solve_mixed_rc2 import build_minimal_options, option_records  # noqa: E402
import solve_relaxed_switch_bound as relaxed  # noqa: E402


DEFAULT_OUTPUT = HERE / "mixed_streaming_bound_201.json"


@dataclass
class VariablePool:
    top: int = 0

    def new(self) -> int:
        self.top += 1
        return self.top


class ClauseSink:
    def __init__(self, solver) -> None:
        self.solver = solver
        self.count = 0
        self.digest = sha256()

    def add(self, clause: Iterable[int]) -> None:
        values = tuple(clause)
        if not values:
            raise AssertionError("empty clause emitted unexpectedly")
        self.solver.add_clause(values)
        self.digest.update(" ".join(map(str, values)).encode("ascii"))
        self.digest.update(b" 0\n")
        self.count += 1

    def hexdigest(self) -> str:
        return self.digest.hexdigest()


def weighted_atmost_stream(
    literals: tuple[int, ...],
    weights: tuple[int, ...],
    bound: int,
    new_variable: Callable[[], int],
    add_clause: Callable[[Iterable[int]], None],
) -> int:
    """Encode ``sum(weight_i * literal_i) <= bound``.

    State ``s[i,j]`` is a one-way witness that the selected weight among items
    ``0..i`` is at least ``j``.  The clauses force the exact accumulated-weight
    path for every assignment; auxiliary variables need not be constrained in
    the reverse direction.  Returns the number of auxiliary variables.
    """

    if len(literals) != len(weights):
        raise ValueError("literal/weight length mismatch")
    if bound < 0:
        raise ValueError("negative bound")
    if not literals:
        return 0
    if any(weight <= 0 for weight in weights):
        raise ValueError("weights must be positive")

    previous: list[int] | None = None
    auxiliary = 0
    for literal, weight in zip(literals, weights):
        if weight > bound:
            add_clause((-literal,))
            continue
        current = [new_variable() for _ in range(bound)]
        auxiliary += bound
        # Selecting this item alone reaches its own weight.
        add_clause((-literal, current[weight - 1]))
        if previous is not None:
            # Existing accumulated weights propagate across this item.
            for threshold in range(1, bound + 1):
                add_clause((-previous[threshold - 1], current[threshold - 1]))
            # Selecting the item advances every previously reached weight, or
            # is forbidden when that advance would exceed the bound.
            for threshold in range(1, bound + 1):
                if threshold + weight <= bound:
                    add_clause(
                        (
                            -literal,
                            -previous[threshold - 1],
                            current[threshold + weight - 1],
                        )
                    )
                else:
                    add_clause((-literal, -previous[threshold - 1]))
        previous = current
    return auxiliary


def self_test_counter() -> None:
    try:
        from pysat.solvers import Solver
    except ImportError as error:  # pragma: no cover
        raise SystemExit("requires python-sat") from error

    cases = (
        ((1,), 0),
        ((1, 1), 1),
        ((1, 2, 3), 3),
        ((2, 2, 3, 4), 5),
        ((1, 4, 1, 4, 1), 6),
    )
    for weights, bound in cases:
        with Solver(name="cadical195") as solver:
            pool = VariablePool(len(weights))
            sink = ClauseSink(solver)
            literals = tuple(range(1, len(weights) + 1))
            weighted_atmost_stream(
                literals, weights, bound, pool.new, sink.add
            )
            for assignment in itertools.product((False, True), repeat=len(weights)):
                assumptions = tuple(
                    literal if selected else -literal
                    for literal, selected in zip(literals, assignment)
                )
                actual = solver.solve(assumptions=assumptions)
                expected = sum(
                    weight for weight, selected in zip(weights, assignment) if selected
                ) <= bound
                if actual != expected:
                    raise AssertionError(
                        f"counter mismatch weights={weights} bound={bound} "
                        f"assignment={assignment}: {actual}!={expected}"
                    )
    print("weighted sequential counter self-test: PASS")


def reconstruct_sources(
    target: int, final_cost: int, required: tuple[int, ...]
) -> tuple[int, ...]:
    arity = {0: 1, 3: 2, 8: 3, 12: 3}[final_cost]
    residual = target
    for value in required:
        residual ^= value
    raw = tuple(1 << bit for bit in range(mixed.BITS) if (residual >> bit) & 1)
    sources = tuple(sorted((*required, *raw)))
    if len(sources) != arity or len(set(sources)) != arity:
        raise AssertionError("invalid selected source arity")
    value = 0
    for source in sources:
        value ^= source
    if value != target:
        raise AssertionError("selected sources do not reconstruct target")
    return sources


def build_and_solve(
    solver_name: str, bound_gate: int, xor3_base_gate: int
):
    try:
        from pysat.solvers import Solver
    except ImportError as error:  # pragma: no cover
        raise SystemExit("requires python-sat") from error
    if xor3_base_gate not in (8, 12):
        raise ValueError("XOR3 base gate must be 8 or 12")
    cost_unit_gate = 3 if xor3_base_gate == 12 else 1
    if bound_gate % cost_unit_gate:
        raise ValueError("gate bound is not divisible by the cost unit")

    option_started = time.perf_counter()
    if xor3_base_gate == 12:
        primary_cost, minimal = build_minimal_options()
        records = option_records(minimal)
    else:
        primary_cost, relaxed_options = relaxed.relaxed_options()
        records = relaxed.option_records(relaxed_options)
    option_seconds = time.perf_counter() - option_started
    used_forms = sorted(
        {
            value
            for output_records in records
            for _cost, required in output_records
            for value in required
        }
    )

    pool = VariablePool()
    form_var = {value: pool.new() for value in used_forms}
    type_var: dict[tuple[int, int], int] = {}
    selector_records: list[tuple[int, int, tuple[int, ...], int]] = []
    selector_auxiliary = 0
    formula_started = time.perf_counter()
    with Solver(name=solver_name) as solver:
        sink = ClauseSink(solver)
        for output, output_records in enumerate(records):
            costs = sorted({cost for cost, _required in output_records})
            type_variables = []
            for cost in costs:
                variable = pool.new()
                type_var[(output, cost)] = variable
                type_variables.append(variable)
            sink.add(type_variables)
            for left_index, left in enumerate(type_variables):
                for right in type_variables[left_index + 1 :]:
                    sink.add((-left, -right))

            selectors = []
            for final_cost, required in output_records:
                selector = pool.new()
                selectors.append(selector)
                selector_records.append((output, final_cost, required, selector))
                sink.add((-selector, type_var[(output, final_cost)]))
                for value in required:
                    sink.add((-selector, form_var[value]))
            sink.add(selectors)
            selector_auxiliary += weighted_atmost_stream(
                tuple(selectors),
                tuple(1 for _ in selectors),
                1,
                pool.new,
                sink.add,
            )

        cost_literals = []
        cost_weights = []
        for value, variable in form_var.items():
            cost_literals.append(variable)
            cost_weights.append(primary_cost[value] // cost_unit_gate)
        for (_output, final_cost), variable in type_var.items():
            if final_cost:
                cost_literals.append(variable)
                cost_weights.append(final_cost // cost_unit_gate)
        cost_auxiliary = weighted_atmost_stream(
            tuple(cost_literals),
            tuple(cost_weights),
            bound_gate // cost_unit_gate,
            pool.new,
            sink.add,
        )
        formula_seconds = time.perf_counter() - formula_started
        digest = sink.hexdigest()
        print(
            f"{solver_name}: built option_s={option_seconds:.3f} "
            f"cnf_s={formula_seconds:.3f} vars={pool.top} "
            f"clauses={sink.count} options={len(selector_records)} "
            f"selector_aux={selector_auxiliary} cost_aux={cost_auxiliary} "
            f"sha256={digest}",
            flush=True,
        )

        solve_started = time.perf_counter()
        status = solver.solve()
        solve_seconds = time.perf_counter() - solve_started
        model = solver.get_model() if status else None
        stats = solver.accum_stats()

    result: dict[str, Any] = {
        "solver": solver_name,
        "status": "sat" if status else "unsat",
        "option_build_seconds": option_seconds,
        "cnf_build_seconds": formula_seconds,
        "solve_seconds": solve_seconds,
        "stats": stats,
        "formula": {
            "sha256": digest,
            "variables": pool.top,
            "clauses": sink.count,
            "candidate_first_forms": len(used_forms),
            "candidate_options": len(selector_records),
            "selector_counter_auxiliary": selector_auxiliary,
            "cost_counter_auxiliary": cost_auxiliary,
            "cost_variables": len(cost_literals),
            "cost_bound_units": bound_gate // cost_unit_gate,
            "cost_unit_gate": cost_unit_gate,
            "xor3_base_gate": xor3_base_gate,
        },
    }
    print(
        f"{solver_name}: {result['status']} solve_s={solve_seconds:.3f}",
        flush=True,
    )
    if model is None:
        return result, None

    positive = {literal for literal in model if literal > 0}
    selected_forms = sorted(
        value for value, variable in form_var.items() if variable in positive
    )
    selected_types = {
        output: cost
        for (output, cost), variable in type_var.items()
        if variable in positive
    }
    selected_options = []
    seen_outputs = set()
    for output, final_cost, required, selector in selector_records:
        if selector not in positive:
            continue
        if output in seen_outputs:
            raise AssertionError("counter allowed two options for one output")
        seen_outputs.add(output)
        sources = reconstruct_sources(
            mixed.target_rows()[output], final_cost, required
        )
        selected_options.append(
            {
                "output": output,
                "final_gate_cost": final_cost,
                "required_first_forms": [f"{value:08x}" for value in required],
                "sources": [f"{value:08x}" for value in sources],
            }
        )
    if seen_outputs != set(range(mixed.BITS)):
        raise AssertionError("SAT model does not select every output")
    gate = sum(primary_cost[value] for value in selected_forms) + sum(
        selected_types.values()
    )
    if gate > bound_gate:
        raise AssertionError("SAT model exceeds requested gate bound")
    sat_model = {
        "gate": gate,
        "selected_first_forms": [f"{value:08x}" for value in selected_forms],
        "selected_final_types": {
            str(output): cost for output, cost in selected_types.items()
        },
        "selected_options": sorted(
            selected_options, key=lambda entry: entry["output"]
        ),
    }
    return result, sat_model


def run(
    bound_gate: int,
    solvers: list[str],
    output: Path,
    xor3_base_gate: int,
) -> dict[str, Any]:
    results = []
    sat_models = []
    formula_digest = None
    for solver_name in solvers:
        result, sat_model = build_and_solve(
            solver_name, bound_gate, xor3_base_gate
        )
        if formula_digest is None:
            formula_digest = result["formula"]["sha256"]
        elif result["formula"]["sha256"] != formula_digest:
            raise AssertionError("streamed formula changed between solvers")
        results.append(result)
        if sat_model is not None:
            sat_models.append(sat_model)
    if len({entry["status"] for entry in results}) != 1:
        raise AssertionError(f"solver disagreement: {results}")
    payload: dict[str, Any] = {
        "schema": 1,
        "model": (
            "complete natural-state depth-two XOR2/XOR3 cover"
            if xor3_base_gate == 12
            else "free-shared-enable depth-two XOR2/Switch-XOR3 relaxation"
        ),
        "encoding": "streamed one-way weighted sequential CNF",
        "xor3_base_gate": xor3_base_gate,
        "bound_gate": bound_gate,
        "combination_delay": 4,
        "result": results[0]["status"],
        "solver_results": results,
        "target_rows": [f"{row:08x}" for row in mixed.target_rows()],
    }
    if xor3_base_gate == 8:
        payload["relaxation_scope"] = (
            "Every XOR3 costs only four Bit Switches; all AND/NOR enable "
            "functions are free and globally shareable. Arbitrary nonlinear "
            "Switch covers remain outside this model."
        )
    if sat_models:
        if any(model != sat_models[0] for model in sat_models[1:]):
            payload["sat_models"] = sat_models
        else:
            payload["sat_model"] = sat_models[0]
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="ascii")
    print(f"wrote {output}", flush=True)
    return payload


def verify_existing(path: Path) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != 1:
        raise AssertionError("unsupported certificate schema")
    if data.get("target_rows") != [f"{row:08x}" for row in mixed.target_rows()]:
        raise AssertionError("target rows changed")
    if data.get("encoding") != "streamed one-way weighted sequential CNF":
        raise AssertionError("encoding identity changed")
    print(
        f"certificate metadata verified for {path}; use --solvers to rerun SAT"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bound-gate", type=int, default=201)
    parser.add_argument("--solvers", nargs="+", default=["cadical195"])
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--xor3-base-gate", type=int, choices=(8, 12), default=12)
    parser.add_argument("--verify-existing", type=Path)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.self_test:
        self_test_counter()
        return
    if args.verify_existing is not None:
        verify_existing(args.verify_existing)
        return
    run(args.bound_gate, args.solvers, args.output, args.xor3_base_gate)


if __name__ == "__main__":
    main()
