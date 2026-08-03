"""低内存并行复算 Hub79 Switch/Boolean BUS 的全局 Pareto。

共享研究脚本的单进程版本对 18 个 BUS 枚举 2^18 个选择。这里仅把 mask
区间切成四份；每个 worker 使用完全相同的 backward-slice 和时序模型，最后按
``(gate, delay)`` 合并。它不运行游戏，也不生成或修改存档。
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import multiprocessing as mp
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
JOINT = ROOT / ".research/byte_adder_switch_z_agent/search_joint_choices.py"


def load_joint(name: str):
    spec = importlib.util.spec_from_file_location(name, JOINT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {JOINT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def search_range(task: tuple[int, int, int]) -> tuple[int, list[dict[str, object]]]:
    depth_limit, start, end = task
    joint = load_joint(f"joint_worker_{depth_limit}_{start}")
    netlist = joint.Netlist(depth_limit, 0)
    best: dict[tuple[int, int], dict[str, object]] = {}
    feasible = 0
    for mask in range(start, end):
        netlist.boolean_mask = mask
        netlist.memo.clear()
        score = netlist.score()
        if int(score["delay"]) > depth_limit:
            continue
        feasible += 1
        key = (int(score["gate"]), int(score["delay"]))
        if key not in best:
            best[key] = {"mask": mask, "bus_order": netlist.bus_order, **score}
    return feasible, list(best.values())


def search(depth_limit: int, workers: int) -> dict[str, object]:
    joint = load_joint(f"joint_parent_{depth_limit}")
    probe = joint.Netlist(depth_limit, 0)
    total = 1 << len(probe.bus_order)
    tasks = []
    for index in range(workers):
        start = total * index // workers
        end = total * (index + 1) // workers
        tasks.append((depth_limit, start, end))
    context = mp.get_context("spawn")
    with context.Pool(workers) as pool:
        chunks = pool.map(search_range, tasks)

    feasible = sum(item[0] for item in chunks)
    merged: dict[tuple[int, int], dict[str, object]] = {}
    for _count, records in chunks:
        for record in records:
            key = (int(record["gate"]), int(record["delay"]))
            old = merged.get(key)
            if old is None or int(record["mask"]) < int(old["mask"]):
                merged[key] = record
    records = sorted(
        merged.values(),
        key=lambda item: (int(item["energy"]), int(item["gate"]), int(item["delay"])),
    )
    pareto = [
        item
        for item in records
        if not any(
            int(other["gate"]) <= int(item["gate"])
            and int(other["delay"]) <= int(item["delay"])
            and (other["gate"], other["delay"]) != (item["gate"], item["delay"])
            for other in records
        )
    ]
    return {
        "schema": "hub79-joint-choice-parallel-v1",
        "depth_limit": depth_limit,
        "worker_count": workers,
        "masks_checked": total,
        "feasible_masks": feasible,
        "best": records[:20],
        "pareto": pareto,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("depth", type=int, choices=range(4, 8))
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    if not 1 <= args.workers <= 4:
        raise SystemExit("workers must be between 1 and 4")
    result = search(args.depth, args.workers)
    output = Path(__file__).with_name(f"joint_choice_depth{args.depth}.json")
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"best": result["best"][:3], "pareto": result["pareto"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
