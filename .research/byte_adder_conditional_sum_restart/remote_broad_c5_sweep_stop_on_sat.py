"""Three-worker stop-on-SAT runner for the broad C5 normal-form sweep.

This is a new derivative and does not modify the already running 49-shard
runner.  It reuses the reviewed bounded-dispatch and process-group shutdown
implementation, while validating the exact 230-shard broad domain and frozen
file hashes before launch.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys

import bit34_broad_c5_normal_form as normal_form


HERE = Path(__file__).resolve().parent
FROZEN_STOP_RUNNER_PATH = HERE / "remote_sweep_stop_on_sat.py"
MAX_WORKERS = 3
MAX_SCHEDULED_MEMORY_MB = 3 * 4096
MIN_NICE = 10
GATE_BOUND = 13


def load_frozen_runner():
    spec = importlib.util.spec_from_file_location(
        "bit34_broad_frozen_stop_runner",
        FROZEN_STOP_RUNNER_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load frozen runner: {FROZEN_STOP_RUNNER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


frozen = load_frozen_runner()
base = frozen.base


def projected_value(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        return {"invalid": value}
    return {
        key: value.get(key)
        for key in ("name", "components", "shard", "constraint_sha256")
    }


def parsed_int(spec: dict[str, object], key: str, errors: list[str]) -> int:
    try:
        return int(spec.get(key, 0))
    except (TypeError, ValueError):
        errors.append(f"{key} is not an integer")
        return 0


def validate_spec_payload(spec_path: Path) -> dict[str, object]:
    spec_path = spec_path.resolve()
    errors = []
    try:
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return {
            "ok": False,
            "spec": str(spec_path),
            "errors": [f"cannot read spec: {exc}"],
        }

    if spec.get("schema") != "tc-byte-adder-remote-sweep-v1":
        errors.append("unsupported schema")
    if spec.get("runner") != Path(__file__).name:
        errors.append("spec runner does not name this broad runner")
    if spec.get("script") != "exact_bit34_broad_c5_normal_form_shard.py":
        errors.append("spec names the wrong search script")
    if spec.get("stop_on_first_sat") is not True:
        errors.append("stop_on_first_sat must be true")
    if spec.get("resume_terminal_outputs") is not True:
        errors.append("resume_terminal_outputs must be true")

    workers = parsed_int(spec, "workers", errors)
    memory_mb = parsed_int(spec, "memory_mb_per_process", errors)
    nice = parsed_int(spec, "nice", errors)
    if not 1 <= workers <= MAX_WORKERS:
        errors.append(f"workers must be between 1 and {MAX_WORKERS}")
    if memory_mb <= 0 or workers * memory_mb > MAX_SCHEDULED_MEMORY_MB:
        errors.append(
            "scheduled memory must be positive and no more than "
            f"{MAX_SCHEDULED_MEMORY_MB} MiB"
        )
    if not MIN_NICE <= nice <= 19:
        errors.append(
            f"nice must be {MIN_NICE}..19 so the existing nice=5 sweep wins"
        )

    expected = normal_form.shard_records(GATE_BOUND, range(GATE_BOUND + 1))
    values = spec.get("values")
    if not isinstance(values, list):
        values = []
        errors.append("values is not a list")
    projected = [projected_value(value) for value in values]
    if projected != expected:
        errors.append("values are not the canonical ordered 230-shard domain")

    expected_arguments = [
        "--gate-bound",
        "13",
        "--components",
        "{components}",
        "--shard",
        "{shard}",
        "--solver",
        "cadical195",
        "--timeout",
        "0",
        "--output",
        "results/bit34_d7_g13_broad_c5_normal_form/{name}.json",
    ]
    if spec.get("arguments") != expected_arguments:
        errors.append("arguments do not match the frozen broad command template")

    required = spec.get("required_files")
    required_hashes = spec.get("required_file_sha256")
    if not isinstance(required, list) or any(
        not isinstance(item, str) for item in required
    ):
        required = []
        errors.append("required_files is not a list of strings")
    if not isinstance(required_hashes, dict):
        required_hashes = {}
        errors.append("required_file_sha256 is not an object")
    if set(required) != set(required_hashes):
        errors.append("required_files and required_file_sha256 keys differ")
    file_checks = []
    for raw_path in required:
        path = Path(str(raw_path))
        path = path if path.is_absolute() else spec_path.parent / path
        path = path.resolve()
        if not path.is_file():
            errors.append(f"required file missing: {path}")
            file_checks.append(
                {"path": str(path), "expected_sha256": required_hashes.get(raw_path)}
            )
            continue
        actual = base.sha256(path)
        expected_hash = required_hashes.get(raw_path)
        if actual != expected_hash:
            errors.append(f"required file hash mismatch: {raw_path}")
        file_checks.append(
            {
                "path": str(path),
                "expected_sha256": expected_hash,
                "actual_sha256": actual,
                "matches": actual == expected_hash,
            }
        )

    partition = spec.get("partition")
    if not isinstance(partition, dict):
        partition = {}
    if partition.get("shard_count") != 230:
        errors.append("partition shard_count must be 230")
    if partition.get("gate_bound") != GATE_BOUND:
        errors.append("partition gate_bound must be 13")
    if partition.get("component_shard_counts") != normal_form.component_shard_counts(
        GATE_BOUND
    ):
        errors.append("partition component_shard_counts mismatch")

    return {
        "ok": not errors,
        "spec": str(spec_path),
        "spec_sha256": base.sha256(spec_path),
        "workers": workers,
        "worker_limit": MAX_WORKERS,
        "memory_mb_per_process": memory_mb,
        "maximum_scheduled_memory_mb": workers * memory_mb,
        "maximum_scheduled_memory_limit_mb": MAX_SCHEDULED_MEMORY_MB,
        "nice": nice,
        "minimum_nice": MIN_NICE,
        "stop_on_first_sat": spec.get("stop_on_first_sat"),
        "resume_terminal_outputs": spec.get("resume_terminal_outputs"),
        "shards": len(values),
        "canonical_domain_exact": projected == expected,
        "required_file_checks": file_checks,
        "errors": errors,
    }


class BroadC5StopOnSatSweep(frozen.StopOnSatSweep):
    def __init__(self, spec_path: Path) -> None:
        validation = validate_spec_payload(spec_path)
        if not validation["ok"]:
            raise ValueError(f"invalid broad spec: {validation['errors']}")
        # Bypass the frozen derivative's workers=2 assertion while retaining
        # all of its bounded-dispatch, resume, and stop-on-SAT methods.
        base.Sweep.__init__(self, spec_path, dry_run=False)
        if not 1 <= self.workers <= MAX_WORKERS:
            raise ValueError(f"workers must be between 1 and {MAX_WORKERS}")
        if self.workers * self.memory_mb > MAX_SCHEDULED_MEMORY_MB:
            raise ValueError("scheduled memory exceeds the broad sweep limit")
        if self.nice < MIN_NICE:
            raise ValueError("broad sweep priority would compete with existing sweep")
        self.poll_seconds = float(self.spec.get("poll_seconds", 0.5))
        if not 0.1 <= self.poll_seconds <= 10:
            raise ValueError("poll_seconds must be between 0.1 and 10")

    def write_summary(self, *, finished: bool = False) -> None:
        ordered = self.ordered_results()
        sat_records = [record for record in ordered if record.get("status") == "sat"]
        payload = {
            "schema": "tc-byte-adder-remote-broad-c5-summary-v1",
            "name": self.name,
            "spec": str(self.spec_path),
            "spec_sha256": base.sha256(self.spec_path),
            "script": str(self.script),
            "script_sha256": base.sha256(self.script),
            "runner": str(Path(__file__).resolve()),
            "runner_sha256": base.sha256(Path(__file__).resolve()),
            "frozen_stop_runner": str(FROZEN_STOP_RUNNER_PATH),
            "frozen_stop_runner_sha256": base.sha256(FROZEN_STOP_RUNNER_PATH),
            "base_runner": str(frozen.BASE_RUNNER_PATH),
            "base_runner_sha256": base.sha256(frozen.BASE_RUNNER_PATH),
            "normal_form": str(Path(normal_form.__file__).resolve()),
            "normal_form_sha256": base.sha256(Path(normal_form.__file__).resolve()),
            "python": sys.version,
            "workers": self.workers,
            "worker_limit": MAX_WORKERS,
            "timeout_seconds": self.timeout,
            "memory_mb_per_process": self.memory_mb,
            "maximum_scheduled_memory_mb": self.workers * self.memory_mb,
            "maximum_scheduled_memory_limit_mb": MAX_SCHEDULED_MEMORY_MB,
            "nice": self.nice,
            "priority_note": "existing 49-shard sweep remains at nice=5",
            "cpu_set": sorted(self.cpu_set) if self.cpu_set else None,
            "poll_seconds": self.poll_seconds,
            "resume_terminal_outputs": True,
            "stop_on_first_sat": True,
            "stopped_on_sat": bool(sat_records),
            "sat_hit": sat_records[0] if sat_records else None,
            "updated_at": base.utc_now(),
            "finished": finished,
            "terminal_result_count": sum(
                record.get("status") in base.TERMINAL_STATUSES
                for record in ordered
            ),
            "total_value_count": len(self.values),
            "remaining_values": self.remaining_values(),
            "results": ordered,
        }
        base.atomic_json(self.summary_path, payload)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("spec", type=Path)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    if args.validate_only:
        report = validate_spec_payload(args.spec)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report["ok"] else 2
    return BroadC5StopOnSatSweep(args.spec).run()


if __name__ == "__main__":
    raise SystemExit(main())
