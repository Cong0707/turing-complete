"""Build a separate two-Architecture-Output runtime probe.

The probe clones the currently selected RNG output.  On the first enabled
tick, output 0 is accepted and output 1 repeats the same value.  A runtime
error naming the second expected RNG value therefore proves that both output
components invoke ``arch_check_output`` during one simulation tick.

This script never writes CODEX-RNG or levels.txt.  It only creates the
standalone CODEX-RNG-2OUT-PROBE schematic.
"""

from __future__ import annotations

import argparse
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path

from tc_save_lab.builder import stable_permanent_id
from tc_save_lab.codec import decode_v15, encode_v15
from tc_save_lab.pins import analyze_connectivity
from tc_save_lab.rng_encoded_asic import _build_router, _layout_safety, _pin
from tc_save_lab.sprite_geometry import DEFAULT_COMPONENT_SPRITE_ROOT, audit_sprite_geometry


DEFAULT_SOURCE = Path(
    r"C:\Users\cong\AppData\Roaming\Turing Complete"
    r"\schematics\architecture\CODEX-RNG\circuit.data"
)
DEFAULT_DESTINATION = Path(
    r"C:\Users\cong\AppData\Roaming\Turing Complete"
    r"\schematics\architecture\CODEX-RNG-2OUT-PROBE\circuit.data"
)


def build(source: Path):
    original = decode_v15(source.read_bytes())
    outputs = tuple(component for component in original.components if component.kind == 70)
    if len(outputs) != 1:
        raise RuntimeError(f"expected one Architecture Output, found {len(outputs)}")
    first = outputs[0]
    second = replace(
        first,
        position=(300, 0),
        permanent_id=stable_permanent_id(
            "architecture/codex-rng-2out-probe", "level-output-2"
        ),
        user_label="RNG output 2",
        ui_order=-1,
    )
    components = original.components + (second,)
    route = _build_router(components)
    wires = original.wires + (
        route(_pin(first, "control"), _pin(second, "control")),
        route(_pin(first, "value"), _pin(second, "value")),
    )
    return replace(
        original,
        custom_id=0,
        design=b"",
        description=(
            "Research probe: duplicate the current RNG output to prove that two "
            "Architecture Output callbacks execute in one tick"
        ),
        components=components,
        wires=wires,
    )


def verify(circuit) -> dict[str, object]:
    connectivity = analyze_connectivity(circuit)
    rejected = (
        "unsupported_component_kind_counts",
        "unconnected_pin_count",
        "multi_driver_network_count",
        "undriven_network_count",
        "width_mismatch_network_count",
        "cycle_component_count",
    )
    for field in rejected:
        if connectivity[field]:
            raise RuntimeError(f"probe connectivity failed {field}: {connectivity[field]}")
    layout = _layout_safety(circuit)
    if any(layout.values()):
        raise RuntimeError(f"probe layout failed: {layout}")
    sprite = audit_sprite_geometry(circuit, DEFAULT_COMPONENT_SPRITE_ROOT)
    internal = tuple(
        collision
        for collision in sprite.wire_collisions
        if collision.component_kind not in {62, 70}
    )
    if (
        sprite.unsupported_component_kinds
        or sprite.component_overlap_cells
        or internal
        or sprite.wire_interior_pin_contacts
    ):
        raise RuntimeError(
            "probe sprite geometry failed: "
            f"unsupported={sprite.unsupported_component_kinds}, "
            f"overlap={len(sprite.component_overlap_cells)}, "
            f"internal_wire_collisions={len(internal)}, "
            f"pin_contacts={len(sprite.wire_interior_pin_contacts)}"
        )
    return {
        "architecture_output_count": sum(
            component.kind == 70 for component in circuit.components
        ),
        "component_count": len(circuit.components),
        "wire_count": len(circuit.wires),
        "connectivity": connectivity,
        "layout": layout,
        "sprite_internal_wire_collision_count": len(internal),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--destination", type=Path, default=DEFAULT_DESTINATION)
    args = parser.parse_args()

    circuit = build(args.source)
    report = verify(circuit)
    payload = encode_v15(circuit)
    if decode_v15(payload) != circuit:
        raise RuntimeError("probe failed v15 round trip")
    args.destination.parent.mkdir(parents=True, exist_ok=True)
    args.destination.write_bytes(payload)
    report.update(
        {
            "source": str(args.source),
            "destination": str(args.destination),
            "sha256": sha256(payload).hexdigest(),
            "formal_target_untouched": str(DEFAULT_SOURCE),
        }
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
