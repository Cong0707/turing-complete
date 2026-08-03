"""Aggregate the complete n14/C5-multi-d2/T5=1/S5=1 g16 shard family.

At gate bound 16 and component count 14, a C5 bus with two Switch drivers
exhausts the entire two-gate weight slack.  Therefore there are exactly two
Switches, no XORs, and the previously reviewed phase-driver argument forces
T5 and S5 to be singleton component outputs.  The C5 normal form then leaves
exactly the thirteen ancestor counts k=0..12 audited here.
"""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Any

import bit35_joint_c5_normal_form as c5_normal
import bit35_joint_phase_driver_classes as phase_normal


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
OUTPUT = HERE / "bit35_joint_g16_n14_c5_multi_d2_t1_s1_complete_audit.json"
GATE_BOUND = 16
COMPONENTS = 14
T5_DRIVERS = 1
S5_DRIVERS = 1
TRUTH_DOMAIN_SHA256 = "1c9768429735b2f87bca12bb62dad82624f45a419b80ea6b5470655764c34b60"


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: object) -> str:
    return sha256(
        json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode(
            "ascii"
        )
    ).hexdigest()


def atomic_write(path: Path, payload: dict[str, Any]) -> str:
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(encoded)
    temporary.replace(path)
    return sha256(encoded).hexdigest()


def main() -> int:
    expected_shards = tuple(
        shard
        for shard in c5_normal.shard_domain(COMPONENTS, GATE_BOUND)
        if shard.startswith("multi_d2_k")
    )
    if expected_shards != tuple(f"multi_d2_k{k}" for k in range(13)):
        raise RuntimeError(f"n14 multi-d2 domain changed: {expected_shards}")
    if c5_normal.maximum_switches(COMPONENTS, GATE_BOUND) != 2:
        raise RuntimeError("n14/g16 maximum Switch count changed")
    if phase_normal.driver_count_domain(COMPONENTS, GATE_BOUND) != (1, 2):
        raise RuntimeError("n14/g16 phase driver-count domain changed")

    errors: list[str] = []
    records: list[dict[str, Any]] = []
    phase_digest = phase_normal.constraint_sha256(
        COMPONENTS, GATE_BOUND, T5_DRIVERS, S5_DRIVERS
    )
    for shard in expected_shards:
        k = int(shard.removeprefix("multi_d2_k"))
        base = f"g16_n14_c5_{shard}_t1_s1"
        artifact_path = RESULTS / f"{base}.json"
        run_path = RESULTS / f"{base}.run.json"
        audit_path = HERE / f"bit35_joint_{base}_terminal_audit.json"
        for path in (artifact_path, run_path, audit_path):
            if not path.is_file():
                errors.append(f"missing {path.name}")
        if any(not path.is_file() for path in (artifact_path, run_path, audit_path)):
            continue

        artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
        run = json.loads(run_path.read_text(encoding="utf-8"))
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
        if run.get("classification") != "solver_exit" or run.get("exit_code") != 0:
            errors.append(f"{run_path.name}: non-terminal wrapper result")
        if (
            run.get("watchdog_seconds"),
            run.get("as_limit_kib"),
            run.get("nice"),
        ) != (21600, 4194304, 10):
            errors.append(f"{run_path.name}: resource policy mismatch")
        artifact_hash = file_sha256(artifact_path)
        run_hash = file_sha256(run_path)
        if (
            audit.get("status") != "pass"
            or audit.get("terminal_classification") != "strict_unsat"
            or audit.get("artifact", {}).get("sha256") != artifact_hash
            or audit.get("run_record", {}).get("sha256") != run_hash
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
            f"observed shard order/domain {observed_shards} != expected {expected_shards}"
        )
    status_counts = {
        status: sum(record["status"] == status for record in records)
        for status in ("sat", "unsat", "unknown")
    }
    collection_identity = [
        {
            "shard": record["shard"],
            "artifact_sha256": record["artifact_sha256"],
            "run_record_sha256": record["run_record_sha256"],
            "terminal_audit_sha256": record["terminal_audit_sha256"],
        }
        for record in records
    ]
    result = {
        "schema": "tc-byte-adder-bit35-joint-n14-multi-d2-complete-audit-v1",
        "status": "pass" if not errors else "fail",
        "scope": {
            "gate_bound": GATE_BOUND,
            "components": COMPONENTS,
            "c5_driver_class": "multi_switch",
            "c5_driver_count": 2,
            "t5_drivers": T5_DRIVERS,
            "s5_drivers": S5_DRIVERS,
            "maximum_switches_by_weight": 2,
            "forced_total_switches": 2,
            "forced_total_xors": 0,
            "truth_domain_rows": 96,
            "truth_domain_sha256": TRUTH_DOMAIN_SHA256,
        },
        "coverage": {
            "expected_shards": list(expected_shards),
            "expected_count": len(expected_shards),
            "observed_count": len(records),
            "missing_shards": sorted(set(expected_shards) - set(observed_shards)),
            "extra_shards": sorted(set(observed_shards) - set(expected_shards)),
            "status_counts": status_counts,
            "complete": observed_shards == expected_shards,
            "argument": (
                "For n=14 and g<=16, two C5 Switch drivers consume all weight slack: "
                "total switches=2 and XORs=0. C5 consumes both Switches, so T5 and S5 "
                "cannot be multi-driver and the reviewed direct-source exclusion forces "
                "one component driver each. The C5 normal form enumerates exactly k=0..12."
            ),
            "not_a_global_g16_claim": True,
        },
        "timing": {
            "total_solve_seconds": sum(float(record["solve_seconds"]) for record in records),
            "maximum_solve_seconds": max(
                (float(record["solve_seconds"]) for record in records), default=0.0
            ),
            "maximum_solve_shard": max(
                records, key=lambda record: float(record["solve_seconds"]), default={}
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
