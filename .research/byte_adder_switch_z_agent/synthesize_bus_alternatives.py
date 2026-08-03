"""枚举 Hub 79 各 Switch BUS 的低成本布尔替代表达式。

脚本只读取归档公开电路。每个 BUS 的候选输入限定为原 Switch 的 enable/data
数值平面，并对实际可达的局部赋值做精确真值综合。它不启动游戏、不写候选或
正式存档。
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
ENGINE = ROOT / "examples/rng/research/archive/rng_switch_public/analyze_hub79.py"
LOCAL_SEARCH = ROOT / ".research/byte_adder_hub79_rewrite_agent/search_local.py"
SOURCE = ROOT / ".research/rng_public_artifacts/hub-79-adder/main/circuit.data"
OUTPUT = Path(__file__).with_name("bus_alternatives.json")


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main() -> None:
    engine = load_module("byte_adder_switch_engine", ENGINE)
    engine.CIRCUIT_PATH = SOURCE
    local = load_module("byte_adder_local_synth", LOCAL_SEARCH)
    circuit, compiled, networks, _outputs = engine.evaluate()

    results: list[dict[str, object]] = []
    for network, pins in sorted(compiled.network_pins.items()):
        switches = [
            pin.component_index
            for pin in pins
            if pin.direction == engine.T
            and circuit.components[pin.component_index].kind == 12
        ]
        if not switches:
            continue

        unique: dict[int, tuple[str, int]] = {}
        factors: list[dict[str, object]] = []
        data_tables: set[int] = set()
        for component_index in switches:
            factor: dict[str, object] = {"component_index": component_index}
            for pin_name in ("enable", "in"):
                signal = networks[compiled.pin_network[(component_index, pin_name)]]
                truth = signal.bits[0]
                label, known_depth = unique.setdefault(
                    truth, (f"c{component_index}.{pin_name}", signal.depth)
                )
                if signal.depth < known_depth:
                    unique[truth] = (label, signal.depth)
                factor[pin_name] = {
                    "label": unique[truth][0],
                    "depth": signal.depth,
                    "ones": truth.bit_count(),
                }
                if pin_name == "in":
                    data_tables.add(truth)
            factors.append(factor)

        raw_tables = list(unique)
        projected, target, possible = local.project(
            raw_tables,
            networks[network].bits[0],
            engine.ASSIGNMENTS,
        )
        inputs = [
            (unique[truth][0], projected[index], unique[truth][1])
            for index, truth in enumerate(raw_tables)
        ]
        alternatives: dict[str, object] = {}
        for depth_limit in range(4, 8):
            alternatives[str(depth_limit)] = local.synthesize(
                inputs,
                target,
                possible,
                depth_limit,
                max(12, 2 * len(switches)),
            )

        results.append(
            {
                "network": network,
                "switch_components": switches,
                "switch_count": len(switches),
                "switch_gate": 2 * len(switches),
                "switch_depth": networks[network].depth,
                "sink_count": sum(pin.direction == engine.I for pin in pins),
                "z_cases": ((~networks[network].driven) & engine.ALL).bit_count(),
                "distinct_data_count": len(data_tables),
                "reachable_local_patterns": possible.bit_count(),
                "factors": factors,
                "boolean_alternatives": alternatives,
            }
        )

    totals: dict[str, object] = {}
    ordinary_gate_baseline = circuit.gate - 2 * sum(
        int(item["switch_count"]) for item in results
    )
    for depth_limit in range(4, 8):
        chosen_gate = 0
        choices: list[dict[str, object]] = []
        feasible = True
        for item in results:
            original = {
                "mode": "switch",
                "gate": item["switch_gate"],
                "depth": item["switch_depth"],
                "expression": None,
            }
            replacement = item["boolean_alternatives"][str(depth_limit)]
            candidates = [original]
            if replacement is not None:
                candidates.append(
                    {
                        "mode": "boolean",
                        "gate": replacement["cost"],
                        "depth": replacement["depth"],
                        "expression": replacement["expression"],
                    }
                )
            valid = [candidate for candidate in candidates if candidate["depth"] <= depth_limit]
            if not valid:
                feasible = False
                break
            selected = min(valid, key=lambda candidate: (candidate["gate"], candidate["depth"]))
            chosen_gate += int(selected["gate"])
            choices.append({"network": item["network"], **selected})
        totals[str(depth_limit)] = {
            "feasible_under_frozen_input_arrivals": feasible,
            "ordinary_gate_baseline": ordinary_gate_baseline,
            "bus_gate": chosen_gate if feasible else None,
            "total_gate_before_global_pruning": ordinary_gate_baseline + chosen_gate
            if feasible
            else None,
            "choices": choices,
        }

    document = {
        "schema": "byte-adder-hub79-bus-alternatives-v1",
        "source": str(SOURCE.relative_to(ROOT)).replace("\\", "/"),
        "vectors": engine.ASSIGNMENTS,
        "serialized_gate": circuit.gate,
        "serialized_delay": circuit.delay,
        "ordinary_gate_baseline": ordinary_gate_baseline,
        "switch_bus_count": len(results),
        "results": results,
        "independent_totals": totals,
        "warning": (
            "Totals freeze original input arrivals and retain all original ordinary gates; "
            "they are a screening bound, not a materialized joint netlist."
        ),
    }
    OUTPUT.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(totals, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
