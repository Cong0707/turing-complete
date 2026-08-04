"""Run the fixed73/high-residual verification and non-deployment pipeline.

The pipeline writes only below this research directory.  It never passes the
materializer's ``--deploy`` flag, never reads or writes the formal game save,
and never starts the game.  Production mode additionally replays
``build(witness_path)`` inside the materializer to prove deterministic graft
generation from the exact witness.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
VERIFIER_PATH = HERE / "verify_fixed73_high29_physical_witness.py"
BUILDER_PATH = HERE / "graft_fixed73_high29_physical_witness.py"
MATERIALIZER_PATH = (
    ROOT / ".research/byte_adder_builder_layout_agent/materialize_factory_dag.py"
)
AUDITOR_PATH = HERE / "audit_factory_candidate.py"
REPO_PYTHON = ROOT / ".venv/Scripts/python.exe"
TOOL_PYTHON = REPO_PYTHON if REPO_PYTHON.is_file() else Path(sys.executable)


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


verifier = _load_module(VERIFIER_PATH, "fixed73_high29_pipeline_verifier")
builder = _load_module(BUILDER_PATH, "fixed73_high29_pipeline_builder")


def _inside_here(path: Path) -> Path:
    resolved = path.resolve()
    if resolved != HERE and HERE not in resolved.parents:
        raise RuntimeError(f"pipeline output must stay below {HERE}: {resolved}")
    return resolved


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path = _inside_here(path)
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(encoded)
    temporary.replace(path)
    if path.read_bytes() != encoded:
        raise RuntimeError(f"written JSON changed: {path}")


def _write_text(path: Path, value: str) -> None:
    path = _inside_here(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(value, encoding="utf-8")
    temporary.replace(path)


def _hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _run(command: list[str], *, stdout_path: Path, stderr_path: Path) -> None:
    result = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    _write_text(stdout_path, result.stdout)
    _write_text(stderr_path, result.stderr)
    if result.returncode:
        raise RuntimeError(
            f"command failed with {result.returncode}: {command!r}; "
            f"see {stdout_path} and {stderr_path}"
        )


def _assert_zero_dict(value: object, label: str) -> None:
    if not isinstance(value, dict) or any(int(item) for item in value.values()):
        raise RuntimeError(f"{label} is not all zero: {value!r}")


def run_pipeline(
    witness_path: Path,
    *,
    output_dir: Path | None = None,
    fixture: bool = False,
) -> dict[str, Any]:
    witness_path = witness_path.resolve()
    witness_hash = _hash(witness_path)
    if output_dir is None:
        mode = "fixture" if fixture else "production"
        output_dir = HERE / f"fixed73_high_residual_{mode}_{witness_hash[:12]}"
    output_dir = _inside_here(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    witness_review = verifier.verify_witness(witness_path, fixture=fixture)
    witness_report_path = output_dir / "witness_verification.json"
    _write_json(witness_report_path, witness_review)

    build_function = builder.build_fixture if fixture else builder.build
    first = build_function(witness_path)
    second = build_function(witness_path)
    if first != second:
        raise RuntimeError("two independent in-process builder replays differ")
    if fixture:
        if first.get("competitive_contract") is not False or first.get("fixture_only") is not True:
            raise RuntimeError("fixture DAG lost its noncompetitive marker")
    elif (
        first.get("competitive_contract") is not True
        or not verifier.complete_score_within_contract(first.get("metrics", {}))
    ):
        raise RuntimeError(
            "production DAG is not a complete <=103/5/515 candidate: "
            f"{first!r}"
        )
    dag_path = output_dir / "complete_factory_dag.json"
    _write_json(dag_path, first)

    materialized_dir = output_dir / "materialized"
    materializer_command = [
        str(TOOL_PYTHON),
        str(MATERIALIZER_PATH),
        str(dag_path),
        "--output-dir",
        str(materialized_dir),
    ]
    if not fixture:
        materializer_command.extend(
            [
                "--builder",
                str(BUILDER_PATH),
                "--builder-witness",
                str(witness_path),
            ]
        )
    _run(
        materializer_command,
        stdout_path=output_dir / "materializer_stdout.json",
        stderr_path=output_dir / "materializer_stderr.txt",
    )

    candidate_path = materialized_dir / "candidate/circuit.data"
    materializer_certificate_path = materialized_dir / "machine_certificate.json"
    if not candidate_path.is_file() or not materializer_certificate_path.is_file():
        raise RuntimeError("materializer did not emit the expected research artifacts")
    materializer_certificate = json.loads(
        materializer_certificate_path.read_text(encoding="utf-8")
    )
    deployment = materializer_certificate.get("deployment")
    if not isinstance(deployment, dict) or deployment != {
        "requested": False,
        "repository_candidate": deployment.get("repository_candidate"),
        "repository_candidate_written": False,
        "formal_save": deployment.get("formal_save"),
        "formal_save_written": False,
        "backup_created": False,
        "game_started": False,
    }:
        raise RuntimeError(f"materializer deployment guard changed: {deployment!r}")
    if materializer_certificate.get("v15_round_trip_verified") is not True:
        raise RuntimeError("materializer v15 roundtrip did not pass")
    source_review = materializer_certificate.get("source_review", {})
    expected_replay = None if fixture else True
    if source_review.get("generator_replay_equal") is not expected_replay:
        raise RuntimeError("materializer generator replay result changed")

    independent_report_path = output_dir / "independent_audit.json"
    independent_proxy_path = output_dir / "independent_semantic_proxy.circuit.data"
    audit_command = [
        str(TOOL_PYTHON),
        str(AUDITOR_PATH),
        str(dag_path),
        str(candidate_path),
        "--certificate",
        str(materializer_certificate_path),
        "--output",
        str(independent_report_path),
        "--proxy",
        str(independent_proxy_path),
    ]
    _run(
        audit_command,
        stdout_path=output_dir / "independent_audit_stdout.json",
        stderr_path=output_dir / "independent_audit_stderr.txt",
    )
    audit = json.loads(independent_report_path.read_text(encoding="utf-8"))
    if audit.get("v15_round_trip_byte_identical") is not True:
        raise RuntimeError("independent v15 roundtrip did not pass")
    if audit.get("deterministic_rebuild_byte_identical") is not True:
        raise RuntimeError("independent deterministic rebuild did not pass")
    if audit.get("native_com_add_count") != 0:
        raise RuntimeError("native com_add appeared in the physical candidate")
    _assert_zero_dict(audit.get("connectivity"), "independent connectivity")
    _assert_zero_dict(audit.get("geometry"), "independent geometry")
    if audit.get("physical_net_partition", {}).get("violation_count") != 0:
        raise RuntimeError("independent physical-net partition failed")
    semantic = audit.get("semantic", {})
    if (
        semantic.get("vectors_checked") != 1 << 17
        or semantic.get("node_replay_mismatch_count") != 0
        or semantic.get("packed_conflict_cases") != 0
        or semantic.get("sum_correct") is not True
        or semantic.get("carry_correct") is not True
        or semantic.get("primary_output_z_count") != 0
    ):
        raise RuntimeError(f"independent physical semantic replay failed: {semantic!r}")
    if (
        audit.get("formal_save_read") is not False
        or audit.get("formal_save_written") is not False
        or audit.get("game_started") is not False
    ):
        raise RuntimeError("independent auditor touched forbidden runtime state")

    summary = {
        "schema": "fixed73-high-residual-nondeployment-pipeline-v2",
        "status": "verified",
        "mode": "fixture" if fixture else "production",
        "competitive_contract": not fixture,
        "competitive_score_contract": {
            "max_gate": verifier.MAX_COMPLETE_GATE,
            "max_delay": verifier.MAX_COMPLETE_DELAY,
            "max_energy": verifier.MAX_COMPLETE_ENERGY,
            "energy_equals_gate_times_delay": True,
        },
        "witness": {
            "path": str(witness_path),
            "sha256": witness_hash,
            "verification": str(witness_report_path),
            "verification_sha256": _hash(witness_report_path),
        },
        "factory_dag": {
            "path": str(dag_path),
            "sha256": _hash(dag_path),
            "factory_dag_sha256": first["factory_dag"]["sha256"],
            "metrics": first["metrics"],
            "semantic": first["semantic"],
            "two_in_process_replays_equal": True,
        },
        "materialization": {
            "candidate": str(candidate_path),
            "candidate_sha256": _hash(candidate_path),
            "certificate": str(materializer_certificate_path),
            "certificate_sha256": _hash(materializer_certificate_path),
            "generator_replay_equal": source_review.get("generator_replay_equal"),
            "v15_round_trip_verified": True,
            "deployment": deployment,
        },
        "independent_audit": {
            "report": str(independent_report_path),
            "report_sha256": _hash(independent_report_path),
            "proxy": str(independent_proxy_path),
            "proxy_sha256": _hash(independent_proxy_path),
            "v15_round_trip_byte_identical": True,
            "deterministic_rebuild_byte_identical": True,
            "native_com_add_count": 0,
            "physical_net_partition_violation_count": 0,
            "geometry": audit["geometry"],
            "connectivity": audit["connectivity"],
            "semantic": semantic,
        },
        "commands": {
            "materializer": materializer_command,
            "independent_auditor": audit_command,
            "deploy_flag_present": False,
        },
        "safety": {
            "research_output_only": True,
            "repository_candidate_written": False,
            "formal_save_read": False,
            "formal_save_written": False,
            "game_started": False,
            "backup_created": False,
        },
    }
    summary_path = output_dir / "pipeline_summary.json"
    _write_json(summary_path, summary)
    summary["summary_path"] = str(summary_path)
    summary["summary_sha256"] = _hash(summary_path)
    return summary


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run fixed73/high-residual verification and research-only materialization."
    )
    parser.add_argument("witness", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument(
        "--fixture",
        action="store_true",
        help="run the explicit noncompetitive S7/C8 positive regression",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    summary = run_pipeline(
        args.witness,
        output_dir=args.output_dir,
        fixture=args.fixture,
    )
    print(
        json.dumps(
            {
                "status": summary["status"],
                "mode": summary["mode"],
                "metrics": summary["factory_dag"]["metrics"],
                "candidate_sha256": summary["materialization"]["candidate_sha256"],
                "summary": summary["summary_path"],
                "summary_sha256": summary["summary_sha256"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
