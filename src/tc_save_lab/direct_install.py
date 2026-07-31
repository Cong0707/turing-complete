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


# Only architectures whose candidate has been checked against the current
# runtime and whose installed payload is already stable are eligible for the
# unattended direct-install plan.  Binary Search still needs game-side
# acceptance after its timing fix; RNG may contain user-owned design data.
ARCHITECTURE_TARGETS: dict[str, tuple[str, Path]] = {
    "circumference": (
        "CODEX-CIRCUMFERENCE",
        Path("examples/circumference/candidate/circuit.data"),
    ),
    "maze": ("CODEX-MAZE", Path("examples/maze/candidate/circuit.data")),
    "mod_4": ("CODEX-MOD-4", Path("examples/mod_4/candidate/circuit.data")),
    "nim": ("CODEX-NIM", Path("examples/nim/candidate/circuit.data")),
}


@dataclass(frozen=True)
class ReviewedNormalTarget:
    """获准直接部署的一份普通关卡精确候选。"""

    source: Path
    sha256: str
    gate: int
    delay: int


# 仅登记已完成完整语义验证和当前版本精灵几何复验的普通候选。摘要是审查
# 边界的一部分：重新生成的候选必须先接受新的审查，才允许直接部署。
NORMAL_TARGETS: dict[str, ReviewedNormalTarget] = {
    "and_gate_3": ReviewedNormalTarget(
        Path("examples/and_gate_3/candidate/circuit.data"),
        "2d79030732da73afb5e10cd632bb2607d91311cc4dfcd492bacb515737f62795",
        2,
        2,
    ),
    "bit_adder": ReviewedNormalTarget(
        Path("examples/bit_adder/candidate/circuit.data"),
        "446a2e5864c613f98e3d2eed7f40ff37a1a3f67e3677735d96d21dd4447a3a3b",
        3,
        2,
    ),
    "bit_inverter": ReviewedNormalTarget(
        Path("examples/bit_inverter/candidate/circuit.data"),
        "38d58faeff314b96b12caf1fc6dcc9a70277a3f4d9e4b2f5a4436b18fcf6a6ce",
        3,
        2,
    ),
    "byte_adder": ReviewedNormalTarget(
        Path("examples/byte_adder/candidate/circuit.data"),
        "b63723b21c16d535828a1a265a7714eea4b43faedacf8925aee8b0fbcd955e32",
        103,
        5,
    ),
    "byte_asr": ReviewedNormalTarget(
        Path("examples/byte_asr/candidate/circuit.data"),
        "c6218070e655602447806f533467c4ff1f2231a956895fbbd104b14dd7ddec8e",
        76,
        3,
    ),
    "byte_constant": ReviewedNormalTarget(
        Path("examples/byte_constant/candidate/circuit.data"),
        "8ba8cb2a677372a6ec4eef9c572666b4fbbf357bbf17c2f56cb218a50bda7131",
        0,
        0,
    ),
    "byte_equal": ReviewedNormalTarget(
        Path("examples/byte_equal/candidate/circuit.data"),
        "cc942e842d6e3f48aa36727d3f322c4aa0e9eeb4d7a335e42287d0c35016fec6",
        38,
        4,
    ),
    "byte_lsr": ReviewedNormalTarget(
        Path("examples/byte_lsr/candidate/circuit.data"),
        "3bf53bcc9b30c5b8f75a9257fa87e5f5ab0fc0000af189974a1864ccbd4234ca",
        70,
        3,
    ),
    "byte_mux": ReviewedNormalTarget(
        Path("examples/byte_mux/candidate/circuit.data"),
        "4cedcb5e016e6a206f3200fec44f9ae9f432c04a67640df2fa8e5ba845c2c020",
        33,
        2,
    ),
    "byte_nand": ReviewedNormalTarget(
        Path("examples/byte_nand/candidate/circuit.data"),
        "3af017e30a23b7c3ddfee89eb2a5aa23db3f8bbf73388333edbf41bb849b2ffd",
        8,
        1,
    ),
    "byte_not": ReviewedNormalTarget(
        Path("examples/byte_not/candidate/circuit.data"),
        "f461a23696812a47bf8e9751511ee7ca5483060dc1548227a02d5c552d2171d7",
        8,
        1,
    ),
    "byte_xor": ReviewedNormalTarget(
        Path("examples/byte_xor/candidate/circuit.data"),
        "3e75395b539d1f980d4f900d42a96d4af78a9a447770904bd1b3765127f36b41",
        24,
        2,
    ),
    "counting_signals": ReviewedNormalTarget(
        Path("examples/counting_signals/candidate/circuit.data"),
        "a8c772330a024989e3db2923a6554f783c09c5ae4b0ce552c6e673cdaf63c681",
        13,
        4,
    ),
    "decoder_2": ReviewedNormalTarget(
        Path("examples/decoder_2/candidate/circuit.data"),
        "f68d242fdc05b4c82d1d8d394be42f397c5efb3e5b1dd08dcca9d51c9e46be20",
        4,
        2,
    ),
    "decoder_3": ReviewedNormalTarget(
        Path("examples/decoder_3/candidate/circuit.data"),
        "27cd1ae3ec2ecc7d8037adc59d1850280917ff2b7a01093c7ed0dbb34f50274c",
        14,
        3,
    ),
    "one_hot_encoding": ReviewedNormalTarget(
        Path("examples/one_hot_encoding/candidate/circuit.data"),
        "76c1e6c77c6dbe86692a7122332564c9e338f55fead6dfc5af3986a510e29e14",
        70,
        3,
    ),
    "or_gate_3": ReviewedNormalTarget(
        Path("examples/or_gate_3/candidate/circuit.data"),
        "7ec9d41610fe2c2ddefbdc459c1c30326734b5112e20569011b13c483168a3bd",
        2,
        2,
    ),
    "saving_bytes": ReviewedNormalTarget(
        Path("examples/saving_bytes/candidate/circuit.data"),
        "5306cffa71ed8cc6aa2113cd7daaee1892d1565b952c7d79c59d26cfa46c714b",
        73,
        5,
    ),
    "saving_gracefully": ReviewedNormalTarget(
        Path("examples/saving_gracefully/candidate/circuit.data"),
        "f0d5632ddc9191b7702d07668aeeb2fdcd7a042a1b9fbf83f923633ee2cc0d26",
        10,
        5,
    ),
    "signed_negator": ReviewedNormalTarget(
        Path("examples/signed_negator/candidate/circuit.data"),
        "fb9c0d2bf13417ed73e59bbae92498182cb142cc79101894a7fd90f6f3062417",
        24,
        5,
    ),
    "xnor": ReviewedNormalTarget(
        Path("examples/xnor/candidate/circuit.data"),
        "ff0b222aa083a6195754eb6cd7ee4ca7e92222dd22515cfb6cea7423aad28971",
        3,
        2,
    ),
    "xor_gate": ReviewedNormalTarget(
        Path("examples/xor_gate/candidate/circuit.data"),
        "f8624d0e9c2a2afe0c757580b016803b4f0be89f0d0ad864872c2e16560079c7",
        3,
        2,
    ),
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
    normal_selections: tuple[tuple[str, str], ...]

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
            "normal_selections": dict(self.normal_selections),
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
    """Replace only the selected schematic field on reviewed architecture lines."""

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


def _selected_normal_schematics(payload: bytes) -> tuple[tuple[str, str], ...]:
    """读取每个已审查普通关卡唯一的当前所选电路图。"""

    parsed = _parse_levels(payload)
    selections: list[tuple[str, str]] = []
    for level in NORMAL_TARGETS:
        rows = [row for row in parsed if row and row[0] == level]
        if len(rows) != 1:
            raise ValueError(
                f"levels.txt must contain ordinary target {level!r} exactly once, "
                f"got {len(rows)}"
            )
        selected = rows[0][2] or "Default"
        candidate_path = Path(selected)
        if (
            candidate_path.name != selected
            or selected in {".", ".."}
            or any(character in selected for character in ("/", "\\", ":"))
            or any(ord(character) < 32 for character in selected)
        ):
            raise ValueError(
                f"普通关卡 {level!r} 的当前选择不是单一存档槽名: {selected!r}"
            )
        selections.append((level, selected))
    return tuple(selections)


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


def _normal_items(
    project_root: Path,
    save_root: Path,
    levels_payload: bytes,
) -> tuple[tuple[DirectInstallItem, ...], tuple[tuple[str, str], ...]]:
    """将已登记普通候选计划到各关卡当前选中的槽位。"""

    selections = _selected_normal_schematics(levels_payload)
    items: list[DirectInstallItem] = []
    for level, selected_schematic in selections:
        target = NORMAL_TARGETS[level]
        source = project_root / target.source
        _reject_reparse_tree(source)
        source = source.resolve()
        try:
            source.relative_to(project_root)
        except ValueError as exc:
            raise ValueError(f"普通候选路径越过项目根目录: {source}") from exc
        if not source.is_file():
            raise ValueError(f"已审查普通候选缺失: {source}")
        payload = source.read_bytes()
        source_digest = sha256(payload).hexdigest()
        if source_digest != target.sha256:
            raise ValueError(
                f"普通候选摘要与审查注册不一致，拒绝部署: {source}"
            )
        circuit = decode_v15(payload)
        if circuit.dependencies:
            raise ValueError(f"普通候选不能依赖 Foundry 元件: {source}")
        if (circuit.gate, circuit.delay) != (target.gate, target.delay):
            raise ValueError(
                f"普通候选成绩与审查注册不一致: {source} "
                f"({circuit.gate}/{circuit.delay})"
            )
        if encode_v15(circuit) != payload:
            raise ValueError(f"普通候选不是规范 v15 编码: {source}")

        schematics_root = save_root / "schematics"
        if not schematics_root.is_dir():
            raise ValueError(f"schematics directory does not exist: {schematics_root}")
        level_root = schematics_root / level
        if level_root.parent != schematics_root:
            raise ValueError(f"普通关卡目录越过 schematics 根目录: {level_root}")
        _reject_reparse_tree(level_root)
        if level_root.exists() and not level_root.is_dir():
            raise ValueError(f"普通关卡存档目录不是目录: {level_root}")
        destination = level_root / selected_schematic / "circuit.data"
        if destination.parent.parent != level_root:
            raise ValueError(f"普通关卡目标越过关卡目录: {destination}")
        destination_kind, destination_digest = _destination_state(destination)
        if destination_kind == "other":
            raise ValueError(f"普通关卡目标不是普通文件: {destination}")
        items.append(
            DirectInstallItem(
                kind="normal",
                name=level,
                source=source,
                destination=destination,
                source_sha256=source_digest,
                sha256=source_digest,
                custom_id=circuit.custom_id,
                destination_before_kind=destination_kind,
                destination_before_sha256=destination_digest,
                payload=payload,
            )
        )
    return tuple(items), selections


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
    levels_path = save_root / "levels.txt"
    _reject_reparse_tree(levels_path)
    if not levels_path.is_file():
        raise ValueError(f"levels.txt is not a regular file: {levels_path}")
    levels_payload = levels_path.read_bytes()
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
    normal_items, normal_selections = _normal_items(
        project_root,
        save_root,
        levels_payload,
    )
    architecture_items = _architecture_items(project_root, save_root)
    levels_after = rewrite_architecture_selections(levels_payload)
    return DirectInstallPlan(
        project_root=project_root,
        save_root=save_root,
        foundry_plan=foundry_plan,
        items=foundry_items + normal_items + architecture_items,
        levels_path=levels_path,
        levels_before_sha256=sha256(levels_payload).hexdigest(),
        levels_after=levels_after,
        normal_selections=normal_selections,
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
        "normal_selections": dict(plan.normal_selections),
    }
