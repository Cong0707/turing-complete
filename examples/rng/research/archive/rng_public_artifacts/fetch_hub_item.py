"""Download and unpack one public Schematic Hub item without launching the game."""

from __future__ import annotations

import argparse
import hashlib
import json
import socket
import struct
from pathlib import Path, PurePosixPath

from tc_save_lab.binary import Reader
from tc_save_lab.snappy import decompress_raw


HOST = "turingcomplete.game"
PORT = 5005
REQUEST_KIND_HUB_ITEM = 5
MAX_RESPONSE_BYTES = 128 * 1024 * 1024
SETTINGS_PATH = Path.home() / "AppData/Roaming/Turing Complete/settings.txt"


def read_server_token() -> bytes:
    matches: list[str] = []
    for line in SETTINGS_PATH.read_text(encoding="utf-8").splitlines():
        key, separator, value = line.partition("=")
        if separator and key.strip() == "setting_server_token":
            matches.append(value.strip())
    if len(matches) != 1:
        raise RuntimeError(f"expected one setting_server_token entry, got {len(matches)}")
    token = matches[0]
    if len(token) >= 2 and token[0] == token[-1] and token[0] in "\"'":
        token = token[1:-1]
    payload = token.encode("utf-8")
    if not payload or len(payload) > 0xFFFF:
        raise RuntimeError("invalid setting_server_token length")
    return payload


def recv_exact(sock: socket.socket, size: int) -> bytes:
    chunks: list[bytes] = []
    while size:
        chunk = sock.recv(min(size, 64 * 1024))
        if not chunk:
            raise ConnectionError(f"connection closed with {size} bytes remaining")
        chunks.append(chunk)
        size -= len(chunk)
    return b"".join(chunks)


def safe_parts(value: str) -> tuple[str, ...]:
    path = PurePosixPath(value.replace("\\", "/"))
    if path.is_absolute() or not path.parts or any(part in ("", ".", "..") for part in path.parts):
        raise ValueError(f"unsafe archive path: {value!r}")
    if ":" in path.parts[0]:
        raise ValueError(f"unsafe archive path: {value!r}")
    return path.parts


def read_u32_bytes(reader: Reader) -> bytes:
    return reader.take(reader.u32())


def write_file(root: Path, archive_name: str, payload: bytes) -> dict[str, object]:
    target = root.joinpath(*safe_parts(archive_name))
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(payload)
    return {
        "archive_name": archive_name,
        "path": target.as_posix(),
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "format_version": payload[0] if archive_name.endswith("circuit.data") and payload else None,
    }


def extract_file_group(reader: Reader, root: Path) -> list[dict[str, object]]:
    files: list[dict[str, object]] = []
    for _ in range(reader.u16() + 1):
        files.append(write_file(root, reader.string(), read_u32_bytes(reader)))
    return files


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("hub_id", type=int)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)

    token = read_server_token()
    payload = (
        struct.pack("<BH", REQUEST_KIND_HUB_ITEM, len(token))
        + token
        + struct.pack("<I", args.hub_id)
    )
    request = struct.pack("<Q", len(payload)) + payload
    with socket.create_connection((HOST, PORT), timeout=10.0) as sock:
        sock.settimeout(20.0)
        sock.sendall(request)
        response_size = struct.unpack("<Q", recv_exact(sock, 8))[0]
        if response_size == 0 or response_size > MAX_RESPONSE_BYTES:
            raise RuntimeError(f"invalid response size: {response_size}")
        response = recv_exact(sock, response_size)

    outer = Reader(response)
    response_kind = outer.u8()
    if response_kind != REQUEST_KIND_HUB_ITEM:
        raise ValueError(f"expected response kind 5, got {response_kind}")
    schematic_type = outer.u8()
    hub_name = outer.string()
    hub_description = outer.string()
    package = read_u32_bytes(outer)
    outer.finish()
    if not package or package[0] != 0:
        raise ValueError(f"unsupported package version: {package[0] if package else None}")

    archive = Reader(decompress_raw(package[1:]))
    level = archive.string()
    dependency_count = archive.u16()
    args.output.mkdir(parents=True)
    (args.output / "response.bin").write_bytes(response)
    dependencies: list[dict[str, object]] = []
    for index in range(dependency_count):
        archive_path = archive.string()
        files = extract_file_group(
            archive,
            args.output / "dependencies" / f"{index:02d}" / Path(*safe_parts(archive_path)),
        )
        dependencies.append({"archive_path": archive_path, "files": files})
    main_files = extract_file_group(archive, args.output / "main")
    archive.finish()

    metadata = {
        "hub_id": args.hub_id,
        "response_kind": response_kind,
        "schematic_type": schematic_type,
        "hub_name": hub_name,
        "hub_description": hub_description,
        "response_bytes": len(response),
        "response_sha256": hashlib.sha256(response).hexdigest(),
        "package_bytes": len(package),
        "package_sha256": hashlib.sha256(package).hexdigest(),
        "level": level,
        "dependencies": dependencies,
        "main_files": main_files,
    }
    (args.output / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(metadata, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
