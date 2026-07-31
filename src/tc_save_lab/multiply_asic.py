"""Build and audit the current v15 U8 low-byte multiplier candidate.

``com_mul`` is a current-game primitive, not a legacy architecture component.
The installed 2.1.x executable exposes it as ``TC_Mul (in0, in1, out)`` with
``assign out = in0 * in1``.  Its single output is masked to the component
word width, which is exactly the
``(A * B) & 0xff`` contract of the Multiply level.

The shared pin table intentionally leaves kind 31 unsupported until it has a
general current-version evidence source.  This module therefore owns the
small, evidence-backed schema required for this one candidate instead of
loosening global validation for every caller.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from pathlib import Path
from .analysis import wire_points
from .builder import stable_permanent_id, wire_from_vertices
from .codec import decode_v15, encode_v15
from .model import Circuit, Component, Point
from .pins import I, O, positioned_pins, rotate_offset
from .sprite_geometry import (
    DEFAULT_COMPONENT_SPRITE_ROOT,
    sprite_alpha_cells,
)


LEVEL = "multiply"
MULTIPLIER_KIND = 31
WORD_SIZE = 8
DECLARED_GATE = 230
DECLARED_DELAY = 11
MULTIPLIER_SPRITE = "com_mul.png"


@dataclass(frozen=True)
class CandidatePin:
    component_index: int
    component_kind: int
    permanent_id: int
    name: str
    direction: str
    width: int
    position: Point


@dataclass(frozen=True)
class ConnectivityAudit:
    pin_count: int
    connected_pin_count: int
    unconnected_inputs: tuple[CandidatePin, ...]
    multi_driver_network_count: int
    undriven_network_count: int
    sinkless_network_count: int
    width_mismatch_network_count: int
    endpoint_non_pin_count: int


@dataclass(frozen=True)
class GeometryAudit:
    sprite_files: tuple[str, ...]
    alpha_cell_count: int
    component_overlap_cells: tuple[Point, ...]
    wire_component_collisions: tuple[tuple[int, int, Point], ...]
    wire_interior_pin_contacts: tuple[tuple[int, int, Point], ...]
    endpoint_non_pin_count: int


@dataclass(frozen=True)
class _CompiledCandidate:
    pins: tuple[CandidatePin, ...]
    pin_networks: dict[tuple[int, str], int]
    network_pins: dict[int, tuple[CandidatePin, ...]]


class MultiplyAsicError(ValueError):
    """The local multiplier evidence or candidate topology is inconsistent."""


class _UnionFind:
    def __init__(self, size: int) -> None:
        self.parent = list(range(size))

    def find(self, value: int) -> int:
        while self.parent[value] != value:
            self.parent[value] = self.parent[self.parent[value]]
            value = self.parent[value]
        return value

    def union(self, left: int, right: int) -> None:
        left = self.find(left)
        right = self.find(right)
        if left != right:
            self.parent[right] = left


def _immutable_components(project_root: Path) -> tuple[Component, ...]:
    path = project_root / "examples" / LEVEL / "scaffold" / "immutable.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    records = []
    for raw in data["immutable_components"]:
        record = dict(raw)
        record.pop("role", None)
        records.append(record)
    components = Circuit.from_dict({"components": records}).components
    if len(components) != 3 or not all(component.immutable for component in components):
        raise MultiplyAsicError("Multiply immutable scaffold is not the expected A/B/Result interface")
    labels = tuple(component.user_label for component in components)
    if labels != ("A", "B", "Result"):
        raise MultiplyAsicError(f"unexpected Multiply immutable labels: {labels!r}")
    return components


def build_multiply_circuit(project_root: Path) -> Circuit:
    """Return the reviewed U8 lower-product candidate for the Multiply level."""

    immutable = _immutable_components(Path(project_root))
    multiplier = Component(
        kind=MULTIPLIER_KIND,
        position=(0, -5),
        rotation=0,
        permanent_id=stable_permanent_id("multiply/asic", "u8-low-product"),
        word_size=WORD_SIZE,
    )
    # The coordinates are intentionally sparse.  Every segment has been
    # checked against the current alpha masks, including the wide MUL sprite.
    wires = (
        wire_from_vertices(((-19, -12), (-13, -6), (-1, -6))),
        wire_from_vertices(((-19, 5), (-2, 5), (-2, -4), (-1, -4))),
        wire_from_vertices(((2, -5), (20, -5))),
    )
    return Circuit(
        gate=DECLARED_GATE,
        delay=DECLARED_DELAY,
        description="Codex U8 low-byte multiplier using the current native MUL primitive.",
        components=immutable + (multiplier,),
        wires=wires,
    )


def _multiplier_pins(component: Component, component_index: int) -> tuple[CandidatePin, ...]:
    if component.kind != MULTIPLIER_KIND:
        raise MultiplyAsicError(f"expected multiplier kind {MULTIPLIER_KIND}, got {component.kind}")
    if component.word_size != WORD_SIZE:
        raise MultiplyAsicError(f"Multiply candidate requires U8 MUL, got U{component.word_size}")
    offsets = (
        ("in0", I, (-1, -1)),
        ("in1", I, (-1, 1)),
        ("out", O, (2, 0)),
    )
    return tuple(
        CandidatePin(
            component_index=component_index,
            component_kind=component.kind,
            permanent_id=component.permanent_id,
            name=name,
            direction=direction,
            width=component.word_size,
            position=(
                component.position[0] + rotate_offset(offset, component.rotation)[0],
                component.position[1] + rotate_offset(offset, component.rotation)[1],
            ),
        )
        for name, direction, offset in offsets
    )


def _candidate_pins(circuit: Circuit) -> tuple[CandidatePin, ...]:
    pins: list[CandidatePin] = []
    for component_index, component in enumerate(circuit.components):
        if component.kind == MULTIPLIER_KIND:
            pins.extend(_multiplier_pins(component, component_index))
            continue
        if component.kind not in {61, 69}:
            raise MultiplyAsicError(f"unexpected component kind in Multiply candidate: {component.kind}")
        for pin in positioned_pins(component, component_index):
            pins.append(
                CandidatePin(
                    component_index=component_index,
                    component_kind=component.kind,
                    permanent_id=component.permanent_id,
                    name=pin.name,
                    direction=pin.direction,
                    width=pin.width,
                    position=pin.position,
                )
            )
    return tuple(pins)


def _compile_candidate(circuit: Circuit) -> _CompiledCandidate:
    pins = _candidate_pins(circuit)
    endpoints = []
    owners: dict[Point, list[int]] = defaultdict(list)
    for wire_index, wire in enumerate(circuit.wires):
        points = wire_points(wire)
        endpoint_pair = (points[0], points[-1])
        endpoints.append(endpoint_pair)
        owners[endpoint_pair[0]].append(wire_index)
        owners[endpoint_pair[1]].append(wire_index)

    union_find = _UnionFind(len(circuit.wires))
    for wire_indices in owners.values():
        for wire_index in wire_indices[1:]:
            union_find.union(wire_indices[0], wire_index)

    network_by_position: dict[Point, int] = {}
    for wire_index, endpoint_pair in enumerate(endpoints):
        network = union_find.find(wire_index)
        for endpoint in endpoint_pair:
            network_by_position[endpoint] = network

    pin_networks: dict[tuple[int, str], int] = {}
    network_pins: dict[int, list[CandidatePin]] = defaultdict(list)
    for pin in pins:
        network = network_by_position.get(pin.position)
        if network is None:
            continue
        key = (pin.component_index, pin.name)
        if key in pin_networks:
            raise MultiplyAsicError(f"duplicate pin key: {key!r}")
        pin_networks[key] = network
        network_pins[network].append(pin)

    return _CompiledCandidate(
        pins=pins,
        pin_networks=pin_networks,
        network_pins={network: tuple(values) for network, values in network_pins.items()},
    )


def audit_connectivity(circuit: Circuit) -> ConnectivityAudit:
    """Check endpoint-only logical connectivity for this reviewed component set."""

    compiled = _compile_candidate(circuit)
    pin_positions = {pin.position for pin in compiled.pins}
    endpoint_non_pin_count = sum(
        endpoint not in pin_positions
        for wire in circuit.wires
        for endpoint in (wire_points(wire)[0], wire_points(wire)[-1])
    )
    unconnected_inputs = tuple(
        pin
        for pin in compiled.pins
        if pin.direction == I and (pin.component_index, pin.name) not in compiled.pin_networks
    )
    multi_driver_network_count = 0
    undriven_network_count = 0
    sinkless_network_count = 0
    width_mismatch_network_count = 0
    for network in compiled.network_pins.values():
        drivers = [pin for pin in network if pin.direction == O]
        receivers = [pin for pin in network if pin.direction == I]
        if len(drivers) > 1:
            multi_driver_network_count += 1
        if not drivers:
            undriven_network_count += 1
        if not receivers:
            sinkless_network_count += 1
        if len({pin.width for pin in network}) > 1:
            width_mismatch_network_count += 1
    return ConnectivityAudit(
        pin_count=len(compiled.pins),
        connected_pin_count=len(compiled.pin_networks),
        unconnected_inputs=unconnected_inputs,
        multi_driver_network_count=multi_driver_network_count,
        undriven_network_count=undriven_network_count,
        sinkless_network_count=sinkless_network_count,
        width_mismatch_network_count=width_mismatch_network_count,
        endpoint_non_pin_count=endpoint_non_pin_count,
    )


def _sprite_name(component: Component) -> str:
    names = {
        61: "com_level_input_word.png",
        69: "com_level_output_word.png",
        MULTIPLIER_KIND: MULTIPLIER_SPRITE,
    }
    try:
        return names[component.kind]
    except KeyError as exc:  # pragma: no cover - _candidate_pins rejects first
        raise MultiplyAsicError(f"no reviewed current sprite for kind {component.kind}") from exc


def audit_geometry(
    circuit: Circuit,
    *,
    sprite_root: Path = DEFAULT_COMPONENT_SPRITE_ROOT,
) -> GeometryAudit:
    """Use installed alpha masks while allowing only exact endpoint contacts."""

    pins = _candidate_pins(circuit)
    pins_by_component: dict[int, set[Point]] = defaultdict(set)
    pins_at_position: dict[Point, set[int]] = defaultdict(set)
    for pin in pins:
        pins_by_component[pin.component_index].add(pin.position)
        pins_at_position[pin.position].add(pin.component_index)

    alpha_owners: dict[Point, list[int]] = defaultdict(list)
    sprite_files: set[str] = set()
    for component_index, component in enumerate(circuit.components):
        sprite_name = _sprite_name(component)
        sprite_files.add(sprite_name)
        for cell in sprite_alpha_cells(sprite_root / sprite_name):
            dx, dy = rotate_offset(cell, component.rotation)
            alpha_owners[(component.position[0] + dx, component.position[1] + dy)].append(component_index)

    component_overlap_cells = tuple(
        sorted(point for point, owners in alpha_owners.items() if len(owners) > 1)
    )
    wire_component_collisions: list[tuple[int, int, Point]] = []
    wire_interior_pin_contacts: list[tuple[int, int, Point]] = []
    endpoint_non_pin_count = 0
    for wire_index, wire in enumerate(circuit.wires):
        points = wire_points(wire)
        endpoints = {points[0], points[-1]}
        for endpoint in endpoints:
            if endpoint not in pins_at_position:
                endpoint_non_pin_count += 1
        for point in points:
            for component_index in alpha_owners.get(point, ()):
                if point in endpoints and point in pins_by_component[component_index]:
                    continue
                wire_component_collisions.append((wire_index, component_index, point))
            if point not in endpoints:
                for component_index in pins_at_position.get(point, ()):
                    wire_interior_pin_contacts.append((wire_index, component_index, point))
    return GeometryAudit(
        sprite_files=tuple(sorted(sprite_files)),
        alpha_cell_count=sum(len(owners) for owners in alpha_owners.values()),
        component_overlap_cells=component_overlap_cells,
        wire_component_collisions=tuple(wire_component_collisions),
        wire_interior_pin_contacts=tuple(wire_interior_pin_contacts),
        endpoint_non_pin_count=endpoint_non_pin_count,
    )


def _require_clean_audits(circuit: Circuit) -> _CompiledCandidate:
    connectivity = audit_connectivity(circuit)
    if connectivity.unconnected_inputs:
        raise MultiplyAsicError(f"unconnected inputs: {connectivity.unconnected_inputs!r}")
    for field in (
        "multi_driver_network_count",
        "undriven_network_count",
        "sinkless_network_count",
        "width_mismatch_network_count",
        "endpoint_non_pin_count",
    ):
        if getattr(connectivity, field):
            raise MultiplyAsicError(f"connectivity audit failed {field}: {getattr(connectivity, field)}")
    geometry = audit_geometry(circuit)
    for field in (
        "component_overlap_cells",
        "wire_component_collisions",
        "wire_interior_pin_contacts",
        "endpoint_non_pin_count",
    ):
        if getattr(geometry, field):
            raise MultiplyAsicError(f"geometry audit failed {field}: {getattr(geometry, field)!r}")
    return _compile_candidate(circuit)


def _find_unique_component(circuit: Circuit, *, kind: int | None = None, label: str | None = None) -> int:
    matches = [
        index
        for index, component in enumerate(circuit.components)
        if (kind is None or component.kind == kind)
        and (label is None or component.user_label == label)
    ]
    if len(matches) != 1:
        raise MultiplyAsicError(f"expected one component kind={kind!r}, label={label!r}; got {matches!r}")
    return matches[0]


def _network_value(compiled: _CompiledCandidate, component_index: int, pin_name: str, values: dict[int, int]) -> int:
    try:
        network = compiled.pin_networks[(component_index, pin_name)]
        return values[network]
    except KeyError as exc:
        raise MultiplyAsicError(f"missing driven network for component {component_index} pin {pin_name}") from exc


def _compile_evaluator(circuit: Circuit) -> tuple[_CompiledCandidate, int, int, int, int]:
    """Resolve the fixed component indexes once for a full truth-table run."""

    compiled = _require_clean_audits(circuit)
    input_a = _find_unique_component(circuit, kind=61, label="A")
    input_b = _find_unique_component(circuit, kind=61, label="B")
    multiplier = _find_unique_component(circuit, kind=MULTIPLIER_KIND)
    result = _find_unique_component(circuit, kind=69, label="Result")
    return compiled, input_a, input_b, multiplier, result


def _evaluate_compiled(
    compiled: _CompiledCandidate,
    input_a: int,
    input_b: int,
    multiplier: int,
    result: int,
    a: int,
    b: int,
) -> int:
    """Evaluate one vector through the candidate's compiled endpoint graph."""

    if not 0 <= a <= 0xFF or not 0 <= b <= 0xFF:
        raise ValueError("Multiply candidate inputs must be U8")
    network_values: dict[int, int] = {}

    def drive(component_index: int, pin_name: str, value: int) -> None:
        network = compiled.pin_networks[(component_index, pin_name)]
        prior = network_values.get(network)
        if prior is not None and prior != value:
            raise MultiplyAsicError(f"conflicting drivers on network {network}")
        network_values[network] = value & 0xFF

    drive(input_a, "value", a)
    drive(input_b, "value", b)
    product = (
        _network_value(compiled, multiplier, "in0", network_values)
        * _network_value(compiled, multiplier, "in1", network_values)
    ) & 0xFF
    drive(multiplier, "out", product)
    return _network_value(compiled, result, "value", network_values)


def simulate_multiply(circuit: Circuit, a: int, b: int) -> int:
    """Evaluate the candidate from its wires and reviewed current ``TC_Mul`` semantics."""

    return _evaluate_compiled(*_compile_evaluator(circuit), a, b)


def verify_multiply_truth_table(circuit: Circuit) -> int:
    """Exhaustively prove the U8 lower-product contract with bounded memory."""

    compiled, input_a, input_b, multiplier, result = _compile_evaluator(circuit)
    network_a = compiled.pin_networks[(input_a, "value")]
    network_b = compiled.pin_networks[(input_b, "value")]
    network_in0 = compiled.pin_networks[(multiplier, "in0")]
    network_in1 = compiled.pin_networks[(multiplier, "in1")]
    network_out = compiled.pin_networks[(multiplier, "out")]
    network_result = compiled.pin_networks[(result, "value")]
    if (network_a, network_b, network_out) != (network_in0, network_in1, network_result):
        raise MultiplyAsicError("A/B/MUL/Result network topology does not match the reviewed contract")
    tested = 0
    for a in range(256):
        for b in range(256):
            actual = _evaluate_compiled(
                compiled, input_a, input_b, multiplier, result, a, b
            )
            expected = (a * b) & 0xFF
            if actual != expected:
                raise MultiplyAsicError(f"truth-table mismatch for A={a}, B={b}: {actual} != {expected}")
            tested += 1
    return tested


def candidate_metadata(circuit: Circuit) -> dict[str, object]:
    payload = encode_v15(circuit)
    connectivity = audit_connectivity(circuit)
    geometry = audit_geometry(circuit)
    metadata = {
        "level": LEVEL,
        "title_zh": "乘法器",
        "format_version": 15,
        "strategy": "current native U8 MUL; only its lower U8 output is wired to Result",
        "metrics": {"gate": circuit.gate, "delay": circuit.delay, "energy": circuit.energy},
        "component_count": len(circuit.components),
        "wire_count": len(circuit.wires),
        "sha256": sha256(payload).hexdigest(),
        "truth_table_vectors": 65536,
        "connectivity": {
            **asdict(connectivity),
            "unconnected_inputs": [asdict(pin) for pin in connectivity.unconnected_inputs],
        },
        "geometry": asdict(geometry),
        "evidence": {
            "component_kind": MULTIPLIER_KIND,
            "runtime_module": "TC_Mul (in0, in1, out); assign out = in0 * in1;",
            "runtime_sprite": MULTIPLIER_SPRITE,
            "source": "Turing Complete 2.1.x installed executable at 0xA4CAC8 and live v15 schematic endpoints",
        },
    }
    # Keep the in-memory return value byte-for-byte comparable to the emitted
    # JSON artifact: dataclass tuples become JSON arrays here, not only on disk.
    return json.loads(json.dumps(metadata, ensure_ascii=False))


def write_candidate(project_root: Path) -> dict[str, object]:
    """Generate the reviewed candidate artifacts under ``examples/multiply``."""

    root = Path(project_root)
    circuit = build_multiply_circuit(root)
    if decode_v15(encode_v15(circuit)) != circuit:
        raise MultiplyAsicError("v15 round trip failed")
    if verify_multiply_truth_table(circuit) != 65536:
        raise MultiplyAsicError("unexpected truth-table vector count")
    metadata = candidate_metadata(circuit)
    directory = root / "examples" / LEVEL / "candidate"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "circuit.data").write_bytes(encode_v15(circuit))
    (directory / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return metadata
