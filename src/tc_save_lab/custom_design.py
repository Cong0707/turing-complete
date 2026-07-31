"""Encode the persistent 32x32 preview grid used by current Custom circuits.

Version-15 stores one four-bit preview value per cell.  The game expands each
stored value into the high nibble of its runtime grid, then rebuilds a separate
low-nibble overlay from the internal components.  A zeroed persistent grid is
therefore a valid circuit, but renders as an empty Custom component until the
editor happens to refresh it.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from .model import Component, Point


DESIGN_GRID_SIZE = 32
DESIGN_BYTES = DESIGN_GRID_SIZE * DESIGN_GRID_SIZE // 2
_DESIGN_ORIGIN = 127

# This is the current game's DESIGN_IDS table, indexed by preview code.  Kinds
# not listed here are rendered with the generic component glyph (3).
DESIGN_CODE_BY_KIND = {
    79: 1,  # Foundry input
    81: 2,  # Foundry output
    82: 4,  # Probe memory bit
    84: 5,  # Probe wire bit
    83: 6,  # Probe memory word
    85: 7,  # Probe wire word
}
GENERIC_COMPONENT_CODE = 3


class CustomDesignError(ValueError):
    """The persistent Custom preview grid is malformed."""


def design_position(position: Point) -> Point:
    """Map an internal circuit coordinate to the game's 32x32 preview grid."""

    def divide(value: int) -> int:
        value += _DESIGN_ORIGIN
        # Nim signed division truncates toward zero.  The adjustment preserves
        # that behavior before the arithmetic right shift used by the game.
        if value < 0:
            value += 7
        return value >> 3

    return (divide(position[0]), divide(position[1]))


def unpack_design(design: bytes) -> tuple[tuple[int, ...], ...]:
    """Return stored preview codes as ``grid[x][y]`` nibbles."""

    if len(design) != DESIGN_BYTES:
        raise CustomDesignError(
            f"Custom design must contain {DESIGN_BYTES} bytes, got {len(design)}"
        )
    columns: list[tuple[int, ...]] = []
    for x in range(DESIGN_GRID_SIZE):
        column: list[int] = []
        for pair in range(DESIGN_GRID_SIZE // 2):
            value = design[x * (DESIGN_GRID_SIZE // 2) + pair]
            column.extend((value >> 4, value & 0x0F))
        columns.append(tuple(column))
    return tuple(columns)


def pack_design(grid: Sequence[Sequence[int]]) -> bytes:
    """Pack ``grid[x][y]`` preview codes into the v15 512-byte representation."""

    if len(grid) != DESIGN_GRID_SIZE or any(
        len(column) != DESIGN_GRID_SIZE for column in grid
    ):
        raise CustomDesignError("Custom design grid must be exactly 32x32")
    result = bytearray(DESIGN_BYTES)
    for x, column in enumerate(grid):
        for pair in range(DESIGN_GRID_SIZE // 2):
            high = column[2 * pair]
            low = column[2 * pair + 1]
            if not 0 <= high <= 0x0F or not 0 <= low <= 0x0F:
                raise CustomDesignError("Custom design cells must be four-bit values")
            result[x * (DESIGN_GRID_SIZE // 2) + pair] = (high << 4) | low
    return bytes(result)


def render_custom_design(components: Iterable[Component]) -> bytes:
    """Build the persistent preview layer for a modern Custom component.

    This reproduces the part of the current game's ``add_position`` routine
    that is serializable: supported Foundry/probe glyphs retain their distinct
    codes, while ordinary components occupy an otherwise empty grid cell with
    the generic glyph.  Components outside the 32x32 preview frame are valid
    in a circuit and are ignored by the game, so they are ignored here too.
    """

    grid = [[0] * DESIGN_GRID_SIZE for _ in range(DESIGN_GRID_SIZE)]
    for component in components:
        x, y = design_position(component.position)
        if not (0 <= x < DESIGN_GRID_SIZE and 0 <= y < DESIGN_GRID_SIZE):
            continue
        code = DESIGN_CODE_BY_KIND.get(component.kind)
        if code is None:
            if grid[x][y] == 0:
                grid[x][y] = GENERIC_COMPONENT_CODE
        else:
            # The runtime chooses the higher code at overlapping special
            # glyphs.  This keeps the persistent layer deterministic too.
            grid[x][y] = max(grid[x][y], code)
    return pack_design(grid)
