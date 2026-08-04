"""Run disjoint suffix-kind shards for the S3/S4-free 18-gate tail."""

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


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


base_runner = _load_module("s34_free_base_runner", BASE_RUNNER_PATH)
domain_worker = _load_module("s34_free_shard_domain", WORKER)


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def suffix_metadata(
    components: int, switches: int, xors: int, shard_count: int, shard_index: int
) -> dict[str, object]:
    universe = domain_worker.physical.suffix_universe(
        components=components,
        split_slots=3,
        switches=switches,
        xors=xors,
    )
    assigned = tuple(
        signature
        for index, signature in enumerate(universe)
        if index % shard_count == shard_index
    )
    encode = lambda rows: json.dumps(
        [[domain_worker.physical.G.KINDS[kind] for kind in row] for row in rows],
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    return {
        "split_slots": 3,
        "shard_count": shard_count,
        "shard_index": shard_index,
        "universe_count": len(universe),
        "universe_sha256": sha256(encode(universe)).hexdigest(),
        "assigned_count": len(assigned),
        "assigned_sha256": sha256(encode(assigned)).hexdigest(),
    }


def run_job(
    out_dir: Path,
    decomposition: tuple[str, int, int, int],
    shard_count: int,
    shard_index: int,
    *,
    python: Path,
    wall_timeout: int,
    address_space: int,
    nice: int,
    solver: str,
) -> dict[str, object]:
    prefix, components, switches, xors = decomposition
    name = f"{prefix}_suffix3_shard{shard_index:02d}-of-{shard_count:02d}"
    job_dir = out_dir / name
    job_dir.mkdir(parents=True, exist_ok=True)
    result_path = job_dir / "result.json"
    stdout_path = job_dir / "stdout.log"
    stderr_path = job_dir / "stderr.log"
    timing_path = job_dir / "time.log"
    run_path = job_dir / "run.json"
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
        "--split-slots", "3",
        "--shard-count", str(shard_count),
        "--shard-index", str(shard_index),
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
        "schema": "s34-free-tail-suffix-shard-run-v1",
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
        "suffix_shard": suffix_metadata(
            components, switches, xors, shard_count, shard_index
        ),
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
    parser.add_argument("--shard-count", type=int, default=16)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--wall-timeout", type=int, default=1200)
    parser.add_argument("--address-space", type=int, default=1610612736)
    parser.add_argument("--nice", type=int, default=10)
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--python", type=Path, default=ROOT / ".venv/bin/python")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.shard_count < 1:
        parser.error("shard-count must be positive")
    jobs = [
        (decomposition, shard)
        for decomposition in DECOMPOSITIONS
        for shard in range(args.shard_count)
    ]
    if not 1 <= args.workers <= len(jobs):
        parser.error(f"workers must be in 1..{len(jobs)}")
    if args.dry_run:
        print(
            json.dumps(
                {
                    "job_count": len(jobs),
                    "decompositions": DECOMPOSITIONS,
                    "shard_count": args.shard_count,
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
                args.shard_count,
                shard,
                python=args.python,
                wall_timeout=args.wall_timeout,
                address_space=args.address_space,
                nice=args.nice,
                solver=args.solver,
            ): (decomposition[0], shard)
            for decomposition, shard in jobs
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
    decomposition_status = {}
    for prefix, _components, _switches, _xors in DECOMPOSITIONS:
        statuses = [
            record["status"]
            for record in records
            if record["decomposition_name"] == prefix
        ]
        decomposition_status[prefix] = (
            "sat"
            if "sat" in statuses
            else "unsat"
            if statuses and all(status == "unsat" for status in statuses)
            else "unknown"
        )
    summary = {
        "schema": "s34-free-tail-suffix-shard-sweep-v1",
        "created_utc": utc_now(),
        "worker_sha256": digest(WORKER),
        "base_runner_sha256": digest(BASE_RUNNER_PATH),
        "launcher_sha256": digest(Path(__file__).resolve()),
        "shard_count": args.shard_count,
        "workers": args.workers,
        "wall_timeout": args.wall_timeout,
        "address_space": args.address_space,
        "records": records,
        "counts": {
            status: sum(record["status"] == status for record in records)
            for status in ("sat", "unsat", "unknown")
        },
        "decomposition_status": decomposition_status,
    }
    summary_path = args.out / "summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    print(
        json.dumps(
            {
                "summary": str(summary_path),
                "summary_sha256": digest(summary_path),
                "counts": summary["counts"],
                "decomposition_status": decomposition_status,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if summary["counts"]["unknown"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
