"""Exact weighted-MaxSAT cover for the shallow encoded RNG candidate."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import time

from pysat.examples.rc2 import RC2Stratified
from pysat.formula import IDPool, WCNF

import solve_mixed_cover as core


def solve(start: Path, memory_mb: int) -> dict[str, object]:
    started = time.perf_counter()
    stopped, peak = core.start_watchdog(memory_mb)
    T, B, C = core.load_last_candidate(start)
    b_options = tuple(core.output_options(row, is_output=False) for row in B)
    c_options = tuple(core.output_options(row, is_output=True) for row in C)
    forms = tuple(
        sorted(
            {
                source
                for rows in (b_options, c_options)
                for options in rows
                for option in options
                for source in option.sources
                if source.bit_count() in (2, 3)
            }
        )
    )

    pool = IDPool()
    formula = WCNF()
    form_var = {form: pool.id(("form", form)) for form in forms}
    option_var: dict[tuple[str, int, int], int] = {}
    users: dict[int, list[int]] = defaultdict(list)
    for kind, rows in (("b", b_options), ("c", c_options)):
        for output, options in enumerate(rows):
            variables = []
            for index, option in enumerate(options):
                variable = pool.id(("option", kind, output, index))
                option_var[kind, output, index] = variable
                variables.append(variable)
                for source in option.sources:
                    if source.bit_count() in (2, 3):
                        formula.append([-variable, form_var[source]])
                        users[source].append(variable)
                if option.final_arity == 2:
                    formula.append([-variable], weight=core.XOR2_COST)
            formula.append(variables)
            for left_index, left in enumerate(variables):
                for right in variables[left_index + 1 :]:
                    formula.append([-left, -right])

    for form, variable in form_var.items():
        cost = core.XOR2_COST if form.bit_count() == 2 else core.XOR3_COST
        formula.append([-variable], weight=cost)
        # Positive form costs already exclude unused forms in every optimum;
        # the reverse implication also makes the certificate structural.
        formula.append([-variable, *users[form]])

    build_seconds = time.perf_counter() - started
    print(
        f"built forms={len(forms)} choices={len(option_var)} vars={pool.top} "
        f"hard={len(formula.hard)} soft={len(formula.soft)}",
        flush=True,
    )
    with RC2Stratified(
        formula,
        solver="cd195",
        adapt=True,
        exhaust=True,
        minz=True,
        trim=2,
        verbose=1,
    ) as solver:
        assignment = solver.compute()
        optimum = solver.cost
    solve_seconds = time.perf_counter() - started - build_seconds
    stopped.set()
    peak[0] = max(peak[0], core.working_set_bytes())
    if assignment is None:
        return {
            "status": "unsat",
            "scope": "exact cancellation-free shallow XOR2/XOR3 steady cover",
            "build_seconds": build_seconds,
            "solve_seconds": solve_seconds,
            "peak_working_set_mb": peak[0] / 1048576,
        }

    positive = {literal for literal in assignment if literal > 0}
    selected_forms = tuple(form for form, variable in form_var.items() if variable in positive)
    outputs: dict[str, list[dict[str, object]]] = {"B": [], "C": []}
    for kind, key, matrix, rows in (
        ("b", "B", B, b_options),
        ("c", "C", C, c_options),
    ):
        for output, options in enumerate(rows):
            active = [
                index
                for index in range(len(options))
                if option_var[kind, output, index] in positive
            ]
            if len(active) != 1:
                raise AssertionError(f"{key}[{output}] has {len(active)} active options")
            option = options[active[0]]
            steady = 0
            for source in option.sources:
                steady ^= source
                if source.bit_count() > 1 and source not in selected_forms:
                    raise AssertionError("output uses an absent first-layer form")
            if steady != matrix[output]:
                raise AssertionError(f"{key}[{output}] steady decomposition mismatch")
            outputs[key].append(
                {
                    "output": output,
                    "target": f"{matrix[output]:08x}",
                    "final_arity": option.final_arity,
                    "sources": [f"{source:08x}" for source in option.sources],
                }
            )

    form_counts = Counter(form.bit_count() for form in selected_forms)
    final_xor2 = sum(
        entry["final_arity"] == 2 for entries in outputs.values() for entry in entries
    )
    recomputed = (
        core.XOR2_COST * (form_counts[2] + final_xor2)
        + core.XOR3_COST * form_counts[3]
    )
    if recomputed != optimum:
        raise AssertionError(f"RC2 cost {optimum} != extracted cost {recomputed}")
    if core.compose(C, T) != core.A or core.compose(T, C) != B:
        raise AssertionError("matrix identity mismatch")

    return {
        "status": "optimal",
        "scope": "exact cancellation-free shallow XOR2/XOR3 steady cover",
        "solver": "RC2Stratified/cd195",
        "build_seconds": build_seconds,
        "solve_seconds": solve_seconds,
        "peak_working_set_mb": peak[0] / 1048576,
        "form_universe": len(forms),
        "choice_count": len(option_var),
        "cover": {
            "T": [f"{row:08x}" for row in T],
            "B": [f"{row:08x}" for row in B],
            "C": [f"{row:08x}" for row in C],
            "selected_first_layer_forms": [f"{form:08x}" for form in selected_forms],
            "outputs": outputs,
            "metrics": {
                "first_xor2": form_counts[2],
                "first_xor3": form_counts[3],
                "final_xor2": final_xor2,
                "xor2": form_counts[2] + final_xor2,
                "xor3": form_counts[3],
                "logic_gate_cost": recomputed,
                "remaining_or_at_gate_430": 430 - core.FIXED_GATE_COST - recomputed,
            },
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=Path, required=True)
    parser.add_argument("--memory-mb", type=int, default=680)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = solve(args.start, args.memory_mb)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "cover"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
