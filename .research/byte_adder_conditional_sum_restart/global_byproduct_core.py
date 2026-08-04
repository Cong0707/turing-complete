"""Independent full-truth and physical-net helpers for Byte Adder research.

The main architecture ledger has its own replay implementation.  This module is
deliberately separate so imported Factory DAGs and local SAT witnesses are not
accepted merely because they passed through the producer that emitted them.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Iterable


ROWS = 1 << 17
ALL = (1 << ROWS) - 1
BYTE_COUNT = ROWS // 8
INPUT_NAMES = tuple(
    [item for bit in range(8) for item in (f"a{bit}", f"b{bit}")] + ["cin"]
)
OUTPUT_NAMES = tuple([f"S{bit}" for bit in range(8)] + ["C8"])

GATE_SPECS: dict[str, tuple[int, int, int]] = {
    "NOT": (1, 1, 1),
    "AND": (1, 1, 2),
    "NAND": (1, 1, 2),
    "OR": (1, 1, 2),
    "NOR": (1, 1, 2),
    "XOR": (3, 2, 2),
    "XNOR": (3, 2, 2),
}


def variable(index: int) -> int:
    run = 1 << index
    period = run << 1
    pattern = ((1 << run) - 1) << run
    value = 0
    for offset in range(0, ROWS, period):
        value |= pattern << offset
    return value & ALL


INPUT_BITS = {
    **{f"a{bit}": variable(bit) for bit in range(8)},
    **{f"b{bit}": variable(8 + bit) for bit in range(8)},
    "cin": variable(16),
}


@dataclass(frozen=True)
class State:
    bits: int
    driven: int
    conflict: int
    arrival: int


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: object) -> str:
    return sha256(
        json.dumps(
            value,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii")
    ).hexdigest()


def packed_sha(bits: int) -> str:
    return sha256(int(bits & ALL).to_bytes(BYTE_COUNT, "little")).hexdigest()


def atomic_write(path: Path, payload: object) -> str:
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(encoded)
    temporary.replace(path)
    return sha256(encoded).hexdigest()


def ordinary_state(op: str, args: tuple[State, ...], mask: int = ALL) -> State:
    if op not in GATE_SPECS:
        raise ValueError(f"unknown ordinary gate: {op}")
    _cost, delay, arity = GATE_SPECS[op]
    if len(args) != arity:
        raise ValueError(f"{op}: expected {arity} args, received {len(args)}")
    left = args[0].bits
    right = args[1].bits if arity == 2 else 0
    if op == "NOT":
        bits = ~left
    elif op == "AND":
        bits = left & right
    elif op == "NAND":
        bits = ~(left & right)
    elif op == "OR":
        bits = left | right
    elif op == "NOR":
        bits = ~(left | right)
    elif op == "XOR":
        bits = left ^ right
    elif op == "XNOR":
        bits = ~(left ^ right)
    else:  # pragma: no cover
        raise AssertionError(op)
    conflict = 0
    for arg in args:
        conflict |= arg.conflict
    return State(
        bits & mask,
        mask,
        conflict & mask,
        max(arg.arrival for arg in args) + delay,
    )


def resolve_bus(drivers: Iterable[State], mask: int = ALL, *, delay: int = 0) -> State:
    values = tuple(drivers)
    if not values:
        return State(0, 0, 0, 0)
    ones = zeros = driven = conflict = 0
    for state in values:
        ones |= state.driven & state.bits
        zeros |= state.driven & (~state.bits & mask)
        driven |= state.driven
        conflict |= state.conflict
    conflict |= ones & zeros
    return State(
        ones & mask,
        driven & mask,
        conflict & mask,
        max(state.arrival for state in values) + delay,
    )


def expected_functions() -> tuple[tuple[int, ...], dict[int, list[str]]]:
    registry: dict[int, set[str]] = defaultdict(set)

    def add(label: str, bits: int) -> None:
        registry[bits & ALL].add(label)

    carries = [INPUT_BITS["cin"]]
    sums: list[int] = []
    leaves: list[dict[str, int]] = []
    for bit in range(8):
        a = INPUT_BITS[f"a{bit}"]
        b = INPUT_BITS[f"b{bit}"]
        g = a & b
        q = a | b
        p = a ^ b
        k = (~q) & ALL
        leaves.append({"G": g, "Q": q, "P": p, "K": k})
        add(f"bit{bit}.G", g)
        add(f"bit{bit}.NG", ~g)
        add(f"bit{bit}.Q", q)
        add(f"bit{bit}.K", k)
        add(f"bit{bit}.P", p)
        add(f"bit{bit}.NP", ~p)
        add(f"bit{bit}.sum_if_c0", p)
        add(f"bit{bit}.sum_if_c1", ~p)
        add(f"bit{bit}.carry_if_c0", g)
        add(f"bit{bit}.carry_if_c1", q)
        carry_in = carries[-1]
        summed = p ^ carry_in
        carry = g | (q & carry_in)
        sums.append(summed & ALL)
        carries.append(carry & ALL)
        add(f"S{bit}", summed)
        add(f"NS{bit}", ~summed)
        add(f"C{bit}", carry_in)
        add(f"NC{bit}", ~carry_in)
        add(f"majority(a{bit},b{bit},C{bit})", carry)
    add("C8", carries[8])
    add("NC8", ~carries[8])

    for low in range(8):
        for high in range(low, 8):
            f0 = 0
            f1 = ALL
            any_generate = 0
            survival = ALL
            xor_propagate = ALL
            for bit in range(low, high + 1):
                leaf = leaves[bit]
                any_generate |= leaf["G"]
                survival &= leaf["Q"]
                xor_propagate &= leaf["P"]
                f0 = leaf["G"] | (leaf["Q"] & f0)
                f1 = leaf["G"] | (leaf["Q"] & f1)
            prefix = f"I[{low}:{high}]"
            add(prefix + ".F0", f0)
            add(prefix + ".F1", f1)
            add(prefix + ".NF0", ~f0)
            add(prefix + ".NF1", ~f1)
            add(prefix + ".transfer_generate", f0)
            add(prefix + ".transfer_propagate", (~f0) & f1)
            add(prefix + ".transfer_kill", ~f1)
            add(prefix + ".any_generate", any_generate)
            add(prefix + ".survival", survival)
            add(prefix + ".xor_propagate", xor_propagate)
            for external in (0, 1):
                current = ALL if external else 0
                for bit in range(low, high + 1):
                    leaf = leaves[bit]
                    add(prefix + f".sum{bit}.cin{external}", leaf["P"] ^ current)
                    current = leaf["G"] | (leaf["Q"] & current)
                add(prefix + f".cout.cin{external}", current)

    return tuple(sums + [carries[8]]), {
        bits: sorted(labels) for bits, labels in registry.items()
    }


EXPECTED_OUTPUTS, SEMANTIC_REGISTRY = expected_functions()


def replay_factory(nodes: Iterable[dict[str, Any]]) -> dict[int, State]:
    states: dict[int, State] = {}
    owners: set[str] = set()
    for node in nodes:
        node_id = int(node["id"])
        if node_id in states:
            raise RuntimeError(f"duplicate Factory node ID {node_id}")
        arguments = tuple(map(int, node.get("args", ())))
        if any(argument not in states for argument in arguments):
            raise RuntimeError(f"non-topological Factory node {node_id}")
        args = tuple(states[argument] for argument in arguments)
        op = str(node["op"])
        if op == "INPUT":
            label = str(node.get("label", ""))
            if label not in INPUT_BITS:
                raise RuntimeError(f"unknown Factory input {label!r}")
            state = State(INPUT_BITS[label], ALL, 0, 0)
            cost = delay = 0
        elif op == "CONST":
            label = str(node.get("label", ""))
            if label not in ("0", "1"):
                raise RuntimeError(f"unknown Factory constant {label!r}")
            state = State(ALL if label == "1" else 0, ALL, 0, 0)
            cost = delay = 0
        elif op == "BUS":
            if len(args) < 2 or len(args) % 2:
                raise RuntimeError(f"malformed Factory BUS {node_id}")
            owner = str(node.get("resolved_network", ""))
            if not owner or owner in owners:
                raise RuntimeError(f"Factory BUS owner collision {node_id}: {owner!r}")
            owners.add(owner)
            expected_drivers = [
                {
                    "enable": arguments[offset],
                    "data": arguments[offset + 1],
                    "owner": owner,
                }
                for offset in range(0, len(arguments), 2)
            ]
            if list(node.get("drivers", ())) != expected_drivers:
                raise RuntimeError(f"Factory BUS driver partition mismatch {node_id}")
            switch_states = [
                State(
                    args[offset].bits & args[offset + 1].bits,
                    args[offset].bits,
                    args[offset].conflict | args[offset + 1].conflict,
                    max(args[offset].arrival, args[offset + 1].arrival) + 1,
                )
                for offset in range(0, len(args), 2)
            ]
            state = resolve_bus(switch_states)
            cost = len(arguments)
            delay = 1
        else:
            state = ordinary_state(op, args)
            cost, delay, _arity = GATE_SPECS[op]
        if int(node.get("cost", -1)) != cost:
            raise RuntimeError(f"Factory cost annotation mismatch at node {node_id}")
        if int(node.get("step_delay", -1)) != delay:
            raise RuntimeError(f"Factory step-delay annotation mismatch at node {node_id}")
        if int(node.get("arrival", -1)) != state.arrival:
            raise RuntimeError(f"Factory arrival annotation mismatch at node {node_id}")
        if bool(node.get("may_z")) != (op == "BUS"):
            raise RuntimeError(f"Factory may_z annotation mismatch at node {node_id}")
        states[node_id] = state
    return states


def factory_analysis(
    candidate_id: str,
    factory: dict[str, Any],
    serialized_metrics: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[int, State]]:
    nodes = tuple(factory["nodes"])
    outputs = tuple(map(int, factory["outputs"]))
    if len(outputs) != len(OUTPUT_NAMES):
        raise RuntimeError(f"{candidate_id}: expected nine Factory outputs")
    if int(factory.get("live_node_count", len(nodes))) != len(nodes):
        raise RuntimeError(f"{candidate_id}: Factory live-node annotation mismatch")
    states = replay_factory(nodes)
    by_id = {int(node["id"]): node for node in nodes}
    input_labels = [str(node.get("label")) for node in nodes if node["op"] == "INPUT"]
    if len(input_labels) != len(INPUT_NAMES) or set(input_labels) != set(INPUT_NAMES):
        raise RuntimeError(f"{candidate_id}: primary-input coverage mismatch")
    if any(output not in states for output in outputs):
        raise RuntimeError(f"{candidate_id}: missing Factory output node")

    output_states = tuple(states[output] for output in outputs)
    mismatches = [
        (state.bits ^ expected).bit_count()
        for state, expected in zip(output_states, EXPECTED_OUTPUTS, strict=True)
    ]
    conflict = 0
    for state in states.values():
        conflict |= state.conflict
    output_z = [((~state.driven) & ALL).bit_count() for state in output_states]
    if any(mismatches) or conflict or any(output_z):
        raise RuntimeError(
            f"{candidate_id}: full replay mismatch={mismatches} "
            f"conflict={conflict.bit_count()} z={output_z}"
        )

    ancestors: dict[int, frozenset[int]] = {}
    supports: dict[int, frozenset[str]] = {}

    def cone(node_id: int) -> frozenset[int]:
        if node_id not in ancestors:
            values = {node_id}
            for argument in map(int, by_id[node_id].get("args", ())):
                values.update(cone(argument))
            ancestors[node_id] = frozenset(values)
        return ancestors[node_id]

    def support(node_id: int) -> frozenset[str]:
        if node_id not in supports:
            node = by_id[node_id]
            if node["op"] == "INPUT":
                values = {str(node["label"])}
            else:
                values: set[str] = set()
                for argument in map(int, node.get("args", ())):
                    values.update(support(argument))
            supports[node_id] = frozenset(values)
        return supports[node_id]

    descendants: dict[int, list[str]] = defaultdict(list)
    for output_name, output in zip(OUTPUT_NAMES, outputs, strict=True):
        for node_id in cone(output):
            descendants[node_id].append(output_name)
    live_union = set().union(*(cone(output) for output in outputs))
    if live_union != set(states):
        dead = sorted(set(states) - live_union)
        raise RuntimeError(f"{candidate_id}: dead serialized Factory nodes {dead}")

    gate = sum(int(node["cost"]) for node in nodes)
    arrivals = [state.arrival for state in output_states]
    metrics = {
        "gate": gate,
        "delay": max(arrivals),
        "energy": gate * max(arrivals),
        "output_arrivals": arrivals,
        "live_node_count": len(nodes),
        "bus_node_count": sum(node["op"] == "BUS" for node in nodes),
        "switch_driver_count": sum(
            len(node.get("args", ())) // 2 for node in nodes if node["op"] == "BUS"
        ),
        "structural_sha256": canonical_sha256(
            {"outputs": list(outputs), "nodes": list(nodes)}
        ),
    }
    if serialized_metrics is not None:
        fields = ("gate", "delay", "energy", "output_arrivals")
        mismatched = {
            field: {
                "serialized": serialized_metrics.get(field),
                "recomputed": metrics[field],
            }
            for field in fields
            if serialized_metrics.get(field) != metrics[field]
        }
        if mismatched:
            raise RuntimeError(f"{candidate_id}: serialized metrics mismatch {mismatched}")

    entries: list[dict[str, Any]] = []
    for node in nodes:
        node_id = int(node["id"])
        state = states[node_id]
        cone_ids = cone(node_id)
        z = (~state.driven) & ALL
        entries.append(
            {
                "node_id": node_id,
                "op": str(node["op"]),
                "local_cost": int(node["cost"]),
                "arrival": state.arrival,
                "cone_gate": sum(int(by_id[item]["cost"]) for item in cone_ids),
                "cone_node_count": len(cone_ids),
                "value_sha256": packed_sha(state.bits),
                "driven_sha256": packed_sha(state.driven),
                "conflict_rows": state.conflict.bit_count(),
                "z_rows": z.bit_count(),
                "z_false_rows": ((~state.bits) & z & ALL).bit_count(),
                "z_true_rows": (state.bits & z).bit_count(),
                "source_support": sorted(support(node_id)),
                "target_descendants": sorted(descendants[node_id]),
                "semantic_labels": SEMANTIC_REGISTRY.get(state.bits, []),
            }
        )
    return (
        {
            "candidate_id": candidate_id,
            "metrics": metrics,
            "factory_dag": {
                "outputs": list(outputs),
                "nodes": list(nodes),
                "live_node_count": len(nodes),
                "sha256": metrics["structural_sha256"],
            },
            "entries": entries,
        },
        states,
    )


def replay_physical_network(
    source_names: list[str],
    source_states: list[State],
    network: list[dict[str, Any]],
    output_buses: list[Any],
    *,
    mask: int = ALL,
) -> dict[str, Any]:
    if len(source_names) != len(source_states):
        raise RuntimeError("physical witness source name/state count mismatch")
    states = list(source_states)
    dependencies: list[frozenset[int]] = [frozenset() for _ in source_states]
    costs = [0 for _ in source_states]
    physical_buses: list[tuple[str, frozenset[int]]] = []
    bus_records: list[dict[str, Any]] = []

    def normalize_bus(value: Any) -> list[int]:
        return [int(value)] if isinstance(value, int) else list(map(int, value))

    def bus_state(name: str, indices: list[int]) -> State:
        if not indices:
            return State(0, 0, 0, 0)
        if any(index < 0 or index >= len(states) for index in indices):
            raise RuntimeError(f"{name}: non-topological physical bus {indices}")
        physical_buses.append((name, frozenset(indices)))
        state = resolve_bus((states[index] for index in indices), mask)
        bus_records.append({"name": name, "drivers": list(indices), "state": state})
        return state

    component_records: list[dict[str, Any]] = []
    for expected_slot, item in enumerate(network):
        if int(item.get("slot", expected_slot)) != expected_slot:
            raise RuntimeError(f"physical witness slot mismatch at {expected_slot}")
        expected_source = len(source_states) + expected_slot
        if int(item["source"]) != expected_source:
            raise RuntimeError(f"physical witness source mismatch at slot {expected_slot}")
        left_ids = normalize_bus(item.get("left_bus", []))
        right_ids = normalize_bus(item.get("right_bus", []))
        left = bus_state(f"slot{expected_slot}.left", left_ids)
        right = bus_state(f"slot{expected_slot}.right", right_ids)
        kind = str(item["kind"])
        if kind == "SWITCH":
            state = State(
                left.bits & right.bits & mask,
                left.bits & mask,
                (left.conflict | right.conflict) & mask,
                max(
                    [states[index].arrival for index in left_ids + right_ids],
                    default=0,
                )
                + 1,
            )
            expected_cost = 2
            expected_delay = 1
        else:
            args = (left,) if kind == "NOT" else (left, right)
            state = ordinary_state(kind, args, mask)
            expected_cost, expected_delay, _arity = GATE_SPECS[kind]
            raw_arrival = max(
                [states[index].arrival for index in left_ids + right_ids],
                default=0,
            ) + expected_delay
            state = State(state.bits, state.driven, state.conflict, raw_arrival)
        if int(item.get("cost", -1)) != expected_cost:
            raise RuntimeError(f"physical witness cost mismatch at slot {expected_slot}")
        if state.arrival > int(item.get("depth_upper_bound", state.arrival)):
            raise RuntimeError(f"physical witness deadline mismatch at slot {expected_slot}")
        direct = set(index for index in left_ids + right_ids if index >= len(source_states))
        closure = set(direct)
        for index in direct:
            closure.update(dependencies[index])
        states.append(state)
        dependencies.append(frozenset(closure))
        costs.append(expected_cost)
        component_records.append(
            {
                "slot": expected_slot,
                "source": expected_source,
                "kind": kind,
                "left_bus": left_ids,
                "right_bus": right_ids,
                "cost": expected_cost,
                "arrival": state.arrival,
                "value_sha256": packed_sha(state.bits) if mask == ALL else None,
                "driven_sha256": packed_sha(state.driven) if mask == ALL else None,
                "conflict_rows": state.conflict.bit_count(),
                "z_rows": ((~state.driven) & mask).bit_count(),
                "cone_gate": expected_cost
                + sum(costs[index] for index in dependencies[-1]),
            }
        )

    normalized_outputs = [normalize_bus(bus) for bus in output_buses]
    output_states = [
        bus_state(f"output{index}", bus)
        for index, bus in enumerate(normalized_outputs)
    ]
    partition_violations = []
    for index, (left_name, left_bus) in enumerate(physical_buses):
        if not left_bus:
            continue
        for right_name, right_bus in physical_buses[index + 1 :]:
            shared = left_bus & right_bus
            if shared and left_bus != right_bus:
                partition_violations.append(
                    {
                        "left": left_name,
                        "right": right_name,
                        "shared_sources": sorted(shared),
                        "left_only": sorted(left_bus - right_bus),
                        "right_only": sorted(right_bus - left_bus),
                    }
                )
    return {
        "states": states,
        "components": component_records,
        "output_buses": normalized_outputs,
        "output_states": output_states,
        "bus_records": bus_records,
        "partition_violations": partition_violations,
        "actual_gate": sum(int(item["cost"]) for item in network),
    }


def source_state(bits: int, arrival: int, *, driven: int = ALL) -> State:
    return State(bits & ALL, driven & ALL, 0, int(arrival))
