"""Conductor-first placement for TuringSynth.

The physical frame is owned by conductors, not by a rectangular gate grid:

    input ports -> splitter bank -> flat bus trunks
                -> timing-driven growth cones -> output comb/ports

Gate coordinates are derived from approved bus lanes, predecessor tips and
static timing.  Top-level component identity and metadata remain unchanged,
but their stale coordinates are deliberately discarded during a relayout.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import replace
from math import floor

from turingsynth.config import ProjectConfig
from turingsynth.floorplan import analyze_timing, extract_io_frontiers
from turingsynth.formats.model import Component, Point
from turingsynth.ir.physical import PhysicalComponent, PhysicalDesign, PhysicalNet, PinRef
from turingsynth.layout.layered import _ranks
from turingsynth.mapping.native import component_bounds, positioned_pins


def _prototype(
    component: PhysicalComponent,
    position: Point = (0, 0),
) -> Component:
    return Component(
        kind=component.kind,
        position=position,
        rotation=component.rotation,
        permanent_id=component.permanent_id,
        user_label=component.user_label,
        settings=component.settings,
        ui_order=component.ui_order,
        word_size=component.word_size,
        immutable=component.immutable,
    )


def _bounds(
    component: PhysicalComponent,
    position: Point,
) -> tuple[int, int, int, int]:
    return component_bounds(_prototype(component, position))


def _pin_offset(component: PhysicalComponent, pin_name: str) -> Point:
    pin = next(
        (
            pin
            for pin in positioned_pins(_prototype(component))
            if pin.name == pin_name
        ),
        None,
    )
    if pin is None:
        raise ValueError(f"component {component.key!r} has no pin {pin_name!r}")
    return pin.position


def _overlap(
    left: tuple[int, int, int, int],
    right: tuple[int, int, int, int],
    clearance: int,
) -> bool:
    return not (
        left[1] + clearance < right[0]
        or right[1] + clearance < left[0]
        or left[3] + clearance < right[2]
        or right[3] + clearance < left[2]
    )


def _weighted_median(values: list[tuple[int, int]]) -> int:
    if not values:
        raise ValueError("weighted median requires at least one value")
    ordered = sorted(values)
    threshold = (sum(weight for _value, weight in ordered) + 1) // 2
    seen = 0
    for value, weight in ordered:
        seen += weight
        if seen >= threshold:
            return value
    return ordered[-1][0]


def _oriented_design(design: PhysicalDesign) -> PhysicalDesign:
    """Choose a downward bus frame and discard all stale coordinates."""

    rotations = {
        "input_port": 1,   # output faces down into a splitter/feed rail
        "splitter": 1,     # lanes form a horizontal comb, then run down
        "maker": 3,        # lane inputs face down; packed output faces up
        "output_port": 1,  # direct scalar outputs are placed below logic
    }
    return replace(
        design,
        components=tuple(
            replace(
                component,
                rotation=rotations.get(component.role, component.rotation),
                position=None,
            )
            for component in design.components
        ),
    )


def _net_maps(
    design: PhysicalDesign,
) -> tuple[
    dict[str, list[tuple[object, PhysicalNet]]],
    dict[str, list[tuple[object, PhysicalNet]]],
]:
    incoming: dict[str, list[tuple[object, PhysicalNet]]] = defaultdict(list)
    outgoing: dict[str, list[tuple[object, PhysicalNet]]] = defaultdict(list)
    for net in design.nets:
        for sink in net.sinks:
            incoming[sink.component].append((sink, net))
        for source in net.sources:
            outgoing[source.component].append((source, net))
    return incoming, outgoing


def _splitter_order_key(
    component: PhysicalComponent,
    incoming: dict[str, list[tuple[object, PhysicalNet]]],
    components: dict[str, PhysicalComponent],
) -> tuple[object, ...]:
    sources = [
        components[source.component]
        for _sink, net in incoming[component.key]
        for source in net.sources
    ]
    return (
        min((source.ui_order for source in sources), default=0),
        min((source.affinity for source in sources), default=component.affinity),
        component.key,
    )


def _place_left_edge(
    component: PhysicalComponent,
    left: int,
    y: int,
) -> tuple[Point, tuple[int, int, int, int]]:
    relative = _bounds(component, (0, 0))
    position = (left - relative[0], y)
    return position, _bounds(component, position)


def _lane_band(affinity: float, base_y: int, pitch: int) -> int:
    return base_y + floor(affinity + 1e-9) * pitch


def _group_slot_offsets(keys: list[str], components: dict[str, PhysicalComponent]) -> dict[str, int]:
    groups: dict[int, list[str]] = defaultdict(list)
    for key in keys:
        groups[floor(components[key].affinity + 1e-9)].append(key)
    result: dict[str, int] = {}
    for group in groups.values():
        ordered = sorted(group, key=lambda key: (components[key].logic_depth, key))
        count = len(ordered)
        for index, key in enumerate(ordered):
            result[key] = (2 * index - count + 1) * 3
    return result


def _component_pin_position(
    component: PhysicalComponent,
    position: Point,
    pin: str,
) -> Point:
    offset = _pin_offset(component, pin)
    return position[0] + offset[0], position[1] + offset[1]


def _terminal_access_position(
    component: PhysicalComponent,
    position: Point,
    pin_name: str,
) -> Point:
    """Return the first free cell outside a positioned component pin."""

    pin = _component_pin_position(component, position, pin_name)
    left, right, top, bottom = _bounds(component, position)
    if pin[0] == left:
        return pin[0] - 1, pin[1]
    if pin[0] == right:
        return pin[0] + 1, pin[1]
    if pin[1] == top:
        return pin[0], pin[1] - 1
    if pin[1] == bottom:
        return pin[0], pin[1] + 1
    raise ValueError(f"pin {component.key}:{pin_name} is not on its component boundary")


def place_growth(
    design: PhysicalDesign,
    config: ProjectConfig,
    *,
    channel_expansion: dict[int, int] | None = None,
) -> tuple[PhysicalDesign, dict[str, object]]:
    """Place a mapped DAG around input trunks and output collectors."""

    del channel_expansion  # Growth stations expand locally, never by global columns.
    oriented = _oriented_design(design)
    timing = analyze_timing(oriented)
    floorplan = extract_io_frontiers(oriented, timing)
    components = oriented.component_by_key()
    ranks = _ranks(oriented)
    incoming, outgoing = _net_maps(oriented)
    timing_by_component = timing.fact_by_component()
    frontier_networks = frozenset(
        lane.net
        for trunk in floorplan.input_trunks
        for lane in trunk.lanes
    )

    positions: dict[str, Point] = {}
    occupied: list[tuple[int, int, int, int]] = []
    splitter_y = 9
    bank_gap = max(3, config.horizontal_clearance // 2)
    cursor = 0
    splitter_positions: dict[str, Point] = {}
    splitters = sorted(
        (component for component in oriented.components if component.role == "splitter"),
        key=lambda component: _splitter_order_key(component, incoming, components),
    )
    for component in splitters:
        position, rectangle = _place_left_edge(component, cursor, splitter_y)
        positions[component.key] = position
        splitter_positions[component.key] = position
        occupied.append(rectangle)
        cursor = rectangle[1] + bank_gap + 1

    splitters_by_input: dict[str, list[str]] = defaultdict(list)
    for splitter in splitters:
        for _sink, net in incoming[splitter.key]:
            for source in net.sources:
                if components[source.component].role == "input_port":
                    splitters_by_input[source.component].append(splitter.key)

    input_positions: dict[str, Point] = {}
    direct_input_cursor = cursor
    input_ports = sorted(
        (component for component in oriented.components if component.role == "input_port"),
        key=lambda component: (component.ui_order, component.affinity, component.key),
    )
    for component in input_ports:
        owned = sorted(set(splitters_by_input.get(component.key, ())))
        if owned:
            xs = sorted(splitter_positions[key][0] for key in owned)
            preferred_x = xs[len(xs) // 2]
            position = (preferred_x, 0)
            rectangle = _bounds(component, position)
        else:
            position, rectangle = _place_left_edge(component, direct_input_cursor, 0)
            direct_input_cursor = rectangle[1] + bank_gap + 1
        while any(_overlap(rectangle, other, 1) for other in occupied):
            position = (position[0] + 1, position[1])
            rectangle = _bounds(component, position)
        positions[component.key] = position
        input_positions[component.key] = position
        occupied.append(rectangle)

    bus_right = max((rectangle[1] for rectangle in occupied), default=0)
    logic_start_x = bus_right + max(7, config.horizontal_clearance + 2)
    logic_base_y = splitter_y + 11
    stage_pitch = max(16, config.horizontal_clearance + 11)
    affinity_pitch = max(12, config.vertical_clearance + 9)
    component_clearance = max(3, config.vertical_clearance)

    gate_keys = [
        component.key
        for component in oriented.components
        if component.role == "gate"
    ]
    collector_drivers = {
        source.component
        for net in oriented.nets
        if net.additional_sources
        for source in net.sources
    }
    structured_nets = {
        conductor.net
        for conductor in floorplan.conductors
        if len(conductor.tips) + len(conductor.sockets) > 2
    }
    conductor_by_net = {
        conductor.net: conductor for conductor in floorplan.conductors
    }
    conductor_spine_x: dict[str, int] = {}
    conductor_vertical: dict[int, list[tuple[int, int, str]]] = defaultdict(list)
    conductor_horizontal: dict[int, list[tuple[int, int, str]]] = defaultdict(list)
    conductor_hubs: dict[Point, str] = {}
    terminal_rows: dict[str, set[int]] = defaultdict(set)
    terminal_refs: dict[str, list[tuple[PinRef, PhysicalNet]]] = defaultdict(list)
    for net in oriented.nets:
        if net.name not in structured_nets:
            continue
        for ref in (*net.sources, *net.sinks):
            terminal_refs[ref.component].append((ref, net))
            known_position = positions.get(ref.component)
            if known_position is not None:
                terminal_rows[net.name].add(
                    _terminal_access_position(
                        components[ref.component],
                        known_position,
                        ref.pin,
                    )[1]
                )

    def corridor_intersects_rectangle(
        rectangle: tuple[int, int, int, int],
    ) -> bool:
        left, right, top, bottom = rectangle
        if any(
            left <= x <= right and min(bottom, high) >= max(top, low)
            for x, intervals in conductor_vertical.items()
            for low, high, _owner in intervals
        ):
            return True
        return any(
            top <= y <= bottom and min(right, high) >= max(left, low)
            for y, intervals in conductor_horizontal.items()
            for low, high, _owner in intervals
        )

    def segment_intersects_rectangle(
        left: Point,
        right: Point,
        rectangle: tuple[int, int, int, int],
    ) -> bool:
        rect_left, rect_right, rect_top, rect_bottom = rectangle
        if left[0] == right[0]:
            low, high = sorted((left[1], right[1]))
            return (
                rect_left <= left[0] <= rect_right
                and min(high, rect_bottom) >= max(low, rect_top)
            )
        if left[1] == right[1]:
            low, high = sorted((left[0], right[0]))
            return (
                rect_top <= left[1] <= rect_bottom
                and min(high, rect_right) >= max(low, rect_left)
            )
        raise ValueError(f"non-orthogonal conductor corridor: {left} -> {right}")

    def point_on_foreign_corridor(point: Point, network: str) -> bool:
        return any(
            owner != network and low <= point[1] <= high
            for low, high, owner in conductor_vertical.get(point[0], ())
        ) or any(
            owner != network and low <= point[0] <= high
            for low, high, owner in conductor_horizontal.get(point[1], ())
        )

    def corridor_plan(
        key: str,
        component: PhysicalComponent,
        position: Point,
    ) -> tuple[
        int,
        tuple[tuple[str, int, int, int, int, int, int], ...],
    ]:
        blocked = 0
        plans = []
        for sink_ref, net in incoming[key]:
            if net.name not in structured_nets or net.additional_sources:
                continue
            source_ref = net.source
            source_position = positions.get(source_ref.component)
            if source_position is None:
                continue
            source_component = components[source_ref.component]
            source_pin = _component_pin_position(
                source_component,
                source_position,
                source_ref.pin,
            )
            source_access = _terminal_access_position(
                source_component,
                source_position,
                source_ref.pin,
            )
            sink_access = _terminal_access_position(
                component,
                position,
                sink_ref.pin,
            )
            outward_x = source_access[0] - source_pin[0]
            existing_x = conductor_spine_x.get(net.name)
            conductor = conductor_by_net[net.name]
            if existing_x is not None:
                candidates = (existing_x,)
            elif conductor.tips[0].trunk_key is not None:
                candidates = (source_access[0],)
            elif outward_x:
                candidates = tuple(
                    source_access[0] + outward_x * distance
                    for distance in range(1, 5)
                )
            else:
                candidates = (
                    source_access[0],
                    source_access[0] - 1,
                    source_access[0] + 1,
                    source_access[0] - 2,
                    source_access[0] + 2,
                )

            selected: tuple[str, int, int, int, int, int, int] | None = None
            for spine_x in candidates:
                source_hub = (spine_x, source_access[1])
                sink_hub = (spine_x, sink_access[1])
                vertical_low, vertical_high = sorted(
                    (source_hub[1], sink_hub[1])
                )
                branch_low, branch_high = sorted((spine_x, sink_access[0]))
                vertical_segment = (source_hub, sink_hub)
                branch_segment = (sink_hub, sink_access)
                if any(
                    segment_intersects_rectangle(*vertical_segment, rectangle)
                    or segment_intersects_rectangle(*branch_segment, rectangle)
                    for rectangle in occupied
                ):
                    continue
                if any(
                    owner != net.name
                    and min(vertical_high, high) >= max(vertical_low, low)
                    for low, high, owner in conductor_vertical.get(spine_x, ())
                ):
                    continue
                if branch_low != branch_high and any(
                    owner != net.name
                    and min(branch_high, high) >= max(branch_low, low)
                    for low, high, owner in conductor_horizontal.get(
                        sink_access[1], ()
                    )
                ):
                    continue
                points = {
                    (spine_x, y)
                    for y in range(vertical_low, vertical_high + 1)
                } | {
                    (x, sink_access[1])
                    for x in range(branch_low, branch_high + 1)
                }
                if any(
                    point in conductor_hubs
                    and conductor_hubs[point] != net.name
                    for point in points
                ):
                    continue
                if any(
                    point_on_foreign_corridor(point, net.name)
                    for point in (source_hub, sink_hub)
                ):
                    continue
                selected = (
                    net.name,
                    spine_x,
                    vertical_low,
                    vertical_high,
                    sink_access[1],
                    branch_low,
                    branch_high,
                )
                break
            if selected is None:
                blocked += 1
            else:
                plans.append(selected)
        return blocked, tuple(plans)

    def commit_corridor_plans(
        plans: tuple[tuple[str, int, int, int, int, int, int], ...],
    ) -> None:
        for network, spine_x, low_y, high_y, branch_y, low_x, high_x in plans:
            conductor_spine_x.setdefault(network, spine_x)
            conductor_vertical[spine_x].append((low_y, high_y, network))
            if low_x != high_x:
                conductor_horizontal[branch_y].append((low_x, high_x, network))
            conductor_hubs.setdefault((spine_x, low_y), network)
            conductor_hubs.setdefault((spine_x, high_y), network)
    arrivals = sorted({timing_by_component[key].arrival for key in gate_keys})
    first_arrival = min(arrivals, default=1)
    for arrival in arrivals:
        keys = sorted(
            (key for key in gate_keys if timing_by_component[key].arrival == arrival),
            key=lambda key: (components[key].affinity, components[key].logic_depth, key),
        )
        slot_offsets = _group_slot_offsets(keys, components)
        for key in keys:
            component = components[key]
            band_y = _lane_band(component.affinity, logic_base_y, affinity_pitch)
            proposals: list[tuple[int, int]] = [
                (band_y + slot_offsets[key], 4),
            ]
            source_right = logic_start_x - 4
            frontier_pins: list[str] = []
            for sink, net in incoming[key]:
                sink_offset = _pin_offset(component, sink.pin)
                if net.name in frontier_networks:
                    frontier_pins.append(sink.pin)
                for source in net.sources:
                    source_position = positions.get(source.component)
                    if source_position is None:
                        continue
                    source_component = components[source.component]
                    source_right = max(
                        source_right,
                        _bounds(source_component, source_position)[1],
                    )
                    if net.name in frontier_networks:
                        continue
                    source_pin = _component_pin_position(
                        source_component,
                        source_position,
                        source.pin,
                    )
                    weight = 2 + min(3, len(net.sinks) - 1)
                    if timing_by_component[key].critical_input_net == net.name:
                        weight += 6
                    proposals.append((source_pin[1] - sink_offset[1], weight))

            ideal_y = _weighted_median(proposals)
            # Timing affinity may pull a consumer toward its predecessors, but
            # a growth cone may never fold back into the splitter/maker row or
            # escape through a neighboring bit's trunk sockets.
            ideal_y = max(band_y - 4, min(band_y + 8, ideal_y))
            natural_x = logic_start_x + (arrival - first_arrival) * stage_pitch
            minimum_x = source_right + max(4, config.horizontal_clearance // 2 + 2)
            stage_x = max(natural_x, minimum_x)
            found: Point | None = None
            found_cost: tuple[int, int, int, int, int, int, int] | None = None
            found_corridors: tuple[
                tuple[str, int, int, int, int, int, int], ...
            ] = ()
            # Keep a timing band compact by trying nearby micro-columns before
            # pushing a gate into another bit lane.
            search_order = (
                (
                    (micro_column, radius)
                    for micro_column in range(5)
                    for radius in range(0, 160)
                )
                if key in collector_drivers
                else (
                    (micro_column, radius)
                    for radius in range(0, 160)
                    for micro_column in range(5)
                )
            )
            for micro_column, radius in search_order:
                candidate_ys = (
                    (ideal_y,)
                    if radius == 0
                    else (ideal_y - radius, ideal_y + radius)
                )
                for candidate_y in candidate_ys:
                    position = (stage_x + micro_column * 8, candidate_y)
                    rectangle = _bounds(component, position)
                    if any(
                        _overlap(rectangle, other, component_clearance)
                        for other in occupied
                    ):
                        continue
                    if corridor_intersects_rectangle(rectangle):
                        continue
                    row_conflicts = sum(
                        _terminal_access_position(
                            component,
                            position,
                            ref.pin,
                        )[1]
                        in terminal_rows[net.name]
                        for ref, net in terminal_refs.get(key, ())
                    )
                    corridor_blocked, candidate_corridors = corridor_plan(
                        key,
                        component,
                        position,
                    )
                    cost = (
                        radius + row_conflicts * 2 + corridor_blocked * 12,
                        corridor_blocked,
                        row_conflicts,
                        radius,
                        micro_column,
                        abs(candidate_y - ideal_y),
                        candidate_y,
                    )
                    if found_cost is None or cost < found_cost:
                        found = position
                        found_cost = cost
                        found_corridors = candidate_corridors
            if found is None:
                raise RuntimeError(f"growth floorplan could not attach component {key!r}")
            positions[key] = found
            occupied.append(_bounds(component, found))
            commit_corridor_plans(found_corridors)
            for ref, net in terminal_refs.get(key, ()):
                terminal_rows[net.name].add(
                    _terminal_access_position(component, found, ref.pin)[1]
                )

    logic_bounds = [
        _bounds(components[key], positions[key])
        for key in gate_keys
    ]
    logic_right = max((bounds[1] for bounds in logic_bounds), default=logic_start_x)
    logic_bottom = max((bounds[3] for bounds in logic_bounds), default=logic_base_y)

    maker_positions: dict[str, Point] = {}
    makers = sorted(
        (component for component in oriented.components if component.role == "maker"),
        key=lambda component: (component.affinity, component.key),
    )
    maker_cursor = logic_right + max(8, config.horizontal_clearance + 3)
    for component in makers:
        position = (maker_cursor, splitter_y)
        rectangle = _bounds(component, position)
        while any(_overlap(rectangle, other, 1) for other in occupied):
            position = (position[0] + 1, position[1])
            rectangle = _bounds(component, position)
        positions[component.key] = position
        maker_positions[component.key] = position
        occupied.append(rectangle)
        maker_cursor = rectangle[1] + bank_gap + 1

    maker_output_ports: set[str] = set()
    for component in oriented.components:
        if component.role != "output_port":
            continue
        maker_output_ports.update(
            [component.key]
            if any(
                components[source.component].role == "maker"
                for _sink, net in incoming[component.key]
                for source in net.sources
            )
            else []
        )
    if maker_output_ports:
        oriented = replace(
            oriented,
            components=tuple(
                replace(component, rotation=3)
                if component.key in maker_output_ports
                else component
                for component in oriented.components
            ),
        )
        components = oriented.component_by_key()

    output_positions: dict[str, Point] = {}
    direct_output_y = logic_bottom + max(8, config.vertical_clearance + 5)
    for component in sorted(
        (component for component in oriented.components if component.role == "output_port"),
        key=lambda component: (component.affinity, component.key),
    ):
        source_refs = [
            source
            for _sink, net in incoming[component.key]
            for source in net.sources
        ]
        maker_sources = [
            source for source in source_refs if components[source.component].role == "maker"
        ]
        if maker_sources:
            maker_position = positions[maker_sources[0].component]
            position = (maker_position[0], 0)
        else:
            source_xs = []
            for source in source_refs:
                source_component = components[source.component]
                source_position = positions[source.component]
                pin = _component_pin_position(
                    source_component,
                    source_position,
                    source.pin,
                )
                source_xs.append(pin[0] + 2)
            preferred_x = sorted(source_xs)[len(source_xs) // 2] if source_xs else maker_cursor
            position = (preferred_x, direct_output_y)
        rectangle = _bounds(component, position)
        while any(_overlap(rectangle, other, 1) for other in occupied):
            position = (position[0] + 1, position[1])
            rectangle = _bounds(component, position)
        positions[component.key] = position
        output_positions[component.key] = position
        occupied.append(rectangle)

    missing = set(components) - positions.keys()
    if missing:
        raise RuntimeError(f"growth floorplan omitted components: {sorted(missing)!r}")
    placed = oriented.with_positions(positions)
    actual_bounds = [
        _bounds(component, positions[component.key])
        for component in placed.components
    ]

    trunk_geometry = []
    placed_components = placed.component_by_key()
    for trunk in floorplan.input_trunks:
        lane_geometry = []
        for lane in trunk.lanes:
            source_component = placed_components[lane.source.component]
            source_position = positions[lane.source.component]
            pin = _component_pin_position(source_component, source_position, lane.source.pin)
            lane_geometry.append(
                {
                    "index": lane.index,
                    "net": lane.net,
                    "rail_x": pin[0],
                    "source_y": pin[1],
                    "arrival": lane.arrival,
                }
            )
        trunk_geometry.append(
            {
                "key": trunk.key,
                "input_port": trunk.input_port,
                "splitters": list(trunk.splitters),
                "lanes": lane_geometry,
            }
        )

    report = {
        "schema": "turingsynth-growth-floorplan-v2",
        "strategy": "bus-trunk-timing-growth-output-merge",
        "ownership": "conductor-first",
        "component_count": len(placed.components),
        "ranks": ranks,
        "timing": timing.to_dict(),
        "floorplan": floorplan.to_dict(),
        "input_frontier_networks": sorted(frontier_networks),
        "input_trunk_count": len(frontier_networks),
        "ordinary_global_trunk_count": 0,
        "planned_conductor_channel_count": len(conductor_spine_x),
        "planned_conductor_spines": dict(sorted(conductor_spine_x.items())),
        "bus_trunks": trunk_geometry,
        "splitter_y": splitter_y,
        "logic_start_x": logic_start_x,
        "logic_base_y": logic_base_y,
        "stage_pitch": stage_pitch,
        "affinity_pitch": affinity_pitch,
        "relocated_top_level_ports": True,
        "splitter_positions": {
            key: list(value) for key, value in splitter_positions.items()
        },
        "input_positions": {key: list(value) for key, value in input_positions.items()},
        "maker_positions": {key: list(value) for key, value in maker_positions.items()},
        "output_positions": {key: list(value) for key, value in output_positions.items()},
        "positions": {key: list(value) for key, value in positions.items()},
        "bounding_box": {
            "min_x": min(bounds[0] for bounds in actual_bounds),
            "max_x": max(bounds[1] for bounds in actual_bounds),
            "min_y": min(bounds[2] for bounds in actual_bounds),
            "max_y": max(bounds[3] for bounds in actual_bounds),
            "width": max(bounds[1] for bounds in actual_bounds)
            - min(bounds[0] for bounds in actual_bounds)
            + 1,
            "height": max(bounds[3] for bounds in actual_bounds)
            - min(bounds[2] for bounds in actual_bounds)
            + 1,
        },
        "component_overlap_count": 0,
    }
    return placed, report


# Public placement entry point used by both Verilog builds and v15 relayouts.
place = place_growth
