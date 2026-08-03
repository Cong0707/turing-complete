"""Run a bounded, resumable family of offline synthesis jobs.

The runner is intentionally independent of the Turing Complete runtime.  It
executes one local Python script repeatedly with a single template variable,
keeps a log and a JSON result for every value, and enforces limits outside the
solver process.  This avoids relying on SAT backends to honour Python timer
callbacks.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import threading
import time
from typing import Any


TERMINAL_STATUSES = {"sat", "unsat"}
SAFE_NAME = re.compile(r"[^A-Za-z0-9_.-]+")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def replacement_tokens(current: object) -> dict[str, str]:
    if isinstance(current, dict):
        return {str(key): str(value) for key, value in current.items()}
    return {"value": str(current)}


def expand(value: object, current: object) -> object:
    if isinstance(value, str):
        for key, replacement in replacement_tokens(current).items():
            value = value.replace("{" + key + "}", replacement)
        return value
    if isinstance(value, list):
        return [expand(item, current) for item in value]
    if isinstance(value, dict):
        return {key: expand(item, current) for key, item in value.items()}
    return value


def parse_cpu_set(text: str | None) -> set[int] | None:
    if not text:
        return None
    result: set[int] = set()
    for item in text.split(","):
        item = item.strip()
        if not item:
            continue
        if "-" in item:
            first, last = (int(part) for part in item.split("-", 1))
            if first > last:
                raise ValueError(f"invalid CPU range: {item}")
            result.update(range(first, last + 1))
        else:
            result.add(int(item))
    if not result:
        raise ValueError("CPU set is empty")
    return result


def find_output(arguments: list[str], working_directory: Path) -> Path | None:
    for index, argument in enumerate(arguments[:-1]):
        if argument == "--output":
            path = Path(arguments[index + 1])
            return path if path.is_absolute() else working_directory / path
    return None


def read_status(path: Path | None) -> str | None:
    if path is None or not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    status = payload.get("status")
    return status if isinstance(status, str) else None


def safe_value_name(value: object) -> str:
    if isinstance(value, dict) and "name" in value:
        value = value["name"]
    rendered = SAFE_NAME.sub("_", str(value)).strip("_")
    return rendered or "value"


def terminate_process_group(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return
    if os.name == "posix":
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            return
    else:
        # The Windows venv launcher may leave the real solver as a child
        # process.  Terminate the complete tree so a first-SAT stop or hard
        # timeout cannot leak a CaDiCaL worker.
        completed = subprocess.run(
            ["taskkill", "/PID", str(process.pid), "/T", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        if completed.returncode and process.poll() is None:
            process.terminate()
    try:
        process.wait(timeout=30)
        return
    except subprocess.TimeoutExpired:
        pass
    if os.name == "posix":
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            return
    else:
        process.kill()
    process.wait()


class Sweep:
    def __init__(self, spec_path: Path, *, dry_run: bool = False) -> None:
        self.spec_path = spec_path.resolve()
        self.root = self.spec_path.parent
        self.spec = json.loads(self.spec_path.read_text(encoding="utf-8"))
        if self.spec.get("schema") != "tc-byte-adder-remote-sweep-v1":
            raise ValueError("unsupported sweep schema")

        self.name = str(self.spec["name"])
        self.values = list(self.spec["values"])
        self.workers = int(self.spec.get("workers", 1))
        if not 1 <= self.workers <= 32:
            raise ValueError("workers must be between 1 and 32")
        self.timeout = float(self.spec.get("timeout_seconds", 3600))
        self.memory_mb = int(self.spec.get("memory_mb_per_process", 0))
        self.cpu_set = parse_cpu_set(self.spec.get("cpu_set"))
        self.nice = int(self.spec.get("nice", 5))
        if not -20 <= self.nice <= 19:
            raise ValueError("nice must be between -20 and 19")
        self.dry_run = dry_run
        self.stop_on_first_sat = bool(self.spec.get("stop_on_first_sat", False))
        self.stop_event = threading.Event()

        script = Path(str(self.spec["script"]))
        self.script = script if script.is_absolute() else self.root / script
        self.script = self.script.resolve()
        if not self.script.is_file():
            raise FileNotFoundError(self.script)

        working = Path(str(self.spec.get("working_directory", ".")))
        self.working_directory = (
            working if working.is_absolute() else self.root / working
        ).resolve()
        self.working_directory.mkdir(parents=True, exist_ok=True)
        self.log_directory = self.root / str(self.spec.get("log_directory", "logs"))
        self.result_directory = self.root / str(
            self.spec.get("result_directory", "run-results")
        )
        self.log_directory.mkdir(parents=True, exist_ok=True)
        self.result_directory.mkdir(parents=True, exist_ok=True)
        self.summary_path = self.root / str(
            self.spec.get("summary", "sweep-summary.json")
        )
        self.lock = threading.Lock()
        self.results: dict[str, dict[str, Any]] = {}

    def command_for(self, value: object) -> tuple[list[str], Path | None]:
        arguments = [str(item) for item in expand(self.spec["arguments"], value)]
        command = [sys.executable, str(self.script), *arguments]
        if os.name == "posix":
            command = ["nice", "-n", str(self.nice), *command]
            if self.memory_mb > 0:
                command = [
                    "prlimit",
                    f"--as={self.memory_mb * 1024 * 1024}",
                    "--",
                    *command,
                ]
            if self.cpu_set:
                cpu_text = ",".join(str(cpu) for cpu in sorted(self.cpu_set))
                command = ["taskset", "-c", cpu_text, *command]
        return command, find_output(arguments, self.working_directory)

    def write_summary(self, *, finished: bool = False) -> None:
        payload = {
            "schema": "tc-byte-adder-remote-sweep-summary-v1",
            "name": self.name,
            "spec": str(self.spec_path),
            "spec_sha256": sha256(self.spec_path),
            "script": str(self.script),
            "script_sha256": sha256(self.script),
            "python": sys.version,
            "workers": self.workers,
            "timeout_seconds": self.timeout,
            "memory_mb_per_process": self.memory_mb,
            "nice": self.nice,
            "cpu_set": sorted(self.cpu_set) if self.cpu_set else None,
            "stop_on_first_sat": self.stop_on_first_sat,
            "stop_event_set": self.stop_event.is_set(),
            "updated_at": utc_now(),
            "finished": finished,
            "results": [
                self.results[key]
                for key in sorted(self.results, key=lambda item: str(item))
            ],
        }
        atomic_json(self.summary_path, payload)

    def run_one(self, value: object) -> dict[str, Any]:
        safe_name = safe_value_name(value)
        command, output = self.command_for(value)
        old_status = read_status(output)
        if old_status in TERMINAL_STATUSES:
            return {
                "value": value,
                "status": old_status,
                "state": "reused",
                "output": str(output),
                "output_sha256": sha256(output) if output else None,
                "finished_at": utc_now(),
            }
        if self.stop_event.is_set():
            return {
                "value": value,
                "state": "skipped-after-sat",
                "finished_at": utc_now(),
            }

        if output is not None:
            output.parent.mkdir(parents=True, exist_ok=True)

        log_path = self.log_directory / f"{safe_name}.log"
        record_path = self.result_directory / f"{safe_name}.json"
        started = time.monotonic()
        record: dict[str, Any] = {
            "value": value,
            "state": "dry-run" if self.dry_run else "running",
            "command": command,
            "working_directory": str(self.working_directory),
            "output": str(output) if output else None,
            "log": str(log_path),
            "started_at": utc_now(),
        }
        atomic_json(record_path, record)
        if self.dry_run:
            record["elapsed_seconds"] = 0.0
            record["finished_at"] = utc_now()
            atomic_json(record_path, record)
            return record

        timed_out = False
        stopped_after_sat = False
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
            atomic_json(record_path, record)
            deadline = time.monotonic() + self.timeout
            while process.poll() is None:
                if self.stop_event.is_set():
                    stopped_after_sat = True
                    terminate_process_group(process)
                    break
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    timed_out = True
                    terminate_process_group(process)
                    break
                try:
                    process.wait(timeout=min(1.0, remaining))
                except subprocess.TimeoutExpired:
                    pass
            return_code = process.returncode

        status = read_status(output)
        record.update(
            {
                "state": (
                    "timeout"
                    if timed_out
                    else "stopped-after-sat"
                    if stopped_after_sat
                    else "completed"
                ),
                "status": status,
                "return_code": return_code,
                "elapsed_seconds": time.monotonic() - started,
                "output_sha256": sha256(output) if output and output.is_file() else None,
                "log_sha256": sha256(log_path),
                "finished_at": utc_now(),
            }
        )
        atomic_json(record_path, record)
        return record

    def run(self) -> int:
        self.write_summary()
        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            futures = {executor.submit(self.run_one, value): value for value in self.values}
            for future in as_completed(futures):
                value = futures[future]
                try:
                    result = future.result()
                except Exception as exc:  # Keep the remaining sweep alive.
                    result = {
                        "value": value,
                        "state": "runner-error",
                        "error": repr(exc),
                        "finished_at": utc_now(),
                    }
                with self.lock:
                    self.results[str(value)] = result
                    if self.stop_on_first_sat and result.get("status") == "sat":
                        self.stop_event.set()
                    self.write_summary()
                print(json.dumps(result, ensure_ascii=False), flush=True)
        self.write_summary(finished=True)
        sat_found = any(
            result.get("status") == "sat" for result in self.results.values()
        )
        early_stop_states = (
            {"skipped-after-sat", "stopped-after-sat"}
            if self.stop_on_first_sat and sat_found
            else set()
        )
        failed = [
            result
            for result in self.results.values()
            if result.get("state") not in early_stop_states
            and (
                result.get("state") in {"runner-error", "timeout"}
                or result.get("status") not in TERMINAL_STATUSES
            )
        ]
        return 1 if failed else 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("spec", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    return Sweep(args.spec, dry_run=args.dry_run).run()


if __name__ == "__main__":
    raise SystemExit(main())
