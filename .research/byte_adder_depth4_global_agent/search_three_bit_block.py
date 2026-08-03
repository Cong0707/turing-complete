"""精确枚举三位区间在两层内的 Lblock / any-G 联合实现。

只使用普通 AND/OR/NAND/NOR/NOT 和 Bit Switch。Switch BUS 的 Z 在普通逻辑
输入处按 0 读取；候选 BUS 的每个 driver 都必须满足 active 时 data 与目标一致，
因此证书同时排除主动 0/1 冲突。

搜索空间只有 6 个原始输入，使用 64 位真值表，不接触游戏或存档。
"""

from __future__ import annotations

from dataclasses import dataclass
import itertools
import json
from pathlib import Path


OUT = Path(__file__).with_name("three_bit_block_frontier.json")
N = 6
ALL = (1 << (1 << N)) - 1


def variable(index: int) -> int:
    value = 0
    for assignment in range(1 << N):
        if (assignment >> index) & 1:
            value |= 1 << assignment
    return value


RAW = {
    "a0": variable(0),
    "b0": variable(1),
    "a1": variable(2),
    "b1": variable(3),
    "a2": variable(4),
    "b2": variable(5),
    "0": 0,
    "1": ALL,
}


@dataclass(frozen=True)
class Signal:
    truth: int
    cost: int
    expression: str
    primitive: tuple[str, ...]


@dataclass(frozen=True)
class Driver:
    enable: int
    data: int
    coverage: int
    used: frozenset[int]
    expression: str


def better(new: Signal, old: Signal | None) -> bool:
    return old is None or (new.cost, new.expression) < (old.cost, old.expression)


def add_signal(table: dict[int, Signal], signal: Signal) -> None:
    old = table.get(signal.truth)
    if better(signal, old):
        table[signal.truth] = signal


def conflict(left: tuple[int, int], right: tuple[int, int]) -> bool:
    le, ld = left
    re, rd = right
    return bool((le & re & (ld ^ rd)) & ALL)


def layer_one() -> dict[int, Signal]:
    signals = {
        truth: Signal(truth, 0, name, ())
        for name, truth in RAW.items()
    }
    leaves = sorted(RAW.items())
    for name, truth in leaves:
        add_signal(
            signals,
            Signal((~truth) & ALL, 1, f"NOT({name})", (f"NOT({name})",)),
        )
    operations = (
        ("AND", lambda a, b: a & b),
        ("OR", lambda a, b: a | b),
        ("NAND", lambda a, b: (~(a & b)) & ALL),
        ("NOR", lambda a, b: (~(a | b)) & ALL),
    )
    for index, (left_name, left) in enumerate(leaves):
        for right_name, right in leaves[index:]:
            for opname, operation in operations:
                expr = f"{opname}({left_name},{right_name})"
                add_signal(signals, Signal(operation(left, right), 1, expr, (expr,)))

    # 深度 1 的多 Switch BUS；只枚举最多三只 raw/raw driver。
    raw_drivers = []
    for ename, enable in leaves:
        if enable == 0:
            continue
        for dname, data in leaves:
            raw_drivers.append((enable, data, f"S({ename},{dname})"))
    # 去掉相同 (enable,data) 语义的重复名称。
    unique_driver: dict[tuple[int, int], str] = {}
    for enable, data, expr in raw_drivers:
        unique_driver.setdefault((enable, data), expr)
    raw_drivers = [(e, d, x) for (e, d), x in unique_driver.items()]

    for count in (1, 2, 3):
        for chosen in itertools.combinations(raw_drivers, count):
            pairs = [(item[0], item[1]) for item in chosen]
            if any(conflict(a, b) for a, b in itertools.combinations(pairs, 2)):
                continue
            truth = 0
            for enable, data, _ in chosen:
                truth |= enable & data
            expressions = tuple(item[2] for item in chosen)
            expr = "BUS(" + ",".join(expressions) + ")"
            add_signal(signals, Signal(truth, 2 * count, expr, expressions))
    return signals


def used_cost(used: frozenset[int], signals: dict[int, Signal]) -> int:
    return sum(signals[truth].cost for truth in used)


def valid_drivers(target: int, signals: dict[int, Signal]) -> list[Driver]:
    values = list(signals.values())
    best: dict[tuple[int, frozenset[int]], Driver] = {}
    raw_truths = set(RAW.values())
    for enable in values:
        for data in values:
            # active 时必须与目标一致；这也令任意两个保留 driver 互不冲突。
            if enable.truth & (data.truth ^ target):
                continue
            coverage = enable.truth & data.truth
            if not coverage:
                continue
            used = frozenset(
                truth
                for truth in (enable.truth, data.truth)
                if truth not in raw_truths
            )
            item = Driver(
                enable.truth,
                data.truth,
                coverage,
                used,
                f"S({enable.expression},{data.expression})",
            )
            key = (coverage, used)
            old = best.get(key)
            if old is None or item.expression < old.expression:
                best[key] = item

    ordered = sorted(
        best.values(),
        key=lambda item: (
            used_cost(item.used, signals),
            -item.coverage.bit_count(),
            item.expression,
        ),
    )
    # 同一 coverage 若 prerequisite 集合为超集且不更便宜，严格支配。
    result = []
    for item in ordered:
        if any(
            known.coverage == item.coverage
            and known.used.issubset(item.used)
            for known in result
        ):
            continue
        result.append(item)
    return result


def output_candidates(target: int, signals: dict[int, Signal], max_switches: int = 4):
    raw_truths = set(RAW.values())
    candidates: dict[tuple[frozenset[int], int], dict[str, object]] = {}

    if target in signals:
        signal = signals[target]
        used = frozenset(() if target in raw_truths else (target,))
        candidates[(used, 0)] = {
            "top": signal.expression,
            "switches": 0,
            "used": used,
            "total_cost": used_cost(used, signals),
        }

    values = list(signals.values())
    operations = (
        ("AND", lambda a, b: a & b),
        ("OR", lambda a, b: a | b),
        ("NAND", lambda a, b: (~(a & b)) & ALL),
        ("NOR", lambda a, b: (~(a | b)) & ALL),
    )
    for left_index, left in enumerate(values):
        for right in values[left_index:]:
            used = frozenset(
                truth
                for truth in (left.truth, right.truth)
                if truth not in raw_truths
            )
            for name, operation in operations:
                if operation(left.truth, right.truth) != target:
                    continue
                record = {
                    "top": f"{name}({left.expression},{right.expression})",
                    "switches": 0,
                    "used": used,
                    "total_cost": used_cost(used, signals) + 1,
                }
                key = (used, -1)
                old = candidates.get(key)
                if old is None or (record["total_cost"], record["top"]) < (
                    old["total_cost"], old["top"]
                ):
                    candidates[key] = record

    drivers = valid_drivers(target, signals)
    by_bit: dict[int, list[int]] = {}
    for index, driver in enumerate(drivers):
        coverage = driver.coverage
        bit = 0
        while coverage:
            low = coverage & -coverage
            assignment = low.bit_length() - 1
            by_bit.setdefault(assignment, []).append(index)
            coverage ^= low

    # 从尚未覆盖 target 的最低样本分支，避免排列重复。
    def visit(
        covered: int,
        chosen: tuple[int, ...],
        used: frozenset[int],
    ) -> None:
        if covered == target:
            count = len(chosen)
            expressions = tuple(drivers[index].expression for index in chosen)
            record = {
                "top": "BUS(" + ",".join(expressions) + ")",
                "switches": count,
                "used": used,
                "total_cost": used_cost(used, signals) + 2 * count,
            }
            key = (used, count)
            old = candidates.get(key)
            if old is None or (record["total_cost"], record["top"]) < (
                old["total_cost"], old["top"]
            ):
                candidates[key] = record
            return
        if len(chosen) >= max_switches:
            return
        missing = target & ~covered
        first = (missing & -missing).bit_length() - 1
        for index in by_bit.get(first, ()):
            if index in chosen:
                continue
            driver = drivers[index]
            if not (driver.coverage & missing):
                continue
            new_used = used | driver.used
            optimistic = used_cost(new_used, signals) + 2 * (len(chosen) + 1)
            if optimistic > 24:
                continue
            visit(
                covered | driver.coverage,
                chosen + (index,),
                new_used,
            )

    visit(0, (), frozenset())
    records = sorted(
        candidates.values(), key=lambda item: (item["total_cost"], item["top"])
    )
    # 保留共享 prerequisite 可能有价值的前沿，而非只留独立最小项。
    return records[:200]


def describe(record: dict[str, object], signals: dict[int, Signal]) -> dict[str, object]:
    used = record["used"]
    assert isinstance(used, frozenset)
    return {
        "cost": record["total_cost"],
        "switches": record["switches"],
        "top": record["top"],
        "prerequisites": [signals[truth].expression for truth in sorted(used)],
        "prerequisite_truths": [f"{truth:016x}" for truth in sorted(used)],
    }


def main() -> None:
    signals = layer_one()
    a0, b0 = RAW["a0"], RAW["b0"]
    a1, b1 = RAW["a1"], RAW["b1"]
    a2, b2 = RAW["a2"], RAW["b2"]
    g0, g1, g2 = a0 & b0, a1 & b1, a2 & b2
    l0, l1, l2 = a0 | b0, a1 | b1, a2 | b2
    lblock = l2 & (g2 | g1 | (l1 & l0))
    any_g = g0 | g1 | g2
    gblock = lblock & any_g

    targets = {
        "Lblock": lblock,
        "AnyG": any_g,
        "Gblock": gblock,
    }
    frontiers = {
        name: output_candidates(target, signals)
        for name, target in targets.items()
    }
    joint = []
    for left in frontiers["Lblock"]:
        for right in frontiers["AnyG"]:
            used = left["used"] | right["used"]
            cost = (
                used_cost(used, signals)
                + 2 * int(left["switches"])
                + 2 * int(right["switches"])
                + (1 if int(left["switches"]) == 0 and str(left["top"]).split("(", 1)[0] in {"AND", "OR", "NAND", "NOR"} else 0)
                + (1 if int(right["switches"]) == 0 and str(right["top"]).split("(", 1)[0] in {"AND", "OR", "NAND", "NOR"} else 0)
            )
            # record.total_cost 已含顶层门；上面的重算只用于共享 prerequisite。
            cost = int(left["total_cost"]) + int(right["total_cost"]) - (
                used_cost(left["used"], signals)
                + used_cost(right["used"], signals)
                - used_cost(used, signals)
            )
            joint.append((cost, left, right, used))
    joint.sort(key=lambda item: (item[0], item[1]["top"], item[2]["top"]))

    document = {
        "schema": "byte-adder-three-bit-depth2-joint-v1",
        "raw_variables": list(RAW),
        "layer_one_unique_truths": len(signals),
        "targets": {
            name: f"{target:016x}" for name, target in targets.items()
        },
        "independent_frontiers": {
            name: [describe(record, signals) for record in records[:30]]
            for name, records in frontiers.items()
        },
        "joint_Lblock_AnyG": [
            {
                "cost": cost,
                "Lblock": describe(left, signals),
                "AnyG": describe(right, signals),
                "shared_prerequisites": [
                    signals[truth].expression for truth in sorted(used)
                ],
            }
            for cost, left, right, used in joint[:100]
        ],
    }
    OUT.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "layer_one_unique_truths": len(signals),
                "best": {
                    name: describe(records[0], signals) if records else None
                    for name, records in frontiers.items()
                },
                "joint_best": document["joint_Lblock_AnyG"][0],
                "output": str(OUT),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
