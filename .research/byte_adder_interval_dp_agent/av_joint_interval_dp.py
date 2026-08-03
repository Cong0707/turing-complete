"""A/V 区间状态下的 Byte Adder 联合 Sum/carry 精确选择。

状态定义：

``A = OR(G_i)`` 是区间中是否出现 generate；``V = F(1)`` 是区间在输入
carry=1 时的输出。对相邻 low/high 区间有：

    Aout = Ah OR Al
    Vout = Vh AND (Ah OR Vl)

因此 V 可以用两只同 data=Vh 的 Bit Switch 在一层产生，A 用一只 OR；该
``5 gate / 1 delay`` black cell 只有一条 resolved BUS，不存在跨 BUS driver
复用。实际 carry 同理为 ``V AND (A OR C)``，快速 gray cell 为 ``4/1``。

每位 Sum 壳同时产生 leaf A/V：G、K、P、L 各一只普通门，最后使用原生
XOR 原语（3 gate / 2 delay）形成 ``P xor C``，合计 7 gate/bit，即 56 门。

脚本只做离线结构求解和完整 2^17 packed truth 重放，不读取游戏存档、不启动
游戏。Cout 允许经游戏现有 Maker/Splitter 适配器把 Z-zero 变为主动 0；该适配器
成本和延迟均为零，和公开 Hub79 的 Cout 接法一致。
"""

from __future__ import annotations

import argparse
import hashlib
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


State = tuple[int, int]  # (A arrival, V arrival)
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


@dataclass(frozen=True, slots=True)
class AVTransfer:
    lo: int
    hi: int
    any_generate: int
    v: int
    recipe: str


def combine_state(low: State, high: State, mode: str) -> State:
    low_a, low_v = low
    high_a, high_v = high
    a = max(low_a, high_a) + 1
    if mode == "ordinary":
        v = max(high_v, max(high_a, low_v) + 1) + 1
    elif mode == "switch":
        v = max(high_a, high_v, low_v) + 1
    else:
        raise ValueError(mode)
    return a, v


def gray_arrival(state: State, carry_arrival: int, mode: str) -> int:
    any_generate, v = state
    if mode == "ordinary":
        return max(v, max(any_generate, carry_arrival) + 1) + 1
    if mode == "switch":
        return max(any_generate, v, carry_arrival) + 1
    raise ValueError(mode)


def enumerate_interval_states() -> tuple[
    dict[Interval, set[State]], dict[tuple[Interval, State], list[Recipe]]
]:
    states: dict[Interval, set[State]] = {}
    recipes: dict[tuple[Interval, State], list[Recipe]] = {}
    for bit in range(core.BITS):
        states[(bit, bit)] = {(1, 1)}
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
                            recipes.setdefault((interval, output), []).append(
                                Recipe(
                                    split,
                                    mode,
                                    low_state,
                                    high_state,
                                    output,
                                    cost,
                                )
                            )
                            values.add(output)
            states[interval] = values
    return states, recipes


def enumerate_carry_arrivals(
    interval_states: dict[Interval, set[State]], delay_limit: int
) -> tuple[list[set[int]], dict[tuple[int, int], list[CarryEdge]]]:
    arrivals: list[set[int]] = [{0}]
    edges: dict[tuple[int, int], list[CarryEdge]] = {}
    carry_deadline = delay_limit - 2
    for target in range(1, core.BITS + 1):
        target_values: set[int] = set()
        for predecessor in range(target):
            interval = (predecessor, target - 1)
            for predecessor_arrival in arrivals[predecessor]:
                for interval_state in interval_states[interval]:
                    for mode, cost in (("ordinary", 2), ("switch", 4)):
                        output = gray_arrival(
                            interval_state, predecessor_arrival, mode
                        )
                        # C0..C7 feed a 2-delay XOR. Cout only needs to meet the
                        # global deadline and may pass through a free Maker adapter.
                        deadline = carry_deadline if target < core.BITS else delay_limit
                        if output > deadline:
                            continue
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


def av_leaves(factory: core.Factory) -> tuple[list[AVTransfer], list[int]]:
    leaves: list[AVTransfer] = []
    propagates: list[int] = []
    for bit in range(core.BITS):
        a = factory.inputs[f"a{bit}"]
        b = factory.inputs[f"b{bit}"]
        generate = factory.gate("AND", a, b)
        kill = factory.gate("NOR", a, b)
        propagate = factory.gate("NOR", generate, kill)
        v = factory.gate("OR", a, b)
        leaves.append(AVTransfer(bit, bit, generate, v, f"bit{bit}"))
        propagates.append(propagate)
    return leaves, propagates


def combine_av(
    factory: core.Factory, low: AVTransfer, high: AVTransfer, mode: str
) -> AVTransfer:
    if low.hi + 1 != high.lo:
        raise ValueError("non-contiguous A/V combine")
    any_generate = factory.gate("OR", high.any_generate, low.any_generate)
    if mode == "ordinary":
        selector = factory.gate("OR", high.any_generate, low.v)
        v = factory.gate("AND", high.v, selector)
    elif mode == "switch":
        # Both physical drivers belong to this V BUS and have the same data.
        v = factory.bus(
            (
                (high.any_generate, high.v),
                (low.v, high.v),
            )
        )
    else:
        raise ValueError(mode)
    return AVTransfer(
        low.lo,
        high.hi,
        any_generate,
        v,
        f"{mode}({low.recipe},{high.recipe})",
    )


def gray_av(
    factory: core.Factory, carry: int, transfer: AVTransfer, mode: str
) -> int:
    if mode == "ordinary":
        selector = factory.gate("OR", transfer.any_generate, carry)
        return factory.gate("AND", transfer.v, selector)
    if mode == "switch":
        return factory.bus(
            (
                (transfer.any_generate, transfer.v),
                (carry, transfer.v),
            )
        )
    raise ValueError(mode)


def packed_verify(
    factory: core.Factory,
    outputs: tuple[int, ...],
    cout_adapter: bool,
) -> dict[str, object]:
    packed, report = factory.evaluate(outputs)
    if cout_adapter:
        # Maker2(in1=Cout) -> Splitter2(out1) preserves the Boolean value but
        # actively drives zero when the scalar source was Z. This is exactly the
        # public Hub79 output adapter and adds no scored gate/delay.
        report["cout_pre_adapter_z_count"] = (
            (~packed[outputs[-1]].driven) & core.ALL
        ).bit_count()
        report["z_assignment_count_by_output"][-1] = 0
        report["cout_adapter"] = "Maker2(in1)->Splitter2(out1), cost=0, delay=0"
    report["post_adapter_z_union_count"] = sum(
        1 for value in report["z_assignment_count_by_output"] if value
    )
    return report


def serialize_live_dag(
    factory: core.Factory, outputs: tuple[int, ...]
) -> dict[str, object]:
    """Serialize the exact scored DAG, including resolved BUS ownership."""

    live = sorted(factory.reachable(outputs))
    rows = []
    for index in live:
        node = factory.nodes[index]
        item: dict[str, object] = {
            "id": index,
            "op": node.op,
            "args": list(node.args),
            "cost": node.cost,
            "step_delay": node.step_delay,
            "arrival": node.arrival,
            "may_z": node.may_z,
            "label": node.label,
        }
        if node.op == "BUS":
            item["resolved_network"] = f"bus_node_{index}"
            item["drivers"] = [
                {
                    "enable": node.args[offset],
                    "data": node.args[offset + 1],
                    "owner": f"bus_node_{index}",
                }
                for offset in range(0, len(node.args), 2)
            ]
        rows.append(item)
    payload = {
        "outputs": list(outputs),
        "nodes": rows,
        "live_node_count": len(live),
    }
    payload["sha256"] = hashlib.sha256(
        json.dumps(payload, ensure_ascii=True, separators=(",", ":")).encode()
    ).hexdigest()
    return payload


def solve_delay(
    delay_limit: int,
    gate_bound: int | None,
    timeout_ms: int,
) -> tuple[core.Witness | None, dict[str, object]]:
    interval_states, recipes = enumerate_interval_states()
    carry_arrivals, carry_edges = enumerate_carry_arrivals(
        interval_states, delay_limit
    )
    if any(not values for values in carry_arrivals[1:]):
        return None, {"status": "unsat", "reason": "empty carry arrival state"}

    solver = z3.Solver()
    solver.set(timeout=timeout_ms)
    z3.set_param("memory_max_size", 900)

    interval_vars: dict[tuple[Interval, State], object] = {}
    recipe_vars: dict[tuple[Interval, State, int], object] = {}
    for interval, state_values in interval_states.items():
        if interval[0] == interval[1]:
            continue
        local_vars = []
        for state in sorted(state_values):
            state_var = z3.Bool(
                f"av_i_{delay_limit}_{interval[0]}_{interval[1]}_{state[0]}_{state[1]}"
            )
            interval_vars[(interval, state)] = state_var
            local_vars.append(state_var)
            choices = []
            for index, recipe in enumerate(recipes[(interval, state)]):
                choice = z3.Bool(
                    f"av_r_{delay_limit}_{interval[0]}_{interval[1]}_{state[0]}_{state[1]}_{index}"
                )
                recipe_vars[(interval, state, index)] = choice
                choices.append(choice)
                low_interval = (interval[0], recipe.split)
                high_interval = (recipe.split + 1, interval[1])
                if low_interval[0] < low_interval[1]:
                    solver.add(
                        z3.Implies(
                            choice,
                            interval_vars[(low_interval, recipe.low_state)],
                        )
                    )
                if high_interval[0] < high_interval[1]:
                    solver.add(
                        z3.Implies(
                            choice,
                            interval_vars[(high_interval, recipe.high_state)],
                        )
                    )
            solver.add(state_var == z3.Or(*choices))
            solver.add(z3.PbLe([(choice, 1) for choice in choices], 1))
        # One named implementation per interval. This is the precise family
        # boundary; several carries may fan out from the selected implementation.
        solver.add(z3.PbLe([(variable, 1) for variable in local_vars], 1))

    carry_vars: dict[tuple[int, int], object] = {(0, 0): z3.BoolVal(True)}
    edge_vars: dict[tuple[int, int, int], object] = {}
    edge_records: dict[tuple[int, int, int], CarryEdge] = {}
    for target in range(1, core.BITS + 1):
        target_choices = []
        for arrival in sorted(carry_arrivals[target]):
            carry_var = z3.Bool(f"av_c_{delay_limit}_{target}_{arrival}")
            carry_vars[(target, arrival)] = carry_var
            incoming = []
            for index, edge in enumerate(carry_edges[(target, arrival)]):
                key = (target, arrival, index)
                choice = z3.Bool(f"av_e_{delay_limit}_{target}_{arrival}_{index}")
                edge_vars[key] = choice
                edge_records[key] = edge
                incoming.append(choice)
                target_choices.append(choice)
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
        solver.add(z3.PbEq([(choice, 1) for choice in target_choices], 1))

    weighted = []
    for (interval, state, index), variable in recipe_vars.items():
        weighted.append((variable, recipes[(interval, state)][index].cost))
    for key, variable in edge_vars.items():
        weighted.append((variable, edge_records[key].cost))
    objective = z3.IntVal(56) + _pb_sum(weighted)
    if gate_bound is not None:
        solver.add(objective <= gate_bound)

    started = time.monotonic()
    status = solver.check()
    elapsed = time.monotonic() - started
    stats: dict[str, object] = {
        "status": str(status),
        "delay_bound": delay_limit,
        "gate_bound": gate_bound,
        "solve_seconds": elapsed,
        "interval_state_count": sum(len(value) for value in interval_states.values()),
        "interval_recipe_count": sum(len(value) for value in recipes.values()),
        "carry_state_counts": [len(value) for value in carry_arrivals],
        "carry_edge_count": sum(len(value) for value in carry_edges.values()),
        "family": "one named A/V interval implementation per interval",
    }
    if status != z3.sat:
        return None, stats
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
                raise RuntimeError(f"multiple edges selected for C{edge.target}")
            chosen_edges[edge.target] = edge

    factory = core.Factory()
    leaves, propagates = av_leaves(factory)
    materialized: dict[tuple[Interval, State], AVTransfer] = {}

    def materialize(interval: Interval, state: State) -> AVTransfer:
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
            result = combine_av(factory, low, high, recipe.mode)
        actual = (
            factory.nodes[result.any_generate].arrival,
            factory.nodes[result.v].arrival,
        )
        if actual != state:
            raise RuntimeError(f"A/V state mismatch {interval}: {actual} != {state}")
        materialized[key] = result
        return result

    carries = [factory.inputs["cin"]]
    edge_descriptions = []
    for target in range(1, core.BITS + 1):
        edge = chosen_edges[target]
        predecessor = carries[edge.predecessor]
        if factory.nodes[predecessor].arrival != edge.predecessor_arrival:
            raise RuntimeError(f"carry predecessor mismatch C{target}")
        transfer = materialize(edge.interval, edge.interval_state)
        carry = gray_av(factory, predecessor, transfer, edge.mode)
        if factory.nodes[carry].arrival != edge.output_arrival:
            raise RuntimeError(f"carry arrival mismatch C{target}")
        carries.append(carry)
        edge_descriptions.append(
            f"C{target}<-C{edge.predecessor}:{edge.mode}"
            f"[{edge.interval[0]},{edge.interval[1]}]@{edge.interval_state}"
        )

    sums = [
        factory.gate("XOR", propagates[bit], carries[bit])
        for bit in range(core.BITS)
    ]
    outputs = tuple([*sums, carries[-1]])
    witness = core.Witness(
        "av-joint-named-interval-dag",
        f"delay_bound={delay_limit};" + ";".join(edge_descriptions),
        outputs,
    )
    metrics = factory.structural_metrics(outputs)
    model_cost = model.eval(objective, model_completion=True).as_long()
    if int(metrics["gate"]) > model_cost:
        raise RuntimeError(
            f"materialized DAG exceeds PB ledger: {metrics['gate']} > {model_cost}"
        )
    semantic = packed_verify(factory, outputs, cout_adapter=True)
    if semantic["mismatch_union_count"] or semantic["conflict_assignment_count"]:
        raise RuntimeError(f"semantic verification failed: {semantic}")
    if any(semantic["z_assignment_count_by_output"]):
        raise RuntimeError(f"post-adapter output still Z: {semantic}")
    stats.update(
        {
            "model_gate": model_cost,
            "actual_gate": metrics["gate"],
            "actual_delay": metrics["delay"],
            "selected_interval_recipe_count": len(chosen_recipes),
            "selected_carry_edges": edge_descriptions,
            "semantic": semantic,
            "factory": factory,
        }
    )
    return witness, stats


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--delay", type=int, action="append", required=True)
    parser.add_argument("--gate", type=int)
    parser.add_argument("--timeout-ms", type=int, default=120_000)
    parser.add_argument(
        "--output",
        type=Path,
        default=HERE / "av_joint_interval_certificate.json",
    )
    args = parser.parse_args()

    runs = []
    witnesses = []
    for delay in dict.fromkeys(args.delay):
        witness, stats = solve_delay(delay, args.gate, args.timeout_ms)
        factory = stats.pop("factory", None)
        if witness is not None:
            assert isinstance(factory, core.Factory)
            metrics = factory.structural_metrics(witness.outputs)
            record = core.summarize_witness(factory, witness, metrics)
            # core verifier sees pre-adapter Cout Z; replace it with the explicit
            # adapter-aware semantic report already checked above.
            record["semantic"] = stats["semantic"]
            record["factory_dag"] = serialize_live_dag(factory, witness.outputs)
            witnesses.append(record)
        runs.append(stats)
        if stats["status"] == "unknown":
            break

    document = {
        "schema": "byte-adder-av-joint-named-interval-v1",
        "cost_model": {
            "ordinary_gate": [1, 1],
            "xor": [3, 2],
            "bit_switch_driver": [2, 1],
            "maker_splitter_z_adapter": [0, 0],
            "joint_sum_av_shell": 56,
        },
        "physical_rule": (
            "each fast A/V node owns exactly one resolved BUS; its two drivers "
            "have the same data and are not reused by another BUS"
        ),
        "test_domain": {
            "variables": core.VARIABLES,
            "rows": core.ASSIGNMENTS,
            "complete_u8_u8_u1": True,
        },
        "runs": runs,
        "witnesses": witnesses,
        "claims": {
            "named_av_interval_family_exact_if_sat_or_unsat": True,
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
                    for item in witnesses
                ],
                "output": str(args.output),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
