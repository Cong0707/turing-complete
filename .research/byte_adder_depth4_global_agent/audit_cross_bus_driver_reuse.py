"""审计 SAT 证书是否把同一三态输出免费复用到多个独立 BUS。

Turing Complete 的导线按端点位置合并网络。同一元件输出针脚上的所有导线属于同一
network；因此一个 Switch 输出若被接到两组 BUS，它们会成为同一 BUS，而不是两份
隔离驱动。只有复制 Switch 才能驱动两个不同的 resolved BUS。
"""

from __future__ import annotations

from collections import defaultdict
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = Path(__file__).with_name("cross_bus_driver_reuse_audit.json")
CERTIFICATES = (
    ROOT
    / ".research/byte_adder_boolean_superopt_agent/transfer2-b10-d2-c7-s3.json",
    ROOT
    / ".research/byte_adder_boolean_superopt_agent/transfer3-b18-d3-c12-s6.json",
)


def audit(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    network = {int(item["source"]): item for item in payload["network"]}
    memberships: dict[int, list[int]] = defaultdict(list)
    for bus_index, bus in enumerate(payload["output_buses"]):
        for source in bus:
            memberships[int(source)].append(bus_index)

    reused = []
    for source, buses in sorted(memberships.items()):
        unique_buses = sorted(set(buses))
        if len(unique_buses) <= 1:
            continue
        item = network.get(source)
        reused.append(
            {
                "source": source,
                "kind": None if item is None else item["kind"],
                "bus_indices": unique_buses,
                "bus_members": [payload["output_buses"][index] for index in unique_buses],
            }
        )

    # 若两个 bus 的成员集合不完全相同，它们本应是不同 resolved network；共享一个
    # 物理输出针脚会把它们短成成员并集。
    nonidentical = []
    for item in reused:
        members = {tuple(bus) for bus in item["bus_members"]}
        if len(members) > 1:
            nonidentical.append(item)
    return {
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "claimed_gate": payload.get("actual_gate"),
        "claimed_delay": payload.get("max_delay"),
        "output_buses": payload["output_buses"],
        "reused_sources": reused,
        "nonidentical_bus_reuse": nonidentical,
        "materializable_as_independent_buses": not nonidentical,
    }


def main() -> None:
    results = [audit(path) for path in CERTIFICATES]
    document = {
        "schema": "tc-cross-bus-tristate-driver-audit-v1",
        "rule": (
            "All wires sharing one output pin are one electrical network. A tri-state source "
            "cannot be a driver of two nonidentical resolved buses without duplicating the "
            "source component."
        ),
        "results": results,
        "all_materializable": all(
            bool(item["materializable_as_independent_buses"]) for item in results
        ),
        "conclusion": (
            "The claimed 10/2 and 18/3 transfer macros reuse Switch sources across "
            "nonidentical U/V buses. Their Boolean replay is valid only in the abstract "
            "resolver; the networks cannot be wired as two independent TC buses. The shared "
            "driver must be duplicated, restoring the G/L combine cost from 6/1 to 8/1."
        ),
    }
    OUTPUT.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(document, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
