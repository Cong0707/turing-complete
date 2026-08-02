"""Low-memory SMT search for the 65-cycle mixed-arrival Kraft condition.

This is a research-only model.  It neither imports the save writer nor touches
the live game/save.  All matrices are over GF(2), stored as 32 little-endian
row bitmasks.

For q = T(x xor seed), write

    q' = B q + D seed
    y  = C q + A seed

where B=T A T^-1, C=A T^-1, and D=T(A+I).  Let K=A(A+I).  Since K commutes
with A, eliminating T gives the equivalent sparse-basis equations

    D A = B D
    C D = K.

K is invertible, so C*D=K itself implies that C and D are invertible.  The
second equation also avoids an explicit symbolic inverse.

At total delay <=9, q leaves (arrival 4) have XOR depth <=2 and seed leaves
(arrival 0) have XOR depth <=4.  Unfolding a binary XOR DAG therefore gives
the necessary per-target Kraft inequality

    4*w_q + w_seed <= 16.

Thus every B row has weight 1..3, its paired D row has weight at most
16-4*weight(B_i), and every C row has weight at most
floor((16-weight(A_i))/4), which is 2 or 3 for this xorshift matrix.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import time
from typing import Iterable, Sequence

import z3


BITS = 32
MASK = (1 << BITS) - 1
IDENTITY = tuple(1 << bit for bit in range(BITS))


def xorshift32(value: int) -> int:
    value ^= value >> 13
    value &= MASK
    value ^= (value << 17) & MASK
    value &= MASK
    value ^= value >> 5
    return value & MASK


def matrix_from_function() -> tuple[int, ...]:
    columns = tuple(xorshift32(1 << bit) for bit in range(BITS))
    return tuple(
        sum(((columns[source] >> output) & 1) << source for source in range(BITS))
        for output in range(BITS)
    )


def apply_row(row: int, matrix: Sequence[int]) -> int:
    result = 0
    while row:
        low = row & -row
        result ^= matrix[low.bit_length() - 1]
        row ^= low
    return result


def compose(left: Sequence[int], right: Sequence[int]) -> tuple[int, ...]:
    return tuple(apply_row(row, right) for row in left)


def invert(matrix: Sequence[int]) -> tuple[int, ...]:
    rows = [matrix[index] | ((1 << index) << BITS) for index in range(BITS)]
    for column in range(BITS):
        pivot = next(
            (index for index in range(column, BITS) if rows[index] >> column & 1),
            None,
        )
        if pivot is None:
            raise ValueError("singular matrix")
        rows[column], rows[pivot] = rows[pivot], rows[column]
        for index in range(BITS):
            if index != column and rows[index] >> column & 1:
                rows[index] ^= rows[column]
    return tuple((row >> BITS) & MASK for row in rows)


A = matrix_from_function()
APLUSI = tuple(row ^ IDENTITY[index] for index, row in enumerate(A))
K = compose(A, APLUSI)


def xor_many(items: Iterable[z3.BitVecRef]) -> z3.BitVecRef:
    result = z3.BitVecVal(0, BITS)
    for item in items:
        result = result ^ item
    return result


def popcount_bv(value: z3.BitVecRef) -> z3.ArithRef:
    return z3.Sum(
        [z3.If(z3.Extract(bit, bit, value) == 1, 1, 0) for bit in range(BITS)]
    )


def apply_constant_matrix(
    row: z3.BitVecRef, matrix: Sequence[int]
) -> z3.BitVecRef:
    return xor_many(
        z3.If(
            z3.Extract(bit, bit, row) == 1,
            z3.BitVecVal(matrix[bit], BITS),
            z3.BitVecVal(0, BITS),
        )
        for bit in range(BITS)
    )


def selected_row(index: z3.ArithRef, rows: Sequence[z3.BitVecRef]) -> z3.BitVecRef:
    """Return rows[index], with sentinel index 32 denoting the zero row."""

    result = z3.BitVecVal(0, BITS)
    for position in range(BITS - 1, -1, -1):
        result = z3.If(index == position, rows[position], result)
    return result


def add_canonical_support(
    solver: z3.Solver,
    prefix: str,
    row_index: int,
    maximum: int,
) -> tuple[list[z3.IntNumRef], z3.ArithRef]:
    """Create a sorted 1..maximum element subset of [0,32)."""

    slots = [z3.Int(f"{prefix}_{row_index}_{slot}") for slot in range(maximum)]
    solver.add(slots[0] >= 0, slots[0] < BITS)
    for slot in slots[1:]:
        solver.add(slot >= 0, slot <= BITS)
    for left, right in zip(slots, slots[1:]):
        # Real indices are strictly increasing; sentinel 32 repeats to the end.
        solver.add(z3.Or(z3.And(left < BITS, left < right), z3.And(left == BITS, right == BITS)))
    weight = z3.Sum([z3.If(slot < BITS, 1, 0) for slot in slots])
    return slots, weight


def matrix_digest(matrix: Sequence[int]) -> str:
    import hashlib

    return hashlib.sha256(
        b"".join(row.to_bytes(4, "little") for row in matrix)
    ).hexdigest()


def build_solver(
    *,
    enforce_feedback: bool,
    enforce_seed_caps: bool,
    sort_basis: bool,
) -> tuple[z3.Solver, list[z3.BitVecRef], list[list[z3.ArithRef]], list[list[z3.ArithRef]]]:
    solver = z3.Solver()
    rows = [z3.BitVec(f"d_{index}", BITS) for index in range(BITS)]

    # Relabelling the q coordinates permutes D's rows and preserves every
    # constraint.  Sorting removes the otherwise catastrophic 32! symmetry.
    if sort_basis:
        for left, right in zip(rows, rows[1:]):
            solver.add(z3.ULT(left, right))
    else:
        solver.add(z3.Distinct(*rows))
    for row in rows:
        solver.add(row != 0)

    b_slots: list[list[z3.ArithRef]] = []
    for index, row in enumerate(rows):
        slots, weight = add_canonical_support(solver, "b", index, 3)
        b_slots.append(slots)
        if enforce_feedback:
            solver.add(
                apply_constant_matrix(row, A)
                == xor_many(selected_row(slot, rows) for slot in slots)
            )
        if enforce_seed_caps:
            solver.add(popcount_bv(row) + 4 * weight <= 16)

    c_slots: list[list[z3.ArithRef]] = []
    for index, target in enumerate(K):
        maximum = (16 - A[index].bit_count()) // 4
        if maximum not in (2, 3):
            raise AssertionError(f"unexpected C row capacity {maximum}")
        slots, _weight = add_canonical_support(solver, "c", index, maximum)
        c_slots.append(slots)
        solver.add(
            xor_many(selected_row(slot, rows) for slot in slots)
            == z3.BitVecVal(target, BITS)
        )

    return solver, rows, b_slots, c_slots


def decode_support(model: z3.ModelRef, slots: Sequence[z3.ArithRef]) -> tuple[int, ...]:
    return tuple(
        value
        for slot in slots
        if (value := model.eval(slot, model_completion=True).as_long()) < BITS
    )


def verify_model(
    d: Sequence[int], b_supports: Sequence[Sequence[int]], c_supports: Sequence[Sequence[int]]
) -> dict[str, object]:
    if len(set(d)) != BITS or 0 in d:
        raise AssertionError("D rows are not 32 distinct nonzero vectors")
    c = tuple(sum(1 << source for source in support) for support in c_supports)
    b = tuple(sum(1 << source for source in support) for support in b_supports)
    if compose(c, d) != K:
        raise AssertionError("C*D != K")
    if compose(d, A) != compose(b, d):
        raise AssertionError("D*A != B*D")
    d_inverse = invert(d)
    if compose(d, d_inverse) != IDENTITY:
        raise AssertionError("D inverse check failed")
    t = compose(d, compose(invert(K), A))
    # K=A(A+I), hence the expression above equals D*(A+I)^-1.
    t_inverse = invert(t)
    reconstructed_b = compose(t, compose(A, t_inverse))
    reconstructed_c = compose(A, t_inverse)
    reconstructed_d = compose(t, APLUSI)
    if reconstructed_b != b or reconstructed_c != c or reconstructed_d != tuple(d):
        raise AssertionError("reconstructed T identities failed")

    feedback_loads = tuple(
        4 * len(b_supports[index]) + d[index].bit_count() for index in range(BITS)
    )
    output_loads = tuple(
        4 * len(c_supports[index]) + A[index].bit_count() for index in range(BITS)
    )
    return {
        "D": [f"0x{row:08x}" for row in d],
        "B": [f"0x{row:08x}" for row in b],
        "C": [f"0x{row:08x}" for row in c],
        "T": [f"0x{row:08x}" for row in t],
        "B_supports": [list(support) for support in b_supports],
        "C_supports": [list(support) for support in c_supports],
        "feedback_kraft_loads": list(feedback_loads),
        "output_kraft_loads": list(output_loads),
        "maximum_feedback_kraft_load": max(feedback_loads),
        "maximum_output_kraft_load": max(output_loads),
        "D_sha256": matrix_digest(d),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout-ms", type=int, default=300_000)
    parser.add_argument("--memory-mb", type=int, default=448)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--relax",
        choices=("none", "no-seed-caps", "output-only"),
        default="none",
        help="diagnostic relaxation; 'none' is the exact Kraft feasibility model",
    )
    parser.add_argument("--no-sort-basis", action="store_true")
    args = parser.parse_args()

    if args.timeout_ms <= 0:
        raise SystemExit("--timeout-ms must be positive")
    if not 64 <= args.memory_mb <= 512:
        raise SystemExit("--memory-mb must be in [64,512]")

    z3.set_param("memory_max_size", args.memory_mb)
    solver, rows, b_slots, c_slots = build_solver(
        enforce_feedback=args.relax != "output-only",
        enforce_seed_caps=args.relax == "none",
        sort_basis=not args.no_sort_basis,
    )
    solver.set(timeout=args.timeout_ms)

    started = time.monotonic()
    result = solver.check()
    elapsed = time.monotonic() - started
    document: dict[str, object] = {
        "schema": 1,
        "model": "65-cycle constant-seed arbitrary invertible T Kraft necessity",
        "equations": ["D*A=B*D", "C*D=A*(A+I)"],
        "relaxation": args.relax,
        "sort_basis": not args.no_sort_basis,
        "timeout_ms": args.timeout_ms,
        "memory_limit_mb": args.memory_mb,
        "result": str(result),
        "reason_unknown": solver.reason_unknown() if result == z3.unknown else None,
        "elapsed_seconds": elapsed,
        "A_sha256": matrix_digest(A),
        "K_sha256": matrix_digest(K),
        "A_row_weights": [row.bit_count() for row in A],
        "C_row_capacities": [(16 - row.bit_count()) // 4 for row in A],
        "statistics": {str(key): value for key, value in solver.statistics()},
    }
    if result == z3.sat:
        model = solver.model()
        d = tuple(model.eval(row, model_completion=True).as_long() for row in rows)
        b_supports = tuple(decode_support(model, slots) for slots in b_slots)
        c_supports = tuple(decode_support(model, slots) for slots in c_slots)
        if args.relax == "none":
            document["certificate"] = verify_model(d, b_supports, c_supports)
        else:
            document["relaxed_assignment"] = {
                "D": [f"0x{row:08x}" for row in d],
                "B_supports": [list(support) for support in b_supports],
                "C_supports": [list(support) for support in c_supports],
            }

    payload = json.dumps(document, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")


if __name__ == "__main__":
    main()
