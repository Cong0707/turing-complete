"""Partition an exact local-repair radius by X/D Hamming weight."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time

from z3 import PbEq, SolverFor


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / ".research" / "rng_42state_direct" / "linear42_audit"))
import repair_smt as base  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--radius", type=int, required=True)
    parser.add_argument("--x-flips", type=int, required=True)
    parser.add_argument("--timeout-ms", type=int, default=60000)
    parser.add_argument("--max-memory-mb", type=int, default=640)
    parser.add_argument("--free-x-rows")
    parser.add_argument("--branch-x-row", type=int)
    parser.add_argument("--branch-x-changed", choices=("yes", "no"))
    parser.add_argument("--require-x-rows")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 0 <= args.x_flips <= args.radius:
        parser.error("x-flips must be in 0..radius")

    solver = SolverFor("QF_FD")
    solver.set(timeout=args.timeout_ms, max_memory=args.max_memory_mb)
    data = base.build_model(solver, base.HIDDEN if hasattr(base, "HIDDEN") else 10,
                            base.DEFAULT_X, base.DEFAULT_D)
    split = base.VISIBLE * 10
    if args.free_x_rows is not None:
        free_rows = {int(value) for value in args.free_x_rows.split(",") if value}
        for row in range(base.VISIBLE):
            if row not in free_rows:
                solver.add(*(literal == False for literal in data.hamming[row * 10:(row + 1) * 10]))
    if args.branch_x_row is not None:
        if args.branch_x_changed is None:
            parser.error("--branch-x-row requires --branch-x-changed")
        row_literals = data.hamming[args.branch_x_row * 10:(args.branch_x_row + 1) * 10]
        if args.branch_x_changed == "yes":
            from z3 import PbGe
            solver.add(PbGe([(literal, 1) for literal in row_literals], 1))
        else:
            solver.add(*(literal == False for literal in row_literals))
    if args.require_x_rows is not None:
        from z3 import PbGe
        required_rows = {int(value) for value in args.require_x_rows.split(",") if value}
        required_literals = [
            literal
            for row in required_rows
            for literal in data.hamming[row * 10:(row + 1) * 10]
        ]
        solver.add(PbGe([(literal, 1) for literal in required_literals], 1))
    solver.add(PbEq([(literal, 1) for literal in data.hamming[:split]], args.x_flips))
    solver.add(PbEq([(literal, 1) for literal in data.hamming[split:]],
                    args.radius - args.x_flips))

    started = time.monotonic()
    status = solver.check()
    elapsed = time.monotonic() - started
    result: dict[str, object] = {
        "scope": "exact QF_FD radius partition around excess-three frontier",
        "radius": args.radius,
        "x_flips": args.x_flips,
        "d_flips": args.radius - args.x_flips,
        "timeout_ms": args.timeout_ms,
        "max_memory_mb": args.max_memory_mb,
        "free_x_rows": args.free_x_rows,
        "branch_x_row": args.branch_x_row,
        "branch_x_changed": args.branch_x_changed,
        "require_x_rows": args.require_x_rows,
        "status": str(status),
        "seconds": elapsed,
    }
    if str(status) == "unknown":
        result["reason"] = solver.reason_unknown()
    elif str(status) == "sat":
        model = solver.model()
        x_rows = base.extract_rows(model, data.x)
        d_rows = base.extract_rows(model, data.d)
        result["X_rows_hex"] = [f"{row:03x}" for row in x_rows]
        result["D_rows_hex"] = [f"{row:011x}" for row in d_rows]
        result["verified"] = base.verify_candidate(x_rows, d_rows, 5000)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
