"""Derive and verify the normal no-RAM 396/9/66 RNG candidate.

The checked-in encoded-state generator already has a two-XOR-layer steady
network.  Its declared delay 10 is caused only by the load-phase polarity:

    ready Delay(4) -> NOT(1) -> Architecture Input -> OR(1) -> XOR(4)

Initialize the phase Delay to one and feed it a zero instead.  The phase output
can then drive Architecture Input directly, while the existing NOT drives the
Architecture Output.  After the first edge the phase state becomes zero and
stays there.  Gate count and cycle count do not change; the longest seed and
feedback paths both become 9.

This research derivation writes only beside itself.  It never reads or writes
the live save and never launches the game.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
import random
import sys


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from tc_save_lab.analysis import wire_points  # noqa: E402
from tc_save_lab.codec import decode_v15, encode_v15  # noqa: E402
from tc_save_lab.pins import analyze_connectivity  # noqa: E402
from tc_save_lab.sprite_geometry import (  # noqa: E402
    DEFAULT_COMPONENT_SPRITE_ROOT,
    audit_sprite_geometry,
)
from tc_save_lab import rng_encoded_asic as encoded  # noqa: E402
from tc_save_lab import simulate  # noqa: E402


HERE = Path(__file__).resolve().parent
OUTPUT_DATA = HERE / "phase_reversed_396_9_66.data"
OUTPUT_JSON = HERE / "phase_reversed_396_9_66.json"


def _pin(component, name: str) -> tuple[int, int]:
    return encoded._pin(component, name)


def _wire_matches(wire, left: tuple[int, int], right: tuple[int, int]) -> bool:
    points = wire_points(wire)
    return {points[0], points[-1]} == {left, right}


def derive():
    base = encoded.build_rng_encoded_asic()
    components = list(base.components)
    role_ids = {
        role: encoded.stable_permanent_id("architecture/codex-rng-encoded", role)
        for role in (
            "level-input",
            "level-output",
            "initialize-one",
            "ready-delay",
            "not-ready",
        )
    }
    by_id = {component.permanent_id: index for index, component in enumerate(components)}
    indices = {role: by_id[value] for role, value in role_ids.items()}

    input_component = components[indices["level-input"]]
    output_component = components[indices["level-output"]]
    constant = components[indices["initialize-one"]]
    ready = components[indices["ready-delay"]]
    inverter = components[indices["not-ready"]]
    if (constant.kind, ready.kind, ready.init_data, inverter.kind) != (2, 13, 0, 3):
        raise RuntimeError("encoded RNG phase scaffold changed")

    components[indices["initialize-one"]] = replace(constant, kind=1)
    components[indices["ready-delay"]] = replace(ready, init_data=1)
    components = tuple(components)

    ready_out = _pin(ready, "out")
    not_out = _pin(inverter, "out")
    input_control = _pin(input_component, "control")
    output_control = _pin(output_component, "control")
    remove_pairs = (
        (not_out, input_control),
        (ready_out, output_control),
    )
    removed = []
    retained = []
    for wire in base.wires:
        if any(_wire_matches(wire, *pair) for pair in remove_pairs):
            removed.append(wire)
        else:
            retained.append(wire)
    if len(removed) != 2:
        raise RuntimeError(f"expected two phase-control wires, removed {len(removed)}")

    # Off and On use the same one-cell footprint.  Extend only the local copy
    # of the generator's conservative router table.
    encoded._FOOTPRINT_BOXES.setdefault(1, encoded._FOOTPRINT_BOXES[2])
    route = encoded._build_router(components)
    wires = tuple(
        (
            *retained,
            route(ready_out, input_control),
            route(not_out, output_control),
        )
    )
    return replace(
        base,
        gate=396,
        delay=9,
        description=(
            "Codex RNG ASIC: phase-reversed encoded depth-two XOR network; "
            "normal components, no RAM"
        ),
        components=components,
        wires=wires,
    )


def _verification_seeds() -> tuple[int, ...]:
    values = [0, 1, 2, 0x12345678, 0xFFFFFFFF]
    generator = random.Random(202608030917)
    while len(values) < 256:
        candidate = generator.getrandbits(32)
        if candidate not in values:
            values.append(candidate)
    return tuple(values)


def verify(circuit) -> dict[str, object]:
    payload = encode_v15(circuit)
    if decode_v15(payload) != circuit:
        raise RuntimeError("phase-reversed candidate failed v15 round trip")

    counts = Counter(component.kind for component in circuit.components)
    expected = {1: 1, 2: 0, 3: 1, 7: 47, 10: 42, 13: 33, 23: 19}
    for kind, count in expected.items():
        if counts[kind] != count:
            raise RuntimeError(f"kind {kind} count {counts[kind]} != {count}")
    delay_initial = Counter(
        component.init_data for component in circuit.components if component.kind == 13
    )
    if delay_initial != {0: 32, 1: 1}:
        raise RuntimeError(f"unexpected Delay initial states: {dict(delay_initial)}")

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
            raise RuntimeError(f"connectivity {field}={connectivity[field]}")

    layout = encoded._layout_safety(circuit)
    if any(layout.values()):
        raise RuntimeError(f"conservative layout failure: {layout}")
    sprite = audit_sprite_geometry(circuit, DEFAULT_COMPONENT_SPRITE_ROOT)
    internal_collisions = tuple(
        collision
        for collision in sprite.wire_collisions
        if collision.component_kind not in {62, 70}
    )
    if (
        sprite.unsupported_component_kinds
        or sprite.component_overlap_cells
        or internal_collisions
        or sprite.wire_interior_pin_contacts
    ):
        raise RuntimeError(
            "sprite layout failure: "
            f"unsupported={sprite.unsupported_component_kinds}, "
            f"overlap={len(sprite.component_overlap_cells)}, "
            f"internal_collisions={len(internal_collisions)}, "
            f"pin_contacts={len(sprite.wire_interior_pin_contacts)}"
        )

    compiled = simulate._compile(circuit)
    seeds = _verification_seeds()
    first_prefix: list[str] = []
    total_ticks = 0
    for seed_index, seed in enumerate(seeds):
        memory = simulate.initial_clocked_memory(circuit)
        expected_value = seed
        output_count = 0
        for tick in range(66):
            result = simulate._simulate_clocked_tick(
                circuit,
                compiled=compiled,
                inputs={"Seed": seed},
                memory=memory,
            )
            memory = result.memory
            total_ticks += 1
            if tick == 0:
                if result.outputs:
                    raise RuntimeError(f"seed {seed:08x} emitted during load")
                encoded_state = encoded._encoded_memory(circuit, memory)
                wanted_state = encoded.apply_matrix(encoded.T, seed)
                if encoded_state != wanted_state:
                    raise RuntimeError(f"seed {seed:08x} load state mismatch")
                continue
            expected_value = encoded.xorshift32(expected_value)
            if result.outputs != {"RNG output": expected_value}:
                raise RuntimeError(
                    f"seed {seed:08x} tick {tick}: "
                    f"expected {expected_value:08x}, got {result.outputs}"
                )
            encoded_state = encoded._encoded_memory(circuit, memory)
            wanted_state = encoded.apply_matrix(encoded.T, expected_value)
            if encoded_state != wanted_state:
                raise RuntimeError(f"seed {seed:08x} tick {tick} state mismatch")
            output_count += 1
            if seed_index == 1 and len(first_prefix) < 3:
                first_prefix.append(f"{expected_value:08x}")
        if output_count != 65:
            raise RuntimeError(f"seed {seed:08x} produced {output_count} outputs")

    return {
        "schema": 1,
        "status": "offline-verified-candidate",
        "artifact": OUTPUT_DATA.name,
        "sha256": sha256(payload).hexdigest(),
        "leaderboard_tuple_prediction": [396, 9, 66],
        "energy_prediction": 396 * 9 * 66,
        "reference_energy_431_9_66": 431 * 9 * 66,
        "energy_margin": (431 - 396) * 9 * 66,
        "normal_components_only": True,
        "uses_ram": False,
        "phase_reversal": {
            "tick0": "phase=1: Architecture Input enabled, output disabled",
            "tick1_plus": "phase=0: Architecture Input Z, output enabled",
            "phase_delay_init": 1,
            "phase_delay_next": 0,
            "constant_kind": 1,
        },
        "path_certificate": {
            "state_to_state": "Delay 4 + mode OR 1 + depth-two XOR 4 = 9",
            "phase_to_seed_state": "Delay 4 + mode OR 1 + depth-two XOR 4 = 9",
            "state_to_output": "Delay 4 + mode OR 1 + depth-two XOR 4 = 9",
            "phase_to_output_enable": "Delay 4 + NOT 1 = 5",
        },
        "component_kind_counts": dict(sorted(counts.items())),
        "verified_seed_count": len(seeds),
        "verified_tick_count": total_ticks,
        "first_seed_prefix": first_prefix,
        "connectivity": connectivity,
        "layout": layout,
        "sprite_layout": {
            "unsupported_component_kinds": list(sprite.unsupported_component_kinds),
            "component_overlap_cell_count": len(sprite.component_overlap_cells),
            "internal_wire_collision_count": len(internal_collisions),
            "wire_interior_pin_contact_count": len(sprite.wire_interior_pin_contacts),
        },
        "evidence_boundary": (
            "gate/delay are structurally predicted from reviewed 2.1.281 costs; "
            "game and server recomputation remain required"
        ),
    }


def main() -> None:
    circuit = derive()
    result = verify(circuit)
    payload = encode_v15(circuit)
    OUTPUT_DATA.write_bytes(payload)
    OUTPUT_JSON.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(
        json.dumps(
            {
                key: result[key]
                for key in (
                    "status",
                    "leaderboard_tuple_prediction",
                    "energy_prediction",
                    "energy_margin",
                    "verified_seed_count",
                    "verified_tick_count",
                    "sprite_layout",
                )
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
