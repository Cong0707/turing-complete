"""搜索 Hub79 高三位共同需要的早到达 carry-zero 相位。

目标是用最多两只普通门、在 depth<=3 产生 ``~C5``。若成功，S5/S6/S7
可把两条 carry=0 Switch 合并成一条，三条总线共享该相位。脚本只读公开电路。
"""

from __future__ import annotations

from dataclasses import dataclass
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
ENGINE = ROOT / "examples/rng/research/archive/rng_switch_public/analyze_hub79.py"
SOURCE = ROOT / ".research/rng_public_artifacts/hub-79-adder/main/circuit.data"
OUTPUT = Path(__file__).with_name("shared_phase_frontier.json")


@dataclass(frozen=True)
class Signal:
    truth: int
    depth: int
    expression: str


def load_engine():
    spec = importlib.util.spec_from_file_location("depth4_phase_engine", ENGINE)
    if spec is None or spec.loader is None:
        raise RuntimeError(ENGINE)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    module.CIRCUIT_PATH = SOURCE
    return module


def support(engine, truth: int) -> frozenset[int]:
    variables = tuple(engine.variable(i) for i in range(engine.VARIABLES))
    return frozenset(engine.dependency_support(truth, variables))


def main() -> None:
    engine = load_engine()
    _circuit, _compiled, networks, _outputs = engine.evaluate()
    all_bits = engine.ALL
    sources: dict[int, Signal] = {}

    def add(signal: Signal) -> None:
        old = sources.get(signal.truth)
        if old is None or (signal.depth, signal.expression) < (old.depth, old.expression):
            sources[signal.truth] = signal

    for index in range(engine.VARIABLES):
        add(Signal(engine.variable(index), 0, f"x{index}"))
    add(Signal(0, 0, "0"))
    add(Signal(all_bits, 0, "1"))
    for network, signal in networks.items():
        if len(signal.bits) == 1:
            add(Signal(signal.bits[0], signal.depth, f"N{network}"))

    c5 = networks[246].bits[0]
    target = (~c5) & all_bits
    target_support = support(engine, target)
    # 两层普通门无需引入目标支撑外变量；保守地只保留支撑子集信号。
    filtered = {
        truth: signal
        for truth, signal in sources.items()
        if support(engine, truth).issubset(target_support)
    }
    early1 = [signal for signal in filtered.values() if signal.depth <= 1]
    early2 = [signal for signal in filtered.values() if signal.depth <= 2]
    operations = (
        ("AND", lambda a, b: a & b),
        ("OR", lambda a, b: a | b),
        ("NAND", lambda a, b: (~(a & b)) & all_bits),
        ("NOR", lambda a, b: (~(a | b)) & all_bits),
    )

    first: dict[int, Signal] = {}

    def add_first(signal: Signal) -> None:
        old = first.get(signal.truth)
        if old is None or signal.expression < old.expression:
            first[signal.truth] = signal

    for signal in early1:
        add_first(Signal((~signal.truth) & all_bits, signal.depth + 1, f"NOT({signal.expression})"))
    for left_index, left in enumerate(early1):
        for right in early1[left_index:]:
            depth = max(left.depth, right.depth) + 1
            for name, operation in operations:
                add_first(
                    Signal(
                        operation(left.truth, right.truth),
                        depth,
                        f"{name}({left.expression},{right.expression})",
                    )
                )

    hits: list[dict[str, object]] = []
    if target in first:
        item = first[target]
        hits.append({"gate": 1, "depth": item.depth, "expression": item.expression})
    for intermediate in first.values():
        if intermediate.depth + 1 <= 3 and ((~intermediate.truth) & all_bits) == target:
            hits.append(
                {
                    "gate": 2,
                    "depth": intermediate.depth + 1,
                    "expression": f"NOT({intermediate.expression})",
                }
            )
        for other in early2:
            depth = max(intermediate.depth, other.depth) + 1
            if depth > 3:
                continue
            for name, operation in operations:
                if operation(intermediate.truth, other.truth) != target:
                    continue
                hits.append(
                    {
                        "gate": 2,
                        "depth": depth,
                        "expression": f"{name}({intermediate.expression},{other.expression})",
                    }
                )
    hits.sort(key=lambda item: (item["gate"], item["depth"], item["expression"]))
    unique = []
    seen = set()
    for item in hits:
        key = (item["gate"], item["depth"], item["expression"])
        if key not in seen:
            seen.add(key)
            unique.append(item)

    document = {
        "schema": "byte-adder-hub79-shared-carry-zero-phase-v1",
        "target": "~C5",
        "target_network": 246,
        "target_support": sorted(target_support),
        "source_signal_count": len(sources),
        "filtered_signal_count": len(filtered),
        "depth1_source_count": len(early1),
        "depth2_source_count": len(early2),
        "first_gate_unique_truths": len(first),
        "hit_count": len(unique),
        "hits": unique[:100],
        "interpretation": (
            "A <=2-gate depth<=3 hit would merge the two C5=0 drivers on each of "
            "S5/S6/S7. No hit means that specific shared-phase rewrite is unavailable "
            "from the current public signal basis."
        ),
    }
    OUTPUT.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(document, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
