"""把抽象 transfer 证书改写为物理上可隔离的独立输出 BUS。

修复只复制必要的 Switch source 或删除被支配项，不改变布尔函数。随后调用原项目的
独立 replay 逻辑重新计算真值、冲突、Z-zero 与实际深度。
"""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = ROOT / ".research/byte_adder_boolean_superopt_agent"
OUT_DIR = Path(__file__).parent


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


exact = load_module("physical_transfer_exact", SOURCE_DIR / "exact_adder_block_sat.py")
sys.modules["exact_adder_block_sat"] = exact
transfer = load_module("physical_transfer_targets", SOURCE_DIR / "exact_transfer_sat.py")


def duplicate(payload: dict[str, object], source: int) -> int:
    network = payload["network"]
    assert isinstance(network, list)
    original = next(item for item in network if int(item["source"]) == source)
    clone = copy.deepcopy(original)
    new_source = max(int(item["source"]) for item in network) + 1
    clone["slot"] = len(network)
    clone["source"] = new_source
    network.append(clone)
    payload["components"] = len(network)
    payload["actual_gate"] = int(payload["actual_gate"]) + int(clone["cost"])
    payload["gate_bound"] = payload["actual_gate"]
    if clone["kind"] == "SWITCH" and payload.get("exact_switches") is not None:
        payload["exact_switches"] = int(payload["exact_switches"]) + 1
    return new_source


def replay(payload: dict[str, object]) -> None:
    old = exact.adder_targets
    exact.adder_targets = transfer.transfer_targets
    try:
        payload["verification"] = exact.verify_payload(payload)
    finally:
        exact.adder_targets = old


def repair_two() -> Path:
    source = SOURCE_DIR / "transfer2-b10-d2-c7-s3.json"
    payload = json.loads(source.read_text(encoding="utf-8"))
    # U=[G1, L1*G0]. V 只需要 [G1, L1*L0]；L1*G0 被 L1*L0 支配。
    duplicate_g1 = duplicate(payload, 7)
    payload["output_buses"] = [[7, 11], [duplicate_g1, 12]]
    payload["physical_bus_isolation"] = {
        "status": "repaired",
        "rule": "no source belongs to more than one output bus",
        "change": "duplicate source 7; remove redundant source 11 from V",
    }
    replay(payload)
    output = OUT_DIR / "transfer2-physical-b12-d2.json"
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output


def repair_three() -> Path:
    source = SOURCE_DIR / "transfer3-b18-d3-c12-s6.json"
    payload = json.loads(source.read_text(encoding="utf-8"))
    duplicate_shared = duplicate(payload, 19)
    payload["output_buses"] = [[17, 19], [18, duplicate_shared]]
    payload["physical_bus_isolation"] = {
        "status": "repaired",
        "rule": "no source belongs to more than one output bus",
        "change": "duplicate shared source 19 for the second output bus",
    }
    replay(payload)
    output = OUT_DIR / "transfer3-physical-b20-d3.json"
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output


def main() -> None:
    outputs = [repair_two(), repair_three()]
    summary = []
    for path in outputs:
        payload = json.loads(path.read_text(encoding="utf-8"))
        memberships: dict[int, int] = {}
        for bus in payload["output_buses"]:
            for source in bus:
                memberships[int(source)] = memberships.get(int(source), 0) + 1
        summary.append(
            {
                "path": str(path.relative_to(ROOT)).replace("\\", "/"),
                "gate": payload["actual_gate"],
                "delay": payload["verification"]["replayed_max_component_depth"],
                "cross_bus_reused_sources": sorted(
                    source for source, count in memberships.items() if count > 1
                ),
                "verification": payload["verification"],
            }
        )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
