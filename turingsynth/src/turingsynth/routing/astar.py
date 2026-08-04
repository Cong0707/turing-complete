"""Deterministic orthogonal routing with fanout trunks and overlap avoidance."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from heapq import heappop, heappush
from turingsynth.formats.model import Component, Point, Wire
from turingsynth.formats.wire import wire_from_vertices, wire_points
from turingsynth.ir.physical import PhysicalComponent, PhysicalDesign, PinRef
from turingsynth.mapping.native import INPUT, component_bounds, positioned_pins


DIRECTIONS: tuple[Point, ...] = (
    (1, 0),
    (0, 1),
    (-1, 0),
    (0, -1),
)


@dataclass(frozen=True)
class RoutedEdge:
    network: str
    source: Point
    sink: Point
    role: str = "direct"


@dataclass(frozen=True)
class RoutingResult:
    wires: tuple[Wire, ...]
    edges: tuple[RoutedEdge, ...]
    report: dict[str, object]


class FanoutTrackCapacityError(RuntimeError):
    """Placement channel is too narrow for legal protected fanout tracks."""

    def __init__(
        self,
        network: str,
        message: str,
        *,
        networks: tuple[str, ...] | None = None,
    ) -> None:
        super().__init__(message)
        self.network = network
        self.networks = networks or (network,)


@dataclass(frozen=True)
class _FanoutTrackRequest:
    network: str
    source: Point
    sinks: tuple[Point, ...]
    candidates: tuple[int, ...]
    low_y: int
    high_y: int


def _component(component: PhysicalComponent) -> Component:
    if component.position is None:
        raise ValueError(f"component {component.key!r} has not been placed")
    return Component(
        kind=component.kind,
        position=component.position,
        rotation=component.rotation,
        permanent_id=component.permanent_id,
        user_label=component.user_label,
        settings=component.settings,
        ui_order=component.ui_order,
        word_size=component.word_size,
        immutable=component.immutable,
    )


def _edge(left: Point, right: Point) -> tuple[Point, Point]:
    return (left, right) if left <= right else (right, left)


def _horizontal_port(hub: Point, terminal: Point) -> Point:
    if hub[1] != terminal[1] or hub[0] == terminal[0]:
        raise ValueError(f"tap/feeder is not horizontal: {hub} -> {terminal}")
    direction = 1 if terminal[0] > hub[0] else -1
    return (hub[0] + direction, hub[1])


def _horizontal_lead(hub: Point, terminal: Point, length: int = 2) -> tuple[Point, ...]:
    """Return the protected horizontal cells from a trunk toward a terminal."""

    if hub[1] != terminal[1]:
        raise ValueError(f"tap/feeder is not horizontal: {hub} -> {terminal}")
    if hub == terminal:
        return ()
    direction = 1 if terminal[0] > hub[0] else -1
    distance = abs(terminal[0] - hub[0])
    return tuple(
        (hub[0] + direction * step, hub[1])
        for step in range(1, min(length, distance) + 1)
    )


def _lead_escape_options(
    hub: Point,
    terminal: Point,
    *,
    forbidden: frozenset[Point],
    reserved: frozenset[Point] = frozenset(),
    bounds: tuple[int, int, int, int],
) -> tuple[Point, ...]:
    """Return legal first routing cells beyond a protected fanout lead.

    The lead cell nearest the terminal becomes an A* endpoint.  It must not be
    left in a pocket whose only free edge returns through the protected lead.
    A lead which already reaches the terminal needs no additional escape cell.
    """

    lead = _horizontal_lead(hub, terminal)
    if not lead:
        return (terminal,)
    endpoint = lead[-1]
    if endpoint == terminal:
        return (terminal,)
    previous = hub if len(lead) == 1 else lead[-2]
    min_x, min_y, max_x, max_y = bounds
    result = []
    for dx, dy in DIRECTIONS:
        point = (endpoint[0] + dx, endpoint[1] + dy)
        if point == previous:
            continue
        if not (min_x <= point[0] <= max_x and min_y <= point[1] <= max_y):
            continue
        if point != terminal and (point in forbidden or point in reserved):
            continue
        result.append(point)
    return tuple(result)


def _fanout_escape_options(
    request: _FanoutTrackRequest,
    x: int,
    *,
    forbidden: frozenset[Point],
    reserved: frozenset[Point] = frozenset(),
    bounds: tuple[int, int, int, int],
) -> tuple[tuple[Point, ...], ...]:
    return tuple(
        _lead_escape_options(
            (x, terminal[1]),
            terminal,
            forbidden=forbidden,
            reserved=reserved,
            bounds=bounds,
        )
        for terminal in (request.source, *request.sinks)
    )


def _pin_access_point(component: Component, pin: Point) -> Point:
    """Return the first grid point immediately outside a component pin."""

    left, right, top, bottom = component_bounds(component)
    x, y = pin
    if x == left:
        return (x - 1, y)
    if x == right:
        return (x + 1, y)
    if y == top:
        return (x, y - 1)
    if y == bottom:
        return (x, y + 1)
    raise ValueError(
        f"pin {pin} for component kind {component.kind} is not on its boundary"
    )


def _pin_access_path(
    component: Component, pin: Point, *, length: int
) -> tuple[Point, ...]:
    """Reserve a straight pin lead of an explicitly assigned length."""

    if length < 1:
        raise ValueError("pin access length must be positive")
    first = _pin_access_point(component, pin)
    dx, dy = first[0] - pin[0], first[1] - pin[1]
    return tuple((pin[0] + dx * step, pin[1] + dy * step) for step in range(1, length + 1))


def _opposite_diagonal(left: Point, right: Point) -> tuple[Point, Point] | None:
    if abs(left[0] - right[0]) != 1 or abs(left[1] - right[1]) != 1:
        return None
    return _edge((left[0], right[1]), (right[0], left[1]))


def _vertices(points: tuple[Point, ...]) -> tuple[Point, ...]:
    if len(points) < 2:
        raise ValueError("route has fewer than two points")
    result = [points[0]]
    previous_direction: Point | None = None
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


def _manhattan(left: Point, right: Point) -> int:
    dx = abs(left[0] - right[0])
    dy = abs(left[1] - right[1])
    return 10 * (dx + dy)


def _search(
    network: str,
    start: Point,
    goal: Point,
    *,
    body: frozenset[Point],
    pins: frozenset[Point],
    edge_owner: dict[tuple[Point, Point], str],
    point_owner: dict[Point, set[str]],
    bounds: tuple[int, int, int, int],
    strict_monotonic: bool = False,
) -> tuple[Point, ...]:
    blocked = (body | pins) - {start, goal}
    min_x, min_y, max_x, max_y = bounds
    start_state = (start, -1)
    frontier: list[tuple[int, int, int, int, int, Point, int]] = []
    heappush(frontier, (_manhattan(start, goal), 0, start[0], start[1], -1, start, -1))
    best: dict[tuple[Point, int], int] = {start_state: 0}
    previous: dict[tuple[Point, int], tuple[Point, int]] = {}
    final: tuple[Point, int] | None = None
    while frontier:
        _score, cost, _x, _y, _sort_dir, point, previous_direction = heappop(frontier)
        state = (point, previous_direction)
        if cost != best.get(state):
            continue
        if point == goal:
            final = state
            break
        ordered = sorted(
            enumerate(DIRECTIONS),
            key=lambda item: (
                _manhattan((point[0] + item[1][0], point[1] + item[1][1]), goal),
                item[0],
            ),
        )
        for direction_index, (dx, dy) in ordered:
            foreign_owners = point_owner.get(point, set()) - {network}
            if (
                foreign_owners
                and previous_direction >= 0
                and direction_index != previous_direction
            ):
                continue
            neighbor = (point[0] + dx, point[1] + dy)
            if not (min_x <= neighbor[0] <= max_x and min_y <= neighbor[1] <= max_y):
                continue
            if neighbor in blocked:
                continue
            if (
                strict_monotonic
                and _manhattan(neighbor, goal) > _manhattan(point, goal)
            ):
                continue
            used_edge = _edge(point, neighbor)
            if used_edge in edge_owner:
                continue
            step_cost = 10
            if previous_direction >= 0 and direction_index != previous_direction:
                step_cost += 70
                if (
                    (direction_index - previous_direction) % len(DIRECTIONS)
                    == len(DIRECTIONS) // 2
                ):
                    step_cost += 180
            if _manhattan(neighbor, goal) > _manhattan(point, goal):
                step_cost += 120
            owners = point_owner.get(neighbor, set())
            if owners and neighbor not in {start, goal}:
                step_cost += 8 if owners == {network} else 24
            crossed = _opposite_diagonal(point, neighbor)
            if crossed is not None and crossed in edge_owner:
                step_cost += 120
            candidate = cost + step_cost
            next_state = (neighbor, direction_index)
            if candidate >= best.get(next_state, 1 << 60):
                continue
            best[next_state] = candidate
            previous[next_state] = state
            heappush(
                frontier,
                (
                    candidate + _manhattan(neighbor, goal),
                    candidate,
                    neighbor[0],
                    neighbor[1],
                    direction_index,
                    neighbor,
                    direction_index,
                ),
            )
    if final is None:
        def incident(point: Point) -> list[str]:
            result = []
            for dx, dy in DIRECTIONS:
                neighbor = (point[0] + dx, point[1] + dy)
                owner = edge_owner.get(_edge(point, neighbor))
                if neighbor in blocked:
                    state = "blocked"
                elif owner is not None:
                    state = f"edge={owner}"
                elif not (
                    min_x <= neighbor[0] <= max_x
                    and min_y <= neighbor[1] <= max_y
                ):
                    state = "outside"
                else:
                    state = "open"
                result.append(f"{neighbor}:{state}")
            return result

        reached_points = {point for point, _direction in best}
        closest = min((_manhattan(point, goal) for point in reached_points), default=-1)
        closest_states = sorted(
            (
                point,
                direction,
                sorted(point_owner.get(point, set())),
            )
            for point, direction in best
            if _manhattan(point, goal) == closest
        )[:8]
        straight_blocked = []
        if start[0] == goal[0] or start[1] == goal[1]:
            if start[1] == goal[1]:
                step = 1 if goal[0] > start[0] else -1
                straight_points = (
                    (x, start[1]) for x in range(start[0] + step, goal[0], step)
                )
            else:
                step = 1 if goal[1] > start[1] else -1
                straight_points = (
                    (start[0], y) for y in range(start[1] + step, goal[1], step)
                )
            straight_blocked = [
                (
                    point,
                    point in body,
                    point in pins,
                    sorted(point_owner.get(point, set())),
                )
                for point in straight_points
                if point in blocked or point_owner.get(point)
            ][:16]
        raise RuntimeError(
            f"no route for {network}: {start} -> {goal}; "
            f"reached={len(reached_points)}, closest={closest}, "
            f"closest_states={closest_states}, "
            f"straight_blocked={straight_blocked}, "
            f"start_incident={incident(start)}, goal_incident={incident(goal)}"
        )
    points = [final[0]]
    while final != start_state:
        final = previous[final]
        points.append(final[0])
    points.reverse()
    return tuple(points)


def _nearest_free(
    preferred: Point,
    *,
    forbidden: frozenset[Point],
    reserved: set[Point],
    bounds: tuple[int, int, int, int],
    minimum_degree: int = 1,
) -> Point:
    min_x, min_y, max_x, max_y = bounds

    def usable(point: Point) -> bool:
        if (
            not (min_x <= point[0] <= max_x and min_y <= point[1] <= max_y)
            or point in forbidden
            or point in reserved
        ):
            return False
        open_neighbors = sum(
            min_x <= point[0] + dx <= max_x
            and min_y <= point[1] + dy <= max_y
            and (point[0] + dx, point[1] + dy) not in forbidden
            and (point[0] + dx, point[1] + dy) not in reserved
            for dx, dy in DIRECTIONS
        )
        return open_neighbors >= minimum_degree

    for radius in range(0, 64):
        candidates = []
        for dx in range(-radius, radius + 1):
            dy = radius - abs(dx)
            candidates.append((preferred[0] + dx, preferred[1] + dy))
            if dy:
                candidates.append((preferred[0] + dx, preferred[1] - dy))
        for point in sorted(set(candidates)):
            if usable(point):
                return point
    raise RuntimeError(
        f"no free fanout hub near {preferred} with degree {minimum_degree}"
    )


def _nearest_free_on_channel(
    preferred: Point,
    *,
    forbidden: frozenset[Point],
    reserved: set[Point],
    bounds: tuple[int, int, int, int],
    minimum_degree: int,
) -> Point:
    """Keep a hub on its routing channel whenever that column has space."""

    min_x, min_y, max_x, max_y = bounds
    channel_x, preferred_y = preferred

    def has_capacity(point: Point) -> bool:
        return sum(
            min_x <= point[0] + dx <= max_x
            and min_y <= point[1] + dy <= max_y
            and (point[0] + dx, point[1] + dy) not in forbidden
            and (point[0] + dx, point[1] + dy) not in reserved
            for dx, dy in DIRECTIONS
        ) >= minimum_degree

    if min_x <= channel_x <= max_x:
        maximum_offset = max(preferred_y - min_y, max_y - preferred_y)
        for offset in range(maximum_offset + 1):
            candidates = (
                (channel_x, preferred_y),
                (channel_x, preferred_y - offset),
                (channel_x, preferred_y + offset),
            )
            for point in dict.fromkeys(candidates):
                if (
                    min_y <= point[1] <= max_y
                    and point not in forbidden
                    and point not in reserved
                    and has_capacity(point)
                ):
                    return point
    return _nearest_free(
        preferred,
        forbidden=forbidden,
        reserved=reserved,
        bounds=bounds,
        minimum_degree=minimum_degree,
    )


def _fanout_channel_x(source: Point, sinks: tuple[Point, ...], direction: int) -> int:
    """Choose an integer channel between the source and the nearest sink layer."""

    distances = [
        (sink[0] - source[0]) * direction
        for sink in sinks
        if (sink[0] - source[0]) * direction > 0
    ]
    if not distances:
        return source[0] + direction
    nearest = min(distances)
    if nearest == 1:
        # There is no integer column between the two pin columns. Branch on
        # the source pin column outside the source body instead of entering
        # the downstream component layer.
        return source[0]
    distance = max(1, nearest // 2)
    return source[0] + direction * min(distance, nearest - 1)


def _fanout_track_x(
    source: Point,
    sinks: tuple[Point, ...],
    *,
    forbidden: frozenset[Point],
    reserved: set[Point],
    track_intervals: dict[int, list[tuple[int, int, str]]],
    network: str,
    bounds: tuple[int, int, int, int],
) -> int:
    candidates, direction, track_min, track_max = _fanout_track_candidates(
        source,
        sinks,
        forbidden=forbidden,
        bounds=bounds,
    )
    low_y = min((source[1], *(sink[1] for sink in sinks)))
    high_y = max((source[1], *(sink[1] for sink in sinks)))
    terminals = (source, *sinks)
    for x in candidates:
        if any(
            not (high_y < other_low or low_y > other_high)
            for other_low, other_high, _owner in track_intervals.get(x, ())
        ):
            continue
        if any((x, y) in reserved for y in range(low_y, high_y + 1)):
            continue
        leads = tuple(
            _horizontal_lead((x, terminal[1]), terminal)
            for terminal in terminals
        )
        if any(point in reserved for lead in leads for point in lead):
            continue
        if any(
            any(
                other_low <= point[1] <= other_high
                for other_low, other_high, _ in track_intervals.get(point[0], ())
            )
            for lead in leads
            for point in lead
        ):
            continue
        track_intervals.setdefault(x, []).append((low_y, high_y, network))
        return x
    raise RuntimeError(
        f"no vertical fanout track for {network}: x={track_min}..{track_max}, "
        f"y={low_y}..{high_y}, direction={direction}"
    )


def _fanout_track_candidates(
    source: Point,
    sinks: tuple[Point, ...],
    *,
    forbidden: frozenset[Point],
    bounds: tuple[int, int, int, int],
) -> tuple[tuple[int, ...], int, int, int]:
    """Return statically legal trunk columns in source-to-consumer order."""

    deltas = [sink[0] - source[0] for sink in sinks]
    if all(delta > 0 for delta in deltas):
        direction = 1
        track_min = source[0] + 1
        track_max = min(sink[0] for sink in sinks) - 1
        raw_candidates = range(track_min, track_max + 1)
    elif all(delta < 0 for delta in deltas):
        direction = -1
        track_min = max(sink[0] for sink in sinks) + 1
        track_max = source[0] - 1
        raw_candidates = range(track_max, track_min - 1, -1)
    else:
        direction = 0
        terminal_xs = [source[0], *(sink[0] for sink in sinks)]
        track_min = min(terminal_xs) + 1
        track_max = max(terminal_xs) - 1
        middle = sorted(terminal_xs)[len(terminal_xs) // 2]
        raw_candidates = sorted(
            range(track_min, track_max + 1),
            key=lambda x: (abs(x - middle), x),
        )
    low_y = min((source[1], *(sink[1] for sink in sinks)))
    high_y = max((source[1], *(sink[1] for sink in sinks)))
    min_x, _min_y, max_x, _max_y = bounds
    terminals = (source, *sinks)
    candidates = []
    for x in raw_candidates:
        if not min_x <= x <= max_x:
            continue
        if any((x, y) in forbidden for y in range(low_y, high_y + 1)):
            continue
        if any(terminal[0] == x for terminal in terminals):
            continue
        leads = tuple(
            _horizontal_lead((x, terminal[1]), terminal)
            for terminal in terminals
        )
        if any(
            point in forbidden and point != terminal
            for lead, terminal in zip(leads, terminals)
            for point in lead
        ):
            continue
        request = _FanoutTrackRequest(
            network="",
            source=source,
            sinks=sinks,
            candidates=(),
            low_y=low_y,
            high_y=high_y,
        )
        if any(
            not options
            for options in _fanout_escape_options(
                request,
                x,
                forbidden=forbidden,
                bounds=bounds,
            )
        ):
            continue
        candidates.append(x)
    return tuple(candidates), direction, track_min, track_max


def _fanout_protected_points(request: _FanoutTrackRequest, x: int) -> frozenset[Point]:
    terminals = (request.source, *request.sinks)
    hubs = {(x, terminal[1]) for terminal in terminals}
    return frozenset(hubs)


def _point_on_track(
    point: Point, track_intervals: dict[int, list[tuple[int, int, str]]]
) -> bool:
    return any(
        low_y <= point[1] <= high_y
        for low_y, high_y, _network in track_intervals.get(point[0], ())
    )


def _plan_fanout_tracks(
    specifications: tuple[tuple[str, Point, tuple[Point, ...]], ...],
    *,
    forbidden: frozenset[Point],
    protected_owners: dict[Point, frozenset[str]] | None = None,
    blocked_track_intervals: dict[int, tuple[tuple[int, int, str], ...]] | None = None,
    bounds: tuple[int, int, int, int],
) -> dict[str, int]:
    """Assign every fanout trunk before reserving any tap or hub.

    Tap/hub points are hard electrical obstacles. Ordinary trunk interiors are
    intentionally not reserved as points so unrelated ordinary wires may cross
    them orthogonally.
    """

    requests = []
    blocked_track_intervals = blocked_track_intervals or {}
    windows: dict[str, tuple[int, int, int]] = {}
    for network, source, sinks in specifications:
        candidates, direction, track_min, track_max = _fanout_track_candidates(
            source,
            sinks,
            forbidden=forbidden,
            bounds=bounds,
        )
        low_y = min((source[1], *(sink[1] for sink in sinks)))
        high_y = max((source[1], *(sink[1] for sink in sinks)))
        windows[network] = (direction, track_min, track_max)
        request = _FanoutTrackRequest(
            network=network,
            source=source,
            sinks=sinks,
            candidates=candidates,
            low_y=low_y,
            high_y=high_y,
        )
        protected_owners = protected_owners or {}
        requests.append(
            _FanoutTrackRequest(
                network=request.network,
                source=request.source,
                sinks=request.sinks,
                candidates=tuple(
                    x
                    for x in request.candidates
                    if not any(
                        protected_owners.get(point, frozenset()) - {network}
                        for point in _fanout_protected_points(request, x)
                    )
                ),
                low_y=request.low_y,
                high_y=request.high_y,
            )
        )

    empty = [request for request in requests if not request.candidates]
    if empty:
        request = empty[0]
        direction, track_min, track_max = windows[request.network]
        raise FanoutTrackCapacityError(
            request.network,
            f"no static vertical fanout track for {request.network}: "
            f"x={track_min}..{track_max}, y={request.low_y}..{request.high_y}, "
            f"direction={direction}"
        )

    orderings = (
        lambda request: (
            -(request.high_y - request.low_y),
            len(request.candidates),
            -len(request.sinks),
            request.network,
        ),
        lambda request: (
            len(request.candidates),
            -(request.high_y - request.low_y),
            -len(request.sinks),
            request.network,
        ),
        lambda request: (
            -len(request.sinks),
            -(request.high_y - request.low_y),
            len(request.candidates),
            request.network,
        ),
    )
    successes: list[dict[str, int]] = []
    failures: list[tuple[str, int]] = []
    for order_key in orderings:
        intervals: dict[int, list[tuple[int, int, str]]] = {
            x: list(values) for x, values in blocked_track_intervals.items()
        }
        protected: set[Point] = set()
        escape_guards: list[set[Point]] = []
        assignments: dict[str, int] = {}
        failed: tuple[str, int] | None = None
        for request in sorted(requests, key=order_key):
            viable = []
            for x in request.candidates:
                if any(
                    not (
                        request.high_y < other_low
                        or request.low_y > other_high
                    )
                    for other_low, other_high, _owner in intervals.get(x, ())
                ):
                    continue
                if any(
                    point[0] == x and request.low_y <= point[1] <= request.high_y
                    for point in protected
                ):
                    continue
                request_points = _fanout_protected_points(request, x)
                if request_points & protected:
                    continue
                if any(options <= request_points for options in escape_guards):
                    continue
                if any(_point_on_track(point, intervals) for point in request_points):
                    continue
                escape_options = _fanout_escape_options(
                    request,
                    x,
                    forbidden=forbidden,
                    reserved=frozenset(protected | request_points),
                    bounds=bounds,
                )
                if any(not options for options in escape_options):
                    continue
                viable.append(x)
            if not viable:
                failed = (request.network, len(request.candidates))
                break
            x = min(
                viable,
                key=lambda candidate: (
                    abs(candidate - request.source[0]),
                    sum(abs(sink[0] - candidate) for sink in request.sinks),
                    -candidate if request.sinks[0][0] > request.source[0] else candidate,
                ),
            )
            assignments[request.network] = x
            intervals.setdefault(x, []).append(
                (request.low_y, request.high_y, request.network)
            )
            request_points = _fanout_protected_points(request, x)
            escape_options = _fanout_escape_options(
                request,
                x,
                forbidden=forbidden,
                reserved=frozenset(protected | request_points),
                bounds=bounds,
            )
            for options in escape_guards:
                options.difference_update(request_points)
            for terminal, options in zip(
                (request.source, *request.sinks),
                escape_options,
            ):
                lead = _horizontal_lead((x, terminal[1]), terminal)
                if lead[-1] != terminal:
                    escape_guards.append(set(options))
            protected.update(request_points)
        if failed is None:
            successes.append(assignments)
        else:
            failures.append(failed)
    if not successes:
        detail = ", ".join(
            f"{network}({candidate_count} candidates)"
            for network, candidate_count in failures
        )
        failed_networks = tuple(dict.fromkeys(network for network, _count in failures))
        network = failed_networks[0]
        raise FanoutTrackCapacityError(
            network,
            f"global fanout track assignment failed: {detail}",
            networks=failed_networks,
        )
    return min(
        successes,
        key=lambda assignment: (
            sum(
                abs(assignment[request.network] - request.source[0])
                for request in requests
            ),
            sum(
                abs(assignment[request.network] - request.source[0])
                + sum(
                    abs(sink[0] - assignment[request.network])
                    for sink in request.sinks
                )
                for request in requests
            ),
            tuple(sorted(assignment.items())),
        ),
    )


def _fanout_edges(
    network: str,
    source: Point,
    sinks: tuple[Point, ...],
    *,
    routing_source: Point,
    routing_sinks: tuple[Point, ...],
    forbidden: frozenset[Point],
    reserved: set[Point],
    track_intervals: dict[int, list[tuple[int, int, str]]],
    bounds: tuple[int, int, int, int],
    channel_x: int | None = None,
) -> tuple[RoutedEdge, ...]:
    if len(sinks) == 1 and channel_x is None:
        return (RoutedEdge(network, source, sinks[0]),)
    terminal_pairs = sorted(
        zip(sinks, routing_sinks),
        key=lambda pair: (pair[1][1], pair[1][0], pair[0]),
    )
    ordered_sinks = tuple(pair[0] for pair in terminal_pairs)
    ordered_routing_sinks = tuple(pair[1] for pair in terminal_pairs)
    if channel_x is None:
        channel_x = _fanout_track_x(
            routing_source,
            ordered_routing_sinks,
            forbidden=forbidden,
            reserved=reserved,
            track_intervals=track_intervals,
            network=network,
            bounds=bounds,
        )
    else:
        low_y = min((routing_source[1], *(sink[1] for sink in ordered_routing_sinks)))
        high_y = max((routing_source[1], *(sink[1] for sink in ordered_routing_sinks)))
        track_intervals.setdefault(channel_x, []).append((low_y, high_y, network))
    source_hub = (channel_x, routing_source[1])
    taps = [(channel_x, sink[1]) for sink in ordered_routing_sinks]
    hubs = sorted(set((source_hub, *taps)), key=lambda point: (point[1], point[0]))
    reserved.update(hubs)
    result = [RoutedEdge(network, source, source_hub, "feeder")]
    result.extend(
        RoutedEdge(network, tap, sink, "tap")
        for tap, sink in zip(taps, ordered_sinks)
    )
    for left, right in zip(hubs, hubs[1:]):
        result.append(RoutedEdge(network, left, right, "trunk"))
    return tuple(result)


def _collector_edges(
    network: str,
    source: Point,
    sinks: tuple[Point, ...],
    *,
    routing_source: Point,
    routing_sinks: tuple[Point, ...],
    forbidden: frozenset[Point],
    reserved: set[Point],
    track_intervals: dict[int, list[tuple[int, int, str]]],
    horizontal_intervals: dict[int, list[tuple[int, int, str]]],
    bounds: tuple[int, int, int, int],
) -> tuple[RoutedEdge, ...]:
    """Route a resolved owner as a clear spine with short terminal taps."""

    physical = (source, *sinks)
    terminals = (routing_source, *routing_sinks)
    if len(physical) != len(terminals):
        raise ValueError("collector physical/routing terminal populations differ")
    min_x, min_y, max_x, max_y = bounds
    center_y = sorted(point[1] for point in terminals)[len(terminals) // 2]
    terminal_high = max(point[1] for point in terminals)
    candidate_rows = sorted(
        range(min_y, max_y + 1),
        key=lambda y: (
            0 if y > terminal_high else 1,
            abs(y - center_y),
            y,
        ),
    )
    chosen: tuple[
        int,
        list[tuple[Point, Point, Point, str]],
        dict[int, list[tuple[int, int, str]]],
        dict[int, list[tuple[int, int, str]]],
        set[Point],
    ] | None = None
    for spine_y in candidate_rows:
        staged_vertical: dict[int, list[tuple[int, int, str]]] = defaultdict(list)
        staged_horizontal: dict[int, list[tuple[int, int, str]]] = defaultdict(list)
        staged_hubs: set[Point] = set()
        records: list[tuple[Point, Point, Point, str]] = []
        failed = False
        for index, (pin, terminal) in enumerate(zip(physical, terminals)):
            outward = (
                1
                if terminal[0] > pin[0]
                else -1
                if terminal[0] < pin[0]
                else 1
            )
            offsets = tuple(
                dict.fromkeys(
                    (
                        *range(outward, outward * 13, outward),
                        *range(-outward, -outward * 9, -outward),
                    )
                )
            )
            branch_choice: tuple[Point, Point] | None = None
            for offset in offsets:
                branch_x = terminal[0] + offset
                if not min_x <= branch_x <= max_x:
                    continue
                tap_hub = (branch_x, terminal[1])
                spine_hub = (branch_x, spine_y)
                tap = _axis_points(terminal, tap_hub)
                branch = _axis_points(tap_hub, spine_hub)
                if any(
                    point in forbidden and point != terminal
                    for point in tap[1:]
                ):
                    continue
                if any(point in forbidden for point in branch):
                    continue
                if (set(tap[1:]) | set(branch)) & (reserved | staged_hubs):
                    continue
                low_y, high_y = sorted((tap_hub[1], spine_hub[1]))
                if any(
                    not (high_y < other_low or low_y > other_high)
                    for other_low, other_high, _owner in (
                        *track_intervals.get(branch_x, ()),
                        *staged_vertical.get(branch_x, ()),
                    )
                ):
                    continue
                tap_low, tap_high = sorted((terminal[0], tap_hub[0]))
                if any(
                    min(tap_high, other_high) >= max(tap_low, other_low)
                    for other_low, other_high, _owner in (
                        *horizontal_intervals.get(terminal[1], ()),
                        *staged_horizontal.get(terminal[1], ()),
                    )
                ):
                    continue
                branch_choice = tap_hub, spine_hub
                break
            if branch_choice is None:
                failed = True
                break
            tap_hub, spine_hub = branch_choice
            role = "feeder" if index == 0 else "tap"
            records.append((pin, terminal, tap_hub, role))
            low_y, high_y = sorted((tap_hub[1], spine_hub[1]))
            staged_vertical[tap_hub[0]].append((low_y, high_y, network))
            tap_low, tap_high = sorted((terminal[0], tap_hub[0]))
            staged_horizontal[terminal[1]].append(
                (tap_low, tap_high, network)
            )
            staged_hubs.update((tap_hub, spine_hub))
        if failed:
            continue
        spine_hubs = sorted(
            {(tap_hub[0], spine_y) for _pin, _terminal, tap_hub, _role in records}
        )
        low_x, high_x = spine_hubs[0][0], spine_hubs[-1][0]
        spine = _axis_points(spine_hubs[0], spine_hubs[-1])
        if any(point in forbidden or point in reserved for point in spine):
            continue
        if any(
            not (high_x < other_low or low_x > other_high)
            for other_low, other_high, _owner in horizontal_intervals.get(
                spine_y, ()
            )
        ):
            continue
        chosen = (
            spine_y,
            records,
            staged_vertical,
            staged_horizontal,
            staged_hubs,
        )
        break
    if chosen is None:
        # Conservative but still conductor-first fallback: put one straight
        # owner spine in the empty margin and let each terminal grow toward a
        # unique socket.  This is used only when dense neighboring pin columns
        # leave no terminal-near vertical branch.
        fallback: tuple[int, list[Point], list[Point]] | None = None
        used_xs: set[int] = set()
        hub_xs = []
        for terminal in terminals:
            candidates = sorted(
                range(min_x + 2, max_x - 1),
                key=lambda x: (abs(x - terminal[0]), x),
            )
            hub_x = next((x for x in candidates if x not in used_xs), None)
            if hub_x is None:
                break
            used_xs.add(hub_x)
            hub_xs.append(hub_x)
        if len(hub_xs) == len(terminals):
            low_hub_x, high_hub_x = min(hub_xs), max(hub_xs)
            for candidate_y in range(max_y - 2, min_y + 1, -1):
                spine = _axis_points(
                    (low_hub_x, candidate_y),
                    (high_hub_x, candidate_y),
                )
                hubs = [(x, candidate_y) for x in hub_xs]
                if any(point in forbidden or point in reserved for point in spine):
                    continue
                escapes = [
                    (
                        hub[0],
                        hub[1]
                        + 2 * (-1 if terminal[1] < hub[1] else 1),
                    )
                    for hub, terminal in zip(hubs, terminals)
                ]
                escape_points = {
                    point
                    for hub, escape in zip(hubs, escapes)
                    for point in _axis_points(hub, escape)[1:]
                }
                if any(
                    point in forbidden or point in reserved
                    for point in escape_points
                ):
                    continue
                if any(
                    not (high_hub_x < other_low or low_hub_x > other_high)
                    for other_low, other_high, _owner in horizontal_intervals.get(
                        candidate_y, ()
                    )
                ):
                    continue
                fallback = candidate_y, hubs, escapes
                break
        if fallback is None:
            raise RuntimeError(f"no horizontal collector spine for {network}")
        spine_y, hubs, escapes = fallback
        result = [
            RoutedEdge(network, source, escapes[0], "feeder"),
            *(
                RoutedEdge(network, escape, sink, "tap")
                for escape, sink in zip(escapes[1:], sinks)
            ),
            *(
                RoutedEdge(network, hub, escape, "branch")
                for hub, escape in zip(hubs, escapes)
                if hub != escape
            ),
        ]
        ordered_hubs = sorted(hubs)
        result.extend(
            RoutedEdge(network, left, right, "spine")
            for left, right in zip(ordered_hubs, ordered_hubs[1:])
        )
        reserved.update(hubs)
        reserved.update(
            point
            for hub, escape in zip(hubs, escapes)
            for point in _axis_points(hub, escape)[1:]
        )
        for hub, escape in zip(hubs, escapes):
            track_intervals.setdefault(hub[0], []).append(
                (min(hub[1], escape[1]), max(hub[1], escape[1]), network)
            )
        horizontal_intervals.setdefault(spine_y, []).append(
            (ordered_hubs[0][0], ordered_hubs[-1][0], network)
        )
        return tuple(result)

    spine_y, records, staged_vertical, staged_horizontal, staged_hubs = chosen
    result: list[RoutedEdge] = []
    for pin, terminal, tap_hub, role in records:
        if role == "feeder":
            result.append(RoutedEdge(network, pin, tap_hub, role))
        else:
            result.append(RoutedEdge(network, tap_hub, pin, role))
        spine_hub = (tap_hub[0], spine_y)
        if tap_hub != spine_hub:
            result.append(RoutedEdge(network, tap_hub, spine_hub, "branch"))
    spine_hubs = sorted({(tap_hub[0], spine_y) for _p, _t, tap_hub, _r in records})
    result.extend(
        RoutedEdge(network, left, right, "spine")
        for left, right in zip(spine_hubs, spine_hubs[1:])
    )
    for x, values in staged_vertical.items():
        track_intervals.setdefault(x, []).extend(values)
    for y, values in staged_horizontal.items():
        horizontal_intervals.setdefault(y, []).extend(values)
    horizontal_intervals.setdefault(spine_y, []).append(
        (spine_hubs[0][0], spine_hubs[-1][0], network)
    )
    reserved.update(staged_hubs)
    return tuple(result)


def _axis_points(left: Point, right: Point) -> tuple[Point, ...]:
    if left[0] != right[0] and left[1] != right[1]:
        raise ValueError(f"non-orthogonal conductor: {left} -> {right}")
    dx = 0 if left[0] == right[0] else (1 if right[0] > left[0] else -1)
    dy = 0 if left[1] == right[1] else (1 if right[1] > left[1] else -1)
    distance = abs(right[0] - left[0]) + abs(right[1] - left[1])
    return tuple(
        (left[0] + dx * step, left[1] + dy * step)
        for step in range(distance + 1)
    )


def _growth_fanout_edges(
    network: str,
    source: Point,
    sinks: tuple[Point, ...],
    *,
    routing_source: Point,
    routing_sinks: tuple[Point, ...],
    forbidden: frozenset[Point],
    forbidden_edges: frozenset[tuple[Point, Point]],
    reserved: set[Point],
    track_intervals: dict[int, list[tuple[int, int, str]]],
    horizontal_intervals: dict[int, list[tuple[int, int, str]]],
) -> tuple[RoutedEdge, ...]:
    """Build a local horizontal stem with consumer-near branches.

    This structure is deliberately unavailable to multi-driver networks.  A
    resolved tristate owner needs one explicit collector; an ordinary fanout
    remains inside the producer cone and receives no global track.
    """

    if len(sinks) < 2:
        raise RuntimeError("growth fanout needs at least two sinks")
    if len(sinks) != len(routing_sinks):
        raise ValueError("physical and routing sink populations differ")
    direction_values = [sink[0] - routing_source[0] for sink in routing_sinks]
    if not all(value > 4 for value in direction_values):
        raise RuntimeError(f"non-forward local fanout {network}")

    branch_records: list[tuple[int, Point, Point, Point]] = []
    staged_intervals: dict[int, list[tuple[int, int, str]]] = defaultdict(list)
    staged_horizontal: dict[int, list[tuple[int, int, str]]] = defaultdict(list)
    staged_hubs: set[Point] = set()
    predicted_right = max(sink[0] - 2 for sink in routing_sinks)
    source_y = routing_source[1]
    spine_y: int | None = None
    for delta in (0, *range(1, 17), *range(-1, -17, -1)):
        candidate_y = source_y + delta
        origin = (routing_source[0], candidate_y)
        source_stem = _axis_points(routing_source, origin)
        if any(
            _edge(left, right) in forbidden_edges
            for left, right in zip(source_stem, source_stem[1:])
        ):
            continue
        if any(
            point in forbidden and point != routing_source
            for point in source_stem[1:]
        ):
            continue
        if set(source_stem[1:]) & reserved:
            continue
        stem_low, stem_high = sorted((source_y, candidate_y))
        if any(
            not (stem_high < other_low or stem_low > other_high)
            for other_low, other_high, _owner in track_intervals.get(
                routing_source[0], ()
            )
        ):
            continue
        preview = _axis_points(origin, (predicted_right, candidate_y))
        if any(
            _edge(left, right) in forbidden_edges
            for left, right in zip(preview, preview[1:])
        ):
            continue
        if any(
            point in forbidden and point != origin
            for point in preview
        ):
            continue
        if set(preview[1:]) & reserved:
            continue
        preview_low, preview_high = sorted((origin[0], preview[-1][0]))
        if any(
            not (preview_high < other_low or preview_low > other_high)
            for other_low, other_high, _owner in horizontal_intervals.get(
                candidate_y, ()
            )
        ):
            continue
        spine_y = candidate_y
        break
    if spine_y is None:
        raise RuntimeError(f"no local spine row for {network}")
    spine_origin = (routing_source[0], spine_y)
    if spine_origin != routing_source:
        staged_intervals[routing_source[0]].append(
            (min(source_y, spine_y), max(source_y, spine_y), network)
        )
        staged_hubs.add(spine_origin)
    ordered = sorted(
        zip(sinks, routing_sinks),
        key=lambda pair: (pair[1][0], pair[1][1], pair[0]),
    )
    for sink, terminal in ordered:
        chosen: tuple[int, Point, Point] | None = None
        first = terminal[0] - 2
        last = routing_source[0] + 2
        for branch_x in range(first, last - 1, -1):
            top = (branch_x, spine_y)
            bottom = (branch_x, terminal[1])
            low_y, high_y = sorted((top[1], bottom[1]))
            if any(
                not (high_y < other_low or low_y > other_high)
                for other_low, other_high, _owner in (
                    *track_intervals.get(branch_x, ()),
                    *staged_intervals.get(branch_x, ()),
                )
            ):
                continue
            vertical = _axis_points(top, bottom)
            if any(
                _edge(left, right) in forbidden_edges
                for left, right in zip(vertical, vertical[1:])
            ):
                continue
            if any(point in forbidden for point in vertical):
                continue
            if set(vertical) & reserved:
                continue
            tap = _axis_points(bottom, terminal)
            if any(
                _edge(left, right) in forbidden_edges
                for left, right in zip(tap, tap[1:])
            ):
                continue
            if any(
                point in forbidden and point != terminal
                for point in tap[1:]
            ):
                continue
            if set(tap[:-1]) & reserved:
                continue
            hubs = {top, bottom}
            if hubs & (reserved | staged_hubs):
                continue
            tap_low, tap_high = sorted((bottom[0], terminal[0]))
            if any(
                (
                    min(tap_high, other_high) > max(tap_low, other_low)
                    if owner == network
                    else min(tap_high, other_high) >= max(tap_low, other_low)
                )
                for other_low, other_high, owner in (
                    *horizontal_intervals.get(bottom[1], ()),
                    *staged_horizontal.get(bottom[1], ()),
                )
            ):
                continue
            chosen = (branch_x, top, bottom)
            break
        if chosen is None:
            raise RuntimeError(f"no local branch station for {network} -> {sink}")
        branch_x, top, bottom = chosen
        staged_intervals[branch_x].append(
            (min(top[1], bottom[1]), max(top[1], bottom[1]), network)
        )
        staged_hubs.update((top, bottom))
        staged_horizontal[bottom[1]].append(
            (min(bottom[0], terminal[0]), max(bottom[0], terminal[0]), network)
        )
        branch_records.append((branch_x, sink, top, bottom))

    spine_points = sorted(
        {spine_origin, *(top for _x, _sink, top, _bottom in branch_records)},
        key=lambda point: point[0],
    )
    if spine_points[0] != spine_origin:
        raise RuntimeError(f"local spine for {network} backtracks before its source")
    for left, right in zip(spine_points, spine_points[1:]):
        spine = _axis_points(left, right)
        if any(
            _edge(first, second) in forbidden_edges
            for first, second in zip(spine, spine[1:])
        ):
            raise RuntimeError(f"local spine for {network} overlaps pin access")
        if any(
            point in forbidden and point != spine_origin
            for point in spine
        ):
            raise RuntimeError(f"local spine for {network} crosses a component")
        if set(spine[1:]) & reserved:
            raise RuntimeError(f"local spine for {network} crosses a reserved tap")
        spine_low, spine_high = sorted((left[0], right[0]))
        if any(
            (
                min(spine_high, other_high) > max(spine_low, other_low)
                if owner == network
                else min(spine_high, other_high) >= max(spine_low, other_low)
            )
            for other_low, other_high, owner in (
                *horizontal_intervals.get(left[1], ()),
                *staged_horizontal.get(left[1], ()),
            )
        ):
            raise RuntimeError(f"local spine for {network} overlaps another net")
        staged_horizontal[left[1]].append((spine_low, spine_high, network))

    reserved.update(staged_hubs)
    for x, values in staged_intervals.items():
        track_intervals.setdefault(x, []).extend(values)
    for y, values in staged_horizontal.items():
        horizontal_intervals.setdefault(y, []).extend(values)
    result = [RoutedEdge(network, source, routing_source, "feeder")]
    if spine_origin != routing_source:
        result.append(RoutedEdge(network, routing_source, spine_origin, "stem"))
    result.extend(
        RoutedEdge(network, left, right, "spine")
        for left, right in zip(spine_points, spine_points[1:])
    )
    for _branch_x, sink, top, bottom in branch_records:
        if top != bottom:
            result.append(RoutedEdge(network, top, bottom, "branch"))
        result.append(RoutedEdge(network, bottom, sink, "tap"))
    return tuple(result)


def _attempt(
    design: PhysicalDesign,
    margin: int,
    order_strategy: str,
) -> RoutingResult:
    components_by_key = design.component_by_key()
    physical_net_by_name = {net.name: net for net in design.nets}
    model_components = {
        key: _component(component) for key, component in components_by_key.items()
    }
    body: set[Point] = set()
    pins: dict[PinRef, Point] = {}
    pin_access: dict[Point, Point] = {}
    pin_access_paths: dict[Point, tuple[Point, ...]] = {}
    all_pin_points: set[Point] = set()
    for key, component in model_components.items():
        left, right, top, bottom = component_bounds(component)
        body.update(
            (x, y)
            for x in range(left, right + 1)
            for y in range(top, bottom + 1)
        )
        component_pins = positioned_pins(component)
        for pin in component_pins:
            ref = PinRef(key, pin.name)
            pins[ref] = pin.position
            all_pin_points.add(pin.position)
            access_path = _pin_access_path(
                component,
                pin.position,
                # Parallel adapter outputs already leave on distinct rows or
                # columns.  Equal two-cell leads create the flat bus baseline;
                # staggering them produced a false staircase before every
                # splitter trunk.
                length=1 if pin.direction == INPUT else 2,
            )
            access = access_path[-1]
            previous = pin_access.setdefault(pin.position, access)
            if previous != access:
                raise ValueError(f"ambiguous pin access direction at {pin.position}")
            previous_path = pin_access_paths.setdefault(pin.position, access_path)
            if previous_path != access_path:
                raise ValueError(f"ambiguous pin access path at {pin.position}")
    all_access_points = {
        point for path in pin_access_paths.values() for point in path
    }
    terminal_access_edges = frozenset(
        _edge(left, right)
        for pin, path in pin_access_paths.items()
        for left, right in zip((pin, *path), path)
    )
    terminal_turn_by_pin: dict[Point, Point] = {}
    for pin, path in pin_access_paths.items():
        terminal = path[-1]
        previous = pin if len(path) == 1 else path[-2]
        direction = (terminal[0] - previous[0], terminal[1] - previous[1])
        terminal_turn_by_pin[pin] = (
            terminal[0] + direction[0],
            terminal[1] + direction[1],
        )
    all_points = body | all_pin_points | all_access_points
    bounds = (
        min(point[0] for point in all_points) - margin,
        min(point[1] for point in all_points) - margin,
        max(point[0] for point in all_points) + margin,
        max(point[1] for point in all_points) + margin,
    )
    net_specs = []
    structured_networks: set[str] = set()
    input_trunk_networks: set[str] = set()
    output_lane_networks: set[str] = set()
    terminal_turn_owners: dict[Point, set[str]] = defaultdict(set)
    for net in design.nets:
        source = pins[net.source]
        sinks = tuple(
            pins[sink] for sink in (*net.additional_sources, *net.sinks)
        )
        span = max((_manhattan(source, sink) for sink in sinks), default=0)
        net_specs.append((-(len(sinks)), -span, net.name, source, sinks))
        source_roles = {
            components_by_key[source_ref.component].role
            for source_ref in net.sources
        }
        sink_roles = {
            components_by_key[sink_ref.component].role
            for sink_ref in net.sinks
        }
        input_derived = source_roles == {"splitter"} or (
            source_roles == {"input_port"} and sink_roles != {"splitter"}
        )
        output_derived = "maker" in sink_roles
        if input_derived:
            input_trunk_networks.add(net.name)
        if output_derived:
            output_lane_networks.add(net.name)
        if len(sinks) > 1 or input_derived or output_derived:
            structured_networks.add(net.name)
        for terminal in (source, *sinks):
            terminal_turn_owners[terminal_turn_by_pin[terminal]].add(net.name)
    net_specs.sort()
    edge_owner: dict[tuple[Point, Point], str] = {}
    point_owner: dict[Point, set[str]] = {}
    reserved_hubs: set[Point] = set()
    track_intervals: dict[int, list[tuple[int, int, str]]] = {}
    horizontal_intervals: dict[int, list[tuple[int, int, str]]] = {}
    routed_edges: list[RoutedEdge] = []
    wires: list[Wire] = []
    route_points: list[tuple[Point, ...]] = []
    # The turn-clearance cells are reserved only against electrical junctions.
    # Ordinary wire geometry may still pass through them.
    forbidden_hubs = frozenset(body | all_pin_points | all_access_points)
    fixed_track_assignments: dict[str, int] = {}
    fixed_track_intervals: dict[int, list[tuple[int, int, str]]] = defaultdict(list)
    fixed_protected_owners: dict[Point, set[str]] = defaultdict(set)
    net_spec_by_name = {
        network: (source, sinks)
        for _fanout, _span, network, source, sinks in net_specs
    }
    for network in sorted(input_trunk_networks | output_lane_networks):
        source, sinks = net_spec_by_name[network]
        routing_source = pin_access.get(source, source)
        routing_sinks = tuple(pin_access.get(sink, sink) for sink in sinks)
        if network in input_trunk_networks:
            track_x = routing_source[0]
        else:
            maker_sinks = [
                pin_access[pins[sink_ref]]
                for net in design.nets
                if net.name == network
                for sink_ref in net.sinks
                if components_by_key[sink_ref.component].role == "maker"
            ]
            if not maker_sinks:
                raise RuntimeError(f"output lane {network!r} has no maker sink")
            track_x = maker_sinks[0][0]
        fixed_track_assignments[network] = track_x
        request = _FanoutTrackRequest(
            network=network,
            source=routing_source,
            sinks=routing_sinks,
            candidates=(track_x,),
            low_y=min((routing_source[1], *(sink[1] for sink in routing_sinks))),
            high_y=max((routing_source[1], *(sink[1] for sink in routing_sinks))),
        )
        fixed_track_intervals[track_x].append(
            (request.low_y, request.high_y, network)
        )
        for point in _fanout_protected_points(request, track_x):
            fixed_protected_owners[point].add(network)

    protected_owners = {
        point: frozenset(owners)
        for point, owners in terminal_turn_owners.items()
    }
    for point, owners in fixed_protected_owners.items():
        protected_owners[point] = frozenset(
            set(protected_owners.get(point, frozenset())) | owners
        )
    fanout_track_assignments = dict(fixed_track_assignments)
    reserved_hubs.update(fixed_protected_owners)
    # Publish every possible collector tap before approving local growth.
    # Ordinary fanout normally becomes a short cone spine, but it may still
    # need its assigned collector as a legality fallback.  Reserving only the
    # prospective junction cells prevents an earlier spine from sealing that
    # fallback without forbidding crossings through straight wire interiors.
    future_track_hubs: dict[str, frozenset[Point]] = {}
    for network, track_x in fanout_track_assignments.items():
        source, sinks = net_spec_by_name[network]
        routing_source = pin_access.get(source, source)
        routing_sinks = tuple(pin_access.get(sink, sink) for sink in sinks)
        future_track_hubs[network] = frozenset(
            (track_x, terminal[1])
            for terminal in (routing_source, *routing_sinks)
        )
        reserved_hubs.update(future_track_hubs[network])
    track_intervals.update(
        {x: list(values) for x, values in fixed_track_intervals.items()}
    )
    planned_nets: list[tuple[str, tuple[RoutedEdge, ...]]] = []
    planning_specs = sorted(
        net_specs,
        key=lambda spec: (
            0 if spec[2] in fixed_track_assignments else
            1 if physical_net_by_name[spec[2]].additional_sources else
            2 if spec[2] in structured_networks else 3,
            *spec,
        ),
    )
    for _fanout, _span, network, source, sinks in planning_specs:
        # The network now owns its reservation.  Its actual growth spine or
        # collector immediately republishes the junctions it really uses.
        reserved_hubs.difference_update(future_track_hubs.get(network, ()))
        net = physical_net_by_name[network]
        routing_source = pin_access.get(source, source)
        routing_sinks = tuple(pin_access.get(sink, sink) for sink in sinks)
        use_collector_spine = bool(
            net.additional_sources and network not in fixed_track_assignments
        )
        use_growth_spine = (
            network in structured_networks
            and network not in fixed_track_assignments
            and not net.additional_sources
        )
        if use_collector_spine:
            try:
                tree_edges = _fanout_edges(
                    network,
                    source,
                    sinks,
                    routing_source=routing_source,
                    routing_sinks=routing_sinks,
                    forbidden=forbidden_hubs,
                    reserved=reserved_hubs,
                    track_intervals=track_intervals,
                    bounds=bounds,
                )
            except RuntimeError:
                tree_edges = _collector_edges(
                    network,
                    source,
                    sinks,
                    routing_source=routing_source,
                    routing_sinks=routing_sinks,
                    forbidden=forbidden_hubs,
                    reserved=reserved_hubs,
                    track_intervals=track_intervals,
                    horizontal_intervals=horizontal_intervals,
                    bounds=bounds,
                )
        elif use_growth_spine:
            try:
                tree_edges = _growth_fanout_edges(
                    network,
                    source,
                    sinks,
                    routing_source=routing_source,
                    routing_sinks=routing_sinks,
                    forbidden=forbidden_hubs,
                    forbidden_edges=terminal_access_edges,
                    reserved=reserved_hubs,
                    track_intervals=track_intervals,
                    horizontal_intervals=horizontal_intervals,
                )
            except RuntimeError as growth_error:
                try:
                    tree_edges = _fanout_edges(
                        network,
                        source,
                        sinks,
                        routing_source=routing_source,
                        routing_sinks=routing_sinks,
                        forbidden=forbidden_hubs,
                        reserved=reserved_hubs,
                        track_intervals=track_intervals,
                        bounds=bounds,
                    )
                except RuntimeError as vertical_error:
                    try:
                        tree_edges = _collector_edges(
                            network,
                            source,
                            sinks,
                            routing_source=routing_source,
                            routing_sinks=routing_sinks,
                            forbidden=forbidden_hubs,
                            reserved=reserved_hubs,
                            track_intervals=track_intervals,
                            horizontal_intervals=horizontal_intervals,
                            bounds=bounds,
                        )
                    except RuntimeError as legacy_error:
                        raise RuntimeError(
                            f"growth routing failed for {network}: {growth_error}; "
                            f"vertical fallback failed: {vertical_error}; "
                            f"horizontal fallback failed: {legacy_error}"
                        ) from legacy_error
        else:
            tree_edges = _fanout_edges(
                network,
                source,
                sinks,
                routing_source=routing_source,
                routing_sinks=routing_sinks,
                forbidden=forbidden_hubs,
                reserved=reserved_hubs,
                track_intervals=track_intervals,
                bounds=bounds,
                channel_x=fanout_track_assignments.get(network),
            )
        planned_nets.append((network, tree_edges))

    structured_leads: dict[RoutedEdge, tuple[Point, ...]] = {}
    structured_lead_points: set[Point] = set()
    protected_point_owner: dict[Point, str] = {}
    for _network, tree_edges in planned_nets:
        for tree_edge in tree_edges:
            if tree_edge.role == "feeder":
                terminal = pin_access[tree_edge.source]
                hub = tree_edge.sink
            elif tree_edge.role == "tap":
                terminal = pin_access[tree_edge.sink]
                hub = tree_edge.source
            else:
                if tree_edge.role in {"trunk", "stem", "spine", "branch"}:
                    for hub_point in (tree_edge.source, tree_edge.sink):
                        previous = protected_point_owner.setdefault(
                            hub_point, tree_edge.network
                        )
                        if previous != tree_edge.network:
                            raise RuntimeError(
                                f"fanout hub {hub_point} belongs to both "
                                f"{previous!r} and {tree_edge.network!r}"
                            )
                continue
            previous = protected_point_owner.setdefault(hub, tree_edge.network)
            if previous != tree_edge.network:
                raise RuntimeError(
                    f"fanout hub {hub} belongs to both {previous!r} and "
                    f"{tree_edge.network!r}"
                )
            # Only the electrical junction is protected.  The conductor after
            # it is an ordinary wire and may be crossed orthogonally; forcing a
            # two-cell private lead here creates the comb-like cages seen in
            # legacy layouts.
            lead: tuple[Point, ...] = ()
            structured_leads[tree_edge] = lead

    # Tap points are electrical endpoints and may not be crossed by foreign
    # wires. Their first horizontal port is protected for the same reason.
    routing_pins = frozenset(
        all_pin_points | all_access_points | reserved_hubs | structured_lead_points
    )
    for network, tree_edges in planned_nets:
        for tree_edge in tree_edges:
            for endpoint in (tree_edge.source, tree_edge.sink):
                access = pin_access.get(endpoint)
                if access is None:
                    continue
                access_points = (endpoint,) + pin_access_paths[endpoint]
                for left, right in zip(access_points, access_points[1:]):
                    access_edge = _edge(left, right)
                    previous_owner = edge_owner.setdefault(access_edge, network)
                    if previous_owner != network:
                        raise RuntimeError(
                            f"pin escape edge collision: {access_edge} belongs to "
                            f"both {previous_owner!r} and {network!r}"
                    )
    for tree_edge, lead in structured_leads.items():
        hub = tree_edge.sink if tree_edge.role == "feeder" else tree_edge.source
        for left, right in zip((hub, *lead), lead):
            lead_edge = _edge(left, right)
            previous_owner = edge_owner.setdefault(
                lead_edge,
                tree_edge.network,
            )
            if previous_owner != tree_edge.network:
                raise RuntimeError(
                    f"structured fanout lead edge collision: {lead_edge} belongs "
                    f"to both {previous_owner!r} and {tree_edge.network!r}"
                )
    backbone_edges = [
        edge
        for _network, tree_edges in planned_nets
        for edge in tree_edges
        if edge.role in {"trunk", "stem", "spine", "branch"}
    ]
    for tree_edge in backbone_edges:
        points = _axis_points(tree_edge.source, tree_edge.sink)
        for left, right in zip(points, points[1:]):
            used_edge = _edge(left, right)
            previous_owner = edge_owner.setdefault(used_edge, tree_edge.network)
            if previous_owner != tree_edge.network:
                raise RuntimeError(
                    f"planned {tree_edge.role} edge collision: {used_edge} belongs "
                    f"to both {previous_owner!r} and {tree_edge.network!r}; "
                    f"horizontal_intervals={horizontal_intervals.get(left[1], ())!r}"
                )
        for point in points:
            point_owner.setdefault(point, set()).add(tree_edge.network)
        routed_edges.append(tree_edge)
        route_points.append(points)
        wires.append(
            wire_from_vertices(
                _vertices(points),
                color=9 if tree_edge.network in input_trunk_networks else 10,
                comment="",
            )
        )
    pending_edges = [
        tree_edge
        for _network, tree_edges in planned_nets
        for tree_edge in tree_edges
        if tree_edge.role not in {"trunk", "stem", "spine", "branch"}
    ]
    monotonic_fallback_count = 0

    def search_terminals(tree_edge: RoutedEdge) -> tuple[Point, Point]:
        search_source = pin_access.get(tree_edge.source, tree_edge.source)
        search_sink = pin_access.get(tree_edge.sink, tree_edge.sink)
        if tree_edge.role == "feeder":
            lead = structured_leads[tree_edge]
            search_sink = lead[-1] if lead else tree_edge.sink
        elif tree_edge.role == "tap":
            lead = structured_leads[tree_edge]
            search_source = lead[-1] if lead else tree_edge.source
        return search_source, search_sink

    def route_priority(tree_edge: RoutedEdge) -> tuple[object, ...]:
        search_source, search_sink = search_terminals(tree_edge)
        straight = (
            search_source[0] == search_sink[0]
            or search_source[1] == search_sink[1]
        )
        local_role = {"direct": 0, "tap": 1, "feeder": 2}[tree_edge.role]
        structured_role = {"feeder": 0, "tap": 1, "direct": 2}[tree_edge.role]
        distance = abs(search_source[0] - search_sink[0]) + abs(
            search_source[1] - search_sink[1]
        )
        stable = (tree_edge.network, search_source, search_sink)
        if order_strategy == "local-first":
            return (local_role, 0 if straight else 1, distance, *stable)
        if order_strategy == "structured-first":
            return (structured_role, 0 if straight else 1, distance, *stable)
        if order_strategy == "shortest-first":
            return (0 if straight else 1, distance, local_role, *stable)
        if order_strategy == "longest-first":
            return (-distance, 0 if straight else 1, local_role, *stable)
        raise ValueError(f"unknown routing order strategy {order_strategy!r}")

    for tree_edge in sorted(pending_edges, key=route_priority):
            network = tree_edge.network
            search_source, search_sink = search_terminals(tree_edge)
            if search_source == search_sink:
                points = (search_source,)
            else:
                try:
                    points = _search(
                        network,
                        search_source,
                        search_sink,
                        body=frozenset(body),
                        pins=routing_pins,
                        edge_owner=edge_owner,
                        point_owner=point_owner,
                        bounds=bounds,
                        strict_monotonic=True,
                    )
                except RuntimeError:
                    monotonic_fallback_count += 1
                    points = _search(
                        network,
                        search_source,
                        search_sink,
                        body=frozenset(body),
                        pins=routing_pins,
                        edge_owner=edge_owner,
                        point_owner=point_owner,
                        bounds=bounds,
                    )
            if (
                search_source != tree_edge.source
                and tree_edge.source in pin_access_paths
            ):
                source_path = (tree_edge.source,) + pin_access_paths[tree_edge.source]
                points = source_path[:-1] + points
            if search_sink != tree_edge.sink:
                if tree_edge.sink in pin_access_paths:
                    sink_path = (tree_edge.sink,) + pin_access_paths[tree_edge.sink]
                    points = points + tuple(reversed(sink_path))[1:]
            if tree_edge.role == "feeder":
                hub_to_terminal = (tree_edge.sink, *structured_leads[tree_edge])
                points = points + tuple(reversed(hub_to_terminal))[1:]
            elif tree_edge.role == "tap":
                hub_to_terminal = (tree_edge.source, *structured_leads[tree_edge])
                points = hub_to_terminal[:-1] + points
            for left, right in zip(points, points[1:]):
                edge_owner[_edge(left, right)] = network
            for point in points:
                point_owner.setdefault(point, set()).add(network)
            routed_edges.append(tree_edge)
            route_points.append(points)
            wires.append(
                wire_from_vertices(
                    _vertices(points),
                    color=(
                        9
                        if network in input_trunk_networks
                        and tree_edge.role == "trunk"
                        else 10
                    ),
                    comment="",
                )
            )
    foreign_tap_contacts = {
        point: sorted(owners - {owner})
        for point, owner in protected_point_owner.items()
        if (owners := point_owner.get(point, set())) - {owner}
    }
    if foreign_tap_contacts:
        raise RuntimeError(
            "foreign networks cross protected fanout taps/hubs: "
            f"{list(foreign_tap_contacts.items())[:4]!r}"
        )
    crossing_points = {
        point: owners for point, owners in point_owner.items() if len(owners) > 1
    }
    diagonal_crossings = 0
    for edge_value in edge_owner:
        opposite = _opposite_diagonal(*edge_value)
        if opposite is not None and opposite in edge_owner and edge_value < opposite:
            diagonal_crossings += 1
    lengths = [len(points) - 1 for points in route_points]
    bend_count = sum(max(0, len(_vertices(points)) - 2) for points in route_points)
    backtrack_segments = 0
    for points in route_points:
        start, goal = points[0], points[-1]
        backtrack_segments += sum(
            _manhattan(right, goal) > _manhattan(left, goal)
            for left, right in zip(points, points[1:])
        )
    report = {
        "schema": "turingsynth-routing-v1",
        "order_strategy": order_strategy,
        "wire_count": len(wires),
        "logical_net_count": len(design.nets),
        "fanout_hub_count": len(
            {
                point
                for _network, tree_edges in planned_nets
                for edge in tree_edges
                if edge.role in {"feeder", "tap", "trunk"}
                for point in (
                    (edge.sink,) if edge.role == "feeder" else
                    (edge.source,) if edge.role == "tap" else
                    (edge.source, edge.sink)
                )
            }
        ),
        "fanout_track_assignments": dict(sorted(fanout_track_assignments.items())),
        "total_wire_length": sum(lengths),
        "maximum_wire_length": max(lengths, default=0),
        "average_wire_length": sum(lengths) / max(1, len(lengths)),
        "bend_count": bend_count,
        "backtrack_segment_count": backtrack_segments,
        "monotonic_fallback_count": monotonic_fallback_count,
        "foreign_point_crossing_count": len(crossing_points),
        "foreign_tap_crossing_count": 0,
        "diagonal_crossing_count": diagonal_crossings,
        "overlapping_edge_count": 0,
        "bounds": list(bounds),
    }
    return RoutingResult(tuple(wires), tuple(routed_edges), report)


def route(design: PhysicalDesign) -> RoutingResult:
    """Route all nets using bounded deterministic rip-up/reroute strategies."""

    errors = []
    for margin in (16, 28, 44, 68):
        successes = []
        for strategy in (
            "shortest-first",
            "local-first",
            "structured-first",
            "longest-first",
        ):
            try:
                successes.append(_attempt(design, margin, strategy))
            except FanoutTrackCapacityError:
                raise
            except RuntimeError as exc:
                errors.append(f"margin={margin}, strategy={strategy}: {exc}")
        if successes:
            return min(
                successes,
                key=lambda result: (
                    int(result.report["backtrack_segment_count"]),
                    int(result.report["monotonic_fallback_count"]),
                    int(result.report["maximum_wire_length"]),
                    int(result.report["total_wire_length"]),
                    int(result.report["bend_count"]),
                    int(result.report["foreign_point_crossing_count"]),
                    str(result.report["order_strategy"]),
                ),
            )
    raise RuntimeError("routing failed after bounded retries:\n" + "\n".join(errors))
