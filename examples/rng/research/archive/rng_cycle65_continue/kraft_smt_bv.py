"""Pure-QF_BV version of the arbitrary-T Kraft feasibility search.

See ``kraft_smt_exact.py`` for the derivation.  This version uses 6-bit
selectors and guarded pseudo-Boolean cardinalities, avoiding the mixed
integer/bit-vector theory combination of the reference encoder.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import time
from typing import Sequence

import z3

import kraft_smt_exact as base


BITS = base.BITS
INDEX_BITS = 6
SENTINEL = BITS


def index_value(value: int) -> z3.BitVecNumRef:
    return z3.BitVecVal(value, INDEX_BITS)


def selected_row(
    index: z3.BitVecRef, rows: Sequence[z3.BitVecRef]
) -> z3.BitVecRef:
    result = z3.BitVecVal(0, BITS)
    for position in range(BITS - 1, -1, -1):
        result = z3.If(index == index_value(position), rows[position], result)
    return result


def make_support(
    solver: z3.Solver,
    prefix: str,
    row_index: int,
    maximum: int,
) -> list[z3.BitVecRef]:
    slots = [
        z3.BitVec(f"{prefix}_{row_index}_{slot}", INDEX_BITS)
        for slot in range(maximum)
    ]
    solver.add(z3.ULT(slots[0], index_value(BITS)))
    for slot in slots[1:]:
        solver.add(z3.ULE(slot, index_value(SENTINEL)))
    for left, right in zip(slots, slots[1:]):
        solver.add(
            z3.Or(
                z3.And(
                    z3.ULT(left, index_value(BITS)),
                    z3.ULT(left, right),
                ),
                z3.And(
                    left == index_value(SENTINEL),
                    right == index_value(SENTINEL),
                ),
            )
        )
    return slots


def bits_of(row: z3.BitVecRef) -> list[z3.BoolRef]:
    return [z3.Extract(bit, bit, row) == 1 for bit in range(BITS)]


def add_seed_cap(
    solver: z3.Solver, row: z3.BitVecRef, slots: Sequence[z3.BitVecRef]
) -> None:
    if len(slots) != 3:
        raise AssertionError("B support must have three slots")
    real1 = z3.ULT(slots[1], index_value(BITS))
    real2 = z3.ULT(slots[2], index_value(BITS))
    bits = bits_of(row)
    solver.add(z3.Implies(z3.Not(real1), z3.PbLe([(bit, 1) for bit in bits], 12)))
    solver.add(
        z3.Implies(
            z3.And(real1, z3.Not(real2)),
            z3.PbLe([(bit, 1) for bit in bits], 8),
        )
    )
    solver.add(z3.Implies(real2, z3.PbLe([(bit, 1) for bit in bits], 4)))


def decode_support(
    model: z3.ModelRef, slots: Sequence[z3.BitVecRef]
) -> tuple[int, ...]:
    return tuple(
        value
        for slot in slots
        if (value := model.eval(slot, model_completion=True).as_long()) < BITS
    )


def build_solver(
    *, relaxation: str, sort_basis: bool, diagonal_c: bool
) -> tuple[
    z3.Solver,
    list[z3.BitVecRef],
    list[list[z3.BitVecRef]],
    list[list[z3.BitVecRef]],
]:
    solver = z3.SolverFor("QF_BV")
    rows = [z3.BitVec(f"d_{index}", BITS) for index in range(BITS)]
    if sort_basis and diagonal_c:
        raise ValueError("sort_basis and diagonal_c are alternative symmetry breaks")
    if sort_basis:
        for left, right in zip(rows, rows[1:]):
            solver.add(z3.ULT(left, right))
    else:
        solver.add(z3.Distinct(*rows))
    for row in rows:
        solver.add(row != 0)

    b_slots: list[list[z3.BitVecRef]] = []
    if relaxation != "output-only":
        for index, row in enumerate(rows):
            slots = make_support(solver, "b", index, 3)
            b_slots.append(slots)
            solver.add(
                base.apply_constant_matrix(row, base.A)
                == base.xor_many(selected_row(slot, rows) for slot in slots)
            )
            if relaxation == "none":
                add_seed_cap(solver, row, slots)

    c_slots: list[list[z3.BitVecRef]] = []
    for index, target in enumerate(base.K):
        maximum = (16 - base.A[index].bit_count()) // 4
        slots = make_support(solver, "c", index, maximum)
        c_slots.append(slots)
        if diagonal_c:
            # C is invertible because C*D=K is invertible.  Choose any perfect
            # matching in C's support and permute the internal q coordinates
            # so that matching is diagonal.  This preserves every row weight
            # and the paired feedback Kraft loads, hence is WLOG.
            solver.add(z3.Or(*(slot == index_value(index) for slot in slots)))
        solver.add(
            base.xor_many(selected_row(slot, rows) for slot in slots)
            == z3.BitVecVal(target, BITS)
        )
    return solver, rows, b_slots, c_slots


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout-ms", type=int, default=300_000)
    parser.add_argument("--memory-mb", type=int, default=448)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--relax",
        choices=("none", "no-seed-caps", "output-only"),
        default="none",
    )
    parser.add_argument("--no-sort-basis", action="store_true")
    parser.add_argument(
        "--diagonal-c",
        action="store_true",
        help="WLOG fix a perfect matching of C to its diagonal",
    )
    args = parser.parse_args()

    if args.timeout_ms <= 0:
        raise SystemExit("--timeout-ms must be positive")
    if not 64 <= args.memory_mb <= 512:
        raise SystemExit("--memory-mb must be in [64,512]")
    z3.set_param("memory_max_size", args.memory_mb)

    sort_basis = not args.no_sort_basis and not args.diagonal_c
    solver, rows, b_slots, c_slots = build_solver(
        relaxation=args.relax,
        sort_basis=sort_basis,
        diagonal_c=args.diagonal_c,
    )
    solver.set(timeout=args.timeout_ms)
    started = time.monotonic()
    try:
        result = solver.check()
        exception = None
    except z3.Z3Exception as error:
        result = z3.unknown
        exception = str(error)
    elapsed = time.monotonic() - started

    document: dict[str, object] = {
        "schema": 1,
        "encoder": "pure QF_BV selectors",
        "model": "65-cycle constant-seed arbitrary invertible T Kraft necessity",
        "equations": ["D*A=B*D", "C*D=A*(A+I)"],
        "relaxation": args.relax,
        "sort_basis": sort_basis,
        "diagonal_c": args.diagonal_c,
        "timeout_ms": args.timeout_ms,
        "memory_limit_mb": args.memory_mb,
        "result": str(result),
        "reason_unknown": (
            exception
            if exception is not None
            else solver.reason_unknown() if result == z3.unknown else None
        ),
        "elapsed_seconds": elapsed,
        "A_sha256": base.matrix_digest(base.A),
        "K_sha256": base.matrix_digest(base.K),
        "A_row_weights": [row.bit_count() for row in base.A],
        "C_row_capacities": [
            (16 - row.bit_count()) // 4 for row in base.A
        ],
        "statistics": {str(key): value for key, value in solver.statistics()},
    }
    if result == z3.sat:
        model = solver.model()
        d = tuple(model.eval(row, model_completion=True).as_long() for row in rows)
        c_supports = tuple(decode_support(model, slots) for slots in c_slots)
        b_supports = tuple(decode_support(model, slots) for slots in b_slots)
        if args.relax == "none":
            document["certificate"] = base.verify_model(d, b_supports, c_supports)
        else:
            relaxed: dict[str, object] = {
                "D": [f"0x{row:08x}" for row in d],
                "C_supports": [list(support) for support in c_supports],
            }
            if b_supports:
                relaxed["B_supports"] = [list(support) for support in b_supports]
            document["relaxed_assignment"] = relaxed

    payload = json.dumps(document, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")


if __name__ == "__main__":
    main()
