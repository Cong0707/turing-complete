"""Generate and verify the current-version zero-gate Mod 4 ASIC."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

from .builder import stable_permanent_id, wire_from_vertices
from .codec import decode_v15, encode_v15
from .model import Circuit, Component
from .pins import analyze_connectivity


def evaluate_mod_4(value: int) -> int:
    if not 0 <= value <= 0xFF:
        raise ValueError(f"value must be an unsigned byte, got {value}")
    return value & 0b11


def build_mod_4_asic() -> Circuit:
    key = "architecture/codex-mod-4"
    component = lambda role, kind, position, **kwargs: Component(
        kind=kind,
        position=position,
        rotation=0,
        permanent_id=stable_permanent_id(key, role),
        **kwargs,
    )
    components = (
        component("level-input", 62, (-4, 0), word_size=2),
        component("level-output", 70, (4, 0), word_size=2),
        component("enable", 2, (-5, 4)),
    )
    wires = (
        wire_from_vertices(((-4, 4), (-4, -2), (-3, -2))),
        wire_from_vertices(((-4, 4), (3, 4), (3, -2))),
        wire_from_vertices(((-1, 0), (1, 0))),
    )
    return Circuit(
        gate=0,
        delay=0,
        description="Codex Mod 4 ASIC: U2 input truncation wired directly to U2 output",
        components=components,
        wires=wires,
    )


def verify_mod_4_asic(circuit: Circuit | None = None) -> dict[str, object]:
    candidate = build_mod_4_asic() if circuit is None else circuit
    for value in range(256):
        if evaluate_mod_4(value) != value % 4:
            raise RuntimeError(f"Mod 4 arithmetic regression at input {value}")
    connectivity = analyze_connectivity(candidate)
    for field in (
        "unsupported_component_kind_counts",
        "unconnected_pin_count",
        "multi_driver_network_count",
        "width_mismatch_network_count",
        "cycle_component_count",
    ):
        if connectivity[field]:
            raise RuntimeError(f"Mod 4 ASIC failed connectivity check {field}: {connectivity[field]}")
    if candidate.gate or candidate.delay:
        raise RuntimeError("Mod 4 direct truncation must remain a zero-gate, zero-delay circuit")
    return {
        "gate": 0,
        "delay": 0,
        "cycles": 1,
        "leaderboard_tuple": [0, 0, 1],
        "energy": 0,
        "exhaustive_test_vectors": 256,
        "connectivity": connectivity,
    }


def write_mod_4_asic(project_root: Path) -> dict[str, object]:
    candidate = build_mod_4_asic()
    verification = verify_mod_4_asic(candidate)
    payload = encode_v15(candidate)
    if decode_v15(payload) != candidate:
        raise RuntimeError("Mod 4 ASIC failed v15 round-trip verification")
    destination = project_root / "examples" / "mod_4" / "candidate" / "circuit.data"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(payload)
    (destination.parent / ".gitkeep").unlink(missing_ok=True)
    metadata = {
        "schema": 1,
        "level": "mod_4",
        "title": "Mod 4",
        "strategy": "current-v15 direct-width ASIC",
        "deployment_target": "schematics/architecture/CODEX-MOD-4/circuit.data",
        "sha256": sha256(payload).hexdigest(),
        "format_version": 15,
        "component_count": len(candidate.components),
        "wire_count": len(candidate.wires),
        **verification,
    }
    (destination.parent / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return metadata
