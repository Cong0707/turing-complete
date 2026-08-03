"""离散状态的 Byte Adder 命名区间 DAG 精确选择器。

旧模型把每个区间的到达时间保留为 Z3 整数，并在 Optimize 中递归嵌套
大量 If。这个版本先在 Python 中穷举所有可能的 ``(G arrival, P arrival)``
状态，再让 Z3 只选择有限个 recipe。每个连续区间至多物化一种状态和一种
recipe，因此多个 carry 可以真实共享同一棵命名区间 DAG。

脚本只做离线数学搜索，不读取或写入游戏存档，也不启动游戏。
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import z3

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import interval_dp as core  # noqa: E402


State = tuple[int, int]
Interval = tuple[int, int]


@dataclass(frozen=True, slots=True)
class Recipe:
    split: int
    mode: str
    low_state: State
    high_state: State
    output_state: State
    cost: int


@dataclass(frozen=True, slots=True)
class CarryEdge:
    target: int
    predecessor: int
    predecessor_arrival: int
    interval: Interval
    interval_state: State
    mode: str
    output_arrival: int
    cost: int


def combine_state(low: State, high: State, mode: str) -> State:
    low_g, low_p = low
    high_g, high_p = high
    if mode == "ordinary":
        term = max(high_p, low_g) + 1
        return max(high_g, term) + 1, max(high_p, low_p) + 1
    if mode == "switch":
        return max(high_g, high_p, low_g) + 1, max(high_p, low_p) + 1
    raise ValueError(mode)


def gray_arrival(interval_state: State, carry_arrival: int, mode: str) -> int:
    generate, propagate = interval_state
    if mode == "ordinary":
        return max(generate, max(propagate, carry_arrival) + 1) + 1
    if mode == "switch":
        return max(generate, propagate, carry_arrival) + 1
    raise ValueError(mode)


def enumerate_interval_states() -> tuple[
    dict[Interval, set[State]], dict[tuple[Interval, State], list[Recipe]]
]:
    states: dict[Interval, set[State]] = {}
    recipes: dict[tuple[Interval, State], list[Recipe]] = {}
    for bit in range(core.BITS):
        states[(bit, bit)] = {(1, 2)}
    for length in range(2, core.BITS + 1):
        for lo in range(core.BITS - length + 1):
            hi = lo + length - 1
            interval = (lo, hi)
            values: set[State] = set()
            for split in range(lo, hi):
                low_interval = (lo, split)
                high_interval = (split + 1, hi)
                for low_state in states[low_interval]:
                    for high_state in states[high_interval]:
                        for mode, cost in (("ordinary", 3), ("switch", 5)):
                            output = combine_state(low_state, high_state, mode)
                            recipe = Recipe(
                                split,
                                mode,
                                low_state,
                                high_state,
                                output,
                                cost,
                            )
                            recipes.setdefault((interval, output), []).append(recipe)
                            values.add(output)
            states[interval] = values
    return states, recipes


def enumerate_carry_arrivals(
    interval_states: dict[Interval, set[State]], delay_limit: int
) -> tuple[list[set[int]], dict[tuple[int, int], list[CarryEdge]]]:
    arrivals: list[set[int]] = [{0}]
    edges: dict[tuple[int, int], list[CarryEdge]] = {}
    for target in range(1, core.BITS + 1):
        target_values: set[int] = set()
        for predecessor in range(target):
            interval = (predecessor, target - 1)
            for predecessor_arrival in arrivals[predecessor]:
                for interval_state in interval_states[interval]:
                    for mode in ("ordinary", "switch"):
                        output = gray_arrival(interval_state, predecessor_arrival, mode)
                        if target < core.BITS and max(2, output) + 2 > delay_limit:
                            continue
                        if target == core.BITS and output > delay_limit:
                            continue
                        cost = 1 if mode == "ordinary" and predecessor == target - 1 else (
                            2 if mode == "ordinary" else 4
                        )
                        edge = CarryEdge(
                            target,
                            predecessor,
                            predecessor_arrival,
                            interval,
                            interval_state,
                            mode,
                            output,
                            cost,
                        )
                        edges.setdefault((target, output), []).append(edge)
                        target_values.add(output)
        arrivals.append(target_values)
    return arrivals, edges


def _pb_sum(weighted: Iterable[tuple[object, int]]) -> object:
    terms = [z3.If(variable, weight, 0) for variable, weight in weighted]
    return z3.Sum(*terms) if terms else z3.IntVal(0)


def solve_delay(
    delay_limit: int,
    gate_bound: int | None,
    timeout_ms: int,
) -> tuple[core.Witness | None, dict[str, object]]:
    interval_states, recipes = enumerate_interval_states()
    carry_arrivals, carry_edges = enumerate_carry_arrivals(interval_states, delay_limit)
    if any(not values for values in carry_arrivals[1:]):
        return None, {"status": "unsat", "reason": "empty carry arrival state"}

    solver = z3.Solver()
    solver.set(timeout=timeout_ms)
    z3.set_param("memory_max_size", 1500)

    interval_vars: dict[tuple[Interval, State], object] = {}
    recipe_vars: dict[tuple[Interval, State, int], object] = {}
    for interval, states in interval_states.items():
        if interval[0] == interval[1]:
            continue
        local_vars = []
        for state in sorted(states):
            state_var = z3.Bool(
                f"i_{delay_limit}_{interval[0]}_{interval[1]}_{state[0]}_{state[1]}"
            )
            interval_vars[(interval, state)] = state_var
            local_vars.append(state_var)
            variants = recipes[(interval, state)]
            choices = []
            for index, recipe in enumerate(variants):
                choice = z3.Bool(
                    f"r_{delay_limit}_{interval[0]}_{interval[1]}_{state[0]}_{state[1]}_{index}"
                )
                recipe_vars[(interval, state, index)] = choice
                choices.append(choice)
                low_interval = (interval[0], recipe.split)
                high_interval = (recipe.split + 1, interval[1])
                if low_interval[0] < low_interval[1]:
                    solver.add(
                        z3.Implies(choice, interval_vars[(low_interval, recipe.low_state)])
                    )
                if high_interval[0] < high_interval[1]:
                    solver.add(
                        z3.Implies(choice, interval_vars[(high_interval, recipe.high_state)])
                    )
            solver.add(state_var == z3.Or(*choices))
            solver.add(z3.PbLe([(choice, 1) for choice in choices], 1))
        solver.add(z3.PbLe([(variable, 1) for variable in local_vars], 1))

    carry_vars: dict[tuple[int, int], object] = {(0, 0): z3.BoolVal(True)}
    edge_vars: dict[tuple[int, int, int], object] = {}
    edge_records: dict[tuple[int, int, int], CarryEdge] = {}
    for target in range(1, core.BITS + 1):
        all_target_edges = []
        for arrival in sorted(carry_arrivals[target]):
            carry_var = z3.Bool(f"c_{delay_limit}_{target}_{arrival}")
            carry_vars[(target, arrival)] = carry_var
            incoming = []
            for index, edge in enumerate(carry_edges[(target, arrival)]):
                key = (target, arrival, index)
                choice = z3.Bool(f"e_{delay_limit}_{target}_{arrival}_{index}")
                edge_vars[key] = choice
                edge_records[key] = edge
                incoming.append(choice)
                all_target_edges.append(choice)
                solver.add(
                    z3.Implies(
                        choice,
                        carry_vars[(edge.predecessor, edge.predecessor_arrival)],
                    )
                )
                if edge.interval[0] < edge.interval[1]:
                    solver.add(
                        z3.Implies(
                            choice,
                            interval_vars[(edge.interval, edge.interval_state)],
                        )
                    )
            solver.add(carry_var == z3.Or(*incoming))
        solver.add(z3.PbEq([(choice, 1) for choice in all_target_edges], 1))

    weighted = []
    for (interval, state, index), variable in recipe_vars.items():
        weighted.append((variable, recipes[(interval, state)][index].cost))
    for key, variable in edge_vars.items():
        weighted.append((variable, edge_records[key].cost))
    objective = z3.IntVal(48) + _pb_sum(weighted)
    if gate_bound is not None:
        solver.add(objective <= gate_bound)

    started = time.monotonic()
    status = solver.check()
    elapsed = time.monotonic() - started
    base_stats: dict[str, object] = {
        "status": str(status),
        "delay_bound": delay_limit,
        "gate_bound": gate_bound,
        "solve_seconds": elapsed,
        "interval_state_count": sum(len(value) for value in interval_states.values()),
        "interval_recipe_count": sum(len(value) for value in recipes.values()),
        "carry_state_counts": [len(value) for value in carry_arrivals],
        "carry_edge_count": sum(len(value) for value in carry_edges.values()),
    }
    if status != z3.sat:
        return None, base_stats
    model = solver.model()

    chosen_recipes: dict[tuple[Interval, State], Recipe] = {}
    for key, variable in recipe_vars.items():
        if z3.is_true(model.eval(variable, model_completion=True)):
            interval, state, index = key
            chosen_recipes[(interval, state)] = recipes[(interval, state)][index]
    chosen_edges: dict[int, CarryEdge] = {}
    for key, variable in edge_vars.items():
        if z3.is_true(model.eval(variable, model_completion=True)):
            edge = edge_records[key]
            if edge.target in chosen_edges:
                raise RuntimeError(f"multiple carry edges for C{edge.target}")
            chosen_edges[edge.target] = edge
    if len(chosen_edges) != core.BITS:
        raise RuntimeError("incomplete carry edge model")

    factory = core.Factory()
    leaves = core.gp_leaves(factory)
    materialized: dict[tuple[Interval, State], core.Transfer] = {}

    def materialize(interval: Interval, state: State) -> core.Transfer:
        key = (interval, state)
        known = materialized.get(key)
        if known is not None:
            return known
        lo, hi = interval
        if lo == hi:
            result = leaves[lo]
        else:
            recipe = chosen_recipes[key]
            low = materialize((lo, recipe.split), recipe.low_state)
            high = materialize((recipe.split + 1, hi), recipe.high_state)
            result = core.combine_gp(factory, low, high, recipe.mode)
        actual = (factory.nodes[result.g].arrival, factory.nodes[result.p].arrival)
        if actual != state:
            raise RuntimeError(f"interval state mismatch {interval}: {actual} != {state}")
        materialized[key] = result
        return result

    carries = [factory.inputs["cin"]]
    edge_descriptions = []
    for target in range(1, core.BITS + 1):
        edge = chosen_edges[target]
        if factory.nodes[carries[edge.predecessor]].arrival != edge.predecessor_arrival:
            raise RuntimeError(f"carry predecessor arrival mismatch C{target}")
        transfer = materialize(edge.interval, edge.interval_state)
        carry = core.gray_gp(factory, carries[edge.predecessor], transfer, edge.mode)
        if factory.nodes[carry].arrival != edge.output_arrival:
            raise RuntimeError(f"carry output arrival mismatch C{target}")
        carries.append(carry)
        edge_descriptions.append(
            f"C{target}<-C{edge.predecessor}:{edge.mode}"
            f"[{edge.interval[0]},{edge.interval[1]}]@{edge.interval_state}"
        )
    sums = [core.sum_from_gp(factory, leaves[bit].p, carries[bit])[0] for bit in range(core.BITS)]
    outputs = tuple([*sums, carries[core.BITS]])
    witness = core.Witness(
        "discrete-named-shared-carry-interval-dag",
        f"delay_bound={delay_limit};" + ";".join(edge_descriptions),
        outputs,
    )
    metrics = factory.structural_metrics(outputs)
    model_cost = model.eval(objective, model_completion=True).as_long()
    if int(metrics["gate"]) > model_cost:
        raise RuntimeError(f"DAG gate exceeds PB ledger: {metrics['gate']} > {model_cost}")
    if int(metrics["delay"]) > delay_limit:
        raise RuntimeError(f"DAG delay exceeds bound: {metrics['delay']} > {delay_limit}")
    base_stats.update(
        {
            "model_gate": model_cost,
            "actual_gate": metrics["gate"],
            "actual_delay": metrics["delay"],
            "selected_interval_recipe_count": len(chosen_recipes),
            "selected_carry_edges": edge_descriptions,
        }
    )
    return witness, {**base_stats, "factory": factory}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--delay", type=int, action="append", required=True)
    parser.add_argument("--gate", type=int)
    parser.add_argument("--timeout-ms", type=int, default=120_000)
    parser.add_argument(
        "--output",
        type=Path,
        default=HERE / "discrete_named_interval_certificate.json",
    )
    args = parser.parse_args()

    records = []
    runs = []
    for delay in dict.fromkeys(args.delay):
        witness, stats = solve_delay(delay, args.gate, args.timeout_ms)
        factory = stats.pop("factory", None)
        if witness is not None:
            assert isinstance(factory, core.Factory)
            metrics = factory.structural_metrics(witness.outputs)
            records.append(core.summarize_witness(factory, witness, metrics))
        runs.append(stats)
        if stats["status"] == "unknown":
            break
    document = {
        "schema": "byte-adder-discrete-named-interval-v1",
        "cost_model": {
            "ordinary_gate": [1, 1],
            "xor_xnor": [3, 2],
            "bit_switch_driver": [2, 1],
            "fixed_gp_sum_shell_gate": 48,
        },
        "test_domain": {
            "variables": core.VARIABLES,
            "rows": core.ASSIGNMENTS,
            "complete_u8_u8_u1": True,
        },
        "runs": runs,
        "witnesses": records,
        "claims": {
            "named_interval_family_exact_if_status_sat_or_unsat": True,
            "global_boolean_lower_bound": False,
        },
    }
    args.output.write_text(
        json.dumps(document, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "runs": runs,
                "witnesses": [
                    {
                        "gate": item["gate"],
                        "delay": item["delay"],
                        "semantic": item["semantic"],
                    }
                    for item in records
                ],
                "output": str(args.output),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
