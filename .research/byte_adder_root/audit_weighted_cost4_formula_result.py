"""Independent structural audit for the weighted local formula closure.

This checker intentionally does not import the enumeration worker.  It
rebuilds the compact source partitions from the reviewed Factory DAG and
derives every expected formula-skeleton attempt count from the recorded level
sizes.  It also verifies the timing-independent payload hash.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DEFAULT_DAG = HERE / "byte-adder-hybrid-phasefold-g80-d7.json"
DEFAULT_RESULT = HERE / "weighted-cost4-formula-resub-80d7.json"
DEFAULT_OUTPUT = HERE / "weighted-cost4-formula-resub-80d7-audit.json"
MATERIALIZER = (
    ROOT / ".research" / "byte_adder_builder_layout_agent" / "materialize_factory_dag.py"
)
FULL_ROWS = 1 << 17


def load_materializer():
    spec = importlib.util.spec_from_file_location(
        "byte_adder_weighted_formula_result_auditor", MATERIALIZER
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(MATERIALIZER)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def unordered_pair_count(level_sizes: list[int], total_child_cost: int) -> int:
    count = 0
    for left_cost in range(total_child_cost + 1):
        right_cost = total_child_cost - left_cost
        if left_cost > right_cost:
            continue
        left_size = level_sizes[left_cost]
        right_size = level_sizes[right_cost]
        if left_cost == right_cost:
            count += left_size * (left_size + 1) // 2
        else:
            count += left_size * right_size
    return count


def expected_attempts(level_sizes: list[int], cost: int, source_count: int) -> dict[str, int]:
    if cost == 0:
        return {"SOURCE": source_count}
    ordinary_pairs = unordered_pair_count(level_sizes, cost - 1)
    expected = {
        "NOT": level_sizes[cost - 1],
        "AND": ordinary_pairs,
        "NAND": ordinary_pairs,
        "OR": ordinary_pairs,
        "NOR": ordinary_pairs,
    }
    if cost >= 2:
        expected["BUS1"] = sum(
            level_sizes[enable_cost] * level_sizes[cost - 2 - enable_cost]
            for enable_cost in range(cost - 1)
        )
    if cost >= 3:
        xor_pairs = unordered_pair_count(level_sizes, cost - 3)
        expected["XOR"] = xor_pairs
        expected["XNOR"] = xor_pairs
    if cost == 4:
        raw_driver_pairs = level_sizes[0] * level_sizes[0]
        expected["BUS2"] = raw_driver_pairs * (raw_driver_pairs + 1) // 2
    return expected


def compact_partition_rows(
    source_ids: list[int],
    target: int,
    states: dict[int, dict[str, int]],
) -> tuple[int, int]:
    classes: dict[tuple[int, ...], tuple[int, int, int]] = {}
    inconsistent = 0
    for row in range(FULL_ROWS):
        signature: list[int] = []
        for node_id in source_ids:
            state = states[node_id]
            signature.extend(
                (
                    (int(state["bits"]) >> row) & 1,
                    (int(state["driven"]) >> row) & 1,
                    (int(state["conflict"]) >> row) & 1,
                )
            )
        target_state = states[target]
        target_value = (
            (int(target_state["bits"]) >> row) & 1,
            (int(target_state["driven"]) >> row) & 1,
            (int(target_state["conflict"]) >> row) & 1,
        )
        key = tuple(signature)
        previous = classes.get(key)
        if previous is not None and previous != target_value:
            inconsistent += 1
        classes[key] = target_value
    return len(classes), inconsistent


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dag", type=Path, default=DEFAULT_DAG)
    parser.add_argument("--result", type=Path, default=DEFAULT_RESULT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    materializer = load_materializer()
    dag = json.loads(args.dag.read_text(encoding="utf-8"))
    result = json.loads(args.result.read_text(encoding="utf-8"))
    states = materializer.logical_states(tuple(dag["factory_dag"]["nodes"]))
    full_mask = (1 << FULL_ROWS) - 1
    errors: list[str] = []

    recorded_hash = str(result.get("deterministic_payload_sha256", ""))
    canonical = copy.deepcopy(result)
    canonical.pop("deterministic_payload_sha256", None)
    canonical["source"] = Path(str(canonical["source"])).name
    for item in canonical["targets"]:
        item.pop("search_seconds", None)
    actual_hash = hashlib.sha256(
        json.dumps(
            canonical,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    if actual_hash != recorded_hash:
        errors.append("deterministic payload hash mismatch")

    if result.get("status") != "unsat":
        errors.append("aggregate status is not unsat")
    if result.get("full_truth_rows") != FULL_ROWS:
        errors.append("full truth row count changed")
    if result.get("baseline", {}).get("gate") != 80:
        errors.append("baseline gate count changed")
    if result.get("baseline", {}).get("delay") != 7:
        errors.append("baseline delay changed")
    if result.get("baseline", {}).get("energy") != 560:
        errors.append("baseline energy changed")

    target_audits: list[dict[str, Any]] = []
    for item in result.get("targets", []):
        target = int(item["target"])
        source_ids = [int(value) for value in item["source_ids"]]
        compact_rows, inconsistent = compact_partition_rows(source_ids, target, states)
        target_state = states[target]
        public_target = (
            int(target_state["driven"]) == full_mask
            and int(target_state["conflict"]) == 0
        )
        levels = item["levels"]
        level_sizes = [int(level["deadline_feasible_states"]) for level in levels]
        attempt_checks = []
        for cost, level in enumerate(levels):
            expected = expected_attempts(level_sizes, cost, len(source_ids))
            observed = {key: int(value) for key, value in level["attempts"].items()}
            matches = observed == expected
            attempt_checks.append(
                {
                    "cost": cost,
                    "expected": expected,
                    "observed": observed,
                    "matches": matches,
                }
            )
            if not matches:
                errors.append(f"target {target} cost {cost} attempt coverage mismatch")

        target_ok = (
            compact_rows == int(item["compact_truth_rows"])
            and inconsistent == 0
            and public_target
            and item.get("status") == "unsat"
            and item.get("witness") is None
            and [int(level["cost"]) for level in levels]
            == list(range(int(item["replacement_cost"]) + 1))
            and all(check["matches"] for check in attempt_checks)
        )
        if not target_ok:
            errors.append(f"target {target} independent audit failed")
        target_audits.append(
            {
                "target": target,
                "output": item["output"],
                "compact_truth_rows_recomputed": compact_rows,
                "inconsistent_partition_rows": inconsistent,
                "public_target_fully_driven_conflict_free": public_target,
                "replacement_cost": int(item["replacement_cost"]),
                "final_deadline_feasible_states": level_sizes[-1],
                "attempt_checks": attempt_checks,
                "audit_pass": target_ok,
            }
        )

    audit = {
        "schema": "byte-adder-weighted-cost4-formula-result-audit-v1",
        "status": "pass" if not errors else "fail",
        "input": {
            "dag": str(args.dag.relative_to(ROOT)).replace("\\", "/"),
            "dag_sha256": file_sha256(args.dag),
            "result": str(args.result.relative_to(ROOT)).replace("\\", "/"),
            "result_sha256": file_sha256(args.result),
        },
        "full_truth_rows_repartitioned": FULL_ROWS,
        "deterministic_payload_sha256": {
            "recorded": recorded_hash,
            "recomputed": actual_hash,
            "matches": recorded_hash == actual_hash,
        },
        "targets": target_audits,
        "errors": errors,
    }
    args.output.write_bytes(
        (json.dumps(audit, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    )
    print(
        json.dumps(
            {
                "output": str(args.output.resolve()),
                "status": audit["status"],
                "targets": len(target_audits),
                "errors": errors,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
