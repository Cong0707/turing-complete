"""Audit and summarize broad strict-C3 C5 normal-form shard artifacts."""

from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

import bit34_broad_c5_normal_form as normal_form


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SEARCH_PATH = HERE / "exact_bit34_broad_c5_normal_form_shard.py"
DEPENDENCY_PATHS = (
    HERE / "bit34_broad_c5_normal_form.py",
    HERE / "exact_bit34_joint_sat.py",
    ROOT
    / ".research"
    / "byte_adder_pair_macro_exact"
    / "exact_paid_physical_search_core.py",
    ROOT
    / ".research"
    / "byte_adder_pair_macro_exact"
    / "exact_paid_physical_core.py",
    ROOT
    / ".research"
    / "byte_adder_pair_macro_exact"
    / "exact_paid_physical_cnf.py",
)
TERMINAL_STATUSES = {"sat", "unsat"}
BAD_VERIFICATION_FIELDS = (
    "mismatch_count",
    "bus_conflict_count",
    "undriven_output_count",
    "physical_net_partition_violation_count",
)


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


def projected_value(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        return {"invalid": value}
    return {
        key: value.get(key)
        for key in ("name", "components", "shard", "constraint_sha256")
    }


def validate_spec(
    spec_path: Path,
    expected: list[dict[str, object]],
) -> tuple[dict[str, object], list[str]]:
    errors = []
    try:
        raw = spec_path.read_bytes()
        spec = json.loads(raw)
    except (OSError, ValueError) as exc:
        return {}, [f"cannot read spec {spec_path}: {exc}"]
    if not isinstance(spec, dict):
        return {
            "path": str(spec_path.resolve()),
            "sha256": sha256(raw).hexdigest(),
            "value_count": 0,
            "values_exact": False,
        }, ["spec top level is not an object"]
    values = spec.get("values")
    if not isinstance(values, list):
        values = []
        errors.append("spec values is not a list")
    projected = [projected_value(value) for value in values]
    if projected != expected:
        errors.append("spec values do not exactly match the canonical ordered domain")
    keys = [
        (value.get("components"), value.get("shard"))
        for value in values
        if isinstance(value, dict)
    ]
    duplicate_keys = sorted(
        [list(key) for key, count in Counter(keys).items() if count > 1],
        key=lambda item: (str(item[0]), str(item[1])),
    )
    if duplicate_keys:
        errors.append(f"spec has duplicate shard keys: {duplicate_keys}")
    names = [value.get("name") for value in values if isinstance(value, dict)]
    duplicate_names = sorted(
        str(name) for name, count in Counter(names).items() if count > 1
    )
    if duplicate_names:
        errors.append(f"spec has duplicate names: {duplicate_names}")
    return {
        "path": str(spec_path.resolve()),
        "sha256": sha256(raw).hexdigest(),
        "schema": spec.get("schema"),
        "name": spec.get("name"),
        "value_count": len(values),
        "duplicate_keys": duplicate_keys,
        "duplicate_names": duplicate_names,
        "values_exact": projected == expected,
    }, errors


def validate_artifact(
    path: Path,
    expected: dict[str, object],
    gate_bound: int,
    search_sha256: str,
    dependency_sha256: dict[str, str],
) -> tuple[dict[str, object], list[str]]:
    errors = []
    raw = path.read_bytes()
    try:
        payload = json.loads(raw)
    except ValueError as exc:
        return {
            "name": expected["name"],
            "path": str(path.resolve()),
            "sha256": sha256(raw).hexdigest(),
            "status": "malformed",
        }, [f"{expected['name']}: malformed JSON: {exc}"]
    if not isinstance(payload, dict):
        return {
            "name": expected["name"],
            "path": str(path.resolve()),
            "sha256": sha256(raw).hexdigest(),
            "status": "malformed",
        }, [f"{expected['name']}: JSON top level is not an object"]

    components = int(expected["components"])
    shard = str(expected["shard"])
    expected_identity = normal_form.constraint_identity(
        shard,
        components,
        gate_bound,
    )
    expected_digest = normal_form.canonical_sha256(expected_identity)
    constraint = payload.get("constraint")
    if not isinstance(constraint, dict):
        constraint = {}
        errors.append(f"{expected['name']}: constraint is not an object")
    checks = {
        "schema": payload.get("schema")
        == "tc-byte-adder-bit34-broad-c5-normal-form-shard-v1",
        "profile": payload.get("profile") == "d7_80",
        "gate_bound": payload.get("gate_bound") == gate_bound,
        "components": payload.get("components") == components,
        "shard": payload.get("shard") == shard,
        "boundary_rows": payload.get("assignments") == 48,
        "output_deadlines": payload.get("output_deadlines") == [5, 7, 4],
        "shard_domain": payload.get("shard_domain")
        == list(normal_form.shard_domain(components, gate_bound)),
        "constraint_identity": constraint.get("identity") == expected_identity,
        "constraint_digest": constraint.get("constraint_sha256")
        == expected_digest,
        "top_level_constraint_digest": payload.get("constraint_sha256")
        == expected_digest,
        "search_sha256": payload.get("script_sha256") == search_sha256,
    }
    dependencies = payload.get("dependencies")
    actual_dependencies = {}
    dependency_entries = 0
    if isinstance(dependencies, list):
        for item in dependencies:
            if not isinstance(item, dict):
                continue
            raw_path = item.get("path")
            digest = item.get("sha256")
            if isinstance(raw_path, str) and isinstance(digest, str):
                dependency_entries += 1
                actual_dependencies[Path(raw_path).name] = digest
    checks["dependency_sha256"] = actual_dependencies == dependency_sha256
    checks["dependency_entries_unique"] = (
        dependency_entries == len(actual_dependencies) == len(dependency_sha256)
    )

    status = payload.get("status")
    checks["known_status"] = status in {"sat", "unsat", "unknown"}
    if status == "sat":
        verification = payload.get("verification")
        checks["sat_verification"] = isinstance(verification, dict) and all(
            verification.get(field) == 0 for field in BAD_VERIFICATION_FIELDS
        )
        checks["sat_actual_gate"] = (
            isinstance(payload.get("actual_gate"), int)
            and int(payload["actual_gate"]) <= gate_bound
        )
        checks["sat_component_count"] = (
            isinstance(payload.get("network"), list)
            and len(payload["network"]) == components
        )
    failed_checks = sorted(key for key, passed in checks.items() if not passed)
    if failed_checks:
        errors.append(f"{expected['name']}: failed checks {failed_checks}")
    return {
        "name": expected["name"],
        "components": components,
        "shard": shard,
        "constraint_sha256": expected_digest,
        "path": str(path.resolve()),
        "sha256": sha256(raw).hexdigest(),
        "status": status,
        "checks": checks,
        "failed_checks": failed_checks,
        "solver": payload.get("solver"),
        "solve_seconds": payload.get("solve_seconds"),
    }, errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate-bound", type=int, default=13)
    parser.add_argument("--component", type=int, action="append", dest="components")
    parser.add_argument("--result-directory", type=Path, required=True)
    parser.add_argument("--spec", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    components = tuple(
        sorted(
            set(
                args.components
                if args.components is not None
                else range(args.gate_bound + 1)
            )
        )
    )
    if (
        not components
        or any(value < 0 or value > args.gate_bound for value in components)
    ):
        parser.error("components must be a non-empty subset of 0..gate-bound")

    expected = normal_form.shard_records(args.gate_bound, components)
    search_sha256 = file_sha256(SEARCH_PATH)
    dependency_sha256 = {
        path.name: file_sha256(path) for path in DEPENDENCY_PATHS
    }
    errors = []
    spec_record = None
    if args.spec is not None:
        spec_record, spec_errors = validate_spec(args.spec, expected)
        errors.extend(spec_errors)

    expected_names = {str(item["name"]) for item in expected}
    actual_paths = {
        path.stem: path
        for path in args.result_directory.glob("*.json")
        if path.is_file()
    }
    unexpected_files = sorted(set(actual_paths) - expected_names)
    if unexpected_files:
        errors.append(f"unexpected result files: {unexpected_files}")

    results = []
    missing = []
    for item in expected:
        name = str(item["name"])
        path = args.result_directory / f"{name}.json"
        if not path.is_file():
            missing.append(name)
            continue
        result, artifact_errors = validate_artifact(
            path,
            item,
            args.gate_bound,
            search_sha256,
            dependency_sha256,
        )
        results.append(result)
        errors.extend(artifact_errors)

    status_by_name = {str(item["name"]): item.get("status") for item in results}
    unknown = sorted(
        name for name, status in status_by_name.items() if status == "unknown"
    )
    sat = sorted(name for name, status in status_by_name.items() if status == "sat")
    unsat = sorted(
        name for name, status in status_by_name.items() if status == "unsat"
    )
    nonterminal = sorted(
        name
        for name, status in status_by_name.items()
        if status not in TERMINAL_STATUSES
    )
    result_keys = [
        (int(item["components"]), str(item["shard"])) for item in results
    ]
    duplicate_shards = sorted(
        [
            {"components": key[0], "shard": key[1]}
            for key, count in Counter(result_keys).items()
            if count > 1
        ],
        key=lambda item: (item["components"], item["shard"]),
    )
    if duplicate_shards:
        errors.append(f"duplicate result shards: {duplicate_shards}")
    coverage_complete = (
        not missing
        and not unknown
        and not nonterminal
        and not errors
        and len(results) == len(expected)
    )
    all_unsat = coverage_complete and len(unsat) == len(expected) and not sat
    payload = {
        "schema": "tc-byte-adder-bit34-broad-c5-summary-v1",
        "scope": {
            "profile": "d7_80",
            "gate_bound": args.gate_bound,
            "components": list(components),
            "output_deadlines": [5, 7, 4],
            "boundary_rows": 48,
            "physical_nets": True,
        },
        "normal_form": {
            "identity_schema": normal_form.IDENTITY_SCHEMA,
            "module": str(Path(normal_form.__file__).resolve()),
            "module_sha256": dependency_sha256[
                Path(normal_form.__file__).name
            ],
            "component_shard_counts": {
                str(value): len(normal_form.shard_domain(value, args.gate_bound))
                for value in components
            },
            "constraint_digests_recomputed": True,
        },
        "search_script": str(SEARCH_PATH.resolve()),
        "search_script_sha256": search_sha256,
        "dependencies": dependency_sha256,
        "spec": spec_record,
        "result_directory": str(args.result_directory.resolve()),
        "expected_shard_count": len(expected),
        "result_count": len(results),
        "missing_shards": missing,
        "unexpected_result_files": unexpected_files,
        "unknown_shards": unknown,
        "nonterminal_shards": nonterminal,
        "sat_shards": sat,
        "unsat_shards": unsat,
        "duplicate_shards": duplicate_shards,
        "errors": errors,
        "coverage_complete": coverage_complete,
        "all_unsat": all_unsat,
        "unknown_counts_as_coverage": False,
        "results": results,
        "script_sha256": file_sha256(Path(__file__).resolve()),
    }
    output_sha256 = atomic_json(args.output, payload)
    print(
        json.dumps(
            {
                "expected": len(expected),
                "results": len(results),
                "missing": len(missing),
                "unknown": len(unknown),
                "sat": len(sat),
                "unsat": len(unsat),
                "errors": len(errors),
                "coverage_complete": coverage_complete,
                "all_unsat": all_unsat,
                "output_sha256": output_sha256,
            },
            separators=(",", ":"),
        )
    )
    return 0 if not errors and (coverage_complete or sat) else 2


if __name__ == "__main__":
    raise SystemExit(main())
