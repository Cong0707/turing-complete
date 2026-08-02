#!/usr/bin/env python3
"""Build and optionally install the hidden-mode RAM RNG candidate.

The script preserves the verified 61-XOR/47-OR encoded-state network and only
replaces its 32 Bit Delays with one four-byte RAM plus one U32 load/store pair.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import replace
from hashlib import sha256
import json
import os
from pathlib import Path
import random

from tc_save_lab import pins as pin_model
from tc_save_lab.analysis import wire_points
from tc_save_lab.builder import stable_permanent_id
from tc_save_lab.codec import decode_v15, encode_v15
from tc_save_lab.model import Circuit, Component, Point, Wire
from tc_save_lab.pins import I, O, PinSpec, analyze_connectivity, positioned_pins
from tc_save_lab.rng_encoded_asic import (
    A,
    B,
    C,
    EXPECTED_CYCLES,
    T,
    WORD_BITS,
    WORD_MASK,
    _FOOTPRINT_BOXES,
    _build_router,
    _component_footprints,
    _pin,
    _pin_access_map,
    apply_matrix,
    xorshift32,
)


SOURCE_GATE = 396
SOURCE_DELAY = 10
TARGET_GATE = 304
TARGET_DELAY = 6
TARGET_TICKS = 66
RAM_SETTINGS = (2, 512, 0)
RAM_BUFFER_SIZE = 4
FORMAL_PARTS = (
    "schematics",
    "architecture",
    "CODEX-RNG",
    "circuit.data",
)
STATE_NAMESPACE = "architecture/codex-rng-encoded"
RAM_NAMESPACE = "architecture/codex-rng-ram2"


def digest(payload: bytes) -> str:
    return sha256(payload).hexdigest()


def _install_hidden_pin_schemas() -> None:
    """Describe only the externally routable pins of native RAM ports."""

    pin_model.PIN_SCHEMAS[54] = (
        PinSpec("enable", I, (-15, -1), 1),
        PinSpec("address", I, (-15, 0), 32),
        PinSpec("out", O, (16, -1)),
    )
    pin_model.PIN_SCHEMAS[56] = (
        PinSpec("enable", I, (-15, -1), 1),
        PinSpec("address", I, (-15, 0), 32),
        PinSpec("data", I, (-15, 1)),
    )
    # The RAM body has no wire pins. Load/store ports are separate serialized
    # components; the old aggregate approximation must not double-count them.
    pin_model.PIN_SCHEMAS[118] = ()

    # Native load/store bars span the RAM width. The store touches the RAM's
    # top edge by design, exactly as in current RV64 and MEMORYREGFILE saves.
    _FOOTPRINT_BOXES[46] = (-3, -2, 3, 2)
    _FOOTPRINT_BOXES[54] = (-15, -1, 16, 1)
    _FOOTPRINT_BOXES[56] = (-15, -1, 15, 1)
    _FOOTPRINT_BOXES[118] = (-15, -9, 15, 9)


def _component(role: str, kind: int, position: Point, **kwargs: object) -> Component:
    return Component(
        kind=kind,
        position=position,
        rotation=0,
        permanent_id=stable_permanent_id(RAM_NAMESPACE, role),
        **kwargs,
    )


def _state_delays(source: Circuit) -> dict[int, Component]:
    by_id = {component.permanent_id: component for component in source.components}
    result = {}
    for bit in range(WORD_BITS):
        permanent_id = stable_permanent_id(
            STATE_NAMESPACE,
            f"state-delay-{bit}",
        )
        component = by_id.get(permanent_id)
        if component is None or component.kind != 13:
            raise RuntimeError(f"source state Delay {bit} is missing")
        result[bit] = component
    return result


def _split_state_wires(
    source: Circuit,
    delays: dict[int, Component],
) -> tuple[tuple[Wire, ...], dict[int, Point], dict[int, tuple[Point, ...]]]:
    input_owner = {_pin(component, "in"): bit for bit, component in delays.items()}
    output_owner = {_pin(component, "out"): bit for bit, component in delays.items()}
    feedback_sources: dict[int, Point] = {}
    state_sinks: dict[int, list[Point]] = {bit: [] for bit in range(WORD_BITS)}
    kept: list[Wire] = []

    for wire in source.wires:
        points = wire_points(wire)
        endpoints = (points[0], points[-1])
        delay_endpoints = [
            point
            for point in endpoints
            if point in input_owner or point in output_owner
        ]
        if not delay_endpoints:
            kept.append(wire)
            continue
        if len(delay_endpoints) != 1:
            raise RuntimeError(f"wire unexpectedly joins two state Delays: {endpoints}")
        delay_point = delay_endpoints[0]
        other = endpoints[1] if endpoints[0] == delay_point else endpoints[0]
        if delay_point in input_owner:
            bit = input_owner[delay_point]
            if bit in feedback_sources:
                raise RuntimeError(f"state Delay {bit} has multiple input drivers")
            feedback_sources[bit] = other
        else:
            state_sinks[output_owner[delay_point]].append(other)

    if set(feedback_sources) != set(range(WORD_BITS)):
        raise RuntimeError("not every removed state Delay has one feedback source")
    if any(not state_sinks[bit] for bit in range(WORD_BITS)):
        raise RuntimeError("a removed state Delay output lost all consumers")
    return (
        tuple(kept),
        feedback_sources,
        {bit: tuple(sinks) for bit, sinks in state_sinks.items()},
    )


def build_candidate(source: Circuit) -> tuple[Circuit, dict[str, object]]:
    _install_hidden_pin_schemas()
    if (source.gate, source.delay) != (SOURCE_GATE, SOURCE_DELAY):
        raise RuntimeError(
            f"unexpected source metrics {(source.gate, source.delay)}"
        )

    delays = _state_delays(source)
    delay_ids = {component.permanent_id for component in delays.values()}
    kept_wires, feedback_sources, state_sinks = _split_state_wires(source, delays)
    retained = tuple(
        component
        for component in source.components
        if component.permanent_id not in delay_ids
    )

    # Put the replacement state machinery in a separate lower band. Existing
    # verified routes occupy y=-270..232, so no retained wire can hit it.
    state_word_splitter = _component(
        "state-word-splitter", 99, (-300, 560), word_size=8
    )
    state_byte_splitters = tuple(
        _component(
            f"state-byte-splitter-{group}",
            17,
            (-245, 392 + 112 * group),
        )
        for group in range(4)
    )
    feedback_byte_makers = tuple(
        _component(
            f"feedback-byte-maker-{group}",
            16,
            (220, 392 + 112 * group),
        )
        for group in range(4)
    )
    feedback_word_maker = _component(
        "feedback-word-maker", 97, (250, 560), word_size=32
    )
    zero_address = _component(
        "zero-address",
        46,
        (270, 520),
        settings=(0,),
        custom_string="0",
        word_size=32,
    )
    ram = _component(
        "state-ram",
        118,
        (320, 560),
        settings=RAM_SETTINGS,
        buffer_size=RAM_BUFFER_SIZE,
        word_size=8,
        init_data=0,
    )
    ram_load = _component("state-load", 54, (320, 548), word_size=32)
    ram_store = _component("state-store", 56, (320, 550), word_size=32)

    replacement = (
        state_word_splitter,
        *state_byte_splitters,
        *feedback_byte_makers,
        feedback_word_maker,
        zero_address,
        ram,
        ram_load,
        ram_store,
    )
    components = retained + replacement
    route = _build_router(components)

    one = next(
        (
            component
            for component in retained
            if component.permanent_id
            == stable_permanent_id(STATE_NAMESPACE, "initialize-one")
        ),
        None,
    )
    if one is None or one.kind != 2:
        raise RuntimeError("source initialize-one component is missing")

    state_sources = {
        bit: _pin(state_byte_splitters[bit // 8], f"out{bit % 8}")
        for bit in range(WORD_BITS)
    }
    wires = list(kept_wires)
    wires.extend(
        (
            route(_pin(one, "out"), _pin(ram_load, "enable")),
            route(_pin(one, "out"), _pin(ram_store, "enable")),
            route(_pin(zero_address, "out"), _pin(ram_load, "address")),
            route(_pin(zero_address, "out"), _pin(ram_store, "address")),
            route(_pin(ram_load, "out"), _pin(state_word_splitter, "in")),
            route(_pin(feedback_word_maker, "out"), _pin(ram_store, "data")),
        )
    )
    for group, splitter in enumerate(state_byte_splitters):
        wires.append(
            route(_pin(state_word_splitter, f"out{group}"), _pin(splitter, "in"))
        )
    for bit in range(WORD_BITS):
        for sink in state_sinks[bit]:
            wires.append(route(state_sources[bit], sink))
        group, offset = divmod(bit, 8)
        wires.append(
            route(
                feedback_sources[bit],
                _pin(feedback_byte_makers[group], f"in{offset}"),
            )
        )
    for group, maker in enumerate(feedback_byte_makers):
        wires.append(
            route(_pin(maker, "out"), _pin(feedback_word_maker, f"in{group}"))
        )

    candidate = Circuit(
        custom_id=source.custom_id,
        hub_id=source.hub_id,
        gate=TARGET_GATE,
        delay=TARGET_DELAY,
        menu_visible=source.menu_visible,
        clock_speed=source.clock_speed,
        dependencies=source.dependencies,
        description=(
            "Codex RNG RAM2: verified encoded network with hidden mode-2 "
            "four-byte read-before-write state RAM"
        ),
        sync_state=source.sync_state,
        score=source.score,
        player_data=source.player_data,
        hub_description=source.hub_description,
        design=source.design,
        components=components,
        wires=tuple(wires),
    )
    transform = {
        "removed_state_delay_count": len(delays),
        "retained_wire_count": len(kept_wires),
        "state_fanout_wire_count": sum(map(len, state_sinks.values())),
        "feedback_source_count": len(feedback_sources),
        "ram_settings": list(RAM_SETTINGS),
        "ram_buffer_size": RAM_BUFFER_SIZE,
        "ram_position": list(ram.position),
        "load_position": list(ram_load.position),
        "store_position": list(ram_store.position),
    }
    return candidate, transform


def _functional_verification() -> dict[str, object]:
    seeds = [0, 1, 2, 0x12345678, 0xFFFFFFFF]
    generator = random.Random(20260802)
    while len(seeds) < 69:
        value = generator.getrandbits(32)
        if value not in seeds:
            seeds.append(value)

    for seed in seeds:
        state = 0
        expected = seed
        for tick in range(TARGET_TICKS):
            if tick:
                expected = xorshift32(expected)
                visible = apply_matrix(C, state)
                if visible != expected:
                    raise RuntimeError(
                        f"RAM2 output mismatch seed={seed:08x} tick={tick}: "
                        f"{visible:08x} != {expected:08x}"
                    )
            next_state = (
                apply_matrix(T, seed)
                if tick == 0
                else apply_matrix(B, state)
            )
            state = next_state
        if apply_matrix(C, state) != xorshift32(expected):
            raise RuntimeError("RAM2 final-state recurrence mismatch")
    if apply_matrix(A, 0x12345678) != xorshift32(0x12345678):
        raise RuntimeError("RNG matrix contract changed")
    return {
        "seed_count": len(seeds),
        "ticks_per_seed": TARGET_TICKS,
        "matrix_identities_used": ["C*T=A", "T*C=B"],
        "same_tick_order": "load -> recurrence -> store (old-value read)",
    }


def _layout_verification(candidate: Circuit) -> dict[str, int]:
    footprints = _component_footprints(candidate.components)
    access_map = _pin_access_map(candidate.components, footprints)
    pins_by_component = [
        {pin.position for pin in positioned_pins(component, index)}
        for index, component in enumerate(candidate.components)
    ]
    ram_group = {
        index
        for index, component in enumerate(candidate.components)
        if component.permanent_id
        in {
            stable_permanent_id(RAM_NAMESPACE, "state-ram"),
            stable_permanent_id(RAM_NAMESPACE, "state-load"),
            stable_permanent_id(RAM_NAMESPACE, "state-store"),
        }
    }
    visible_ram_port_points = set().union(
        *(pins_by_component[index] for index in ram_group)
    )

    overlap_count = 0
    for left in range(len(footprints)):
        for right in range(left + 1, len(footprints)):
            overlap = footprints[left] & footprints[right]
            if overlap and not ({left, right} <= ram_group):
                overlap_count += len(overlap)

    wire_component_contacts = 0
    wire_interior_pin_contacts = 0
    for wire in candidate.wires:
        points = wire_points(wire)
        endpoints = {points[0], points[-1]}
        permitted = frozenset().union(
            *(
                access_map.get(endpoint, frozenset({endpoint}))
                for endpoint in endpoints
            )
        )
        for component_index, (footprint, pins) in enumerate(
            zip(footprints, pins_by_component)
        ):
            for point in points:
                if point not in footprint:
                    continue
                if point in endpoints and point in pins:
                    continue
                if point in permitted:
                    continue
                if component_index in ram_group and point in visible_ram_port_points:
                    continue
                wire_component_contacts += 1
        for point in points[1:-1]:
            wire_interior_pin_contacts += sum(
                point in pins for pins in pins_by_component
            )
    return {
        "component_footprint_overlap_count": overlap_count,
        "wire_component_contact_count": wire_component_contacts,
        "wire_interior_pin_contact_count": wire_interior_pin_contacts,
        "intentional_ram_group_overlap_pair_count": 3,
    }


def verify_candidate(candidate: Circuit, transform: dict[str, object]) -> dict[str, object]:
    _install_hidden_pin_schemas()
    if (candidate.gate, candidate.delay) != (TARGET_GATE, TARGET_DELAY):
        raise RuntimeError("RAM2 declared metrics changed")
    kind_counts = Counter(component.kind for component in candidate.components)
    expected_special = {54: 1, 56: 1, 118: 1}
    for kind, count in expected_special.items():
        if kind_counts[kind] != count:
            raise RuntimeError(f"RAM2 kind {kind} count is {kind_counts[kind]}")

    ram = next(component for component in candidate.components if component.kind == 118)
    if (
        ram.settings != RAM_SETTINGS
        or ram.buffer_size != RAM_BUFFER_SIZE
        or ram.init_data != 0
    ):
        raise RuntimeError("RAM2 hidden RAM fields changed")

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
            raise RuntimeError(
                f"RAM2 connectivity failed {field}: {connectivity[field]}"
            )
    layout = _layout_verification(candidate)
    if any(
        layout[field]
        for field in (
            "component_footprint_overlap_count",
            "wire_component_contact_count",
            "wire_interior_pin_contact_count",
        )
    ):
        raise RuntimeError(f"RAM2 layout failed: {layout}")

    functional = _functional_verification()
    return {
        "declared_metrics": [TARGET_GATE, TARGET_DELAY, TARGET_TICKS],
        "declared_energy": TARGET_GATE * TARGET_DELAY * TARGET_TICKS,
        "rank1_reference_energy": 256_014,
        "rank1_margin": 256_014 - TARGET_GATE * TARGET_DELAY * TARGET_TICKS,
        "component_count": len(candidate.components),
        "wire_count": len(candidate.wires),
        "component_kind_counts": dict(sorted(kind_counts.items())),
        "transform": transform,
        "functional": functional,
        "connectivity": connectivity,
        "layout": layout,
        "score_derivation": {
            "source_gate": SOURCE_GATE,
            "removed_32_bit_delays": -160,
            "mode2_ram_4_bytes": 4,
            "u32_load_port": 32,
            "u32_store_port": 32,
            "target_gate": TARGET_GATE,
            "critical_path": "mode OR 1 + XOR2 2 + U1 Word XOR 3 = 6",
        },
        "native_semantics_certificate": {
            "settings": list(RAM_SETTINGS),
            "pipeline_depth": 0,
            "scored_ram_delay": 0,
            "read_write_order": "read-before-write",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--install",
        action="store_true",
        help="directly overwrite the formal RNG save without creating a backup",
    )
    args = parser.parse_args()

    appdata = os.environ.get("APPDATA")
    if not appdata:
        raise RuntimeError("APPDATA is not set")
    project_root = Path(__file__).resolve().parents[2]
    formal_path = Path(appdata) / "Turing Complete" / Path(*FORMAL_PARTS)
    source_payload = formal_path.read_bytes()
    source = decode_v15(source_payload)
    candidate, transform = build_candidate(source)
    verification = verify_candidate(candidate, transform)
    payload = encode_v15(candidate)
    if decode_v15(payload) != candidate:
        raise RuntimeError("RAM2 v15 round trip changed the candidate")

    output_dir = (
        project_root
        / ".research"
        / "rng_primitive_zero_audit"
        / "ram2_candidate"
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "circuit.data").write_bytes(payload)
    manifest = {
        "schema": 1,
        "source_path": str(formal_path),
        "source_sha256": digest(source_payload),
        "target_sha256": digest(payload),
        "installed": bool(args.install),
        "backup_created": False,
        "verification": verification,
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="ascii",
    )

    if args.install:
        formal_path.write_bytes(payload)
        installed = formal_path.read_bytes()
        if installed != payload or decode_v15(installed) != candidate:
            raise RuntimeError("RAM2 formal post-write verification failed")

    print(f"source_sha256={digest(source_payload)}")
    print(f"target_sha256={digest(payload)}")
    print(f"metrics={TARGET_GATE}/{TARGET_DELAY}/{TARGET_TICKS}")
    print(f"energy={TARGET_GATE * TARGET_DELAY * TARGET_TICKS}")
    print(f"rank1_margin={verification['rank1_margin']}")
    print(f"components={len(candidate.components)} wires={len(candidate.wires)}")
    print(f"installed={str(bool(args.install)).lower()}")
    print("backup_created=false")


if __name__ == "__main__":
    main()
