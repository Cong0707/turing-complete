"""Bounds-checked little-endian binary primitives used by circuit codecs."""

from __future__ import annotations

from dataclasses import dataclass, field
import struct


class FormatError(ValueError):
    """Raised when a circuit container is malformed or unsupported."""


MAX_SEQUENCE_ITEMS = 10_000_000
MAX_STRING_BYTES = 0xFFFF


class Reader:
    def __init__(self, data: bytes):
        self.data = data
        self.offset = 0

    def take(self, size: int) -> bytes:
        if size < 0 or self.offset + size > len(self.data):
            raise FormatError(
                f"truncated data at offset {self.offset}: need {size} byte(s), "
                f"have {len(self.data) - self.offset}"
            )
        result = self.data[self.offset : self.offset + size]
        self.offset += size
        return result

    def unpack(self, spec: str) -> int:
        size = struct.calcsize(spec)
        return int(struct.unpack(spec, self.take(size))[0])

    def u8(self) -> int:
        return self.unpack("<B")

    def u16(self) -> int:
        return self.unpack("<H")

    def i16(self) -> int:
        return self.unpack("<h")

    def u32(self) -> int:
        return self.unpack("<I")

    def i64(self) -> int:
        return self.unpack("<q")

    def u64(self) -> int:
        return self.unpack("<Q")

    def boolean(self) -> bool:
        value = self.u8()
        if value not in (0, 1):
            raise FormatError(f"invalid boolean {value} at offset {self.offset - 1}")
        return bool(value)

    def string(self) -> str:
        size = self.u16()
        payload = self.take(size)
        try:
            return payload.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise FormatError(
                f"invalid UTF-8 string ending at offset {self.offset}"
            ) from exc

    def bytes_u16(self) -> bytes:
        return self.take(self.u16())

    def point(self) -> tuple[int, int]:
        return self.i16(), self.i16()

    def count_i64(self, label: str) -> int:
        value = self.i64()
        if not 0 <= value <= MAX_SEQUENCE_ITEMS:
            raise FormatError(f"invalid {label} count {value}")
        return value

    def finish(self) -> None:
        if self.offset != len(self.data):
            raise FormatError(
                f"{len(self.data) - self.offset} trailing byte(s) after circuit"
            )


@dataclass
class Writer:
    data: bytearray = field(default_factory=bytearray)

    def pack(self, spec: str, value: int) -> None:
        try:
            self.data.extend(struct.pack(spec, value))
        except struct.error as exc:
            raise FormatError(f"value {value!r} does not fit {spec}") from exc

    def u8(self, value: int) -> None:
        self.pack("<B", value)

    def u16(self, value: int) -> None:
        self.pack("<H", value)

    def i16(self, value: int) -> None:
        self.pack("<h", value)

    def u32(self, value: int) -> None:
        self.pack("<I", value)

    def i64(self, value: int) -> None:
        self.pack("<q", value)

    def u64(self, value: int) -> None:
        self.pack("<Q", value)

    def boolean(self, value: bool) -> None:
        self.u8(1 if value else 0)

    def string(self, value: str) -> None:
        payload = value.encode("utf-8")
        if len(payload) > MAX_STRING_BYTES:
            raise FormatError(f"UTF-8 string is too long: {len(payload)} bytes")
        self.u16(len(payload))
        self.data.extend(payload)

    def bytes_u16(self, value: bytes) -> None:
        if len(value) > 0xFFFF:
            raise FormatError(f"byte string is too long: {len(value)} bytes")
        self.u16(len(value))
        self.data.extend(value)

    def point(self, value: tuple[int, int]) -> None:
        self.i16(value[0])
        self.i16(value[1])
