"""Convert the public 154/4 Hub 79 adder into the Byte Adder campaign slot.

Only the five Foundry boundary ports are replaced.  The reviewed internal
Switch/Z topology and all of its wires remain byte-for-byte equivalent at the
logical endpoints.  This is a bootstrap candidate for an account whose
Byte Adder cost frontier is still empty; it does not start the game or touch
the formal save.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass, replace
from hashlib import sha256
import json
from pathlib import Path

from tc_save_lab.codec import decode_v15, encode_v15
from tc_save_lab.analysis import wire_points
from tc_save_lab.model import Wire
from tc_save_lab.pins import analyze_connectivity
from tc_save_lab.simulate import verify_truth_table
from tc_save_lab.sprite_geometry import (
    DEFAULT_COMPONENT_SPRITE_ROOT,
    audit_sprite_geometry,
)


ROOT = Path(__file__).resolve().parents[2]
SOURCE = (
    ROOT
    / "examples"
    / "rng"
    / "research"
    / "archive"
    / "rng_public_artifacts"
    / "hub-79-adder"
    / "main"
    / "circuit.data"
)
INTERFACE = ROOT / "examples" / "byte_adder" / "candidate" / "circuit.data"
OUTPUT = Path(__file__).with_name("hub79_campaign_154x4.data")
CERTIFICATE = Path(__file__).with_name("hub79_campaign_154x4.json")


@dataclass(frozen=True)
class Verification:
    gate: int
    delay: int
    energy: int
    components: int
    wires: int
    vectors: int
    multi_driver_networks: int
    component_overlap_cells: int
    wire_collisions: int
    wire_interior_pin_contacts: int
    payload_bytes: int
    sha256: str


def build():
    public = decode_v15(SOURCE.read_bytes())
    interface = decode_v15(INTERFACE.read_bytes())
    templates = {
        component.user_label: component
        for component in interface.components
        if component.kind in {61, 69}
    }
    expected_templates = {"A", "B", "Carry in", "Output", "Carry out"}
    if set(templates) != expected_templates:
        raise RuntimeError(f"campaign interface changed: {sorted(templates)}")

    label_map = {
        "A": "A",
        "B": "B",
        "Cin": "Carry in",
        "sum": "Output",
        "Cout": "Carry out",
    }
    replaced_ports = Counter()
    components = []
    removed_zero_adapter_ids = set()
    for component in public.components:
        if (component.kind, component.position) in {
            (111, (-50, -15)),
            (109, (-47, -15)),
        }:
            removed_zero_adapter_ids.add(component.permanent_id)
            continue
        if component.kind not in {79, 81}:
            components.append(component)
            continue
        campaign_label = label_map.get(component.user_label)
        if campaign_label is None:
            raise RuntimeError(f"unknown Hub 79 port {component.user_label!r}")
        template = templates[campaign_label]
        components.append(
            replace(
                template,
                position=component.position,
                rotation=component.rotation,
            )
        )
        replaced_ports[campaign_label] += 1
    if replaced_ports != Counter({name: 1 for name in expected_templates}):
        raise RuntimeError(f"unexpected port multiplicity: {replaced_ports}")
    if len(removed_zero_adapter_ids) != 2:
        raise RuntimeError("Hub 79 carry adapter topology changed")

    # Hub 79 packed Cout into Maker2 bit 1 and immediately extracted it again.
    # The unused Maker2 bit 0 is accepted as zero in Foundry but a campaign
    # circuit is cleaner when the already-scalar Switch bus is wired directly.
    adapter_link = {(-49, -15), (-48, -15)}
    wires = []
    removed_adapter_wire = 0
    for wire in public.wires:
        endpoints = {wire_points(wire)[0], wire_points(wire)[-1]}
        if endpoints == adapter_link:
            removed_adapter_wire += 1
            continue
        wires.append(wire)
    if removed_adapter_wire != 1:
        raise RuntimeError(f"expected one Maker2/Splitter2 link, got {removed_adapter_wire}")
    wires.append(
        Wire(
            color=0,
            comment="Codex direct scalar Cout bridge",
            start=(-51, -15),
            segments=((0, 5),),
        )
    )

    candidate = replace(
        interface,
        gate=public.gate,
        delay=public.delay,
        description="Codex Hub 79 Switch/Z bootstrap for Byte Adder",
        components=tuple(components),
        wires=tuple(wires),
    )
    permanent_ids = [component.permanent_id for component in candidate.components]
    if len(permanent_ids) != len(set(permanent_ids)):
        raise RuntimeError("campaign conversion introduced duplicate permanent IDs")
    return candidate


def verify(candidate) -> Verification:
    payload = encode_v15(candidate)
    if decode_v15(payload) != candidate:
        raise RuntimeError("v15 round trip changed Hub 79 campaign candidate")
    if (candidate.gate, candidate.delay) != (154, 4):
        raise RuntimeError(f"unexpected score: {candidate.gate}/{candidate.delay}")

    tested = verify_truth_table(
        candidate,
        inputs={"A": 8, "B": 8, "Carry in": 1},
        output_label=("Output", "Carry out"),
        expected=lambda values: {
            "Output": (values["A"] + values["B"] + values["Carry in"]) & 0xFF,
            "Carry out": (values["A"] + values["B"] + values["Carry in"]) >> 8,
        },
    )
    if tested != 1 << 17:
        raise RuntimeError(f"truth-table coverage changed: {tested}")

    connectivity = analyze_connectivity(candidate)
    for field in (
        "unsupported_component_kind_counts",
        "unconnected_pin_count",
        "undriven_network_count",
        "sinkless_network_count",
        "width_mismatch_network_count",
        "cycle_component_count",
    ):
        if connectivity[field]:
            raise RuntimeError(f"connectivity failure {field}: {connectivity[field]!r}")
    if connectivity["multi_driver_network_count"] != 18:
        raise RuntimeError(
            "Hub 79 Switch bus count changed: "
            f"{connectivity['multi_driver_network_count']}"
        )

    geometry = audit_sprite_geometry(candidate, DEFAULT_COMPONENT_SPRITE_ROOT)
    if (
        geometry.unsupported_component_kinds
        or geometry.component_overlap_cells
        or geometry.wire_collisions
        or geometry.wire_interior_pin_contacts
    ):
        raise RuntimeError(f"sprite geometry failure: {geometry!r}")

    return Verification(
        gate=candidate.gate,
        delay=candidate.delay,
        energy=candidate.energy,
        components=len(candidate.components),
        wires=len(candidate.wires),
        vectors=tested,
        multi_driver_networks=connectivity["multi_driver_network_count"],
        component_overlap_cells=len(geometry.component_overlap_cells),
        wire_collisions=len(geometry.wire_collisions),
        wire_interior_pin_contacts=len(geometry.wire_interior_pin_contacts),
        payload_bytes=len(payload),
        sha256=sha256(payload).hexdigest(),
    )


def main() -> None:
    candidate = build()
    report = verify(candidate)
    payload = encode_v15(candidate)
    OUTPUT.write_bytes(payload)
    document = {
        "schema": "byte-adder-hub79-campaign-bootstrap-v1",
        "source": str(SOURCE.relative_to(ROOT)).replace("\\", "/"),
        "source_sha256": sha256(SOURCE.read_bytes()).hexdigest(),
        "formal_save_touched": False,
        "verification": asdict(report),
    }
    CERTIFICATE.write_text(
        json.dumps(document, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(document, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
