"""Build and verify the all-U1-Word-XOR RNG RAM research candidate.

This is an isolated derivative of the reviewed 191/10 candidate.  The only
topology change is replacing its remaining 19 Bit XOR components with U1 Word
XOR components.  Current live primitive costs make both variants delay two,
while reducing gate cost from three to one.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
import runpy
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from tc_save_lab.codec import decode_v15, encode_v15  # noqa: E402
from tc_save_lab.pins import analyze_connectivity, positioned_pins  # noqa: E402
from tc_save_lab.sprite_geometry import (  # noqa: E402
    DEFAULT_COMPONENT_SPRITE_ROOT,
    audit_sprite_geometry,
)
from tc_save_lab import rng_ram_asic as ram_asic  # noqa: E402


BASE_PATH = PROJECT_ROOT / ".research" / "rng_control_simplify" / "build_candidate.py"
BASE = runpy.run_path(str(BASE_PATH))

TARGET_GATE = 153
TARGET_DELAY = 10
TARGET_CYCLES = 66
RAM_BUFFER_SIZE = 8


def build_candidate():
    base = BASE["build_candidate"]()
    bit_xor_ids = {
        component.permanent_id for component in base.components if component.kind == 10
    }
    if len(bit_xor_ids) != 19:
        raise RuntimeError(f"expected 19 remaining Bit XORs, got {len(bit_xor_ids)}")
    components = tuple(
        replace(component, kind=23, word_size=1)
        if component.kind == 10
        else component
        for component in base.components
    )
    candidate = replace(
        base,
        gate=TARGET_GATE,
        delay=TARGET_DELAY,
        description=(
            "Codex RNG RAM8 split B/C all-U1-Word-XOR network; current XOR "
            "primitive frontier gives U1 Word XOR one gate and two delay"
        ),
        components=components,
    )
    return base, candidate, bit_xor_ids


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


def verify_candidate(base, candidate, changed_ids):
    if (candidate.gate, candidate.delay) != (TARGET_GATE, TARGET_DELAY):
        raise RuntimeError("candidate metric declaration changed")
    if candidate.wires != base.wires:
        raise RuntimeError("XOR substitution unexpectedly changed routing")
    changed = tuple(
        (before, after)
        for before, after in zip(base.components, candidate.components)
        if before != after
    )
    if len(changed) != 19 or {
        before.permanent_id for before, _ in changed
    } != changed_ids:
        raise RuntimeError("candidate is not an exact 19-component substitution")
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
            7: 47,
            13: 1,
            16: 8,
            17: 8,
            23: 76,
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
    gate_ledger = {
        "mode_or": 47,
        "u1_word_xor": 76,
        "ready_delay_and_not": 6,
        "ram_backing": RAM_BUFFER_SIZE,
        "ram_load": RAM_BUFFER_SIZE,
        "ram_store": RAM_BUFFER_SIZE,
    }
    if sum(gate_ledger.values()) != TARGET_GATE:
        raise RuntimeError(f"gate ledger does not sum to {TARGET_GATE}: {gate_ledger}")

    return {
        "leaderboard_tuple": [TARGET_GATE, TARGET_DELAY, TARGET_CYCLES],
        "energy": TARGET_GATE * TARGET_DELAY * TARGET_CYCLES,
        "component_count": len(candidate.components),
        "wire_count": len(candidate.wires),
        "substitution_count": len(changed),
        "component_kind_counts": dict(sorted(counts.items())),
        "gate_ledger": gate_ledger,
        "delay_certificate": {
            "local_b_data_path": "mode OR 1 + U1 Word XOR 2 + U1 Word XOR 2 = 5",
            "local_c_data_path": "U1 Word XOR 2 + U1 Word XOR 2 = 4",
            "full_scored_delay": (
                "10: Architecture Input switched-control propagation adds "
                "the ready-control arrival"
            ),
        },
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
    base, candidate, changed_ids = build_candidate()
    verification = verify_candidate(base, candidate, changed_ids)
    payload = encode_v15(candidate)
    if decode_v15(payload) != candidate or encode_v15(decode_v15(payload)) != payload:
        raise RuntimeError("v15 round trip changed the candidate")
    (output_root / "circuit.data").write_bytes(payload)
    result = {
        "schema": 1,
        "level": "rng",
        "strategy": "all-U1-Word-XOR split B/C RAM8 network",
        "sha256": sha256(payload).hexdigest(),
        "format_version": 15,
        "base_sha256": sha256(encode_v15(base)).hexdigest(),
        "v15_byte_identical_round_trip": True,
        **verification,
    }
    (output_root / "result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
