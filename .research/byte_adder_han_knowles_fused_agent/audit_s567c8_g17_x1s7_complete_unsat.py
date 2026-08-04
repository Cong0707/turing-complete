"""Audit the complete eight-position g17/o0/s7/x1 UNSAT sweep."""

from __future__ import annotations

import argparse
from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SWEEP = HERE / "remote-sweeps/s567c8_sparse_g17_g18_20260804"
CLASS_DIR = SWEEP / "g17_x1s7"
PREFLIGHT = SWEEP / "preflight"
POSITIVE = SWEEP / "positive_regression"
PHYSICAL_EXACT = ROOT / ".research/byte_adder_phase_shortcut_restart/physical_exact.py"
DEFAULT_AUDIT = HERE / "s567c8_g17_x1s7_complete_unsat_audit.json"
DEFAULT_MANIFEST = HERE / "s567c8_g17_x1s7_complete_unsat_manifest.json"

EXPECTED_WORKER_SHA256 = (
    "c48a96e55d8c5076418999f5fa5ee95e9f8207c03f138cd4bccf48908a69c071"
)
EXPECTED_DEPENDENCIES = {
    ".research/byte_adder_ling_theory_agent/exact_free_ling_pair_sat.py": (
        "49bb2640e1cb08c6e2b9ac412a8cf56c058f27966e1dd799d1d813c8f1821017"
    ),
    ".research/byte_adder_boolean_superopt_agent/exact_adder_block_sat.py": (
        "f320ed3029b949185acd13b5462b659502a970406d1bf5047713279e152f56de"
    ),
    ".research/rng_468_joint_macro/joint_parity_cnf.py": (
        "a565201bf7e99f6ded6732e70d883cd9a90e5da2e42d72171f11952bb3566ca4"
    ),
}
EXPECTED_SUFFIX_SHA256 = (
    "920b0950e3ece8f8e5870ea85704dc5490e6ccf8ecdb95b44f584554ffe8bd66"
)
EXPECTED_SUFFIX = [["XOR"], ["SWITCH"]]
OUTPUTS = ["S5", "S6", "S7", "C8"]


def relative(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT)).replace("\\", "/")


def digest(path: Path) -> str | None:
    return sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object in {path}")
    return value


def expected_fixed(xor_slot: int) -> list[str]:
    result = ["SWITCH"] * 8
    result[xor_slot] = "XOR"
    return result


def parse_utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def check_equal(
    checks: dict[str, bool], name: str, actual: object, expected: object
) -> None:
    checks[name] = actual == expected


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", type=Path, default=DEFAULT_AUDIT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args()

    invalid: list[dict[str, object]] = []
    structural_manifest_path = PREFLIGHT / "g17_sparse_manifest.json"
    structural_audit_path = PREFLIGHT / "g17_sparse_audit.json"
    sweep_summary_path = CLASS_DIR / "summary.json"
    positive_result_path = POSITIVE / "tail_s7c8_g16_fixed_kinds_d5.json"
    positive_run_path = POSITIVE / "tail_s7c8_g16_fixed_kinds_d5.run.json"
    positive_replay_path = POSITIVE / "tail_s7c8_g16_fixed_kinds_d5.replay.json"

    required = [
        PHYSICAL_EXACT,
        structural_manifest_path,
        structural_audit_path,
        sweep_summary_path,
        positive_result_path,
        positive_run_path,
        positive_replay_path,
    ]
    for slot in range(8):
        required.extend(
            (
                CLASS_DIR / "results" / f"x{slot}.json",
                CLASS_DIR / "logs" / f"x{slot}.log",
                CLASS_DIR / "runs" / f"x{slot}.run.json",
            )
        )
    missing = [relative(path) for path in required if not path.is_file()]
    if missing:
        invalid.append({"reason": "missing_files", "paths": missing})

    structural_manifest = read_json(structural_manifest_path)
    structural_audit = read_json(structural_audit_path)
    sweep_summary = read_json(sweep_summary_path)
    positive_result = read_json(positive_result_path)
    positive_run = read_json(positive_run_path)
    positive_replay = read_json(positive_replay_path)

    structural_class = next(
        row
        for row in structural_manifest.get("classes", [])
        if row.get("name") == "g17_x1s7"
    )
    structural_patterns = {
        int(row["xor_slot"]): row for row in structural_class.get("patterns", [])
    }
    structural_checks = {
        "manifest_status": structural_manifest.get("status") == "complete",
        "audit_status": structural_audit.get("status") == "complete",
        "audit_manifest_sha256": structural_audit.get("manifest_sha256")
        == digest(structural_manifest_path),
        "worker_sha256": digest(PHYSICAL_EXACT) == EXPECTED_WORKER_SHA256,
        "manifest_worker_sha256": structural_manifest.get("worker", {}).get("sha256")
        == EXPECTED_WORKER_SHA256,
        "dependency_sha256": structural_manifest.get("worker", {}).get(
            "dependency_sha256"
        )
        == EXPECTED_DEPENDENCIES,
        "class_scope": structural_class.get("scope")
        == {
            "domain": "s34567c8_leaf",
            "rows": 486,
            "outputs": OUTPUTS,
            "gate_bound": 17,
            "max_delay": 5,
            "components": 8,
            "ordinary": 0,
            "switches": 7,
            "xors": 1,
            "position_patterns": 8,
            "concrete_kind_assignments": 8,
        },
        "position_patterns": set(structural_patterns) == set(range(8)),
        "suffix_universe": structural_class.get("shard", {}).get("suffix_universe")
        == EXPECTED_SUFFIX,
        "suffix_universe_sha256": structural_class.get("shard", {}).get(
            "suffix_universe_sha256"
        )
        == EXPECTED_SUFFIX_SHA256,
        "assigned_suffix_signatures": structural_class.get("shard", {}).get(
            "assigned_suffix_signatures"
        )
        == EXPECTED_SUFFIX,
        "structural_class_checks": all(structural_class.get("checks", {}).values()),
    }
    if not all(structural_checks.values()):
        invalid.append({"reason": "structural_preflight", "checks": structural_checks})

    positive_checks = {
        "result_status": positive_result.get("status") == "sat",
        "run_status": positive_run.get("status") == "sat",
        "run_raw_status": positive_run.get("raw_status") == "sat",
        "run_exit": positive_run.get("exit_code") == 0,
        "run_not_timed_out": positive_run.get("timed_out") is False,
        "run_result_sha256": positive_run.get("result_sha256")
        == digest(positive_result_path),
        "replay_status": positive_replay.get("status") == "verified",
        "replay_errors": positive_replay.get("errors") == [],
        "replay_evidence_sha256": positive_replay.get("evidence_sha256")
        == digest(positive_result_path),
        "replay_worker_sha256": positive_replay.get("physical_exact_sha256")
        == EXPECTED_WORKER_SHA256,
        "replay_rows": positive_replay.get("recomputed", {}).get("rows") == 486,
        "replay_zero_counts": all(
            positive_replay.get("recomputed", {}).get(field) == 0
            for field in (
                "mismatch_count",
                "bus_conflict_count",
                "undriven_output_count",
                "physical_net_partition_violation_count",
                "dead_component_count",
                "depth_upper_bound_violation_count",
                "output_deadline_violation_count",
                "malformed_bus_count",
            )
        ),
    }
    if not all(positive_checks.values()):
        invalid.append({"reason": "positive_regression", "checks": positive_checks})

    records: list[dict[str, object]] = []
    seen_slots: set[int] = set()
    for xor_slot in range(8):
        key = f"x{xor_slot}"
        result_path = CLASS_DIR / "results" / f"{key}.json"
        log_path = CLASS_DIR / "logs" / f"{key}.log"
        run_path = CLASS_DIR / "runs" / f"{key}.run.json"
        result = read_json(result_path)
        log = read_json(log_path)
        run = read_json(run_path)
        fixed = expected_fixed(xor_slot)
        checks: dict[str, bool] = {}

        for name, actual, expected in (
            ("result_schema", result.get("schema"), "exact-fast-negative-physical-shard-v2"),
            ("result_status", result.get("status"), "unsat"),
            ("domain", result.get("domain"), "s34567c8_leaf"),
            ("rows", result.get("rows"), 486),
            ("outputs", result.get("output_names"), OUTPUTS),
            ("gate_bound", result.get("gate_bound"), 17),
            ("max_delay", result.get("max_delay"), 5),
            ("components", result.get("components"), 8),
            ("ordinary", result.get("ordinary"), 0),
            ("switches", result.get("exact_switches"), 7),
            ("xors", result.get("exact_xors"), 1),
            ("fixed_kinds", result.get("fixed_kinds"), fixed),
            ("solver", result.get("solver"), "cadical195"),
            ("physical_nets", result.get("physical_nets"), True),
            (
                "public_outputs_must_be_driven",
                result.get("public_outputs_must_be_driven"),
                True,
            ),
            ("timer_errors", result.get("timer_errors"), []),
            ("dependency_sha256", result.get("dependency_sha256"), EXPECTED_DEPENDENCIES),
            ("run_schema", run.get("schema"), "s567c8-sparse-position-run-v1"),
            ("run_target_class", run.get("target_class"), "g17_x1s7"),
            ("run_key", run.get("key"), key),
            ("run_status", run.get("status"), "unsat"),
            ("run_raw_status", run.get("raw_status"), "unsat"),
            ("run_exit", run.get("exit_code"), 0),
            ("run_classification", run.get("classification"), "solver_exit"),
            ("run_timed_out", run.get("timed_out"), False),
            ("run_killed", run.get("killed_after_timeout"), False),
            ("run_validation_errors", run.get("validation_errors"), []),
            ("run_xor_slot", run.get("xor_slot"), xor_slot),
            ("run_ordinary_slot", run.get("ordinary_slot"), None),
            ("run_fixed_kinds", run.get("fixed_kinds"), fixed),
            ("run_result_sha256", run.get("result_sha256"), digest(result_path)),
            ("run_log_sha256", run.get("log_sha256"), digest(log_path)),
            ("log_status", log.get("status"), "unsat"),
            ("log_sha256", log.get("sha256"), digest(result_path)),
        ):
            check_equal(checks, name, actual, expected)

        shard = result.get("shard") or {}
        for name, actual, expected in (
            ("split_slots", shard.get("split_slots"), 1),
            ("shard_count", shard.get("shard_count"), 1),
            ("shard_index", shard.get("shard_index"), 0),
            ("suffix_universe_count", shard.get("suffix_universe_count"), 2),
            (
                "suffix_universe_sha256",
                shard.get("suffix_universe_sha256"),
                EXPECTED_SUFFIX_SHA256,
            ),
            (
                "assigned_suffix_signatures",
                shard.get("assigned_suffix_signatures"),
                EXPECTED_SUFFIX,
            ),
        ):
            check_equal(checks, name, actual, expected)

        start = parse_utc(str(run.get("start_utc")))
        end = parse_utc(str(run.get("end_utc")))
        checks["positive_elapsed"] = end > start
        checks["wall_under_watchdog"] = 0 < float(run.get("wall_seconds", 0)) < 180
        checks["solve_under_wall"] = 0 < float(result.get("solve_seconds", 0)) <= float(
            run.get("wall_seconds", 0)
        )
        checks["resource_limits"] = run.get("resource_limits") == {
            "watchdog_seconds": 180.0,
            "as_limit_kib": 1310720,
            "nice": 5,
        }
        checks["structural_pattern_agrees"] = structural_patterns[xor_slot].get(
            "fixed_kinds"
        ) == fixed and all(structural_patterns[xor_slot].get("checks", {}).values())

        if all(checks.values()):
            seen_slots.add(xor_slot)
        else:
            invalid.append({"reason": "evidence_record", "key": key, "checks": checks})
        records.append(
            {
                "key": key,
                "xor_slot": xor_slot,
                "fixed_kinds": fixed,
                "status": result.get("status"),
                "solve_seconds": result.get("solve_seconds"),
                "wall_seconds": run.get("wall_seconds"),
                "pid": run.get("pid"),
                "variables": result.get("variables"),
                "clauses": result.get("clauses"),
                "result": relative(result_path),
                "result_sha256": digest(result_path),
                "log": relative(log_path),
                "log_sha256": digest(log_path),
                "run": relative(run_path),
                "run_sha256": digest(run_path),
                "checks": checks,
            }
        )

    summary_checks = {
        "schema": sweep_summary.get("schema")
        == "s567c8-sparse-position-class-summary-v1",
        "target_class": sweep_summary.get("target_class") == "g17_x1s7",
        "expected_patterns": sweep_summary.get("expected_position_patterns") == 8,
        "attempted_patterns": sweep_summary.get("attempted_position_patterns") == 8,
        "status_counts": sweep_summary.get("status_counts") == {"unsat": 8},
        "raw_sat": sweep_summary.get("raw_sat") == [],
        "verified_sat": sweep_summary.get("verified_sat") == [],
        "unknown_is_not_unsat": sweep_summary.get("unknown_is_not_unsat") is True,
    }
    if not all(summary_checks.values()):
        invalid.append({"reason": "sweep_summary", "checks": summary_checks})

    coverage_checks = {
        "xor_slots": seen_slots == set(range(8)),
        "record_count": len(records) == 8,
        "unique_fixed_kinds": len({tuple(row["fixed_kinds"]) for row in records}) == 8,
        "all_status_unsat": all(row["status"] == "unsat" for row in records),
        "no_invalid": not invalid,
    }
    complete = all(coverage_checks.values())

    manifest = {
        "schema": "s567c8-g17-x1s7-complete-unsat-manifest-v1",
        "status": "unsat-covered" if complete else "incomplete",
        "scope": {
            "domain": "s34567c8_leaf",
            "rows": 486,
            "outputs": OUTPUTS,
            "gate_bound": 17,
            "max_delay": 5,
            "components": 8,
            "ordinary": 0,
            "switches": 7,
            "xors": 1,
            "position_patterns": 8,
        },
        "worker": {
            "path": relative(PHYSICAL_EXACT),
            "sha256": digest(PHYSICAL_EXACT),
            "dependency_sha256": EXPECTED_DEPENDENCIES,
        },
        "positive_regression": {
            "result": relative(positive_result_path),
            "result_sha256": digest(positive_result_path),
            "run": relative(positive_run_path),
            "run_sha256": digest(positive_run_path),
            "replay": relative(positive_replay_path),
            "replay_sha256": digest(positive_replay_path),
            "checks": positive_checks,
        },
        "structural_preflight": {
            "manifest": relative(structural_manifest_path),
            "manifest_sha256": digest(structural_manifest_path),
            "audit": relative(structural_audit_path),
            "audit_sha256": digest(structural_audit_path),
            "checks": structural_checks,
        },
        "sweep_summary": {
            "path": relative(sweep_summary_path),
            "sha256": digest(sweep_summary_path),
            "checks": summary_checks,
        },
        "suffix_shard": {
            "split_slots": 1,
            "shard_count": 1,
            "shard_index": 0,
            "suffix_universe": EXPECTED_SUFFIX,
            "suffix_universe_sha256": EXPECTED_SUFFIX_SHA256,
        },
        "coverage_checks": coverage_checks,
        "records": records,
        "invalid": invalid,
        "scope_exclusions": [
            "ordinary gates",
            "more than one XOR",
            "other Switch/XOR decompositions",
            "component counts other than eight",
            "a complete g17 or cost-17 lower bound",
        ],
        "conclusion": (
            "All eight possible XOR positions in the exact g17/o0/s7/x1, "
            "D5, eight-component class are strict UNSAT. This conclusion is "
            "limited to that fixed decomposition and interface."
        ),
    }
    manifest_encoded = (
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    ).encode()
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_bytes(manifest_encoded)

    audit = {
        "schema": "s567c8-g17-x1s7-complete-unsat-audit-v1",
        "status": "unsat-covered" if complete else "incomplete",
        "manifest": relative(args.manifest),
        "manifest_sha256": sha256(manifest_encoded).hexdigest(),
        "auditor": relative(Path(__file__)),
        "auditor_sha256": digest(Path(__file__)),
        "worker_sha256": digest(PHYSICAL_EXACT),
        "position_count": len(seen_slots),
        "unsat_count": sum(row["status"] == "unsat" for row in records),
        "unknown_count": sum(row["status"] != "unsat" for row in records),
        "invalid_count": len(invalid),
        "coverage_checks": coverage_checks,
    }
    audit_encoded = (json.dumps(audit, ensure_ascii=False, indent=2) + "\n").encode()
    args.audit.parent.mkdir(parents=True, exist_ok=True)
    args.audit.write_bytes(audit_encoded)

    print(
        json.dumps(
            {
                "status": audit["status"],
                "position_count": audit["position_count"],
                "unsat_count": audit["unsat_count"],
                "unknown_count": audit["unknown_count"],
                "invalid_count": audit["invalid_count"],
                "manifest_sha256": sha256(manifest_encoded).hexdigest(),
                "audit_sha256": sha256(audit_encoded).hexdigest(),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if complete else 1


if __name__ == "__main__":
    raise SystemExit(main())
