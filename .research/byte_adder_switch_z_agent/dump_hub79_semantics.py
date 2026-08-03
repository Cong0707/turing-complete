"""为 Hub 79 的每个网络标注区间进位语义和依赖关系。"""

from __future__ import annotations

from collections import defaultdict
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
ENGINE = ROOT / "examples/rng/research/archive/rng_switch_public/analyze_hub79.py"
SOURCE = ROOT / ".research/rng_public_artifacts/hub-79-adder/main/circuit.data"
OUTPUT = Path(__file__).with_name("hub79_semantic_netlist.json")


def load_engine():
    spec = importlib.util.spec_from_file_location("hub79_semantic_engine", ENGINE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {ENGINE}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    module.CIRCUIT_PATH = SOURCE
    return module


def main() -> None:
    engine = load_engine()
    circuit, compiled, networks, outputs = engine.evaluate()
    variables = tuple(engine.variable(index) for index in range(engine.VARIABLES))

    labels: dict[int, list[str]] = defaultdict(list)

    def add(value: int, name: str) -> None:
        labels[value & engine.ALL].append(name)

    for bit in range(8):
        a, b = variables[bit], variables[8 + bit]
        add(a, f"A{bit}")
        add(b, f"B{bit}")
        add(a & b, f"G[{bit}:{bit}]")
        add(a | b, f"H[{bit}:{bit}]")
        add((~(a | b)) & engine.ALL, f"K[{bit}:{bit}]")
        add((~(a & b)) & engine.ALL, f"NG[{bit}:{bit}]")
        add(a ^ b, f"P[{bit}:{bit}]")

    add(variables[16], "Cin/C0")
    carry = variables[16]
    for bit in range(8):
        a, b = variables[bit], variables[8 + bit]
        add((a ^ b) ^ carry, f"S{bit}")
        carry = (a & b) | ((a ^ b) & carry)
        add(carry, f"C{bit + 1}")

    for lo in range(8):
        g = 0
        h = engine.ALL
        for hi in range(lo, 8):
            a, b = variables[hi], variables[8 + hi]
            propagate = a ^ b
            generate = a & b
            g = generate | (propagate & g)
            h = generate | (propagate & h)
            add(g, f"G[{hi}:{lo}]")
            add(h, f"H[{hi}:{lo}]")
            add((~h) & engine.ALL, f"K[{hi}:{lo}]")
            add((~g) & engine.ALL, f"NG[{hi}:{lo}]")
            add(h & ((~g) & engine.ALL), f"P[{hi}:{lo}]")

    def signal_record(network: int) -> dict[str, object]:
        signal = networks[network]
        pins = compiled.network_pins[network]
        return {
            "network": network,
            "depth": signal.depth,
            "labels": labels.get(signal.bits[0], []),
            "support": list(engine.dependency_support(signal.bits[0], variables)),
            "z_cases": ((~signal.driven) & engine.ALL).bit_count(),
            "drivers": [
                {
                    "component": pin.component_index,
                    "kind": circuit.components[pin.component_index].kind,
                    "pin": pin.name,
                }
                for pin in pins
                if pin.direction in {engine.O, engine.T}
            ],
            "sinks": [
                {
                    "component": pin.component_index,
                    "kind": circuit.components[pin.component_index].kind,
                    "pin": pin.name,
                }
                for pin in pins
                if pin.direction == engine.I
            ],
        }

    network_records = [signal_record(network) for network in sorted(networks)]
    component_records = []
    for index, component in enumerate(circuit.components):
        input_records = []
        output_records = []
        for (component_index, pin_name), pin in compiled.pins.items():
            if component_index != index:
                continue
            network = compiled.pin_network.get((index, pin_name))
            item = {
                "pin": pin_name,
                "network": network,
                "labels": labels.get(networks[network].bits[0], [])
                if network in networks
                else [],
            }
            if pin.direction == engine.I:
                input_records.append(item)
            else:
                output_signal = outputs.get((index, pin_name))
                item["output_labels"] = labels.get(output_signal.bits[0], []) if output_signal else []
                output_records.append(item)
        component_records.append(
            {
                "component": index,
                "kind": component.kind,
                "user_label": component.user_label,
                "inputs": input_records,
                "outputs": output_records,
            }
        )

    OUTPUT.write_text(
        json.dumps(
            {
                "schema": "hub79-semantic-netlist-v1",
                "networks": network_records,
                "components": component_records,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    for item in network_records:
        if len(item["drivers"]) >= 2:
            print(
                f"N{item['network']} d={item['depth']} z={item['z_cases']} "
                f"labels={item['labels']} drivers={item['drivers']} sinks={item['sinks']}"
            )


if __name__ == "__main__":
    main()
