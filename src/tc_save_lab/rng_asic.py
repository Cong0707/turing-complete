"""Build and independently simulate the fixed-network RNG architecture ASIC."""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
import random

from .analysis import wire_points
from .builder import stable_permanent_id, wire_from_vertices
from .codec import decode_v15, encode_v15
from .model import Circuit, Component, Point
from .pins import I, O, T, analyze_connectivity, positioned_pins
from .simulate import simulate_clocked_ticks


WORD_BITS = 32
WORD_MASK = (1 << WORD_BITS) - 1
# U32 Word Delay (160) + U32 Word Switch (64) + 61 XOR (183) + bit Delay
# (5) + NOT (1).  This is derived from the game's component-cost routine.
EXPECTED_GATE = 413
EXPECTED_DELAY = 11
EXPECTED_CYCLES = 66
PUBLIC_REFERENCE = (381, 11, 66, 276_606)


def xorshift32(value: int) -> int:
    """The exact transition function in the current RNG level script."""

    if not 0 <= value <= WORD_MASK:
        raise ValueError(f"RNG state must fit U32, got {value}")
    value ^= value >> 13
    value &= WORD_MASK
    value ^= (value << 17) & WORD_MASK
    value &= WORD_MASK
    value ^= value >> 5
    return value & WORD_MASK


def _pin(component: Component, name: str) -> Point:
    matches = [pin.position for pin in positioned_pins(component) if pin.name == name]
    if len(matches) != 1:
        raise RuntimeError(f"component kind {component.kind} has no unique pin {name!r}")
    return matches[0]


def _component_footprints(
    components: tuple[Component, ...],
) -> tuple[frozenset[Point], ...]:
    """Use a conservative box from every verified current-version pin."""

    footprints: list[frozenset[Point]] = []
    for index, component in enumerate(components):
        points = [component.position]
        points.extend(pin.position for pin in positioned_pins(component, index))
        min_x = min(point[0] for point in points)
        max_x = max(point[0] for point in points)
        min_y = min(point[1] for point in points)
        max_y = max(point[1] for point in points)
        footprints.append(
            frozenset(
                (x, y)
                for x in range(min_x, max_x + 1)
                for y in range(min_y, max_y + 1)
            )
        )
    return tuple(footprints)


def _layout_safety(circuit: Circuit) -> dict[str, int]:
    """Reject a wire that crosses a component body or a non-endpoint pin."""

    footprints = _component_footprints(circuit.components)
    pins_by_component = [
        {pin.position for pin in positioned_pins(component, index)}
        for index, component in enumerate(circuit.components)
    ]
    wire_component_contacts = 0
    wire_interior_pin_contacts = 0
    for wire in circuit.wires:
        points = wire_points(wire)
        endpoints = {points[0], points[-1]}
        for footprint, pins in zip(footprints, pins_by_component):
            wire_component_contacts += sum(
                point in footprint and not (point in endpoints and point in pins)
                for point in points
            )
        for point in points[1:-1]:
            wire_interior_pin_contacts += sum(point in pins for pins in pins_by_component)

    footprint_owners: Counter[Point] = Counter(
        point for footprint in footprints for point in footprint
    )
    return {
        "wire_component_contact_count": wire_component_contacts,
        "wire_interior_pin_contact_count": wire_interior_pin_contacts,
        "component_footprint_overlap_count": sum(
            count - 1 for count in footprint_owners.values() if count > 1
        ),
    }


def _vertices(*points: Point) -> tuple[Point, ...]:
    """Drop adjacent duplicate vertices while retaining only real segments."""

    result: list[Point] = []
    for point in points:
        if not result or point != result[-1]:
            result.append(point)
    if len(result) < 2:
        raise RuntimeError("wire route has fewer than two distinct vertices")
    return tuple(result)


def _forward_route(source: Point, sink: Point, *, lane_y: int | None = None):
    """Route left-to-right through the fixed empty channel between columns.

    Every logic column is spaced by at least 70 cells and every logic row by
    eight cells.  ``source.y + 3`` therefore sits between component bodies;
    this avoids general pathfinding and keeps the result deterministic.
    """

    if source[0] >= sink[0]:
        raise RuntimeError(f"forward route requires increasing X: {source} -> {sink}")
    source_exit = (source[0] + 1, source[1])
    sink_approach = (sink[0] - 1, sink[1])
    lane = source[1] + 3 if lane_y is None else lane_y
    return wire_from_vertices(
        _vertices(
            source,
            source_exit,
            (source_exit[0], lane),
            (sink_approach[0], lane),
            sink_approach,
            sink,
        )
    )


def _direct_route(source: Point, sink: Point):
    if source[0] == sink[0] or source[1] == sink[1]:
        return wire_from_vertices((source, sink))
    return _forward_route(source, sink)


def build_rng_asic() -> Circuit:
    """Build a 66-tick xorshift32 feedback machine from current components."""

    key = "architecture/codex-rng"

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
        "level-input", 62, (-250, 120), word_size=32, ui_order=-2, user_label="Seed"
    )
    level_output = component(
        "level-output", 70, (190, 120), word_size=32, ui_order=-2, user_label="RNG output"
    )
    one = component("initialize-one", 2, (-255, 100))
    ready_delay = component("ready-delay", 13, (-250, 100), init_data=0)
    not_ready = component("not-ready", 3, (-230, 100))
    state_delay = component("state-delay", 55, (-200, 120), word_size=32, init_data=0)
    feedback_switch = component("feedback-switch", 25, (170, 140), word_size=32)
    word_splitter = component("state-splitter-32", 99, (-170, 120), word_size=8)
    byte_splitters = tuple(
        component(f"state-splitter-8-{group}", 17, (-140, group * 64 + 3))
        for group in range(4)
    )
    stage_1 = {
        bit: component(f"stage-1-xor-{bit}", 10, (-80, bit * 8))
        for bit in range(19)
    }
    stage_2 = {
        bit: component(f"stage-2-xor-{bit}", 10, (0, bit * 8))
        for bit in range(17, 32)
    }
    stage_3 = {
        bit: component(f"stage-3-xor-{bit}", 10, (80, bit * 8))
        for bit in range(27)
    }
    byte_makers = tuple(
        component(f"result-maker-8-{group}", 16, (120, group * 64 + 3))
        for group in range(4)
    )
    word_maker = component("result-maker-32", 97, (150, 120), word_size=32)

    components = (
        level_input,
        level_output,
        one,
        ready_delay,
        not_ready,
        state_delay,
        feedback_switch,
        word_splitter,
        *byte_splitters,
        *(stage_1[bit] for bit in sorted(stage_1)),
        *(stage_2[bit] for bit in sorted(stage_2)),
        *(stage_3[bit] for bit in sorted(stage_3)),
        *byte_makers,
        word_maker,
    )

    state_bits = {
        bit: _pin(byte_splitters[bit // 8], f"out{bit % 8}")
        for bit in range(WORD_BITS)
    }
    stage_1_values = {
        bit: _pin(stage_1[bit], "out") if bit in stage_1 else state_bits[bit]
        for bit in range(WORD_BITS)
    }
    stage_2_values = {
        bit: _pin(stage_2[bit], "out") if bit in stage_2 else stage_1_values[bit]
        for bit in range(WORD_BITS)
    }
    result_bits = {
        bit: _pin(stage_3[bit], "out") if bit in stage_3 else stage_2_values[bit]
        for bit in range(WORD_BITS)
    }

    wires = [
        _direct_route(_pin(one, "out"), _pin(ready_delay, "in")),
        _direct_route(_pin(ready_delay, "out"), _pin(not_ready, "in")),
        wire_from_vertices(
            _vertices(
                _pin(not_ready, "out"),
                (-227, 100),
                (-227, 110),
                (-249, 110),
                (-249, 117),
                _pin(level_input, "control"),
            )
        ),
        _direct_route(_pin(level_input, "value"), _pin(state_delay, "in")),
        _direct_route(_pin(state_delay, "out"), _pin(word_splitter, "in")),
    ]

    for group, splitter in enumerate(byte_splitters):
        wires.append(
            _forward_route(
                _pin(word_splitter, f"out{group}"),
                _pin(splitter, "in"),
            )
        )

    # t1 = state xor (state >> 13)
    for bit, xor in stage_1.items():
        wires.extend(
            (
                _forward_route(state_bits[bit], _pin(xor, "in0"), lane_y=bit * 8 + 3),
                _forward_route(state_bits[bit + 13], _pin(xor, "in1"), lane_y=bit * 8 + 3),
            )
        )

    # t2 = t1 xor (t1 << 17)
    for bit, xor in stage_2.items():
        wires.extend(
            (
                _forward_route(stage_1_values[bit], _pin(xor, "in0"), lane_y=bit * 8 + 3),
                _forward_route(stage_1_values[bit - 17], _pin(xor, "in1"), lane_y=bit * 8 + 3),
            )
        )

    # result = t2 xor (t2 >> 5)
    for bit, xor in stage_3.items():
        wires.extend(
            (
                _forward_route(stage_2_values[bit], _pin(xor, "in0"), lane_y=bit * 8 + 3),
                _forward_route(stage_2_values[bit + 5], _pin(xor, "in1"), lane_y=bit * 8 + 3),
            )
        )

    for bit, source in result_bits.items():
        group, offset = divmod(bit, 8)
        wires.append(
            _forward_route(
                source,
                _pin(byte_makers[group], f"in{offset}"),
                lane_y=bit * 8 + 3,
            )
        )
    for group, maker in enumerate(byte_makers):
        wires.append(_forward_route(_pin(maker, "out"), _pin(word_maker, f"in{group}")))

    result_word = _pin(word_maker, "out")
    wires.extend(
        (
            _direct_route(result_word, _pin(level_output, "value")),
            _forward_route(result_word, _pin(feedback_switch, "in")),
            wire_from_vertices(
                _vertices(
                    _pin(feedback_switch, "out"),
                    (173, 140),
                    (173, 230),
                    (-203, 230),
                    (-203, 120),
                    _pin(state_delay, "in"),
                )
            ),
            wire_from_vertices(
                _vertices(
                    _pin(ready_delay, "out"),
                    (-246, 100),
                    (-246, -20),
                    (170, -20),
                    (170, 138),
                    _pin(feedback_switch, "enable"),
                )
            ),
            wire_from_vertices(
                _vertices(
                    _pin(ready_delay, "out"),
                    (-246, 100),
                    (-246, -20),
                    (189, -20),
                    (189, 117),
                    _pin(level_output, "control"),
                )
            ),
        )
    )

    return Circuit(
        gate=EXPECTED_GATE,
        delay=EXPECTED_DELAY,
        description=(
            "Codex RNG ASIC: 32-bit fixed xorshift feedback network; "
            "first tick loads the seed and the following 65 ticks emit results"
        ),
        components=components,
        wires=tuple(wires),
    )


def _verify_output_stream(circuit: Circuit, seed: int) -> tuple[int, ...]:
    expected = seed
    outputs: list[int] = []
    for tick, result in enumerate(
        simulate_clocked_ticks(
            circuit,
            inputs={"Seed": seed},
            tick_count=EXPECTED_CYCLES,
        )
    ):
        if tick == 0:
            if result.outputs:
                raise RuntimeError(f"RNG emitted a value during seed-load tick: {result.outputs}")
            continue
        expected = xorshift32(expected)
        if result.outputs != {"RNG output": expected}:
            raise RuntimeError(
                f"RNG transition mismatch for {seed:08x} at output {tick}: "
                f"expected {expected:08x}, got {result.outputs}"
            )
        outputs.append(expected)
    if len(outputs) != 65:
        raise RuntimeError(f"RNG emitted {len(outputs)} outputs instead of 65")
    return tuple(outputs)


def _verify_rng_asic(circuit: Circuit) -> dict[str, object]:
    """Validate topology, geometry and 65-output timing against the level oracle."""

    candidate = circuit
    if (candidate.gate, candidate.delay) != (EXPECTED_GATE, EXPECTED_DELAY):
        raise RuntimeError("RNG candidate metric declaration changed")
    kind_counts = Counter(component.kind for component in candidate.components)
    if kind_counts[10] != 61:
        raise RuntimeError(f"RNG fixed network must contain 61 bit XORs, got {kind_counts[10]}")
    connectivity = analyze_connectivity(candidate)
    for field in (
        "unsupported_component_kind_counts",
        "unconnected_pin_count",
        "multi_driver_network_count",
        "undriven_network_count",
        "width_mismatch_network_count",
        "cycle_component_count",
    ):
        if connectivity[field]:
            raise RuntimeError(f"RNG ASIC failed connectivity check {field}: {connectivity[field]}")
    layout = _layout_safety(candidate)
    if any(layout.values()):
        raise RuntimeError(f"RNG ASIC failed layout safety check: {layout}")

    seeds = (1, 2, 0x12345678, 0xFFFFFFFF)
    generator = random.Random(0xC0DEC0DE)
    random_seeds = tuple(generator.randrange(1, WORD_MASK) for _ in range(64))
    first_stream = _verify_output_stream(candidate, seeds[0])
    for seed in (*seeds[1:], *random_seeds):
        _verify_output_stream(candidate, seed)
    return {
        "gate": candidate.gate,
        "delay": candidate.delay,
        "cycles": EXPECTED_CYCLES,
        "leaderboard_tuple": [candidate.gate, candidate.delay, EXPECTED_CYCLES],
        "declared_energy": candidate.gate * candidate.delay * EXPECTED_CYCLES,
        "public_reference": list(PUBLIC_REFERENCE),
        "fixed_test_seeds": [f"{seed:08x}" for seed in seeds],
        "random_test_seed_count": len(random_seeds),
        "first_seed_prefix": [f"{value:08x}" for value in first_stream[:3]],
        "component_kind_counts": dict(sorted(kind_counts.items())),
        "connectivity": connectivity,
        "layout": layout,
    }


@lru_cache(maxsize=1)
def _default_verification() -> dict[str, object]:
    """Cache the deterministic full trace for repeated candidate builds."""

    return _verify_rng_asic(build_rng_asic())


def verify_rng_asic(circuit: Circuit | None = None) -> dict[str, object]:
    """Validate a supplied candidate, or the deterministic default candidate."""

    if circuit is not None:
        return _verify_rng_asic(circuit)
    # Callers receive their own nested mapping and cannot mutate the cache.
    return deepcopy(_default_verification())


def write_rng_asic(project_root: Path) -> dict[str, object]:
    candidate = build_rng_asic()
    verification = verify_rng_asic()
    payload = encode_v15(candidate)
    if decode_v15(payload) != candidate:
        raise RuntimeError("RNG ASIC failed v15 round-trip verification")
    destination = project_root / "examples" / "rng" / "candidate" / "circuit.data"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(payload)
    (destination.parent / ".gitkeep").unlink(missing_ok=True)
    metadata = {
        "schema": 1,
        "level": "rng",
        "title": "Random Number Generator",
        "strategy": "current-v15 fixed-xorshift32 feedback ASIC",
        "deployment_target": "schematics/architecture/CODEX-RNG/circuit.data",
        "sha256": sha256(payload).hexdigest(),
        "format_version": 15,
        "component_count": len(candidate.components),
        "wire_count": len(candidate.wires),
        "metric_status": (
            "gate is derived from verified component costs; delay and final score "
            "still require game-side recomputation"
        ),
        **verification,
    }
    (destination.parent / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return metadata
