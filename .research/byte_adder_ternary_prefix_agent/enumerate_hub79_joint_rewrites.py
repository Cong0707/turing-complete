"""复算 Hub79 Switch BUS 的联合保留/布尔替换前沿。

本脚本只读公开 Hub79 电路以及已经生成的逐 BUS 表达式库，不读取或修改游戏存档。
它调用经过校准的全局 backward-slice 计分器，因此会在替换后重新递归计算真实到达
时间，而不是把各 BUS 的冻结输入到达时间直接相加。
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
SEARCH = ROOT / ".research/byte_adder_switch_z_agent/search_joint_choices.py"
OUTPUT_DIR = Path(__file__).resolve().parent


def load_search():
    spec = importlib.util.spec_from_file_location("byte_adder_joint_rewrite", SEARCH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载 {SEARCH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--depth",
        type=int,
        action="append",
        choices=(4, 5, 6, 7),
        help="可重复指定；默认复算 5、6 延迟前沿",
    )
    args = parser.parse_args()
    depths = args.depth or [5, 6]
    search = load_search()

    original = search.Netlist(7, 0).score()
    if (original["gate"], original["delay"]) != (154, 4):
        raise RuntimeError(f"Hub79 基线计分漂移：{original}")

    for depth in depths:
        result = search.search(depth)
        output = OUTPUT_DIR / f"joint_d{depth}.json"
        output.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(
            json.dumps(
                {
                    "depth": depth,
                    "masks_checked": result["masks_checked"],
                    "feasible_masks": result["feasible_masks"],
                    "pareto": [
                        {
                            "gate": item["gate"],
                            "delay": item["delay"],
                            "energy": item["energy"],
                            "boolean_buses": item["boolean_buses"],
                        }
                        for item in result["pareto"]
                    ],
                    "output": str(output),
                },
                ensure_ascii=False,
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
