"""Validate and summarize strict S1+S2 mixed cost-nine solver shards."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
WORKER = HERE / "exact_80d7_s1_s2_joint_strict_sat.py"
RESULT_DIR = HERE / "s1s2_joint_cost9_results"
REGRESSIONS = {
    "cadical195": HERE / "s1s2_joint_strict_g10_regression_cadical195.json",
    "glucose42": HERE / "s1s2_joint_strict_g10_regression_glucose42.json",
}
SOLVERS = ("cadical195", "glucose42")
CASES = (
    ("o7_s1_x0", 7, 1, 0),
    ("o5_s2_x0", 5, 2, 0),
    ("o3_s3_x0", 3, 3, 0),
    ("o1_s4_x0", 1, 4, 0),
    ("o6_s0_x1", 6, 0, 1),
    ("o4_s1_x1", 4, 1, 1),
    ("o2_s2_x1", 2, 2, 1),
    ("o0_s3_x1", 0, 3, 1),
    ("o3_s0_x2", 3, 0, 2),
    ("o1_s1_x2", 1, 1, 2),
    ("o0_s0_x3", 0, 0, 3),
)
EXPECTED_SOURCE_IDS = [4, 5, 22, 25, 51, 45, 56]
EXPECTED_TARGET_IDS = [77, 81]
EXPECTED_DEADLINES = [4, 7]
EXPECTED_CUT = [23, 24, 52, 53, 76, 77, 78, 79, 80, 81]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def atomic_write(path: Path, payload: dict[str, Any]) -> str:
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(encoded)
    temporary.replace(path)
    return sha256(encoded).hexdigest()


def common_errors(
    payload: dict[str, Any], path: Path, worker_sha: str
) -> list[str]:
    errors = []
    if payload.get("schema") != "byte-adder-80d7-s1-s2-joint-strict-physical-v1":
        errors.append(f"{path.name}: schema mismatch")
    if payload.get("script_sha256") != worker_sha:
        errors.append(f"{path.name}: worker hash mismatch")
    if payload.get("source_ids") != EXPECTED_SOURCE_IDS:
        errors.append(f"{path.name}: source IDs mismatch")
    if payload.get("target_ids") != EXPECTED_TARGET_IDS:
        errors.append(f"{path.name}: target IDs mismatch")
    if payload.get("output_deadlines") != EXPECTED_DEADLINES:
        errors.append(f"{path.name}: deadlines mismatch")
    if payload.get("cut_node_ids") != EXPECTED_CUT:
        errors.append(f"{path.name}: cut mismatch")
    if payload.get("compressed_truth_rows") != 36:
        errors.append(f"{path.name}: compressed row count mismatch")
    if payload.get("source_driven_one_counts", {}).get("C1") != 81920:
        errors.append(f"{path.name}: C1 driven count mismatch")
    if payload.get("source_driven_one_counts", {}).get("C3") != 94208:
        errors.append(f"{path.name}: C3 driven count mismatch")
    if payload.get("physical_nets") is not True:
        errors.append(f"{path.name}: physical-net flag missing")
    if payload.get("all_components_live") is not True:
        errors.append(f"{path.name}: liveness flag missing")
    if payload.get("final_outputs_fully_driven") is not True:
        errors.append(f"{path.name}: output-driven flag missing")
    return errors


def verify_regression(
    solver: str, path: Path, worker_sha: str
) -> tuple[dict[str, Any], list[str]]:
    errors = []
    if not path.is_file():
        return {}, [f"missing regression {path}"]
    payload = load_json(path)
    errors.extend(common_errors(payload, path, worker_sha))
    if payload.get("solver") != solver:
        errors.append(f"{path.name}: solver mismatch")
    expected = {
        "status": "sat",
        "gate_bound": 10,
        "components": 10,
        "exact_ordinary": 10,
        "exact_switches": 0,
        "exact_xors": 0,
        "weighted_gate": 10,
        "seed_current": True,
    }
    for field, value in expected.items():
        if payload.get(field) != value:
            errors.append(f"{path.name}: {field} mismatch")
    full = payload.get("full_verification", {})
    for field in (
        "mismatch_count",
        "bus_conflict_count",
        "undriven_output_count",
        "physical_net_partition_violation_count",
        "dead_component_count",
    ):
        if full.get(field) != 0:
            errors.append(f"{path.name}: full replay {field} is not zero")
    if full.get("actual_gate") != 10:
        errors.append(f"{path.name}: full replay gate mismatch")
    if full.get("output_arrivals") != EXPECTED_DEADLINES:
        errors.append(f"{path.name}: output arrival mismatch")
    if full.get("actual_component_arrivals") != [1, 2, 3, 4, 3, 4, 5, 5, 6, 7]:
        errors.append(f"{path.name}: component arrival mismatch")
    return {
        "solver": solver,
        "path": str(path.resolve()),
        "sha256": file_sha256(path),
        "status": payload.get("status"),
        "variables": payload.get("variables"),
        "clauses": payload.get("clauses"),
        "solve_seconds": payload.get("solve_seconds"),
        "full_verification": full,
    }, errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=HERE / "s1s2_joint_strict_cost9_mixed_summary.json",
    )
    args = parser.parse_args()

    worker_sha = file_sha256(WORKER)
    errors = []
    regressions = []
    for solver, path in REGRESSIONS.items():
        record, found = verify_regression(solver, path, worker_sha)
        regressions.append(record)
        errors.extend(found)

    case_records = []
    evidence_files = []
    for name, ordinary, switches, xors in CASES:
        per_solver = []
        for solver in SOLVERS:
            path = RESULT_DIR / f"{name}_{solver}.json"
            if not path.is_file():
                errors.append(f"missing result {path}")
                continue
            payload = load_json(path)
            errors.extend(common_errors(payload, path, worker_sha))
            expected = {
                "status": "unsat",
                "solver": solver,
                "gate_bound": 9,
                "components": ordinary + switches + xors,
                "exact_ordinary": ordinary,
                "exact_switches": switches,
                "exact_xors": xors,
                "weighted_gate": 9,
                "seed_current": False,
            }
            for field, value in expected.items():
                if payload.get(field) != value:
                    errors.append(f"{path.name}: {field} mismatch")
            record = {
                "solver": solver,
                "path": str(path.resolve()),
                "sha256": file_sha256(path),
                "status": payload.get("status"),
                "variables": payload.get("variables"),
                "clauses": payload.get("clauses"),
                "build_seconds": payload.get("build_seconds"),
                "solve_seconds": payload.get("solve_seconds"),
            }
            per_solver.append(record)
            evidence_files.append(record)
        if len(per_solver) == len(SOLVERS):
            if len({item["variables"] for item in per_solver}) != 1:
                errors.append(f"{name}: solver variable counts differ")
            if len({item["clauses"] for item in per_solver}) != 1:
                errors.append(f"{name}: solver clause counts differ")
            if {item["status"] for item in per_solver} != {"unsat"}:
                errors.append(f"{name}: not dual-solver UNSAT")
        case_records.append(
            {
                "name": name,
                "decomposition": {
                    "ordinary": ordinary,
                    "switches": switches,
                    "xors": xors,
                    "components": ordinary + switches + xors,
                    "weighted_gate": ordinary + 2 * switches + 3 * xors,
                },
                "solver_runs": per_solver,
                "status": (
                    "unsat"
                    if len(per_solver) == len(SOLVERS)
                    and {item["status"] for item in per_solver} == {"unsat"}
                    else "incomplete"
                ),
            }
        )

    complete = not errors
    payload = {
        "schema": "byte-adder-80d7-s1-s2-joint-strict-mixed-cost9-summary-v1",
        "scope": {
            "cut_node_ids": EXPECTED_CUT,
            "source_ids": EXPECTED_SOURCE_IDS,
            "target_ids": EXPECTED_TARGET_IDS,
            "target_names": ["S1", "S2"],
            "output_deadlines": EXPECTED_DEADLINES,
            "full_truth_rows": 131072,
            "compressed_truth_rows": 36,
            "strict_source_drivens": {"C1": 81920, "C3": 94208},
            "physical_nets": True,
            "all_components_live": True,
            "final_outputs_fully_driven": True,
        },
        "library_costs": {"ordinary": 1, "switch": 2, "xor": 3},
        "excluded_decomposition": {
            "ordinary": 9,
            "switches": 0,
            "xors": 0,
            "reason": "owned by the root task; not duplicated here",
        },
        "covered_mixed_decompositions": [
            item["decomposition"] for item in case_records
        ],
        "worker_path": str(WORKER.resolve()),
        "worker_sha256": worker_sha,
        "summarizer_sha256": file_sha256(Path(__file__).resolve()),
        "positive_regressions": regressions,
        "cases": case_records,
        "errors": errors,
        "coverage_complete": complete,
        "all_mixed_unsat": complete,
        "status": "all-mixed-cost9-unsat" if complete else "incomplete",
        "limitations": [
            "does not include the separately owned n9/s0/x0 decomposition",
            "fixed retained source pool only",
            "does not co-synthesize the retained boundary",
            "not a global 79/7 lower bound",
        ],
    }
    output_sha = atomic_write(args.output, payload)
    print(
        json.dumps(
            {
                "output": str(args.output.resolve()),
                "status": payload["status"],
                "cases": len(case_records),
                "solver_runs": len(evidence_files),
                "errors": len(errors),
                "output_sha256": output_sha,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if complete else 2


if __name__ == "__main__":
    raise SystemExit(main())
