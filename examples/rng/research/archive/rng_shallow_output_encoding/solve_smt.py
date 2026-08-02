"""Exact offline SMT model for a shallow-output xorshift32 encoding.

The model searches matrices satisfying

    q = T*x
    C*T = A
    T*C = B

with row-weight(C)<=2 and row-weight(B)<=4.  The canonical dual-mode
initialization network also needs each tick-zero T row to fit through the
corresponding B output cone, hence weight(T_i)<=weight(B_i)<=4.

This file has no save/game imports and only reads an explicitly supplied
research JSONL file when --start is used.
"""

from __future__ import annotations

import argparse
from collections import Counter
import ctypes
import json
import os
from pathlib import Path
import random
import threading
import time
from typing import Sequence

import z3


N = 32
MASK = (1 << N) - 1
IDENTITY = tuple(1 << bit for bit in range(N))


def xorshift32(value: int) -> int:
    value ^= value >> 13
    value &= MASK
    value ^= (value << 17) & MASK
    value ^= value >> 5
    return value & MASK


def matrix_from_function(function) -> tuple[int, ...]:
    return tuple(
        sum(((function(1 << source) >> output) & 1) << source for source in range(N))
        for output in range(N)
    )


A = matrix_from_function(xorshift32)


def apply_row(row: int, matrix: Sequence[int]) -> int:
    result = 0
    while row:
        low = row & -row
        result ^= matrix[low.bit_length() - 1]
        row ^= low
    return result


def compose(left: Sequence[int], right: Sequence[int]) -> tuple[int, ...]:
    return tuple(apply_row(row, right) for row in left)


def apply_matrix(matrix: Sequence[int], value: int) -> int:
    return sum(((row & value).bit_count() & 1) << bit for bit, row in enumerate(matrix))


def load_last_C(path: Path) -> tuple[int, ...]:
    candidate = None
    with path.open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            if not line.strip():
                continue
            record = json.loads(line)
            if "C" in record:
                candidate = tuple(int(value, 16) for value in record["C"])
    if candidate is None or len(candidate) != N:
        raise ValueError(f"{path} has no complete C record")
    return candidate


def working_set_bytes() -> int:
    if os.name != "nt":
        return 0
    from ctypes import wintypes

    class Counters(ctypes.Structure):
        _fields_ = [
            ("cb", wintypes.DWORD),
            ("PageFaultCount", wintypes.DWORD),
            ("PeakWorkingSetSize", ctypes.c_size_t),
            ("WorkingSetSize", ctypes.c_size_t),
            ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
            ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
            ("PagefileUsage", ctypes.c_size_t),
            ("PeakPagefileUsage", ctypes.c_size_t),
        ]

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.GetCurrentProcess.restype = wintypes.HANDLE
    query = kernel32.K32GetProcessMemoryInfo
    query.argtypes = [wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD]
    query.restype = wintypes.BOOL
    counters = Counters()
    counters.cb = ctypes.sizeof(counters)
    if not query(kernel32.GetCurrentProcess(), ctypes.byref(counters), counters.cb):
        return 0
    return int(counters.WorkingSetSize)


def start_watchdog(limit_mb: int) -> tuple[threading.Event, list[int]]:
    stopped = threading.Event()
    peak = [working_set_bytes()]

    def watch() -> None:
        limit = limit_mb * 1024 * 1024
        while not stopped.wait(0.25):
            current = working_set_bytes()
            peak[0] = max(peak[0], current)
            if current > limit:
                os.write(
                    2,
                    (
                        f"memory_limit_exceeded working_set_mb={current / 1048576:.1f} "
                        f"limit_mb={limit_mb}\n"
                    ).encode("ascii"),
                )
                os._exit(75)

    threading.Thread(target=watch, daemon=True).start()
    return stopped, peak


def bit_bools(value: z3.BitVecRef) -> tuple[z3.BoolRef, ...]:
    return tuple(z3.Extract(bit, bit, value) == 1 for bit in range(N))


def symbolic_compose_row(
    left: z3.BitVecRef, right: Sequence[z3.BitVecRef]
) -> z3.BitVecRef:
    result = z3.BitVecVal(0, N)
    zero = z3.BitVecVal(0, N)
    for bit, row in enumerate(right):
        result = result ^ z3.If(z3.Extract(bit, bit, left) == 1, row, zero)
    return result


def histogram(rows: Sequence[int]) -> dict[str, int]:
    return {
        str(weight): count
        for weight, count in sorted(Counter(row.bit_count() for row in rows).items())
    }


def verify(
    T: Sequence[int],
    B: Sequence[int],
    C: Sequence[int],
    *,
    require_label_capacity: bool,
) -> dict[str, object]:
    if compose(C, T) != A:
        raise AssertionError("C*T != A")
    if compose(T, C) != tuple(B):
        raise AssertionError("T*C != B")
    if max(row.bit_count() for row in C) > 2:
        raise AssertionError("C is not shallow")
    if max(row.bit_count() for row in B) > 4:
        raise AssertionError("B exceeds depth-two support")
    if require_label_capacity and any(
        t.bit_count() > b.bit_count() for t, b in zip(T, B)
    ):
        raise AssertionError("tick-zero label capacity failed")

    seeds = [0, 1, 2, 0x12345678, MASK]
    seeds.extend(random.Random(0x5A1109).getrandbits(32) for _ in range(64))
    for seed in seeds:
        encoded = apply_matrix(T, seed)
        natural = seed
        for _ in range(65):
            natural = xorshift32(natural)
            if apply_matrix(C, encoded) != natural:
                raise AssertionError("visible output replay failed")
            encoded = apply_matrix(B, encoded)
    return {
        "matrix_identities": ["C*T=A", "T*C=B"],
        "row_weight_histograms": {
            "T": histogram(T),
            "B": histogram(B),
            "C": histogram(C),
        },
        "verified_seed_count": len(seeds),
        "verified_outputs_per_seed": 65,
    }


def solve(args: argparse.Namespace) -> dict[str, object]:
    stopped, peak = start_watchdog(args.memory_mb)
    started = time.perf_counter()
    solver = z3.Solver()
    solver.set(timeout=args.timeout_ms, max_memory=args.memory_mb - 32)

    C = tuple(z3.BitVec(f"C_{row}", N) for row in range(N))
    T = tuple(z3.BitVec(f"T_{row}", N) for row in range(N))
    B = tuple(z3.BitVec(f"B_{row}", N) for row in range(N))
    c_bits = tuple(bit_bools(row) for row in C)
    t_bits = tuple(bit_bools(row) for row in T)
    b_bits = tuple(bit_bools(row) for row in B)

    for row in range(N):
        solver.add(z3.PbGe([(bit, 1) for bit in c_bits[row]], 1))
        solver.add(z3.PbLe([(bit, 1) for bit in c_bits[row]], 2))
        solver.add(z3.PbLe([(bit, 1) for bit in t_bits[row]], 4))
        solver.add(z3.PbGe([(bit, 1) for bit in b_bits[row]], 1))
        solver.add(z3.PbLe([(bit, 1) for bit in b_bits[row]], 4))
        if not args.relax_label_capacity:
            for bound in range(1, 4):
                solver.add(
                    z3.Implies(
                        z3.PbLe([(bit, 1) for bit in b_bits[row]], bound),
                        z3.PbLe([(bit, 1) for bit in t_bits[row]], bound),
                    )
                )

        solver.add(symbolic_compose_row(C[row], T) == z3.BitVecVal(A[row], N))
        solver.add(symbolic_compose_row(T[row], C) == B[row])

    start = load_last_C(args.start) if args.start else None
    if start is not None and args.radius is not None:
        solver.add(
            z3.PbLe(
                [(C[row] != z3.BitVecVal(start[row], N), 1) for row in range(N)],
                args.radius,
            )
        )

    build_seconds = time.perf_counter() - started
    result = solver.check()
    solve_seconds = time.perf_counter() - started - build_seconds
    stopped.set()
    peak[0] = max(peak[0], working_set_bytes())
    report: dict[str, object] = {
        "status": str(result),
        "scope": "exact shallow C / depth-two B / canonical tick-zero capacity",
        "label_capacity_enabled": not args.relax_label_capacity,
        "timeout_ms": args.timeout_ms,
        "memory_limit_mb": args.memory_mb,
        "peak_working_set_mb": peak[0] / 1048576,
        "build_seconds": build_seconds,
        "solve_seconds": solve_seconds,
        "start": None if args.start is None else str(args.start),
        "radius": args.radius,
        "reason_unknown": solver.reason_unknown() if result == z3.unknown else None,
        "statistics": str(solver.statistics()),
    }
    if result != z3.sat:
        return report

    model = solver.model()
    c_rows = tuple(model.eval(row, model_completion=True).as_long() for row in C)
    t_rows = tuple(model.eval(row, model_completion=True).as_long() for row in T)
    b_rows = tuple(model.eval(row, model_completion=True).as_long() for row in B)
    report["candidate"] = {
        "C": [f"{row:08x}" for row in c_rows],
        "T": [f"{row:08x}" for row in t_rows],
        "B": [f"{row:08x}" for row in b_rows],
        "verification": verify(
            t_rows,
            b_rows,
            c_rows,
            require_label_capacity=not args.relax_label_capacity,
        ),
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=Path)
    parser.add_argument("--radius", type=int)
    parser.add_argument("--timeout-ms", type=int, default=120_000)
    parser.add_argument("--memory-mb", type=int, default=680)
    parser.add_argument("--relax-label-capacity", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = solve(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "candidate"}, indent=2))
    return 0 if result["status"] in {"sat", "unsat"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
