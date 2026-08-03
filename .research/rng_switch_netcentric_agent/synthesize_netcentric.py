"""Bounded exact synthesis with physical tri-state nets as first-class objects.

Unlike a functional BUS DAG, every source or gate output owns exactly one
physical output terminal and therefore exactly one ``net_id``.  Gate input
ports and architecture output ports select a net, not an arbitrary subset of
drivers.  Drivers with the same ``net_id`` are resolved together everywhere.

The model is intentionally limited to small scalar macros.  Its purpose is to
produce replayable witnesses and strict bounded UNSAT results without the BUS
alias relaxation used by earlier experiments.  It never touches a game save.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import time
from typing import Sequence

import z3


@dataclass(frozen=True)
class Kind:
    name: str
    cost: int
    delay: int
    unary: bool = False
    commutative: bool = False


BASIC = (
    Kind("NOT", 1, 1, unary=True),
    Kind("OR", 1, 1, commutative=True),
    Kind("XOR", 3, 2, commutative=True),
    Kind("SWITCH", 2, 1),
)
REVIEWED = (
    Kind("NOT", 1, 1, unary=True),
    Kind("AND", 1, 1, commutative=True),
    Kind("OR", 1, 1, commutative=True),
    Kind("NAND", 1, 1, commutative=True),
    Kind("NOR", 1, 1, commutative=True),
    Kind("XOR", 3, 2, commutative=True),
    Kind("SWITCH", 2, 1),
)


def variable_table(input_count: int, index: int) -> int:
    return sum(
        ((assignment >> index) & 1) << assignment
        for assignment in range(1 << input_count)
    )


def parity_table(input_count: int, support: Sequence[int]) -> int:
    return sum(
        (sum((assignment >> bit) & 1 for bit in support) & 1) << assignment
        for assignment in range(1 << input_count)
    )


def _bit_or(expressions: Sequence[z3.BitVecRef], width: int) -> z3.BitVecRef:
    result = z3.BitVecVal(0, width)
    for expression in expressions:
        result = result | expression
    return result


def _maximum(expressions: Sequence[z3.ArithRef]) -> z3.ArithRef:
    result: z3.ArithRef = z3.IntVal(0)
    for expression in expressions:
        result = z3.If(expression > result, expression, result)
    return result


def solve_exact_slots(
    *,
    input_count: int,
    targets: Sequence[int],
    exact_drive: Sequence[bool],
    gate_bound: int,
    max_delay: int,
    slots: int,
    kinds: Sequence[Kind],
    timeout_ms: int,
    memory_mb: int,
    free_complements: bool = False,
    exact_xors: int | None = None,
    exact_switches: int | None = None,
) -> dict[str, object]:
    if len(targets) != len(exact_drive):
        raise ValueError("targets and exact_drive differ")
    if slots < 1:
        raise ValueError("slots must be positive")
    assignments = 1 << input_count
    full = (1 << assignments) - 1
    raw_values = [variable_table(input_count, bit) for bit in range(input_count)]
    source_values = raw_values + ([full ^ value for value in raw_values] if free_complements else [])
    source_names = [f"x{bit}" for bit in range(input_count)] + (
        [f"not_x{bit}" for bit in range(input_count)] if free_complements else []
    )
    source_count = len(source_values)
    terminal_count = source_count + slots
    output_count = len(targets)

    solver = z3.Solver()
    solver.set(timeout=timeout_ms, max_memory=memory_mb)
    started = time.perf_counter()

    # net_of[t] is the canonical (lowest-terminal) representative of the one
    # physical net containing output terminal t.
    net_of = [z3.Int(f"net_of_{terminal}") for terminal in range(terminal_count)]
    for terminal, net in enumerate(net_of):
        solver.add(net >= 0, net <= terminal)
        for representative in range(terminal + 1):
            solver.add(z3.Implies(net == representative, net_of[representative] == representative))
    # Distinct always-driven input functions can never be safely shorted.
    for source in range(source_count):
        solver.add(net_of[source] == source)

    values: list[z3.BitVecRef] = [
        z3.BitVecVal(value, assignments) for value in source_values
    ]
    drivens: list[z3.BitVecRef] = [z3.BitVecVal(full, assignments) for _ in values]
    depths: list[z3.ArithRef] = [z3.IntVal(0) for _ in values]
    gate_kinds: list[z3.IntNumRef] = []
    left_nets: list[z3.IntNumRef] = []
    right_nets: list[z3.IntNumRef] = []
    costs: list[z3.ArithRef] = []

    def resolved(port_net: z3.ArithRef) -> tuple[z3.BitVecRef, z3.BitVecRef, z3.ArithRef]:
        ones = _bit_or(
            [z3.If(net_of[index] == port_net, values[index], z3.BitVecVal(0, assignments))
             for index in range(len(values))],
            assignments,
        )
        zeros = _bit_or(
            [z3.If(
                net_of[index] == port_net,
                drivens[index] & ~values[index],
                z3.BitVecVal(0, assignments),
            ) for index in range(len(values))],
            assignments,
        )
        depth = _maximum(
            [z3.If(net_of[index] == port_net, depths[index], z3.IntVal(0))
             for index in range(len(values))]
        )
        solver.add((ones & zeros) == z3.BitVecVal(0, assignments))
        return ones, ones | zeros, depth

    for slot in range(slots):
        kind = z3.Int(f"kind_{slot}")
        left_net = z3.Int(f"left_net_{slot}")
        right_net = z3.Int(f"right_net_{slot}")
        solver.add(kind >= 0, kind < len(kinds))
        solver.add(left_net >= 0, left_net < terminal_count)
        solver.add(right_net >= 0, right_net < terminal_count)

        # Inputs must be nonempty completed nets.  Once a net has been read,
        # no current/future driver may later be wired onto it.
        available = range(source_count + slot)
        solver.add(z3.Or(*(net_of[index] == left_net for index in available)))
        solver.add(z3.Or(*(net_of[index] == right_net for index in available)))
        for future in range(source_count + slot, terminal_count):
            solver.add(net_of[future] != left_net, net_of[future] != right_net)

        unary_cases = [kind == index for index, item in enumerate(kinds) if item.unary]
        commutative_cases = [kind == index for index, item in enumerate(kinds) if item.commutative]
        if unary_cases:
            solver.add(z3.Implies(z3.Or(*unary_cases), right_net == left_net))
        if commutative_cases:
            solver.add(z3.Implies(z3.Or(*commutative_cases), left_net <= right_net))

        lv, _ld, ldepth = resolved(left_net)
        rv, _rd, rdepth = resolved(right_net)
        maximum = z3.If(ldepth >= rdepth, ldepth, rdepth)

        gate_value: z3.BitVecRef = lv
        gate_driven: z3.BitVecRef = z3.BitVecVal(full, assignments)
        gate_depth: z3.ArithRef = ldepth
        gate_cost: z3.ArithRef = z3.IntVal(0)
        for index, item in reversed(tuple(enumerate(kinds))):
            if item.name == "NOT":
                value = ~lv
                driven = z3.BitVecVal(full, assignments)
                depth = ldepth + item.delay
            elif item.name == "AND":
                value = lv & rv
                driven = z3.BitVecVal(full, assignments)
                depth = maximum + item.delay
            elif item.name == "OR":
                value = lv | rv
                driven = z3.BitVecVal(full, assignments)
                depth = maximum + item.delay
            elif item.name == "NAND":
                value = ~(lv & rv)
                driven = z3.BitVecVal(full, assignments)
                depth = maximum + item.delay
            elif item.name == "NOR":
                value = ~(lv | rv)
                driven = z3.BitVecVal(full, assignments)
                depth = maximum + item.delay
            elif item.name == "XOR":
                value = lv ^ rv
                driven = z3.BitVecVal(full, assignments)
                depth = maximum + item.delay
            elif item.name == "SWITCH":
                value = lv & rv
                driven = lv
                depth = maximum + item.delay
            else:  # pragma: no cover - guarded library
                raise ValueError(item.name)
            gate_value = z3.If(kind == index, value, gate_value)
            gate_driven = z3.If(kind == index, driven, gate_driven)
            gate_depth = z3.If(kind == index, depth, gate_depth)
            gate_cost = z3.If(kind == index, item.cost, gate_cost)
        solver.add(gate_depth <= max_delay)
        values.append(gate_value)
        drivens.append(gate_driven)
        depths.append(gate_depth)
        gate_kinds.append(kind)
        left_nets.append(left_net)
        right_nets.append(right_net)
        costs.append(gate_cost)

    solver.add(z3.Sum(costs) <= gate_bound)
    if exact_xors is not None:
        xor_indexes = [index for index, item in enumerate(kinds) if item.name == "XOR"]
        solver.add(
            z3.Sum(
                [z3.If(kind == index, 1, 0) for kind in gate_kinds for index in xor_indexes]
            )
            == exact_xors
        )
    if exact_switches is not None:
        switch_indexes = [index for index, item in enumerate(kinds) if item.name == "SWITCH"]
        solver.add(
            z3.Sum(
                [z3.If(kind == index, 1, 0) for kind in gate_kinds for index in switch_indexes]
            )
            == exact_switches
        )

    # Minimum-network normalization: a fully driven source/gate sharing a net
    # with another output makes every additional driver electrically
    # redundant.  Such a paid driver can be deleted.  Since slot counts are
    # checked in ascending order, excluding these redundant mergers preserves
    # every minimum witness and removes most net-label symmetry.
    switch_indexes = [index for index, item in enumerate(kinds) if item.name == "SWITCH"]
    for source in range(source_count):
        for gate_slot in range(slots):
            solver.add(net_of[source] != net_of[source_count + gate_slot])
    for left_slot in range(slots):
        for right_slot in range(left_slot + 1, slots):
            same_net = net_of[source_count + left_slot] == net_of[source_count + right_slot]
            solver.add(
                z3.Implies(
                    same_net,
                    z3.And(
                        z3.Or(*(gate_kinds[left_slot] == index for index in switch_indexes)),
                        z3.Or(*(gate_kinds[right_slot] == index for index in switch_indexes)),
                    ),
                )
            )

    # Any two output terminals wired to one physical net must be compatible,
    # whether or not that net is ultimately observed.
    for left in range(terminal_count):
        for right in range(left + 1, terminal_count):
            conflict = drivens[left] & drivens[right] & (values[left] ^ values[right])
            solver.add(z3.Implies(net_of[left] == net_of[right], conflict == 0))

    output_nets = [z3.Int(f"output_net_{index}") for index in range(output_count)]
    output_depths: list[z3.ArithRef] = []
    for output, (port_net, target, require_full) in enumerate(
        zip(output_nets, targets, exact_drive, strict=True)
    ):
        solver.add(port_net >= 0, port_net < terminal_count)
        solver.add(z3.Or(*(net_of[index] == port_net for index in range(terminal_count))))
        value, driven, depth = resolved(port_net)
        solver.add(value == z3.BitVecVal(target, assignments))
        if require_full:
            solver.add(driven == z3.BitVecVal(full, assignments))
        solver.add(depth <= max_delay)
        output_depths.append(depth)

    # Every paid output is attached to a later consumer or an output.  This is
    # a safe normalization for minimum circuits and removes dead-gate models.
    for slot in range(slots):
        terminal = source_count + slot
        later_ports = []
        for later in range(slot + 1, slots):
            later_ports.extend((left_nets[later], right_nets[later]))
        later_ports.extend(output_nets)
        solver.add(z3.Or(*(net_of[terminal] == port for port in later_ports)))

    status = solver.check()
    elapsed = time.perf_counter() - started
    result: dict[str, object] = {
        "schema": 1,
        "model": "exact physical net_id partition; no directed BUS aliases",
        "status": str(status),
        "input_count": input_count,
        "targets": [f"{target:0{max(1, assignments // 4)}x}" for target in targets],
        "exact_drive": list(exact_drive),
        "gate_bound": gate_bound,
        "max_delay": max_delay,
        "slots": slots,
        "timeout_ms": timeout_ms,
        "memory_mb": memory_mb,
        "free_complements": free_complements,
        "exact_xors": exact_xors,
        "exact_switches": exact_switches,
        "solve_seconds": elapsed,
        "library": {item.name: [item.cost, item.delay] for item in kinds},
    }
    if status != z3.sat:
        if status == z3.unknown:
            result["reason_unknown"] = solver.reason_unknown()
        return result

    model = solver.model()
    concrete_net_of = [model.eval(net, model_completion=True).as_long() for net in net_of]
    concrete_values = [model.eval(value, model_completion=True).as_long() for value in values]
    concrete_drivens = [model.eval(driven, model_completion=True).as_long() for driven in drivens]
    concrete_depths = [model.eval(depth, model_completion=True).as_long() for depth in depths]
    groups: dict[int, list[int]] = {}
    for terminal, net in enumerate(concrete_net_of):
        groups.setdefault(net, []).append(terminal)
    concrete_gates = []
    for slot in range(slots):
        kind_index = model.eval(gate_kinds[slot], model_completion=True).as_long()
        concrete_gates.append(
            {
                "terminal": source_count + slot,
                "kind": kinds[kind_index].name,
                "left_net": model.eval(left_nets[slot], model_completion=True).as_long(),
                "right_net": model.eval(right_nets[slot], model_completion=True).as_long(),
                "value": f"{concrete_values[source_count + slot]:0{max(1, assignments // 4)}x}",
                "driven": f"{concrete_drivens[source_count + slot]:0{max(1, assignments // 4)}x}",
                "depth": concrete_depths[source_count + slot],
                "cost": kinds[kind_index].cost,
            }
        )
    result["network"] = {
        "sources": [
            {
                "terminal": bit,
                "name": source_names[bit],
                "net": concrete_net_of[bit],
                "value": f"{concrete_values[bit]:0{max(1, assignments // 4)}x}",
                "driven": f"{concrete_drivens[bit]:0{max(1, assignments // 4)}x}",
                "depth": 0,
            }
            for bit in range(source_count)
        ],
        "gates": concrete_gates,
        "nets": [
            {"net": net, "drivers": members}
            for net, members in sorted(groups.items())
        ],
        "outputs": [
            {
                "net": model.eval(port, model_completion=True).as_long(),
                "target": f"{targets[index]:0{max(1, assignments // 4)}x}",
                "exact_drive": exact_drive[index],
                "depth": model.eval(output_depths[index], model_completion=True).as_long(),
            }
            for index, port in enumerate(output_nets)
        ],
        "cost": sum(gate["cost"] for gate in concrete_gates),
        "depth": max(model.eval(depth, model_completion=True).as_long() for depth in output_depths),
    }
    return result


def write_payload(path: Path, payload: object) -> None:
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encoded)
    print(json.dumps({"path": str(path), "sha256": sha256(encoded).hexdigest()}, ensure_ascii=False))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", type=int, required=True)
    parser.add_argument(
        "--supports",
        required=True,
        help="semicolon-separated comma lists, e.g. 0,1;0,2;1,2",
    )
    parser.add_argument("--weak-output", action="store_true")
    parser.add_argument("--gate-bound", type=int, required=True)
    parser.add_argument("--max-delay", type=int, required=True)
    parser.add_argument("--minimum-slots", type=int, default=1)
    parser.add_argument("--maximum-slots", type=int, required=True)
    parser.add_argument("--library", choices=("basic", "reviewed"), default="basic")
    parser.add_argument("--free-complements", action="store_true")
    parser.add_argument("--exact-xors", type=int)
    parser.add_argument("--exact-switches", type=int)
    parser.add_argument("--timeout-ms", type=int, default=60_000)
    parser.add_argument("--memory-mb", type=int, default=700)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    parsed = []
    for item in args.supports.split(";"):
        inverted = item.startswith("~")
        if inverted:
            item = item[1:]
        parsed.append((tuple(int(bit) for bit in item.split(",") if bit != ""), inverted))
    supports = [support for support, _inverted in parsed]
    truth_full = (1 << (1 << args.inputs)) - 1
    targets = [
        (truth_full ^ parity_table(args.inputs, support))
        if inverted else parity_table(args.inputs, support)
        for support, inverted in parsed
    ]
    kinds = BASIC if args.library == "basic" else REVIEWED
    results = []
    for slots in range(args.minimum_slots, args.maximum_slots + 1):
        result = solve_exact_slots(
            input_count=args.inputs,
            targets=targets,
            exact_drive=[not args.weak_output] * len(targets),
            gate_bound=args.gate_bound,
            max_delay=args.max_delay,
            slots=slots,
            kinds=kinds,
            timeout_ms=args.timeout_ms,
            memory_mb=args.memory_mb,
            free_complements=args.free_complements,
            exact_xors=args.exact_xors,
            exact_switches=args.exact_switches,
        )
        results.append(result)
        print(json.dumps({"slots": slots, "status": result["status"], "seconds": result["solve_seconds"]}))
        if result["status"] == "sat":
            break
    payload = {
        "schema": 1,
        "query": {
            "inputs": args.inputs,
            "supports": [
                {"bits": list(support), "inverted": inverted}
                for support, inverted in parsed
            ],
            "weak_output": args.weak_output,
            "gate_bound": args.gate_bound,
            "max_delay": args.max_delay,
            "slot_range": [args.minimum_slots, args.maximum_slots],
            "library": args.library,
            "free_complements": args.free_complements,
            "exact_xors": args.exact_xors,
            "exact_switches": args.exact_switches,
        },
        "results": results,
    }
    write_payload(args.output, payload)
    return 2 if any(result["status"] == "unknown" for result in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
