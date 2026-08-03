"""Audit the OR-to-NOT one-kind neighbor of the tail ordinary multiset."""

from __future__ import annotations

import argparse
from hashlib import sha256
import itertools
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORKER = HERE / "physical_exact.py"
ORDINARY_MULTISET = ("NOT", "NOR", "OR", "NOT")
TERMINAL = {"sat", "unsat"}
ZERO_FIELDS = (
    "mismatch_count",
    "bus_conflict_count",
    "undriven_output_count",
    "physical_net_partition_violation_count",
    "depth_upper_bound_violation_count",
    "output_deadline_violation_count",
)


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def constraint_digest(fixed: tuple[str, ...]) -> str:
    encoded = json.dumps(
        fixed,
        ensure_ascii=True,
        separators=(",", ":"),
    ).encode("ascii")
    return sha256(encoded).hexdigest()


def audit(spec_path: Path) -> dict[str, object]:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    proof = spec.get("proof_scope", {})
    repository = (spec_path.parent / spec["working_directory"]).resolve()
    expected_orders = set(itertools.permutations(ORDINARY_MULTISET))
    seen_orders: set[tuple[str, ...]] = set()
    seen_names: set[str] = set()
    seen_outputs: set[str] = set()
    overlaps = 0
    constraint_records: list[dict[str, str]] = []
    records: list[dict[str, object]] = []
    missing = invalid = unknown = 0
    sat_paths: list[str] = []

    for value in spec.get("values", ()):
        fixed = tuple(str(value.get("fixed_kinds", "")).split(","))
        ordinary = fixed[:4]
        actual_constraint = constraint_digest(fixed)
        suffix = "-".join(kind.lower() for kind in ordinary)
        expected_name = f"s567c8-d5-g18-o04-s07-adj-or2not-{suffix}"
        name = str(value.get("name"))
        output = str(value.get("output", ""))
        record: dict[str, object] = {
            "name": value.get("name"),
            "constraint_sha256_expected": value.get("constraint_sha256"),
            "constraint_sha256_actual": actual_constraint,
        }
        structural = (
            len(fixed) == 11
            and ordinary in expected_orders
            and fixed[4:] == ("SWITCH",) * 7
            and name == expected_name
            and output.endswith(f"/{expected_name}.json")
            and value.get("constraint_sha256") == actual_constraint
            and value.get("domain") == "s34567c8_leaf"
            and value.get("outputs") == "S5,S6,S7,C8"
            and int(value.get("gate", -1)) == 18
            and int(value.get("delay", -1)) == 5
            and int(value.get("components", -1)) == 11
            and int(value.get("ordinary", -1)) == 4
            and int(value.get("switches", -1)) == 7
            and int(value.get("xors", -1)) == 0
        )
        if ordinary in seen_orders or name in seen_names or output in seen_outputs:
            overlaps += 1
        seen_orders.add(ordinary)
        seen_names.add(name)
        seen_outputs.add(output)
        constraint_records.append({"name": name, "sha256": actual_constraint})
        path = repository / output
        record["path"] = str(path)
        if not structural:
            record["state"] = "invalid-manifest-value"
            invalid += 1
            records.append(record)
            continue
        if not path.is_file():
            record["state"] = "missing"
            missing += 1
            records.append(record)
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            record.update({"state": "invalid-json", "error": repr(exc)})
            invalid += 1
            records.append(record)
            continue
        status = payload.get("status")
        checks = (
            payload.get("schema") == "exact-fast-negative-physical-shard-v2"
            and payload.get("domain") == "s34567c8_leaf"
            and tuple(payload.get("output_names", ()))
            == ("S5", "S6", "S7", "C8")
            and int(payload.get("gate_bound", -1)) == 18
            and int(payload.get("max_delay", -1)) == 5
            and int(payload.get("components", -1)) == 11
            and int(payload.get("ordinary", -1)) == 4
            and int(payload.get("exact_switches", -1)) == 7
            and int(payload.get("exact_xors", -1)) == 0
            and tuple(payload.get("fixed_kinds", ())) == fixed
            and payload.get("physical_nets") is True
            and payload.get("public_outputs_must_be_driven") is True
            and payload.get("dependency_sha256")
            == proof.get("dependency_sha256")
        )
        if status == "sat":
            verification = payload.get("verification", {})
            checks = checks and all(
                int(verification.get(field, -1)) == 0 for field in ZERO_FIELDS
            )
            checks = checks and int(payload.get("actual_gate", 10**9)) <= 18
            checks = checks and int(
                verification.get("actual_max_delay", 10**9)
            ) <= 5
        record.update(
            {
                "status": status,
                "sha256": digest(path),
                "solve_seconds": payload.get("solve_seconds"),
            }
        )
        if not checks:
            record["state"] = "invalid-payload"
            invalid += 1
        elif status not in TERMINAL:
            record["state"] = "unknown"
            unknown += 1
        else:
            record["state"] = "terminal"
            if status == "sat":
                sat_paths.append(str(path))
        records.append(record)

    constraint_set = json.dumps(
        constraint_records,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    constraint_set_actual = sha256(constraint_set).hexdigest()
    proof_matches = (
        proof.get("domain") == "s34567c8_leaf"
        and proof.get("outputs") == ["S5", "S6", "S7", "C8"]
        and int(proof.get("gate", -1)) == 18
        and int(proof.get("max_delay", -1)) == 5
        and int(proof.get("components", -1)) == 11
        and int(proof.get("ordinary", -1)) == 4
        and int(proof.get("switches", -1)) == 7
        and int(proof.get("xors", -1)) == 0
        and proof.get("base_ordinary_multiset") == ["NOT", "NOR", "OR", "OR"]
        and proof.get("ordinary_multiset") == list(ORDINARY_MULTISET)
        and proof.get("one_kind_change") == "OR->NOT"
        and int(proof.get("unique_orders", -1)) == 12
        and proof.get("unknown_is_not_unsat") is True
    )
    manifest_complete = (
        spec.get("schema") == "tc-byte-adder-remote-sweep-v1"
        and spec.get("script") == "physical_exact.py"
        and spec.get("stop_on_first_sat") is True
        and len(spec.get("values", ())) == 12
        and seen_orders == expected_orders
        and len(seen_names) == 12
        and len(seen_outputs) == 12
        and overlaps == 0
        and proof_matches
        and constraint_set_actual == proof.get("constraint_set_sha256")
    )
    worker_match = proof.get("worker_sha256") == digest(WORKER)
    if sat_paths and manifest_complete and worker_match and not invalid:
        status = "sat-witnesses"
    elif (
        manifest_complete
        and worker_match
        and not missing
        and not invalid
        and not unknown
        and all(record.get("status") == "unsat" for record in records)
    ):
        status = "unsat-covered"
    else:
        status = "incomplete"
    return {
        "schema": "s567c8-g18-o4-s7-adjacent-or-to-not-audit-v1",
        "status": status,
        "coverage": "or-to-not-neighbor-terminal-switch-class-only",
        "spec": str(spec_path),
        "spec_sha256": digest(spec_path),
        "worker_sha256_expected": proof.get("worker_sha256"),
        "worker_sha256_actual": digest(WORKER),
        "worker_sha256_match": worker_match,
        "constraint_set_sha256_expected": proof.get("constraint_set_sha256"),
        "constraint_set_sha256_actual": constraint_set_actual,
        "manifest_complete": manifest_complete,
        "proof_scope_match": proof_matches,
        "orders_expected": 12,
        "orders_seen": len(seen_orders),
        "overlap_count": overlaps,
        "jobs_expected": 12,
        "missing_jobs": missing,
        "invalid_jobs": invalid,
        "unknown_jobs": unknown,
        "sat_witnesses": sat_paths,
        "records": records,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("spec", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = audit(args.spec.resolve())
    encoded = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0 if payload["status"] in {"sat-witnesses", "unsat-covered"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
