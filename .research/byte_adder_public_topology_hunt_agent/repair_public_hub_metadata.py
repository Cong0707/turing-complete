"""Rebuild metadata for already downloaded public Hub responses.

The original downloader predates the optional four-byte package trailer used
by computer schematics.  This repairer never contacts the server and never
rewrites response.bin or extracted files.  It verifies every extracted byte
against the response before creating a missing metadata.json.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath

from tc_save_lab.binary import Reader
from tc_save_lab.snappy import decompress_raw


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PUBLIC_ROOT = ROOT / ".research" / "byte_adder_public"


def safe_parts(value: str) -> tuple[str, ...]:
    path = PurePosixPath(value.replace("\\", "/"))
    if path.is_absolute() or not path.parts or any(part in ("", ".", "..") for part in path.parts):
        raise ValueError(f"unsafe archive path: {value!r}")
    if ":" in path.parts[0]:
        raise ValueError(f"unsafe archive path: {value!r}")
    return path.parts


def read_u32_bytes(reader: Reader) -> bytes:
    return reader.take(reader.u32())


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def verify_file(target: Path, archive_name: str, payload: bytes) -> dict[str, object]:
    if not target.is_file():
        raise FileNotFoundError(target)
    actual = target.read_bytes()
    if actual != payload:
        raise ValueError(f"extracted file differs from response: {target}")
    return {
        "archive_name": archive_name,
        "path": relative(target),
        "bytes": len(payload),
        "sha256": sha256(payload).hexdigest(),
        "format_version": payload[0] if archive_name.endswith("circuit.data") and payload else None,
    }


def read_file_group(reader: Reader, root: Path) -> list[dict[str, object]]:
    files: list[dict[str, object]] = []
    for _ in range(reader.u16() + 1):
        archive_name = reader.string()
        payload = read_u32_bytes(reader)
        target = root.joinpath(*safe_parts(archive_name))
        files.append(verify_file(target, archive_name, payload))
    return files


def repair_one(hub_root: Path) -> dict[str, object]:
    hub_id = int(hub_root.name.removeprefix("hub-"))
    response_path = hub_root / "response.bin"
    response = response_path.read_bytes()
    outer = Reader(response)
    response_kind = outer.u8()
    schematic_type = outer.u8()
    hub_name = outer.string()
    hub_description = outer.string()
    package = read_u32_bytes(outer)
    outer.finish()
    if response_kind != 5:
        raise ValueError(f"Hub {hub_id}: expected response kind 5, got {response_kind}")
    if not package or package[0] != 0:
        raise ValueError(f"Hub {hub_id}: unsupported package version")

    archive = Reader(decompress_raw(package[1:]))
    level = archive.string()
    dependency_count = archive.u16()
    dependencies: list[dict[str, object]] = []
    for index in range(dependency_count):
        archive_path = archive.string()
        files = read_file_group(
            archive,
            hub_root / "dependencies" / f"{index:02d}" / Path(*safe_parts(archive_path)),
        )
        dependencies.append({"archive_path": archive_path, "files": files})
    main_files = read_file_group(archive, hub_root / "main")

    remaining = len(archive.data) - archive.offset
    trailer_u32: int | None = None
    if remaining == 4:
        trailer_u32 = archive.u32()
    elif remaining:
        raise ValueError(f"Hub {hub_id}: unsupported {remaining}-byte package trailer")
    archive.finish()

    return {
        "hub_id": hub_id,
        "response_kind": response_kind,
        "schematic_type": schematic_type,
        "hub_name": hub_name,
        "hub_description": hub_description,
        "response_bytes": len(response),
        "response_sha256": sha256(response).hexdigest(),
        "package_bytes": len(package),
        "package_sha256": sha256(package).hexdigest(),
        "level": level,
        "dependencies": dependencies,
        "main_files": main_files,
        "archive_trailer_u32": trailer_u32,
        "archive_trailer_note": (
            "optional computer-package trailer; preserved as an uninterpreted u32"
            if trailer_u32 is not None
            else None
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--public-root", type=Path, default=DEFAULT_PUBLIC_ROOT)
    args = parser.parse_args()
    repaired: list[dict[str, object]] = []
    for hub_root in sorted(args.public_root.glob("hub-*"), key=lambda path: int(path.name[4:].split("-")[0])):
        metadata_path = hub_root / "metadata.json"
        if metadata_path.exists() or not (hub_root / "response.bin").exists():
            continue
        metadata = repair_one(hub_root)
        metadata_path.write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        repaired.append(
            {
                "hub_id": metadata["hub_id"],
                "metadata": relative(metadata_path),
                "metadata_sha256": sha256(metadata_path.read_bytes()).hexdigest(),
                "archive_trailer_u32": metadata["archive_trailer_u32"],
            }
        )
    print(json.dumps({"repaired": repaired, "count": len(repaired)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
