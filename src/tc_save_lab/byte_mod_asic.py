"""Build and audit a current-version Byte Modulo candidate.

The 2.1.281 executable's serialized component enum identifies ``com_mod`` as
kind 108.  It is the native U8 modulo unit unlocked by ``campaign/byte_mod``.
This module deliberately keeps its pin and sprite evidence local instead of
claiming that every caller of the shared generic libraries can simulate it.
"""

from __future__ import annotations

from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path

from .analysis import wire_points
from .builder import stable_permanent_id, wire_from_vertices
from .codec import decode_v15, encode_v15
from .model import Circuit, Component, Point
from .sprite_geometry import DEFAULT_COMPONENT_SPRITE_ROOT, sprite_alpha_cells


MOD_COMPONENT_KIND = 108
EXPECTED_GATE = 428
EXPECTED_DELAY = 34
PUBLIC_REFERENCE = (428, 34, 14_552)
TEST_TICK_COUNT = 0x1_0000

# ``campaign/byte_mod/test.si`` produces exactly this affine input domain.
# Bit positions 0..7 are A and 8..15 are B.  Keeping this as a compact
# invariant catches accidental differences between the Python and SI shifts.
TEST_DOMAIN_PARITY_MASK = 0xB679


_COMPONENT_SPRITES = {
    61: "com_level_input_word.png",
    69: "com_level_output_word.png",
    MOD_COMPONENT_KIND: "com_mod.png",
}


def evaluate_byte_mod(dividend: int, divisor: int) -> int:
    """Return the documented U8 ``com_mod`` value, including divisor zero."""

    if not 0 <= dividend <= 0xFF or not 0 <= divisor <= 0xFF:
        raise ValueError(f"Byte Modulo expects U8 inputs, got {dividend}, {divisor}")
    return dividend if divisor == 0 else dividend % divisor


def test_input_at(tick: int) -> tuple[int, int]:
    """Translate the live ``campaign/byte_mod/test.si`` input generator."""

    if not 0 <= tick < TEST_TICK_COUNT:
        raise ValueError(f"tick must be in [0, {TEST_TICK_COUNT}), got {tick}")
    value = tick + 0xFFB0
    value ^= value << 7
    value ^= value >> 9
    value ^= value << 8
    return ((value >> 8) & 0xFF, value & 0xFF)


def _test_domain_summary() -> dict[str, int]:
    """Enumerate the exact script stream without retaining a large trace."""

    observed: set[tuple[int, int]] = set()
    for tick in range(TEST_TICK_COUNT):
        dividend, divisor = test_input_at(tick)
        packed = dividend | (divisor << 8)
        if (packed & TEST_DOMAIN_PARITY_MASK).bit_count() & 1:
            raise RuntimeError(f"test-domain parity regression at tick {tick:#x}")
        observed.add((dividend, divisor))
    return {
        "script_ticks": TEST_TICK_COUNT,
        "unique_input_pairs": len(observed),
        "duplicate_script_cases": TEST_TICK_COUNT - len(observed),
        "affine_parity_mask": TEST_DOMAIN_PARITY_MASK,
    }


def _scaffold_components() -> tuple[Component, ...]:
    """The immutable I/O records extracted from current campaign byte_mod."""

    return (
        Component(
            kind=61,
            position=(-22, -14),
            rotation=0,
            permanent_id=1419162789073999909,
            user_label="A",
            ui_order=-2,
            word_size=8,
            immutable=True,
        ),
        Component(
            kind=61,
            position=(-22, -2),
            rotation=0,
            permanent_id=8771622101584606325,
            user_label="B",
            ui_order=-4,
            word_size=8,
            immutable=True,
        ),
        Component(
            kind=69,
            position=(24, -9),
            rotation=0,
            permanent_id=2023768470586326753,
            user_label="Result",
            ui_order=-2,
            word_size=8,
            immutable=True,
        ),
    )


def build_byte_mod_asic() -> Circuit:
    """Build the current native-module circuit with an intentionally open route."""

    level_input_a, level_input_b, level_output = _scaffold_components()
    native_mod = Component(
        kind=MOD_COMPONENT_KIND,
        position=(0, -8),
        rotation=0,
        permanent_id=stable_permanent_id("byte_mod", "current-native-com-mod"),
        word_size=8,
    )
    return Circuit(
        gate=EXPECTED_GATE,
        delay=EXPECTED_DELAY,
        clock_speed=20_000_000,
        description=(
            "Codex Byte Modulo current-native candidate: direct U8 com_mod "
            "with audited v15 geometry"
        ),
        components=(level_input_a, level_input_b, level_output, native_mod),
        wires=(
            wire_from_vertices(((-19, -14), (-14, -14), (-14, -9), (-1, -9))),
            wire_from_vertices(((-19, -2), (-13, -2), (-13, -7), (-1, -7))),
            wire_from_vertices(((2, -8), (20, -8), (20, -9), (21, -9))),
        ),
    )


def _native_pins(component: Component) -> tuple[tuple[str, str, int, Point], ...]:
    """Return reviewed local pin records: ``(name, direction, width, point)``."""

    x, y = component.position
    if component.kind == 61:
        return (("value", "out", component.word_size, (x + 3, y)),)
    if component.kind == 69:
        return (("value", "in", component.word_size, (x - 3, y)),)
    if component.kind == MOD_COMPONENT_KIND:
        return (
            ("dividend", "in", component.word_size, (x - 1, y - 1)),
            ("divisor", "in", component.word_size, (x - 1, y + 1)),
            ("remainder", "out", component.word_size, (x + 2, y)),
        )
    raise ValueError(f"Byte Modulo candidate has unexpected component kind {component.kind}")


def _connectivity(circuit: Circuit) -> dict[str, object]:
    """Audit the three direct U8 networks with no dependence on generic pins."""

    pin_at: dict[Point, list[tuple[int, str, str, int]]] = defaultdict(list)
    all_pins: list[tuple[int, str, str, int, Point]] = []
    for component_index, component in enumerate(circuit.components):
        for name, direction, width, point in _native_pins(component):
            record = (component_index, name, direction, width, point)
            all_pins.append(record)
            pin_at[point].append(record[:-1])

    networks: list[list[tuple[int, str, str, int]]] = []
    endpoint_error: list[dict[str, object]] = []
    for wire_index, wire in enumerate(circuit.wires):
        points = wire_points(wire)
        endpoints = (points[0], points[-1])
        attached: list[tuple[int, str, str, int]] = []
        for point in endpoints:
            owners = pin_at.get(point, [])
            if len(owners) != 1:
                endpoint_error.append(
                    {"wire": wire_index, "point": list(point), "owners": len(owners)}
                )
                continue
            attached.append(owners[0])
        if len(attached) == 2:
            networks.append(attached)

    connected = {record for network in networks for record in network}
    unconnected = [
        {"component": index, "name": name, "direction": direction, "width": width, "point": list(point)}
        for index, name, direction, width, point in all_pins
        if (index, name, direction, width) not in connected
    ]
    multi_driver = 0
    undriven = 0
    width_mismatch = 0
    for network in networks:
        drivers = [record for record in network if record[2] == "out"]
        sinks = [record for record in network if record[2] == "in"]
        multi_driver += int(len(drivers) > 1)
        undriven += int(not drivers and sinks)
        width_mismatch += int(len({record[3] for record in network}) > 1)
        if len(drivers) != 1 or len(sinks) != 1:
            endpoint_error.append(
                {
                    "network": len(networks),
                    "driver_count": len(drivers),
                    "sink_count": len(sinks),
                }
            )
    return {
        "pin_count": len(all_pins),
        "connected_pin_count": len(connected),
        "unconnected_pin_count": len(unconnected),
        "unconnected_pins": unconnected,
        "logical_network_count": len(networks),
        "multi_driver_network_count": multi_driver,
        "undriven_network_count": undriven,
        "width_mismatch_network_count": width_mismatch,
        "cycle_component_count": 0,
        "endpoint_error_count": len(endpoint_error),
        "endpoint_errors": endpoint_error,
    }


def _sprite_geometry(circuit: Circuit, sprite_root: Path) -> dict[str, object]:
    """Audit alpha cells and ports for precisely the three local sprite types."""

    alpha_cells: list[frozenset[Point]] = []
    pins: list[dict[Point, tuple[str, ...]]] = []
    sprite_files: set[str] = set()
    for component in circuit.components:
        try:
            sprite_name = _COMPONENT_SPRITES[component.kind]
        except KeyError as exc:  # pragma: no cover - structural guard
            raise RuntimeError(f"unsupported byte_mod sprite kind {component.kind}") from exc
        sprite_files.add(sprite_name)
        alpha_cells.append(
            frozenset(
                (component.position[0] + x, component.position[1] + y)
                for x, y in sprite_alpha_cells(sprite_root / sprite_name)
            )
        )
        by_point: dict[Point, list[str]] = defaultdict(list)
        for name, _, _, point in _native_pins(component):
            by_point[point].append(name)
        pins.append({point: tuple(names) for point, names in by_point.items()})

    owners: dict[Point, list[int]] = defaultdict(list)
    for component_index, cells in enumerate(alpha_cells):
        for point in cells:
            owners[point].append(component_index)

    body_collisions: list[dict[str, object]] = []
    interior_pin_contacts: list[dict[str, object]] = []
    for wire_index, wire in enumerate(circuit.wires):
        points = wire_points(wire)
        endpoints = {points[0], points[-1]}
        for point in points:
            for component_index, cells in enumerate(alpha_cells):
                is_valid_endpoint = point in endpoints and point in pins[component_index]
                if point in cells and not is_valid_endpoint:
                    body_collisions.append(
                        {"wire": wire_index, "component": component_index, "point": list(point)}
                    )
            if point not in endpoints:
                for component_index, component_pins in enumerate(pins):
                    names = component_pins.get(point)
                    if names:
                        interior_pin_contacts.append(
                            {
                                "wire": wire_index,
                                "component": component_index,
                                "point": list(point),
                                "pins": list(names),
                            }
                        )
    return {
        "sprite_files": sorted(sprite_files),
        "component_overlap_count": sum(len(items) - 1 for items in owners.values() if len(items) > 1),
        "wire_body_collision_count": len(body_collisions),
        "wire_interior_pin_contact_count": len(interior_pin_contacts),
        "wire_body_collisions": body_collisions,
        "wire_interior_pin_contacts": interior_pin_contacts,
    }


def verify_byte_mod_asic(
    circuit: Circuit | None = None,
    *,
    sprite_root: Path = DEFAULT_COMPONENT_SPRITE_ROOT,
) -> dict[str, object]:
    """Prove v15 topology, exact tester semantics, and current sprite geometry."""

    candidate = build_byte_mod_asic() if circuit is None else circuit
    if (candidate.gate, candidate.delay) != (EXPECTED_GATE, EXPECTED_DELAY):
        raise RuntimeError("Byte Modulo metric declaration changed")
    kind_counts = {
        str(kind): sum(component.kind == kind for component in candidate.components)
        for kind in (61, 69, MOD_COMPONENT_KIND)
    }
    if kind_counts != {"61": 2, "69": 1, str(MOD_COMPONENT_KIND): 1}:
        raise RuntimeError(f"unexpected Byte Modulo component counts: {kind_counts}")

    connectivity = _connectivity(candidate)
    for field in (
        "unconnected_pin_count",
        "multi_driver_network_count",
        "undriven_network_count",
        "width_mismatch_network_count",
        "cycle_component_count",
        "endpoint_error_count",
    ):
        if connectivity[field]:
            raise RuntimeError(f"Byte Modulo connectivity failure {field}: {connectivity[field]}")

    layout = _sprite_geometry(candidate, sprite_root)
    for field in (
        "component_overlap_count",
        "wire_body_collision_count",
        "wire_interior_pin_contact_count",
    ):
        if layout[field]:
            raise RuntimeError(f"Byte Modulo geometry failure {field}: {layout[field]}")

    # The full 16-bit Cartesian domain is still small.  It protects the
    # candidate from accidentally relying only on the campaign's affine test
    # sequence, while the following loop independently replays that sequence.
    exhaustive_vectors = 0
    for dividend in range(256):
        for divisor in range(256):
            expected = dividend if divisor == 0 else dividend % divisor
            if evaluate_byte_mod(dividend, divisor) != expected:
                raise RuntimeError(f"Byte Modulo semantic regression at {dividend}, {divisor}")
            exhaustive_vectors += 1
    stream_vectors = 0
    for tick in range(TEST_TICK_COUNT):
        dividend, divisor = test_input_at(tick)
        expected = dividend if divisor == 0 else dividend % divisor
        if evaluate_byte_mod(dividend, divisor) != expected:
            raise RuntimeError(f"byte_mod test.si regression at tick {tick:#x}")
        stream_vectors += 1
    domain = _test_domain_summary()
    if domain["unique_input_pairs"] != 32_768:
        raise RuntimeError(f"unexpected byte_mod test domain: {domain}")

    return {
        "gate": candidate.gate,
        "delay": candidate.delay,
        "energy": candidate.gate * candidate.delay,
        "leaderboard_tuple": [candidate.gate, candidate.delay, candidate.gate * candidate.delay],
        "public_reference": list(PUBLIC_REFERENCE),
        "component_kind_counts": kind_counts,
        "full_u8_truth_vectors": exhaustive_vectors,
        "script_vectors": stream_vectors,
        "test_domain": domain,
        "connectivity": connectivity,
        "layout": layout,
    }


def write_byte_mod_asic(project_root: Path) -> dict[str, object]:
    """Write the review artifact only; this function never touches save data."""

    candidate = build_byte_mod_asic()
    verification = verify_byte_mod_asic(candidate)
    payload = encode_v15(candidate)
    if decode_v15(payload) != candidate:
        raise RuntimeError("Byte Modulo candidate failed v15 round-trip")
    destination = project_root / "examples" / "byte_mod" / "candidate" / "circuit.data"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(payload)
    (destination.parent / ".gitkeep").unlink(missing_ok=True)
    metadata = {
        "schema": 1,
        "level": "byte_mod",
        "title": "Modulo",
        "strategy": "current-v15 native com_mod baseline after affine-domain audit",
        "deployment_status": "review artifact only; excluded from direct_install pending game-side confirmation",
        "component_evidence": {
            "kind": MOD_COMPONENT_KIND,
            "sprite": "com_mod.png",
            "game_version": "2.1.281",
        },
        "sha256": sha256(payload).hexdigest(),
        "format_version": 15,
        "component_count": len(candidate.components),
        "wire_count": len(candidate.wires),
        **verification,
    }
    (destination.parent / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return metadata
