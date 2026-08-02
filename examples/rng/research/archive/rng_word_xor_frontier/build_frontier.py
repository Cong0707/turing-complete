from __future__ import annotations

from collections import Counter
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from tc_save_lab.codec import decode_v15, encode_v15
from tc_save_lab.builder import stable_permanent_id
from tc_save_lab.pins import analyze_connectivity, positioned_pins
from tc_save_lab.rng_encoded_asic import GATES, _verification_seeds, _verify_output_stream
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
BASELINE_SHA256 = "844f4a950499cd8823bcee48dffafc4474e3a176225716c65f5d87403026d0c1"

# Exact maximum-cardinality certificate under the measured 11-delay timing model.
ROWS_304 = frozenset(
    int(row, 16)
    for row in """
00000021 00000042 00000084 00000108 00000210 00000420 00000840 00001080
00002021 00002100 00004042 00004200 00008008 00008808 00010010 00011010
00420000 00840000 01080000 01088008 02100000 02110010 04200000 04200021
08008400 08008840 08400000 08400042 10010800 10011080 10800000 10800084
20000001 20002101 21000000 21000108 40000002 40004202 40420002 42000000
42000210 80000004 80000404 80840004 84000000 84000420
""".split()
)


def _pin_signature(component, index: int) -> tuple[tuple[object, ...], ...]:
    return tuple(
        (pin.name, pin.direction, pin.width, pin.position)
        for pin in positioned_pins(component, index)
    )


def _build(rows: frozenset[int], gate: int, delay: int):
    payload = BASELINE.read_bytes()
    if sha256(payload).hexdigest() != BASELINE_SHA256:
        raise RuntimeError("verified RNG baseline hash changed")
    baseline = decode_v15(payload)

    bit_xors = [component for component in baseline.components if component.kind == 10]
    if len(bit_xors) != 61:
        raise RuntimeError(f"expected 61 bit XORs, got {len(bit_xors)}")

    row_by_id = {
        stable_permanent_id(
            "architecture/codex-rng-encoded",
            f"xor-depth-{gate.depth}-{gate.output:08x}",
        ): gate.output
        for gate in GATES
    }
    row_by_index = {
        index: row_by_id[component.permanent_id]
        for index, component in enumerate(baseline.components)
        if component.kind == 10 and component.permanent_id in row_by_id
    }
    if len(row_by_index) != 61:
        raise RuntimeError(f"mapped {len(row_by_index)} of 61 XOR stable IDs")

    if rows and not rows <= frozenset(row_by_index.values()):
        missing = sorted(rows - frozenset(row_by_index.values()))
        raise RuntimeError(f"missing certified XOR rows: {[f'{row:08x}' for row in missing]}")

    replace_all = not rows
    components = []
    changed = []
    for index, component in enumerate(baseline.components):
        selected = component.kind == 10 and (replace_all or row_by_index[index] in rows)
        if not selected:
            components.append(component)
            continue
        replacement = replace(component, kind=23, word_size=1)
        if _pin_signature(component, index) != _pin_signature(replacement, index):
            raise RuntimeError(f"pin geometry changed at component {index}")
        components.append(replacement)
        changed.append(index)

    candidate = replace(
        baseline,
        gate=gate,
        delay=delay,
        components=tuple(components),
    )
    counts = Counter(component.kind for component in candidate.components)
    expected_word = 61 if replace_all else len(rows)
    if counts[23] != expected_word or counts[10] != 61 - expected_word:
        raise RuntimeError(f"unexpected XOR counts: {dict(counts)}")
    if gate != 396 - 2 * expected_word:
        raise RuntimeError("declared gate count does not match the exact XOR delta")

    connectivity = analyze_connectivity(candidate)
    bad_fields = (
        "unsupported_component_kind_counts",
        "unconnected_pin_count",
        "multi_driver_network_count",
        "undriven_network_count",
        "width_mismatch_network_count",
        "cycle_component_count",
    )
    bad = {field: connectivity[field] for field in bad_fields if connectivity[field]}
    if bad:
        raise RuntimeError(f"connectivity failed: {bad}")

    if sprite_alpha_cells(DEFAULT_COMPONENT_SPRITE_ROOT / "com_xor_bit.png") != sprite_alpha_cells(
        DEFAULT_COMPONENT_SPRITE_ROOT / "com_xor_word.png"
    ):
        raise RuntimeError("bit and word XOR sprite occupancy differs")
    geometry = audit_sprite_geometry(candidate, DEFAULT_COMPONENT_SPRITE_ROOT)
    internal = tuple(
        collision
        for collision in geometry.wire_collisions
        if collision.component_kind not in {62, 70}
    )
    if (
        geometry.unsupported_component_kinds
        or geometry.component_overlap_cells
        or internal
        or geometry.wire_interior_pin_contacts
    ):
        raise RuntimeError("live sprite geometry audit failed")

    streams = tuple(_verify_output_stream(candidate, seed) for seed in _verification_seeds())
    encoded = encode_v15(candidate)
    if decode_v15(encoded) != candidate:
        raise RuntimeError("v15 round trip failed")
    return encoded, {
        "gate": gate,
        "delay": delay,
        "cycles": 66,
        "energy": gate * delay * 66,
        "sha256": sha256(encoded).hexdigest(),
        "changed_xor_count": expected_word,
        "bit_xor_count": counts[10],
        "word_xor_count": counts[23],
        "verified_seed_count": len(streams),
        "verified_output_count": sum(len(stream) for stream in streams),
        "geometry": {
            "component_overlap_cell_count": len(geometry.component_overlap_cells),
            "internal_wire_collision_count": len(internal),
            "wire_interior_pin_contact_count": len(geometry.wire_interior_pin_contacts),
        },
    }


def main() -> None:
    output_dir = Path(__file__).resolve().parent
    reports = []
    for rows, gate, delay in ((ROWS_304, 304, 11), (frozenset(), 274, 12)):
        payload, report = _build(rows, gate, delay)
        destination = output_dir / f"candidate-{gate}-{delay}-66.data"
        destination.write_bytes(payload)
        if destination.read_bytes() != payload:
            raise RuntimeError(f"write verification failed for {destination}")
        reports.append({"path": str(destination), **report})
    (output_dir / "RESULT.json").write_text(
        json.dumps(reports, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(reports, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
