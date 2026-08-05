"""Read-only bit-parallel audit for the user-supplied Byte Adder samples.

The three samples are standalone v15 campaign circuits.  This analyzer keeps
tri-state drive masks separate from Boolean zero, reports BUS conflicts, and
only normalizes Z when an ordinary component (including a free maker/splitter)
reads it.  It never writes a circuit or touches the live save.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import sys


PROJECT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT / "src"))

from tc_save_lab.analysis import wire_points  # noqa: E402
from tc_save_lab.codec import decode_v15  # noqa: E402
from tc_save_lab.pins import I, O, T, PositionedPin, positioned_pins  # noqa: E402


VARIABLE_COUNT = 17
ASSIGNMENT_COUNT = 1 << VARIABLE_COUNT
ALL = (1 << ASSIGNMENT_COUNT) - 1
TABLE_BYTES = ASSIGNMENT_COUNT // 8

INPUT_KIND = 61
OUTPUT_KIND = 69
SWITCH_KIND = 12

KIND_NAMES = {
    2: "ON",
    3: "NOT",
    4: "AND",
    6: "NAND",
    7: "OR",
    9: "NOR",
    12: "SWITCH",
    16: "MAKER8",
    17: "SPLITTER8",
    61: "INPUT",
    69: "OUTPUT",
    109: "SPLITTER2",
    111: "MAKER2",
}


class UnionFind:
    def __init__(self, size: int) -> None:
        self.parent = list(range(size))

    def find(self, value: int) -> int:
        while self.parent[value] != value:
            self.parent[value] = self.parent[self.parent[value]]
            value = self.parent[value]
        return value

    def union(self, left: int, right: int) -> None:
        left = self.find(left)
        right = self.find(right)
        if left != right:
            self.parent[right] = left


@dataclass(frozen=True)
class Signal:
    bits: tuple[int, ...]
    driven: int
    depth: int
    conflict: int = 0


@dataclass(frozen=True)
class Compiled:
    pins: dict[tuple[int, str], PositionedPin]
    pin_network: dict[tuple[int, str], int]
    network_pins: dict[int, tuple[PositionedPin, ...]]


def variable(index: int) -> int:
    if index < 3:
        byte = (0xAA, 0xCC, 0xF0)[index]
        return int.from_bytes(bytes([byte]) * TABLE_BYTES, "little")
    block = 1 << (index - 3)
    data = (bytes(block) + bytes([0xFF]) * block) * (
        ASSIGNMENT_COUNT // (16 * block)
    )
    return int.from_bytes(data, "little")


def normal(bits: tuple[int, ...], depth: int, conflict: int = 0) -> Signal:
    return Signal(tuple(value & ALL for value in bits), ALL, depth, conflict)


def resolve(drivers: list[Signal]) -> Signal:
    width = max(len(driver.bits) for driver in drivers)
    ones = [0] * width
    zeros = [0] * width
    driven = 0
    conflict = 0
    depth = 0
    for driver in drivers:
        depth = max(depth, driver.depth)
        driven |= driver.driven
        conflict |= driver.conflict
        for bit_index in range(width):
            value = driver.bits[bit_index] if bit_index < len(driver.bits) else 0
            ones[bit_index] |= driver.driven & value
            zeros[bit_index] |= driver.driven & (~value & ALL)
    for one, zero in zip(ones, zeros):
        conflict |= one & zero
    return Signal(tuple(ones), driven, depth, conflict)


def compile_circuit(circuit) -> Compiled:
    endpoints: list[tuple[tuple[int, int], tuple[int, int]]] = []
    owners: dict[tuple[int, int], list[int]] = defaultdict(list)
    for wire_index, wire in enumerate(circuit.wires):
        points = wire_points(wire)
        pair = (points[0], points[-1])
        endpoints.append(pair)
        owners[pair[0]].append(wire_index)
        owners[pair[1]].append(wire_index)

    union_find = UnionFind(len(circuit.wires))
    for wire_indices in owners.values():
        for wire_index in wire_indices[1:]:
            union_find.union(wire_indices[0], wire_index)

    network_by_position = {
        position: union_find.find(wire_index)
        for wire_index, pair in enumerate(endpoints)
        for position in pair
    }
    pins: dict[tuple[int, str], PositionedPin] = {}
    pin_network: dict[tuple[int, str], int] = {}
    network_pins: dict[int, list[PositionedPin]] = defaultdict(list)
    for component_index, component in enumerate(circuit.components):
        component_pins = positioned_pins(component, component_index)
        if not component_pins:
            raise RuntimeError(
                f"unsupported component kind {component.kind} at {component_index}"
            )
        for pin in component_pins:
            pins[(component_index, pin.name)] = pin
            network = network_by_position.get(pin.position)
            if network is not None:
                pin_network[(component_index, pin.name)] = network
                network_pins[network].append(pin)
    return Compiled(
        pins=pins,
        pin_network=pin_network,
        network_pins={key: tuple(value) for key, value in network_pins.items()},
    )


def _source_bits(label: str, variables: tuple[int, ...]) -> tuple[int, ...]:
    if label == "A":
        return variables[:8]
    if label == "B":
        return variables[8:16]
    if label == "Carry in":
        return (variables[16],)
    raise RuntimeError(f"unknown Byte Adder input label {label!r}")


def evaluate(circuit, compiled: Compiled):
    variables = tuple(variable(index) for index in range(VARIABLE_COUNT))
    outputs: dict[tuple[int, str], Signal] = {}
    networks: dict[int, Signal] = {}

    for component_index, component in enumerate(circuit.components):
        if component.kind == INPUT_KIND:
            outputs[(component_index, "value")] = normal(
                _source_bits(component.user_label, variables), 0
            )
        elif component.kind == 2:
            outputs[(component_index, "out")] = normal((ALL,), 0)

    pending = {
        index
        for index, component in enumerate(circuit.components)
        if component.kind not in {2, INPUT_KIND, OUTPUT_KIND}
    }
    while pending:
        progress = False
        for network, pins in compiled.network_pins.items():
            if network in networks:
                continue
            drivers = [pin for pin in pins if pin.direction in {O, T}]
            if drivers and all(
                (pin.component_index, pin.name) in outputs for pin in drivers
            ):
                networks[network] = resolve(
                    [outputs[(pin.component_index, pin.name)] for pin in drivers]
                )
                progress = True

        for component_index in tuple(pending):
            component = circuit.components[component_index]
            input_pins = [
                pin
                for (index, _), pin in compiled.pins.items()
                if index == component_index and pin.direction == I
            ]
            if not all(
                (component_index, pin.name) not in compiled.pin_network
                or compiled.pin_network[(component_index, pin.name)] in networks
                for pin in input_pins
            ):
                continue
            values = {
                pin.name: (
                    networks[compiled.pin_network[(component_index, pin.name)]]
                    if (component_index, pin.name) in compiled.pin_network
                    else normal((0,) * pin.width, 0)
                )
                for pin in input_pins
            }
            input_depth = max((signal.depth for signal in values.values()), default=0)
            input_conflict = 0
            for signal in values.values():
                input_conflict |= signal.conflict

            def bit(name: str, offset: int = 0) -> int:
                signal = values[name]
                return signal.bits[offset] if offset < len(signal.bits) else 0

            kind = component.kind
            if kind == 3:
                result = {
                    "out": normal(
                        ((~bit("in")) & ALL,), input_depth + 1, input_conflict
                    )
                }
            elif kind == 4:
                result = {
                    "out": normal(
                        (bit("in0") & bit("in1"),), input_depth + 1, input_conflict
                    )
                }
            elif kind == 6:
                result = {
                    "out": normal(
                        ((~(bit("in0") & bit("in1"))) & ALL,),
                        input_depth + 1,
                        input_conflict,
                    )
                }
            elif kind == 7:
                result = {
                    "out": normal(
                        (bit("in0") | bit("in1"),), input_depth + 1, input_conflict
                    )
                }
            elif kind == 9:
                result = {
                    "out": normal(
                        ((~(bit("in0") | bit("in1"))) & ALL,),
                        input_depth + 1,
                        input_conflict,
                    )
                }
            elif kind == SWITCH_KIND:
                enable = bit("enable")
                result = {
                    "out": Signal(
                        (bit("in"),),
                        enable,
                        input_depth + 1,
                        input_conflict,
                    )
                }
            elif kind == 16:
                result = {
                    "out": normal(
                        tuple(bit(f"in{offset}") for offset in range(8)),
                        input_depth,
                        input_conflict,
                    )
                }
            elif kind == 17:
                result = {
                    f"out{offset}": normal(
                        (bit("in", offset),), input_depth, input_conflict
                    )
                    for offset in range(8)
                }
            elif kind == 109:
                result = {
                    f"out{offset}": normal(
                        (bit("in", offset),), input_depth, input_conflict
                    )
                    for offset in range(2)
                }
            elif kind == 111:
                result = {
                    "out": normal(
                        (bit("in0"), bit("in1")), input_depth, input_conflict
                    )
                }
            else:
                raise RuntimeError(
                    f"unsupported sample component kind {kind} at {component_index}"
                )
            outputs.update(
                {
                    (component_index, name): signal
                    for name, signal in result.items()
                }
            )
            pending.remove(component_index)
            progress = True
        if not progress:
            raise RuntimeError(f"evaluation stalled at components {sorted(pending)}")

    for network, pins in compiled.network_pins.items():
        if network in networks:
            continue
        drivers = [pin for pin in pins if pin.direction in {O, T}]
        if drivers and all(
            (pin.component_index, pin.name) in outputs for pin in drivers
        ):
            networks[network] = resolve(
                [outputs[(pin.component_index, pin.name)] for pin in drivers]
            )
    return variables, networks, outputs


def _truth_hash(value: int) -> str:
    return sha256(value.to_bytes(TABLE_BYTES, "little")).hexdigest()


def _support(value: int, variables: tuple[int, ...]) -> list[int]:
    result = []
    for index, truth in enumerate(variables):
        shift = 1 << index
        low_mask = ~truth & ALL
        if ((value ^ (value >> shift)) & low_mask) != 0:
            result.append(index)
    return result


def _semantic_labels(variables: tuple[int, ...]) -> dict[int, list[str]]:
    labels: dict[int, list[str]] = defaultdict(list)

    def add(value: int, label: str) -> None:
        if label not in labels[value]:
            labels[value].append(label)

    a = variables[:8]
    b = variables[8:16]
    carry = variables[16]
    add(carry, "C0/Cin")
    add((~carry) & ALL, "nC0/nCin")
    for bit_index, (left, right) in enumerate(zip(a, b)):
        generate = left & right
        kill = (~(left | right)) & ALL
        propagate = left ^ right
        value_or = left | right
        not_generate = (~generate) & ALL
        add(left, f"A{bit_index}")
        add(right, f"B{bit_index}")
        add(generate, f"G{bit_index}")
        add(kill, f"Q{bit_index}")
        add(propagate, f"P{bit_index}")
        add(value_or, f"V{bit_index}")
        add(not_generate, f"nG{bit_index}")
        total = propagate ^ carry
        add(total, f"S{bit_index}")
        carry = generate | (propagate & carry)
        add(carry, f"C{bit_index + 1}")
        add((~carry) & ALL, f"nC{bit_index + 1}")
    add(carry, "Cout")
    return labels


def _pin_record(pin: PositionedPin) -> dict[str, object]:
    return {
        "component_index": pin.component_index,
        "component_kind": pin.component_kind,
        "pin": pin.name,
        "direction": pin.direction,
        "width": pin.width,
    }


def audit(path: Path) -> dict[str, object]:
    payload = path.read_bytes()
    circuit = decode_v15(payload)
    compiled = compile_circuit(circuit)
    variables, networks, outputs = evaluate(circuit, compiled)
    semantic = _semantic_labels(variables)

    output_values: dict[str, tuple[int, ...]] = {}
    output_depths: dict[str, int] = {}
    for component_index, component in enumerate(circuit.components):
        if component.kind != OUTPUT_KIND:
            continue
        network = compiled.pin_network[(component_index, "value")]
        signal = networks[network]
        output_values[component.user_label] = signal.bits
        output_depths[component.user_label] = signal.depth

    expected_sum = tuple(next(value for value, names in semantic.items() if f"S{i}" in names) for i in range(8))
    expected_carry = next(value for value, names in semantic.items() if "Cout" in names)
    sum_bits = output_values.get("Output")
    carry_bits = output_values.get("Carry out")
    if sum_bits != expected_sum:
        raise RuntimeError(f"{path}: sum truth table mismatch")
    if carry_bits != (expected_carry,):
        raise RuntimeError(f"{path}: carry truth table mismatch")

    conflict_union = 0
    for signal in networks.values():
        conflict_union |= signal.conflict
    if conflict_union:
        raise RuntimeError(
            f"{path}: BUS conflicts on {conflict_union.bit_count()} assignments"
        )

    kind_counts: dict[str, int] = defaultdict(int)
    derived_gate = 0
    for component in circuit.components:
        kind_counts[KIND_NAMES.get(component.kind, f"kind-{component.kind}")] += 1
        if component.kind in {3, 4, 6, 7, 9}:
            derived_gate += 1
        elif component.kind == SWITCH_KIND:
            derived_gate += 2

    component_records = []
    for component_index, component in enumerate(circuit.components):
        output_records = []
        for (index, pin_name), signal in outputs.items():
            if index != component_index:
                continue
            output_records.append(
                {
                    "pin": pin_name,
                    "network": compiled.pin_network.get((component_index, pin_name)),
                    "depth": signal.depth,
                    "driven_rows": signal.driven.bit_count(),
                    "z_rows": ASSIGNMENT_COUNT - signal.driven.bit_count(),
                    "truth": [
                        {
                            "sha256": _truth_hash(value),
                            "support": _support(value, variables),
                            "semantic_labels": semantic.get(value, []),
                        }
                        for value in signal.bits
                    ],
                }
            )
        input_networks = {
            pin.name: compiled.pin_network.get((component_index, pin.name))
            for (index, _), pin in compiled.pins.items()
            if index == component_index and pin.direction == I
        }
        component_records.append(
            {
                "index": component_index,
                "permanent_id": component.permanent_id,
                "kind": component.kind,
                "op": KIND_NAMES.get(component.kind, f"kind-{component.kind}"),
                "position": list(component.position),
                "input_networks": input_networks,
                "outputs": output_records,
            }
        )

    network_records = []
    for network, pins in sorted(compiled.network_pins.items()):
        signal = networks.get(network)
        if signal is None:
            continue
        network_records.append(
            {
                "network": network,
                "depth": signal.depth,
                "driver_count": sum(pin.direction in {O, T} for pin in pins),
                "receiver_count": sum(pin.direction == I for pin in pins),
                "drivers": [_pin_record(pin) for pin in pins if pin.direction in {O, T}],
                "receivers": [_pin_record(pin) for pin in pins if pin.direction == I],
                "driven_rows": signal.driven.bit_count(),
                "z_rows": ASSIGNMENT_COUNT - signal.driven.bit_count(),
                "truth": [
                    {
                        "sha256": _truth_hash(value),
                        "support": _support(value, variables),
                        "semantic_labels": semantic.get(value, []),
                    }
                    for value in signal.bits
                ],
            }
        )

    return {
        "schema": "byte-adder-user-frontier-sample-audit-v1",
        "source": {
            "path": str(path.resolve()),
            "size": len(payload),
            "sha256": sha256(payload).hexdigest(),
        },
        "declared": {
            "gate": circuit.gate,
            "delay": circuit.delay,
            "energy": circuit.energy,
        },
        "derived": {
            "gate": derived_gate,
            "output_depths": output_depths,
            "max_output_depth": max(output_depths.values()),
            "truth_rows": ASSIGNMENT_COUNT,
            "mismatch_count": 0,
            "bus_conflict_rows": 0,
            "component_count": len(circuit.components),
            "wire_count": len(circuit.wires),
            "kind_counts": dict(sorted(kind_counts.items())),
        },
        "components": component_records,
        "networks": network_records,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    summaries = []
    for path in args.paths:
        report = audit(path)
        slug = path.parent.name.lower().replace(" ", "-")
        destination = args.output_dir / f"{slug}-audit.json"
        destination.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        summaries.append(
            {
                "path": str(path),
                "report": str(destination),
                "declared": report["declared"],
                "derived": report["derived"],
            }
        )
    print(json.dumps(summaries, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
