"""Bounded remote sweep for the 18-gate S3/S4-free high tail.

Every external timeout, signal, missing result, or malformed result remains
UNKNOWN.  The launcher never upgrades such a run to UNSAT.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import time


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORKER = HERE / "exact_tail_with_s34_free.py"
JOBS = (
    ("g18_o02_s08_x0", 10, 8, 0),
    ("g18_o04_s07_x0", 11, 7, 0),
    ("g18_o06_s06_x0", 12, 6, 0),
    ("g18_o08_s05_x0", 13, 5, 0),
)
ZERO_VERIFICATION_FIELDS = (
    "mismatch_count",
    "bus_conflict_count",
    "undriven_output_count",
    "physical_net_partition_violation_count",
    "depth_upper_bound_violation_count",
    "output_deadline_violation_count",
)


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def validate_payload(path: Path) -> tuple[str, list[str]]:
    errors: list[str] = []
    if not path.is_file():
        return "unknown", ["result file absent"]
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # malformed evidence is never a proof
        return "unknown", [f"malformed result: {exc!r}"]
    status = str(payload.get("status", "unknown"))
    if status not in {"sat", "unsat", "unknown"}:
        return "unknown", [f"invalid status: {status!r}"]
    if status == "sat":
        verification = payload.get("verification", {})
        for field in ZERO_VERIFICATION_FIELDS:
            if int(verification.get(field, -1)) != 0:
                errors.append(f"SAT verification failed: {field}")
        if int(payload.get("actual_gate", 10**9)) > 18:
            errors.append("SAT witness exceeds gate bound")
        if int(payload.get("verification", {}).get("actual_max_delay", 10**9)) > 5:
            errors.append("SAT witness exceeds delay bound")
        provenance = payload.get("free_intermediate_provenance", {})
        if not provenance.get("u6_equals_s3"):
            errors.append("SAT witness lacks audited S3 provenance")
    return ("unknown" if errors else status), errors


def run_job(
    out_dir: Path,
    job: tuple[str, int, int, int],
    *,
    python: Path,
    wall_timeout: int,
    address_space: int,
    nice: int,
    solver: str,
) -> dict[str, object]:
    name, components, switches, xors = job
    job_dir = out_dir / name
    job_dir.mkdir(parents=True, exist_ok=True)
    result_path = job_dir / "result.json"
    stdout_path = job_dir / "stdout.log"
    stderr_path = job_dir / "stderr.log"
    timing_path = job_dir / "time.log"
    run_path = job_dir / "run.json"
    command = [
        "/usr/bin/time",
        "-v",
        "-o",
        str(timing_path),
        "timeout",
        "--signal=TERM",
        "--kill-after=30s",
        f"{wall_timeout}s",
        "prlimit",
        f"--as={address_space}",
        "--",
        "nice",
        "-n",
        str(nice),
        str(python),
        str(WORKER),
        "--gate-bound",
        "18",
        "--max-delay",
        "5",
        "--components",
        str(components),
        "--switches",
        str(switches),
        "--xors",
        str(xors),
        "--split-slots",
        "3",
        "--shard-count",
        "1",
        "--shard-index",
        "0",
        "--solver",
        solver,
        "--timeout",
        "0",
        "--output",
        str(result_path),
    ]
    started = utc_now()
    before = time.monotonic()
    with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            stdout=stdout,
            stderr=stderr,
            check=False,
        )
    elapsed = time.monotonic() - before
    status, validation_errors = validate_payload(result_path)
    timed_out = completed.returncode in {124, 137}
    if completed.returncode != 0 and status != "sat":
        status = "unknown"
    record: dict[str, object] = {
        "schema": "s34-free-tail-run-v1",
        "name": name,
        "started_utc": started,
        "finished_utc": utc_now(),
        "elapsed_seconds": elapsed,
        "command": command,
        "returncode": completed.returncode,
        "timed_out": timed_out,
        "status": status,
        "validation_errors": validation_errors,
        "decomposition": {
            "gate_bound": 18,
            "components": components,
            "ordinary": components - switches - xors,
            "switches": switches,
            "xors": xors,
        },
        "artifacts": {
            "result": str(result_path),
            "result_sha256": digest(result_path) if result_path.is_file() else None,
            "stdout": str(stdout_path),
            "stdout_sha256": digest(stdout_path),
            "stderr": str(stderr_path),
            "stderr_sha256": digest(stderr_path),
            "time": str(timing_path),
            "time_sha256": digest(timing_path) if timing_path.is_file() else None,
        },
    }
    run_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    record["run"] = str(run_path)
    record["run_sha256"] = digest(run_path)
    return record


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--wall-timeout", type=int, default=1200)
    parser.add_argument("--address-space", type=int, default=1610612736)
    parser.add_argument("--nice", type=int, default=10)
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--python", type=Path, default=ROOT / ".venv/bin/python")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.workers < 1 or args.workers > len(JOBS):
        parser.error(f"workers must be in 1..{len(JOBS)}")
    if args.dry_run:
        print(json.dumps({"jobs": JOBS, "worker": str(WORKER)}, indent=2))
        return 0

    args.out.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, object]] = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(
                run_job,
                args.out,
                job,
                python=args.python,
                wall_timeout=args.wall_timeout,
                address_space=args.address_space,
                nice=args.nice,
                solver=args.solver,
            ): job[0]
            for job in JOBS
        }
        for future in as_completed(futures):
            record = future.result()
            records.append(record)
            print(
                json.dumps(
                    {
                        "name": record["name"],
                        "status": record["status"],
                        "returncode": record["returncode"],
                        "elapsed_seconds": record["elapsed_seconds"],
                    },
                    ensure_ascii=False,
                ),
                flush=True,
            )
    records.sort(key=lambda item: str(item["name"]))
    summary = {
        "schema": "s34-free-tail-sweep-v1",
        "created_utc": utc_now(),
        "worker_sha256": digest(WORKER),
        "launcher_sha256": digest(Path(__file__).resolve()),
        "wall_timeout": args.wall_timeout,
        "address_space": args.address_space,
        "workers": args.workers,
        "records": records,
        "counts": {
            status: sum(record["status"] == status for record in records)
            for status in ("sat", "unsat", "unknown")
        },
    }
    summary_path = args.out / "summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    print(
        json.dumps(
            {
                "summary": str(summary_path),
                "summary_sha256": digest(summary_path),
                "counts": summary["counts"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if summary["counts"]["unknown"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
