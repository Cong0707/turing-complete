"""Build and verify the U64 phase-packed, dual-store RNG candidate."""

from __future__ import annotations

from collections import Counter
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from tc_save_lab.analysis import wire_points  # noqa: E402
from tc_save_lab.builder import stable_permanent_id, wire_from_vertices  # noqa: E402
from tc_save_lab.codec import decode_v15, encode_v15  # noqa: E402
from tc_save_lab.model import Circuit, Component, Point, Wire  # noqa: E402
from tc_save_lab.pins import analyze_connectivity, positioned_pins  # noqa: E402
from tc_save_lab import rng_bit_state_asic as bit_state  # noqa: E402
from tc_save_lab import rng_ram_asic as ram_asic  # noqa: E402
from tc_save_lab.simulate import (  # noqa: E402
    _compile,
    _simulate_clocked_tick,
    initial_clocked_memory,
)
from tc_save_lab.sprite_geometry import (  # noqa: E402
    DEFAULT_COMPONENT_SPRITE_ROOT,
    audit_sprite_geometry,
)


BASE_PATH = (
    PROJECT_ROOT
    / ".research"
    / "rng_natural_ram_u1"
    / "candidate"
    / "circuit.data"
)
KEY = "architecture/codex-rng-u64-phase-dual-store"
RAM_BUFFER_SIZE = 8
EXPECTED_GATE = 94
EXPECTED_DELAY = 6
EXPECTED_CYCLES = 66


def _pin(component: Component, name: str) -> Point:
    matches = [pin.position for pin in positioned_pins(component) if pin.name == name]
    if len(matches) != 1:
        raise RuntimeError(f"component kind {component.kind} has no unique pin {name!r}")
    return matches[0]


def _component(role: str, kind: int, position: Point, **kwargs: object) -> Component:
    return Component(
        kind=kind,
        position=position,
        rotation=0,
        permanent_id=stable_permanent_id(KEY, role),
        **kwargs,
    )


def _wire_to_sink(circuit: Circuit, sink: Point) -> Wire:
    matches = [wire for wire in circuit.wires if wire_points(wire)[-1] == sink]
    if len(matches) != 1:
        raise RuntimeError(f"expected one wire ending at {sink}, got {len(matches)}")
    return matches[0]


def build_candidate() -> Circuit:
    base = decode_v15(BASE_PATH.read_bytes())

    level_input = next(component for component in base.components if component.kind == 62)
    level_output = next(component for component in base.components if component.kind == 70)
    one = next(component for component in base.components if component.kind == 2)
    ready_delay = next(component for component in base.components if component.kind == 13)
    not_ready = next(component for component in base.components if component.kind == 3)
    seed_word_splitter = next(
        component
        for component in base.components
        if component.kind == 99 and component.position == (-330, 120)
    )
    seed_bit_splitters = tuple(
        component
        for component in base.components
        if component.kind == 17 and component.position[0] == -300
    )
    seed_ors = tuple(component for component in base.components if component.kind == 7)
    output_byte_makers = tuple(
        sorted(
            (
                component
                for component in base.components
                if component.kind == 16 and component.position[0] == 130
            ),
            key=lambda component: component.position[1],
        )
    )
    state_word_splitter = next(
        component
        for component in base.components
        if component.kind == 99 and component.position == (-300, 560)
    )
    state_byte_splitters = tuple(
        sorted(
            (
                component
                for component in base.components
                if component.kind == 17 and component.position[0] == -245
            ),
            key=lambda component: component.position[1],
        )
    )
    feedback_byte_makers = tuple(
        sorted(
            (
                component
                for component in base.components
                if component.kind == 16 and component.position[0] == 220
            ),
            key=lambda component: component.position[1],
        )
    )
    feedback_word_maker = next(
        component
        for component in base.components
        if component.kind == 97 and component.position == (250, 560)
    )
    address_zero = next(component for component in base.components if component.kind == 46)
    ram = next(component for component in base.components if component.kind == 118)
    old_load = next(component for component in base.components if component.kind == 54)
    old_store = next(component for component in base.components if component.kind == 56)

    if not (
        len(seed_bit_splitters) == 4
        and len(seed_ors) == 32
        and len(output_byte_makers) == 4
        and len(state_byte_splitters) == 4
        and len(feedback_byte_makers) == 4
    ):
        raise RuntimeError("natural candidate topology changed")

    result_sources: dict[int, Point] = {}
    for bit in range(32):
        group, offset = divmod(bit, 8)
        sink = _pin(output_byte_makers[group], f"in{offset}")
        result_sources[bit] = wire_points(_wire_to_sink(base, sink))[0]

    removed = {
        ready_delay.permanent_id,
        state_word_splitter.permanent_id,
        feedback_word_maker.permanent_id,
        old_load.permanent_id,
        old_store.permanent_id,
        *(component.permanent_id for component in seed_bit_splitters),
        *(component.permanent_id for component in seed_ors),
    }
    removed_pins = {
        pin.position
        for component in base.components
        if component.permanent_id in removed
        for pin in positioned_pins(component)
    }

    state_splitter64 = _component(
        "state-splitter64", 100, (-300, 560), word_size=8
    )
    ready_byte_splitter = _component(
        "ready-byte-splitter", 17, (-245, 840)
    )
    next_ready_byte_maker = _component(
        "next-ready-byte-maker", 16, (220, 840)
    )
    feedback_maker64 = _component(
        "feedback-maker64", 98, (250, 560), word_size=64
    )
    seed_maker64 = _component("seed-maker64", 98, (250, 840), word_size=64)
    ram_load = _component("state-load64", 54, (320, 548), word_size=64)
    feedback_store = _component(
        "feedback-store64", 56, (320, 550), word_size=64
    )
    seed_store = _component("seed-store64", 56, (320, 554), word_size=64)

    components = (
        *(
            component
            for component in base.components
            if component.permanent_id not in removed
        ),
        state_splitter64,
        ready_byte_splitter,
        next_ready_byte_maker,
        feedback_maker64,
        seed_maker64,
        ram_load,
        feedback_store,
        seed_store,
    )
    route = ram_asic._build_router(components)
    wires = [
        wire
        for wire in base.wires
        if wire_points(wire)[0] not in removed_pins
        and wire_points(wire)[-1] not in removed_pins
    ]

    def connect(source: Point, sink: Point) -> None:
        wires.append(route(source, sink))

    ready = _pin(ready_byte_splitter, "out0")
    not_ready_out = _pin(not_ready, "out")
    address = _pin(address_zero, "out")

    connect(_pin(one, "out"), _pin(ram_load, "enable"))
    connect(_pin(one, "out"), _pin(next_ready_byte_maker, "in0"))
    connect(ready, _pin(not_ready, "in"))
    connect(ready, _pin(level_output, "control"))
    connect(ready, _pin(feedback_store, "enable"))
    connect(not_ready_out, _pin(seed_store, "enable"))
    connect(address, _pin(ram_load, "address"))
    connect(address, _pin(feedback_store, "address"))
    connect(address, _pin(seed_store, "address"))
    connect(_pin(ram_load, "out"), _pin(state_splitter64, "in"))

    for group in range(4):
        connect(
            _pin(state_splitter64, f"out{group}"),
            _pin(state_byte_splitters[group], "in"),
        )
    connect(_pin(state_splitter64, "out4"), _pin(ready_byte_splitter, "in"))
    for bit in range(1, 8):
        connect(
            _pin(ready_byte_splitter, f"out{bit}"),
            _pin(next_ready_byte_maker, f"in{bit}"),
        )

    for bit in range(32):
        group, offset = divmod(bit, 8)
        connect(
            result_sources[bit],
            _pin(feedback_byte_makers[group], f"in{offset}"),
        )
    for group in range(4):
        connect(
            _pin(feedback_byte_makers[group], "out"),
            _pin(feedback_maker64, f"in{group}"),
        )
        connect(
            _pin(seed_word_splitter, f"out{group}"),
            _pin(seed_maker64, f"in{group}"),
        )

    connect(_pin(next_ready_byte_maker, "out"), _pin(feedback_maker64, "in4"))
    connect(_pin(next_ready_byte_maker, "out"), _pin(seed_maker64, "in4"))
    for group in range(5, 8):
        source = _pin(state_splitter64, f"out{group}")
        connect(source, _pin(feedback_maker64, f"in{group}"))
        connect(source, _pin(seed_maker64, f"in{group}"))

    connect(_pin(feedback_maker64, "out"), _pin(feedback_store, "data"))
    connect(_pin(seed_maker64, "out"), _pin(seed_store, "data"))

    return replace(
        base,
        gate=EXPECTED_GATE,
        delay=EXPECTED_DELAY,
        description=(
            "Codex natural xorshift32: U64 RAM packs ready with state; "
            "dual stores select seed or feedback"
        ),
        components=components,
        wires=tuple(wires),
    )


def _direct_wire(source: Point, sink: Point) -> Wire:
    vertices = [source]
    bend = (sink[0], source[1])
    if bend not in {source, sink}:
        vertices.append(bend)
    vertices.append(sink)
    return wire_from_vertices(tuple(vertices))


def _surrogate(candidate: Circuit) -> Circuit:
    ram = next(component for component in candidate.components if component.kind == 118)
    load = next(component for component in candidate.components if component.kind == 54)
    stores = tuple(component for component in candidate.components if component.kind == 56)
    if len(stores) != 2:
        raise RuntimeError("dual-store candidate no longer has two stores")

    ram_group = {ram.permanent_id, load.permanent_id, *(store.permanent_id for store in stores)}
    ram_group_pins = {
        pin.position
        for component in (load, *stores)
        for pin in positioned_pins(component)
    }
    kept_wires = [
        wire
        for wire in candidate.wires
        if wire_points(wire)[0] not in ram_group_pins
        and wire_points(wire)[-1] not in ram_group_pins
    ]

    delay = replace(
        ram,
        kind=55,
        position=(360, 900),
        word_size=64,
        settings=(),
        buffer_size=0,
        init_data=0,
    )
    switches = tuple(
        replace(
            store,
            kind=25,
            position=(300, 900 + index * 12),
            word_size=64,
        )
        for index, store in enumerate(stores)
    )
    components = (
        *(
            component
            for component in candidate.components
            if component.permanent_id not in ram_group
        ),
        delay,
        *switches,
    )
    wires = list(kept_wires)

    load_out_wire = next(
        wire
        for wire in candidate.wires
        if wire_points(wire)[0] == _pin(load, "out")
    )
    wires.append(_direct_wire(_pin(delay, "out"), wire_points(load_out_wire)[-1]))
    for store, switch in zip(stores, switches):
        data_wire = _wire_to_sink(candidate, _pin(store, "data"))
        enable_wire = _wire_to_sink(candidate, _pin(store, "enable"))
        wires.append(_direct_wire(wire_points(data_wire)[0], _pin(switch, "in")))
        wires.append(_direct_wire(wire_points(enable_wire)[0], _pin(switch, "enable")))
        wires.append(_direct_wire(_pin(switch, "out"), _pin(delay, "in")))
    return replace(candidate, components=components, wires=tuple(wires))


def _verify_runtime(candidate: Circuit) -> tuple[int, ...]:
    surrogate = _surrogate(candidate)
    compiled = _compile(surrogate)
    delay = next(component for component in surrogate.components if component.kind == 55)
    first_stream: list[int] = []
    for test_id in range(256):
        seed = ram_asic._runtime_seed(test_id)
        memory = initial_clocked_memory(surrogate)
        first = _simulate_clocked_tick(
            surrogate,
            inputs={"Seed": seed},
            memory=memory,
            compiled=compiled,
        )
        if first.outputs:
            raise RuntimeError(f"RNG emitted during seed tick for test {test_id}")
        packed = first.memory[delay.permanent_id]
        if packed != ((1 << 32) | seed):
            raise RuntimeError(f"packed seed mismatch for test {test_id}: {packed:016x}")
        memory = first.memory
        expected = seed
        for tick in range(65):
            result = _simulate_clocked_tick(
                surrogate,
                inputs={"Seed": seed},
                memory=memory,
                compiled=compiled,
            )
            expected = bit_state.xorshift32(expected)
            if result.outputs != {"RNG output": expected}:
                raise RuntimeError(
                    f"RNG mismatch test={test_id} tick={tick}: "
                    f"expected={expected:08x} actual={result.outputs}"
                )
            packed = result.memory[delay.permanent_id]
            if packed != ((1 << 32) | expected):
                raise RuntimeError(
                    f"packed feedback mismatch test={test_id} tick={tick}: {packed:016x}"
                )
            memory = result.memory
            if test_id == 0 and len(first_stream) < 3:
                first_stream.append(expected)
    return tuple(first_stream)


def _layout(candidate: Circuit) -> dict[str, int]:
    raw = ram_asic._layout_safety(candidate)
    audit = audit_sprite_geometry(candidate, DEFAULT_COMPONENT_SPRITE_ROOT)
    ram_group = {
        index
        for index, component in enumerate(candidate.components)
        if component.kind in {54, 56, 118}
    }
    ram_pins = {
        pin.position
        for index in ram_group
        for pin in positioned_pins(candidate.components[index], index)
    }
    architecture_io = {
        index
        for index, component in enumerate(candidate.components)
        if component.kind in {62, 70}
    }
    internal_collisions = [
        collision
        for collision in audit.wire_collisions
        if not (
            collision.component_index in ram_group and collision.point in ram_pins
        )
        and collision.component_index not in architecture_io
    ]
    return {
        **raw,
        "live_component_overlap_cell_count": len(audit.component_overlap_cells),
        "live_internal_wire_collision_count": len(internal_collisions),
        "live_wire_interior_pin_contact_count": len(audit.wire_interior_pin_contacts),
        "live_unsupported_component_count": len(audit.unsupported_component_kinds),
    }


def verify_candidate(candidate: Circuit) -> dict[str, object]:
    if (candidate.gate, candidate.delay) != (EXPECTED_GATE, EXPECTED_DELAY):
        raise RuntimeError("candidate header changed")
    counts = Counter(component.kind for component in candidate.components)
    expected_counts = {3: 1, 7: 0, 13: 0, 23: 61, 54: 1, 56: 2, 98: 2, 100: 1, 118: 1}
    for kind, count in expected_counts.items():
        if counts[kind] != count:
            raise RuntimeError(f"unexpected kind {kind} count: {counts[kind]} != {count}")
    ram = next(component for component in candidate.components if component.kind == 118)
    if ram.settings != (2, 512, 0) or ram.buffer_size != RAM_BUFFER_SIZE:
        raise RuntimeError("RAM hidden mode or buffer changed")
    if any(component.word_size != 64 for component in candidate.components if component.kind in {54, 56}):
        raise RuntimeError("RAM access port is not U64")

    connectivity = analyze_connectivity(candidate)
    for field in (
        "unconnected_pin_count",
        "multi_driver_network_count",
        "undriven_network_count",
        "sinkless_network_count",
        "width_mismatch_network_count",
        "cycle_component_count",
    ):
        if connectivity[field]:
            raise RuntimeError(f"connectivity failure {field}={connectivity[field]}")
    layout = _layout(candidate)
    for field in (
        "wire_component_contact_count",
        "wire_interior_pin_contact_count",
        "component_footprint_overlap_count",
        "live_internal_wire_collision_count",
        "live_wire_interior_pin_contact_count",
        "live_unsupported_component_count",
    ):
        if layout[field]:
            raise RuntimeError(f"layout failure {field}={layout[field]}")

    first_stream = _verify_runtime(candidate)
    payload = encode_v15(candidate)
    if encode_v15(decode_v15(payload)) != payload:
        raise RuntimeError("candidate is not a byte-identical v15 round trip")
    return {
        "schema": 1,
        "level": "rng",
        "strategy": "U64 phase-packed state with mutually enabled seed/feedback stores",
        "sha256": sha256(payload).hexdigest(),
        "format_version": 15,
        "leaderboard_tuple": [EXPECTED_GATE, EXPECTED_DELAY, EXPECTED_CYCLES],
        "energy": EXPECTED_GATE * EXPECTED_DELAY * EXPECTED_CYCLES,
        "component_count": len(candidate.components),
        "wire_count": len(candidate.wires),
        "component_kind_counts": dict(sorted(counts.items())),
        "runtime_test_seed_count": 256,
        "runtime_tick_count": 256 * EXPECTED_CYCLES,
        "first_seed_prefix": [f"{value:08x}" for value in first_stream],
        "connectivity": connectivity,
        "layout": layout,
        "gate_ledger": {
            "u1_word_xor": 61,
            "not_ready": 1,
            "ram_backing": 8,
            "ram_load": 8,
            "ram_feedback_store": 8,
            "ram_seed_store": 8,
        },
        "delay_certificate": {
            "state_output": "three U1 Word XOR stages = 6",
            "feedback_store": "three U1 Word XOR stages = 6",
            "seed_store": "RAM ready + NOT = 1 before the seed data source",
        },
        "v15_byte_identical_round_trip": True,
    }


def main() -> None:
    output_root = Path(__file__).resolve().parent / "candidate"
    output_root.mkdir(parents=True, exist_ok=True)
    staged_path = output_root / "unverified.circuit.data"
    if staged_path.exists():
        candidate = decode_v15(staged_path.read_bytes())
    else:
        candidate = build_candidate()
        staged_path.write_bytes(encode_v15(candidate))
    result = verify_candidate(candidate)
    payload = encode_v15(candidate)
    (output_root / "circuit.data").write_bytes(payload)
    (output_root / "result.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
