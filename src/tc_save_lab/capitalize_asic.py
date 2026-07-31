"""Capitalize architecture ASIC.

The input alphabet is lower-case ASCII letters plus space.  Bit 6 is therefore
exactly the predicate ``is_letter``: it is one for ``a`` through ``z`` and zero
for space.  A single Bit Delay stores that predicate, and a Maker8 replaces the
current character's bit 5 with the delayed predicate.  Splitter8/Maker8 are
zero-cost wiring primitives, leaving the Bit Delay's measured 5/4 metric.
"""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

from .analysis import wire_points
from .builder import stable_permanent_id, wire_from_vertices
from .codec import decode_v15, encode_v15
from .model import Circuit, Component, Point
from .pins import analyze_connectivity, positioned_pins
from .simulate import simulate_clocked_tick
from .sprite_geometry import DEFAULT_COMPONENT_SPRITE_ROOT, sprite_alpha_cells


EXPECTED_GATE = 5
EXPECTED_DELAY = 4
EXPECTED_CYCLES = (101, 112, 111)
PUBLIC_REFERENCE = (5, 4, 112)

TEST_TEXTS = (
    "computable numbers are the real numbers whose expressions as a decimal are calculable by finite means",
    "the fundamental problem of communication is that of reproducing at one point a message selected at another point",
    "future users of large data banks must be protected from having to know how the data is organized in the machine",
)


_SPRITE_BY_KIND = {
    2: "com_on.png",
    13: "com_delay_line_bit.png",
    16: "com_maker_bit_8.png",
    17: "com_splitter_bit_8.png",
    62: "com_level_input_switched.png",
    70: "com_level_output_switched.png",
}


def expected_character(text: str, index: int) -> int:
    """Return the exact output expected by ``campaign/capitalize/test.si``."""

    value = ord(text[index])
    if index == 0 or text[index - 1] == " ":
        value &= 0xDF
    return value


def _component(
    key: str,
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


def build_capitalize_asic() -> Circuit:
    """Build the one-delay, 5/4 Capitalize circuit."""

    key = "architecture/codex-capitalize"
    level_input = _component(
        key, "level-input", 62, (-45, 0), word_size=8, ui_order=-2, user_label="Character"
    )
    level_output = _component(
        key, "level-output", 70, (45, 0), word_size=8, ui_order=-2, user_label="Capitalized"
    )
    input_enable = _component(key, "input-enable", 2, (-55, -5))
    output_enable = _component(key, "output-enable", 2, (40, -6))
    splitter = _component(key, "splitter", 17, (-30, 0), word_size=8)
    letter_delay = _component(key, "letter-delay", 13, (-5, 10), init_data=0)
    maker = _component(key, "maker", 16, (20, 0))

    components = (
        level_input,
        level_output,
        input_enable,
        output_enable,
        splitter,
        letter_delay,
        maker,
    )

    # Control pins are approached from outside the switched I/O sprites.  The
    # long lanes are intentional: they keep every intermediate grid point out
    # of component alpha and leave only legal pin endpoints on sprite cells.
    wires = [
        wire_from_vertices(((-54, -5), (-53, -5), (-53, -3), (-44, -3), (-44, -2))),
        wire_from_vertices(((41, -6), (42, -6), (42, -3), (44, -3), (44, -2))),
        wire_from_vertices(((-42, 0), (-31, 0))),
    ]

    # Bits 0..4 and 7 pass through unchanged.  Bit 6 is the current
    # is-letter predicate and is captured for the next character.
    for bit in (0, 1, 2, 3, 4, 6, 7):
        y = bit - 3
        wires.append(wire_from_vertices(((-29, y), (19, y))))
    wires.append(wire_from_vertices(((-29, 3), (-24, 3), (-24, 10), (-8, 10))))

    # The delayed bit becomes Maker8 input 5 (the character's bit 5).
    wires.append(
        wire_from_vertices(((-2, 10), (15, 10), (15, 6), (18, 6), (18, 2), (19, 2)))
    )
    wires.append(wire_from_vertices(((21, 0), (42, 0))))

    return Circuit(
        gate=EXPECTED_GATE,
        delay=EXPECTED_DELAY,
        description=(
            "Codex Capitalize ASIC: delay current ASCII bit 6 and use it as "
            "the next character's bit 5"
        ),
        components=components,
        wires=tuple(wires),
    )


def _sprite_geometry(circuit: Circuit, sprite_root: Path) -> dict[str, object]:
    """Audit current alpha sprites without changing the shared audit registry."""

    alpha_by_component: list[frozenset[Point]] = []
    pins_by_component: list[dict[Point, tuple[str, ...]]] = []
    unsupported: list[int] = []
    for index, component in enumerate(circuit.components):
        name = _SPRITE_BY_KIND.get(component.kind)
        if name is None:
            unsupported.append(component.kind)
            alpha_by_component.append(frozenset())
        else:
            path = sprite_root / name
            cells = sprite_alpha_cells(path)
            alpha_by_component.append(
                frozenset(
                    (
                        component.position[0] + point[0],
                        component.position[1] + point[1],
                    )
                    for point in cells
                )
            )
        names: dict[Point, list[str]] = {}
        for pin in positioned_pins(component, index):
            names.setdefault(pin.position, []).append(pin.name)
        pins_by_component.append({point: tuple(values) for point, values in names.items()})

    owners: dict[Point, list[int]] = {}
    for index, cells in enumerate(alpha_by_component):
        for point in cells:
            owners.setdefault(point, []).append(index)

    body_collisions: list[tuple[int, int, Point]] = []
    interior_pins: list[tuple[int, int, Point, tuple[str, ...]]] = []
    for wire_index, wire in enumerate(circuit.wires):
        points = wire_points(wire)
        endpoints = {points[0], points[-1]}
        for point in points:
            for component_index, cells in enumerate(alpha_by_component):
                pin_names = pins_by_component[component_index].get(point, ())
                if point in cells and not (point in endpoints and pin_names):
                    body_collisions.append((wire_index, component_index, point))
            if point not in endpoints:
                for component_index, pins in enumerate(pins_by_component):
                    pin_names = pins.get(point, ())
                    if pin_names:
                        interior_pins.append((wire_index, component_index, point, pin_names))

    return {
        "sprite_files": sorted(_SPRITE_BY_KIND[k] for k in _SPRITE_BY_KIND if k in {c.kind for c in circuit.components}),
        "unsupported_component_kinds": sorted(set(unsupported)),
        "component_overlap_count": sum(len(values) - 1 for values in owners.values() if len(values) > 1),
        "wire_body_collision_count": len(body_collisions),
        "wire_interior_pin_contact_count": len(interior_pins),
        "wire_body_collisions": [
            {"wire": w, "component": c, "point": list(p)} for w, c, p in body_collisions
        ],
        "wire_interior_pin_contacts": [
            {"wire": w, "component": c, "point": list(p), "pins": list(names)}
            for w, c, p, names in interior_pins
        ],
    }


def _verify_stream(circuit: Circuit, text: str) -> int:
    memory = None
    for index, character in enumerate(text):
        result = simulate_clocked_tick(
            circuit,
            inputs={"Character": ord(character)},
            memory=memory,
        )
        expected = expected_character(text, index)
        if result.outputs != {"Capitalized": expected}:
            raise RuntimeError(
                f"capitalize mismatch at {index}: expected {expected:#04x}, "
                f"got {result.outputs}"
            )
        memory = result.memory
    return len(text)


def verify_capitalize_asic(
    circuit: Circuit | None = None,
    *,
    sprite_root: Path = DEFAULT_COMPONENT_SPRITE_ROOT,
) -> dict[str, object]:
    candidate = build_capitalize_asic() if circuit is None else circuit
    if (candidate.gate, candidate.delay) != (EXPECTED_GATE, EXPECTED_DELAY):
        raise RuntimeError("Capitalize candidate metric declaration changed")
    kind_counts = {kind: sum(component.kind == kind for component in candidate.components) for kind in (2, 13, 16, 17, 62, 70)}
    if kind_counts != {2: 2, 13: 1, 16: 1, 17: 1, 62: 1, 70: 1}:
        raise RuntimeError(f"unexpected Capitalize component counts: {kind_counts}")

    connectivity = analyze_connectivity(candidate)
    for field in (
        "unsupported_component_kind_counts",
        "multi_driver_network_count",
        "undriven_network_count",
        "width_mismatch_network_count",
        "cycle_component_count",
    ):
        if connectivity[field]:
            raise RuntimeError(f"Capitalize connectivity failure {field}: {connectivity[field]}")
    unconnected = connectivity["unconnected_pins"]
    if [pin["name"] for pin in unconnected] != ["out5"]:
        raise RuntimeError(f"Capitalize unexpected unconnected pins: {unconnected}")

    layout = _sprite_geometry(candidate, sprite_root)
    for field in (
        "unsupported_component_kinds",
        "component_overlap_count",
        "wire_body_collision_count",
        "wire_interior_pin_contact_count",
    ):
        if layout[field]:
            raise RuntimeError(f"Capitalize geometry failure {field}: {layout[field]}")

    cycles = tuple(_verify_stream(candidate, text) for text in TEST_TEXTS)
    if cycles != EXPECTED_CYCLES:
        raise RuntimeError(f"Capitalize cycle regression: {cycles!r}")
    return {
        "gate": candidate.gate,
        "delay": candidate.delay,
        "cycles": list(cycles),
        "leaderboard_tuple": [candidate.gate, candidate.delay, max(cycles)],
        "energy": candidate.gate * candidate.delay * max(cycles),
        "public_reference": list(PUBLIC_REFERENCE),
        "component_kind_counts": {str(k): v for k, v in sorted(kind_counts.items())},
        "connectivity": connectivity,
        "layout": layout,
    }


def write_capitalize_asic(project_root: Path) -> dict[str, object]:
    candidate = build_capitalize_asic()
    verification = verify_capitalize_asic(candidate)
    payload = encode_v15(candidate)
    if decode_v15(payload) != candidate:
        raise RuntimeError("Capitalize candidate failed v15 round-trip")
    destination = project_root / "examples" / "capitalize" / "candidate" / "circuit.data"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(payload)
    metadata = {
        "schema": 1,
        "level": "capitalize",
        "title": "Capitalize",
        "strategy": "bit-6 delayed state with zero-cost Splitter8/Maker8",
        "deployment_target": "schematics/architecture/CODEX-CAPITALIZE/circuit.data",
        "sha256": sha256(payload).hexdigest(),
        "format_version": 15,
        "component_count": len(candidate.components),
        "wire_count": len(candidate.wires),
        **verification,
    }
    (destination.parent / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return metadata
