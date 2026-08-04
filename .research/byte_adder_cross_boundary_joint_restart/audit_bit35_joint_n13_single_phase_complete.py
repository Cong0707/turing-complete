"""Aggregate one exact n13/C5-single phase-driver family without a solver."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Any

import bit35_joint_c5_normal_form as c5_normal
import bit35_joint_phase_driver_classes as phase_normal


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
GATE_BOUND = 16
COMPONENTS = 13
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
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(encoded)
    temporary.replace(path)
    return sha256(encoded).hexdigest()


def evidence_shards(t5_drivers: int, s5_drivers: int) -> tuple[str, ...]:
    suffix = f"t{t5_drivers}_s{s5_drivers}"
    pattern = re.compile(
        rf"g16_n13_c5_(single_k\d+)_{re.escape(suffix)}\.run\.json"
    )
    matches = {
        match.group(1)
        for path in RESULTS.iterdir()
        if path.is_file() and (match := pattern.fullmatch(path.name)) is not None
    }
    return tuple(sorted(matches, key=lambda shard: int(shard.removeprefix("single_k"))))


def terminal_classification(status: str) -> str:
    return {
        "sat": "sat_pending_independent_96_and_full_replay",
        "unsat": "strict_unsat",
        "unknown": "unknown_internal_timeout",
        "unknown_watchdog": "unknown_watchdog_timeout",
    }[status]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--t5-drivers", type=int, required=True)
    parser.add_argument("--s5-drivers", type=int, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    if (args.t5_drivers, args.s5_drivers) not in phase_normal.pair_domain(
        COMPONENTS, GATE_BOUND
    ):
        parser.error("phase-driver pair is outside the n13/g16 exact domain")
    output = (
        args.output.resolve()
        if args.output is not None
        else (
            HERE
            / (
                "bit35_joint_g16_n13_c5_single_"
                f"t{args.t5_drivers}_s{args.s5_drivers}_complete_audit.json"
            )
        ).resolve()
    )

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

    errors: list[str] = []
    records: list[dict[str, Any]] = []
    observed_evidence_shards = evidence_shards(args.t5_drivers, args.s5_drivers)
    if observed_evidence_shards != expected_shards:
        errors.append(
            "canonical run-record shard domain "
            f"{observed_evidence_shards} != expected {expected_shards}"
        )

    phase_digest = phase_normal.constraint_sha256(
        COMPONENTS,
        GATE_BOUND,
        args.t5_drivers,
        args.s5_drivers,
    )
    for shard in expected_shards:
        k = int(shard.removeprefix("single_k"))
        base = (
            f"g16_n13_c5_{shard}_"
            f"t{args.t5_drivers}_s{args.s5_drivers}"
        )
        artifact_path = RESULTS / f"{base}.json"
        run_path = RESULTS / f"{base}.run.json"
        launcher_path = RESULTS / f"{base}.launcher.log"
        audit_path = HERE / f"bit35_joint_{base}_terminal_audit.json"
        required_paths = (run_path, launcher_path, audit_path)
        for path in required_paths:
            if not path.is_file():
                errors.append(f"missing {path.name}")
        if any(not path.is_file() for path in required_paths):
            continue

        artifact = (
            json.loads(artifact_path.read_text(encoding="utf-8"))
            if artifact_path.is_file()
            else None
        )
        run = json.loads(run_path.read_text(encoding="utf-8"))
        audit = json.loads(audit_path.read_text(encoding="utf-8"))
        if artifact is None:
            status = "unknown_watchdog"
        else:
            status = str(artifact.get("status"))
            if status not in {"sat", "unsat", "unknown"}:
                errors.append(f"{artifact_path.name}: invalid status {status!r}")
                status = "unknown"

        c5_digest = c5_normal.constraint_sha256(shard, COMPONENTS, GATE_BOUND)
        artifact_hash = file_sha256(artifact_path) if artifact is not None else None
        if artifact is not None:
            expected_metadata = {
                "schema": "tc-byte-adder-bit35-joint-phase-driver-shard-v1",
                "profile": "d7_80_bit35_joint",
                "gate_bound": GATE_BOUND,
                "components": COMPONENTS,
                "c5_shard": shard,
                "t5_drivers": args.t5_drivers,
                "s5_drivers": args.s5_drivers,
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
            if artifact.get("c5_constraint_sha256") != c5_digest:
                errors.append(f"{artifact_path.name}: C5 digest mismatch")
            if artifact.get("phase_constraint_sha256") != phase_digest:
                errors.append(f"{artifact_path.name}: phase digest mismatch")

            try:
                launcher = json.loads(launcher_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                errors.append(f"{launcher_path.name}: invalid terminal JSON: {exc}")
            else:
                expected_launcher = {
                    "status": status,
                    "components": COMPONENTS,
                    "c5_shard": shard,
                    "t5_drivers": args.t5_drivers,
                    "s5_drivers": args.s5_drivers,
                    "solve_seconds": artifact.get("solve_seconds"),
                    "output": f"results/{base}.json",
                    "output_sha256": artifact_hash,
                }
                if launcher != expected_launcher:
                    errors.append(f"{launcher_path.name}: launcher summary mismatch")

        expected_run = {
            "sat": ("solver_exit", 0),
            "unsat": ("solver_exit", 0),
            "unknown": ("solver_exit", 2),
            "unknown_watchdog": ("watchdog_timeout", {124, 137}),
        }[status]
        if status == "unknown_watchdog":
            if (
                run.get("classification") != expected_run[0]
                or run.get("exit_code") not in expected_run[1]
            ):
                errors.append(f"{run_path.name}: invalid watchdog terminal result")
        elif (
            run.get("classification") != expected_run[0]
            or run.get("exit_code") != expected_run[1]
        ):
            errors.append(f"{run_path.name}: invalid solver terminal result")
        if (
            run.get("watchdog_seconds"),
            run.get("as_limit_kib"),
            run.get("nice"),
        ) != (21600, 4194304, 10):
            errors.append(f"{run_path.name}: resource policy mismatch")

        run_hash = file_sha256(run_path)
        expected_terminal = terminal_classification(status)
        audit_artifact = audit.get("artifact", {})
        if (
            audit.get("status") != "pass"
            or audit.get("terminal_classification") != expected_terminal
            or audit_artifact.get("exists") != (artifact is not None)
            or audit_artifact.get("sha256") != artifact_hash
            or audit.get("run_record", {}).get("sha256") != run_hash
            or audit.get("recomputed_constraints", {}).get("c5_constraint_sha256")
            != c5_digest
            or audit.get("recomputed_constraints", {}).get("phase_constraint_sha256")
            != phase_digest
            or audit.get("errors") != []
        ):
            errors.append(f"{audit_path.name}: terminal audit mismatch")

        records.append(
            {
                "k": k,
                "shard": shard,
                "status": "unknown" if status == "unknown_watchdog" else status,
                "unknown_kind": "watchdog" if status == "unknown_watchdog" else None,
                "artifact": str(artifact_path.resolve()),
                "artifact_exists": artifact is not None,
                "artifact_sha256": artifact_hash,
                "run_record": str(run_path.resolve()),
                "run_record_sha256": run_hash,
                "launcher_log": str(launcher_path.resolve()),
                "launcher_log_sha256": file_sha256(launcher_path),
                "terminal_audit": str(audit_path.resolve()),
                "terminal_audit_sha256": file_sha256(audit_path),
                "c5_constraint_sha256": c5_digest,
                "phase_constraint_sha256": phase_digest,
                "solve_seconds": artifact.get("solve_seconds") if artifact else None,
                "elapsed_seconds": artifact.get("elapsed_seconds") if artifact else None,
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
    evidence_complete = observed_shards == expected_shards and not errors
    strict_unsat_complete = (
        evidence_complete
        and status_counts == {"sat": 0, "unsat": 13, "unknown": 0}
    )
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
    solved_records = [
        record for record in records if record["solve_seconds"] is not None
    ]
    result = {
        "schema": "tc-byte-adder-bit35-joint-n13-single-phase-complete-audit-v1",
        "status": "pass" if not errors else "fail",
        "scope": {
            "gate_bound": GATE_BOUND,
            "components": COMPONENTS,
            "c5_driver_class": "single_component",
            "c5_driver_count": 1,
            "t5_drivers": args.t5_drivers,
            "s5_drivers": args.s5_drivers,
            "truth_domain_rows": 96,
            "truth_domain_sha256": TRUTH_DOMAIN_SHA256,
        },
        "coverage": {
            "expected_shards": list(expected_shards),
            "expected_count": len(expected_shards),
            "observed_count": len(records),
            "missing_shards": sorted(set(expected_shards) - set(observed_shards)),
            "extra_shards": sorted(
                set(observed_evidence_shards) - set(expected_shards)
            ),
            "status_counts": status_counts,
            "evidence_complete": evidence_complete,
            "strict_unsat_complete": strict_unsat_complete,
            "not_all_c5_single_phase_pairs": True,
            "not_a_global_g16_claim": True,
        },
        "timing": {
            "total_solve_seconds": sum(
                float(record["solve_seconds"]) for record in solved_records
            ),
            "maximum_solve_seconds": max(
                (float(record["solve_seconds"]) for record in solved_records),
                default=0.0,
            ),
            "maximum_solve_shard": max(
                solved_records,
                key=lambda record: float(record["solve_seconds"]),
                default={},
            ).get("shard"),
        },
        "collection_sha256": canonical_sha256(collection_identity),
        "records": records,
        "errors": errors,
    }
    output_sha = atomic_write(output, result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"sha256={output_sha}")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
