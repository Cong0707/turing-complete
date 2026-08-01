"""Strict current-sprite geometry checks for reviewed campaign candidates.

The save format accepts a wire that geometrically passes through a component.
The running game does not: it can turn such a route into an accidental junction
or reject the circuit altogether.  This module reads the installed component
sprites and treats every opaque grid cell as occupied.  It deliberately allows
wire-to-wire intersections, while rejecting component crossings and contacts
with non-endpoint pins.

Only component kinds that have an explicit, current-version sprite mapping are
audited.  An unknown kind is reported instead of being approximated by a
rectangle, so a passing report never rests on guessed geometry.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import struct
import zlib

from .analysis import wire_points
from .model import Circuit, Component, Point
from .pins import positioned_pins, rotate_offset


DEFAULT_COMPONENT_SPRITE_ROOT = Path(
    r"D:\Game\Steam\steamapps\common\Turing Complete\asset\component_sprites"
)
PIXELS_PER_GRID_CELL = 20


# These names are checked against the currently installed game files by the
# live-alpha regression test.  Keep this map deliberately explicit: silently
# guessing a sprite for a new component defeats the purpose of the audit.
SPRITE_NAME_BY_COMPONENT_KIND: dict[int, str] = {
    1: "com_off.png",
    2: "com_on.png",
    3: "com_not_bit.png",
    4: "com_and_bit.png",
    5: "com_and_3_bit.png",
    6: "com_nand_bit.png",
    7: "com_or_bit.png",
    8: "com_or_3_bit.png",
    9: "com_nor_bit.png",
    10: "com_xor_bit.png",
    11: "com_xnor_bit.png",
    12: "com_switch_bit.png",
    13: "com_delay_line_bit.png",
    14: "com_register_bit.png",
    15: "com_full_adder.png",
    16: "com_maker_bit_8.png",
    17: "com_splitter_bit_8.png",
    18: "com_not_word.png",
    19: "com_or_word.png",
    20: "com_and_word.png",
    21: "com_nand_word.png",
    22: "com_nor_word.png",
    23: "com_xor_word.png",
    24: "com_xnor_word.png",
    25: "com_switch_word.png",
    26: "com_equal.png",
    27: "com_less_u.png",
    28: "com_less_s.png",
    29: "com_neg.png",
    30: "com_add.png",
    31: "com_mul.png",
    32: "com_div.png",
    33: "com_lsl.png",
    34: "com_lsr.png",
    35: "com_asr.png",
    36: "com_rol.png",
    37: "com_ror.png",
    38: "com_register_word_config.png",
    39: "com_register_word.png",
    40: "com_level_output_8_pin.png",
    42: "com_mux.png",
    43: "com_decoder_1.png",
    44: "com_decoder_2.png",
    45: "com_decoder_3.png",
    46: "com_constant.png",
    49: "com_clz.png",
    55: "com_delay_line_word.png",
    60: "com_level_input_1_pin.png",
    61: "com_level_input_word.png",
    62: "com_cc_level_input.png",
    63: "com_level_input_2_pin.png",
    64: "com_level_input_3_pin.png",
    65: "com_level_input_4_pin.png",
    68: "com_level_output_1_pin.png",
    69: "com_level_output_word.png",
    70: "com_cc_level_output.png",
    73: "com_level_output_2_pin.png",
    74: "com_level_output_3_pin.png",
    75: "com_level_output_4_pin.png",
    77: "com_level_output_counter.png",
    97: "com_maker_word_4.png",
    99: "com_splitter_word_4.png",
    108: "com_mod.png",
    111: "com_maker_bit_2.png",
    118: "com_ram.png",
}


@dataclass(frozen=True)
class SpriteWireCollision:
    """One wire grid cell covered by a component body away from a valid endpoint."""

    wire_index: int
    component_index: int
    point: Point
    component_kind: int
    endpoint: bool
    pin_names: tuple[str, ...]


@dataclass(frozen=True)
class InteriorPinContact:
    """A wire passes over a port without ending at that port."""

    wire_index: int
    component_index: int
    point: Point
    pin_names: tuple[str, ...]


@dataclass(frozen=True)
class SpriteGeometryAudit:
    """Strict geometry result for a circuit drawn against live component sprites."""

    sprite_files: tuple[str, ...]
    alpha_cell_count: int
    unsupported_component_kinds: tuple[int, ...]
    component_overlap_cells: tuple[Point, ...]
    wire_collisions: tuple[SpriteWireCollision, ...]
    wire_interior_pin_contacts: tuple[InteriorPinContact, ...]


class PngAlphaError(ValueError):
    """The installed component sprite is not the reviewed RGBA8 PNG form."""


def _png_rgba_rows(path: Path) -> tuple[int, int, bytes]:
    """Decode the exact non-interlaced RGBA8 PNG subset used by game sprites."""

    data = path.read_bytes()
    signature = b"\x89PNG\r\n\x1a\n"
    if not data.startswith(signature):
        raise PngAlphaError(f"not a PNG file: {path}")
    offset = len(signature)
    width = height = bit_depth = color_type = compression = filter_method = interlace = None
    idat_parts: list[bytes] = []
    saw_iend = False
    while offset < len(data):
        if offset + 12 > len(data):
            raise PngAlphaError(f"truncated PNG chunk header: {path}")
        length = struct.unpack_from(">I", data, offset)[0]
        offset += 4
        chunk_type = data[offset : offset + 4]
        offset += 4
        end = offset + length
        if end + 4 > len(data):
            raise PngAlphaError(f"truncated PNG chunk data: {path}")
        payload = data[offset:end]
        offset = end
        stored_crc = struct.unpack_from(">I", data, offset)[0]
        offset += 4
        if zlib.crc32(chunk_type + payload) & 0xFFFFFFFF != stored_crc:
            raise PngAlphaError(f"PNG CRC mismatch in {path}")
        if chunk_type == b"IHDR":
            if len(payload) != 13 or width is not None:
                raise PngAlphaError(f"invalid IHDR in {path}")
            width, height, bit_depth, color_type, compression, filter_method, interlace = struct.unpack(
                ">IIBBBBB", payload
            )
        elif chunk_type == b"IDAT":
            idat_parts.append(payload)
        elif chunk_type == b"IEND":
            saw_iend = True
            break
    if not saw_iend or width is None or height is None:
        raise PngAlphaError(f"incomplete PNG: {path}")
    if (bit_depth, color_type, compression, filter_method, interlace) != (8, 6, 0, 0, 0):
        raise PngAlphaError(
            f"expected non-interlaced RGBA8 component sprite, got "
            f"bit_depth={bit_depth}, color_type={color_type}, interlace={interlace}: {path}"
        )
    try:
        filtered = zlib.decompress(b"".join(idat_parts))
    except zlib.error as exc:
        raise PngAlphaError(f"could not inflate PNG data: {path}") from exc
    stride = width * 4
    if len(filtered) != height * (stride + 1):
        raise PngAlphaError(f"unexpected PNG data size for {path}")

    rows = bytearray()
    previous = bytearray(stride)
    source_offset = 0
    for _ in range(height):
        filter_type = filtered[source_offset]
        source_offset += 1
        row = bytearray(filtered[source_offset : source_offset + stride])
        source_offset += stride
        for index in range(stride):
            left = row[index - 4] if index >= 4 else 0
            above = previous[index]
            upper_left = previous[index - 4] if index >= 4 else 0
            if filter_type == 0:
                correction = 0
            elif filter_type == 1:
                correction = left
            elif filter_type == 2:
                correction = above
            elif filter_type == 3:
                correction = (left + above) // 2
            elif filter_type == 4:
                predictor = left + above - upper_left
                distances = (
                    abs(predictor - left),
                    abs(predictor - above),
                    abs(predictor - upper_left),
                )
                correction = (
                    left
                    if distances[0] <= distances[1] and distances[0] <= distances[2]
                    else above if distances[1] <= distances[2] else upper_left
                )
            else:
                raise PngAlphaError(f"unsupported PNG filter {filter_type}: {path}")
            row[index] = (row[index] + correction) & 0xFF
        rows.extend(row)
        previous = row
    return width, height, bytes(rows)


@lru_cache(maxsize=None)
def sprite_alpha_cells(sprite_path: Path) -> frozenset[Point]:
    """Map every non-transparent pixel in a live sprite onto board grid cells."""

    width, height, rgba = _png_rgba_rows(sprite_path)
    if width % PIXELS_PER_GRID_CELL or height % PIXELS_PER_GRID_CELL:
        raise PngAlphaError(
            f"sprite is not aligned to {PIXELS_PER_GRID_CELL}px cells: {sprite_path}"
        )
    origin_x = width // 2 - PIXELS_PER_GRID_CELL // 2
    origin_y = height // 2 - PIXELS_PER_GRID_CELL // 2
    cells: set[Point] = set()
    for y in range(height):
        row_offset = y * width * 4
        cell_y = (y - origin_y) // PIXELS_PER_GRID_CELL
        for x in range(width):
            if rgba[row_offset + x * 4 + 3] != 0:
                cells.add(((x - origin_x) // PIXELS_PER_GRID_CELL, cell_y))
    if not cells:
        raise PngAlphaError(f"sprite contains no opaque pixels: {sprite_path}")
    return frozenset(cells)


def _component_sprite_path(component: Component, sprite_root: Path) -> Path | None:
    name = SPRITE_NAME_BY_COMPONENT_KIND.get(component.kind)
    if name is None:
        return None
    path = sprite_root / name
    if not path.is_file():
        raise FileNotFoundError(f"current component sprite is missing: {path}")
    return path


def _component_alpha_cells(component: Component, sprite_root: Path) -> frozenset[Point] | None:
    path = _component_sprite_path(component, sprite_root)
    if path is None:
        return None
    return frozenset(
        (
            component.position[0] + rotate_offset(cell, component.rotation)[0],
            component.position[1] + rotate_offset(cell, component.rotation)[1],
        )
        for cell in sprite_alpha_cells(path)
    )


def audit_sprite_geometry(circuit: Circuit, sprite_root: Path) -> SpriteGeometryAudit:
    """Audit a candidate with real sprite alpha and reviewed endpoint geometry.

    A wire may share a point with another wire.  It may touch opaque component
    alpha only at one of its own endpoints, and that endpoint must be a pin of
    that exact component.  Separately checking every interior point against
    all reviewed pins catches transparent-port sprite details as well.
    """

    alpha_owners: dict[Point, list[int]] = {}
    pin_names_by_component: list[dict[Point, tuple[str, ...]]] = []
    all_pin_owners: dict[Point, list[tuple[int, tuple[str, ...]]]] = {}
    sprite_files: set[str] = set()
    unsupported: list[int] = []

    for component_index, component in enumerate(circuit.components):
        cells = _component_alpha_cells(component, sprite_root)
        if cells is None:
            unsupported.append(component.kind)
            pin_names_by_component.append({})
            continue
        path = _component_sprite_path(component, sprite_root)
        assert path is not None
        sprite_files.add(path.name)
        for cell in cells:
            alpha_owners.setdefault(cell, []).append(component_index)

        names_at_position: dict[Point, list[str]] = {}
        for pin in positioned_pins(component, component_index):
            names_at_position.setdefault(pin.position, []).append(pin.name)
        resolved_names = {
            point: tuple(names) for point, names in names_at_position.items()
        }
        pin_names_by_component.append(resolved_names)
        for point, names in resolved_names.items():
            all_pin_owners.setdefault(point, []).append((component_index, names))

    wire_collisions: list[SpriteWireCollision] = []
    interior_pin_contacts: list[InteriorPinContact] = []
    for wire_index, wire in enumerate(circuit.wires):
        points = wire_points(wire)
        endpoints = {points[0], points[-1]}
        for point in points:
            for component_index in alpha_owners.get(point, ()):
                pin_names = pin_names_by_component[component_index].get(point, ())
                if point in endpoints and pin_names:
                    continue
                component = circuit.components[component_index]
                wire_collisions.append(
                    SpriteWireCollision(
                        wire_index=wire_index,
                        component_index=component_index,
                        point=point,
                        component_kind=component.kind,
                        endpoint=point in endpoints,
                        pin_names=pin_names,
                    )
                )
            if point in endpoints:
                continue
            for component_index, pin_names in all_pin_owners.get(point, ()):
                interior_pin_contacts.append(
                    InteriorPinContact(
                        wire_index=wire_index,
                        component_index=component_index,
                        point=point,
                        pin_names=pin_names,
                    )
                )

    return SpriteGeometryAudit(
        sprite_files=tuple(sorted(sprite_files)),
        alpha_cell_count=sum(len(owners) for owners in alpha_owners.values()),
        unsupported_component_kinds=tuple(sorted(set(unsupported))),
        component_overlap_cells=tuple(
            sorted(point for point, owners in alpha_owners.items() if len(owners) > 1)
        ),
        wire_collisions=tuple(wire_collisions),
        wire_interior_pin_contacts=tuple(interior_pin_contacts),
    )
