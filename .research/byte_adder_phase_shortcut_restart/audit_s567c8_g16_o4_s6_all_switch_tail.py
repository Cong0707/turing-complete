"""Strictly audit the fixed g16/o4/s6 all-Switch-tail exact job."""

from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORKER = HERE / "physical_exact.py"
FIXED_KINDS = ("NOT", "NOR", "OR", "OR", *("SWITCH" for _ in range(6)))
EXPECTED_NAME = "s567c8-d5-g16-o04-s06-all-switch-tail"
TERMINAL = {"sat", "unsat"}
ZERO_FIELDS = (
    "mismatch_count",
    "bus_conflict_count",
    "undriven_output_count",
    "physical_net_partition_violation_count",
    "depth_upper_bound_violation_count",
    "output_deadline_violation_count",
)


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def constraint_digest(fixed: tuple[str, ...]) -> str:
    return sha256(
        json.dumps(fixed, ensure_ascii=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def positive_regression_check(proof: dict[str, object]) -> tuple[bool, list[str]]:
    errors: list[str] = []
    positive = proof.get("positive_regression", {})
    try:
        script = ROOT / positive["script"]
        artifact = ROOT / positive["artifact"]
    except (KeyError, TypeError):
        return False, ["positive regression paths are missing"]
    if not script.is_file() or digest(script) != positive.get("script_sha256"):
        errors.append("positive regression script hash mismatch")
    if not artifact.is_file() or digest(artifact) != positive.get("artifact_sha256"):
        errors.append("positive regression artifact hash mismatch")
        return False, errors
    try:
        payload = json.loads(artifact.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return False, [*errors, f"positive regression JSON error: {exc!r}"]
    verification = payload.get("verification", {})
    regression = payload.get("regression", {})
    if payload.get("status") != "verified-positive-regression":
        errors.append("positive regression status mismatch")
    if verification.get("verified") is not True:
        errors.append("positive regression verification is not true")
    if tuple(regression.get("fixed_kinds", ())) != FIXED_KINDS:
        errors.append("positive regression topology mismatch")
    if regression.get("output_names") != ["S7", "C8"]:
        errors.append("positive regression output scope mismatch")
    if verification.get("rows") != 486:
        errors.append("positive regression row count mismatch")
    if verification.get("actual_gate") != 16:
        errors.append("positive regression gate count mismatch")
    if verification.get("actual_max_delay") != 5:
        errors.append("positive regression delay mismatch")
    for key, value in verification.items():
        if key.endswith("count") and value != 0:
            errors.append(f"positive regression nonzero {key}")
    return not errors, errors


def audit_summary(
    *,
    summary_path: Path,
    spec_path: Path,
    spec: dict[str, object],
    repository: Path,
    record: dict[str, object],
) -> dict[str, object]:
    result: dict[str, object] = {
        "path": str(summary_path),
        "exists": summary_path.is_file(),
        "integrity": False,
        "errors": [],
    }
    if not summary_path.is_file():
        result["errors"] = ["summary missing"]
        return result
    try:
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        result["errors"] = [f"summary JSON error: {exc!r}"]
        return result
    errors: list[str] = []
    if summary.get("schema") != "tc-byte-adder-remote-sweep-summary-v1":
        errors.append("summary schema mismatch")
    if summary.get("spec_sha256") != digest(spec_path):
        errors.append("summary spec SHA mismatch")
    if summary.get("script_sha256") != digest(WORKER):
        errors.append("summary worker SHA mismatch")
    if summary.get("finished") is not True:
        errors.append("summary is not finished")
    items = list(summary.get("results", ()))
    states: Counter[str] = Counter()
    statuses: Counter[str] = Counter()
    unknown_entries = 0
    seen_names: set[str] = set()
    expected = spec["values"][0]
    for item in items:
        value = item.get("value", {})
        name = value.get("name")
        if name in seen_names:
            errors.append(f"duplicate summary result: {name}")
            continue
        seen_names.add(str(name))
        if value != expected:
            errors.append(f"summary value mismatch: {name}")
            continue
        state = str(item.get("state"))
        status = item.get("status")
        states[state] += 1
        statuses[str(status)] += 1
        local_path = repository / expected["output"]
        if Path(str(item.get("output", ""))).name != local_path.name:
            errors.append(f"summary basename mismatch: {name}")
        if state in {"completed", "reused"}:
            if status not in TERMINAL:
                errors.append(f"nonterminal completed result: {name}")
                continue
            if not local_path.is_file():
                errors.append(f"completed result file missing: {name}")
                continue
            if item.get("output_sha256") != digest(local_path):
                errors.append(f"summary output SHA mismatch: {name}")
            if record.get("state") != "terminal" or record.get("status") != status:
                errors.append(f"summary/payload terminal mismatch: {name}")
        else:
            unknown_entries += 1
    result.update(
        {
            "sha256": digest(summary_path),
            "finished": summary.get("finished"),
            "result_count": len(items),
            "states": dict(states),
            "statuses": dict(statuses),
            "unknown_entries": unknown_entries,
            "sat_present": any(item.get("status") == "sat" for item in items),
            "complete_unsat": (
                len(items) == 1
                and unknown_entries == 0
                and items[0].get("state") in {"completed", "reused"}
                and items[0].get("status") == "unsat"
            ),
            "integrity": not errors,
            "errors": errors,
        }
    )
    return result


def audit(spec_path: Path, summary_path: Path | None) -> dict[str, object]:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    proof = spec.get("proof_scope", {})
    repository = (spec_path.parent / spec["working_directory"]).resolve()
    values = list(spec.get("values", ()))
    value = values[0] if len(values) == 1 else {}
    fixed = tuple(str(value.get("fixed_kinds", "")).split(","))
    output = str(value.get("output", ""))
    actual_constraint = constraint_digest(fixed)
    structural = (
        len(values) == 1
        and fixed == FIXED_KINDS
        and value.get("name") == EXPECTED_NAME
        and output.endswith(f"/{EXPECTED_NAME}.json")
        and value.get("constraint_sha256") == actual_constraint
        and value.get("domain") == "s34567c8_leaf"
        and value.get("outputs") == "S5,S6,S7,C8"
        and int(value.get("gate", -1)) == 16
        and int(value.get("delay", -1)) == 5
        and int(value.get("components", -1)) == 10
        and int(value.get("ordinary", -1)) == 4
        and int(value.get("switches", -1)) == 6
        and int(value.get("xors", -1)) == 0
        and int(value.get("split_slots", -1)) == 1
        and int(value.get("shard_count", -1)) == 1
        and int(value.get("shard_index", -1)) == 0
        and value.get("solver") == "cadical195"
    )
    record: dict[str, object] = {
        "name": value.get("name"),
        "constraint_sha256_expected": value.get("constraint_sha256"),
        "constraint_sha256_actual": actual_constraint,
    }
    missing = invalid = unknown = 0
    sat_paths: list[str] = []
    path = repository / output
    record["path"] = str(path)
    if not structural:
        record["state"] = "invalid-manifest-value"
        invalid = 1
    elif not path.is_file():
        record["state"] = "missing"
        missing = 1
    else:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            payload = {}
            record.update({"state": "invalid-json", "error": repr(exc)})
            invalid = 1
        if payload:
            status = payload.get("status")
            checks = (
                payload.get("schema") == "exact-fast-negative-physical-shard-v2"
                and payload.get("domain") == "s34567c8_leaf"
                and tuple(payload.get("output_names", ())) == ("S5", "S6", "S7", "C8")
                and int(payload.get("rows", -1)) == 486
                and int(payload.get("gate_bound", -1)) == 16
                and int(payload.get("max_delay", -1)) == 5
                and int(payload.get("components", -1)) == 10
                and int(payload.get("ordinary", -1)) == 4
                and int(payload.get("exact_switches", -1)) == 6
                and int(payload.get("exact_xors", -1)) == 0
                and tuple(payload.get("fixed_kinds", ())) == FIXED_KINDS
                and payload.get("physical_nets") is True
                and payload.get("public_outputs_must_be_driven") is True
                and payload.get("dependency_sha256") == proof.get("dependency_sha256")
            )
            if status == "sat":
                verification = payload.get("verification", {})
                checks = checks and all(
                    int(verification.get(field, -1)) == 0 for field in ZERO_FIELDS
                )
                checks = checks and int(payload.get("actual_gate", 10**9)) <= 16
                checks = checks and int(
                    verification.get("actual_max_delay", 10**9)
                ) <= 5
            record.update(
                {
                    "status": status,
                    "sha256": digest(path),
                    "solve_seconds": payload.get("solve_seconds"),
                }
            )
            if not checks:
                record["state"] = "invalid-payload"
                invalid = 1
            elif status not in TERMINAL:
                record["state"] = "unknown"
                unknown = 1
            else:
                record["state"] = "terminal"
                if status == "sat":
                    sat_paths.append(str(path))

    constraint_record = [{"name": str(value.get("name")), "sha256": actual_constraint}]
    constraint_set_actual = sha256(
        json.dumps(
            constraint_record,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii")
    ).hexdigest()
    proof_matches = (
        proof.get("mode") == "fixed-topology"
        and proof.get("domain") == "s34567c8_leaf"
        and proof.get("outputs") == ["S5", "S6", "S7", "C8"]
        and int(proof.get("gate", -1)) == 16
        and int(proof.get("max_delay", -1)) == 5
        and int(proof.get("components", -1)) == 10
        and int(proof.get("ordinary", -1)) == 4
        and int(proof.get("switches", -1)) == 6
        and int(proof.get("xors", -1)) == 0
        and proof.get("fixed_topology") == list(FIXED_KINDS)
        and proof.get("coverage") == "complete-single-fixed-g16-all-switch-tail-class"
        and proof.get("unknown_is_not_unsat") is True
    )
    manifest_complete = (
        spec.get("schema") == "tc-byte-adder-remote-sweep-v1"
        and spec.get("script") == "physical_exact.py"
        and spec.get("stop_on_first_sat") is True
        and structural
        and proof_matches
        and constraint_set_actual == proof.get("constraint_set_sha256")
    )
    worker_match = proof.get("worker_sha256") == digest(WORKER)
    auditor_info = proof.get("auditor", {})
    auditor_match = (
        auditor_info.get("path")
        == str(Path(__file__).resolve().relative_to(ROOT)).replace("\\", "/")
        and auditor_info.get("sha256") == digest(Path(__file__).resolve())
    )
    dependency_errors = []
    for relative, expected in proof.get("dependency_sha256", {}).items():
        dependency = ROOT / relative
        if not dependency.is_file() or digest(dependency) != expected:
            dependency_errors.append(relative)
    dependency_match = not dependency_errors
    positive_match, positive_errors = positive_regression_check(proof)
    if summary_path is None:
        summary_path = (spec_path.parent / str(spec.get("summary", ""))).resolve()
    summary = audit_summary(
        summary_path=summary_path,
        spec_path=spec_path,
        spec=spec,
        repository=repository,
        record=record,
    )
    common_ready = (
        manifest_complete
        and worker_match
        and auditor_match
        and dependency_match
        and positive_match
        and not invalid
        and summary.get("integrity") is True
    )
    if sat_paths and common_ready and summary.get("sat_present") is True:
        status = "sat-witnesses"
    elif (
        common_ready
        and not missing
        and not unknown
        and record.get("status") == "unsat"
        and summary.get("complete_unsat") is True
    ):
        status = "unsat-covered"
    else:
        status = "incomplete"
    return {
        "schema": "s567c8-g16-o4-s6-all-switch-tail-audit-v1",
        "status": status,
        "coverage": proof.get("coverage"),
        "spec": str(spec_path),
        "spec_sha256": digest(spec_path),
        "worker_sha256_expected": proof.get("worker_sha256"),
        "worker_sha256_actual": digest(WORKER),
        "worker_sha256_match": worker_match,
        "auditor_sha256_expected": auditor_info.get("sha256"),
        "auditor_sha256_actual": digest(Path(__file__).resolve()),
        "auditor_sha256_match": auditor_match,
        "dependency_sha256_match": dependency_match,
        "dependency_errors": dependency_errors,
        "positive_regression_match": positive_match,
        "positive_regression_errors": positive_errors,
        "constraint_set_sha256_expected": proof.get("constraint_set_sha256"),
        "constraint_set_sha256_actual": constraint_set_actual,
        "manifest_complete": manifest_complete,
        "proof_scope_match": proof_matches,
        "jobs_expected": 1,
        "missing_jobs": missing,
        "invalid_jobs": invalid,
        "unknown_jobs": unknown,
        "sat_paths": sat_paths,
        "records": [record],
        "summary": summary,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("spec", type=Path)
    parser.add_argument("--summary", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = audit(
        args.spec.resolve(),
        args.summary.resolve() if args.summary is not None else None,
    )
    encoded = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0 if payload["status"] in {"sat-witnesses", "unsat-covered"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
