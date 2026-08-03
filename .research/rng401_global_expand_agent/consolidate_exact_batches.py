"""Consolidate exact SAT checkpoints and reject incomplete evidence sets."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def digest_t(record: dict) -> str:
    payload = "".join(
        f"{int(str(row), 16):08x}" for row in record["T"]
    ).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def iter_jsonl(path: Path):
    with path.open(encoding="utf-8-sig") as stream:
        for line_number, raw in enumerate(stream, 1):
            if raw.strip():
                yield line_number, json.loads(raw)


def set_hash(values) -> str:
    payload = "".join(f"{value}\n" for value in sorted(values)).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--checkpoints", type=Path, nargs="+", required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--expected-count", type=int, required=True)
    parser.add_argument("--logic-budget", type=int, required=True)
    parser.add_argument("--fixed-gate", type=int, required=True)
    parser.add_argument("--delay", type=int, required=True)
    parser.add_argument("--cycles", type=int, required=True)
    args = parser.parse_args()

    candidates: dict[str, int] = {}
    for line_number, record in iter_jsonl(args.candidate):
        digest = digest_t(record)
        if digest in candidates:
            raise AssertionError(f"duplicate candidate T at lines {candidates[digest]},{line_number}")
        candidates[digest] = line_number

    results: dict[str, dict] = {}
    artifacts = []
    peak_rss = 0.0
    solver_seconds = 0.0
    clauses = []
    for checkpoint in args.checkpoints:
        summary_path = checkpoint.with_suffix(".json")
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        expected_metadata = {
            "status": "unsat-complete",
            "complete": True,
            "truncated": False,
        }
        for key, expected in expected_metadata.items():
            if summary.get(key) != expected:
                raise AssertionError(f"{summary_path}: {key}={summary.get(key)!r}")
        cost = summary["cost"]
        target = summary["target"]
        if (
            int(cost["logic_budget"]) != args.logic_budget
            or int(cost["fixed_shell_gate"]) != args.fixed_gate
            or int(target["gate"]) != args.fixed_gate + args.logic_budget
            or int(target["delay"]) != args.delay
            or int(target["cycles"]) != args.cycles
        ):
            raise AssertionError(f"{summary_path}: cost/target metadata mismatch")

        checkpoint_count = 0
        for line_number, record in iter_jsonl(checkpoint):
            checkpoint_count += 1
            digest = str(record["T_sha256"]).lower()
            if str(record.get("status", "")).lower() != "unsat":
                raise AssertionError(f"{checkpoint}:{line_number}: non-UNSAT status")
            if digest in results:
                raise AssertionError(f"duplicate result T {digest}")
            results[digest] = {
                "checkpoint": checkpoint.name,
                "line": line_number,
                "clause_sha256": record["clause_sha256"],
            }
            clauses.append(str(record["clause_sha256"]).lower())
            peak_rss = max(peak_rss, float(record.get("peak_rss_mb") or 0.0))
            solver_seconds += float(record.get("elapsed_seconds") or 0.0)
        if checkpoint_count != int(summary["processed_record_count"]):
            raise AssertionError(f"{checkpoint}: checkpoint/summary count mismatch")
        artifacts.append({
            "checkpoint": str(checkpoint),
            "checkpoint_bytes": checkpoint.stat().st_size,
            "checkpoint_sha256": sha256_file(checkpoint),
            "summary": str(summary_path),
            "summary_bytes": summary_path.stat().st_size,
            "summary_sha256": sha256_file(summary_path),
            "record_count": checkpoint_count,
        })

    if len(candidates) != args.expected_count or len(results) != args.expected_count:
        raise AssertionError(
            f"expected {args.expected_count}, candidates={len(candidates)}, results={len(results)}"
        )
    if set(candidates) != set(results):
        raise AssertionError(
            f"candidate/result mismatch: missing={len(set(candidates)-set(results))} "
            f"extra={len(set(results)-set(candidates))}"
        )

    result = {
        "schema": 1,
        "status": "unsat-complete",
        "candidate": {
            "path": str(args.candidate),
            "bytes": args.candidate.stat().st_size,
            "sha256": sha256_file(args.candidate),
            "unique_T": len(candidates),
            "T_set_sha256": set_hash(candidates),
        },
        "model": {
            "path": str(args.model),
            "bytes": args.model.stat().st_size,
            "sha256": sha256_file(args.model),
        },
        "cost": {
            "fixed_shell_gate": args.fixed_gate,
            "logic_budget": args.logic_budget,
            "target_gate": args.fixed_gate + args.logic_budget,
            "delay": args.delay,
            "cycles": args.cycles,
            "xor2_gate": 3,
            "xor2_delay": 2,
        },
        "results": {
            "unique_T": len(results),
            "unsat": len(results),
            "sat": 0,
            "unknown": 0,
            "clause_set_sha256": set_hash(clauses),
            "solver_seconds_sum": round(solver_seconds, 6),
            "peak_rss_mb": round(peak_rss, 3),
        },
        "artifacts": artifacts,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(args.output),
        "candidate": result["candidate"],
        "results": result["results"],
        "output_sha256": sha256_file(args.output),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
