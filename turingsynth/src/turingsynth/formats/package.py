"""Current Turing Complete schematic-package codec."""

from __future__ import annotations

from dataclasses import dataclass

from turingsynth.formats.binary import FormatError, MAX_SEQUENCE_ITEMS, Reader, Writer
from turingsynth.formats.snappy import compress_raw, decompress_raw


PACKAGE_VERSION = 0
MAX_UNCOMPRESSED_SIZE = 100_000_000


@dataclass(frozen=True)
class PackageFile:
    name: str
    data: bytes


@dataclass(frozen=True)
class PackageDependency:
    path: str
    files: tuple[PackageFile, ...]


@dataclass(frozen=True)
class SchematicPackage:
    level: str
    dependencies: tuple[PackageDependency, ...]
    main_files: tuple[PackageFile, ...]
    version: int = PACKAGE_VERSION


def _safe_path(value: str) -> str:
    value = value.replace("\\", "/").strip("/")
    if not value or any(part in {"", ".", ".."} for part in value.split("/")):
        raise FormatError(f"invalid package dependency path {value!r}")
    return value


def _write_files(writer: Writer, files: tuple[PackageFile, ...]) -> None:
    if not files or len(files) > 0x1_0000:
        raise FormatError(f"invalid package file count {len(files)}")
    names = [item.name for item in files]
    if len(names) != len(set(names)) or any(
        not name or "/" in name or "\\" in name for name in names
    ):
        raise FormatError("package filenames must be unique plain names")
    writer.u16(len(files) - 1)
    for item in files:
        writer.string(item.name)
        writer.u32(len(item.data))
        writer.data.extend(item.data)


def _read_files(reader: Reader) -> tuple[PackageFile, ...]:
    count = reader.u16() + 1
    if count > MAX_SEQUENCE_ITEMS:
        raise FormatError(f"invalid package file count {count}")
    return tuple(
        PackageFile(name=reader.string(), data=reader.take(reader.u32()))
        for _ in range(count)
    )


def encode_package(package: SchematicPackage) -> bytes:
    if package.version != PACKAGE_VERSION:
        raise FormatError(f"unsupported package version {package.version}")
    if len(package.dependencies) > 0xFFFF:
        raise FormatError("too many package dependencies")
    writer = Writer()
    writer.string(package.level)
    writer.u16(len(package.dependencies))
    seen_paths: set[str] = set()
    for dependency in package.dependencies:
        path = _safe_path(dependency.path)
        if path in seen_paths:
            raise FormatError(f"duplicate package dependency path {path!r}")
        seen_paths.add(path)
        writer.string(path)
        _write_files(writer, dependency.files)
    _write_files(writer, package.main_files)
    return bytes((PACKAGE_VERSION,)) + compress_raw(bytes(writer.data))


def decode_package(payload: bytes) -> SchematicPackage:
    if not payload:
        raise FormatError("empty package")
    version = payload[0]
    if version != PACKAGE_VERSION:
        raise FormatError(f"unsupported package version {version}")
    raw = decompress_raw(payload[1:])
    if len(raw) > MAX_UNCOMPRESSED_SIZE:
        raise FormatError(
            f"package expands to {len(raw)} bytes, limit is {MAX_UNCOMPRESSED_SIZE}"
        )
    reader = Reader(raw)
    level = reader.string()
    dependency_count = reader.u16()
    dependencies = tuple(
        PackageDependency(path=_safe_path(reader.string()), files=_read_files(reader))
        for _ in range(dependency_count)
    )
    main_files = _read_files(reader)
    reader.finish()
    return SchematicPackage(
        version=version,
        level=level,
        dependencies=dependencies,
        main_files=main_files,
    )
