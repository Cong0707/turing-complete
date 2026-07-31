"""Extract minimal immutable campaign interfaces for candidate generation."""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict
from hashlib import sha256
from pathlib import Path
import json

from .campaign import campaign_levels
from .codec import decode_circuit
from .model import Component


LEVEL_INPUT_KINDS = frozenset({60, 61, 62, 63, 64, 65, 106})
LEVEL_OUTPUT_KINDS = frozenset({40, 58, 68, 69, 70, 73, 74, 75, 77})


def component_role(component: Component) -> str:
    if component.kind in LEVEL_INPUT_KINDS:
        return "input"
    if component.kind in LEVEL_OUTPUT_KINDS:
        return "output"
    return "fixed"


def _component_record(component: Component) -> dict[str, object]:
    result = asdict(component)
    result["role"] = component_role(component)
    return result


def _duplicates(values: list[int]) -> list[int]:
    counts = Counter(values)
    return sorted(value for value, count in counts.items() if count > 1)


def extract_level_scaffold(
    project_root: Path,
    campaign_root: Path,
    level: str,
) -> dict[str, object]:
    source = campaign_root / level / "circuit.data"
    payload = source.read_bytes()
    circuit = decode_circuit(payload)
    immutable = tuple(component for component in circuit.components if component.immutable)
    immutable_ids = [component.permanent_id for component in immutable]
    if 0 in immutable_ids:
        raise ValueError(f"immutable component without permanent ID in {level}")
    duplicate_immutable_ids = _duplicates(immutable_ids)
    if duplicate_immutable_ids:
        raise ValueError(
            f"duplicate immutable permanent IDs in {level}: {duplicate_immutable_ids}"
        )

    baseline_path = project_root / "examples" / level / "baseline" / "circuit.data"
    embedded_ids: list[int] = []
    baseline_record: dict[str, object] | None = None
    if baseline_path.is_file():
        baseline_payload = baseline_path.read_bytes()
        baseline = decode_circuit(baseline_payload)
        baseline_ids = {component.permanent_id for component in baseline.components}
        embedded_ids = sorted(baseline_ids.intersection(immutable_ids))
        baseline_record = {
            "path": "baseline/circuit.data",
            "format_version": baseline_payload[0],
            "sha256": sha256(baseline_payload).hexdigest(),
            "embedded_immutable_permanent_ids": embedded_ids,
        }

    result: dict[str, object] = {
        "level": level,
        "source": f"campaign/{level}/circuit.data",
        "source_format_version": payload[0],
        "source_size": len(payload),
        "source_sha256": sha256(payload).hexdigest(),
        "source_component_count": len(circuit.components),
        "source_wire_count": len(circuit.wires),
        "immutable_component_count": len(immutable),
        "mutable_seed_component_count": len(circuit.components) - len(immutable),
        "interface_input_count": sum(
            component.kind in LEVEL_INPUT_KINDS for component in immutable
        ),
        "interface_output_count": sum(
            component.kind in LEVEL_OUTPUT_KINDS for component in immutable
        ),
        "duplicate_source_permanent_ids": _duplicates(
            [component.permanent_id for component in circuit.components]
        ),
        "baseline": baseline_record,
        "immutable_components": [_component_record(component) for component in immutable],
    }

    destination = (
        project_root / "examples" / level / "scaffold" / "immutable.json"
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return result


def extract_campaign_scaffolds(
    project_root: Path,
    campaign_root: Path,
) -> dict[str, object]:
    records = [
        extract_level_scaffold(project_root, campaign_root, level)
        for level in campaign_levels(campaign_root)
    ]
    summary = {
        "level_count": len(records),
        "format_versions": dict(
            sorted(Counter(record["source_format_version"] for record in records).items())
        ),
        "immutable_component_count": sum(
            int(record["immutable_component_count"]) for record in records
        ),
        "empty_scaffold_count": sum(
            int(record["immutable_component_count"]) == 0 for record in records
        ),
        "baseline_embedded_immutable_count": sum(
            len(record["baseline"]["embedded_immutable_permanent_ids"])
            for record in records
            if record["baseline"] is not None
        ),
    }
    destination = project_root / "examples" / "scaffolds.json"
    destination.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return summary
