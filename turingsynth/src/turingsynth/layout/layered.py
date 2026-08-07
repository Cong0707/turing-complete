"""Compact deterministic DAG placement with stable bit affinity ordering."""

from __future__ import annotations

from collections import defaultdict
from turingsynth.config import ProjectConfig
from turingsynth.formats.model import Component, Point
from turingsynth.ir.physical import PhysicalComponent, PhysicalDesign
from turingsynth.mapping.native import INPUT, component_bounds, positioned_pins


def _prototype(component: PhysicalComponent, position: Point = (0, 0)) -> Component:
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
        custom_id=component.custom_id,
        custom_word_sizes=component.custom_word_sizes,
    )


def _bounds_at(component: PhysicalComponent, position: Point) -> tuple[int, int, int, int]:
    return component_bounds(_prototype(component, position))


def _driver_breakout(component: PhysicalComponent) -> int:
    """Maximum protected lead required by a driver bank on this component."""

    prototype = _prototype(component)
    groups: dict[Point, int] = defaultdict(int)
    for pin in positioned_pins(prototype):
        if pin.direction == INPUT:
            continue
        left, right, top, bottom = component_bounds(prototype)
        if pin.position[0] == left:
            direction = (-1, 0)
        elif pin.position[0] == right:
            direction = (1, 0)
        elif pin.position[1] == top:
            direction = (0, -1)
        elif pin.position[1] == bottom:
            direction = (0, 1)
        else:
            raise ValueError(f"pin {pin.name!r} is not on the component boundary")
        groups[direction] += 1
    return max((count + 1 for count in groups.values()), default=0)


def _overlap(
    left: tuple[int, int, int, int], right: tuple[int, int, int, int]
) -> bool:
    return not (
        left[1] < right[0]
        or right[1] < left[0]
        or left[3] < right[2]
        or right[3] < left[2]
    )


def _ranks(design: PhysicalDesign) -> dict[str, int]:
    """Assign strict global DAG ranks for monotonic left-to-right flow."""

    components = design.component_by_key()
    predecessors: dict[str, set[str]] = {key: set() for key in components}
    for net in design.nets:
        for sink in net.sinks:
            for source in net.sources:
                if sink.component == source.component:
                    continue
                predecessors[sink.component].add(source.component)
    pending = set(components)
    ranks: dict[str, int] = {}
    while pending:
        ready = sorted(
            key for key in pending if predecessors[key] <= ranks.keys()
        )
        if not ready:
            raise ValueError("physical component graph contains a cycle")
        for key in ready:
            ranks[key] = (
                max((ranks[value] + 1 for value in predecessors[key]), default=0)
            )
            pending.remove(key)
    maximum = max(ranks.values(), default=0)
    for key, component in components.items():
        if component.role == "output_port" and component.position is None:
            ranks[key] = maximum + 1
    return ranks


def _graph_neighbors(
    design: PhysicalDesign,
) -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    components = design.component_by_key()
    predecessors = {key: set() for key in components}
    successors = {key: set() for key in components}
    for net in design.nets:
        for sink in net.sinks:
            for source in net.sources:
                if source.component == sink.component:
                    continue
                predecessors[sink.component].add(source.component)
                successors[source.component].add(sink.component)
    return predecessors, successors


def _mean(values: list[float], default: float) -> float:
    return sum(values) / len(values) if values else default


def _ordered_layers(
    layers: dict[int, list[str]],
    components: dict[str, PhysicalComponent],
    ranks: dict[str, int],
    predecessors: dict[str, set[str]],
    successors: dict[str, set[str]],
) -> tuple[dict[int, list[str]], int]:
    """Order layers by generic DAG barycenters and reconvergent cones.

    No gate kind is special-cased. Producers which share any downstream
    consumer are treated as one visual block after the ordinary Sugiyama
    sweeps, so a local logic cone remains recognizable before routing.
    """

    ordered = {
        rank: sorted(keys, key=lambda key: (components[key].affinity, key))
        for rank, keys in layers.items()
    }

    def normalized_positions() -> dict[str, float]:
        result: dict[str, float] = {}
        for rank, keys in ordered.items():
            denominator = max(1, len(keys) - 1)
            result.update(
                {key: index / denominator for index, key in enumerate(keys)}
            )
        affinities = [component.affinity for component in components.values()]
        low = min(affinities, default=0.0)
        span = max(affinities, default=low) - low
        for key, component in components.items():
            if key not in result:
                result[key] = (
                    (component.affinity - low) / span if span else 0.5
                )
        return result

    for _iteration in range(6):
        positions = normalized_positions()
        for rank in sorted(ordered):
            previous_index = {
                key: index for index, key in enumerate(ordered[rank])
            }
            ordered[rank].sort(
                key=lambda key: (
                    _mean(
                        [positions[value] for value in predecessors[key]],
                        positions[key],
                    ),
                    previous_index[key],
                    key,
                )
            )
        positions = normalized_positions()
        for rank in sorted(ordered, reverse=True):
            previous_index = {
                key: index for index, key in enumerate(ordered[rank])
            }
            ordered[rank].sort(
                key=lambda key: (
                    _mean(
                        [positions[value] for value in successors[key]],
                        positions[key],
                    ),
                    previous_index[key],
                    key,
                )
            )

    cluster_count = 0
    positions = normalized_positions()
    for rank, keys in ordered.items():
        parent = {key: key for key in keys}

        def find(key: str) -> str:
            while parent[key] != key:
                parent[key] = parent[parent[key]]
                key = parent[key]
            return key

        def union(left: str, right: str) -> None:
            left, right = find(left), find(right)
            if left != right:
                parent[right] = left

        producers_by_consumer: dict[str, list[str]] = defaultdict(list)
        layer_keys = set(keys)
        for producer in keys:
            for consumer in successors[producer]:
                if ranks[consumer] > rank:
                    producers_by_consumer[consumer].append(producer)
        for producers in producers_by_consumer.values():
            producers = [key for key in producers if key in layer_keys]
            for producer in producers[1:]:
                union(producers[0], producer)

        blocks: dict[str, list[str]] = defaultdict(list)
        for key in keys:
            blocks[find(key)].append(key)
        cluster_count += sum(len(block) > 1 for block in blocks.values())
        old_index = {key: index for index, key in enumerate(keys)}
        block_values = []
        for block in blocks.values():
            block.sort(key=lambda key: (old_index[key], key))
            downstream = [
                positions[consumer]
                for key in block
                for consumer in successors[key]
                if ranks[consumer] > rank
            ]
            score = _mean(
                downstream,
                _mean([positions[key] for key in block], 0.5),
            )
            block_values.append((score, min(old_index[key] for key in block), block))
        ordered[rank] = [
            key
            for _score, _index, block in sorted(block_values)
            for key in block
        ]
    return ordered, cluster_count


def _pack_ordered_rows(
    ordered: list[str],
    desired: dict[str, float],
    components: dict[str, PhysicalComponent],
    vertical_clearance: int,
) -> dict[str, int]:
    """Closest compact integer rows under a fixed non-overlap order."""

    if not ordered:
        return {}
    prefix = [0]
    for previous, key in zip(ordered, ordered[1:]):
        _left, _right, _top, previous_bottom = _bounds_at(
            components[previous],
            (0, 0),
        )
        _left, _right, current_top, _bottom = _bounds_at(
            components[key],
            (0, 0),
        )
        gap = previous_bottom + vertical_clearance - current_top
        prefix.append(prefix[-1] + gap)

    # Pool-adjacent-violators solves the one-dimensional ordered compaction
    # problem after subtracting the mandatory component-to-component gaps.
    blocks: list[list[float | int]] = []
    for index, key in enumerate(ordered):
        value = desired[key] - prefix[index]
        blocks.append([index, index, value, 1])
        while len(blocks) >= 2:
            left, right = blocks[-2], blocks[-1]
            if float(left[2]) / int(left[3]) <= float(right[2]) / int(right[3]):
                break
            blocks[-2:] = [[
                int(left[0]),
                int(right[1]),
                float(left[2]) + float(right[2]),
                int(left[3]) + int(right[3]),
            ]]
    levels = [0.0] * len(ordered)
    for start, end, total, count in blocks:
        level = float(total) / int(count)
        for index in range(int(start), int(end) + 1):
            levels[index] = level
    return {
        key: round(levels[index]) + prefix[index]
        for index, key in enumerate(ordered)
    }


def _layer_rows(
    keys: list[str],
    components: dict[str, PhysicalComponent],
    vertical_clearance: int,
    desired: dict[str, float],
) -> dict[str, int]:
    return _pack_ordered_rows(keys, desired, components, vertical_clearance)


def _natural_columns(
    layers: dict[int, list[str]],
    components: dict[str, PhysicalComponent],
    horizontal_clearance: int,
    channel_tracks: dict[int, int],
    channel_expansion: dict[int, int],
) -> dict[int, int]:
    result: dict[int, int] = {}
    previous_right: int | None = None
    previous_breakout = 0
    for rank in sorted(layers):
        left_extent = min(
            _bounds_at(components[key], (0, 0))[0] for key in layers[rank]
        )
        right_extent = max(
            _bounds_at(components[key], (0, 0))[1] for key in layers[rank]
        )
        previous_rank = max(result) if result else None
        track_count = 0 if previous_rank is None else channel_tracks.get(previous_rank, 0)
        separation = max(
            horizontal_clearance,
            max(previous_breakout, track_count) + 3,
        )
        if previous_rank is not None:
            separation += channel_expansion.get(previous_rank, 0)
        center = 0 if previous_right is None else previous_right + separation - left_extent
        result[rank] = center
        previous_right = center + right_extent
        previous_breakout = max(
            (_driver_breakout(components[key]) for key in layers[rank]),
            default=0,
        )
    first_left = min(
        result[rank]
        + min(_bounds_at(components[key], (0, 0))[0] for key in layers[rank])
        for rank in layers
    )
    last_right = max(
        result[rank]
        + max(_bounds_at(components[key], (0, 0))[1] for key in layers[rank])
        for rank in layers
    )
    shift = -((first_left + last_right) // 2)
    return {rank: x + shift for rank, x in result.items()}


def _fit_level_columns(
    natural: dict[int, int],
    layers: dict[int, list[str]],
    components: dict[str, PhysicalComponent],
    clearance: int,
) -> dict[int, int]:
    inputs = [
        component
        for component in components.values()
        if component.role == "input_port" and component.position is not None
    ]
    dynamic_ranks = [
        rank
        for rank, keys in layers.items()
        if any(components[key].position is None for key in keys)
    ]
    if not inputs or not dynamic_ranks:
        return natural
    left = max(
        _bounds_at(component, component.position)[1]
        for component in inputs
    ) + clearance
    first_dynamic_left = min(
        natural[rank]
        + min(
            _bounds_at(components[key], (0, 0))[0]
            for key in layers[rank]
            if components[key].position is None
        )
        for rank in dynamic_ranks
    )
    shift = left - first_dynamic_left
    return {
        rank: x + shift if rank in dynamic_ranks else x
        for rank, x in natural.items()
    }


def _avoid_immutable_obstacles(
    columns: dict[int, int],
    layers: dict[int, list[str]],
    rows: dict[str, int],
    components: dict[str, PhysicalComponent],
    terminal_clearance: int = 2,
) -> tuple[dict[int, int], dict[int, int]]:
    """Shift complete downstream layers past fixed component obstacles.

    Two empty cells are required between bodies: one for the pin access point
    and one for the first legal turn. This prevents a perfectly non-overlapping
    component placement from nevertheless sealing a neighboring terminal.
    """

    immutable_bounds = [
        _bounds_at(component, component.position)
        for component in components.values()
        if component.position is not None
    ]
    result: dict[int, int] = {}
    shifts: dict[int, int] = {}
    cumulative_shift = 0
    for rank in sorted(layers):
        x = columns[rank] + cumulative_shift
        rank_shift = 0
        while True:
            required = 0
            for key in layers[rank]:
                left, right, top, bottom = _bounds_at(
                    components[key],
                    (x, rows[key]),
                )
                for fixed_left, fixed_right, fixed_top, fixed_bottom in immutable_bounds:
                    vertical_overlap = not (
                        bottom < fixed_top or fixed_bottom < top
                    )
                    horizontal_halo_overlap = not (
                        right < fixed_left - terminal_clearance
                        or left > fixed_right + terminal_clearance
                    )
                    if vertical_overlap and horizontal_halo_overlap:
                        required = max(
                            required,
                            fixed_right + terminal_clearance + 1 - left,
                        )
            if required <= 0:
                break
            x += required
            rank_shift += required
            cumulative_shift += required
        result[rank] = x
        if rank_shift:
            shifts[rank] = rank_shift
    return result, shifts


def place(
    design: PhysicalDesign,
    config: ProjectConfig,
    channel_expansion: dict[int, int] | None = None,
) -> tuple[PhysicalDesign, dict[str, object]]:
    channel_expansion = dict(channel_expansion or {})
    components = design.component_by_key()
    ranks = _ranks(design)
    predecessors, successors = _graph_neighbors(design)
    layers: dict[int, list[str]] = defaultdict(list)
    for key, rank in ranks.items():
        if components[key].position is None:
            layers[rank].append(key)
    ordered_layers, reconvergent_cluster_count = _ordered_layers(
        layers,
        components,
        ranks,
        predecessors,
        successors,
    )
    layers = defaultdict(list, ordered_layers)
    channel_tracks: dict[int, int] = defaultdict(int)
    for net in design.nets:
        if len(net.sinks) + len(net.additional_sources) > 1:
            channel_tracks[ranks[net.source.component]] += 1
    dynamic_components = [
        component for component in components.values() if component.position is None
    ]
    affinity_min = min(
        (component.affinity for component in dynamic_components),
        default=0.0,
    )
    affinity_max = max(
        (component.affinity for component in dynamic_components),
        default=0.0,
    )
    affinity_center = (affinity_min + affinity_max) / 2
    row_pitch = max(7, config.vertical_clearance + 4)
    affinity_target = {
        key: (component.affinity - affinity_center) * row_pitch
        for key, component in components.items()
    }
    rows: dict[str, int] = {}
    for rank, keys in layers.items():
        dynamic = [key for key in keys if components[key].position is None]
        rows.update(
            _layer_rows(
                dynamic,
                components,
                config.vertical_clearance,
                affinity_target,
            )
        )
    fixed_rows = {
        key: component.position[1]
        for key, component in components.items()
        if component.position is not None
    }
    for iteration in range(10):
        rank_order = (
            sorted(layers)
            if iteration % 2 == 0
            else sorted(layers, reverse=True)
        )
        known_rows = {**fixed_rows, **rows}
        for rank in rank_order:
            keys = layers[rank]
            desired: dict[str, float] = {}
            for key in keys:
                neighbor_rows = [
                    known_rows[value]
                    for value in predecessors[key] | successors[key]
                    if value in known_rows
                ]
                if neighbor_rows:
                    desired[key] = _mean(neighbor_rows, affinity_target[key])
                else:
                    desired[key] = affinity_target[key]
            packed = _layer_rows(
                keys,
                components,
                config.vertical_clearance,
                desired,
            )
            rows.update(packed)
            known_rows.update(packed)
    columns = _natural_columns(
        layers,
        components,
        config.horizontal_clearance,
        channel_tracks,
        channel_expansion,
    )
    if design.target_kind == "level":
        columns = _fit_level_columns(
            columns, layers, components, config.horizontal_clearance
        )
    columns, immutable_obstacle_shifts = _avoid_immutable_obstacles(
        columns,
        layers,
        rows,
        components,
    )
    positions: dict[str, Point] = {
        key: component.position
        for key, component in components.items()
        if component.position is not None
    }
    occupied = [
        _bounds_at(components[key], position) for key, position in positions.items()
    ]
    for rank in sorted(layers):
        dynamic = [key for key in layers[rank] if components[key].position is None]
        if not dynamic:
            continue
        shifts = [0]
        for offset in range(1, 10_001):
            shifts.extend((-offset, offset))
        for shift in shifts:
            proposed = {
                key: (columns[rank], rows[key] + shift) for key in dynamic
            }
            rectangles = [
                _bounds_at(components[key], position)
                for key, position in proposed.items()
            ]
            if not any(_overlap(rectangle, other) for rectangle in rectangles for other in occupied):
                positions.update(proposed)
                occupied.extend(rectangles)
                break
        else:
            raise RuntimeError("could not place a collision-free component layer")
    placed = design.with_positions(positions)
    all_bounds = [
        _bounds_at(component, positions[component.key])
        for component in placed.components
    ]
    minimum_x = min(item[0] for item in all_bounds)
    maximum_x = max(item[1] for item in all_bounds)
    minimum_y = min(item[2] for item in all_bounds)
    maximum_y = max(item[3] for item in all_bounds)
    report = {
        "schema": "turingsynth-layered-layout-v1",
        "layer_count": len(layers),
        "component_count": len(placed.components),
        "bounding_box": {
            "min_x": minimum_x,
            "max_x": maximum_x,
            "min_y": minimum_y,
            "max_y": maximum_y,
            "width": maximum_x - minimum_x + 1,
            "height": maximum_y - minimum_y + 1,
            "area": (maximum_x - minimum_x + 1) * (maximum_y - minimum_y + 1),
        },
        "ranks": ranks,
        "fanout_track_capacity": channel_tracks,
        "channel_expansion": dict(sorted(channel_expansion.items())),
        "immutable_obstacle_column_shift": immutable_obstacle_shifts,
        "global_bit_rails": {
            "affinity_center": affinity_center,
            "row_pitch": row_pitch,
        },
        "reconvergent_cluster_count": reconvergent_cluster_count,
        "layer_order": {
            str(rank): list(keys) for rank, keys in sorted(layers.items())
        },
        "positions": {key: list(position) for key, position in positions.items()},
        "component_overlap_count": 0,
    }
    return placed, report
