"""Enumerate canonical 61-XOR DAGs from the general prefix-1 model.

The general model permits weight-three/four targets to be implemented either
at XOR depth two or at depth three.  SAT assignments otherwise contain
irrelevant freedom (several decompositions of one form may all be true), so
this enumerator first adds exactly-one normalization for every selected form.
It then blocks the selected decomposition set after each model and audits the
late-seed phase correction with the exact meet-in-the-middle routine.
"""

from __future__ import annotations

import argparse
from collections import Counter
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


def add_at_most_one(problem, variables: list[int]) -> None:
    if len(variables) < 2:
        return
    problem["cnf"].extend(
        CardEnc.atmost(
            lits=variables,
            bound=1,
            vpool=problem["pool"],
            encoding=EncType.seqcounter,
        ).clauses
    )


def normalize_choices(problem) -> tuple[int, ...]:
    """Make each SAT model correspond to one concrete extracted DAG."""
    for form, options in problem["depth_options"].items():
        add_at_most_one(
            problem,
            [problem["depth_choice"][(form, index)] for index in range(len(options))],
        )
    for form, options in problem["final_options"].items():
        choices = [
            problem["final_choice"][(form, index)]
            for index in range(len(options))
        ]
        add_at_most_one(problem, choices)
        if form in problem["low_targets"]:
            shallow = problem["shallow_target"][form]
            for choice in choices:
                problem["cnf"].append([-choice, -shallow])
    return tuple(
        (*problem["depth_choice"].values(), *problem["final_choice"].values())
    )


def dag_hash(gates) -> str:
    return hashlib.sha256(
        json.dumps(
            [asdict(gate) for gate in gates],
            sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii")
    ).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--limit", type=int, default=1_000)
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--phase-max-sites", type=int, default=6)
    parser.add_argument("--target-or", type=int, default=38)
    args = parser.parse_args()
    if args.limit <= 0:
        parser.error("--limit must be positive")
    if args.phase_max_sites <= 0:
        parser.error("--phase-max-sites must be positive")

    here = Path(__file__).resolve().parent
    general = load(
        "rng_prefix1_general_enum_search",
        here / "search_prefix1_layered_general_cnf.py",
    )
    layered = load(
        "rng_prefix1_general_enum_layered",
        here / "search_prefix1_layered_cnf.py",
    )
    base = load(
        "rng_prefix1_general_enum_base", here / "audit_cyclic_retime.py"
    )
    problem = general.build_problem(layered, base, extra_limit=10)
    choice_variables = normalize_choices(problem)

    records = []
    best = None
    exhausted = False
    duplicate_dag_count = 0
    seen_dags: set[str] = set()
    started = time.perf_counter()
    with Solver(
        name=args.solver, bootstrap_with=problem["cnf"].clauses
    ) as solver:
        for index in range(args.limit):
            if not solver.solve():
                exhausted = True
                break
            model = frozenset(
                value for value in (solver.get_model() or ()) if value > 0
            )
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
            if max(depths[signal] for signal in (*visible, *feedback)) > 3:
                raise AssertionError("DAG exceeds XOR depth three")

            fingerprint = dag_hash(gates)
            if fingerprint in seen_dags:
                duplicate_dag_count += 1
            seen_dags.add(fingerprint)
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
            record = {
                "index": index,
                "or_count": or_count,
                "phase_status": phase["status"],
                "phase_certificate_sha256": phase.get("certificate_sha256"),
                "dag_sha256": fingerprint,
            }
            records.append(record)
            if or_count is not None and (
                best is None or or_count < best["or_count"]
            ):
                gate_count = (
                    layered.FIXED_SHELL_GATE
                    + layered.XOR_GATE_COST * len(gates)
                    + or_count
                )
                best = {
                    **record,
                    "xor_count": len(gates),
                    "xor_gate_cost": layered.XOR_GATE_COST,
                    "xor_delay": layered.XOR_DELAY,
                    "gate": gate_count,
                    "delay": 10,
                    "cycles": 66,
                    "energy": gate_count * 10 * 66,
                    "beats_431_9_66": gate_count * 10 < 431 * 9,
                    "depth_two_decompositions": {
                        f"{form:08x}": [f"{value:08x}" for value in option]
                        for form, option in depth_options.items()
                    },
                    "final_decompositions": {
                        f"{form:08x}": [f"{value:08x}" for value in option]
                        for form, option in final_options.items()
                    },
                    "visible_forms": [f"{forms[signal]:08x}" for signal in visible],
                    "feedback_forms": [
                        f"{forms[signal]:08x}" for signal in feedback
                    ],
                    "gate_dag": [asdict(gate) for gate in gates],
                    "phase_audit": phase,
                }
                print(
                    f"new best index={index} xor=61 or={or_count} "
                    f"gate={gate_count}",
                    flush=True,
                )

            selected_choices = [
                variable for variable in choice_variables if variable in model
            ]
            if not selected_choices:
                raise AssertionError("model has no selected decomposition choices")
            solver.add_clause([-variable for variable in selected_choices])
            if or_count is not None and or_count <= args.target_or:
                break
            if (index + 1) % 25 == 0:
                print(
                    f"enumerated={index + 1} unique={len(seen_dags)} best_or="
                    f"{None if best is None else best['or_count']}",
                    flush=True,
                )

    histogram = Counter(record["or_count"] for record in records)
    payload = {
        "schema": 1,
        "model": "canonical enumeration of general prefix1 61-XOR DAGs",
        "solver": args.solver,
        "requested_limit": args.limit,
        "enumerated_count": len(records),
        "unique_dag_count": len(seen_dags),
        "duplicate_dag_count": duplicate_dag_count,
        "exhausted": exhausted,
        "target_or": args.target_or,
        "hit_target": best is not None and best["or_count"] <= args.target_or,
        "xor_gate_cost": layered.XOR_GATE_COST,
        "xor_delay": layered.XOR_DELAY,
        "variable_count": problem["pool"].top,
        "clause_count": len(problem["cnf"].clauses),
        "clause_sha256": general.clause_fingerprint(problem["cnf"]),
        "elapsed_seconds": round(time.perf_counter() - started, 6),
        "or_histogram": {
            str(key): value
            for key, value in sorted(
                histogram.items(), key=lambda item: (item[0] is None, item[0])
            )
        },
        "records": records,
        "best": best,
    }
    payload["records_sha256"] = hashlib.sha256(
        json.dumps(records, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                key: value
                for key, value in payload.items()
                if key not in {"records", "best"}
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
