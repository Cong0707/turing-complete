"""Strictly audit the g17/o5/s6 three-early-Switch mid-BUS matrix."""

from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORKER = HERE / "physical_exact.py"
FIXED_PREFIX = ("NOT", "NOR", "OR", "OR", "SWITCH", "SWITCH", "SWITCH")
FIXED_SUFFIX = ("SWITCH",) * 3
ORDINARY_KINDS = ("NOT", "AND", "OR", "NAND", "NOR")
EXPECTED_KINDS = set(ORDINARY_KINDS)
KIND_PRIORITY = ("OR",) + tuple(kind for kind in ORDINARY_KINDS if kind != "OR")
TERMINAL = {"sat", "unsat"}
JOB_COUNT = 5
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
    expected_fixed = (*FIXED_PREFIX, "OR", *FIXED_SUFFIX)
    if payload.get("status") != "verified-positive-regression":
        errors.append("positive regression status mismatch")
    if verification.get("verified") is not True:
        errors.append("positive regression verification is not true")
    if tuple(regression.get("fixed_kinds", ())) != expected_fixed:
        errors.append("positive regression topology mismatch")
    if regression.get("output_names") != ["S7", "C8"]:
        errors.append("positive regression output scope mismatch")
    if verification.get("rows") != 486:
        errors.append("positive regression row count mismatch")
    if verification.get("actual_gate") != 17:
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
    records_by_name: dict[str, dict[str, object]],
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
    expected_values = {value["name"]: value for value in spec.get("values", ())}
    seen: set[str] = set()
    states: Counter[str] = Counter()
    statuses: Counter[str] = Counter()
    unknown_entries = 0
    for item in summary.get("results", ()):
        value = item.get("value", {})
        name = value.get("name")
        if name in seen:
            errors.append(f"duplicate summary result: {name}")
            continue
        seen.add(name)
        expected = expected_values.get(name)
        if expected is None or value != expected:
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
            record = records_by_name.get(str(name), {})
            if record.get("state") != "terminal" or record.get("status") != status:
                errors.append(f"summary/payload terminal mismatch: {name}")
        else:
            unknown_entries += 1
    result.update(
        {
            "sha256": digest(summary_path),
            "finished": summary.get("finished"),
            "result_count": len(summary.get("results", ())),
            "states": dict(states),
            "statuses": dict(statuses),
            "unknown_entries": unknown_entries,
            "sat_present": any(
                item.get("status") == "sat" for item in summary.get("results", ())
            ),
            "complete_unsat": (
                len(summary.get("results", ())) == JOB_COUNT
                and unknown_entries == 0
                and all(
                    item.get("state") in {"completed", "reused"}
                    and item.get("status") == "unsat"
                    for item in summary.get("results", ())
                )
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
    seen_kinds: set[str] = set()
    seen_names: set[str] = set()
    seen_outputs: set[str] = set()
    overlaps = 0
    constraint_records: list[dict[str, str]] = []
    records: list[dict[str, object]] = []
    missing = invalid = unknown = 0
    sat_paths: list[str] = []

    for value in spec.get("values", ()):
        fixed = tuple(str(value.get("fixed_kinds", "")).split(","))
        kind = fixed[7] if len(fixed) == 11 else ""
        actual_constraint = constraint_digest(fixed)
        name = str(value.get("name"))
        output = str(value.get("output", ""))
        expected_name = (
            f"s567c8-d5-g17-o05-s06-midbus3-{kind.lower()}"
            if kind in EXPECTED_KINDS
            else ""
        )
        record: dict[str, object] = {
            "name": value.get("name"),
            "kind": kind,
            "constraint_sha256_expected": value.get("constraint_sha256"),
            "constraint_sha256_actual": actual_constraint,
        }
        structural = (
            len(fixed) == 11
            and fixed[:7] == FIXED_PREFIX
            and kind in EXPECTED_KINDS
            and fixed[8:] == FIXED_SUFFIX
            and name == expected_name
            and output.endswith(f"/{expected_name}.json")
            and value.get("constraint_sha256") == actual_constraint
            and value.get("domain") == "s34567c8_leaf"
            and value.get("outputs") == "S5,S6,S7,C8"
            and int(value.get("gate", -1)) == 17
            and int(value.get("delay", -1)) == 5
            and int(value.get("components", -1)) == 11
            and int(value.get("ordinary", -1)) == 5
            and int(value.get("switches", -1)) == 6
            and int(value.get("xors", -1)) == 0
            and int(value.get("split_slots", -1)) == 1
            and int(value.get("shard_count", -1)) == 1
            and int(value.get("shard_index", -1)) == 0
            and value.get("solver") == "cadical195"
        )
        if kind in seen_kinds or name in seen_names or output in seen_outputs:
            overlaps += 1
        if kind:
            seen_kinds.add(kind)
        seen_names.add(name)
        seen_outputs.add(output)
        constraint_records.append({"name": name, "sha256": actual_constraint})
        path = repository / output
        record["path"] = str(path)
        if not structural:
            record["state"] = "invalid-manifest-value"
            invalid += 1
            records.append(record)
            continue
        if not path.is_file():
            record["state"] = "missing"
            missing += 1
            records.append(record)
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            record.update({"state": "invalid-json", "error": repr(exc)})
            invalid += 1
            records.append(record)
            continue
        status = payload.get("status")
        checks = (
            payload.get("schema") == "exact-fast-negative-physical-shard-v2"
            and payload.get("domain") == "s34567c8_leaf"
            and tuple(payload.get("output_names", ())) == ("S5", "S6", "S7", "C8")
            and int(payload.get("rows", -1)) == 486
            and int(payload.get("gate_bound", -1)) == 17
            and int(payload.get("max_delay", -1)) == 5
            and int(payload.get("components", -1)) == 11
            and int(payload.get("ordinary", -1)) == 5
            and int(payload.get("exact_switches", -1)) == 6
            and int(payload.get("exact_xors", -1)) == 0
            and tuple(payload.get("fixed_kinds", ())) == fixed
            and payload.get("physical_nets") is True
            and payload.get("public_outputs_must_be_driven") is True
            and payload.get("dependency_sha256") == proof.get("dependency_sha256")
        )
        if status == "sat":
            verification = payload.get("verification", {})
            checks = checks and all(
                int(verification.get(field, -1)) == 0 for field in ZERO_FIELDS
            )
            checks = checks and int(payload.get("actual_gate", 10**9)) <= 17
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
            invalid += 1
        elif status not in TERMINAL:
            record["state"] = "unknown"
            unknown += 1
        else:
            record["state"] = "terminal"
            if status == "sat":
                sat_paths.append(str(path))
        records.append(record)

    constraint_set_actual = sha256(
        json.dumps(
            constraint_records,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii")
    ).hexdigest()
    expected_topology = [*FIXED_PREFIX, "ordinary-kind-slot", *FIXED_SUFFIX]
    proof_matches = (
        proof.get("mode") == "matrix"
        and proof.get("domain") == "s34567c8_leaf"
        and proof.get("outputs") == ["S5", "S6", "S7", "C8"]
        and int(proof.get("gate", -1)) == 17
        and int(proof.get("max_delay", -1)) == 5
        and int(proof.get("components", -1)) == 11
        and int(proof.get("ordinary", -1)) == 5
        and int(proof.get("switches", -1)) == 6
        and int(proof.get("xors", -1)) == 0
        and proof.get("fixed_prefix") == list(FIXED_PREFIX[:4])
        and proof.get("early_switch_slots_zero_based") == [4, 5, 6]
        and proof.get("variable_ordinary_slots_zero_based") == [7]
        and proof.get("terminal_switch_slots_zero_based") == [8, 9, 10]
        and proof.get("ordinary_kinds") == list(ORDINARY_KINDS)
        and int(proof.get("ordered_kind_count", -1)) == JOB_COUNT
        and proof.get("kind_execution_order") == list(KIND_PRIORITY)
        and proof.get("fixed_topology") == expected_topology
        and proof.get("coverage") == "complete-5-way-partition-of-midbus3-one-slot-class"
        and proof.get("unknown_is_not_unsat") is True
    )
    manifest_complete = (
        spec.get("schema") == "tc-byte-adder-remote-sweep-v1"
        and spec.get("script") == "physical_exact.py"
        and spec.get("stop_on_first_sat") is True
        and len(spec.get("values", ())) == JOB_COUNT
        and seen_kinds == EXPECTED_KINDS
        and len(seen_names) == JOB_COUNT
        and len(seen_outputs) == JOB_COUNT
        and overlaps == 0
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
        path = ROOT / relative
        if not path.is_file() or digest(path) != expected:
            dependency_errors.append(relative)
    dependency_match = not dependency_errors
    positive_match, positive_errors = positive_regression_check(proof)
    records_by_name = {str(record.get("name")): record for record in records}
    if summary_path is None:
        summary_path = (spec_path.parent / str(spec.get("summary", ""))).resolve()
    summary = audit_summary(
        summary_path=summary_path,
        spec_path=spec_path,
        spec=spec,
        repository=repository,
        records_by_name=records_by_name,
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
        and all(record.get("status") == "unsat" for record in records)
        and summary.get("complete_unsat") is True
    ):
        status = "unsat-covered"
    else:
        status = "incomplete"
    return {
        "schema": "s567c8-g17-o5-s6-midbus3-one-slot-audit-v1",
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
        "kinds_expected": JOB_COUNT,
        "kinds_seen": len(seen_kinds),
        "overlap_count": overlaps,
        "jobs_expected": JOB_COUNT,
        "missing_jobs": missing,
        "invalid_jobs": invalid,
        "unknown_jobs": unknown,
        "sat_paths": sat_paths,
        "records": records,
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
