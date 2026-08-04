"""Audit the downloaded S3/S4-free terminal-priority sweep evidence.

The sweep is intentionally a priority probe, not a proof sweep.  In
particular, a watchdog timeout must remain UNKNOWN.  This auditor verifies
the Cartesian job set, every recorded artifact hash, and the absence of SAT
or UNSAT result files before producing a compact machine-readable report.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import itertools
import json
from pathlib import Path


DECOMPOSITIONS = {
    "g18_o04_s07_x0": (18, 11, 4, 7, 0),
    "g18_o06_s06_x0": (18, 12, 6, 6, 0),
    "g18_o08_s05_x0": (18, 13, 8, 5, 0),
}


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def audit(root: Path) -> dict[str, object]:
    summary_path = root / "summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    errors: list[str] = []
    if summary.get("schema") != "s34-free-tail-terminal-priority-sweep-v1":
        errors.append("unexpected summary schema")
    if summary.get("complete_priority_set") is not True:
        errors.append("summary does not mark the priority set complete")
    if summary.get("global_decomposition_lower_bound_proved") is not False:
        errors.append("summary incorrectly claims a global lower bound")

    suffixes = tuple(tuple(item) for item in summary.get("suffixes", ()))
    if len(suffixes) != 16 or len(set(suffixes)) != 16:
        errors.append("terminal suffix universe is not 16 unique signatures")
    expected_pairs = set(itertools.product(DECOMPOSITIONS, suffixes))
    seen_pairs: set[tuple[str, tuple[str, ...]]] = set()
    status_counts = {"sat": 0, "unsat": 0, "unknown": 0}
    artifact_files = 0
    run_hashes: list[tuple[str, str]] = []

    records = summary.get("records", ())
    if len(records) != 48:
        errors.append(f"expected 48 summary records, got {len(records)}")
    for record in records:
        name = str(record.get("name", ""))
        decomposition_name = str(record.get("decomposition_name", ""))
        suffix = tuple(record.get("terminal_suffix", ()))
        pair = (decomposition_name, suffix)
        if pair in seen_pairs:
            errors.append(f"duplicate decomposition/suffix pair: {pair}")
        seen_pairs.add(pair)
        if pair not in expected_pairs:
            errors.append(f"unexpected decomposition/suffix pair: {pair}")

        run_relative = Path(str(record.get("run", "")))
        run_path = root / name / "run.json"
        if not run_path.is_file():
            errors.append(f"missing run.json: {name}")
            continue
        if run_relative.name != "run.json" or run_relative.parent.name != name:
            errors.append(f"summary run path disagrees with job name: {name}")
        actual_run_sha = digest(run_path)
        if actual_run_sha != record.get("run_sha256"):
            errors.append(f"run SHA mismatch: {name}")
        run_hashes.append((name, actual_run_sha))

        run = json.loads(run_path.read_text(encoding="utf-8"))
        for field in ("name", "decomposition_name", "terminal_suffix", "fixed_kinds"):
            if run.get(field) != record.get(field):
                errors.append(f"summary/run {field} mismatch: {name}")
        status = str(run.get("status"))
        if status not in status_counts:
            errors.append(f"invalid status {status}: {name}")
        else:
            status_counts[status] += 1
        if status != "unknown":
            errors.append(f"priority record is unexpectedly terminal: {name}={status}")
        if run.get("timed_out") is not True or int(run.get("returncode", -1)) != 124:
            errors.append(f"UNKNOWN is not an outer watchdog timeout: {name}")
        if run.get("validation_errors") != ["result file absent"]:
            errors.append(f"unexpected validation errors: {name}")

        expected = DECOMPOSITIONS.get(decomposition_name)
        decomposition = run.get("decomposition", {})
        actual = (
            int(decomposition.get("gate_bound", -1)),
            int(decomposition.get("components", -1)),
            int(decomposition.get("ordinary", -1)),
            int(decomposition.get("switches", -1)),
            int(decomposition.get("xors", -1)),
        )
        if actual != expected:
            errors.append(f"decomposition mismatch: {name}={actual}")
        fixed_kinds = tuple(run.get("fixed_kinds", ()))
        if len(fixed_kinds) != actual[1] or fixed_kinds[-3:] != suffix:
            errors.append(f"fixed-kind suffix mismatch: {name}")

        result_path = root / name / "result.json"
        if result_path.exists() or run.get("artifacts", {}).get("result_sha256") is not None:
            errors.append(f"timeout job unexpectedly has a result: {name}")
        for artifact in ("stdout", "stderr", "time"):
            path = root / name / f"{artifact}.log"
            if not path.is_file():
                errors.append(f"missing {artifact}: {name}")
                continue
            artifact_files += 1
            if digest(path) != run.get("artifacts", {}).get(f"{artifact}_sha256"):
                errors.append(f"{artifact} SHA mismatch: {name}")

    if seen_pairs != expected_pairs:
        errors.append(
            f"priority Cartesian coverage mismatch: expected={len(expected_pairs)} "
            f"seen={len(seen_pairs)}"
        )
    if summary.get("counts") != status_counts:
        errors.append(
            f"summary status counts mismatch: {summary.get('counts')} != {status_counts}"
        )
    stray_results = sorted(root.rglob("result.json"))
    if stray_results:
        errors.append(f"found {len(stray_results)} stray result files")

    stream = sha256()
    for name, run_sha in sorted(run_hashes):
        stream.update(f"{name}  {run_sha}\n".encode())
    return {
        "schema": "s34-free-tail-terminal-priority-independent-audit-v1",
        "status": "verified_unknown_priority_set" if not errors else "invalid",
        "scope": {
            "complete_priority_set": True,
            "global_decomposition_lower_bound_proved": False,
            "watchdog_timeout_is_unknown": True,
            "decompositions": list(DECOMPOSITIONS),
            "suffix_count": len(suffixes),
            "expected_jobs": len(expected_pairs),
        },
        "evidence": {
            "summary_sha256": digest(summary_path),
            "run_count": len(run_hashes),
            "artifact_file_count": artifact_files,
            "result_file_count": len(stray_results),
            "status_counts": status_counts,
            "run_name_sha_stream": stream.hexdigest(),
        },
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = audit(args.root.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["status"] == "verified_unknown_priority_set" else 1


if __name__ == "__main__":
    raise SystemExit(main())
