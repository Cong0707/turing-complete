"""Deterministic circuit construction primitives and reviewed recipes."""

from __future__ import annotations

from dataclasses import dataclass, replace
from hashlib import sha256
from pathlib import Path
import json

from .analysis import analyze_examples
from .codec import decode_v15, encode_v15
from .model import Circuit, Component, Point, Wire
from .pins import analyze_connectivity
from .simulate import verify_truth_table


DIRECTION_BY_STEP = {
    (1, 0): 0,
    (1, 1): 1,
    (0, 1): 2,
    (-1, 1): 3,
    (-1, 0): 4,
    (-1, -1): 5,
    (0, -1): 6,
    (1, -1): 7,
}


@dataclass(frozen=True)
class Recipe:
    level: str
    declared_gate: int
    declared_delay: int
    build: object
    inputs: tuple[tuple[str, int], ...]
    output_label: str
    expected: object


def stable_permanent_id(level: str, name: str) -> int:
    digest = sha256(f"tc-save-lab:{level}:{name}".encode("utf-8")).digest()
    value = int.from_bytes(digest[:8], "little") & ((1 << 63) - 1)
    return value or 1


def wire_from_vertices(
    vertices: tuple[Point, ...],
    *,
    color: int = 0,
    comment: str = "",
) -> Wire:
    if len(vertices) < 2:
        raise ValueError("a routed wire needs at least two vertices")
    segments: list[tuple[int, int]] = []
    for start, end in zip(vertices, vertices[1:]):
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = max(abs(dx), abs(dy))
        if length == 0:
            continue
        if dx and dy and abs(dx) != abs(dy):
            raise ValueError(f"wire segment is not horizontal, vertical, or 45 degree: {start} -> {end}")
        step = (0 if dx == 0 else dx // abs(dx), 0 if dy == 0 else dy // abs(dy))
        direction = DIRECTION_BY_STEP[step]
        if segments and segments[-1][0] == direction:
            previous_direction, previous_length = segments[-1]
            segments[-1] = (previous_direction, previous_length + length)
        else:
            segments.append((direction, length))
    if not segments:
        raise ValueError("wire route has zero length")
    return Wire(color=color, comment=comment, start=vertices[0], segments=tuple(segments))


def _load_scaffold_components(project_root: Path, level: str) -> tuple[Component, ...]:
    path = project_root / "examples" / level / "scaffold" / "immutable.json"
    data = json.loads(path.read_text("utf-8"))
    records = []
    for component in data["immutable_components"]:
        component = dict(component)
        component.pop("role", None)
        records.append(component)
    return Circuit.from_dict({"components": records}).components


def _triple_input_two_gate(project_root: Path, level: str, kind: int) -> tuple[tuple[Component, ...], tuple[Wire, ...]]:
    scaffold = _load_scaffold_components(project_root, level)
    components = scaffold + (
        Component(kind, (-5, -1), 0, stable_permanent_id(level, "first")),
        Component(kind, (3, 0), 0, stable_permanent_id(level, "second")),
    )
    wires = (
        wire_from_vertices(((-13, -1), (-7, -1), (-6, -2))),
        wire_from_vertices(((-13, 0), (-6, 0))),
        wire_from_vertices(((-3, -1), (2, -1))),
        wire_from_vertices(((-13, 1), (2, 1))),
        wire_from_vertices(((5, 0), (12, 0))),
    )
    return components, wires


def _xnor(project_root: Path, level: str) -> tuple[tuple[Component, ...], tuple[Wire, ...]]:
    scaffold = _load_scaffold_components(project_root, level)
    components = scaffold + (
        Component(4, (-5, -2), 0, stable_permanent_id(level, "and")),
        Component(9, (-5, 2), 0, stable_permanent_id(level, "nor")),
        Component(7, (4, 0), 0, stable_permanent_id(level, "or")),
    )
    wires = (
        wire_from_vertices(((-13, -1), (-11, -3), (-6, -3))),
        wire_from_vertices(((-13, -1), (-11, 1), (-6, 1))),
        wire_from_vertices(((-13, 1), (-11, -1), (-6, -1))),
        wire_from_vertices(((-13, 1), (-11, 3), (-6, 3))),
        wire_from_vertices(((-3, -2), (2, -2), (3, -1))),
        wire_from_vertices(((-3, 2), (2, 2), (3, 1))),
        wire_from_vertices(((6, 0), (12, 0))),
    )
    return components, wires


def _bit_inverter(project_root: Path, level: str) -> tuple[tuple[Component, ...], tuple[Wire, ...]]:
    scaffold = _load_scaffold_components(project_root, level)
    components = scaffold + (
        Component(10, (0, 0), 0, stable_permanent_id(level, "xor")),
    )
    wires = (
        wire_from_vertices(((-13, -1), (-1, -1))),
        wire_from_vertices(((-13, 1), (-1, 1))),
        wire_from_vertices(((2, 0), (12, 0))),
    )
    return components, wires


def _bit_adder(project_root: Path, level: str) -> tuple[tuple[Component, ...], tuple[Wire, ...]]:
    scaffold = _load_scaffold_components(project_root, level)
    components = scaffold + (
        Component(4, (-4, 3), 0, stable_permanent_id(level, "and")),
        Component(9, (-4, -3), 0, stable_permanent_id(level, "nor-inputs")),
        Component(9, (4, -3), 0, stable_permanent_id(level, "nor-sum")),
    )
    wires = (
        wire_from_vertices(((-13, -3), (-6, -3), (-5, -4))),
        wire_from_vertices(((-13, -3), (-10, -3), (-5, 2))),
        wire_from_vertices(((-13, 3), (-10, 3), (-5, -2))),
        wire_from_vertices(((-13, 3), (-6, 3), (-5, 4))),
        wire_from_vertices(((-2, -3), (2, -3), (3, -4))),
        wire_from_vertices(((-2, 3), (3, -2))),
        wire_from_vertices(((-2, 3), (8, 3))),
        wire_from_vertices(((6, -3), (8, -3))),
    )
    return components, wires


def _counting_signals(project_root: Path, level: str) -> tuple[tuple[Component, ...], tuple[Wire, ...]]:
    scaffold = _load_scaffold_components(project_root, level)
    components = scaffold + (
        Component(4, (-10, -9), 0, stable_permanent_id(level, "ab-and")),
        Component(9, (-10, -5), 0, stable_permanent_id(level, "ab-nor")),
        Component(9, (-4, -7), 0, stable_permanent_id(level, "ab-sum")),
        Component(4, (-10, 5), 0, stable_permanent_id(level, "cd-and")),
        Component(9, (-10, 9), 0, stable_permanent_id(level, "cd-nor")),
        Component(9, (-4, 7), 0, stable_permanent_id(level, "cd-sum")),
        Component(4, (1, -2), 0, stable_permanent_id(level, "pq-and")),
        Component(9, (1, 2), 0, stable_permanent_id(level, "pq-nor")),
        Component(9, (7, 0), 0, stable_permanent_id(level, "bit-0")),
        Component(4, (1, 7), 0, stable_permanent_id(level, "gh-and")),
        Component(9, (1, 11), 0, stable_permanent_id(level, "gh-nor")),
        Component(9, (7, 9), 0, stable_permanent_id(level, "gh-sum")),
        Component(7, (11, 5), 0, stable_permanent_id(level, "bit-1")),
    )
    wires = (
        wire_from_vertices(((-14, -2), (-13, -3), (-13, -8), (-11, -10))),
        wire_from_vertices(((-14, -2), (-13, -3), (-13, -4), (-11, -6))),
        wire_from_vertices(((-14, -1), (-12, -3), (-12, -7), (-11, -8))),
        wire_from_vertices(((-14, -1), (-11, -4))),
        wire_from_vertices(((-14, 0), (-13, 1), (-13, 2), (-11, 4))),
        wire_from_vertices(((-14, 0), (-12, 2), (-12, 7), (-11, 8))),
        wire_from_vertices(((-14, 1), (-13, 2), (-13, 4), (-11, 6))),
        wire_from_vertices(((-14, 1), (-12, 3), (-12, 9), (-11, 10))),
        wire_from_vertices(((-8, -9), (-6, -9), (-5, -8))),
        wire_from_vertices(((-8, -5), (-6, -5), (-5, -6))),
        wire_from_vertices(((-8, 5), (-6, 5), (-5, 6))),
        wire_from_vertices(((-8, 9), (-6, 9), (-5, 8))),
        wire_from_vertices(((-2, -7), (-1, -6), (-1, -4), (0, -3))),
        wire_from_vertices(((-2, -7), (-3, -6), (-3, -1), (-1, 1), (0, 1))),
        wire_from_vertices(((-2, 7), (-1, 6), (-1, 0), (0, -1))),
        wire_from_vertices(((-2, 7), (0, 5), (0, 3))),
        wire_from_vertices(((3, -2), (5, -2), (6, -1))),
        wire_from_vertices(((3, 2), (5, 2), (6, 1))),
        wire_from_vertices(((3, -2), (4, -1), (4, 0), (8, 4), (10, 4))),
        wire_from_vertices(((-8, -9), (-7, -8), (-7, -1), (0, 6))),
        wire_from_vertices(((-8, -9), (-6, -7), (-6, 4), (0, 10))),
        wire_from_vertices(((-8, 5), (-5, 8), (0, 8))),
        wire_from_vertices(((-8, 5), (-7, 6), (-7, 7), (-2, 12), (0, 12))),
        wire_from_vertices(((3, 7), (5, 7), (6, 8))),
        wire_from_vertices(((3, 11), (5, 11), (6, 10))),
        wire_from_vertices(((9, 9), (10, 8), (10, 6))),
        wire_from_vertices(((9, 0), (11, 0), (12, -1), (14, -1))),
        wire_from_vertices(((13, 5), (14, 4), (14, 0))),
        wire_from_vertices(((3, 7), (4, 7), (10, 1), (14, 1))),
    )
    return components, wires


def _decoder_1(project_root: Path, level: str) -> tuple[tuple[Component, ...], tuple[Wire, ...]]:
    scaffold = _load_scaffold_components(project_root, level)
    components = scaffold + (
        Component(3, (0, 0), 0, stable_permanent_id(level, "not")),
    )
    wires = (
        wire_from_vertices(((-12, 0), (-1, 0))),
        wire_from_vertices(((-12, 0), (-12, 1), (12, 1), (12, 0))),
        wire_from_vertices(((2, 0), (11, 0), (12, -1))),
    )
    return components, wires


def _byte_mux(project_root: Path, level: str) -> tuple[tuple[Component, ...], tuple[Wire, ...]]:
    scaffold = _load_scaffold_components(project_root, level)
    components = scaffold + (
        Component(42, (0, 0), 0, stable_permanent_id(level, "mux"), word_size=8),
    )
    wires = (
        wire_from_vertices(((-14, -3), (-3, -3), (-1, -1))),
        wire_from_vertices(((-12, 0), (-1, 0))),
        wire_from_vertices(((-12, 3), (-3, 3), (-1, 1))),
        wire_from_vertices(((2, 0), (12, 0))),
    )
    return components, wires


def _byte_xor(project_root: Path, level: str) -> tuple[tuple[Component, ...], tuple[Wire, ...]]:
    scaffold = _load_scaffold_components(project_root, level)
    components = scaffold + (
        Component(23, (0, 1), 0, stable_permanent_id(level, "xor"), word_size=8),
    )
    wires = (
        wire_from_vertices(((-13, -4), (-4, -4), (-1, -1), (-1, 0))),
        wire_from_vertices(((-13, 6), (-5, 6), (-1, 2))),
        wire_from_vertices(((2, 1), (15, 1))),
    )
    return components, wires


def _byte_not(project_root: Path, level: str) -> tuple[tuple[Component, ...], tuple[Wire, ...]]:
    scaffold = _load_scaffold_components(project_root, level)
    components = scaffold + (
        Component(18, (0, 0), 0, stable_permanent_id(level, "not"), word_size=8),
    )
    wires = (
        wire_from_vertices(((-12, 0), (-1, 0))),
        wire_from_vertices(((2, 0), (12, 0))),
    )
    return components, wires


def _byte_nand(project_root: Path, level: str) -> tuple[tuple[Component, ...], tuple[Wire, ...]]:
    scaffold = _load_scaffold_components(project_root, level)
    components = scaffold + (
        Component(21, (0, 0), 0, stable_permanent_id(level, "nand"), word_size=8),
    )
    wires = (
        wire_from_vertices(((-12, -3), (-3, -3), (-1, -1))),
        wire_from_vertices(((-12, 3), (-3, 3), (-1, 1))),
        wire_from_vertices(((2, 0), (12, 0))),
    )
    return components, wires


def _byte_equal(project_root: Path, level: str) -> tuple[tuple[Component, ...], tuple[Wire, ...]]:
    scaffold = _load_scaffold_components(project_root, level)
    components = scaffold + (
        Component(26, (0, 0), 0, stable_permanent_id(level, "equal"), word_size=8),
    )
    wires = (
        wire_from_vertices(((-13, -5), (-5, -5), (-1, -1))),
        wire_from_vertices(((-13, 5), (-5, 5), (-1, 1))),
        wire_from_vertices(((2, 0), (15, 0))),
    )
    return components, wires


def _byte_less_u(project_root: Path, level: str) -> tuple[tuple[Component, ...], tuple[Wire, ...]]:
    scaffold = _load_scaffold_components(project_root, level)
    components = scaffold + (
        Component(27, (0, 0), 0, stable_permanent_id(level, "less-u"), word_size=8),
    )
    wires = (
        wire_from_vertices(((-11, -5), (-5, -5), (-1, -1))),
        wire_from_vertices(((-11, 5), (-5, 5), (-1, 1))),
        wire_from_vertices(((2, 0), (15, 0))),
    )
    return components, wires


def _byte_asr(project_root: Path, level: str) -> tuple[tuple[Component, ...], tuple[Wire, ...]]:
    scaffold = _load_scaffold_components(project_root, level)
    components = scaffold + (
        Component(37, (0, 0), 0, stable_permanent_id(level, "asr"), word_size=8),
    )
    wires = (
        wire_from_vertices(((-17, -10), (-1, -10), (-1, -1))),
        wire_from_vertices(((-17, 9), (-1, 9), (-1, 1))),
        wire_from_vertices(((2, 0), (17, 0))),
    )
    return components, wires


def _byte_constant(project_root: Path, level: str) -> tuple[tuple[Component, ...], tuple[Wire, ...]]:
    scaffold = _load_scaffold_components(project_root, level)
    components = scaffold + (
        Component(
            46,
            (0, 0),
            0,
            stable_permanent_id(level, "constant-164"),
            word_size=8,
            init_data=164,
        ),
    )
    wires = (wire_from_vertices(((3, 0), (22, 0))),)
    return components, wires


def _decoder_2(project_root: Path, level: str) -> tuple[tuple[Component, ...], tuple[Wire, ...]]:
    scaffold = _load_scaffold_components(project_root, level)
    components = scaffold + (
        Component(44, (0, -1), 0, stable_permanent_id(level, "decoder")),
    )
    wires = (
        wire_from_vertices(((-11, -1), (-3, -1), (-2, -2), (-1, -2))),
        wire_from_vertices(((-11, 1), (-3, 1), (-1, -1))),
        *(wire_from_vertices(((1, y), (12, y))) for y in range(-2, 2)),
    )
    return components, wires


def _decoder_3(project_root: Path, level: str) -> tuple[tuple[Component, ...], tuple[Wire, ...]]:
    scaffold = _load_scaffold_components(project_root, level)
    components = scaffold + (
        Component(45, (0, -2), 0, stable_permanent_id(level, "decoder")),
    )
    wires = (
        wire_from_vertices(((-11, -5), (-1, -5))),
        wire_from_vertices(((-11, -4), (-1, -4))),
        wire_from_vertices(((-11, -3), (-1, -3))),
        wire_from_vertices(((-11, 1), (-7, 1), (0, -6))),
        *(wire_from_vertices(((1, y), (11, y))) for y in range(-5, 3)),
    )
    return components, wires


def _signed_negator(project_root: Path, level: str) -> tuple[tuple[Component, ...], tuple[Wire, ...]]:
    scaffold = _load_scaffold_components(project_root, level)
    components = scaffold + (
        Component(29, (0, 0), 0, stable_permanent_id(level, "negator"), word_size=8),
    )
    wires = (
        wire_from_vertices(((-12, 0), (-1, 0))),
        wire_from_vertices(((2, 0), (12, 0))),
    )
    return components, wires


def _signed_negator_low_gate(
    project_root: Path,
    level: str,
) -> tuple[tuple[Component, ...], tuple[Wire, ...]]:
    scaffold = _load_scaffold_components(project_root, level)
    identity = f"{level}:low-gate"
    components = [
        *scaffold,
        Component(17, (-9, 0), 0, stable_permanent_id(identity, "splitter")),
        Component(16, (9, 0), 0, stable_permanent_id(identity, "merger")),
    ]
    stage_y: dict[int, int] = {}
    for bit in range(1, 8):
        base_y = (bit - 4) * 8
        stage_y[bit] = base_y
        components.extend(
            (
                Component(7, (0, base_y), 0, stable_permanent_id(identity, f"carry-{bit}")),
                Component(6, (0, base_y + 4), 0, stable_permanent_id(identity, f"nand-{bit}")),
                Component(4, (5, base_y + 2), 0, stable_permanent_id(identity, f"xor-{bit}")),
            )
        )

    wires = [
        wire_from_vertices(((-12, 0), (-10, 0))),
        wire_from_vertices(((-8, -3), (8, -3))),
        wire_from_vertices(((10, 0), (12, 0))),
    ]
    for bit in range(1, 8):
        base_y = stage_y[bit]
        bit_source = (-8, bit - 3)
        and_bit = (-1, base_y - 1)
        nor_bit = (-1, base_y + 3)
        bit_lane_and = -12 - bit
        bit_lane_nor = -24 - bit
        wires.extend(
            (
                wire_from_vertices(
                    (
                        bit_source,
                        (bit_lane_and, bit_source[1]),
                        (bit_lane_and, and_bit[1]),
                        and_bit,
                    )
                ),
                wire_from_vertices(
                    (
                        bit_source,
                        (bit_lane_nor, bit_source[1]),
                        (bit_lane_nor, nor_bit[1]),
                        nor_bit,
                    )
                ),
            )
        )

        carry_source = (-8, -3) if bit == 1 else (2, stage_y[bit - 1])
        and_carry = (-1, base_y + 1)
        nor_carry = (-1, base_y + 5)
        carry_lane_and = -38 - bit * 2
        carry_lane_nor = carry_lane_and - 1
        wires.extend(
            (
                wire_from_vertices(
                    (
                        carry_source,
                        (carry_lane_and, carry_source[1]),
                        (carry_lane_and, and_carry[1]),
                        and_carry,
                    )
                ),
                wire_from_vertices(
                    (
                        carry_source,
                        (carry_lane_nor, carry_source[1]),
                        (carry_lane_nor, nor_carry[1]),
                        nor_carry,
                    )
                ),
                wire_from_vertices(((2, base_y), (3, base_y), (4, base_y + 1))),
                wire_from_vertices(
                    ((2, base_y + 4), (3, base_y + 4), (4, base_y + 3))
                ),
            )
        )

        merger_input = (8, bit - 3)
        output_lane = 8 + bit
        wires.append(
            wire_from_vertices(
                (
                    (7, base_y + 2),
                    (output_lane, base_y + 2),
                    (output_lane, merger_input[1]),
                    merger_input,
                )
            )
        )
    return tuple(components), tuple(wires)


def _byte_less_s(project_root: Path, level: str) -> tuple[tuple[Component, ...], tuple[Wire, ...]]:
    scaffold = _load_scaffold_components(project_root, level)
    components = scaffold + (
        Component(46, (-9, -4), 0, stable_permanent_id(level, "constant-a"), word_size=8, init_data=0x80),
        Component(23, (-3, -5), 0, stable_permanent_id(level, "xor-a"), word_size=8),
        Component(46, (-9, 6), 0, stable_permanent_id(level, "constant-b"), word_size=8, init_data=0x80),
        Component(23, (-3, 5), 0, stable_permanent_id(level, "xor-b"), word_size=8),
        Component(27, (5, 0), 0, stable_permanent_id(level, "unsigned-less"), word_size=8),
    )
    wires = (
        wire_from_vertices(((-12, -6), (-4, -6))),
        wire_from_vertices(((-6, -4), (-4, -4))),
        wire_from_vertices(((-12, 4), (-4, 4))),
        wire_from_vertices(((-6, 6), (-4, 6))),
        wire_from_vertices(((-1, -5), (3, -1), (4, -1))),
        wire_from_vertices(((-1, 5), (3, 1), (4, 1))),
        wire_from_vertices(((7, 0), (13, 0), (14, -1))),
    )
    return components, wires


def _byte_lsr(project_root: Path, level: str) -> tuple[tuple[Component, ...], tuple[Wire, ...]]:
    scaffold = _load_scaffold_components(project_root, level)
    components = scaffold + (
        Component(34, (0, 0), 0, stable_permanent_id(level, "lsr"), word_size=8),
    )
    wires = (
        wire_from_vertices(((-17, -10), (-1, -10), (-1, -1))),
        wire_from_vertices(((-17, 9), (-1, 9), (-1, 1))),
        wire_from_vertices(((2, 0), (17, 0))),
    )
    return components, wires


def _full_adder(project_root: Path, level: str) -> tuple[tuple[Component, ...], tuple[Wire, ...]]:
    scaffold = _load_scaffold_components(project_root, level)
    components = scaffold + (
        Component(15, (0, -1), 0, stable_permanent_id(level, "full-adder")),
    )
    wires = (
        wire_from_vertices(((-16, -4), (-3, -4), (-1, -2))),
        wire_from_vertices(((-16, 0), (-2, 0), (-1, -1))),
        wire_from_vertices(((-16, 4), (-5, 4), (-1, 0))),
        wire_from_vertices(((1, -1), (12, -1), (14, -3))),
        wire_from_vertices(((1, 0), (12, 0), (14, 2))),
    )
    return components, wires


def _one_hot_encoding(project_root: Path, level: str) -> tuple[tuple[Component, ...], tuple[Wire, ...]]:
    scaffold = _load_scaffold_components(project_root, level)
    components = scaffold + (
        Component(2, (-10, -2), 0, stable_permanent_id(level, "one")),
        Component(33, (-7, -1), 0, stable_permanent_id(level, "shift"), word_size=8),
        Component(17, (-1, -1), 0, stable_permanent_id(level, "splitter")),
    )
    wires = (
        wire_from_vertices(((-9, -2), (-8, -2))),
        wire_from_vertices(((-14, -1), (-14, 0), (-8, 0))),
        wire_from_vertices(((-5, -1), (-2, -1))),
        *(wire_from_vertices(((0, y), (16, y))) for y in range(-4, 4)),
    )
    return components, wires


RECIPES: dict[str, Recipe] = {
    "or_gate_3": Recipe(
        "or_gate_3",
        2,
        2,
        lambda root, level: _triple_input_two_gate(root, level, 7),
        (("Input", 3),),
        "Output",
        lambda values: int(values["Input"] != 0),
    ),
    "and_gate_3": Recipe(
        "and_gate_3",
        2,
        2,
        lambda root, level: _triple_input_two_gate(root, level, 4),
        (("Input", 3),),
        "Output",
        lambda values: int(values["Input"] == 0b111),
    ),
    "xnor": Recipe(
        "xnor",
        3,
        2,
        _xnor,
        (("Input", 2),),
        "Output",
        lambda values: int((values["Input"] & 1) == ((values["Input"] >> 1) & 1)),
    ),
    "bit_inverter": Recipe(
        "bit_inverter",
        3,
        2,
        _bit_inverter,
        (("Input", 2),),
        "Output",
        lambda values: (values["Input"] & 1) ^ ((values["Input"] >> 1) & 1),
    ),
    "bit_adder": Recipe(
        "bit_adder",
        3,
        2,
        _bit_adder,
        (("A", 1), ("B", 1)),
        ("Sum", "Carry"),
        lambda values: {
            "Sum": values["A"] ^ values["B"],
            "Carry": values["A"] & values["B"],
        },
    ),
    "counting_signals": Recipe(
        "counting_signals",
        13,
        4,
        _counting_signals,
        (("Input", 4),),
        "Output",
        lambda values: values["Input"].bit_count(),
    ),
    "decoder_1": Recipe(
        "decoder_1",
        1,
        1,
        _decoder_1,
        (("Input", 1),),
        "Output",
        lambda values: (1 - (values["Input"] & 1)) | ((values["Input"] & 1) << 1),
    ),
    "byte_mux": Recipe(
        "byte_mux",
        33,
        2,
        _byte_mux,
        (("Select", 1), ("A", 8), ("B", 8)),
        "Output",
        lambda values: values["B"] if values["Select"] else values["A"],
    ),
    "byte_xor": Recipe(
        "byte_xor",
        24,
        2,
        _byte_xor,
        (("A", 8), ("B", 8)),
        "Result",
        lambda values: values["A"] ^ values["B"],
    ),
    "byte_not": Recipe(
        "byte_not",
        8,
        1,
        _byte_not,
        (("Input", 8),),
        "Output",
        lambda values: (~values["Input"]) & 0xFF,
    ),
    "byte_nand": Recipe(
        "byte_nand",
        8,
        1,
        _byte_nand,
        (("A", 8), ("B", 8)),
        "Output",
        lambda values: (~(values["A"] & values["B"])) & 0xFF,
    ),
    "byte_equal": Recipe(
        "byte_equal",
        38,
        4,
        _byte_equal,
        (("A", 8), ("B", 8)),
        "Result",
        lambda values: int(values["A"] == values["B"]),
    ),
    "byte_less_u": Recipe(
        "byte_less_u",
        90,
        4,
        _byte_less_u,
        (("A", 8), ("B", 8)),
        "Result",
        lambda values: int(values["A"] < values["B"]),
    ),
    "byte_asr": Recipe(
        "byte_asr",
        76,
        3,
        _byte_asr,
        (("Input", 8), ("Shift", 3)),
        "Result",
        lambda values: (
            ((values["Input"] - 256) if values["Input"] & 0x80 else values["Input"])
            >> values["Shift"]
        )
        & 0xFF,
    ),
    "byte_constant": Recipe(
        "byte_constant",
        0,
        0,
        _byte_constant,
        (),
        "Output",
        lambda values: 164,
    ),
    "decoder_2": Recipe(
        "decoder_2",
        4,
        2,
        _decoder_2,
        (("Input", 2),),
        "Output",
        lambda values: 1 << values["Input"],
    ),
    "decoder_3": Recipe(
        "decoder_3",
        14,
        3,
        _decoder_3,
        (("Input", 3), ("Disable", 1)),
        "Output",
        lambda values: 0 if values["Disable"] else 1 << values["Input"],
    ),
    "signed_negator": Recipe(
        "signed_negator",
        24,
        5,
        _signed_negator,
        (("Input", 8),),
        "Output",
        lambda values: (-values["Input"]) & 0xFF,
    ),
    "byte_less_s": Recipe(
        "byte_less_s",
        90,
        4,
        _byte_less_s,
        (("A", 8), ("B", 8)),
        "Result",
        lambda values: int((values["A"] ^ 0x80) < (values["B"] ^ 0x80)),
    ),
    "byte_lsr": Recipe(
        "byte_lsr",
        70,
        3,
        _byte_lsr,
        (("Input", 8), ("Shift", 3)),
        "Result",
        lambda values: values["Input"] >> values["Shift"],
    ),
    "full_adder": Recipe(
        "full_adder",
        14,
        3,
        _full_adder,
        (("Input 0", 1), ("Input 1", 1), ("Input 2", 1)),
        ("Sum", "Carry"),
        lambda values: {
            "Sum": sum(values.values()) & 1,
            "Carry": (sum(values.values()) >> 1) & 1,
        },
    ),
    "one_hot_encoding": Recipe(
        "one_hot_encoding",
        70,
        3,
        _one_hot_encoding,
        (("Input", 3),),
        "Output",
        lambda values: 1 << values["Input"],
    ),
}


VARIANT_RECIPES: dict[tuple[str, str], Recipe] = {
    ("signed_negator", "low-gate"): Recipe(
        "signed_negator",
        21,
        8,
        _signed_negator_low_gate,
        (("Input", 8),),
        "Output",
        lambda values: (-values["Input"]) & 0xFF,
    ),
}


def _build_recipe_to(
    project_root: Path,
    recipe: Recipe,
    destination: Path,
) -> dict[str, object]:
    level = recipe.level
    baseline_path = project_root / "examples" / level / "baseline" / "circuit.data"
    baseline = decode_v15(baseline_path.read_bytes()) if baseline_path.exists() else Circuit()
    components, wires = recipe.build(project_root, level)
    candidate = replace(
        baseline,
        gate=recipe.declared_gate,
        delay=recipe.declared_delay,
        components=components,
        wires=wires,
    )
    connectivity = analyze_connectivity(candidate)
    if connectivity["unsupported_component_kind_counts"]:
        raise ValueError(f"recipe {level} contains unsupported components")
    if connectivity["unconnected_pin_count"]:
        raise ValueError(
            f"recipe {level} has unconnected pins: {connectivity['unconnected_pins']}"
        )
    if connectivity["cycle_component_count"]:
        raise ValueError(f"recipe {level} unexpectedly contains a logic cycle")
    tested_vectors = verify_truth_table(
        candidate,
        inputs=dict(recipe.inputs),
        output_label=recipe.output_label,
        expected=recipe.expected,
    )
    payload = encode_v15(candidate)
    if decode_v15(payload) != candidate:
        raise RuntimeError(f"recipe {level} failed v15 verification")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(payload)
    (destination.parent / ".gitkeep").unlink(missing_ok=True)
    relative_path = destination.relative_to(project_root / "examples").as_posix()
    return {
        "level": level,
        "path": relative_path,
        "sha256": sha256(payload).hexdigest(),
        "declared_gate": candidate.gate,
        "declared_delay": candidate.delay,
        "declared_energy": candidate.energy,
        "component_count": len(candidate.components),
        "wire_count": len(candidate.wires),
        "unit_logic_depth": connectivity["unit_logic_depth"],
        "connected_pin_count": connectivity["connected_pin_count"],
        "exhaustive_test_vectors": tested_vectors,
    }


def build_recipe(project_root: Path, level: str) -> dict[str, object]:
    destination = project_root / "examples" / level / "candidate" / "circuit.data"
    return _build_recipe_to(project_root, RECIPES[level], destination)


def build_variant_recipe(project_root: Path, level: str, variant: str) -> dict[str, object]:
    destination = (
        project_root
        / "examples"
        / level
        / "variants"
        / variant
        / "circuit.data"
    )
    record = _build_recipe_to(project_root, VARIANT_RECIPES[(level, variant)], destination)
    metadata = {"schema": 1, "variant": variant, **record}
    (destination.parent / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return record


def build_known_candidates(project_root: Path) -> dict[str, object]:
    records = [build_recipe(project_root, level) for level in RECIPES]
    analyze_examples(project_root)
    return {"candidate_count": len(records), "candidates": records}


def build_known_variants(
    project_root: Path,
    *,
    levels: tuple[str, ...] = (),
) -> dict[str, object]:
    selected = [
        (level, variant)
        for level, variant in VARIANT_RECIPES
        if not levels or level in levels
    ]
    missing = sorted(set(levels) - {level for level, _ in selected})
    if missing:
        raise ValueError(f"关卡没有已审查的 Pareto 变体：{', '.join(missing)}")
    records = [build_variant_recipe(project_root, level, variant) for level, variant in selected]
    return {"variant_count": len(records), "variants": records}
