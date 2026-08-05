#!/usr/bin/env python3
"""Read-only audit for the deployed Patchouli 84/6 Byte Adder candidate."""

from __future__ import annotations

import argparse
from dataclasses import replace
from hashlib import sha256
import json
import os
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "turingsynth" / "src"))

from tc_save_lab.analysis import analyze_file
from turingsynth.audit.relayout import audit_relayout
from turingsynth.formats.v15 import decode_v15


EXPECTED_SOURCE_SHA256 = (
    "16ad06eff5eb93e8bada90f5284ae4e3b1e21848e18319ccb11e6d6006030a51"
)
EXPECTED_DEPLOYED_SHA256 = (
    "953a83a229df9c1d104498f0dcefd9da216b63599445e7d9df85e543d175b14a"
)
EXPECTED_GAME_WIRE_GEOMETRY_SHA256 = (
    "df134468647fd0e67c8ee1b6aaf461ef9da3b60c62578bf7a858827959cfb770"
)
EXPECTED_SCORE = (84, 6, 504)


def _normalize_verified_game_save(source, candidate):
    """Remove only the metadata normalization performed by game 2.1.292.

    The game preserved every wire and all logic-bearing component fields.  It
    assigned the schematic identity/design buffer, selected its runtime clock,
    and normalized the display word_size field of the two splitters and merger.
    """

    top_level_fields = (
        "custom_id",
        "hub_id",
        "gate",
        "delay",
        "menu_visible",
        "clock_speed",
        "dependencies",
        "description",
        "sync_state",
        "score",
        "player_data",
        "hub_description",
        "design",
    )
    changed_top_level = [
        name
        for name in top_level_fields
        if getattr(source, name) != getattr(candidate, name)
    ]
    if changed_top_level != ["custom_id", "clock_speed", "design"]:
        raise RuntimeError(
            f"unexpected game top-level changes: {changed_top_level!r}"
        )
    if source.custom_id != 0 or candidate.custom_id != 5676103807039119249:
        raise RuntimeError("unexpected game-assigned custom_id")
    if (source.clock_speed, candidate.clock_speed) != (100_000, 1_000_000_000):
        raise RuntimeError("unexpected game clock normalization")
    if source.design != b"" or candidate.design != bytes(512):
        raise RuntimeError("unexpected game design buffer normalization")

    expected_word_size_changes = {5: 17, 6: 17, 78: 16}
    normalized_components = []
    observed_word_size_changes = {}
    for index, (left, right) in enumerate(zip(source.components, candidate.components)):
        left_static = replace(left, position=(0, 0), rotation=0)
        right_static = replace(right, position=(0, 0), rotation=0)
        if left_static != right_static:
            if (
                index not in expected_word_size_changes
                or right.kind != expected_word_size_changes[index]
                or (left.word_size, right.word_size) != (8, 1)
                or replace(right_static, word_size=left.word_size) != left_static
            ):
                raise RuntimeError(
                    f"unexpected game component normalization at index {index}"
                )
            observed_word_size_changes[index] = right.kind
            right = replace(right, word_size=left.word_size)
        normalized_components.append(right)
    if observed_word_size_changes != expected_word_size_changes:
        raise RuntimeError(
            "missing game word-size normalization: "
            f"{observed_word_size_changes!r}"
        )

    wire_geometry_sha256 = sha256(repr(candidate.wires).encode("utf-8")).hexdigest()
    if wire_geometry_sha256 != EXPECTED_GAME_WIRE_GEOMETRY_SHA256:
        raise RuntimeError(
            f"unexpected verified wire geometry: {wire_geometry_sha256}"
        )

    normalized = replace(
        candidate,
        custom_id=source.custom_id,
        clock_speed=source.clock_speed,
        design=source.design,
        components=tuple(normalized_components),
    )
    return normalized, {
        "status": "pass",
        "game_version": "2.1.292",
        "top_level_fields": changed_top_level,
        "component_word_size_changes": [
            {
                "index": index,
                "kind": kind,
                "before": 8,
                "after": 1,
            }
            for index, kind in expected_word_size_changes.items()
        ],
        "wire_geometry_preserved_after_game_save": True,
        "wire_geometry_sha256": wire_geometry_sha256,
        "logic_normalized_before_relayout_audit": True,
    }


def _digest(payload: bytes) -> str:
    return sha256(payload).hexdigest()


def _default_save() -> Path:
    appdata = Path(os.environ["APPDATA"])
    return appdata / "Turing Complete" / "schematics" / "byte_adder" / "Default" / "circuit.data"


def audit(save: Path) -> dict[str, object]:
    source_path = (
        HERE
        / "materialized_patchouli84_s5_five_gate"
        / "candidate"
        / "circuit.data"
    )
    candidate_path = ROOT / "examples" / "byte_adder" / "candidate" / "circuit.data"

    source_payload = source_path.read_bytes()
    candidate_payload = candidate_path.read_bytes()
    save_payload = save.read_bytes()
    source_hash = _digest(source_payload)
    candidate_hash = _digest(candidate_payload)
    save_hash = _digest(save_payload)

    if source_hash != EXPECTED_SOURCE_SHA256:
        raise RuntimeError(f"unexpected materialized source hash: {source_hash}")
    if candidate_hash != EXPECTED_DEPLOYED_SHA256:
        raise RuntimeError(f"unexpected repository candidate hash: {candidate_hash}")
    if save_hash != candidate_hash or save_payload != candidate_payload:
        raise RuntimeError("formal save differs from repository candidate")

    analysis = analyze_file(candidate_path)
    metrics = analysis["metrics"]
    score = (
        metrics["declared_gate"],
        metrics["declared_delay"],
        metrics["declared_energy_gate_delay"],
    )
    if score != EXPECTED_SCORE:
        raise RuntimeError(f"unexpected score: {score!r}")
    connectivity = metrics["connectivity"]
    for key in (
        "unconnected_pin_count",
        "multi_driver_network_count",
        "undriven_network_count",
        "sinkless_network_count",
        "width_mismatch_network_count",
        "cycle_component_count",
    ):
        if connectivity[key] != 0:
            raise RuntimeError(f"connectivity audit failed: {key}={connectivity[key]}")
    if metrics["component_kind_counts"].get(30, 0) != 0:
        raise RuntimeError("native com_add is present")

    source = decode_v15(source_payload)
    candidate = decode_v15(candidate_payload)
    normalized, game_canonicalization = _normalize_verified_game_save(
        source, candidate
    )
    relayout = audit_relayout(source, normalized)
    return {
        "schema": "patchouli-byte-adder-84-deployment-audit-v1",
        "status": "pass",
        "score": list(score),
        "source": str(source_path.relative_to(ROOT)).replace("\\", "/"),
        "source_sha256": source_hash,
        "candidate": str(candidate_path.relative_to(ROOT)).replace("\\", "/"),
        "candidate_sha256": candidate_hash,
        "formal_save": str(save),
        "formal_save_sha256": save_hash,
        "formal_save_matches": True,
        "component_count": metrics["component_count"],
        "wire_count": metrics["wire"]["wire_count"],
        "logical_network_count": connectivity["logical_network_count"],
        "native_com_add_count": 0,
        "connectivity": {
            key: connectivity[key]
            for key in (
                "unconnected_pin_count",
                "multi_driver_network_count",
                "undriven_network_count",
                "sinkless_network_count",
                "width_mismatch_network_count",
                "cycle_component_count",
            )
        },
        "game_canonicalization": game_canonicalization,
        "relayout": relayout,
        "in_game_verified": True,
        "in_game_verified_date": "2026-08-05",
        "backup_created": False,
        "game_started": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--save", type=Path, default=_default_save())
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit(args.save)
    payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output is not None:
        args.output.write_text(payload, encoding="utf-8", newline="\n")
    print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
