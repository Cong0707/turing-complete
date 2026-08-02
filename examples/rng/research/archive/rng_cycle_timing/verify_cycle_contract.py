#!/usr/bin/env python3
"""Read-only certificate for the RNG architecture timing contract."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import random


BITS = 32
MASK = (1 << BITS) - 1
OUTPUT_COUNT = 65
REFERENCE_ENERGY = 256_014
EXPECTED_HASHES = {
    "Turing Complete.exe": "c93f5e8e826050c3f92e2b3891d26fcdfc933658614185cb9b2eb6a34c5b8d1c",
    "campaign/rng/test.si": "b396a9d5bba76bec2ceb123478dadc4616b6057894f17775982ed097c62fd50c",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def xorshift32(value: int) -> int:
    value ^= value >> 13
    value &= MASK
    value ^= (value << 17) & MASK
    value &= MASK
    value ^= value >> 5
    return value & MASK


def matrix_from_function(function) -> tuple[int, ...]:
    return tuple(
        sum(((function(1 << source) >> output) & 1) << source for source in range(BITS))
        for output in range(BITS)
    )


def apply_row(row: int, matrix: tuple[int, ...]) -> int:
    result = 0
    while row:
        low = row & -row
        result ^= matrix[low.bit_length() - 1]
        row ^= low
    return result


def apply_matrix(matrix: tuple[int, ...], value: int) -> int:
    return sum(((row & value).bit_count() & 1) << bit for bit, row in enumerate(matrix))


def compose(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(apply_row(row, right) for row in left)


def add(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(a ^ b for a, b in zip(left, right))


def invert(matrix: tuple[int, ...]) -> tuple[int, ...]:
    rows = [matrix[index] | ((1 << index) << BITS) for index in range(BITS)]
    for column in range(BITS):
        pivot = next(index for index in range(column, BITS) if rows[index] >> column & 1)
        rows[column], rows[pivot] = rows[pivot], rows[column]
        for index in range(BITS):
            if index != column and rows[index] >> column & 1:
                rows[index] ^= rows[column]
    return tuple((row >> BITS) & MASK for row in rows)


def right_shear(distance: int) -> tuple[int, ...]:
    return matrix_from_function(lambda value: (value ^ (value >> distance)) & MASK)


IDENTITY = tuple(1 << bit for bit in range(BITS))
A = matrix_from_function(xorshift32)
T = compose(right_shear(17), right_shear(13))
T_INVERSE = invert(T)
B = compose(T, compose(A, T_INVERSE))
C = compose(A, T_INVERSE)
D = compose(T, add(A, IDENTITY))


def require_fragment(blob: bytes, fragment: str, owner: str) -> int:
    offset = blob.find(fragment.encode("utf-8"))
    if offset < 0:
        raise RuntimeError(f"{owner} is missing runtime fragment {fragment!r}")
    return offset


def verify_runtime(game_root: Path) -> dict[str, object]:
    paths = {
        "Turing Complete.exe": game_root / "Turing Complete.exe",
        "campaign/rng/test.si": game_root / "campaign" / "rng" / "test.si",
    }
    hashes = {name: sha256(path) for name, path in paths.items()}
    if hashes != EXPECTED_HASHES:
        raise RuntimeError(f"live runtime hashes changed: {hashes}")

    test_blob = paths["campaign/rng/test.si"].read_bytes()
    executable = paths["Turing Complete.exe"].read_bytes()
    test_offsets = {
        fragment: require_fragment(test_blob, fragment, "campaign/rng/test.si")
        for fragment in (
            "var count = 0",
            "return .initial_seed",
            "if .count == 64",
            ".count += 1",
            ".seed = result",
        )
    }
    runtime_offsets = {
        fragment: require_fragment(executable, fragment, "Turing Complete.exe")
        for fragment in (
            "def mode_run(target_tick: Int) {",
            "while .tick < burst_target_tick {",
            " arch_get_input()",
            "let result = arch_check_output(Int arch_output)",
            "handle_test_result(result)",
            ".tick += 1 // Do this late as it signals to the front end that it can update",
        )
    }
    if not (
        runtime_offsets["while .tick < burst_target_tick {"]
        < runtime_offsets[".tick += 1 // Do this late as it signals to the front end that it can update"]
    ):
        raise RuntimeError("mode_run source ordering changed")

    count = 0
    callbacks = 0
    while True:
        callbacks += 1
        if count == 64:
            break
        count += 1
    if callbacks != OUTPUT_COUNT:
        raise AssertionError(f"test callback count changed: {callbacks}")
    return {
        "sha256": hashes,
        "test_fragment_offsets": test_offsets,
        "runtime_fragment_offsets": runtime_offsets,
        "required_output_callbacks": callbacks,
        "single_standard_output_minimum_cycles": callbacks,
    }


def verify_constant_seed_protocol() -> dict[str, object]:
    if compose(C, T) != A or compose(T, C) != B:
        raise AssertionError("encoded-state identities changed")
    if D != compose(T, add(A, IDENTITY)):
        raise AssertionError("constant-seed injection matrix changed")

    seeds = [0, 1, 2, 0x12345678, 0xFFFFFFFF]
    generator = random.Random(20260801)
    seeds.extend(generator.getrandbits(BITS) for _ in range(64))
    for seed in seeds:
        q = 0
        natural = seed
        for _ in range(OUTPUT_COUNT):
            output = apply_matrix(C, q) ^ apply_matrix(A, seed)
            next_q = apply_matrix(B, q) ^ apply_matrix(D, seed)
            natural = xorshift32(natural)
            if output != natural:
                raise AssertionError("direct-output constant-seed protocol failed")
            if next_q != apply_matrix(T, natural ^ seed):
                raise AssertionError("constant-seed state invariant failed")
            decoded_next = apply_matrix(T_INVERSE, next_q) ^ seed
            if decoded_next != natural:
                raise AssertionError("next-state decoder protocol failed")
            q = next_q
    return {
        "definition": "q_t = T*(x_t xor seed), q_0 = 0",
        "feedback": "q_next = B*q xor D*seed",
        "direct_output": "output = C*q xor A*seed",
        "next_state_output": "output = T^-1*q_next xor seed",
        "verified_seed_count": len(seeds),
        "verified_outputs_per_seed": OUTPUT_COUNT,
        "output_register_required": False,
    }


def score_budgets() -> dict[str, object]:
    budgets = {}
    for delay in range(8, 13):
        maximum_gate = (REFERENCE_ENERGY - 1) // (delay * OUTPUT_COUNT)
        maximum_xor = (maximum_gate - 32 * 5) // 3
        budgets[str(delay)] = {
            "maximum_gate_to_beat_reference": maximum_gate,
            "maximum_xor_with_32_delay_bits_and_no_other_scored_parts": maximum_xor,
        }
    return {
        "reference_energy": REFERENCE_ENERGY,
        "cycles": OUTPUT_COUNT,
        "budgets_by_delay": budgets,
    }


def multi_output_extension() -> dict[str, object]:
    return {
        "status": "runtime hypothesis; duplicate Architecture Output acceptance needs in-game validation",
        "reason": (
            "the code-generation template invokes arch_check_output for each enabled architecture-output "
            "component before the single tick increment"
        ),
        "cycles_if_m_callbacks_per_tick": {
            str(m): (OUTPUT_COUNT + m - 1) // m for m in range(1, 9)
        },
        "stride_m_state": "q_t = T*(A^(m*t)*seed xor seed)",
        "outputs_in_tick": "y_j = A^j*T^-1*q_t xor A^j*seed, j=1..m",
        "feedback": "q_next = T*A^m*T^-1*q_t xor T*(A^m+I)*seed",
    }


def main() -> int:
    game_root = Path(r"D:\Game\Steam\steamapps\common\Turing Complete")
    certificate = {
        "schema": 1,
        "runtime": verify_runtime(game_root),
        "constant_seed_protocol": verify_constant_seed_protocol(),
        "score": score_budgets(),
        "multi_output_extension": multi_output_extension(),
    }
    print(json.dumps(certificate, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
