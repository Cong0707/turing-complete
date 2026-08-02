"""Build and verify the split B/C RNG RAM candidate.

This research candidate keeps the existing dual-mode B recurrence network, but
changes its first layer to cheap U1 Word XORs and its final layer to Bit XORs.
The C-only depth-two outputs are rebuilt as an independent q-only U1 Word-XOR
network. That removes the architecture-input path from their first layer. The
native local B/C data delays are five and four; switched-input control makes
the whole-circuit scored delay ten.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path

from tc_save_lab.analysis import wire_points
from tc_save_lab.builder import stable_permanent_id
from tc_save_lab.codec import decode_v15, encode_v15
from tc_save_lab.model import Circuit, Component
from tc_save_lab.pins import analyze_connectivity, positioned_pins
from tc_save_lab.sprite_geometry import (
    DEFAULT_COMPONENT_SPRITE_ROOT,
    audit_sprite_geometry,
)
from tc_save_lab import rng_encoded_asic as encoded
from tc_save_lab import rng_ram_asic as ram_asic


TARGET_GATE = 191
TARGET_DELAY = 10
TARGET_CYCLES = 66
RAM_BUFFER_SIZE = 8
RESEARCH_KEY = "research/rng-control-simplify-191"
ENCODED_KEY = "architecture/codex-rng-encoded"
RAM_KEY = "architecture/codex-rng-ram2"

# Exact optimum q-pair cover for the 15 C-only rows of weight three or four.
C_PAIR_FORMS = frozenset(
    int(value, 16)
    for value in """
00020001 00040002 00080004 00100008 00200010
00400020 00800040 01000080 02000100 04000200
08000400 10000800 20001000 40002000 80004000
""".split()
)


def _pin(component: Component, name: str) -> tuple[int, int]:
    matches = [pin.position for pin in positioned_pins(component) if pin.name == name]
    if len(matches) != 1:
        raise RuntimeError(f"component kind {component.kind} has no unique pin {name}")
    return matches[0]


def _gate_id(gate: encoded.XorGate) -> int:
    return stable_permanent_id(
        ENCODED_KEY,
        f"xor-depth-{gate.depth}-{gate.output:08x}",
    )


def _state_sources(components: tuple[Component, ...]) -> dict[int, tuple[int, int]]:
    by_id = {component.permanent_id: component for component in components}
    splitters = tuple(
        by_id[stable_permanent_id(RAM_KEY, f"state-byte-splitter-{group}")]
        for group in range(4)
    )
    return {
        bit: _pin(splitters[bit // 8], f"out{bit % 8}")
        for bit in range(encoded.WORD_BITS)
    }


def _selected_c_partition(row: int) -> tuple[int, int]:
    matches = tuple(
        partition
        for partition in encoded._pair_partitions(row)
        if all(form.bit_count() == 1 or form in C_PAIR_FORMS for form in partition)
    )
    if len(matches) != 1:
        raise RuntimeError(
            f"C row {row:08x} does not have one certified selected partition: {matches}"
        )
    return matches[0]


def build_candidate() -> Circuit:
    base = ram_asic.build_rng_ram_asic()
    gate_by_id = {_gate_id(gate): gate for gate in encoded.GATES}

    changed_components: list[Component] = []
    for component in base.components:
        gate = gate_by_id.get(component.permanent_id)
        if gate is not None:
            if gate.depth == 1:
                component = replace(component, kind=23, word_size=1)
            elif gate.output in encoded.B:
                component = replace(component, kind=10, word_size=1)
            elif gate.output in encoded.C:
                component = replace(component, kind=23, word_size=1)
            else:  # pragma: no cover - certificate invariant
                raise RuntimeError(f"unclassified depth-two row {gate.output:08x}")
        if component.kind == 118:
            component = replace(component, buffer_size=RAM_BUFFER_SIZE)
        changed_components.append(component)

    c_pair_components = {
        form: Component(
            kind=23,
            position=(-20, 820 + index * 14),
            rotation=0,
            permanent_id=stable_permanent_id(RESEARCH_KEY, f"c-pair-{form:08x}"),
            word_size=1,
        )
        for index, form in enumerate(sorted(C_PAIR_FORMS))
    }
    components = (*changed_components, *c_pair_components.values())
    components_by_id = {component.permanent_id: component for component in components}

    c_final_gates = tuple(
        gate for gate in encoded.GATES if gate.depth == 2 and gate.output in encoded.C
    )
    c_final_input_points = {
        _pin(components_by_id[_gate_id(gate)], pin_name)
        for gate in c_final_gates
        for pin_name in ("in0", "in1")
    }
    wires = [
        wire
        for wire in base.wires
        if wire_points(wire)[-1] not in c_final_input_points
    ]

    route = ram_asic._build_router(components)
    state_sources = _state_sources(components)
    pair_sources: dict[int, tuple[int, int]] = {}
    for form, component in c_pair_components.items():
        left_bit, right_bit = encoded.bits(form)
        wires.append(route(state_sources[left_bit], _pin(component, "in0")))
        wires.append(route(state_sources[right_bit], _pin(component, "in1")))
        pair_sources[form] = _pin(component, "out")

    for gate in c_final_gates:
        component = components_by_id[_gate_id(gate)]
        for pin_name, form in zip(("in0", "in1"), _selected_c_partition(gate.output)):
            if form.bit_count() == 1:
                source = state_sources[encoded.bits(form)[0]]
            else:
                source = pair_sources[form]
            wires.append(route(source, _pin(component, pin_name)))

    return Circuit(
        gate=TARGET_GATE,
        delay=TARGET_DELAY,
        description=(
            "Codex RNG RAM8 split B/C: dual-mode B word/bit network and "
            "independent q-only C word/word network; switched input control "
            "sets the full scored delay"
        ),
        components=tuple(components),
        wires=tuple(wires),
    )


def _live_sprite_summary(candidate: Circuit) -> dict[str, int | list[int]]:
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


def verify_candidate(candidate: Circuit) -> dict[str, object]:
    if (candidate.gate, candidate.delay) != (TARGET_GATE, TARGET_DELAY):
        raise RuntimeError("candidate metric declaration changed")

    counts = Counter(component.kind for component in candidate.components)
    expected_counts = {
        2: 1,
        3: 1,
        7: 47,
        10: 19,
        13: 1,
        16: 8,
        17: 8,
        23: 57,
        46: 1,
        54: 1,
        56: 1,
        62: 1,
        70: 1,
        97: 2,
        99: 2,
        118: 1,
    }
    for kind, expected in expected_counts.items():
        if counts[kind] != expected:
            raise RuntimeError(
                f"component kind {kind} count {counts[kind]} != {expected}"
            )
    backing_ram = next(component for component in candidate.components if component.kind == 118)
    if backing_ram.buffer_size != RAM_BUFFER_SIZE:
        raise RuntimeError("RAM buffer size is not the native-stable eight bytes")

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

    layout = ram_asic._layout_safety(candidate)
    for field in (
        "wire_component_contact_count",
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

    first_stream = ram_asic._verify_all_runtime_streams(candidate)
    cost_terms = {
        "mode_or": 47,
        "b_final_bit_xor": 19 * 3,
        "u1_word_xor": 57,
        "ready_delay_and_not": 6,
        "ram_backing": RAM_BUFFER_SIZE,
        "ram_load": RAM_BUFFER_SIZE,
        "ram_store": RAM_BUFFER_SIZE,
    }
    if sum(cost_terms.values()) != TARGET_GATE:
        raise RuntimeError(f"cost ledger does not sum to {TARGET_GATE}: {cost_terms}")

    return {
        "leaderboard_tuple": [TARGET_GATE, TARGET_DELAY, TARGET_CYCLES],
        "energy": TARGET_GATE * TARGET_DELAY * TARGET_CYCLES,
        "component_count": len(candidate.components),
        "wire_count": len(candidate.wires),
        "component_kind_counts": dict(sorted(counts.items())),
        "cost_terms": cost_terms,
        "delay_certificate": {
            "local_b_data_path": "mode OR 1 + U1 Word XOR 2 + Bit XOR 2 = 5",
            "local_c_data_path": "U1 Word XOR 2 + U1 Word XOR 2 = 4",
            "full_scored_delay": (
                "10: native Architecture Input switched-control propagation "
                "includes the ready-control arrival"
            ),
        },
        "ram_settings": list(backing_ram.settings),
        "ram_buffer_size": backing_ram.buffer_size,
        "runtime_test_seed_count": 256,
        "runtime_tick_count": 256 * TARGET_CYCLES,
        "first_seed_prefix": [f"{value:08x}" for value in first_stream[:3]],
        "connectivity": connectivity,
        "layout": layout,
        "live_sprite_layout": live_sprite,
    }


def main() -> None:
    output_root = Path(__file__).resolve().parent / "candidate"
    output_root.mkdir(parents=True, exist_ok=True)
    candidate = build_candidate()
    verification = verify_candidate(candidate)
    payload = encode_v15(candidate)
    if decode_v15(payload) != candidate:
        raise RuntimeError("v15 round trip changed the candidate")
    (output_root / "circuit.data").write_bytes(payload)
    result = {
        "schema": 1,
        "level": "rng",
        "strategy": "split B/C RAM8 encoded-state network",
        "sha256": sha256(payload).hexdigest(),
        "format_version": 15,
        **verification,
    }
    (output_root / "result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
