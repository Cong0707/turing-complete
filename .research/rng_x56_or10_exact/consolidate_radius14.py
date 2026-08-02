"""Consolidate the checkpointed radius-14 exact joint audit.

This script only reads research artifacts.  It verifies that every input
matrix occurs exactly once, that its digest still matches the source JSONL,
and that every retained solver result is a completed UNSAT result.
"""

from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUT = ROOT / ".research" / "rng_word_residual_search" / "radius14-x56-neighbors.jsonl"
OUTPUT = HERE / "radius14-joint-mediated-unsat-complete.json"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def matrix_digest(record: dict[str, object]) -> str:
    rows = record["T"]
    if not isinstance(rows, list) or len(rows) != 32:
        raise AssertionError("T must have 32 rows")
    normalized = "".join(f"{int(str(row), 16):08x}" for row in rows)
    return hashlib.sha256(normalized.encode("ascii")).hexdigest()


def load_json_record(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    records = payload.get("records")
    if not isinstance(records, list) or len(records) != 1:
        raise AssertionError(f"{path.name} must contain exactly one record")
    return records[0]


def main() -> None:
    inputs = [
        json.loads(line)
        for line in INPUT.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    expected = {
        line: matrix_digest(record) for line, record in enumerate(inputs, start=1)
    }
    if len(expected) != 128 or len(set(expected.values())) != 128:
        raise AssertionError("radius-14 input is not 128 unique matrices")

    chosen: dict[int, tuple[dict[str, object], str, str]] = {}

    def retain(item: dict[str, object], solver: str, encoding: str) -> None:
        source_line = int(item["source_line"])
        if source_line in chosen:
            raise AssertionError(f"duplicate completed result for line {source_line}")
        if item["status"] != "unsat":
            raise AssertionError(f"line {source_line} is not completed UNSAT")
        if item["T_sha256"] != expected[source_line]:
            raise AssertionError(f"line {source_line} matrix digest mismatch")
        chosen[source_line] = (item, solver, encoding)

    retain(load_json_record(HERE / "radius14-first221.json"), "g4", "seqcounter")
    retain(
        load_json_record(HERE / "radius14-line2-221-m22-kmt.json"),
        "m22",
        "kmtotalizer",
    )
    retain(
        load_json_record(HERE / "radius14-line3-m22-mtotalizer-45s.json"),
        "m22",
        "mtotalizer",
    )

    timed_out: set[int] = set()
    for checkpoint in sorted(HERE.glob("radius14-m22-mtotalizer-?.jsonl")):
        for raw in checkpoint.read_text(encoding="utf-8").splitlines():
            if not raw.strip():
                continue
            item = json.loads(raw)
            source_line = int(item["source_line"])
            if item["status"] == "unknown":
                timed_out.add(source_line)
                continue
            retain(item, "m22", "mtotalizer")

    expected_timeouts = {42, 53, 75, 117}
    if timed_out != expected_timeouts:
        raise AssertionError(f"unexpected timeout set: {sorted(timed_out)}")
    for source_line in sorted(timed_out):
        retain(
            load_json_record(HERE / f"line{source_line}-g4-mtotalizer-90s.json"),
            "g4",
            "mtotalizer",
        )

    if set(chosen) != set(expected):
        missing = sorted(set(expected) - set(chosen))
        extra = sorted(set(chosen) - set(expected))
        raise AssertionError(f"coverage mismatch missing={missing} extra={extra}")

    records = []
    for source_line in sorted(chosen):
        item, solver, encoding = chosen[source_line]
        records.append(
            {
                "source_line": source_line,
                "T_sha256": item["T_sha256"],
                "status": item["status"],
                "solver": solver,
                "budget_encoding": encoding,
                "elapsed_seconds": item["elapsed_seconds"],
                "variable_count": item["variable_count"],
                "clause_count": item["clause_count"],
                "clause_sha256": item["clause_sha256"],
                "peak_rss_bytes": item["peak_rss_bytes"],
            }
        )

    solver_counts = Counter(record["solver"] for record in records)
    encoding_counts = Counter(record["budget_encoding"] for record in records)
    result = {
        "schema": 1,
        "status": "unsat-complete",
        "complete": True,
        "model": "exact joint arbitrary pair cover + mediated B weight1/2 + tick-zero OR labels",
        "scope": {
            "candidate_count": 128,
            "logic_budget": 221,
            "fixed_shell_gate": 166,
            "gate_target": 387,
            "delay": 10,
            "cycles": 66,
            "xor2_gate": 3,
            "xor2_delay": 2,
            "or_gate": 1,
            "or_delay": 1,
            "ram": False,
            "topology_limit": None,
            "component_limit": None,
            "global_beam": None,
        },
        "coverage": {
            "unsat": 128,
            "sat": 0,
            "unknown": 0,
            "initial_timeout_lines": sorted(timed_out),
            "resolved_timeout_lines": sorted(timed_out),
            "solver_counts": dict(sorted(solver_counts.items())),
            "encoding_counts": dict(sorted(encoding_counts.items())),
        },
        "resources": {
            "solver_elapsed_seconds_sum": sum(
                float(record["elapsed_seconds"]) for record in records
            ),
            "peak_rss_bytes": max(int(record["peak_rss_bytes"]) for record in records),
        },
        "evidence": {
            "input": str(INPUT),
            "input_sha256": sha256_file(INPUT),
            "model_script": str(HERE / "joint_mediated_sat.py"),
            "model_script_sha256": sha256_file(HERE / "joint_mediated_sat.py"),
            "record_T_sha256_unique": len({record["T_sha256"] for record in records}),
            "clause_sha256_unique": len(
                {record["clause_sha256"] for record in records}
            ),
        },
        "records": records,
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {key: value for key, value in result.items() if key != "records"},
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
