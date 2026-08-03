"""Run the deterministic ABC residual graft and offline materialization pipeline.

The pipeline performs two identical importer builds, writes the derived Factory
DAG, materializes only a research candidate, and invokes the independent
physical auditor.  Deployment is intentionally unavailable from this entry
point: it never reads or writes the formal save or repository candidate and it
never launches the game.
"""

from __future__ import annotations

import argparse
from contextlib import redirect_stdout
from hashlib import sha256
import importlib.util
import io
import json
from pathlib import Path
import sys
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
IMPORTER_PATH = HERE / "graft_abc_mapped_residual.py"
MATERIALIZER_PATH = (
    ROOT / ".research" / "byte_adder_builder_layout_agent" / "materialize_factory_dag.py"
)
INDEPENDENT_AUDITOR_PATH = (
    ROOT / ".research" / "byte_adder_builder_verify_restart" / "audit_factory_candidate.py"
)
DEFAULT_DAG = HERE / "byte-adder-hybrid-phasefold-g80-d7.json"
DEFAULT_METADATA = HERE / "abc_residual_current80" / "metadata.json"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def portable(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(resolved).replace("\\", "/")


def derived_directory(path: Path) -> Path:
    resolved = path.resolve()
    if resolved == HERE or HERE not in resolved.parents:
        raise RuntimeError(f"pipeline output must be a subdirectory of {HERE}: {resolved}")
    return resolved


def encoded(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode()


def atomic_write(path: Path, payload: dict[str, Any]) -> str:
    raw = encoded(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(raw)
    temporary.replace(path)
    return sha256(raw).hexdigest()


def check_metrics(metrics: dict[str, Any], args: argparse.Namespace) -> None:
    for field in ("gate", "delay", "energy"):
        expected = getattr(args, f"expected_{field}")
        maximum = getattr(args, f"max_{field}")
        actual = int(metrics[field])
        if expected is not None and actual != expected:
            raise RuntimeError(f"{field}={actual}, expected exactly {expected}")
        if maximum is not None and actual > maximum:
            raise RuntimeError(f"{field}={actual}, exceeds maximum {maximum}")


def require_clean_materialization(certificate: dict[str, Any], graft: dict[str, Any]) -> None:
    if certificate.get("serialized_score") != {
        "gate": int(graft["metrics"]["gate"]),
        "delay": int(graft["metrics"]["delay"]),
        "energy": int(graft["metrics"]["energy"]),
    }:
        raise RuntimeError("materializer score differs from graft")
    if int(certificate.get("reviewed_gate", -1)) != int(graft["metrics"]["gate"]):
        raise RuntimeError("materializer primitive gate differs from graft")
    if certificate.get("native_com_add_count") != 0:
        raise RuntimeError("materialized candidate contains native com_add")
    for section, fields in {
        "connectivity": (
            "unconnected_pin_count",
            "unsafe_multi_driver_network_count",
            "undriven_network_count",
            "sinkless_network_count",
            "width_mismatch_network_count",
            "cycle_component_count",
        ),
        "geometry": (
            "component_overlap_cells",
            "wire_collisions",
            "wire_interior_pin_contacts",
        ),
    }.items():
        record = certificate.get(section, {})
        for field in fields:
            value = record.get(field)
            if value not in (0, []):
                raise RuntimeError(f"materializer {section}.{field} is not clean: {value!r}")
    resolved = certificate.get("resolved_networks", {})
    for field in (
        "mixed_intended_physical_network_count",
        "fragmented_intended_network_count",
    ):
        if resolved.get(field) != 0:
            raise RuntimeError(f"materializer resolved_networks.{field} is not zero")
    if resolved.get("tri_state_output_pin_count") != resolved.get(
        "tri_state_outputs_with_exactly_one_resolved_network"
    ):
        raise RuntimeError("not every tri-state output belongs to exactly one resolved net")
    semantic = certificate.get("semantic", {})
    if (
        semantic.get("vectors_checked") != 131072
        or semantic.get("node_replay_mismatch_count") != 0
        or semantic.get("packed_conflict_cases") != 0
        or semantic.get("sum_correct") is not True
        or semantic.get("carry_correct") is not True
        or semantic.get("output_arrivals") != graft["metrics"]["output_arrivals"]
        or semantic.get("global_depth") != graft["metrics"]["delay"]
    ):
        raise RuntimeError(f"materializer semantic replay is not clean: {semantic!r}")
    if certificate.get("v15_round_trip_verified") is not True:
        raise RuntimeError("materializer v15 round trip was not verified")
    if certificate.get("research_candidate_matches") is not True:
        raise RuntimeError("materializer research candidate changed after write")
    deployment = certificate.get("deployment", {})
    expected_deployment = {
        "requested": False,
        "repository_candidate_written": False,
        "formal_save_written": False,
        "backup_created": False,
        "game_started": False,
    }
    for field, expected in expected_deployment.items():
        if deployment.get(field) != expected:
            raise RuntimeError(f"forbidden deployment field {field}={deployment.get(field)!r}")


def require_clean_independent_audit(report: dict[str, Any], graft: dict[str, Any]) -> None:
    factory = report.get("factory", {})
    expected_factory = {
        "gate": graft["metrics"]["gate"],
        "delay": graft["metrics"]["delay"],
        "energy": graft["metrics"]["energy"],
        "vectors_checked": 131072,
        "mismatch_count": 0,
        "conflict_assignment_count": 0,
        "output_z_assignment_count": 0,
        "recursive_cost_delay_verified": True,
    }
    for field, expected in expected_factory.items():
        if factory.get(field) != expected:
            raise RuntimeError(f"independent factory.{field}={factory.get(field)!r}")
    if report.get("v15_round_trip_byte_identical") is not True:
        raise RuntimeError("independent v15 round trip changed bytes")
    if report.get("deterministic_rebuild_byte_identical") is not True:
        raise RuntimeError("independent deterministic physical rebuild changed bytes")
    if report.get("physical_primitive_gate") != graft["metrics"]["gate"]:
        raise RuntimeError("independent physical primitive gate differs")
    if report.get("native_com_add_count") != 0:
        raise RuntimeError("independent audit found native com_add")
    for section in ("connectivity", "geometry"):
        for field, value in report.get(section, {}).items():
            if isinstance(value, int) and value != 0:
                raise RuntimeError(f"independent {section}.{field}={value}")
    physical = report.get("physical_net_partition", {})
    if physical.get("violation_count") != 0:
        raise RuntimeError("independent physical-net partition violation")
    semantic = report.get("semantic", {})
    if (
        semantic.get("vectors_checked") != 131072
        or semantic.get("node_replay_mismatch_count") != 0
        or semantic.get("packed_conflict_cases") != 0
        or semantic.get("sum_correct") is not True
        or semantic.get("carry_correct") is not True
        or semantic.get("primary_output_z_count") != 0
        or semantic.get("output_arrivals") != graft["metrics"]["output_arrivals"]
        or semantic.get("global_recursive_delay") != graft["metrics"]["delay"]
    ):
        raise RuntimeError(f"independent semantic replay is not clean: {semantic!r}")
    if (
        report.get("formal_save_read") is not False
        or report.get("formal_save_written") is not False
        or report.get("game_started") is not False
    ):
        raise RuntimeError("independent auditor touched forbidden runtime state")


def run(args: argparse.Namespace) -> dict[str, Any]:
    dag = args.dag.resolve()
    metadata = args.metadata.resolve()
    blif = args.blif.resolve()
    output_dir = derived_directory(args.output_dir)
    for path in (
        dag,
        metadata,
        blif,
        IMPORTER_PATH,
        MATERIALIZER_PATH,
        INDEPENDENT_AUDITOR_PATH,
    ):
        if not path.is_file():
            raise FileNotFoundError(path)
    input_paths = (
        dag,
        metadata,
        blif,
        IMPORTER_PATH,
        MATERIALIZER_PATH,
        INDEPENDENT_AUDITOR_PATH,
    )
    before_hashes = {portable(path): file_sha256(path) for path in input_paths}

    importer = load(IMPORTER_PATH, "abc_mapped_residual_pipeline_importer")
    first = importer.build(dag, metadata, blif)
    second = importer.build(dag, metadata, blif)
    if encoded(first) != encoded(second):
        raise RuntimeError("deterministic importer replay changed JSON bytes")
    check_metrics(first["metrics"], args)

    graft_path = output_dir / "grafted_factory_dag.json"
    graft_sha = atomic_write(graft_path, first)
    if graft_sha != file_sha256(graft_path):
        raise RuntimeError("graft changed after atomic write")

    materializer = load(MATERIALIZER_PATH, "abc_mapped_residual_pipeline_materializer")
    materialized_dir = output_dir / "materialized"
    with redirect_stdout(io.StringIO()):
        certificate = materializer.materialize(
            graft_path,
            output_dir=materialized_dir,
            deploy=False,
        )
    require_clean_materialization(certificate, first)
    candidate_path = materialized_dir / "candidate" / "circuit.data"
    certificate_path = materialized_dir / "machine_certificate.json"
    materializer_proxy = materialized_dir / "semantic_proxy.circuit.data"
    for path in (candidate_path, certificate_path, materializer_proxy):
        if not path.is_file():
            raise RuntimeError(f"materializer output is missing: {path}")

    independent = load(
        INDEPENDENT_AUDITOR_PATH,
        "abc_mapped_residual_pipeline_independent_auditor",
    )
    independent_report_path = output_dir / "independent_audit.json"
    independent_proxy_path = output_dir / "independent_proxy.circuit.data"
    with redirect_stdout(io.StringIO()):
        independent_report = independent.audit(
            graft_path,
            candidate_path,
            certificate_path=certificate_path,
            output_path=independent_report_path,
            proxy_path=independent_proxy_path,
        )
    require_clean_independent_audit(independent_report, first)
    if independent_report.get("candidate_sha256") != certificate.get("candidate_sha256"):
        raise RuntimeError("materializer and independent auditor candidate hashes differ")

    after_hashes = {portable(path): file_sha256(path) for path in input_paths}
    if before_hashes != after_hashes:
        raise RuntimeError("pipeline changed one or more immutable inputs")

    outputs = {
        "grafted_factory_dag": {
            "path": portable(graft_path),
            "sha256": file_sha256(graft_path),
        },
        "research_candidate": {
            "path": portable(candidate_path),
            "sha256": file_sha256(candidate_path),
        },
        "materializer_certificate": {
            "path": portable(certificate_path),
            "sha256": file_sha256(certificate_path),
        },
        "materializer_semantic_proxy": {
            "path": portable(materializer_proxy),
            "sha256": file_sha256(materializer_proxy),
        },
        "independent_audit": {
            "path": portable(independent_report_path),
            "sha256": file_sha256(independent_report_path),
        },
        "independent_semantic_proxy": {
            "path": portable(independent_proxy_path),
            "sha256": file_sha256(independent_proxy_path),
        },
    }
    summary = {
        "schema": "byte-adder-abc-mapped-residual-materialization-pipeline-v1",
        "status": "accepted",
        "inputs": before_hashes,
        "limits": {
            "expected_gate": args.expected_gate,
            "expected_delay": args.expected_delay,
            "expected_energy": args.expected_energy,
            "max_gate": args.max_gate,
            "max_delay": args.max_delay,
            "max_energy": args.max_energy,
        },
        "metrics": first["metrics"],
        "mapped_residual": {
            key: first["mapped_residual"][key]
            for key in (
                "cell_count",
                "materialized_new_node_count",
                "kind_counts",
                "residual_gate",
            )
        },
        "checks": {
            "same_process_importer_json_byte_identical": True,
            "authoritative_partition_recomputed": True,
            "fixed_bus_slice_byte_identical": first["partition"][
                "fixed_slice_byte_identical"
            ],
            "full_131072_rows": first["semantic"]["truth_table_rows"] == 131072,
            "mismatch_union_zero": first["semantic"]["mismatch_union_count"] == 0,
            "bus_conflict_zero": first["semantic"]["conflict_assignment_count"] == 0,
            "primary_output_z_zero": not any(
                first["semantic"]["z_assignment_count_by_output"]
            ),
            "physical_net_partition_zero": first["physical"][
                "physical_net_partition_violation_count"
            ]
            == 0,
            "dead_node_zero": all(
                first["dead_node_audit"][field] == 0
                for field in (
                    "mapped_blif_dead_cell_count",
                    "dead_shell_node_count",
                    "dead_generated_node_count",
                )
            ),
            "materializer_clean": True,
            "v15_round_trip_verified": True,
            "independent_physical_audit_clean": True,
            "deterministic_physical_rebuild_byte_identical": True,
            "immutable_inputs_unchanged": True,
            "formal_save_read": False,
            "formal_save_written": False,
            "repository_candidate_written": False,
            "game_started": False,
        },
        "outputs": outputs,
        "scripts": {
            "pipeline": {
                "path": portable(Path(__file__)),
                "sha256": file_sha256(Path(__file__)),
            },
            "importer": {
                "path": portable(IMPORTER_PATH),
                "sha256": file_sha256(IMPORTER_PATH),
            },
            "materializer": {
                "path": portable(MATERIALIZER_PATH),
                "sha256": file_sha256(MATERIALIZER_PATH),
            },
            "independent_auditor": {
                "path": portable(INDEPENDENT_AUDITOR_PATH),
                "sha256": file_sha256(INDEPENDENT_AUDITOR_PATH),
            },
        },
    }
    summary_path = output_dir / "pipeline_summary.json"
    summary_sha = atomic_write(summary_path, summary)
    print(
        json.dumps(
            {
                "summary": str(summary_path),
                "summary_sha256": summary_sha,
                "status": summary["status"],
                "metrics": summary["metrics"],
                "candidate_sha256": outputs["research_candidate"]["sha256"],
                "checks": summary["checks"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return summary


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--dag", type=Path, default=DEFAULT_DAG)
    result.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    result.add_argument("--blif", type=Path, required=True)
    result.add_argument("--output-dir", type=Path, required=True)
    result.add_argument("--expected-gate", type=int)
    result.add_argument("--expected-delay", type=int)
    result.add_argument("--expected-energy", type=int)
    result.add_argument("--max-gate", type=int)
    result.add_argument("--max-delay", type=int)
    result.add_argument("--max-energy", type=int)
    return result


def main() -> int:
    run(parser().parse_args())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
