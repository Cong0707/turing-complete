"""Export the public Hub 79 adder as a semantic, timing-aware netlist.

The exporter is read-only.  It reuses the exhaustive packed evaluator, labels
recognisable adder interval signals, and records both the value plane and the
driven plane of every Switch bus.  The result is intended for global rewrites;
local Boolean equality alone is insufficient when downstream logic observes Z.
"""

from __future__ import annotations

from collections import defaultdict
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
ENGINE_PATH = (
    ROOT
    / "examples"
    / "rng"
    / "research"
    / "archive"
    / "rng_switch_public"
    / "analyze_hub79.py"
)
SOURCE = (
    ROOT
    / "examples"
    / "rng"
    / "research"
    / "archive"
    / "rng_public_artifacts"
    / "hub-79-adder"
    / "main"
    / "circuit.data"
)
OUTPUT = Path(__file__).with_name("hub79_semantic_netlist.json")

KIND_NAMES = {
    2: "ON",
    3: "NOT",
    4: "AND",
    6: "NAND",
    7: "OR",
    9: "NOR",
    12: "SWITCH",
    16: "MAKER8",
    17: "SPLITTER8",
    79: "INPUT",
    81: "OUTPUT",
    109: "SPLITTER2",
    111: "MAKER2",
}


def load_engine():
    spec = importlib.util.spec_from_file_location("byte_adder_root_hub79", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load evaluator: {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    module.CIRCUIT_PATH = SOURCE
    return module


def add_label(labels: dict[int, set[str]], truth: int, name: str, all_bits: int) -> None:
    labels[truth & all_bits].add(name)


def semantic_labels(engine) -> dict[int, set[str]]:
    variables = tuple(engine.variable(index) for index in range(engine.VARIABLES))
    a = variables[:8]
    b = variables[8:16]
    cin = variables[16]
    labels: dict[int, set[str]] = defaultdict(set)
    add_label(labels, 0, "0", engine.ALL)
    add_label(labels, engine.ALL, "1", engine.ALL)
    add_label(labels, cin, "Cin", engine.ALL)
    add_label(labels, ~cin, "~Cin", engine.ALL)

    propagate = []
    generate = []
    kill = []
    for bit, (left, right) in enumerate(zip(a, b)):
        add_label(labels, left, f"A{bit}", engine.ALL)
        add_label(labels, right, f"B{bit}", engine.ALL)
        propagate.append(left ^ right)
        generate.append(left & right)
        kill.append((~(left | right)) & engine.ALL)
        add_label(labels, propagate[-1], f"P{bit}", engine.ALL)
        add_label(labels, generate[-1], f"G{bit}", engine.ALL)
        add_label(labels, kill[-1], f"K{bit}", engine.ALL)

    carry = cin
    add_label(labels, carry, "C0", engine.ALL)
    for bit in range(8):
        add_label(labels, propagate[bit] ^ carry, f"S{bit}", engine.ALL)
        carry = generate[bit] | (propagate[bit] & carry)
        add_label(labels, carry, f"C{bit + 1}", engine.ALL)
        add_label(labels, ~carry, f"~C{bit + 1}", engine.ALL)

    for low in range(8):
        interval_p = engine.ALL
        interval_g = 0
        interval_k = engine.ALL
        for high in range(low, 8):
            interval_g = generate[high] | (propagate[high] & interval_g)
            interval_k = kill[high] | (propagate[high] & interval_k)
            interval_p &= propagate[high]
            suffix = f"[{high}:{low}]"
            add_label(labels, interval_g, f"G{suffix}", engine.ALL)
            add_label(labels, interval_k, f"K{suffix}", engine.ALL)
            add_label(labels, interval_p, f"P{suffix}", engine.ALL)
            add_label(labels, ~interval_g, f"~G{suffix}", engine.ALL)
            add_label(labels, ~interval_k, f"~K{suffix}", engine.ALL)
            add_label(labels, ~interval_p, f"~P{suffix}", engine.ALL)
    return labels


def short_hash(value: int) -> str:
    byte_count = max(1, (value.bit_length() + 7) // 8)
    import hashlib

    return hashlib.sha256(value.to_bytes(byte_count, "little")).hexdigest()[:16]


def signal_record(signal, labels: dict[int, set[str]], all_bits: int) -> dict[str, object]:
    return {
        "width": len(signal.bits),
        "depth": signal.depth,
        "driven_cases": signal.driven.bit_count(),
        "driven_labels": sorted(labels.get(signal.driven & all_bits, ())),
        "z_cases": ((~signal.driven) & all_bits).bit_count(),
        "z_labels": sorted(labels.get((~signal.driven) & all_bits, ())),
        "conflict_cases": signal.conflict.bit_count(),
        "bits": [
            {
                "labels": sorted(labels.get(value & all_bits, ())),
                "ones": (value & all_bits).bit_count(),
                "truth_sha256_16": short_hash(value & all_bits),
            }
            for value in signal.bits
        ],
        "driven_sha256_16": short_hash(signal.driven & all_bits),
    }


def main() -> None:
    engine = load_engine()
    circuit, compiled, networks, outputs = engine.evaluate()
    labels = semantic_labels(engine)

    network_records = []
    for network, signal in sorted(networks.items()):
        pins = compiled.network_pins.get(network, ())
        drivers = [pin for pin in pins if pin.direction in {engine.O, engine.T}]
        sinks = [pin for pin in pins if pin.direction == engine.I]
        network_records.append(
            {
                "network": network,
                "signal": signal_record(signal, labels, engine.ALL),
                "drivers": [
                    {
                        "component": pin.component_index,
                        "kind": KIND_NAMES.get(circuit.components[pin.component_index].kind),
                        "pin": pin.name,
                        "tristate": pin.direction == engine.T,
                    }
                    for pin in drivers
                ],
                "sinks": [
                    {
                        "component": pin.component_index,
                        "kind": KIND_NAMES.get(circuit.components[pin.component_index].kind),
                        "pin": pin.name,
                    }
                    for pin in sinks
                ],
            }
        )

    component_records = []
    for index, component in enumerate(circuit.components):
        input_networks = {}
        output_networks = {}
        for (component_index, pin_name), pin in compiled.pins.items():
            if component_index != index:
                continue
            network = compiled.pin_network.get((index, pin_name))
            target = input_networks if pin.direction == engine.I else output_networks
            target[pin_name] = network
        component_records.append(
            {
                "index": index,
                "kind": component.kind,
                "operation": KIND_NAMES.get(component.kind, f"KIND_{component.kind}"),
                "label": component.user_label,
                "inputs": input_networks,
                "outputs": output_networks,
                "output_signals": {
                    pin_name: signal_record(signal, labels, engine.ALL)
                    for (component_index, pin_name), signal in outputs.items()
                    if component_index == index
                },
            }
        )

    document = {
        "schema": "byte-adder-hub79-semantic-netlist-v1",
        "source": str(SOURCE.relative_to(ROOT)).replace("\\", "/"),
        "vectors": engine.ASSIGNMENTS,
        "serialized_score": {
            "gate": circuit.gate,
            "delay": circuit.delay,
            "energy": circuit.energy,
        },
        "components": component_records,
        "networks": network_records,
    }
    OUTPUT.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "components": len(component_records),
                "networks": len(network_records),
                "multi_driver_networks": sum(
                    len(record["drivers"]) > 1 for record in network_records
                ),
                "output": str(OUTPUT),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
