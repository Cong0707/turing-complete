"""Run prioritized sparse g17/g18 S5/S6/S7/C8 position sweeps on Ubuntu.

Order and concurrency are fixed by design:

1. g17/o1/s8/x0: 9 ordinary positions, at most 2 workers.
2. g17/o0/s7/x1: 8 XOR positions, at most 2 workers.
3. g18/o1/s7/x1: 72 ordered (XOR, ordinary) positions, at most 4 workers.

Before target solving, both structural auditors must pass and a known S7/C8
SAT topology must reproduce and pass the independent physical replay.  Every
solver runs with an RLIMIT_AS inherited from a tiny bash wrapper and an outer
Python watchdog.  A timeout, nonzero exit, absent/invalid JSON, or metadata
mismatch is recorded as UNKNOWN and is never promoted to UNSAT.
"""

from __future__ import annotations

import argparse
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import shlex
import signal
import subprocess
import sys
import time
from typing import Any


EXPECTED_WORKER_SHA256 = (
    "c48a96e55d8c5076418999f5fa5ee95e9f8207c03f138cd4bccf48908a69c071"
)
ORDINARY_KINDS = ("NOT", "AND", "OR", "NAND", "NOR")
KNOWN_POSITIVE_FIXED = (
    "NOT",
    "NOR",
    "OR",
    "OR",
    "SWITCH",
    "SWITCH",
    "SWITCH",
    "SWITCH",
    "SWITCH",
    "SWITCH",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def digest(path: Path) -> str | None:
    return sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def atomic_json(path: Path, payload: object) -> None:
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".tmp.{os.getpid()}")
    temporary.write_bytes(encoded)
    temporary.replace(path)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object in {path}")
    return value


def available_memory_kib() -> int | None:
    try:
        for line in Path("/proc/meminfo").read_text().splitlines():
            if line.startswith("MemAvailable:"):
                return int(line.split()[1])
    except Exception:
        return None
    return None


class SweepRunner:
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.root = args.root.resolve()
        self.out = args.out.resolve()
        self.worker = (
            self.root
            / ".research/byte_adder_phase_shortcut_restart/physical_exact.py"
        )
        self.replayer = (
            self.root
            / ".research/byte_adder_han_knowles_fused_agent/"
            "replay_s567c8_physical_witness.py"
        )
        self.sparse_auditor = (
            self.root
            / ".research/byte_adder_han_knowles_fused_agent/"
            "audit_s567c8_g17_sparse_position_universes.py"
        )
        self.g18_auditor = (
            self.root
            / ".research/byte_adder_han_knowles_fused_agent/"
            "audit_s567c8_g18_o1s7x1_position_universe.py"
        )
        self.preflight = self.out / "preflight"
        self.sparse_manifest = self.preflight / "g17_sparse_manifest.json"
        self.g18_manifest = self.preflight / "g18_o1s7x1_manifest.json"
        self.global_sat = self.out / "SAT_FOUND.json"
        self.global_verified_sat = self.out / "SAT_VERIFIED.json"

    def check_configuration(self) -> None:
        if self.args.small_workers < 1 or self.args.small_workers > 2:
            raise ValueError("small-workers must be in 1..2")
        if self.args.g18_workers < 1 or self.args.g18_workers > 4:
            raise ValueError("g18-workers must be in 1..4")
        if self.args.as_kib <= 0 or self.args.as_kib > 1_310_720:
            raise ValueError("as-kib must be <= 1310720 (1.25 GiB)")
        if self.args.watchdog <= 0 or self.args.positive_watchdog <= 0:
            raise ValueError("watchdogs must be positive")
        required = (
            self.worker,
            self.replayer,
            self.sparse_auditor,
            self.g18_auditor,
            self.args.python,
        )
        missing = [str(path) for path in required if not path.is_file()]
        if missing:
            raise FileNotFoundError(missing)
        actual_worker_sha = digest(self.worker)
        if actual_worker_sha != EXPECTED_WORKER_SHA256:
            raise RuntimeError(
                f"physical_exact SHA mismatch: {actual_worker_sha}"
            )
        self.out.mkdir(parents=True, exist_ok=True)

    def run_logged(
        self,
        command: list[str],
        log_path: Path,
        watchdog_seconds: float,
    ) -> dict[str, object]:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        shell_command = (
            f"ulimit -v {self.args.as_kib}; "
            f"exec nice -n {self.args.nice} {shlex.join(command)}"
        )
        start_utc = utc_now()
        start = time.monotonic()
        timed_out = False
        killed = False
        with log_path.open("wb") as log:
            process = subprocess.Popen(
                ["bash", "-lc", shell_command],
                stdout=log,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )
            pid = process.pid
            try:
                return_code = process.wait(timeout=watchdog_seconds)
            except subprocess.TimeoutExpired:
                timed_out = True
                try:
                    os.killpg(process.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
                try:
                    return_code = process.wait(timeout=self.args.kill_after)
                except subprocess.TimeoutExpired:
                    killed = True
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    return_code = process.wait()
        end_utc = utc_now()
        if timed_out:
            classification = "watchdog_timeout_killed" if killed else "watchdog_timeout"
        elif return_code == 0:
            classification = "solver_exit"
        else:
            classification = "solver_nonzero"
        return {
            "start_utc": start_utc,
            "end_utc": end_utc,
            "wall_seconds": time.monotonic() - start,
            "pid": pid,
            "exit_code": return_code,
            "classification": classification,
            "timed_out": timed_out,
            "killed_after_timeout": killed,
        }

    def run_auditor(
        self, script: Path, audit: Path, manifest: Path, log: Path
    ) -> None:
        audit.parent.mkdir(parents=True, exist_ok=True)
        command = [
            str(self.args.python),
            str(script),
            "--audit",
            str(audit),
            "--manifest",
            str(manifest),
        ]
        with log.open("wb") as output:
            completed = subprocess.run(command, stdout=output, stderr=subprocess.STDOUT)
        if completed.returncode != 0:
            raise RuntimeError(f"auditor failed: {script} rc={completed.returncode}")
        payload = read_json(audit)
        if payload.get("status") != "complete":
            raise RuntimeError(f"incomplete auditor: {audit}")

    def audit_preflight(self) -> None:
        self.preflight.mkdir(parents=True, exist_ok=True)
        self.run_auditor(
            self.sparse_auditor,
            self.preflight / "g17_sparse_audit.json",
            self.sparse_manifest,
            self.preflight / "g17_sparse_auditor.log",
        )
        self.run_auditor(
            self.g18_auditor,
            self.preflight / "g18_o1s7x1_audit.json",
            self.g18_manifest,
            self.preflight / "g18_o1s7x1_auditor.log",
        )
        payload = {
            "schema": "s567c8-sparse-position-sweep-preflight-v1",
            "status": "complete",
            "physical_exact_sha256": digest(self.worker),
            "sparse_auditor_sha256": digest(self.sparse_auditor),
            "sparse_audit_sha256": digest(self.preflight / "g17_sparse_audit.json"),
            "sparse_manifest_sha256": digest(self.sparse_manifest),
            "g18_auditor_sha256": digest(self.g18_auditor),
            "g18_audit_sha256": digest(self.preflight / "g18_o1s7x1_audit.json"),
            "g18_manifest_sha256": digest(self.g18_manifest),
            "resource_limits": {
                "as_limit_kib": self.args.as_kib,
                "nice": self.args.nice,
                "small_workers": self.args.small_workers,
                "g18_workers": self.args.g18_workers,
                "watchdog_seconds": self.args.watchdog,
                "positive_watchdog_seconds": self.args.positive_watchdog,
            },
            "available_memory_kib": available_memory_kib(),
        }
        atomic_json(self.preflight / "preflight.json", payload)
        print(
            "PREFLIGHT complete "
            f"sparse={payload['sparse_manifest_sha256']} "
            f"g18={payload['g18_manifest_sha256']}",
            flush=True,
        )

    def validate_result(
        self,
        result_path: Path,
        process: dict[str, object],
        expected: dict[str, object],
    ) -> tuple[str, str | None, list[dict[str, object]], dict[str, Any] | None]:
        errors: list[dict[str, object]] = []
        payload: dict[str, Any] | None = None
        raw_status: str | None = None
        if not result_path.is_file():
            errors.append({"reason": "missing_result"})
        else:
            try:
                payload = read_json(result_path)
                value = payload.get("status")
                raw_status = value if isinstance(value, str) else None
            except Exception as exc:
                errors.append({"reason": "invalid_json", "error": repr(exc)})
        if payload is not None:
            exact_fields = {
                "schema": "exact-fast-negative-physical-shard-v2",
                "domain": "s34567c8_leaf",
                "rows": 486,
                "output_names": expected["outputs"],
                "gate_bound": expected["gate_bound"],
                "max_delay": 5,
                "components": expected["components"],
                "ordinary": expected["ordinary"],
                "exact_switches": expected["switches"],
                "exact_xors": expected["xors"],
                "fixed_kinds": expected["fixed_kinds"],
                "solver": self.args.solver,
                "physical_nets": True,
                "public_outputs_must_be_driven": True,
                "timer_errors": [],
            }
            for field, wanted in exact_fields.items():
                actual = payload.get(field)
                if actual != wanted:
                    errors.append(
                        {
                            "reason": "field_mismatch",
                            "field": field,
                            "expected": wanted,
                            "actual": actual,
                        }
                    )
            shard = payload.get("shard") or {}
            for field, wanted in (
                ("split_slots", 1),
                ("shard_count", 1),
                ("shard_index", 0),
            ):
                if shard.get(field) != wanted:
                    errors.append(
                        {
                            "reason": "shard_mismatch",
                            "field": field,
                            "expected": wanted,
                            "actual": shard.get(field),
                        }
                    )
            if payload.get("dependency_sha256") != expected["dependency_sha256"]:
                errors.append({"reason": "dependency_sha256_mismatch"})
        if process["timed_out"]:
            errors.append({"reason": "watchdog_timeout"})
        if process["exit_code"] != 0:
            errors.append(
                {"reason": "nonzero_exit", "exit_code": process["exit_code"]}
            )
        if raw_status not in ("sat", "unsat"):
            errors.append({"reason": "nonfinal_status", "status": raw_status})
        canonical = raw_status if not errors and raw_status in ("sat", "unsat") else "unknown"
        return canonical, raw_status, errors, payload

    def replay_sat(self, result_path: Path, replay_path: Path, log_path: Path) -> dict[str, object]:
        command = [
            str(self.args.python),
            str(self.replayer),
            str(result_path),
            "--output",
            str(replay_path),
        ]
        with log_path.open("wb") as output:
            completed = subprocess.run(command, stdout=output, stderr=subprocess.STDOUT)
        replay_status = None
        errors: object = None
        if replay_path.is_file():
            try:
                replay = read_json(replay_path)
                replay_status = replay.get("status")
                errors = replay.get("errors")
            except Exception as exc:
                errors = [{"reason": "invalid_replay_json", "error": repr(exc)}]
        return {
            "exit_code": completed.returncode,
            "status": replay_status,
            "errors": errors,
            "path": str(replay_path),
            "sha256": digest(replay_path),
            "log": str(log_path),
            "log_sha256": digest(log_path),
        }

    def positive_regression(self, dependency_sha256: dict[str, str]) -> None:
        directory = self.out / "positive_regression"
        directory.mkdir(parents=True, exist_ok=True)
        result = directory / "tail_s7c8_g16_fixed_kinds_d5.json"
        log = directory / "tail_s7c8_g16_fixed_kinds_d5.log"
        run_path = directory / "tail_s7c8_g16_fixed_kinds_d5.run.json"
        replay_path = directory / "tail_s7c8_g16_fixed_kinds_d5.replay.json"
        replay_log = directory / "tail_s7c8_g16_fixed_kinds_d5.replay.log"

        expected: dict[str, object] = {
            "outputs": ["S7", "C8"],
            "gate_bound": 16,
            "components": 10,
            "ordinary": 4,
            "switches": 6,
            "xors": 0,
            "fixed_kinds": list(KNOWN_POSITIVE_FIXED),
            "dependency_sha256": dependency_sha256,
        }
        existing_ok = False
        if run_path.is_file() and replay_path.is_file() and result.is_file():
            try:
                old_run = read_json(run_path)
                old_replay = read_json(replay_path)
                existing_ok = (
                    old_run.get("status") == "sat"
                    and old_replay.get("status") == "verified"
                    and old_run.get("result_sha256") == digest(result)
                )
            except Exception:
                existing_ok = False
        if existing_ok:
            print("POSITIVE regression already verified", flush=True)
            return

        command = [
            str(self.args.python),
            str(self.worker),
            "--domain",
            "s34567c8_leaf",
            "--outputs",
            "S7,C8",
            "--gate-bound",
            "16",
            "--max-delay",
            "5",
            "--components",
            "10",
            "--switches",
            "6",
            "--xors",
            "0",
            "--fixed-kinds",
            ",".join(KNOWN_POSITIVE_FIXED),
            "--split-slots",
            "1",
            "--shard-count",
            "1",
            "--shard-index",
            "0",
            "--solver",
            self.args.solver,
            "--timeout",
            "0",
            "--output",
            str(result),
        ]
        process = self.run_logged(command, log, self.args.positive_watchdog)
        canonical, raw_status, errors, _payload = self.validate_result(
            result, process, expected
        )
        replay = None
        if raw_status == "sat" and result.is_file():
            replay = self.replay_sat(result, replay_path, replay_log)
        run = {
            "schema": "s567c8-positive-regression-run-v1",
            **process,
            "status": canonical,
            "raw_status": raw_status,
            "validation_errors": errors,
            "result": str(result),
            "result_sha256": digest(result),
            "log": str(log),
            "log_sha256": digest(log),
            "replay": replay,
            "resource_limits": {
                "watchdog_seconds": self.args.positive_watchdog,
                "as_limit_kib": self.args.as_kib,
                "nice": self.args.nice,
            },
            "expected": expected,
        }
        atomic_json(run_path, run)
        if canonical != "sat" or not replay or replay.get("status") != "verified":
            raise RuntimeError(
                "positive regression failed closed: "
                f"status={canonical} raw={raw_status} replay={replay} errors={errors}"
            )
        print(
            "POSITIVE verified "
            f"solve_wall={process['wall_seconds']:.3f}s "
            f"result_sha={run['result_sha256']} replay_sha={replay['sha256']}",
            flush=True,
        )

    def preserve_sat_candidate(
        self,
        target_class: str,
        key: str,
        result_path: Path,
        result_sha: str | None,
        raw_status: str,
    ) -> None:
        payload = {
            "schema": "s567c8-sparse-position-sat-candidate-v1",
            "observed_utc": utc_now(),
            "target_class": target_class,
            "key": key,
            "raw_status": raw_status,
            "result": str(result_path),
            "result_sha256": result_sha,
        }
        # First SAT wins the global marker; all result files remain preserved.
        try:
            descriptor = os.open(
                self.global_sat,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                0o644,
            )
        except FileExistsError:
            return
        with os.fdopen(descriptor, "wb") as output:
            output.write((json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode())

    def run_one(
        self,
        target_class: str,
        class_dir: Path,
        pattern: dict[str, Any],
        scope: dict[str, Any],
        dependency_sha256: dict[str, str],
    ) -> dict[str, Any]:
        key = str(pattern["key"])
        result = class_dir / "results" / f"{key}.json"
        log = class_dir / "logs" / f"{key}.log"
        run_path = class_dir / "runs" / f"{key}.run.json"
        replay_path = class_dir / "replays" / f"{key}.replay.json"
        replay_log = class_dir / "replays" / f"{key}.replay.log"
        for directory in (result.parent, log.parent, run_path.parent, replay_path.parent):
            directory.mkdir(parents=True, exist_ok=True)

        fixed = list(pattern["fixed_kinds"])
        expected: dict[str, object] = {
            "outputs": ["S5", "S6", "S7", "C8"],
            "gate_bound": int(scope["gate_bound"]),
            "components": int(scope["components"]),
            "ordinary": int(scope["ordinary"]),
            "switches": int(scope["switches"]),
            "xors": int(scope["xors"]),
            "fixed_kinds": fixed,
            "dependency_sha256": dependency_sha256,
        }
        command = [
            str(self.args.python),
            str(self.worker),
            "--domain",
            "s34567c8_leaf",
            "--outputs",
            "S5,S6,S7,C8",
            "--gate-bound",
            str(scope["gate_bound"]),
            "--max-delay",
            "5",
            "--components",
            str(scope["components"]),
            "--switches",
            str(scope["switches"]),
            "--xors",
            str(scope["xors"]),
            "--fixed-kinds",
            ",".join(fixed),
            "--split-slots",
            "1",
            "--shard-count",
            "1",
            "--shard-index",
            "0",
            "--solver",
            self.args.solver,
            "--timeout",
            "0",
            "--output",
            str(result),
        ]
        process = self.run_logged(command, log, self.args.watchdog)
        canonical, raw_status, errors, _payload = self.validate_result(
            result, process, expected
        )
        result_sha = digest(result)
        replay = None
        if raw_status == "sat" and result.is_file():
            self.preserve_sat_candidate(
                target_class, key, result, result_sha, raw_status
            )
            replay = self.replay_sat(result, replay_path, replay_log)

        run: dict[str, Any] = {
            "schema": "s567c8-sparse-position-run-v1",
            **process,
            "target_class": target_class,
            "key": key,
            "status": canonical,
            "raw_status": raw_status,
            "validation_errors": errors,
            "xor_slot": pattern.get("xor_slot"),
            "ordinary_slot": pattern.get("ordinary_slot"),
            "fixed_kinds": fixed,
            "allowed_ordinary_kinds": pattern.get("allowed_ordinary_kinds", []),
            "result": str(result),
            "result_sha256": result_sha,
            "log": str(log),
            "log_sha256": digest(log),
            "replay": replay,
            "resource_limits": {
                "watchdog_seconds": self.args.watchdog,
                "as_limit_kib": self.args.as_kib,
                "nice": self.args.nice,
            },
            "expected": expected,
        }
        atomic_json(run_path, run)

        if replay and replay.get("status") == "verified":
            verified = {
                "schema": "s567c8-sparse-position-verified-sat-v1",
                "observed_utc": utc_now(),
                "target_class": target_class,
                "key": key,
                "result": str(result),
                "result_sha256": result_sha,
                "run": str(run_path),
                "run_sha256": digest(run_path),
                "replay": str(replay_path),
                "replay_sha256": replay.get("sha256"),
            }
            if not self.global_verified_sat.exists():
                atomic_json(self.global_verified_sat, verified)
        return run

    def write_class_summary(
        self,
        target_class: str,
        class_dir: Path,
        scope: dict[str, Any],
        patterns: list[dict[str, Any]],
    ) -> dict[str, Any]:
        records: list[dict[str, Any]] = []
        for path in sorted((class_dir / "runs").glob("*.run.json")):
            try:
                records.append(read_json(path))
            except Exception as exc:
                records.append(
                    {
                        "key": path.name.removesuffix(".run.json"),
                        "status": "unknown",
                        "raw_status": None,
                        "run": str(path),
                        "run_parse_error": repr(exc),
                    }
                )
        statuses = sorted({str(row.get("status")) for row in records})
        summary = {
            "schema": "s567c8-sparse-position-class-summary-v1",
            "target_class": target_class,
            "scope": scope,
            "expected_position_patterns": len(patterns),
            "attempted_position_patterns": len(records),
            "status_counts": {
                status: sum(row.get("status") == status for row in records)
                for status in statuses
            },
            "raw_sat": [row.get("key") for row in records if row.get("raw_status") == "sat"],
            "verified_sat": [
                row.get("key")
                for row in records
                if (row.get("replay") or {}).get("status") == "verified"
            ],
            "unknown_is_not_unsat": True,
            "stopped_on_sat": self.global_sat.is_file(),
            "records": records,
        }
        atomic_json(class_dir / "summary.json", summary)
        return summary

    def run_class(
        self,
        target_class: str,
        scope: dict[str, Any],
        patterns: list[dict[str, Any]],
        max_workers: int,
        dependency_sha256: dict[str, str],
    ) -> dict[str, Any]:
        class_dir = self.out / target_class
        for name in ("results", "logs", "runs", "replays"):
            (class_dir / name).mkdir(parents=True, exist_ok=True)

        completed_keys: set[str] = set()
        for path in (class_dir / "runs").glob("*.run.json"):
            try:
                row = read_json(path)
                key = row.get("key")
                if isinstance(key, str):
                    if self.args.rerun_unknown and row.get("status") == "unknown":
                        continue
                    completed_keys.add(key)
                    if row.get("raw_status") == "sat":
                        self.preserve_sat_candidate(
                            target_class,
                            key,
                            Path(str(row.get("result"))),
                            row.get("result_sha256"),
                            "sat",
                        )
            except Exception:
                continue
        remaining = [row for row in patterns if row["key"] not in completed_keys]
        print(
            f"CLASS {target_class} start patterns={len(patterns)} "
            f"remaining={len(remaining)} workers={max_workers} "
            f"available_kib={available_memory_kib()}",
            flush=True,
        )

        iterator = iter(remaining)
        futures: dict[Future[dict[str, Any]], str] = {}
        stop = self.global_sat.is_file()
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            while not stop and len(futures) < max_workers:
                try:
                    pattern = next(iterator)
                except StopIteration:
                    break
                future = executor.submit(
                    self.run_one,
                    target_class,
                    class_dir,
                    pattern,
                    scope,
                    dependency_sha256,
                )
                futures[future] = str(pattern["key"])

            while futures:
                done, _pending = wait(tuple(futures), return_when=FIRST_COMPLETED)
                for future in done:
                    key = futures.pop(future)
                    try:
                        record = future.result()
                    except Exception as exc:
                        record = {
                            "schema": "s567c8-sparse-position-run-v1",
                            "target_class": target_class,
                            "key": key,
                            "status": "unknown",
                            "raw_status": None,
                            "runner_exception": repr(exc),
                        }
                        atomic_json(class_dir / "runs" / f"{key}.run.json", record)
                    print(
                        f"RESULT {target_class}/{key} status={record.get('status')} "
                        f"raw={record.get('raw_status')} rc={record.get('exit_code')} "
                        f"wall={record.get('wall_seconds')}",
                        flush=True,
                    )
                    if record.get("raw_status") == "sat":
                        stop = True
                self.write_class_summary(target_class, class_dir, scope, patterns)
                while not stop and len(futures) < max_workers:
                    try:
                        pattern = next(iterator)
                    except StopIteration:
                        break
                    future = executor.submit(
                        self.run_one,
                        target_class,
                        class_dir,
                        pattern,
                        scope,
                        dependency_sha256,
                    )
                    futures[future] = str(pattern["key"])

        summary = self.write_class_summary(target_class, class_dir, scope, patterns)
        print(
            f"CLASS {target_class} end attempted={summary['attempted_position_patterns']} "
            f"counts={summary['status_counts']} sat={summary['raw_sat']}",
            flush=True,
        )
        return summary

    def load_classes(self) -> list[tuple[str, dict[str, Any], list[dict[str, Any]], int]]:
        sparse = read_json(self.sparse_manifest)
        g18 = read_json(self.g18_manifest)
        sparse_by_name = {row["name"]: row for row in sparse["classes"]}
        order = []
        for name in ("g17_o1s8", "g17_x1s7"):
            row = sparse_by_name[name]
            order.append(
                (name, dict(row["scope"]), list(row["patterns"]), self.args.small_workers)
            )
        order.append(
            (
                "g18_o1s7x1",
                dict(g18["scope"]),
                list(g18["patterns"]),
                self.args.g18_workers,
            )
        )
        return order

    def write_overall_summary(self, class_summaries: list[dict[str, Any]]) -> None:
        positive_dir = self.out / "positive_regression"
        payload = {
            "schema": "s567c8-prioritized-sparse-g17-g18-sweep-summary-v1",
            "priority_order": ["g17_o1s8", "g17_x1s7", "g18_o1s7x1"],
            "preflight_sha256": digest(self.preflight / "preflight.json"),
            "positive_run_sha256": digest(
                positive_dir / "tail_s7c8_g16_fixed_kinds_d5.run.json"
            ),
            "positive_replay_sha256": digest(
                positive_dir / "tail_s7c8_g16_fixed_kinds_d5.replay.json"
            ),
            "sat_found": read_json(self.global_sat) if self.global_sat.is_file() else None,
            "verified_sat": (
                read_json(self.global_verified_sat)
                if self.global_verified_sat.is_file()
                else None
            ),
            "unknown_is_not_unsat": True,
            "class_summaries": class_summaries,
            "resource_limits": {
                "small_workers": self.args.small_workers,
                "g18_workers": self.args.g18_workers,
                "watchdog_seconds": self.args.watchdog,
                "positive_watchdog_seconds": self.args.positive_watchdog,
                "as_limit_kib": self.args.as_kib,
                "nice": self.args.nice,
            },
        }
        atomic_json(self.out / "summary.json", payload)

    def run(self) -> int:
        self.check_configuration()
        self.audit_preflight()
        sparse_manifest = read_json(self.sparse_manifest)
        dependency_sha256 = dict(sparse_manifest["worker"]["dependency_sha256"])
        self.positive_regression(dependency_sha256)

        summaries: list[dict[str, Any]] = []
        for target_class, scope, patterns, workers in self.load_classes():
            if self.global_sat.is_file():
                break
            summaries.append(
                self.run_class(
                    target_class,
                    scope,
                    patterns,
                    workers,
                    dependency_sha256,
                )
            )
            self.write_overall_summary(summaries)
        self.write_overall_summary(summaries)
        print(
            f"DONE sat_found={self.global_sat.is_file()} classes={len(summaries)}",
            flush=True,
        )
        return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    default_root = Path("/root/congProjects/turing-complete-works")
    parser.add_argument("--root", type=Path, default=default_root)
    parser.add_argument(
        "--python", type=Path, default=default_root / ".venv/bin/python"
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=(
            default_root
            / ".research/byte_adder_han_knowles_fused_agent/remote-sweeps/"
            "s567c8_sparse_g17_g18_20260804"
        ),
    )
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--watchdog", type=float, default=180.0)
    parser.add_argument("--positive-watchdog", type=float, default=180.0)
    parser.add_argument("--kill-after", type=float, default=30.0)
    parser.add_argument("--as-kib", type=int, default=1_310_720)
    parser.add_argument("--nice", type=int, default=5)
    parser.add_argument("--small-workers", type=int, default=2)
    parser.add_argument("--g18-workers", type=int, default=4)
    parser.add_argument("--rerun-unknown", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    try:
        raise SystemExit(SweepRunner(parse_args()).run())
    except Exception as exc:
        print(f"FATAL {type(exc).__name__}: {exc}", file=sys.stderr, flush=True)
        raise
