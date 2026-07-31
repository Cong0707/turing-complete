"""Build and verify compact current-version primitive level candidates.

These candidates deliberately use native current-game components rather than
expanding them into obsolete tutorial constructions.  They retain each level's
campaign-owned immutable I/O from ``scaffold/immutable.json`` and only replace
the mutable circuit area.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path

from .analysis import wire_points
from .builder import stable_permanent_id, wire_from_vertices
from .codec import decode_v15, encode_v15
from .model import Circuit, Component, Point
from .pins import analyze_connectivity, positioned_pins, rotate_offset
from .simulate import _compile, verify_truth_table


PRIMITIVE_LEVELS = (
    "byte_adder",
    "count_leading_zeroes",
    "saving_gracefully",
    "saving_bytes",
)


@dataclass(frozen=True)
class PrimitiveLevel:
    title: str
    title_zh: str
    gate: int
    delay: int
    strategy_zh: str

    @property
    def energy(self) -> int:
        return self.gate * self.delay


PRIMITIVES: dict[str, PrimitiveLevel] = {
    "byte_adder": PrimitiveLevel(
        title="Adding Bytes",
        title_zh="字节加法器",
        gate=103,
        delay=5,
        strategy_zh="使用原生 U8 加法器，保留独立的进位输入与进位输出。",
    ),
    "count_leading_zeroes": PrimitiveLevel(
        title="Count leading zeroes",
        title_zh="前导零计数器",
        gate=22,
        delay=4,
        strategy_zh="使用原生 U8 前导零计数器。",
    ),
    "saving_gracefully": PrimitiveLevel(
        title="Saving Gracefully",
        title_zh="位寄存器",
        gate=10,
        delay=5,
        strategy_zh="使用原生单位置位寄存器，输出保持上一拍状态。",
    ),
    "saving_bytes": PrimitiveLevel(
        title="Saving Bytes",
        title_zh="字寄存器",
        gate=73,
        delay=5,
        strategy_zh="使用原生 U8 字寄存器，并用 On 元件持续打开三态输出。",
    ),
}


# These masks intentionally cover only unquestionably occupied cells.  Pin
# cells remain outside the mask, so a wire may terminate at a legal pin while
# still being rejected if it traverses a component body or another pin.
BODY_MASKS: dict[int, frozenset[Point]] = {
    2: frozenset({(0, 0)}),
    14: frozenset((x, y) for x in range(-2, 3) for y in range(-2, 3)),
    30: frozenset((0, y) for y in range(-1, 2)),
    39: frozenset((0, y) for y in range(-1, 2)),
    49: frozenset((x, y) for x in range(0, 2) for y in range(-1, 2)),
    60: frozenset({(0, 0)}),
    61: frozenset((x, y) for x in range(-2, 3) for y in range(-1, 2)),
    68: frozenset({(0, 0)}),
    69: frozenset((x, y) for x in range(-2, 3) for y in range(-1, 2)),
}


SAVING_GRACEFULLY_INPUTS: tuple[tuple[int, int], ...] = (
    (1, 1),
    (1, 1),
    (1, 0),
    (1, 0),
    (0, 0),
    (0, 1),
    (1, 0),
    (1, 1),
    (1, 1),
    (0, 1),
    (0, 0),
    (1, 0),
    (1, 0),
)
SAVING_GRACEFULLY_OUTPUTS = (0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0)


def _require_level(level: str) -> PrimitiveLevel:
    try:
        return PRIMITIVES[level]
    except KeyError as exc:
        raise ValueError(f"unsupported primitive candidate level: {level!r}") from exc


def _scaffold_components(project_root: Path, level: str) -> tuple[Component, ...]:
    path = project_root / "examples" / level / "scaffold" / "immutable.json"
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"missing immutable scaffold for {level}: {path}") from exc
    components = []
    for raw_component in record.get("immutable_components", []):
        component = dict(raw_component)
        component.pop("role", None)
        components.append(component)
    immutable = Circuit.from_dict({"components": components}).components
    if not immutable or not all(component.immutable for component in immutable):
        raise RuntimeError(f"primitive candidate {level} has an invalid immutable scaffold")
    ids = [component.permanent_id for component in immutable]
    if len(ids) != len(set(ids)) or 0 in ids:
        raise RuntimeError(f"primitive candidate {level} has duplicate immutable IDs")
    return immutable


def _component(level: str, role: str, kind: int, position: Point, **kwargs: object) -> Component:
    return Component(
        kind=kind,
        position=position,
        rotation=0,
        permanent_id=stable_permanent_id(f"primitive/{level}", role),
        **kwargs,
    )


def _assert_unique_ids(components: tuple[Component, ...]) -> None:
    ids = [component.permanent_id for component in components]
    if 0 in ids or len(ids) != len(set(ids)):
        raise RuntimeError("primitive candidate contains missing or duplicate permanent IDs")


def build_primitive_circuit(project_root: Path, level: str) -> Circuit:
    """Return the deterministic v15 candidate for one compact normal level."""

    project_root = Path(project_root)
    primitive = _require_level(level)
    immutable = _scaffold_components(project_root, level)

    if level == "byte_adder":
        mutable = (
            _component(level, "adder", 30, (0, 0), word_size=8),
        )
        wires = (
            wire_from_vertices(((-17, -12), (-3, -12), (-3, -1), (-1, -1))),
            wire_from_vertices(((-17, -4), (-5, -4), (-5, 0), (-1, 0))),
            wire_from_vertices(((-17, 4), (-4, 4), (-4, 1), (-1, 1))),
            wire_from_vertices(((1, -1), (5, -1), (5, -4), (18, -4))),
            wire_from_vertices(((1, 0), (7, 0), (7, 4), (18, 4))),
        )
    elif level == "count_leading_zeroes":
        mutable = (
            _component(level, "clz", 49, (0, -4), word_size=8),
        )
        wires = (
            wire_from_vertices(((-25, -4), (-1, -4))),
            wire_from_vertices(((2, -4), (26, -4))),
        )
    elif level == "saving_gracefully":
        mutable = (
            _component(level, "register-bit", 14, (0, 0), word_size=1),
        )
        wires = (
            wire_from_vertices(((-14, -2), (-7, -2), (-7, -3), (-3, -3))),
            wire_from_vertices(((-14, 2), (-8, 2), (-8, 0), (-3, 0))),
            wire_from_vertices(((3, 0), (14, 0))),
        )
    elif level == "saving_bytes":
        mutable = (
            _component(level, "output-enable", 2, (-8, -6)),
            _component(level, "register-word", 39, (0, 0), word_size=8),
        )
        # The campaign-owned Save source has a one-cell output at (-15, -3).
        # The older baseline happens to place its embedded copy differently,
        # so candidate routing is derived from the current immutable scaffold.
        wires = (
            wire_from_vertices(((-7, -6), (-4, -6), (-4, -1), (-1, -1))),
            wire_from_vertices(((-15, -3), (-5, -3), (-5, 0), (-1, 0))),
            wire_from_vertices(((-13, 3), (-6, 3), (-6, 1), (-1, 1))),
            wire_from_vertices(((1, 0), (7, 0), (7, 3), (15, 3))),
        )
    else:  # pragma: no cover - _require_level and branches keep this exhaustive
        raise AssertionError(level)

    components = immutable + mutable
    _assert_unique_ids(components)
    return Circuit(
        gate=primitive.gate,
        delay=primitive.delay,
        description=f"Codex {primitive.title}: {primitive.strategy_zh}",
        components=components,
        wires=wires,
    )


def _pin(component: Component, name: str) -> Point:
    matches = [pin.position for pin in positioned_pins(component) if pin.name == name]
    if len(matches) != 1:
        raise RuntimeError(
            f"component kind {component.kind} lacks one unambiguous pin named {name!r}"
        )
    return matches[0]


def _component_index(circuit: Circuit, permanent_id: int) -> int:
    matches = [
        index
        for index, component in enumerate(circuit.components)
        if component.permanent_id == permanent_id
    ]
    if len(matches) != 1:
        raise RuntimeError(f"expected exactly one component with permanent ID {permanent_id}")
    return matches[0]


def _labeled_component_index(circuit: Circuit, label: str) -> int:
    matches = [
        index
        for index, component in enumerate(circuit.components)
        if component.user_label == label
    ]
    if len(matches) != 1:
        raise RuntimeError(f"expected exactly one component labeled {label!r}")
    return matches[0]


def _body_points(component: Component) -> frozenset[Point]:
    try:
        offsets = BODY_MASKS[component.kind]
    except KeyError as exc:
        raise RuntimeError(
            f"primitive physical audit has no body mask for kind {component.kind}"
        ) from exc
    result = set()
    for offset in offsets:
        dx, dy = rotate_offset(offset, component.rotation)
        result.add((component.position[0] + dx, component.position[1] + dy))
    return frozenset(result)


def layout_safety(circuit: Circuit) -> dict[str, int]:
    """Audit endpoint-only pin access without treating wire crossings as faults."""

    bodies = tuple(_body_points(component) for component in circuit.components)
    pin_positions = {
        pin.position
        for index, component in enumerate(circuit.components)
        for pin in positioned_pins(component, index)
    }
    body_owners = Counter(point for body in bodies for point in body)
    result = {
        "wire_endpoint_non_pin_count": 0,
        "wire_component_contact_count": 0,
        "wire_interior_pin_contact_count": 0,
        "component_body_overlap_count": sum(
            count - 1 for count in body_owners.values() if count > 1
        ),
    }
    for wire in circuit.wires:
        points = wire_points(wire)
        endpoints = (points[0], points[-1])
        result["wire_endpoint_non_pin_count"] += sum(
            endpoint not in pin_positions for endpoint in endpoints
        )
        for point in points:
            result["wire_component_contact_count"] += sum(
                point in body for body in bodies
            )
        result["wire_interior_pin_contact_count"] += sum(
            point in pin_positions for point in points[1:-1]
        )
    return result


def _require_clean_connectivity(circuit: Circuit) -> dict[str, object]:
    connectivity = analyze_connectivity(circuit)
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
            raise RuntimeError(
                f"primitive candidate failed connectivity check {field}: "
                f"{connectivity[field]}"
            )
    return connectivity


def _require_same_network(
    circuit: Circuit,
    left: tuple[int, str],
    right: tuple[int, str],
) -> None:
    compiled = _compile(circuit)
    if compiled.pin_networks[left] != compiled.pin_networks[right]:
        raise RuntimeError(f"expected connected pins {left!r} and {right!r}")


def _verify_register_bit_topology(circuit: Circuit, level: str) -> None:
    register = _component_index(
        circuit, stable_permanent_id(f"primitive/{level}", "register-bit")
    )
    _require_same_network(
        circuit, (_labeled_component_index(circuit, "Save"), "value"), (register, "save")
    )
    _require_same_network(
        circuit, (_labeled_component_index(circuit, "Value"), "value"), (register, "in")
    )
    _require_same_network(
        circuit, (register, "out"), (_labeled_component_index(circuit, "Output"), "value")
    )


def _verify_register_word_topology(circuit: Circuit, level: str) -> None:
    register = _component_index(
        circuit, stable_permanent_id(f"primitive/{level}", "register-word")
    )
    enable = _component_index(
        circuit, stable_permanent_id(f"primitive/{level}", "output-enable")
    )
    _require_same_network(circuit, (enable, "out"), (register, "load"))
    _require_same_network(
        circuit, (_labeled_component_index(circuit, "Save"), "value"), (register, "save")
    )
    _require_same_network(
        circuit, (_labeled_component_index(circuit, "Input"), "value"), (register, "in")
    )
    _require_same_network(
        circuit, (register, "out"), (_labeled_component_index(circuit, "Output"), "value")
    )


def _bit_register_tick(memory: int, save: int, value: int) -> tuple[int, int]:
    if memory not in (0, 1) or save not in (0, 1) or value not in (0, 1):
        raise ValueError("bit-register values must be U1")
    return memory, value if save else memory


def _word_register_tick(memory: int, save: int, value: int) -> tuple[int, int]:
    if not 0 <= memory <= 0xFF or not 0 <= value <= 0xFF or save not in (0, 1):
        raise ValueError("word-register state must be U8 and save must be U1")
    return memory, value if save else memory


def _verify_saving_gracefully_semantics() -> dict[str, int]:
    memory = 0
    observed = []
    for save, value in SAVING_GRACEFULLY_INPUTS:
        output, memory = _bit_register_tick(memory, save, value)
        observed.append(output)
    if tuple(observed) != SAVING_GRACEFULLY_OUTPUTS:
        raise RuntimeError(f"Saving Gracefully sequence mismatch: {observed!r}")

    transition_count = 0
    for memory in range(2):
        for save in range(2):
            for value in range(2):
                output, next_memory = _bit_register_tick(memory, save, value)
                if output != memory or next_memory != (value if save else memory):
                    raise RuntimeError("bit-register state-transition mismatch")
                transition_count += 1
    return {
        "script_tick_count": len(SAVING_GRACEFULLY_INPUTS),
        "exhaustive_state_transition_count": transition_count,
    }


def _verify_saving_bytes_semantics() -> dict[str, int]:
    transition_count = 0
    for memory in range(256):
        for save in range(2):
            for value in range(256):
                output, next_memory = _word_register_tick(memory, save, value)
                if output != memory or next_memory != (value if save else memory):
                    raise RuntimeError("word-register state-transition mismatch")
                transition_count += 1
    return {"exhaustive_state_transition_count": transition_count}


def verify_primitive_candidate(circuit: Circuit, level: str) -> dict[str, object]:
    """Validate metrics, topology, geometry and complete primitive semantics."""

    primitive = _require_level(level)
    if (circuit.gate, circuit.delay) != (primitive.gate, primitive.delay):
        raise RuntimeError(
            f"{level} header changed: {(circuit.gate, circuit.delay)!r} != "
            f"{(primitive.gate, primitive.delay)!r}"
        )
    if decode_v15(encode_v15(circuit)) != circuit:
        raise RuntimeError(f"{level} failed v15 codec round-trip verification")
    connectivity = _require_clean_connectivity(circuit)
    layout = layout_safety(circuit)
    if any(layout.values()):
        raise RuntimeError(f"primitive candidate has unsafe wire geometry: {layout}")

    semantic: dict[str, int]
    if level == "byte_adder":
        tested = verify_truth_table(
            circuit,
            inputs={"A": 8, "B": 8, "Carry in": 1},
            output_label=("Output", "Carry out"),
            expected=lambda values: {
                "Output": (values["A"] + values["B"] + values["Carry in"]) & 0xFF,
                "Carry out": (values["A"] + values["B"] + values["Carry in"]) >> 8,
            },
        )
        semantic = {"exhaustive_truth_table_vector_count": tested}
    elif level == "count_leading_zeroes":
        tested = verify_truth_table(
            circuit,
            inputs={"Input": 8},
            output_label="Result",
            expected=lambda values: (
                8 if values["Input"] == 0 else 8 - values["Input"].bit_length()
            ),
        )
        semantic = {"exhaustive_truth_table_vector_count": tested}
    elif level == "saving_gracefully":
        _verify_register_bit_topology(circuit, level)
        semantic = _verify_saving_gracefully_semantics()
    elif level == "saving_bytes":
        _verify_register_word_topology(circuit, level)
        semantic = _verify_saving_bytes_semantics()
    else:  # pragma: no cover - _require_level and branches keep this exhaustive
        raise AssertionError(level)

    kind_counts = Counter(component.kind for component in circuit.components)
    return {
        "gate": circuit.gate,
        "delay": circuit.delay,
        "energy": primitive.energy,
        "leaderboard_tuple": [circuit.gate, circuit.delay, primitive.energy],
        "v15_round_trip_verified": True,
        "component_kind_counts": dict(sorted(kind_counts.items())),
        "connectivity": connectivity,
        "layout": layout,
        "semantic": semantic,
    }


def write_primitive_candidate(project_root: Path, level: str) -> dict[str, object]:
    """Write one reviewed candidate under its example directory, never a save file."""

    project_root = Path(project_root)
    primitive = _require_level(level)
    circuit = build_primitive_circuit(project_root, level)
    verification = verify_primitive_candidate(circuit, level)
    payload = encode_v15(circuit)
    if decode_v15(payload) != circuit:
        raise RuntimeError(f"{level} failed v15 codec round-trip verification")

    destination = project_root / "examples" / level / "candidate" / "circuit.data"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(payload)
    (destination.parent / ".gitkeep").unlink(missing_ok=True)
    metadata = {
        "schema": 1,
        "level": level,
        "title": primitive.title,
        "title_zh": primitive.title_zh,
        "strategy": primitive.strategy_zh,
        "validation_status": "已完成离线穷举、状态转换、v15 往返、连通性和物理几何审计；待游戏内验收。",
        "deployment_target": f"schematics/{level}/Default/circuit.data",
        "sha256": sha256(payload).hexdigest(),
        "format_version": 15,
        "component_count": len(circuit.components),
        "wire_count": len(circuit.wires),
        **verification,
    }
    (destination.parent / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return metadata


def write_primitive_candidates(
    project_root: Path,
    levels: tuple[str, ...] = PRIMITIVE_LEVELS,
) -> dict[str, dict[str, object]]:
    """Write a selected deterministic subset of ordinary primitive candidates."""

    return {
        level: write_primitive_candidate(project_root, level)
        for level in levels
    }
