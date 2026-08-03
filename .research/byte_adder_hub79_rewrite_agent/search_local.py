"""对 Hub 79 的每个 Switch 汇合网络做精确局部布尔重综合。

每个网络的候选输入只取原 Switch 的 enable/data 数值平面。先把 131072
个原始输入压缩成这些局部信号的可达联合赋值，再枚举 AND/OR/NAND/NOR/NOT
表达式树。深度使用原电路中每个输入信号的真实到达深度，候选不得超过原网络
深度，门数必须严格少于被替换 Switch 的 2*k 门。
"""

from __future__ import annotations

from dataclasses import dataclass
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
SOURCE = (
    ROOT / "examples/rng/research/archive/rng_public_artifacts/hub-79-adder/main/circuit.data"
)
ENGINE = ROOT / "examples/rng/research/archive/rng_switch_public/analyze_hub79.py"
OUTPUT = Path(__file__).with_name("local_synthesis_certificate.json")


@dataclass(frozen=True)
class State:
    truth: int
    depth: int
    expression: str


def load_engine():
    spec = importlib.util.spec_from_file_location("hub79_local_engine", ENGINE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {ENGINE}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    module.CIRCUIT_PATH = SOURCE
    return module


def project(tables: list[int], target: int, assignments: int) -> tuple[list[int], int, int]:
    """Project packed raw truth tables onto reachable local input patterns."""

    pattern_target: dict[int, int] = {}
    for raw in range(assignments):
        pattern = sum(((table >> raw) & 1) << index for index, table in enumerate(tables))
        value = (target >> raw) & 1
        previous = pattern_target.setdefault(pattern, value)
        if previous != value:
            raise RuntimeError("target is not a function of the selected local inputs")
    possible = sum(1 << pattern for pattern in pattern_target)
    projected_target = sum(value << pattern for pattern, value in pattern_target.items())
    projected_inputs = []
    for index in range(len(tables)):
        projected_inputs.append(
            sum(((pattern >> index) & 1) << pattern for pattern in pattern_target)
        )
    return projected_inputs, projected_target, possible


def dominates(frontier: dict[tuple[int, int], tuple[int, str]], truth: int, depth: int, cost: int) -> bool:
    return any(
        known_truth == truth and known_depth <= depth and known_cost <= cost
        for (known_truth, known_depth), (known_cost, _expr) in frontier.items()
    )


def synthesize(
    inputs: list[tuple[str, int, int]],
    target: int,
    possible: int,
    max_depth: int,
    max_cost: int,
) -> dict[str, object] | None:
    layers: list[list[State]] = [[] for _ in range(max_cost + 1)]
    frontier: dict[tuple[int, int], tuple[int, str]] = {}
    for name, truth, depth in inputs:
        key = (truth & possible, depth)
        if key not in frontier:
            frontier[key] = (0, name)
            layers[0].append(State(key[0], depth, name))

    target &= possible
    direct = [state for state in layers[0] if state.truth == target]
    if direct:
        best = min(direct, key=lambda state: state.depth)
        return {"cost": 0, "depth": best.depth, "expression": best.expression}

    operations = (
        ("AND", lambda left, right: left & right),
        ("OR", lambda left, right: left | right),
        ("NAND", lambda left, right: ~(left & right)),
        ("NOR", lambda left, right: ~(left | right)),
    )
    for cost in range(1, max_cost + 1):
        candidates: dict[tuple[int, int], str] = {}

        for child in layers[cost - 1]:
            depth = child.depth + 1
            if depth <= max_depth:
                truth = (~child.truth) & possible
                if not dominates(frontier, truth, depth, cost):
                    candidates.setdefault((truth, depth), f"NOT({child.expression})")

        for left_cost in range(cost):
            right_cost = cost - 1 - left_cost
            if left_cost > right_cost:
                continue
            left_layer = layers[left_cost]
            right_layer = layers[right_cost]
            for left_index, left in enumerate(left_layer):
                start = left_index if left_cost == right_cost else 0
                for right in right_layer[start:]:
                    depth = max(left.depth, right.depth) + 1
                    if depth > max_depth:
                        continue
                    for name, operation in operations:
                        truth = operation(left.truth, right.truth) & possible
                        if dominates(frontier, truth, depth, cost):
                            continue
                        candidates.setdefault(
                            (truth, depth),
                            f"{name}({left.expression},{right.expression})",
                        )

        # Remove same-cost states dominated by a shallower state of equal truth.
        by_truth: dict[int, tuple[int, str]] = {}
        for (truth, depth), expression in candidates.items():
            old = by_truth.get(truth)
            if old is None or depth < old[0]:
                by_truth[truth] = (depth, expression)
        for truth, (depth, expression) in by_truth.items():
            frontier[(truth, depth)] = (cost, expression)
            layers[cost].append(State(truth, depth, expression))

        hits = [state for state in layers[cost] if state.truth == target]
        if hits:
            best = min(hits, key=lambda state: state.depth)
            return {"cost": cost, "depth": best.depth, "expression": best.expression}
    return None


def main() -> None:
    engine = load_engine()
    circuit, compiled, networks, _outputs = engine.evaluate()
    results = []
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
        factor_records = []
        for component_index in switches:
            item = {"component_index": component_index}
            for pin_name in ("enable", "in"):
                signal = networks[compiled.pin_network[(component_index, pin_name)]]
                truth = signal.bits[0]
                label, old_depth = unique.setdefault(
                    truth, (f"c{component_index}.{pin_name}", signal.depth)
                )
                if signal.depth < old_depth:
                    unique[truth] = (label, signal.depth)
                item[pin_name] = {"label": label, "depth": signal.depth}
            factor_records.append(item)

        raw_tables = list(unique)
        projected, target, possible = project(
            raw_tables,
            networks[network].bits[0],
            engine.ASSIGNMENTS,
        )
        local_inputs = [
            (unique[truth][0], projected[index], unique[truth][1])
            for index, truth in enumerate(raw_tables)
        ]
        original_cost = 2 * len(switches)
        solution = synthesize(
            local_inputs,
            target,
            possible,
            networks[network].depth,
            original_cost - 1,
        )
        results.append(
            {
                "network": network,
                "switch_components": switches,
                "switch_cost": original_cost,
                "original_depth": networks[network].depth,
                "local_input_count": len(local_inputs),
                "reachable_local_patterns": possible.bit_count(),
                "factors": factor_records,
                "strict_improvement": solution,
            }
        )

    improvements = [item for item in results if item["strict_improvement"] is not None]
    certificate = {
        "schema": "hub79-local-switch-network-synthesis-v1",
        "primitive_library": {
            "AND": {"gate": 1, "delay": 1},
            "OR": {"gate": 1, "delay": 1},
            "NAND": {"gate": 1, "delay": 1},
            "NOR": {"gate": 1, "delay": 1},
            "NOT": {"gate": 1, "delay": 1},
        },
        "raw_vectors": engine.ASSIGNMENTS,
        "network_count": len(results),
        "improvement_count": len(improvements),
        "results": results,
    }
    OUTPUT.write_text(json.dumps(certificate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(certificate, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
