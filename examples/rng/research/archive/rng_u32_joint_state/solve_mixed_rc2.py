"""Exact weighted MaxSAT solver for the natural depth-two XOR2/XOR3 DAG.

The hard single-U32 theorem in ``verify_hard_u32.py`` forces the 32-bit state
map to be the natural xorshift matrix when there is no extra first-output phase
state.  This script therefore minimizes a complete depth-two linear network
for those 32 rows using the reviewed primitives:

* XOR2: 3 gate, 2 delay;
* XOR3: 12 gate, 2 delay.

First-level XOR2/XOR3 forms may be shared by any outputs.  Every output may be
a direct first-level form or one final XOR2/XOR3 over inputs/first-level forms.
Overlap and cancellation are included.  No save or game modules are imported.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time
from typing import Any


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import search_depth2_mixed as mixed  # noqa: E402


DEFAULT_OUTPUT = HERE / "mixed_rc2_certificate.json"


def build_minimal_options() -> tuple[
    dict[int, int], list[dict[int, tuple[tuple[int, ...], ...]]]
]:
    sources, primary_cost = mixed.forms()
    minimal: list[dict[int, tuple[tuple[int, ...], ...]]] = []
    for output, row in enumerate(mixed.target_rows()):
        options = mixed.enumerate_options(row, sources, primary_cost)
        entry = {
            cost: mixed.minimal_requirements(options, cost)
            for cost in (0, 3, 12)
        }
        entry[12] = mixed.remove_xor3_dominated_by_xor2(
            entry[3], entry[12], primary_cost
        )
        if not any(entry.values()):
            raise AssertionError(f"output {output} has no depth-two option")
        minimal.append(entry)
    return primary_cost, minimal


def option_records(
    minimal: list[dict[int, tuple[tuple[int, ...], ...]]],
) -> list[list[tuple[int, tuple[int, ...]]]]:
    return [
        [
            (cost, required)
            for cost in (0, 3, 12)
            for required in entry[cost]
        ]
        for entry in minimal
    ]


def solve(output: Path, solver_name: str, verbose: int) -> None:
    try:
        from pysat.examples.rc2 import RC2Stratified
        from pysat.formula import IDPool, WCNF
    except ImportError as error:  # pragma: no cover - optional research dependency
        raise SystemExit("requires python-sat") from error

    started = time.perf_counter()
    primary_cost, minimal = build_minimal_options()
    records = option_records(minimal)
    built_s = time.perf_counter() - started

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
    option_var: list[list[int]] = []
    wcnf = WCNF()

    for value, variable in form_var.items():
        gate_cost = primary_cost[value]
        if gate_cost % 3:
            raise AssertionError("primitive cost is not divisible by three")
        wcnf.append([-variable], weight=gate_cost // 3)

    for output_index, output_records in enumerate(records):
        variables = []
        for option_index, (final_cost, required) in enumerate(output_records):
            variable = pool.id(("option", output_index, option_index))
            variables.append(variable)
            for value in required:
                wcnf.append([-variable, form_var[value]])
            if final_cost:
                if final_cost % 3:
                    raise AssertionError("final cost is not divisible by three")
                wcnf.append([-variable], weight=final_cost // 3)
        wcnf.append(variables)
        option_var.append(variables)

    print(
        f"built_s={built_s:.3f} forms={len(used_forms)} "
        f"options={sum(map(len, records))} vars={pool.top} "
        f"hard={len(wcnf.hard)} soft={len(wcnf.soft)}",
        flush=True,
    )

    solve_started = time.perf_counter()
    with RC2Stratified(
        wcnf,
        solver=solver_name,
        adapt=True,
        exhaust=True,
        minz=True,
        verbose=verbose,
    ) as rc2:
        model = rc2.compute()
        optimum_units = rc2.cost
        oracle_time = rc2.oracle_time()
    solve_s = time.perf_counter() - solve_started
    if model is None:
        raise AssertionError("hard option model is unexpectedly UNSAT")
    true_variables = {literal for literal in model if literal > 0}

    selected_options: list[tuple[int, tuple[int, ...]]] = []
    for output_index, variables in enumerate(option_var):
        selected_indices = [
            index for index, variable in enumerate(variables) if variable in true_variables
        ]
        if not selected_indices:
            raise AssertionError(f"output {output_index} has no selected option")
        selected_options.append(records[output_index][selected_indices[0]])

    selected_forms = sorted(
        {value for _cost, required in selected_options for value in required}
    )
    reconstructed_gate = sum(primary_cost[value] for value in selected_forms) + sum(
        cost for cost, _required in selected_options
    )
    if reconstructed_gate != optimum_units * 3:
        raise AssertionError(
            f"canonical model costs {reconstructed_gate}, RC2 reports {optimum_units * 3}"
        )

    certificate: dict[str, Any] = {
        "schema": 1,
        "model": "complete natural-state depth-two XOR2/XOR3 cover",
        "solver": solver_name,
        "cost_unit_gate": 3,
        "optimum_cost_units": optimum_units,
        "optimum_gate_cost": optimum_units * 3,
        "target_gate_cost": 201,
        "target_met": optimum_units * 3 <= 201,
        "combination_delay": 4,
        "build_seconds": built_s,
        "solve_seconds": solve_s,
        "oracle_seconds": oracle_time,
        "target_rows": [f"{row:08x}" for row in mixed.target_rows()],
        "selected_first_forms": [
            {
                "form": f"{value:08x}",
                "arity": value.bit_count(),
                "gate_cost": primary_cost[value],
            }
            for value in selected_forms
        ],
        "outputs": [
            {
                "index": index,
                "target": f"{mixed.target_rows()[index]:08x}",
                "final_gate_cost": cost,
                "required_first_forms": [f"{value:08x}" for value in required],
            }
            for index, (cost, required) in enumerate(selected_options)
        ],
        "encoding_counts": {
            "candidate_first_form_count": len(used_forms),
            "candidate_option_count": sum(map(len, records)),
            "selected_first_form_count": len(selected_forms),
            "hard_clause_count": len(wcnf.hard),
            "soft_clause_count": len(wcnf.soft),
        },
    }
    verify_certificate(certificate)
    output.write_text(json.dumps(certificate, indent=2) + "\n", encoding="utf-8")
    print(
        f"optimum_gate={certificate['optimum_gate_cost']} "
        f"target_met={certificate['target_met']} solve_s={solve_s:.3f}",
        flush=True,
    )
    print(f"wrote {output}", flush=True)


def verify_certificate(certificate: dict[str, Any]) -> None:
    if certificate.get("schema") != 1:
        raise AssertionError("unsupported certificate schema")
    if certificate.get("model") != "complete natural-state depth-two XOR2/XOR3 cover":
        raise AssertionError("model changed")
    rows = mixed.target_rows()
    if certificate.get("target_rows") != [f"{row:08x}" for row in rows]:
        raise AssertionError("target matrix changed")

    primary_cost, minimal = build_minimal_options()
    records = option_records(minimal)
    selected_forms = {
        int(entry["form"], 16) for entry in certificate["selected_first_forms"]
    }
    if len(selected_forms) != len(certificate["selected_first_forms"]):
        raise AssertionError("duplicate selected first form")
    for entry in certificate["selected_first_forms"]:
        value = int(entry["form"], 16)
        if value not in primary_cost:
            raise AssertionError("selected form is not a legal first-level primitive")
        if entry["arity"] != value.bit_count() or entry["gate_cost"] != primary_cost[value]:
            raise AssertionError("selected form metadata changed")

    outputs = certificate["outputs"]
    if len(outputs) != mixed.BITS:
        raise AssertionError("certificate does not cover all outputs")
    used_forms: set[int] = set()
    final_gate_cost = 0
    for index, entry in enumerate(outputs):
        if entry["index"] != index or entry["target"] != f"{rows[index]:08x}":
            raise AssertionError("output identity changed")
        cost = int(entry["final_gate_cost"])
        required = tuple(int(value, 16) for value in entry["required_first_forms"])
        if (cost, required) not in records[index]:
            raise AssertionError(f"output {index} option is not in the exact option set")
        if not set(required) <= selected_forms:
            raise AssertionError(f"output {index} references an unselected first form")
        used_forms.update(required)
        final_gate_cost += cost
    if used_forms != selected_forms:
        raise AssertionError("selected first-form set is not exact")

    gate_cost = final_gate_cost + sum(primary_cost[value] for value in selected_forms)
    if gate_cost != certificate["optimum_gate_cost"]:
        raise AssertionError("gate cost mismatch")
    if gate_cost != certificate["optimum_cost_units"] * certificate["cost_unit_gate"]:
        raise AssertionError("cost-unit mismatch")
    if certificate["target_met"] != (gate_cost <= certificate["target_gate_cost"]):
        raise AssertionError("target comparison mismatch")
    if certificate["combination_delay"] != 4:
        raise AssertionError("depth-two delay changed")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--verbose", type=int, default=1)
    parser.add_argument("--verify-existing", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.verify_existing is not None:
        certificate = json.loads(args.verify_existing.read_text(encoding="utf-8"))
        verify_certificate(certificate)
        print(f"verified {args.verify_existing}")
        return
    solve(args.output, args.solver, args.verbose)


if __name__ == "__main__":
    main()
