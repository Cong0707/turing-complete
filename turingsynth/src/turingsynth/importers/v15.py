"""Lossless v15 topology import for placement-and-routing regeneration."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from turingsynth.formats.model import Circuit
from turingsynth.formats.v15 import decode_v15
from turingsynth.formats.wire import wire_points
from turingsynth.ir.physical import (
    PhysicalComponent,
    PhysicalDesign,
    PhysicalNet,
    PinRef,
)
from turingsynth.mapping.native import (
    COMPONENTS,
    INPUT,
    OUTPUT,
    TRISTATE,
    positioned_pins,
)


MAKER_KINDS = frozenset({16, 97, 98, 111, 112})
SPLITTER_KINDS = frozenset({17, 99, 100, 109, 110})


@dataclass(frozen=True)
class ImportedV15:
    circuit: Circuit
    design: PhysicalDesign
    component_key_by_index: tuple[str, ...]
    logical_network_count: int


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


def _component_cost(kind: int, word_size: int) -> tuple[int, int]:
    if kind in {3, 4, 6, 7, 9}:
        return word_size, 1
    if kind == 10:
        return 3 * word_size, 2
    if kind == 12:
        return 2, 1
    if kind in {18, 19, 20, 21, 22}:
        return word_size, 1
    if kind == 23:
        return 3 * word_size, 2
    return 0, 0


def _role(kind: int) -> str:
    if kind in {61, 79}:
        return "input_port"
    if kind in {69, 81}:
        return "output_port"
    if kind in MAKER_KINDS:
        return "maker"
    if kind in SPLITTER_KINDS:
        return "splitter"
    return "gate"


def _splitter_output_affinity(kind: int, pin_name: str) -> float:
    """Return the center lane carried by a splitter output pin."""

    if kind not in SPLITTER_KINDS or not pin_name.startswith("out"):
        raise ValueError(f"{kind}:{pin_name} is not a splitter output")
    index = int(pin_name[3:])
    pin = next(pin for pin in COMPONENTS[kind].pins if pin.name == pin_name)
    if pin.width is None:
        raise ValueError(f"splitter output {kind}:{pin_name} has dynamic width")
    return index * pin.width + (pin.width - 1) / 2


def _splitter_affinity(kind: int) -> float:
    """Place a bus splitter one complete lane before its first output."""

    outputs = [
        pin for pin in COMPONENTS[kind].pins if pin.direction in {OUTPUT, TRISTATE}
    ]
    if not outputs or any(pin.width is None for pin in outputs):
        raise ValueError(f"splitter kind {kind} has no fixed-width outputs")
    first = min(outputs, key=lambda pin: _splitter_output_affinity(kind, pin.name))
    assert first.width is not None
    return _splitter_output_affinity(kind, first.name) - first.width


def _maker_affinity(kind: int, incoming_affinities: tuple[float, ...]) -> float:
    """Place a bus maker one complete lane after its final producer."""

    inputs = [pin for pin in COMPONENTS[kind].pins if pin.direction == INPUT]
    stride = max((pin.width or 1 for pin in inputs), default=1)
    return max(incoming_affinities, default=-float(stride)) + stride


def _network_roots(circuit: Circuit) -> tuple[dict[tuple[int, int], int], int]:
    union = _UnionFind(len(circuit.wires))
    owners: dict[tuple[int, int], list[int]] = defaultdict(list)
    endpoints = []
    for index, wire in enumerate(circuit.wires):
        points = wire_points(wire)
        pair = (points[0], points[-1])
        endpoints.append(pair)
        owners[pair[0]].append(index)
        owners[pair[1]].append(index)
    for wires in owners.values():
        for wire in wires[1:]:
            union.union(wires[0], wire)
    root_by_endpoint = {}
    roots = set()
    for index, pair in enumerate(endpoints):
        root = union.find(index)
        roots.add(root)
        root_by_endpoint[pair[0]] = root
        root_by_endpoint[pair[1]] = root
    return root_by_endpoint, len(roots)


def import_v15(path: Path) -> ImportedV15:
    source_path = Path(path).resolve()
    circuit = decode_v15(source_path.read_bytes())
    unsupported = sorted({component.kind for component in circuit.components} - COMPONENTS.keys())
    if unsupported:
        raise ValueError(f"v15 relayout has unsupported component kinds: {unsupported!r}")

    keys = tuple(
        f"import:{index}:{component.permanent_id}"
        for index, component in enumerate(circuit.components)
    )
    root_by_endpoint, root_count = _network_roots(circuit)
    pins_by_root: dict[int, list[tuple[PinRef, object]]] = defaultdict(list)
    pin_root: dict[tuple[int, str], int] = {}
    for index, component in enumerate(circuit.components):
        for pin in positioned_pins(component, index):
            root = root_by_endpoint.get(pin.position)
            if root is None:
                raise ValueError(
                    f"component {index} pin {pin.name!r} is unconnected at {pin.position}"
                )
            ref = PinRef(keys[index], pin.name)
            pins_by_root[root].append((ref, pin))
            pin_root[(index, pin.name)] = root

    nets = []
    for ordinal, root in enumerate(sorted(pins_by_root)):
        members = pins_by_root[root]
        drivers = sorted(
            (
                (ref, pin)
                for ref, pin in members
                if pin.direction in {OUTPUT, TRISTATE}
            ),
            key=lambda value: (value[1].component_index, value[1].name),
        )
        sinks = sorted(
            ((ref, pin) for ref, pin in members if pin.direction == INPUT),
            key=lambda value: (value[1].component_index, value[1].name),
        )
        if not drivers or not sinks:
            raise ValueError(
                f"imported network {root} lacks drivers or sinks: "
                f"drivers={len(drivers)}, sinks={len(sinks)}"
            )
        if len(drivers) > 1 and any(pin.direction != TRISTATE for _ref, pin in drivers):
            raise ValueError(f"imported network {root} has unsafe multiple drivers")
        widths = {pin.width for _ref, pin in (*drivers, *sinks)}
        if len(widths) != 1:
            raise ValueError(f"imported network {root} has mixed widths {sorted(widths)!r}")
        nets.append(
            PhysicalNet(
                name=f"import:net:{ordinal}",
                width=widths.pop(),
                source=drivers[0][0],
                additional_sources=tuple(ref for ref, _pin in drivers[1:]),
                sinks=tuple(ref for ref, _pin in sinks),
            )
        )

    predecessors: dict[int, set[int]] = {
        index: set() for index in range(len(circuit.components))
    }
    incoming_net: dict[int, list[PhysicalNet]] = defaultdict(list)
    outgoing_net: dict[int, list[tuple[PhysicalNet, str]]] = defaultdict(list)
    index_by_key = {key: index for index, key in enumerate(keys)}
    for net in nets:
        driver_indices = [index_by_key[source.component] for source in net.sources]
        for source in net.sources:
            outgoing_net[index_by_key[source.component]].append((net, source.pin))
        for sink in net.sinks:
            sink_index = index_by_key[sink.component]
            incoming_net[sink_index].append(net)
            predecessors[sink_index].update(
                driver for driver in driver_indices if driver != sink_index
            )

    pending = set(predecessors)
    order = []
    while pending:
        ready = sorted(index for index in pending if predecessors[index] <= set(order))
        if not ready:
            raise ValueError("imported v15 component graph contains a cycle")
        order.extend(ready)
        pending.difference_update(ready)

    arrival: dict[int, int] = {}
    component_affinity: dict[int, float] = {}
    net_affinities: dict[str, list[float]] = defaultdict(list)
    net_arrivals: dict[str, list[int]] = defaultdict(list)
    for index in order:
        component = circuit.components[index]
        incoming_affinities = [
            value
            for net in incoming_net[index]
            for value in net_affinities[net.name]
        ]
        incoming_arrivals = [
            value
            for net in incoming_net[index]
            for value in net_arrivals[net.name]
        ]
        if component.kind in {61, 79}:
            affinity = 0.0 if "carry" in component.user_label.lower() else 3.5
        elif component.kind in SPLITTER_KINDS:
            affinity = _splitter_affinity(component.kind)
        elif component.kind in MAKER_KINDS:
            affinity = _maker_affinity(
                component.kind,
                tuple(incoming_affinities),
            )
        elif component.kind == 69:
            affinity = 8.0 if "carry" in component.user_label.lower() else 3.5
        else:
            affinity = max(incoming_affinities, default=3.5)
        _gate_cost, gate_delay = _component_cost(component.kind, component.word_size)
        component_arrival = max(incoming_arrivals, default=0) + gate_delay
        component_affinity[index] = affinity
        arrival[index] = component_arrival
        for net, pin_name in outgoing_net[index]:
            if component.kind in SPLITTER_KINDS and pin_name.startswith("out"):
                output_affinity = _splitter_output_affinity(
                    component.kind,
                    pin_name,
                )
            else:
                output_affinity = affinity
            net_affinities[net.name].append(output_affinity)
            net_arrivals[net.name].append(component_arrival)

    components = []
    for index, component in enumerate(circuit.components):
        gate_cost, gate_delay = _component_cost(component.kind, component.word_size)
        components.append(
            PhysicalComponent(
                key=keys[index],
                kind=component.kind,
                word_size=component.word_size,
                role=_role(component.kind),
                affinity=component_affinity[index],
                logic_depth=arrival[index],
                gate_cost=gate_cost,
                gate_delay=gate_delay,
                user_label=component.user_label,
                settings=component.settings,
                ui_order=component.ui_order,
                immutable=component.immutable,
                rotation=component.rotation,
                position=component.position if component.immutable else None,
                permanent_id=component.permanent_id,
            )
        )

    calculated_gate = sum(component.gate_cost for component in components)
    output_delay = max(
        (
            arrival[index]
            for index, component in enumerate(circuit.components)
            if component.kind in {69, 81}
        ),
        default=0,
    )
    if calculated_gate != circuit.gate or output_delay != circuit.delay:
        raise ValueError(
            "imported score contract differs from component graph: "
            f"gate={calculated_gate}/{circuit.gate}, delay={output_delay}/{circuit.delay}"
        )
    design = PhysicalDesign(
        name=source_path.stem,
        components=tuple(components),
        nets=tuple(nets),
        gate=circuit.gate,
        delay=circuit.delay,
        target_kind="level",
        custom_id=circuit.custom_id,
    )
    return ImportedV15(
        circuit=circuit,
        design=design,
        component_key_by_index=keys,
        logical_network_count=root_count,
    )
