"""Independently validate a downloaded reachable-output-grouping summary.

This audit is intentionally summary-scoped when the per-group BLIF/log tree is
not present locally.  It does not rerun Espresso or ABC and does not promote a
summary-only result to importer or physical verification.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DEFAULT_PLA = (
    HERE / "abc_residual_current80" / "care_pla" / "reachable_relation_fr.pla"
)
DEFAULT_METADATA = HERE / "abc_residual_current80" / "metadata.json"
DEFAULT_LIBRARY = HERE.parent / "turing-complete.genlib"
EXPECTED_GROUPINGS: dict[str, list[list[int]]] = {
    "all": [list(range(9))],
    "independent": [[index] for index in range(9)],
    "low6_high3": [list(range(6)), [6, 7, 8]],
    "low5_high4": [list(range(5)), [5, 6, 7, 8]],
    "low4_mid2_high3": [[0, 1, 2, 3], [4, 5], [6, 7, 8]],
    "three_clusters": [[0, 1, 2], [3, 4, 5], [6, 7, 8]],
    "adjacent_pairs": [[0, 1], [2, 3], [4, 5], [6, 7], [8]],
    "staggered_pairs": [[0], [1, 2], [3, 4], [5, 6], [7, 8]],
    "high_independent": [list(range(6)), [6], [7], [8]],
    "low_independent": [[0], [1], [2], [3], [4], [5], [6, 7, 8]],
}


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def portable(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(resolved).replace("\\", "/")


def canonical_sha256(value: object) -> str:
    return sha256(
        json.dumps(value, ensure_ascii=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def atomic_write(path: Path, value: dict[str, Any]) -> str:
    raw = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(raw)
    temporary.replace(path)
    return sha256(raw).hexdigest()


def validate_metric_record(record: dict[str, Any], fixed_gate: int) -> None:
    arrivals = list(record["output_arrivals"])
    if len(arrivals) != 9:
        raise ValueError(f"grouping {record['name']!r} has wrong output-arrival width")
    if int(record["total_gate"]) != fixed_gate + int(record["residual_gate"]):
        raise ValueError(f"grouping {record['name']!r} has inconsistent gate count")
    if int(record["delay"]) != max(int(value) for value in arrivals):
        raise ValueError(f"grouping {record['name']!r} has inconsistent delay")
    if int(record["energy"]) != int(record["total_gate"]) * int(record["delay"]):
        raise ValueError(f"grouping {record['name']!r} has inconsistent energy")
    if int(record.get("care_mismatches", -1)) != 0:
        raise ValueError(f"grouping {record['name']!r} reports care mismatches")


def run(args: argparse.Namespace) -> dict[str, Any]:
    summary_path = args.summary.resolve()
    pla = args.pla.resolve()
    metadata_path = args.metadata.resolve()
    library = args.library.resolve()
    output = args.output.resolve()
    artifact_root = args.artifact_dir.resolve()
    for path in (summary_path, pla, metadata_path, library):
        if not path.is_file():
            raise FileNotFoundError(path)
    if not artifact_root.is_dir():
        raise NotADirectoryError(artifact_root)
    if args.energy_threshold <= 0:
        raise ValueError("energy threshold must be positive")

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if summary.get("schema") != "byte-adder-reachable-output-grouping-search-v1":
        raise ValueError("unexpected output-grouping schema")
    expected_count = len(EXPECTED_GROUPINGS)
    if (
        summary.get("expected_groupings") != expected_count
        or summary.get("completed_groupings") != expected_count
        or summary.get("error_count") != 0
        or summary.get("errors") != []
    ):
        raise ValueError("output-grouping summary is incomplete or contains errors")
    expected_hashes = {
        "input_sha256": file_sha256(pla),
        "metadata_sha256": file_sha256(metadata_path),
        "library_sha256": file_sha256(library),
    }
    for field, expected in expected_hashes.items():
        if summary.get(field) != expected:
            raise ValueError(f"summary {field} differs from current input")

    results = list(summary.get("results", ()))
    by_name: dict[str, dict[str, Any]] = {}
    for record in results:
        name = str(record["name"])
        if name in by_name:
            raise ValueError(f"duplicate grouping name {name!r}")
        by_name[name] = record
        groups = record["groups"]
        flattened = [int(value) for group in groups for value in group]
        if not groups or any(not group for group in groups):
            raise ValueError(f"grouping {name!r} contains an empty partition")
        if sorted(flattened) != list(range(9)) or len(set(flattened)) != 9:
            raise ValueError(f"grouping {name!r} is not a disjoint cover of outputs 0..8")
        if groups != EXPECTED_GROUPINGS.get(name):
            raise ValueError(f"grouping {name!r} differs from the declared search set")
        stats = list(record["group_stats"])
        if len(stats) != len(groups):
            raise ValueError(f"grouping {name!r} has wrong group_stats count")
        if [item["outputs"] for item in stats] != groups:
            raise ValueError(f"grouping {name!r} group_stats outputs differ")
        validate_metric_record(record, int(metadata["fixed_gate"]))
    if set(by_name) != set(EXPECTED_GROUPINGS) or len(results) != expected_count:
        raise ValueError("summary lacks one or more expected grouping names")

    best = min(
        results,
        key=lambda item: (
            int(item["energy"]),
            int(item["delay"]),
            int(item["total_gate"]),
            str(item["name"]),
        ),
    )
    hits = [item for item in results if int(item["energy"]) < args.energy_threshold]
    local_dirs = sorted(
        path.name
        for path in artifact_root.iterdir()
        if path.is_dir() and path.name in EXPECTED_GROUPINGS
    )
    verified = sorted(
        (
            (portable(summary_path), file_sha256(summary_path)),
            (portable(pla), file_sha256(pla)),
            (portable(metadata_path), file_sha256(metadata_path)),
            (portable(library), file_sha256(library)),
            (portable(HERE / "search_reachable_output_groupings.py"), file_sha256(HERE / "search_reachable_output_groupings.py")),
        )
    )
    payload = {
        "schema": "byte-adder-reachable-output-grouping-independent-summary-audit-v1",
        "status": "accepted",
        "summary": {
            "path": portable(summary_path),
            "sha256": file_sha256(summary_path),
            "record_count": len(results),
            "names_unique": True,
            "groups_are_disjoint_complete_partitions": True,
            "group_definitions_exact": True,
            "care_mismatches_zero": True,
            "metric_equations_exact": True,
            "best": {
                "name": best["name"],
                "gate": int(best["total_gate"]),
                "delay": int(best["delay"]),
                "energy": int(best["energy"]),
            },
            "energy_strictly_below": args.energy_threshold,
            "hit_count": len(hits),
        },
        "local_artifacts": {
            "group_directory_count": len(local_dirs),
            "group_directories": local_dirs,
            "summary_only": not local_dirs,
            "per_group_sha_recomputed": False,
            "importer_run": False,
        },
        "artifact_set": {
            "verified_file_count": len(verified),
            "path_sha256_set_sha256": canonical_sha256(verified),
        },
        "scope_note": (
            "Per-group BLIF/log artifacts are absent locally; acceptance covers summary "
            "combinatorics, source hashes, reported care status, and metric equations only."
        ),
        "safety": {
            "espresso_enumeration_run": False,
            "abc_mapping_run": False,
            "formal_save_read": False,
            "formal_save_written": False,
            "repository_candidate_written": False,
            "game_started": False,
        },
    }
    output_sha = atomic_write(output, payload)
    print(
        json.dumps(
            {
                "output": str(output),
                "output_sha256": output_sha,
                "status": payload["status"],
                "summary": payload["summary"],
                "local_artifacts": payload["local_artifacts"],
                "safety": payload["safety"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return payload


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--summary", type=Path, required=True)
    result.add_argument("--artifact-dir", type=Path, required=True)
    result.add_argument("--pla", type=Path, default=DEFAULT_PLA)
    result.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    result.add_argument("--library", type=Path, default=DEFAULT_LIBRARY)
    result.add_argument("--output", type=Path, required=True)
    result.add_argument("--energy-threshold", type=int, default=560)
    return result


def main() -> int:
    run(parser().parse_args())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
