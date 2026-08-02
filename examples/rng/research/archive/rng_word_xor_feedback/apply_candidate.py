from __future__ import annotations

from collections import Counter
from dataclasses import replace
from hashlib import sha256
from pathlib import Path
import json
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from tc_save_lab.builder import stable_permanent_id
from tc_save_lab.codec import decode_v15, encode_v15
from tc_save_lab.pins import analyze_connectivity, positioned_pins
from tc_save_lab.rng_encoded_asic import (
    B,
    C,
    GATE_BY_OUTPUT,
    _verification_seeds,
    _verify_output_stream,
)
from tc_save_lab.sprite_geometry import (
    DEFAULT_COMPONENT_SPRITE_ROOT,
    audit_sprite_geometry,
    sprite_alpha_cells,
)


BASELINE = (
    PROJECT_ROOT
    / ".research"
    / "rng_cost_injection"
    / "rng-verified-396-10-66.data"
)
LIVE_CIRCUIT = Path(
    r"C:\Users\cong\AppData\Roaming\Turing Complete"
    r"\schematics\architecture\CODEX-RNG\circuit.data"
)
EXPECTED_BASELINE_SHA256 = (
    "844f4a950499cd8823bcee48dffafc4474e3a176225716c65f5d87403026d0c1"
)
TARGET_ROWS = (
    0x00002021,
    0x00004042,
    0x00008808,
    0x00011010,
    0x01088008,
    0x02110010,
    0x04200021,
    0x08008840,
    0x08400042,
    0x10011080,
    0x10800084,
    0x20002101,
    0x21000108,
    0x40004202,
    0x40420002,
    0x42000210,
    0x80000404,
    0x80840004,
    0x84000420,
)
IDENTITY = "architecture/codex-rng-encoded"
BAD_CONNECTIVITY_FIELDS = (
    "unsupported_component_kind_counts",
    "unconnected_pin_count",
    "multi_driver_network_count",
    "undriven_network_count",
    "width_mismatch_network_count",
    "cycle_component_count",
)


def _component_pins(component, index: int) -> tuple[tuple[object, ...], ...]:
    return tuple(
        (pin.name, pin.direction, pin.width, pin.position)
        for pin in positioned_pins(component, index)
    )


def _validate_and_build():
    payload = BASELINE.read_bytes()
    actual_sha256 = sha256(payload).hexdigest()
    if actual_sha256 != EXPECTED_BASELINE_SHA256:
        raise RuntimeError(
            f"refusing unknown baseline {actual_sha256}; "
            f"expected {EXPECTED_BASELINE_SHA256}"
        )

    baseline = decode_v15(payload)
    if (baseline.gate, baseline.delay) != (396, 9):
        raise RuntimeError(
            f"unexpected verified header {baseline.gate}/{baseline.delay}"
        )
    if Counter(component.kind for component in baseline.components)[62] != 1:
        raise RuntimeError("verified baseline must contain exactly one architecture input")
    if Counter(component.kind for component in baseline.components)[70] != 1:
        raise RuntimeError("verified baseline must contain exactly one architecture output")

    target_by_id = {
        stable_permanent_id(IDENTITY, f"xor-depth-2-{row:08x}"): row
        for row in TARGET_ROWS
    }
    if len(target_by_id) != len(TARGET_ROWS):
        raise RuntimeError("target permanent IDs are not unique")

    new_components = []
    changed_indices: list[int] = []
    for index, component in enumerate(baseline.components):
        row = target_by_id.get(component.permanent_id)
        if row is None:
            new_components.append(component)
            continue
        if component.kind != 10 or component.word_size != 1:
            raise RuntimeError(
                f"target {row:08x} is not a U1 bit XOR: "
                f"kind={component.kind}, width={component.word_size}"
            )
        if row not in B or row in C or GATE_BY_OUTPUT[row].depth != 2:
            raise RuntimeError(f"target {row:08x} is not feedback-only depth-two XOR")
        replacement = replace(component, kind=23, word_size=1)
        if _component_pins(component, index) != _component_pins(replacement, index):
            raise RuntimeError(f"pin geometry changed for target {row:08x}")
        new_components.append(replacement)
        changed_indices.append(index)

    if len(changed_indices) != len(TARGET_ROWS):
        found = {
            component.permanent_id
            for component in baseline.components
            if component.permanent_id in target_by_id
        }
        missing = sorted(target_by_id[permanent_id] for permanent_id in target_by_id.keys() - found)
        raise RuntimeError(
            f"found {len(changed_indices)} of {len(TARGET_ROWS)} targets; "
            f"missing={[f'{row:08x}' for row in missing]}"
        )

    candidate = replace(
        baseline,
        gate=358,
        delay=10,
        components=tuple(new_components),
    )
    for index, (old, new) in enumerate(zip(baseline.components, candidate.components)):
        if index in changed_indices:
            if new != replace(old, kind=23, word_size=1):
                raise RuntimeError(f"unexpected replacement at component {index}")
        elif new != old:
            raise RuntimeError(f"non-target component {index} changed")
    if candidate.wires != baseline.wires:
        raise RuntimeError("wire topology changed")

    counts = Counter(component.kind for component in candidate.components)
    if counts[10] != 42 or counts[23] != 19 or counts[62] != 1 or counts[70] != 1:
        raise RuntimeError(f"unexpected candidate component counts: {dict(counts)}")

    # The reviewed primitive costs are exact for these two U1 XOR families.
    # No other component changes, so the gate delta must be 19 * (3 - 1).
    if candidate.gate != baseline.gate - len(TARGET_ROWS) * 2:
        raise RuntimeError("candidate gate declaration does not match exact XOR delta")

    connectivity = analyze_connectivity(candidate)
    bad_connectivity = {
        field: connectivity[field]
        for field in BAD_CONNECTIVITY_FIELDS
        if connectivity[field]
    }
    if bad_connectivity:
        raise RuntimeError(f"candidate connectivity failed: {bad_connectivity}")

    xor_bit_cells = sprite_alpha_cells(
        DEFAULT_COMPONENT_SPRITE_ROOT / "com_xor_bit.png"
    )
    xor_word_cells = sprite_alpha_cells(
        DEFAULT_COMPONENT_SPRITE_ROOT / "com_xor_word.png"
    )
    if xor_bit_cells != xor_word_cells:
        raise RuntimeError("bit-XOR and word-XOR live sprite occupancy differs")

    geometry = audit_sprite_geometry(candidate, DEFAULT_COMPONENT_SPRITE_ROOT)
    internal_collisions = tuple(
        collision
        for collision in geometry.wire_collisions
        if collision.component_kind not in {62, 70}
    )
    if (
        geometry.unsupported_component_kinds
        or geometry.component_overlap_cells
        or internal_collisions
        or geometry.wire_interior_pin_contacts
    ):
        raise RuntimeError(
            "candidate live geometry failed: "
            f"unsupported={geometry.unsupported_component_kinds}, "
            f"overlap={len(geometry.component_overlap_cells)}, "
            f"internal_collisions={len(internal_collisions)}, "
            f"pin_contacts={len(geometry.wire_interior_pin_contacts)}"
        )

    seeds = _verification_seeds()
    streams = tuple(_verify_output_stream(candidate, seed) for seed in seeds)
    if any(len(stream) != 65 for stream in streams):
        raise RuntimeError("candidate did not emit 65 values for every seed")

    encoded = encode_v15(candidate)
    decoded = decode_v15(encoded)
    if decoded != candidate or encode_v15(decoded) != encoded:
        raise RuntimeError("candidate failed canonical v15 round trip")

    report = {
        "source_sha256": actual_sha256,
        "candidate_sha256": sha256(encoded).hexdigest(),
        "changed_component_count": len(changed_indices),
        "changed_component_indices": changed_indices,
        "kind_counts": dict(sorted(counts.items())),
        "leaderboard_tuple_prediction": [358, 10, 66],
        "predicted_energy": 358 * 10 * 66,
        "verified_seed_count": len(seeds),
        "verified_output_count": sum(len(stream) for stream in streams),
        "connectivity": {
            field: connectivity[field] for field in BAD_CONNECTIVITY_FIELDS
        },
        "geometry": {
            "unsupported_component_kind_count": len(
                geometry.unsupported_component_kinds
            ),
            "component_overlap_cell_count": len(geometry.component_overlap_cells),
            "internal_wire_collision_count": len(internal_collisions),
            "wire_interior_pin_contact_count": len(
                geometry.wire_interior_pin_contacts
            ),
        },
    }
    return candidate, encoded, report


def main() -> None:
    _, encoded, report = _validate_and_build()
    LIVE_CIRCUIT.parent.mkdir(parents=True, exist_ok=True)
    LIVE_CIRCUIT.write_bytes(encoded)
    written = LIVE_CIRCUIT.read_bytes()
    if written != encoded or decode_v15(written) != decode_v15(encoded):
        raise RuntimeError("live circuit verification failed after direct overwrite")
    print(json.dumps({**report, "live_path": str(LIVE_CIRCUIT)}, indent=2))


if __name__ == "__main__":
    main()
