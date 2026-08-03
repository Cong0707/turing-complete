"""Isolated prototype for placing and routing Boolean Byte Adder netlists.

This file intentionally lives under ``.research``.  It does not write the
checked-in candidate or the live save.  The reusable production boundary is
``build_byte_adder_circuit``: callers provide a reviewed ``TuringNetlist`` and
receive a fully placed v15 ``Circuit`` after deterministic, sprite-aware
routing.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from hashlib import sha256
from heapq import heappop, heappush
import json
from pathlib import Path
from typing import Iterable, Mapping

from tc_save_lab.analysis import wire_points
from tc_save_lab.builder import stable_permanent_id, wire_from_vertices
from tc_save_lab.codec import decode_v15, encode_v15
from tc_save_lab.logic_layout import MappedGate, TuringNetlist, map_logic_network
from tc_save_lab.logic_network import LogicBuilder, LogicNetwork
from tc_save_lab.model import Circuit, Component, Point, Wire
from tc_save_lab.pins import I, O, analyze_connectivity, positioned_pins
from tc_save_lab.simulate import verify_truth_table
from tc_save_lab.sprite_geometry import (
    DEFAULT_COMPONENT_SPRITE_ROOT,
    _component_alpha_cells,
    audit_sprite_geometry,
)


BYTE_INPUT_NAMES = frozenset(
    ["Carry in"]
    + [f"A[{bit}]" for bit in range(8)]
    + [f"B[{bit}]" for bit in range(8)]
)
BYTE_OUTPUT_NAMES = frozenset(
    [f"Output[{bit}]" for bit in range(8)] + ["Carry out"]
)


@dataclass(frozen=True)
class Connection:
    """One directed, width-compatible pin connection.

    ``network`` identifies electrically identical fanout routes.  Duplicate
    edges are allowed only for the same network; unrelated nets may cross at a
    point but may never overlap along an edge.
    """

    network: str
    source: Point
    sink: Point


@dataclass(frozen=True)
class BuildReport:
    gate: int
    delay: int
    component_count: int
    wire_count: int
    exhaustive_vectors: int
    sha256: str


def _scaffold(project_root: Path) -> tuple[Component, ...]:
    path = project_root / "examples" / "byte_adder" / "scaffold" / "immutable.json"
    record = json.loads(path.read_text(encoding="utf-8"))
    raw_components = []
    for raw in record["immutable_components"]:
        item = dict(raw)
        item.pop("role", None)
        raw_components.append(item)
    components = Circuit.from_dict({"components": raw_components}).components
    expected = {"A", "B", "Carry in", "Output", "Carry out"}
    if {component.user_label for component in components} != expected:
        raise RuntimeError("byte_adder immutable scaffold labels changed")
    if not all(component.immutable for component in components):
        raise RuntimeError("byte_adder scaffold contains a mutable interface")
    return components


def _labeled(components: Iterable[Component], label: str) -> Component:
    matches = [component for component in components if component.user_label == label]
    if len(matches) != 1:
        raise RuntimeError(f"expected exactly one component labeled {label!r}")
    return matches[0]


def _pin(component: Component, name: str) -> Point:
    matches = [pin.position for pin in positioned_pins(component) if pin.name == name]
    if len(matches) != 1:
        raise RuntimeError(
            f"component kind {component.kind} lacks exactly one pin {name!r}"
        )
    return matches[0]


def _input_pins(component: Component) -> tuple[Point, ...]:
    return tuple(pin.position for pin in positioned_pins(component) if pin.direction == I)


def _only_output(component: Component) -> Point:
    pins = [pin.position for pin in positioned_pins(component) if pin.direction == O]
    if len(pins) != 1:
        raise RuntimeError(f"component kind {component.kind} needs one output pin")
    return pins[0]


def _centered_rows(count: int, spacing: int = 6) -> tuple[int, ...]:
    return tuple(index * spacing - ((count - 1) * spacing) // 2 for index in range(count))


def _validate_contract(netlist: TuringNetlist) -> None:
    inputs = {name for name, _ in netlist.inputs}
    outputs = {name for name, _ in netlist.outputs}
    if inputs != BYTE_INPUT_NAMES:
        raise RuntimeError(
            f"byte-adder bit input contract mismatch: missing={sorted(BYTE_INPUT_NAMES-inputs)}, "
            f"extra={sorted(inputs-BYTE_INPUT_NAMES)}"
        )
    if outputs != BYTE_OUTPUT_NAMES:
        raise RuntimeError(
            f"byte-adder bit output contract mismatch: missing={sorted(BYTE_OUTPUT_NAMES-outputs)}, "
            f"extra={sorted(outputs-BYTE_OUTPUT_NAMES)}"
        )


def _place_components(
    project_root: Path,
    netlist: TuringNetlist,
) -> tuple[
    tuple[Component, ...],
    dict[str, Point],
    dict[str, Component],
    Component,
    tuple[Connection, ...],
]:
    """Place campaign I/O, U8 bridges, constants, and one-bit mapped gates."""

    immutable = _scaffold(project_root)
    a_input = _labeled(immutable, "A")
    b_input = _labeled(immutable, "B")
    carry_input = _labeled(immutable, "Carry in")
    word_output = _labeled(immutable, "Output")
    carry_output = _labeled(immutable, "Carry out")

    identity = "byte_adder:boolean-layout-prototype"
    a_split = Component(
        17,
        (-10, -8),
        0,
        stable_permanent_id(identity, "a-split"),
        word_size=8,
    )
    b_split = Component(
        17,
        (-10, 8),
        0,
        stable_permanent_id(identity, "b-split"),
        word_size=8,
    )

    max_depth = max((gate.depth for gate in netlist.gates), default=0)
    merger = Component(
        16,
        (48 + max_depth * 8, 0),
        0,
        stable_permanent_id(identity, "sum-merge"),
        word_size=8,
    )

    components: list[Component] = [*immutable, a_split, b_split, merger]
    source_points: dict[str, Point] = {}
    for name, key in netlist.inputs:
        if name == "Carry in":
            source_points[key] = _pin(carry_input, "value")
        elif name.startswith("A["):
            bit = int(name[2:-1])
            source_points[key] = _pin(a_split, f"out{bit}")
        elif name.startswith("B["):
            bit = int(name[2:-1])
            source_points[key] = _pin(b_split, f"out{bit}")
        else:  # guarded by _validate_contract
            raise AssertionError(name)

    constants_x = 24
    for index, (value, key) in enumerate(netlist.constants):
        component = Component(
            2 if value else 1,
            (constants_x, _centered_rows(len(netlist.constants))[index]),
            0,
            stable_permanent_id(identity, key),
        )
        components.append(component)
        source_points[key] = _only_output(component)

    gates_by_depth: dict[int, list[MappedGate]] = {}
    for gate in netlist.gates:
        gates_by_depth.setdefault(gate.depth, []).append(gate)
    gate_components: dict[str, Component] = {}
    for depth in sorted(gates_by_depth):
        layer = gates_by_depth[depth]
        for gate, y in zip(layer, _centered_rows(len(layer))):
            component = Component(
                gate.kind,
                (32 + (depth - 1) * 8, y),
                0,
                stable_permanent_id(identity, gate.key),
            )
            components.append(component)
            gate_components[gate.key] = component
            source_points[gate.key] = _only_output(component)

    bridge_connections = (
        Connection("bridge:A", _pin(a_input, "value"), _pin(a_split, "in")),
        Connection("bridge:B", _pin(b_input, "value"), _pin(b_split, "in")),
        Connection("bridge:Output", _pin(merger, "out"), _pin(word_output, "value")),
    )
    output_sinks = {
        **{f"Output[{bit}]": _pin(merger, f"in{bit}") for bit in range(8)},
        "Carry out": _pin(carry_output, "value"),
    }
    return (
        tuple(components),
        source_points,
        gate_components,
        merger,
        bridge_connections,
    ), output_sinks


def _alpha_and_pins(
    components: tuple[Component, ...],
    sprite_root: Path,
) -> tuple[frozenset[Point], frozenset[Point]]:
    alpha_owners: dict[Point, int] = {}
    pins: set[Point] = set()
    for index, component in enumerate(components):
        cells = _component_alpha_cells(component, sprite_root)
        if cells is None:
            raise RuntimeError(f"no current sprite mapping for component kind {component.kind}")
        for point in cells:
            previous = alpha_owners.get(point)
            if previous is not None:
                raise RuntimeError(
                    f"component body overlap at {point}: components {previous} and {index}"
                )
            alpha_owners[point] = index
        pins.update(pin.position for pin in positioned_pins(component, index))
    return frozenset(alpha_owners), frozenset(pins)


def _edge(left: Point, right: Point) -> tuple[Point, Point]:
    return (left, right) if left <= right else (right, left)


def _search_route(
    connection: Connection,
    *,
    alpha: frozenset[Point],
    pins: frozenset[Point],
    edge_owners: Mapping[tuple[Point, Point], str],
    bounds: tuple[int, int, int, int],
) -> tuple[Point, ...]:
    """Find one orthogonal path around exact sprite cells and all other pins."""

    start, goal = connection.source, connection.sink
    if start == goal:
        raise RuntimeError(f"zero-length connection {connection.network}")
    blocked = (alpha | pins) - {start, goal}
    min_x, min_y, max_x, max_y = bounds
    directions = (
        (1, 0),
        (1, 1),
        (0, 1),
        (-1, 1),
        (-1, 0),
        (-1, -1),
        (0, -1),
        (1, -1),
    )

    def heuristic(point: Point) -> int:
        return max(abs(point[0] - goal[0]), abs(point[1] - goal[1]))

    frontier: list[tuple[int, int, int, int, Point]] = []
    heappush(frontier, (heuristic(start), 0, start[0], start[1], start))
    best: dict[Point, int] = {start: 0}
    previous: dict[Point, Point] = {}

    while frontier:
        _, distance, _, _, point = heappop(frontier)
        if distance != best.get(point):
            continue
        if point == goal:
            path = [goal]
            while path[-1] != start:
                path.append(previous[path[-1]])
            path.reverse()
            return tuple(path)

        ordered = sorted(
            directions,
            key=lambda step: (
                heuristic((point[0] + step[0], point[1] + step[1])),
                step,
            ),
        )
        for dx, dy in ordered:
            neighbor = (point[0] + dx, point[1] + dy)
            if not (min_x <= neighbor[0] <= max_x and min_y <= neighbor[1] <= max_y):
                continue
            if neighbor in blocked:
                continue
            owner = edge_owners.get(_edge(point, neighbor))
            if owner is not None and owner != connection.network:
                continue
            candidate = distance + 1
            if candidate >= best.get(neighbor, 1 << 60):
                continue
            best[neighbor] = candidate
            previous[neighbor] = point
            heappush(
                frontier,
                (
                    candidate + heuristic(neighbor),
                    candidate,
                    neighbor[0],
                    neighbor[1],
                    neighbor,
                ),
            )
    raise RuntimeError(f"no geometry-safe route for {connection.network}: {start} -> {goal}")


def _vertices(points: tuple[Point, ...]) -> tuple[Point, ...]:
    """Collapse an eight-direction unit-step path into v15 route vertices."""

    if len(points) < 2:
        raise RuntimeError("a routed path needs at least two points")
    result = [points[0]]
    previous_direction = None
    for index in range(1, len(points)):
        direction = (
            points[index][0] - points[index - 1][0],
            points[index][1] - points[index - 1][1],
        )
        if previous_direction is not None and direction != previous_direction:
            result.append(points[index - 1])
        previous_direction = direction
    result.append(points[-1])
    return tuple(result)


def _route_all(
    components: tuple[Component, ...],
    connections: tuple[Connection, ...],
    sprite_root: Path,
) -> tuple[Wire, ...]:
    alpha, pins = _alpha_and_pins(components, sprite_root)
    all_points = alpha | pins
    margin = max(32, len(connections) // 3)
    bounds = (
        min(point[0] for point in all_points) - margin,
        min(point[1] for point in all_points) - margin,
        max(point[0] for point in all_points) + margin,
        max(point[1] for point in all_points) + margin,
    )
    edge_owners: dict[tuple[Point, Point], str] = {}
    wires: list[Wire] = []
    for connection in connections:
        points = _search_route(
            connection,
            alpha=alpha,
            pins=pins,
            edge_owners=edge_owners,
            bounds=bounds,
        )
        for left, right in zip(points, points[1:]):
            edge_owners.setdefault(_edge(left, right), connection.network)
        wires.append(wire_from_vertices(_vertices(points)))
    return tuple(wires)


def build_byte_adder_circuit(
    project_root: Path,
    netlist: TuringNetlist,
    *,
    sprite_root: Path = DEFAULT_COMPONENT_SPRITE_ROOT,
) -> Circuit:
    """Place and route a reviewed Boolean netlist behind campaign U8 ports."""

    project_root = Path(project_root)
    _validate_contract(netlist)
    placed, output_sinks = _place_components(project_root, netlist)
    components, sources, gate_components, _merger, bridge_connections = placed

    connections = list(bridge_connections)
    for gate in netlist.gates:
        sinks = _input_pins(gate_components[gate.key])
        if len(sinks) != len(gate.fanins):
            raise RuntimeError(f"mapped gate {gate.key!r} pin count changed")
        for input_index, (fanin, sink) in enumerate(zip(gate.fanins, sinks)):
            connections.append(
                Connection(f"signal:{fanin}", sources[fanin], sink)
            )
    for name, signal in netlist.outputs:
        connections.append(Connection(f"signal:{signal}", sources[signal], output_sinks[name]))

    wires = _route_all(components, tuple(connections), Path(sprite_root))
    baseline = decode_v15(
        (project_root / "examples" / "byte_adder" / "baseline" / "circuit.data").read_bytes()
    )
    return replace(
        baseline,
        gate=netlist.gate_count,
        delay=netlist.delay,
        description="Codex Boolean byte adder geometry prototype",
        components=components,
        wires=wires,
    )


def verify_byte_adder_circuit(
    circuit: Circuit,
    *,
    sprite_root: Path = DEFAULT_COMPONENT_SPRITE_ROOT,
) -> BuildReport:
    payload = encode_v15(circuit)
    if decode_v15(payload) != circuit:
        raise RuntimeError("v15 encode/decode round trip changed the circuit")

    connectivity = analyze_connectivity(circuit)
    for field in (
        "unsupported_component_kind_counts",
        "unconnected_pin_count",
        "multi_driver_network_count",
        "undriven_network_count",
        "sinkless_network_count",
        "width_mismatch_network_count",
        "cycle_component_count",
    ):
        if connectivity[field]:
            raise RuntimeError(f"connectivity failure {field}: {connectivity[field]!r}")

    geometry = audit_sprite_geometry(circuit, Path(sprite_root))
    if (
        geometry.unsupported_component_kinds
        or geometry.component_overlap_cells
        or geometry.wire_collisions
        or geometry.wire_interior_pin_contacts
    ):
        raise RuntimeError(f"sprite geometry failure: {geometry!r}")

    tested = verify_truth_table(
        circuit,
        inputs={"A": 8, "B": 8, "Carry in": 1},
        output_label=("Output", "Carry out"),
        expected=lambda values: {
            "Output": (values["A"] + values["B"] + values["Carry in"]) & 0xFF,
            "Carry out": (values["A"] + values["B"] + values["Carry in"]) >> 8,
        },
    )
    return BuildReport(
        gate=circuit.gate,
        delay=circuit.delay,
        component_count=len(circuit.components),
        wire_count=len(circuit.wires),
        exhaustive_vectors=tested,
        sha256=sha256(payload).hexdigest(),
    )


def ripple_reference_network() -> LogicNetwork:
    """Build a simple correctness fixture, not an optimization claim."""

    builder = LogicBuilder()
    carry = builder.input("Carry in")
    left = [builder.input(f"A[{bit}]") for bit in range(8)]
    right = [builder.input(f"B[{bit}]") for bit in range(8)]
    sums = []
    for bit in range(8):
        parity = builder.xor(left[bit], right[bit])
        sums.append(builder.xor(parity, carry))
        carry = builder.or_(
            builder.and_(left[bit], right[bit]),
            builder.and_(parity, carry),
        )
    for bit, signal in enumerate(sums):
        builder.output(f"Output[{bit}]", signal)
    builder.output("Carry out", carry)
    return builder.build()


def main() -> None:
    project_root = Path(__file__).resolve().parents[2]
    network = ripple_reference_network()
    netlist = map_logic_network(network)
    circuit = build_byte_adder_circuit(project_root, netlist)
    report = verify_byte_adder_circuit(circuit)
    output = Path(__file__).with_name("ripple_reference.circuit.data")
    output.write_bytes(encode_v15(circuit))
    print(json.dumps(report.__dict__, ensure_ascii=False, indent=2))
    print(f"research-only output: {output}")


if __name__ == "__main__":
    main()
