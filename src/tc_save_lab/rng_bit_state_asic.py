"""Build the low-delay bit-state ASIC for the RNG architecture level."""

from __future__ import annotations

from collections import Counter
from copy import deepcopy, replace
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
import random

from .builder import stable_permanent_id, wire_from_vertices
from .codec import decode_v15, encode_v15
from .model import Circuit, Component, Point
from .pins import analyze_connectivity, positioned_pins
from .rng_asic import _layout_safety, _vertices, xorshift32
from .simulate import initial_clocked_memory, simulate_clocked_tick
from .sprite_geometry import DEFAULT_COMPONENT_SPRITE_ROOT, audit_sprite_geometry


WORD_BITS = 32
WORD_MASK = (1 << WORD_BITS) - 1

# 32 Delay Bits (160) + 61 XORs (183) + 32 ORs (32) + the ready
# Delay Bit (5) + NOT (1). Splitters, makers and architecture I/O are free.
EXPECTED_GATE = 381
EXPECTED_DELAY = 11
EXPECTED_CYCLES = 66
PUBLIC_REFERENCE = (431, 9, 66, 256_014)


def _pin(component: Component, name: str) -> Point:
    matches = [pin.position for pin in positioned_pins(component) if pin.name == name]
    if len(matches) != 1:
        raise RuntimeError(f"component kind {component.kind} has no unique pin {name!r}")
    return matches[0]


def _forward_route(source: Point, sink: Point, *, lane_y: int) -> object:
    if source[0] >= sink[0]:
        raise RuntimeError(f"forward route requires increasing X: {source} -> {sink}")
    source_exit = (source[0] + 1, source[1])
    sink_approach = (sink[0] - 1, sink[1])
    return wire_from_vertices(
        _vertices(
            source,
            source_exit,
            (source_exit[0], lane_y),
            (sink_approach[0], lane_y),
            sink_approach,
            sink,
        )
    )


def _direct_route(source: Point, sink: Point) -> object:
    if source[0] == sink[0] or source[1] == sink[1]:
        return wire_from_vertices((source, sink))
    return _forward_route(source, sink, lane_y=source[1] + 3)


def build_rng_bit_state_asic() -> Circuit:
    """Build the predicted 381/9/66 xorshift32 feedback machine.

    The state starts at zero. During tick zero, the switched architecture
    input contributes the seed to 32 OR gates, so the Delay Bits capture the
    seed. On later ticks the disabled input contributes zero and each OR gate
    feeds back one bit of F(state). The output remains disabled on tick zero.
    """

    key = "architecture/codex-rng-bit-state"

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
        "level-input", 62, (-360, 120), word_size=32, ui_order=-2, user_label="Seed"
    )
    level_output = component(
        "level-output",
        70,
        (200, 120),
        word_size=32,
        ui_order=-2,
        user_label="RNG output",
    )
    one = component("initialize-one", 2, (-360, -30))
    ready_delay = component("ready-delay", 13, (-350, -30), init_data=0)
    not_ready = component("not-ready", 3, (-330, -30))

    seed_word_splitter = component("seed-splitter-32", 99, (-330, 120), word_size=8)
    seed_byte_splitters = tuple(
        component(f"seed-splitter-8-{group}", 17, (-300, group * 64 + 3))
        for group in range(4)
    )
    state_delays = tuple(
        component(f"state-delay-{bit}", 13, (-240, bit * 8), init_data=0)
        for bit in range(WORD_BITS)
    )
    stage_1 = {
        bit: component(f"stage-1-xor-{bit}", 10, (-160, bit * 8))
        for bit in range(19)
    }
    stage_2 = {
        bit: component(f"stage-2-xor-{bit}", 10, (-80, bit * 8))
        for bit in range(17, 32)
    }
    stage_3 = {
        bit: component(f"stage-3-xor-{bit}", 10, (0, bit * 8))
        for bit in range(27)
    }
    seed_or = tuple(
        component(f"seed-or-{bit}", 7, (80, bit * 8))
        for bit in range(WORD_BITS)
    )
    byte_makers = tuple(
        component(f"result-maker-8-{group}", 16, (130, group * 64 + 3))
        for group in range(4)
    )
    word_maker = component("result-maker-32", 97, (160, 120), word_size=32)

    components = (
        level_input,
        level_output,
        one,
        ready_delay,
        not_ready,
        seed_word_splitter,
        *seed_byte_splitters,
        *state_delays,
        *(stage_1[bit] for bit in sorted(stage_1)),
        *(stage_2[bit] for bit in sorted(stage_2)),
        *(stage_3[bit] for bit in sorted(stage_3)),
        *seed_or,
        *byte_makers,
        word_maker,
    )

    seed_bits = {
        bit: _pin(seed_byte_splitters[bit // 8], f"out{bit % 8}")
        for bit in range(WORD_BITS)
    }
    state_bits = {bit: _pin(state_delays[bit], "out") for bit in range(WORD_BITS)}
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
                (-327, -30),
                (-327, -50),
                (-365, -50),
                (-365, 117),
                (-359, 117),
                _pin(level_input, "control"),
            )
        ),
        _direct_route(_pin(level_input, "value"), _pin(seed_word_splitter, "in")),
        wire_from_vertices(
            _vertices(
                _pin(ready_delay, "out"),
                (-346, -30),
                (-346, -60),
                (199, -60),
                (199, 117),
                _pin(level_output, "control"),
            )
        ),
    ]

    for group, splitter in enumerate(seed_byte_splitters):
        wires.append(
            _forward_route(
                _pin(seed_word_splitter, f"out{group}"),
                _pin(splitter, "in"),
                lane_y=group * 64 + 11,
            )
        )

    # t1 = state xor (state >> 13)
    for bit, xor in stage_1.items():
        wires.extend(
            (
                _forward_route(state_bits[bit], _pin(xor, "in0"), lane_y=bit * 8 + 3),
                _forward_route(
                    state_bits[bit + 13], _pin(xor, "in1"), lane_y=bit * 8 + 3
                ),
            )
        )

    # t2 = t1 xor (t1 << 17)
    for bit, xor in stage_2.items():
        wires.extend(
            (
                _forward_route(
                    stage_1_values[bit], _pin(xor, "in0"), lane_y=bit * 8 + 3
                ),
                _forward_route(
                    stage_1_values[bit - 17], _pin(xor, "in1"), lane_y=bit * 8 + 3
                ),
            )
        )

    # result = t2 xor (t2 >> 5)
    for bit, xor in stage_3.items():
        wires.extend(
            (
                _forward_route(
                    stage_2_values[bit], _pin(xor, "in0"), lane_y=bit * 8 + 3
                ),
                _forward_route(
                    stage_2_values[bit + 5], _pin(xor, "in1"), lane_y=bit * 8 + 3
                ),
            )
        )

    for bit in range(WORD_BITS):
        row_lane = bit * 8 + 3
        gate = seed_or[bit]
        wires.append(
            _forward_route(result_bits[bit], _pin(gate, "in0"), lane_y=row_lane)
        )
        wires.append(
            _forward_route(seed_bits[bit], _pin(gate, "in1"), lane_y=row_lane)
        )

        # The raw result bypasses the initialization OR on the visible output
        # path. This keeps the steady-state critical path at nine delay units.
        group, offset = divmod(bit, 8)
        wires.append(
            _forward_route(
                result_bits[bit],
                _pin(byte_makers[group], f"in{offset}"),
                lane_y=row_lane + 1,
            )
        )

        # Each feedback bit receives a private pair of outer routing lanes.
        # No two nets overlap, and all long segments stay outside the logic.
        right_x = 84 + bit
        left_x = -250 - bit
        return_y = 300 + bit * 3
        wires.append(
            wire_from_vertices(
                _vertices(
                    _pin(gate, "out"),
                    (right_x, bit * 8),
                    (right_x, return_y),
                    (left_x, return_y),
                    (left_x, bit * 8),
                    _pin(state_delays[bit], "in"),
                )
            )
        )

    for group, maker in enumerate(byte_makers):
        wires.append(
            _forward_route(
                _pin(maker, "out"),
                _pin(word_maker, f"in{group}"),
                lane_y=group * 64 + 11,
            )
        )
    wires.append(_direct_route(_pin(word_maker, "out"), _pin(level_output, "value")))

    return Circuit(
        gate=EXPECTED_GATE,
        delay=EXPECTED_DELAY,
        description=(
            "Codex RNG ASIC: bit-state xorshift32 with zero-state OR seed loading; "
            "one load tick followed by 65 outputs"
        ),
        components=components,
        wires=tuple(wires),
    )


def _disabled_input_probe(circuit: Circuit) -> Circuit:
    """Replace the switched level input with a zero-valued ordinary source.

    The runtime preserves a disabled architecture input's numeric zero while
    marking the bus high impedance. The OR initialization topology deliberately
    consumes that numeric value. A normal source lets the reviewed simulator
    exercise the same data path without teaching its generic network resolver
    four-state bus semantics.
    """

    components = list(circuit.components)
    if components[0].kind != 62:
        raise RuntimeError("RNG level input is not the expected first component")
    components[0] = replace(components[0], kind=61)
    return replace(circuit, components=tuple(components))


def _verify_output_stream(circuit: Circuit, seed: int) -> tuple[int, ...]:
    memory = initial_clocked_memory(circuit)
    first = simulate_clocked_tick(circuit, inputs={"Seed": seed}, memory=memory)
    if first.outputs:
        raise RuntimeError(f"RNG emitted a value during seed-load tick: {first.outputs}")

    probe = _disabled_input_probe(circuit)
    memory = first.memory
    expected = seed
    outputs: list[int] = []
    for tick in range(1, EXPECTED_CYCLES):
        result = simulate_clocked_tick(probe, inputs={"Seed": 0}, memory=memory)
        expected = xorshift32(expected)
        if result.outputs != {"RNG output": expected}:
            raise RuntimeError(
                f"RNG transition mismatch for {seed:08x} at output {tick}: "
                f"expected {expected:08x}, got {result.outputs}"
            )
        outputs.append(expected)
        memory = result.memory
    if len(outputs) != 65:
        raise RuntimeError(f"RNG emitted {len(outputs)} outputs instead of 65")
    return tuple(outputs)


def _verify_rng_bit_state_asic(circuit: Circuit) -> dict[str, object]:
    if (circuit.gate, circuit.delay) != (EXPECTED_GATE, EXPECTED_DELAY):
        raise RuntimeError("RNG bit-state candidate metric declaration changed")
    kind_counts = Counter(component.kind for component in circuit.components)
    expected_counts = {7: 32, 10: 61, 13: 33}
    for kind, count in expected_counts.items():
        if kind_counts[kind] != count:
            raise RuntimeError(
                f"RNG bit-state candidate kind {kind} count changed: {kind_counts[kind]}"
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
                f"RNG bit-state ASIC failed connectivity check {field}: "
                f"{connectivity[field]}"
            )
    layout = _layout_safety(circuit)
    if any(layout.values()):
        raise RuntimeError(f"RNG bit-state ASIC failed layout safety check: {layout}")
    sprite_audit = audit_sprite_geometry(circuit, DEFAULT_COMPONENT_SPRITE_ROOT)
    internal_sprite_collisions = tuple(
        collision
        for collision in sprite_audit.wire_collisions
        if collision.component_kind not in {62, 70}
    )
    if (
        sprite_audit.unsupported_component_kinds
        or sprite_audit.component_overlap_cells
        or internal_sprite_collisions
        or sprite_audit.wire_interior_pin_contacts
    ):
        raise RuntimeError(
            "RNG bit-state ASIC failed live-sprite geometry check: "
            f"unsupported={sprite_audit.unsupported_component_kinds}, "
            f"overlap={len(sprite_audit.component_overlap_cells)}, "
            f"internal_collisions={len(internal_sprite_collisions)}, "
            f"pin_contacts={len(sprite_audit.wire_interior_pin_contacts)}"
        )

    seeds = (1, 2, 0x12345678, 0xFFFFFFFF)
    generator = random.Random(0xC0DEC0DE)
    random_seeds = tuple(generator.randrange(1, WORD_MASK) for _ in range(64))
    first_stream = _verify_output_stream(circuit, seeds[0])
    for seed in (*seeds[1:], *random_seeds):
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
        "fixed_test_seeds": [f"{seed:08x}" for seed in seeds],
        "random_test_seed_count": len(random_seeds),
        "first_seed_prefix": [f"{value:08x}" for value in first_stream[:3]],
        "component_kind_counts": dict(sorted(kind_counts.items())),
        "connectivity": connectivity,
        "layout": layout,
        "live_sprite_layout": {
            "unsupported_component_kinds": list(sprite_audit.unsupported_component_kinds),
            "component_overlap_cell_count": len(sprite_audit.component_overlap_cells),
            "internal_wire_collision_count": len(internal_sprite_collisions),
            "wire_interior_pin_contact_count": len(
                sprite_audit.wire_interior_pin_contacts
            ),
            "architecture_io_access_cell_count": len(sprite_audit.wire_collisions)
            - len(internal_sprite_collisions),
        },
    }


@lru_cache(maxsize=1)
def _default_verification() -> dict[str, object]:
    return _verify_rng_bit_state_asic(build_rng_bit_state_asic())


def verify_rng_bit_state_asic(circuit: Circuit | None = None) -> dict[str, object]:
    if circuit is not None:
        return _verify_rng_bit_state_asic(circuit)
    return deepcopy(_default_verification())


def write_rng_bit_state_asic(project_root: Path) -> dict[str, object]:
    candidate = build_rng_bit_state_asic()
    verification = verify_rng_bit_state_asic()
    payload = encode_v15(candidate)
    if decode_v15(payload) != candidate:
        raise RuntimeError("RNG bit-state ASIC failed v15 round-trip verification")

    destination = project_root / "examples" / "rng" / "candidate" / "circuit.data"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(payload)
    metadata = {
        "schema": 1,
        "level": "rng",
        "title": "Random Number Generator",
        "strategy": "bit-state xorshift32 with zero-state OR seed loading",
        "deployment_target": "schematics/architecture/CODEX-RNG/circuit.data",
        "sha256": sha256(payload).hexdigest(),
        "format_version": 15,
        "component_count": len(candidate.components),
        "wire_count": len(candidate.wires),
        "metric_status": (
            "gate is derived from current component costs; delay 9 is a topology "
            "prediction and must be recomputed by the game"
        ),
        **verification,
    }
    (destination.parent / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return metadata
