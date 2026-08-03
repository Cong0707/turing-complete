"""Exact mixed-primitive cost-3 audit for the 80/7 S0 and S6 roots.

The reviewed authoritative DAG has private four-ordinary-gate cones ending at
node 49 (``S0``) and node 73 (``S6``).  The existing local-root enumerator
closed every live three-ordinary-gate replacement over explicit retained
source pools.  With costs ordinary=1, Switch=2, XOR=3, the only remaining
exact weighted-cost-three decompositions are:

* one ordinary component plus one Switch (``o1+s1``);
* one XOR component (``x1``).

This companion reuses the reviewed physical BUS encoder and the independently
reviewed full-mask replay from the S2/S4 mixed-root audit.  Retained sources
keep exact value/driven/conflict/depth state over all 131072 rows.  Every build
starts from a pristine truth-table copy because the reused generic core
appends free constants in place.

Offline research only: no game launch, formal-save access, graft, or deploy.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
import time
from typing import Any

from pysat.solvers import Solver


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SHARED_PATH = HERE / "audit_80d7_weighted4_mixed_roots.py"
DEFAULT_DAG = (
    ROOT
    / ".research"
    / "byte_adder_root"
    / "byte-adder-hybrid-phasefold-g80-d7.json"
)
MATERIALIZER = (
    ROOT
    / ".research"
    / "byte_adder_builder_layout_agent"
    / "materialize_factory_dag.py"
)
EXACT_ADAPTER = (
    ROOT
    / ".research"
    / "byte_adder_han_knowles_fused_agent"
    / "search_av97_local_suffix.py"
)
ORDINARY_AUDIT = (
    ROOT
    / ".research"
    / "byte_adder_root"
    / "three-gate-root-resub-80d7.json"
)

TARGET_POOLS = {
    49: (2, 3, 18, 43, 44, 45),
    73: (12, 13, 14, 15, 34, 35, 36, 37, 38, 39, 62, 63, 64, 65, 66, 67, 68, 69),
}
TARGET_LABELS = {49: "S0", 73: "S6"}
DEADLINE = 7
FULL_ROWS = 1 << 17
MIXED_DECOMPOSITIONS = (
    {"name": "o1_s1", "components": 2, "switches": 1, "xors": 0},
    {"name": "x1", "components": 1, "switches": 0, "xors": 1},
)


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


shared = load(SHARED_PATH, "weighted3_root_shared")
shared.TARGET_LABELS.update(TARGET_LABELS)


def solver_status(answer: bool | None) -> str:
    if answer is True:
        return "sat"
    if answer is False:
        return "unsat"
    return "unknown"


def solve_case(
    exact: dict[str, Any],
    states: dict[int, dict[str, int]],
    source_ids: tuple[int, ...],
    target_id: int,
    decomposition: dict[str, Any],
    solver_name: str,
) -> dict[str, Any]:
    args = argparse.Namespace(
        interface="s6",
        gate_bound=3,
        max_delay=DEADLINE,
        components=int(decomposition["components"]),
        switches=int(decomposition["switches"]),
        xors=int(decomposition["xors"]),
        h_arrival=4,
        c5_arrival=4,
        output_deadlines=str(DEADLINE),
        solver=solver_name,
        timeout=0,
        output=HERE / "unused.json",
    )
    started = time.perf_counter()
    encoder, state = shared.fresh_exact_build(exact, args)
    with Solver(name=solver_name, bootstrap_with=encoder.cnf) as solver:
        answer = solver.solve()
        model = solver.get_model() if answer is True else None
    result: dict[str, Any] = {
        **decomposition,
        "ordinary": int(decomposition["components"])
        - int(decomposition["switches"])
        - int(decomposition["xors"]),
        "weighted_gate": 3,
        "solver": solver_name,
        "status": solver_status(answer),
        "variables": encoder.pool.top,
        "clauses": len(encoder.cnf.clauses),
        "solve_seconds": time.perf_counter() - started,
    }
    if model is not None:
        witness = exact["decode"](args, state, model)
        compressed = exact["verify"](witness, state)
        full = shared.independent_full_replay(
            witness, source_ids, target_id, states, exact["G"]
        )
        if int(witness["actual_gate"]) != 3 or int(full["actual_gate"]) != 3:
            raise RuntimeError("decoded mixed witness does not have weighted cost three")
        result["witness"] = witness
        result["compressed_verification"] = compressed
        result["full_verification"] = full
    return result


def positive_regression(
    exact: dict[str, Any],
    states: dict[int, dict[str, int]],
    source_ids: tuple[int, ...],
    target_id: int,
    solver_name: str,
) -> dict[str, Any]:
    args = argparse.Namespace(
        interface="s6",
        gate_bound=4,
        max_delay=DEADLINE,
        components=4,
        switches=0,
        xors=0,
        h_arrival=4,
        c5_arrival=4,
        output_deadlines=str(DEADLINE),
        solver=solver_name,
        timeout=0,
        output=HERE / "unused.json",
    )
    started = time.perf_counter()
    encoder, state = shared.fresh_exact_build(exact, args)
    with Solver(name=solver_name, bootstrap_with=encoder.cnf) as solver:
        answer = solver.solve()
        model = solver.get_model() if answer is True else None
    if model is None:
        raise RuntimeError(
            f"target {target_id} four-gate regression failed with {solver_name}: "
            f"{solver_status(answer)}"
        )
    witness = exact["decode"](args, state, model)
    compressed = exact["verify"](witness, state)
    full = shared.independent_full_replay(
        witness, source_ids, target_id, states, exact["G"]
    )
    if int(witness["actual_gate"]) != 4 or int(full["actual_gate"]) != 4:
        raise RuntimeError("positive regression has the wrong weighted cost")
    return {
        "status": "sat",
        "solver": solver_name,
        "components": 4,
        "exact_switches": 0,
        "exact_xors": 0,
        "variables": encoder.pool.top,
        "clauses": len(encoder.cnf.clauses),
        "solve_seconds": time.perf_counter() - started,
        "witness": witness,
        "compressed_verification": compressed,
        "full_verification": full,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dag", type=Path, default=DEFAULT_DAG)
    parser.add_argument(
        "--solvers", default="cadical195,glucose42", help="comma-separated solvers"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=HERE / "weighted3_mixed_roots_80d7.json",
    )
    args_cli = parser.parse_args()

    solvers = tuple(item.strip() for item in args_cli.solvers.split(",") if item.strip())
    if not solvers:
        parser.error("at least one solver is required")

    materializer = load(MATERIALIZER, "weighted3_root_materializer")
    adapter = load(EXACT_ADAPTER, "weighted3_root_exact_adapter")
    dag_payload = json.loads(args_cli.dag.read_text(encoding="utf-8"))
    ordered_nodes = tuple(dag_payload["factory_dag"]["nodes"])
    states = materializer.logical_states(ordered_nodes)
    started = time.perf_counter()
    targets = []
    any_sat = False
    any_unknown = False

    for target_id, source_ids in TARGET_POOLS.items():
        problem, source_drivens, metadata = shared.make_problem(
            source_ids, target_id, states
        )
        exact = adapter.load_core(problem, source_drivens)
        exact["_weighted4_truth_template"] = (
            tuple(problem[0]),
            tuple(tuple(row) for row in problem[1]),
            tuple(problem[2]),
            dict(problem[3]),
        )

        regressions = [
            positive_regression(exact, states, source_ids, target_id, solver_name)
            for solver_name in solvers
        ]
        runs = []
        for decomposition in MIXED_DECOMPOSITIONS:
            per_solver = [
                solve_case(
                    exact,
                    states,
                    source_ids,
                    target_id,
                    decomposition,
                    solver_name,
                )
                for solver_name in solvers
            ]
            statuses = {run["status"] for run in per_solver}
            if len(statuses) != 1:
                raise RuntimeError(
                    f"solver disagreement for target {target_id} "
                    f"{decomposition['name']}: {statuses}"
                )
            status = per_solver[0]["status"]
            any_sat |= status == "sat"
            any_unknown |= status == "unknown"
            runs.append(
                {
                    "decomposition": decomposition,
                    "status": status,
                    "solver_runs": per_solver,
                }
            )
        target_statuses = {item["status"] for item in runs}
        targets.append(
            {
                **metadata,
                "deadline": DEADLINE,
                "private_gate_cost": 4,
                "replacement_weighted_gate": 3,
                "four_gate_positive_regressions": regressions,
                "mixed_cost3_runs": runs,
                "status": (
                    "sat"
                    if "sat" in target_statuses
                    else "unknown"
                    if "unknown" in target_statuses
                    else "unsat"
                ),
            }
        )

    if any_sat:
        overall = "sat"
    elif any_unknown:
        overall = "unknown"
    else:
        overall = "all-mixed-cost3-unsat"
    result = {
        "schema": "byte-adder-80d7-weighted3-mixed-root-audit-v1",
        "source": str(args_cli.dag.resolve()),
        "source_sha256": file_sha256(args_cli.dag),
        "reviewed_all_ordinary_audit": str(ORDINARY_AUDIT.resolve()),
        "reviewed_all_ordinary_audit_sha256": file_sha256(ORDINARY_AUDIT),
        "shared_replay_path": str(SHARED_PATH.resolve()),
        "shared_replay_sha256": file_sha256(SHARED_PATH),
        "script_sha256_dependencies": {
            "materializer": file_sha256(MATERIALIZER),
            "exact_adapter": file_sha256(EXACT_ADAPTER),
        },
        "full_truth_rows": FULL_ROWS,
        "solvers": list(solvers),
        "library_costs": {"ordinary": 1, "switch": 2, "xor": 3},
        "covered_remaining_exact_cost3_decompositions": [
            dict(item) for item in MIXED_DECOMPOSITIONS
        ],
        "all_ordinary_cost3": "covered separately by reviewed root enumerator",
        "targets": targets,
        "status": overall,
        "scope": (
            "all live mixed-primitive weighted-cost3 DAGs over each explicit "
            "retained source pool, exact source value/driven masks, physical BUS "
            "partition, and final driven Sum at delay<=7"
        ),
        "limitations": [
            "fixed retained source pools only",
            "does not co-synthesize upstream retained nodes",
            "not a global 79/7 lower bound",
        ],
        "elapsed_seconds": time.perf_counter() - started,
    }
    encoded = (json.dumps(result, ensure_ascii=False, indent=2) + "\n").encode()
    args_cli.output.parent.mkdir(parents=True, exist_ok=True)
    args_cli.output.write_bytes(encoded)
    print(
        json.dumps(
            {
                "output": str(args_cli.output.resolve()),
                "status": overall,
                "targets": [
                    {
                        "target": item["target"],
                        "label": item["target_label"],
                        "status": item["status"],
                        "compressed_truth_rows": item["compressed_truth_rows"],
                    }
                    for item in targets
                ],
                "elapsed_seconds": result["elapsed_seconds"],
                "sha256": sha256(encoded).hexdigest(),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if overall != "unknown" else 2


if __name__ == "__main__":
    raise SystemExit(main())
