"""Decide a generous shared-enable Switch-XOR3 relaxation at gate 201.

The natural-state theorem fixes the target rows.  This model keeps the complete
two-level linear decomposition family but deliberately undercharges every
XOR3, first-level or final-level, as only four Bit Switches:

* XOR2: 3 gate / 2 delay (the reviewed game cost);
* relaxed XOR3: 8 gate / 2 delay;
* every AND/NOR enable function: free and globally shareable.

Consequently UNSAT is a valid lower bound for every depth-two network made of
XOR2 and the reviewed four-driver XOR3 topology, including arbitrary sharing
of its enable gates.  It is not a proof about arbitrary nonlinear Switch-bus
covers.
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


DEFAULT_OUTPUT = HERE / "relaxed_switch_bound_201.json"
FINAL_COSTS = (0, 3, 8)


def relaxed_options() -> tuple[
    dict[int, int], list[dict[int, tuple[tuple[int, ...], ...]]]
]:
    sources, _atomic_primary = mixed.forms()
    primary_cost = {
        value: 3 if value.bit_count() == 2 else 8
        for value in sources
        if value.bit_count() >= 2
    }
    result: list[dict[int, tuple[tuple[int, ...], ...]]] = []
    for row in mixed.target_rows():
        raw = mixed.enumerate_options(row, sources, _atomic_primary)
        by_cost = {
            0: mixed.minimal_requirements(raw, 0),
            3: mixed.minimal_requirements(raw, 3),
            8: mixed.minimal_requirements(raw, 12),
        }
        reduced: dict[int, tuple[tuple[int, ...], ...]] = {}
        for final_cost in FINAL_COSTS:
            kept = []
            for required in by_cost[final_cost]:
                present = set(required)
                dominated = False
                for alternative_cost in FINAL_COSTS:
                    if alternative_cost >= final_cost:
                        break
                    premium = final_cost - alternative_cost
                    if any(
                        sum(
                            primary_cost[value]
                            for value in alternative
                            if value not in present
                        )
                        <= premium
                        for alternative in by_cost[alternative_cost]
                    ):
                        dominated = True
                        break
                if not dominated:
                    kept.append(required)
            reduced[final_cost] = tuple(kept)
        if not any(reduced.values()):
            raise AssertionError("target row lost every relaxed option")
        result.append(reduced)
    return primary_cost, result


def option_records(
    options: list[dict[int, tuple[tuple[int, ...], ...]]]
) -> list[list[tuple[int, tuple[int, ...]]]]:
    return [
        [
            (cost, required)
            for cost in FINAL_COSTS
            for required in entry[cost]
        ]
        for entry in options
    ]


def build_formula(bound_gate: int):
    try:
        from pysat.formula import CNFPlus, IDPool
    except ImportError as error:  # pragma: no cover
        raise SystemExit("requires python-sat") from error

    primary_cost, options = relaxed_options()
    records = option_records(options)
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
        formula.append([selectors, 1], is_atmost=True)

    cost_literals = []
    for value, variable in form_var.items():
        cost_literals.extend([variable] * primary_cost[value])
    for (output, final_cost), variable in type_var.items():
        del output
        cost_literals.extend([variable] * final_cost)
    formula.append([cost_literals, bound_gate], is_atmost=True)

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
        "options_by_output": [len(value) for value in records],
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


def extract_model(
    model: list[int], metadata: dict[str, Any], bound_gate: int
) -> dict[str, Any]:
    positive = {literal for literal in model if literal > 0}
    selected_forms = sorted(
        value
        for value, variable in metadata["form_var"].items()
        if variable in positive
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
                    "final_gate": final_cost,
                    "required_first_forms": [
                        f"{value:08x}" for value in required
                    ],
                }
            )
    gate = sum(
        metadata["primary_cost"][value] for value in selected_forms
    ) + sum(selected_types.values())
    if gate > bound_gate:
        raise AssertionError("relaxed SAT model exceeds its bound")
    return {
        "gate": gate,
        "selected_first_forms": [f"{value:08x}" for value in selected_forms],
        "selected_final_types": {
            str(output): cost for output, cost in selected_types.items()
        },
        "selected_options": selected_options,
    }


def run(bound_gate: int, solvers: list[str], output: Path) -> dict[str, Any]:
    try:
        from pysat.solvers import Solver
    except ImportError as error:  # pragma: no cover
        raise SystemExit("requires python-sat") from error

    started = time.perf_counter()
    formula, metadata = build_formula(bound_gate)
    build_seconds = time.perf_counter() - started
    digest = formula_digest(formula)
    print(
        f"built_s={build_seconds:.3f} vars={metadata['variable_count']} "
        f"clauses={metadata['hard_clause_count']} "
        f"options={metadata['candidate_option_count']} "
        f"cost_literals={metadata['cost_literal_count']} sha256={digest}",
        flush=True,
    )

    results = []
    sat_model = None
    for solver_name in solvers:
        solve_started = time.perf_counter()
        with Solver(name=solver_name, bootstrap_with=formula) as solver:
            status = solver.solve()
            model = solver.get_model() if status else None
            stats = solver.accum_stats()
        seconds = time.perf_counter() - solve_started
        entry = {
            "solver": solver_name,
            "status": "sat" if status else "unsat",
            "seconds": seconds,
            "stats": stats,
        }
        results.append(entry)
        print(f"{solver_name}: {entry['status']} in {seconds:.3f}s", flush=True)
        if status:
            sat_model = extract_model(model, metadata, bound_gate)
    if len({entry["status"] for entry in results}) != 1:
        raise AssertionError(f"relaxed solver disagreement: {results}")

    payload: dict[str, Any] = {
        "schema": 1,
        "model": "free-shared-enable depth-two XOR2/Switch-XOR3 relaxation",
        "scope": (
            "XOR3 costs only four Bit Switches; all XOR3 enable gates are "
            "free and globally shared; arbitrary nonlinear Switch covers excluded"
        ),
        "bound_gate": bound_gate,
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
            "options_by_output": metadata["options_by_output"],
            "build_seconds": build_seconds,
        },
        "target_rows": [f"{row:08x}" for row in mixed.target_rows()],
    }
    if sat_model is not None:
        payload["sat_model"] = sat_model
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="ascii")
    print(f"wrote {output}", flush=True)
    return payload


def verify_existing(path: Path) -> None:
    certificate = json.loads(path.read_text(encoding="utf-8"))
    if certificate.get("schema") != 1:
        raise AssertionError("unsupported certificate schema")
    if certificate.get("target_rows") != [
        f"{row:08x}" for row in mixed.target_rows()
    ]:
        raise AssertionError("target matrix changed")
    formula, metadata = build_formula(int(certificate["bound_gate"]))
    expected = {
        "sha256": formula_digest(formula),
        "variables": metadata["variable_count"],
        "hard_clauses": metadata["hard_clause_count"],
        "native_atmost_constraints": metadata["native_atmost_count"],
        "cost_literals": metadata["cost_literal_count"],
        "candidate_first_forms": len(metadata["used_forms"]),
        "candidate_options": metadata["candidate_option_count"],
        "options_by_output": metadata["options_by_output"],
    }
    for key, value in expected.items():
        if certificate["formula"].get(key) != value:
            raise AssertionError(f"formula field {key} changed")
    print(f"verified formula for {path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bound-gate", type=int, default=201)
    parser.add_argument("--solvers", nargs="+", default=["minicard", "gluecard3"])
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--verify-existing", type=Path)
    parser.add_argument("--build-only", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.verify_existing is not None:
        verify_existing(args.verify_existing)
        return
    if args.build_only:
        started = time.perf_counter()
        formula, metadata = build_formula(args.bound_gate)
        print(
            json.dumps(
                {
                    "build_seconds": time.perf_counter() - started,
                    "sha256": formula_digest(formula),
                    "variables": metadata["variable_count"],
                    "hard_clauses": metadata["hard_clause_count"],
                    "native_atmost_constraints": metadata["native_atmost_count"],
                    "candidate_options": metadata["candidate_option_count"],
                    "options_by_output": metadata["options_by_output"],
                    "cost_literals": metadata["cost_literal_count"],
                },
                indent=2,
            )
        )
        return
    run(args.bound_gate, args.solvers, args.output)


if __name__ == "__main__":
    main()
