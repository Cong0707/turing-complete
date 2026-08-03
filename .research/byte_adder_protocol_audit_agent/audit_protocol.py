"""只读审计当前 Byte Adder 协议、候选和正式存档。"""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path

from tc_save_lab.codec import decode_circuit
from tc_save_lab.pins import analyze_connectivity, positioned_pins
from tc_save_lab.primitive_candidates import layout_safety


REPOSITORY = Path(__file__).resolve().parents[2]
GAME = Path(r"D:\Game\Steam\steamapps\common\Turing Complete")
SAVE = Path(r"C:\Users\cong\AppData\Roaming\Turing Complete")


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def gf2_rank(columns: list[int]) -> int:
    basis: dict[int, int] = {}
    for value in columns:
        while value:
            pivot = value.bit_length() - 1
            if pivot in basis:
                value ^= basis[pivot]
            else:
                basis[pivot] = value
                break
    return len(basis)


def transform_tick(tick: int) -> int:
    value = tick
    value ^= value << 6
    value ^= value >> 11
    value ^= value << 9
    return value & 0x1FFFF


def test_domain_audit() -> dict[str, object]:
    images = [transform_tick(tick) for tick in range(0x20000)]
    columns = [transform_tick(1 << bit) for bit in range(17)]
    return {
        "tick_first": 0,
        "tick_last": 0x1FFFF,
        "test_count": len(images),
        "unique_17_bit_inputs": len(set(images)),
        "gf2_rank": gf2_rank(columns),
        "covers_full_domain": set(images) == set(range(0x20000)),
        "basis_columns_hex": [f"0x{value:05x}" for value in columns],
    }


def circuit_audit(path: Path) -> dict[str, object]:
    payload = path.read_bytes()
    circuit = decode_circuit(payload)
    try:
        layout: dict[str, int] | dict[str, str] = layout_safety(circuit)
    except RuntimeError as error:
        layout = {"status": "not_audited", "reason": str(error)}
    return {
        "path": str(path),
        "size": len(payload),
        "sha256": sha256(payload).hexdigest(),
        "format_version": payload[0],
        "gate": circuit.gate,
        "delay": circuit.delay,
        "component_count": len(circuit.components),
        "wire_count": len(circuit.wires),
        "component_kind_counts": dict(sorted(Counter(item.kind for item in circuit.components).items())),
        "components": [
            {
                **asdict(component),
                "pins": [asdict(pin) for pin in positioned_pins(component, index)],
            }
            for index, component in enumerate(circuit.components)
        ],
        "connectivity": analyze_connectivity(circuit),
        "layout": layout,
    }


def main() -> None:
    campaign = GAME / "campaign" / "byte_adder"
    candidate = REPOSITORY / "examples" / "byte_adder" / "candidate" / "circuit.data"
    formal = SAVE / "schematics" / "byte_adder" / "Default" / "circuit.data"
    hint = campaign / "hint_solution.data"
    public_4d = (
        REPOSITORY
        / ".research"
        / "rng_public_artifacts"
        / "hub-79-adder"
        / "main"
        / "circuit.data"
    )

    report = {
        "scope": "read-only; no game process; no save writes",
        "campaign": {
            "meta_path": str(campaign / "meta.txt"),
            "meta_sha256": digest(campaign / "meta.txt"),
            "test_path": str(campaign / "test.si"),
            "test_sha256": digest(campaign / "test.si"),
            "self_unlock": "com_add",
            "kind": "combinational",
            "immutable_io": circuit_audit(campaign / "circuit.data"),
            "official_hint_solution": circuit_audit(hint),
        },
        "test_domain": test_domain_audit(),
        "candidate": circuit_audit(candidate),
        "formal": circuit_audit(formal),
        "candidate_formal_exact_bytes": candidate.read_bytes() == formal.read_bytes(),
        "public_4_delay_reference": circuit_audit(public_4d),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
