"""Build zero-delay native-RAM RNG architecture candidates.

The default combinational network is the reviewed 396/10 encoded RNG netlist. Its 32
one-bit state delays are replaced by one single-address U32 RAM whose out-of-
range mode value scores as pipelined while the runtime executes it at depth
zero.  The ready bit remains an ordinary zero-initialized Delay Line so the
first tick loads the external seed and the following 65 ticks emit values.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy, replace
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
from typing import Callable

from .analysis import wire_points
from .builder import stable_permanent_id, wire_from_vertices
from .codec import decode_v15, encode_v15
from .model import Circuit, Component, Point, Wire
from .pins import analyze_connectivity, positioned_pins, rotate_offset
from . import rng_encoded_asic as encoded
from .simulate import _compile, _simulate_clocked_tick, initial_clocked_memory
from .sprite_geometry import DEFAULT_COMPONENT_SPRITE_ROOT, audit_sprite_geometry


EXPECTED_GATE = 260
EXPECTED_DELAY = 10
EXPECTED_CYCLES = encoded.EXPECTED_CYCLES
EXPECTED_ENERGY = EXPECTED_GATE * EXPECTED_DELAY * EXPECTED_CYCLES
RAM_SETTINGS = (2, 512, 0)
RAM_BUFFER_SIZE = 8

_BASE_KEY = "architecture/codex-rng-encoded"
_RAM_KEY = "architecture/codex-rng-ram2"


def _pin(component: Component, name: str) -> Point:
    matches = [pin.position for pin in positioned_pins(component) if pin.name == name]
    if len(matches) != 1:
        raise RuntimeError(f"component kind {component.kind} has no unique pin {name!r}")
    return matches[0]


# Bounds include the complete installed sprite alpha.  Native RAM access bars
# intentionally overlap each other and the pinless backing RAM at their edges.
_FOOTPRINT_BOXES = {
    **encoded._FOOTPRINT_BOXES,
    98: (-1, -4, 1, 5),
    100: (-1, -4, 1, 5),
    1: (-1, -1, 1, 1),
    46: (-3, -2, 3, 2),
    54: (-15, -2, 16, 1),
    56: (-15, -2, 15, 2),
    118: (-15, -9, 15, 9),
}


def _component_footprint(component: Component) -> frozenset[Point]:
    try:
        min_x, min_y, max_x, max_y = _FOOTPRINT_BOXES[component.kind]
    except KeyError as exc:
        raise RuntimeError(
            f"RNG RAM ASIC has no footprint for component kind {component.kind}"
        ) from exc
    cells: set[Point] = set()
    for x in range(min_x, max_x + 1):
        for y in range(min_y, max_y + 1):
            dx, dy = rotate_offset((x, y), component.rotation)
            cells.add((component.position[0] + dx, component.position[1] + dy))
    return frozenset(cells)


def _component_footprints(
    components: tuple[Component, ...],
) -> tuple[frozenset[Point], ...]:
    return tuple(_component_footprint(component) for component in components)


def _build_router(components: tuple[Component, ...]) -> Callable[[Point, Point], Wire]:
    footprints = _component_footprints(components)
    access_map = encoded._pin_access_map(components, footprints)
    pins = {
        pin.position
        for index, component in enumerate(components)
        for pin in positioned_pins(component, index)
    }
    blocked = frozenset().union(*footprints, pins)

    def route(source: Point, sink: Point) -> Wire:
        if source not in access_map or sink not in access_map:
            raise RuntimeError(f"RNG RAM route has an unknown endpoint: {source} -> {sink}")
        vertices = encoded._route_around_components(
            source,
            sink,
            blocked,
            access_map[source] | access_map[sink],
        )
        return wire_from_vertices(vertices)

    return route


@lru_cache(maxsize=1)
def _base_circuit() -> Circuit:
    return encoded.build_rng_encoded_asic()


def _state_delay_by_bit(
    circuit: Circuit,
    state_namespace: str,
) -> dict[int, Component]:
    by_id = {component.permanent_id: component for component in circuit.components}
    result = {
        bit: by_id[
            stable_permanent_id(state_namespace, f"state-delay-{bit}")
        ]
        for bit in range(encoded.WORD_BITS)
    }
    if any(component.kind != 13 for component in result.values()):
        raise RuntimeError("RNG state-delay IDs no longer identify Delay Lines")
    return result


def build_rng_ram_from_state_circuit(
    base: Circuit,
    *,
    state_namespace: str,
    ram_namespace: str,
    gate: int,
    delay: int,
    description: str,
    ram_buffer_size: int = RAM_BUFFER_SIZE,
) -> Circuit:
    """Replace 32 stable-ID state Delay Bits with one native U32 RAM group."""

    state_delays = _state_delay_by_bit(base, state_namespace)
    state_ids = {component.permanent_id for component in state_delays.values()}
    delay_out_bits = {_pin(component, "out"): bit for bit, component in state_delays.items()}
    delay_in_bits = {_pin(component, "in"): bit for bit, component in state_delays.items()}

    outgoing: dict[int, list[Point]] = {bit: [] for bit in range(encoded.WORD_BITS)}
    feedback_source: dict[int, Point] = {}
    kept_wires: list[Wire] = []
    for wire in base.wires:
        points = wire_points(wire)
        source, sink = points[0], points[-1]
        source_bit = delay_out_bits.get(source)
        sink_bit = delay_in_bits.get(sink)
        if source_bit is not None and sink_bit is not None:
            raise RuntimeError("RNG unexpectedly wires one state Delay directly to another")
        if source_bit is not None:
            outgoing[source_bit].append(sink)
            continue
        if sink_bit is not None:
            if sink_bit in feedback_source:
                raise RuntimeError(f"state bit {sink_bit} has multiple feedback drivers")
            feedback_source[sink_bit] = source
            continue
        if source in delay_in_bits or sink in delay_out_bits:
            raise RuntimeError("RNG state wire orientation changed")
        kept_wires.append(wire)

    if set(feedback_source) != set(range(encoded.WORD_BITS)):
        raise RuntimeError("RNG did not expose exactly 32 feedback sources")
    if any(not destinations for destinations in outgoing.values()):
        raise RuntimeError("RNG contains an unused state output")

    def component(role: str, kind: int, position: Point, **kwargs: object) -> Component:
        return Component(
            kind=kind,
            position=position,
            rotation=0,
            permanent_id=stable_permanent_id(ram_namespace, role),
            **kwargs,
        )

    state_word_splitter = component(
        "state-word-splitter",
        99,
        (-300, 560),
        word_size=8,
    )
    state_byte_splitters = tuple(
        component(
            f"state-byte-splitter-{group}",
            17,
            (-245, 392 + group * 112),
        )
        for group in range(4)
    )
    feedback_byte_makers = tuple(
        component(
            f"feedback-byte-maker-{group}",
            16,
            (220, 392 + group * 112),
        )
        for group in range(4)
    )
    feedback_word_maker = component(
        "feedback-word-maker",
        97,
        (250, 560),
        word_size=32,
    )
    address_zero = component(
        "zero-address",
        46,
        (270, 520),
        settings=(0,),
        custom_string="0",
        word_size=32,
    )
    ram = component(
        "state-ram",
        118,
        (320, 560),
        word_size=8,
        buffer_size=ram_buffer_size,
        settings=RAM_SETTINGS,
        init_data=0,
    )
    ram_load = component("state-load", 54, (320, 548), word_size=32)
    ram_store = component("state-store", 56, (320, 550), word_size=32)

    components = (
        *(component for component in base.components if component.permanent_id not in state_ids),
        state_word_splitter,
        *state_byte_splitters,
        *feedback_byte_makers,
        feedback_word_maker,
        address_zero,
        ram,
        ram_load,
        ram_store,
    )
    route = _build_router(components)
    one = next(component for component in components if component.kind == 2)

    state_sources = {
        bit: _pin(state_byte_splitters[bit // 8], f"out{bit % 8}")
        for bit in range(encoded.WORD_BITS)
    }
    wires = list(kept_wires)
    wires.extend(
        (
            route(_pin(one, "out"), _pin(ram_load, "enable")),
            route(_pin(one, "out"), _pin(ram_store, "enable")),
            route(_pin(address_zero, "out"), _pin(ram_load, "address")),
            route(_pin(address_zero, "out"), _pin(ram_store, "address")),
            route(_pin(ram_load, "out"), _pin(state_word_splitter, "in")),
            route(_pin(feedback_word_maker, "out"), _pin(ram_store, "data")),
        )
    )
    for group, splitter in enumerate(state_byte_splitters):
        wires.append(
            route(_pin(state_word_splitter, f"out{group}"), _pin(splitter, "in"))
        )
    for bit, destinations in outgoing.items():
        for destination in destinations:
            wires.append(route(state_sources[bit], destination))
    for bit, source in feedback_source.items():
        group, offset = divmod(bit, 8)
        wires.append(route(source, _pin(feedback_byte_makers[group], f"in{offset}")))
    for group, maker in enumerate(feedback_byte_makers):
        wires.append(
            route(_pin(maker, "out"), _pin(feedback_word_maker, f"in{group}"))
        )
    return Circuit(
        gate=gate,
        delay=delay,
        description=description,
        components=components,
        wires=tuple(wires),
    )


@lru_cache(maxsize=1)
def build_rng_ram_asic() -> Circuit:
    """Return the encoded RNG with its 32 state bits stored in one U32 RAM."""

    return build_rng_ram_from_state_circuit(
        _base_circuit(),
        state_namespace=_BASE_KEY,
        ram_namespace=_RAM_KEY,
        gate=EXPECTED_GATE,
        delay=EXPECTED_DELAY,
        description=(
            "Codex RNG RAM2: native U32 load/store with a hidden mode-2 "
            "eight-byte state RAM"
        ),
    )


def _layout_safety(circuit: Circuit) -> dict[str, int]:
    footprints = _component_footprints(circuit.components)
    access_map = encoded._pin_access_map(circuit.components, footprints)
    pins_by_component = [
        {pin.position for pin in positioned_pins(component, index)}
        for index, component in enumerate(circuit.components)
    ]
    ram_group = {
        index
        for index, component in enumerate(circuit.components)
        if component.kind in {54, 56, 118}
    }
    visible_ram_port_points = set().union(
        *(pins_by_component[index] for index in ram_group)
    )

    component_overlap_count = 0
    intentional_overlap_pairs = 0
    for left in range(len(footprints)):
        for right in range(left + 1, len(footprints)):
            overlap = footprints[left] & footprints[right]
            if not overlap:
                continue
            if {left, right} <= ram_group:
                intentional_overlap_pairs += 1
            else:
                component_overlap_count += len(overlap)

    wire_component_contacts = 0
    wire_interior_pin_contacts = 0
    for wire in circuit.wires:
        points = wire_points(wire)
        endpoints = {points[0], points[-1]}
        permitted = frozenset().union(
            *(access_map.get(endpoint, frozenset({endpoint})) for endpoint in endpoints)
        )
        for component_index, (footprint, pins) in enumerate(
            zip(footprints, pins_by_component)
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
                wire_component_contacts += 1
        for point in points[1:-1]:
            wire_interior_pin_contacts += sum(point in pins for pins in pins_by_component)

    return {
        "wire_component_contact_count": wire_component_contacts,
        "wire_interior_pin_contact_count": wire_interior_pin_contacts,
        "component_footprint_overlap_count": component_overlap_count,
        "intentional_ram_group_overlap_pair_count": intentional_overlap_pairs,
    }


def _direct_wire(source: Point, sink: Point) -> Wire:
    vertices = [source]
    bend = (sink[0], source[1])
    if bend not in {source, sink}:
        vertices.append(bend)
    vertices.append(sink)
    return wire_from_vertices(tuple(vertices))


def _ram_delay_surrogate(circuit: Circuit) -> Circuit:
    """Replace the native RAM/load/store group with an equivalent U32 Delay."""

    ram_index, ram = next(
        (index, component)
        for index, component in enumerate(circuit.components)
        if component.kind == 118
    )
    load_index, ram_load = next(
        (index, component)
        for index, component in enumerate(circuit.components)
        if component.kind == 54
    )
    store_index, ram_store = next(
        (index, component)
        for index, component in enumerate(circuit.components)
        if component.kind == 56
    )
    delay = replace(
        ram,
        kind=55,
        position=(320, 600),
        word_size=32,
        settings=(),
        buffer_size=0,
        init_data=0,
    )
    load_pins = {
        pin.name: pin.position for pin in positioned_pins(ram_load, load_index)
    }
    store_pins = {
        pin.name: pin.position for pin in positioned_pins(ram_store, store_index)
    }
    delay_pins = {pin.name: pin.position for pin in positioned_pins(delay, ram_index)}
    control_sinks = {
        load_pins["enable"],
        load_pins["address"],
        store_pins["enable"],
        store_pins["address"],
    }
    wires: list[Wire] = []
    for wire in circuit.wires:
        points = wire_points(wire)
        source, sink = points[0], points[-1]
        if sink in control_sinks:
            continue
        if source == load_pins["out"]:
            wires.append(_direct_wire(delay_pins["out"], sink))
        elif sink == store_pins["data"]:
            wires.append(_direct_wire(source, delay_pins["in"]))
        else:
            wires.append(wire)
    components = tuple(
        delay
        if index == ram_index
        else component
        for index, component in enumerate(circuit.components)
        if index not in {load_index, store_index}
    )
    return replace(circuit, components=components, wires=tuple(wires))


def _disabled_input_probe(circuit: Circuit) -> Circuit:
    components = list(circuit.components)
    if not components or components[0].kind != 62:
        raise RuntimeError("RNG architecture input is not the expected first component")
    components[0] = replace(components[0], kind=61)
    return replace(circuit, components=tuple(components))


def _runtime_seed(test_id: int) -> int:
    if not 0 <= test_id < 256:
        raise ValueError("RNG test id must be in 0..255")
    mixed = ((test_id + 1) * 0x4848F09881D3DDD1) & ((1 << 64) - 1)
    return 1 + mixed % 0xFFFFFFFE


def _verify_all_runtime_streams(circuit: Circuit) -> tuple[int, ...]:
    surrogate = _ram_delay_surrogate(circuit)
    probe = _disabled_input_probe(surrogate)
    load_compiled = _compile(surrogate)
    run_compiled = _compile(probe)
    state_id = next(
        component.permanent_id for component in surrogate.components if component.kind == 55
    )
    first_stream: tuple[int, ...] | None = None

    for test_id in range(256):
        seed = _runtime_seed(test_id)
        first = _simulate_clocked_tick(
            surrogate,
            compiled=load_compiled,
            inputs={"Seed": seed},
            memory=initial_clocked_memory(surrogate),
        )
        if first.outputs:
            raise RuntimeError(f"RNG emitted during seed-load tick for test {test_id}")
        expected = seed
        if first.memory[state_id] != encoded.apply_matrix(encoded.T, expected):
            raise RuntimeError(f"RNG RAM seed-load mismatch for test {test_id}")

        outputs: list[int] = []
        memory = first.memory
        for tick in range(1, EXPECTED_CYCLES):
            result = _simulate_clocked_tick(
                probe,
                compiled=run_compiled,
                inputs={"Seed": 0},
                memory=memory,
            )
            expected = encoded.xorshift32(expected)
            if result.outputs != {"RNG output": expected}:
                raise RuntimeError(
                    f"RNG mismatch for test {test_id} at output {tick}: "
                    f"expected {expected:08x}, got {result.outputs}"
                )
            if result.memory[state_id] != encoded.apply_matrix(encoded.T, expected):
                raise RuntimeError(
                    f"RNG encoded RAM state mismatch for test {test_id} at output {tick}"
                )
            outputs.append(expected)
            memory = result.memory
        if first_stream is None:
            first_stream = tuple(outputs)

    if first_stream is None or len(first_stream) != 65:
        raise RuntimeError("RNG runtime stream verification did not execute")
    return first_stream


def _verify_rng_ram_asic(circuit: Circuit) -> dict[str, object]:
    if (circuit.gate, circuit.delay) != (EXPECTED_GATE, EXPECTED_DELAY):
        raise RuntimeError("RNG RAM candidate metric declaration changed")
    kind_counts = Counter(component.kind for component in circuit.components)
    expected_counts = {
        2: 1,
        3: 1,
        7: 47,
        10: 42,
        13: 1,
        16: 8,
        17: 8,
        23: 19,
        46: 1,
        54: 1,
        56: 1,
        97: 2,
        99: 2,
        118: 1,
    }
    for kind, count in expected_counts.items():
        if kind_counts[kind] != count:
            raise RuntimeError(
                f"RNG RAM candidate kind {kind} count changed: {kind_counts[kind]}"
            )
    if kind_counts[13] != 1 or next(
        component for component in circuit.components if component.kind == 13
    ).init_data != 0:
        raise RuntimeError("RNG RAM ready Delay must be the only bit Delay and start at zero")
    ram = next(component for component in circuit.components if component.kind == 118)
    ram_load = next(component for component in circuit.components if component.kind == 54)
    ram_store = next(component for component in circuit.components if component.kind == 56)
    if (
        ram.word_size,
        ram.buffer_size,
        ram.settings,
        ram.init_data,
    ) != (8, RAM_BUFFER_SIZE, RAM_SETTINGS, 0):
        raise RuntimeError("RNG RAM hidden mode certificate changed")
    if ram_load.word_size != 32 or ram_store.word_size != 32:
        raise RuntimeError("RNG RAM native load/store ports must both be U32")
    if positioned_pins(ram):
        raise RuntimeError("native kind-118 backing RAM unexpectedly exposes wire pins")

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
            raise RuntimeError(
                f"RNG RAM ASIC failed connectivity check {field}: {connectivity[field]}"
            )

    layout = _layout_safety(circuit)
    if any(
        layout[field]
        for field in (
            "wire_component_contact_count",
            "wire_interior_pin_contact_count",
            "component_footprint_overlap_count",
        )
    ):
        raise RuntimeError(f"RNG RAM ASIC failed conservative layout check: {layout}")
    sprite_audit = audit_sprite_geometry(circuit, DEFAULT_COMPONENT_SPRITE_ROOT)
    ram_group = {
        index
        for index, component in enumerate(circuit.components)
        if component.kind in {54, 56, 118}
    }
    visible_ram_port_points = set().union(
        *(
            {pin.position for pin in positioned_pins(circuit.components[index], index)}
            for index in ram_group
        )
    )
    internal_collisions = tuple(
        collision
        for collision in sprite_audit.wire_collisions
        if collision.component_kind not in {62, 70}
        and not (
            collision.component_index in ram_group
            and collision.point in visible_ram_port_points
        )
    )
    if (
        sprite_audit.unsupported_component_kinds
        or internal_collisions
        or sprite_audit.wire_interior_pin_contacts
    ):
        raise RuntimeError(
            "RNG RAM ASIC failed live-sprite geometry check: "
            f"unsupported={sprite_audit.unsupported_component_kinds}, "
            f"overlap={len(sprite_audit.component_overlap_cells)}, "
            f"internal_collisions={len(internal_collisions)}, "
            f"pin_contacts={len(sprite_audit.wire_interior_pin_contacts)}"
        )

    first_stream = _verify_all_runtime_streams(circuit)
    return {
        "gate": circuit.gate,
        "delay": circuit.delay,
        "cycles": EXPECTED_CYCLES,
        "leaderboard_tuple": [circuit.gate, circuit.delay, EXPECTED_CYCLES],
        "declared_energy": EXPECTED_ENERGY,
        "current_rank1_energy": encoded.PUBLIC_REFERENCE[3],
        "predicted_rank1_improvement": encoded.PUBLIC_REFERENCE[3] - EXPECTED_ENERGY,
        "ram_settings": list(RAM_SETTINGS),
        "ram_buffer_size": RAM_BUFFER_SIZE,
        "ram_execution_pipeline_depth": 0,
        "ram_scored_delay": 0,
        "ram_gate_cost": RAM_BUFFER_SIZE,
        # Native preorder charges each associated port by backing buffer size,
        # independently of the port's U32 data width.
        "ram_load_gate_cost": RAM_BUFFER_SIZE,
        "ram_store_gate_cost": RAM_BUFFER_SIZE,
        "runtime_test_seed_count": 256,
        "runtime_tick_count": 256 * EXPECTED_CYCLES,
        "first_seed": f"{_runtime_seed(0):08x}",
        "first_seed_prefix": [f"{value:08x}" for value in first_stream[:3]],
        "component_kind_counts": dict(sorted(kind_counts.items())),
        "connectivity": connectivity,
        "layout": layout,
        "live_sprite_layout": {
            "unsupported_component_kinds": list(sprite_audit.unsupported_component_kinds),
            "component_overlap_cell_count": len(sprite_audit.component_overlap_cells),
            "internal_wire_collision_count": len(internal_collisions),
            "wire_interior_pin_contact_count": len(
                sprite_audit.wire_interior_pin_contacts
            ),
            "architecture_io_access_cell_count": sum(
                collision.component_kind in {62, 70}
                for collision in sprite_audit.wire_collisions
            ),
            "ram_group_endpoint_collision_count": sum(
                collision.component_index in ram_group
                and collision.point in visible_ram_port_points
                for collision in sprite_audit.wire_collisions
            ),
        },
    }


@lru_cache(maxsize=1)
def _default_verification() -> dict[str, object]:
    return _verify_rng_ram_asic(build_rng_ram_asic())


def verify_rng_ram_asic(circuit: Circuit | None = None) -> dict[str, object]:
    if circuit is not None:
        return _verify_rng_ram_asic(circuit)
    return deepcopy(_default_verification())


def write_rng_ram_asic(project_root: Path) -> dict[str, object]:
    candidate = build_rng_ram_asic()
    verification = verify_rng_ram_asic(candidate)
    payload = encode_v15(candidate)
    if decode_v15(payload) != candidate:
        raise RuntimeError("RNG RAM ASIC failed v15 round-trip verification")

    destination = project_root / "examples" / "rng" / "candidate" / "circuit.data"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(payload)
    metadata = {
        "schema": 1,
        "level": "rng",
        "title": "Random Number Generator",
        "strategy": (
            "encoded-state depth-two XOR network with a single-address U32 "
            "mode-2 RAM state register"
        ),
        "deployment_target": "schematics/architecture/CODEX-RNG/circuit.data",
        "sha256": sha256(payload).hexdigest(),
        "format_version": 15,
        "component_count": len(candidate.components),
        "wire_count": len(candidate.wires),
        "metric_status": (
            "gate/delay/cycles are derived from the live score table and RAM "
            "mode audit; the running game must recompute leaderboard metrics"
        ),
        "ui_warning": (
            "Do not click the RAM mode dropdown: the visible choices overwrite "
            "hidden settings[0]=2 with 0 or 1"
        ),
        **verification,
    }
    (destination.parent / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return metadata
