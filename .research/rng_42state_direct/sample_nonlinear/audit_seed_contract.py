#!/usr/bin/env python3
"""Cross-check the two equivalent live RNG seed formulae.

This audit is intentionally independent from the saved rank certificates.  It
loads the runtime-backed contract verifier, reconstructs the same 256 seeds by
the reduced small-test formula, and compares both seed vectors and their
xorshift32 trajectories.  It never reads or writes the player save and never
starts the game.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import struct
from types import ModuleType


HERE = Path(__file__).resolve().parent
ROOT = next(parent for parent in HERE.parents if (parent / "pyproject.toml").exists())
CONTRACT_PATH = ROOT / ".research" / "rng_test_specialization" / "verify_rng_contract.py"

MASK64 = (1 << 64) - 1
SCRIPT_RANDOM_MODULUS = 0xFFFFFFFE
SMALL_TEST_LINEAR_MULTIPLIER = 0x4848F09881D3DDD1
EXPECTED_SEED_VECTOR_SHA256 = (
    "d8ef931e5eb213217aa4faedc43783f0875e52607f991e89080c6046aad1e24b"
)


def load_contract() -> ModuleType:
    spec = importlib.util.spec_from_file_location("rng_live_contract", CONTRACT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load contract verifier: {CONTRACT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def reduced_seed(test_id: int) -> int:
    n = test_id + 1
    return 1 + (((n * SMALL_TEST_LINEAR_MULTIPLIER) & MASK64) % SCRIPT_RANDOM_MODULUS)


def u32_vector_sha256(values: list[int]) -> str:
    packed = b"".join(struct.pack("<I", value) for value in values)
    return sha256(packed).hexdigest()


def trajectory(contract: ModuleType, seeds: list[int], rounds: int) -> list[int]:
    values: list[int] = []
    for seed in seeds:
        value = seed
        for _ in range(rounds):
            values.append(value)
            value = contract.xorshift32(value)
    return values


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rounds", type=int, default=66)
    parser.add_argument(
        "--output",
        type=Path,
        default=HERE / "seed_contract_audit.json",
    )
    args = parser.parse_args()
    if args.rounds <= 0:
        raise SystemExit("rounds must be positive")

    contract = load_contract()
    runtime_formula = [contract.initial_seed(test_id) for test_id in range(256)]
    reduced_formula = [reduced_seed(test_id) for test_id in range(256)]
    mismatches = [
        {
            "test_id": test_id,
            "runtime": f"{runtime_formula[test_id]:08x}",
            "reduced": f"{reduced_formula[test_id]:08x}",
        }
        for test_id in range(256)
        if runtime_formula[test_id] != reduced_formula[test_id]
    ]
    runtime_hash = u32_vector_sha256(runtime_formula)
    reduced_hash = u32_vector_sha256(reduced_formula)
    if runtime_hash != EXPECTED_SEED_VECTOR_SHA256:
        raise RuntimeError(f"runtime seed vector changed: {runtime_hash}")
    if mismatches:
        raise RuntimeError(f"seed formulae differ first at {mismatches[0]}")

    runtime_trajectory = trajectory(contract, runtime_formula, args.rounds)
    reduced_trajectory = trajectory(contract, reduced_formula, args.rounds)
    result = {
        "schema": 1,
        "contract_path": str(CONTRACT_PATH),
        "formulae": {
            "runtime": (
                "1 + (xorshift64star(test_id + 1, shifts 12/25/27, "
                "multiplier 0x2545f4914f6cdd1) mod 0xfffffffe)"
            ),
            "small_test_reduction": (
                "1 + ((((test_id + 1) * 0x4848f09881d3ddd1) mod 2^64) "
                "mod 0xfffffffe)"
            ),
        },
        "seed_count": len(runtime_formula),
        "runtime_unique_count": len(set(runtime_formula)),
        "reduced_unique_count": len(set(reduced_formula)),
        "set_intersection_count": len(set(runtime_formula) & set(reduced_formula)),
        "ordered_mismatch_count": len(mismatches),
        "first_ordered_mismatch": mismatches[0] if mismatches else None,
        "runtime_seed_vector_sha256": runtime_hash,
        "reduced_seed_vector_sha256": reduced_hash,
        "ordered_vectors_equal": runtime_formula == reduced_formula,
        "first_seeds_hex": [f"{seed:08x}" for seed in runtime_formula[:8]],
        "trajectory_rounds_per_seed": args.rounds,
        "trajectory_state_count": len(runtime_trajectory),
        "trajectory_unique_count": len(set(runtime_trajectory)),
        "runtime_trajectory_sha256": u32_vector_sha256(runtime_trajectory),
        "reduced_trajectory_sha256": u32_vector_sha256(reduced_trajectory),
        "ordered_trajectories_equal": runtime_trajectory == reduced_trajectory,
        "conclusion": (
            "0x2545f4914f6cdd1 and 0x4848f09881d3ddd1 are not competing "
            "RNG definitions: the latter is the exact reduced seed formula for "
            "test_id 0..255, while xorshift32 defines the per-tick transition"
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
