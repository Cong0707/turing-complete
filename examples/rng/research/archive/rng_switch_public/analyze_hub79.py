"""Bit-parallel audit of the public Hub 79 tri-state adder.

The circuit was published by the same group as the current RNG leaders.  This
script reconstructs endpoint networks, evaluates all 2^17 relevant inputs,
and reports the multi-driver buses without starting Turing Complete.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from tc_save_lab.analysis import wire_points
from tc_save_lab.codec import decode_v15
from tc_save_lab.pins import I, O, T, PositionedPin, positioned_pins


ROOT = Path(__file__).resolve().parents[2]
CIRCUIT_PATH = (
    ROOT
    / ".research"
    / "rng_public_artifacts"
    / "hub-79-adder"
    / "main"
    / "circuit.data"
)
VARIABLES = 17
ASSIGNMENTS = 1 << VARIABLES
ALL = (1 << ASSIGNMENTS) - 1


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
    """Return a packed truth table whose bit n is input index of n."""

    if index < 3:
        byte = (0xAA, 0xCC, 0xF0)[index]
        return int.from_bytes(bytes([byte]) * (ASSIGNMENTS // 8), "little")
    block = 1 << (index - 3)
    data = (bytes(block) + bytes([0xFF]) * block) * (
        ASSIGNMENTS // (16 * block)
    )
    return int.from_bytes(data, "little")


def compile_circuit() -> tuple[object, Compiled]:
    circuit = decode_v15(CIRCUIT_PATH.read_bytes())
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
    endpoint_positions = set(network_by_position)

    def component_pins(index: int) -> tuple[PositionedPin, ...]:
        component = circuit.components[index]
        if component.kind not in {79, 81}:
            return positioned_pins(component, index)
        candidates = {
            span: positioned_pins(component, index, foundry_port_span=span)
            for span in (1, 3)
        }
        connected = [
            span
            for span, candidate in candidates.items()
            if candidate[0].position in endpoint_positions
        ]
        return candidates[connected[0] if len(connected) == 1 else 3]

    pins: dict[tuple[int, str], PositionedPin] = {}
    pin_network: dict[tuple[int, str], int] = {}
    network_pins: dict[int, list[PositionedPin]] = defaultdict(list)
    for index in range(len(circuit.components)):
        for pin in component_pins(index):
            pins[(index, pin.name)] = pin
            network = network_by_position.get(pin.position)
            if network is not None:
                pin_network[(index, pin.name)] = network
                network_pins[network].append(pin)
            # Foundry accepts an intentionally unconnected scalar receiver as
            # zero.  Hub 79 uses that rule for Maker2.in0 before extracting
            # its carry bit again.
    return circuit, Compiled(
        pins=pins,
        pin_network=pin_network,
        network_pins={key: tuple(value) for key, value in network_pins.items()},
    )


def normal(bits: tuple[int, ...], depth: int) -> Signal:
    return Signal(tuple(value & ALL for value in bits), ALL, depth)


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
        for bit in range(width):
            value = driver.bits[bit] if bit < len(driver.bits) else 0
            ones[bit] |= driver.driven & value
            zeros[bit] |= driver.driven & (~value & ALL)
    for one, zero in zip(ones, zeros):
        conflict |= one & zero
    return Signal(tuple(ones), driven, depth, conflict)


def evaluate() -> tuple[object, Compiled, dict[int, Signal], dict[tuple[int, str], Signal]]:
    circuit, compiled = compile_circuit()
    variables = tuple(variable(index) for index in range(VARIABLES))
    outputs: dict[tuple[int, str], Signal] = {}
    networks: dict[int, Signal] = {}

    for index, component in enumerate(circuit.components):
        if component.kind == 79:
            if component.user_label == "A":
                bits = variables[:8]
            elif component.user_label == "B":
                bits = variables[8:16]
            elif component.user_label == "Cin":
                bits = (variables[16],) + (0,) * 7
            else:
                raise RuntimeError(f"unknown public-adder source {component.user_label!r}")
            outputs[(index, "in")] = normal(tuple(bits), 0)
        elif component.kind == 2:
            outputs[(index, "out")] = normal((ALL,), 0)

    pending = {
        index
        for index, component in enumerate(circuit.components)
        if component.kind not in {2, 79, 81}
    }
    while pending:
        progress = False
        for network, pins in compiled.network_pins.items():
            if network in networks:
                continue
            drivers = [pin for pin in pins if pin.direction in {O, T}]
            if drivers and all((pin.component_index, pin.name) in outputs for pin in drivers):
                networks[network] = resolve(
                    [outputs[(pin.component_index, pin.name)] for pin in drivers]
                )
                progress = True

        for index in tuple(pending):
            component = circuit.components[index]
            input_pins = [
                pin
                for (component_index, _), pin in compiled.pins.items()
                if component_index == index and pin.direction == I
            ]
            if not all(
                (index, pin.name) not in compiled.pin_network
                or compiled.pin_network[(index, pin.name)] in networks
                for pin in input_pins
            ):
                continue
            values = {
                pin.name: (
                    networks[compiled.pin_network[(index, pin.name)]]
                    if (index, pin.name) in compiled.pin_network
                    else normal((0,) * pin.width, 0)
                )
                for pin in input_pins
            }
            input_depth = max((signal.depth for signal in values.values()), default=0)

            def bit(name: str, offset: int = 0) -> int:
                signal = values[name]
                return signal.bits[offset] if offset < len(signal.bits) else 0

            kind = component.kind
            if kind == 3:
                result = {"out": normal(((~bit("in")) & ALL,), input_depth + 1)}
            elif kind == 4:
                result = {"out": normal((bit("in0") & bit("in1"),), input_depth + 1)}
            elif kind == 6:
                result = {"out": normal(((~(bit("in0") & bit("in1"))) & ALL,), input_depth + 1)}
            elif kind == 7:
                result = {"out": normal((bit("in0") | bit("in1"),), input_depth + 1)}
            elif kind == 9:
                result = {"out": normal(((~(bit("in0") | bit("in1"))) & ALL,), input_depth + 1)}
            elif kind == 12:
                enable = bit("enable")
                result = {
                    "out": Signal((bit("in"),), enable, input_depth + 1)
                }
            elif kind == 16:
                result = {
                    "out": normal(
                        tuple(bit(f"in{offset}") for offset in range(8)),
                        input_depth,
                    )
                }
            elif kind == 17:
                result = {
                    f"out{offset}": normal((bit("in", offset),), input_depth)
                    for offset in range(8)
                }
            elif kind == 109:
                result = {
                    f"out{offset}": normal((bit("in", offset),), input_depth)
                    for offset in range(2)
                }
            elif kind == 111:
                result = {
                    "out": normal((bit("in0"), bit("in1")), input_depth)
                }
            else:
                raise RuntimeError(f"unsupported public-adder component kind {kind}")
            outputs.update({(index, name): signal for name, signal in result.items()})
            pending.remove(index)
            progress = True
        if not progress:
            raise RuntimeError(f"evaluation stalled with components {sorted(pending)}")

    # Resolve output-only networks after the final components were evaluated.
    for network, pins in compiled.network_pins.items():
        if network in networks:
            continue
        drivers = [pin for pin in pins if pin.direction in {O, T}]
        if drivers and all((pin.component_index, pin.name) in outputs for pin in drivers):
            networks[network] = resolve(
                [outputs[(pin.component_index, pin.name)] for pin in drivers]
            )
    return circuit, compiled, networks, outputs


def dependency_support(table: int, variables: tuple[int, ...]) -> tuple[int, ...]:
    support = []
    for index, truth in enumerate(variables):
        shift = 1 << index
        low_mask = ~truth & ALL
        if ((table ^ (table >> shift)) & low_mask) != 0:
            support.append(index)
    return tuple(support)


def main() -> None:
    circuit, compiled, networks, _outputs = evaluate()
    variables = tuple(variable(index) for index in range(VARIABLES))
    a = variables[:8]
    b = variables[8:16]
    carry = variables[16]
    expected_sum = []
    labels: dict[int, str] = {value: f"A{index}" for index, value in enumerate(a)}
    labels.update({value: f"B{index}" for index, value in enumerate(b)})
    labels[carry] = "Cin"
    for index, (left, right) in enumerate(zip(a, b)):
        propagate = left ^ right
        generate = left & right
        labels.setdefault(propagate, f"P{index}")
        labels.setdefault(generate, f"G{index}")
        labels.setdefault((~(left | right)) & ALL, f"NOR{index}")
        total = propagate ^ carry
        expected_sum.append(total)
        labels.setdefault(carry, f"C{index}")
        labels.setdefault(total, f"S{index}")
        carry = generate | (propagate & carry)
    labels.setdefault(carry, "Cout")

    sum_component = next(
        index
        for index, component in enumerate(circuit.components)
        if component.kind == 81 and component.user_label == "sum"
    )
    cout_component = next(
        index
        for index, component in enumerate(circuit.components)
        if component.kind == 81 and component.user_label == "Cout"
    )
    sum_signal = networks[compiled.pin_network[(sum_component, "out")]]
    cout_signal = networks[compiled.pin_network[(cout_component, "out")]]
    if sum_signal.bits[:8] != tuple(expected_sum):
        raise RuntimeError("Hub 79 sum truth table mismatch")
    if cout_signal.bits[0] != carry:
        raise RuntimeError("Hub 79 carry truth table mismatch")

    conflicts = sum(signal.conflict.bit_count() for signal in networks.values())
    if conflicts:
        raise RuntimeError(f"Hub 79 has {conflicts} packed short-circuit cases")
    print(
        f"verified gate={circuit.gate} delay={circuit.delay} "
        f"components={len(circuit.components)} wires={len(circuit.wires)} "
        f"vectors={ASSIGNMENTS}"
    )

    for network, pins in sorted(compiled.network_pins.items()):
        switch_drivers = [
            pin
            for pin in pins
            if pin.direction == T and circuit.components[pin.component_index].kind == 12
        ]
        if len(switch_drivers) < 2:
            continue
        signal = networks[network]
        sinks = [
            f"{pin.component_index}:{circuit.components[pin.component_index].kind}:{pin.name}"
            for pin in pins
            if pin.direction == I
        ]
        table = signal.bits[0]
        print(
            f"net={network:03} switches={len(switch_drivers)} depth={signal.depth} "
            f"z={((~signal.driven) & ALL).bit_count()} "
            f"ones={table.bit_count()} label={labels.get(table, '-')} "
            f"support={dependency_support(table, variables)} "
            f"sinks={','.join(sinks)}"
        )


if __name__ == "__main__":
    main()
