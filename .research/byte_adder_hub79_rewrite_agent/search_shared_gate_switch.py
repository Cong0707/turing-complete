"""搜索“一只普通门换掉一只或多只 Switch”的四延迟联合改写。

对每个 Switch BUS，原有可用信号是到达深度严格小于 BUS 深度的所有标量网络。
脚本枚举由这些信号通过一只 AND/OR/NAND/NOR/NOT 新生成的中间量 ``g``，再把
``g`` 加入 Switch 因子池。若 BUS 能从 k 只 Switch 降到 k-1 只，则单 BUS 已净省
一门；同一个 g 若服务多个 BUS，节省更多。所有判断在完整 2^17 真值位集上进行，
并要求每个候选 Switch 在 enable 有效时 data 与目标完全一致，故不会产生 0/1
多驱动冲突。
"""

from __future__ import annotations

from dataclasses import dataclass
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
ENGINE = ROOT / "examples/rng/research/archive/rng_switch_public/analyze_hub79.py"
SOURCE = ROOT / "examples/rng/research/archive/rng_public_artifacts/hub-79-adder/main/circuit.data"
OUTPUT = Path(__file__).with_name("shared_gate_switch_certificate.json")


@dataclass(frozen=True)
class Signal:
    truth: int
    depth: int
    label: str


def load_engine():
    spec = importlib.util.spec_from_file_location("hub79_shared_gate_engine", ENGINE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {ENGINE}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    module.CIRCUIT_PATH = SOURCE
    return module


def valid_coverage(enable: int, data: int, target: int) -> int | None:
    if enable & (data ^ target):
        return None
    coverage = enable & data
    return coverage if coverage else None


def maximal_coverages(signals: list[Signal], target: int) -> list[tuple[int, str, str]]:
    records: dict[int, tuple[int, str, str]] = {}
    for enable in signals:
        for data in signals:
            coverage = valid_coverage(enable.truth, data.truth, target)
            if coverage is None:
                continue
            old = records.get(coverage)
            candidate = (coverage, enable.label, data.label)
            if old is None or candidate[1:] < old[1:]:
                records[coverage] = candidate
    ordered = sorted(records.values(), key=lambda item: item[0].bit_count(), reverse=True)
    maximal: list[tuple[int, str, str]] = []
    for item in ordered:
        if any(item[0] & ~known[0] == 0 for known in maximal):
            continue
        maximal.append(item)
    return maximal


def old_needs(target: int, coverages: list[tuple[int, str, str]], old_switches: int) -> list[tuple[int, list[tuple[int, str, str]]]]:
    """Regions one new Switch must cover alongside at most k-2 old switches."""

    limit = max(0, old_switches - 2)
    choices: list[tuple[int, list[tuple[int, str, str]]]] = [(target, [])]
    if limit >= 1:
        choices.extend((target & ~item[0], [item]) for item in coverages)
    if limit >= 2:
        choices.extend(
            (target & ~(left[0] | right[0]), [left, right])
            for index, left in enumerate(coverages)
            for right in coverages[index:]
        )
    return choices


def main() -> None:
    engine = load_engine()
    circuit, compiled, networks, _outputs = engine.evaluate()

    global_signals: dict[int, Signal] = {}
    for network, value in networks.items():
        if len(value.bits) != 1:
            continue
        candidate = Signal(value.bits[0], value.depth, f"n{network}")
        old = global_signals.get(candidate.truth)
        if old is None or (candidate.depth, candidate.label) < (old.depth, old.label):
            global_signals[candidate.truth] = candidate
    for truth, label in ((0, "ZERO"), (engine.ALL, "ONE")):
        old = global_signals.get(truth)
        candidate = Signal(truth, 0, label)
        if old is None or candidate.depth < old.depth:
            global_signals[truth] = candidate

    bus_results = []
    shared_hits: dict[int, dict[str, object]] = {}
    for network, pins in sorted(compiled.network_pins.items()):
        switches = [
            pin.component_index
            for pin in pins
            if pin.direction == engine.T
            and circuit.components[pin.component_index].kind == 12
        ]
        if not switches:
            continue
        bus_depth = networks[network].depth
        target = networks[network].bits[0]
        available = [signal for signal in global_signals.values() if signal.depth < bus_depth]
        existing_truths = {signal.truth: signal.depth for signal in available}
        old_cover = maximal_coverages(available, target)
        needs = old_needs(target, old_cover, len(switches))

        gate_inputs = [signal for signal in available if signal.depth + 1 < bus_depth]
        generated: dict[int, tuple[int, str]] = {}
        for signal in gate_inputs:
            truth = (~signal.truth) & engine.ALL
            depth = signal.depth + 1
            if existing_truths.get(truth, 10**9) <= depth:
                continue
            generated.setdefault(truth, (depth, f"NOT({signal.label})"))
        operations = (
            ("AND", lambda left, right: left & right),
            ("OR", lambda left, right: left | right),
            ("NAND", lambda left, right: ~(left & right) & engine.ALL),
            ("NOR", lambda left, right: ~(left | right) & engine.ALL),
        )
        for left_index, left in enumerate(gate_inputs):
            for right in gate_inputs[left_index:]:
                depth = max(left.depth, right.depth) + 1
                if depth >= bus_depth:
                    continue
                for name, operation in operations:
                    truth = operation(left.truth, right.truth)
                    if existing_truths.get(truth, 10**9) <= depth:
                        continue
                    candidate = (depth, f"{name}({left.label},{right.label})")
                    old = generated.get(truth)
                    if old is None or candidate < old:
                        generated[truth] = candidate

        hits = []
        for gate_truth, (gate_depth, expression) in generated.items():
            gate = Signal(gate_truth, gate_depth, "g")
            new_terms: dict[int, tuple[str, str]] = {}
            for other in available + [gate]:
                for enable, data in ((gate, other), (other, gate)):
                    coverage = valid_coverage(enable.truth, data.truth, target)
                    if coverage is None:
                        continue
                    new_terms.setdefault(coverage, (enable.label, data.label))
            chosen = None
            for coverage, orientation in new_terms.items():
                for need, retained in needs:
                    if need & ~coverage == 0:
                        chosen = (coverage, orientation, retained)
                        break
                if chosen is not None:
                    break
            if chosen is None:
                continue
            coverage, orientation, retained = chosen
            record = {
                "gate_truth_sha256": __import__("hashlib").sha256(
                    gate_truth.to_bytes(engine.ASSIGNMENTS // 8, "little")
                ).hexdigest(),
                "gate_depth": gate_depth,
                "gate_expression": expression,
                "new_switch": {"enable": orientation[0], "data": orientation[1]},
                "retained_old_terms": [
                    {"enable": item[1], "data": item[2]} for item in retained
                ],
                "new_switch_count": 1 + len(retained),
                "old_switch_count": len(switches),
                "net_gate_saving": 2 * (len(switches) - 1 - len(retained)) - 1,
                "coverage_cases": coverage.bit_count(),
            }
            hits.append(record)
            shared = shared_hits.setdefault(
                gate_truth,
                {
                    "gate_depth": gate_depth,
                    "gate_expression": expression,
                    "networks": [],
                },
            )
            shared["networks"].append(network)

        hits.sort(
            key=lambda item: (
                -int(item["net_gate_saving"]),
                int(item["gate_depth"]),
                str(item["gate_expression"]),
            )
        )
        bus_results.append(
            {
                "network": network,
                "depth": bus_depth,
                "old_switch_count": len(switches),
                "available_signal_count": len(available),
                "generated_one_gate_signal_count": len(generated),
                "improvement_count": len(hits),
                "best_improvements": hits[:20],
            }
        )

    shared_records = [
        {
            "gate_truth_sha256": __import__("hashlib").sha256(
                truth.to_bytes(engine.ASSIGNMENTS // 8, "little")
            ).hexdigest(),
            **record,
            "network_count": len(record["networks"]),
        }
        for truth, record in shared_hits.items()
        if len(record["networks"]) > 1
    ]
    certificate = {
        "schema": "hub79-shared-one-gate-switch-reduction-v1",
        "vectors": engine.ASSIGNMENTS,
        "bus_count": len(bus_results),
        "buses_with_improvement": sum(item["improvement_count"] > 0 for item in bus_results),
        "shared_improvement_count": len(shared_records),
        "results": bus_results,
        "shared_improvements": shared_records,
    }
    OUTPUT.write_text(json.dumps(certificate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(certificate, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
