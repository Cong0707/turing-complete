#!/usr/bin/env python3
"""Read-only certificates for two 65-cycle delay-9 dead ends.

The first certificate checks the fixed finite shear family used by the
constant-seed encoder search.  The second uses the live 256 test seeds and
all 65 trajectories to show that a raw seed bit cannot be OR-mixed with any
nonzero linear encoded-state bit without observing a simultaneous-one sample.
This is a necessary-condition audit, not a claim about arbitrary nonlinear
sample-specialized circuits.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".research" / "rng_constant_seed_search"))
import search  # noqa: E402


BITS = 32
MASK = (1 << BITS) - 1
OUT = ROOT / ".research" / "rng_cycle65_continue" / "phase_free_or_certificate.json"


def gf2_rank(values: list[int]) -> int:
    basis = [0] * BITS
    rank = 0
    for value in values:
        value &= MASK
        while value:
            pivot = value.bit_length() - 1
            if basis[pivot]:
                value ^= basis[pivot]
            else:
                basis[pivot] = value
                rank += 1
                break
    return rank


def left_shear(distance: int) -> tuple[int, ...]:
    return search.matrix_from_function(
        lambda value: (value ^ ((value << distance) & MASK)) & MASK
    )


def load_seeds() -> list[int]:
    # The fixed vector is independently pinned by the existing runtime
    # contract verifier.  Keep the formula local so this certificate remains
    # a small standard-library replay.
    multiplier = 0x4848F09881D3DDD1
    modulus = 0xFFFFFFFE
    mask64 = (1 << 64) - 1
    result = []
    for test_id in range(256):
        n = test_id + 1
        value = (n * multiplier) & mask64
        result.append(1 + (value % modulus))
    return result


def trajectory_rank_certificate() -> dict[str, object]:
    seeds = load_seeds()
    by_seed_bit: list[list[int]] = [[] for _ in range(BITS)]
    for seed in seeds:
        state = seed
        # t=0 gives q=0 and cannot affect the rank.  The remaining 64
        # states are exactly the states visible during the 65-callback run.
        for _ in range(65):
            q = state ^ seed
            for bit in range(BITS):
                if (seed >> bit) & 1:
                    by_seed_bit[bit].append(q)
            state = search.xorshift32(state)
    ranks = [gf2_rank(values) for values in by_seed_bit]
    if ranks != [BITS] * BITS:
        raise AssertionError(f"seed-conditioned trajectory ranks changed: {ranks}")
    packed = b"".join(value.to_bytes(4, "little") for value in seeds)
    return {
        "seed_count": len(seeds),
        "trajectory_states_per_seed": 65,
        "seed_vector_sha256": hashlib.sha256(packed).hexdigest(),
        "conditioned_vector_counts": [len(values) for values in by_seed_bit],
        "conditioned_q_span_ranks": ranks,
        "conclusion": (
            "for every raw seed bit s_i, the q=x xor seed values observed when "
            "s_i=1 span GF(2)^32; hence no nonzero linear q row is identically "
            "zero on that condition, so every raw (s_i,q_j) OR pair has a "
            "simultaneous-one test state"
        ),
    }


def kraft_loads(encoding: tuple[int, ...]) -> list[int]:
    matrices = search.Matrices.from_encoding(encoding)
    decoder = matrices.decoder
    output_q = search.matrix_multiply(search.A, decoder)
    return [
        *(
            4 * transition.bit_count() + injection.bit_count()
            for transition, injection in zip(matrices.transition, matrices.seed_injection)
        ),
        *(4 * row.bit_count() + seed_row.bit_count() for row, seed_row in zip(output_q, search.A)),
    ]


def shear_family_certificate() -> dict[str, object]:
    operations: list[tuple[str, tuple[int, ...]]] = [("I", search.IDENTITY)]
    operations.extend((f"R{distance}", search.right_shear(distance)) for distance in range(1, BITS))
    operations.extend((f"L{distance}", left_shear(distance)) for distance in range(1, BITS))
    best: tuple[tuple[int, ...], tuple[str, ...], tuple[int, ...], list[int]] | None = None
    feasible = 0
    candidates = 0
    for name_a, matrix_a in operations:
        for name_b, matrix_b in operations:
            prefix = search.matrix_multiply(matrix_b, matrix_a)
            for name_c, matrix_c in operations:
                encoding = search.matrix_multiply(matrix_c, prefix)
                loads = kraft_loads(encoding)
                excess = [max(0, load - 16) for load in loads]
                key = (
                    sum(value * value for value in excess),
                    sum(excess),
                    sum(value != 0 for value in excess),
                    max(loads),
                    sum(loads),
                )
                candidates += 1
                if key[0] == 0:
                    feasible += 1
                record = (key, (name_a, name_b, name_c), encoding, loads)
                if best is None or key < best[0]:
                    best = record
    assert best is not None
    return {
        "family": "ordered products of three choices from I, I+Rk, I+Lk; 1<=k<32",
        "candidate_count": candidates,
        "kraft_feasible_count": feasible,
        "delay9_kraft_rule": "4*q_weight + seed_weight <= 16 for every target",
        "best": {
            "squared_excess": best[0][0],
            "excess": best[0][1],
            "violating_rows": best[0][2],
            "maximum_load": best[0][3],
            "total_load": best[0][4],
            "operations": best[1],
            "encoding": [f"{row:08x}" for row in best[2]],
            "loads": best[3],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUT)
    parser.add_argument("--skip-shear-family", action="store_true")
    args = parser.parse_args()
    payload = {
        "schema": 1,
        "scope": "65-cycle constant-seed delay9 necessary conditions; no save/game access",
        "trajectory_rank": trajectory_rank_certificate(),
    }
    if not args.skip_shear_family:
        payload["shear_family"] = shear_family_certificate()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
