"""Bounded SAT for complete depth-two XOR2/XOR3 count fingerprints.

The complete cancellation-aware option family is retained.  Instead of one
weak weighted bound, each run fixes the total number of 12/2 XOR3 gates and
bounds the 3/2 XOR2 gates by ``x + 4*y <= 67``.  Native MiniCard constraints
then propagate the two gate populations independently.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import gc
from pathlib import Path
import sys
import threading
import time

from pysat.card import CardEnc, EncType as CardEncType
from pysat.formula import CNFPlus, IDPool
from pysat.solvers import Solver

import solve_mixed_cover as common
import solve_shared_tristate_complete as source_tools


_MODEL_CACHE = None


def load_rc2_helpers():
    path = Path(__file__).resolve().parents[1] / "rng_u32_joint_state" / "solve_mixed_rc2.py"
    spec = importlib.util.spec_from_file_location("exact_count_rc2_helpers", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def build(exact_xor3: int, at_most_only: bool):
    global _MODEL_CACHE
    if _MODEL_CACHE is None:
        helpers = load_rc2_helpers()
        primary_cost, minimal = helpers.build_minimal_options()
        records = helpers.option_records(minimal)
        used_forms = tuple(
            sorted(
                {
                    form
                    for output_records in records
                    for _cost, required in output_records
                    for form in required
                }
            )
        )
        _MODEL_CACHE = helpers, primary_cost, records, used_forms
    helpers, primary_cost, records, used_forms = _MODEL_CACHE
    pool = IDPool()
    formula = CNFPlus()
    form_var = {form: pool.id(("form", form)) for form in used_forms}
    type_var: dict[tuple[int, int], int] = {}
    selectors: dict[tuple[int, int], int] = {}

    for output, output_records in enumerate(records):
        costs = tuple(sorted({cost for cost, _required in output_records}))
        types = []
        for cost in costs:
            variable = pool.id(("type", output, cost))
            type_var[output, cost] = variable
            types.append(variable)
        formula.append(types)
        formula.append([types, 1], is_atmost=True)

        output_selectors = []
        for option_index, (cost, required) in enumerate(output_records):
            variable = pool.id(("option", output, option_index))
            selectors[output, option_index] = variable
            output_selectors.append(variable)
            formula.append([-variable, type_var[output, cost]])
            for form in required:
                formula.append([-variable, form_var[form]])
        formula.append(output_selectors)
        formula.append([output_selectors, 1], is_atmost=True)

    xor2_literals = [
        variable for form, variable in form_var.items() if form.bit_count() == 2
    ]
    xor2_literals.extend(
        variable for (output, cost), variable in type_var.items() if cost == 3
    )
    xor3_literals = [
        variable for form, variable in form_var.items() if form.bit_count() == 3
    ]
    xor3_literals.extend(
        variable for (output, cost), variable in type_var.items() if cost == 12
    )
    xor2_bound = 67 - 4 * exact_xor3
    if xor2_bound < 0:
        raise ValueError("XOR3 count already exceeds 201-gate budget")
    formula.append([xor2_literals, xor2_bound], is_atmost=True)
    formula.append([xor3_literals, exact_xor3], is_atmost=True)
    if not at_most_only:
        formula.append(
            [[-literal for literal in xor3_literals], len(xor3_literals) - exact_xor3],
            is_atmost=True,
        )
    return formula, {
        "helpers": helpers,
        "primary_cost": primary_cost,
        "records": records,
        "used_forms": used_forms,
        "form_var": form_var,
        "type_var": type_var,
        "selectors": selectors,
        "xor2_literals": xor2_literals,
        "xor3_literals": xor3_literals,
        "xor2_bound": xor2_bound,
        "variable_count": pool.top,
    }


def solve(
    exact_xor3: int,
    timeout_seconds: int,
    memory_mb: int,
    solver_name: str,
    at_most_only: bool,
) -> dict[str, object]:
    started = time.perf_counter()
    stopped, peak = common.start_watchdog(memory_mb)
    formula, metadata = build(exact_xor3, at_most_only)
    build_seconds = time.perf_counter() - started
    print(
        f"built y={exact_xor3} x<={metadata['xor2_bound']} "
        f"vars={metadata['variable_count']} clauses={len(formula.clauses)} "
        f"native={len(formula.atmosts)} options={sum(map(len, metadata['records']))}",
        flush=True,
    )

    bootstrap = formula
    encoded_clause_count = None
    encoded_variable_count = None
    if solver_name in {"cd195", "cadical195"}:
        clauses = list(formula.clauses)
        top_id = metadata["variable_count"]
        for literals, bound in formula.atmosts:
            encoding = CardEnc.atmost(
                lits=literals,
                bound=bound,
                top_id=top_id,
                encoding=CardEncType.seqcounter,
            )
            clauses.extend(encoding.clauses)
            top_id = max(top_id, encoding.nv)
        bootstrap = clauses
        encoded_clause_count = len(clauses)
        encoded_variable_count = top_id
        print(
            f"encoded_cnf vars={top_id} clauses={len(clauses)}",
            flush=True,
        )

    interrupted = threading.Event()
    with Solver(name=solver_name, bootstrap_with=bootstrap) as oracle:
        def interrupt() -> None:
            interrupted.set()
            try:
                oracle.interrupt()
            except NotImplementedError:
                os._exit(124)

        timer = threading.Timer(timeout_seconds, interrupt)
        timer.start()
        try:
            status = oracle.solve_limited(expect_interrupt=True)
            assignment = oracle.get_model() if status is True else None
            stats = oracle.accum_stats()
        finally:
            timer.cancel()
            try:
                oracle.clear_interrupt()
            except NotImplementedError:
                pass
    solve_seconds = time.perf_counter() - started - build_seconds
    stopped.set()
    peak[0] = max(peak[0], common.working_set_bytes())
    report: dict[str, object] = {
        "status": "sat" if status is True else "unsat" if status is False else "unknown",
        "scope": "complete cancellation-aware depth-two XOR2/XOR3 count fingerprint",
        "exact_xor3": exact_xor3,
        "xor3_constraint": "at_most" if at_most_only else "exact",
        "max_xor2": metadata["xor2_bound"],
        "gate_bound": 201,
        "timeout_seconds": timeout_seconds,
        "memory_limit_mb": memory_mb,
        "peak_working_set_mb": peak[0] / 1048576,
        "build_seconds": build_seconds,
        "solve_seconds": solve_seconds,
        "solver": f"{solver_name}/native cardinality",
        "stats": stats,
        "candidate_options": sum(map(len, metadata["records"])),
        "encoded_cnf_variables": encoded_variable_count,
        "encoded_cnf_clauses": encoded_clause_count,
    }
    if status is not True:
        return report

    positive = {literal for literal in assignment if literal > 0}
    selected_forms = tuple(
        form for form, variable in metadata["form_var"].items() if variable in positive
    )
    selected_types = {
        output: cost
        for (output, cost), variable in metadata["type_var"].items()
        if variable in positive
    }
    outputs = []
    rows = metadata["helpers"].mixed.target_rows()
    for output, output_records in enumerate(metadata["records"]):
        active = [
            index
            for index in range(len(output_records))
            if metadata["selectors"][output, index] in positive
        ]
        if len(active) != 1:
            raise AssertionError(f"output {output} has {len(active)} selected options")
        cost, required = output_records[active[0]]
        arity = 0 if cost == 0 else 2 if cost == 3 else 3
        sources = source_tools.recover_sources(rows[output], arity, required)
        outputs.append(
            {
                "output": output,
                "target": f"{rows[output]:08x}",
                "final_arity": arity,
                "sources": [f"{source:08x}" for source in sources],
                "required_first_forms": [f"{form:08x}" for form in required],
            }
        )
    xor2 = sum(form.bit_count() == 2 for form in selected_forms) + sum(
        cost == 3 for cost in selected_types.values()
    )
    xor3 = sum(form.bit_count() == 3 for form in selected_forms) + sum(
        cost == 12 for cost in selected_types.values()
    )
    gate = 3 * xor2 + 12 * xor3
    if ((xor3 > exact_xor3 if at_most_only else xor3 != exact_xor3)
            or xor2 > metadata["xor2_bound"] or gate > 201):
        raise AssertionError("extracted count certificate violates requested fingerprint")
    selected = set(selected_forms)
    for output, entry in enumerate(outputs):
        value = 0
        for encoded in entry["sources"]:
            source = int(encoded, 16)
            value ^= source
            if source.bit_count() > 1 and source not in selected:
                raise AssertionError("output uses absent first-layer form")
        if value != rows[output]:
            raise AssertionError("output reconstruction mismatch")
    vectors = [0, 1, 2, 0x12345678, 0xFFFFFFFF]
    vectors.extend(__import__("random").Random(0x5A201).getrandbits(32) for _ in range(64))
    for value in vectors:
        if common.apply_matrix(rows, value) != common.xorshift32(value):
            raise AssertionError("transition vector mismatch")
    report["certificate"] = {
        "T": "natural",
        "single_u32_input": True,
        "single_u32_output": True,
        "selected_first_forms": [f"{form:08x}" for form in selected_forms],
        "outputs": outputs,
        "metrics": {
            "xor2": xor2,
            "xor3": xor3,
            "core_gate": gate,
            "core_delay": 4,
            "full_rng_gate": 230 + gate,
            "full_rng_delay": 9,
        },
        "verification": {
            "transition_vectors": len(vectors),
            "outputs_reconstructed": 32,
            "uses_score_field_forgery": False,
        },
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--exact-xor3", type=int, nargs="+", required=True)
    parser.add_argument("--timeout-seconds", type=int, default=120)
    parser.add_argument("--memory-mb", type=int, default=680)
    parser.add_argument("--solver", default="minicard")
    parser.add_argument("--at-most-xor3", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    results = []
    for exact_xor3 in args.exact_xor3:
        results.append(
            solve(
                exact_xor3,
                args.timeout_seconds,
                args.memory_mb,
                args.solver,
                args.at_most_xor3,
            )
        )
        gc.collect()
    result = results[0] if len(results) == 1 else {
        "status": (
            "sat" if any(item["status"] == "sat" for item in results)
            else "unknown" if any(item["status"] == "unknown" for item in results)
            else "unsat"
        ),
        "scope": "complete cancellation-aware XOR2/XOR3 fingerprint sweep",
        "results": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "certificate"}, indent=2))
    if "certificate" in result:
        print(json.dumps(result["certificate"]["metrics"], indent=2))
    return 0 if result["status"] in {"sat", "unsat"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
