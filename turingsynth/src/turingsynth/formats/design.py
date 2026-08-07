"""Persistent 32x32 preview geometry for current v15 Custom components."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence

from turingsynth.formats.model import Circuit, Component, Point


DESIGN_GRID_SIZE = 32
DESIGN_BYTES = DESIGN_GRID_SIZE * DESIGN_GRID_SIZE // 2
DESIGN_ORIGIN = (15, 15)
_COORDINATE_ORIGIN = 127
DESIGN_CODE_BY_KIND = {79: 1, 81: 2, 82: 4, 84: 5, 83: 6, 85: 7}
GENERIC_COMPONENT_CODE = 3


def _rotate_offset(offset: Point, rotation: int) -> Point:
    x, y = offset
    try:
        return ((x, y), (-y, x), (-x, -y), (y, -x))[rotation]
    except IndexError as exc:
        raise ValueError(f"invalid component rotation {rotation}") from exc


def design_position(position: Point) -> Point:
    def divide(value: int) -> int:
        value += _COORDINATE_ORIGIN
        if value < 0:
            value += 7
        return value >> 3

    return divide(position[0]), divide(position[1])


def unpack_design(design: bytes) -> tuple[tuple[int, ...], ...]:
    if len(design) != DESIGN_BYTES:
        raise ValueError(
            f"Custom design must contain {DESIGN_BYTES} bytes, got {len(design)}"
        )
    columns = []
    for x in range(DESIGN_GRID_SIZE):
        column = []
        for pair in range(DESIGN_GRID_SIZE // 2):
            value = design[x * (DESIGN_GRID_SIZE // 2) + pair]
            column.extend((value >> 4, value & 0x0F))
        columns.append(tuple(column))
    return tuple(columns)


def pack_design(grid: Sequence[Sequence[int]]) -> bytes:
    if len(grid) != DESIGN_GRID_SIZE or any(
        len(column) != DESIGN_GRID_SIZE for column in grid
    ):
        raise ValueError("Custom design grid must be exactly 32x32")
    result = bytearray(DESIGN_BYTES)
    for x, column in enumerate(grid):
        for pair in range(DESIGN_GRID_SIZE // 2):
            high = column[2 * pair]
            low = column[2 * pair + 1]
            if not 0 <= high <= 0x0F or not 0 <= low <= 0x0F:
                raise ValueError("Custom design cells must be four-bit values")
            result[x * (DESIGN_GRID_SIZE // 2) + pair] = (high << 4) | low
    return bytes(result)


def render_custom_design(
    components: Iterable[Component],
    dependencies: Mapping[int, Circuit] | None = None,
) -> bytes:
    dependencies = dependencies or {}
    components = tuple(components)
    grid = [[0] * DESIGN_GRID_SIZE for _ in range(DESIGN_GRID_SIZE)]
    for component in components:
        x, y = design_position(component.position)
        if not (0 <= x < DESIGN_GRID_SIZE and 0 <= y < DESIGN_GRID_SIZE):
            continue
        code = DESIGN_CODE_BY_KIND.get(component.kind, GENERIC_COMPONENT_CODE)
        grid[x][y] = max(grid[x][y], code)

    for component in components:
        if component.kind != 78:
            continue
        try:
            child = dependencies[component.custom_id]
        except KeyError as exc:
            raise ValueError(
                f"missing Custom design dependency {component.custom_id}"
            ) from exc
        for x, column in enumerate(unpack_design(child.design)):
            for y, code in enumerate(column):
                if not code:
                    continue
                local = (x - DESIGN_ORIGIN[0], y - DESIGN_ORIGIN[1])
                dx, dy = _rotate_offset(local, component.rotation)
                parent = (
                    component.position[0] + dx,
                    component.position[1] + dy,
                )
                parent_x, parent_y = design_position(parent)
                if 0 <= parent_x < DESIGN_GRID_SIZE and 0 <= parent_y < DESIGN_GRID_SIZE:
                    grid[parent_x][parent_y] = max(
                        grid[parent_x][parent_y], GENERIC_COMPONENT_CODE
                    )
    return pack_design(grid)


def occupied_design_offsets(circuit: Circuit) -> frozenset[Point]:
    result = {
        (x - DESIGN_ORIGIN[0], y - DESIGN_ORIGIN[1])
        for x, column in enumerate(unpack_design(circuit.design))
        for y, value in enumerate(column)
        if value
    }
    if not result:
        raise ValueError(f"Custom circuit {circuit.custom_id} has an empty design")
    return frozenset(result)
