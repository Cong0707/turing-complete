"""Build the one-register RNG phase-control retiming candidate.

This keeps the reviewed 396-gate encoded RNG datapath unchanged.  The only
change is to initialize its phase Delay Bit to one, drive it with constant
zero, use the register output directly for Level Input enable, and use the
existing NOT only for Level Output enable.  The seed path therefore avoids
the NOT delay while the gate count remains unchanged.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path

from tc_save_lab.codec import decode_v15, encode_v15
from tc_save_lab.rng_encoded_asic import (
    _FOOTPRINT_BOXES,
    _build_router,
    _pin,
    build_rng_encoded_asic,
    verify_rng_encoded_asic,
)


def build_control_retimed_rng():
    circuit = build_rng_encoded_asic()
    components = list(circuit.components)

    level_input = components[0]
    level_output = components[1]
    phase_constant = replace(components[2], kind=1, init_data=0)
    phase_delay = replace(components[3], init_data=1)
    output_enable = components[4]
    components[2:5] = (phase_constant, phase_delay, output_enable)
    component_tuple = tuple(components)

    # Constant False has the same one-bit footprint as Constant True.
    _FOOTPRINT_BOXES.setdefault(1, _FOOTPRINT_BOXES[2])
    route = _build_router(component_tuple)
    wires = list(circuit.wires)
    wires[2] = route(_pin(phase_delay, "out"), _pin(level_input, "control"))
    wires[4] = route(_pin(output_enable, "out"), _pin(level_output, "control"))

    return replace(
        circuit,
        description=(
            "Codex RNG ASIC: encoded depth-two XOR network with an init-one "
            "phase register; input enable is direct and output enable inverted"
        ),
        components=component_tuple,
        wires=tuple(wires),
    )


def write_candidate(project_root: Path) -> dict[str, object]:
    circuit = build_control_retimed_rng()
    verification = verify_rng_encoded_asic(circuit)
    counts = Counter(component.kind for component in circuit.components)
    expected = {1: 1, 2: 0, 3: 1, 7: 47, 10: 61, 13: 33}
    for kind, count in expected.items():
        if counts[kind] != count:
            raise RuntimeError(f"kind {kind} count {counts[kind]} != {count}")

    delays = [component for component in circuit.components if component.kind == 13]
    if Counter(component.init_data for component in delays) != {0: 32, 1: 1}:
        raise RuntimeError("phase/state Delay Bit initial values changed")

    payload = encode_v15(circuit)
    if decode_v15(payload) != circuit:
        raise RuntimeError("control-retimed RNG failed v15 round trip")

    destination = project_root / ".research" / "rng_control_retime" / "circuit.data"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(payload)
    metadata = {
        "schema": 1,
        "status": "offline-verified; game metric recomputation pending",
        "strategy": "single init-one phase Delay; NOT moved to output enable only",
        "sha256": sha256(payload).hexdigest(),
        "gate": circuit.gate,
        "delay": circuit.delay,
        "cycles": 66,
        "leaderboard_tuple": [circuit.gate, circuit.delay, 66],
        "energy": circuit.gate * circuit.delay * 66,
        "component_count": len(circuit.components),
        "wire_count": len(circuit.wires),
        "component_kind_counts": dict(sorted(counts.items())),
        "phase_delay_init_data": 1,
        "timing": {
            "seed_control": "phase Delay 4 + OR 1 + XOR 2 + XOR 2 = 9",
            "steady_feedback": "state Delay 4 + OR 1 + XOR 2 + XOR 2 = 9",
            "output_control": "phase Delay 4 + NOT 1 = 5",
        },
        "verification": verification,
    }
    (destination.parent / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return metadata


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2]
    print(json.dumps(write_candidate(root), ensure_ascii=False, indent=2))
