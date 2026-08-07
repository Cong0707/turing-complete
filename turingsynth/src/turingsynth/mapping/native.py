"""Reviewed native component ABI and cost profile for Turing Complete 2.1.x.

Only components emitted by this compiler are listed here. Unknown kinds are a
hard error: geometry and pin contracts are never guessed during a build.
"""

from __future__ import annotations

from dataclasses import dataclass

from turingsynth.formats.design import DESIGN_ORIGIN, design_position, occupied_design_offsets
from turingsynth.formats.model import Circuit, Component, Point


INPUT = "input"
OUTPUT = "output"
TRISTATE = "output_tristate"


@dataclass(frozen=True)
class PinSpec:
    name: str
    direction: str
    offset: Point
    width: int | None = None
    permanent_id: int | None = None


@dataclass(frozen=True)
class PositionedPin:
    component_index: int
    component_kind: int
    name: str
    direction: str
    width: int
    position: Point


@dataclass(frozen=True)
class ComponentSpec:
    kind: int
    name: str
    pins: tuple[PinSpec, ...]
    bounds: tuple[int, int, int, int]


@dataclass(frozen=True)
class GateSpec:
    op: str
    scalar_kind: int
    word_kind: int
    cost_per_bit: int
    delay: int
    arity: int


def _pins(*values: PinSpec) -> tuple[PinSpec, ...]:
    return values


COMPONENTS: dict[int, ComponentSpec] = {
    1: ComponentSpec(1, "constant_zero", _pins(PinSpec("out", OUTPUT, (1, 0), 1)), (-1, 1, -1, 1)),
    2: ComponentSpec(2, "constant_one", _pins(PinSpec("out", OUTPUT, (1, 0), 1)), (-1, 1, -1, 1)),
    3: ComponentSpec(3, "not_bit", _pins(PinSpec("in", INPUT, (-1, 0), 1), PinSpec("out", OUTPUT, (2, 0), 1)), (-1, 2, -1, 1)),
    4: ComponentSpec(4, "and_bit", _pins(PinSpec("in0", INPUT, (-1, -1), 1), PinSpec("in1", INPUT, (-1, 1), 1), PinSpec("out", OUTPUT, (2, 0), 1)), (-1, 2, -2, 2)),
    6: ComponentSpec(6, "nand_bit", _pins(PinSpec("in0", INPUT, (-1, -1), 1), PinSpec("in1", INPUT, (-1, 1), 1), PinSpec("out", OUTPUT, (2, 0), 1)), (-1, 2, -2, 2)),
    7: ComponentSpec(7, "or_bit", _pins(PinSpec("in0", INPUT, (-1, -1), 1), PinSpec("in1", INPUT, (-1, 1), 1), PinSpec("out", OUTPUT, (2, 0), 1)), (-1, 2, -2, 2)),
    9: ComponentSpec(9, "nor_bit", _pins(PinSpec("in0", INPUT, (-1, -1), 1), PinSpec("in1", INPUT, (-1, 1), 1), PinSpec("out", OUTPUT, (2, 0), 1)), (-1, 2, -2, 2)),
    10: ComponentSpec(10, "xor_bit", _pins(PinSpec("in0", INPUT, (-1, -1), 1), PinSpec("in1", INPUT, (-1, 1), 1), PinSpec("out", OUTPUT, (2, 0), 1)), (-1, 2, -2, 2)),
    12: ComponentSpec(12, "switch_bit", _pins(PinSpec("enable", INPUT, (0, 1), 1), PinSpec("in", INPUT, (-1, 0), 1), PinSpec("out", TRISTATE, (2, 0), 1)), (-1, 2, -1, 1)),
    16: ComponentSpec(16, "maker_8", _pins(*(PinSpec(f"in{i}", INPUT, (-1, i - 3), 1) for i in range(8)), PinSpec("out", OUTPUT, (1, 0), 8)), (-1, 1, -4, 5)),
    17: ComponentSpec(17, "splitter_8", _pins(PinSpec("in", INPUT, (-1, 0), 8), *(PinSpec(f"out{i}", OUTPUT, (1, i - 3), 1) for i in range(8))), (-1, 1, -4, 5)),
    18: ComponentSpec(18, "not_word", _pins(PinSpec("in", INPUT, (-1, 0)), PinSpec("out", OUTPUT, (2, 0))), (-1, 2, -1, 1)),
    19: ComponentSpec(19, "or_word", _pins(PinSpec("in0", INPUT, (-1, -1)), PinSpec("in1", INPUT, (-1, 1)), PinSpec("out", OUTPUT, (2, 0))), (-1, 2, -2, 2)),
    20: ComponentSpec(20, "and_word", _pins(PinSpec("in0", INPUT, (-1, -1)), PinSpec("in1", INPUT, (-1, 1)), PinSpec("out", OUTPUT, (2, 0))), (-1, 2, -2, 2)),
    21: ComponentSpec(21, "nand_word", _pins(PinSpec("in0", INPUT, (-1, -1)), PinSpec("in1", INPUT, (-1, 1)), PinSpec("out", OUTPUT, (2, 0))), (-1, 2, -2, 2)),
    22: ComponentSpec(22, "nor_word", _pins(PinSpec("in0", INPUT, (-1, -1)), PinSpec("in1", INPUT, (-1, 1)), PinSpec("out", OUTPUT, (2, 0))), (-1, 2, -2, 2)),
    23: ComponentSpec(23, "xor_word", _pins(PinSpec("in0", INPUT, (-1, -1)), PinSpec("in1", INPUT, (-1, 1)), PinSpec("out", OUTPUT, (2, 0))), (-1, 2, -2, 2)),
    61: ComponentSpec(61, "campaign_input", _pins(PinSpec("value", OUTPUT, (3, 0))), (-3, 3, -2, 2)),
    69: ComponentSpec(69, "campaign_output", _pins(PinSpec("value", INPUT, (-3, 0))), (-3, 3, -2, 2)),
    79: ComponentSpec(79, "foundry_input", _pins(PinSpec("in", OUTPUT, (3, 0))), (-3, 3, -2, 2)),
    81: ComponentSpec(81, "foundry_output", _pins(PinSpec("out", INPUT, (-3, 0))), (-3, 3, -2, 2)),
    97: ComponentSpec(97, "maker_32", _pins(*(PinSpec(f"in{i}", INPUT, (-1, i - 1), 8) for i in range(4)), PinSpec("out", OUTPUT, (1, 0), 32)), (-1, 1, -2, 3)),
    98: ComponentSpec(98, "maker_64", _pins(*(PinSpec(f"in{i}", INPUT, (-1, i - 3), 8) for i in range(8)), PinSpec("out", OUTPUT, (1, 0), 64)), (-1, 1, -4, 5)),
    99: ComponentSpec(99, "splitter_32", _pins(PinSpec("in", INPUT, (-1, 0), 32), *(PinSpec(f"out{i}", OUTPUT, (1, i - 1), 8) for i in range(4))), (-1, 1, -2, 3)),
    100: ComponentSpec(100, "splitter_64", _pins(PinSpec("in", INPUT, (-1, 0), 64), *(PinSpec(f"out{i}", OUTPUT, (1, i - 3), 8) for i in range(8))), (-1, 1, -4, 5)),
    109: ComponentSpec(109, "splitter_2", _pins(PinSpec("in", INPUT, (-1, 0), 2), PinSpec("out0", OUTPUT, (1, -1), 1), PinSpec("out1", OUTPUT, (1, 0), 1)), (-1, 1, -2, 1)),
    110: ComponentSpec(110, "splitter_4", _pins(PinSpec("in", INPUT, (-1, 0), 4), *(PinSpec(f"out{i}", OUTPUT, (1, i - 1), 1) for i in range(4))), (-1, 1, -2, 3)),
    111: ComponentSpec(111, "maker_2", _pins(PinSpec("in0", INPUT, (-1, -1), 1), PinSpec("in1", INPUT, (-1, 0), 1), PinSpec("out", OUTPUT, (1, 0), 2)), (-1, 1, -2, 1)),
    112: ComponentSpec(112, "maker_4", _pins(*(PinSpec(f"in{i}", INPUT, (-1, i - 1), 1) for i in range(4)), PinSpec("out", OUTPUT, (1, 0), 4)), (-1, 1, -2, 3)),
}


CUSTOM_COMPONENTS: dict[int, ComponentSpec] = {}


def configure_custom_components(circuits: tuple[Circuit, ...]) -> None:
    """Install deterministic kind-78 geometry for the current compiler build."""

    CUSTOM_COMPONENTS.clear()
    for circuit in circuits:
        if circuit.custom_id <= 0 or circuit.custom_id in CUSTOM_COMPONENTS:
            raise ValueError(f"invalid or duplicate Custom identity {circuit.custom_id}")
        pins = []
        input_index = 0
        output_index = 0
        for port in circuit.components:
            if port.kind not in {79, 81}:
                continue
            grid_x, grid_y = design_position(port.position)
            offset = (
                grid_x - DESIGN_ORIGIN[0],
                grid_y - DESIGN_ORIGIN[1],
            )
            if port.kind == 79:
                fallback = f"in{input_index}"
                input_index += 1
                direction = INPUT
            else:
                fallback = f"out{output_index}"
                output_index += 1
                direction = OUTPUT
            pins.append(
                PinSpec(
                    port.user_label or fallback,
                    direction,
                    offset,
                    port.word_size,
                    port.permanent_id,
                )
            )
        if not pins:
            raise ValueError(f"Custom circuit {circuit.custom_id} has no interface ports")
        if len({pin.name for pin in pins}) != len(pins):
            raise ValueError(f"Custom circuit {circuit.custom_id} has duplicate port labels")
        occupied = occupied_design_offsets(circuit)
        xs = [point[0] for point in occupied]
        ys = [point[1] for point in occupied]
        bounds = min(xs), max(xs), min(ys), max(ys)
        if any(
            not (bounds[0] <= pin.offset[0] <= bounds[1])
            or not (bounds[2] <= pin.offset[1] <= bounds[3])
            for pin in pins
        ):
            raise ValueError(f"Custom circuit {circuit.custom_id} has a port outside its design")
        CUSTOM_COMPONENTS[circuit.custom_id] = ComponentSpec(
            78,
            f"custom_{circuit.custom_id}",
            tuple(pins),
            bounds,
        )


def component_spec(component: Component) -> ComponentSpec:
    if component.kind == 78:
        try:
            return CUSTOM_COMPONENTS[component.custom_id]
        except KeyError as exc:
            raise ValueError(
                f"Custom component {component.custom_id} has no registered geometry"
            ) from exc
    try:
        return COMPONENTS[component.kind]
    except KeyError as exc:
        raise ValueError(f"unsupported component kind {component.kind}") from exc


GATE_LIBRARY: dict[str, GateSpec] = {
    "NOT": GateSpec("NOT", 3, 18, 1, 1, 1),
    "AND": GateSpec("AND", 4, 20, 1, 1, 2),
    "NAND": GateSpec("NAND", 6, 21, 1, 1, 2),
    "OR": GateSpec("OR", 7, 19, 1, 1, 2),
    "NOR": GateSpec("NOR", 9, 22, 1, 1, 2),
    "XOR": GateSpec("XOR", 10, 23, 3, 2, 2),
}


PACK_WIDTHS = (8, 4, 2, 1)
MAKER_KIND = {2: 111, 4: 112, 8: 16, 32: 97, 64: 98}
SPLITTER_KIND = {2: 109, 4: 110, 8: 17, 32: 99, 64: 100}


def rotate_offset(offset: Point, rotation: int) -> Point:
    x, y = offset
    transforms = ((x, y), (-y, x), (-x, -y), (y, -x))
    if not 0 <= rotation < 4:
        raise ValueError(f"invalid component rotation {rotation}")
    return transforms[rotation]


def positioned_pins(
    component: Component, component_index: int = 0
) -> tuple[PositionedPin, ...]:
    spec = component_spec(component)
    word_overrides = dict(component.custom_word_sizes)
    result = []
    for pin in spec.pins:
        dx, dy = rotate_offset(pin.offset, component.rotation)
        result.append(
            PositionedPin(
                component_index=component_index,
                component_kind=component.kind,
                name=pin.name,
                direction=pin.direction,
                width=(
                    word_overrides.get(pin.permanent_id, pin.width)
                    if pin.permanent_id is not None
                    else (component.word_size if pin.width is None else pin.width)
                ),
                position=(component.position[0] + dx, component.position[1] + dy),
            )
        )
    return tuple(result)


def component_bounds(component: Component) -> tuple[int, int, int, int]:
    left, right, top, bottom = component_spec(component).bounds
    corners = tuple(
        rotate_offset(point, component.rotation)
        for point in ((left, top), (left, bottom), (right, top), (right, bottom))
    )
    xs = [component.position[0] + point[0] for point in corners]
    ys = [component.position[1] + point[1] for point in corners]
    return min(xs), max(xs), min(ys), max(ys)
