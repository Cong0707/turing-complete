"""Materialize the public Hub79 154/4 topology behind campaign Byte Adder I/O.

Research-only bootstrap.  It never writes ``examples/byte_adder/candidate`` or
the live save.  The public circuit is compiled with its frozen tri-state
evaluator; components are re-positioned into non-overlapping layers and each
endpoint network is reconstructed as a geometry-safe star.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import replace
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys

from tc_save_lab.builder import stable_permanent_id
from tc_save_lab.builder import wire_from_vertices
from tc_save_lab.analysis import wire_points
from tc_save_lab.codec import decode_v15, encode_v15
from tc_save_lab.model import Circuit, Component, Point
from tc_save_lab.pins import I, O, T, PositionedPin, analyze_connectivity, positioned_pins
from tc_save_lab.sprite_geometry import (
    DEFAULT_COMPONENT_SPRITE_ROOT,
    SPRITE_NAME_BY_COMPONENT_KIND,
    audit_sprite_geometry,
)

from route_byte_adder import Connection


ROOT = Path(__file__).resolve().parents[2]
SOURCE = (
    ROOT
    / "examples"
    / "rng"
    / "research"
    / "archive"
    / "rng_public_artifacts"
    / "hub-79-adder"
    / "main"
    / "circuit.data"
)
OUT_DIR = Path(__file__).with_name("hub79_bootstrap")
OUT_CIRCUIT = OUT_DIR / "candidate" / "circuit.data"
OUT_PROXY = OUT_DIR / "semantic_proxy.circuit.data"
OUT_CERT = OUT_DIR / "machine_certificate.json"
SPRITE_ROOT = DEFAULT_COMPONENT_SPRITE_ROOT

# The reviewed table omitted the 2-bit splitter although the installed sprite
# and pin schema are present.  Keep this local to the research process rather
# than changing a shared module in a dirty worktree.
SPRITE_NAME_BY_COMPONENT_KIND.setdefault(109, "com_splitter_bit_2.png")


def _load_engine():
    path = ROOT / "examples" / "rng" / "research" / "archive" / "rng_switch_public" / "analyze_hub79.py"
    spec = importlib.util.spec_from_file_location("hub79_bootstrap_engine", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load frozen Hub79 evaluator: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    module.CIRCUIT_PATH = SOURCE
    return module


def _scaffold() -> tuple[Component, ...]:
    data = json.loads(
        (ROOT / "examples" / "byte_adder" / "scaffold" / "immutable.json").read_text(
            encoding="utf-8"
        )
    )
    records = []
    for raw in data["immutable_components"]:
        record = dict(raw)
        record.pop("role", None)
        records.append(record)
    components = Circuit.from_dict({"components": records}).components
    if {component.user_label for component in components} != {
        "A",
        "B",
        "Carry in",
        "Output",
        "Carry out",
    }:
        raise RuntimeError("campaign byte_adder scaffold labels changed")
    return components


def _label_index(components: tuple[Component, ...], label: str) -> int:
    matches = [index for index, component in enumerate(components) if component.user_label == label]
    if len(matches) != 1:
        raise RuntimeError(f"expected one campaign component {label!r}")
    return matches[0]


def _pin(component: Component, name: str) -> Point:
    values = [pin.position for pin in positioned_pins(component) if pin.name == name]
    if len(values) != 1:
        raise RuntimeError(f"component kind {component.kind} has ambiguous pin {name!r}")
    return values[0]


def _component_depths(engine, circuit: Circuit, compiled, networks, outputs) -> dict[int, int]:
    """Use frozen evaluator signal depth to preserve the four-delay topology."""

    depths: dict[int, int] = {}
    for (component_index, pin_name), signal in outputs.items():
        depths[component_index] = max(depths.get(component_index, 0), signal.depth)
    # Sources, sinks, and disconnected output-only pins are deliberately kept
    # in the first/last layer; their positions do not affect logical depth.
    for index, component in enumerate(circuit.components):
        depths.setdefault(index, 0)
        if component.kind == 81:
            depths[index] = 4
    return depths


def _replace_ports(
    source: Circuit,
    compiled,
    engine,
) -> tuple[tuple[Component, ...], dict[tuple[int, str], tuple[int, str]]]:
    """Create campaign interfaces and map every old pin to its new pin."""

    scaffold = _scaffold()
    label_to_new = {
        component.user_label: index for index, component in enumerate(scaffold)
    }
    replacement: dict[tuple[int, str], tuple[int, str]] = {}
    kept: list[Component] = list(scaffold)

    port_labels = {
        "A": "A",
        "B": "B",
        "Cin": "Carry in",
        "sum": "Output",
        "Cout": "Carry out",
    }
    for old_index, component in enumerate(source.components):
        if component.kind in {79, 81}:
            target_label = port_labels.get(component.user_label)
            if target_label is None:
                raise RuntimeError(f"unexpected Hub79 port label {component.user_label!r}")
            target = scaffold[label_to_new[target_label]]
            old_pin_name = "in" if component.kind == 79 else "out"
            new_pin_name = "value"
            replacement[(old_index, old_pin_name)] = (
                label_to_new[target_label],
                new_pin_name,
            )
            continue

        # Keep the published primitive and its permanent ID, but place it in a
        # collision-free depth layer below.
        new_index = len(kept)
        kept.append(component)
        for pin in positioned_pins(component, old_index):
            replacement[(old_index, pin.name)] = (new_index, pin.name)

    return tuple(kept), replacement


def _place_internal(
    components: tuple[Component, ...],
    source: Circuit,
    engine,
    compiled,
    networks,
    outputs,
) -> tuple[Component, ...]:
    """Reposition only mutable/public internal parts into generous layers."""

    scaffold_count = 5
    depths = _component_depths(engine, source, compiled, networks, outputs)
    by_depth: dict[int, list[int]] = defaultdict(list)
    for index in range(scaffold_count, len(components)):
        # The original index is offset by removed ports.  Use component
        # identity/ID to recover its frozen depth when possible.
        original_index = next(
            (
                old
                for old, old_component in enumerate(source.components)
                if old_component.permanent_id == components[index].permanent_id
            ),
            None,
        )
        depth = depths.get(original_index, 0) if original_index is not None else 0
        by_depth[min(depth, 4)].append(index)

    placed = list(components)
    identity = "byte_adder:hub79-bootstrap"
    ordered = [index for depth in sorted(by_depth) for index in by_depth[depth]]
    rows = tuple(i * 12 - ((len(ordered) - 1) * 12) // 2 for i in range(len(ordered)))
    # Every component receives its own 40-cell horizontal slot.  This is
    # intentionally spacious: each pin can then own a distinct vertical trunk
    # without that trunk crossing any other component body.
    for slot, (index, y) in enumerate(zip(ordered, rows)):
            old = placed[index]
            placed[index] = replace(
                old,
                position=(48 + slot * 40, y),
                rotation=0,
                permanent_id=old.permanent_id
                or stable_permanent_id(identity, f"component-{index}"),
            )
    return tuple(placed)


def _pin_trunks(components: tuple[Component, ...]) -> dict[Point, int]:
    """Assign a unique vertical routing column to every reviewed pin."""

    trunks: dict[Point, int] = {}
    used: set[int] = set()
    campaign_override = {
        "Carry in": -14,
        "A": -16,
        "B": -15,
        "Output": 17,
        "Carry out": 16,
    }
    for component_index, component in enumerate(components):
        pins = positioned_pins(component, component_index)
        left = sorted(
            (pin for pin in pins if pin.position[0] < component.position[0]),
            key=lambda pin: (pin.position[1], pin.name),
        )
        right = sorted(
            (pin for pin in pins if pin.position[0] > component.position[0]),
            key=lambda pin: (pin.position[1], pin.name),
        )
        center = sorted(
            (pin for pin in pins if pin.position[0] == component.position[0]),
            key=lambda pin: (pin.position[1], pin.name),
        )
        for rank, pin in enumerate(left):
            trunk = component.position[0] - 2 - rank
            trunks[pin.position] = trunk
            if component.user_label in campaign_override:
                trunks[pin.position] = campaign_override[component.user_label]
        for rank, pin in enumerate(right):
            trunk = component.position[0] + 3 + rank
            trunks[pin.position] = trunk
            if component.user_label in campaign_override:
                trunks[pin.position] = campaign_override[component.user_label]
        for rank, pin in enumerate(center):
            # Switch enable sits on the positive-y face.  Move left at the pin
            # cell before rising to the common lanes; a center-column vertical
            # approach would pass through two switch body cells.
            trunks[pin.position] = component.position[0] - 3 - rank
        for pin in pins:
            trunk = trunks[pin.position]
            # Internal 40-cell slots make these columns globally unique.  The
            # five fixed campaign overrides were chosen unique by inspection.
            if trunk in used:
                raise RuntimeError(f"routing trunk collision at x={trunk}")
            used.add(trunk)
    return trunks


def _compress_vertices(vertices: list[Point]) -> tuple[Point, ...]:
    compact: list[Point] = []
    for point in vertices:
        if compact and point == compact[-1]:
            continue
        compact.append(point)
    changed = True
    while changed and len(compact) >= 3:
        changed = False
        reduced = [compact[0]]
        for index in range(1, len(compact) - 1):
            left, point, right = reduced[-1], compact[index], compact[index + 1]
            d0 = (point[0] - left[0], point[1] - left[1])
            d1 = (right[0] - point[0], right[1] - point[1])
            cross = d0[0] * d1[1] - d0[1] * d1[0]
            if cross == 0 and (d0[0] == 0) == (d1[0] == 0):
                changed = True
                continue
            reduced.append(point)
        reduced.append(compact[-1])
        compact = reduced
    return tuple(compact)


def _channel_route(
    components: tuple[Component, ...],
    connections: tuple[Connection, ...],
) -> tuple:
    """Route each logical network on a unique lane above all components."""

    trunks = _pin_trunks(components)
    escapes = {
        pin.position: (
            (pin.position[0], pin.position[1] + 1)
            if pin.position[0] == components[pin.component_index].position[0]
            else pin.position
        )
        for index, component in enumerate(components)
        for pin in positioned_pins(component, index)
    }
    network_names = sorted({connection.network for connection in connections})
    minimum_y = min(
        pin.position[1]
        for index, component in enumerate(components)
        for pin in positioned_pins(component, index)
    )
    lanes = {
        network: minimum_y - 24 - ordinal * 3
        for ordinal, network in enumerate(network_names)
    }
    wires = []
    for connection in connections:
        source_x = trunks[connection.source]
        sink_x = trunks[connection.sink]
        lane = lanes[connection.network]
        source_escape = escapes[connection.source]
        sink_escape = escapes[connection.sink]
        vertices = _compress_vertices(
            [
                connection.source,
                source_escape,
                (source_x, source_escape[1]),
                (source_x, lane),
                (sink_x, lane),
                (sink_x, sink_escape[1]),
                sink_escape,
                connection.sink,
            ]
        )
        wires.append(wire_from_vertices(vertices))

    edge_owner: dict[tuple[Point, Point], str] = {}
    foreign_overlap = []
    for wire, connection in zip(wires, connections):
        points = wire_points(wire)
        for left, right in zip(points, points[1:]):
            edge = (left, right) if left <= right else (right, left)
            previous = edge_owner.get(edge)
            if previous is not None and previous != connection.network:
                foreign_overlap.append((edge, previous, connection.network))
            edge_owner.setdefault(edge, connection.network)
    if foreign_overlap:
        raise RuntimeError(f"foreign-network edge overlap: {foreign_overlap[:4]!r}")
    return tuple(wires)


def _network_connections(
    source: Circuit,
    compiled,
    replacement: dict[tuple[int, str], tuple[int, str]],
    placed: tuple[Component, ...],
) -> tuple[Connection, ...]:
    result: list[Connection] = []
    for network, pins in sorted(compiled.network_pins.items()):
        mapped: list[tuple[int, PositionedPin]] = []
        for old_pin in pins:
            key = (old_pin.component_index, old_pin.name)
            if key not in replacement:
                raise RuntimeError(f"missing replacement for Hub79 pin {key!r}")
            new_index, new_name = replacement[key]
            candidates = [
                pin
                for pin in positioned_pins(placed[new_index], new_index)
                if pin.name == new_name
            ]
            if len(candidates) != 1:
                raise RuntimeError(f"missing new pin {new_index}:{new_name}")
            mapped.append((new_index, candidates[0]))

        # Preserve the intentional unconnected Maker2.in0 and splitter2.out0.
        if len(mapped) < 2:
            continue
        drivers = [
            pair
            for pair in mapped
            if pair[1].direction in {O, T}
        ]
        anchor = (drivers or mapped)[0][1].position
        for _, pin in mapped:
            if pin.position == anchor:
                continue
            result.append(Connection(f"hub79:net:{network}", anchor, pin.position))
    return tuple(result)


def _proxy_for_semantics(candidate: Circuit) -> Circuit:
    """Swap campaign I/O to evaluator-compatible Foundry ports in memory."""

    port_map = {
        "A": (79, 8, "A"),
        "B": (79, 8, "B"),
        "Carry in": (79, 8, "Cin"),
        "Output": (81, 8, "sum"),
        "Carry out": (81, 8, "Cout"),
    }
    components = []
    for component in candidate.components:
        spec = port_map.get(component.user_label)
        if spec is None:
            components.append(component)
            continue
        kind, word_size, proxy_label = spec
        components.append(
            replace(
                component,
                kind=kind,
                word_size=word_size,
                user_label=proxy_label,
                immutable=False,
            )
        )
    return replace(candidate, components=tuple(components))


def _audit_semantics(candidate: Circuit) -> dict[str, object]:
    engine = _load_engine()
    proxy = _proxy_for_semantics(candidate)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_PROXY.write_bytes(encode_v15(proxy))
    engine.CIRCUIT_PATH = OUT_PROXY
    evaluated, compiled, networks, outputs = engine.evaluate()
    variables = tuple(engine.variable(index) for index in range(engine.VARIABLES))
    carry = variables[16]
    expected_sum = []
    for left, right in zip(variables[:8], variables[8:16]):
        propagate = left ^ right
        expected_sum.append(propagate ^ carry)
        carry = (left & right) | (propagate & carry)

    sum_index = next(i for i, c in enumerate(proxy.components) if c.user_label == "sum")
    cout_index = next(i for i, c in enumerate(proxy.components) if c.user_label == "Cout")
    sum_signal = networks[compiled.pin_network[(sum_index, "out")]]
    cout_signal = networks[compiled.pin_network[(cout_index, "out")]]
    if sum_signal.bits[:8] != tuple(expected_sum):
        raise RuntimeError("campaign-port proxy sum mismatch")
    if cout_signal.bits[0] != carry:
        raise RuntimeError("campaign-port proxy carry mismatch")
    conflict_cases = sum(signal.conflict.bit_count() for signal in networks.values())
    if conflict_cases:
        raise RuntimeError(f"Z/multi-driver conflict cases: {conflict_cases}")
    depths = [signal.depth for signal in networks.values()]
    if max(depths, default=0) != 4:
        raise RuntimeError(f"global semantic depth is {max(depths, default=0)}, expected 4")
    if sum_signal.depth != 4 or cout_signal.depth != 4:
        raise RuntimeError("output depth is not exactly 4")
    return {
        "vectors_checked": engine.ASSIGNMENTS,
        "sum_correct": True,
        "carry_correct": True,
        "packed_conflict_cases": conflict_cases,
        "global_depth": max(depths, default=0),
        "sum_depth": sum_signal.depth,
        "cout_depth": cout_signal.depth,
        "multi_driver_network_count": sum(
            len([pin for pin in pins if pin.direction in {O, T}]) > 1
            for pins in compiled.network_pins.values()
        ),
    }


def build() -> dict[str, object]:
    engine = _load_engine()
    source, compiled = engine.compile_circuit()
    _circuit, _compiled, networks, outputs = engine.evaluate()
    components, replacement = _replace_ports(source, compiled, engine)
    components = _place_internal(components, source, engine, compiled, networks, outputs)
    connections = _network_connections(source, compiled, replacement, components)
    wires = _channel_route(components, connections)
    # Keep the published score and all non-layout metadata; no custom port IDs
    # or design bytes are copied into this campaign candidate.
    candidate = replace(
        source,
        custom_id=0,
        hub_id=0,
        design=b"",
        gate=154,
        delay=4,
        components=components,
        wires=wires,
        description="Codex Hub79 4-delay topology with campaign Byte Adder ports",
    )
    payload = encode_v15(candidate)
    if decode_v15(payload) != candidate:
        raise RuntimeError("candidate v15 round trip failed")
    geometry = audit_sprite_geometry(candidate, SPRITE_ROOT)
    if (
        geometry.unsupported_component_kinds
        or geometry.component_overlap_cells
        or geometry.wire_collisions
        or geometry.wire_interior_pin_contacts
    ):
        raise RuntimeError(f"candidate geometry failure: {geometry!r}")
    semantic = _audit_semantics(candidate)
    connectivity = analyze_connectivity(candidate)
    expected_unconnected = {(111, "in0", "input"), (109, "out0", "output")}
    actual_unconnected = {
        (item["kind"], item["name"], item["direction"])
        for item in connectivity["unconnected_pins"]
    }
    if actual_unconnected != expected_unconnected:
        raise RuntimeError(
            f"unexpected disconnected candidate pins: {connectivity['unconnected_pins']!r}"
        )
    for field in (
        "unsupported_component_kind_counts",
        "multi_driver_network_count",
        "undriven_network_count",
        "sinkless_network_count",
        "width_mismatch_network_count",
        "cycle_component_count",
    ):
        if connectivity[field]:
            raise RuntimeError(f"candidate connectivity failure {field}: {connectivity[field]!r}")
    # The only disconnected receiver is Maker2.in0's published implicit zero;
    # therefore all 49 Switch enable/data pins are necessarily connected.
    switch_enable_connected = sum(component.kind == 12 for component in candidate.components)
    if switch_enable_connected != 49:
        raise RuntimeError("published Hub79 Switch population changed")
    OUT_CIRCUIT.parent.mkdir(parents=True, exist_ok=True)
    OUT_CIRCUIT.write_bytes(payload)
    kind_counts = Counter(component.kind for component in candidate.components)
    reviewed_cost = {
        "bit_switch": kind_counts[12] * 2,
        "and": kind_counts[4],
        "nand": kind_counts[6],
        "or": kind_counts[7],
        "nor": kind_counts[9],
        "not": kind_counts[3],
    }
    if sum(reviewed_cost.values()) != 154:
        raise RuntimeError(f"cost mismatch: {reviewed_cost}")
    certificate = {
        "schema": "turing-complete-byte-adder-hub79-campaign-bootstrap-v1",
        "source": str(SOURCE.relative_to(ROOT)).replace("\\", "/"),
        "source_sha256": sha256(SOURCE.read_bytes()).hexdigest(),
        "candidate": str(OUT_CIRCUIT.relative_to(ROOT)).replace("\\", "/"),
        "candidate_sha256": sha256(payload).hexdigest(),
        "serialized_score": {"gate": 154, "delay": 4, "energy": 616},
        "component_count": len(candidate.components),
        "wire_count": len(candidate.wires),
        "component_kind_counts": {str(k): v for k, v in sorted(kind_counts.items())},
        "reviewed_gate_cost_breakdown": reviewed_cost,
        "semantic": semantic,
        "connectivity": {
            "unsupported_component_kind_counts": connectivity[
                "unsupported_component_kind_counts"
            ],
            "unconnected_pin_count": connectivity["unconnected_pin_count"],
            "intentional_unconnected_pins": connectivity["unconnected_pins"],
            "unsafe_multi_driver_network_count": connectivity[
                "multi_driver_network_count"
            ],
            "undriven_network_count": connectivity["undriven_network_count"],
            "sinkless_network_count": connectivity["sinkless_network_count"],
            "width_mismatch_network_count": connectivity[
                "width_mismatch_network_count"
            ],
            "cycle_component_count": connectivity["cycle_component_count"],
            "switch_enable_connected_count": switch_enable_connected,
            "topology_only_unit_depth": connectivity["unit_logic_depth"],
            "topology_depth_note": "non-Z-aware graph depth; semantic tri-state depth is authoritative",
        },
        "geometry": {
            "unsupported_component_kinds": list(geometry.unsupported_component_kinds),
            "component_overlap_cells": len(geometry.component_overlap_cells),
            "wire_collisions": len(geometry.wire_collisions),
            "wire_interior_pin_contacts": len(geometry.wire_interior_pin_contacts),
        },
        "v15_round_trip_verified": True,
        "intentional_unconnected_ports": ["kind111.in0", "kind109.out0"],
        "formal_save_untouched": True,
    }
    OUT_CERT.write_text(json.dumps(certificate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(certificate, ensure_ascii=False, indent=2))
    return certificate


if __name__ == "__main__":
    build()
