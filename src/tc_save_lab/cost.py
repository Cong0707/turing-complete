"""递归分析当前 v15 自定义元件的门数与依赖关系。

该模块只读扫描电路文件。头部的 ``gate``/``delay`` 是游戏写入的计分结果；
本工具不会猜测基础元件成本，也不会伪造延迟。门数可以利用 Custom 实例
递归展开，延迟只报告头部实测值与子电路的关键路径下界。
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import json

from .codec import decode_v15
from .model import Circuit


@dataclass(frozen=True)
class CustomCircuit:
    custom_id: int
    path: str
    circuit: Circuit


def _find_circuit_files(root: Path) -> list[Path]:
    return sorted(root.rglob("circuit.data")) if root.exists() else []


def _custom_instances(circuit: Circuit) -> Counter[int]:
    return Counter(
        component.custom_id
        for component in circuit.components
        if component.kind == 78 and component.custom_id
    )


def scan_custom_circuits(root: Path) -> tuple[dict[int, list[CustomCircuit]], list[dict[str, object]]]:
    """读取 ``root`` 下所有可解码的自定义电路，并保留重复 ID 证据。"""

    by_id: dict[int, list[CustomCircuit]] = {}
    errors: list[dict[str, object]] = []
    for path in _find_circuit_files(root):
        try:
            circuit = decode_v15(path.read_bytes())
        except Exception as exc:  # pragma: no cover - defensive inventory path
            errors.append({"path": str(path), "error": str(exc)})
            continue
        if not circuit.custom_id:
            continue
        record = CustomCircuit(circuit.custom_id, str(path), circuit)
        by_id.setdefault(circuit.custom_id, []).append(record)
    return by_id, errors


class CostModelError(ValueError):
    """依赖图存在缺失或环，无法给出可信递归门数。"""


def analyze_custom_costs(root: Path) -> dict[str, object]:
    """生成可审计的递归成本报告，不写入被扫描目录。"""

    by_id, decode_errors = scan_custom_circuits(root)
    unique = {custom_id: records[0] for custom_id, records in by_id.items()}
    duplicate_ids = {
        str(custom_id): [record.path for record in records]
        for custom_id, records in sorted(by_id.items())
        if len(records) > 1
    }
    state: dict[int, int] = {}
    resolved: dict[int, int] = {}
    stack: list[int] = []
    cycle_ids: list[list[int]] = []

    def resolve(custom_id: int) -> int | None:
        mark = state.get(custom_id, 0)
        if mark == 2:
            return resolved.get(custom_id)
        if mark == 1:
            try:
                first = stack.index(custom_id)
            except ValueError:  # pragma: no cover - defensive
                first = 0
            cycle_ids.append(stack[first:] + [custom_id])
            return None
        record = unique.get(custom_id)
        if record is None:
            return None
        state[custom_id] = 1
        stack.append(custom_id)
        instances = _custom_instances(record.circuit)
        child_values: dict[int, int | None] = {
            child_id: resolve(child_id) for child_id in instances
        }
        stack.pop()
        if any(value is None for value in child_values.values()):
            state[custom_id] = 2
            return None
        direct_declared = sum(
            count * unique[child_id].circuit.gate
            for child_id, count in instances.items()
            if child_id in unique
        )
        local_gate = record.circuit.gate - direct_declared
        recursive_gate = local_gate + sum(
            count * child_values[child_id]
            for child_id, count in instances.items()
            if child_values[child_id] is not None
        )
        resolved[custom_id] = recursive_gate
        state[custom_id] = 2
        return recursive_gate

    circuits: list[dict[str, object]] = []
    missing_ids: set[int] = set()
    for custom_id, record in sorted(unique.items()):
        circuit = record.circuit
        instances = _custom_instances(circuit)
        declared_dependencies = set(circuit.dependencies)
        direct_dependencies = set(instances)
        missing = sorted(child_id for child_id in direct_dependencies if child_id not in unique)
        missing_ids.update(missing)
        recursive_gate = resolve(custom_id)
        direct_declared_gate = sum(
            count * unique[child_id].circuit.gate
            for child_id, count in instances.items()
            if child_id in unique
        )
        circuits.append(
            {
                "custom_id": custom_id,
                "path": record.path,
                "declared_gate": circuit.gate,
                "declared_delay": circuit.delay,
                "declared_energy": circuit.energy,
                "component_count": len(circuit.components),
                "direct_custom_instances": {str(k): v for k, v in sorted(instances.items())},
                "declared_dependencies": sorted(declared_dependencies),
                "direct_dependencies": sorted(direct_dependencies),
                "dependency_mismatch": sorted(declared_dependencies ^ direct_dependencies),
                "missing_dependencies": missing,
                "local_gate_excluding_children": circuit.gate - direct_declared_gate,
                "recursive_gate": recursive_gate,
                "recursive_gate_matches_header": recursive_gate == circuit.gate
                if recursive_gate is not None
                else False,
                "delay_note": "延迟使用电路头部实测值；递归关键路径尚未从时序元件语义重建",
            }
        )

    return {
        "root": str(root),
        "format": "v15 custom circuit recursive gate report",
        "circuit_count": len(circuits),
        "duplicate_custom_ids": duplicate_ids,
        "missing_dependency_ids": sorted(missing_ids),
        "cycle_ids": cycle_ids,
        "decode_errors": decode_errors,
        "circuits": circuits,
        "healthy": not duplicate_ids and not missing_ids and not cycle_ids and not decode_errors
        and all(item["recursive_gate_matches_header"] and not item["dependency_mismatch"] for item in circuits),
    }


def write_cost_report(root: Path, destination: Path) -> dict[str, object]:
    report = analyze_custom_costs(root)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report
