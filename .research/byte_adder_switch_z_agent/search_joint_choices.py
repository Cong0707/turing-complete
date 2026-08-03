"""在 Hub 79 的 18 个 Switch BUS 上搜索保留/布尔替换组合。

与独立门数相加不同，本脚本从 Sum/Cout 反向遍历，只统计仍可达的原始普通门、
Switch 和新表达式门，并按替换后的真实输入到达时间重算关键路径。
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
import importlib.util
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[2]
ENGINE = ROOT / "examples/rng/research/archive/rng_switch_public/analyze_hub79.py"
SOURCE = ROOT / ".research/rng_public_artifacts/hub-79-adder/main/circuit.data"
ALTERNATIVES = Path(__file__).with_name("bus_alternatives.json")
OUTPUT = Path(__file__).with_name("joint_choice_frontier.json")

LOGIC_KINDS = {3, 4, 6, 7, 9}
ZERO_KINDS = {2, 16, 17, 79, 109, 111}


def load_engine():
    spec = importlib.util.spec_from_file_location("byte_adder_joint_engine", ENGINE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {ENGINE}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    module.CIRCUIT_PATH = SOURCE
    return module


def label(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        match = re.fullmatch(r"c(\d+)_(enable|in)", node.id)
        if match:
            return f"c{match.group(1)}.{match.group(2)}"
    raise ValueError(f"unsupported expression leaf: {ast.dump(node)}")


def expression_gate_count(node: ast.AST) -> int:
    if isinstance(node, ast.Expression):
        return expression_gate_count(node.body)
    if isinstance(node, ast.Call):
        return 1 + sum(expression_gate_count(argument) for argument in node.args)
    label(node)
    return 0


@dataclass
class Evaluation:
    depth: int
    original_logic: set[int]
    switch_buses: set[int]
    boolean_buses: set[int]

    @property
    def gate(self) -> int:
        return len(self.original_logic)


class Netlist:
    def __init__(self, depth_limit: int, boolean_mask: int) -> None:
        self.engine = load_engine()
        self.circuit, self.compiled = self.engine.compile_circuit()
        self.depth_limit = depth_limit
        self.boolean_mask = boolean_mask
        document = json.loads(ALTERNATIVES.read_text(encoding="utf-8"))
        self.bus_records = {int(item["network"]): item for item in document["results"]}
        self.expressions: dict[int, ast.Expression | None] = {}
        for network, item in self.bus_records.items():
            replacement = item["boolean_alternatives"][str(depth_limit)]
            self.expressions[network] = (
                ast.parse(
                    re.sub(
                        r"c(\d+)\.(enable|in)",
                        lambda match: f"c{match.group(1)}_{match.group(2)}",
                        replacement["expression"],
                    ),
                    mode="eval",
                )
                if replacement is not None
                else None
            )
        self.bus_order = sorted(
            network for network, expression in self.expressions.items() if expression is not None
        )
        self.bus_index = {network: index for index, network in enumerate(self.bus_order)}
        self.drivers: dict[int, list[object]] = {}
        for network, pins in self.compiled.network_pins.items():
            self.drivers[network] = [
                pin for pin in pins if pin.direction in {self.engine.O, self.engine.T}
            ]
        self.memo: dict[tuple[int, int], Evaluation] = {}

    def is_boolean(self, network: int) -> bool:
        index = self.bus_index.get(network)
        if index is None:
            return False
        return bool((self.boolean_mask >> index) & 1) and self.expressions[network] is not None

    def input_ref(self, component_index: int, pin_name: str, bit: int = 0) -> tuple[int, int] | None:
        network = self.compiled.pin_network.get((component_index, pin_name))
        return None if network is None else (network, bit)

    @staticmethod
    def merge(depth: int, *items: Evaluation) -> Evaluation:
        original_logic: set[int] = set()
        switch_buses: set[int] = set()
        boolean_buses: set[int] = set()
        for item in items:
            original_logic.update(item.original_logic)
            switch_buses.update(item.switch_buses)
            boolean_buses.update(item.boolean_buses)
        return Evaluation(depth, original_logic, switch_buses, boolean_buses)

    @staticmethod
    def zero() -> Evaluation:
        return Evaluation(0, set(), set(), set())

    def expression_eval(self, network: int, node: ast.AST) -> Evaluation:
        if isinstance(node, ast.Expression):
            return self.expression_eval(network, node.body)
        if isinstance(node, ast.Call):
            children = [self.expression_eval(network, argument) for argument in node.args]
            return self.merge(max((child.depth for child in children), default=0) + 1, *children)
        item = label(node)
        component_text, pin_name = item.split(".", 1)
        component_index = int(component_text[1:])
        ref = self.input_ref(component_index, pin_name)
        return self.zero() if ref is None else self.network_eval(*ref)

    def component_eval(self, component_index: int, output_name: str, bit: int) -> Evaluation:
        component = self.circuit.components[component_index]
        kind = component.kind
        if kind in {2, 79}:
            return self.zero()
        if kind in LOGIC_KINDS:
            input_names = ("in",) if kind == 3 else ("in0", "in1")
            children = []
            for name in input_names:
                ref = self.input_ref(component_index, name)
                children.append(self.zero() if ref is None else self.network_eval(*ref))
            result = self.merge(max(child.depth for child in children) + 1, *children)
            result.original_logic.add(component_index)
            return result
        if kind == 16:
            ref = self.input_ref(component_index, f"in{bit}")
            return self.zero() if ref is None else self.network_eval(*ref)
        if kind == 17:
            ref = self.input_ref(component_index, "in", int(output_name[3:]))
            return self.zero() if ref is None else self.network_eval(*ref)
        if kind == 109:
            ref = self.input_ref(component_index, "in", int(output_name[3:]))
            return self.zero() if ref is None else self.network_eval(*ref)
        if kind == 111:
            ref = self.input_ref(component_index, f"in{bit}")
            return self.zero() if ref is None else self.network_eval(*ref)
        raise RuntimeError(f"unsupported component kind {kind} at {component_index}")

    def network_eval(self, network: int, bit: int = 0) -> Evaluation:
        key = (network, bit)
        known = self.memo.get(key)
        if known is not None:
            return Evaluation(
                known.depth,
                set(known.original_logic),
                set(known.switch_buses),
                set(known.boolean_buses),
            )
        drivers = self.drivers.get(network, [])
        if not drivers:
            result = self.zero()
        elif network in self.bus_records:
            if self.is_boolean(network):
                expression = self.expressions[network]
                assert expression is not None
                result = self.expression_eval(network, expression)
                result.boolean_buses.add(network)
            else:
                children: list[Evaluation] = []
                for driver in drivers:
                    component_index = driver.component_index
                    for pin_name in ("enable", "in"):
                        ref = self.input_ref(component_index, pin_name)
                        children.append(self.zero() if ref is None else self.network_eval(*ref))
                result = self.merge(max(child.depth for child in children) + 1, *children)
                result.switch_buses.add(network)
        elif len(drivers) == 1:
            driver = drivers[0]
            result = self.component_eval(driver.component_index, driver.name, bit)
        else:
            raise RuntimeError(f"unexpected non-Switch multi-driver network {network}")
        self.memo[key] = Evaluation(
            result.depth,
            set(result.original_logic),
            set(result.switch_buses),
            set(result.boolean_buses),
        )
        return result

    def outputs(self) -> Evaluation:
        roots: list[Evaluation] = []
        for index, component in enumerate(self.circuit.components):
            if component.kind != 81:
                continue
            network = self.compiled.pin_network[(index, "out")]
            width = 8 if component.user_label == "sum" else 1
            roots.extend(self.network_eval(network, bit) for bit in range(width))
        return self.merge(max(root.depth for root in roots), *roots)

    def score(self) -> dict[str, object]:
        result = self.outputs()
        switch_gate = sum(
            int(self.bus_records[network]["switch_gate"])
            for network in result.switch_buses
        )
        boolean_gate = sum(
            expression_gate_count(self.expressions[network])
            for network in result.boolean_buses
            if self.expressions[network] is not None
        )
        gate = len(result.original_logic) + switch_gate + boolean_gate
        return {
            "gate": gate,
            "delay": result.depth,
            "energy": gate * result.depth,
            "original_logic_gate": len(result.original_logic),
            "switch_gate": switch_gate,
            "boolean_gate": boolean_gate,
            "live_original_logic": sorted(result.original_logic),
            "switch_buses": sorted(result.switch_buses),
            "boolean_buses": sorted(result.boolean_buses),
        }


def search(depth_limit: int) -> dict[str, object]:
    netlist = Netlist(depth_limit, 0)
    count = len(netlist.bus_order)
    best: dict[tuple[int, int], dict[str, object]] = {}
    feasible = 0
    for mask in range(1 << count):
        netlist.boolean_mask = mask
        netlist.memo.clear()
        score = netlist.score()
        if int(score["delay"]) <= depth_limit:
            feasible += 1
            key = (int(score["gate"]), int(score["delay"]))
            if key not in best:
                best[key] = {"mask": mask, "bus_order": netlist.bus_order, **score}
    records = sorted(best.values(), key=lambda item: (item["energy"], item["gate"], item["delay"]))
    pareto = [
        item
        for item in records
        if not any(
            other["gate"] <= item["gate"]
            and other["delay"] <= item["delay"]
            and (other["gate"], other["delay"]) != (item["gate"], item["delay"])
            for other in records
        )
    ]
    return {
        "depth_limit": depth_limit,
        "masks_checked": 1 << count,
        "feasible_masks": feasible,
        "best": records[:20],
        "pareto": pareto,
    }


def main() -> None:
    original = Netlist(7, 0).score()
    if original["gate"] != 154 or original["delay"] != 4:
        raise RuntimeError(f"backward model does not reproduce 154/4: {original}")
    results = [search(depth_limit) for depth_limit in (4,)]
    document = {
        "schema": "byte-adder-hub79-joint-choice-frontier-v1",
        "original": original,
        "results": results,
    }
    OUTPUT.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                str(item["depth_limit"]): item["best"][:3]
                for item in results
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
