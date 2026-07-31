"""Directly install reviewed candidates without backup or transaction files."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from hashlib import sha256
from pathlib import Path
import csv
import io
import json
import re

from .codec import decode_v15, encode_v15
from .foundry import (
    FoundryDeployPlan,
    _assert_game_not_running,
    _current_plan_fingerprints,
    _reject_reparse_tree,
    _validate_installed_plan,
    plan_codex_deployment,
)
from .storage import DEFAULT_SAVE_ROOT


ARCHITECTURE_TARGETS: dict[str, tuple[str, Path]] = {
    "binary_search": (
        "CODEX-BINARY-SEARCH",
        Path("examples/binary_search/candidate/circuit.data"),
    ),
    "circumference": (
        "CODEX-CIRCUMFERENCE",
        Path("examples/circumference/candidate/circuit.data"),
    ),
    "maze": ("CODEX-MAZE", Path("examples/maze/candidate/circuit.data")),
    "mod_4": ("CODEX-MOD-4", Path("examples/mod_4/candidate/circuit.data")),
    "nim": ("CODEX-NIM", Path("examples/nim/candidate/circuit.data")),
    "rng": ("CODEX-RNG", Path("examples/rng/candidate/circuit.data")),
}


@dataclass(frozen=True)
class DirectInstallItem:
    kind: str
    name: str
    source: Path
    destination: Path
    source_sha256: str
    sha256: str
    custom_id: int = 0
    destination_before_kind: str = "absent"
    destination_before_sha256: str | None = None
    payload: bytes = field(default=b"", repr=False)

    def to_dict(self) -> dict[str, object]:
        return {
            "kind": self.kind,
            "name": self.name,
            "source": str(self.source),
            "destination": str(self.destination),
            "source_sha256": self.source_sha256,
            "sha256": self.sha256,
            "custom_id": self.custom_id,
            "destination_before_kind": self.destination_before_kind,
            "destination_before_sha256": self.destination_before_sha256,
            "will_write": self.destination_before_sha256 != self.sha256,
        }


@dataclass(frozen=True)
class DirectInstallPlan:
    project_root: Path
    save_root: Path
    foundry_plan: FoundryDeployPlan
    items: tuple[DirectInstallItem, ...]
    levels_path: Path
    levels_before_sha256: str
    levels_after: bytes

    def to_dict(self) -> dict[str, object]:
        return {
            "project_root": str(self.project_root),
            "save_root": str(self.save_root),
            "direct_write": True,
            "creates_backup": False,
            "item_count": len(self.items),
            "items": [item.to_dict() for item in self.items],
            "levels_path": str(self.levels_path),
            "levels_before_sha256": self.levels_before_sha256,
            "levels_after_sha256": sha256(self.levels_after).hexdigest(),
            "selections": {
                level: schematic
                for level, (schematic, _) in ARCHITECTURE_TARGETS.items()
            },
        }


def _parse_levels(payload: bytes) -> list[list[str]]:
    text = payload.decode("utf-8", errors="strict")
    try:
        rows = list(csv.reader(io.StringIO(text, newline=""), strict=True))
    except csv.Error as exc:
        raise ValueError(f"invalid levels.txt CSV: {exc}") from exc
    for row in rows:
        if row and len(row) != 4:
            raise ValueError(f"expected 4 columns in levels.txt, got {len(row)}: {row!r}")
    return rows


def rewrite_architecture_selections(payload: bytes) -> bytes:
    """Replace only the selected schematic field on the two reviewed level lines."""

    parsed = _parse_levels(payload)
    csv_counts = {
        level: sum(1 for row in parsed if row and row[0] == level)
        for level in ARCHITECTURE_TARGETS
    }
    duplicates = [level for level, count in csv_counts.items() if count != 1]
    if duplicates:
        details = ", ".join(f"{level}={csv_counts[level]}" for level in duplicates)
        raise ValueError(f"levels.txt must contain each target exactly once: {details}")
    text = payload.decode("utf-8", errors="strict")
    lines = text.splitlines(keepends=True)
    counts = {level: 0 for level in ARCHITECTURE_TARGETS}
    rewritten: list[str] = []
    for line in lines:
        ending = ""
        body = line
        if body.endswith("\r\n"):
            body, ending = body[:-2], "\r\n"
        elif body.endswith("\n") or body.endswith("\r"):
            body, ending = body[:-1], body[-1]
        replaced = body
        for level, (schematic, _) in ARCHITECTURE_TARGETS.items():
            pattern = re.compile(
                rf'^(?P<prefix>\s*"{re.escape(level)}"\s*,\s*(?:true|false)\s*,\s*)'
                r'"[^"\r\n]*"(?P<suffix>\s*,.*)$',
                re.IGNORECASE,
            )
            match = pattern.fullmatch(body)
            if not match:
                continue
            counts[level] += 1
            replaced = f'{match.group("prefix")}"{schematic}"{match.group("suffix")}'
            break
        rewritten.append(replaced + ending)
    missing = [level for level, count in counts.items() if count != 1]
    if missing:
        details = ", ".join(f"{level}={counts[level]}" for level in missing)
        raise ValueError(f"levels.txt must contain each target exactly once: {details}")
    result = "".join(rewritten).encode("utf-8")
    rows = _parse_levels(result)
    for level, (schematic, _) in ARCHITECTURE_TARGETS.items():
        selected = [row for row in rows if row and row[0] == level]
        if len(selected) != 1 or selected[0][2] != schematic:
            raise RuntimeError(f"failed to select {schematic} for {level}")
    return result


def _destination_state(path: Path) -> tuple[str, str | None]:
    current = path
    while True:
        if current.is_symlink():
            raise ValueError(f"symlink is not allowed in direct install path: {current}")
        if current.parent == current:
            break
        current = current.parent
    _reject_reparse_tree(path)
    if path.is_file():
        return "file", sha256(path.read_bytes()).hexdigest()
    if path.exists():
        return "other", None
    return "absent", None


def _architecture_items(project_root: Path, save_root: Path) -> tuple[DirectInstallItem, ...]:
    items: list[DirectInstallItem] = []
    architecture_root = (save_root / "schematics" / "architecture").resolve()
    if not architecture_root.is_dir():
        raise ValueError(f"architecture directory does not exist: {architecture_root}")
    _reject_reparse_tree(architecture_root)
    for level, (schematic, relative_source) in ARCHITECTURE_TARGETS.items():
        source = project_root / relative_source
        _reject_reparse_tree(source)
        source = source.resolve()
        destination = architecture_root / schematic / "circuit.data"
        if destination.parent.parent != architecture_root:
            raise ValueError(f"architecture target escaped save root: {destination}")
        if not source.is_file():
            raise ValueError(f"reviewed architecture candidate is missing: {source}")
        payload = source.read_bytes()
        circuit = decode_v15(payload)
        if circuit.custom_id or circuit.dependencies:
            raise ValueError(f"architecture candidate must be standalone: {source}")
        if encode_v15(circuit) != payload:
            raise ValueError(f"architecture candidate is not canonical v15: {source}")
        metadata_path = source.parent / "metadata.json"
        metadata = json.loads(metadata_path.read_text("utf-8"))
        source_digest = sha256(payload).hexdigest()
        expected_target = f"schematics/architecture/{schematic}/circuit.data"
        if metadata.get("sha256") != source_digest:
            raise ValueError(f"architecture metadata digest mismatch: {source}")
        if metadata.get("deployment_target") != expected_target:
            raise ValueError(f"architecture metadata target mismatch: {source}")
        destination_kind, destination_digest = _destination_state(destination)
        if destination_kind == "other":
            raise ValueError(f"architecture target is not a regular file: {destination}")
        install_payload = payload
        install_custom_id = circuit.custom_id
        if destination_kind == "file":
            destination_payload = destination.read_bytes()
            installed = decode_v15(destination_payload)
            if installed.custom_id:
                if len(installed.design) != 512:
                    raise ValueError(f"architecture target has invalid design data: {destination}")
                merged = replace(
                    circuit,
                    custom_id=installed.custom_id,
                    design=installed.design,
                )
                install_payload = (
                    destination_payload if installed == merged else encode_v15(merged)
                )
                install_custom_id = installed.custom_id
        items.append(
            DirectInstallItem(
                kind="architecture",
                name=level,
                source=source,
                destination=destination,
                source_sha256=source_digest,
                sha256=sha256(install_payload).hexdigest(),
                custom_id=install_custom_id,
                destination_before_kind=destination_kind,
                destination_before_sha256=destination_digest,
                payload=install_payload,
            )
        )
    return tuple(items)


def plan_direct_install(
    project_root: Path,
    save_root: Path = DEFAULT_SAVE_ROOT,
) -> DirectInstallPlan:
    project_root = project_root.resolve()
    save_root = save_root.resolve()
    foundry_plan = plan_codex_deployment(project_root, save_root)
    foundry_items_list: list[DirectInstallItem] = []
    for item in foundry_plan.items:
        payload = item.source.read_bytes()
        destination_kind, destination_digest = _destination_state(item.destination)
        if destination_kind == "other":
            raise ValueError(f"Foundry target is not a regular file: {item.destination}")
        foundry_items_list.append(
            DirectInstallItem(
                kind="foundry",
                name=item.display_path,
                source=item.source,
                destination=item.destination,
                source_sha256=item.sha256,
                sha256=item.sha256,
                custom_id=item.custom_id,
                destination_before_kind=destination_kind,
                destination_before_sha256=destination_digest,
                payload=payload,
            )
        )
    foundry_items = tuple(foundry_items_list)
    architecture_items = _architecture_items(project_root, save_root)
    levels_path = save_root / "levels.txt"
    _reject_reparse_tree(levels_path)
    if not levels_path.is_file():
        raise ValueError(f"levels.txt is not a regular file: {levels_path}")
    levels_payload = levels_path.read_bytes()
    levels_after = rewrite_architecture_selections(levels_payload)
    return DirectInstallPlan(
        project_root=project_root,
        save_root=save_root,
        foundry_plan=foundry_plan,
        items=foundry_items + architecture_items,
        levels_path=levels_path,
        levels_before_sha256=sha256(levels_payload).hexdigest(),
        levels_after=levels_after,
    )


def _validate_plan_unchanged(plan: DirectInstallPlan) -> dict[Path, bytes]:
    _reject_reparse_tree(plan.levels_path)
    if not plan.levels_path.is_file():
        raise RuntimeError("levels.txt is no longer a regular file")
    if sha256(plan.levels_path.read_bytes()).hexdigest() != plan.levels_before_sha256:
        raise RuntimeError("levels.txt changed after planning")
    expected_fingerprints = (
        plan.foundry_plan.source_fingerprint,
        plan.foundry_plan.foundry_fingerprint,
    )
    if _current_plan_fingerprints(plan.foundry_plan) != expected_fingerprints:
        raise RuntimeError("Foundry source or destination changed after planning")
    payloads: dict[Path, bytes] = {}
    for item in plan.items:
        current_kind, current_digest = _destination_state(item.destination)
        expected = (item.destination_before_kind, item.destination_before_sha256)
        if (current_kind, current_digest) != expected:
            raise RuntimeError(f"destination changed after planning: {item.destination}")
        source_payload = item.source.read_bytes()
        if sha256(source_payload).hexdigest() != item.source_sha256:
            raise RuntimeError(f"candidate changed after planning: {item.source}")
        decode_v15(source_payload)
        if sha256(item.payload).hexdigest() != item.sha256:
            raise RuntimeError(f"planned payload digest mismatch: {item.destination}")
        decode_v15(item.payload)
        payloads[item.destination] = item.payload
    if len(payloads) != len(plan.items):
        raise RuntimeError("multiple candidates resolved to the same destination")
    return payloads


def install_reviewed_direct(plan: DirectInstallPlan) -> dict[str, object]:
    """Write only final files in place; no backup, staging, or atomic temp files."""

    _assert_game_not_running()
    payloads = _validate_plan_unchanged(plan)
    _assert_game_not_running()
    for destination, payload in payloads.items():
        item = next(item for item in plan.items if item.destination == destination)
        current = _destination_state(destination)
        expected = (item.destination_before_kind, item.destination_before_sha256)
        if current != expected:
            raise RuntimeError(f"destination changed before write: {destination}")
        if current[1] == sha256(payload).hexdigest():
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(payload)
    _assert_game_not_running()
    _reject_reparse_tree(plan.levels_path)
    if sha256(plan.levels_path.read_bytes()).hexdigest() != plan.levels_before_sha256:
        raise RuntimeError("levels.txt changed before write")
    plan.levels_path.write_bytes(plan.levels_after)
    _validate_installed_plan(plan.foundry_plan)
    for item in plan.items:
        installed = item.destination.read_bytes()
        if sha256(installed).hexdigest() != item.sha256:
            raise RuntimeError(f"installed digest mismatch: {item.destination}")
        circuit = decode_v15(installed)
        if circuit.custom_id != item.custom_id:
            raise RuntimeError(f"installed custom_id mismatch: {item.destination}")
    if plan.levels_path.read_bytes() != plan.levels_after:
        raise RuntimeError("levels.txt direct write verification failed")
    return {
        "installed": True,
        "direct_write": True,
        "created_backup": False,
        "item_count": len(plan.items),
        "items": [item.to_dict() for item in plan.items],
        "levels_path": str(plan.levels_path),
        "selections": {
            level: schematic
            for level, (schematic, _) in ARCHITECTURE_TARGETS.items()
        },
    }
