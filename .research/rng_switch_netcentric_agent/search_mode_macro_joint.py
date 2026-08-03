"""Exact physical-net synthesis for joint 402 RNG mode-consuming macros.

The boundary model contains only runtime-reachable rows:

* load: all state-delay outputs are zero and selected Seed bits are driven;
* steady: Seed is Z and selected state bits are arbitrary and driven.

Every component output owns one terminal and one undirected physical net.
Several drivers may share a net only when their driven value planes never
conflict.  A gate cannot read a net that receives a current/future driver, so
serialized witnesses are acyclic under physical net closure.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import time
from typing import Iterable, Sequence

import z3


HERE = Path(__file__).resolve().parent
GRAPH_PATH = HERE / "actual_graph_analysis.json"


@dataclass(frozen=True)
class Kind:
    name: str
    cost: int
    delay: int
    unary: bool = False
    commutative: bool = False


KINDS = (
    Kind("NOT", 1, 1, unary=True),
    Kind("AND", 1, 1, commutative=True),
    Kind("OR", 1, 1, commutative=True),
    Kind("NAND", 1, 1, commutative=True),
    Kind("NOR", 1, 1, commutative=True),
    Kind("XOR", 3, 2, commutative=True),
    Kind("SWITCH", 2, 1),
)


def next_power_of_two(value: int) -> int:
    return 1 << max(0, (value - 1).bit_length())


def pack(values: Iterable[bool]) -> int:
    return sum(int(value) << index for index, value in enumerate(values))


def hex_value(value: int, width: int) -> str:
    return f"{value:0{max(1, (width + 3) // 4)}x}"


def load_nodes(path: Path = GRAPH_PATH) -> dict[int, tuple[tuple[int, int | None], ...]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    result: dict[int, tuple[tuple[int, int | None], ...]] = {}
    for component in payload["components"]:
        for raw_node, raw_pairs in zip(
            component["ordered_nodes"], component["ordered_leaf_pairs"], strict=True
        ):
            node = int(raw_node, 16)
            pairs = tuple(
                (int(pair[0]), None if pair[1] is None else int(pair[1]))
                for pair in raw_pairs
            )
            previous = result.setdefault(node, pairs)
            if previous != pairs:
                raise ValueError(f"inconsistent leaf boundary for {node:08x}")
    return result


def build_scenarios(
    selected: Sequence[tuple[int, tuple[tuple[int, int | None], ...]]]
) -> dict[str, object]:
    state_bits = sorted({state for _node, pairs in selected for state, _seed in pairs})
    seed_bits = sorted(
        {seed for _node, pairs in selected for _state, seed in pairs if seed is not None}
    )
    rows: list[dict[str, object]] = []
    for assignment in range(1 << len(seed_bits)):
        rows.append(
            {
                "phase": "load",
                "state": {str(bit): 0 for bit in state_bits},
                "seed": {
                    str(bit): (assignment >> index) & 1
                    for index, bit in enumerate(seed_bits)
                },
            }
        )
    for assignment in range(1 << len(state_bits)):
        rows.append(
            {
                "phase": "steady",
                "state": {
                    str(bit): (assignment >> index) & 1
                    for index, bit in enumerate(state_bits)
                },
                "seed": {str(bit): None for bit in seed_bits},
            }
        )

    reachable_count = len(rows)
    padded_count = next_power_of_two(reachable_count)
    rows.extend(dict(rows[0]) for _ in range(padded_count - reachable_count))
    full = (1 << padded_count) - 1

    sources = []
    for bit in state_bits:
        sources.append(
            {
                "name": f"q{bit}",
                "value": pack(bool(row["state"][str(bit)]) for row in rows),
                "driven": full,
                "depth": 0,
            }
        )
    for bit in seed_bits:
        sources.append(
            {
                "name": f"seed{bit}",
                "value": pack(row["seed"][str(bit)] == 1 for row in rows),
                "driven": pack(row["seed"][str(bit)] is not None for row in rows),
                "depth": 0,
            }
        )

    targets = []
    for node, pairs in selected:
        values = []
        for row in rows:
            if row["phase"] == "load":
                value = sum(
                    int(row["seed"][str(seed)])
                    for _state, seed in pairs
                    if seed is not None
                ) & 1
            else:
                value = sum(int(row["state"][str(state)]) for state, _seed in pairs) & 1
            values.append(bool(value))
        targets.append(
            {
                "node": f"{node:08x}",
                "value": pack(values),
                "driven": full,
                "baseline_gate": 3 + sum(seed is not None for _state, seed in pairs),
            }
        )
    return {
        "state_bits": state_bits,
        "seed_bits": seed_bits,
        "reachable_rows": reachable_count,
        "padded_rows": padded_count,
        "rows": rows,
        "sources": sources,
        "targets": targets,
    }


def bit_or(expressions: Sequence[z3.BitVecRef], width: int) -> z3.BitVecRef:
    result = z3.BitVecVal(0, width)
    for expression in expressions:
        result |= expression
    return result


def maximum(expressions: Sequence[z3.ArithRef]) -> z3.ArithRef:
    result: z3.ArithRef = z3.IntVal(0)
    for expression in expressions:
        result = z3.If(expression > result, expression, result)
    return result


def solve_slots(
    scenario: dict[str, object],
    *,
    slots: int,
    gate_bound: int,
    max_delay: int,
    timeout_ms: int,
    memory_mb: int,
    exact_xors: int | None = None,
    exact_switches: int | None = None,
) -> dict[str, object]:
    source_records = list(scenario["sources"])
    target_records = list(scenario["targets"])
    width = int(scenario["padded_rows"])
    full_int = (1 << width) - 1
    full = z3.BitVecVal(full_int, width)
    source_count = len(source_records)
    terminal_count = source_count + slots

    solver = z3.Solver()
    solver.set(timeout=timeout_ms, max_memory=memory_mb)
    started = time.perf_counter()

    net_of = [z3.Int(f"net_of_{terminal}") for terminal in range(terminal_count)]
    for terminal, net in enumerate(net_of):
        solver.add(net >= 0, net <= terminal)
        for representative in range(terminal + 1):
            solver.add(z3.Implies(net == representative, net_of[representative] == representative))
    # The selected raw sources are independently variable on at least one
    # reachable phase.  Their physical terminals therefore cannot be shorted.
    for source in range(source_count):
        solver.add(net_of[source] == source)

    values: list[z3.BitVecRef] = [
        z3.BitVecVal(int(source["value"]), width) for source in source_records
    ]
    drivens: list[z3.BitVecRef] = [
        z3.BitVecVal(int(source["driven"]), width) for source in source_records
    ]
    depths: list[z3.ArithRef] = [z3.IntVal(int(source["depth"])) for source in source_records]
    gate_kinds: list[z3.ArithRef] = []
    left_nets: list[z3.ArithRef] = []
    right_nets: list[z3.ArithRef] = []
    costs: list[z3.ArithRef] = []

    def resolved(port_net: z3.ArithRef) -> tuple[z3.BitVecRef, z3.BitVecRef, z3.ArithRef]:
        ones = bit_or(
            [
                z3.If(net_of[index] == port_net, values[index], z3.BitVecVal(0, width))
                for index in range(len(values))
            ],
            width,
        )
        zeros = bit_or(
            [
                z3.If(
                    net_of[index] == port_net,
                    drivens[index] & ~values[index],
                    z3.BitVecVal(0, width),
                )
                for index in range(len(values))
            ],
            width,
        )
        depth = maximum(
            [z3.If(net_of[index] == port_net, depths[index], z3.IntVal(0)) for index in range(len(values))]
        )
        solver.add((ones & zeros) == z3.BitVecVal(0, width))
        return ones, ones | zeros, depth

    for slot in range(slots):
        kind = z3.Int(f"kind_{slot}")
        left_net = z3.Int(f"left_net_{slot}")
        right_net = z3.Int(f"right_net_{slot}")
        solver.add(kind >= 0, kind < len(KINDS))
        solver.add(left_net >= 0, left_net < terminal_count)
        solver.add(right_net >= 0, right_net < terminal_count)

        available = range(source_count + slot)
        solver.add(z3.Or(*(net_of[index] == left_net for index in available)))
        solver.add(z3.Or(*(net_of[index] == right_net for index in available)))
        for future in range(source_count + slot, terminal_count):
            solver.add(net_of[future] != left_net, net_of[future] != right_net)

        unary = [kind == index for index, item in enumerate(KINDS) if item.unary]
        commutative = [kind == index for index, item in enumerate(KINDS) if item.commutative]
        solver.add(z3.Implies(z3.Or(*unary), right_net == left_net))
        solver.add(z3.Implies(z3.Or(*commutative), left_net <= right_net))

        left_value, _left_driven, left_depth = resolved(left_net)
        right_value, _right_driven, right_depth = resolved(right_net)
        maximum_depth = z3.If(left_depth >= right_depth, left_depth, right_depth)

        gate_value: z3.BitVecRef = left_value
        gate_driven: z3.BitVecRef = full
        gate_depth: z3.ArithRef = left_depth
        gate_cost: z3.ArithRef = z3.IntVal(0)
        for index, item in reversed(tuple(enumerate(KINDS))):
            if item.name == "NOT":
                value, driven, depth = ~left_value, full, left_depth + item.delay
            elif item.name == "AND":
                value, driven, depth = left_value & right_value, full, maximum_depth + item.delay
            elif item.name == "OR":
                value, driven, depth = left_value | right_value, full, maximum_depth + item.delay
            elif item.name == "NAND":
                value, driven, depth = ~(left_value & right_value), full, maximum_depth + item.delay
            elif item.name == "NOR":
                value, driven, depth = ~(left_value | right_value), full, maximum_depth + item.delay
            elif item.name == "XOR":
                value, driven, depth = left_value ^ right_value, full, maximum_depth + item.delay
            elif item.name == "SWITCH":
                value, driven, depth = left_value & right_value, left_value, maximum_depth + item.delay
            else:  # pragma: no cover
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

    switch_index = next(index for index, item in enumerate(KINDS) if item.name == "SWITCH")
    xor_index = next(index for index, item in enumerate(KINDS) if item.name == "XOR")
    if exact_xors is not None:
        solver.add(z3.Sum([z3.If(kind == xor_index, 1, 0) for kind in gate_kinds]) == exact_xors)
    if exact_switches is not None:
        solver.add(z3.Sum([z3.If(kind == switch_index, 1, 0) for kind in gate_kinds]) == exact_switches)
    # An always-driven raw source cannot gain information from another driver.
    for source, record in enumerate(source_records):
        if int(record["driven"]) == full_int:
            for slot in range(slots):
                solver.add(net_of[source] != net_of[source_count + slot])
    # If two paid outputs share a net in a minimum witness, both must be Z-capable.
    for left in range(slots):
        for right in range(left + 1, slots):
            solver.add(
                z3.Implies(
                    net_of[source_count + left] == net_of[source_count + right],
                    z3.And(gate_kinds[left] == switch_index, gate_kinds[right] == switch_index),
                )
            )

    for left in range(terminal_count):
        for right in range(left + 1, terminal_count):
            conflict = drivens[left] & drivens[right] & (values[left] ^ values[right])
            solver.add(z3.Implies(net_of[left] == net_of[right], conflict == 0))

    output_nets = [z3.Int(f"output_net_{index}") for index in range(len(target_records))]
    output_depths: list[z3.ArithRef] = []
    for output, (port_net, target_record) in enumerate(zip(output_nets, target_records, strict=True)):
        solver.add(port_net >= 0, port_net < terminal_count)
        solver.add(z3.Or(*(net_of[index] == port_net for index in range(terminal_count))))
        value, driven, depth = resolved(port_net)
        solver.add(value == z3.BitVecVal(int(target_record["value"]), width))
        solver.add(driven == full)
        solver.add(depth <= max_delay)
        output_depths.append(depth)

    # No paid terminal is dead.  Net equality, rather than terminal identity,
    # is used so all multi-driver output nets remain covered.
    for slot in range(slots):
        terminal = source_count + slot
        consumers = []
        for later in range(slot + 1, slots):
            consumers.extend((left_nets[later], right_nets[later]))
        consumers.extend(output_nets)
        solver.add(z3.Or(*(net_of[terminal] == consumer for consumer in consumers)))

    status = solver.check()
    elapsed = time.perf_counter() - started
    result: dict[str, object] = {
        "schema": 1,
        "model": "reachable load/steady rows with exact undirected physical net ownership",
        "status": str(status),
        "input_count": width.bit_length() - 1,
        "scenario_width": width,
        "gate_bound": gate_bound,
        "max_delay": max_delay,
        "slots": slots,
        "timeout_ms": timeout_ms,
        "memory_mb": memory_mb,
        "exact_xors": exact_xors,
        "exact_switches": exact_switches,
        "solve_seconds": elapsed,
        "targets": [hex_value(int(target["value"]), width) for target in target_records],
        "exact_drive": [True] * len(target_records),
        "library": {item.name: [item.cost, item.delay] for item in KINDS},
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
                "kind": KINDS[kind_index].name,
                "left_net": model.eval(left_nets[slot], model_completion=True).as_long(),
                "right_net": model.eval(right_nets[slot], model_completion=True).as_long(),
                "value": hex_value(concrete_values[source_count + slot], width),
                "driven": hex_value(concrete_drivens[source_count + slot], width),
                "depth": concrete_depths[source_count + slot],
                "cost": KINDS[kind_index].cost,
            }
        )
    result["network"] = {
        "sources": [
            {
                "terminal": source,
                "name": str(record["name"]),
                "net": concrete_net_of[source],
                "value": hex_value(int(record["value"]), width),
                "driven": hex_value(int(record["driven"]), width),
                "depth": int(record["depth"]),
            }
            for source, record in enumerate(source_records)
        ],
        "gates": concrete_gates,
        "nets": [{"net": net, "drivers": members} for net, members in sorted(groups.items())],
        "outputs": [
            {
                "net": model.eval(port, model_completion=True).as_long(),
                "target": hex_value(int(target_records[index]["value"]), width),
                "exact_drive": True,
                "depth": model.eval(output_depths[index], model_completion=True).as_long(),
                "node": target_records[index]["node"],
            }
            for index, port in enumerate(output_nets)
        ],
        "cost": sum(int(gate["cost"]) for gate in concrete_gates),
        "depth": max(model.eval(depth, model_completion=True).as_long() for depth in output_depths),
    }
    return result


def write_json(path: Path, payload: object) -> None:
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode()
    path.write_bytes(encoded)
    print(json.dumps({"path": str(path), "sha256": sha256(encoded).hexdigest()}))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--nodes", required=True, help="comma-separated first-layer hex rows")
    parser.add_argument("--gate-bound", type=int, required=True)
    parser.add_argument("--max-delay", type=int, default=3)
    parser.add_argument("--minimum-slots", type=int, default=1)
    parser.add_argument("--maximum-slots", type=int, required=True)
    parser.add_argument("--timeout-ms", type=int, default=120_000)
    parser.add_argument("--memory-mb", type=int, default=700)
    parser.add_argument("--exact-xors", type=int)
    parser.add_argument("--exact-switches", type=int)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    node_map = load_nodes()
    nodes = tuple(int(item, 16) for item in args.nodes.split(","))
    if len(nodes) != len(set(nodes)):
        raise ValueError("duplicate node")
    selected = tuple((node, node_map[node]) for node in nodes)
    scenario = build_scenarios(selected)
    baseline = sum(int(target["baseline_gate"]) for target in scenario["targets"])
    results = []
    for slots in range(args.minimum_slots, args.maximum_slots + 1):
        result = solve_slots(
            scenario,
            slots=slots,
            gate_bound=args.gate_bound,
            max_delay=args.max_delay,
            timeout_ms=args.timeout_ms,
            memory_mb=args.memory_mb,
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
            "nodes": [f"{node:08x}" for node in nodes],
            "baseline_gate": baseline,
            "gate_bound": args.gate_bound,
            "max_delay": args.max_delay,
            "slot_range": [args.minimum_slots, args.maximum_slots],
            "source_boundary": "selected raw Seed/state terminals only",
            "exact_xors": args.exact_xors,
            "exact_switches": args.exact_switches,
        },
        "scenario": {
            "state_bits": scenario["state_bits"],
            "seed_bits": scenario["seed_bits"],
            "reachable_rows": scenario["reachable_rows"],
            "padded_rows": scenario["padded_rows"],
            "rows": scenario["rows"],
            "targets": [
                {
                    **target,
                    "value": hex_value(int(target["value"]), int(scenario["padded_rows"])),
                    "driven": hex_value(int(target["driven"]), int(scenario["padded_rows"])),
                }
                for target in scenario["targets"]
            ],
        },
        "results": results,
    }
    write_json(args.output, payload)
    return 0 if any(result["status"] == "sat" for result in results) else (
        2 if any(result["status"] == "unknown" for result in results) else 1
    )


if __name__ == "__main__":
    raise SystemExit(main())
