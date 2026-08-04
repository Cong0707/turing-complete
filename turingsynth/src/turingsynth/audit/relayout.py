"""Lossless topology and metadata audit for v15 relayout builds."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import replace

from turingsynth.formats.model import Circuit
from turingsynth.formats.wire import wire_points
from turingsynth.mapping.native import positioned_pins


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


def topology_signature(circuit: Circuit) -> Counter[tuple[tuple[object, ...], ...]]:
    """Return the pin partition induced only by connected wire endpoints.

    Wire crossings are deliberately ignored. A logical junction exists only
    where two wire endpoints coincide, matching the game save representation.
    """

    if not circuit.wires:
        if circuit.components:
            raise ValueError("circuit has components but no physical wires")
        return Counter()

    union = _UnionFind(len(circuit.wires))
    wire_endpoints: list[tuple[tuple[int, int], tuple[int, int]]] = []
    wires_at_endpoint: dict[tuple[int, int], list[int]] = defaultdict(list)
    for index, wire in enumerate(circuit.wires):
        points = wire_points(wire)
        endpoints = (points[0], points[-1])
        wire_endpoints.append(endpoints)
        wires_at_endpoint[endpoints[0]].append(index)
        wires_at_endpoint[endpoints[1]].append(index)
    for indices in wires_at_endpoint.values():
        for index in indices[1:]:
            union.union(indices[0], index)

    root_at_endpoint: dict[tuple[int, int], int] = {}
    physical_roots = set()
    for index, endpoints in enumerate(wire_endpoints):
        root = union.find(index)
        physical_roots.add(root)
        root_at_endpoint[endpoints[0]] = root
        root_at_endpoint[endpoints[1]] = root

    members: dict[int, list[tuple[object, ...]]] = defaultdict(list)
    for component_index, component in enumerate(circuit.components):
        for pin in positioned_pins(component, component_index):
            root = root_at_endpoint.get(pin.position)
            if root is None:
                raise ValueError(
                    "relayout topology contains an unconnected pin: "
                    f"component={component_index}, pin={pin.name!r}, "
                    f"position={pin.position!r}"
                )
            members[root].append(
                (
                    component_index,
                    component.permanent_id,
                    component.kind,
                    pin.name,
                    pin.direction,
                    pin.width,
                )
            )

    pin_roots = set(members)
    if physical_roots != pin_roots:
        orphaned = sorted(physical_roots - pin_roots)
        raise ValueError(
            "relayout topology contains wire-only physical networks: "
            f"{orphaned[:8]!r}"
        )
    return Counter(tuple(sorted(group)) for group in members.values())


def audit_relayout(source: Circuit, candidate: Circuit) -> dict[str, object]:
    """Prove that relayout changed only physical orientation and wire geometry."""

    if replace(source, components=(), wires=()) != replace(
        candidate,
        components=(),
        wires=(),
    ):
        raise ValueError("relayout changed top-level circuit metadata")
    if len(source.components) != len(candidate.components):
        raise ValueError("relayout changed the component population")

    source_ids = tuple(component.permanent_id for component in source.components)
    candidate_ids = tuple(component.permanent_id for component in candidate.components)
    if source_ids != candidate_ids:
        raise ValueError("relayout changed component identity or order")
    for index, (left, right) in enumerate(
        zip(source.components, candidate.components)
    ):
        if replace(left, position=(0, 0), rotation=0) != replace(
            right,
            position=(0, 0),
            rotation=0,
        ):
            raise ValueError(
                "relayout changed a component field other than position/rotation: "
                f"component={index}"
            )

    source_signature = topology_signature(source)
    candidate_signature = topology_signature(candidate)
    if source_signature != candidate_signature:
        removed = source_signature - candidate_signature
        added = candidate_signature - source_signature
        raise ValueError(
            "relayout changed the logical pin partition: "
            f"removed={list(removed.items())[:2]!r}, "
            f"added={list(added.items())[:2]!r}"
        )

    return {
        "schema": "turingsynth-v15-relayout-audit-v1",
        "status": "pass",
        "top_level_metadata_preserved": True,
        "component_identity_order_preserved": True,
        "component_fields_except_position_and_rotation_preserved": True,
        "logical_network_partition_preserved": True,
        "component_count": len(candidate.components),
        "logical_network_count": sum(candidate_signature.values()),
    }
