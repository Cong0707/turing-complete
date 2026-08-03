"""Audit a terminal bit-3:5 phase-driver shard artifact and watchdog record.

The audit is intentionally solver-free.  It recomputes both normal-form
identities and digests from the pure metadata modules, verifies every recorded
dependency hash against the local reviewed files, checks the expected shard
parameters, and classifies the wrapper result.  A SAT artifact is never treated
as accepted here: it remains pending the separate 96-row verifier and full DAG
graft/replay.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path, PurePath
from typing import Any

import bit35_joint_c5_normal_form as c5_normal
import bit35_joint_phase_driver_classes as phase_normal


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PAIR_CORE = ROOT / ".research" / "byte_adder_pair_macro_exact"
DEFAULT_ARTIFACT = HERE / "results" / "g16_n14_c5_multi_d2_k3_t1_s1.json"
DEFAULT_RUN_RECORD = HERE / "results" / "g16_n14_c5_multi_d2_k3_t1_s1.run.json"
DEFAULT_OUTPUT = HERE / "bit35_joint_g16_n14_c5_multi_d2_k3_t1_s1_terminal_audit.json"
WORKER = HERE / "exact_bit35_joint_phase_driver_shard.py"
TRUTH_DOMAIN_SHA256 = "1c9768429735b2f87bca12bb62dad82624f45a419b80ea6b5470655764c34b60"
TARGET_NAMES = ["S3", "S4", "C5", "T5", "S5"]
OUTPUT_DEADLINES = [5, 7, 4, 5, 6]
SOURCE_COUNT = 14


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def atomic_write(path: Path, payload: dict[str, Any]) -> str:
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(encoded)
    temporary.replace(path)
    return sha256(encoded).hexdigest()


def portable_basename(raw: object) -> str:
    # Artifact paths may use either Windows or POSIX separators.
    return str(raw).replace("\\", "/").rsplit("/", 1)[-1]


def expected_dependency_paths() -> tuple[Path, ...]:
    return (
        HERE / "bit35_joint_c5_normal_form.py",
        HERE / "bit35_joint_phase_driver_classes.py",
        HERE / "exact_bit35_joint_c5_normal_form_shard.py",
        HERE / "exact_bit35_joint_sat.py",
        PAIR_CORE / "exact_paid_physical_search_core.py",
        PAIR_CORE / "exact_paid_physical_core.py",
        PAIR_CORE / "exact_paid_physical_cnf.py",
    )


def expected_c5_encoding(
    shard: str, components: int, gate_bound: int
) -> dict[str, object]:
    parsed = c5_normal.parse_shard(shard, components, gate_bound)
    driver_class = parsed["driver_class"]
    if driver_class == "source":
        return {
            "forbidden_component_output_sources": list(
                range(SOURCE_COUNT, SOURCE_COUNT + components)
            )
        }
    if driver_class == "single_component":
        ancestor_count = int(parsed["ancestor_count"])
        driver_slot = ancestor_count
        terminal_end = driver_slot + 1
        return {
            "driver_slot": driver_slot,
            "driver_source": SOURCE_COUNT + driver_slot,
            "ancestor_user_clause_lengths": [
                2 * (terminal_end - slot - 1) for slot in range(ancestor_count)
            ],
        }
    ancestor_count = int(parsed["ancestor_count"])
    driver_count = int(parsed["driver_count"])
    driver_slots = list(range(ancestor_count, ancestor_count + driver_count))
    terminal_end = ancestor_count + driver_count
    return {
        "driver_slots": driver_slots,
        "driver_sources": [SOURCE_COUNT + slot for slot in driver_slots],
        "ancestor_user_clause_lengths": [
            2 * (terminal_end - slot - 1) for slot in range(ancestor_count)
        ],
    }


def expected_phase_encoding(
    components: int, t5_drivers: int, s5_drivers: int
) -> dict[str, object]:
    def record(output_index: int, count: int) -> dict[str, object]:
        return {
            "output_index": output_index,
            "forbidden_paid_source_selectors": SOURCE_COUNT,
            "component_selector_count": components,
            "exact_driver_count": count,
            "required_kind_if_selected": "SWITCH" if count > 1 else "any",
        }

    return {"T5": record(3, t5_drivers), "S5": record(4, s5_drivers)}


def expected_accounting(gate_bound: int) -> dict[str, int]:
    complete_gate = 80
    complete_delay = 7
    fixed_shell = 63
    projected = fixed_shell + gate_bound
    return {
        "current_complete_gate": complete_gate,
        "current_complete_delay": complete_delay,
        "current_complete_energy": complete_gate * complete_delay,
        "current_joint_gate": 17,
        "current_joint_components": 15,
        "fixed_shell_with_paid_sources": fixed_shell,
        "projected_complete_gate_at_bound": projected,
        "projected_complete_delay": complete_delay,
        "projected_complete_energy_at_bound": projected * complete_delay,
    }


def audit_artifact(args: argparse.Namespace, artifact: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    expected_metadata = {
        "schema": "tc-byte-adder-bit35-joint-phase-driver-shard-v1",
        "profile": "d7_80_bit35_joint",
        "gate_bound": args.gate_bound,
        "max_delay": 7,
        "components": args.components,
        "c5_shard": args.c5_shard,
        "t5_drivers": args.t5_drivers,
        "s5_drivers": args.s5_drivers,
        "target_names": TARGET_NAMES,
        "output_deadlines": OUTPUT_DEADLINES,
        "assignments": 96,
        "truth_domain_sha256": TRUTH_DOMAIN_SHA256,
        "solver": args.solver,
        "timeout_seconds": args.internal_timeout,
    }
    for key, expected in expected_metadata.items():
        if artifact.get(key) != expected:
            errors.append(f"metadata {key}: {artifact.get(key)!r} != {expected!r}")
    if artifact.get("status") not in {"sat", "unsat", "unknown"}:
        errors.append(f"invalid artifact status {artifact.get('status')!r}")

    c5_identity = c5_normal.constraint_identity(
        args.c5_shard, args.components, args.gate_bound
    )
    c5_digest = c5_normal.canonical_sha256(c5_identity)
    expected_c5 = {
        "identity": c5_identity,
        "constraint_sha256": c5_digest,
        "encoding_evidence": expected_c5_encoding(
            args.c5_shard, args.components, args.gate_bound
        ),
    }
    if artifact.get("c5_constraint") != expected_c5:
        errors.append("C5 constraint identity, digest, or encoding evidence changed")
    if artifact.get("c5_constraint_sha256") != c5_digest:
        errors.append("top-level C5 constraint digest changed")

    phase_identity = phase_normal.constraint_identity(
        args.components,
        args.gate_bound,
        args.t5_drivers,
        args.s5_drivers,
    )
    phase_digest = phase_normal.canonical_sha256(phase_identity)
    expected_phase = {
        "identity": phase_identity,
        "constraint_sha256": phase_digest,
        "encoding_evidence": expected_phase_encoding(
            args.components, args.t5_drivers, args.s5_drivers
        ),
    }
    if artifact.get("phase_constraint") != expected_phase:
        errors.append("phase constraint identity, digest, or encoding evidence changed")
    if artifact.get("phase_constraint_sha256") != phase_digest:
        errors.append("top-level phase constraint digest changed")
    expected_pairs = [
        {"t5_drivers": t5, "s5_drivers": s5}
        for t5, s5 in phase_normal.pair_domain(args.components, args.gate_bound)
    ]
    if artifact.get("phase_pair_domain") != expected_pairs:
        errors.append("phase pair domain changed")

    if artifact.get("script_sha256") != file_sha256(WORKER):
        errors.append("worker script hash changed")
    recorded_dependencies = artifact.get("dependencies")
    expected_paths = expected_dependency_paths()
    if not isinstance(recorded_dependencies, list) or len(recorded_dependencies) != len(
        expected_paths
    ):
        errors.append("dependency record count changed")
    else:
        for index, (record, path) in enumerate(
            zip(recorded_dependencies, expected_paths, strict=True)
        ):
            if portable_basename(record.get("path")) != path.name:
                errors.append(
                    f"dependency {index} basename {record.get('path')!r} != {path.name!r}"
                )
            if not path.is_file():
                errors.append(f"dependency {index} is absent locally: {path}")
            elif record.get("sha256") != file_sha256(path):
                errors.append(f"dependency {index} hash changed: {path.name}")

    accounting = artifact.get("accounting", {})
    expected_base_accounting = expected_accounting(args.gate_bound)
    for key, expected in expected_base_accounting.items():
        if accounting.get(key) != expected:
            errors.append(f"accounting {key}: {accounting.get(key)!r} != {expected!r}")
    if not isinstance(artifact.get("variables"), int) or int(artifact["variables"]) <= 0:
        errors.append("invalid SAT variable count")
    if not isinstance(artifact.get("clauses"), int) or int(artifact["clauses"]) <= 0:
        errors.append("invalid SAT clause count")
    for key in ("build_seconds", "solve_seconds", "elapsed_seconds"):
        value = artifact.get(key)
        if not isinstance(value, (int, float)) or value < 0:
            errors.append(f"invalid timing field {key}={value!r}")

    status = artifact.get("status")
    if status == "sat":
        network = artifact.get("network")
        if not isinstance(network, list) or len(network) != args.components:
            errors.append("SAT network/component count mismatch")
        if int(artifact.get("actual_gate", -1)) > args.gate_bound:
            errors.append("SAT witness exceeds gate bound")
        verification = artifact.get("verification", {})
        for key in (
            "mismatch_count",
            "bus_conflict_count",
            "undriven_output_count",
            "physical_net_partition_violation_count",
        ):
            if verification.get(key) != 0:
                errors.append(f"embedded SAT verification {key}={verification.get(key)!r}")
        if artifact.get("actual_phase_driver_counts") != {
            "T5": args.t5_drivers,
            "S5": args.s5_drivers,
        }:
            errors.append("decoded SAT phase driver counts changed")
    elif status == "unknown":
        if not artifact.get("reason_unknown"):
            errors.append("UNKNOWN artifact lacks reason_unknown")
    else:
        for key in ("network", "output_buses", "verification", "actual_gate"):
            if key in artifact:
                errors.append(f"UNSAT artifact unexpectedly contains {key}")
    return errors


def audit_run_record(args: argparse.Namespace, record: dict[str, Any], artifact_status: str | None) -> list[str]:
    errors: list[str] = []
    expected = {
        "watchdog_seconds": args.watchdog_seconds,
        "as_limit_kib": args.as_limit_kib,
        "nice": args.nice,
    }
    for key, value in expected.items():
        if record.get(key) != value:
            errors.append(f"run record {key}: {record.get(key)!r} != {value!r}")
    classification = record.get("classification")
    exit_code = record.get("exit_code")
    if artifact_status in {"sat", "unsat"}:
        if classification != "solver_exit" or exit_code != 0:
            errors.append(
                f"terminal artifact has wrapper classification={classification!r} exit={exit_code!r}"
            )
    elif artifact_status == "unknown":
        if classification != "solver_exit" or exit_code != 2:
            errors.append("internal-timeout UNKNOWN has unexpected wrapper exit")
    elif artifact_status is None:
        if classification != "watchdog_timeout" or exit_code not in {124, 137}:
            errors.append("missing artifact is not explained by the external watchdog")
    for start_key, end_key in (("start_utc", "end_utc"), ("started_at", "finished_at")):
        if start_key in record or end_key in record:
            if not record.get(start_key) or not record.get(end_key):
                errors.append(f"run record has incomplete {start_key}/{end_key} pair")
            break
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--run-record", type=Path, default=DEFAULT_RUN_RECORD)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--gate-bound", type=int, default=16)
    parser.add_argument("--components", type=int, default=14)
    parser.add_argument("--c5-shard", default="multi_d2_k3")
    parser.add_argument("--t5-drivers", type=int, default=1)
    parser.add_argument("--s5-drivers", type=int, default=1)
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--internal-timeout", type=float, default=0.0)
    parser.add_argument("--watchdog-seconds", type=int, default=21600)
    parser.add_argument("--as-limit-kib", type=int, default=4194304)
    parser.add_argument("--nice", type=int, default=10)
    parser.add_argument("--allow-missing-run-record", action="store_true")
    args = parser.parse_args()

    artifact_path = args.artifact.resolve()
    run_path = args.run_record.resolve()
    artifact = (
        json.loads(artifact_path.read_text(encoding="utf-8"))
        if artifact_path.is_file()
        else None
    )
    record = json.loads(run_path.read_text(encoding="utf-8")) if run_path.is_file() else None
    errors: list[str] = []
    artifact_status: str | None = None
    if artifact is not None:
        artifact_status = str(artifact.get("status"))
        errors.extend(audit_artifact(args, artifact))
    if record is not None:
        errors.extend(audit_run_record(args, record, artifact_status))
    elif not args.allow_missing_run_record:
        errors.append("run record is absent")

    if artifact is None and record is None:
        terminal_classification = "running_or_not_started"
        audit_status = "incomplete"
    elif artifact is None:
        terminal_classification = "unknown_watchdog_timeout"
        audit_status = "pass" if not errors else "fail"
    elif artifact_status == "sat":
        terminal_classification = "sat_pending_independent_96_and_full_replay"
        audit_status = "pass" if not errors else "fail"
    elif artifact_status == "unsat":
        terminal_classification = "strict_unsat"
        audit_status = "pass" if not errors else "fail"
    else:
        terminal_classification = "unknown_internal_timeout"
        audit_status = "pass" if not errors else "fail"

    result = {
        "schema": "tc-byte-adder-bit35-joint-phase-driver-terminal-audit-v1",
        "status": audit_status,
        "terminal_classification": terminal_classification,
        "expected": {
            "gate_bound": args.gate_bound,
            "components": args.components,
            "c5_shard": args.c5_shard,
            "t5_drivers": args.t5_drivers,
            "s5_drivers": args.s5_drivers,
            "solver": args.solver,
            "internal_timeout": args.internal_timeout,
            "watchdog_seconds": args.watchdog_seconds,
            "as_limit_kib": args.as_limit_kib,
            "nice": args.nice,
            "truth_domain_rows": 96,
            "truth_domain_sha256": TRUTH_DOMAIN_SHA256,
        },
        "artifact": {
            "path": str(artifact_path),
            "exists": artifact is not None,
            "sha256": file_sha256(artifact_path) if artifact is not None else None,
            "solver_status": artifact_status,
        },
        "run_record": {
            "path": str(run_path),
            "exists": record is not None,
            "sha256": file_sha256(run_path) if record is not None else None,
            "classification": record.get("classification") if record else None,
            "exit_code": record.get("exit_code") if record else None,
        },
        "recomputed_constraints": {
            "c5_constraint_sha256": c5_normal.constraint_sha256(
                args.c5_shard, args.components, args.gate_bound
            ),
            "phase_constraint_sha256": phase_normal.constraint_sha256(
                args.components,
                args.gate_bound,
                args.t5_drivers,
                args.s5_drivers,
            ),
        },
        "worker": {"path": str(WORKER), "sha256": file_sha256(WORKER)},
        "dependencies": [
            {"path": str(path), "sha256": file_sha256(path)}
            for path in expected_dependency_paths()
        ],
        "errors": errors,
    }
    output_sha = atomic_write(args.output.resolve(), result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"sha256={output_sha}")
    if audit_status == "incomplete":
        return 2
    return 0 if audit_status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
