"""Directly install reviewed candidates without backup or transaction files."""

from __future__ import annotations

from dataclasses import dataclass
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
    _validate_installed_plan,
    plan_codex_deployment,
)
from .storage import DEFAULT_SAVE_ROOT


ARCHITECTURE_TARGETS: dict[str, tuple[str, Path]] = {
    "maze": ("CODEX-MAZE", Path("examples/maze/candidate/circuit.data")),
    "mod_4": ("CODEX-MOD-4", Path("examples/mod_4/candidate/circuit.data")),
}


@dataclass(frozen=True)
class DirectInstallItem:
    kind: str
    name: str
    source: Path
    destination: Path
    sha256: str
    custom_id: int = 0
    destination_before_sha256: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "kind": self.kind,
            "name": self.name,
            "source": str(self.source),
            "destination": str(self.destination),
            "sha256": self.sha256,
            "custom_id": self.custom_id,
            "destination_before_sha256": self.destination_before_sha256,
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

    _parse_levels(payload)
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
    rows = {row[0]: row for row in _parse_levels(result) if row}
    for level, (schematic, _) in ARCHITECTURE_TARGETS.items():
        if rows[level][2] != schematic:
            raise RuntimeError(f"failed to select {schematic} for {level}")
    return result


def _architecture_items(project_root: Path, save_root: Path) -> tuple[DirectInstallItem, ...]:
    items: list[DirectInstallItem] = []
    architecture_root = (save_root / "schematics" / "architecture").resolve()
    if not architecture_root.is_dir():
        raise ValueError(f"architecture directory does not exist: {architecture_root}")
    for level, (schematic, relative_source) in ARCHITECTURE_TARGETS.items():
        source = (project_root / relative_source).resolve()
        destination = (architecture_root / schematic / "circuit.data").resolve()
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
        digest = sha256(payload).hexdigest()
        expected_target = f"schematics/architecture/{schematic}/circuit.data"
        if metadata.get("sha256") != digest:
            raise ValueError(f"architecture metadata digest mismatch: {source}")
        if metadata.get("deployment_target") != expected_target:
            raise ValueError(f"architecture metadata target mismatch: {source}")
        items.append(
            DirectInstallItem(
                kind="architecture",
                name=level,
                source=source,
                destination=destination,
                sha256=digest,
                destination_before_sha256=(
                    sha256(destination.read_bytes()).hexdigest()
                    if destination.is_file()
                    else None
                ),
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
    foundry_items = tuple(
        DirectInstallItem(
            kind="foundry",
            name=item.display_path,
            source=item.source,
            destination=item.destination,
            sha256=item.sha256,
            custom_id=item.custom_id,
            destination_before_sha256=(
                sha256(item.destination.read_bytes()).hexdigest()
                if item.destination.is_file()
                else None
            ),
        )
        for item in foundry_plan.items
    )
    architecture_items = _architecture_items(project_root, save_root)
    levels_path = save_root / "levels.txt"
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
        current_destination_sha = (
            sha256(item.destination.read_bytes()).hexdigest()
            if item.destination.is_file()
            else None
        )
        if current_destination_sha != item.destination_before_sha256:
            raise RuntimeError(f"destination changed after planning: {item.destination}")
        payload = item.source.read_bytes()
        if sha256(payload).hexdigest() != item.sha256:
            raise RuntimeError(f"candidate changed after planning: {item.source}")
        decode_v15(payload)
        payloads[item.destination] = payload
    return payloads


def install_reviewed_direct(plan: DirectInstallPlan) -> dict[str, object]:
    """Write only final files in place; no backup, staging, or atomic temp files."""

    _assert_game_not_running()
    payloads = _validate_plan_unchanged(plan)
    _assert_game_not_running()
    for destination, payload in payloads.items():
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(payload)
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
