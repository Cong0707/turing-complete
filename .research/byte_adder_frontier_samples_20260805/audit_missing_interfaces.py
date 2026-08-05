#!/usr/bin/env python3
"""Audit the early-state interfaces missing from the verified 84/6 adder.

This is a fixed-node bridge audit, not a circuit synthesis search.  It checks
the signals already present in the verified Patchouli 84/6 DAG and in the
three user-supplied frontier samples.  The only derived candidates are one
ordinary gate or one Bit Switch over already-present early signals.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
PATCHOULI_DAG = (
    PROJECT
    / ".research"
    / "byte84_patchouli_image"
    / "byte-adder-patchouli84-s5-five-gate-full.json"
)
SAMPLE_ANALYZER = HERE / "analyze_frontier_samples.py"
SAMPLES = (
    HERE / "raw" / "extracted" / "Switch 154 4" / "circuit.data",
    HERE / "raw" / "extracted" / "Switch 103 5 A" / "circuit.data",
    HERE / "raw" / "extracted" / "Switch 103 5 B" / "circuit.data",
)

VARIABLE_COUNT = 17
ASSIGNMENT_COUNT = 1 << VARIABLE_COUNT
ALL = (1 << ASSIGNMENT_COUNT) - 1
TABLE_BYTES = ASSIGNMENT_COUNT // 8


@dataclass(frozen=True)
class Signal:
    value: int
    driven: int
    arrival: int
    conflict: int = 0


def variable(index: int) -> int:
    if index < 3:
        byte = (0xAA, 0xCC, 0xF0)[index]
        return int.from_bytes(bytes([byte]) * TABLE_BYTES, "little")
    block = 1 << (index - 3)
    data = (bytes(block) + bytes([0xFF]) * block) * (
        ASSIGNMENT_COUNT // (16 * block)
    )
    return int.from_bytes(data, "little")


def normal(value: int, arrival: int, conflict: int = 0) -> Signal:
    return Signal(value & ALL, ALL, arrival, conflict)


def resolve(drivers: list[Signal], arrival: int) -> Signal:
    ones = 0
    zeros = 0
    driven = 0
    conflict = 0
    for driver in drivers:
        ones |= driver.value & driver.driven
        zeros |= (~driver.value & ALL) & driver.driven
        driven |= driver.driven
        conflict |= driver.conflict
    conflict |= ones & zeros
    return Signal(ones, driven, arrival, conflict)


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def evaluate_patchouli() -> tuple[dict[int, Signal], dict[int, str]]:
    document = json.loads(PATCHOULI_DAG.read_text(encoding="utf-8"))
    nodes = document["factory_dag"]["nodes"]
    signals: dict[int, Signal] = {}
    labels: dict[int, str] = {}

    for node in nodes:
        node_id = node["id"]
        op = node["op"]
        args = node["args"]
        arrival = node["arrival"]
        labels[node_id] = node.get("label", "")
        if op == "INPUT":
            label = node["label"]
            if label == "cin":
                value = variable(16)
            elif label.startswith("a"):
                value = variable(int(label[1:]))
            elif label.startswith("b"):
                value = variable(8 + int(label[1:]))
            else:
                raise RuntimeError(f"unknown input label {label!r}")
            signal = normal(value, arrival)
        elif op in {"AND", "OR", "NAND", "NOR", "XOR"}:
            left = signals[args[0]].value
            right = signals[args[1]].value
            conflict = signals[args[0]].conflict | signals[args[1]].conflict
            if op == "AND":
                value = left & right
            elif op == "OR":
                value = left | right
            elif op == "NAND":
                value = ~(left & right) & ALL
            elif op == "NOR":
                value = ~(left | right) & ALL
            else:
                value = left ^ right
            signal = normal(value, arrival, conflict)
        elif op == "BUS":
            drivers = []
            for enable_id, data_id in zip(args[::2], args[1::2]):
                enable = signals[enable_id]
                data = signals[data_id]
                drivers.append(
                    Signal(
                        value=data.value,
                        driven=enable.value,
                        arrival=arrival,
                        conflict=enable.conflict | data.conflict,
                    )
                )
            signal = resolve(drivers, arrival)
        else:
            raise RuntimeError(f"unsupported Patchouli op {op!r}")
        signals[node_id] = signal

    conflict = 0
    for signal in signals.values():
        conflict |= signal.conflict
    if conflict:
        raise RuntimeError(
            f"verified Patchouli DAG unexpectedly conflicts on {conflict.bit_count()} rows"
        )
    return signals, labels


def target_functions() -> dict[str, int]:
    variables = tuple(variable(index) for index in range(VARIABLE_COUNT))
    a = variables[:8]
    b = variables[8:16]
    carry = variables[16]
    generates = tuple(left & right for left, right in zip(a, b))
    propagates = tuple(left ^ right for left, right in zip(a, b))
    values_or = tuple(left | right for left, right in zip(a, b))
    carries = [carry]
    for generate, propagate in zip(generates, propagates):
        carries.append(generate | (propagate & carries[-1]))

    b23 = (
        values_or[2]
        & values_or[3]
        & (carries[2] | generates[2])
    )
    e6 = b23 | generates[3] | generates[4] | generates[5]
    d45 = generates[5] | (values_or[4] & values_or[5])
    return {
        "C4": carries[4],
        "nC4": ~carries[4] & ALL,
        "C6": carries[6],
        "nC6": ~carries[6] & ALL,
        "E6": e6,
        "D45": d45,
    }


def matches(value: int, target: int, care: int) -> bool:
    return ((value ^ target) & care) == 0


def bridge_audit(
    signals: dict[int, Signal],
    labels: dict[int, str],
    target: int,
    care: int,
    output_arrival: int,
) -> dict[str, object]:
    existing = [
        {
            "node": node_id,
            "label": labels.get(node_id, ""),
            "arrival": signal.arrival,
            "driven_rows": signal.driven.bit_count(),
        }
        for node_id, signal in signals.items()
        if signal.arrival <= output_arrival
        and matches(signal.value, target, care)
    ]
    roots = sorted(
        node_id
        for node_id, signal in signals.items()
        if signal.arrival <= output_arrival - 1
    )
    ordinary: list[dict[str, object]] = []
    switches: list[dict[str, object]] = []
    for left_index, left_id in enumerate(roots):
        left = signals[left_id].value
        not_value = ~left & ALL
        if matches(not_value, target, care):
            ordinary.append({"op": "NOT", "args": [left_id]})
        for right_id in roots[left_index:]:
            right = signals[right_id].value
            candidates = {
                "AND": left & right,
                "OR": left | right,
                "NAND": ~(left & right) & ALL,
                "NOR": ~(left | right) & ALL,
            }
            for op, value in candidates.items():
                if matches(value, target, care):
                    ordinary.append({"op": op, "args": [left_id, right_id]})
    for enable_id in roots:
        enable = signals[enable_id].value
        for data_id in roots:
            value = enable & signals[data_id].value
            if matches(value, target, care):
                switches.append({"op": "SWITCH", "args": [enable_id, data_id]})
    return {
        "eligible_root_count": len(roots),
        "existing_matches": existing,
        "one_ordinary_gate_matches": ordinary,
        "one_bit_switch_matches": switches,
    }


def sample_audits(targets: dict[str, int]) -> list[dict[str, object]]:
    analyzer = load_module(SAMPLE_ANALYZER, "frontier_sample_analyzer_for_gap_audit")
    from tc_save_lab.codec import decode_v15

    result = []
    for path in SAMPLES:
        circuit = decode_v15(path.read_bytes())
        compiled = analyzer.compile_circuit(circuit)
        _, networks, _ = analyzer.evaluate(circuit, compiled)
        signals = {
            root: Signal(
                value=signal.bits[0],
                driven=signal.driven,
                arrival=signal.depth,
                conflict=signal.conflict,
            )
            for root, signal in networks.items()
            if len(signal.bits) == 1
        }
        labels = {root: f"network-{root}" for root in signals}
        result.append(
            {
                "sample": path.parent.name,
                "source_sha256": sha256(path.read_bytes()).hexdigest(),
                "nC4_at_D3": bridge_audit(
                    signals, labels, targets["nC4"], ALL, 3
                ),
                "E6_at_D3_under_D45_care": bridge_audit(
                    signals, labels, targets["E6"], targets["D45"], 3
                ),
            }
        )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=HERE / "derived" / "missing-interface-audit.json",
    )
    args = parser.parse_args()

    targets = target_functions()
    patchouli_signals, patchouli_labels = evaluate_patchouli()
    report = {
        "schema": "byte-adder-frontier-sample-interface-gap-audit-v1",
        "scope": (
            "Fixed existing nodes plus one ordinary gate or one Bit Switch; "
            "this is not general circuit synthesis."
        ),
        "patchouli84": {
            "source": str(PATCHOULI_DAG),
            "source_sha256": sha256(PATCHOULI_DAG.read_bytes()).hexdigest(),
            "E6_at_D3_under_D45_care": bridge_audit(
                patchouli_signals,
                patchouli_labels,
                targets["E6"],
                targets["D45"],
                3,
            ),
            "nC6_at_D4": bridge_audit(
                patchouli_signals,
                patchouli_labels,
                targets["nC6"],
                ALL,
                4,
            ),
        },
        "samples": sample_audits(targets),
    }

    patchouli_e6 = report["patchouli84"]["E6_at_D3_under_D45_care"]
    patchouli_nc6 = report["patchouli84"]["nC6_at_D4"]
    assert not patchouli_e6["existing_matches"]
    assert not patchouli_e6["one_ordinary_gate_matches"]
    assert not patchouli_e6["one_bit_switch_matches"]
    assert not patchouli_nc6["existing_matches"]
    assert not patchouli_nc6["one_ordinary_gate_matches"]
    assert not patchouli_nc6["one_bit_switch_matches"]
    for sample in report["samples"]:
        for key in ("nC4_at_D3", "E6_at_D3_under_D45_care"):
            audit = sample[key]
            assert not audit["existing_matches"]
            assert not audit["one_ordinary_gate_matches"]
            assert not audit["one_bit_switch_matches"]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "patchouli_E6_D3": "no fixed one-component bridge",
        "patchouli_nC6_D4": "no fixed one-component bridge",
        "samples_checked": len(report["samples"]),
        "output": str(args.output),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
