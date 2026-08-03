"""Merge terminal C5 single-driver cone shards with provenance checks."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SEARCH_PATH = HERE / "exact_bit34_c5_single_driver_cone_shards.py"
EXACT_PATH = HERE / "exact_bit34_joint_sat.py"
SCHEMA = "tc-byte-adder-bit34-c5-single-driver-cone-shards-v1"
OUTPUT_SCHEMA = "tc-byte-adder-bit34-c5-single-driver-merged-ledger-v1"
SHARDS = ("source", *(f"k{count}" for count in range(11)))


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: root JSON value is not an object")
    return value


def atomic_write(path: Path, payload: dict[str, object]) -> None:
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode(
        "utf-8"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(encoded)
    temporary.replace(path)


def shard_sort_key(shard: str) -> tuple[int, int]:
    return (0, -1) if shard == "source" else (1, int(shard[1:]))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifacts", nargs="+", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    expected_search_sha = file_sha256(SEARCH_PATH)
    expected_exact_sha = file_sha256(EXACT_PATH)
    provenance = []
    observations: dict[str, list[dict[str, object]]] = {shard: [] for shard in SHARDS}
    constraint_digests: dict[str, set[str]] = {shard: set() for shard in SHARDS}

    for path in args.artifacts:
        payload = load_json(path)
        if payload.get("schema") != SCHEMA:
            raise ValueError(f"{path}: unexpected schema {payload.get('schema')!r}")
        if payload.get("script_sha256") != expected_search_sha:
            raise ValueError(f"{path}: search script hash mismatch")
        if payload.get("exact_search_sha256") != expected_exact_sha:
            raise ValueError(f"{path}: exact encoder hash mismatch")
        if tuple(payload.get("shard_domain", ())) != SHARDS:
            raise ValueError(f"{path}: shard domain mismatch")

        artifact_sha = file_sha256(path)
        provenance.append(
            {
                "path": str(path.resolve()),
                "sha256": artifact_sha,
                "solver": payload.get("solver"),
                "timeout_seconds_per_shard": payload.get(
                    "timeout_seconds_per_shard"
                ),
            }
        )
        for result in payload.get("results", ()):  # type: ignore[union-attr]
            shard = str(result.get("shard"))
            if shard not in observations:
                raise ValueError(f"{path}: unknown result shard {shard!r}")
            digest = result.get("constraint_sha256")
            if not isinstance(digest, str):
                raise ValueError(f"{path}: shard {shard} lacks constraint digest")
            constraint_digests[shard].add(digest)
            observations[shard].append(
                {
                    **result,
                    "artifact_path": str(path.resolve()),
                    "artifact_sha256": artifact_sha,
                    "solver": payload.get("solver"),
                    "timeout_seconds_per_shard": payload.get(
                        "timeout_seconds_per_shard"
                    ),
                }
            )

    selected = []
    conflicts = []
    missing = []
    unknown_only = []
    for shard in SHARDS:
        if len(constraint_digests[shard]) > 1:
            conflicts.append(
                {
                    "shard": shard,
                    "reason": "constraint digest mismatch",
                    "digests": sorted(constraint_digests[shard]),
                }
            )
            continue
        rows = observations[shard]
        if not rows:
            missing.append(shard)
            continue
        terminal = [row for row in rows if row.get("status") in {"sat", "unsat"}]
        terminal_statuses = {str(row["status"]) for row in terminal}
        if len(terminal_statuses) > 1:
            conflicts.append(
                {
                    "shard": shard,
                    "reason": "conflicting terminal statuses",
                    "statuses": sorted(terminal_statuses),
                }
            )
            continue
        if not terminal:
            unknown_only.append(shard)
            continue
        terminal.sort(
            key=lambda row: (
                float(row.get("solve_seconds", float("inf"))),
                str(row.get("artifact_sha256")),
            )
        )
        selected.append(terminal[0])

    selected.sort(key=lambda row: shard_sort_key(str(row["shard"])))
    sat = [str(row["shard"]) for row in selected if row["status"] == "sat"]
    unsat = [str(row["shard"]) for row in selected if row["status"] == "unsat"]
    coverage_complete = not conflicts and not missing and not unknown_only
    all_unsat = coverage_complete and not sat and tuple(unsat) == SHARDS

    payload = {
        "schema": OUTPUT_SCHEMA,
        "source_artifacts": provenance,
        "search_script_path": str(SEARCH_PATH),
        "search_script_sha256": expected_search_sha,
        "exact_search_path": str(EXACT_PATH),
        "exact_search_sha256": expected_exact_sha,
        "summarizer_sha256": file_sha256(Path(__file__).resolve()),
        "shard_domain": list(SHARDS),
        "selected_terminal_results": selected,
        "unsat_shards": unsat,
        "sat_shards": sat,
        "missing_shards": missing,
        "unknown_only_shards": unknown_only,
        "conflicts": conflicts,
        "coverage_complete": coverage_complete,
        "all_unsat": all_unsat,
    }
    atomic_write(args.output, payload)
    print(
        json.dumps(
            {
                "coverage_complete": coverage_complete,
                "all_unsat": all_unsat,
                "sat_shards": sat,
                "missing_shards": missing,
                "unknown_only_shards": unknown_only,
                "conflicts": conflicts,
                "output_sha256": file_sha256(args.output),
            },
            separators=(",", ":"),
        )
    )
    return 0 if coverage_complete else 2


if __name__ == "__main__":
    raise SystemExit(main())
