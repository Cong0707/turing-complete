"""Audit the fixed two-shear direct 65-cycle XOR model.

This is a research-only, low-memory checker.  It derives the exact matrices

    feedback = B*q xor D*seed
    output   = C*q xor A*seed

for T = R17*R13, then applies an arrival-time obstruction that holds for every
fan-in-two XOR DAG.  It neither imports save-writing code nor starts the game.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Callable, Sequence


N = 32
MASK = (1 << N) - 1
Q_ARRIVAL = 4
SEED_ARRIVAL = 0
XOR_DELAY = 2
DEADLINE = 9
XOR_BUDGET = 92
IDENTITY = tuple(1 << bit for bit in range(N))


def xorshift32(value: int) -> int:
    value ^= value >> 13
    value &= MASK
    value ^= (value << 17) & MASK
    value &= MASK
    value ^= value >> 5
    return value & MASK


def matrix_from_function(function: Callable[[int], int]) -> tuple[int, ...]:
    rows = [0] * N
    for source in range(N):
        output = function(1 << source)
        for target in range(N):
            if output >> target & 1:
                rows[target] |= 1 << source
    return tuple(rows)


def apply_row(row: int, matrix: Sequence[int]) -> int:
    result = 0
    while row:
        low = row & -row
        result ^= matrix[low.bit_length() - 1]
        row ^= low
    return result


def compose(left: Sequence[int], right: Sequence[int]) -> tuple[int, ...]:
    return tuple(apply_row(row, right) for row in left)


def add(left: Sequence[int], right: Sequence[int]) -> tuple[int, ...]:
    return tuple(a ^ b for a, b in zip(left, right))


def invert(matrix: Sequence[int]) -> tuple[int, ...]:
    rows = [row | ((1 << index) << N) for index, row in enumerate(matrix)]
    for column in range(N):
        pivot = next(
            (index for index in range(column, N) if rows[index] >> column & 1),
            None,
        )
        if pivot is None:
            raise ValueError("singular matrix")
        rows[column], rows[pivot] = rows[pivot], rows[column]
        for index in range(N):
            if index != column and rows[index] >> column & 1:
                rows[index] ^= rows[column]
    return tuple((row >> N) & MASK for row in rows)


def right_shear(distance: int) -> tuple[int, ...]:
    return matrix_from_function(lambda value: value ^ (value >> distance))


def apply_matrix(matrix: Sequence[int], value: int) -> int:
    return sum(((row & value).bit_count() & 1) << bit for bit, row in enumerate(matrix))


def derive() -> dict[str, tuple[int, ...]]:
    a = matrix_from_function(xorshift32)
    t = compose(right_shear(17), right_shear(13))
    inverse = invert(t)
    b = compose(t, compose(a, inverse))
    c = compose(a, inverse)
    d = compose(t, add(a, IDENTITY))
    return {"A": a, "T": t, "T_inverse": inverse, "B": b, "C": c, "D": d}


def verify_matrices(matrices: dict[str, tuple[int, ...]]) -> None:
    a = matrices["A"]
    t = matrices["T"]
    inverse = matrices["T_inverse"]
    b = matrices["B"]
    c = matrices["C"]
    d = matrices["D"]
    if compose(t, inverse) != IDENTITY:
        raise AssertionError("T*T_inverse != I")
    if compose(c, t) != a:
        raise AssertionError("C*T != A")
    if compose(t, c) != b:
        raise AssertionError("T*C != B")
    if d != compose(t, add(a, IDENTITY)):
        raise AssertionError("D != T*(A+I)")

    # Exhaustively cover all 256 byte-valued seeds for 65 emitted values.
    for seed in range(256):
        q = 0
        natural = seed
        for _ in range(65):
            feedback = apply_matrix(b, q) ^ apply_matrix(d, seed)
            visible = apply_matrix(c, q) ^ apply_matrix(a, seed)
            natural = xorshift32(natural)
            if visible != natural:
                raise AssertionError("direct output protocol mismatch")
            if feedback != apply_matrix(t, natural ^ seed):
                raise AssertionError("encoded feedback protocol mismatch")
            q = feedback


def matrix_histogram(matrix: Sequence[int]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in matrix:
        key = str(row.bit_count())
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items(), key=lambda item: int(item[0])))


def target_rows(matrices: dict[str, tuple[int, ...]]):
    for branch, q_name, seed_name in (
        ("feedback", "B", "D"),
        ("output", "C", "A"),
    ):
        for index, (q_mask, seed_mask) in enumerate(
            zip(matrices[q_name], matrices[seed_name])
        ):
            yield branch, index, q_mask, seed_mask


def obstruction(branch: str, index: int, q_mask: int, seed_mask: int) -> dict[str, object]:
    """Describe the q-weight-four timing contradiction.

    At a deadline-9 XOR output, both fanins arrive by 7.  Any fanin arriving by
    7 can contain at most two q leaves.  If it contains exactly two, its only
    possible q-sensitive construction is XOR(raw_q_i, raw_q_j), because a
    derived q-sensitive child cannot arrive before 6 and feeding it through
    another XOR would arrive at 8.  Thus both fanins needed for four q leaves
    have zero seed support, contradicting a nonzero target seed mask.
    """

    return {
        "branch": branch,
        "index": index,
        "q_mask": f"{q_mask:08x}",
        "q_weight": q_mask.bit_count(),
        "seed_mask": f"{seed_mask:08x}",
        "seed_weight": seed_mask.bit_count(),
        "deadline": DEADLINE,
        "minimum_arrival": 10,
        "reason": "q_weight_4_exhausts_both_depth_2_XOR_fanins_so_seed_support_must_be_zero",
    }


def existing_artifact_audit(root: Path) -> list[dict[str, object]]:
    paths = (
        root / ".research/rng_joint_sat/agent_joint/fixed-two-shear.json",
        root / ".research/rng_constant_seed_math/two_shear_direct.v",
        root / ".research/rng_constant_seed_math/two_shear_direct_mapped.v",
        root / ".research/rng_constant_seed_math/two_shear_direct_yosys.log",
        root / ".research/rng_cycle65_fixed/cycle65_fixed_certificate.json",
    )
    result = []
    for path in paths:
        data = path.read_bytes()
        result.append(
            {
                "path": str(path.relative_to(root)).replace("\\", "/"),
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        )
    return result


def make_certificate(root: Path) -> dict[str, object]:
    matrices = derive()
    verify_matrices(matrices)
    blockers = [
        obstruction(branch, index, q_mask, seed_mask)
        for branch, index, q_mask, seed_mask in target_rows(matrices)
        if q_mask.bit_count() == 4 and seed_mask != 0
    ]
    if not blockers:
        raise AssertionError("expected fixed two-shear timing obstructions")

    by_branch = {
        branch: sum(item["branch"] == branch for item in blockers)
        for branch in ("feedback", "output")
    }
    return {
        "schema": 1,
        "scope": "research-only fixed two-shear direct 64-target XOR2 timing audit",
        "model": {
            "targets": ["B*q xor D*seed", "C*q xor A*seed"],
            "T": "R17*R13",
            "q_arrival": Q_ARRIVAL,
            "seed_arrival": SEED_ARRIVAL,
            "xor2_delay": XOR_DELAY,
            "deadline": DEADLINE,
            "xor_budget": XOR_BUDGET,
        },
        "matrix_checks": {
            "T*T_inverse=I": True,
            "C*T=A": True,
            "T*C=B": True,
            "D=T*(A+I)": True,
            "protocol_seeds": 256,
            "outputs_per_seed": 65,
        },
        "row_weight_histograms": {
            name: matrix_histogram(matrices[name]) for name in ("B", "D", "C", "A")
        },
        "existing_artifacts": existing_artifact_audit(root),
        "existing_model_findings": [
            "fixed-two-shear.json contains only 32-bit T/B/C depth-two synthesis, not D/A or the direct 64-bit targets",
            "two_shear_direct_mapped.v is an unconstrained Yosys/ABC area mapping (83 XOR, 207 XNOR, 3 NOT), not an arrival-constrained <=92-XOR witness",
            "cycle65_fixed_certificate.json proves only phase-labeling failure on the fixed 61-XOR B/C DAG, whereas this certificate covers every XOR2 DAG for the direct targets",
        ],
        "timing_lemma": {
            "fanin_arrival_limit": DEADLINE - XOR_DELAY,
            "earliest_derived_q_arrival": Q_ARRIVAL + XOR_DELAY,
            "statement": "A deadline-9 target with q support weight 4 must have zero seed support in every fan-in-two XOR DAG.",
            "proof": [
                "The final XOR fanins must arrive by 7.",
                "A signal arriving by 7 contains at most two q leaves.",
                "A by-7 signal containing two q leaves must XOR two raw q leaves and therefore has zero seed support.",
                "Four q leaves require two such q-pair fanins, so the final target has zero seed support.",
            ],
        },
        "obstruction_count": len(blockers),
        "obstruction_count_by_branch": by_branch,
        "obstructions": blockers,
        "result": {
            "status": "unsat",
            "budget_dependency": "none",
            "best_xor_count": None,
            "verdict": "No direct fixed-two-shear XOR2 DAG meets delay <= 9, even with unlimited XOR gates; therefore none meets XOR <= 92.",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
        help="repository root (auto-detected by default)",
    )
    args = parser.parse_args()
    certificate = make_certificate(args.root.resolve())
    encoded = json.dumps(certificate, indent=2) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="ascii")
    print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
