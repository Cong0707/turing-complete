"""Resumable two-worker sweep that stops the queue on the first SAT result.

This runner reuses the reviewed command construction, hashing, resource limits,
and process-group termination helpers from ``remote_sweep.py``.  Unlike the
generic runner, it submits at most ``workers`` tasks at a time.  A SAT result
sets a shared stop event, prevents further dispatch, and terminates any sibling
process still running.  On restart, terminal SAT/UNSAT output JSONs are scanned
before any process is launched and are recorded as reused checkpoints.
"""

from __future__ import annotations

import argparse
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE_RUNNER_PATH = ROOT / ".research/byte_adder_remote_compute/remote_sweep.py"


def load_base_runner():
    spec = importlib.util.spec_from_file_location("bit34_remote_sweep_base", BASE_RUNNER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load base runner: {BASE_RUNNER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


base = load_base_runner()


def value_key(value: object) -> str:
    return base.safe_value_name(value)


class StopOnSatSweep(base.Sweep):
    def __init__(self, spec_path: Path) -> None:
        super().__init__(spec_path, dry_run=False)
        if self.spec.get("stop_on_first_sat") is not True:
            raise ValueError("spec must set stop_on_first_sat=true")
        if self.spec.get("resume_terminal_outputs") is not True:
            raise ValueError("spec must set resume_terminal_outputs=true")
        if self.workers != 2:
            raise ValueError("the reviewed remote kind-shard budget requires workers=2")
        self.poll_seconds = float(self.spec.get("poll_seconds", 0.5))
        if not 0.1 <= self.poll_seconds <= 10:
            raise ValueError("poll_seconds must be between 0.1 and 10")
        self.stop_event = threading.Event()

    def reusable_record(self, value: object) -> dict[str, Any] | None:
        _command, output = self.command_for(value)
        status = base.read_status(output)
        if status not in base.TERMINAL_STATUSES:
            return None
        return {
            "value": value,
            "status": status,
            "state": "reused",
            "output": str(output),
            "output_sha256": base.sha256(output),
            "finished_at": base.utc_now(),
        }

    def preload_terminal_outputs(self) -> None:
        for value in self.values:
            record = self.reusable_record(value)
            if record is None:
                continue
            self.results[value_key(value)] = record
            if record["status"] == "sat":
                self.stop_event.set()

    def ordered_results(self) -> list[dict[str, Any]]:
        return [
            self.results[value_key(value)]
            for value in self.values
            if value_key(value) in self.results
        ]

    def remaining_values(self) -> list[object]:
        terminal = {
            key
            for key, record in self.results.items()
            if record.get("status") in base.TERMINAL_STATUSES
        }
        return [value for value in self.values if value_key(value) not in terminal]

    def write_summary(self, *, finished: bool = False) -> None:
        ordered = self.ordered_results()
        sat_records = [record for record in ordered if record.get("status") == "sat"]
        payload = {
            "schema": "tc-byte-adder-remote-sweep-summary-v1",
            "name": self.name,
            "spec": str(self.spec_path),
            "spec_sha256": base.sha256(self.spec_path),
            "script": str(self.script),
            "script_sha256": base.sha256(self.script),
            "runner": str(Path(__file__).resolve()),
            "runner_sha256": base.sha256(Path(__file__).resolve()),
            "base_runner": str(BASE_RUNNER_PATH),
            "base_runner_sha256": base.sha256(BASE_RUNNER_PATH),
            "python": sys.version,
            "workers": self.workers,
            "timeout_seconds": self.timeout,
            "memory_mb_per_process": self.memory_mb,
            "nice": self.nice,
            "cpu_set": sorted(self.cpu_set) if self.cpu_set else None,
            "poll_seconds": self.poll_seconds,
            "resume_terminal_outputs": True,
            "stop_on_first_sat": True,
            "stopped_on_sat": bool(sat_records),
            "sat_hit": sat_records[0] if sat_records else None,
            "updated_at": base.utc_now(),
            "finished": finished,
            "terminal_result_count": sum(
                record.get("status") in base.TERMINAL_STATUSES for record in ordered
            ),
            "total_value_count": len(self.values),
            "remaining_values": self.remaining_values(),
            "results": ordered,
        }
        base.atomic_json(self.summary_path, payload)

    def run_one(self, value: object) -> dict[str, Any]:
        reusable = self.reusable_record(value)
        if reusable is not None:
            if reusable["status"] == "sat":
                self.stop_event.set()
            return reusable
        if self.stop_event.is_set():
            return {
                "value": value,
                "state": "not-started-after-sat",
                "finished_at": base.utc_now(),
            }

        safe_name = value_key(value)
        command, output = self.command_for(value)
        if output is not None:
            output.parent.mkdir(parents=True, exist_ok=True)
        log_path = self.log_directory / f"{safe_name}.log"
        record_path = self.result_directory / f"{safe_name}.json"
        started = time.monotonic()
        record: dict[str, Any] = {
            "value": value,
            "state": "running",
            "command": command,
            "working_directory": str(self.working_directory),
            "output": str(output) if output else None,
            "log": str(log_path),
            "started_at": base.utc_now(),
        }
        base.atomic_json(record_path, record)

        timed_out = False
        cancelled_after_sat = False
        return_code: int | None = None
        with log_path.open("wb") as log_handle:
            process = subprocess.Popen(
                command,
                cwd=self.working_directory,
                stdout=log_handle,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )
            record["pid"] = process.pid
            base.atomic_json(record_path, record)
            deadline = started + self.timeout
            while True:
                return_code = process.poll()
                if return_code is not None:
                    break
                if self.stop_event.is_set():
                    cancelled_after_sat = True
                    base.terminate_process_group(process)
                    return_code = process.returncode
                    break
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    timed_out = True
                    base.terminate_process_group(process)
                    return_code = process.returncode
                    break
                time.sleep(min(self.poll_seconds, remaining))

        status = base.read_status(output)
        if status == "sat":
            self.stop_event.set()
        if status in base.TERMINAL_STATUSES:
            state = "completed"
        elif timed_out:
            state = "timeout"
        elif cancelled_after_sat:
            state = "cancelled-after-sat"
        else:
            state = "completed-without-terminal-certificate"
        record.update(
            {
                "state": state,
                "status": status,
                "return_code": return_code,
                "elapsed_seconds": time.monotonic() - started,
                "output_sha256": (
                    base.sha256(output) if output and output.is_file() else None
                ),
                "log_sha256": base.sha256(log_path),
                "finished_at": base.utc_now(),
            }
        )
        base.atomic_json(record_path, record)
        return record

    def run(self) -> int:
        self.preload_terminal_outputs()
        self.write_summary(finished=False)
        if self.stop_event.is_set():
            # A previous run already found SAT.  Resume is intentionally a
            # no-op, and the summary still advertises the unrun remainder.
            self.write_summary(finished=False)
            return 0

        pending = [
            value
            for value in self.values
            if value_key(value) not in self.results
        ]
        futures: dict[object, object] = {}
        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            while pending and len(futures) < self.workers:
                value = pending.pop(0)
                futures[executor.submit(self.run_one, value)] = value

            while futures:
                completed, _not_done = wait(futures, return_when=FIRST_COMPLETED)
                for future in completed:
                    value = futures.pop(future)
                    try:
                        result = future.result()
                    except Exception as exc:
                        result = {
                            "value": value,
                            "state": "runner-error",
                            "error": repr(exc),
                            "finished_at": base.utc_now(),
                        }
                    with self.lock:
                        self.results[value_key(value)] = result
                        if result.get("status") == "sat":
                            self.stop_event.set()
                        self.write_summary(finished=False)
                    print(json.dumps(result, ensure_ascii=False), flush=True)

                if not self.stop_event.is_set():
                    while pending and len(futures) < self.workers:
                        value = pending.pop(0)
                        futures[executor.submit(self.run_one, value)] = value

        terminal_complete = all(
            self.results.get(value_key(value), {}).get("status")
            in base.TERMINAL_STATUSES
            for value in self.values
        )
        stopped_on_sat = any(
            record.get("status") == "sat" for record in self.results.values()
        )
        self.write_summary(finished=terminal_complete)
        if stopped_on_sat:
            return 0
        failed = not terminal_complete or any(
            record.get("status") not in base.TERMINAL_STATUSES
            for record in self.results.values()
        )
        return 1 if failed else 0


def validate_only(spec_path: Path) -> dict[str, object]:
    spec_path = spec_path.resolve()
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    errors = []
    if spec.get("schema") != "tc-byte-adder-remote-sweep-v1":
        errors.append("unsupported schema")
    if spec.get("runner") != Path(__file__).name:
        errors.append("spec runner does not name this stop-on-SAT runner")
    if spec.get("workers") != 2:
        errors.append("workers must equal 2")
    if spec.get("stop_on_first_sat") is not True:
        errors.append("stop_on_first_sat must be true")
    if spec.get("resume_terminal_outputs") is not True:
        errors.append("resume_terminal_outputs must be true")
    values = spec.get("values", [])
    pairs = {
        (value.get("slot0_kind"), value.get("slot1_kind"))
        for value in values
        if isinstance(value, dict)
    }
    kinds = {"NOT", "AND", "OR", "NAND", "NOR", "XOR", "SWITCH"}
    expected_pairs = {(left, right) for left in kinds for right in kinds}
    if len(values) != 49 or pairs != expected_pairs:
        errors.append("values are not the complete 7x7 slot-kind product")
    script = Path(str(spec.get("script", "")))
    script = script if script.is_absolute() else spec_path.parent / script
    if not script.is_file():
        errors.append(f"search script missing: {script}")
    for required in spec.get("required_files", []):
        path = Path(str(required))
        path = path if path.is_absolute() else spec_path.parent / path
        if not path.is_file():
            errors.append(f"required file missing: {path}")
    return {
        "ok": not errors,
        "spec": str(spec_path),
        "spec_sha256": base.sha256(spec_path),
        "workers": spec.get("workers"),
        "maximum_scheduled_memory_mb": (
            int(spec.get("workers", 0)) * int(spec.get("memory_mb_per_process", 0))
        ),
        "stop_on_first_sat": spec.get("stop_on_first_sat"),
        "resume_terminal_outputs": spec.get("resume_terminal_outputs"),
        "shards": len(values),
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("spec", type=Path)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    if args.validate_only:
        report = validate_only(args.spec)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report["ok"] else 2
    return StopOnSatSweep(args.spec).run()


if __name__ == "__main__":
    raise SystemExit(main())
