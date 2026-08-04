"""Independent basename/SHA cross-check for the fixed g16 result."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path


FIXED_KINDS = ("NOT", "NOR", "OR", "OR", *("SWITCH" for _ in range(6)))
EXPECTED_NAME = "s567c8-d5-g16-o04-s06-all-switch-tail"
TERMINAL_STATES = {"completed", "reused"}


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def crosscheck(spec_path: Path, summary_path: Path) -> dict[str, object]:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    repository = (spec_path.parent / spec["working_directory"]).resolve()
    worker_path = spec_path.parent / spec["script"]
    errors: list[str] = []

    values = list(spec.get("values", ()))
    value = values[0] if len(values) == 1 else {}
    result_path = (repository / str(value.get("output", ""))).resolve()
    result_directory = result_path.parent
    items = list(summary.get("results", ()))
    item = items[0] if len(items) == 1 else {}
    payload: dict[str, object] = {}
    if result_path.is_file():
        try:
            payload = json.loads(result_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            errors.append(f"payload JSON error: {exc!r}")
    else:
        errors.append("payload missing")

    expected_files = {result_path.name}
    actual_files = (
        {path.name for path in result_directory.glob("*.json")}
        if result_directory.is_dir()
        else set()
    )
    proof = spec.get("proof_scope", {})
    checks = {
        "single_manifest_value": len(values) == 1,
        "manifest_name": value.get("name") == EXPECTED_NAME,
        "manifest_topology": tuple(str(value.get("fixed_kinds", "")).split(","))
        == FIXED_KINDS,
        "single_summary_result": len(items) == 1,
        "summary_finished": summary.get("finished") is True,
        "summary_value_equal": item.get("value") == value,
        "summary_basename_equal": Path(str(item.get("output", ""))).name
        == result_path.name,
        "terminal_state": item.get("state") in TERMINAL_STATES,
        "summary_status_unsat": item.get("status") == "unsat",
        "payload_status_equal": payload.get("status") == item.get("status"),
        "payload_topology_equal": tuple(payload.get("fixed_kinds", ()))
        == FIXED_KINDS,
        "payload_shape_equal": (
            payload.get("gate_bound"),
            payload.get("max_delay"),
            payload.get("components"),
            payload.get("ordinary"),
            payload.get("exact_switches"),
            payload.get("exact_xors"),
            payload.get("rows"),
        )
        == (16, 5, 10, 4, 6, 0, 486),
        "payload_sha_equal": (
            result_path.is_file() and digest(result_path) == item.get("output_sha256")
        ),
        "spec_sha_equal": summary.get("spec_sha256") == digest(spec_path),
        "worker_sha_equal": (
            summary.get("script_sha256")
            == proof.get("worker_sha256")
            == digest(worker_path)
        ),
        "directory_exact": expected_files == actual_files,
        "no_timeout": item.get("state") in TERMINAL_STATES,
    }
    errors.extend(name for name, passed in checks.items() if not passed)
    return {
        "schema": "s567c8-g16-o4-s6-all-switch-tail-crosscheck-v1",
        "status": "verified" if not errors else "invalid",
        "path_mapping": "basename(summary.output) -> local manifest result directory",
        "spec": str(spec_path),
        "spec_sha256": digest(spec_path),
        "summary": str(summary_path),
        "summary_sha256": digest(summary_path),
        "worker": str(worker_path.resolve()),
        "worker_sha256": digest(worker_path),
        "result_directory": str(result_directory),
        "jobs_expected": 1,
        "jobs_seen": len(items),
        "file_count": len(actual_files),
        "completed": sum(item.get("state") == "completed" for item in items),
        "reused": sum(item.get("state") == "reused" for item in items),
        "mismatch_count": len(errors),
        "errors": errors,
        "checks": checks,
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
