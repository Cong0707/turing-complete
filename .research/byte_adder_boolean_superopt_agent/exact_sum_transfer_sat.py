"""Exact physical synthesis of Sum plus U/V carry-transfer block outputs."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

import exact_adder_block_sat as exact


def sum_transfer_targets(bits: int, dual_cout: bool = False) -> tuple[int, tuple[int, ...]]:
    if dual_cout:
        raise ValueError("sum-transfer wrapper does not use dual_cout")
    inputs = 2 * bits + 1
    assignments = 1 << inputs
    word_mask = (1 << bits) - 1
    targets = [0] * (bits + 2)
    for case in range(assignments):
        a = case & word_mask
        b = (case >> bits) & word_mask
        cin = (case >> (2 * bits)) & 1
        total = a + b + cin
        for output in range(bits):
            targets[output] |= ((total >> output) & 1) << case
        targets[bits] |= (((a + b) >> bits) & 1) << case
        targets[bits + 1] |= (((a + b + 1) >> bits) & 1) << case
    return inputs, tuple(targets)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bits", type=int, choices=(1, 2, 3, 4), required=True)
    parser.add_argument("--gate-bound", type=int, required=True)
    parser.add_argument("--max-delay", type=int, required=True)
    parser.add_argument("--components", type=int, required=True)
    parser.add_argument("--switches", type=int)
    parser.add_argument("--xors", type=int)
    parser.add_argument("--single-driver", action="store_true")
    parser.add_argument("--cin-arrival", type=int, default=0)
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
        cin_arrival=args.cin_arrival,
        sum_deadline=None,
        carry_deadline=None,
        carry_bar_deadline=None,
        dual_cin=False,
        dual_cout=False,
        allow_z_false=False,
        allow_z_false_outputs=tuple([False] * args.bits + [True, True]),
        abstract_buses=False,
        solver=args.solver,
        timeout=args.timeout,
        conflicts=args.conflicts,
    )

    original_targets = exact.adder_targets
    exact.adder_targets = sum_transfer_targets
    try:
        payload = exact.solve(solve_args)
    finally:
        exact.adder_targets = original_targets

    payload["schema"] = "exact-sum-carry-transfer-switch-cnf-v1"
    payload["interface"] = {
        "inputs": "a[0..n-1], b[0..n-1], cin",
        "outputs": [
            *[f"sum{bit}" for bit in range(args.bits)],
            "U=f(0)",
            "V=f(1)",
        ],
        "drive_policy": "Sum always driven; false U/V may be Z",
        "physical_nets": "overlap implies identical complete driver set",
    }
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(encoded)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"sha256={sha256(encoded).hexdigest()}")
    return 0 if payload["status"] != "unknown" else 2


if __name__ == "__main__":
    raise SystemExit(main())
