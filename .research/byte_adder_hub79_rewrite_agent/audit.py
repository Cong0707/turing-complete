"""冻结 Hub 79 四延迟加法器的可重复静态审计证书。

本脚本只读取仓库内公开电路，不启动游戏，不修改候选或正式存档。
它复用已经归档的位并行 Z/多驱动求值器，并额外输出稳定 JSON 证书。
"""

from __future__ import annotations

from collections import Counter
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
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
ENGINE = (
    ROOT
    / "examples"
    / "rng"
    / "research"
    / "archive"
    / "rng_switch_public"
    / "analyze_hub79.py"
)
OUTPUT = Path(__file__).with_name("certificate.json")


def load_engine():
    spec = importlib.util.spec_from_file_location("hub79_frozen_audit", ENGINE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {ENGINE}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    module.CIRCUIT_PATH = SOURCE
    return module


def support(table: int, variables: tuple[int, ...], all_bits: int) -> list[int]:
    result: list[int] = []
    for index, truth in enumerate(variables):
        shift = 1 << index
        low_mask = (~truth) & all_bits
        if ((table ^ (table >> shift)) & low_mask) != 0:
            result.append(index)
    return result


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
        if component.kind == 81 and component.user_label == "sum"
    )
    cout_component = next(
        index
        for index, component in enumerate(circuit.components)
        if component.kind == 81 and component.user_label == "Cout"
    )
    sum_signal = networks[compiled.pin_network[(sum_component, "out")]]
    cout_signal = networks[compiled.pin_network[(cout_component, "out")]]

    if sum_signal.bits[:8] != tuple(expected_sum):
        raise RuntimeError("sum does not implement A + B + Cin")
    if cout_signal.bits[0] != carry:
        raise RuntimeError("Cout does not implement carry-out")
    conflict_cases = sum(signal.conflict.bit_count() for signal in networks.values())
    if conflict_cases:
        raise RuntimeError(f"found {conflict_cases} packed driver conflicts")

    kind_counts = Counter(component.kind for component in circuit.components)
    reviewed_cost = {
        "bit_switch": kind_counts[12] * 2,
        "and": kind_counts[4],
        "nand": kind_counts[6],
        "or": kind_counts[7],
        "nor": kind_counts[9],
        "not": kind_counts[3],
    }
    if sum(reviewed_cost.values()) != circuit.gate:
        raise RuntimeError("reviewed primitive cost does not equal serialized gate score")

    multi_driver = []
    for network, pins in sorted(compiled.network_pins.items()):
        drivers = [pin for pin in pins if pin.direction in {engine.O, engine.T}]
        if len(drivers) < 2:
            continue
        signal = networks[network]
        multi_driver.append(
            {
                "network": network,
                "driver_count": len(drivers),
                "switch_driver_count": sum(
                    pin.direction == engine.T
                    and circuit.components[pin.component_index].kind == 12
                    for pin in drivers
                ),
                "sink_count": sum(pin.direction == engine.I for pin in pins),
                "depth": signal.depth,
                "z_cases": ((~signal.driven) & engine.ALL).bit_count(),
                "one_cases": signal.bits[0].bit_count(),
                "conflict_cases": signal.conflict.bit_count(),
                "support": support(signal.bits[0], variables, engine.ALL),
            }
        )

    certificate = {
        "schema": "turing-complete-byte-adder-hub79-static-audit-v1",
        "source": str(SOURCE.relative_to(ROOT)).replace("\\", "/"),
        "source_sha256": sha256(SOURCE.read_bytes()).hexdigest(),
        "serialized_score": {
            "gate": circuit.gate,
            "delay": circuit.delay,
            "energy": circuit.energy,
        },
        "component_count": len(circuit.components),
        "wire_count": len(circuit.wires),
        "component_kind_counts": {
            str(kind): count for kind, count in sorted(kind_counts.items())
        },
        "reviewed_gate_cost_breakdown": reviewed_cost,
        "input_schema": {"A": 8, "B": 8, "Cin": 1},
        "vectors_checked": engine.ASSIGNMENTS,
        "truth": {
            "sum_equals_low8_A_plus_B_plus_Cin": True,
            "cout_equals_bit8_A_plus_B_plus_Cin": True,
        },
        "output_depths": {
            "sum_bits": [sum_signal.depth] * 8,
            "cout": cout_signal.depth,
        },
        "packed_conflict_cases": conflict_cases,
        "multi_driver_network_count": len(multi_driver),
        "multi_driver_networks": multi_driver,
        "candidate": None,
        "candidate_reason": "冻结时尚无满足全真值和四延迟约束的严格改进物化网表",
    }
    OUTPUT.write_text(
        json.dumps(certificate, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(certificate, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
