"""Strict, dependency-free parser and writer for v15 circuit containers."""

from __future__ import annotations

from .binary import FormatError, Reader, Writer
from .model import Circuit, Component, Wire
from .snappy import compress_raw, decompress_raw
FORMAT_VERSION = 15
CUSTOM_COMPONENT_KIND = 78
CUSTOM_DESIGN_BYTES = 512


def _read_component(reader: Reader) -> Component:
    kind = reader.u16()
    position = reader.point()
    rotation = reader.u8()
    permanent_id = reader.i64()
    user_label = reader.string()
    custom_string = reader.string()
    settings = tuple(reader.u64() for _ in range(reader.u16()))
    buffer_size = reader.i64()
    ui_order = reader.i16()
    word_size = reader.i64()
    immutable = reader.boolean()
    cost_gate = reader.i64()
    cost_delay = reader.i64()
    little_endian = reader.boolean()
    init_data = reader.u8()
    linked = tuple(
        (reader.i64(), reader.i64(), reader.string(), reader.i64(), reader.i64())
        for _ in range(reader.u16())
    )
    selected = tuple((reader.string(), reader.string()) for _ in range(reader.u16()))
    custom_id = 0
    custom_word_sizes: tuple[tuple[int, int], ...] = ()
    if kind == CUSTOM_COMPONENT_KIND:
        custom_id = reader.i64()
        custom_word_sizes = tuple(
            (reader.i64(), reader.i64()) for _ in range(reader.u16())
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
        immutable=immutable,
        cost_gate=cost_gate,
        cost_delay=cost_delay,
        little_endian=little_endian,
        init_data=init_data,
        linked_components=linked,
        selected_programs=selected,
        custom_id=custom_id,
        custom_word_sizes=custom_word_sizes,
    )


def _read_wire(reader: Reader) -> Wire:
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


def decode_v15(payload: bytes) -> Circuit:
    if not payload or payload[0] != FORMAT_VERSION:
        actual = payload[0] if payload else None
        raise FormatError(f"expected circuit version 15, got {actual}")
    reader = Reader(decompress_raw(payload[1:]))
    custom_id = reader.i64()
    hub_id = reader.u32()
    gate = reader.i64()
    delay = reader.i64()
    menu_visible = reader.boolean()
    clock_speed = reader.u64()
    dependencies = tuple(reader.i64() for _ in range(reader.u16()))
    description = reader.string()
    sync_state = reader.u8()
    score = reader.u16()
    player_data = reader.bytes_u16()
    hub_description = reader.string()
    design = reader.take(CUSTOM_DESIGN_BYTES) if custom_id else b""
    components = tuple(_read_component(reader) for _ in range(reader.count_i64("component")))
    wires = tuple(_read_wire(reader) for _ in range(reader.count_i64("wire")))
    reader.finish()
    return Circuit(
        custom_id=custom_id,
        hub_id=hub_id,
        gate=gate,
        delay=delay,
        menu_visible=menu_visible,
        clock_speed=clock_speed,
        dependencies=dependencies,
        description=description,
        sync_state=sync_state,
        score=score,
        player_data=player_data,
        hub_description=hub_description,
        design=design,
        components=components,
        wires=wires,
    )


def _write_component(writer: Writer, component: Component) -> None:
    writer.u16(component.kind)
    writer.point(component.position)
    writer.u8(component.rotation)
    writer.i64(component.permanent_id)
    writer.string(component.user_label)
    writer.string(component.custom_string)
    writer.u16(len(component.settings))
    for setting in component.settings:
        writer.u64(setting)
    writer.i64(component.buffer_size)
    writer.i16(component.ui_order)
    writer.i64(component.word_size)
    writer.boolean(component.immutable)
    writer.i64(component.cost_gate)
    writer.i64(component.cost_delay)
    writer.boolean(component.little_endian)
    writer.u8(component.init_data)
    writer.u16(len(component.linked_components))
    for permanent_id, inner_id, name, offset, word_size in component.linked_components:
        writer.i64(permanent_id)
        writer.i64(inner_id)
        writer.string(name)
        writer.i64(offset)
        writer.i64(word_size)
    writer.u16(len(component.selected_programs))
    for level, program in component.selected_programs:
        writer.string(level)
        writer.string(program)
    if component.kind == CUSTOM_COMPONENT_KIND:
        writer.i64(component.custom_id)
        writer.u16(len(component.custom_word_sizes))
        for permanent_id, word_size in component.custom_word_sizes:
            writer.i64(permanent_id)
            writer.i64(word_size)


def _write_wire(writer: Writer, wire: Wire) -> None:
    if wire.teleport_end is not None:
        raise FormatError("v15 cannot encode a v7 teleport wire")
    writer.u8(wire.color)
    writer.string(wire.comment)
    writer.point(wire.start)
    for direction, length in wire.segments:
        if not 0 <= direction <= 7 or not 1 <= length <= 0x1FFF:
            raise FormatError(f"invalid wire segment ({direction}, {length})")
        writer.u16((direction << 13) | length)
    writer.u16(0)


def encode_v15(circuit: Circuit) -> bytes:
    if circuit.custom_id and len(circuit.design) != CUSTOM_DESIGN_BYTES:
        raise FormatError("custom circuit design must contain exactly 512 bytes")
    if not circuit.custom_id and circuit.design:
        raise FormatError("non-custom circuit cannot contain custom design bytes")
    writer = Writer()
    writer.i64(circuit.custom_id)
    writer.u32(circuit.hub_id)
    writer.i64(circuit.gate)
    writer.i64(circuit.delay)
    writer.boolean(circuit.menu_visible)
    writer.u64(circuit.clock_speed)
    writer.u16(len(circuit.dependencies))
    for dependency in circuit.dependencies:
        writer.i64(dependency)
    writer.string(circuit.description)
    writer.u8(circuit.sync_state)
    writer.u16(circuit.score)
    writer.bytes_u16(circuit.player_data)
    writer.string(circuit.hub_description)
    if circuit.custom_id:
        writer.data.extend(circuit.design)
    writer.i64(len(circuit.components))
    for component in circuit.components:
        _write_component(writer, component)
    writer.i64(len(circuit.wires))
    for wire in circuit.wires:
        _write_wire(writer, wire)
    payload = bytes([FORMAT_VERSION]) + compress_raw(bytes(writer.data))
    if decode_v15(payload) != circuit:
        raise FormatError("internal v15 round-trip verification failed")
    return payload
