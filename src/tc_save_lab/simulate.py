"""Strict offline simulation for reviewed combinational components."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from itertools import product

from .analysis import wire_points
from .model import Circuit
from .pins import I, O, T, positioned_pins


SOURCE_KINDS = {60, 61, 63, 64, 65}
SINK_KINDS = {40, 68, 69, 73, 74, 75}
CONSTANT_KINDS = {1, 2, 46}


class SimulationError(ValueError):
    """Raised when a circuit cannot be simulated without guessing."""


class _UnionFind:
    def __init__(self, size: int):
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
class _CompiledCircuit:
    pin_networks: dict[tuple[int, str], int]
    source_widths: dict[str, int]


def _compile(circuit: Circuit) -> _CompiledCircuit:
    owners: dict[tuple[int, int], list[int]] = defaultdict(list)
    endpoints: list[tuple[tuple[int, int], tuple[int, int]]] = []
    for wire_index, wire in enumerate(circuit.wires):
        points = wire_points(wire)
        pair = (points[0], points[-1])
        endpoints.append(pair)
        owners[pair[0]].append(wire_index)
        owners[pair[1]].append(wire_index)

    union_find = _UnionFind(len(circuit.wires))
    for wire_indices in owners.values():
        for wire_index in wire_indices[1:]:
            union_find.union(wire_indices[0], wire_index)

    network_by_position: dict[tuple[int, int], int] = {}
    for wire_index, pair in enumerate(endpoints):
        network = union_find.find(wire_index)
        network_by_position[pair[0]] = network
        network_by_position[pair[1]] = network

    pin_networks: dict[tuple[int, str], int] = {}
    for component_index, component in enumerate(circuit.components):
        pins = positioned_pins(component, component_index)
        if not pins:
            raise SimulationError(f"component kind {component.kind} has no reviewed pin schema")
        for pin in pins:
            try:
                pin_networks[(component_index, pin.name)] = network_by_position[pin.position]
            except KeyError as exc:
                raise SimulationError(
                    f"component {component.permanent_id} pin {pin.name} is unconnected"
                ) from exc
    source_widths: dict[str, int] = {}
    for component_index, component in enumerate(circuit.components):
        if component.kind not in SOURCE_KINDS:
            continue
        key = component.user_label or str(component.permanent_id)
        output_pins = [
            pin
            for pin in positioned_pins(component, component_index)
            if pin.direction in {O, T}
        ]
        source_widths[key] = sum(pin.width for pin in output_pins)
    return _CompiledCircuit(pin_networks=pin_networks, source_widths=source_widths)


def _mask(width: int) -> int:
    return (1 << width) - 1


def _signed(value: int, width: int) -> int:
    value &= _mask(width)
    sign = 1 << (width - 1)
    return value - (1 << width) if value & sign else value


def _evaluate(kind: int, width: int, values: dict[str, int]) -> dict[str, int]:
    mask = _mask(width)
    if kind == 3:
        return {"out": (~values["in"]) & 1}
    if kind in {4, 5}:
        return {"out": values["in0"] & values["in1"] & values.get("in2", 1)}
    if kind == 6:
        return {"out": (~(values["in0"] & values["in1"])) & 1}
    if kind in {7, 8}:
        return {"out": values["in0"] | values["in1"] | values.get("in2", 0)}
    if kind == 9:
        return {"out": (~(values["in0"] | values["in1"])) & 1}
    if kind == 10:
        return {"out": values["in0"] ^ values["in1"]}
    if kind == 11:
        return {"out": (~(values["in0"] ^ values["in1"])) & 1}
    if kind == 15:
        total = values["carry_in"] + values["in0"] + values["in1"]
        return {"sum": total & 1, "carry_out": (total >> 1) & 1}
    if kind == 16:
        return {"out": sum((values[f"in{index}"] & 1) << index for index in range(8))}
    if kind == 17:
        return {f"out{index}": (values["in"] >> index) & 1 for index in range(8)}
    if kind == 18:
        return {"out": (~values["in"]) & mask}
    if kind == 19:
        return {"out": (values["in0"] | values["in1"]) & mask}
    if kind == 20:
        return {"out": (values["in0"] & values["in1"]) & mask}
    if kind == 21:
        return {"out": (~(values["in0"] & values["in1"])) & mask}
    if kind == 22:
        return {"out": (~(values["in0"] | values["in1"])) & mask}
    if kind == 23:
        return {"out": (values["in0"] ^ values["in1"]) & mask}
    if kind == 24:
        return {"out": (~(values["in0"] ^ values["in1"])) & mask}
    if kind == 26:
        return {"out": int(values["in0"] == values["in1"])}
    if kind == 27:
        return {"out": int(values["in0"] < values["in1"])}
    if kind == 28:
        return {"out": int(_signed(values["in0"], width) < _signed(values["in1"], width))}
    if kind == 29:
        return {"out": (-values["in"]) & mask}
    if kind == 30:
        total = values["carry_in"] + values["in0"] + values["in1"]
        return {"out": total & mask, "carry_out": (total >> width) & 1}
    if kind == 33:
        return {"out": (values["in"] << values["shift"]) & mask}
    if kind == 34:
        return {"out": (values["in"] & mask) >> values["shift"]}
    if kind == 37:
        return {"out": (_signed(values["in"], width) >> values["shift"]) & mask}
    if kind == 42:
        return {"out": values["in1"] if values["select"] else values["in0"]}
    if kind == 43:
        selected = values["select"] & 1
        return {"out0": 1 - selected, "out1": selected}
    if kind == 44:
        selected = (values["select0"] & 1) | ((values["select1"] & 1) << 1)
        return {f"out{index}": int(index == selected) for index in range(4)}
    if kind == 45:
        if values["disable"] & 1:
            return {f"out{index}": 0 for index in range(8)}
        selected = sum((values[f"select{index}"] & 1) << index for index in range(3))
        return {f"out{index}": int(index == selected) for index in range(8)}
    raise SimulationError(f"component kind {kind} has no reviewed combinational semantics")


def _simulate_compiled(
    circuit: Circuit,
    compiled: _CompiledCircuit,
    inputs: dict[str, int],
) -> dict[str, int]:
    network_values: dict[int, int] = {}

    def assign(component_index: int, pin_name: str, value: int) -> None:
        network = compiled.pin_networks[(component_index, pin_name)]
        previous = network_values.get(network)
        if previous is not None and previous != value:
            raise SimulationError(f"conflicting drivers on network {network}")
        network_values[network] = value

    pending: set[int] = set()
    for component_index, component in enumerate(circuit.components):
        pins = positioned_pins(component, component_index)
        if component.kind in SOURCE_KINDS:
            key = component.user_label or str(component.permanent_id)
            if key not in inputs:
                raise SimulationError(f"missing value for level input {key!r}")
            raw_value = inputs[key]
            output_pins = [pin for pin in pins if pin.direction in {O, T}]
            if len(output_pins) == 1:
                assign(component_index, output_pins[0].name, raw_value & _mask(output_pins[0].width))
            else:
                for bit, pin in enumerate(output_pins):
                    assign(component_index, pin.name, (raw_value >> bit) & 1)
        elif component.kind in CONSTANT_KINDS:
            value = component.init_data if component.kind == 46 else int(component.kind == 2)
            assign(component_index, "out", value & _mask(component.word_size))
        elif component.kind not in SINK_KINDS:
            pending.add(component_index)

    while pending:
        progressed = False
        for component_index in tuple(pending):
            component = circuit.components[component_index]
            pins = positioned_pins(component, component_index)
            input_pins = [pin for pin in pins if pin.direction == I]
            if not all(compiled.pin_networks[(component_index, pin.name)] in network_values for pin in input_pins):
                continue
            values = {
                pin.name: network_values[compiled.pin_networks[(component_index, pin.name)]]
                for pin in input_pins
            }
            for name, value in _evaluate(component.kind, component.word_size, values).items():
                assign(component_index, name, value)
            pending.remove(component_index)
            progressed = True
        if not progressed:
            unresolved = [circuit.components[index].permanent_id for index in sorted(pending)]
            raise SimulationError(f"unresolved combinational components: {unresolved}")

    outputs: dict[str, int] = {}
    for component_index, component in enumerate(circuit.components):
        if component.kind not in SINK_KINDS:
            continue
        key = component.user_label or str(component.permanent_id)
        pins = [
            pin
            for pin in positioned_pins(component, component_index)
            if pin.direction == I
        ]
        if len(pins) == 1:
            outputs[key] = network_values[compiled.pin_networks[(component_index, pins[0].name)]]
        else:
            outputs[key] = sum(
                (network_values[compiled.pin_networks[(component_index, pin.name)]] & 1) << bit
                for bit, pin in enumerate(pins)
            )
    return outputs


def simulate_combinational(circuit: Circuit, inputs: dict[str, int]) -> dict[str, int]:
    """Evaluate one stable combinational state and return labeled level outputs."""

    return _simulate_compiled(circuit, _compile(circuit), inputs)


def verify_truth_table(
    circuit: Circuit,
    *,
    inputs: dict[str, int],
    output_label: str | tuple[str, ...],
    expected: object,
) -> int:
    """Exhaustively verify labeled inputs without rebuilding the network per vector.

    ``inputs`` maps each level-input label to its bit width. ``expected`` receives
    one ``dict[str, int]`` containing the current vector and returns the expected
    packed value for ``output_label``.
    """

    if not callable(expected):
        raise TypeError("expected must be callable")
    if any(width <= 0 for width in inputs.values()):
        raise ValueError("input widths must be positive")

    labels = tuple(inputs)
    compiled = _compile(circuit)
    if inputs != compiled.source_widths:
        raise SimulationError(
            f"input schema mismatch: expected {compiled.source_widths}, got {inputs}"
        )
    tested = 0
    for raw_values in product(*(range(1 << inputs[label]) for label in labels)):
        vector = dict(zip(labels, raw_values))
        actual_outputs = _simulate_compiled(circuit, compiled, vector)
        if isinstance(output_label, str):
            actual: object = actual_outputs[output_label]
        else:
            actual = {label: actual_outputs[label] for label in output_label}
        wanted = expected(vector)
        if actual != wanted:
            rendered = ", ".join(f"{label}={vector[label]}" for label in labels)
            raise SimulationError(
                f"truth table mismatch at {rendered}: expected {wanted}, got {actual}"
            )
        tested += 1
    return tested


def verify_single_input_truth_table(
    circuit: Circuit,
    *,
    input_label: str,
    input_width: int,
    output_label: str,
    expected: object,
) -> int:
    """Exhaustively verify a single packed input against a reviewed oracle."""

    return verify_truth_table(
        circuit,
        inputs={input_label: input_width},
        output_label=output_label,
        expected=lambda values: expected(values[input_label]),
    )
