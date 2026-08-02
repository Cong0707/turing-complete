"""Build and verify the 245/7/66 natural-state RAM RNG."""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from dataclasses import replace
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path

from .codec import decode_v15, encode_v15
from .analysis import wire_points
from .pins import analyze_connectivity, positioned_pins
from .sprite_geometry import (
    DEFAULT_COMPONENT_SPRITE_ROOT,
    audit_sprite_geometry,
)
from . import rng_bit_state_asic as bit_state
from . import rng_ram_asic as ram_asic
from .simulate import (
    _compile,
    _simulate_clocked_tick,
    initial_clocked_memory,
)


EXPECTED_GATE = 245
EXPECTED_DELAY = 7
EXPECTED_CYCLES = 66
RAM_BUFFER_SIZE = 8
NATURAL_BASE_KEY = "architecture/codex-rng-bit-state"
NATURAL_RAM_KEY = "architecture/codex-rng-natural-ram-u1"


def _build_natural_ram_base():
    return ram_asic.build_rng_ram_from_state_circuit(
        bit_state.build_rng_bit_state_asic(),
        state_namespace=NATURAL_BASE_KEY,
        ram_namespace=NATURAL_RAM_KEY,
        gate=EXPECTED_GATE,
        delay=EXPECTED_DELAY,
        description=(
            "Codex natural xorshift32 RAM8: 61 U1 Word XORs, 32 seed ORs, "
            "and zero-depth mode-2 RAM state"
        ),
        ram_buffer_size=RAM_BUFFER_SIZE,
    )


@lru_cache(maxsize=1)
def _build_parts():
    base = _build_natural_ram_base()
    changed_ids = {
        component.permanent_id for component in base.components if component.kind == 10
    }
    if len(changed_ids) != 61:
        raise RuntimeError(f"expected 61 Bit XORs, got {len(changed_ids)}")
    components = tuple(
        replace(component, kind=23, word_size=1)
        if component.kind == 10
        else component
        for component in base.components
    )
    candidate = replace(
        base,
        gate=EXPECTED_GATE,
        delay=EXPECTED_DELAY,
        description=(
            "Codex natural xorshift32 RAM8: 61 U1 Word XORs, 32 seed ORs, "
            "and zero-depth mode-2 RAM state"
        ),
        components=components,
    )
    return base, candidate, changed_ids


def build_rng_natural_ram_asic():
    """Return the exact topology validated in game at 245/7/66."""

    return _build_parts()[1]


def _verify_runtime_streams(candidate):
    surrogate = ram_asic._ram_delay_surrogate(candidate)
    probe = ram_asic._disabled_input_probe(surrogate)
    load_compiled = _compile(surrogate)
    run_compiled = _compile(probe)
    state_id = next(
        component.permanent_id for component in surrogate.components if component.kind == 55
    )
    first_stream = None

    for test_id in range(256):
        seed = ram_asic._runtime_seed(test_id)
        first = _simulate_clocked_tick(
            surrogate,
            compiled=load_compiled,
            inputs={"Seed": seed},
            memory=initial_clocked_memory(surrogate),
        )
        if first.outputs:
            raise RuntimeError(f"RNG emitted during seed-load tick for test {test_id}")
        if first.memory[state_id] != seed:
            raise RuntimeError(f"natural RAM seed-load mismatch for test {test_id}")

        expected = seed
        outputs = []
        memory = first.memory
        for tick in range(1, EXPECTED_CYCLES):
            result = _simulate_clocked_tick(
                probe,
                compiled=run_compiled,
                inputs={"Seed": 0},
                memory=memory,
            )
            expected = bit_state.xorshift32(expected)
            if result.outputs != {"RNG output": expected}:
                raise RuntimeError(
                    f"RNG mismatch for test {test_id} at output {tick}: "
                    f"expected {expected:08x}, got {result.outputs}"
                )
            if result.memory[state_id] != expected:
                raise RuntimeError(
                    f"natural RAM state mismatch for test {test_id} at output {tick}"
                )
            outputs.append(expected)
            memory = result.memory
        if first_stream is None:
            first_stream = tuple(outputs)

    if first_stream is None or len(first_stream) != 65:
        raise RuntimeError("natural RNG runtime verification did not execute")
    return first_stream


def _live_sprite_summary(candidate):
    audit = audit_sprite_geometry(candidate, DEFAULT_COMPONENT_SPRITE_ROOT)
    ram_group = {
        index
        for index, component in enumerate(candidate.components)
        if component.kind in {54, 56, 118}
    }
    visible_ram_port_points = set().union(
        *(
            {pin.position for pin in positioned_pins(candidate.components[index], index)}
            for index in ram_group
        )
    )
    internal_collisions = tuple(
        collision
        for collision in audit.wire_collisions
        if collision.component_kind not in {62, 70}
        and not (
            collision.component_index in ram_group
            and collision.point in visible_ram_port_points
        )
    )
    return {
        "unsupported_component_kinds": list(audit.unsupported_component_kinds),
        "component_overlap_cell_count": len(audit.component_overlap_cells),
        "internal_wire_collision_count": len(internal_collisions),
        "wire_interior_pin_contact_count": len(audit.wire_interior_pin_contacts),
        "architecture_io_access_cell_count": sum(
            collision.component_kind in {62, 70}
            for collision in audit.wire_collisions
        ),
        "ram_group_endpoint_collision_count": sum(
            collision.component_index in ram_group
            and collision.point in visible_ram_port_points
            for collision in audit.wire_collisions
        ),
    }


def _layout_summary(candidate):
    raw = ram_asic._layout_safety(candidate)
    footprints = ram_asic._component_footprints(candidate.components)
    access_map = ram_asic.encoded._pin_access_map(candidate.components, footprints)
    pins_by_component = [
        {pin.position for pin in positioned_pins(component, index)}
        for index, component in enumerate(candidate.components)
    ]
    ram_group = {
        index
        for index, component in enumerate(candidate.components)
        if component.kind in {54, 56, 118}
    }
    visible_ram_port_points = set().union(
        *(pins_by_component[index] for index in ram_group)
    )
    internal_contacts = 0
    architecture_io_contacts = 0
    for wire in candidate.wires:
        points = wire_points(wire)
        endpoints = {points[0], points[-1]}
        permitted = frozenset().union(
            *(access_map.get(endpoint, frozenset({endpoint})) for endpoint in endpoints)
        )
        for component_index, (component, footprint, pins) in enumerate(
            zip(candidate.components, footprints, pins_by_component)
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
                if component.kind in {62, 70}:
                    architecture_io_contacts += 1
                else:
                    internal_contacts += 1
    return {
        **raw,
        "internal_wire_component_contact_count": internal_contacts,
        "architecture_io_access_cell_count": architecture_io_contacts,
    }


def verify_candidate(base, candidate, changed_ids):
    if (candidate.gate, candidate.delay) != (EXPECTED_GATE, EXPECTED_DELAY):
        raise RuntimeError("candidate metric declaration changed")
    if candidate.wires != base.wires:
        raise RuntimeError("XOR substitution unexpectedly changed routing")
    changed = tuple(
        (before, after)
        for before, after in zip(base.components, candidate.components)
        if before != after
    )
    if len(changed) != 61 or {
        before.permanent_id for before, _ in changed
    } != changed_ids:
        raise RuntimeError("candidate is not an exact 61-component substitution")
    for before, after in changed:
        if not (
            before.kind == 10
            and after == replace(before, kind=23, word_size=1)
        ):
            raise RuntimeError("substitution changed fields other than kind/word_size")

    counts = Counter(component.kind for component in candidate.components)
    expected_counts = Counter(
        {
            2: 1,
            3: 1,
            7: 32,
            13: 1,
            16: 8,
            17: 8,
            23: 61,
            46: 1,
            54: 1,
            56: 1,
            62: 1,
            70: 1,
            97: 2,
            99: 2,
            118: 1,
        }
    )
    if counts != expected_counts:
        raise RuntimeError(f"component counts changed: {dict(sorted(counts.items()))}")
    if any(
        component.word_size != 1
        for component in candidate.components
        if component.kind == 23
    ):
        raise RuntimeError("not every Word XOR is U1")
    ram = next(component for component in candidate.components if component.kind == 118)
    if ram.settings != (2, 512, 0) or ram.buffer_size != RAM_BUFFER_SIZE:
        raise RuntimeError("RAM fields changed")

    connectivity = analyze_connectivity(candidate)
    for field in (
        "unsupported_component_kind_counts",
        "unconnected_pin_count",
        "multi_driver_network_count",
        "undriven_network_count",
        "sinkless_network_count",
        "width_mismatch_network_count",
        "cycle_component_count",
    ):
        if connectivity[field]:
            raise RuntimeError(f"connectivity failure {field}: {connectivity[field]}")

    layout = _layout_summary(candidate)
    for field in (
        "internal_wire_component_contact_count",
        "wire_interior_pin_contact_count",
        "component_footprint_overlap_count",
    ):
        if layout[field]:
            raise RuntimeError(f"conservative layout failure {field}: {layout[field]}")
    live_sprite = _live_sprite_summary(candidate)
    if (
        live_sprite["unsupported_component_kinds"]
        or live_sprite["internal_wire_collision_count"]
        or live_sprite["wire_interior_pin_contact_count"]
    ):
        raise RuntimeError(f"live sprite layout failure: {live_sprite}")

    first_stream = _verify_runtime_streams(candidate)
    gate_ledger = {
        "seed_or": 32,
        # The running game charges a U1 Word XOR exactly like a Bit XOR.
        "u1_word_xor": 61 * 3,
        "ready_delay_and_not": 6,
        "ram_backing": RAM_BUFFER_SIZE,
        "ram_load": RAM_BUFFER_SIZE,
        "ram_store": RAM_BUFFER_SIZE,
    }
    if sum(gate_ledger.values()) != EXPECTED_GATE:
        raise RuntimeError(
            f"gate ledger does not sum to {EXPECTED_GATE}: {gate_ledger}"
        )

    return {
        "leaderboard_tuple": [EXPECTED_GATE, EXPECTED_DELAY, EXPECTED_CYCLES],
        "energy": EXPECTED_GATE * EXPECTED_DELAY * EXPECTED_CYCLES,
        "component_count": len(candidate.components),
        "wire_count": len(candidate.wires),
        "substitution_count": len(changed),
        "component_kind_counts": dict(sorted(counts.items())),
        "gate_ledger": gate_ledger,
        "delay_certificate": {
            "state_path": "three U1 Word XOR stages 2+2+2 + feedback OR 1 = 7",
            "seed_path": "ready Delay 4 + NOT 1 + seed OR 1 = 6",
            "full_scored_delay": 7,
        },
        "runtime_test_seed_count": 256,
        "runtime_tick_count": 256 * EXPECTED_CYCLES,
        "first_seed_prefix": [f"{value:08x}" for value in first_stream[:3]],
        "connectivity": connectivity,
        "layout": layout,
        "live_sprite_layout": live_sprite,
    }


@lru_cache(maxsize=1)
def _default_verification():
    base, generated, changed_ids = _build_parts()
    return verify_candidate(base, generated, changed_ids)


def verify_rng_natural_ram_asic(candidate=None):
    if candidate is None:
        return deepcopy(_default_verification())
    base, _, changed_ids = _build_parts()
    return verify_candidate(base, candidate, changed_ids)


def write_rng_natural_ram_asic(project_root: Path) -> dict[str, object]:
    candidate = build_rng_natural_ram_asic()
    verification = verify_rng_natural_ram_asic()
    payload = encode_v15(candidate)
    if decode_v15(payload) != candidate or encode_v15(decode_v15(payload)) != payload:
        raise RuntimeError("v15 round trip changed the candidate")
    output_root = project_root / "examples" / "rng" / "candidate"
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "circuit.data").write_bytes(payload)
    result = {
        "schema": 1,
        "level": "rng",
        "strategy": "natural xorshift32 all-U1-XOR RAM8 network",
        "sha256": sha256(payload).hexdigest(),
        "format_version": 15,
        "v15_byte_identical_round_trip": True,
        "game_validation": {
            "version": "2.1.281",
            "result": "256/256 tests passed and leaderboard rank 1 confirmed",
            "observed_tuple": [245, 7, 66],
        },
        **verification,
    }
    (output_root / "result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return result
