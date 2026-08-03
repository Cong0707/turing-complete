"""Audit exact shard coverage and decoded physical witnesses."""

from __future__ import annotations

import argparse
from collections import defaultdict
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
WORKER_PATH = HERE / "physical_exact.py"
TERMINAL = {"sat", "unsat"}
ZERO_FIELDS = (
    "mismatch_count",
    "bus_conflict_count",
    "undriven_output_count",
    "physical_net_partition_violation_count",
    "depth_upper_bound_violation_count",
    "output_deadline_violation_count",
)


def _load_worker():
    spec = importlib.util.spec_from_file_location("phase_shortcut_audit_worker", WORKER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(WORKER_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


worker = _load_worker()


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def group_key(value: dict[str, object]) -> tuple[object, ...]:
    return (
        value["domain"],
        value.get("outputs", ""),
        int(value["delay"]),
        int(value["gate"]),
        int(value["components"]),
        int(value["switches"]),
        int(value["xors"]),
        int(value["split_slots"]),
        int(value["shard_count"]),
    )


def audit(spec_path: Path) -> dict[str, object]:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    if spec.get("schema") != "tc-byte-adder-remote-sweep-v1":
        raise ValueError("unsupported sweep schema")
    expected_worker = spec["proof_scope"]["worker_sha256"]
    actual_worker = digest(WORKER_PATH)
    worker_match = expected_worker == actual_worker
    expected_dependencies = spec["proof_scope"]["dependency_sha256"]
    actual_dependencies = worker.dependency_sha256()
    dependency_match = expected_dependencies == actual_dependencies
    repository = (spec_path.parent / spec["working_directory"]).resolve()
    groups: dict[tuple[object, ...], list[dict[str, object]]] = defaultdict(list)
    missing = invalid = unknown = 0
    sat_paths = []
    records = []
    for value in spec["values"]:
        path = repository / value["output"]
        record = {"name": value["name"], "path": str(path)}
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
        record.update({"state": "read", "status": status, "sha256": digest(path)})
        checks = (
            payload.get("schema") == "exact-fast-negative-physical-shard-v2"
            and payload.get("domain") == value["domain"]
            and int(payload.get("gate_bound", -1)) == int(value["gate"])
            and int(payload.get("max_delay", -1)) == int(value["delay"])
            and int(payload.get("components", -1)) == int(value["components"])
            and int(payload.get("exact_switches", -1)) == int(value["switches"])
            and int(payload.get("exact_xors", -1)) == int(value["xors"])
            and payload.get("physical_nets") is True
            and payload.get("public_outputs_must_be_driven") is True
            and payload.get("dependency_sha256") == expected_dependencies
        )
        if value.get("outputs"):
            checks = checks and tuple(payload.get("output_names", ())) == tuple(
                str(value["outputs"]).split(",")
            )
        shard = payload.get("shard", {})
        checks = checks and (
            int(shard.get("shard_count", -1)) == int(value["shard_count"])
            and int(shard.get("shard_index", -1)) == int(value["shard_index"])
            and int(shard.get("split_slots", -1))
            == min(int(value["split_slots"]), int(value["components"]))
        )
        if status == "sat":
            verification = payload.get("verification", {})
            checks = checks and all(int(verification.get(field, -1)) == 0 for field in ZERO_FIELDS)
            checks = checks and int(payload.get("actual_gate", 10**9)) <= int(value["gate"])
            checks = checks and int(verification.get("actual_max_delay", 10**9)) <= int(value["delay"])
            if checks:
                sat_paths.append(str(path))
        if not checks:
            record["state"] = "invalid-payload"
            invalid += 1
        elif status not in TERMINAL:
            record["state"] = "unknown"
            unknown += 1
        else:
            groups[group_key(value)].append({"value": value, "payload": payload})
        records.append(record)

    group_reports = []
    for key, items in sorted(groups.items(), key=lambda row: row[0]):
        (
            domain,
            outputs,
            delay,
            gate,
            components,
            switches,
            xors,
            split_slots,
            shard_count,
        ) = key
        expected = worker.suffix_universe(
            components=components,
            split_slots=split_slots,
            switches=switches,
            xors=xors,
        )
        expected_names = {
            tuple(worker.G.KINDS[kind] for kind in signature) for signature in expected
        }
        seen: set[tuple[str, ...]] = set()
        overlaps = 0
        shard_indices = set()
        statuses = []
        hashes = set()
        for item in items:
            value = item["value"]
            payload = item["payload"]
            shard_indices.add(int(value["shard_index"]))
            statuses.append(payload["status"])
            hashes.add(payload["shard"]["suffix_universe_sha256"])
            for signature in payload["shard"]["assigned_suffix_signatures"]:
                rendered = tuple(signature)
                if rendered in seen:
                    overlaps += 1
                seen.add(rendered)
        complete = (
            len(shard_indices) == shard_count
            and shard_indices == set(range(shard_count))
            and seen == expected_names
            and not overlaps
            and len(hashes) == 1
            and all(status in TERMINAL for status in statuses)
        )
        group_reports.append(
            {
                "domain": domain,
                "outputs": outputs.split(",") if outputs else None,
                "max_delay": delay,
                "gate": gate,
                "components": components,
                "switches": switches,
                "xors": xors,
                "shards_seen": len(shard_indices),
                "shards_expected": shard_count,
                "signatures_seen": len(seen),
                "signatures_expected": len(expected_names),
                "overlap_count": overlaps,
                "complete": complete,
                "sat_shards": statuses.count("sat"),
                "unsat_shards": statuses.count("unsat"),
            }
        )

    expected_groups = len(spec["proof_scope"]["decompositions"])
    complete_groups = sum(report["complete"] for report in group_reports)
    all_complete = (
            worker_match
            and dependency_match
        and not missing
        and not invalid
        and not unknown
        and len(group_reports) == expected_groups
        and complete_groups == expected_groups
    )
    if sat_paths:
        status = (
            "sat-witnesses"
            if worker_match and dependency_match and not invalid
            else "invalid"
        )
    elif all_complete:
        status = "unsat-covered"
    else:
        status = "incomplete"
    return {
        "schema": "fast-negative-physical-sweep-audit-v1",
        "status": status,
        "spec": str(spec_path.resolve()),
        "spec_sha256": digest(spec_path),
        "worker_sha256_expected": expected_worker,
        "worker_sha256_actual": actual_worker,
        "worker_sha256_match": worker_match,
        "dependency_sha256_expected": expected_dependencies,
        "dependency_sha256_actual": actual_dependencies,
        "dependency_sha256_match": dependency_match,
        "jobs_expected": len(spec["values"]),
        "missing_jobs": missing,
        "invalid_jobs": invalid,
        "unknown_jobs": unknown,
        "groups_expected": expected_groups,
        "groups_complete": complete_groups,
        "sat_witnesses": sat_paths,
        "groups": group_reports,
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
