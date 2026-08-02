"""Find a sparse independent-init basis for the delay-9 RNG architecture.

This deliberately omits pair-cover variables.  It first asks the smaller,
decisive structural question whether an invertible 32-bit T exists with
row weight at most two while both C=A*T^-1 and B=T*A*T^-1 have row weight at
most four.  State-coordinate permutations are quotient out by sorting T rows.
The script is research-only and never imports save/game modules.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import time

from z3 import And, BitVec, BoolRef, Extract, If, Not, Or, PbEq, PbLe, Solver, ULT, Xor, sat, unsat


N = 32
MASK = (1 << N) - 1


def xorshift32(value: int) -> int:
    value ^= value >> 13
    value &= MASK
    value ^= (value << 17) & MASK
    value &= MASK
    value ^= value >> 5
    return value & MASK


def matrix_from_function(function) -> tuple[int, ...]:
    return tuple(
        sum(((function(1 << source) >> target) & 1) << source for source in range(N))
        for target in range(N)
    )


A = matrix_from_function(xorshift32)


def bit(row, column: int):
    return Extract(column, column, row) == 1


def parity(terms: list[BoolRef]):
    result = terms[0]
    for term in terms[1:]:
        result = Xor(result, term)
    return result


def apply_row(row: int, matrix: tuple[int, ...]) -> int:
    result = 0
    while row:
        low = row & -row
        result ^= matrix[low.bit_length() - 1]
        row ^= low
    return result


def compose(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(apply_row(row, right) for row in left)


def solve(timeout_ms: int, memory_mb: int, max_t_xor: int, output: Path | None) -> int:
    solver = Solver()
    solver.set(timeout=timeout_ms, max_memory=memory_mb)
    T = [BitVec(f"T_{row}", N) for row in range(N)]
    B = [BitVec(f"B_{row}", N) for row in range(N)]
    C = [BitVec(f"C_{row}", N) for row in range(N)]

    t_bits = [[bit(T[row], column) for column in range(N)] for row in range(N)]
    b_bits = [[bit(B[row], column) for column in range(N)] for row in range(N)]
    c_bits = [[bit(C[row], column) for column in range(N)] for row in range(N)]
    t_is_pair = []
    for row in range(N):
        solver.add(PbLe([(value, 1) for value in t_bits[row]], 2))
        solver.add(Or(*t_bits[row]))
        pair = And(PbLe([(value, 1) for value in t_bits[row]], 2),
                   Not(PbLe([(value, 1) for value in t_bits[row]], 1)))
        t_is_pair.append(pair)
        solver.add(PbLe([(value, 1) for value in b_bits[row]], 4))
        solver.add(PbLe([(value, 1) for value in c_bits[row]], 4))

    if max_t_xor >= 0:
        solver.add(PbLe([(value, 1) for value in t_is_pair], max_t_xor))

    # Any feasible solution can be renamed in q-space so its distinct T rows
    # are increasing.  This removes the full 32! row-permutation symmetry.
    for row in range(N - 1):
        solver.add(ULT(T[row], T[row + 1]))

    # C*T=A and T*C=B.  Since A is invertible, C*T=A also proves T and C
    # invertible; no determinant or explicit inverse is needed.
    for row in range(N):
        for column in range(N):
            ct = parity([And(c_bits[row][k], t_bits[k][column]) for k in range(N)])
            solver.add(ct if A[row] >> column & 1 else Not(ct))
            tc = parity([And(t_bits[row][k], c_bits[k][column]) for k in range(N)])
            solver.add(b_bits[row][column] == tc)

    started = time.perf_counter()
    status = solver.check()
    elapsed = time.perf_counter() - started
    result: dict[str, object] = {
        "scope": "all sorted invertible T with row weight <=2; B/C row weight <=4",
        "status": str(status),
        "timeout_ms": timeout_ms,
        "memory_mb": memory_mb,
        "max_t_xor": max_t_xor,
        "elapsed_seconds": round(elapsed, 6),
        "reason_unknown": solver.reason_unknown() if status not in (sat, unsat) else "",
    }
    if status == sat:
        model = solver.model()
        matrices = {
            name: tuple(model.eval(value, model_completion=True).as_long() for value in values)
            for name, values in (("T", T), ("B", B), ("C", C))
        }
        if compose(matrices["C"], matrices["T"]) != A:
            raise AssertionError("C*T != A")
        if compose(matrices["T"], matrices["C"]) != matrices["B"]:
            raise AssertionError("T*C != B")
        if max(row.bit_count() for row in matrices["T"]) > 2:
            raise AssertionError("T exceeds row weight two")
        if max(row.bit_count() for row in matrices["B"] + matrices["C"]) > 4:
            raise AssertionError("B/C exceeds row weight four")
        result.update(
            {
                name: [f"{row:08x}" for row in matrix]
                for name, matrix in matrices.items()
            }
        )
        result["t_xor"] = sum(row.bit_count() == 2 for row in matrices["T"])
        result["B_weights"] = [row.bit_count() for row in matrices["B"]]
        result["C_weights"] = [row.bit_count() for row in matrices["C"]]

    encoded = json.dumps(result, indent=2) + "\n"
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0 if status in (sat, unsat) else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout-ms", type=int, default=300_000)
    parser.add_argument("--memory-mb", type=int, default=480)
    parser.add_argument("--max-t-xor", type=int, default=24)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    return solve(args.timeout_ms, args.memory_mb, args.max_t_xor, args.output)


if __name__ == "__main__":
    raise SystemExit(main())
