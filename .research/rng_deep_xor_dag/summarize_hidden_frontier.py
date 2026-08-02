"""Validate and summarize the exact hidden-x56 frontier audit."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent


def load(name: str) -> dict[str, Any]:
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def jsonl(name: str) -> list[dict[str, Any]]:
    with (HERE / name).open(encoding="utf-8") as source:
        return [json.loads(line) for line in source if line.strip()]


def sha256(name: str) -> str:
    digest = hashlib.sha256()
    with (HERE / name).open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def hashes(records: list[dict[str, Any]]) -> set[str]:
    result = {str(record["t_sha256"]) for record in records}
    if len(result) != len(records):
        raise AssertionError("candidate JSONL contains duplicate T hashes")
    return result


def verify_phase(name: str, expected_records: int) -> tuple[int, int]:
    result = load(name)
    cost = result["cost_model"]
    if cost["ordinary_xor"] != [3, 2] or cost["u1_xor"] != [3, 2]:
        raise AssertionError(f"{name} uses the wrong scalar XOR cost")
    if cost["width_w_xor"] != ["3*w", 2]:
        raise AssertionError(f"{name} uses the wrong wide XOR cost")
    if cost["fixed_shell_gate"] != 230 or cost["target"] != [431, 9, 66]:
        raise AssertionError(f"{name} uses the wrong shell or target")
    if result["record_count"] != expected_records:
        raise AssertionError(f"{name} record count changed")
    if result["solve_count"] != result["cover_count"]:
        raise AssertionError(f"{name} did not solve every exact cover")
    if result["statuses"] != {"unsat": result["solve_count"]}:
        raise AssertionError(f"{name} contains SAT or UNKNOWN results")
    if result["best"] is not None:
        raise AssertionError(f"{name} unexpectedly contains a feasible candidate")
    for record in result["records"]:
        if record["cover_count"] != record["solve_count"]:
            raise AssertionError(f"{name} has an incomplete record")
        if record["statuses"] != {"unsat": record["solve_count"]}:
            raise AssertionError(f"{name} has a non-UNSAT record")
    return int(result["cover_count"]), int(result["solve_count"])


def verify_level(
    summary_name: str,
    frontier_name: str | None,
    expected_new: int,
) -> dict[str, Any]:
    summary = load(summary_name)
    histogram = {int(key): int(value) for key, value in summary["xor_histogram"].items()}
    if any(xor_count < 56 for xor_count in histogram):
        raise AssertionError(f"{summary_name} contains an x55-or-better state")
    if histogram.get(56, 0) != expected_new:
        raise AssertionError(f"{summary_name} x56 count changed")
    frontier_count = 0
    if frontier_name is not None:
        frontier = jsonl(frontier_name)
        frontier_count = len(frontier)
        if frontier_count != expected_new or any(item["exact_xor"] != 56 for item in frontier):
            raise AssertionError(f"{frontier_name} is not the expected exact-x56 frontier")
    elif expected_new:
        raise AssertionError("nonempty frontier lacks a JSONL certificate")
    return {
        "summary": summary_name,
        "scored_unique_neighbors": int(summary["scored_t_count"]),
        "exact_xor_histogram": {str(key): value for key, value in sorted(histogram.items())},
        "new_x56": expected_new,
        "frontier": frontier_name,
        "frontier_count": frontier_count,
    }


def main() -> int:
    initial = jsonl("radius10-15-hidden-x56.jsonl")
    level1 = jsonl("hidden-neighbor-new-exact-x56.jsonl")
    level2 = jsonl("plateau-r2-new-x56.jsonl")
    level3 = jsonl("plateau-r3-new-x56.jsonl")
    level4 = jsonl("plateau-r4-new-x56.jsonl")
    groups = [initial, level1, level2, level3, level4]
    union: set[str] = set()
    for group in groups:
        current = hashes(group)
        if union & current:
            raise AssertionError("x56 BFS frontier levels overlap")
        union |= current
    if [len(group) for group in groups] != [205, 43, 27, 11, 2]:
        raise AssertionError("x56 BFS frontier width changed")

    source = load("radius10-15-summary.json")
    if source["xor_histogram"] != {"56": 205, "57": 3373}:
        raise AssertionError("hidden-cover source histogram changed")
    if source["emitted_count"] != 205:
        raise AssertionError("hidden-cover source output changed")

    levels = [
        verify_level("hidden-neighbor-all-cover-summary.json", "hidden-neighbor-new-exact-x56.jsonl", 43),
        verify_level("plateau-r2-all-cover-summary.json", "plateau-r2-new-x56.jsonl", 27),
        verify_level("plateau-r3-all-cover-summary.json", "plateau-r3-new-x56.jsonl", 11),
        verify_level("plateau-r4-all-cover-summary.json", "plateau-r4-new-x56.jsonl", 2),
        verify_level("plateau-r5-all-cover-summary.json", None, 0),
    ]

    phase_groups = [
        ("hidden-x56-all-phase.json", 205),
        ("hidden-neighbor-new-all-phase.json", 43),
        ("plateau-r2-r4-all-phase.json", 40),
    ]
    phase = []
    total_covers = total_solves = 0
    for name, records in phase_groups:
        covers, solves = verify_phase(name, records)
        total_covers += covers
        total_solves += solves
        phase.append({"file": name, "records": records, "covers": covers, "unsat": solves})
    if total_covers != 800 or total_solves != 800:
        raise AssertionError("combined phase audit count changed")

    retained = [
        "2026-08-03-XOR宽度成本与隐藏x56前沿审计.md",
        "audit_hidden_covers.py",
        "audit_hidden_phase.py",
        "summarize_hidden_frontier.py",
        "radius10-15-hidden-x56.jsonl",
        "radius10-15-summary.json",
        "hidden-x56-all-phase.json",
        "hidden-neighbor-new-exact-x56.jsonl",
        "hidden-neighbor-new-all-phase.json",
        "plateau-r2-new-x56.jsonl",
        "plateau-r3-new-x56.jsonl",
        "plateau-r4-new-x56.jsonl",
        "plateau-r2-r4-x56.jsonl",
        "plateau-r2-r4-all-phase.json",
        "hidden-neighbor-all-cover-summary.json",
        "plateau-r2-all-cover-summary.json",
        "plateau-r3-all-cover-summary.json",
        "plateau-r4-all-cover-summary.json",
        "plateau-r5-all-cover-summary.json",
    ]
    result = {
        "schema": 1,
        "model": "complete exact-x56 legal-shear component audit",
        "scope": {
            "state_rows": "T/B/C rows remain nonzero and weight <= 4",
            "network": "shared scalar depth-two XOR2 DAG",
            "neighbor": "one GF(2) row shear",
            "phase": "physical U32 Switch phase CNF",
            "not_global_lower_bound": True,
        },
        "cost_model": {
            "ordinary_xor": [3, 2],
            "u1_xor": [3, 2],
            "u2_xor": [6, 2],
            "u3_xor": [9, 2],
            "u4_xor": [12, 2],
            "u8_xor": [24, 2],
            "width_w_xor": ["3*w", 2],
            "x56_logic_gate": 168,
            "fixed_shell_gate": 230,
            "phase_repair_budget": 33,
            "target": [431, 9, 66],
        },
        "source_pool": {
            "input_records": source["input_count"],
            "unique_states": source["unique_t_count"],
            "exact_xor_histogram": source["xor_histogram"],
            "x56_seed_count": len(initial),
        },
        "x56_component": {
            "level_widths": [len(group) for group in groups] + [0],
            "total_states": len(union),
            "neighbor_levels": levels,
            "x55_found": False,
        },
        "phase_audit": {
            "groups": phase,
            "records": len(union),
            "covers": total_covers,
            "statuses": {"unsat": total_solves},
            "sat": 0,
            "unknown": 0,
        },
        "files": {name: sha256(name) for name in retained},
    }
    (HERE / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "files"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
