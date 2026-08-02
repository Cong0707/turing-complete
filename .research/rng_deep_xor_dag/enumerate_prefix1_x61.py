"""Enumerate distinct 61-XOR prefix-1 DAGs and audit their phase cost."""

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

from pysat.solvers import Solver


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


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

    here = Path(__file__).resolve().parent
    search = load("rng_prefix1_enum_search", here / "search_prefix1_layered_cnf.py")
    base = load("rng_prefix1_enum_base", here / "audit_cyclic_retime.py")
    problem = search.build_problem(base, extra_limit=10)
    original = base.build(1)
    original_forms, original_visible, original_feedback = original[1], original[3], original[4]
    problem["target_visible_forms"] = tuple(
        original_forms[signal] for signal in original_visible
    )
    problem["target_feedback_forms"] = tuple(
        original_forms[signal] for signal in original_feedback
    )

    choice_variables = tuple(
        (*problem["depth_choice"].values(), *problem["final_choice"].values())
    )
    records = []
    best = None
    exhausted = False
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
            dag = search.extract_dag(base, problem, model)
            gates, forms, depths, visible, feedback, depth_options, final_options = dag
            if len(gates) != 61:
                raise AssertionError(f"expected 61 XOR gates, got {len(gates)}")
            phase = search.audit_phase(
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
                "dag_sha256": hashlib.sha256(
                    json.dumps(
                        [asdict(gate) for gate in gates],
                        sort_keys=True,
                        separators=(",", ":"),
                    ).encode("ascii")
                ).hexdigest(),
            }
            records.append(record)
            if or_count is not None and (
                best is None or or_count < best["or_count"]
            ):
                best = {
                    **record,
                    "xor_count": len(gates),
                    "gate": search.FIXED_SHELL_GATE
                    + search.XOR_GATE_COST * len(gates)
                    + or_count,
                    "delay": 10,
                    "cycles": 66,
                    "depth_two_decompositions": {
                        f"{form:08x}": [f"{value:08x}" for value in option]
                        for form, option in depth_options.items()
                    },
                    "final_decompositions": {
                        f"{form:08x}": [f"{value:08x}" for value in option]
                        for form, option in final_options.items()
                    },
                    "visible_forms": [f"{forms[signal]:08x}" for signal in visible],
                    "feedback_forms": [f"{forms[signal]:08x}" for signal in feedback],
                    "gate_dag": [asdict(gate) for gate in gates],
                    "phase_audit": phase,
                }
                print(
                    f"new best index={index} xor=61 or={or_count} "
                    f"gate={best['gate']}",
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
            if (index + 1) % 100 == 0:
                print(
                    f"enumerated={index + 1} best_or="
                    f"{None if best is None else best['or_count']}",
                    flush=True,
                )

    histogram = Counter(record["or_count"] for record in records)
    payload = {
        "schema": 1,
        "model": "enumerated prefix1 layered 61-XOR DAGs",
        "solver": args.solver,
        "requested_limit": args.limit,
        "enumerated_count": len(records),
        "exhausted": exhausted,
        "target_or": args.target_or,
        "hit_target": best is not None and best["or_count"] <= args.target_or,
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
            {key: value for key, value in payload.items() if key not in {"records", "best"}},
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
