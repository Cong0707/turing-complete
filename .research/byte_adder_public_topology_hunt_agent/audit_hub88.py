"""Exhaustively audit the public Hub 88 U8 ripple adder."""

from __future__ import annotations

from collections import Counter
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / ".research" / "byte_adder_public" / "hub-88" / "main" / "circuit.data"
ENGINE = (
    ROOT
    / "examples"
    / "rng"
    / "research"
    / "archive"
    / "rng_switch_public"
    / "analyze_hub79.py"
)
OUTPUT = HERE / "hub-88-certificate.json"


def load_engine():
    spec = importlib.util.spec_from_file_location("hub88_bit_parallel_engine", ENGINE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {ENGINE}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    module.CIRCUIT_PATH = SOURCE
    return module


def main() -> None:
    engine = load_engine()
    circuit, compiled, networks, _outputs = engine.evaluate()
    variables = tuple(engine.variable(index) for index in range(engine.VARIABLES))

    carry = variables[16]
    expected_sum: list[int] = []
    for left, right in zip(variables[:8], variables[8:16]):
        propagate = left ^ right
        expected_sum.append(propagate ^ carry)
        carry = (left & right) | (propagate & carry)

    sum_component = next(
        index
        for index, component in enumerate(circuit.components)
        if component.kind == 81 and component.user_label.casefold() == "sum"
    )
    cout_component = next(
        index
        for index, component in enumerate(circuit.components)
        if component.kind == 81 and component.user_label.casefold() == "cout"
    )
    sum_signal = networks[compiled.pin_network[(sum_component, "out")]]
    cout_signal = networks[compiled.pin_network[(cout_component, "out")]]

    if sum_signal.bits[:8] != tuple(expected_sum):
        raise RuntimeError("Hub 88 sum truth table mismatch")
    if cout_signal.bits[0] != carry:
        raise RuntimeError("Hub 88 carry truth table mismatch")
    conflict_cases = sum(signal.conflict.bit_count() for signal in networks.values())
    if conflict_cases:
        raise RuntimeError(f"Hub 88 contains {conflict_cases} packed driver conflicts")

    counts = Counter(component.kind for component in circuit.components)
    gate_breakdown = {
        "and": counts[4],
        "or": counts[7],
        "nor": counts[9],
    }
    if sum(gate_breakdown.values()) != circuit.gate:
        raise RuntimeError("primitive gate count does not match Hub 88 header")
    if (circuit.gate, circuit.delay) != (56, 18):
        raise RuntimeError(f"unexpected Hub 88 score: {circuit.gate}/{circuit.delay}")

    certificate = {
        "schema": "turing-complete-byte-adder-hub88-static-audit-v1",
        "source": SOURCE.relative_to(ROOT).as_posix(),
        "source_sha256": sha256(SOURCE.read_bytes()).hexdigest(),
        "serialized_score": {
            "gate": circuit.gate,
            "delay": circuit.delay,
            "energy": circuit.energy,
        },
        "component_count": len(circuit.components),
        "wire_count": len(circuit.wires),
        "component_kind_counts": {
            str(kind): count for kind, count in sorted(counts.items())
        },
        "reviewed_gate_cost_breakdown": gate_breakdown,
        "ripple_slice_average": {
            "bit_count": 8,
            "gate_per_bit": 7,
            "and_per_bit": 2,
            "or_per_bit": 1,
            "nor_per_bit": 4,
        },
        "input_schema": {"A": 8, "B": 8, "Cin": 1},
        "vectors_checked": engine.ASSIGNMENTS,
        "truth": {
            "sum_equals_low8_A_plus_B_plus_Cin": True,
            "cout_equals_bit8_A_plus_B_plus_Cin": True,
        },
        "output_depths": {
            "sum_word": sum_signal.depth,
            "cout": cout_signal.depth,
        },
        "packed_conflict_cases": conflict_cases,
        "custom_dependency_count": 0,
        "author_note": "Hub list attributes item 88 to SYSTEM-PSD, not FermiEnergy.",
    }
    OUTPUT.write_bytes(
        (json.dumps(certificate, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    )
    print(json.dumps(certificate, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
