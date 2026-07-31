"""Dependency-free raw Snappy codec with deterministic literal-only writes."""

from __future__ import annotations

from .binary import FormatError


MAX_DECOMPRESSED_SIZE = 256 * 1024 * 1024


def _read_varint(data: bytes) -> tuple[int, int]:
    value = 0
    shift = 0
    for offset in range(min(10, len(data))):
        byte = data[offset]
        value |= (byte & 0x7F) << shift
        if byte < 0x80:
            return value, offset + 1
        shift += 7
    raise FormatError("truncated or oversized Snappy length varint")


def _write_varint(value: int) -> bytes:
    if value < 0:
        raise ValueError("Snappy length cannot be negative")
    output = bytearray()
    while True:
        byte = value & 0x7F
        value >>= 7
        output.append(byte | (0x80 if value else 0))
        if not value:
            return bytes(output)


def compress_raw(data: bytes) -> bytes:
    output = bytearray(_write_varint(len(data)))
    offset = 0
    while offset < len(data):
        length = min(len(data) - offset, 65536)
        code = length - 1
        if length < 60:
            output.append(code << 2)
        else:
            width = max(1, (code.bit_length() + 7) // 8)
            output.append((59 + width) << 2)
            output.extend(code.to_bytes(width, "little"))
        output.extend(data[offset : offset + length])
        offset += length
    return bytes(output)


def decompress_raw(data: bytes) -> bytes:
    expected, offset = _read_varint(data)
    if expected > MAX_DECOMPRESSED_SIZE:
        raise FormatError(f"Snappy output length {expected} exceeds safety limit")
    output = bytearray()

    def copy(distance: int, length: int) -> None:
        if distance <= 0 or distance > len(output):
            raise FormatError(f"invalid Snappy copy distance {distance}")
        if len(output) + length > expected:
            raise FormatError("Snappy copy exceeds declared output length")
        for _ in range(length):
            output.append(output[-distance])

    while len(output) < expected:
        if offset >= len(data):
            raise FormatError("truncated Snappy tag stream")
        tag = data[offset]
        offset += 1
        kind = tag & 3
        if kind == 0:
            code = tag >> 2
            if code < 60:
                length = code + 1
            else:
                width = code - 59
                if offset + width > len(data):
                    raise FormatError("truncated Snappy literal length")
                length = int.from_bytes(data[offset : offset + width], "little") + 1
                offset += width
            if offset + length > len(data) or len(output) + length > expected:
                raise FormatError("truncated or oversized Snappy literal")
            output.extend(data[offset : offset + length])
            offset += length
        elif kind == 1:
            if offset >= len(data):
                raise FormatError("truncated Snappy COPY_1")
            length = 4 + ((tag >> 2) & 7)
            distance = ((tag & 0xE0) << 3) | data[offset]
            offset += 1
            copy(distance, length)
        elif kind == 2:
            if offset + 2 > len(data):
                raise FormatError("truncated Snappy COPY_2")
            length = 1 + (tag >> 2)
            distance = int.from_bytes(data[offset : offset + 2], "little")
            offset += 2
            copy(distance, length)
        else:
            if offset + 4 > len(data):
                raise FormatError("truncated Snappy COPY_4")
            length = 1 + (tag >> 2)
            distance = int.from_bytes(data[offset : offset + 4], "little")
            offset += 4
            copy(distance, length)

    if offset != len(data):
        raise FormatError(f"{len(data) - offset} trailing byte(s) after Snappy stream")
    return bytes(output)
