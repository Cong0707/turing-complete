#!/usr/bin/env python3
"""Strictly audit the completed 64-shard primary tail729 high30 sweep."""

from __future__ import annotations

import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNNER_PATH = (
    ROOT
    / ".research/byte_adder_paper_synthesis_root/"
    "run_tail729_high30_suffix_shards.py"
)
HEX64 = set("0123456789abcdef")


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


runner = _load_module("tail729_high30_primary_sweep_audit_runner", RUNNER_PATH)


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def canonical_sha(payload: object) -> str:
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_bytes())
    if not isinstance(payload, dict):
        raise RuntimeError(f"JSON root is not an object: {path}")
    return payload


def expected_jobs(shard_count: int = 16, profile: str = "primary") -> list[dict[str, Any]]:
    jobs = []
    for decomposition_name, components, switches, xors in runner.DECOMPOSITIONS:
        universe = runner.worker_module.base.physical.suffix_universe(
            components=components,
            split_slots=runner.SPLIT_SLOTS,
            switches=switches,
            xors=xors,
        )
        for shard_index in range(shard_count):
            assigned = [
                [runner.worker_module.base.physical.G.KINDS[kind] for kind in signature]
                for index, signature in enumerate(universe)
                if index % shard_count == shard_index
            ]
            suffix = runner.suffix_metadata(
                components, switches, xors, shard_count, shard_index
            )
            name = (
                f"{profile}_{decomposition_name}_suffix3_"
                f"shard{shard_index:02d}-of-{shard_count:02d}"
            )
            formula_spec = {
                "schema": "tail729-high30-formula-spec-v1",
                "worker_sha256": digest(runner.WORKER),
                "worker_dependencies": runner.worker_module.dependency_sha256(),
                "profile": profile,
                "gate_bound": runner.GATE_BOUND,
                "max_delay": 5,
                "components": components,
                "switches": switches,
                "xors": xors,
                "split_slots": runner.SPLIT_SLOTS,
                "shard_count": shard_count,
                "shard_index": shard_index,
                "suffix_universe_sha256": suffix["universe_sha256"],
                "assigned_suffix_sha256": suffix["assigned_sha256"],
            }
            jobs.append(
                {
                    "name": name,
                    "decomposition_name": decomposition_name,
                    "components": components,
                    "ordinary": components - switches - xors,
                    "switches": switches,
                    "xors": xors,
                    "shard_index": shard_index,
                    "suffix_shard": suffix,
                    "assigned_suffix_signatures": assigned,
                    "formula_spec_sha256": canonical_sha(formula_spec),
                    "formula_spec": formula_spec,
                }
            )
    return jobs


def audit(sweep_dir: Path) -> dict[str, Any]:
    sweep_dir = sweep_dir.resolve()
    summary_path = sweep_dir / "summary.json"
    if not summary_path.is_file():
        raise RuntimeError("main sweep summary.json is absent; runner is not complete")
    summary = load_json(summary_path)
    errors: list[str] = []
    if summary.get("schema") != "tail729-high30-suffix-shard-sweep-v1":
        errors.append("summary schema changed")
    if summary.get("profile") != "primary" or summary.get("shard_count") != 16:
        errors.append("summary primary/16-shard contract changed")
    if summary.get("worker_sha256") != digest(runner.WORKER):
        errors.append("summary worker SHA changed")
    if summary.get("launcher_sha256") != digest(RUNNER_PATH):
        errors.append("summary launcher SHA changed")

    summary_records = summary.get("records")
    if not isinstance(summary_records, list):
        errors.append("summary records missing")
        summary_records = []
    summary_by_name = {
        str(record.get("name")): record
        for record in summary_records
        if isinstance(record, dict)
    }
    if len(summary_by_name) != len(summary_records):
        errors.append("summary record names are duplicated")

    records = []
    for expected in expected_jobs():
        name = expected["name"]
        job_dir = sweep_dir / name
        run_path = job_dir / "run.json"
        result_path = job_dir / "result.json"
        if not run_path.is_file():
            errors.append(f"{name}: run.json absent")
            continue
        run = load_json(run_path)
        if run.get("schema") != "tail729-high30-suffix-shard-run-v1":
            errors.append(f"{name}: run schema changed")
        if run.get("name") != name:
            errors.append(f"{name}: run name changed")
        if run.get("decomposition") != {
            "gate_bound": runner.GATE_BOUND,
            "components": expected["components"],
            "ordinary": expected["ordinary"],
            "switches": expected["switches"],
            "xors": expected["xors"],
        }:
            errors.append(f"{name}: decomposition changed")
        if run.get("suffix_shard") != expected["suffix_shard"]:
            errors.append(f"{name}: suffix metadata changed")
        if summary_by_name.get(name) != run:
            errors.append(f"{name}: summary/run record mismatch")

        result = load_json(result_path) if result_path.is_file() else None
        artifacts = run.get("artifacts", {})
        if result is None:
            if artifacts.get("result_sha256") is not None:
                errors.append(f"{name}: absent result has a SHA")
        elif artifacts.get("result_sha256") != digest(result_path):
            errors.append(f"{name}: result SHA mismatch")

        status = "unknown"
        if result is not None and result.get("status") in {"sat", "unsat"}:
            candidate = str(result["status"])
            clean_result = (
                result.get("schema")
                == "exact-s34-family1-two-phase-physical729-tail-v1"
                and result.get("extended_dependency_sha256")
                == runner.worker_module.dependency_sha256()
                and result.get("gate_bound") == runner.GATE_BOUND
                and result.get("max_delay") == 5
                and result.get("components") == expected["components"]
                and result.get("exact_switches") == expected["switches"]
                and result.get("exact_xors") == expected["xors"]
                and tuple(result.get("output_names", ())) == ("S5", "S6", "S7", "C8")
            )
            clean_run = (
                run.get("status") == candidate
                and run.get("returncode") == 0
                and run.get("timed_out") is False
                and run.get("validation_errors") == []
            )
            if clean_result and clean_run:
                status = candidate
            else:
                errors.append(f"{name}: unclean {candidate} result/run")
        elif not (
            run.get("status") == "unknown"
            and run.get("returncode") in {124, 137}
            and run.get("timed_out") is True
        ):
            errors.append(f"{name}: UNKNOWN provenance changed")

        records.append(
            {
                **expected,
                "status": status,
                "run": {
                    "path": str(run_path),
                    "sha256": digest(run_path),
                    "returncode": run.get("returncode"),
                    "timed_out": run.get("timed_out"),
                    "elapsed_seconds": run.get("elapsed_seconds"),
                    "solver": "cadical195",
                },
                "result": (
                    {
                        "path": str(result_path),
                        "sha256": digest(result_path),
                        "variables": result.get("variables"),
                        "clauses": result.get("clauses"),
                        "solve_seconds": result.get("solve_seconds"),
                    }
                    if result is not None
                    else None
                ),
            }
        )

    unexpected_dirs = sorted(
        path.name
        for path in sweep_dir.iterdir()
        if path.is_dir() and path.name not in {job["name"] for job in expected_jobs()}
    )
    if unexpected_dirs:
        errors.append(f"unexpected job directories: {unexpected_dirs}")
    counts = {
        status: sum(record["status"] == status for record in records)
        for status in ("sat", "unsat", "unknown")
    }
    if summary.get("counts") != counts:
        errors.append("summary counts differ from independent classification")
    decomposition_counts = {}
    for name, _components, _switches, _xors in runner.DECOMPOSITIONS:
        selected = [record for record in records if record["decomposition_name"] == name]
        decomposition_counts[name] = {
            status: sum(record["status"] == status for record in selected)
            for status in ("sat", "unsat", "unknown")
        }
    spec_hashes = [record["formula_spec_sha256"] for record in records]
    if len(spec_hashes) != len(set(spec_hashes)):
        errors.append("formula-spec SHA collision or duplicate")
    return {
        "schema": "tail729-high30-primary-sweep-independent-audit-v1",
        "status": "verified" if not errors else "invalid",
        "sweep": str(sweep_dir),
        "summary": {"path": str(summary_path), "sha256": digest(summary_path)},
        "runner": {"path": str(RUNNER_PATH), "sha256": digest(RUNNER_PATH)},
        "worker": {
            "path": str(runner.WORKER),
            "sha256": digest(runner.WORKER),
            "dependencies": runner.worker_module.dependency_sha256(),
        },
        "counts": counts,
        "decomposition_counts": decomposition_counts,
        "job_count": len(records),
        "complete_64_job_coverage": len(records) == 64,
        "formula_spec_sha256_unique_count": len(set(spec_hashes)),
        "global_lower_bound_proved": counts == {"sat": 0, "unsat": 64, "unknown": 0},
        "records": records,
        "errors": errors,
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path = path.resolve()
    if not path.is_relative_to(HERE):
        raise RuntimeError(f"audit output is outside research line: {path}")
    if path.exists():
        raise RuntimeError(f"refusing to overwrite {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode()
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(encoded)
    temporary.replace(path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("sweep_dir", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    report = audit(args.sweep_dir)
    write_json(args.output, report)
    print(
        json.dumps(
            {
                "status": report["status"],
                "counts": report["counts"],
                "decomposition_counts": report["decomposition_counts"],
                "complete_64_job_coverage": report["complete_64_job_coverage"],
                "global_lower_bound_proved": report["global_lower_bound_proved"],
                "errors": report["errors"],
                "output": str(args.output.resolve()),
                "sha256": digest(args.output),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if report["status"] == "verified" else 1


if __name__ == "__main__":
    raise SystemExit(main())
