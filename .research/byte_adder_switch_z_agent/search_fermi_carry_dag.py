"""搜索 Fermi Byte Adder Pareto 链的共享全加器/区间进位 DAG。

基线每位使用六个始终需要的普通门生成 G/P、相位项和 Sum；carry 可选共享的
本地 OR、普通区间 gray cell 或冲突安全的 Switch gray cell。区间 G/P 状态也可
使用普通 3/2 black cell 或 Switch 5/1 black cell。
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from functools import lru_cache
import hashlib
import json
from pathlib import Path


BITS = 8
OUTPUT = Path(__file__).with_name("fermi_carry_frontier.json")


@dataclass(frozen=True, slots=True)
class Node:
    op: str
    args: tuple[int, ...]
    cost: int
    delay: int
    arrival: int
    label: str = ""


@dataclass(frozen=True, slots=True)
class Transfer:
    lo: int
    hi: int
    g: int
    p: int
    recipe: str


@dataclass(frozen=True, slots=True)
class Partial:
    carries: tuple[int, ...]
    sums: tuple[int, ...]


class Factory:
    COMMUTATIVE = {"AND", "OR", "NAND", "NOR"}

    def __init__(self) -> None:
        self.nodes: list[Node] = []
        self.intern: dict[tuple[object, ...], int] = {}
        self.const0 = self._new(("CONST", 0), Node("CONST", (), 0, 0, 0, "0"))
        self.const1 = self._new(("CONST", 1), Node("CONST", (), 0, 0, 0, "1"))
        self.inputs: dict[str, int] = {}
        for bit in range(BITS):
            self.inputs[f"a{bit}"] = self.input(f"a{bit}")
            self.inputs[f"b{bit}"] = self.input(f"b{bit}")
        self.inputs["cin"] = self.input("cin")

    def _new(self, key: tuple[object, ...], node: Node) -> int:
        known = self.intern.get(key)
        if known is not None:
            return known
        index = len(self.nodes)
        self.nodes.append(node)
        self.intern[key] = index
        return index

    def input(self, name: str) -> int:
        return self._new(("INPUT", name), Node("INPUT", (), 0, 0, 0, name))

    def gate(self, op: str, left: int, right: int) -> int:
        if op in self.COMMUTATIVE and right < left:
            left, right = right, left
        if op == "AND":
            if self.const0 in {left, right}:
                return self.const0
            if left == self.const1:
                return right
            if right == self.const1 or left == right:
                return left
        elif op == "OR":
            if self.const1 in {left, right}:
                return self.const1
            if left == self.const0:
                return right
            if right == self.const0 or left == right:
                return left
        arrival = max(self.nodes[left].arrival, self.nodes[right].arrival) + 1
        return self._new((op, left, right), Node(op, (left, right), 1, 1, arrival))

    def bus2(self, enable0: int, data0: int, enable1: int, data1: int, tag: str) -> int:
        drivers = tuple(sorted(((enable0, data0), (enable1, data1))))
        arrival = max(
            max(self.nodes[enable].arrival, self.nodes[data].arrival) + 1
            for enable, data in drivers
        )
        args = tuple(item for driver in drivers for item in driver)
        return self._new(("BUS2", tag, *args), Node("BUS2", args, 4, 1, arrival, tag))

    @lru_cache(maxsize=None)
    def reachable(self, outputs: tuple[int, ...]) -> frozenset[int]:
        pending = list(outputs)
        seen: set[int] = set()
        while pending:
            node = pending.pop()
            if node in seen:
                continue
            seen.add(node)
            pending.extend(self.nodes[node].args)
        return frozenset(seen)

    def metrics(self, outputs: tuple[int, ...]) -> tuple[int, int, frozenset[int]]:
        live = self.reachable(outputs)
        gate = sum(self.nodes[node].cost for node in live)
        delay = max((self.nodes[node].arrival for node in outputs), default=0)
        return gate, delay, live

    def structural_hash(self, outputs: tuple[int, ...]) -> str:
        memo: dict[int, str] = {}

        def visit(index: int) -> str:
            known = memo.get(index)
            if known is not None:
                return known
            node = self.nodes[index]
            payload = [node.op, node.cost, node.delay, node.label]
            payload.extend(visit(arg) for arg in node.args)
            value = hashlib.sha256(json.dumps(payload, separators=(",", ":")).encode()).hexdigest()
            memo[index] = value
            return value

        return hashlib.sha256("".join(visit(node) for node in outputs).encode()).hexdigest()


class Search:
    def __init__(self, plan_limit: int = 24, beam: int = 30000) -> None:
        self.factory = Factory()
        self.plan_limit = plan_limit
        self.beam = beam
        self.g: list[int] = []
        self.p: list[int] = []
        for bit in range(BITS):
            a = self.factory.inputs[f"a{bit}"]
            b = self.factory.inputs[f"b{bit}"]
            generate = self.factory.gate("AND", a, b)
            kill = self.factory.gate("NOR", a, b)
            propagate = self.factory.gate("NOR", kill, generate)
            self.g.append(generate)
            self.p.append(propagate)
        self.transfers: dict[tuple[int, int], list[Transfer]] = {}
        self._build_transfers()

    def slow_combine(self, high: Transfer, low: Transfer) -> Transfer:
        propagated = self.factory.gate("AND", high.p, low.g)
        g = self.factory.gate("OR", high.g, propagated)
        p = self.factory.gate("AND", high.p, low.p)
        return Transfer(low.lo, high.hi, g, p, f"slow({high.recipe},{low.recipe})")

    def fast_combine(self, high: Transfer, low: Transfer) -> Transfer:
        g = self.factory.bus2(high.g, self.factory.const1, high.p, low.g, "gp-black")
        p = self.factory.gate("AND", high.p, low.p)
        return Transfer(low.lo, high.hi, g, p, f"fast({high.recipe},{low.recipe})")

    def _plan_score(self, transfer: Transfer) -> tuple[int, int, int]:
        gate, _delay, _live = self.factory.metrics((transfer.g, transfer.p))
        return gate, self.factory.nodes[transfer.g].arrival, self.factory.nodes[transfer.p].arrival

    def _prune_plans(self, values: list[Transfer]) -> list[Transfer]:
        unique: dict[tuple[int, int], Transfer] = {(item.g, item.p): item for item in values}
        scored = [(self._plan_score(item), item) for item in unique.values()]
        pareto: list[tuple[tuple[int, int, int], Transfer]] = []
        for score, item in sorted(scored, key=lambda pair: pair[0]):
            if any(
                old[0] <= score[0] and old[1] <= score[1] and old[2] <= score[2]
                for old, _ in pareto
            ):
                continue
            pareto.append((score, item))
        # Preserve several equal-metric trees because their subinterval nodes
        # can be shared by different carry shortcuts.
        by_metric: dict[tuple[int, int, int], list[Transfer]] = {}
        for score, item in scored:
            by_metric.setdefault(score, []).append(item)
        result: list[Transfer] = []
        for score, _item in pareto:
            result.extend(by_metric[score][: self.plan_limit])
        return result[: self.plan_limit]

    def _build_transfers(self) -> None:
        for bit in range(BITS):
            self.transfers[(bit, bit)] = [Transfer(bit, bit, self.g[bit], self.p[bit], f"b{bit}")]
        for length in range(2, BITS + 1):
            for lo in range(BITS - length + 1):
                hi = lo + length - 1
                values: list[Transfer] = []
                for split in range(lo, hi):
                    for low in self.transfers[(lo, split)]:
                        for high in self.transfers[(split + 1, hi)]:
                            values.append(self.slow_combine(high, low))
                            values.append(self.fast_combine(high, low))
                self.transfers[(lo, hi)] = self._prune_plans(values)

    def slow_carry(self, transfer: Transfer, carry: int) -> int:
        term = self.factory.gate("AND", transfer.p, carry)
        return self.factory.gate("OR", transfer.g, term)

    def fast_carry(self, transfer: Transfer, carry: int) -> int:
        return self.factory.bus2(
            transfer.g,
            self.factory.const1,
            transfer.p,
            carry,
            "gp-gray",
        )

    def sum_nodes(self, bit: int, carry: int) -> tuple[int, int]:
        term = self.factory.gate("AND", self.p[bit], carry)
        phase = self.factory.gate("NOR", self.p[bit], carry)
        summation = self.factory.gate("NOR", phase, term)
        return summation, term

    def _candidate_carries(self, partial: Partial, bit: int, local_term: int) -> list[int]:
        candidates = {self.factory.gate("OR", self.g[bit], local_term)}
        for lo in range(bit + 1):
            carry = partial.carries[lo]
            for transfer in self.transfers[(lo, bit)]:
                candidates.add(self.slow_carry(transfer, carry))
                candidates.add(self.fast_carry(transfer, carry))
        return list(candidates)

    def _partial_gate(self, partial: Partial) -> int:
        outputs = (*partial.sums, partial.carries[-1])
        return self.factory.metrics(outputs)[0]

    def _prune_partials(self, values: list[Partial], bit: int, target_gate: int) -> list[Partial]:
        unique: dict[tuple[tuple[int, ...], tuple[int, ...]], Partial] = {
            (item.carries, item.sums): item for item in values
        }
        scored = []
        remaining = BITS - (bit + 1)
        for item in unique.values():
            gate = self._partial_gate(item)
            # Every future sum needs its G/Q/P plus three phase/output gates.
            if gate + 6 * remaining > target_gate:
                continue
            carry_arrival = self.factory.nodes[item.carries[-1]].arrival
            max_sum = max((self.factory.nodes[node].arrival for node in item.sums), default=0)
            scored.append((gate, carry_arrival, max_sum, item))

        # Retain the best representatives per (current carry arrival, current
        # max output arrival), then fill a global beam by gate count.
        buckets: dict[tuple[int, int], list[tuple[int, Partial]]] = {}
        for gate, carry_arrival, max_sum, item in scored:
            buckets.setdefault((carry_arrival, max_sum), []).append((gate, item))
        retained: list[tuple[int, Partial]] = []
        per_bucket = max(32, self.beam // max(1, len(buckets)))
        for bucket in buckets.values():
            bucket.sort(key=lambda pair: pair[0])
            retained.extend(bucket[:per_bucket])
        retained.sort(key=lambda pair: pair[0])
        return [item for _gate, item in retained[: self.beam]]

    def run(self, delay_target: int, gate_target: int) -> dict[str, object]:
        partials = [Partial((self.factory.inputs["cin"],), ())]
        layer_counts = []
        for bit in range(BITS):
            next_values: list[Partial] = []
            carry_limit = delay_target if bit == BITS - 1 else delay_target - 2
            for partial in partials:
                summation, term = self.sum_nodes(bit, partial.carries[bit])
                if self.factory.nodes[summation].arrival > delay_target:
                    continue
                for carry in self._candidate_carries(partial, bit, term):
                    if self.factory.nodes[carry].arrival > carry_limit:
                        continue
                    next_values.append(
                        Partial(partial.carries + (carry,), partial.sums + (summation,))
                    )
            partials = self._prune_partials(next_values, bit, gate_target)
            layer_counts.append({"bit": bit, "generated": len(next_values), "retained": len(partials)})
            if not partials:
                break

        records = []
        for partial in partials:
            outputs = (*partial.sums, partial.carries[-1])
            gate, delay, live = self.factory.metrics(outputs)
            if gate <= gate_target and delay <= delay_target:
                records.append(
                    {
                        "gate": gate,
                        "delay": delay,
                        "energy": gate * delay,
                        "carry_arrivals": [self.factory.nodes[node].arrival for node in partial.carries],
                        "sum_arrivals": [self.factory.nodes[node].arrival for node in partial.sums],
                        "outputs": list(outputs),
                        "live_nodes": len(live),
                        "structural_sha256": self.factory.structural_hash(outputs),
                    }
                )
        records.sort(key=lambda item: (item["energy"], item["gate"], item["delay"]))
        return {
            "delay_target": delay_target,
            "gate_target": gate_target,
            "layer_counts": layer_counts,
            "witness_count": len(records),
            "best": records[:20],
        }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--beam", type=int, default=30000)
    parser.add_argument("--plan-limit", type=int, default=24)
    parser.add_argument("--delay", type=int, action="append")
    parser.add_argument("--gate", type=int)
    args = parser.parse_args()
    targets = {6: 88, 7: 79, 8: 74, 18: 56}
    delays = args.delay or [8, 7, 6]
    search = Search(plan_limit=args.plan_limit, beam=args.beam)
    results = [search.run(delay, args.gate if args.gate is not None else targets[delay]) for delay in delays]
    document = {
        "schema": "byte-adder-fermi-shared-carry-search-v1",
        "model": {
            "shared_full_adder_baseline": "56/18",
            "gp_slow_black": "3/2",
            "gp_fast_black": "5/1",
            "gp_slow_gray": "2/2",
            "gp_fast_gray": "4/1",
        },
        "plan_limit": args.plan_limit,
        "beam": args.beam,
        "results": results,
    }
    OUTPUT.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
