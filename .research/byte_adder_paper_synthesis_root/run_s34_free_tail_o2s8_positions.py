"""Exact positional sweep for the interleaved S3/S4-free o2/s8 tail.

The two ordinary components are left as kind wildcards while all other slots
are fixed to ``SWITCH``.  The exact global quotas in the physical encoder then
make each wildcard one of NOT/AND/OR/NAND/NOR.  Consequently one job covers all
25 ordered ordinary-kind pairs for one of the C(10, 2) topological placements.

External timeouts, signals, missing payloads, and malformed payloads remain
UNKNOWN.  This launcher never promotes an interrupted search to UNSAT.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from hashlib import sha256
import importlib.util
import itertools
import json
from pathlib import Path
import subprocess
import sys
import time


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORKER = HERE / "exact_tail_with_s34_free.py"
BASE_RUNNER_PATH = HERE / "run_s34_free_tail_sweep.py"
COMPONENTS = 10
SWITCHES = 8
GATE_BOUND = 18


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


base_runner = _load_module("s34_free_o2s8_position_base", BASE_RUNNER_PATH)


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def placement_class(first: int, second: int) -> str:
    """Return a deterministic search-priority class for one placement."""

    if first >= 2 and second <= COMPONENTS - 2:
        return "strict_switch_ordinary_switch"
    if first >= 2:
        return "switch_ordinary_terminal_ordinary"
    if second <= COMPONENTS - 2:
        return "early_ordinary_interleaved"
    return "ordinary_edge_normal_form"


def placements() -> tuple[tuple[int, int], ...]:
    """Return all 45 placements, high-value interleaves first."""

    rows = tuple(itertools.combinations(range(COMPONENTS), 2))
    priority = {
        "strict_switch_ordinary_switch": 0,
        "switch_ordinary_terminal_ordinary": 1,
        "early_ordinary_interleaved": 2,
        "ordinary_edge_normal_form": 3,
    }
    return tuple(
        sorted(
            rows,
            key=lambda pair: (
                priority[placement_class(*pair)],
                -pair[0],
                pair[1],
            ),
        )
    )


def fixed_kinds(pair: tuple[int, int]) -> tuple[str, ...]:
    result = ["SWITCH"] * COMPONENTS
    for slot in pair:
        result[slot] = "*"
    return tuple(result)


def run_job(
    out_dir: Path,
    pair: tuple[int, int],
    *,
    python: Path,
    wall_timeout: int,
    address_space: int,
    nice: int,
    solver: str,
) -> dict[str, object]:
    first, second = pair
    name = f"g18_o02_s08_x0_ordinary_slots_{first:02d}_{second:02d}"
    job_dir = out_dir / name
    job_dir.mkdir(parents=True, exist_ok=True)
    result_path = job_dir / "result.json"
    stdout_path = job_dir / "stdout.log"
    stderr_path = job_dir / "stderr.log"
    timing_path = job_dir / "time.log"
    run_path = job_dir / "run.json"
    kinds = fixed_kinds(pair)
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
        str(GATE_BOUND),
        "--max-delay",
        "5",
        "--components",
        str(COMPONENTS),
        "--switches",
        str(SWITCHES),
        "--xors",
        "0",
        "--fixed-kinds",
        ",".join(kinds),
        "--split-slots",
        "0",
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
            command, cwd=ROOT, stdout=stdout, stderr=stderr, check=False
        )
    elapsed = time.monotonic() - before
    status, validation_errors = base_runner.validate_payload(result_path)
    if completed.returncode != 0 and status != "sat":
        status = "unknown"
    record = {
        "schema": "s34-free-tail-o2s8-position-run-v1",
        "name": name,
        "started_utc": started,
        "finished_utc": utc_now(),
        "elapsed_seconds": elapsed,
        "returncode": completed.returncode,
        "timed_out": completed.returncode in {124, 137},
        "status": status,
        "validation_errors": validation_errors,
        "placement": {
            "ordinary_slots": pair,
            "class": placement_class(*pair),
            "ordered_ordinary_kind_assignments_covered": 25,
        },
        "decomposition": {
            "gate_bound": GATE_BOUND,
            "components": COMPONENTS,
            "ordinary": 2,
            "switches": SWITCHES,
            "xors": 0,
        },
        "fixed_kinds": kinds,
        "command": command,
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
    run_path.write_bytes(
        (json.dumps(record, ensure_ascii=False, indent=2) + "\n").encode()
    )
    record["run"] = str(run_path)
    record["run_sha256"] = digest(run_path)
    return record


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--wall-timeout", type=int, default=900)
    parser.add_argument("--address-space", type=int, default=1610612736)
    parser.add_argument("--nice", type=int, default=10)
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--python", type=Path, default=ROOT / ".venv/bin/python")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    jobs = placements()
    if not 1 <= args.workers <= len(jobs):
        parser.error(f"workers must be in 1..{len(jobs)}")
    if args.dry_run:
        counts = {
            category: sum(placement_class(*pair) == category for pair in jobs)
            for category in (
                "strict_switch_ordinary_switch",
                "switch_ordinary_terminal_ordinary",
                "early_ordinary_interleaved",
                "ordinary_edge_normal_form",
            )
        }
        print(
            json.dumps(
                {
                    "job_count": len(jobs),
                    "ordered_kind_assignments_per_job": 25,
                    "total_ordered_kind_assignments": len(jobs) * 25,
                    "placement_class_counts": counts,
                    "placements": jobs,
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
                pair,
                python=args.python,
                wall_timeout=args.wall_timeout,
                address_space=args.address_space,
                nice=args.nice,
                solver=args.solver,
            ): pair
            for pair in jobs
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
            if record["status"] == "sat":
                print("SAT witness found; remaining queued jobs continue", flush=True)
    records.sort(key=lambda record: str(record["name"]))
    summary = {
        "schema": "s34-free-tail-o2s8-position-sweep-v1",
        "created_utc": utc_now(),
        "complete_position_coverage": True,
        "complete_ordered_ordinary_kind_coverage": True,
        "global_o2s8_lower_bound_proved": all(
            record["status"] == "unsat" for record in records
        ),
        "worker_sha256": digest(WORKER),
        "base_runner_sha256": digest(BASE_RUNNER_PATH),
        "launcher_sha256": digest(Path(__file__).resolve()),
        "workers": args.workers,
        "wall_timeout": args.wall_timeout,
        "address_space": args.address_space,
        "records": records,
        "counts": {
            status: sum(record["status"] == status for record in records)
            for status in ("sat", "unsat", "unknown")
        },
    }
    summary_path = args.out / "summary.json"
    summary_path.write_bytes(
        (json.dumps(summary, ensure_ascii=False, indent=2) + "\n").encode()
    )
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
