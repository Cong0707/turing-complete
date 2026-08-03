"""Generate the frozen 230-shard broad C5 remote sweep and manifest."""

from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

import bit34_broad_c5_normal_form as normal_form


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GATE_BOUND = 13
OUTPUT_SPEC = HERE / "bit34_d7_g13_broad_c5_normal_form_workers3.json"
OUTPUT_MANIFEST = (
    HERE / "bit34_d7_g13_broad_c5_normal_form_workers3_manifest.json"
)
SEARCH_SCRIPT = HERE / "exact_bit34_broad_c5_normal_form_shard.py"
RUNNER = HERE / "remote_broad_c5_sweep_stop_on_sat.py"
SUMMARIZER = HERE / "summarize_bit34_broad_c5_shards.py"
POSITIVE_SCRIPT = HERE / "verify_bit34_broad_c5_positive_regression.py"
POSITIVE_ARTIFACT = HERE / "bit34_broad_c5_positive_g14.json"
POSITIVE_INDEPENDENT = (
    HERE / "bit34_broad_c5_positive_g14_independent_verify.json"
)
SMOKE_SUMMARY = HERE / "bit34_broad_c5_smoke_n00_n02_complete.json"
STATIC_AUDIT = HERE / "2026-08-04-bit34-broad-C5正常形独立静态覆盖审计.md"

REQUIRED_FILES = {
    "bit34_broad_c5_normal_form.py": HERE / "bit34_broad_c5_normal_form.py",
    "exact_bit34_broad_c5_normal_form_shard.py": SEARCH_SCRIPT,
    "exact_bit34_joint_sat.py": HERE / "exact_bit34_joint_sat.py",
    "verify_bit34_certificate.py": HERE / "verify_bit34_certificate.py",
    "summarize_bit34_broad_c5_shards.py": SUMMARIZER,
    "remote_broad_c5_sweep_stop_on_sat.py": RUNNER,
    "remote_sweep_stop_on_sat.py": HERE / "remote_sweep_stop_on_sat.py",
    "../byte_adder_pair_macro_exact/exact_paid_physical_search_core.py": (
        ROOT
        / ".research"
        / "byte_adder_pair_macro_exact"
        / "exact_paid_physical_search_core.py"
    ),
    "../byte_adder_pair_macro_exact/exact_paid_physical_core.py": (
        ROOT
        / ".research"
        / "byte_adder_pair_macro_exact"
        / "exact_paid_physical_core.py"
    ),
    "../byte_adder_pair_macro_exact/exact_paid_physical_cnf.py": (
        ROOT
        / ".research"
        / "byte_adder_pair_macro_exact"
        / "exact_paid_physical_cnf.py"
    ),
    "../byte_adder_remote_compute/remote_sweep.py": (
        ROOT / ".research" / "byte_adder_remote_compute" / "remote_sweep.py"
    ),
}


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_json(path: Path, payload: object) -> str:
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode(
        "utf-8"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(encoded)
    temporary.replace(path)
    return sha256(encoded).hexdigest()


def artifact_record(path: Path) -> dict[str, object]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": file_sha256(path),
    }


def main() -> int:
    missing_required = [
        str(path) for path in REQUIRED_FILES.values() if not path.is_file()
    ]
    if missing_required:
        raise RuntimeError(f"required files missing: {missing_required}")
    required_hashes = {
        raw_path: file_sha256(path)
        for raw_path, path in REQUIRED_FILES.items()
    }
    values = normal_form.shard_records(GATE_BOUND, range(GATE_BOUND + 1))
    if len(values) != 230:
        raise RuntimeError(f"expected 230 shards, got {len(values)}")
    if len({str(value["name"]) for value in values}) != 230:
        raise RuntimeError("shard names are not unique")
    if len({str(value["constraint_sha256"]) for value in values}) != 230:
        raise RuntimeError("constraint identities are not unique")

    spec = {
        "schema": "tc-byte-adder-remote-sweep-v1",
        "name": "bit34-d7-g13-broad-c5-normal-form-workers3",
        "script": SEARCH_SCRIPT.name,
        "working_directory": ".",
        "values": values,
        "workers": 3,
        "timeout_seconds": 21600,
        "memory_mb_per_process": 4096,
        "cpu_set": "0-23",
        "nice": 10,
        "log_directory": "logs/bit34_d7_g13_broad_c5_normal_form_workers3",
        "result_directory": (
            "run-results/bit34_d7_g13_broad_c5_normal_form_workers3"
        ),
        "summary": "bit34-d7-g13-broad-c5-normal-form-workers3-summary.json",
        "runner": RUNNER.name,
        "stop_on_first_sat": True,
        "resume_terminal_outputs": True,
        "poll_seconds": 0.5,
        "arguments": [
            "--gate-bound",
            "13",
            "--components",
            "{components}",
            "--shard",
            "{shard}",
            "--solver",
            "cadical195",
            "--timeout",
            "0",
            "--output",
            "results/bit34_d7_g13_broad_c5_normal_form/{name}.json",
        ],
        "partition": {
            "profile": "d7_80",
            "gate_bound": GATE_BOUND,
            "component_domain": list(range(GATE_BOUND + 1)),
            "component_shard_counts": normal_form.component_shard_counts(
                GATE_BOUND
            ),
            "shard_count": len(values),
            "constraint_identity_schema": normal_form.IDENTITY_SCHEMA,
            "pairwise_exclusive_within_normal_form": True,
            "complete_up_to_topological_normalization": True,
            "proof": (
                "C5 is non-empty.  A source driver is necessarily singleton; "
                "a singleton component driver has one normalized ancestor "
                "count; every multi-driver C5 net contains only Switch outputs. "
                "Physical-net partition makes those Switch drivers mutually "
                "independent, so all of their component ancestors can be "
                "topologically ordered first, followed by the d drivers and "
                "then every non-ancestor.  The weighted bound gives "
                "d <= min(n,13-n)."
            ),
        },
        "priority": {
            "existing_sweep": (
                "bit34-d7-g13-n11-s2-x0-slot01-kind-partition-workers4-resume"
            ),
            "existing_sweep_nice": 5,
            "broad_sweep_nice": 10,
            "existing_runner_not_modified": True,
            "broad_dynamic_concurrency_limit": 3,
        },
        "required_files": list(REQUIRED_FILES),
        "required_file_sha256": required_hashes,
        "python_requirement": (
            "CPython 3.12; python-sat 1.8.dev24 with cadical195"
        ),
    }
    spec_sha256 = atomic_json(OUTPUT_SPEC, spec)

    regression_paths = (
        POSITIVE_SCRIPT,
        POSITIVE_ARTIFACT,
        POSITIVE_INDEPENDENT,
        SMOKE_SUMMARY,
    )
    missing_regression = [str(path) for path in regression_paths if not path.is_file()]
    if missing_regression:
        raise RuntimeError(f"regression artifacts missing: {missing_regression}")
    smoke_paths = sorted((HERE / "broad_c5_smoke").glob("*.json"))
    if len(smoke_paths) != 7:
        raise RuntimeError(f"expected 7 smoke artifacts, got {len(smoke_paths)}")

    manifest = {
        "schema": "tc-byte-adder-bit34-broad-c5-remote-manifest-v1",
        "status": "prepared-not-uploaded-not-started",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "scope": {
            "profile": "d7_80",
            "gate_bound": GATE_BOUND,
            "components": list(range(GATE_BOUND + 1)),
            "switches": None,
            "xors": None,
            "output_deadlines": [5, 7, 4],
            "boundary_rows": 48,
        },
        "spec": {
            "path": str(OUTPUT_SPEC.resolve()),
            "sha256": spec_sha256,
            "shards": len(values),
        },
        "required_files": [
            {
                "remote_path": raw_path,
                "local_path": str(path.resolve()),
                "sha256": required_hashes[raw_path],
            }
            for raw_path, path in REQUIRED_FILES.items()
        ],
        "regressions": {
            "positive_g14": artifact_record(POSITIVE_ARTIFACT),
            "positive_g14_independent_verify": artifact_record(
                POSITIVE_INDEPENDENT
            ),
            "smoke_summary": artifact_record(SMOKE_SUMMARY),
            "smoke_shards": [artifact_record(path) for path in smoke_paths],
        },
        "static_audit": (
            artifact_record(STATIC_AUDIT) if STATIC_AUDIT.is_file() else None
        ),
        "resource_policy": {
            "workers": 3,
            "maximum_dynamic_concurrency": 3,
            "memory_mb_per_process": 4096,
            "maximum_scheduled_memory_mb": 12288,
            "cpu_set": "0-23",
            "nice": 10,
            "outer_timeout_seconds_per_shard": 21600,
            "internal_solver_timeout_seconds": 0,
            "stop_on_first_sat": True,
            "resume_terminal_outputs": True,
            "existing_49_shard_runner_untouched": True,
        },
        "shards": [
            {
                **value,
                "output": (
                    "results/bit34_d7_g13_broad_c5_normal_form/"
                    f"{value['name']}.json"
                ),
            }
            for value in values
        ],
    }
    manifest_sha256 = atomic_json(OUTPUT_MANIFEST, manifest)
    print(
        json.dumps(
            {
                "spec": str(OUTPUT_SPEC),
                "spec_sha256": spec_sha256,
                "manifest": str(OUTPUT_MANIFEST),
                "manifest_sha256": manifest_sha256,
                "shards": len(values),
                "workers": spec["workers"],
                "maximum_scheduled_memory_mb": (
                    spec["workers"] * spec["memory_mb_per_process"]
                ),
                "nice": spec["nice"],
                "status": manifest["status"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
