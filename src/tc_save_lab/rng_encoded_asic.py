"""Build the encoded-state 396/9/66 RNG architecture candidate.

The circuit uses one physical depth-two XOR network in two modes.  During the
seed-load tick each of 47 OR gates sees ``seed[i]`` and a zero-valued state bit;
afterwards the disabled architecture input contributes zero and the same OR
gates expose the encoded state bits.  This lets the steady-state B/C network
also compute the initialization transform T without a separate XOR network.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy, replace
from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha256
from heapq import heappop, heappush
import json
from pathlib import Path
import random
from typing import Callable, Sequence

from .analysis import wire_points
from .builder import stable_permanent_id, wire_from_vertices
from .codec import decode_v15, encode_v15
from .model import Circuit, Component, Point
from .pins import analyze_connectivity, positioned_pins, rotate_offset
from .simulate import initial_clocked_memory, simulate_clocked_tick, simulate_clocked_ticks
from .sprite_geometry import DEFAULT_COMPONENT_SPRITE_ROOT, audit_sprite_geometry


WORD_BITS = 32
WORD_MASK = (1 << WORD_BITS) - 1
IDENTITY = tuple(1 << bit for bit in range(WORD_BITS))

EXPECTED_GATE = 396
EXPECTED_DELAY = 9
EXPECTED_CYCLES = 66
PUBLIC_REFERENCE = (431, 9, 66, 256_014)


def xorshift32(value: int) -> int:
    """Return the exact U32 transition from ``campaign/rng/test.si``."""

    if not 0 <= value <= WORD_MASK:
        raise ValueError(f"RNG state must fit U32, got {value}")
    value ^= value >> 13
    value &= WORD_MASK
    value ^= (value << 17) & WORD_MASK
    value &= WORD_MASK
    value ^= value >> 5
    return value & WORD_MASK


def matrix_from_function(function: Callable[[int], int]) -> tuple[int, ...]:
    return tuple(
        sum(
            ((function(1 << source) >> output) & 1) << source
            for source in range(WORD_BITS)
        )
        for output in range(WORD_BITS)
    )


def apply_row(row: int, matrix: Sequence[int]) -> int:
    result = 0
    remaining = row
    while remaining:
        low_bit = remaining & -remaining
        result ^= matrix[low_bit.bit_length() - 1]
        remaining ^= low_bit
    return result


def apply_matrix(matrix: Sequence[int], value: int) -> int:
    return sum(
        ((row & value).bit_count() & 1) << index
        for index, row in enumerate(matrix)
    )


def compose(left: Sequence[int], right: Sequence[int]) -> tuple[int, ...]:
    return tuple(apply_row(row, right) for row in left)


def invert(matrix: Sequence[int]) -> tuple[int, ...]:
    rows = [matrix[index] | ((1 << index) << WORD_BITS) for index in range(WORD_BITS)]
    for column in range(WORD_BITS):
        pivot = next(
            (index for index in range(column, WORD_BITS) if (rows[index] >> column) & 1),
            None,
        )
        if pivot is None:
            raise ValueError("matrix is singular")
        rows[column], rows[pivot] = rows[pivot], rows[column]
        for index in range(WORD_BITS):
            if index != column and ((rows[index] >> column) & 1):
                rows[index] ^= rows[column]
    return tuple((row >> WORD_BITS) & WORD_MASK for row in rows)


def right_shear(distance: int) -> tuple[int, ...]:
    return matrix_from_function(lambda value: (value ^ (value >> distance)) & WORD_MASK)


A = matrix_from_function(xorshift32)
T = compose(right_shear(17), right_shear(13))
T_INVERSE = invert(T)
C = compose(A, T_INVERSE)
B = compose(T, C)


BC_EXTRA_PAIRS = frozenset(
    int(value, 16)
    for value in (
        "00420000",
        "00840000",
        "01080000",
        "02100000",
        "04200000",
        "08008000",
        "08400000",
        "10010000",
        "10800000",
        "20000001",
        "21000000",
        "40000002",
        "42000000",
        "80000004",
        "84000000",
    )
)


FIRST_SEED_LABELS = {
    int(steady, 16): int(seed, 16)
    for steady, seed in (
        ("00000021", "00020000"),
        ("00000042", "00040000"),
        ("00000084", "00080000"),
        ("00000108", "00100000"),
        ("00000210", "00200000"),
        ("00000420", "00400000"),
        ("00000840", "00800000"),
        ("00001080", "01000000"),
        ("00002100", "02000000"),
        ("00004200", "04000000"),
        ("00008008", "00008000"),
        ("00010010", "00010000"),
        ("00420000", "00020001"),
        ("00840000", "00040002"),
        ("01080000", "00080004"),
        ("02100000", "00100008"),
        ("04200000", "00200010"),
        ("08008000", "08000400"),
        ("08400000", "00400020"),
        ("10010000", "10000800"),
        ("10800000", "00800040"),
        ("20000001", "20001000"),
        ("21000000", "01000080"),
        ("40000002", "40002000"),
        ("42000000", "02000100"),
        ("80000004", "80004000"),
        ("84000000", "04000200"),
    )
}


MODE_PAIRS = frozenset(
    {
        (0, 22),
        (1, 23),
        (2, 24),
        (3, 25),
        (4, 26),
        (5, 27),
        (6, 28),
        (7, 29),
        (8, 30),
        (9, 31),
        (10, 27),
        (11, 28),
        (12, 29),
        (13, 30),
        (14, 31),
        (15, 15),
        (16, 16),
        (17, 0),
        (17, 17),
        (18, 1),
        (18, 18),
        (19, 2),
        (19, 19),
        (20, 3),
        (20, 20),
        (21, 4),
        (21, 21),
        (22, 10),
        (22, 22),
        (23, 6),
        (23, 23),
        (24, 12),
        (24, 24),
        (25, 13),
        (25, 25),
        (26, 14),
        (26, 26),
        (27, 10),
        (27, 15),
        (28, 11),
        (28, 16),
        (29, 0),
        (29, 12),
        (30, 1),
        (30, 13),
        (31, 2),
        (31, 14),
    }
)


@dataclass(frozen=True)
class XorGate:
    output: int
    left: int
    right: int
    depth: int


def bits(value: int) -> tuple[int, ...]:
    return tuple(index for index in range(WORD_BITS) if (value >> index) & 1)


def _pair_partitions(row: int) -> tuple[tuple[int, int], ...]:
    support = bits(row)
    if len(support) == 3:
        return tuple((1 << lone, row ^ (1 << lone)) for lone in support)
    if len(support) == 4:
        a, b, c, d = support
        return (
            ((1 << a) ^ (1 << b), (1 << c) ^ (1 << d)),
            ((1 << a) ^ (1 << c), (1 << b) ^ (1 << d)),
            ((1 << a) ^ (1 << d), (1 << b) ^ (1 << c)),
        )
    raise ValueError(f"row {row:08x} cannot be partitioned at depth two")


def _build_steady_network() -> tuple[XorGate, ...]:
    targets = frozenset(B + C)
    direct = frozenset(IDENTITY)
    pair_outputs = frozenset(
        row for row in targets - direct if row.bit_count() == 2
    )
    first_layer = pair_outputs | BC_EXTRA_PAIRS
    if first_layer != frozenset(FIRST_SEED_LABELS):
        raise AssertionError("first-layer certificate changed")

    gates: list[XorGate] = []
    for pair in sorted(first_layer):
        left, right = bits(pair)
        gates.append(XorGate(pair, 1 << left, 1 << right, 1))

    available = direct | first_layer
    for target in sorted(targets - direct - pair_outputs):
        partition = next(
            (
                candidate
                for candidate in _pair_partitions(target)
                if candidate[0] in available and candidate[1] in available
            ),
            None,
        )
        if partition is None:
            raise AssertionError(f"no certified depth-two partition for {target:08x}")
        gates.append(XorGate(target, partition[0], partition[1], 2))
    if len(gates) != 61 or sum(gate.depth == 1 for gate in gates) != 27:
        raise AssertionError("61-XOR certificate metrics changed")
    return tuple(gates)


GATES = _build_steady_network()
GATE_BY_OUTPUT = {gate.output: gate for gate in GATES}
FIRST_LAYER = frozenset(gate.output for gate in GATES if gate.depth == 1)
DIRECT = frozenset(IDENTITY)


def _choose_first_leaf_seeds(
    steady_pair: int, seed_form: int
) -> tuple[int | None, int | None]:
    state_left, state_right = bits(steady_pair)
    candidates = (None, *range(WORD_BITS))
    for seed_left in candidates:
        for seed_right in candidates:
            form = (0 if seed_left is None else 1 << seed_left) ^ (
                0 if seed_right is None else 1 << seed_right
            )
            if form != seed_form:
                continue
            used = {
                pair
                for pair in ((seed_left, state_left), (seed_right, state_right))
                if pair[0] is not None
            }
            if used <= MODE_PAIRS:
                return seed_left, seed_right
    raise AssertionError(f"no mode-pair realization for {steady_pair:08x}")


FIRST_LEAF_SEEDS = {
    node: _choose_first_leaf_seeds(node, seed_form)
    for node, seed_form in FIRST_SEED_LABELS.items()
}


def _seed_form_of_fanin(node: int, consumer: int, side: int) -> int:
    if node in FIRST_LAYER:
        return FIRST_SEED_LABELS[node]
    if node not in DIRECT:
        raise AssertionError(f"unsupported fanin {node:08x}")
    if consumer not in B:
        return 0
    output_index = B.index(consumer)
    target = T[output_index]
    gate = GATE_BY_OUTPUT[consumer]
    other = gate.right if side == 0 else gate.left
    other_seed = FIRST_SEED_LABELS[other] if other in FIRST_LAYER else 0
    residual = target ^ other_seed
    if residual.bit_count() > 1:
        raise AssertionError(f"B[{output_index}] raw residual is not one bit")
    return residual


def _verify_certificate() -> dict[int, int]:
    if compose(C, T) != A or compose(T, C) != B:
        raise AssertionError("encoded-state matrix identities failed")
    if compose(T, T_INVERSE) != IDENTITY:
        raise AssertionError("T inverse certificate failed")

    seed_labels: dict[int, int] = {}
    used_pairs: set[tuple[int, int]] = set()
    for gate in GATES:
        if gate.depth == 1:
            state_support = bits(gate.output)
            seed_support = FIRST_LEAF_SEEDS[gate.output]
            for seed_bit, state_bit in zip(seed_support, state_support):
                if seed_bit is not None:
                    used_pairs.add((seed_bit, state_bit))
            left_seed = 0 if seed_support[0] is None else 1 << seed_support[0]
            right_seed = 0 if seed_support[1] is None else 1 << seed_support[1]
        else:
            left_seed = (
                seed_labels[gate.left]
                if gate.left in seed_labels
                else _seed_form_of_fanin(gate.left, gate.output, 0)
            )
            right_seed = (
                seed_labels[gate.right]
                if gate.right in seed_labels
                else _seed_form_of_fanin(gate.right, gate.output, 1)
            )
            for node, seed_form in ((gate.left, left_seed), (gate.right, right_seed)):
                if node in DIRECT and seed_form:
                    used_pairs.add((bits(seed_form)[0], bits(node)[0]))
        if gate.left ^ gate.right != gate.output:
            raise AssertionError(f"steady XOR semantics changed for {gate.output:08x}")
        seed_labels[gate.output] = left_seed ^ right_seed

    for index, (seed_target, steady_target) in enumerate(zip(T, B)):
        if steady_target in seed_labels:
            actual = seed_labels[steady_target]
        else:
            pair = (bits(seed_target)[0], bits(steady_target)[0])
            used_pairs.add(pair)
            actual = seed_target
        if actual != seed_target:
            raise AssertionError(
                f"B[{index}] tick-zero label {actual:08x} != {seed_target:08x}"
            )
    if frozenset(used_pairs) != MODE_PAIRS:
        raise AssertionError("47-OR mode-pair certificate changed")
    return seed_labels


SEED_LABELS = _verify_certificate()


def _pin(component: Component, name: str) -> Point:
    matches = [pin.position for pin in positioned_pins(component) if pin.name == name]
    if len(matches) != 1:
        raise RuntimeError(f"component kind {component.kind} has no unique pin {name!r}")
    return matches[0]


# Conservative current-v15 sprite bounds.  Routing blocks every cell in each
# rectangle; the verifier then checks the result against exact installed PNG
# alpha.  All generated components use rotation zero, but rotation is handled
# so this helper fails safely if that changes later.
_FOOTPRINT_BOXES = {
    2: (-1, -1, 1, 1),
    3: (-1, -1, 2, 1),
    7: (-1, -2, 2, 2),
    10: (-1, -2, 2, 2),
    13: (-3, -2, 3, 2),
    16: (-1, -4, 1, 5),
    17: (-1, -4, 1, 5),
    62: (-5, -4, 4, 4),
    70: (-4, -5, 4, 3),
    97: (-1, -2, 1, 3),
    99: (-1, -2, 1, 3),
}


def _component_footprint(component: Component) -> frozenset[Point]:
    try:
        min_x, min_y, max_x, max_y = _FOOTPRINT_BOXES[component.kind]
    except KeyError as exc:
        raise RuntimeError(
            f"RNG encoded ASIC has no footprint for component kind {component.kind}"
        ) from exc
    cells: set[Point] = set()
    for x in range(min_x, max_x + 1):
        for y in range(min_y, max_y + 1):
            dx, dy = rotate_offset((x, y), component.rotation)
            cells.add((component.position[0] + dx, component.position[1] + dy))
    return frozenset(cells)


def _component_footprints(
    components: tuple[Component, ...],
) -> tuple[frozenset[Point], ...]:
    return tuple(_component_footprint(component) for component in components)


def _pin_access_cells(
    component: Component,
    pin_position: Point,
    pin_direction: str,
    footprint: frozenset[Point],
) -> frozenset[Point]:
    """Return the outward corridor through a component's own pin."""

    if component.kind == 62:
        step = rotate_offset((1, 0), component.rotation)
    elif component.kind == 70:
        step = rotate_offset((-1, 0), component.rotation)
    elif pin_direction in {"output", "output_tristate"}:
        step = rotate_offset((1, 0), component.rotation)
    else:
        step = rotate_offset((-1, 0), component.rotation)

    cells: set[Point] = set()
    point = pin_position
    for _ in range(16):
        cells.add(point)
        if point not in footprint:
            break
        point = (point[0] + step[0], point[1] + step[1])
    else:  # pragma: no cover - current sprites are at most ten cells wide
        raise RuntimeError(f"unbounded pin corridor for component kind {component.kind}")
    return frozenset(cells)


def _pin_access_map(
    components: tuple[Component, ...],
    footprints: tuple[frozenset[Point], ...],
) -> dict[Point, frozenset[Point]]:
    result: dict[Point, frozenset[Point]] = {}
    for index, (component, footprint) in enumerate(zip(components, footprints)):
        for pin in positioned_pins(component, index):
            cells = _pin_access_cells(
                component,
                pin.position,
                pin.direction,
                footprint,
            )
            previous = result.get(pin.position)
            if previous is not None and previous != cells:
                raise RuntimeError(f"ambiguous pin access at {pin.position}")
            result[pin.position] = cells
    return result


def _compress_route(points: list[Point]) -> tuple[Point, ...]:
    if len(points) < 2:
        raise RuntimeError("route has fewer than two points")
    vertices = [points[0]]
    previous_step: Point | None = None
    for start, end in zip(points, points[1:]):
        step = (end[0] - start[0], end[1] - start[1])
        if previous_step is not None and step != previous_step:
            vertices.append(start)
        previous_step = step
    vertices.append(points[-1])
    return tuple(vertices)


def _route_around_components(
    source: Point,
    sink: Point,
    blocked: frozenset[Point],
    access_cells: frozenset[Point],
) -> tuple[Point, ...]:
    """Find a short orthogonal route without crossing components or pins."""

    if source == sink:
        raise RuntimeError(f"cannot route a zero-length connection at {source}")
    allowed_component_cells = access_cells | {source, sink}
    all_points = (*blocked, source, sink)
    margin = 96
    min_x = min(point[0] for point in all_points) - margin
    max_x = max(point[0] for point in all_points) + margin
    min_y = min(point[1] for point in all_points) - margin
    max_y = max(point[1] for point in all_points) + margin
    directions: tuple[Point, ...] = ((1, 0), (0, -1), (0, 1), (-1, 0))
    start = (source, -1)
    queue: list[tuple[int, int, int, int, int]] = []
    heappush(
        queue,
        (
            abs(sink[0] - source[0]) + abs(sink[1] - source[1]),
            0,
            source[0],
            source[1],
            -1,
        ),
    )
    costs = {start: 0}
    previous: dict[tuple[Point, int], tuple[Point, int] | None] = {start: None}
    target: tuple[Point, int] | None = None

    while queue:
        _, cost, x, y, direction_index = heappop(queue)
        state = ((x, y), direction_index)
        if cost != costs.get(state):
            continue
        if (x, y) == sink:
            target = state
            break
        for next_direction, (dx, dy) in enumerate(directions):
            point = (x + dx, y + dy)
            if not (min_x <= point[0] <= max_x and min_y <= point[1] <= max_y):
                continue
            if point in blocked and point not in allowed_component_cells:
                continue
            next_cost = cost + 1 + (
                8 if direction_index >= 0 and direction_index != next_direction else 0
            )
            next_state = (point, next_direction)
            if next_cost >= costs.get(next_state, 1 << 60):
                continue
            costs[next_state] = next_cost
            previous[next_state] = state
            heuristic = abs(sink[0] - point[0]) + abs(sink[1] - point[1])
            heappush(
                queue,
                (next_cost + heuristic, next_cost, point[0], point[1], next_direction),
            )

    if target is None:
        raise RuntimeError(f"no component-safe route from {source} to {sink}")
    path: list[Point] = []
    state: tuple[Point, int] | None = target
    while state is not None:
        path.append(state[0])
        state = previous[state]
    path.reverse()
    return _compress_route(path)


def _build_router(components: tuple[Component, ...]):
    footprints = _component_footprints(components)
    access_map = _pin_access_map(components, footprints)
    pins = {
        pin.position
        for index, component in enumerate(components)
        for pin in positioned_pins(component, index)
    }
    blocked = frozenset().union(*footprints, pins)

    def route(source: Point, sink: Point):
        if source not in access_map or sink not in access_map:
            raise RuntimeError(f"RNG route has an unknown endpoint: {source} -> {sink}")
        vertices = _route_around_components(
            source,
            sink,
            blocked,
            access_map[source] | access_map[sink],
        )
        return wire_from_vertices(vertices)

    return route


def _mode_source(
    seed_form: int,
    state_form: int,
    *,
    state_sources: dict[int, Point],
    mode_sources: dict[tuple[int, int], Point],
) -> Point:
    if state_form.bit_count() != 1:
        raise RuntimeError(f"mode source state form is not one bit: {state_form:08x}")
    state_bit = bits(state_form)[0]
    if not seed_form:
        return state_sources[state_bit]
    if seed_form.bit_count() != 1:
        raise RuntimeError(f"mode source seed form is not one bit: {seed_form:08x}")
    pair = (bits(seed_form)[0], state_bit)
    try:
        return mode_sources[pair]
    except KeyError as exc:
        raise RuntimeError(f"missing certified mode pair {pair}") from exc


def build_rng_encoded_asic() -> Circuit:
    """Build the 47-OR/61-XOR encoded-state RNG candidate."""

    key = "architecture/codex-rng-encoded"

    def component(
        role: str,
        kind: int,
        position: Point,
        **kwargs: object,
    ) -> Component:
        return Component(
            kind=kind,
            position=position,
            rotation=0,
            permanent_id=stable_permanent_id(key, role),
            **kwargs,
        )

    level_input = component(
        "level-input", 62, (-410, 0), word_size=32, ui_order=-2, user_label="Seed"
    )
    level_output = component(
        "level-output",
        70,
        (180, 0),
        word_size=32,
        ui_order=-2,
        user_label="RNG output",
    )
    one = component("initialize-one", 2, (-410, -270))
    ready_delay = component("ready-delay", 13, (-392, -270), init_data=0)
    not_ready = component("not-ready", 3, (-374, -270))

    seed_word_splitter = component("seed-splitter-32", 99, (-380, 0), word_size=8)
    seed_byte_splitters = tuple(
        component(f"seed-splitter-8-{group}", 17, (-350, group * 112 - 168))
        for group in range(4)
    )
    state_delays = tuple(
        component(f"state-delay-{bit}", 13, (-290, bit * 14 - 217), init_data=0)
        for bit in range(WORD_BITS)
    )
    first_gates = tuple(gate for gate in GATES if gate.depth == 1)
    second_gates = tuple(gate for gate in GATES if gate.depth == 2)
    xor_components = {
        gate.output: component(
            f"xor-depth-{gate.depth}-{gate.output:08x}",
            10,
            (
                -100,
                index * 14 - 182,
            )
            if gate.depth == 1
            else (
                10,
                index * 14 - 231,
            ),
        )
        for gates in (first_gates, second_gates)
        for index, gate in enumerate(gates)
    }

    # Every certified mode pair feeds exactly one XOR input (five of those OR
    # outputs additionally fan out to a direct B feedback bit).  Keeping each
    # OR beside that XOR avoids a tall, cross-coupled central bank while
    # preserving the exact logical netlist.
    mode_pair_consumers: dict[tuple[int, int], tuple[XorGate, int]] = {}
    for gate in GATES:
        for side, fanin in enumerate((gate.left, gate.right)):
            if gate.depth == 1:
                seed_bit = FIRST_LEAF_SEEDS[gate.output][side]
                state_bit = bits(fanin)[0]
            elif fanin in FIRST_LAYER:
                continue
            else:
                seed_form = _seed_form_of_fanin(fanin, gate.output, side)
                if not seed_form:
                    continue
                seed_bit = bits(seed_form)[0]
                state_bit = bits(fanin)[0]
            if seed_bit is None:
                continue
            pair = (seed_bit, state_bit)
            if pair in mode_pair_consumers:
                raise AssertionError(f"mode pair {pair} has multiple XOR consumers")
            mode_pair_consumers[pair] = (gate, side)
    if frozenset(mode_pair_consumers) != MODE_PAIRS:
        raise AssertionError("mode-pair layout consumers changed")

    consumer_pair_counts = Counter(
        gate.output for gate, _ in mode_pair_consumers.values()
    )
    mode_ors = {}
    for pair in sorted(MODE_PAIRS):
        consumer, side = mode_pair_consumers[pair]
        consumer_y = xor_components[consumer.output].position[1]
        if consumer.depth == 1:
            offset_y = (
                -4 if side == 0 else 4
            ) if consumer_pair_counts[consumer.output] == 2 else 0
            position = (-175, consumer_y + offset_y)
        else:
            position = (-65, consumer_y)
        mode_ors[pair] = component(
            f"mode-or-seed-{pair[0]}-state-{pair[1]}",
            7,
            position,
        )

    byte_makers = tuple(
        component(f"result-maker-8-{group}", 16, (125, group * 112 - 168))
        for group in range(4)
    )
    word_maker = component("result-maker-32", 97, (150, 0), word_size=32)

    components = (
        level_input,
        level_output,
        one,
        ready_delay,
        not_ready,
        seed_word_splitter,
        *seed_byte_splitters,
        *state_delays,
        *(mode_ors[pair] for pair in sorted(mode_ors)),
        *(xor_components[gate.output] for gate in GATES),
        *byte_makers,
        word_maker,
    )
    route = _build_router(components)

    seed_sources = {
        bit: _pin(seed_byte_splitters[bit // 8], f"out{bit % 8}")
        for bit in range(WORD_BITS)
    }
    state_sources = {bit: _pin(state_delays[bit], "out") for bit in range(WORD_BITS)}
    mode_sources = {pair: _pin(gate, "out") for pair, gate in mode_ors.items()}

    wires = [
        route(_pin(one, "out"), _pin(ready_delay, "in")),
        route(_pin(ready_delay, "out"), _pin(not_ready, "in")),
        route(_pin(not_ready, "out"), _pin(level_input, "control")),
        route(_pin(level_input, "value"), _pin(seed_word_splitter, "in")),
        route(_pin(ready_delay, "out"), _pin(level_output, "control")),
    ]
    for group, splitter in enumerate(seed_byte_splitters):
        wires.append(
            route(_pin(seed_word_splitter, f"out{group}"), _pin(splitter, "in"))
        )

    for (seed_bit, state_bit), gate in sorted(mode_ors.items()):
        wires.append(route(state_sources[state_bit], _pin(gate, "in0")))
        wires.append(route(seed_sources[seed_bit], _pin(gate, "in1")))

    signal_sources: dict[int, Point] = {
        1 << bit: source for bit, source in state_sources.items()
    }
    for gate in GATES:
        gate_component = xor_components[gate.output]
        if gate.depth == 1:
            state_support = bits(gate.output)
            seed_support = FIRST_LEAF_SEEDS[gate.output]
            left_source = _mode_source(
                0 if seed_support[0] is None else 1 << seed_support[0],
                1 << state_support[0],
                state_sources=state_sources,
                mode_sources=mode_sources,
            )
            right_source = _mode_source(
                0 if seed_support[1] is None else 1 << seed_support[1],
                1 << state_support[1],
                state_sources=state_sources,
                mode_sources=mode_sources,
            )
        else:
            sources: list[Point] = []
            for side, fanin in enumerate((gate.left, gate.right)):
                if fanin in FIRST_LAYER:
                    sources.append(signal_sources[fanin])
                else:
                    sources.append(
                        _mode_source(
                            _seed_form_of_fanin(fanin, gate.output, side),
                            fanin,
                            state_sources=state_sources,
                            mode_sources=mode_sources,
                        )
                    )
            left_source, right_source = sources
        wires.append(route(left_source, _pin(gate_component, "in0")))
        wires.append(route(right_source, _pin(gate_component, "in1")))
        signal_sources[gate.output] = _pin(gate_component, "out")

    for bit, steady_target in enumerate(B):
        if steady_target in GATE_BY_OUTPUT:
            source = signal_sources[steady_target]
        else:
            source = _mode_source(
                T[bit],
                steady_target,
                state_sources=state_sources,
                mode_sources=mode_sources,
            )
        wires.append(route(source, _pin(state_delays[bit], "in")))

    for bit, steady_target in enumerate(C):
        source = signal_sources[steady_target]
        group, offset = divmod(bit, 8)
        wires.append(route(source, _pin(byte_makers[group], f"in{offset}")))
    for group, maker in enumerate(byte_makers):
        wires.append(route(_pin(maker, "out"), _pin(word_maker, f"in{group}")))
    wires.append(route(_pin(word_maker, "out"), _pin(level_output, "value")))

    return Circuit(
        gate=EXPECTED_GATE,
        delay=EXPECTED_DELAY,
        description=(
            "Codex RNG ASIC: encoded bit state with one 61-XOR B/C network and "
            "47 dual-mode OR leaves; one load tick followed by 65 outputs"
        ),
        components=components,
        wires=tuple(wires),
    )


def _disabled_input_probe(circuit: Circuit) -> Circuit:
    components = list(circuit.components)
    if not components or components[0].kind != 62:
        raise RuntimeError("RNG architecture input is not the expected first component")
    components[0] = replace(components[0], kind=61)
    return replace(circuit, components=tuple(components))


def _encoded_memory(circuit: Circuit, memory: dict[int, int]) -> int:
    result = 0
    for bit in range(WORD_BITS):
        key = stable_permanent_id("architecture/codex-rng-encoded", f"state-delay-{bit}")
        result |= (memory[key] & 1) << bit
    return result


def _verify_output_stream(circuit: Circuit, seed: int) -> tuple[int, ...]:
    first = simulate_clocked_tick(
        circuit,
        inputs={"Seed": seed},
        memory=initial_clocked_memory(circuit),
    )
    if first.outputs:
        raise RuntimeError(f"RNG emitted during seed-load tick: {first.outputs}")
    expected_encoded = apply_matrix(T, seed)
    if _encoded_memory(circuit, first.memory) != expected_encoded:
        raise RuntimeError(f"RNG encoded seed-load mismatch for {seed:08x}")

    probe = _disabled_input_probe(circuit)
    trace = simulate_clocked_ticks(
        probe,
        inputs={"Seed": 0},
        tick_count=EXPECTED_CYCLES - 1,
        memory=first.memory,
    )
    expected = seed
    outputs: list[int] = []
    for tick, result in enumerate(trace, start=1):
        expected = xorshift32(expected)
        if result.outputs != {"RNG output": expected}:
            raise RuntimeError(
                f"RNG mismatch for {seed:08x} at output {tick}: "
                f"expected {expected:08x}, got {result.outputs}"
            )
        encoded = _encoded_memory(circuit, result.memory)
        if encoded != apply_matrix(T, expected):
            raise RuntimeError(
                f"RNG encoded-state invariant failed for {seed:08x} at output {tick}"
            )
        outputs.append(expected)
    if len(outputs) != 65:
        raise RuntimeError(f"RNG emitted {len(outputs)} values instead of 65")
    return tuple(outputs)


def _layout_safety(circuit: Circuit) -> dict[str, int]:
    footprints = _component_footprints(circuit.components)
    access_map = _pin_access_map(circuit.components, footprints)
    pins_by_component = [
        {pin.position for pin in positioned_pins(component, index)}
        for index, component in enumerate(circuit.components)
    ]
    wire_component_contacts = 0
    wire_interior_pin_contacts = 0
    for wire in circuit.wires:
        points = wire_points(wire)
        endpoints = {points[0], points[-1]}
        permitted = frozenset().union(
            *(access_map.get(endpoint, frozenset({endpoint})) for endpoint in endpoints)
        )
        for footprint, pins in zip(footprints, pins_by_component):
            wire_component_contacts += sum(
                point in footprint
                and not (point in endpoints and point in pins)
                and point not in permitted
                for point in points
            )
        for point in points[1:-1]:
            wire_interior_pin_contacts += sum(point in pins for pins in pins_by_component)

    owners: Counter[Point] = Counter(point for footprint in footprints for point in footprint)
    return {
        "wire_component_contact_count": wire_component_contacts,
        "wire_interior_pin_contact_count": wire_interior_pin_contacts,
        "component_footprint_overlap_count": sum(
            count - 1 for count in owners.values() if count > 1
        ),
    }


def _verification_seeds() -> tuple[int, ...]:
    values = [0, 1, 2, 0x12345678, 0xFFFFFFFF]
    generator = random.Random(20260801)
    while len(values) < 69:
        candidate = generator.getrandbits(32)
        if candidate not in values:
            values.append(candidate)
    return tuple(values)


def _verify_rng_encoded_asic(circuit: Circuit) -> dict[str, object]:
    if (circuit.gate, circuit.delay) != (EXPECTED_GATE, EXPECTED_DELAY):
        raise RuntimeError("RNG encoded candidate metric declaration changed")
    kind_counts = Counter(component.kind for component in circuit.components)
    expected_counts = {7: 47, 10: 61, 13: 33}
    for kind, count in expected_counts.items():
        if kind_counts[kind] != count:
            raise RuntimeError(
                f"RNG encoded candidate kind {kind} count changed: {kind_counts[kind]}"
            )

    connectivity = analyze_connectivity(circuit)
    for field in (
        "unsupported_component_kind_counts",
        "unconnected_pin_count",
        "multi_driver_network_count",
        "undriven_network_count",
        "width_mismatch_network_count",
        "cycle_component_count",
    ):
        if connectivity[field]:
            raise RuntimeError(
                f"RNG encoded ASIC failed connectivity check {field}: "
                f"{connectivity[field]}"
            )

    layout = _layout_safety(circuit)
    if any(layout.values()):
        raise RuntimeError(f"RNG encoded ASIC failed conservative layout check: {layout}")
    sprite_audit = audit_sprite_geometry(circuit, DEFAULT_COMPONENT_SPRITE_ROOT)
    internal_collisions = tuple(
        collision
        for collision in sprite_audit.wire_collisions
        if collision.component_kind not in {62, 70}
    )
    if (
        sprite_audit.unsupported_component_kinds
        or sprite_audit.component_overlap_cells
        or internal_collisions
        or sprite_audit.wire_interior_pin_contacts
    ):
        raise RuntimeError(
            "RNG encoded ASIC failed live-sprite geometry check: "
            f"unsupported={sprite_audit.unsupported_component_kinds}, "
            f"overlap={len(sprite_audit.component_overlap_cells)}, "
            f"internal_collisions={len(internal_collisions)}, "
            f"pin_contacts={len(sprite_audit.wire_interior_pin_contacts)}"
        )

    seeds = _verification_seeds()
    first_stream = _verify_output_stream(circuit, seeds[1])
    for seed in (*seeds[:1], *seeds[2:]):
        _verify_output_stream(circuit, seed)
    return {
        "gate": circuit.gate,
        "delay": circuit.delay,
        "cycles": EXPECTED_CYCLES,
        "leaderboard_tuple": [circuit.gate, circuit.delay, EXPECTED_CYCLES],
        "declared_energy": circuit.gate * circuit.delay * EXPECTED_CYCLES,
        "public_reference": list(PUBLIC_REFERENCE),
        "predicted_rank1_improvement": PUBLIC_REFERENCE[3]
        - circuit.gate * circuit.delay * EXPECTED_CYCLES,
        "matrix_identities": ["C*T=A", "T*C=B", "T*T^-1=I"],
        "xor_count": len(GATES),
        "mode_pair_or_count": len(MODE_PAIRS),
        "verified_seed_count": len(seeds),
        "first_seed_prefix": [f"{value:08x}" for value in first_stream[:3]],
        "component_kind_counts": dict(sorted(kind_counts.items())),
        "connectivity": connectivity,
        "layout": layout,
        "live_sprite_layout": {
            "unsupported_component_kinds": list(sprite_audit.unsupported_component_kinds),
            "component_overlap_cell_count": len(sprite_audit.component_overlap_cells),
            "internal_wire_collision_count": len(internal_collisions),
            "wire_interior_pin_contact_count": len(
                sprite_audit.wire_interior_pin_contacts
            ),
            "architecture_io_access_cell_count": len(sprite_audit.wire_collisions)
            - len(internal_collisions),
        },
    }


@lru_cache(maxsize=1)
def _default_verification() -> dict[str, object]:
    return _verify_rng_encoded_asic(build_rng_encoded_asic())


def verify_rng_encoded_asic(circuit: Circuit | None = None) -> dict[str, object]:
    if circuit is not None:
        return _verify_rng_encoded_asic(circuit)
    return deepcopy(_default_verification())


def write_rng_encoded_asic(project_root: Path) -> dict[str, object]:
    candidate = build_rng_encoded_asic()
    verification = verify_rng_encoded_asic(candidate)
    payload = encode_v15(candidate)
    if decode_v15(payload) != candidate:
        raise RuntimeError("RNG encoded ASIC failed v15 round-trip verification")

    destination = project_root / "examples" / "rng" / "candidate" / "circuit.data"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(payload)
    metadata = {
        "schema": 1,
        "level": "rng",
        "title": "Random Number Generator",
        "strategy": "encoded-state depth-two XOR network with dual-mode OR leaves",
        "deployment_target": "schematics/architecture/CODEX-RNG/circuit.data",
        "sha256": sha256(payload).hexdigest(),
        "format_version": 15,
        "component_count": len(candidate.components),
        "wire_count": len(candidate.wires),
        "metric_status": (
            "gate/delay/cycles are derived from current component costs and a "
            "fully simulated topology; the game must still recompute leaderboard metrics"
        ),
        **verification,
    }
    (destination.parent / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return metadata
