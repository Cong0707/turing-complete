"""Hub79 的跨 BUS / 跨输出全局 D5 函数重映射。

与已经封闭的“每条 BUS 独立替换”不同，本脚本先把公开 154/4 电路压缩成
实际出现的布尔函数集合，再允许任意输出共同复用：

* 普通 NOT/AND/OR/NAND/NOR，成本 1、延迟 1；
* 原电路中的完整 resolved BUS；
* 新枚举的两个 Switch resolved BUS，成本 4、延迟 1。

两个 Switch 的枚举严格检查每个 driver 在 enable 区域都与目标函数一致，且两个
driver 的 1 覆盖并集等于目标函数。因此重叠启用时不可能产生 0/1 冲突；目标为 0
的输入允许整条 BUS 为 Z，后续普通门按游戏规则读取为 0。

搜索空间刻意限制为 Hub79 已出现的 93 个标量函数及其补函数（共 164 个函数）。
所以 SAT 见证是完整合法上界，UNSAT 只构成这一“Hub79 函数闭包”内的下界，绝不
外推为任意 Byte Adder 的全局下界。

脚本只做离线求解，不启动游戏，不读取或修改正式存档。
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time
from typing import Iterable

import z3


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ENGINE = ROOT / "examples/rng/research/archive/rng_switch_public/analyze_hub79.py"
SOURCE = (
    ROOT
    / "examples/rng/research/archive/rng_public_artifacts/hub-79-adder/main/circuit.data"
)
DEFAULT_OUTPUT = HERE / "hub79-global-function-map-d5.json"


@dataclass(frozen=True, slots=True)
class Recipe:
    target: int
    op: str
    deps: tuple[int, ...]
    cost: int
    step_delay: int
    detail: tuple[object, ...] = ()


@dataclass(frozen=True, slots=True)
class Candidate:
    recipe_index: int
    arrival: int


def reachable_recipes(
    recipes: list[Recipe], sources: set[int] | dict[int, int], delay_bound: int
) -> tuple[list[int], dict[int, int]]:
    """返回在深度界内可能物化的配方和每个函数的乐观最早到达。"""

    earliest = (
        dict(sources)
        if isinstance(sources, dict)
        else {truth: 0 for truth in sources}
    )
    changed = True
    while changed:
        changed = False
        for recipe in recipes:
            if not all(dep in earliest for dep in recipe.deps):
                continue
            arrival = max((earliest[dep] for dep in recipe.deps), default=0) + 1
            if arrival > delay_bound:
                continue
            old = earliest.get(recipe.target)
            if old is None or arrival < old:
                earliest[recipe.target] = arrival
                changed = True
    active = [
        index
        for index, recipe in enumerate(recipes)
        if all(dep in earliest for dep in recipe.deps)
        and max((earliest[dep] for dep in recipe.deps), default=0) + 1
        <= delay_bound
    ]
    return active, earliest


def pysat_select(
    recipes: list[Recipe],
    active_recipe_indices: list[int],
    producers: dict[int, list[int]],
    earliest: dict[int, int],
    sources: dict[int, int],
    outputs: list[tuple[str, int]],
    *,
    delay_bound: int,
    gate_bound: int,
    timeout_ms: int,
    solver_name: str,
    cost_encoding: str,
    cardinality_encoding: str,
) -> tuple[str, list[int], dict[int, int], dict[str, object]]:
    """用 CaDiCaL + PB CNF 完成有界联合选择。"""

    import threading

    from pysat.card import CardEnc, EncType
    from pysat.formula import CNF, IDPool
    from pysat.solvers import Solver

    pool = IDPool()
    xvars = {index: pool.id(("x", index)) for index in active_recipe_indices}
    avars = {
        (truth, depth): pool.id(("a", truth, depth))
        for truth in producers
        for depth in range(max(1, earliest[truth]), delay_bound + 1)
    }
    cnf = CNF()

    def add_at_most_one(literals: list[int]) -> None:
        if len(literals) > 1:
            encoded = CardEnc.atmost(
                lits=literals, bound=1, vpool=pool, encoding=EncType.seqcounter
            )
            cnf.extend(encoded.clauses)

    for truth, recipe_rows in producers.items():
        selected_rows = [xvars[index] for index in recipe_rows]
        arrival_rows = [
            avars[(truth, depth)]
            for depth in range(max(1, earliest[truth]), delay_bound + 1)
        ]
        add_at_most_one(selected_rows)
        add_at_most_one(arrival_rows)
        # 被选中的 producer 必须选择一个到达层；反向也成立。
        for variable in selected_rows:
            cnf.append([-variable, *arrival_rows])
        for variable in arrival_rows:
            cnf.append([-variable, *selected_rows])

    def available_before(truth: int, deadline: int) -> list[int] | None:
        if truth in sources and sources[truth] <= deadline:
            return None
        return [
            avars[(truth, depth)]
            for depth in range(max(1, earliest.get(truth, delay_bound + 1)), deadline + 1)
            if (truth, depth) in avars
        ]

    for recipe_index in active_recipe_indices:
        recipe = recipes[recipe_index]
        selected = xvars[recipe_index]
        for target_depth in range(max(1, earliest[recipe.target]), delay_bound + 1):
            target_arrival = avars[(recipe.target, target_depth)]
            for dep in recipe.deps:
                dependency_rows = available_before(
                    dep, target_depth - recipe.step_delay
                )
                if dependency_rows is not None:
                    cnf.append([-selected, -target_arrival, *dependency_rows])

    for _name, truth in outputs:
        cnf.append([xvars[index] for index in producers.get(truth, ())])

    encoding_by_name = {
        "seqcounter": EncType.seqcounter,
        "cardnetwrk": EncType.cardnetwrk,
        "sortnetwrk": EncType.sortnetwrk,
        "totalizer": EncType.totalizer,
        "mtotalizer": EncType.mtotalizer,
        "kmtotalizer": EncType.kmtotalizer,
    }
    encoding = encoding_by_name[cardinality_encoding]

    # 当前环境不依赖 pypblib。把小整数权重严格展开成普通 cardinality。
    # grouped 与 expanded 完全等价：每个函数至多选择一个 producer，因此可用
    # 唯一 arrival literal 支付基础 1 gate，只为昂贵配方展开 cost-1 份附加成本。
    # producer-tiered 再利用同一个“至多一个 producer”约束，把基础成本和每个
    # surcharge 层级各压成每目标函数一个 literal。若选中 cost=c 的 producer，
    # 则该函数的 materialized literal 和 tier 2..c 恰好为真，仍严格支付 c gate，
    # 但不会为同一目标的数千条 BUS recipe 重复展开顺序计数器输入。
    cost_literals: list[int] = []
    if cost_encoding == "grouped":
        for truth in producers:
            cost_literals.extend(
                avars[(truth, depth)]
                for depth in range(max(1, earliest[truth]), delay_bound + 1)
            )
        surcharges = (
            (index, recipes[index].cost - 1) for index in active_recipe_indices
        )
    elif cost_encoding == "producer-tiered":
        for truth, recipe_rows in producers.items():
            arrival_rows = [
                avars[(truth, depth)]
                for depth in range(max(1, earliest[truth]), delay_bound + 1)
            ]
            materialized = pool.id(("cost_target", truth))
            for arrival in arrival_rows:
                cnf.append([-arrival, materialized])
            cnf.append([-materialized, *arrival_rows])
            cost_literals.append(materialized)

            maximum_cost = max(recipes[index].cost for index in recipe_rows)
            for tier in range(2, maximum_cost + 1):
                eligible = [
                    xvars[index]
                    for index in recipe_rows
                    if recipes[index].cost >= tier
                ]
                if not eligible:
                    continue
                tier_literal = pool.id(("cost_tier", truth, tier))
                for selected in eligible:
                    cnf.append([-selected, tier_literal])
                cnf.append([-tier_literal, *eligible])
                cost_literals.append(tier_literal)
        surcharges = ()
    elif cost_encoding == "expanded":
        surcharges = (
            (index, recipes[index].cost) for index in active_recipe_indices
        )
    else:
        raise ValueError(f"unknown cost encoding: {cost_encoding}")
    for index, copies in surcharges:
        selected = xvars[index]
        for offset in range(copies):
            copy = pool.id(("cost", index, offset))
            cnf.append([-copy, selected])
            cnf.append([-selected, copy])
            cost_literals.append(copy)
    bounded = CardEnc.atmost(
        lits=cost_literals,
        bound=gate_bound,
        vpool=pool,
        encoding=encoding,
    )
    cnf.extend(bounded.clauses)

    solver = Solver(name=solver_name, bootstrap_with=cnf.clauses)
    timer = threading.Timer(timeout_ms / 1000, solver.interrupt)
    timer.daemon = True
    timer.start()
    try:
        solved = solver.solve_limited(expect_interrupt=True)
        model = solver.get_model() if solved else None
        stats = solver.accum_stats()
    finally:
        timer.cancel()
        solver.delete()
    meta: dict[str, object] = {
        "backend": f"pysat-{solver_name}-cardinality",
        "solver": solver_name,
        "cost_encoding": cost_encoding,
        "cardinality_encoding": cardinality_encoding,
        "cost_literal_count": len(cost_literals),
        "cnf_variables": pool.top,
        "cnf_clauses": len(cnf.clauses),
        "solver_stats": stats,
    }
    if solved is None:
        return "unknown", [], {}, meta
    if not solved:
        return "unsat", [], {}, meta
    assert model is not None
    positive = {literal for literal in model if literal > 0}
    selected = [index for index, variable in xvars.items() if variable in positive]
    arrivals = {
        truth: depth
        for (truth, depth), variable in avars.items()
        if variable in positive
    }
    return "sat", selected, arrivals, meta


def load_engine():
    spec = importlib.util.spec_from_file_location("hub79_global_d5_engine", ENGINE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {ENGINE}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    module.CIRCUIT_PATH = SOURCE
    return module


def digest(value: int, byte_count: int) -> str:
    return hashlib.sha256(value.to_bytes(byte_count, "little")).hexdigest()


def component_input_truth(engine, compiled, networks, index: int, pin: str) -> int:
    network = compiled.pin_network.get((index, pin))
    if network is None:
        return 0
    return networks[network].bits[0]


def output_truths(engine, circuit, compiled, networks) -> list[tuple[str, int]]:
    roots: list[tuple[str, int]] = []
    for index, component in enumerate(circuit.components):
        if component.kind != 81:
            continue
        network = compiled.pin_network[(index, "out")]
        signal = networks[network]
        if component.user_label == "sum":
            roots.extend((f"sum{bit}", truth) for bit, truth in enumerate(signal.bits[:8]))
        else:
            roots.append(("cout", signal.bits[0]))
    if len(roots) != 9:
        raise RuntimeError(f"unexpected output roots: {roots}")
    return roots


def source_truths(engine, circuit, compiled, networks) -> dict[int, str]:
    result = {0: "ZERO", engine.ALL: "ONE"}
    for index, component in enumerate(circuit.components):
        if component.kind != 79:
            continue
        network = compiled.pin_network[(index, "in")]
        for bit, truth in enumerate(networks[network].bits):
            if component.user_label in {"A", "B"}:
                result.setdefault(truth, f"{component.user_label.lower()}{bit}")
            elif component.user_label == "Cin" and bit == 0:
                result.setdefault(truth, "cin")
    expected = 19
    if len(result) != expected:
        raise RuntimeError(f"expected {expected} constants/inputs, got {len(result)}")
    return result


def add_recipe(
    recipes_by_target: dict[int, dict[tuple[object, ...], Recipe]], recipe: Recipe
) -> None:
    # 同一布尔目标依赖自身的正延迟配方不可能成为 DAG 的首个 producer。
    if recipe.target in recipe.deps:
        return
    key = (recipe.op, recipe.deps, recipe.cost, recipe.step_delay, recipe.detail)
    recipes_by_target.setdefault(recipe.target, {})[key] = recipe


def ordinary_recipes(
    universe: list[int], all_mask: int
) -> dict[int, dict[tuple[object, ...], Recipe]]:
    allowed = set(universe)
    result: dict[int, dict[tuple[object, ...], Recipe]] = {}
    for source in universe:
        target = (~source) & all_mask
        if target in allowed:
            add_recipe(result, Recipe(target, "NOT", (source,), 1, 1))
    operations = (
        ("AND", lambda left, right: left & right),
        ("OR", lambda left, right: left | right),
        ("NAND", lambda left, right: (~(left & right)) & all_mask),
        ("NOR", lambda left, right: (~(left | right)) & all_mask),
    )
    for left_index, left in enumerate(universe):
        for right in universe[left_index:]:
            deps = (left, right)
            for name, operation in operations:
                target = operation(left, right)
                if target in allowed:
                    add_recipe(result, Recipe(target, name, deps, 1, 1))
    return result


def original_bus_recipes(
    engine, circuit, compiled, networks
) -> list[Recipe]:
    result: list[Recipe] = []
    for network, pins in compiled.network_pins.items():
        switches = [
            pin.component_index
            for pin in pins
            if pin.direction == engine.T and circuit.components[pin.component_index].kind == 12
        ]
        if not switches:
            continue
        target = networks[network].bits[0]
        drivers = tuple(
            (
                component_input_truth(engine, compiled, networks, index, "enable"),
                component_input_truth(engine, compiled, networks, index, "in"),
            )
            for index in switches
        )
        deps = tuple(sorted({truth for driver in drivers for truth in driver}))
        result.append(
            Recipe(
                target,
                "ORIGINAL_BUS",
                deps,
                2 * len(drivers),
                1,
                (network, drivers),
            )
        )
    return result


def minimal_dependency_sets(
    records: dict[frozenset[int], tuple[tuple[int, int], tuple[int, int]]]
) -> list[tuple[frozenset[int], tuple[tuple[int, int], tuple[int, int]]]]:
    ordered = sorted(records.items(), key=lambda item: (len(item[0]), sorted(item[0])))
    retained: list[tuple[frozenset[int], tuple[tuple[int, int], tuple[int, int]]]] = []
    for deps, drivers in ordered:
        if any(old_deps <= deps for old_deps, _ in retained):
            continue
        retained.append((deps, drivers))
    return retained


def minimal_driver_forms(rows: Iterable[tuple[int, int]]) -> list[tuple[int, int]]:
    """Keep dependency-minimal forms for one side of a disjoint driver class.

    For a fixed target and coverage, two valid ``(enable, data)`` forms have
    identical Boolean BUS behaviour, cost, and delay.  A form whose dependency
    set strictly contains another form's dependency set can therefore never be
    preferable when the opposite Switch is guaranteed to come from a disjoint
    form class.  Equal dependency sets retain the lexicographically first
    physical orientation.  This reduction must not be used when both Switches
    draw from the same class: the smaller form could equal the opposite driver,
    while the dominated physical orientation remains a valid distinct Switch.
    """

    by_deps: dict[frozenset[int], tuple[int, int]] = {}
    for row in set(rows):
        deps = frozenset(row)
        old = by_deps.get(deps)
        if old is None or row < old:
            by_deps[deps] = row
    ordered = sorted(by_deps.items(), key=lambda item: (len(item[0]), sorted(item[0]), item[1]))
    retained: list[tuple[int, int]] = []
    retained_deps: list[frozenset[int]] = []
    for deps, row in ordered:
        if any(old <= deps for old in retained_deps):
            continue
        retained_deps.append(deps)
        retained.append(row)
    return retained


def new_two_switch_recipes(
    universe: list[int], *, max_per_coverage: int = 8
) -> tuple[list[Recipe], dict[str, int]]:
    """枚举冲突安全、两个 driver 即可覆盖目标 1 集合的 BUS。"""

    result: list[Recipe] = []
    targets_with_recipe = 0
    raw_recipe_count = 0
    max_driver_forms_in_coverage = 0
    truncated_coverage_count = 0
    coverage_count = 0
    for target in universe:
        if target == 0:
            continue
        by_coverage: dict[int, list[tuple[int, int]]] = {}
        for enable in universe:
            if enable == target:
                # 会造成直接的正延迟自依赖；在函数 DAG 中没有用途。
                continue
            for data in universe:
                if data == target:
                    continue
                if enable & (data ^ target):
                    continue
                coverage = enable & data
                if not coverage:
                    continue
                rows = by_coverage.setdefault(coverage, [])
                pair = (enable, data)
                if pair not in rows:
                    rows.append(pair)
        # 对同一 coverage 只保留依赖去重后最简的少量 driver。不同表示仍可能
        # 因跨输出共享而有价值，不能只留一个。
        for coverage, rows in list(by_coverage.items()):
            rows.sort(key=lambda row: (len(set(row)), row))
            coverage_count += 1
            max_driver_forms_in_coverage = max(
                max_driver_forms_in_coverage, len(rows)
            )
            truncated_coverage_count += len(rows) > max_per_coverage
            by_coverage[coverage] = rows[:max_per_coverage]

        coverages = sorted(by_coverage, key=lambda value: value.bit_count(), reverse=True)
        records: dict[
            frozenset[int], tuple[tuple[int, int], tuple[int, int]]
        ] = {}
        for left_index, left_coverage in enumerate(coverages):
            missing = target & ~left_coverage
            for right_coverage in coverages[left_index:]:
                if missing & ~right_coverage:
                    continue
                for left_driver in by_coverage[left_coverage]:
                    for right_driver in by_coverage[right_coverage]:
                        if left_driver == right_driver:
                            continue
                        deps = frozenset((*left_driver, *right_driver))
                        if target in deps:
                            continue
                        drivers = tuple(sorted((left_driver, right_driver)))
                        old = records.get(deps)
                        if old is None or drivers < old:
                            records[deps] = drivers
        retained = minimal_dependency_sets(records)
        if retained:
            targets_with_recipe += 1
        raw_recipe_count += len(records)
        for deps, drivers in retained:
            result.append(
                Recipe(
                    target,
                    "BUS2",
                    tuple(sorted(deps)),
                    4,
                    1,
                    drivers,
                )
            )
    return result, {
        "targets_with_bus2": targets_with_recipe,
        "raw_dependency_sets": raw_recipe_count,
        "retained_bus2_recipes": len(result),
        "bus2_coverage_count": coverage_count,
        "max_driver_forms_in_any_coverage": max_driver_forms_in_coverage,
        "truncated_bus2_coverage_count": truncated_coverage_count,
        "bus2_enumeration_complete": truncated_coverage_count == 0,
    }


def new_targeted_mixed_two_switch_recipes(
    base_universe: list[int],
    expanded_enables: list[int],
    targets: list[int],
    *,
    max_per_coverage: int = 128,
) -> tuple[list[Recipe], dict[str, int | bool | str]]:
    """Enumerate an exact, targeted ``base driver + mixed driver`` BUS class.

    The first Switch driver uses ``enable,data`` from ``base_universe``.  The
    second uses an enable from ``expanded_enables`` and data from
    ``base_universe``.  ``expanded_enables`` should contain only functions not
    already in the base set.  Both drivers are checked row-for-row against the
    target, so overlap can only drive the same Boolean value and is conflict
    free.  Only ``targets`` are produced; this deliberately avoids the
    unrestricted O(N^3) expanded-universe enumeration.

    Completeness in the returned metadata refers exactly to this declared
    driver/target class.  It is false if any dependency-minimal driver coverage
    is truncated by ``max_per_coverage``.
    """

    base = sorted(set(base_universe))
    base_set = set(base)
    new_enables = sorted(set(expanded_enables) - base_set)
    target_rows = sorted(set(targets))
    result: list[Recipe] = []
    targets_with_recipe = 0
    raw_recipe_count = 0
    base_coverage_count = 0
    mixed_coverage_count = 0
    candidate_expanded_enable_count = 0
    valid_mixed_driver_count = 0
    max_base_forms = 0
    max_mixed_forms = 0
    truncated_base_coverages = 0
    truncated_mixed_coverages = 0

    for target in target_rows:
        if target == 0:
            continue

        base_by_coverage: dict[int, list[tuple[int, int]]] = {}
        for enable in base:
            if enable == target:
                continue
            for data in base:
                if data == target or enable & (data ^ target):
                    continue
                coverage = enable & data
                if coverage:
                    base_by_coverage.setdefault(coverage, []).append((enable, data))

        for coverage, rows in list(base_by_coverage.items()):
            rows = minimal_driver_forms(rows)
            base_coverage_count += 1
            max_base_forms = max(max_base_forms, len(rows))
            truncated_base_coverages += len(rows) > max_per_coverage
            base_by_coverage[coverage] = rows[:max_per_coverage]

        if not base_by_coverage:
            continue

        # Only maximal base coverages are needed for the existence test below:
        # if none contains the missing 1-rows, no base driver can complement the
        # expanded-enable driver.  This filter is exact and usually removes the
        # vast majority of expanded enables before scanning base data forms.
        base_coverages = tuple(base_by_coverage)
        maximal_base_coverages = tuple(
            coverage
            for coverage in base_coverages
            if not any(
                coverage != other and not (coverage & ~other)
                for other in base_coverages
            )
        )

        mixed_by_coverage: dict[int, list[tuple[int, int]]] = {}
        for enable in new_enables:
            if enable == target:
                continue
            coverage = enable & target
            if not coverage:
                continue
            missing = target & ~coverage
            if not any(not (missing & ~base_coverage) for base_coverage in maximal_base_coverages):
                continue
            candidate_expanded_enable_count += 1
            for data in base:
                if data == target or enable & (data ^ target):
                    continue
                mixed_by_coverage.setdefault(coverage, []).append((enable, data))
                valid_mixed_driver_count += 1

        for coverage, rows in list(mixed_by_coverage.items()):
            rows = minimal_driver_forms(rows)
            mixed_coverage_count += 1
            max_mixed_forms = max(max_mixed_forms, len(rows))
            truncated_mixed_coverages += len(rows) > max_per_coverage
            mixed_by_coverage[coverage] = rows[:max_per_coverage]

        records: dict[
            frozenset[int], tuple[tuple[int, int], tuple[int, int]]
        ] = {}
        for mixed_coverage, mixed_drivers in mixed_by_coverage.items():
            missing = target & ~mixed_coverage
            for base_coverage, base_drivers in base_by_coverage.items():
                if missing & ~base_coverage:
                    continue
                for base_driver in base_drivers:
                    for mixed_driver in mixed_drivers:
                        if base_driver == mixed_driver:
                            continue
                        deps = frozenset((*base_driver, *mixed_driver))
                        if target in deps:
                            continue
                        drivers = tuple(sorted((base_driver, mixed_driver)))
                        old = records.get(deps)
                        if old is None or drivers < old:
                            records[deps] = drivers

        retained = minimal_dependency_sets(records)
        if retained:
            targets_with_recipe += 1
        raw_recipe_count += len(records)
        for deps, drivers in retained:
            result.append(
                Recipe(
                    target,
                    "BUS2_MIXED_ENABLE",
                    tuple(sorted(deps)),
                    4,
                    1,
                    drivers,
                )
            )

    truncated = truncated_base_coverages + truncated_mixed_coverages
    return result, {
        "mixed_bus2_scope": "one-base-driver+one-expanded-enable-base-data-driver",
        "mixed_bus2_target_count": len(target_rows),
        "mixed_bus2_expanded_enable_universe_count": len(new_enables),
        "mixed_bus2_targets_with_recipe": targets_with_recipe,
        "mixed_bus2_raw_dependency_sets": raw_recipe_count,
        "mixed_bus2_retained_recipes": len(result),
        "mixed_bus2_base_coverage_count": base_coverage_count,
        "mixed_bus2_coverage_count": mixed_coverage_count,
        "mixed_bus2_candidate_expanded_enable_count": candidate_expanded_enable_count,
        "mixed_bus2_valid_driver_count": valid_mixed_driver_count,
        "mixed_bus2_max_base_forms_in_any_coverage": max_base_forms,
        "mixed_bus2_max_expanded_forms_in_any_coverage": max_mixed_forms,
        "mixed_bus2_truncated_base_coverage_count": truncated_base_coverages,
        "mixed_bus2_truncated_expanded_coverage_count": truncated_mixed_coverages,
        "mixed_bus2_enumeration_complete": truncated == 0,
    }


def possible_candidates(
    recipes: list[Recipe], sources: set[int], delay_bound: int
) -> tuple[list[Candidate], dict[int, list[int]]]:
    candidates: list[Candidate] = []
    producers: dict[int, list[int]] = {}
    possible_by_depth: list[set[int]] = [set(sources)]
    for depth in range(1, delay_bound + 1):
        previous = possible_by_depth[-1]
        now = set(previous)
        for recipe_index, recipe in enumerate(recipes):
            if all(dep in previous for dep in recipe.deps):
                candidate_index = len(candidates)
                candidates.append(Candidate(recipe_index, depth))
                producers.setdefault(recipe.target, []).append(candidate_index)
                now.add(recipe.target)
        possible_by_depth.append(now)
    return candidates, producers


def solve(
    *,
    delay_bound: int,
    gate_bound: int,
    timeout_ms: int,
    include_new_bus2: bool,
    max_per_coverage: int,
    backend: str,
    solver_name: str,
    cost_encoding: str,
    cardinality_encoding: str,
) -> dict[str, object]:
    engine = load_engine()
    circuit, compiled, networks, component_outputs = engine.evaluate()
    del component_outputs
    sources = source_truths(engine, circuit, compiled, networks)
    outputs = output_truths(engine, circuit, compiled, networks)

    initial = {0, engine.ALL}
    for signal in networks.values():
        initial.update(signal.bits)
    universe_set = initial | {((~truth) & engine.ALL) for truth in initial}
    universe = sorted(universe_set)

    by_target = ordinary_recipes(universe, engine.ALL)
    original_buses = original_bus_recipes(engine, circuit, compiled, networks)
    for recipe in original_buses:
        add_recipe(by_target, recipe)

    bus2_stats = {
        "targets_with_bus2": 0,
        "raw_dependency_sets": 0,
        "retained_bus2_recipes": 0,
        "bus2_coverage_count": 0,
        "max_driver_forms_in_any_coverage": 0,
        "truncated_bus2_coverage_count": 0,
        "bus2_enumeration_complete": True,
    }
    if include_new_bus2:
        bus2, bus2_stats = new_two_switch_recipes(
            universe, max_per_coverage=max_per_coverage
        )
        for recipe in bus2:
            add_recipe(by_target, recipe)

    recipes = [
        recipe
        for target in universe
        for recipe in by_target.get(target, {}).values()
    ]
    active_recipe_indices, earliest = reachable_recipes(
        recipes, {truth: 0 for truth in sources}, delay_bound
    )
    producers: dict[int, list[int]] = {}
    for recipe_index in active_recipe_indices:
        producers.setdefault(recipes[recipe_index].target, []).append(recipe_index)

    started = time.monotonic()
    selected: list[int] = []
    declared_arrival: dict[int, int] = {}
    backend_meta: dict[str, object] = {}
    reason: str | None = None
    if backend == "pysat":
        status_text, selected, declared_arrival, backend_meta = pysat_select(
            recipes,
            active_recipe_indices,
            producers,
            earliest,
            {truth: 0 for truth in sources},
            outputs,
            delay_bound=delay_bound,
            gate_bound=gate_bound,
            timeout_ms=timeout_ms,
            solver_name=solver_name,
            cost_encoding=cost_encoding,
            cardinality_encoding=cardinality_encoding,
        )
    elif backend == "z3":
        # 备用审计后端；主搜索优先使用上面的 CaDiCaL/PB CNF。
        solver = z3.SolverFor("QF_FD")
        solver.set(timeout=timeout_ms)
        z3.set_param("memory_max_size", 1000)
        variables = {
            recipe_index: z3.Bool(f"x_{recipe_index}")
            for recipe_index in active_recipe_indices
        }
        truth_ids = {truth: index for index, truth in enumerate(universe)}
        arrivals = {
            (truth, depth): z3.Bool(f"a_{truth_ids[truth]}_{depth}")
            for truth in producers
            for depth in range(max(1, earliest[truth]), delay_bound + 1)
        }
        for truth, rows in producers.items():
            if len(rows) > 1:
                solver.add(z3.PbLe([(variables[index], 1) for index in rows], 1))
            arrival_rows = [
                arrivals[(truth, depth)]
                for depth in range(max(1, earliest[truth]), delay_bound + 1)
            ]
            solver.add(
                z3.Sum(*arrival_rows)
                == z3.Sum(*[variables[index] for index in rows])
            )
            if len(arrival_rows) > 1:
                solver.add(z3.PbLe([(row, 1) for row in arrival_rows], 1))

        def z3_available_before(truth: int, deadline: int):
            if truth in sources:
                return z3.BoolVal(True)
            rows = [
                arrivals[(truth, depth)]
                for depth in range(
                    max(1, earliest.get(truth, delay_bound + 1)), deadline + 1
                )
                if (truth, depth) in arrivals
            ]
            return z3.Or(*rows) if rows else z3.BoolVal(False)

        for recipe_index in active_recipe_indices:
            recipe = recipes[recipe_index]
            variable = variables[recipe_index]
            for target_depth in range(
                max(1, earliest[recipe.target]), delay_bound + 1
            ):
                target_arrival = arrivals[(recipe.target, target_depth)]
                for dep in recipe.deps:
                    solver.add(
                        z3.Implies(
                            z3.And(variable, target_arrival),
                            z3_available_before(
                                dep, target_depth - recipe.step_delay
                            ),
                        )
                    )
        for _name, truth in outputs:
            solver.add(z3.Or(*[variables[index] for index in producers.get(truth, ())]))
        solver.add(
            z3.PbLe(
                [
                    (variables[index], recipes[index].cost)
                    for index in active_recipe_indices
                ],
                gate_bound,
            )
        )
        status = solver.check()
        status_text = str(status)
        if status == z3.unknown:
            reason = solver.reason_unknown()
        elif status == z3.sat:
            model = solver.model()
            selected = [
                index
                for index, variable in variables.items()
                if z3.is_true(model.eval(variable, model_completion=True))
            ]
            declared_arrival = {
                truth: depth
                for (truth, depth), variable in arrivals.items()
                if z3.is_true(model.eval(variable, model_completion=True))
            }
        backend_meta = {"backend": "z3-qf-fd"}
    else:
        raise ValueError(f"unknown backend: {backend}")
    elapsed = time.monotonic() - started
    payload: dict[str, object] = {
        "schema": "hub79-global-function-map-v1",
        "status": status_text,
        "scope": "Hub79 scalar functions plus complements; ordinary gates, original BUS, optional new BUS2",
        "delay_bound": delay_bound,
        "gate_bound": gate_bound,
        "include_new_bus2": include_new_bus2,
        "max_driver_forms_per_coverage": max_per_coverage,
        "seconds": elapsed,
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "vectors": engine.ASSIGNMENTS,
        "universe_functions": len(universe),
        "source_functions": len(sources),
        "ordinary_recipe_count": sum(
            recipe.op in {"NOT", "AND", "OR", "NAND", "NOR"}
            for recipe in recipes
        ),
        "original_bus_recipe_count": sum(
            recipe.op == "ORIGINAL_BUS" for recipe in recipes
        ),
        **bus2_stats,
        "recipe_count": len(recipes),
        "candidate_count": len(active_recipe_indices),
        **backend_meta,
        "output_functions": [name for name, _truth in outputs],
        "proof_limit": (
            "UNSAT only applies to the finite Hub79-function universe and enumerated recipes; "
            "SAT is a constructive full truth-table upper bound."
        ),
    }
    if status_text != "sat":
        if reason is not None:
            payload["reason"] = reason
        return payload
    selected_by_truth = {
        recipes[index].target: index for index in selected
    }

    # 第二套直接重放：逐节点检查布尔函数与 BUS 冲突条件，并递归重算真实延迟。
    actual_arrival: dict[int, int] = {truth: 0 for truth in sources}
    unresolved = set(selected)
    rows = []
    conflict_free = True
    while unresolved:
        progress = False
        for index in tuple(unresolved):
            recipe = recipes[index]
            if not all(dep in actual_arrival for dep in recipe.deps):
                continue
            arrival = max((actual_arrival[dep] for dep in recipe.deps), default=0) + 1
            actual_arrival[recipe.target] = arrival
            if recipe.op == "NOT":
                replay = (~recipe.deps[0]) & engine.ALL
            elif recipe.op == "AND":
                replay = recipe.deps[0] & recipe.deps[1]
            elif recipe.op == "OR":
                replay = recipe.deps[0] | recipe.deps[1]
            elif recipe.op == "NAND":
                replay = (~(recipe.deps[0] & recipe.deps[1])) & engine.ALL
            elif recipe.op == "NOR":
                replay = (~(recipe.deps[0] | recipe.deps[1])) & engine.ALL
            elif recipe.op == "BUS2":
                drivers = recipe.detail
                ones = 0
                zeros = 0
                for enable, data in drivers:
                    ones |= enable & data
                    zeros |= enable & (~data & engine.ALL)
                conflict_free &= not bool(ones & zeros)
                replay = ones
            elif recipe.op == "ORIGINAL_BUS":
                _network, drivers = recipe.detail
                ones = 0
                zeros = 0
                for enable, data in drivers:
                    ones |= enable & data
                    zeros |= enable & (~data & engine.ALL)
                conflict_free &= not bool(ones & zeros)
                replay = ones
            else:
                raise RuntimeError(recipe.op)
            if replay != recipe.target:
                raise RuntimeError(f"recipe replay mismatch: {recipe.op}")
            rows.append(
                {
                    "function_sha256": digest(recipe.target, engine.ASSIGNMENTS // 8),
                    "op": recipe.op,
                    "dependency_sha256": [
                        digest(dep, engine.ASSIGNMENTS // 8) for dep in recipe.deps
                    ],
                    "cost": recipe.cost,
                    "declared_arrival": declared_arrival[recipe.target],
                    "actual_arrival": arrival,
                    "detail": (
                        {
                            "network": recipe.detail[0],
                            "drivers": [
                                [
                                    digest(enable, engine.ASSIGNMENTS // 8),
                                    digest(data, engine.ASSIGNMENTS // 8),
                                ]
                                for enable, data in recipe.detail[1]
                            ],
                        }
                        if recipe.op == "ORIGINAL_BUS"
                        else (
                            {
                                "drivers": [
                                    [
                                        digest(enable, engine.ASSIGNMENTS // 8),
                                        digest(data, engine.ASSIGNMENTS // 8),
                                    ]
                                    for enable, data in recipe.detail
                                ]
                            }
                            if recipe.op == "BUS2"
                            else None
                        )
                    ),
                }
            )
            unresolved.remove(index)
            progress = True
        if not progress:
            raise RuntimeError("selected model contains a dependency cycle")

    output_rows = []
    for name, truth in outputs:
        if truth not in actual_arrival:
            raise RuntimeError(f"missing output {name}")
        output_rows.append(
            {
                "name": name,
                "function_sha256": digest(truth, engine.ASSIGNMENTS // 8),
                "arrival": actual_arrival[truth],
                "producer_index": selected_by_truth.get(truth),
            }
        )
    actual_gate = sum(
        recipes[index].cost for index in selected
    )
    payload.update(
        {
            "actual_gate": actual_gate,
            "actual_delay": max(row["arrival"] for row in output_rows),
            "energy": actual_gate * max(row["arrival"] for row in output_rows),
            "selected_node_count": len(selected),
            "selected_op_histogram": {
                op: sum(
                    recipes[index].op == op
                    for index in selected
                )
                for op in sorted(
                    {
                        recipes[index].op
                        for index in selected
                    }
                )
            },
            "replay": {
                "all_selected_functions_exact": True,
                "all_bus_drivers_conflict_free": conflict_free,
                "all_outputs_present": True,
                "complete_truth_rows": engine.ASSIGNMENTS,
            },
            "outputs": output_rows,
            "selected_nodes": sorted(rows, key=lambda row: (row["actual_arrival"], row["function_sha256"])),
        }
    )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--delay", type=int, default=5)
    parser.add_argument("--gate", type=int, default=102)
    parser.add_argument("--timeout-ms", type=int, default=120_000)
    parser.add_argument("--without-new-bus2", action="store_true")
    parser.add_argument("--max-per-coverage", type=int, default=8)
    parser.add_argument("--backend", choices=("pysat", "z3"), default="pysat")
    parser.add_argument(
        "--solver",
        default="cadical195",
        help="PySAT solver name (for example cadical195, glucose4, or mergesat3)",
    )
    parser.add_argument(
        "--cost-encoding",
        choices=("grouped", "producer-tiered", "expanded"),
        default="grouped",
    )
    parser.add_argument(
        "--cardinality-encoding",
        choices=(
            "seqcounter",
            "cardnetwrk",
            "sortnetwrk",
            "totalizer",
            "mtotalizer",
            "kmtotalizer",
        ),
        default="seqcounter",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = solve(
        delay_bound=args.delay,
        gate_bound=args.gate,
        timeout_ms=args.timeout_ms,
        include_new_bus2=not args.without_new_bus2,
        max_per_coverage=args.max_per_coverage,
        backend=args.backend,
        solver_name=args.solver,
        cost_encoding=args.cost_encoding,
        cardinality_encoding=args.cardinality_encoding,
    )
    encoded = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(encoded, encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(args.output),
                "status": payload["status"],
                "gate": payload.get("actual_gate"),
                "delay": payload.get("actual_delay"),
                "energy": payload.get("energy"),
                "seconds": payload["seconds"],
                "recipes": payload["recipe_count"],
                "candidates": payload["candidate_count"],
                "sha256": hashlib.sha256(encoded.encode()).hexdigest(),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
