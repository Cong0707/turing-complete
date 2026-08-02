"""Search bounded intermediate-form swaps around the prefix-1 x61 DAG."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time

from pysat.card import CardEnc, EncType
from pysat.solvers import Solver


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def reconstruct_forms(gates: list[dict[str, int]]) -> tuple[dict[int, int], dict[int, set[int]]]:
    forms = {signal: 1 << signal for signal in range(32)}
    by_stage = {stage: set() for stage in range(3)}
    for gate in gates:
        form = forms[gate["left"]] ^ forms[gate["right"]]
        forms[gate["output"]] = form
        by_stage[gate["stage"]].add(form)
    return forms, by_stage


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--incumbent", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--radius", type=int, required=True)
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--phase-max-sites", type=int, default=6)
    args = parser.parse_args()
    if args.radius <= 0:
        parser.error("--radius must be positive")

    here = Path(__file__).resolve().parent
    general = load(
        "rng_prefix1_neighbor_general",
        here / "search_prefix1_layered_general_cnf.py",
    )
    layered = load(
        "rng_prefix1_neighbor_layered", here / "search_prefix1_layered_cnf.py"
    )
    base = load(
        "rng_prefix1_neighbor_base", here / "audit_cyclic_retime.py"
    )
    problem = general.build_problem(layered, base, extra_limit=10)
    incumbent = json.loads(args.incumbent.read_text(encoding="utf-8"))
    _, by_stage = reconstruct_forms(incumbent["gate_dag"])

    extra_variables = {
        **{
            form: variable
            for form, variable in problem["pair_used"].items()
            if form not in problem["pair_targets"]
        },
        **{
            form: variable
            for form, variable in problem["depth_used"].items()
            if form not in problem["low_targets"]
        },
    }
    incumbent_extra_forms = frozenset(
        form
        for form in (*by_stage[0], *by_stage[1])
        if form in extra_variables
    )
    if len(incumbent_extra_forms) != 10:
        raise AssertionError(
            f"expected ten incumbent extra forms, got {len(incumbent_extra_forms)}"
        )
    old_variables = [extra_variables[form] for form in incumbent_extra_forms]
    new_variables = [
        variable
        for form, variable in extra_variables.items()
        if form not in incumbent_extra_forms
    ]

    # x60 is independently UNSAT, so every model under the global x61 bound
    # selects exactly ten extras.  These two bounds therefore describe at most
    # ``radius`` balanced replacements, while the clause excludes radius zero.
    problem["cnf"].append([-variable for variable in old_variables])
    problem["cnf"].extend(
        CardEnc.atmost(
            lits=[-variable for variable in old_variables],
            bound=args.radius,
            vpool=problem["pool"],
            encoding=EncType.seqcounter,
        ).clauses
    )
    problem["cnf"].extend(
        CardEnc.atmost(
            lits=new_variables,
            bound=args.radius,
            vpool=problem["pool"],
            encoding=EncType.seqcounter,
        ).clauses
    )

    started = time.perf_counter()
    with Solver(
        name=args.solver, bootstrap_with=problem["cnf"].clauses
    ) as solver:
        sat = solver.solve()
        model = frozenset(
            value for value in (solver.get_model() or ()) if value > 0
        )
        stats = solver.accum_stats()
    result = {
        "schema": 1,
        "model": "prefix1 general x61 bounded intermediate-form swaps",
        "status": "sat" if sat else "unsat",
        "solver": args.solver,
        "radius": args.radius,
        "xor_gate_cost": layered.XOR_GATE_COST,
        "xor_delay": layered.XOR_DELAY,
        "variable_count": problem["pool"].top,
        "clause_count": len(problem["cnf"].clauses),
        "clause_sha256": general.clause_fingerprint(problem["cnf"]),
        "elapsed_seconds": round(time.perf_counter() - started, 6),
        "solver_stats": stats,
        "incumbent_extra_forms": [
            f"{form:08x}" for form in sorted(incumbent_extra_forms)
        ],
    }
    if sat:
        dag = general.extract(layered, base, problem, model)
        (
            gates,
            forms,
            depths,
            visible,
            feedback,
            depth_options,
            final_options,
        ) = dag
        if len(gates) != 61:
            raise AssertionError(f"expected 61 XOR gates, got {len(gates)}")
        chosen_extra_forms = frozenset(
            form for form, variable in extra_variables.items() if variable in model
        )
        removed = incumbent_extra_forms - chosen_extra_forms
        added = chosen_extra_forms - incumbent_extra_forms
        if not removed or len(removed) > args.radius or len(added) > args.radius:
            raise AssertionError("extracted model violates replacement radius")
        phase = layered.audit_phase(
            base,
            gates,
            forms,
            depths,
            feedback,
            problem["T"],
            args.phase_max_sites,
        )
        or_count = phase.get("or_count")
        gate_count = None
        if or_count is not None:
            gate_count = (
                layered.FIXED_SHELL_GATE
                + layered.XOR_GATE_COST * len(gates)
                + or_count
            )
        result.update(
            {
                "xor_count": len(gates),
                "removed_extra_forms": [f"{form:08x}" for form in sorted(removed)],
                "added_extra_forms": [f"{form:08x}" for form in sorted(added)],
                "max_xor_depth": max(
                    depths[signal] for signal in (*visible, *feedback)
                ),
                "gate": gate_count,
                "delay": 10,
                "cycles": 66,
                "energy": None if gate_count is None else gate_count * 10 * 66,
                "beats_431_9_66": (
                    gate_count is not None and gate_count * 10 < 431 * 9
                ),
                "dag_sha256": hashlib.sha256(
                    json.dumps(
                        [asdict(gate) for gate in gates],
                        sort_keys=True,
                        separators=(",", ":"),
                    ).encode("ascii")
                ).hexdigest(),
                "depth_two_decompositions": {
                    f"{form:08x}": [f"{value:08x}" for value in option]
                    for form, option in depth_options.items()
                },
                "final_decompositions": {
                    f"{form:08x}": [f"{value:08x}" for value in option]
                    for form, option in final_options.items()
                },
                "gate_dag": [asdict(gate) for gate in gates],
                "phase_audit": phase,
            }
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                key: value
                for key, value in result.items()
                if key
                not in {
                    "incumbent_extra_forms",
                    "depth_two_decompositions",
                    "final_decompositions",
                    "gate_dag",
                    "phase_audit",
                }
            },
            indent=2,
        )
    )
    return 0 if sat else 2


if __name__ == "__main__":
    raise SystemExit(main())
