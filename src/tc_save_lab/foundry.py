"""Build and explicitly deploy modern v15 Foundry components."""

from __future__ import annotations

from dataclasses import dataclass, replace
from hashlib import sha256
from pathlib import Path
import csv
import json
import os
import shutil
import stat
import struct
import subprocess
import unicodedata
import uuid

from .codec import CUSTOM_DESIGN_BYTES, decode_v15, encode_v15
from .model import Circuit, Component, Point, Wire
from .storage import DEFAULT_SAVE_ROOT


CUSTOM_INSTANCE_KIND = 78
FOUNDRY_INPUT_KIND = 79
FOUNDRY_OUTPUT_KIND = 81
CUSTOM_ID_NAMESPACE = "github.com/Cong0707/turing-complete"
CUSTOM_ID_DOMAIN = b"tc-save-lab/custom-id/v1\0"
PERMANENT_ID_DOMAIN = b"tc-save-lab/foundry-permanent-id/v1\0"
REGISTRY_SCHEMA = 1
PROJECT_CODEX_ROOT = Path("examples/foundry/codex")
SAVE_CODEX_ROOT = Path("schematics/foundry/codex")
INT64_MAX = (1 << 63) - 1


class FoundryError(ValueError):
    """A candidate violates the Codex Foundry identity or graph contract."""


@dataclass(frozen=True)
class FoundryDeployItem:
    logical_key: str
    display_path: str
    custom_id: int
    source: Path
    destination: Path
    sha256: str


@dataclass(frozen=True)
class FoundryDeployPlan:
    project_root: Path
    save_root: Path
    source_root: Path
    foundry_root: Path
    target_root: Path
    registry_path: Path
    source_fingerprint: str
    foundry_fingerprint: str
    items: tuple[FoundryDeployItem, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "project_root": str(self.project_root),
            "save_root": str(self.save_root),
            "source_root": str(self.source_root),
            "target_root": str(self.target_root),
            "source_fingerprint": self.source_fingerprint,
            "foundry_fingerprint": self.foundry_fingerprint,
            "component_count": len(self.items),
            "items": [
                {
                    "logical_key": item.logical_key,
                    "display_path": item.display_path,
                    "custom_id": item.custom_id,
                    "source": str(item.source),
                    "destination": str(item.destination),
                    "sha256": item.sha256,
                }
                for item in self.items
            ],
        }


def _framed_nfc(value: str) -> bytes:
    encoded = unicodedata.normalize("NFC", value).encode("utf-8")
    return struct.pack("<I", len(encoded)) + encoded


def normalize_logical_key(value: str) -> str:
    """Return the immutable ASCII identity key used by parent Custom links."""

    value = unicodedata.normalize("NFC", value.strip()).replace("\\", "/")
    if not value.startswith("foundry/codex/"):
        value = f"foundry/codex/{value}"
    parts = value.split("/")
    if parts[:2] != ["foundry", "codex"] or len(parts) < 3:
        raise FoundryError(f"invalid logical key: {value!r}")
    if any(not part or part in {".", ".."} for part in parts):
        raise FoundryError(f"invalid logical key: {value!r}")
    try:
        value.encode("ascii")
    except UnicodeEncodeError as exc:
        raise FoundryError("logical_key must be stable ASCII; use display_path for Chinese names") from exc
    return value


def _custom_id_candidate(
    logical_key: str,
    *,
    nonce: int = 0,
    namespace: str = CUSTOM_ID_NAMESPACE,
) -> int:
    key = normalize_logical_key(logical_key)
    if not 0 <= nonce <= 0xFFFF_FFFF:
        raise FoundryError("custom_id nonce must fit u32")
    digest = sha256(
        CUSTOM_ID_DOMAIN
        + _framed_nfc(namespace)
        + _framed_nfc(key)
        + struct.pack("<I", nonce)
    ).digest()
    return int.from_bytes(digest[:8], "little") & INT64_MAX


def stable_custom_id(
    logical_key: str,
    *,
    nonce: int = 0,
    namespace: str = CUSTOM_ID_NAMESPACE,
) -> int:
    """Generate a deterministic positive signed-64-bit Custom identity."""

    value = _custom_id_candidate(logical_key, nonce=nonce, namespace=namespace)
    if not value:
        raise FoundryError("custom_id candidate is zero; choose the next explicit nonce")
    return value


def _stable_permanent_id(logical_key: str, role: str) -> int:
    digest = sha256(
        PERMANENT_ID_DOMAIN
        + _framed_nfc(normalize_logical_key(logical_key))
        + _framed_nfc(role)
    ).digest()
    value = int.from_bytes(digest[:8], "little") & INT64_MAX
    if not value:
        raise FoundryError("deterministic permanent_id resolved to zero")
    return value


def _validate_port_values(rotation: int, word_size: int, index: int) -> None:
    if rotation not in range(4):
        raise FoundryError(f"invalid Foundry port rotation {rotation}")
    if word_size <= 0:
        raise FoundryError(f"invalid Foundry port word size {word_size}")
    if index < 0:
        raise FoundryError(f"invalid Foundry port index {index}")


def foundry_input(
    logical_key: str,
    name: str,
    position: Point,
    *,
    rotation: int = 0,
    word_size: int = 1,
    index: int = 0,
) -> Component:
    """Create a modern three-cell Foundry input (an internal network source)."""

    _validate_port_values(rotation, word_size, index)
    return Component(
        kind=FOUNDRY_INPUT_KIND,
        position=position,
        rotation=rotation,
        permanent_id=_stable_permanent_id(logical_key, f"input:{index}:{name}"),
        user_label=name,
        settings=(2,),
        ui_order=-2 * (index + 1),
        word_size=word_size,
    )


def foundry_output(
    logical_key: str,
    name: str,
    position: Point,
    *,
    rotation: int = 0,
    word_size: int = 1,
    index: int = 0,
) -> Component:
    """Create a modern three-cell Foundry output (an internal network sink)."""

    _validate_port_values(rotation, word_size, index)
    return Component(
        kind=FOUNDRY_OUTPUT_KIND,
        position=position,
        rotation=rotation,
        permanent_id=_stable_permanent_id(logical_key, f"output:{index}:{name}"),
        user_label=name,
        settings=(0,),
        ui_order=-2 * (index + 1),
        word_size=word_size,
    )


def custom_instance(
    owner_logical_key: str,
    instance_name: str,
    child_custom_id: int,
    position: Point,
    *,
    rotation: int = 0,
    word_size: int = 1,
    custom_word_sizes: tuple[tuple[int, int], ...] = (),
) -> Component:
    """Create a kind-78 instance whose dependency will be derived automatically."""

    if not 1 <= child_custom_id <= INT64_MAX:
        raise FoundryError(f"invalid child custom_id {child_custom_id}")
    if rotation not in range(4) or word_size <= 0:
        raise FoundryError("invalid Custom instance rotation or word size")
    return Component(
        kind=CUSTOM_INSTANCE_KIND,
        position=position,
        rotation=rotation,
        permanent_id=_stable_permanent_id(owner_logical_key, f"custom:{instance_name}"),
        word_size=word_size,
        custom_id=child_custom_id,
        custom_word_sizes=custom_word_sizes,
    )


def ordered_custom_dependencies(components: tuple[Component, ...]) -> tuple[int, ...]:
    """Return direct kind-78 IDs in first-occurrence order."""

    seen: set[int] = set()
    result: list[int] = []
    for component in components:
        if component.kind != CUSTOM_INSTANCE_KIND or not component.custom_id:
            continue
        if component.custom_id not in seen:
            seen.add(component.custom_id)
            result.append(component.custom_id)
    return tuple(result)


def _modernize_ports(components: tuple[Component, ...]) -> tuple[Component, ...]:
    result: list[Component] = []
    for component in components:
        if component.kind == FOUNDRY_INPUT_KIND:
            component = replace(component, settings=(2,))
        elif component.kind == FOUNDRY_OUTPUT_KIND:
            component = replace(component, settings=(0,))
        result.append(component)
    return tuple(result)


def interface_signature(circuit: Circuit) -> list[dict[str, object]]:
    """Describe the externally visible modern interface in component order."""

    result: list[dict[str, object]] = []
    for component in circuit.components:
        if component.kind not in {FOUNDRY_INPUT_KIND, FOUNDRY_OUTPUT_KIND}:
            continue
        result.append(
            {
                "direction": "input" if component.kind == FOUNDRY_INPUT_KIND else "output",
                "permanent_id": component.permanent_id,
                "label": component.user_label,
                "position": list(component.position),
                "rotation": component.rotation,
                "word_size": component.word_size,
                "ui_order": component.ui_order,
            }
        )
    return result


def validate_custom_circuit(
    circuit: Circuit,
    *,
    expected_custom_id: int | None = None,
    modern_ports: bool = True,
) -> None:
    """Validate the container and direct dependency invariants used by Codex."""

    if not 1 <= circuit.custom_id <= INT64_MAX:
        raise FoundryError(f"invalid custom_id {circuit.custom_id}")
    if expected_custom_id is not None and circuit.custom_id != expected_custom_id:
        raise FoundryError(
            f"custom_id mismatch: expected {expected_custom_id}, got {circuit.custom_id}"
        )
    if len(circuit.design) != CUSTOM_DESIGN_BYTES:
        raise FoundryError("custom circuit design must contain exactly 512 bytes")
    expected_dependencies = ordered_custom_dependencies(circuit.components)
    if circuit.dependencies != expected_dependencies:
        raise FoundryError(
            "dependencies must equal first-occurrence kind-78 IDs: "
            f"expected {expected_dependencies}, got {circuit.dependencies}"
        )
    if circuit.custom_id in circuit.dependencies:
        raise FoundryError("a Custom component cannot directly depend on itself")
    permanent_ids = [component.permanent_id for component in circuit.components]
    if any(value <= 0 for value in permanent_ids):
        raise FoundryError("all component permanent_id values must be positive")
    if len(permanent_ids) != len(set(permanent_ids)):
        raise FoundryError("component permanent_id values must be unique")
    for component in circuit.components:
        if component.rotation not in range(4):
            raise FoundryError(f"invalid component rotation {component.rotation}")
        if component.word_size <= 0:
            raise FoundryError(f"invalid component word size {component.word_size}")
        if component.kind == CUSTOM_INSTANCE_KIND:
            if not 1 <= component.custom_id <= INT64_MAX:
                raise FoundryError("kind-78 instance requires a positive custom_id")
        elif component.custom_id:
            raise FoundryError("only kind-78 components may carry custom_id")
        if modern_ports and component.kind == FOUNDRY_INPUT_KIND and component.settings != (2,):
            raise FoundryError("modern kind-79 input must use settings=(2,)")
        if modern_ports and component.kind == FOUNDRY_OUTPUT_KIND and component.settings != (0,):
            raise FoundryError("modern kind-81 output must use settings=(0,)")
    payload = encode_v15(circuit)
    if decode_v15(payload) != circuit:
        raise FoundryError("custom circuit failed v15 round-trip verification")


def create_custom_circuit(logical_key: str, source: Circuit, *, nonce: int = 0) -> Circuit:
    """Wrap a logic network in a deterministic modern Foundry v15 container."""

    custom_id = stable_custom_id(logical_key, nonce=nonce)
    components = _modernize_ports(source.components)
    circuit = Circuit(
        custom_id=custom_id,
        gate=source.gate,
        delay=source.delay,
        menu_visible=source.menu_visible,
        clock_speed=source.clock_speed,
        dependencies=ordered_custom_dependencies(components),
        description=source.description,
        design=bytes(CUSTOM_DESIGN_BYTES),
        components=components,
        wires=source.wires,
    )
    validate_custom_circuit(circuit, expected_custom_id=custom_id)
    return circuit


def _safe_display_path(value: str) -> Path:
    normalized = unicodedata.normalize("NFC", value.strip()).replace("\\", "/")
    path = Path(normalized)
    if not normalized or path.is_absolute():
        raise FoundryError(f"invalid display path: {value!r}")
    reserved = {
        "con", "prn", "aux", "nul",
        *(f"com{i}" for i in range(1, 10)),
        *(f"lpt{i}" for i in range(1, 10)),
    }
    for part in path.parts:
        if part in {"", ".", ".."} or part.endswith((" ", ".")):
            raise FoundryError(f"invalid display path segment: {part!r}")
        if part.casefold().split(".")[0] in reserved or any(ord(char) < 32 for char in part):
            raise FoundryError(f"invalid Windows display path segment: {part!r}")
    return path


def _registry_path(project_root: Path) -> Path:
    return project_root / PROJECT_CODEX_ROOT / "custom-ids.json"


def _empty_registry() -> dict[str, object]:
    return {
        "schema": REGISTRY_SCHEMA,
        "namespace": CUSTOM_ID_NAMESPACE,
        "entries": {},
    }


def _load_registry(path: Path) -> dict[str, object]:
    registry = json.loads(path.read_text("utf-8")) if path.is_file() else _empty_registry()
    if registry.get("schema") != REGISTRY_SCHEMA:
        raise FoundryError(f"unsupported custom ID registry schema: {registry.get('schema')!r}")
    if registry.get("namespace") != CUSTOM_ID_NAMESPACE:
        raise FoundryError("custom ID registry namespace does not match this project")
    entries = registry.get("entries")
    if not isinstance(entries, dict):
        raise FoundryError("custom ID registry entries must be an object")
    seen_ids: dict[int, str] = {}
    seen_paths: dict[str, str] = {}
    for raw_key, raw_entry in entries.items():
        key = normalize_logical_key(raw_key)
        if key != raw_key or not isinstance(raw_entry, dict):
            raise FoundryError(f"invalid custom ID registry entry {raw_key!r}")
        nonce = raw_entry.get("nonce")
        custom_id = raw_entry.get("custom_id")
        display_path = raw_entry.get("display_path")
        if not isinstance(nonce, int) or not isinstance(custom_id, int) or not isinstance(display_path, str):
            raise FoundryError(f"incomplete custom ID registry entry {key!r}")
        if stable_custom_id(key, nonce=nonce) != custom_id:
            raise FoundryError(f"custom ID registry hash mismatch for {key!r}")
        normalized_path = _safe_display_path(display_path).as_posix()
        folded_path = unicodedata.normalize("NFC", normalized_path).casefold()
        if custom_id in seen_ids:
            raise FoundryError(f"duplicate registered custom_id {custom_id}")
        if folded_path in seen_paths:
            raise FoundryError(f"duplicate registered display path {normalized_path!r}")
        seen_ids[custom_id] = key
        seen_paths[folded_path] = key
    return registry


def _write_bytes_atomic(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tc-save-lab.tmp")
    try:
        with temporary.open("wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _write_json_atomic(path: Path, value: object) -> None:
    payload = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    _write_bytes_atomic(path, payload)


def _active_circuit_paths(root: Path) -> list[Path]:
    return sorted(root.rglob("circuit.data")) if root.exists() else []


def _read_custom_records(paths: list[Path]) -> dict[int, tuple[Path, Circuit]]:
    records: dict[int, tuple[Path, Circuit]] = {}
    for path in paths:
        try:
            circuit = decode_v15(path.read_bytes())
        except Exception as exc:
            raise FoundryError(f"cannot decode active Foundry circuit {path}: {exc}") from exc
        if not circuit.custom_id:
            continue
        previous = records.get(circuit.custom_id)
        if previous is not None:
            raise FoundryError(
                f"duplicate custom_id {circuit.custom_id}: {previous[0]} and {path}"
            )
        records[circuit.custom_id] = (path, circuit)
    return records


def _validate_dependency_graph(records: dict[int, tuple[Path, Circuit]]) -> None:
    for custom_id, (path, circuit) in records.items():
        try:
            validate_custom_circuit(
                circuit,
                expected_custom_id=custom_id,
                modern_ports=False,
            )
        except FoundryError as exc:
            raise FoundryError(f"invalid Custom circuit {path}: {exc}") from exc
        missing = [dependency for dependency in circuit.dependencies if dependency not in records]
        if missing:
            raise FoundryError(f"missing dependencies for {path}: {missing}")
    states: dict[int, int] = {}
    stack: list[int] = []

    def visit(custom_id: int) -> None:
        state = states.get(custom_id, 0)
        if state == 2:
            return
        if state == 1:
            first = stack.index(custom_id)
            raise FoundryError(f"Custom dependency cycle: {stack[first:] + [custom_id]}")
        states[custom_id] = 1
        stack.append(custom_id)
        for dependency in records[custom_id][1].dependencies:
            visit(dependency)
        stack.pop()
        states[custom_id] = 2

    for custom_id in records:
        visit(custom_id)


def _combined_records(
    roots: tuple[Path, ...],
    *,
    excluded_paths: tuple[Path, ...] = (),
    additions: tuple[tuple[Path, Circuit], ...] = (),
) -> dict[int, tuple[Path, Circuit]]:
    excluded = {path.resolve() for path in excluded_paths}
    paths = [
        path
        for root in roots
        for path in _active_circuit_paths(root)
        if path.resolve() not in excluded
    ]
    records = _read_custom_records(paths)
    for path, circuit in additions:
        previous = records.get(circuit.custom_id)
        if previous is not None:
            raise FoundryError(
                f"custom_id {circuit.custom_id} collision: {previous[0]} and {path}"
            )
        records[circuit.custom_id] = (path, circuit)
    return records


def build_codex_candidate(
    project_root: Path,
    logical_key: str,
    display_path: str,
    source: Circuit,
    *,
    dependency_roots: tuple[Path, ...] = (),
    allow_interface_change: bool = False,
) -> dict[str, object]:
    """Build one registered candidate under ``examples/foundry/codex``."""

    project_root = project_root.resolve()
    key = normalize_logical_key(logical_key)
    relative_display = _safe_display_path(display_path)
    display_text = relative_display.as_posix()
    registry_path = _registry_path(project_root)
    registry = _load_registry(registry_path)
    entries = registry["entries"]
    assert isinstance(entries, dict)
    entry = entries.get(key)
    candidate_path = project_root / PROJECT_CODEX_ROOT / relative_display / "candidate" / "circuit.data"
    metadata_path = candidate_path.parent / "metadata.json"
    if entry is not None:
        if entry["display_path"] != display_text:
            raise FoundryError(
                f"registered key {key!r} is bound to display path {entry['display_path']!r}"
            )
        nonce = entry["nonce"]
        assert isinstance(nonce, int)
    else:
        occupied = {
            custom_id
            for custom_id in _combined_records(
                (project_root / PROJECT_CODEX_ROOT, *dependency_roots),
                excluded_paths=(candidate_path,),
            )
        }
        registered_ids = {
            int(item["custom_id"])
            for item in entries.values()
            if isinstance(item, dict) and "custom_id" in item
        }
        occupied.update(registered_ids)
        nonce = 0
        while True:
            candidate_id = _custom_id_candidate(key, nonce=nonce)
            if candidate_id and candidate_id not in occupied:
                break
            nonce += 1
            if nonce > 0xFFFF_FFFF:
                raise FoundryError("unable to allocate a collision-free custom_id")
    circuit = create_custom_circuit(key, source, nonce=nonce)
    signature = interface_signature(circuit)
    if entry is not None:
        if entry["custom_id"] != circuit.custom_id:
            raise FoundryError(f"registered custom_id changed for {key!r}")
        old_signature = entry.get("interface_signature")
        if old_signature is not None and old_signature != signature and not allow_interface_change:
            raise FoundryError(
                "Foundry interface changed; pass allow_interface_change only after updating every parent"
            )
    records = _combined_records(
        (project_root / PROJECT_CODEX_ROOT, *dependency_roots),
        excluded_paths=(candidate_path,),
        additions=((candidate_path, circuit),),
    )
    _validate_dependency_graph(records)
    payload = encode_v15(circuit)
    metadata = {
        "logical_key": key,
        "display_path": display_text,
        "custom_id": circuit.custom_id,
        "nonce": nonce,
        "sha256": sha256(payload).hexdigest(),
        "dependencies": list(circuit.dependencies),
        "interface_signature": signature,
        "gate": circuit.gate,
        "delay": circuit.delay,
        "energy": circuit.energy,
    }
    entries[key] = {
        "display_path": display_text,
        "nonce": nonce,
        "custom_id": circuit.custom_id,
        "interface_signature": signature,
    }
    _write_bytes_atomic(candidate_path, payload)
    if decode_v15(candidate_path.read_bytes()) != circuit:
        raise FoundryError(f"written candidate failed verification: {candidate_path}")
    _write_json_atomic(metadata_path, metadata)
    _write_json_atomic(registry_path, registry)
    return {**metadata, "candidate": str(candidate_path), "metadata": str(metadata_path)}


def build_codex_candidate_from_json(
    project_root: Path,
    logical_key: str,
    display_path: str,
    source_json: Path,
    *,
    dependency_roots: tuple[Path, ...] = (),
    allow_interface_change: bool = False,
) -> dict[str, object]:
    data = json.loads(source_json.read_text("utf-8"))
    return build_codex_candidate(
        project_root,
        logical_key,
        display_path,
        Circuit.from_dict(data),
        dependency_roots=dependency_roots,
        allow_interface_change=allow_interface_change,
    )


def _tree_fingerprint(paths: list[Path], root: Path) -> str:
    digest = sha256()
    for path in sorted(paths, key=lambda item: item.relative_to(root).as_posix().casefold()):
        relative = unicodedata.normalize("NFC", path.relative_to(root).as_posix()).encode("utf-8")
        payload = path.read_bytes()
        digest.update(struct.pack("<I", len(relative)))
        digest.update(relative)
        digest.update(struct.pack("<Q", len(payload)))
        digest.update(sha256(payload).digest())
    return digest.hexdigest()


def _source_files(source_root: Path) -> list[Path]:
    files = [source_root / "custom-ids.json"]
    files.extend(sorted(source_root.glob("**/candidate/circuit.data")))
    files.extend(sorted(source_root.glob("**/candidate/metadata.json")))
    return [path for path in files if path.is_file()]


def _foundry_files(foundry_root: Path) -> list[Path]:
    result: list[Path] = []
    for path in _active_circuit_paths(foundry_root):
        relative = path.relative_to(foundry_root)
        if relative.parts and relative.parts[0].startswith(".codex.tc-save-lab."):
            continue
        result.append(path)
    return result


def _is_reparse_point(path: Path) -> bool:
    try:
        attributes = path.lstat().st_file_attributes
    except AttributeError:
        return path.is_symlink()
    return bool(attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)


def _reject_reparse_tree(path: Path) -> None:
    current = path
    while True:
        if current.exists() and _is_reparse_point(current):
            raise FoundryError(f"reparse point is not allowed in deployment path: {current}")
        if current.parent == current:
            break
        current = current.parent
    if path.exists():
        for child in path.rglob("*"):
            if _is_reparse_point(child):
                raise FoundryError(f"reparse point is not allowed in deployment tree: {child}")


def _assert_unique_display_paths(paths: list[str]) -> None:
    seen: dict[str, str] = {}
    for path in paths:
        folded = unicodedata.normalize("NFC", path).casefold()
        if folded in seen:
            raise FoundryError(f"case/Unicode display path collision: {seen[folded]!r} and {path!r}")
        seen[folded] = path


def plan_codex_deployment(project_root: Path, save_root: Path = DEFAULT_SAVE_ROOT) -> FoundryDeployPlan:
    """Create a read-only deployment plan for every registered Codex candidate."""

    project_root = project_root.resolve()
    save_root = save_root.resolve()
    source_root = (project_root / PROJECT_CODEX_ROOT).resolve()
    foundry_root = (save_root / "schematics" / "foundry").resolve()
    target_root = (foundry_root / "codex").resolve()
    if not save_root.is_dir() or not (save_root / "schematics").is_dir() or not foundry_root.is_dir():
        raise FoundryError(f"existing Turing Complete foundry directory is required: {foundry_root}")
    if not source_root.is_dir():
        raise FoundryError(f"project Codex source directory does not exist: {source_root}")
    if target_root != (save_root / SAVE_CODEX_ROOT).resolve():
        raise FoundryError("resolved Codex target escaped the selected save root")
    _reject_reparse_tree(source_root)
    _reject_reparse_tree(foundry_root)
    interrupted = sorted(foundry_root.glob(".codex.tc-save-lab.*"))
    if interrupted:
        raise FoundryError(
            "an interrupted Codex transaction requires manual inspection: "
            + ", ".join(str(path) for path in interrupted)
        )
    registry_path = source_root / "custom-ids.json"
    registry = _load_registry(registry_path)
    entries = registry["entries"]
    assert isinstance(entries, dict)
    items: list[FoundryDeployItem] = []
    display_paths: list[str] = []
    excluded: list[Path] = []
    additions: list[tuple[Path, Circuit]] = []
    for logical_key, entry in sorted(entries.items()):
        assert isinstance(entry, dict)
        display_path = _safe_display_path(str(entry["display_path"]))
        source = source_root / display_path / "candidate" / "circuit.data"
        destination = target_root / display_path / "circuit.data"
        if not source.is_file():
            raise FoundryError(f"registered candidate is missing: {source}")
        circuit = decode_v15(source.read_bytes())
        validate_custom_circuit(circuit, expected_custom_id=int(entry["custom_id"]))
        if interface_signature(circuit) != entry.get("interface_signature"):
            raise FoundryError(f"candidate interface differs from registry: {source}")
        if destination.is_file():
            installed = decode_v15(destination.read_bytes())
            if installed.custom_id != circuit.custom_id:
                raise FoundryError(
                    f"refusing to replace a different Custom identity at {destination}"
                )
            excluded.append(destination)
        additions.append((destination, circuit))
        display_text = display_path.as_posix()
        display_paths.append(display_text)
        items.append(
            FoundryDeployItem(
                logical_key=logical_key,
                display_path=display_text,
                custom_id=circuit.custom_id,
                source=source,
                destination=destination,
                sha256=sha256(source.read_bytes()).hexdigest(),
            )
        )
    if not items:
        raise FoundryError("no registered Codex candidates are available for deployment")
    _assert_unique_display_paths(display_paths)
    records = _combined_records(
        (foundry_root,),
        excluded_paths=tuple(excluded),
        additions=tuple(additions),
    )
    _validate_dependency_graph(records)
    source_files = _source_files(source_root)
    foundry_files = _foundry_files(foundry_root)
    return FoundryDeployPlan(
        project_root=project_root,
        save_root=save_root,
        source_root=source_root,
        foundry_root=foundry_root,
        target_root=target_root,
        registry_path=registry_path,
        source_fingerprint=_tree_fingerprint(source_files, source_root),
        foundry_fingerprint=_tree_fingerprint(foundry_files, foundry_root),
        items=tuple(items),
    )


def _assert_game_not_running() -> None:
    if os.name != "nt":
        raise RuntimeError("formal Foundry deployment is supported only on Windows")
    try:
        completed = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq Turing Complete.exe", "/FO", "CSV", "/NH"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise RuntimeError(f"cannot verify whether Turing Complete is running: {exc}") from exc
    if completed.returncode != 0:
        raise RuntimeError(
            f"tasklist failed with exit code {completed.returncode}; refusing deployment"
        )
    try:
        rows = list(csv.reader(completed.stdout.splitlines()))
    except csv.Error as exc:
        raise RuntimeError(f"cannot parse tasklist output: {exc}") from exc
    for row in rows:
        if row and row[0].strip().casefold() == "turing complete.exe":
            raise RuntimeError("Turing Complete.exe is running; refusing Foundry deployment")


def _current_plan_fingerprints(plan: FoundryDeployPlan) -> tuple[str, str]:
    source = _tree_fingerprint(_source_files(plan.source_root), plan.source_root)
    foundry = _tree_fingerprint(_foundry_files(plan.foundry_root), plan.foundry_root)
    return source, foundry


def _validate_installed_plan(plan: FoundryDeployPlan) -> None:
    for item in plan.items:
        if not item.destination.is_file():
            raise FoundryError(f"deployed circuit is missing: {item.destination}")
        payload = item.destination.read_bytes()
        if sha256(payload).hexdigest() != item.sha256:
            raise FoundryError(f"deployed circuit digest mismatch: {item.destination}")
        validate_custom_circuit(decode_v15(payload), expected_custom_id=item.custom_id)
    records = _read_custom_records(_foundry_files(plan.foundry_root))
    _validate_dependency_graph(records)


def deploy_codex_foundry(plan: FoundryDeployPlan) -> dict[str, object]:
    """Transactionally install a previously reviewed plan without persistent backups."""

    _assert_game_not_running()
    current = _current_plan_fingerprints(plan)
    expected = (plan.source_fingerprint, plan.foundry_fingerprint)
    if current != expected:
        raise FoundryError("project candidates or the target Foundry changed after planning")
    suffix = uuid.uuid4().hex
    staging = plan.foundry_root / f".codex.tc-save-lab.new.{suffix}"
    previous = plan.foundry_root / f".codex.tc-save-lab.old.{suffix}"
    if staging.exists() or previous.exists():
        raise FoundryError("unexpected Foundry transaction directory already exists")
    moved_previous = False
    installed = False
    committed = False
    try:
        if plan.target_root.exists():
            shutil.copytree(plan.target_root, staging)
        else:
            staging.mkdir()
        for item in plan.items:
            relative = item.destination.relative_to(plan.target_root)
            destination = staging / relative
            payload = item.source.read_bytes()
            _write_bytes_atomic(destination, payload)
            if decode_v15(destination.read_bytes()).custom_id != item.custom_id:
                raise FoundryError(f"staged circuit verification failed: {destination}")
        if _current_plan_fingerprints(plan) != expected:
            raise FoundryError("project candidates or the target Foundry changed during staging")
        _assert_game_not_running()
        if plan.target_root.exists():
            os.replace(plan.target_root, previous)
            moved_previous = True
        os.replace(staging, plan.target_root)
        installed = True
        _validate_installed_plan(plan)
        committed = True
        if previous.exists():
            shutil.rmtree(previous)
        return {
            "deployed": True,
            "target_root": str(plan.target_root),
            "component_count": len(plan.items),
            "custom_ids": [item.custom_id for item in plan.items],
            "persistent_backup": False,
        }
    except Exception:
        if not committed:
            if installed and plan.target_root.exists():
                shutil.rmtree(plan.target_root)
            if moved_previous and previous.exists():
                os.replace(previous, plan.target_root)
        raise
    finally:
        if staging.exists():
            shutil.rmtree(staging)
        if committed and previous.exists():
            shutil.rmtree(previous)
