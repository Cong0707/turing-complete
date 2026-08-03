"""Enumerate conventional 8-bit adder frontiers in the current TC gate model.

This is a structural, technology-aware audit rather than a transistor estimate.
The model is pinned to current game observations:

* NOT/AND/NAND/OR/NOR: 1 gate, 1 delay;
* XOR/XNOR: 3 gates, 2 delay;
* Bit Switch: 2 gates, 1 delay (only used as a paired mux below);
* splitters, makers, wires, constants and level ports: free.

The half-adder preprocessing deliberately shares AND/NOR terms: producing both
P=A xor B and G=A and B costs three gates at depth two, not four gates.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import random
from typing import Iterable


HERE = Path(__file__).resolve().parent
N = 8


@dataclass(frozen=True)
class Node:
    op: str
    fanins: tuple[int, ...]
    gate: int
    delay: int
    name: str = ""


@dataclass(frozen=True)
class State:
    g: int
    p: int
    lo: int
    hi: int


class Net:
    def __init__(self) -> None:
        self.nodes: list[Node] = [Node("CONST0", (), 0, 0, "0"), Node("CONST1", (), 0, 0, "1")]
        self.cache: dict[tuple[object, ...], int] = {}
        self.inputs: dict[str, int] = {}

    def input(self, name: str) -> int:
        if name in self.inputs:
            return self.inputs[name]
        node = len(self.nodes)
        self.nodes.append(Node("INPUT", (), 0, 0, name))
        self.inputs[name] = node
        return node

    def _node(self, op: str, fanins: Iterable[int], gate: int = 1, delay: int = 1) -> int:
        fs = tuple(fanins)
        if op in {"AND", "NAND", "OR", "NOR", "XOR"}:
            fs = tuple(sorted(fs))
        key = (op, fs, gate, delay)
        if key in self.cache:
            return self.cache[key]
        node = len(self.nodes)
        self.nodes.append(Node(op, fs, gate, delay))
        self.cache[key] = node
        return node

    def not_(self, a: int) -> int:
        if a == 0:
            return 1
        if a == 1:
            return 0
        source = self.nodes[a]
        if source.op == "NOT":
            return source.fanins[0]
        return self._node("NOT", (a,))

    def and_(self, a: int, b: int) -> int:
        if 0 in {a, b}:
            return 0
        if a == 1:
            return b
        if b == 1 or a == b:
            return a
        return self._node("AND", (a, b))

    def or_(self, a: int, b: int) -> int:
        if 1 in {a, b}:
            return 1
        if a == 0:
            return b
        if b == 0 or a == b:
            return a
        return self._node("OR", (a, b))

    def nor(self, a: int, b: int) -> int:
        if a == 1 or b == 1:
            return 0
        if a == 0:
            return self.not_(b)
        if b == 0:
            return self.not_(a)
        return self._node("NOR", (a, b))

    def xor(self, a: int, b: int) -> int:
        if a == 0:
            return b
        if b == 0:
            return a
        if a == 1:
            return self.not_(b)
        if b == 1:
            return self.not_(a)
        if a == b:
            return 0
        return self._node("XOR", (a, b), gate=3, delay=2)

    def switch_mux(self, select: int, select_n: int, low: int, high: int) -> int:
        """Two mutually exclusive Bit Switches, with the inverse shared outside.

        The output is always driven.  Four gates are charged for the two
        switches and one delay after the latest enable/data input.
        """

        if low == high:
            return low
        return self._node("SWITCH_MUX", (select, select_n, low, high), gate=4, delay=1)

    def arrivals(self) -> list[int]:
        result: list[int] = []
        for node in self.nodes:
            if not node.fanins:
                result.append(0)
            else:
                result.append(max(result[x] for x in node.fanins) + node.delay)
        return result

    def reachable(self, outputs: Iterable[int]) -> set[int]:
        reached: set[int] = set()
        work = list(outputs)
        while work:
            node = work.pop()
            if node in reached:
                continue
            reached.add(node)
            work.extend(self.nodes[node].fanins)
        return reached

    def score(self, outputs: Iterable[int]) -> tuple[int, int, list[int], set[int]]:
        outs = list(outputs)
        reached = self.reachable(outs)
        arrivals = self.arrivals()
        gate = sum(self.nodes[node].gate for node in reached)
        output_arrivals = [arrivals[node] for node in outs]
        return gate, max(output_arrivals, default=0), output_arrivals, reached

    def evaluate(self, outputs: Iterable[int], values: dict[str, int]) -> list[int]:
        computed: list[int] = []
        for node in self.nodes:
            args = [computed[x] for x in node.fanins]
            if node.op == "CONST0":
                value = 0
            elif node.op == "CONST1":
                value = 1
            elif node.op == "INPUT":
                value = values[node.name]
            elif node.op == "NOT":
                value = 1 ^ args[0]
            elif node.op == "AND":
                value = args[0] & args[1]
            elif node.op == "NAND":
                value = 1 ^ (args[0] & args[1])
            elif node.op == "OR":
                value = args[0] | args[1]
            elif node.op == "NOR":
                value = 1 ^ (args[0] | args[1])
            elif node.op == "XOR":
                value = args[0] ^ args[1]
            elif node.op == "SWITCH_MUX":
                select, select_n, low, high = args
                if select == select_n:
                    raise AssertionError("switch mux controls are not complementary")
                value = high if select else low
            else:
                raise AssertionError(node.op)
            computed.append(value)
        return [computed[x] for x in outputs]


@dataclass
class Prepared:
    net: Net
    a: list[int]
    b: list[int]
    cin: int
    p: list[int]
    g: list[int]
    q: list[int]
    initial: list[State]

    @property
    def initial_with_cin(self) -> list[State]:
        # P=0 makes every cell whose low interval already contains cin a gray
        # cell automatically.  This is the standard dynamic-cin prefix trick.
        return [State(self.cin, 0, -1, -1), *self.initial]


def prepare() -> Prepared:
    net = Net()
    a = [net.input(f"a{i}") for i in range(N)]
    b = [net.input(f"b{i}") for i in range(N)]
    cin = net.input("cin")
    p: list[int] = []
    g: list[int] = []
    q: list[int] = []
    initial: list[State] = []
    for bit in range(N):
        gi = net.and_(a[bit], b[bit])
        qi = net.nor(a[bit], b[bit])
        pi = net.nor(qi, gi)
        g.append(gi)
        q.append(qi)
        p.append(pi)
        initial.append(State(gi, pi, bit, bit))
    return Prepared(net, a, b, cin, p, g, q, initial)


def combine(net: Net, high: State, low: State) -> State:
    if low.hi + 1 != high.lo:
        raise AssertionError((low, high))
    propagated_generate = net.and_(high.p, low.g)
    group_generate = net.or_(high.g, propagated_generate)
    group_propagate = net.and_(high.p, low.p)
    return State(group_generate, group_propagate, low.lo, high.hi)


def kogge_stone(prepared: Prepared) -> list[State]:
    states = prepared.initial
    distance = 1
    while distance < N:
        old = states
        states = [combine(prepared.net, old[i], old[i - distance]) if i >= distance else old[i] for i in range(N)]
        distance *= 2
    return states


def kogge_stone_integrated_cin(prepared: Prepared) -> list[State]:
    states = prepared.initial_with_cin
    distance = 1
    while distance < len(states):
        old = states
        states = [
            combine(prepared.net, old[i], old[i - distance]) if i >= distance else old[i]
            for i in range(len(states))
        ]
        distance *= 2
    assert [(state.lo, state.hi) for state in states] == [(-1, i - 1) for i in range(N + 1)]
    return states


def sklansky_integrated_cin(prepared: Prepared) -> list[State]:
    states = prepared.initial_with_cin
    distance = 1
    while distance < len(states):
        old = list(states)
        block = 2 * distance
        for start in range(0, len(states), block):
            root = start + distance - 1
            if root >= len(states):
                continue
            for index in range(start + distance, min(start + block, len(states))):
                states[index] = combine(prepared.net, old[index], old[root])
        distance *= 2
    assert [(state.lo, state.hi) for state in states] == [(-1, i - 1) for i in range(N + 1)]
    return states


def brent_kung_integrated_cin(prepared: Prepared) -> list[State]:
    # Brent-Kung on the first power-of-two prefix (cin + bits 0..6), followed
    # by one gray combine for bit 7.  This is the usual 9-leaf adaptation.
    states = prepared.initial_with_cin
    limit = 8
    distance = 1
    while distance < limit:
        old = list(states)
        for index in range(2 * distance - 1, limit, 2 * distance):
            states[index] = combine(prepared.net, old[index], old[index - distance])
        distance *= 2
    distance //= 4
    while distance >= 1:
        old = list(states)
        for index in range(3 * distance - 1, limit, 2 * distance):
            states[index] = combine(prepared.net, old[index], old[index - distance])
        distance //= 2
    states[8] = combine(prepared.net, states[8], states[7])
    assert [(state.lo, state.hi) for state in states] == [(-1, i - 1) for i in range(N + 1)]
    return states


def brent_kung(prepared: Prepared) -> list[State]:
    states = list(prepared.initial)
    distance = 1
    while distance < N:
        old = list(states)
        for index in range(2 * distance - 1, N, 2 * distance):
            states[index] = combine(prepared.net, old[index], old[index - distance])
        distance *= 2
    distance //= 4
    while distance >= 1:
        old = list(states)
        for index in range(3 * distance - 1, N, 2 * distance):
            states[index] = combine(prepared.net, old[index], old[index - distance])
        distance //= 2
    assert [(state.lo, state.hi) for state in states] == [(0, i) for i in range(N)]
    return states


def sklansky(prepared: Prepared) -> list[State]:
    states = list(prepared.initial)
    distance = 1
    while distance < N:
        old = list(states)
        block = 2 * distance
        for start in range(0, N, block):
            root = start + distance - 1
            for index in range(start + distance, min(start + block, N)):
                states[index] = combine(prepared.net, old[index], old[root])
        distance *= 2
    assert [(state.lo, state.hi) for state in states] == [(0, i) for i in range(N)]
    return states


def han_carlson(prepared: Prepared) -> list[State]:
    states = list(prepared.initial)
    old = list(states)
    for index in range(1, N, 2):
        states[index] = combine(prepared.net, old[index], old[index - 1])
    distance = 2
    while distance < N:
        old = list(states)
        for index in range(distance + 1, N, 2):
            states[index] = combine(prepared.net, old[index], old[index - distance])
        distance *= 2
    old = list(states)
    for index in range(2, N, 2):
        states[index] = combine(prepared.net, old[index], old[index - 1])
    assert [(state.lo, state.hi) for state in states] == [(0, i) for i in range(N)]
    return states


def serial_prefix(prepared: Prepared) -> list[State]:
    states = list(prepared.initial)
    for index in range(1, N):
        states[index] = combine(prepared.net, states[index], states[index - 1])
    return states


def finish_prefix(prepared: Prepared, states: list[State], local_mask: int) -> tuple[list[int], int]:
    """Finish a prefix network, optionally replacing selected carries by ripple cells."""

    net = prepared.net
    carries = [prepared.cin]
    sums: list[int] = []
    for bit, state in enumerate(states):
        prefix_carry = net.or_(state.g, net.and_(state.p, prepared.cin))
        if (local_mask >> bit) & 1:
            h = net.and_(prepared.p[bit], carries[bit])
            local_carry = net.or_(prepared.g[bit], h)
            n_or = net.nor(prepared.p[bit], carries[bit])
            sum_bit = net.nor(n_or, h)
            carries.append(local_carry)
            sums.append(sum_bit)
        else:
            carries.append(prefix_carry)
            sums.append(net.xor(prepared.p[bit], carries[bit]))
    return sums, carries[N]


def finish_integrated_prefix(prepared: Prepared, states: list[State], local_mask: int) -> tuple[list[int], int]:
    net = prepared.net
    carries = [prepared.cin]
    sums: list[int] = []
    for bit in range(N):
        prefix_carry = states[bit + 1].g
        if (local_mask >> bit) & 1:
            h = net.and_(prepared.p[bit], carries[bit])
            carries.append(net.or_(prepared.g[bit], h))
            sums.append(net.nor(net.nor(prepared.p[bit], carries[bit]), h))
        else:
            carries.append(prefix_carry)
            sums.append(net.xor(prepared.p[bit], carries[bit]))
    return sums, carries[N]


def ripple() -> tuple[Prepared, list[int], int]:
    prepared = prepare()
    return prepared, *finish_prefix(prepared, prepared.initial, (1 << N) - 1)


def carry_select(partition: tuple[int, ...]) -> tuple[Prepared, list[int], int]:
    if sum(partition) != N or min(partition) < 1:
        raise ValueError(partition)
    prepared = prepare()
    net = prepared.net

    def full_adder(bit: int, carry: int) -> tuple[int, int]:
        if carry == 0:
            return prepared.p[bit], prepared.g[bit]
        if carry == 1:
            # q|g = XNOR; a|b is the carry for an assumed carry-in of one.
            return net.or_(prepared.q[bit], prepared.g[bit]), net.or_(prepared.a[bit], prepared.b[bit])
        h = net.and_(prepared.p[bit], carry)
        return net.nor(net.nor(prepared.p[bit], carry), h), net.or_(prepared.g[bit], h)

    sums: list[int] = []
    carry = prepared.cin
    start = 0
    for block_index, width in enumerate(partition):
        if block_index == 0:
            for bit in range(start, start + width):
                sum_bit, carry = full_adder(bit, carry)
                sums.append(sum_bit)
        else:
            low_sums: list[int] = []
            high_sums: list[int] = []
            low_carry = 0
            high_carry = 1
            for bit in range(start, start + width):
                low_sum, low_carry = full_adder(bit, low_carry)
                high_sum, high_carry = full_adder(bit, high_carry)
                low_sums.append(low_sum)
                high_sums.append(high_sum)
            carry_n = net.not_(carry)
            sums.extend(
                net.switch_mux(carry, carry_n, low, high)
                for low, high in zip(low_sums, high_sums)
            )
            carry = net.switch_mux(carry, carry_n, low_carry, high_carry)
        start += width
    return prepared, sums, carry


def compositions(total: int, prefix: tuple[int, ...] = ()) -> Iterable[tuple[int, ...]]:
    if total == 0:
        yield prefix
        return
    for value in range(1, total + 1):
        yield from compositions(total - value, prefix + (value,))


def verify(prepared: Prepared, outputs: list[int], *, trials: int = 32) -> None:
    rng = random.Random(0xB17EADDE)
    vectors = [(a, b, cin) for a in range(4) for b in range(4) for cin in range(2)]
    vectors += [(rng.randrange(256), rng.randrange(256), rng.randrange(2)) for _ in range(trials)]
    for a, b, cin in vectors:
        values = {f"a{i}": (a >> i) & 1 for i in range(N)}
        values.update({f"b{i}": (b >> i) & 1 for i in range(N)})
        values["cin"] = cin
        actual_bits = prepared.net.evaluate(outputs, values)
        actual = sum(bit << index for index, bit in enumerate(actual_bits))
        expected = a + b + cin
        if actual != expected:
            raise AssertionError((a, b, cin, actual, expected))


def record(name: str, family: str, prepared: Prepared, sums: list[int], cout: int, detail: dict[str, object]) -> dict[str, object]:
    outputs = sums + [cout]
    gate, delay, arrivals, reached = prepared.net.score(outputs)
    verify(prepared, outputs)
    serial = [
        (node, prepared.net.nodes[node].op, prepared.net.nodes[node].fanins, prepared.net.nodes[node].gate, prepared.net.nodes[node].delay)
        for node in sorted(reached)
    ]
    digest = sha256(json.dumps(serial, separators=(",", ":")).encode()).hexdigest()
    return {
        "name": name,
        "family": family,
        "gate": gate,
        "delay": delay,
        "energy": gate * delay,
        "output_arrivals": {**{f"sum{bit}": arrivals[bit] for bit in range(N)}, "cout": arrivals[-1]},
        "reachable_nodes": len(reached),
        "structural_sha256": digest,
        "verification": "64 deterministic vectors plus prefix-interval invariants",
        **detail,
    }


def pareto(records: list[dict[str, object]]) -> list[dict[str, object]]:
    result = []
    for item in records:
        if any(
            other["gate"] <= item["gate"]
            and other["delay"] <= item["delay"]
            and (other["gate"], other["delay"]) != (item["gate"], item["delay"])
            for other in records
        ):
            continue
        result.append(item)
    return sorted(result, key=lambda item: (item["energy"], item["delay"], item["gate"], item["name"]))


def main() -> None:
    records: list[dict[str, object]] = []
    prepared, sums, cout = ripple()
    records.append(record("Ripple/shared full-adder", "ripple", prepared, sums, cout, {}))

    topologies = {
        "Serial prefix": serial_prefix,
        "Brent-Kung": brent_kung,
        "Kogge-Stone": kogge_stone,
        "Sklansky": sklansky,
        "Han-Carlson": han_carlson,
    }
    for topology_name, topology in topologies.items():
        for mask in range(1 << N):
            prepared = prepare()
            states = topology(prepared)
            sums, cout = finish_prefix(prepared, states, mask)
            records.append(
                record(
                    f"{topology_name}/local-{mask:02x}",
                    "prefix-hybrid",
                    prepared,
                    sums,
                    cout,
                    {"topology": topology_name, "local_ripple_mask": f"0x{mask:02x}"},
                )
            )

    integrated_topologies = {
        "Brent-Kung integrated-cin": brent_kung_integrated_cin,
        "Kogge-Stone integrated-cin": kogge_stone_integrated_cin,
        "Sklansky integrated-cin": sklansky_integrated_cin,
    }
    for topology_name, topology in integrated_topologies.items():
        for mask in range(1 << N):
            prepared = prepare()
            states = topology(prepared)
            sums, cout = finish_integrated_prefix(prepared, states, mask)
            records.append(
                record(
                    f"{topology_name}/local-{mask:02x}",
                    "integrated-cin-prefix-hybrid",
                    prepared,
                    sums,
                    cout,
                    {"topology": topology_name, "local_ripple_mask": f"0x{mask:02x}"},
                )
            )

    for partition in compositions(N):
        prepared, sums, cout = carry_select(partition)
        records.append(
            record(
                "Carry-select/" + "+".join(map(str, partition)),
                "carry-select",
                prepared,
                sums,
                cout,
                {"partition": list(partition)},
            )
        )

    # Keep the best realization for each family/gate/delay tuple in the compact table.
    unique: dict[tuple[str, int, int], dict[str, object]] = {}
    for item in records:
        key = (str(item["family"]), int(item["gate"]), int(item["delay"]))
        if key not in unique or str(item["name"]) < str(unique[key]["name"]):
            unique[key] = item
    compact = sorted(unique.values(), key=lambda item: (item["energy"], item["delay"], item["gate"], item["name"]))
    payload = {
        "schema": 1,
        "scope": "8-bit A+B+cin -> sum[7:0],cout; conventional gate/prefix/carry-select structures",
        "cost_model": {
            "NOT_AND_NAND_OR_NOR": [1, 1],
            "XOR_XNOR": [3, 2],
            "Bit_Switch": [2, 1],
            "paired_switch_mux": [4, 1],
            "shared_inverse_per_mux_bank": [1, 1],
            "free": ["wire", "splitter", "maker", "constant", "level I/O"],
        },
        "reference": {"native_com_add": {"gate": 103, "delay": 5, "energy": 515}},
        "enumerated_realization_count": len(records),
        "unique_family_cost_points": compact,
        "global_pareto": pareto(records),
        "strictly_below_515": [item for item in records if item["energy"] < 515],
        "best_energy": min(records, key=lambda item: (item["energy"], item["delay"], item["gate"])),
    }
    (HERE / "frontier.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "enumerated": len(records),
        "pareto": [(x["name"], x["gate"], x["delay"], x["energy"]) for x in payload["global_pareto"]],
        "best": (payload["best_energy"]["name"], payload["best_energy"]["gate"], payload["best_energy"]["delay"], payload["best_energy"]["energy"]),
        "below_515": len(payload["strictly_below_515"]),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
