"""Auditable pin schemas and endpoint-based logical connectivity.

Only component kinds whose geometry has been checked against current circuits
are listed here.  Unsupported kinds remain explicit in analysis results rather
than receiving guessed pins.
"""

from __future__ import annotations

from collections import Counter, defaultdict, deque
from dataclasses import dataclass

from .analysis import wire_points
from .model import Circuit, Component, Point


@dataclass(frozen=True)
class PinSpec:
    name: str
    direction: str
    offset: Point
    width: int | None = None


@dataclass(frozen=True)
class PositionedPin:
    component_index: int
    permanent_id: int
    component_kind: int
    name: str
    direction: str
    width: int
    position: Point


def _pins(*values: PinSpec) -> tuple[PinSpec, ...]:
    return values


I = "input"
O = "output"
T = "output_tristate"


PIN_SCHEMAS: dict[int, tuple[PinSpec, ...]] = {
    1: _pins(PinSpec("out", O, (1, 0), 1)),
    2: _pins(PinSpec("out", O, (1, 0), 1)),
    3: _pins(PinSpec("in", I, (-1, 0), 1), PinSpec("out", O, (2, 0), 1)),
    4: _pins(PinSpec("in0", I, (-1, -1), 1), PinSpec("in1", I, (-1, 1), 1), PinSpec("out", O, (2, 0), 1)),
    5: _pins(PinSpec("in0", I, (-1, -1), 1), PinSpec("in1", I, (-1, 0), 1), PinSpec("in2", I, (-1, 1), 1), PinSpec("out", O, (2, 0), 1)),
    6: _pins(PinSpec("in0", I, (-1, -1), 1), PinSpec("in1", I, (-1, 1), 1), PinSpec("out", O, (2, 0), 1)),
    7: _pins(PinSpec("in0", I, (-1, -1), 1), PinSpec("in1", I, (-1, 1), 1), PinSpec("out", O, (2, 0), 1)),
    8: _pins(PinSpec("in0", I, (-1, -1), 1), PinSpec("in1", I, (-1, 0), 1), PinSpec("in2", I, (-1, 1), 1), PinSpec("out", O, (2, 0), 1)),
    9: _pins(PinSpec("in0", I, (-1, -1), 1), PinSpec("in1", I, (-1, 1), 1), PinSpec("out", O, (2, 0), 1)),
    10: _pins(PinSpec("in0", I, (-1, -1), 1), PinSpec("in1", I, (-1, 1), 1), PinSpec("out", O, (2, 0), 1)),
    11: _pins(PinSpec("in0", I, (-1, -1), 1), PinSpec("in1", I, (-1, 1), 1), PinSpec("out", O, (2, 0), 1)),
    12: _pins(PinSpec("enable", I, (0, -1), 1), PinSpec("in", I, (-1, 0), 1), PinSpec("out", T, (2, 0), 1)),
    13: _pins(PinSpec("in", I, (-3, 0), 1), PinSpec("out", O, (3, 0), 1)),
    15: _pins(PinSpec("carry_in", I, (-1, -1), 1), PinSpec("in0", I, (-1, 0), 1), PinSpec("in1", I, (-1, 1), 1), PinSpec("sum", O, (1, 0), 1), PinSpec("carry_out", O, (1, 1), 1)),
    16: _pins(*(tuple(PinSpec(f"in{i}", I, (-1, i - 3), 1) for i in range(8)) + (PinSpec("out", O, (1, 0), 8),))),
    17: _pins(PinSpec("in", I, (-1, 0), 8), *(PinSpec(f"out{i}", O, (1, i - 3), 1) for i in range(8))),
    18: _pins(PinSpec("in", I, (-1, 0)), PinSpec("out", O, (2, 0))),
    19: _pins(PinSpec("in0", I, (-1, -1)), PinSpec("in1", I, (-1, 1)), PinSpec("out", O, (2, 0))),
    20: _pins(PinSpec("in0", I, (-1, -1)), PinSpec("in1", I, (-1, 1)), PinSpec("out", O, (2, 0))),
    21: _pins(PinSpec("in0", I, (-1, -1)), PinSpec("in1", I, (-1, 1)), PinSpec("out", O, (2, 0))),
    22: _pins(PinSpec("in0", I, (-1, -1)), PinSpec("in1", I, (-1, 1)), PinSpec("out", O, (2, 0))),
    23: _pins(PinSpec("in0", I, (-1, -1)), PinSpec("in1", I, (-1, 1)), PinSpec("out", O, (2, 0))),
    24: _pins(PinSpec("in0", I, (-1, -1)), PinSpec("in1", I, (-1, 1)), PinSpec("out", O, (2, 0))),
    25: _pins(PinSpec("enable", I, (0, -1), 1), PinSpec("in", I, (-1, 0)), PinSpec("out", T, (2, 0))),
    26: _pins(PinSpec("in0", I, (-1, -1)), PinSpec("in1", I, (-1, 1)), PinSpec("out", O, (2, 0), 1)),
    27: _pins(PinSpec("in0", I, (-1, -1)), PinSpec("in1", I, (-1, 1)), PinSpec("out", O, (2, 0), 1)),
    28: _pins(PinSpec("in0", I, (-1, -1)), PinSpec("in1", I, (-1, 1)), PinSpec("out", O, (2, 0), 1)),
    29: _pins(PinSpec("in", I, (-1, 0)), PinSpec("out", O, (2, 0))),
    30: _pins(PinSpec("carry_in", I, (-1, -1), 1), PinSpec("in0", I, (-1, 0)), PinSpec("in1", I, (-1, 1)), PinSpec("out", O, (1, -1)), PinSpec("carry_out", O, (1, 0), 1)),
    31: _pins(PinSpec("in0", I, (-1, -1)), PinSpec("in1", I, (-1, 0)), PinSpec("low", O, (1, -1)), PinSpec("high", O, (1, 0))),
    32: _pins(PinSpec("in0", I, (-1, -1)), PinSpec("in1", I, (-1, 0)), PinSpec("quotient", O, (1, -1)), PinSpec("remainder", O, (1, 0))),
    33: _pins(PinSpec("in", I, (-1, -1)), PinSpec("shift", I, (-1, 1), 8), PinSpec("out", O, (2, 0))),
    34: _pins(PinSpec("in", I, (-1, -1)), PinSpec("shift", I, (-1, 1), 8), PinSpec("out", O, (2, 0))),
    35: _pins(PinSpec("in", I, (-1, -1)), PinSpec("shift", I, (-1, 1), 8), PinSpec("out", O, (2, 0))),
    36: _pins(PinSpec("in", I, (-1, -1)), PinSpec("shift", I, (-1, 1), 8), PinSpec("out", O, (2, 0))),
    37: _pins(PinSpec("in", I, (-1, -1)), PinSpec("shift", I, (-1, 1), 8), PinSpec("out", O, (2, 0))),
    42: _pins(PinSpec("select", I, (-1, -1), 1), PinSpec("in0", I, (-1, 0)), PinSpec("in1", I, (-1, 1)), PinSpec("out", O, (2, 0))),
    43: _pins(PinSpec("select", I, (-1, 0), 1), PinSpec("out0", O, (1, 0), 1), PinSpec("out1", O, (1, 1), 1)),
    44: _pins(PinSpec("select0", I, (-1, -1), 1), PinSpec("select1", I, (-1, 0), 1), *(PinSpec(f"out{i}", O, (1, i - 1), 1) for i in range(4))),
    40: _pins(*(PinSpec(f"value{i}", I, (-1, i - 4), 1) for i in range(8))),
    45: _pins(PinSpec("disable", I, (0, -4), 1), *(PinSpec(f"select{i}", I, (-1, i - 3), 1) for i in range(3)), *(PinSpec(f"out{i}", O, (1, i - 3), 1) for i in range(8))),
    60: _pins(PinSpec("value", O, (1, 0), 1)),
    63: _pins(PinSpec("value0", O, (0, -1), 1), PinSpec("value1", O, (0, 1), 1)),
    64: _pins(PinSpec("value0", O, (1, -2), 1), PinSpec("value1", O, (1, -1), 1), PinSpec("value2", O, (1, 0), 1)),
    65: _pins(PinSpec("value0", O, (1, -2), 1), PinSpec("value1", O, (1, -1), 1), PinSpec("value2", O, (1, 0), 1), PinSpec("value3", O, (1, 1), 1)),
    68: _pins(PinSpec("value", I, (-1, 0), 1)),
    73: _pins(PinSpec("value0", I, (-1, -1), 1), PinSpec("value1", I, (-1, 0), 1)),
    74: _pins(PinSpec("value0", I, (-1, -1), 1), PinSpec("value1", I, (-1, 0), 1), PinSpec("value2", I, (-1, 1), 1)),
    75: _pins(PinSpec("value0", I, (-1, -2), 1), PinSpec("value1", I, (-1, -1), 1), PinSpec("value2", I, (-1, 0), 1), PinSpec("value3", I, (-1, 1), 1)),
    77: _pins(PinSpec("value0", I, (-1, -1), 1), PinSpec("value1", I, (-1, 0), 1), PinSpec("value2", I, (-1, 1), 1)),
    # Modern Codex Foundry interface ports.  These are the v15 counterparts of
    # the Input64/Output64 schemas in tc_circuit's component_info.json; the
    # port distance is three cells and is independent of word_size.  Legacy
    # OVERTRUE/LEG templates can use one-cell ports and must be analyzed with
    # their original template metadata instead of this default.
    79: _pins(PinSpec("in", O, (3, 0))),
    81: _pins(PinSpec("out", I, (-3, 0))),
}


def pin_specs_for(component: Component) -> tuple[PinSpec, ...] | None:
    if component.kind == 46:
        return _pins(PinSpec("out", O, (3, 0)))
    if component.kind == 61:
        # Current campaign word I/O components use a fixed three-cell body,
        # including the U1/U3 controls used by a few byte-level levels.  This
        # is verified against v15 baseline wire endpoints; it is not derived
        # from the payload word_size field.
        return _pins(PinSpec("value", O, (3, 0)))
    if component.kind == 62:
        return _pins(PinSpec("control", I, (1, -2), 1), PinSpec("value", T, (3, 0)))
    if component.kind == 69:
        return _pins(PinSpec("value", I, (-3, 0)))
    if component.kind == 70:
        return _pins(PinSpec("control", I, (-1, -2), 1), PinSpec("value", I, (-3, 0)))
    return PIN_SCHEMAS.get(component.kind)


def rotate_offset(offset: Point, rotation: int) -> Point:
    x, y = offset
    transforms = {
        0: (x, y),
        1: (-y, x),
        2: (-x, -y),
        3: (y, -x),
    }
    try:
        return transforms[rotation]
    except KeyError as exc:
        raise ValueError(f"invalid component rotation {rotation}") from exc


def positioned_pins(
    component: Component,
    component_index: int = 0,
    *,
    foundry_port_span: int = 3,
) -> tuple[PositionedPin, ...]:
    specs = pin_specs_for(component)
    if specs is None:
        return ()
    if component.kind in {79, 81}:
        if foundry_port_span not in {1, 3}:
            raise ValueError("Foundry port span must be 1 or 3")
        direction = 1 if component.kind == 79 else -1
        specs = _pins(PinSpec(specs[0].name, specs[0].direction, (direction * foundry_port_span, 0)))
    result: list[PositionedPin] = []
    for spec in specs:
        dx, dy = rotate_offset(spec.offset, component.rotation)
        result.append(
            PositionedPin(
                component_index=component_index,
                permanent_id=component.permanent_id,
                component_kind=component.kind,
                name=spec.name,
                direction=spec.direction,
                width=component.word_size if spec.width is None else spec.width,
                position=(component.position[0] + dx, component.position[1] + dy),
            )
        )
    return tuple(result)


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


def _effective_components(
    circuit: Circuit,
    extra_components: tuple[Component, ...],
) -> tuple[Component, ...]:
    components = list(circuit.components)
    seen = {component.permanent_id for component in components if component.permanent_id}
    for component in extra_components:
        if component.permanent_id not in seen:
            components.append(component)
            seen.add(component.permanent_id)
    return tuple(components)


def analyze_connectivity(
    circuit: Circuit,
    *,
    extra_components: tuple[Component, ...] = (),
) -> dict[str, object]:
    components = _effective_components(circuit, extra_components)
    unsupported = Counter(
        component.kind for component in components if pin_specs_for(component) is None
    )

    endpoints_by_wire: list[tuple[Point, Point]] = []
    owners: dict[Point, list[int]] = defaultdict(list)
    for index, wire in enumerate(circuit.wires):
        points = wire_points(wire)
        endpoints = (points[0], points[-1])
        endpoints_by_wire.append(endpoints)
        owners[endpoints[0]].append(index)
        owners[endpoints[1]].append(index)

    endpoint_positions = set(owners)

    def pins_for(component: Component, index: int) -> tuple[PositionedPin, ...]:
        if component.kind not in {79, 81}:
            return positioned_pins(component, index)
        candidates = {
            span: positioned_pins(component, index, foundry_port_span=span)
            for span in (1, 3)
        }
        connected_spans = [
            span
            for span, candidate_pins in candidates.items()
            if candidate_pins[0].position in endpoint_positions
        ]
        span = connected_spans[0] if len(connected_spans) == 1 else 3
        return candidates[span]

    pins = tuple(
        pin
        for index, component in enumerate(components)
        for pin in pins_for(component, index)
    )

    union_find = _UnionFind(len(circuit.wires))
    for wire_indices in owners.values():
        for wire_index in wire_indices[1:]:
            union_find.union(wire_indices[0], wire_index)

    network_for_position: dict[Point, int] = {}
    for wire_index, endpoints in enumerate(endpoints_by_wire):
        root = union_find.find(wire_index)
        network_for_position[endpoints[0]] = root
        network_for_position[endpoints[1]] = root

    network_pins: dict[int, list[PositionedPin]] = defaultdict(list)
    connected_pins: list[PositionedPin] = []
    unconnected_pins: list[PositionedPin] = []
    for pin in pins:
        network = network_for_position.get(pin.position)
        if network is None:
            unconnected_pins.append(pin)
        else:
            network_pins[network].append(pin)
            connected_pins.append(pin)

    edges: set[tuple[int, int]] = set()
    sequential_kinds = {13, 14, 38, 39, 50, 55, 118, 119}
    multi_driver_networks = 0
    undriven_networks = 0
    sinkless_networks = 0
    width_mismatch_networks = 0
    for network in network_pins.values():
        drivers = [pin for pin in network if pin.direction in {O, T}]
        receivers = [pin for pin in network if pin.direction == I]
        if len(drivers) > 1 and not all(pin.direction == T for pin in drivers):
            multi_driver_networks += 1
        if not drivers:
            undriven_networks += 1
        if not receivers:
            sinkless_networks += 1
        if len({pin.width for pin in network}) > 1:
            width_mismatch_networks += 1
        for driver in drivers:
            for receiver in receivers:
                if (
                    driver.component_index != receiver.component_index
                    and receiver.component_kind not in sequential_kinds
                ):
                    edges.add((driver.component_index, receiver.component_index))

    successors: dict[int, set[int]] = defaultdict(set)
    indegree = [0] * len(components)
    for source, destination in edges:
        if destination not in successors[source]:
            successors[source].add(destination)
            indegree[destination] += 1
    queue = deque(index for index, degree in enumerate(indegree) if degree == 0)
    depths = [0] * len(components)
    visited = 0
    while queue:
        source = queue.popleft()
        visited += 1
        for destination in successors[source]:
            weight = 0 if components[destination].kind in {40, 62, 68, 69, 70, 73, 74, 75, 77, 79, 81} else 1
            depths[destination] = max(depths[destination], depths[source] + weight)
            indegree[destination] -= 1
            if indegree[destination] == 0:
                queue.append(destination)

    return {
        "effective_component_count": len(components),
        "supported_component_count": len(components) - sum(unsupported.values()),
        "unsupported_component_kind_counts": dict(sorted(unsupported.items())),
        "pin_count": len(pins),
        "connected_pin_count": len(connected_pins),
        "unconnected_pin_count": len(unconnected_pins),
        "unconnected_pins": [
            {
                "permanent_id": pin.permanent_id,
                "kind": pin.component_kind,
                "name": pin.name,
                "direction": pin.direction,
                "width": pin.width,
                "position": pin.position,
            }
            for pin in unconnected_pins
        ],
        "logical_network_count": len(network_pins),
        "logical_edge_count": len(edges),
        "multi_driver_network_count": multi_driver_networks,
        "undriven_network_count": undriven_networks,
        "sinkless_network_count": sinkless_networks,
        "width_mismatch_network_count": width_mismatch_networks,
        "unit_logic_depth": max(depths, default=0),
        "cycle_component_count": len(components) - visited,
    }
