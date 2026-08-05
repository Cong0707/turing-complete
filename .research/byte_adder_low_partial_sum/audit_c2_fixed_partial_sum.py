"""审计 85/6 Byte Adder 的 C2@2 与部分 S1 边界。

默认只执行轻量的正覆盖扫描；``--ordinary-sat`` 会调用仓库已有的
四门普通 DAG 精确编码器，验证 S1 的四门下界。脚本只读 Factory DAG，
不会访问游戏进程、正式存档或布局输出。
"""

from __future__ import annotations

import argparse
import importlib.util
import itertools
import json
from pathlib import Path
import sys
from typing import Any


HERE = Path(__file__).resolve().parent
# ``HERE`` is ``repo/.research/byte_adder_low_partial_sum``; its second
# parent is the repository root (``Path.parents[0]`` is ``.research``).
ROOT = HERE.parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))
DAG_PATH = (
    ROOT
    / ".research"
    / "byte_adder_architecture_restart"
    / "byte-adder-human85-s3-positive-phase-full.json"
)
MATERIALIZER_PATH = (
    ROOT
    / ".research"
    / "byte_adder_builder_layout_agent"
    / "materialize_factory_dag.py"
)
SAT_PATH = ROOT / ".research" / "byte_adder_root" / "audit_80d7_four_gate_dag_sat.py"

OUTPUT_NAMES = ("S0", "S1", "S2", "S3", "S4", "S5", "S6", "S7", "C8")
S1_SOURCE_IDS = (1, 2, 9, 10, 17, 18, 19, 20, 21, 22, 23, 26, 45)
S1_PRIVATE_IDS = (36, 37, 38, 39, 46)
ORDINARY_KINDS = ("AND", "NAND", "OR", "NOR")


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载模块：{path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load() -> tuple[dict[int, dict[str, Any]], dict[str, int]]:
    payload = json.loads(DAG_PATH.read_text(encoding="utf-8"))
    nodes = tuple(payload["factory_dag"]["nodes"])
    materializer = load_module(MATERIALIZER_PATH, "low_partial_sum_materializer")
    states = materializer.logical_states(nodes)
    outputs = dict(zip(OUTPUT_NAMES, payload["factory_dag"]["outputs"], strict=True))
    return states, outputs


def private_cones(nodes: dict[int, dict[str, Any]], outputs: dict[str, int]) -> dict[str, set[int]]:
    reaches: dict[int, set[str]] = {node_id: set() for node_id in nodes}

    def visit(node_id: int, output_name: str) -> None:
        if output_name in reaches[node_id]:
            return
        reaches[node_id].add(output_name)
        for parent in nodes[node_id]["args"]:
            visit(int(parent), output_name)

    for name, node_id in outputs.items():
        visit(node_id, name)
    return {
        name: {
            node_id
            for node_id, downstream in reaches.items()
            if downstream == {name} and nodes[node_id]["op"] != "INPUT"
        }
        for name in outputs
    }


def conflict_free_pair(
    first: tuple[int, int, int], second: tuple[int, int, int], target: int
) -> bool:
    enable_a, data_a, term_a = first
    enable_b, data_b, term_b = second
    if (term_a | term_b) != target:
        return False
    # A simultaneous 0/1 drive is a physical conflict even if the Boolean OR
    # happens to equal the requested positive cover.
    conflict = enable_a & enable_b & (data_a ^ data_b)
    return conflict == 0


def apply_gate(kind: str, left: int, right: int, mask: int) -> int:
    if kind == "AND":
        return left & right
    if kind == "NAND":
        return mask ^ (left & right)
    if kind == "OR":
        return left | right
    if kind == "NOR":
        return mask ^ (left | right)
    raise ValueError(kind)


def compact_low_truth(
    states: dict[int, dict[str, Any]], source_ids: tuple[int, ...], target_id: int
) -> tuple[list[tuple[int, int, str]], int, int]:
    classes: dict[int, bool] = {}
    for row in range(1 << 17):
        vector = 0
        for index, source_id in enumerate(source_ids):
            vector |= ((int(states[source_id]["bits"]) >> row) & 1) << index
        target = bool((int(states[target_id]["bits"]) >> row) & 1)
        previous = classes.get(vector)
        if previous is not None and previous != target:
            raise RuntimeError("目标函数不能由给定 source pool 决定")
        classes[vector] = target

    vectors = sorted(classes)
    source_rows = [
        (
            sum(((vector >> index) & 1) << row for row, vector in enumerate(vectors)),
            int(states[source_id]["depth"]),
            f"n{source_id}",
        )
        for index, source_id in enumerate(source_ids)
    ]
    target = sum(int(classes[vector]) << row for row, vector in enumerate(vectors))
    return source_rows, target, len(vectors)


def weighted_s1_shapes(states: dict[int, dict[str, Any]]) -> dict[str, Any]:
    """穷举固定 source pool 上成本不超过四的非普通四门形态。"""

    base, target, row_count = compact_low_truth(states, S1_SOURCE_IDS, 46)
    mask = (1 << row_count) - 1

    one_by_value: dict[int, tuple[int, str]] = {}
    for left_index, left in enumerate(base):
        for right in base[left_index:]:
            for kind in ORDINARY_KINDS:
                value = apply_gate(kind, left[0], right[0], mask)
                arrival = max(left[1], right[1]) + 1
                expression = f"{kind}({left[2]},{right[2]})"
                previous = one_by_value.get(value)
                if previous is None or (arrival, expression) < previous:
                    one_by_value[value] = (arrival, expression)
    one = [(value, arrival, expression) for value, (arrival, expression) in one_by_value.items()]

    def switch_hit(left: tuple[int, int, str], right: tuple[int, int, str]) -> str | None:
        if max(left[1], right[1]) + 1 > 6:
            return None
        if (left[0] & right[0]) != target:
            return None
        return f"SW({left[2]},{right[2]})"

    switch_hits: set[str] = set()
    # 0 或 1 只普通门后接最终 Switch。
    for left in [*base, *one]:
        for right in base:
            hit = switch_hit(left, right)
            if hit:
                switch_hits.add(hit)
    # 两只互相独立的一门信号后接最终 Switch。
    for left_index, left in enumerate(one):
        for right in one[left_index:]:
            hit = switch_hit(left, right)
            if hit:
                switch_hits.add(hit)
    # 两门串联；最终 Switch 可同时消费祖先或任一原 source。
    for ancestor in one:
        available = [*base, ancestor]
        for right_operand in available:
            for kind in ORDINARY_KINDS:
                chain = (
                    apply_gate(kind, ancestor[0], right_operand[0], mask),
                    max(ancestor[1], right_operand[1]) + 1,
                    f"{kind}({ancestor[2]},{right_operand[2]})",
                )
                for final_peer in [*base, ancestor]:
                    hit = switch_hit(chain, final_peer)
                    if hit:
                        switch_hits.add(hit)

    xor_hits: set[str] = set()
    for left_index, left in enumerate(base):
        for right in base[left_index:]:
            xor_value = left[0] ^ right[0]
            xor_arrival = max(left[1], right[1]) + 2
            xor_expression = f"XOR({left[2]},{right[2]})"
            if xor_arrival <= 6 and xor_value == target:
                xor_hits.add(xor_expression)
            xor_signal = (xor_value, xor_arrival, xor_expression)
            for peer in [*base, xor_signal]:
                for kind in ORDINARY_KINDS:
                    value = apply_gate(kind, xor_signal[0], peer[0], mask)
                    arrival = max(xor_signal[1], peer[1]) + 1
                    if arrival <= 6 and value == target:
                        xor_hits.add(f"{kind}({xor_expression},{peer[2]})")

    for ordinary in one:
        for source in base:
            value = ordinary[0] ^ source[0]
            arrival = max(ordinary[1], source[1]) + 2
            if arrival <= 6 and value == target:
                xor_hits.add(f"XOR({ordinary[2]},{source[2]})")

    return {
        "compressed_truth_rows": row_count,
        "one_gate_function_count": len(one),
        "final_switch_plus_at_most_two_ordinary_hits": sorted(switch_hits),
        "switch_shape_hit_count": len(switch_hits),
        "xor_or_xor_plus_one_ordinary_hits": sorted(xor_hits),
        "xor_shape_hit_count": len(xor_hits),
    }


def positive_cover(
    states: dict[int, dict[str, Any]],
    nodes: dict[int, dict[str, Any]],
    output_id: int,
    excluded: set[int],
) -> dict[str, Any]:
    target = int(states[output_id]["bits"])
    candidate_ids = [
        node_id
        for node_id, node in nodes.items()
        if node_id not in excluded and int(node["arrival"]) <= 5
    ]
    terms: list[tuple[int, int, int, int]] = []
    for enable_id in candidate_ids:
        enable = int(states[enable_id]["bits"])
        for data_id in candidate_ids:
            data = int(states[data_id]["bits"])
            term = enable & data
            if term and not (term & ~target):
                terms.append((enable_id, data_id, enable, data))

    pairs = []
    for index, left in enumerate(terms):
        left_tuple = (left[2], left[3], left[2] & left[3])
        for right in terms[index:]:
            right_tuple = (right[2], right[3], right[2] & right[3])
            if conflict_free_pair(left_tuple, right_tuple, target):
                pairs.append(
                    {
                        "left": [left[0], left[1]],
                        "right": [right[0], right[1]],
                    }
                )
    return {
        "target": output_id,
        "candidate_nodes": len(candidate_ids),
        "positive_term_count": len(terms),
        "two_switch_conflict_free_covers": pairs,
        "cover_count": len(pairs),
    }


def ordinary_s1(states: dict[int, dict[str, Any]], gate_count: int) -> dict[str, Any]:
    sat = load_module(SAT_PATH, "low_partial_sum_ordinary_sat")
    sat.DELAY_LIMIT = 6
    result = sat.solve_target(S1_SOURCE_IDS, 46, states, gate_count, "cadical195")
    return {
        "gate_count": gate_count,
        "status": result["status"],
        "compressed_truth_rows": result["compressed_truth_rows"],
        "delay_limit": result["delay_limit"],
        "witness": result.get("witness"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--ordinary-sat",
        action="store_true",
        help="调用 PySAT 验证 S1 的 4/5 门普通 DAG；默认不启动求解器",
    )
    args = parser.parse_args()

    states, outputs = load()
    payload = json.loads(DAG_PATH.read_text(encoding="utf-8"))
    nodes = {int(node["id"]): node for node in payload["factory_dag"]["nodes"]}
    cones = private_cones(nodes, outputs)
    result: dict[str, Any] = {
        "schema": "byte-adder-c2-fixed-partial-sum-audit-v1",
        "dag": str(DAG_PATH),
        "baseline": {"gate": 85, "delay": 6, "energy": 510},
        "s1_boundary": {
            "source_ids": list(S1_SOURCE_IDS),
            "private_ids": list(S1_PRIVATE_IDS),
            "private_gate_cost": sum(int(nodes[node_id]["cost"]) for node_id in S1_PRIVATE_IDS),
            "two_switch_source_cover": positive_cover(
                states, nodes, 46, set(S1_PRIVATE_IDS)
            ),
            "weighted_cost_at_most_four_nonordinary_shapes": weighted_s1_shapes(states),
        },
        "all_large_private_sum_cones": {
            name: {
                "private_ids": sorted(cones[name]),
                "private_gate_cost": sum(
                    int(nodes[node_id]["cost"]) for node_id in cones[name]
                ),
                "two_switch_source_cover": positive_cover(
                    states, nodes, outputs[name], cones[name]
                ),
            }
            for name in ("S0", "S1", "S3")
        },
        "ordinary_s1": None,
    }
    if args.ordinary_sat:
        result["ordinary_s1"] = {
            "four": ordinary_s1(states, 4),
            "five": ordinary_s1(states, 5),
        }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
