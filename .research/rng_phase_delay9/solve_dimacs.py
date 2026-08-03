"""Solve an exported propositional RNG phase model with PySAT."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import time

from pysat.formula import CNF
from pysat.solvers import Solver


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("cnf", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--solver", default="cadical195")
    args = parser.parse_args()

    started = time.perf_counter()
    payload = args.cnf.read_bytes()
    formula = CNF(from_string=payload.decode("ascii"))
    loaded = time.perf_counter()
    with Solver(name=args.solver, bootstrap_with=formula.clauses) as solver:
        solved = solver.solve()
        model = solver.get_model() if solved else None
        stats = solver.accum_stats()
    finished = time.perf_counter()
    result = {
        "schema": 1,
        "cnf": str(args.cnf),
        "cnf_sha256": sha256(payload).hexdigest(),
        "variables": formula.nv,
        "clauses": len(formula.clauses),
        "solver": args.solver,
        "status": "sat" if solved else "unsat",
        "load_seconds": loaded - started,
        "solve_seconds": finished - loaded,
        "solver_stats": stats,
        "positive_model_literals": (
            [literal for literal in model if literal > 0] if model is not None else None
        ),
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "positive_model_literals"}))


if __name__ == "__main__":
    main()
