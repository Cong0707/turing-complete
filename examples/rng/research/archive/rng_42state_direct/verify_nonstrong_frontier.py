#!/usr/bin/env python3
"""Verify a genuinely non-strong 42-state RNG frontier.

The certificate is research-only.  It proves exact linear behavior and also
records why the matrix is not a depth-two XOR implementation.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import random


VISIBLE = 32
HIDDEN = 10
STATE_BITS = VISIBLE + HIDDEN
MASK32 = (1 << VISIBLE) - 1

X_ROWS = tuple(
    int(value, 16)
    for value in (
        "010,122,040,004,008,090,020,040,108,200,080,044,101,100,200,004,"
        "008,011,022,040,004,008,210,020,040,100,200,280,000,000,100,200"
    ).split(",")
)
D_ROWS = tuple(
    int(value, 16)
    for value in (
        "20040020001,10400004002,00800110008,00100220010,08200040020,"
        "04400080040,00401100080,0a000800400,20004002000,08008404000"
    ).split(",")
)


def xorshift32(value: int) -> int:
    value ^= value >> 13
    value ^= (value << 17) & MASK32
    value ^= value >> 5
    return value & MASK32


def transition_rows() -> tuple[int, ...]:
    return tuple(
        sum(((xorshift32(1 << source) >> target) & 1) << source for source in range(VISIBLE))
        for target in range(VISIBLE)
    )


def apply_row(row: int, matrix: tuple[int, ...]) -> int:
    result = 0
    while row:
        low = row & -row
        result ^= matrix[low.bit_length() - 1]
        row ^= low
    return result


def compose(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(apply_row(row, right) for row in left)


def apply_matrix(matrix: tuple[int, ...], value: int) -> int:
    return sum(((row & value).bit_count() & 1) << index for index, row in enumerate(matrix))


def gf2_rank(rows: tuple[int, ...]) -> int:
    basis: dict[int, int] = {}
    for original in rows:
        row = original
        while row:
            pivot = row.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = row
                break
            row ^= basis[pivot]
    return len(basis)


def build_matrices() -> tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]:
    a_rows = transition_rows()
    o_rows = tuple((1 << index) | (X_ROWS[index] << VISIBLE) for index in range(VISIBLE))
    top_rows = tuple(
        apply_row(a_rows[index], o_rows) ^ apply_row(X_ROWS[index], D_ROWS)
        for index in range(VISIBLE)
    )
    return a_rows, top_rows + D_ROWS, o_rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("nonstrong_frontier_certificate.json"),
    )
    args = parser.parse_args()

    a_rows, h_rows, o_rows = build_matrices()
    identity = tuple(1 << index for index in range(VISIBLE))
    if tuple(row & MASK32 for row in o_rows) != identity:
        raise AssertionError("O*S != I")
    if compose(o_rows, h_rows) != compose(a_rows, o_rows):
        raise AssertionError("O*H != A*O")

    # S=[I;0], so E=H*S is the low 32 columns of H.
    e_rows = tuple(row & MASK32 for row in h_rows)
    if compose(o_rows, e_rows) != a_rows:
        raise AssertionError("O*E != A")
    defect = tuple(
        left ^ right
        for left, right in zip(compose(h_rows, e_rows), compose(e_rows, a_rows))
    )
    if not any(defect):
        raise AssertionError("frontier unexpectedly satisfies the strong invariant")
    if any(compose(o_rows, defect)):
        raise AssertionError("strong-invariant defect is visible")

    seeds = [0, 1, 2, 0x12345678, MASK32]
    generator = random.Random(20260802)
    seeds.extend(generator.getrandbits(VISIBLE) for _ in range(64))
    for seed in seeds:
        state = apply_matrix(h_rows, seed)  # tick-zero load: H*S*seed
        natural = seed
        for _ in range(65):
            natural = xorshift32(natural)
            if apply_matrix(o_rows, state) != natural:
                raise AssertionError(f"visible sequence mismatch for seed {seed:08x}")
            state = apply_matrix(h_rows, state)

    targets = o_rows + h_rows
    weights = tuple(row.bit_count() for row in targets)
    bad_rows = []
    for index, (row, weight) in enumerate(zip(targets, weights)):
        if weight > 4:
            bad_rows.append(
                {
                    "branch": "O" if index < VISIBLE else "H",
                    "index": index if index < VISIBLE else index - VISIBLE,
                    "weight": weight,
                    "row_hex_42bit": f"{row:011x}",
                }
            )

    matrix_payload = {
        "A": [f"{row:08x}" for row in a_rows],
        "H": [f"{row:011x}" for row in h_rows],
        "O": [f"{row:011x}" for row in o_rows],
    }
    fingerprint = sha256(
        json.dumps(matrix_payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()
    result = {
        "schema": 1,
        "status": "invalid-frontier",
        "scope": "42-state unrestricted hidden-dynamics semiconjugacy O=[I32|X]",
        "matrix_fingerprint_sha256": fingerprint,
        "identities": {
            "O*S=I": True,
            "O*H=A*O": True,
            "O*E=A": True,
            "H*E=E*A": False,
            "O*(H*E+E*A)=0": True,
        },
        "nonstrong_defect": {
            "rank": gf2_rank(defect),
            "nonzero_rows": sum(bool(row) for row in defect),
            "rows_hex": [f"{row:08x}" for row in defect],
        },
        "verified_sequences": {"seeds": len(seeds), "outputs_per_seed": 65},
        "support": {
            "excess_over_4": sum(max(0, weight - 4) for weight in weights),
            "maximum_weight": max(weights),
            "total_weight": sum(weights),
            "bad_rows": bad_rows,
            "conclusion": "three weight-5 H rows strictly violate XOR2 depth<=2",
        },
        "target_accounting": {
            "delay_bits": 42,
            "selector_or": 32,
            "xor_budget": 61,
            "control_gate": 6,
            "target_gate": 431,
        },
        "X_rows_hex": [f"{row:03x}" for row in X_ROWS],
        "D_rows_hex_42bit": [f"{row:011x}" for row in D_ROWS],
        "E_rows_hex": [f"{row:08x}" for row in e_rows],
        "H_rows_hex_42bit": matrix_payload["H"],
        "O_rows_hex_42bit": matrix_payload["O"],
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps({"support": result["support"], "defect": result["nonstrong_defect"]}, indent=2))


if __name__ == "__main__":
    main()
