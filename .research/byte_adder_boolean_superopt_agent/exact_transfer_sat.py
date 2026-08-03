"""Exact synthesis of 2--4 bit carry-transfer interfaces.

For an n-bit interval, outputs are ``U=f(0)`` and ``V=f(1)``.  The primitive
CNF model and independent value/Z replay come from ``exact_adder_block_sat``.
False internal rails may be represented by Z; true rows must be actively
driven, and every multi-driver bus remains conflict-free.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

import exact_adder_block_sat as exact


def transfer_targets(bits: int, dual_cout: bool = False) -> tuple[int, tuple[int, ...]]:
    if dual_cout:
        raise ValueError("transfer synthesis has exactly two U/V outputs")
    inputs = 2 * bits
    assignments = 1 << inputs
    word_mask = (1 << bits) - 1
    u = 0
    v = 0
    for case in range(assignments):
        a = case & word_mask
        b = (case >> bits) & word_mask
        u |= (((a + b) >> bits) & 1) << case
        v |= (((a + b + 1) >> bits) & 1) << case
    return inputs, (u, v)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bits", type=int, choices=(2, 3, 4), required=True)
    parser.add_argument("--gate-bound", type=int, required=True)
    parser.add_argument("--max-delay", type=int, required=True)
    parser.add_argument("--components", type=int, required=True)
    parser.add_argument("--switches", type=int)
    parser.add_argument("--xors", type=int)
    parser.add_argument("--single-driver", action="store_true")
    parser.add_argument("--fully-driven", action="store_true")
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--conflicts", type=int)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    solve_args = argparse.Namespace(
        bits=args.bits,
        gate_bound=args.gate_bound,
        max_delay=args.max_delay,
        components=args.components,
        switches=args.switches,
        xors=args.xors,
        single_driver=args.single_driver,
        cin_arrival=0,
        sum_deadline=None,
        carry_deadline=None,
        carry_bar_deadline=None,
        dual_cin=False,
        dual_cout=False,
        allow_z_false=not args.fully_driven,
        abstract_buses=False,
        solver=args.solver,
        timeout=args.timeout,
        conflicts=args.conflicts,
    )

    original_targets = exact.adder_targets
    exact.adder_targets = transfer_targets
    try:
        payload = exact.solve(solve_args)
    finally:
        exact.adder_targets = original_targets

    payload["schema"] = "exact-carry-transfer-switch-cnf-v1"
    payload["interface"] = {
        "inputs": "a[0..n-1], b[0..n-1]",
        "outputs": ["U=f(0)", "V=f(1)"],
        "invariant": "U <= V",
        "false_rail": "driven 0" if args.fully_driven else "driven 0 or Z",
    }
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(encoded)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"sha256={sha256(encoded).hexdigest()}")
    return 0 if payload["status"] != "unknown" else 2


if __name__ == "__main__":
    raise SystemExit(main())
