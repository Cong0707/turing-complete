#!/usr/bin/env python3
"""Bound four-input parity with implicit, over-relaxed tri-state buses.

Every gate input and the final output may merge an arbitrary conflict-free
subset of earlier drivers at zero cost.  This removes explicit BUS nodes and
their topological permutations.  It also permits one driver to appear in
different logical buses, which is an electrical relaxation: UNSAT remains a
valid lower bound, while any SAT witness needs a unique-net audit.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import time

import z3


KINDS = ("NOP", "NOT", "AND", "OR", "NAND", "NOR", "XOR", "SWITCH")
NOP, NOT, AND, OR, NAND, NOR, XOR, SWITCH = range(len(KINDS))
COST = (0, 1, 1, 1, 1, 1, 3, 2)
DELAY = (0, 1, 1, 1, 1, 1, 2, 1)
COMMUTATIVE = frozenset((AND, OR, NAND, NOR, XOR))


def variable_table(index: int, variables: int) -> int:
    return sum(
        ((assignment >> index) & 1) << assignment
        for assignment in range(1 << variables)
    )


def max_expr(left: z3.ArithRef, right: z3.ArithRef) -> z3.ArithRef:
    return z3.If(left >= right, left, right)


def merge_bus(
    solver: z3.Solver,
    prefix: str,
    values: list[z3.BitVecRef],
    drivens: list[z3.BitVecRef],
    depths: list[z3.ArithRef],
    width: int,
) -> tuple[
    z3.BitVecRef,
    z3.BitVecRef,
    z3.ArithRef,
    z3.ArithRef,
    list[z3.BoolRef],
]:
    uses = [z3.Bool(f"{prefix}_use_{index}") for index in range(len(values))]
    zero = z3.BitVecVal(0, width)
    full = z3.BitVecVal((1 << width) - 1, width)
    ones = zero
    zeros = zero
    depth: z3.ArithRef = z3.IntVal(0)
    mask: z3.ArithRef = z3.IntVal(0)
    for index, (use, value, driven, source_depth) in enumerate(
        zip(uses, values, drivens, depths, strict=True)
    ):
        ones = ones | z3.If(use, driven & value, zero)
        zeros = zeros | z3.If(use, driven & (full ^ value), zero)
        depth = max_expr(depth, z3.If(use, source_depth, 0))
        mask = mask + z3.If(use, 1 << index, 0)
    solver.add((ones & zeros) == zero)
    return ones, ones | zeros, depth, mask, uses


def solve(
    gate_bound: int,
    max_delay: int,
    slots: int,
    timeout_ms: int,
    memory_mb: int,
) -> dict[str, object]:
    variables = 4
    assignments = 1 << variables
    truth_width = assignments
    all_assignments = (1 << truth_width) - 1
    zero = z3.BitVecVal(0, truth_width)
    full = z3.BitVecVal(all_assignments, truth_width)
    source_values = [
        z3.BitVecVal(variable_table(index, variables), truth_width)
        for index in range(variables)
    ]
    source_values.extend((zero, full))
    values = list(source_values)
    drivens = [full for _ in values]
    depths: list[z3.ArithRef] = [z3.IntVal(0) for _ in values]
    source_count = len(values)

    solver = z3.Solver()
    solver.set(timeout=timeout_ms, max_memory=memory_mb)
    kinds: list[z3.IntNumRef] = []
    costs: list[z3.ArithRef] = []
    gate_depths: list[z3.ArithRef] = []
    left_uses: list[list[z3.BoolRef]] = []
    right_uses: list[list[z3.BoolRef]] = []
    started = time.perf_counter()

    for slot in range(slots):
        kind = z3.Int(f"kind_{slot}")
        solver.add(kind >= NOP, kind <= SWITCH)
        if slot:
            solver.add(z3.Implies(kinds[-1] == NOP, kind == NOP))

        lv, _ldrive, ldepth, lmask, luse = merge_bus(
            solver, f"g{slot}_left", values, drivens, depths, truth_width
        )
        rv, _rdrive, rdepth, rmask, ruse = merge_bus(
            solver, f"g{slot}_right", values, drivens, depths, truth_width
        )
        solver.add(z3.Implies(kind == NOP, z3.And(lmask == 0, rmask == 0)))
        solver.add(z3.Implies(kind == NOT, rmask == lmask))
        solver.add(
            z3.Implies(
                z3.Or(*(kind == candidate for candidate in COMMUTATIVE)),
                lmask < rmask,
            )
        )
        for earlier_slot in range(slot):
            signal_index = source_count + earlier_slot
            solver.add(
                z3.Implies(
                    z3.Or(luse[signal_index], ruse[signal_index]),
                    kinds[earlier_slot] != NOP,
                )
            )

        value = z3.If(
            kind == NOP,
            zero,
            z3.If(
                kind == NOT,
                ~lv,
                z3.If(
                    kind == AND,
                    lv & rv,
                    z3.If(
                        kind == OR,
                        lv | rv,
                        z3.If(
                            kind == NAND,
                            ~(lv & rv),
                            z3.If(
                                kind == NOR,
                                ~(lv | rv),
                                z3.If(kind == XOR, lv ^ rv, rv),
                            ),
                        ),
                    ),
                ),
            ),
        )
        driven = z3.If(kind == NOP, zero, z3.If(kind == SWITCH, lv, full))
        input_depth = z3.If(
            kind == NOP,
            0,
            z3.If(kind == NOT, ldepth, max_expr(ldepth, rdepth)),
        )
        delay = z3.Sum(
            [z3.If(kind == candidate, DELAY[candidate], 0) for candidate in range(len(KINDS))]
        )
        depth = input_depth + delay
        solver.add(z3.Implies(kind != NOP, depth <= max_delay))
        cost = z3.Sum(
            [z3.If(kind == candidate, COST[candidate], 0) for candidate in range(len(KINDS))]
        )

        kinds.append(kind)
        costs.append(cost)
        gate_depths.append(depth)
        left_uses.append(luse)
        right_uses.append(ruse)
        values.append(value)
        drivens.append(driven)
        depths.append(depth)

    solver.add(z3.Sum(costs) <= gate_bound)
    out_value, out_driven, out_depth, _out_mask, output_uses = merge_bus(
        solver, "output", values, drivens, depths, truth_width
    )
    target = sum(
        (assignment.bit_count() & 1) << assignment
        for assignment in range(assignments)
    )
    solver.add(out_value == z3.BitVecVal(target, truth_width))
    solver.add(out_depth <= max_delay)
    solver.add(z3.Or(*output_uses))

    for slot, kind in enumerate(kinds):
        signal_index = source_count + slot
        consumers = [output_uses[signal_index]]
        for later_slot in range(slot + 1, slots):
            consumers.extend(
                (
                    left_uses[later_slot][signal_index],
                    right_uses[later_slot][signal_index],
                )
            )
        solver.add(z3.Implies(kind != NOP, z3.Or(*consumers)))

    status = solver.check()
    payload: dict[str, object] = {
        "schema": 1,
        "model": (
            "four-input parity; arbitrary reviewed scalar gates and implicit "
            "conflict-free buses at every input/output"
        ),
        "scope_relaxation": (
            "a driver may appear in multiple logical buses; UNSAT is safe, "
            "SAT requires a unique electrical-net audit"
        ),
        "status": str(status),
        "gate_bound": gate_bound,
        "max_delay": max_delay,
        "slots": slots,
        "timeout_ms": timeout_ms,
        "memory_mb": memory_mb,
        "solve_seconds": time.perf_counter() - started,
        "library": {
            name: {"gate": COST[index], "delay": DELAY[index]}
            for index, name in enumerate(KINDS)
        },
        "target_value": f"{target:04x}",
    }
    if status == z3.unknown:
        payload["reason_unknown"] = solver.reason_unknown()
    if status == z3.sat:
        model = solver.model()

        def selected(uses: list[z3.BoolRef]) -> list[int]:
            return [
                index
                for index, use in enumerate(uses)
                if z3.is_true(model.eval(use, model_completion=True))
            ]

        network = []
        for slot, kind in enumerate(kinds):
            kind_value = model.eval(kind, model_completion=True).as_long()
            if kind_value == NOP:
                continue
            network.append(
                {
                    "slot": slot,
                    "kind": KINDS[kind_value],
                    "left_drivers": selected(left_uses[slot]),
                    "right_drivers": selected(right_uses[slot]),
                    "cost": model.eval(costs[slot], model_completion=True).as_long(),
                    "depth": model.eval(gate_depths[slot], model_completion=True).as_long(),
                    "value": f"{model.eval(values[source_count + slot], model_completion=True).as_long():04x}",
                    "driven": f"{model.eval(drivens[source_count + slot], model_completion=True).as_long():04x}",
                }
            )
        payload["network"] = network
        payload["output_drivers"] = selected(output_uses)
        payload["output_value"] = f"{model.eval(out_value, model_completion=True).as_long():04x}"
        payload["output_driven"] = f"{model.eval(out_driven, model_completion=True).as_long():04x}"
        payload["output_depth"] = model.eval(out_depth, model_completion=True).as_long()
        payload["replayed_gate_cost"] = sum(item["cost"] for item in network)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate-bound", type=int, default=8)
    parser.add_argument("--max-delay", type=int, default=4)
    parser.add_argument("--slots", type=int, default=8)
    parser.add_argument("--timeout-ms", type=int, default=180_000)
    parser.add_argument("--memory-mb", type=int, default=700)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = solve(
        args.gate_bound,
        args.max_delay,
        args.slots,
        args.timeout_ms,
        args.memory_mb,
    )
    encoded = (json.dumps(payload, indent=2) + "\n").encode("ascii")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(encoded)
    print(json.dumps(payload, indent=2))
    print(f"sha256={hashlib.sha256(encoded).hexdigest()}")
    return 0 if payload["status"] != "unknown" else 2


if __name__ == "__main__":
    raise SystemExit(main())
