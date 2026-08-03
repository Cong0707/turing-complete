"""Verify transport and terminal-state integrity of the broad remote sweep."""

from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SEARCH_PATH = HERE / "exact_bit34_broad_c5_normal_form_shard.py"
RUNNER_PATH = HERE / "remote_broad_c5_sweep_stop_on_sat.py"


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_json(path: Path, payload: object) -> str:
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode(
        "utf-8"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(encoded)
    temporary.replace(path)
    return sha256(encoded).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--result-directory", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    summary_raw = args.summary.read_bytes()
    spec_raw = args.spec.read_bytes()
    summary = json.loads(summary_raw)
    spec = json.loads(spec_raw)
    errors = []
    if not isinstance(summary, dict) or not isinstance(spec, dict):
        raise ValueError("summary and spec must have JSON-object top levels")

    expected_values = spec.get("values")
    result_records = summary.get("results")
    if not isinstance(expected_values, list):
        expected_values = []
        errors.append("spec values is not a list")
    if not isinstance(result_records, list):
        result_records = []
        errors.append("summary results is not a list")

    expected_by_name = {
        str(value.get("name")): value
        for value in expected_values
        if isinstance(value, dict)
    }
    names = [
        str(record.get("value", {}).get("name"))
        for record in result_records
        if isinstance(record, dict) and isinstance(record.get("value"), dict)
    ]
    duplicate_names = sorted(
        name for name, count in Counter(names).items() if count > 1
    )
    if duplicate_names:
        errors.append(f"duplicate summary result names: {duplicate_names}")

    verified_results = []
    for record in result_records:
        if not isinstance(record, dict) or not isinstance(record.get("value"), dict):
            errors.append("summary contains a malformed result record")
            continue
        value = record["value"]
        name = str(value.get("name"))
        expected = expected_by_name.get(name)
        local_path = args.result_directory / f"{name}.json"
        item_errors = []
        if expected is None:
            item_errors.append("name is absent from spec")
        else:
            for field in ("components", "shard", "constraint_sha256"):
                if value.get(field) != expected.get(field):
                    item_errors.append(f"summary/spec {field} mismatch")
        if record.get("status") != "unsat":
            item_errors.append(f"non-UNSAT terminal status: {record.get('status')}")
        if record.get("state") not in {"completed", "reused"}:
            item_errors.append(f"nonterminal state: {record.get('state')}")
        if not local_path.is_file():
            item_errors.append("downloaded result is missing")
            local_sha256 = None
            artifact_status = None
        else:
            local_sha256 = file_sha256(local_path)
            if local_sha256 != record.get("output_sha256"):
                item_errors.append("downloaded SHA differs from remote summary")
            try:
                artifact = json.loads(local_path.read_text(encoding="utf-8"))
            except ValueError:
                artifact = None
                item_errors.append("downloaded artifact is malformed JSON")
            artifact_status = (
                artifact.get("status") if isinstance(artifact, dict) else None
            )
            if artifact_status != "unsat":
                item_errors.append(f"downloaded artifact status is {artifact_status}")
        if item_errors:
            errors.append(f"{name}: {item_errors}")
        verified_results.append(
            {
                "name": name,
                "status": record.get("status"),
                "state": record.get("state"),
                "remote_output_sha256": record.get("output_sha256"),
                "local_output_sha256": local_sha256,
                "artifact_status": artifact_status,
                "errors": item_errors,
            }
        )

    missing_summary_names = sorted(set(expected_by_name) - set(names))
    unexpected_summary_names = sorted(set(names) - set(expected_by_name))
    if missing_summary_names:
        errors.append(f"summary missing names: {missing_summary_names}")
    if unexpected_summary_names:
        errors.append(f"summary has unexpected names: {unexpected_summary_names}")

    top_level_checks = {
        "schema": summary.get("schema")
        == "tc-byte-adder-remote-broad-c5-summary-v1",
        "finished": summary.get("finished") is True,
        "not_stopped_on_sat": summary.get("stopped_on_sat") is False,
        "no_sat_hit": summary.get("sat_hit") is None,
        "terminal_count_230": summary.get("terminal_result_count") == 230,
        "total_count_230": summary.get("total_value_count") == 230,
        "results_count_230": len(result_records) == 230,
        "spec_sha256": summary.get("spec_sha256") == sha256(spec_raw).hexdigest(),
        "search_sha256": summary.get("script_sha256") == file_sha256(SEARCH_PATH),
        "runner_sha256": summary.get("runner_sha256") == file_sha256(RUNNER_PATH),
        "remaining_empty": summary.get("remaining_values") == [],
    }
    failed_top_level = sorted(
        key for key, passed in top_level_checks.items() if not passed
    )
    if failed_top_level:
        errors.append(f"failed summary checks: {failed_top_level}")

    payload = {
        "schema": "tc-byte-adder-bit34-broad-c5-remote-transport-verify-v1",
        "summary": str(args.summary.resolve()),
        "summary_sha256": sha256(summary_raw).hexdigest(),
        "spec": str(args.spec.resolve()),
        "spec_sha256": sha256(spec_raw).hexdigest(),
        "result_directory": str(args.result_directory.resolve()),
        "top_level_checks": top_level_checks,
        "failed_top_level_checks": failed_top_level,
        "expected_results": len(expected_values),
        "summary_results": len(result_records),
        "verified_results": len(verified_results),
        "duplicate_names": duplicate_names,
        "missing_summary_names": missing_summary_names,
        "unexpected_summary_names": unexpected_summary_names,
        "errors": errors,
        "ok": not errors,
        "results": verified_results,
        "script_sha256": file_sha256(Path(__file__).resolve()),
    }
    output_sha256 = atomic_json(args.output, payload)
    print(
        json.dumps(
            {
                "ok": payload["ok"],
                "expected": payload["expected_results"],
                "summary_results": payload["summary_results"],
                "errors": len(errors),
                "summary_sha256": payload["summary_sha256"],
                "output_sha256": output_sha256,
            },
            separators=(",", ":"),
        )
    )
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
