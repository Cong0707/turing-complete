"""Static campaign discovery and reproducible per-level workspace creation."""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import json
import re
import shutil

from .codec import decode_v15
from .storage import LevelProgress, read_progress, selected_circuit_path


LEVEL_COMPONENT_KINDS = {41, 59}


def read_level_meta(path: Path) -> dict[str, object]:
    if not path.is_file():
        return {}
    text = path.read_text("utf-8", errors="replace")
    result: dict[str, object] = {}
    for key in ("kind", "size", "next_level", "no_score", "no_controls"):
        match = re.search(rf"(?m)^\s*{re.escape(key)}\s*=\s*([^\r\n]+)", text)
        if not match:
            continue
        raw = match.group(1).strip()
        if raw.casefold() in {"true", "false"}:
            result[key] = raw.casefold() == "true"
        elif raw.startswith('"') and raw.endswith('"'):
            result[key] = raw[1:-1]
        elif raw.isdigit():
            result[key] = int(raw)
        else:
            result[key] = raw
    title = re.search(r"(?m)^\s*title\s*=.*?`([^`]*)`", text)
    if title:
        result["title"] = title.group(1)
    return result


def campaign_levels(campaign_root: Path) -> list[str]:
    main = decode_v15((campaign_root / "main" / "circuit.data").read_bytes())
    candidates = []
    seen: set[str] = set()
    for component in main.components:
        name = component.user_label
        if (
            component.kind in LEVEL_COMPONENT_KINDS
            and name
            and name not in seen
            and (campaign_root / name).is_dir()
        ):
            candidates.append(component)
            seen.add(name)
    # The binary component order is an editor artifact. The map itself is laid
    # out from top to bottom; x resolves parallel branches on the same row.
    candidates.sort(key=lambda component: (-component.position[1], component.position[0]))
    return [component.user_label for component in candidates]


def _asset_record(path: Path, relative_path: str) -> dict[str, object] | None:
    if not path.is_file():
        return None
    payload = path.read_bytes()
    return {
        "path": relative_path,
        "size": len(payload),
        "sha256": sha256(payload).hexdigest(),
        "format_version": payload[0] if payload else None,
    }


def initialize_examples(
    project_root: Path,
    campaign_root: Path,
    save_root: Path,
) -> dict[str, object]:
    levels = campaign_levels(campaign_root)
    progress = read_progress(save_root / "levels.txt")
    examples = project_root / "examples"
    examples.mkdir(parents=True, exist_ok=True)
    exported = 0
    missing = 0
    manifest: list[dict[str, object]] = []
    architectures: dict[str, dict[str, object]] = {}

    for order, level in enumerate(levels, start=1):
        level_dir = examples / level
        baseline_dir = level_dir / "baseline"
        candidate_dir = level_dir / "candidate"
        baseline_dir.mkdir(parents=True, exist_ok=True)
        candidate_dir.mkdir(parents=True, exist_ok=True)

        meta = read_level_meta(campaign_root / level / "meta.txt")
        selected = progress.get(level, LevelProgress(level, False, "Default", ""))
        is_architecture = meta.get("kind") == "architecture"
        if is_architecture:
            source = save_root / "schematics" / "architecture" / selected.selected_schematic / "circuit.data"
            source_relative = f"schematics/architecture/{selected.selected_schematic}/circuit.data"
        else:
            source = selected_circuit_path(save_root, progress, level)
            source_relative = (
                f"schematics/{level}/"
                f"{selected.selected_schematic or 'Default'}/circuit.data"
            )
        baseline = baseline_dir / "circuit.data"
        if source.is_file() and not is_architecture:
            shutil.copyfile(source, baseline)
            exported += 1
            baseline_record = _asset_record(baseline, "baseline/circuit.data")
            try:
                parsed = decode_v15(baseline.read_bytes())
                baseline_record.update(
                    {
                        "valid_v15": True,
                        "gate": parsed.gate,
                        "delay": parsed.delay,
                        "energy": parsed.energy,
                        "component_count": len(parsed.components),
                        "wire_count": len(parsed.wires),
                    }
                )
            except Exception as exc:
                baseline_record.update({"valid_v15": False, "error": str(exc)})
        else:
            if not is_architecture:
                missing += 1
            baseline_record = None
            baseline.unlink(missing_ok=True)

        architecture_record = None
        if is_architecture:
            architecture_dir = examples / "_architectures" / selected.selected_schematic
            architecture_baseline = architecture_dir / "baseline" / "circuit.data"
            architecture_baseline.parent.mkdir(parents=True, exist_ok=True)
            (architecture_dir / "candidate").mkdir(parents=True, exist_ok=True)
            if selected.selected_schematic in architectures:
                architecture_record = architectures[selected.selected_schematic]["baseline"]
            elif source.is_file():
                shutil.copyfile(source, architecture_baseline)
                exported += 1
                architecture_record = _asset_record(
                    architecture_baseline,
                    f"_architectures/{selected.selected_schematic}/baseline/circuit.data",
                )
                parsed = decode_v15(architecture_baseline.read_bytes())
                architecture_record.update(
                    {
                        "valid_v15": True,
                        "gate": parsed.gate,
                        "delay": parsed.delay,
                        "energy": parsed.energy,
                        "component_count": len(parsed.components),
                        "wire_count": len(parsed.wires),
                    }
                )
            elif selected.selected_schematic not in architectures:
                missing += 1
            if selected.selected_schematic not in architectures:
                architectures[selected.selected_schematic] = {
                    "scheme": selected.selected_schematic,
                    "source": source_relative,
                    "baseline": architecture_record,
                }

        record: dict[str, object] = {
            "order": order,
            "level": level,
            "title": meta.get("title", level),
            "kind": meta.get("kind"),
            "no_score": bool(meta.get("no_score", False)),
            "scoreable": not bool(meta.get("no_score", False)),
            "complete": selected.complete,
            "selected_schematic": selected.selected_schematic,
            "score_history": selected.score_history,
            "current_save_source": source_relative,
            "baseline": baseline_record,
            "architecture": selected.selected_schematic if is_architecture else None,
            "architecture_baseline": architecture_record,
            "campaign_circuit": _asset_record(
                campaign_root / level / "circuit.data", f"campaign/{level}/circuit.data"
            ),
            "campaign_hint_solution": _asset_record(
                campaign_root / level / "hint_solution.data",
                f"campaign/{level}/hint_solution.data",
            ),
            "candidate_status": "pending",
        }
        (level_dir / "level.json").write_text(
            json.dumps(record, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (candidate_dir / ".gitkeep").touch()
        manifest.append(record)

    top = {
        "campaign_main": _asset_record(campaign_root / "main" / "circuit.data", "campaign/main/circuit.data"),
        "level_count": len(levels),
        "baseline_exported": exported,
        "baseline_missing": missing,
        "architectures": list(architectures.values()),
        "levels": manifest,
    }
    (examples / "manifest.json").write_text(
        json.dumps(top, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return top
