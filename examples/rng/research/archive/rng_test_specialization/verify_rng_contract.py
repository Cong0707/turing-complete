#!/usr/bin/env python3
"""Verify the live RNG test contract and its fixed 256-case sample set.

This script is intentionally read-only.  It reads the installed game assets,
reconstructs the script PRNG for test ids 0..255, and emits a compact JSON
certificate.  It does not read or write the player's save directory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
from pathlib import Path


MASK32 = (1 << 32) - 1
MASK64 = (1 << 64) - 1
SCRIPT_RANDOM_MODULUS = 0xFFFFFFFE
XORSHIFT64_STAR_MULTIPLIER = 0x2545F4914F6CDD1
SMALL_TEST_LINEAR_MULTIPLIER = 0x4848F09881D3DDD1

EXPECTED_HASHES = {
    "Turing Complete.exe": "c93f5e8e826050c3f92e2b3891d26fcdfc933658614185cb9b2eb6a34c5b8d1c",
    "compile.dll": "d4f258ca43456df685592f4562cd4450a0baecc47972d6c615042e34e33eb08b",
    "campaign/rng/test.si": "b396a9d5bba76bec2ceb123478dadc4616b6057894f17775982ed097c62fd50c",
    "campaign/rng/meta.txt": "b75269554e75007582f0f4b7a2d022767e618faca18e6c5337a93a953ff32141",
}

EXPECTED_SEED_VECTOR_SHA256 = (
    "d8ef931e5eb213217aa4faedc43783f0875e52607f991e89080c6046aad1e24b"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def xorshift64_star(value: int) -> int:
    value &= MASK64
    value ^= (value << 12) & MASK64
    value ^= value >> 25
    value ^= value >> 27
    return (value * XORSHIFT64_STAR_MULTIPLIER) & MASK64


def initial_seed(test_id: int) -> int:
    if not 0 <= test_id < 256:
        raise ValueError("test_id must be in 0..255")
    random_value = xorshift64_star(test_id + 1)
    return 1 + random_value % SCRIPT_RANDOM_MODULUS


def xorshift32(value: int) -> int:
    value &= MASK32
    value = (value ^ (value >> 13)) & MASK32
    value = (value ^ ((value << 17) & MASK32)) & MASK32
    value = (value ^ (value >> 5)) & MASK32
    return value


def gf2_rank(values: list[int], width: int = 32) -> int:
    basis = [0] * width
    rank = 0
    for original in values:
        value = original & ((1 << width) - 1)
        while value:
            pivot = value.bit_length() - 1
            if basis[pivot]:
                value ^= basis[pivot]
                continue
            basis[pivot] = value
            rank += 1
            break
    return rank


def require_bytes(blob: bytes, needle: str, owner: str) -> None:
    encoded = needle.encode("utf-8")
    if encoded not in blob:
        raise RuntimeError(f"{owner} no longer contains runtime evidence: {needle!r}")


def verify_sources(game_root: Path) -> dict[str, object]:
    paths = {
        "Turing Complete.exe": game_root / "Turing Complete.exe",
        "compile.dll": game_root / "compile.dll",
        "campaign/rng/test.si": game_root / "campaign" / "rng" / "test.si",
        "campaign/rng/meta.txt": game_root / "campaign" / "rng" / "meta.txt",
    }
    observed_hashes = {name: sha256(path) for name, path in paths.items()}
    if observed_hashes != EXPECTED_HASHES:
        raise RuntimeError(
            "installed runtime hashes changed; review the live files before trusting this certificate: "
            + json.dumps(observed_hashes, sort_keys=True)
        )

    test_source = paths["campaign/rng/test.si"].read_text(encoding="utf-8")
    meta_source = paths["campaign/rng/meta.txt"].read_text(encoding="utf-8")
    executable = paths["Turing Complete.exe"].read_bytes()
    compiler = paths["compile.dll"].read_bytes()

    required_test_fragments = (
        "var initial_seed = 1 + random(0xfffffffe)",
        "var seed = initial_seed",
        "def arch_get_input() Int",
        "return .initial_seed",
        "def arch_check_output(output: Int) TestResult",
        "if .count == 64",
        "return win",
        ".seed = result",
    )
    for fragment in required_test_fragments:
        if fragment not in test_source:
            raise RuntimeError(f"rng/test.si contract changed: missing {fragment!r}")

    tests_match = re.search(r"(?m)^tests\s*=\s*(\d+)\s*$", meta_source)
    if tests_match is None or int(tests_match.group(1)) != 256:
        raise RuntimeError("rng/meta.txt no longer declares exactly 256 tests")

    # These are source templates embedded in the live runtime.  Together they
    # pin the decisive ordering: reset selects ctl_test, then every simulation
    # tick executes generated circuit code containing arch_get_input(), and an
    # enabled architecture output calls arch_check_output once in that tick.
    executable_fragments = (
        ".global_seed = Seed (get_command(ctl_test) + 1) // 0 can't be seed",
        "def mode_run(target_tick: Int) {",
        "while .tick < burst_target_tick {",
        " arch_get_input()",
        "let result = arch_check_output(Int arch_output)",
        ".tick += 1 // Do this late as it signals to the front end that it can update",
    )
    for fragment in executable_fragments:
        require_bytes(executable, fragment, "Turing Complete.exe")

    compiler_fragments = (
        "def xorshift(input: Int) Int {",
        "x ^= x << 12",
        "x ^= x >> 25",
        "x ^= x >> 27",
        "return x * 0x2545F4914F6CDD1",
        "return Int (U64 result % U64 max)",
    )
    for fragment in compiler_fragments:
        require_bytes(compiler, fragment, "compile.dll")

    return {
        "game_root": str(game_root),
        "sha256": observed_hashes,
        "test_count": 256,
        "test_ids": [0, 255],
        "input_semantics": (
            "arch_get_input is evaluated by generated circuit code on every tick; "
            "rng/test.si returns the unchanged initial_seed every time"
        ),
        "output_semantics": (
            "each enabled architecture-output tick invokes arch_check_output once"
        ),
    }


def build_sample_certificate() -> dict[str, object]:
    seeds = [initial_seed(test_id) for test_id in range(256)]
    packed = b"".join(struct.pack("<I", seed) for seed in seeds)
    vector_hash = hashlib.sha256(packed).hexdigest()
    if vector_hash != EXPECTED_SEED_VECTOR_SHA256:
        raise RuntimeError(f"fixed seed vector changed: {vector_hash}")

    for test_id, seed in enumerate(seeds):
        n = test_id + 1
        reduced = 1 + (((n * SMALL_TEST_LINEAR_MULTIPLIER) & MASK64) % SCRIPT_RANDOM_MODULUS)
        if seed != reduced:
            raise RuntimeError(f"small-test PRNG reduction failed at test {test_id}")

    full_rank_prefix = next(
        count for count in range(1, len(seeds) + 1) if gf2_rank(seeds[:count]) == 32
    )
    affine_rank = gf2_rank([seed ^ seeds[0] for seed in seeds[1:]])

    visited: dict[int, tuple[int, int]] = {}
    for test_id, seed in enumerate(seeds):
        value = seed
        for offset in range(66):
            previous = visited.setdefault(value, (test_id, offset))
            if previous != (test_id, offset):
                raise RuntimeError(
                    f"trajectory collision: {(test_id, offset)} collides with {previous}"
                )
            value = xorshift32(value)

    return {
        "seed_formula": (
            "seed(test_id) = 1 + (((test_id + 1) * 0x4848f09881d3ddd1 mod 2^64) "
            "mod 0xfffffffe)"
        ),
        "seed_vector_encoding": "256 little-endian U32 values in test-id order",
        "seed_vector_sha256": vector_hash,
        "seed_count": len(seeds),
        "seed_unique_count": len(set(seeds)),
        "seed_linear_rank_gf2": gf2_rank(seeds),
        "seed_affine_rank_gf2": affine_rank,
        "first_full_rank_prefix_length": full_rank_prefix,
        "trajectory_definition": "seed plus F(seed)..F^65(seed) for each test",
        "trajectory_state_count": 256 * 66,
        "trajectory_unique_state_count": len(visited),
        "first_seeds_hex": [f"{seed:08x}" for seed in seeds[:8]],
        "linear_specialization_consequence": (
            "the tested initial seeds span GF(2)^32, so any linear 32-bit first-step "
            "network agreeing with F on all tests is exactly F on every 32-bit input"
        ),
    }


def build_affine_state_certificate() -> dict[str, object]:
    return {
        "definition": "q_t = T(x_t xor s), where x_0=s and T is any invertible GF(2) map",
        "initial_state": "q_0 = 0",
        "transition": "q_(t+1) = B*q_t xor D*s",
        "B": "T*A*T^-1",
        "D": "T*(A+I) = (B+I)*T",
        "output_forms": [
            "x_(t+1) = T^-1*q_(t+1) xor s",
            "x_(t+1) = (A*T^-1)*q_t xor A*s",
        ],
        "protocol_precondition": (
            "s is continuously available because rng arch_get_input returns initial_seed on every tick"
        ),
        "scope": (
            "algebraic protocol certificate only; a concrete circuit still needs joint XOR synthesis, "
            "timing, routing, and in-game verification"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--game-root",
        type=Path,
        default=Path(r"D:\Game\Steam\steamapps\common\Turing Complete"),
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    certificate = {
        "schema": 1,
        "runtime": verify_sources(args.game_root),
        "samples": build_sample_certificate(),
        "continuous_seed_affine_state": build_affine_state_certificate(),
    }
    rendered = json.dumps(certificate, ensure_ascii=False, indent=2) + "\n"
    if args.output is None:
        print(rendered, end="")
    else:
        args.output.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
