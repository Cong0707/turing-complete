"""Strict, read-only decoders for campaign circuit formats before v15.

The layouts in this module are intentionally not paired with encoders.  Old
campaign assets are useful as immutable level scaffolding and reference
solutions, but all generated/current save files must use the v15 writer.
"""

from __future__ import annotations

from .binary import FormatError, Reader
from .model import Circuit, Component, Wire
from .snappy import decompress_raw


READ_ONLY_FORMAT_VERSIONS = (7, 13, 14)
CUSTOM_COMPONENT_KIND = 78
CUSTOM_DESIGN_BYTES = 512

# Before v15 only one label string was stored.  These component kinds used it
# as custom_string; every other kind used it as user_label.
OLD_CUSTOM_STRING_COMPONENT_KINDS = frozenset({46, 87, 94, 101})

# v7 stored program selections and abbreviated watched-component records only
# for these component kinds.
V7_LINKED_COMPONENT_KINDS = frozenset({50, 82, 83, 88, 90, 91})
V7_TELEPORT_WIRE = 0x20


def _reader_for(payload: bytes, expected_version: int) -> Reader:
    if not payload or payload[0] != expected_version:
        actual = payload[0] if payload else None
        raise FormatError(
            f"expected circuit version {expected_version}, got {actual}"
        )
    return Reader(decompress_raw(payload[1:]))


def _read_legacy_label(reader: Reader, kind: int) -> tuple[str, str]:
    value = reader.string()
    if kind in OLD_CUSTOM_STRING_COMPONENT_KINDS:
        return "", value
    return value, ""


def _read_settings(reader: Reader) -> tuple[int, ...]:
    return tuple(reader.u64() for _ in range(reader.u16()))


def _read_selected_programs(reader: Reader) -> tuple[tuple[str, str], ...]:
    return tuple((reader.string(), reader.string()) for _ in range(reader.u16()))


def _read_custom_word_sizes(reader: Reader) -> tuple[tuple[int, int], ...]:
    return tuple((reader.i64(), reader.i64()) for _ in range(reader.u16()))


def _read_component_v7(reader: Reader) -> Component:
    kind = reader.u16()
    position = reader.point()
    rotation = reader.u8()
    permanent_id = reader.i64()
    user_label, custom_string = _read_legacy_label(reader, kind)
    settings = _read_settings(reader)
    buffer_size = reader.i64()
    ui_order = reader.i16()
    word_size = reader.i64()
    reader.i64()  # Removed runtime/static-state identifier.

    custom_id = 0
    custom_word_sizes: tuple[tuple[int, int], ...] = ()
    selected_programs: tuple[tuple[str, str], ...] = ()
    linked_components: tuple[tuple[int, int, str, int, int], ...] = ()

    if kind == CUSTOM_COMPONENT_KIND:
        custom_id = reader.i64()
        custom_word_sizes = _read_custom_word_sizes(reader)
        # Removed custom-linked word-size map: (outer permanent ID, inner ID).
        for _ in range(reader.u16()):
            reader.i64()
            reader.i64()
    elif kind in V7_LINKED_COMPONENT_KINDS:
        selected_programs = _read_selected_programs(reader)
        linked_components = tuple(
            (reader.i64(), reader.i64(), reader.string(), 0, 0)
            for _ in range(reader.u16())
        )

    return Component(
        kind=kind,
        position=position,
        rotation=rotation,
        permanent_id=permanent_id,
        user_label=user_label,
        custom_string=custom_string,
        settings=settings,
        buffer_size=buffer_size,
        ui_order=ui_order,
        word_size=word_size,
        linked_components=linked_components,
        selected_programs=selected_programs,
        custom_id=custom_id,
        custom_word_sizes=custom_word_sizes,
    )


def _read_component_v13_or_v14(reader: Reader, *, with_cost: bool) -> Component:
    kind = reader.u16()
    position = reader.point()
    rotation = reader.u8()
    permanent_id = reader.i64()
    user_label, custom_string = _read_legacy_label(reader, kind)
    settings = _read_settings(reader)
    buffer_size = reader.i64()
    ui_order = reader.i16()
    word_size = reader.i64()
    immutable = reader.boolean()
    cost_gate = reader.i64() if with_cost else -1
    cost_delay = reader.i64() if with_cost else 0
    little_endian = reader.boolean()
    init_data = reader.u8()
    linked_components = tuple(
        (
            reader.i64(),
            reader.i64(),
            reader.string(),
            reader.i64(),
            reader.i64(),
        )
        for _ in range(reader.u16())
    )
    selected_programs = _read_selected_programs(reader)

    custom_id = 0
    custom_word_sizes: tuple[tuple[int, int], ...] = ()
    if kind == CUSTOM_COMPONENT_KIND:
        custom_id = reader.i64()
        custom_word_sizes = _read_custom_word_sizes(reader)

    return Component(
        kind=kind,
        position=position,
        rotation=rotation,
        permanent_id=permanent_id,
        user_label=user_label,
        custom_string=custom_string,
        settings=settings,
        buffer_size=buffer_size,
        ui_order=ui_order,
        word_size=word_size,
        immutable=immutable,
        cost_gate=cost_gate,
        cost_delay=cost_delay,
        little_endian=little_endian,
        init_data=init_data,
        linked_components=linked_components,
        selected_programs=selected_programs,
        custom_id=custom_id,
        custom_word_sizes=custom_word_sizes,
    )


def _read_wire_v7(reader: Reader) -> Wire:
    color = reader.u8()
    comment = reader.string()
    start = reader.point()
    first = reader.u8()
    if first == V7_TELEPORT_WIRE:
        return Wire(
            color=color,
            comment=comment,
            start=start,
            segments=(),
            teleport_end=reader.point(),
        )

    segments: list[tuple[int, int]] = []
    code = first
    while code & 0x1F:
        segments.append((code >> 5, code & 0x1F))
        code = reader.u8()
    return Wire(color=color, comment=comment, start=start, segments=tuple(segments))


def _read_wire_v13_or_v14(reader: Reader) -> Wire:
    color = reader.u8()
    comment = reader.string()
    start = reader.point()
    segments: list[tuple[int, int]] = []
    while True:
        code = reader.u16()
        length = code & 0x1FFF
        if length == 0:
            break
        segments.append((code >> 13, length))
    return Wire(color=color, comment=comment, start=start, segments=tuple(segments))


def _read_header(reader: Reader, *, has_camera_position: bool) -> dict[str, object]:
    result: dict[str, object] = {
        "custom_id": reader.i64(),
        "hub_id": reader.u32(),
        "gate": reader.i64(),
        "delay": reader.i64(),
        "menu_visible": reader.boolean(),
        "clock_speed": reader.u64(),
        "dependencies": tuple(reader.i64() for _ in range(reader.u16())),
        "description": reader.string(),
    }
    if has_camera_position:
        reader.point()
    result.update(
        {
            "sync_state": reader.u8(),
            "score": reader.u16(),
            "player_data": reader.bytes_u16(),
            "hub_description": reader.string(),
        }
    )
    return result


def decode_v7(payload: bytes) -> Circuit:
    reader = _reader_for(payload, 7)
    header = _read_header(reader, has_camera_position=True)
    components = tuple(
        _read_component_v7(reader) for _ in range(reader.count_i64("component"))
    )
    wires = tuple(_read_wire_v7(reader) for _ in range(reader.count_i64("wire")))
    reader.finish()
    return Circuit(**header, components=components, wires=wires)


def _decode_v13_or_v14(payload: bytes, version: int) -> Circuit:
    reader = _reader_for(payload, version)
    header = _read_header(reader, has_camera_position=False)
    custom_id = int(header["custom_id"])
    design = reader.take(CUSTOM_DESIGN_BYTES) if custom_id else b""
    components = tuple(
        _read_component_v13_or_v14(reader, with_cost=version >= 14)
        for _ in range(reader.count_i64("component"))
    )
    wires = tuple(
        _read_wire_v13_or_v14(reader) for _ in range(reader.count_i64("wire"))
    )
    reader.finish()
    return Circuit(**header, design=design, components=components, wires=wires)


def decode_v13(payload: bytes) -> Circuit:
    return _decode_v13_or_v14(payload, 13)


def decode_v14(payload: bytes) -> Circuit:
    return _decode_v13_or_v14(payload, 14)
