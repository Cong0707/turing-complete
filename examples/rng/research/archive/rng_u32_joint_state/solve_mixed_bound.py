"""Decide a gate bound for the complete depth-two XOR2/XOR3 cover.

The encoding is equivalent to ``solve_mixed_rc2.py`` but asks a single bound
through a native AtMostK constraint.  Costs are divided by three:

* XOR2 has weight 1;
* XOR3 has weight 4;
* the 201-gate target is weight 67.

Two independent native-cardinality SAT backends are used by default.  The
formula includes every cancellation-aware option from the exact mixed model.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import time
from typing import Any


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import search_depth2_mixed as mixed  # noqa: E402
from solve_mixed_rc2 import build_minimal_options, option_records  # noqa: E402


DEFAULT_OUTPUT = HERE / "mixed_bound_201.json"


def build_formula(bound_gate: int):
    try:
        from pysat.formula import CNFPlus, IDPool
    except ImportError as error:  # pragma: no cover
        raise SystemExit("requires python-sat") from error
    if bound_gate % 3:
        raise ValueError("gate bound must be divisible by three")

    primary_cost, minimal = build_minimal_options()
    records = option_records(minimal)
    used_forms = sorted(
        {
            value
            for output_records in records
            for _cost, required in output_records
            for value in required
        }
    )
    pool = IDPool()
    form_var = {value: pool.id(("form", value)) for value in used_forms}
    type_var: dict[tuple[int, int], int] = {}
    selector_records: list[tuple[int, int, tuple[int, ...], int]] = []
    formula = CNFPlus()

    for output, output_records in enumerate(records):
        costs = sorted({cost for cost, _required in output_records})
        type_variables = []
        for cost in costs:
            variable = pool.id(("type", output, cost))
            type_var[(output, cost)] = variable
            type_variables.append(variable)
        formula.append(type_variables)
        for left_index, left in enumerate(type_variables):
            for right in type_variables[left_index + 1 :]:
                formula.append([-left, -right])

        selectors = []
        for option_index, (final_cost, required) in enumerate(output_records):
            selector = pool.id(("option", output, option_index))
            selectors.append(selector)
            selector_records.append((output, final_cost, required, selector))
            formula.append([-selector, type_var[(output, final_cost)]])
            for value in required:
                formula.append([-selector, form_var[value]])
        formula.append(selectors)
        # Multiple decompositions for one physical output never help: keeping
        # one selected option can only remove form requirements and cost.
        # The native AtMost1 removes a large amount of selector symmetry.
        formula.append([selectors, 1], is_atmost=True)

    cost_literals = []
    for value, variable in form_var.items():
        units = primary_cost[value] // 3
        cost_literals.extend([variable] * units)
    for (_output, final_cost), variable in type_var.items():
        units = final_cost // 3
        cost_literals.extend([variable] * units)
    formula.append([cost_literals, bound_gate // 3], is_atmost=True)

    metadata = {
        "primary_cost": primary_cost,
        "records": records,
        "used_forms": used_forms,
        "form_var": form_var,
        "type_var": type_var,
        "selector_records": selector_records,
        "variable_count": pool.top,
        "hard_clause_count": len(formula.clauses),
        "native_atmost_count": len(formula.atmosts),
        "cost_literal_count": len(cost_literals),
        "candidate_option_count": sum(map(len, records)),
    }
    return formula, metadata


def formula_digest(formula) -> str:
    digest = sha256()
    for clause in formula.clauses:
        digest.update(" ".join(map(str, clause)).encode("ascii"))
        digest.update(b" 0\n")
    for literals, bound in formula.atmosts:
        digest.update(b"atmost ")
        digest.update(str(bound).encode("ascii"))
        digest.update(b" ")
        digest.update(" ".join(map(str, literals)).encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def extract_sat_model(
    model: list[int], metadata: dict[str, Any], bound_gate: int
) -> dict[str, Any]:
    positive = {literal for literal in model if literal > 0}
    primary_cost = metadata["primary_cost"]
    selected_forms = sorted(
        value for value, variable in metadata["form_var"].items() if variable in positive
    )
    selected_types = {
        output: cost
        for (output, cost), variable in metadata["type_var"].items()
        if variable in positive
    }
    selected_options = []
    for output, final_cost, required, selector in metadata["selector_records"]:
        if selector in positive:
            selected_options.append(
                {
                    "output": output,
                    "final_gate_cost": final_cost,
                    "required_first_forms": [f"{value:08x}" for value in required],
                }
            )
    gate_cost = sum(primary_cost[value] for value in selected_forms) + sum(
        selected_types.values()
    )
    if gate_cost > bound_gate:
        raise AssertionError("SAT model exceeds requested bound")
    return {
        "gate_cost": gate_cost,
        "selected_first_forms": [f"{value:08x}" for value in selected_forms],
        "selected_final_types": {str(key): value for key, value in selected_types.items()},
        "selected_options": selected_options,
    }


def run(bound_gate: int, solvers: list[str], output: Path) -> dict[str, Any]:
    try:
        from pysat.solvers import Solver
    except ImportError as error:  # pragma: no cover
        raise SystemExit("requires python-sat") from error

    build_started = time.perf_counter()
    formula, metadata = build_formula(bound_gate)
    build_seconds = time.perf_counter() - build_started
    digest = formula_digest(formula)
    print(
        f"built_s={build_seconds:.3f} vars={metadata['variable_count']} "
        f"clauses={metadata['hard_clause_count']} "
        f"options={metadata['candidate_option_count']} "
        f"cost_literals={metadata['cost_literal_count']} sha256={digest}",
        flush=True,
    )

    results = []
    sat_payload = None
    for solver_name in solvers:
        started = time.perf_counter()
        with Solver(name=solver_name, bootstrap_with=formula) as solver:
            status = solver.solve()
            model = solver.get_model() if status else None
            stats = solver.accum_stats()
        elapsed = time.perf_counter() - started
        result = {
            "solver": solver_name,
            "status": "sat" if status else "unsat",
            "seconds": elapsed,
            "stats": stats,
        }
        results.append(result)
        print(f"{solver_name}: {result['status']} in {elapsed:.3f}s", flush=True)
        if status:
            sat_payload = extract_sat_model(model, metadata, bound_gate)

    statuses = {result["status"] for result in results}
    if len(statuses) != 1:
        raise AssertionError(f"solver disagreement: {results}")
    payload: dict[str, Any] = {
        "schema": 1,
        "model": "complete natural-state depth-two XOR2/XOR3 cover",
        "bound_gate": bound_gate,
        "bound_cost_units": bound_gate // 3,
        "combination_delay": 4,
        "result": results[0]["status"],
        "solver_results": results,
        "formula": {
            "sha256": digest,
            "variables": metadata["variable_count"],
            "hard_clauses": metadata["hard_clause_count"],
            "native_atmost_constraints": metadata["native_atmost_count"],
            "cost_literals": metadata["cost_literal_count"],
            "candidate_first_forms": len(metadata["used_forms"]),
            "candidate_options": metadata["candidate_option_count"],
            "build_seconds": build_seconds,
        },
        "target_rows": [f"{row:08x}" for row in mixed.target_rows()],
    }
    if sat_payload is not None:
        payload["sat_model"] = sat_payload
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {output}", flush=True)
    return payload


def verify_existing(path: Path, rerun: bool) -> None:
    certificate = json.loads(path.read_text(encoding="utf-8"))
    if certificate.get("schema") != 1:
        raise AssertionError("unsupported certificate schema")
    if certificate.get("model") != "complete natural-state depth-two XOR2/XOR3 cover":
        raise AssertionError("model changed")
    if certificate.get("target_rows") != [f"{row:08x}" for row in mixed.target_rows()]:
        raise AssertionError("target matrix changed")
    bound_gate = int(certificate["bound_gate"])
    formula, metadata = build_formula(bound_gate)
    expected = {
        "sha256": formula_digest(formula),
        "variables": metadata["variable_count"],
        "hard_clauses": metadata["hard_clause_count"],
        "native_atmost_constraints": metadata["native_atmost_count"],
        "cost_literals": metadata["cost_literal_count"],
        "candidate_first_forms": len(metadata["used_forms"]),
        "candidate_options": metadata["candidate_option_count"],
    }
    for key, value in expected.items():
        if certificate["formula"].get(key) != value:
            raise AssertionError(f"formula field {key} changed")
    if rerun:
        rerun_path = path.with_name(path.stem + ".rerun.json")
        rerun_payload = run(
            bound_gate,
            [entry["solver"] for entry in certificate["solver_results"]],
            rerun_path,
        )
        if rerun_payload["result"] != certificate["result"]:
            raise AssertionError("rerun result changed")
    print(f"verified formula for {path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bound-gate", type=int, default=201)
    parser.add_argument("--solvers", nargs="+", default=["minicard", "gluecard3"])
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--verify-existing", type=Path)
    parser.add_argument("--rerun", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.verify_existing is not None:
        verify_existing(args.verify_existing, args.rerun)
        return
    run(args.bound_gate, args.solvers, args.output)


if __name__ == "__main__":
    main()
