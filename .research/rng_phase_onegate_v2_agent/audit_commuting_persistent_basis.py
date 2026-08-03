"""Prove the persistent-seed XOR2 timing obstruction for T commuting with A.

The script is research-only.  It imports matrix helpers, derives the proof
certificate, replays the particularly simple T=(A+I)^-1 realization, and
writes only the JSON file next to this source file.
"""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import random
import sys


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from tc_save_lab.rng_encoded_asic import (  # noqa: E402
    A,
    IDENTITY,
    apply_matrix,
    compose,
    invert,
    xorshift32,
)


OUT = Path(__file__).with_name("commuting_persistent_basis.json")
BITS = 32


def xor_matrix(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(a ^ b for a, b in zip(left, right, strict=True))


def matrix_power(matrix: tuple[int, ...], exponent: int) -> tuple[int, ...]:
    if exponent < 0:
        return matrix_power(invert(matrix), -exponent)
    result = IDENTITY
    base = matrix
    while exponent:
        if exponent & 1:
            result = compose(result, base)
        base = compose(base, base)
        exponent >>= 1
    return result


def histogram(rows: tuple[int, ...]) -> dict[str, int]:
    return {
        str(weight): sum(row.bit_count() == weight for row in rows)
        for weight in sorted({row.bit_count() for row in rows})
    }


def sha256_rows(rows: tuple[int, ...]) -> str:
    payload = b"".join(row.to_bytes(4, "little") for row in rows)
    return sha256(payload).hexdigest()


def replay_simple_basis() -> dict[str, object]:
    a_plus_i = xor_matrix(A, IDENTITY)
    t = invert(a_plus_i)
    t_inverse = a_plus_i
    b = compose(compose(t, A), t_inverse)
    d = compose(t, a_plus_i)
    c65 = compose(A, t_inverse)
    c66 = t_inverse

    identities = {
        "T commutes with A": compose(t, A) == compose(A, t),
        "B=A": b == A,
        "D=I": d == IDENTITY,
        "C66=A+I": c66 == a_plus_i,
        "C65=A*(A+I)": c65 == compose(A, a_plus_i),
    }
    if not all(identities.values()):
        raise AssertionError(f"simple-basis identity failure: {identities}")

    seeds = [0, 1, 2, 0x12345678, 0xFFFFFFFF]
    seeds.extend(1 << bit for bit in range(BITS))
    generator = random.Random(0xC011_2026)
    while len(seeds) < 293:
        candidate = generator.getrandbits(BITS)
        if candidate not in seeds:
            seeds.append(candidate)

    checks65 = 0
    checks66 = 0
    for seed in seeds:
        q = 0
        expected = seed
        for _ in range(65):
            expected = xorshift32(expected)
            output = apply_matrix(c65, q) ^ apply_matrix(A, seed)
            if output != expected:
                raise AssertionError("65-cycle simple-basis replay mismatch")
            q = apply_matrix(b, q) ^ seed
            checks65 += 1

        q = seed  # Tick zero is suppressed and captures D*seed = seed.
        expected = seed
        for _ in range(65):
            expected = xorshift32(expected)
            output = apply_matrix(c66, q) ^ seed
            if output != expected:
                raise AssertionError("66-cycle simple-basis replay mismatch")
            q = apply_matrix(b, q) ^ seed
            checks66 += 1

    return {
        "T": [f"{row:08x}" for row in t],
        "B": [f"{row:08x}" for row in b],
        "D": [f"{row:08x}" for row in d],
        "C65": [f"{row:08x}" for row in c65],
        "C66": [f"{row:08x}" for row in c66],
        "identities": identities,
        "seed_count": len(seeds),
        "checks65": checks65,
        "checks66": checks66,
        "recurrence": "q_next=A*q XOR seed",
        "output66": "(A+I)*q XOR seed = q_next XOR q",
    }


def main() -> None:
    a_plus_i = xor_matrix(A, IDENTITY)
    # Invert raises if A+I is singular.  Its invertibility also means every
    # row of D=T*(A+I) is nonzero for every invertible T.
    invert(a_plus_i)

    a_weights = tuple(row.bit_count() for row in A)
    obstructed = tuple(index for index, weight in enumerate(a_weights) if weight >= 4)
    witnesses = [
        {
            "row": index,
            "B_mask": f"{A[index]:08x}",
            "B_weight": a_weights[index],
            "minimum_D_weight": 1,
            "minimum_mixed_kraft_load": 4 * a_weights[index] + 1,
        }
        for index in obstructed
    ]

    cyclic_scan = []
    for exponent in range(-8, 9):
        t = matrix_power(A, exponent)
        b = compose(compose(t, A), invert(t))
        d = compose(t, a_plus_i)
        if b != A or min(row.bit_count() for row in d) < 1:
            raise AssertionError("commuting cyclic scan invariant failed")
        cyclic_scan.append(
            {
                "T": f"A^{exponent}",
                "B_weight_histogram": histogram(b),
                "D_weight_histogram": histogram(d),
                "minimum_feedback_kraft_load": min(
                    4 * b_row.bit_count() + d_row.bit_count()
                    for b_row, d_row in zip(b, d, strict=True)
                    if b_row.bit_count() >= 4
                ),
            }
        )

    result = {
        "schema": 1,
        "status": "commuting persistent XOR2 family timing-unsat",
        "game_started": False,
        "live_save_read_or_written": False,
        "model": {
            "state_arrival": 4,
            "seed_arrival": 0,
            "xor2_delay": 2,
            "deadline": [8, 9],
            "feedback": "B*q XOR D*seed",
            "B": "T*A*T^-1",
            "D": "T*(A+I)",
            "restriction": "T*A=A*T",
        },
        "proof": {
            "A_plus_I_invertible": True,
            "A_sha256": sha256_rows(A),
            "A_plus_I_sha256": sha256_rows(a_plus_i),
            "A_weight_histogram": histogram(A),
            "commutation_implies": "B=A",
            "invertible_T_and_A_plus_I_imply": "D is invertible, hence every D row has weight >=1",
            "mixed_kraft_condition": "4*wt(B_i)+wt(D_i)<=16",
            "obstructed_row_count": len(obstructed),
            "obstructed_rows": list(obstructed),
            "witnesses": witnesses,
            "sharing_note": "unfolding a shared XOR DAG into formulas preserves every required odd leaf and cannot lower Kraft load",
            "conclusion": "all invertible T commuting with A are impossible at total delay 8 or 9 in the XOR2 model",
        },
        "simple_basis_T_equals_inverse_A_plus_I": replay_simple_basis(),
        "cyclic_power_scan": cyclic_scan,
        "scope_limit": "does not exclude one-delay dual-rail Switch parity macros, nonlinear cancellation, noncommuting T, or redundant state",
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": result["status"],
                "A_weight_histogram": result["proof"]["A_weight_histogram"],
                "obstructed_row_count": len(obstructed),
                "simple_basis_replay": {
                    "seed_count": result["simple_basis_T_equals_inverse_A_plus_I"]["seed_count"],
                    "checks65": result["simple_basis_T_equals_inverse_A_plus_I"]["checks65"],
                    "checks66": result["simple_basis_T_equals_inverse_A_plus_I"]["checks66"],
                },
                "output": str(OUT),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
