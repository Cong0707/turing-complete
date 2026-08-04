"""Concrete terminal-kind priority sweep for the S3/S4-free tail."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORKER = HERE / "exact_tail_with_s34_free.py"
BASE_RUNNER_PATH = HERE / "run_s34_free_tail_sweep.py"
DECOMPOSITIONS = (
    ("g18_o04_s07_x0", 11, 7, 0),
    ("g18_o06_s06_x0", 12, 6, 0),
    ("g18_o08_s05_x0", 13, 5, 0),
)
ORDINARY = ("NOT", "AND", "OR", "NAND", "NOR")


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


base_runner = _load_module("s34_free_terminal_base_runner", BASE_RUNNER_PATH)


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def priority_suffixes() -> tuple[tuple[str, str, str], ...]:
    result = [("SWITCH", "SWITCH", "SWITCH")]
    for ordinary in ORDINARY:
        for slot in range(3):
            row = ["SWITCH", "SWITCH", "SWITCH"]
            row[slot] = ordinary
            result.append(tuple(row))
    return tuple(result)


def run_job(
    out_dir: Path,
    decomposition: tuple[str, int, int, int],
    suffix: tuple[str, str, str],
    *,
    python: Path,
    wall_timeout: int,
    address_space: int,
    nice: int,
    solver: str,
) -> dict[str, object]:
    prefix, components, switches, xors = decomposition
    suffix_name = "-".join(name.lower() for name in suffix)
    name = f"{prefix}_terminal_{suffix_name}"
    job_dir = out_dir / name
    job_dir.mkdir(parents=True, exist_ok=True)
    result_path = job_dir / "result.json"
    stdout_path = job_dir / "stdout.log"
    stderr_path = job_dir / "stderr.log"
    timing_path = job_dir / "time.log"
    run_path = job_dir / "run.json"
    fixed_kinds = ["*"] * (components - 3) + list(suffix)
    command = [
        "/usr/bin/time", "-v", "-o", str(timing_path),
        "timeout", "--signal=TERM", "--kill-after=30s", f"{wall_timeout}s",
        "prlimit", f"--as={address_space}", "--",
        "nice", "-n", str(nice),
        str(python), str(WORKER),
        "--gate-bound", "18",
        "--max-delay", "5",
        "--components", str(components),
        "--switches", str(switches),
        "--xors", str(xors),
        "--fixed-kinds", ",".join(fixed_kinds),
        "--split-slots", "0",
        "--shard-count", "1",
        "--shard-index", "0",
        "--solver", solver,
        "--timeout", "0",
        "--output", str(result_path),
    ]
    started = utc_now()
    before = time.monotonic()
    with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
        completed = subprocess.run(
            command, cwd=ROOT, stdout=stdout, stderr=stderr, check=False
        )
    elapsed = time.monotonic() - before
    status, validation_errors = base_runner.validate_payload(result_path)
    if completed.returncode != 0 and status != "sat":
        status = "unknown"
    record = {
        "schema": "s34-free-tail-terminal-priority-run-v1",
        "name": name,
        "decomposition_name": prefix,
        "started_utc": started,
        "finished_utc": utc_now(),
        "elapsed_seconds": elapsed,
        "returncode": completed.returncode,
        "timed_out": completed.returncode in {124, 137},
        "status": status,
        "validation_errors": validation_errors,
        "command": command,
        "decomposition": {
            "gate_bound": 18,
            "components": components,
            "ordinary": components - switches - xors,
            "switches": switches,
            "xors": xors,
        },
        "terminal_suffix": suffix,
        "fixed_kinds": fixed_kinds,
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
    run_path.write_bytes((json.dumps(record, ensure_ascii=False, indent=2) + "\n").encode())
    record["run"] = str(run_path)
    record["run_sha256"] = digest(run_path)
    return record


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--wall-timeout", type=int, default=300)
    parser.add_argument("--address-space", type=int, default=1610612736)
    parser.add_argument("--nice", type=int, default=10)
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--python", type=Path, default=ROOT / ".venv/bin/python")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    suffixes = priority_suffixes()
    jobs = [
        (decomposition, suffix)
        for suffix in suffixes
        for decomposition in DECOMPOSITIONS
    ]
    if not 1 <= args.workers <= len(jobs):
        parser.error(f"workers must be in 1..{len(jobs)}")
    if args.dry_run:
        print(
            json.dumps(
                {
                    "job_count": len(jobs),
                    "suffix_count": len(suffixes),
                    "suffixes": suffixes,
                    "decompositions": DECOMPOSITIONS,
                    "workers": args.workers,
                    "worker_sha256": digest(WORKER),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    args.out.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, object]] = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(
                run_job,
                args.out,
                decomposition,
                suffix,
                python=args.python,
                wall_timeout=args.wall_timeout,
                address_space=args.address_space,
                nice=args.nice,
                solver=args.solver,
            ): (decomposition[0], suffix)
            for decomposition, suffix in jobs
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
    records.sort(key=lambda record: str(record["name"]))
    summary = {
        "schema": "s34-free-tail-terminal-priority-sweep-v1",
        "created_utc": utc_now(),
        "complete_priority_set": True,
        "global_decomposition_lower_bound_proved": False,
        "worker_sha256": digest(WORKER),
        "base_runner_sha256": digest(BASE_RUNNER_PATH),
        "launcher_sha256": digest(Path(__file__).resolve()),
        "workers": args.workers,
        "wall_timeout": args.wall_timeout,
        "address_space": args.address_space,
        "suffixes": suffixes,
        "records": records,
        "counts": {
            status: sum(record["status"] == status for record in records)
            for status in ("sat", "unsat", "unknown")
        },
    }
    summary_path = args.out / "summary.json"
    summary_path.write_bytes((json.dumps(summary, ensure_ascii=False, indent=2) + "\n").encode())
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
