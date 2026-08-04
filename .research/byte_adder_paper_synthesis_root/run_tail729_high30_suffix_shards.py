"""Run disjoint 729-row suffix shards for a 103/5 Byte Adder tie.

The reviewed S3/S4 family costs 11 gates.  Two additional D4 phases are
already exposed as paid sources by the worker, so a 17-gate physical tail
gives a 30-gate high window and a complete 103/5/515 design.  Every timeout
remains UNKNOWN; only a canonical result payload can report SAT or UNSAT.
"""

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
WORKER = (
    ROOT
    / ".research"
    / "byte_adder_phase_shortcut_restart"
    / "exact_tail729_with_s34_family1_two_phase_free.py"
)
GATE_BOUND = 17
SPLIT_SLOTS = 3
DECOMPOSITIONS = (
    ("g17_o01_s08_x0", 9, 8, 0),
    ("g17_o03_s07_x0", 10, 7, 0),
    ("g17_o05_s06_x0", 11, 6, 0),
    ("g17_o07_s05_x0", 12, 5, 0),
)


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


worker_module = _load_module("tail729_high30_worker", WORKER)


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, payload: object) -> None:
    path.write_bytes(
        (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    )


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def suffix_metadata(
    components: int, switches: int, xors: int, shard_count: int, shard_index: int
) -> dict[str, object]:
    universe = worker_module.base.physical.suffix_universe(
        components=components,
        split_slots=SPLIT_SLOTS,
        switches=switches,
        xors=xors,
    )
    assigned = tuple(
        signature
        for index, signature in enumerate(universe)
        if index % shard_count == shard_index
    )

    def encode(rows) -> bytes:
        return json.dumps(
            [
                [worker_module.base.physical.G.KINDS[kind] for kind in row]
                for row in rows
            ],
            sort_keys=True,
            separators=(",", ":"),
        ).encode()

    return {
        "split_slots": SPLIT_SLOTS,
        "shard_count": shard_count,
        "shard_index": shard_index,
        "universe_count": len(universe),
        "universe_sha256": sha256(encode(universe)).hexdigest(),
        "assigned_count": len(assigned),
        "assigned_sha256": sha256(encode(assigned)).hexdigest(),
    }


def validate_payload(
    path: Path, components: int, switches: int, xors: int
) -> tuple[str, list[str]]:
    if not path.is_file():
        return "unknown", ["result payload absent"]
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return "unknown", [f"result payload parse failed: {exc}"]
    errors = []
    status = str(payload.get("status", "unknown")).lower()
    expected = {
        "schema": "exact-s34-family1-two-phase-physical729-tail-v1",
        "rows": 729,
        "gate_bound": GATE_BOUND,
        "max_delay": 5,
        "components": components,
        "exact_switches": switches,
        "exact_xors": xors,
        "physical_nets": True,
        "public_outputs_must_be_driven": True,
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            errors.append(f"{key}: expected {value!r}, got {payload.get(key)!r}")
    if tuple(payload.get("output_names", ())) != ("S5", "S6", "S7", "C8"):
        errors.append("unexpected output_names")
    if status not in {"sat", "unsat", "unknown"}:
        errors.append(f"unexpected status {status!r}")
    dependencies = payload.get("extended_dependency_sha256", {})
    if dependencies.get(str(WORKER.relative_to(ROOT)).replace("\\", "/")) != digest(
        WORKER
    ):
        errors.append("worker dependency hash mismatch")
    return (status if not errors else "unknown"), errors


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
    profile: str,
    resume: bool,
) -> dict[str, object]:
    prefix, components, switches, xors = decomposition
    name = f"{profile}_{prefix}_suffix3_shard{shard_index:02d}-of-{shard_count:02d}"
    job_dir = out_dir / name
    job_dir.mkdir(parents=True, exist_ok=True)
    result_path = job_dir / "result.json"
    stdout_path = job_dir / "stdout.log"
    stderr_path = job_dir / "stderr.log"
    timing_path = job_dir / "time.log"
    run_path = job_dir / "run.json"
    if resume and run_path.is_file():
        record = json.loads(run_path.read_text(encoding="utf-8"))
        record["resumed_from_existing_record"] = True
        return record

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
        "--phase-profile",
        profile,
        "--gate-bound",
        str(GATE_BOUND),
        "--max-delay",
        "5",
        "--components",
        str(components),
        "--switches",
        str(switches),
        "--xors",
        str(xors),
        "--split-slots",
        str(SPLIT_SLOTS),
        "--shard-count",
        str(shard_count),
        "--shard-index",
        str(shard_index),
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
    status, validation_errors = validate_payload(
        result_path, components, switches, xors
    )
    if completed.returncode != 0 and status != "sat":
        status = "unknown"
    record = {
        "schema": "tail729-high30-suffix-shard-run-v1",
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
            "gate_bound": GATE_BOUND,
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
            "stdout_sha256": digest(stdout_path),
            "stderr_sha256": digest(stderr_path),
            "time_sha256": digest(timing_path) if timing_path.is_file() else None,
        },
    }
    write_json(run_path, record)
    if status == "sat":
        write_json(out_dir / "RAW_SAT_FOUND.json", record)
    return record


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--shard-count", type=int, default=16)
    parser.add_argument("--workers", type=int, default=12)
    parser.add_argument("--wall-timeout", type=int, default=900)
    parser.add_argument("--address-space", type=int, default=2147483648)
    parser.add_argument("--nice", type=int, default=0)
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--profile", choices=("primary", "alternate"), default="primary")
    parser.add_argument("--python", type=Path, default=ROOT / ".venv/bin/python")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
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
                    "suffix_universe_counts": {
                        prefix: suffix_metadata(
                            components, switches, xors, 1, 0
                        )["universe_count"]
                        for prefix, components, switches, xors in DECOMPOSITIONS
                    },
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    args.out.mkdir(parents=True, exist_ok=True)
    records = []
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
                profile=args.profile,
                resume=args.resume,
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
    counts = {
        status: sum(record["status"] == status for record in records)
        for status in ("sat", "unsat", "unknown")
    }
    summary = {
        "schema": "tail729-high30-suffix-shard-sweep-v1",
        "created_utc": utc_now(),
        "worker_sha256": digest(WORKER),
        "launcher_sha256": digest(Path(__file__).resolve()),
        "complete_score_target": {"gate": 103, "delay": 5, "energy": 515},
        "profile": args.profile,
        "shard_count": args.shard_count,
        "workers": args.workers,
        "wall_timeout": args.wall_timeout,
        "address_space": args.address_space,
        "records": records,
        "counts": counts,
    }
    summary_path = args.out / "summary.json"
    write_json(summary_path, summary)
    print(json.dumps({"summary": str(summary_path), "counts": counts}, indent=2))
    return 0 if counts["unknown"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
