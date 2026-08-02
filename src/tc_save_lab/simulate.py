"""Strict offline simulation for reviewed combinational components."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from itertools import product
from typing import Iterable

from .analysis import wire_points
from .model import Circuit
from .pins import I, O, T, positioned_pins


SOURCE_KINDS = {60, 61, 63, 64, 65, 79}
SINK_KINDS = {40, 68, 69, 73, 74, 75, 77, 81}
CONSTANT_KINDS = {1, 2, 46}
CLOCKED_MEMORY_KINDS = {13, 55}
ARCHITECTURE_INPUT_KIND = 62
ARCHITECTURE_OUTPUT_KIND = 70


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
    network_driver_counts: dict[int, int]


@dataclass(frozen=True)
class ClockedTickResult:
    """Observable output events and memory state after one architecture tick."""

    outputs: dict[str, int]
    memory: dict[int, int]


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
            network = network_by_position.get(pin.position)
            if network is None:
                # A circuit may deliberately leave a fan-out output unused.
                # The running game accepts that topology; only an unconnected
                # receiver makes simulation impossible.
                if pin.direction == I:
                    raise SimulationError(
                        f"component {component.permanent_id} pin {pin.name} is unconnected"
                    )
                continue
            pin_networks[(component_index, pin.name)] = network
    source_widths: dict[str, int] = {}
    network_driver_counts: dict[int, int] = defaultdict(int)
    for component_index, component in enumerate(circuit.components):
        output_pins = tuple(
            pin
            for pin in positioned_pins(component, component_index)
            if pin.direction in {O, T}
        )
        for pin in output_pins:
            network = pin_networks.get((component_index, pin.name))
            if network is not None:
                network_driver_counts[network] += 1
        if component.kind in SOURCE_KINDS:
            key = component.user_label or str(component.permanent_id)
            source_widths[key] = sum(pin.width for pin in output_pins)
    return _CompiledCircuit(
        pin_networks=pin_networks,
        source_widths=source_widths,
        network_driver_counts=dict(network_driver_counts),
    )


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
    if kind == 97:
        return {
            "out": sum((values[f"in{index}"] & 0xFF) << (index * 8) for index in range(4))
        }
    if kind == 98:
        return {
            "out": sum((values[f"in{index}"] & 0xFF) << (index * 8) for index in range(8))
        }
    if kind == 99:
        return {
            f"out{index}": (values["in"] >> (index * 8)) & 0xFF
            for index in range(4)
        }
    if kind == 100:
        return {
            f"out{index}": (values["in"] >> (index * 8)) & 0xFF
            for index in range(8)
        }
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
    if kind == 49:
        value = values["in"] & mask
        return {"out": width if value == 0 else width - value.bit_length()}
    raise SimulationError(f"component kind {kind} has no reviewed combinational semantics")


def _simulate_compiled(
    circuit: Circuit,
    compiled: _CompiledCircuit,
    inputs: dict[str, int],
) -> dict[str, int]:
    network_values: dict[int, int] = {}
    network_driven_masks: dict[int, int] = {}
    resolved_drivers: dict[int, int] = defaultdict(int)

    def resolve_driver(
        component_index: int,
        pin_name: str,
        value: int = 0,
        *,
        driven: bool = True,
    ) -> None:
        network = compiled.pin_networks.get((component_index, pin_name))
        if network is None:
            return
        width = _output_width(circuit, component_index, pin_name)
        new_mask = _mask(width) if driven else 0
        previous_mask = network_driven_masks.get(network, 0)
        conflict_mask = previous_mask & new_mask
        previous = network_values.get(network, 0)
        if (previous ^ value) & conflict_mask:
            raise SimulationError(f"conflicting drivers on network {network}")
        network_values[network] = (previous & previous_mask) | (value & new_mask)
        network_driven_masks[network] = previous_mask | new_mask
        resolved_drivers[network] += 1
        if resolved_drivers[network] > compiled.network_driver_counts[network]:
            raise SimulationError(f"network {network} driver resolved more than once")

    def network_ready(network: int) -> bool:
        count = compiled.network_driver_counts.get(network, 0)
        return count > 0 and resolved_drivers[network] == count

    def read_network(network: int) -> int:
        if not network_ready(network):
            raise SimulationError(f"network {network} is not fully driven")
        # High-impedance bits read as zero, matching the runtime Wire value.
        return network_values.get(network, 0) & network_driven_masks.get(network, 0)

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
                resolve_driver(
                    component_index,
                    output_pins[0].name,
                    raw_value & _mask(output_pins[0].width),
                )
            else:
                for bit, pin in enumerate(output_pins):
                    resolve_driver(component_index, pin.name, (raw_value >> bit) & 1)
        elif component.kind in CONSTANT_KINDS:
            value = component.init_data if component.kind == 46 else int(component.kind == 2)
            resolve_driver(component_index, "out", value & _mask(component.word_size))
        elif component.kind not in SINK_KINDS:
            pending.add(component_index)

    while pending:
        progressed = False
        for component_index in tuple(pending):
            component = circuit.components[component_index]
            pins = positioned_pins(component, component_index)
            input_pins = [pin for pin in pins if pin.direction == I]
            if not all(
                network_ready(compiled.pin_networks[(component_index, pin.name)])
                for pin in input_pins
            ):
                continue
            values = {
                pin.name: read_network(compiled.pin_networks[(component_index, pin.name)])
                for pin in input_pins
            }
            if component.kind in {12, 25}:
                resolve_driver(
                    component_index,
                    "out",
                    values["in"],
                    driven=values["enable"] == 1,
                )
            else:
                for name, value in _evaluate(component.kind, component.word_size, values).items():
                    resolve_driver(component_index, name, value)
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
            outputs[key] = read_network(
                compiled.pin_networks[(component_index, pins[0].name)]
            )
        else:
            outputs[key] = sum(
                (read_network(compiled.pin_networks[(component_index, pin.name)]) & 1)
                << bit
                for bit, pin in enumerate(pins)
            )
    return outputs


def simulate_combinational(circuit: Circuit, inputs: dict[str, int]) -> dict[str, int]:
    """Evaluate one stable combinational state and return labeled level outputs."""

    return _simulate_compiled(circuit, _compile(circuit), inputs)


def _component_key(component_index: int, permanent_id: int, user_label: str) -> str:
    return user_label or str(permanent_id or -(component_index + 1))


def _output_width(circuit: Circuit, component_index: int, name: str) -> int:
    for pin in positioned_pins(circuit.components[component_index], component_index):
        if pin.name == name:
            return pin.width
    raise SimulationError(f"component {component_index} has no output pin {name!r}")


def initial_clocked_memory(circuit: Circuit) -> dict[int, int]:
    """Return the documented v15 initial state for reviewed delay components."""

    memory: dict[int, int] = {}
    for component_index, component in enumerate(circuit.components):
        if component.kind not in CLOCKED_MEMORY_KINDS:
            continue
        key = component.permanent_id or -(component_index + 1)
        memory[key] = component.init_data & _mask(component.word_size)
    return memory


def _simulate_clocked_tick(
    circuit: Circuit,
    *,
    compiled: _CompiledCircuit,
    inputs: dict[str, int],
    memory: dict[int, int] | None = None,
) -> ClockedTickResult:
    """Simulate one stable architecture tick with reviewed delay and I/O parts.

    Delay Line outputs are read from the pre-tick memory snapshot and inputs
    are captured only after all combinational components have settled.  The
    architecture I/O control pins use the current runtime's exact ``== 1``
    enable rule; disabled tristate outputs leave their network undriven.
    """

    current_memory = initial_clocked_memory(circuit)
    if memory is not None:
        current_memory.update(memory)
    network_values: dict[int, int] = {}
    network_driven_masks: dict[int, int] = {}
    resolved_drivers: dict[int, int] = defaultdict(int)

    def resolve_driver(
        component_index: int,
        pin_name: str,
        value: int = 0,
        *,
        driven: bool = True,
    ) -> None:
        network = compiled.pin_networks.get((component_index, pin_name))
        if network is None:
            return
        width = _output_width(circuit, component_index, pin_name)
        new_mask = _mask(width) if driven else 0
        previous_mask = network_driven_masks.get(network, 0)
        conflict_mask = previous_mask & new_mask
        previous = network_values.get(network, 0)
        if (previous ^ value) & conflict_mask:
            raise SimulationError(f"conflicting drivers on network {network}")
        network_values[network] = (previous & previous_mask) | (value & new_mask)
        network_driven_masks[network] = previous_mask | new_mask
        resolved_drivers[network] += 1
        if resolved_drivers[network] > compiled.network_driver_counts[network]:
            raise SimulationError(f"network {network} driver resolved more than once")

    def network_ready(network: int) -> bool:
        count = compiled.network_driver_counts.get(network, 0)
        return count > 0 and resolved_drivers[network] == count

    def read_network(network: int) -> int:
        if not network_ready(network):
            raise SimulationError(f"network {network} is not fully driven")
        return network_values.get(network, 0) & network_driven_masks.get(network, 0)

    pending: set[int] = set()
    for component_index, component in enumerate(circuit.components):
        if component.kind in CLOCKED_MEMORY_KINDS:
            key = component.permanent_id or -(component_index + 1)
            resolve_driver(
                component_index,
                "out",
                current_memory[key] & _mask(component.word_size),
            )
        elif component.kind in CONSTANT_KINDS:
            value = component.init_data if component.kind == 46 else int(component.kind == 2)
            resolve_driver(component_index, "out", value & _mask(component.word_size))
        elif component.kind in SOURCE_KINDS:
            key = _component_key(component_index, component.permanent_id, component.user_label)
            try:
                raw_value = inputs[key]
            except KeyError as exc:
                raise SimulationError(f"missing value for level input {key!r}") from exc
            output_pins = [
                pin
                for pin in positioned_pins(component, component_index)
                if pin.direction in {O, T}
            ]
            if len(output_pins) == 1:
                resolve_driver(
                    component_index,
                    output_pins[0].name,
                    raw_value & _mask(output_pins[0].width),
                )
            else:
                for bit, pin in enumerate(output_pins):
                    resolve_driver(component_index, pin.name, (raw_value >> bit) & 1)
        elif component.kind not in SINK_KINDS | {ARCHITECTURE_OUTPUT_KIND}:
            pending.add(component_index)

    while pending:
        progressed = False
        for component_index in tuple(pending):
            component = circuit.components[component_index]
            pins = positioned_pins(component, component_index)
            input_pins = [pin for pin in pins if pin.direction == I]
            if not all(
                network_ready(compiled.pin_networks[(component_index, pin.name)])
                for pin in input_pins
            ):
                continue
            values = {
                pin.name: read_network(compiled.pin_networks[(component_index, pin.name)])
                for pin in input_pins
            }
            if component.kind == ARCHITECTURE_INPUT_KIND:
                if values["control"] == 1:
                    key = _component_key(component_index, component.permanent_id, component.user_label)
                    try:
                        raw_value = inputs[key]
                    except KeyError as exc:
                        raise SimulationError(f"missing architecture input {key!r}") from exc
                    resolve_driver(
                        component_index,
                        "value",
                        raw_value & _mask(component.word_size),
                    )
                else:
                    resolve_driver(component_index, "value", driven=False)
            elif component.kind in {12, 25}:
                resolve_driver(
                    component_index,
                    "out",
                    values["in"] & _mask(component.word_size),
                    driven=values["enable"] == 1,
                )
            else:
                for name, value in _evaluate(component.kind, component.word_size, values).items():
                    resolve_driver(
                        component_index,
                        name,
                        value & _mask(_output_width(circuit, component_index, name)),
                    )
            pending.remove(component_index)
            progressed = True
        if not progressed:
            unresolved = [circuit.components[index].permanent_id for index in sorted(pending)]
            raise SimulationError(f"unresolved clocked components: {unresolved}")

    outputs: dict[str, int] = {}
    for component_index, component in enumerate(circuit.components):
        if component.kind != ARCHITECTURE_OUTPUT_KIND:
            continue
        control_network = compiled.pin_networks[(component_index, "control")]
        if not network_ready(control_network):
            raise SimulationError(f"architecture output {component.permanent_id} control is undriven")
        if read_network(control_network) != 1:
            continue
        value_network = compiled.pin_networks[(component_index, "value")]
        if not network_ready(value_network):
            raise SimulationError(f"architecture output {component.permanent_id} value is undriven")
        key = _component_key(component_index, component.permanent_id, component.user_label)
        outputs[key] = read_network(value_network) & _mask(component.word_size)

    next_memory: dict[int, int] = {}
    for component_index, component in enumerate(circuit.components):
        if component.kind not in CLOCKED_MEMORY_KINDS:
            continue
        input_network = compiled.pin_networks[(component_index, "in")]
        if not network_ready(input_network):
            raise SimulationError(f"delay input {component.permanent_id} is undriven")
        key = component.permanent_id or -(component_index + 1)
        next_memory[key] = read_network(input_network) & _mask(component.word_size)
    return ClockedTickResult(outputs=outputs, memory=next_memory)


def simulate_clocked_tick(
    circuit: Circuit,
    *,
    inputs: dict[str, int],
    memory: dict[int, int] | None = None,
) -> ClockedTickResult:
    """Simulate one architecture tick, compiling the circuit for this call."""

    return _simulate_clocked_tick(
        circuit,
        compiled=_compile(circuit),
        inputs=inputs,
        memory=memory,
    )


def simulate_clocked_ticks(
    circuit: Circuit,
    *,
    inputs: dict[str, int],
    tick_count: int,
    memory: dict[int, int] | None = None,
) -> tuple[ClockedTickResult, ...]:
    """Simulate several consecutive ticks while compiling connectivity once."""

    if tick_count < 0:
        raise ValueError("tick_count must not be negative")
    compiled = _compile(circuit)
    current_memory = memory
    results: list[ClockedTickResult] = []
    for _ in range(tick_count):
        result = _simulate_clocked_tick(
            circuit,
            compiled=compiled,
            inputs=inputs,
            memory=current_memory,
        )
        results.append(result)
        current_memory = result.memory
    return tuple(results)


def simulate_clocked_trace(
    circuit: Circuit,
    *,
    inputs: Iterable[dict[str, int]],
    memory: dict[int, int] | None = None,
) -> tuple[ClockedTickResult, ...]:
    """Simulate a clocked circuit with a distinct input mapping on each tick."""

    compiled = _compile(circuit)
    current_memory = memory
    results: list[ClockedTickResult] = []
    for input_values in inputs:
        result = _simulate_clocked_tick(
            circuit,
            compiled=compiled,
            inputs=input_values,
            memory=current_memory,
        )
        results.append(result)
        current_memory = result.memory
    return tuple(results)


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
