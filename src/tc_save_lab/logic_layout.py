"""Map Boolean IR into deterministic modern Foundry gate layouts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .builder import stable_permanent_id, wire_from_vertices
from .foundry import foundry_input, foundry_output
from .logic_network import LogicNetwork, LogicNetworkError, Op, Signal, estimate_turing_cost
from .model import Circuit, Component, Point
from .pins import I, O, positioned_pins
from .simulate import verify_truth_table


NOT_KIND = 3
AND_KIND = 4
NAND_KIND = 6
OR_KIND = 7
NOR_KIND = 9


@dataclass(frozen=True)
class MappedGate:
    """One unit-delay primitive in a technology-mapped one-bit netlist."""

    key: str
    kind: int
    fanins: tuple[str, ...]
    depth: int


@dataclass(frozen=True)
class TuringNetlist:
    """Technology netlist using only reviewed unit-cost one-bit primitives."""

    inputs: tuple[tuple[str, str], ...]
    constants: tuple[tuple[bool, str], ...]
    gates: tuple[MappedGate, ...]
    outputs: tuple[tuple[str, str], ...]

    def __post_init__(self) -> None:
        known: set[str] = set()
        input_names: set[str] = set()
        for name, key in self.inputs:
            if not name or name in input_names or not key or key in known:
                raise LogicNetworkError("mapped inputs need unique names and signal keys")
            input_names.add(name)
            known.add(key)
        for _, key in self.constants:
            if not key or key in known:
                raise LogicNetworkError("mapped constants need unique signal keys")
            known.add(key)
        for gate in self.gates:
            expected_fanins = 1 if gate.kind == NOT_KIND else 2
            if gate.kind not in {NOT_KIND, AND_KIND, NAND_KIND, OR_KIND, NOR_KIND}:
                raise LogicNetworkError(f"unsupported mapped gate kind {gate.kind}")
            if not gate.key or gate.key in known or len(gate.fanins) != expected_fanins:
                raise LogicNetworkError(f"invalid mapped gate {gate.key!r}")
            if any(fanin not in known for fanin in gate.fanins):
                raise LogicNetworkError(f"mapped gate {gate.key!r} has a forward reference")
            if gate.depth != max(_signal_depth(self.gates, fanin) for fanin in gate.fanins) + 1:
                raise LogicNetworkError(f"mapped gate {gate.key!r} has an invalid depth")
            known.add(gate.key)
        output_names: set[str] = set()
        for name, key in self.outputs:
            if not name or name in output_names or key not in known:
                raise LogicNetworkError(f"invalid mapped output {name!r}")
            output_names.add(name)

    @property
    def gate_count(self) -> int:
        return len(self.gates)

    @property
    def delay(self) -> int:
        depths = {gate.key: gate.depth for gate in self.gates}
        return max((depths.get(key, 0) for _, key in self.outputs), default=0)


def _signal_depth(gates: tuple[MappedGate, ...] | list[MappedGate], key: str) -> int:
    for gate in reversed(gates):
        if gate.key == key:
            return gate.depth
    return 0


def map_logic_network(network: LogicNetwork) -> TuringNetlist:
    """Map an XAG/AIG to current TC primitives with explicit signal phases.

    AND and NAND phases are emitted in parallel. XOR and XNOR use a shared
    ``AND + NOR`` first layer followed by NOR and OR respectively, matching the
    reviewed ``3 gates / 2 delay`` implementation.
    """

    demanded: dict[int, set[bool]] = {}

    def demand(signal: Signal) -> None:
        phases = demanded.setdefault(signal.node, set())
        if signal.inverted in phases:
            return
        phases.add(signal.inverted)
        for fanin in network.nodes[signal.node].fanins:
            demand(fanin)

    for output in network.outputs:
        demand(output.signal)

    inputs: list[tuple[str, str]] = []
    constants: list[tuple[bool, str]] = []
    gates: list[MappedGate] = []
    phase_keys: dict[Signal, str] = {}
    depths: dict[str, int] = {}

    def add_gate(key: str, kind: int, fanins: tuple[str, ...]) -> str:
        depth = max((depths[fanin] for fanin in fanins), default=0) + 1
        gates.append(MappedGate(key, kind, fanins, depth))
        depths[key] = depth
        return key

    for inverted in sorted(demanded.get(0, ())):
        key = f"constant:{int(inverted)}"
        constants.append((inverted, key))
        phase_keys[Signal(0, inverted)] = key
        depths[key] = 0

    for node_id, node in enumerate(network.nodes[1:], start=1):
        phases = demanded.get(node_id)
        if not phases:
            continue
        if node.op == Op.INPUT:
            positive_key = f"input:{node_id}"
            inputs.append((node.name, positive_key))
            phase_keys[Signal(node_id)] = positive_key
            depths[positive_key] = 0
            if True in phases:
                negative_key = add_gate(
                    f"node:{node_id}:negative",
                    NOT_KIND,
                    (positive_key,),
                )
                phase_keys[Signal(node_id, True)] = negative_key
            continue

        fanins = tuple(phase_keys[fanin] for fanin in node.fanins)
        if node.op == Op.AND:
            for inverted in sorted(phases):
                suffix = "negative" if inverted else "positive"
                kind = NAND_KIND if inverted else AND_KIND
                phase_keys[Signal(node_id, inverted)] = add_gate(
                    f"node:{node_id}:{suffix}",
                    kind,
                    fanins,
                )
            continue
        if node.op == Op.XOR:
            conjunction = add_gate(f"node:{node_id}:xor-and", AND_KIND, fanins)
            neither = add_gate(f"node:{node_id}:xor-nor", NOR_KIND, fanins)
            core = (conjunction, neither)
            if False in phases:
                phase_keys[Signal(node_id)] = add_gate(
                    f"node:{node_id}:positive",
                    NOR_KIND,
                    core,
                )
            if True in phases:
                phase_keys[Signal(node_id, True)] = add_gate(
                    f"node:{node_id}:negative",
                    OR_KIND,
                    core,
                )
            continue
        raise LogicNetworkError(f"cannot map operation {node.op}")

    outputs = tuple((output.name, phase_keys[output.signal]) for output in network.outputs)
    netlist = TuringNetlist(tuple(inputs), tuple(constants), tuple(gates), outputs)
    expected = estimate_turing_cost(network)
    if (netlist.gate_count, netlist.delay) != (expected.gates, expected.delay):
        raise LogicNetworkError(
            "technology mapper disagrees with the reviewed cost model: "
            f"mapped={netlist.gate_count}/{netlist.delay}, "
            f"estimated={expected.gates}/{expected.delay}"
        )
    return netlist


def _centered_rows(count: int, spacing: int) -> tuple[int, ...]:
    return tuple(index * spacing - ((count - 1) * spacing) // 2 for index in range(count))


def _only_pin(component: Component, direction: str) -> Point:
    pins = [pin for pin in positioned_pins(component) if pin.direction == direction]
    if len(pins) != 1:
        raise LogicNetworkError(
            f"component kind {component.kind} does not have exactly one {direction} pin"
        )
    return pins[0].position


def _input_pins(component: Component) -> tuple[Point, ...]:
    pins = [pin.position for pin in positioned_pins(component) if pin.direction == I]
    if not pins:
        raise LogicNetworkError(f"component kind {component.kind} has no mapped input pins")
    return tuple(pins)


def _route(source: Point, sink: Point) -> tuple[Point, ...]:
    if source == sink:
        raise LogicNetworkError(f"cannot route a zero-length connection at {source}")
    dx = sink[0] - source[0]
    dy = sink[1] - source[1]
    if dx == 0 or dy == 0 or abs(dx) == abs(dy):
        return source, sink
    return source, (sink[0], source[1]), sink


def layout_turing_netlist(
    logical_key: str,
    netlist: TuringNetlist,
    *,
    layer_spacing: int = 10,
    row_spacing: int = 6,
    clock_speed: int = 100_000,
) -> Circuit:
    """Place a mapped netlist and route one endpoint-to-endpoint wire per sink."""

    if layer_spacing < 6 or row_spacing < 4:
        raise ValueError("layout spacing is too small for reviewed pin geometry")
    if clock_speed <= 0:
        raise ValueError("clock_speed must be positive")

    source_count = len(netlist.inputs) + len(netlist.constants)
    source_rows = _centered_rows(source_count, row_spacing)
    components: list[Component] = []
    source_components: dict[str, Component] = {}
    source_index = 0
    for input_index, (name, key) in enumerate(netlist.inputs):
        component = foundry_input(
            logical_key,
            name,
            (-12, source_rows[source_index]),
            index=input_index,
        )
        source_index += 1
        components.append(component)
        source_components[key] = component
    for value, key in netlist.constants:
        component = Component(
            kind=2 if value else 1,
            position=(-12, source_rows[source_index]),
            rotation=0,
            permanent_id=stable_permanent_id(logical_key, key),
        )
        source_index += 1
        components.append(component)
        source_components[key] = component

    max_depth = max((gate.depth for gate in netlist.gates), default=0)
    output_x = max_depth * layer_spacing + 12
    output_components: dict[str, Component] = {}
    for output_index, ((name, _), y) in enumerate(
        zip(netlist.outputs, _centered_rows(len(netlist.outputs), row_spacing))
    ):
        component = foundry_output(
            logical_key,
            name,
            (output_x, y),
            index=output_index,
        )
        components.append(component)
        output_components[name] = component

    gates_by_depth: dict[int, list[MappedGate]] = {}
    for gate in netlist.gates:
        gates_by_depth.setdefault(gate.depth, []).append(gate)
    gate_components: dict[str, Component] = {}
    for depth in sorted(gates_by_depth):
        layer = gates_by_depth[depth]
        rows = _centered_rows(len(layer), row_spacing)
        for gate, y in zip(layer, rows):
            component = Component(
                kind=gate.kind,
                position=((depth - 1) * layer_spacing, y),
                rotation=0,
                permanent_id=stable_permanent_id(logical_key, gate.key),
            )
            components.append(component)
            gate_components[gate.key] = component

    signal_sources: dict[str, Point] = {
        key: _only_pin(component, O) for key, component in source_components.items()
    }
    signal_sources.update(
        {key: _only_pin(component, O) for key, component in gate_components.items()}
    )

    wires = []
    for gate in netlist.gates:
        sinks = _input_pins(gate_components[gate.key])
        if len(sinks) != len(gate.fanins):
            raise LogicNetworkError(f"mapped gate {gate.key!r} pin count changed")
        for fanin, sink in zip(gate.fanins, sinks):
            wires.append(wire_from_vertices(_route(signal_sources[fanin], sink)))
    for name, signal in netlist.outputs:
        sink = _only_pin(output_components[name], I)
        wires.append(wire_from_vertices(_route(signal_sources[signal], sink)))

    return Circuit(
        gate=netlist.gate_count,
        delay=netlist.delay,
        clock_speed=clock_speed,
        components=tuple(components),
        wires=tuple(wires),
    )


def layout_logic_network(
    logical_key: str,
    network: LogicNetwork,
    **layout_options: int,
) -> Circuit:
    """Technology-map and place one named Boolean network."""

    return layout_turing_netlist(logical_key, map_logic_network(network), **layout_options)


def verify_logic_layout(network: LogicNetwork, circuit: Circuit) -> int:
    """Exhaustively verify a placed circuit against its named Boolean IR."""

    return verify_truth_table(
        circuit,
        inputs={name: 1 for name in network.input_names},
        output_label=tuple(output.name for output in network.outputs),
        expected=lambda values: network.evaluate(values),
    )
