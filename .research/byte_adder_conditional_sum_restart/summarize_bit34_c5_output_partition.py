"""Close fixed g13/n11/s2/x0 by the exhaustive C5 driver partition."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
EXACT_PATH = HERE / "exact_bit34_joint_sat.py"
PAIR_SEARCH_PATH = HERE / "exact_bit34_c5_pair_cone_shards.py"
SINGLE_SEARCH_PATH = HERE / "exact_bit34_c5_single_driver_cone_shards.py"
PAIR_SCHEMA = "tc-byte-adder-bit34-c5-pair-cone-shards-v1"
SINGLE_SCHEMA = "tc-byte-adder-bit34-c5-single-driver-merged-ledger-v1"
OUTPUT_SCHEMA = "tc-byte-adder-bit34-c5-output-partition-ledger-v1"


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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pair", type=Path, required=True)
    parser.add_argument("--single", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    exact_sha = file_sha256(EXACT_PATH)
    pair_search_sha = file_sha256(PAIR_SEARCH_PATH)
    single_search_sha = file_sha256(SINGLE_SEARCH_PATH)
    pair = load_json(args.pair)
    single = load_json(args.single)
    errors = []

    if pair.get("schema") != PAIR_SCHEMA:
        errors.append("pair artifact schema mismatch")
    if pair.get("exact_search_sha256") != exact_sha:
        errors.append("pair artifact exact encoder hash mismatch")
    if pair.get("script_sha256") != pair_search_sha:
        errors.append("pair artifact search script hash mismatch")
    if pair.get("cone_size_domain") != list(range(10)):
        errors.append("pair artifact cone-size domain mismatch")
    if not pair.get("coverage_complete") or not pair.get("all_unsat"):
        errors.append("pair artifact is not complete all-UNSAT")

    if single.get("schema") != SINGLE_SCHEMA:
        errors.append("single artifact schema mismatch")
    if single.get("exact_search_sha256") != exact_sha:
        errors.append("single artifact exact encoder hash mismatch")
    if single.get("search_script_sha256") != single_search_sha:
        errors.append("single artifact search script hash mismatch")
    if single.get("shard_domain") != ["source", *(f"k{k}" for k in range(11))]:
        errors.append("single artifact shard domain mismatch")
    if not single.get("coverage_complete") or not single.get("all_unsat"):
        errors.append("single artifact is not complete all-UNSAT")

    complete = not errors
    payload = {
        "schema": OUTPUT_SCHEMA,
        "scope": {
            "profile": "d7_80",
            "gate_bound": 13,
            "components": 11,
            "exact_switches": 2,
            "exact_xors": 0,
            "output_deadlines": [5, 7, 4],
            "physical_nets": True,
            "boundary_rows": 48,
        },
        "partition_argument": [
            "The exact encoder adds a non-empty selector clause for C5, so its driver count is at least one.",
            "The encoder's active-bus normalization forbids any paid source or ordinary component output from coexisting with another selected driver.",
            "Therefore every C5 bus with at least two drivers consists only of Switch outputs.",
            "The base case contains exactly two Switch components, so a multi-driver C5 bus has exactly those two drivers.",
            "The single-driver ledger covers driver count one; the pair-cone ledger covers driver count two. No third case exists.",
        ],
        "branches": {
            "single_driver": {
                "artifact_path": str(args.single.resolve()),
                "artifact_sha256": file_sha256(args.single),
                "coverage_complete": single.get("coverage_complete"),
                "all_unsat": single.get("all_unsat"),
            },
            "two_switch_c5_net": {
                "artifact_path": str(args.pair.resolve()),
                "artifact_sha256": file_sha256(args.pair),
                "coverage_complete": pair.get("coverage_complete"),
                "all_unsat": pair.get("all_unsat"),
            },
        },
        "exact_search_path": str(EXACT_PATH),
        "exact_search_sha256": exact_sha,
        "pair_search_path": str(PAIR_SEARCH_PATH),
        "pair_search_sha256": pair_search_sha,
        "single_search_path": str(SINGLE_SEARCH_PATH),
        "single_search_sha256": single_search_sha,
        "summarizer_sha256": file_sha256(Path(__file__).resolve()),
        "errors": errors,
        "coverage_complete": complete,
        "all_unsat": complete,
        "conclusion": (
            "fixed d7_80 g13/n11/s2/x0 is UNSAT"
            if complete
            else "incomplete; no fixed-case conclusion"
        ),
        "scope_warning": (
            "This does not cover other component counts or Switch/XOR cost decompositions at gate 13."
        ),
    }
    atomic_write(args.output, payload)
    print(
        json.dumps(
            {
                "coverage_complete": complete,
                "all_unsat": complete,
                "errors": errors,
                "conclusion": payload["conclusion"],
                "output_sha256": file_sha256(args.output),
            },
            separators=(",", ":"),
        )
    )
    return 0 if complete else 2


if __name__ == "__main__":
    raise SystemExit(main())
