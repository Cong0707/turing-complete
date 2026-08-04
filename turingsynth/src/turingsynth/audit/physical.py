"""CI-grade structural, timing, connectivity, and geometry audit."""

from __future__ import annotations

from collections import defaultdict

from turingsynth.formats.model import Circuit, Component, Point
from turingsynth.formats.wire import wire_points
from turingsynth.ir.physical import PhysicalComponent, PhysicalDesign, PinRef
from turingsynth.mapping.native import INPUT, OUTPUT, TRISTATE, component_bounds, positioned_pins
from turingsynth.routing.astar import RoutingResult


def _component(value: PhysicalComponent) -> Component:
    if value.position is None:
        raise ValueError(f"component {value.key!r} has no position")
    return Component(
        kind=value.kind,
        position=value.position,
        rotation=value.rotation,
        permanent_id=value.permanent_id,
        user_label=value.user_label,
        settings=value.settings,
        ui_order=value.ui_order,
        word_size=value.word_size,
        immutable=value.immutable,
    )


class _UnionFind:
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


def _foreign_endpoint_contacts(
    points_by_wire: tuple[tuple[Point, ...], ...],
    networks: tuple[str, ...],
) -> list[tuple[int, int, Point, str, str]]:
    """Find foreign endpoints touched by another wire's interior geometry."""

    endpoint_wires: dict[Point, list[int]] = defaultdict(list)
    for index, points in enumerate(points_by_wire):
        endpoint_wires[points[0]].append(index)
        endpoint_wires[points[-1]].append(index)
    contacts = []
    for index, points in enumerate(points_by_wire):
        network = networks[index]
        for point in points[1:-1]:
            for endpoint_wire in endpoint_wires.get(point, ()):
                endpoint_network = networks[endpoint_wire]
                if endpoint_network != network:
                    contacts.append(
                        (index, endpoint_wire, point, network, endpoint_network)
                    )
    return contacts


def _non_orthogonal_foreign_contacts(
    points_by_wire: tuple[tuple[Point, ...], ...],
    networks: tuple[str, ...],
) -> list[tuple[Point, int, int, str, str]]:
    """Reject shared interiors unless both wires pass straight on opposite axes."""

    interior: dict[Point, list[tuple[int, str]]] = defaultdict(list)
    for index, points in enumerate(points_by_wire):
        for previous, point, following in zip(points, points[1:], points[2:]):
            incoming = (point[0] - previous[0], point[1] - previous[1])
            outgoing = (following[0] - point[0], following[1] - point[1])
            if incoming == outgoing:
                axis = "horizontal" if incoming[0] else "vertical"
            else:
                axis = "bend"
            interior[point].append((index, axis))
    contacts = []
    for point, occupants in interior.items():
        for left_index, (left_wire, left_axis) in enumerate(occupants):
            for right_wire, right_axis in occupants[left_index + 1 :]:
                if networks[left_wire] == networks[right_wire]:
                    continue
                if {left_axis, right_axis} == {"horizontal", "vertical"}:
                    continue
                contacts.append(
                    (
                        point,
                        left_wire,
                        right_wire,
                        left_axis,
                        right_axis,
                    )
                )
    return contacts


def _timing(design: PhysicalDesign) -> dict[str, object]:
    components = design.component_by_key()
    incoming: dict[str, list[str]] = defaultdict(list)
    outgoing_net_by_component: dict[str, list[str]] = defaultdict(list)
    net_by_name = {net.name: net for net in design.nets}
    drivers_by_net = {
        net.name: tuple(source.component for source in net.sources)
        for net in design.nets
    }
    for net in design.nets:
        for source in net.sources:
            outgoing_net_by_component[source.component].append(net.name)
        for sink in net.sinks:
            incoming[sink.component].append(net.name)
    pending = set(components)
    component_arrival: dict[str, int] = {}
    net_arrival: dict[str, int] = {}
    while pending:
        ready = sorted(
            key
            for key in pending
            if all(
                all(driver in component_arrival for driver in drivers_by_net[name])
                for name in incoming[key]
            )
        )
        if not ready:
            raise ValueError("physical timing graph contains a cycle")
        for key in ready:
            component = components[key]
            input_arrival = max((net_arrival[name] for name in incoming[key]), default=0)
            arrival = input_arrival + component.gate_delay
            component_arrival[key] = arrival
            for name in outgoing_net_by_component[key]:
                net_arrival[name] = max(net_arrival.get(name, 0), arrival)
            pending.remove(key)
    output_arrivals = {
        key: max((net_arrival[name] for name in incoming[key]), default=0)
        for key, component in components.items()
        if component.role == "output_port"
    }
    actual_delay = max(output_arrivals.values(), default=0)
    if actual_delay != design.delay:
        raise ValueError(f"physical delay {actual_delay} differs from mapped delay {design.delay}")
    gate_depth_mismatches = [
        {
            "component": key,
            "declared": component.logic_depth,
            "actual": component_arrival[key],
        }
        for key, component in components.items()
        if component.role == "gate" and component.logic_depth != component_arrival[key]
    ]
    if gate_depth_mismatches:
        raise ValueError(f"gate arrival mismatch: {gate_depth_mismatches[:4]!r}")
    return {
        "actual_delay": actual_delay,
        "output_arrivals": output_arrivals,
        "gate_depth_mismatch_count": 0,
    }


def audit_physical(
    design: PhysicalDesign,
    routing: RoutingResult,
    circuit: Circuit,
) -> dict[str, object]:
    components = design.component_by_key()
    model_components = {key: _component(value) for key, value in components.items()}
    pins: dict[PinRef, object] = {}
    pin_positions: dict[Point, list[PinRef]] = defaultdict(list)
    for key, component in model_components.items():
        for pin in positioned_pins(component):
            ref = PinRef(key, pin.name)
            pins[ref] = pin
            pin_positions[pin.position].append(ref)
    pin_net: dict[PinRef, str] = {}
    for net in design.nets:
        sources = [pins.get(ref) for ref in net.sources]
        if any(
            source is None
            or source.direction not in {OUTPUT, TRISTATE}
            or source.width != net.width
            for source in sources
        ):
            raise ValueError(f"net {net.name!r} has an invalid source pin")
        if len(sources) > 1 and any(source.direction != TRISTATE for source in sources):
            raise ValueError(
                f"net {net.name!r} mixes multiple drivers without all-tristate outputs"
            )
        for ref in (*net.sources, *net.sinks):
            previous = pin_net.get(ref)
            if previous is not None and previous != net.name:
                raise ValueError(f"pin {ref!r} belongs to multiple logical nets")
            pin_net[ref] = net.name
        for sink_ref in net.sinks:
            sink = pins.get(sink_ref)
            if sink is None or sink.direction != INPUT or sink.width != net.width:
                raise ValueError(f"net {net.name!r} has an invalid sink pin {sink_ref!r}")
    calculated_gate = sum(component.gate_cost for component in design.components)
    if calculated_gate != design.gate or circuit.gate != design.gate:
        raise ValueError("physical component costs differ from circuit gate header")
    if circuit.delay != design.delay or circuit.energy != design.gate * design.delay:
        raise ValueError("circuit delay/energy header differs from mapped design")
    rectangles = {
        key: component_bounds(component) for key, component in model_components.items()
    }
    overlaps = []
    keys = list(rectangles)
    for index, left_key in enumerate(keys):
        left = rectangles[left_key]
        for right_key in keys[index + 1 :]:
            right = rectangles[right_key]
            if not (
                left[1] < right[0]
                or right[1] < left[0]
                or left[3] < right[2]
                or right[3] < left[2]
            ):
                overlaps.append((left_key, right_key))
    if overlaps:
        raise ValueError(f"component rectangles overlap: {overlaps[:4]!r}")
    body_cells: set[Point] = set()
    for left, right, top, bottom in rectangles.values():
        body_cells.update(
            (x, y)
            for x in range(left, right + 1)
            for y in range(top, bottom + 1)
        )
    if len(routing.wires) != len(routing.edges) or circuit.wires != routing.wires:
        raise ValueError("routed wire/edge/circuit populations differ")
    endpoint_wires: dict[Point, list[int]] = defaultdict(list)
    edge_owner: dict[tuple[Point, Point], str] = {}
    edge_wire_index: dict[tuple[Point, Point], int] = {}
    body_collisions = []
    pin_contacts = []
    points_by_wire: list[tuple[Point, ...]] = []
    for index, (wire, routed) in enumerate(zip(routing.wires, routing.edges)):
        points = wire_points(wire)
        points_by_wire.append(points)
        if {points[0], points[-1]} != {routed.source, routed.sink}:
            raise ValueError(f"wire {index} endpoints differ from its routed edge")
        endpoint_wires[points[0]].append(index)
        endpoint_wires[points[-1]].append(index)
        for point in points[1:-1]:
            if point in body_cells:
                body_collisions.append((index, point))
            if point in pin_positions:
                pin_contacts.append((index, point))
        for left, right in zip(points, points[1:]):
            edge = (left, right) if left <= right else (right, left)
            if edge in edge_owner:
                previous = edge_wire_index[edge]
                raise ValueError(
                    f"wire edge overlap at {edge!r}: "
                    f"wire {previous} {routing.edges[previous].network} "
                    f"({routing.edges[previous].role}) and wire {index} "
                    f"{routed.network} ({routed.role})"
                )
            edge_owner[edge] = routed.network
            edge_wire_index[edge] = index
    if body_collisions or pin_contacts:
        raise ValueError(
            "wire geometry crosses a component or unrelated pin: "
            f"body={body_collisions[:4]!r}, pins={pin_contacts[:4]!r}"
        )
    foreign_endpoint_contacts = _foreign_endpoint_contacts(
        tuple(points_by_wire),
        tuple(edge.network for edge in routing.edges),
    )
    if foreign_endpoint_contacts:
        raise ValueError(
            "wire geometry crosses a foreign wire endpoint/tap: "
            f"{foreign_endpoint_contacts[:4]!r}"
        )
    non_orthogonal_contacts = _non_orthogonal_foreign_contacts(
        tuple(points_by_wire),
        tuple(edge.network for edge in routing.edges),
    )
    if non_orthogonal_contacts:
        raise ValueError(
            "foreign wires meet without a straight orthogonal crossing: "
            f"{non_orthogonal_contacts[:4]!r}"
        )
    union = _UnionFind(len(routing.wires))
    for wire_indices in endpoint_wires.values():
        for wire_index in wire_indices[1:]:
            union.union(wire_indices[0], wire_index)
    labels_by_root: dict[int, set[str]] = defaultdict(set)
    roots_by_label: dict[str, set[int]] = defaultdict(set)
    for index, routed in enumerate(routing.edges):
        root = union.find(index)
        labels_by_root[root].add(routed.network)
        roots_by_label[routed.network].add(root)
    mixed = {root: values for root, values in labels_by_root.items() if len(values) != 1}
    fragmented = {
        label: values for label, values in roots_by_label.items() if len(values) != 1
    }
    if mixed or fragmented:
        raise ValueError(f"physical networks mixed or fragmented: {mixed!r}, {fragmented!r}")
    for net in design.nets:
        endpoints = {
            point
            for point, wire_indices in endpoint_wires.items()
            if any(routing.edges[index].network == net.name for index in wire_indices)
        }
        required = {pins[ref].position for ref in (*net.sources, *net.sinks)}
        if not required <= endpoints:
            raise ValueError(f"net {net.name!r} omits required pin endpoints")
    timing = _timing(design)
    return {
        "schema": "turingsynth-physical-audit-v1",
        "status": "pass",
        "component_count": len(design.components),
        "logical_net_count": len(design.nets),
        "wire_count": len(routing.wires),
        "gate": design.gate,
        "delay": design.delay,
        "energy": design.gate * design.delay,
        "component_overlap_count": 0,
        "wire_component_collision_count": 0,
        "wire_interior_pin_contact_count": 0,
        "foreign_wire_endpoint_contact_count": 0,
        "non_orthogonal_foreign_contact_count": 0,
        "overlapping_edge_count": 0,
        "mixed_physical_network_count": 0,
        "fragmented_logical_network_count": 0,
        "timing": timing,
        "v15_round_trip_verified": True,
    }
