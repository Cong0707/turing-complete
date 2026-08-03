"""Exact physical synthesis for a two-bit Sum/Sum/Cout hotspot.

Only the carry output may encode false as Z.  Both sum outputs must always be
actively driven because they are final Byte Adder outputs.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys
import threading
import time

from pysat.solvers import Solver


HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "byte_adder_boolean_superopt_agent/exact_adder_block_sat.py"
spec = importlib.util.spec_from_file_location("hotspot_zcarry_exact", SOURCE)
if spec is None or spec.loader is None:
    raise RuntimeError(SOURCE)
exact = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = exact
spec.loader.exec_module(exact)


def solve(args: argparse.Namespace) -> dict[str, object]:
    started = time.perf_counter()
    deadlines = tuple(args.deadlines)
    enc, state = exact.build(
        2,
        args.gate,
        max(deadlines),
        args.components,
        exact_switches=args.switches,
        exact_xors=args.xors,
        single_driver=False,
        cin_arrival=args.cin_arrival,
        output_deadlines=deadlines,
        dual_cin=False,
        dual_cout=False,
        allow_z_false=False,
        allow_z_false_outputs=(False, False, True),
        physical_nets=True,
    )
    timer = None
    model = None
    status = "unknown"
    with Solver(name=args.solver, bootstrap_with=enc.cnf) as solver:
        if args.timeout:
            timer = threading.Timer(args.timeout, solver.interrupt)
            timer.start()
        try:
            answer = solver.solve_limited(expect_interrupt=True)
        finally:
            if timer:
                timer.cancel()
        if answer is True:
            status = "sat"
            model = solver.get_model()
        elif answer is False:
            status = "unsat"

    payload: dict[str, object] = {
        "schema": "byte-adder-hotspot-zcarry-physical-exact-v1",
        "status": status,
        "bits": 2,
        "gate_bound": args.gate,
        "components": args.components,
        "cin_arrival": args.cin_arrival,
        "output_deadlines": list(deadlines),
        "exact_switches": args.switches,
        "exact_xors": args.xors,
        "solver": args.solver,
        "variables": enc.pool.top,
        "clauses": len(enc.cnf.clauses),
        "seconds": time.perf_counter() - started,
        "physical_nets": True,
        "allow_z_false": False,
        "allow_z_false_outputs": [False, False, True],
        "dual_cin": False,
        "dual_cout": False,
    }
    if model is not None:
        payload.update(exact.decode(args, state, model))
        payload["verification"] = exact.verify_payload(payload)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", type=int, required=True)
    parser.add_argument("--components", type=int, required=True)
    parser.add_argument("--cin-arrival", type=int, required=True)
    parser.add_argument(
        "--deadlines", type=int, nargs=3, required=True, metavar=("S0", "S1", "COUT")
    )
    parser.add_argument("--switches", type=int)
    parser.add_argument("--xors", type=int)
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = solve(args)
    print(
        json.dumps(
            {key: value for key, value in payload.items() if key != "network"},
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
