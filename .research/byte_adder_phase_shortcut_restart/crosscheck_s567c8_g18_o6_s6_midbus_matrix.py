"""Cross-check the remote mid-BUS matrix summary against local payloads.

The runner stores absolute Ubuntu output paths.  Map each path by basename to
the result directory declared by the local spec, then independently compare
manifest values, terminal states, payload statuses, and SHA-256 digests.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import itertools
import json
from pathlib import Path


TERMINAL_STATES = {"completed", "reused"}
ORDINARY_KINDS = ("NOT", "AND", "OR", "NAND", "NOR")
EXPECTED_PAIRS = set(itertools.product(ORDINARY_KINDS, repeat=2))
FIXED_PREFIX = ("NOT", "NOR", "OR", "OR", "SWITCH", "SWITCH")
FIXED_SUFFIX = ("SWITCH",) * 4


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def crosscheck(spec_path: Path, summary_path: Path) -> dict[str, object]:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    repository = (spec_path.parent / spec["working_directory"]).resolve()
    worker_path = spec_path.parent / spec["script"]

    errors: list[str] = []
    spec_values: dict[str, dict[str, object]] = {}
    pairs: set[tuple[str, str]] = set()
    for value in spec.get("values", ()):
        name = str(value.get("name"))
        if name in spec_values:
            errors.append(f"duplicate manifest value: {name}")
        spec_values[name] = value
        fixed = tuple(str(value.get("fixed_kinds", "")).split(","))
        if (
            len(fixed) != 12
            or fixed[:6] != FIXED_PREFIX
            or fixed[8:] != FIXED_SUFFIX
            or fixed[6:8] not in EXPECTED_PAIRS
        ):
            errors.append(f"invalid fixed topology: {name}")
        else:
            pairs.add((fixed[6], fixed[7]))

    summary_values: dict[str, dict[str, object]] = {}
    for record in summary.get("results", ()):
        value = record.get("value", {})
        name = str(value.get("name"))
        if name in summary_values:
            errors.append(f"duplicate summary result: {name}")
        summary_values[name] = record

    if set(spec_values) != set(summary_values):
        missing = sorted(set(spec_values) - set(summary_values))
        extra = sorted(set(summary_values) - set(spec_values))
        errors.append(f"summary name-set mismatch: missing={missing}, extra={extra}")

    output_parents = {
        (repository / str(value["output"])).parent.resolve()
        for value in spec_values.values()
    }
    if len(output_parents) != 1:
        errors.append(f"manifest uses multiple result directories: {output_parents}")
        result_directory = repository
    else:
        result_directory = next(iter(output_parents))

    records: list[dict[str, object]] = []
    for name, value in spec_values.items():
        expected_path = (repository / str(value["output"])).resolve()
        expected_basename = expected_path.name
        summary_record = summary_values.get(name)
        record: dict[str, object] = {
            "name": name,
            "expected_basename": expected_basename,
            "local_path": str(expected_path),
        }
        if summary_record is None:
            record["state"] = "missing-summary-record"
            records.append(record)
            continue

        summary_output = Path(str(summary_record.get("output", ""))).name
        state = summary_record.get("state")
        status = summary_record.get("status")
        summary_sha = summary_record.get("output_sha256")
        local_sha = digest(expected_path) if expected_path.is_file() else None
        payload_status = None
        payload_fixed: tuple[str, ...] = ()
        if expected_path.is_file():
            try:
                payload = json.loads(expected_path.read_text(encoding="utf-8"))
                payload_status = payload.get("status")
                payload_fixed = tuple(payload.get("fixed_kinds", ()))
            except (OSError, ValueError) as exc:
                errors.append(f"invalid local result {name}: {exc!r}")

        manifest_fixed = tuple(str(value["fixed_kinds"]).split(","))
        checks = {
            "manifest_value_equal": summary_record.get("value") == value,
            "basename_equal": summary_output == expected_basename,
            "terminal_state": state in TERMINAL_STATES,
            "summary_status_unsat": status == "unsat",
            "payload_status_equal": payload_status == status,
            "payload_topology_equal": payload_fixed == manifest_fixed,
            "sha256_equal": local_sha == summary_sha,
        }
        for check, passed in checks.items():
            if not passed:
                errors.append(f"{name}: {check} failed")
        record.update(
            {
                "state": state,
                "status": status,
                "summary_basename": summary_output,
                "summary_sha256": summary_sha,
                "local_sha256": local_sha,
                "checks": checks,
            }
        )
        records.append(record)

    expected_files = {
        Path(str(value["output"])).name for value in spec_values.values()
    }
    actual_files = (
        {path.name for path in result_directory.glob("*.json")}
        if result_directory.is_dir()
        else set()
    )
    if expected_files != actual_files:
        errors.append(
            "result directory mismatch: "
            f"missing={sorted(expected_files - actual_files)}, "
            f"extra={sorted(actual_files - expected_files)}"
        )

    proof = spec.get("proof_scope", {})
    top_checks = {
        "summary_finished": summary.get("finished") is True,
        "result_count_25": len(summary_values) == 25,
        "ordered_pairs_complete": pairs == EXPECTED_PAIRS,
        "spec_sha256_equal": summary.get("spec_sha256") == digest(spec_path),
        "worker_sha256_equal": (
            summary.get("script_sha256")
            == proof.get("worker_sha256")
            == digest(worker_path)
        ),
        "all_unsat": all(
            record.get("status") == "unsat"
            for record in summary.get("results", ())
        ),
        "no_timeout": all(
            record.get("state") in TERMINAL_STATES
            for record in summary.get("results", ())
        ),
        "directory_exact": expected_files == actual_files,
    }
    for check, passed in top_checks.items():
        if not passed:
            errors.append(f"top-level check failed: {check}")

    return {
        "schema": "s567c8-g18-o6-s6-midbus-matrix-crosscheck-v1",
        "status": "verified" if not errors else "invalid",
        "path_mapping": "basename(summary.output) -> local manifest result directory",
        "spec": str(spec_path),
        "spec_sha256": digest(spec_path),
        "summary": str(summary_path),
        "summary_sha256": digest(summary_path),
        "worker": str(worker_path.resolve()),
        "worker_sha256": digest(worker_path),
        "result_directory": str(result_directory),
        "jobs_expected": len(spec_values),
        "jobs_seen": len(summary_values),
        "pairs_seen": len(pairs),
        "file_count": len(actual_files),
        "reused": sum(
            record.get("state") == "reused"
            for record in summary.get("results", ())
        ),
        "completed": sum(
            record.get("state") == "completed"
            for record in summary.get("results", ())
        ),
        "mismatch_count": len(errors),
        "errors": errors,
        "checks": top_checks,
        "records": records,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("spec", type=Path)
    parser.add_argument("summary", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = crosscheck(args.spec.resolve(), args.summary.resolve())
    encoded = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0 if payload["status"] == "verified" else 1


if __name__ == "__main__":
    raise SystemExit(main())
