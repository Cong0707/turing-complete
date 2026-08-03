"""Fetch and parse the public SchematicHub list without launching the game.

Only request kind 4 is supported.  The authentication token is read at runtime,
used in memory, and never included in output.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import argparse
import hashlib
import json
from pathlib import Path
import socket
import struct


HOST = "turingcomplete.game"
PORT = 5005
REQUEST_KIND = 4
MAX_RESPONSE_BYTES = 128 * 1024 * 1024
SETTINGS_PATH = Path.home() / "AppData/Roaming/Turing Complete/settings.txt"


class Reader:
    def __init__(self, data: bytes) -> None:
        self.data = data
        self.offset = 0

    def take(self, size: int) -> bytes:
        end = self.offset + size
        if size < 0 or end > len(self.data):
            raise ValueError(f"read beyond response at {self.offset}: need {size}")
        value = self.data[self.offset:end]
        self.offset = end
        return value

    def unpack(self, fmt: str) -> int:
        return struct.unpack(fmt, self.take(struct.calcsize(fmt)))[0]

    def u8(self) -> int:
        return self.unpack("<B")

    def i8(self) -> int:
        return self.unpack("<b")

    def u16(self) -> int:
        return self.unpack("<H")

    def u32(self) -> int:
        return self.unpack("<I")

    def i64(self) -> int:
        return self.unpack("<q")

    def string(self) -> str:
        return self.take(self.u16()).decode("utf-8")


@dataclass
class Item:
    hub_id: int
    schematic_type: int
    name: str
    description: str
    package_bytes: int
    published_timestamp: int
    image_bytes: int
    image_sha256: str
    hidden_flag: bool
    author_id: int
    author: str
    unknown_i8: int
    dependency_count_hint: int
    component_count_hint: int


def read_token() -> bytes:
    values = []
    for line in SETTINGS_PATH.read_text(encoding="utf-8").splitlines():
        key, separator, value = line.partition("=")
        if separator and key.strip() == "setting_server_token":
            values.append(value.strip().strip("\"'"))
    if len(values) != 1 or not values[0]:
        raise RuntimeError(f"expected one nonempty setting_server_token, got {len(values)}")
    token = values[0].encode("utf-8")
    if len(token) > 0xFFFF:
        raise RuntimeError("token is too long")
    return token


def recv_exact(sock: socket.socket, size: int) -> bytes:
    chunks = []
    while size:
        chunk = sock.recv(min(size, 64 * 1024))
        if not chunk:
            raise ConnectionError(f"connection closed with {size} bytes remaining")
        chunks.append(chunk)
        size -= len(chunk)
    return b"".join(chunks)


def fetch() -> bytes:
    token = read_token()
    payload = struct.pack("<BH", REQUEST_KIND, len(token)) + token
    request = struct.pack("<Q", len(payload)) + payload
    with socket.create_connection((HOST, PORT), timeout=10.0) as sock:
        sock.settimeout(30.0)
        sock.sendall(request)
        size = struct.unpack("<Q", recv_exact(sock, 8))[0]
        if size == 0 or size > MAX_RESPONSE_BYTES:
            raise RuntimeError(f"invalid response size: {size}")
        return recv_exact(sock, size)


def parse(data: bytes) -> list[Item]:
    reader = Reader(data)
    if reader.u8() != REQUEST_KIND:
        raise ValueError("response is not kind 4")
    result = []
    for _ in range(reader.u16()):
        hub_id = reader.i64()
        schematic_type = reader.u8()
        name = reader.string()
        description = reader.string()
        package_bytes = reader.u32()
        published_timestamp = reader.i64()
        image = reader.take(reader.u32())
        hidden_flag = bool(reader.u8())
        author_id = reader.u32()
        author = reader.string()
        unknown_i8 = reader.i8()
        dependency_count_hint = reader.i64()
        component_count_hint = reader.i64()
        result.append(
            Item(
                hub_id,
                schematic_type,
                name,
                description,
                package_bytes,
                published_timestamp,
                len(image),
                hashlib.sha256(image).hexdigest(),
                hidden_flag,
                author_id,
                author,
                unknown_i8,
                dependency_count_hint,
                component_count_hint,
            )
        )
    if reader.offset != len(data):
        raise ValueError(f"trailing bytes: {len(data) - reader.offset}")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).parent)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    response = fetch()
    items = parse(response)
    raw_path = args.output_dir / "hub-list-response.bin"
    json_path = args.output_dir / "hub-list-public-metadata.json"
    raw_path.write_bytes(response)
    json_path.write_text(
        json.dumps([asdict(item) for item in items], ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "count": len(items),
                "max_hub_id": max(item.hub_id for item in items),
                "response_bytes": len(response),
                "response_sha256": hashlib.sha256(response).hexdigest(),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
