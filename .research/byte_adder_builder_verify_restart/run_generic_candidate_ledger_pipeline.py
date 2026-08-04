#!/usr/bin/env python3
"""Verify, materialize, and optionally deploy any complete candidate ledger.

The materializer always runs in research-only mode.  After independent
131072-row logical and physical replay, geometry/connectivity checks, current
v15 round trip, and deterministic rebuild, deployment writes only the formal
Byte Adder save.  It never writes the repository candidate, creates a backup,
or launches Turing Complete.
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

from tc_save_lab.codec import decode_v15, encode_v15
from tc_save_lab.foundry import _assert_game_not_running


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LEDGER_PATH = HERE / "generic_candidate_ledger.py"
MATERIALIZER_PATH = (
    ROOT / ".research/byte_adder_builder_layout_agent/materialize_factory_dag.py"
)
AUDITOR_PATH = HERE / "audit_factory_candidate.py"
REPO_PYTHON = ROOT / ".venv/Scripts/python.exe"
TOOL_PYTHON = REPO_PYTHON if REPO_PYTHON.is_file() else Path(sys.executable)
DEFAULT_FORMAL_SAVE = (
    Path.home()
    / "AppData/Roaming/Turing Complete/schematics/byte_adder/Default/circuit.data"
)


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ledger_api = _load_module("generic_candidate_pipeline_ledger", LEDGER_PATH)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def inside_here(path: Path) -> Path:
    resolved = path.resolve()
    require(resolved.is_relative_to(HERE), f"pipeline output is outside research line: {resolved}")
    return resolved


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path = inside_here(path)
    require(not path.exists(), f"refusing to overwrite {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode()
    temporary.write_bytes(encoded)
    temporary.replace(path)
    require(path.read_bytes() == encoded, f"JSON write changed: {path}")


def write_text(path: Path, value: str) -> None:
    path = inside_here(path)
    require(not path.exists(), f"refusing to overwrite {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(value, encoding="utf-8")
    temporary.replace(path)


def run(command: list[str], *, stdout_path: Path, stderr_path: Path) -> None:
    result = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    write_text(stdout_path, result.stdout)
    write_text(stderr_path, result.stderr)
    require(
        result.returncode == 0,
        f"command failed with {result.returncode}: {command!r}; see {stdout_path} and {stderr_path}",
    )


def assert_zero_dict(value: object, label: str) -> None:
    require(isinstance(value, dict), f"{label} is missing")
    failures = {key: item for key, item in value.items() if int(item)}
    require(not failures, f"{label} is not all zero: {failures}")


def _load_or_create_ledger(source: Path, output_dir: Path) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    source = source.resolve()
    raw = ledger_api.load_json(source)
    ledger_path = output_dir / "candidate_ledger.json"
    if raw.get("schema") == ledger_api.SCHEMA:
        ledger, review = ledger_api.validate_ledger(source)
        write_json(ledger_path, ledger)
    else:
        ledger = ledger_api.build_ledger(source)
        write_json(ledger_path, ledger)
        _verified, review = ledger_api.validate_ledger(ledger_path)
    return ledger_path, ledger, review


def run_pipeline(
    source: Path,
    *,
    output_dir: Path | None = None,
    deploy_formal: bool = False,
    formal_save: Path = DEFAULT_FORMAL_SAVE,
) -> dict[str, Any]:
    source = source.resolve()
    source_hash = digest(source)
    if output_dir is None:
        output_dir = HERE / f"generic_candidate_{source_hash[:12]}"
    output_dir = inside_here(output_dir)
    require(not output_dir.exists(), f"refusing to reuse pipeline directory: {output_dir}")
    output_dir.mkdir(parents=True)

    ledger_path, ledger, ledger_review = _load_or_create_ledger(source, output_dir)
    candidate_payload_path = output_dir / "candidate_factory_dag.json"
    write_json(candidate_payload_path, ledger["candidate_payload"])

    materialized_dir = output_dir / "materialized"
    materializer_command = [
        str(TOOL_PYTHON),
        str(MATERIALIZER_PATH),
        str(candidate_payload_path),
        "--output-dir",
        str(materialized_dir),
    ]
    run(
        materializer_command,
        stdout_path=output_dir / "materializer_stdout.json",
        stderr_path=output_dir / "materializer_stderr.txt",
    )
    candidate_path = materialized_dir / "candidate/circuit.data"
    certificate_path = materialized_dir / "machine_certificate.json"
    require(candidate_path.is_file() and certificate_path.is_file(), "materializer artifacts missing")
    certificate = ledger_api.load_json(certificate_path)
    deployment = certificate.get("deployment")
    require(isinstance(deployment, dict), "materializer deployment guard missing")
    require(
        deployment.get("requested") is False
        and deployment.get("repository_candidate_written") is False
        and deployment.get("formal_save_written") is False
        and deployment.get("backup_created") is False
        and deployment.get("game_started") is False,
        "materializer unexpectedly deployed",
    )
    require(certificate.get("v15_round_trip_verified") is True, "materializer v15 roundtrip failed")

    audit_path = output_dir / "independent_audit.json"
    proxy_path = output_dir / "independent_semantic_proxy.circuit.data"
    auditor_command = [
        str(TOOL_PYTHON),
        str(AUDITOR_PATH),
        str(candidate_payload_path),
        str(candidate_path),
        "--certificate",
        str(certificate_path),
        "--output",
        str(audit_path),
        "--proxy",
        str(proxy_path),
    ]
    run(
        auditor_command,
        stdout_path=output_dir / "independent_audit_stdout.json",
        stderr_path=output_dir / "independent_audit_stderr.txt",
    )
    audit = ledger_api.load_json(audit_path)
    require(audit.get("v15_round_trip_byte_identical") is True, "independent v15 roundtrip failed")
    require(audit.get("deterministic_rebuild_byte_identical") is True, "deterministic rebuild failed")
    require(audit.get("native_com_add_count") == 0, "native com_add is present")
    assert_zero_dict(audit.get("connectivity"), "connectivity")
    assert_zero_dict(audit.get("geometry"), "geometry")
    require(audit.get("physical_net_partition", {}).get("violation_count") == 0, "owner partition failed")
    semantic = audit.get("semantic")
    require(isinstance(semantic, dict), "physical semantic report missing")
    require(
        semantic.get("vectors_checked") == 1 << 17
        and semantic.get("node_replay_mismatch_count") == 0
        and semantic.get("packed_conflict_cases") == 0
        and semantic.get("sum_correct") is True
        and semantic.get("carry_correct") is True
        and semantic.get("primary_output_z_count") == 0,
        f"physical 131072-row replay failed: {semantic}",
    )

    candidate_bytes = candidate_path.read_bytes()
    decoded = decode_v15(candidate_bytes)
    require(encode_v15(decoded) == candidate_bytes, "candidate is not byte-identical v15")
    formal_save = formal_save.resolve()
    formal_written = False
    if deploy_formal:
        _assert_game_not_running()
        require(formal_save.parent.is_dir(), f"formal save directory is missing: {formal_save.parent}")
        formal_save.write_bytes(candidate_bytes)
        _assert_game_not_running()
        formal_bytes = formal_save.read_bytes()
        require(formal_bytes == candidate_bytes, "formal save bytes differ after deployment")
        require(encode_v15(decode_v15(formal_bytes)) == formal_bytes, "formal save v15 roundtrip failed")
        formal_written = True

    summary = {
        "schema": "byte-adder-generic-candidate-ledger-pipeline-v1",
        "status": "deployed" if formal_written else "verified",
        "source": {"path": str(source), "sha256": source_hash},
        "ledger": {
            "path": str(ledger_path),
            "sha256": digest(ledger_path),
            "ledger_sha256": ledger["ledger_sha256"],
            "contracts": ledger["contracts"],
            "vectors_checked": ledger_review["vectors_checked"],
        },
        "factory_dag": {
            "path": str(candidate_payload_path),
            "sha256": digest(candidate_payload_path),
            "factory_dag_sha256": ledger["source"]["factory_dag_sha256"],
            "score": ledger["contracts"]["score"],
        },
        "materialization": {
            "candidate": str(candidate_path),
            "candidate_sha256": digest(candidate_path),
            "certificate": str(certificate_path),
            "certificate_sha256": digest(certificate_path),
            "v15_round_trip_verified": True,
        },
        "independent_audit": {
            "report": str(audit_path),
            "report_sha256": digest(audit_path),
            "proxy": str(proxy_path),
            "proxy_sha256": digest(proxy_path),
            "vectors_checked": semantic["vectors_checked"],
            "v15_round_trip_byte_identical": True,
            "deterministic_rebuild_byte_identical": True,
            "native_com_add_count": 0,
            "physical_net_partition_violation_count": 0,
            "geometry": audit["geometry"],
            "connectivity": audit["connectivity"],
            "semantic": semantic,
        },
        "deployment": {
            "requested": deploy_formal,
            "scope": "formal-save-only",
            "formal_save": str(formal_save),
            "formal_save_written": formal_written,
            "formal_save_sha256": digest(formal_save) if formal_written else None,
            "repository_candidate_written": False,
            "backup_created": False,
            "game_started": False,
        },
        "commands": {
            "materializer": materializer_command,
            "materializer_deploy_flag_present": False,
            "independent_auditor": auditor_command,
        },
    }
    summary_path = output_dir / "pipeline_summary.json"
    write_json(summary_path, summary)
    summary["summary"] = {"path": str(summary_path), "sha256": digest(summary_path)}
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path, help="raw complete Factory DAG or generic ledger")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--deploy-formal", action="store_true")
    parser.add_argument("--formal-save", type=Path, default=DEFAULT_FORMAL_SAVE)
    args = parser.parse_args(argv)
    summary = run_pipeline(
        args.source,
        output_dir=args.output_dir,
        deploy_formal=args.deploy_formal,
        formal_save=args.formal_save,
    )
    print(
        json.dumps(
            {
                "status": summary["status"],
                "score": summary["factory_dag"]["score"],
                "candidate_sha256": summary["materialization"]["candidate_sha256"],
                "formal_save_written": summary["deployment"]["formal_save_written"],
                "summary": summary["summary"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
