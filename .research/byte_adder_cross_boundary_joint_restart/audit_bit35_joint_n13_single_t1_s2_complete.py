"""Aggregate the complete n13/C5-single/T5=1/S5=2 g16 shard family."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Any

import bit35_joint_c5_normal_form as c5_normal
import bit35_joint_phase_driver_classes as phase_normal


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
OUTPUT = HERE / "bit35_joint_g16_n13_c5_single_t1_s2_complete_audit.json"
GATE_BOUND = 16
COMPONENTS = 13
T5_DRIVERS = 1
S5_DRIVERS = 2
TRUTH_DOMAIN_SHA256 = "1c9768429735b2f87bca12bb62dad82624f45a419b80ea6b5470655764c34b60"


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: object) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return sha256(encoded).hexdigest()


def atomic_write(path: Path, payload: dict[str, Any]) -> str:
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(encoded)
    temporary.replace(path)
    return sha256(encoded).hexdigest()


def canonical_artifact_shards() -> tuple[str, ...]:
    pattern = re.compile(r"g16_n13_c5_(single_k\d+)_t1_s2\.json")
    matches = {
        match.group(1)
        for path in RESULTS.iterdir()
        if path.is_file() and (match := pattern.fullmatch(path.name)) is not None
    }
    return tuple(sorted(matches, key=lambda shard: int(shard.removeprefix("single_k"))))


def main() -> int:
    expected_shards = tuple(
        shard
        for shard in c5_normal.shard_domain(COMPONENTS, GATE_BOUND)
        if shard.startswith("single_k")
    )
    exact_domain = tuple(f"single_k{k}" for k in range(13))
    if expected_shards != exact_domain:
        raise RuntimeError(f"n13 singleton domain changed: {expected_shards}")
    if c5_normal.maximum_switches(COMPONENTS, GATE_BOUND) != 3:
        raise RuntimeError("n13/g16 maximum Switch count changed")
    if phase_normal.driver_count_domain(COMPONENTS, GATE_BOUND) != (1, 2, 3):
        raise RuntimeError("n13/g16 phase driver-count domain changed")

    errors: list[str] = []
    records: list[dict[str, Any]] = []
    observed_artifact_shards = canonical_artifact_shards()
    if observed_artifact_shards != expected_shards:
        errors.append(
            "canonical artifact shard domain "
            f"{observed_artifact_shards} != expected {expected_shards}"
        )

    phase_digest = phase_normal.constraint_sha256(
        COMPONENTS,
        GATE_BOUND,
        T5_DRIVERS,
        S5_DRIVERS,
    )
    for shard in expected_shards:
        k = int(shard.removeprefix("single_k"))
        base = f"g16_n13_c5_{shard}_t1_s2"
        artifact_path = RESULTS / f"{base}.json"
        run_path = RESULTS / f"{base}.run.json"
        launcher_path = RESULTS / f"{base}.launcher.log"
        audit_path = HERE / f"bit35_joint_{base}_terminal_audit.json"
        evidence_paths = (artifact_path, run_path, launcher_path, audit_path)
        for path in evidence_paths:
            if not path.is_file():
                errors.append(f"missing {path.name}")
        if any(not path.is_file() for path in evidence_paths):
            continue

        artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
        run = json.loads(run_path.read_text(encoding="utf-8"))
        launcher = json.loads(launcher_path.read_text(encoding="utf-8"))
        audit = json.loads(audit_path.read_text(encoding="utf-8"))
        expected_metadata = {
            "schema": "tc-byte-adder-bit35-joint-phase-driver-shard-v1",
            "status": "unsat",
            "profile": "d7_80_bit35_joint",
            "gate_bound": GATE_BOUND,
            "components": COMPONENTS,
            "c5_shard": shard,
            "t5_drivers": T5_DRIVERS,
            "s5_drivers": S5_DRIVERS,
            "assignments": 96,
            "truth_domain_sha256": TRUTH_DOMAIN_SHA256,
            "solver": "cadical195",
            "timeout_seconds": 0.0,
        }
        for key, expected in expected_metadata.items():
            if artifact.get(key) != expected:
                errors.append(
                    f"{artifact_path.name}:{key}={artifact.get(key)!r} != {expected!r}"
                )

        c5_digest = c5_normal.constraint_sha256(shard, COMPONENTS, GATE_BOUND)
        if artifact.get("c5_constraint_sha256") != c5_digest:
            errors.append(f"{artifact_path.name}: C5 digest mismatch")
        if artifact.get("phase_constraint_sha256") != phase_digest:
            errors.append(f"{artifact_path.name}: phase digest mismatch")

        artifact_hash = file_sha256(artifact_path)
        expected_launcher = {
            "status": "unsat",
            "components": COMPONENTS,
            "c5_shard": shard,
            "t5_drivers": T5_DRIVERS,
            "s5_drivers": S5_DRIVERS,
            "solve_seconds": artifact.get("solve_seconds"),
            "output": f"results/{base}.json",
            "output_sha256": artifact_hash,
        }
        if launcher != expected_launcher:
            errors.append(f"{launcher_path.name}: launcher summary mismatch")

        if run.get("classification") != "solver_exit" or run.get("exit_code") != 0:
            errors.append(f"{run_path.name}: non-terminal wrapper result")
        if (
            run.get("watchdog_seconds"),
            run.get("as_limit_kib"),
            run.get("nice"),
        ) != (21600, 4194304, 10):
            errors.append(f"{run_path.name}: resource policy mismatch")

        run_hash = file_sha256(run_path)
        if (
            audit.get("status") != "pass"
            or audit.get("terminal_classification") != "strict_unsat"
            or audit.get("artifact", {}).get("sha256") != artifact_hash
            or audit.get("run_record", {}).get("sha256") != run_hash
            or audit.get("recomputed_constraints", {}).get("c5_constraint_sha256")
            != c5_digest
            or audit.get("recomputed_constraints", {}).get("phase_constraint_sha256")
            != phase_digest
            or audit.get("errors") != []
        ):
            errors.append(f"{audit_path.name}: terminal audit is not a clean strict UNSAT")

        records.append(
            {
                "k": k,
                "shard": shard,
                "artifact": str(artifact_path.resolve()),
                "artifact_sha256": artifact_hash,
                "run_record": str(run_path.resolve()),
                "run_record_sha256": run_hash,
                "launcher_log": str(launcher_path.resolve()),
                "launcher_log_sha256": file_sha256(launcher_path),
                "terminal_audit": str(audit_path.resolve()),
                "terminal_audit_sha256": file_sha256(audit_path),
                "c5_constraint_sha256": c5_digest,
                "phase_constraint_sha256": phase_digest,
                "solve_seconds": artifact.get("solve_seconds"),
                "elapsed_seconds": artifact.get("elapsed_seconds"),
                "status": artifact.get("status"),
            }
        )

    observed_shards = tuple(record["shard"] for record in records)
    if observed_shards != expected_shards:
        errors.append(
            f"observed evidence shard domain {observed_shards} != expected {expected_shards}"
        )
    status_counts = {
        status: sum(record["status"] == status for record in records)
        for status in ("sat", "unsat", "unknown")
    }
    if status_counts != {"sat": 0, "unsat": 13, "unknown": 0}:
        errors.append(f"unexpected status counts: {status_counts}")

    collection_identity = [
        {
            "shard": record["shard"],
            "artifact_sha256": record["artifact_sha256"],
            "run_record_sha256": record["run_record_sha256"],
            "launcher_log_sha256": record["launcher_log_sha256"],
            "terminal_audit_sha256": record["terminal_audit_sha256"],
        }
        for record in records
    ]
    result = {
        "schema": "tc-byte-adder-bit35-joint-n13-single-t1-s2-complete-audit-v1",
        "status": "pass" if not errors else "fail",
        "scope": {
            "gate_bound": GATE_BOUND,
            "components": COMPONENTS,
            "c5_driver_class": "single_component",
            "c5_driver_count": 1,
            "t5_drivers": T5_DRIVERS,
            "s5_drivers": S5_DRIVERS,
            "maximum_switches_by_weight": 3,
            "minimum_weighted_cut_cost": 13,
            "maximum_weighted_cut_cost": 16,
            "truth_domain_rows": 96,
            "truth_domain_sha256": TRUTH_DOMAIN_SHA256,
        },
        "coverage": {
            "expected_shards": list(expected_shards),
            "expected_count": len(expected_shards),
            "observed_count": len(records),
            "missing_shards": sorted(set(expected_shards) - set(observed_shards)),
            "extra_shards": sorted(set(observed_artifact_shards) - set(expected_shards)),
            "status_counts": status_counts,
            "complete": observed_shards == expected_shards and not errors,
            "argument": (
                "For n=13 the singleton C5 normal form places all strict component "
                "ancestors first, the single C5 driver next, and all non-ancestors "
                "last. The thirteen counts k=0..12 partition every singleton C5 "
                "component driver while retaining every optional Switch/XOR network "
                "allowed by g<=16. T5 has exactly one component driver and S5 has "
                "exactly two Switch drivers."
            ),
            "not_all_c5_single_phase_pairs": True,
            "not_a_global_g16_claim": True,
        },
        "timing": {
            "total_solve_seconds": sum(float(record["solve_seconds"]) for record in records),
            "maximum_solve_seconds": max(
                (float(record["solve_seconds"]) for record in records), default=0.0
            ),
            "maximum_solve_shard": max(
                records,
                key=lambda record: float(record["solve_seconds"]),
                default={},
            ).get("shard"),
        },
        "collection_sha256": canonical_sha256(collection_identity),
        "records": records,
        "errors": errors,
    }
    output_sha = atomic_write(OUTPUT, result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"sha256={output_sha}")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
