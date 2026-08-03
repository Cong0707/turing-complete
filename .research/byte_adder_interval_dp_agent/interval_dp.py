"""Exact structured carry-interval search for Turing Complete Byte Adder.

This is deliberately an offline mathematical model.  It never reads or writes
the live save and it does not launch the game.  Structural enumeration is done
without allocating truth tables; only final Pareto witnesses are expanded to
the complete 2^17 input domain.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Sequence


BITS = 8
VARIABLES = 17
ASSIGNMENTS = 1 << VARIABLES
ALL = (1 << ASSIGNMENTS) - 1


@dataclass(frozen=True, slots=True)
class Node:
    op: str
    args: tuple[int, ...]
    cost: int
    step_delay: int
    arrival: int
    may_z: bool
    label: str = ""


@dataclass(frozen=True, slots=True)
class PackedSignal:
    value: int
    driven: int
    conflict: int


@dataclass(frozen=True, slots=True)
class Transfer:
    lo: int
    hi: int
    g: int
    p: int
    recipe: str


@dataclass(frozen=True, slots=True)
class Witness:
    family: str
    detail: str
    outputs: tuple[int, ...]


class Factory:
    """Canonical structural DAG with the reviewed TC cost model."""

    COMMUTATIVE = {"AND", "OR", "NAND", "NOR", "XOR", "XNOR"}
    GATE_COST = {
        "NOT": (1, 1),
        "AND": (1, 1),
        "OR": (1, 1),
        "NAND": (1, 1),
        "NOR": (1, 1),
        "XOR": (3, 2),
        "XNOR": (3, 2),
    }

    def __init__(self) -> None:
        self.nodes: list[Node] = []
        self.intern: dict[tuple[object, ...], int] = {}
        self.const0 = self._new(("CONST", 0), Node("CONST", (), 0, 0, 0, False, "0"))
        self.const1 = self._new(("CONST", 1), Node("CONST", (), 0, 0, 0, False, "1"))
        self.inputs: dict[str, int] = {}
        for bit in range(BITS):
            self.inputs[f"a{bit}"] = self._input(f"a{bit}", bit)
            self.inputs[f"b{bit}"] = self._input(f"b{bit}", BITS + bit)
        self.inputs["cin"] = self._input("cin", 16)

    def _new(self, key: tuple[object, ...], node: Node) -> int:
        found = self.intern.get(key)
        if found is not None:
            return found
        result = len(self.nodes)
        self.nodes.append(node)
        self.intern[key] = result
        return result

    def _input(self, label: str, index: int) -> int:
        return self._new(
            ("INPUT", index), Node("INPUT", (), 0, 0, 0, False, label)
        )

    def gate(self, op: str, left: int, right: int | None = None) -> int:
        if op == "NOT":
            if left == self.const0:
                return self.const1
            if left == self.const1:
                return self.const0
            source = self.nodes[left]
            if source.op == "NOT":
                return source.args[0]
            args = (left,)
        else:
            if right is None:
                raise ValueError(f"{op} requires two arguments")
            if op in self.COMMUTATIVE and right < left:
                left, right = right, left
            if op == "AND":
                if left == self.const0 or right == self.const0:
                    return self.const0
                if left == self.const1:
                    return right
                if right == self.const1 or left == right:
                    return left
            elif op == "OR":
                if left == self.const1 or right == self.const1:
                    return self.const1
                if left == self.const0:
                    return right
                if right == self.const0 or left == right:
                    return left
            elif op == "NAND":
                if left == self.const0 or right == self.const0:
                    return self.const1
                if left == self.const1:
                    return self.gate("NOT", right)
                if right == self.const1 or left == right:
                    return self.gate("NOT", left)
            elif op == "NOR":
                if left == self.const1 or right == self.const1:
                    return self.const0
                if left == self.const0:
                    return self.gate("NOT", right)
                if right == self.const0 or left == right:
                    return self.gate("NOT", left)
            elif op == "XOR":
                if left == right:
                    return self.const0
                if left == self.const0:
                    return right
                if right == self.const0:
                    return left
                if left == self.const1:
                    return self.gate("NOT", right)
                if right == self.const1:
                    return self.gate("NOT", left)
            elif op == "XNOR":
                if left == right:
                    return self.const1
                if left == self.const0:
                    return self.gate("NOT", right)
                if right == self.const0:
                    return self.gate("NOT", left)
                if left == self.const1:
                    return right
                if right == self.const1:
                    return left
            args = (left, right)
        cost, delay = self.GATE_COST[op]
        arrival = max(self.nodes[arg].arrival for arg in args) + delay
        return self._new(
            (op, *args), Node(op, args, cost, delay, arrival, False)
        )

    def bus(self, drivers: Iterable[tuple[int, int]]) -> int:
        unique = sorted(set(drivers))
        unique = [pair for pair in unique if pair[0] != self.const0]
        if not unique:
            return self._new(("BUS",), Node("BUS", (), 0, 0, 0, True, "Z"))
        if len(unique) == 1 and unique[0][0] == self.const1:
            return unique[0][1]
        flat = tuple(item for pair in unique for item in pair)
        arrival = max(
            max(self.nodes[enable].arrival, self.nodes[data].arrival) + 1
            for enable, data in unique
        )
        return self._new(
            ("BUS", *flat),
            Node("BUS", flat, 2 * len(unique), 1, arrival, True),
        )

    def force_driven(self, node: int) -> int:
        if not self.nodes[node].may_z:
            return node
        return self.gate("OR", node, self.const0)

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

    def structural_metrics(self, outputs: tuple[int, ...]) -> dict[str, object]:
        live = self.reachable(outputs)
        gate = sum(self.nodes[index].cost for index in live)
        arrivals = [self.nodes[index].arrival for index in outputs]
        return {
            "gate": gate,
            "delay": max(arrivals, default=0),
            "energy": gate * max(arrivals, default=0),
            "output_arrivals": arrivals,
            "reachable_nodes": len(live),
            "structural_sha256": self.structural_hash(outputs),
        }

    def structural_hash(self, outputs: tuple[int, ...]) -> str:
        memo: dict[int, str] = {}

        def visit(index: int) -> str:
            if index in memo:
                return memo[index]
            node = self.nodes[index]
            payload = [node.op, node.label, node.cost, node.step_delay]
            payload.extend(visit(arg) for arg in node.args)
            result = hashlib.sha256(
                json.dumps(payload, ensure_ascii=True, separators=(",", ":")).encode()
            ).hexdigest()
            memo[index] = result
            return result

        return hashlib.sha256("".join(visit(x) for x in outputs).encode()).hexdigest()

    @staticmethod
    def _variable(index: int) -> int:
        if index < 3:
            byte = (0xAA, 0xCC, 0xF0)[index]
            return int.from_bytes(bytes([byte]) * (ASSIGNMENTS // 8), "little")
        block = 1 << (index - 3)
        data = (bytes(block) + bytes([0xFF]) * block) * (
            ASSIGNMENTS // (16 * block)
        )
        return int.from_bytes(data, "little")

    def evaluate(self, outputs: tuple[int, ...]) -> tuple[dict[int, PackedSignal], dict[str, object]]:
        live = self.reachable(outputs)
        packed: dict[int, PackedSignal] = {}
        input_index = {
            self.inputs[f"a{bit}"]: bit for bit in range(BITS)
        } | {
            self.inputs[f"b{bit}"]: BITS + bit for bit in range(BITS)
        } | {self.inputs["cin"]: 16}

        def value(index: int) -> PackedSignal:
            found = packed.get(index)
            if found is not None:
                return found
            node = self.nodes[index]
            if node.op == "CONST":
                result = PackedSignal(ALL if node.label == "1" else 0, ALL, 0)
            elif node.op == "INPUT":
                result = PackedSignal(self._variable(input_index[index]), ALL, 0)
            elif node.op == "BUS":
                ones = 0
                zeros = 0
                driven = 0
                conflict = 0
                for offset in range(0, len(node.args), 2):
                    enable = value(node.args[offset])
                    data = value(node.args[offset + 1])
                    active = enable.value
                    ones |= active & data.value
                    zeros |= active & (~data.value & ALL)
                    driven |= active
                    conflict |= enable.conflict | data.conflict
                conflict |= ones & zeros
                result = PackedSignal(ones & ALL, driven & ALL, conflict & ALL)
            else:
                args = [value(arg) for arg in node.args]
                conflict = 0
                for arg in args:
                    conflict |= arg.conflict
                left = args[0].value
                right = args[1].value if len(args) == 2 else 0
                if node.op == "NOT":
                    output = ~left
                elif node.op == "AND":
                    output = left & right
                elif node.op == "OR":
                    output = left | right
                elif node.op == "NAND":
                    output = ~(left & right)
                elif node.op == "NOR":
                    output = ~(left | right)
                elif node.op == "XOR":
                    output = left ^ right
                elif node.op == "XNOR":
                    output = ~(left ^ right)
                else:
                    raise AssertionError(node.op)
                result = PackedSignal(output & ALL, ALL, conflict & ALL)
            packed[index] = result
            return result

        actual = [value(index) for index in outputs]
        variables = [self._variable(index) for index in range(VARIABLES)]
        carry = variables[16]
        expected: list[int] = []
        for bit in range(BITS):
            propagate = variables[bit] ^ variables[BITS + bit]
            expected.append(propagate ^ carry)
            carry = (variables[bit] & variables[BITS + bit]) | (propagate & carry)
        expected.append(carry)
        mismatch_masks = [signal.value ^ target for signal, target in zip(actual, expected)]
        conflict = 0
        for index in live:
            conflict |= value(index).conflict
        z_masks = [(~signal.driven) & ALL for signal in actual]
        digest_payload = b"".join(
            signal.value.to_bytes(ASSIGNMENTS // 8, "little") for signal in actual
        )
        report = {
            "truth_table_rows": ASSIGNMENTS,
            "mismatch_count_by_output": [mask.bit_count() for mask in mismatch_masks],
            "mismatch_union_count": _or_all(mismatch_masks).bit_count(),
            "conflict_assignment_count": conflict.bit_count(),
            "z_assignment_count_by_output": [mask.bit_count() for mask in z_masks],
            "output_vector_sha256": hashlib.sha256(digest_payload).hexdigest(),
        }
        return packed, report

    def arrival_path(self, output: int) -> list[dict[str, object]]:
        result: list[dict[str, object]] = []
        current = output
        while True:
            node = self.nodes[current]
            result.append(
                {
                    "node": current,
                    "op": node.op,
                    "label": node.label,
                    "arrival": node.arrival,
                    "step_delay": node.step_delay,
                }
            )
            if not node.args:
                break
            if node.op == "BUS":
                pairs = [node.args[i : i + 2] for i in range(0, len(node.args), 2)]
                current = max(
                    (arg for pair in pairs for arg in pair),
                    key=lambda arg: self.nodes[arg].arrival,
                )
            else:
                current = max(node.args, key=lambda arg: self.nodes[arg].arrival)
        result.reverse()
        return result


def _or_all(values: Iterable[int]) -> int:
    result = 0
    for value in values:
        result |= value
    return result


def gp_leaves(factory: Factory) -> list[Transfer]:
    result = []
    for bit in range(BITS):
        a = factory.inputs[f"a{bit}"]
        b = factory.inputs[f"b{bit}"]
        g = factory.gate("AND", a, b)
        k = factory.gate("NOR", a, b)
        p = factory.gate("NOR", g, k)
        result.append(Transfer(bit, bit, g, p, f"bit{bit}"))
    return result


def combine_gp(factory: Factory, low: Transfer, high: Transfer, mode: str) -> Transfer:
    if low.hi + 1 != high.lo:
        raise ValueError(f"non-contiguous combine {low.lo}:{low.hi} + {high.lo}:{high.hi}")
    if mode == "ordinary":
        g = factory.gate("OR", high.g, factory.gate("AND", high.p, low.g))
    elif mode == "switch":
        g = factory.bus(((high.g, factory.const1), (high.p, low.g)))
    else:
        raise ValueError(mode)
    p = factory.gate("AND", high.p, low.p)
    return Transfer(
        low.lo,
        high.hi,
        g,
        p,
        f"{mode}({low.recipe},{high.recipe})",
    )


def gray_gp(factory: Factory, low_carry: int, high: Transfer, mode: str) -> int:
    if mode == "ordinary":
        return factory.gate("OR", high.g, factory.gate("AND", high.p, low_carry))
    if mode == "switch":
        return factory.bus(((high.g, factory.const1), (high.p, low_carry)))
    raise ValueError(mode)


def prefix_schedule(name: str, count: int) -> list[list[tuple[int, int]]]:
    levels: list[list[tuple[int, int]]] = []
    if name == "serial":
        for target in range(1, count):
            levels.append([(target, target - 1)])
        return levels
    if name == "kogge-stone":
        distance = 1
        while distance < count:
            levels.append([(target, target - distance) for target in range(distance, count)])
            distance *= 2
        return levels
    if name == "sklansky":
        distance = 1
        while distance < count:
            operations: list[tuple[int, int]] = []
            for start in range(0, count, 2 * distance):
                source = start + distance - 1
                for target in range(start + distance, min(start + 2 * distance, count)):
                    operations.append((target, source))
            levels.append(operations)
            distance *= 2
        return levels
    if name == "brent-kung":
        distance = 1
        while distance < count:
            operations = [
                (target, target - distance)
                for target in range(2 * distance - 1, count, 2 * distance)
            ]
            if operations:
                levels.append(operations)
            distance *= 2
        distance //= 4
        while distance >= 1:
            operations = [
                (target, target - distance)
                for target in range(3 * distance - 1, count, 2 * distance)
            ]
            if operations:
                levels.append(operations)
            distance //= 2
        return levels
    raise ValueError(name)


def schedule_cell_count(schedule: Sequence[Sequence[tuple[int, int]]]) -> int:
    return sum(len(level) for level in schedule)


def build_integrated_prefix(
    factory: Factory,
    leaves: Sequence[Transfer],
    topology: str,
    mode_bits: int,
) -> Witness:
    cin = factory.inputs["cin"]
    states = [Transfer(-1, -1, cin, factory.const0, "cin"), *leaves]
    cell = 0
    for level in prefix_schedule(topology, len(states)):
        before = list(states)
        for target, source in level:
            mode = "switch" if (mode_bits >> cell) & 1 else "ordinary"
            states[target] = combine_gp(factory, before[source], before[target], mode)
            cell += 1
    for index, state in enumerate(states):
        if state.lo != -1 or state.hi != index - 1:
            raise AssertionError(
                f"{topology} failed prefix invariant at {index}: {state.lo}:{state.hi}"
            )
    sums = [factory.gate("XOR", leaves[bit].p, states[bit].g) for bit in range(BITS)]
    cout = factory.force_driven(states[BITS].g)
    return Witness(
        family=f"integrated-prefix/{topology}",
        detail=f"mode_mask=0x{mode_bits:x}",
        outputs=tuple([*sums, cout]),
    )


def build_shared_ripple(factory: Factory) -> Witness:
    carry = factory.inputs["cin"]
    sums: list[int] = []
    for bit in range(BITS):
        incoming = carry
        a = factory.inputs[f"a{bit}"]
        b = factory.inputs[f"b{bit}"]
        n = factory.gate("NAND", a, b)
        v = factory.gate("OR", a, b)
        p = factory.gate("AND", n, v)
        t = factory.gate("NAND", incoming, p)
        carry = factory.gate("NAND", n, t)
        other = factory.gate("OR", incoming, p)
        sums.append(factory.gate("AND", t, other))
    return Witness("ripple", "shared seven-gate full-adder chain", tuple([*sums, carry]))


def shared_full_adder(factory: Factory, bit: int, incoming: int) -> tuple[int, int]:
    a = factory.inputs[f"a{bit}"]
    b = factory.inputs[f"b{bit}"]
    n = factory.gate("NAND", a, b)
    v = factory.gate("OR", a, b)
    p = factory.gate("AND", n, v)
    t = factory.gate("NAND", incoming, p)
    carry = factory.gate("NAND", n, t)
    other = factory.gate("OR", incoming, p)
    return factory.gate("AND", t, other), carry


def ripple_block(factory: Factory, start: int, length: int, incoming: int) -> tuple[tuple[int, ...], int]:
    sums: list[int] = []
    carry = incoming
    for bit in range(start, start + length):
        total, carry = shared_full_adder(factory, bit, carry)
        sums.append(total)
    return tuple(sums), carry


def select_generic(
    factory: Factory, selector: int, inverse: int, when_zero: int, when_one: int, mode: str
) -> int:
    if mode == "ordinary":
        return factory.gate(
            "OR",
            factory.gate("AND", inverse, when_zero),
            factory.gate("AND", selector, when_one),
        )
    if mode == "switch":
        return factory.bus(((inverse, when_zero), (selector, when_one)))
    raise ValueError(mode)


def select_monotone(
    factory: Factory, selector: int, when_zero: int, when_one: int, mode: str
) -> int:
    """Select C0/C1 under the invariant C0 implies C1."""

    if mode == "ordinary":
        return factory.gate("OR", when_zero, factory.gate("AND", selector, when_one))
    if mode == "switch":
        # If both drivers are active, C0=1 implies C1=1, so they agree.
        return factory.bus(((when_zero, factory.const1), (selector, when_one)))
    raise ValueError(mode)


def ordered_partitions(total: int) -> list[tuple[int, ...]]:
    result: list[tuple[int, ...]] = []

    def visit(remaining: int, prefix: tuple[int, ...]) -> None:
        if remaining == 0:
            result.append(prefix)
            return
        for size in range(1, remaining + 1):
            visit(remaining - size, (*prefix, size))

    visit(total, ())
    return result


def build_carry_select(
    factory: Factory, partition: tuple[int, ...], mode_bits: int
) -> Witness:
    cin = factory.inputs["cin"]
    first_sums, carry = ripple_block(factory, 0, partition[0], cin)
    sums = list(first_sums)
    start = partition[0]
    for block_index, length in enumerate(partition[1:]):
        mode = "switch" if (mode_bits >> block_index) & 1 else "ordinary"
        sums0, carry0 = ripple_block(factory, start, length, factory.const0)
        sums1, carry1 = ripple_block(factory, start, length, factory.const1)
        inverse = factory.gate("NOT", carry)
        sums.extend(
            select_generic(factory, carry, inverse, zero, one, mode)
            for zero, one in zip(sums0, sums1)
        )
        carry = select_monotone(factory, carry, carry0, carry1, mode)
        start += length
    return Witness(
        "conditional-sum/ordered-partition",
        f"partition={'+'.join(map(str, partition))};mode_mask=0x{mode_bits:x}",
        tuple([*sums, factory.force_driven(carry)]),
    )


def transfer_tree_dp(factory: Factory, leaves: Sequence[Transfer]) -> tuple[dict[tuple[int, int], list[Transfer]], dict[str, int]]:
    """Exact local Pareto DP over all GP parenthesizations and cell modes."""

    table: dict[tuple[int, int], list[Transfer]] = {
        (leaf.lo, leaf.hi): [leaf] for leaf in leaves
    }
    generated = len(leaves)
    for length in range(2, BITS + 1):
        for lo in range(0, BITS - length + 1):
            hi = lo + length - 1
            candidates: list[Transfer] = []
            for split in range(lo, hi):
                for low in table[(lo, split)]:
                    for high in table[(split + 1, hi)]:
                        for mode in ("ordinary", "switch"):
                            candidates.append(combine_gp(factory, low, high, mode))
            generated += len(candidates)
            # Preserve every distinct witness on a nondominated local
            # (gate, G-arrival, P-arrival) point.  Equal points retain all
            # roots, so later multi-output selection can still exploit exact
            # structural sharing.
            groups: dict[tuple[int, int, int], dict[tuple[int, int], Transfer]] = {}
            for candidate in candidates:
                metrics = factory.structural_metrics((candidate.g, candidate.p))
                point = (
                        int(metrics["gate"]),
                        factory.nodes[candidate.g].arrival,
                        factory.nodes[candidate.p].arrival,
                )
                groups.setdefault(point, {})[(candidate.g, candidate.p)] = candidate
            points = list(groups)
            frontier_points = [
                point
                for point in points
                if not any(
                    other[0] <= point[0]
                    and other[1] <= point[1]
                    and other[2] <= point[2]
                    and other != point
                    for other in points
                )
            ]
            # Equal metric points retain every structurally distinct root so
            # the global stage can still exploit exact cross-output sharing.
            table[(lo, hi)] = [
                candidate
                for point in frontier_points
                for candidate in groups[point].values()
            ]
    return table, {
        "generated_transfer_plans": generated,
        "retained_transfer_plans": sum(len(value) for value in table.values()),
    }


@dataclass(frozen=True, slots=True)
class OutputOption:
    output: int
    mask: int
    detail: str


@dataclass(frozen=True, slots=True)
class CarryPlan:
    index: int
    node: int
    recipe: str


def _gate_mask(factory: Factory, output: int) -> int:
    result = 0
    for node in factory.reachable((output,)):
        if factory.nodes[node].cost:
            result |= 1 << node
    return result


def _prune_masks(states: dict[int, tuple[int, ...]]) -> dict[int, tuple[int, ...]]:
    """Remove exact set-supersets; all processed outputs are equivalent."""

    ordered = sorted(states, key=lambda mask: (mask.bit_count(), mask))
    kept: list[int] = []
    for mask in ordered:
        if any((other & mask) == other for other in kept):
            continue
        kept = [other for other in kept if (mask & other) != mask]
        kept.append(mask)
    return {mask: states[mask] for mask in kept}


def select_prefix_outputs(
    factory: Factory,
    leaves: Sequence[Transfer],
    transfer_dp: dict[tuple[int, int], list[Transfer]],
) -> tuple[list[Witness], dict[str, object]]:
    """Exact weighted-union DP with structural sharing across all outputs."""

    cin = factory.inputs["cin"]
    sum0 = factory.gate("XOR", leaves[0].p, cin)
    groups: list[list[OutputOption]] = []
    for carry_index in range(1, BITS + 1):
        options: dict[int, OutputOption] = {}
        for transfer in transfer_dp[(0, carry_index - 1)]:
            for mode in ("ordinary", "switch"):
                carry = gray_gp(factory, cin, transfer, mode)
                if carry_index < BITS:
                    output = factory.gate("XOR", leaves[carry_index].p, carry)
                else:
                    output = factory.force_driven(carry)
                options[output] = OutputOption(
                    output,
                    _gate_mask(factory, output),
                    f"c{carry_index}:{mode}:{transfer.recipe}",
                )
        groups.append(list(options.values()))

    witnesses: list[Witness] = []
    delay_runs: dict[str, object] = {}
    fixed_mask = _gate_mask(factory, sum0)
    try:
        import z3  # type: ignore[import-not-found]
    except ImportError as error:  # pragma: no cover - research environment guard
        raise RuntimeError("the exact weighted-union stage requires z3-solver") from error
    z3.set_param("memory_max_size", 900)
    for delay_limit in range(4, 19):
        if factory.nodes[sum0].arrival > delay_limit:
            continue
        filtered_groups = [
            [option for option in group if factory.nodes[option.output].arrival <= delay_limit]
            for group in groups
        ]
        if any(not group for group in filtered_groups):
            continue
        optimizer = z3.Optimize()
        choices = [
            [z3.Bool(f"d{delay_limit}_g{group_index}_o{option_index}") for option_index in range(len(group))]
            for group_index, group in enumerate(filtered_groups)
        ]
        for group_choices in choices:
            optimizer.add(z3.PbEq([(choice, 1) for choice in group_choices], 1))
        fixed_nodes = {
            index for index in range(len(factory.nodes)) if (fixed_mask >> index) & 1
        }
        node_users: dict[int, list[object]] = {}
        for group, group_choices in zip(filtered_groups, choices):
            for option, choice in zip(group, group_choices):
                mask = option.mask
                while mask:
                    low = mask & -mask
                    index = low.bit_length() - 1
                    if index not in fixed_nodes:
                        node_users.setdefault(index, []).append(choice)
                    mask ^= low
        fixed_cost = sum(factory.nodes[index].cost for index in fixed_nodes)
        objective_terms = [
            z3.If(z3.Or(*users), factory.nodes[index].cost, 0)
            for index, users in node_users.items()
        ]
        objective = z3.IntVal(fixed_cost) + z3.Sum(*objective_terms)
        optimizer.minimize(objective)
        if optimizer.check() != z3.sat:
            raise RuntimeError(f"weighted-union optimization failed at delay {delay_limit}")
        model = optimizer.model()
        selected: list[OutputOption] = []
        selected_indices: list[int] = []
        for group, group_choices in zip(filtered_groups, choices):
            true_indices = [
                index for index, choice in enumerate(group_choices) if z3.is_true(model.eval(choice, model_completion=True))
            ]
            if len(true_indices) != 1:
                raise RuntimeError(f"non-unique option selection at delay {delay_limit}")
            selected_indices.append(true_indices[0])
            selected.append(group[true_indices[0]])
        outputs = tuple([sum0, *(option.output for option in selected)])
        exact_metrics = factory.structural_metrics(outputs)
        optimized_cost = model.eval(objective).as_long()
        if int(exact_metrics["gate"]) != optimized_cost:
            raise RuntimeError(
                f"union objective mismatch: z3={optimized_cost}, DAG={exact_metrics['gate']}"
            )
        witnesses.append(
            Witness(
                "interval-transfer-dp",
                f"delay_bound={delay_limit};" + ";".join(option.detail for option in selected),
                outputs,
            )
        )
        delay_runs[str(delay_limit)] = {
            "option_counts": [len(group) for group in filtered_groups],
            "selected_option_indices": selected_indices,
            "minimum_union_gate": optimized_cost,
            "actual_delay": exact_metrics["delay"],
        }
    return witnesses, {"weighted_union_delay_runs": delay_runs}


def sum_from_gp(factory: Factory, propagate: int, carry: int) -> tuple[int, int]:
    """Three ordinary gates; the P&C term is shared with local ripple carry."""

    term = factory.gate("AND", propagate, carry)
    phase = factory.gate("NOR", propagate, carry)
    return factory.gate("NOR", phase, term), term


def _prune_carry_plans(factory: Factory, candidates: Iterable[CarryPlan]) -> list[CarryPlan]:
    unique: dict[int, CarryPlan] = {candidate.node: candidate for candidate in candidates}
    groups: dict[tuple[int, int], list[CarryPlan]] = {}
    for candidate in unique.values():
        metrics = factory.structural_metrics((candidate.node,))
        groups.setdefault(
            (int(metrics["gate"]), factory.nodes[candidate.node].arrival), []
        ).append(candidate)
    points = list(groups)
    frontier = [
        point
        for point in points
        if not any(
            other[0] <= point[0]
            and other[1] <= point[1]
            and other != point
            for other in points
        )
    ]
    return [candidate for point in frontier for candidate in groups[point]]


def build_carry_skip_plans(
    factory: Factory,
    leaves: Sequence[Transfer],
    transfer_dp: dict[tuple[int, int], list[Transfer]],
) -> tuple[list[list[CarryPlan]], dict[str, object]]:
    cin = factory.inputs["cin"]
    carries: list[list[CarryPlan]] = [[CarryPlan(0, cin, "cin")]]
    generated_counts = [1]
    retained_counts = [1]
    for index in range(1, BITS + 1):
        candidates: list[CarryPlan] = []
        for predecessor in range(index):
            for carry in carries[predecessor]:
                for transfer in transfer_dp[(predecessor, index - 1)]:
                    for mode in ("ordinary", "switch"):
                        node = gray_gp(factory, carry.node, transfer, mode)
                        candidates.append(
                            CarryPlan(
                                index,
                                node,
                                f"C{index}={mode}[{predecessor}:{index - 1}]({carry.recipe};{transfer.recipe})",
                            )
                        )
        generated_counts.append(len(candidates))
        carries.append(_prune_carry_plans(factory, candidates))
        retained_counts.append(len(carries[-1]))
    return carries, {
        "generated_carry_plan_counts": generated_counts,
        "retained_carry_plan_counts": retained_counts,
    }


def solve_carry_skip_outputs(
    factory: Factory,
    leaves: Sequence[Transfer],
    carries: Sequence[Sequence[CarryPlan]],
) -> tuple[list[Witness], dict[str, object]]:
    groups: list[list[OutputOption]] = []
    for bit in range(BITS):
        options: dict[int, OutputOption] = {}
        for carry in carries[bit]:
            output, _term = sum_from_gp(factory, leaves[bit].p, carry.node)
            options[output] = OutputOption(
                output,
                _gate_mask(factory, output),
                f"S{bit}<-{carry.recipe}",
            )
        groups.append(list(options.values()))
    groups.append(
        [
            OutputOption(carry.node, _gate_mask(factory, carry.node), carry.recipe)
            for carry in carries[BITS]
        ]
    )

    try:
        import z3  # type: ignore[import-not-found]
    except ImportError as error:  # pragma: no cover
        raise RuntimeError("carry-skip weighted-union stage requires z3-solver") from error
    z3.set_param("memory_max_size", 1500)
    witnesses: list[Witness] = []
    runs: dict[str, object] = {}
    for delay_limit in range(4, 19):
        filtered = [
            [option for option in group if factory.nodes[option.output].arrival <= delay_limit]
            for group in groups
        ]
        if any(not group for group in filtered):
            continue
        optimizer = z3.Optimize()
        choices = [
            [z3.Bool(f"skip_d{delay_limit}_g{gi}_o{oi}") for oi in range(len(group))]
            for gi, group in enumerate(filtered)
        ]
        for variables in choices:
            optimizer.add(z3.PbEq([(variable, 1) for variable in variables], 1))
        node_users: dict[int, list[object]] = {}
        for group, variables in zip(filtered, choices):
            for option, variable in zip(group, variables):
                mask = option.mask
                while mask:
                    low = mask & -mask
                    node = low.bit_length() - 1
                    node_users.setdefault(node, []).append(variable)
                    mask ^= low
        objective = z3.Sum(
            *[
                z3.If(z3.Or(*users), factory.nodes[node].cost, 0)
                for node, users in node_users.items()
            ]
        )
        optimizer.minimize(objective)
        if optimizer.check() != z3.sat:
            raise RuntimeError(f"carry-skip optimization failed at delay {delay_limit}")
        model = optimizer.model()
        selected: list[OutputOption] = []
        selected_indices: list[int] = []
        for group, variables in zip(filtered, choices):
            hits = [
                index
                for index, variable in enumerate(variables)
                if z3.is_true(model.eval(variable, model_completion=True))
            ]
            if len(hits) != 1:
                raise RuntimeError(f"carry-skip non-unique selection at delay {delay_limit}")
            selected_indices.append(hits[0])
            selected.append(group[hits[0]])
        outputs = tuple(option.output for option in selected)
        metrics = factory.structural_metrics(outputs)
        optimized = model.eval(objective).as_long()
        if int(metrics["gate"]) != optimized:
            raise RuntimeError(f"carry-skip objective mismatch z3={optimized} DAG={metrics['gate']}")
        witnesses.append(
            Witness(
                "carry-skip-interval-dp",
                f"delay_bound={delay_limit};" + ";".join(option.detail for option in selected),
                outputs,
            )
        )
        runs[str(delay_limit)] = {
            "option_counts": [len(group) for group in filtered],
            "selected_option_indices": selected_indices,
            "minimum_union_gate": optimized,
            "actual_delay": metrics["delay"],
        }
    return witnesses, {"weighted_union_delay_runs": runs}


def solve_named_interval_dag(
    factory: Factory,
    leaves: Sequence[Transfer],
    delay_limits: Iterable[int] = range(4, 19),
) -> tuple[list[Witness], dict[str, object]]:
    """Exact shared interval-DAG optimization under the reviewed GP macros.

    Every non-leaf interval has at most one selected implementation.  All
    carries may reuse that named interval and may jump from any earlier C_l.
    The 48-gate fixed shell is 8*(G/Q/P + T/N/S); a local one-bit slow gray
    shares T=P&C with Sum and therefore adds only its final OR.
    """

    try:
        import z3  # type: ignore[import-not-found]
    except ImportError as error:  # pragma: no cover
        raise RuntimeError("named interval DAG optimization requires z3-solver") from error
    z3.set_param("memory_max_size", 1500)
    intervals = [(lo, hi) for lo in range(BITS) for hi in range(lo, BITS)]
    nonleaves = [(lo, hi) for lo, hi in intervals if lo < hi]
    witnesses: list[Witness] = []
    runs: dict[str, object] = {}
    for delay_limit in delay_limits:
        optimizer = z3.Optimize()
        use = {interval: z3.Bool(f"named_d{delay_limit}_use_{interval[0]}_{interval[1]}") for interval in nonleaves}
        arrival_g = {interval: z3.Int(f"named_d{delay_limit}_ag_{interval[0]}_{interval[1]}") for interval in intervals}
        arrival_p = {interval: z3.Int(f"named_d{delay_limit}_ap_{interval[0]}_{interval[1]}") for interval in intervals}
        recipes: dict[tuple[int, int], list[tuple[int, str, object]]] = {}
        for bit in range(BITS):
            optimizer.add(arrival_g[(bit, bit)] == 1, arrival_p[(bit, bit)] == 2)
        interval_cost_terms = []
        for lo, hi in nonleaves:
            values: list[tuple[int, str, object]] = []
            for split in range(lo, hi):
                low = (lo, split)
                high = (split + 1, hi)
                for mode in ("ordinary", "switch"):
                    choice = z3.Bool(
                        f"named_d{delay_limit}_r_{lo}_{hi}_{split}_{mode}"
                    )
                    values.append((split, mode, choice))
                    if low[0] < low[1]:
                        optimizer.add(z3.Implies(choice, use[low]))
                    if high[0] < high[1]:
                        optimizer.add(z3.Implies(choice, use[high]))
                    if mode == "ordinary":
                        term = z3.If(
                            arrival_p[high] >= arrival_g[low],
                            arrival_p[high],
                            arrival_g[low],
                        ) + 1
                        g_value = z3.If(arrival_g[high] >= term, arrival_g[high], term) + 1
                        p_value = z3.If(
                            arrival_p[high] >= arrival_p[low],
                            arrival_p[high],
                            arrival_p[low],
                        ) + 1
                        cell_cost = 3
                    else:
                        high_max = z3.If(
                            arrival_g[high] >= arrival_p[high],
                            arrival_g[high],
                            arrival_p[high],
                        )
                        all_max = z3.If(high_max >= arrival_g[low], high_max, arrival_g[low])
                        g_value = all_max + 1
                        p_value = z3.If(
                            arrival_p[high] >= arrival_p[low],
                            arrival_p[high],
                            arrival_p[low],
                        ) + 1
                        cell_cost = 5
                    optimizer.add(
                        z3.Implies(choice, arrival_g[(lo, hi)] == g_value),
                        z3.Implies(choice, arrival_p[(lo, hi)] == p_value),
                    )
                    interval_cost_terms.append(z3.If(choice, cell_cost, 0))
            recipes[(lo, hi)] = values
            optimizer.add(
                z3.Sum(*[z3.If(choice, 1, 0) for _split, _mode, choice in values])
                == z3.If(use[(lo, hi)], 1, 0)
            )

        carry_arrival = [z3.Int(f"named_d{delay_limit}_c{index}") for index in range(BITS + 1)]
        optimizer.add(carry_arrival[0] == 0)
        edge_choices: dict[int, list[tuple[int, str, object]]] = {}
        edge_cost_terms = []
        for target in range(1, BITS + 1):
            values = []
            for predecessor in range(target):
                interval = (predecessor, target - 1)
                for mode in ("ordinary", "switch"):
                    choice = z3.Bool(
                        f"named_d{delay_limit}_e_{target}_{predecessor}_{mode}"
                    )
                    values.append((predecessor, mode, choice))
                    if interval[0] < interval[1]:
                        optimizer.add(z3.Implies(choice, use[interval]))
                    if mode == "ordinary":
                        term = z3.If(
                            arrival_p[interval] >= carry_arrival[predecessor],
                            arrival_p[interval],
                            carry_arrival[predecessor],
                        ) + 1
                        result_arrival = z3.If(
                            arrival_g[interval] >= term,
                            arrival_g[interval],
                            term,
                        ) + 1
                        edge_cost = 1 if predecessor == target - 1 else 2
                    else:
                        gp_max = z3.If(
                            arrival_g[interval] >= arrival_p[interval],
                            arrival_g[interval],
                            arrival_p[interval],
                        )
                        result_arrival = z3.If(
                            gp_max >= carry_arrival[predecessor],
                            gp_max,
                            carry_arrival[predecessor],
                        ) + 1
                        edge_cost = 4
                    optimizer.add(
                        z3.Implies(choice, carry_arrival[target] == result_arrival)
                    )
                    edge_cost_terms.append(z3.If(choice, edge_cost, 0))
            edge_choices[target] = values
            optimizer.add(z3.PbEq([(choice, 1) for _pred, _mode, choice in values], 1))

        for bit in range(BITS):
            optimizer.add(carry_arrival[bit] + 2 <= delay_limit)
        optimizer.add(carry_arrival[BITS] <= delay_limit)
        objective = z3.IntVal(48) + z3.Sum(*interval_cost_terms) + z3.Sum(*edge_cost_terms)
        optimizer.minimize(objective)
        status = optimizer.check()
        if status != z3.sat:
            runs[str(delay_limit)] = {"status": str(status)}
            continue
        model = optimizer.model()

        chosen_recipes: dict[tuple[int, int], tuple[int, str]] = {}
        for interval, values in recipes.items():
            hits = [
                (split, mode)
                for split, mode, choice in values
                if z3.is_true(model.eval(choice, model_completion=True))
            ]
            if len(hits) > 1:
                raise RuntimeError(f"multiple named recipes for {interval}")
            if hits:
                chosen_recipes[interval] = hits[0]

        @lru_cache(maxsize=None)
        def materialize(interval: tuple[int, int]) -> Transfer:
            lo, hi = interval
            if lo == hi:
                return leaves[lo]
            split, mode = chosen_recipes[interval]
            return combine_gp(
                factory,
                materialize((lo, split)),
                materialize((split + 1, hi)),
                mode,
            )

        carries = [factory.inputs["cin"]]
        edge_description = []
        for target in range(1, BITS + 1):
            hits = [
                (pred, mode)
                for pred, mode, choice in edge_choices[target]
                if z3.is_true(model.eval(choice, model_completion=True))
            ]
            if len(hits) != 1:
                raise RuntimeError(f"named carry edge selection failed for C{target}")
            predecessor, mode = hits[0]
            carries.append(
                gray_gp(
                    factory,
                    carries[predecessor],
                    materialize((predecessor, target - 1)),
                    mode,
                )
            )
            edge_description.append(f"C{target}<-C{predecessor}:{mode}[{predecessor},{target-1}]")
        sums = [sum_from_gp(factory, leaves[bit].p, carries[bit])[0] for bit in range(BITS)]
        outputs = tuple([*sums, carries[BITS]])
        metrics = factory.structural_metrics(outputs)
        optimized = model.eval(objective).as_long()
        if int(metrics["gate"]) != optimized:
            raise RuntimeError(
                f"named interval objective mismatch d{delay_limit}: z3={optimized} DAG={metrics['gate']}"
            )
        if int(metrics["delay"]) > delay_limit:
            raise RuntimeError(f"named interval timing mismatch d{delay_limit}: {metrics['delay']}")
        witnesses.append(
            Witness(
                "named-shared-carry-interval-dag",
                f"delay_bound={delay_limit};" + ";".join(edge_description),
                outputs,
            )
        )
        runs[str(delay_limit)] = {
            "status": "sat",
            "gate": optimized,
            "actual_delay": metrics["delay"],
            "carry_arrivals": [model.eval(value).as_long() for value in carry_arrival],
            "selected_interval_recipes": {
                f"{lo}:{hi}": {"split": split, "mode": mode}
                for (lo, hi), (split, mode) in sorted(chosen_recipes.items())
            },
            "selected_carry_edges": edge_description,
        }
    return witnesses, {"delay_runs": runs}


def pareto(factory: Factory, witnesses: Iterable[Witness]) -> list[tuple[Witness, dict[str, object]]]:
    unique: dict[str, tuple[Witness, dict[str, object]]] = {}
    for witness in witnesses:
        metrics = factory.structural_metrics(witness.outputs)
        key = str(metrics["structural_sha256"])
        unique[key] = (witness, metrics)
    metric_points: dict[tuple[int, int], tuple[Witness, dict[str, object]]] = {}
    for witness, metrics in unique.values():
        point = (int(metrics["gate"]), int(metrics["delay"]))
        current = metric_points.get(point)
        if current is None or (
            sum(metrics["output_arrivals"]), str(metrics["structural_sha256"])
        ) < (
            sum(current[1]["output_arrivals"]), str(current[1]["structural_sha256"])
        ):
            metric_points[point] = (witness, metrics)
    records = list(metric_points.values())
    result = []
    for index, (witness, metrics) in enumerate(records):
        gate = int(metrics["gate"])
        delay = int(metrics["delay"])
        if any(
            int(other["gate"]) <= gate
            and int(other["delay"]) <= delay
            and (
                int(other["gate"]) < gate or int(other["delay"]) < delay
            )
            for other_index, (_other_witness, other) in enumerate(records)
            if other_index != index
        ):
            continue
        result.append((witness, metrics))
    result.sort(key=lambda item: (item[1]["energy"], item[1]["delay"], item[1]["gate"]))
    return result


def summarize_witness(factory: Factory, witness: Witness, metrics: dict[str, object]) -> dict[str, object]:
    _packed, semantic = factory.evaluate(witness.outputs)
    arrivals = list(metrics["output_arrivals"])
    return {
        "family": witness.family,
        "detail": witness.detail,
        **metrics,
        "output_arrivals_named": {
            **{f"sum{bit}": arrivals[bit] for bit in range(BITS)},
            "cout": arrivals[BITS],
        },
        "arrival_paths": {
            **{f"sum{bit}": factory.arrival_path(witness.outputs[bit]) for bit in range(BITS)},
            "cout": factory.arrival_path(witness.outputs[BITS]),
        },
        "semantic": semantic,
    }


def run(output: Path, max_schedule_cells: int) -> dict[str, object]:
    factory = Factory()
    leaves = gp_leaves(factory)
    witnesses: list[Witness] = [build_shared_ripple(factory)]
    schedule_audit = []
    for topology in ("serial", "sklansky", "brent-kung", "kogge-stone"):
        schedule = prefix_schedule(topology, BITS + 1)
        cells = schedule_cell_count(schedule)
        if cells <= max_schedule_cells:
            mask_count = 1 << cells
            for mask in range(mask_count):
                witnesses.append(build_integrated_prefix(factory, leaves, topology, mask))
            mode = "all_cell_masks"
        else:
            # Exact within the explicitly stated uniform-per-level subfamily.
            mask_count = 1 << len(schedule)
            for level_mask in range(mask_count):
                cell_mask = 0
                offset = 0
                for level_index, level in enumerate(schedule):
                    if (level_mask >> level_index) & 1:
                        cell_mask |= ((1 << len(level)) - 1) << offset
                    offset += len(level)
                witnesses.append(build_integrated_prefix(factory, leaves, topology, cell_mask))
            mode = "uniform_per_level"
        schedule_audit.append(
            {
                "topology": topology,
                "levels": len(schedule),
                "cells": cells,
                "enumeration_mode": mode,
                "enumerated_masks": mask_count,
            }
        )

    transfer_dp, transfer_stats = transfer_tree_dp(factory, leaves)
    interval_witnesses, global_stats = select_prefix_outputs(factory, leaves, transfer_dp)
    witnesses.extend(interval_witnesses)
    frontier = pareto(factory, witnesses)
    summarized = [summarize_witness(factory, witness, metrics) for witness, metrics in frontier]
    thresholds = {"5": 102, "6": 85, "7": 73}
    best_by_delay = {}
    all_metrics = [(witness, factory.structural_metrics(witness.outputs)) for witness in witnesses]
    for delay_limit in range(4, 19):
        feasible = [item for item in all_metrics if int(item[1]["delay"]) <= delay_limit]
        if feasible:
            best = min(feasible, key=lambda item: (item[1]["gate"], item[1]["delay"]))
            best_by_delay[str(delay_limit)] = {
                "gate": best[1]["gate"],
                "delay": best[1]["delay"],
                "energy": best[1]["energy"],
                "family": best[0].family,
                "detail": best[0].detail,
                "structural_sha256": best[1]["structural_sha256"],
            }
    certificate = {
        "schema": 1,
        "scope": (
            "8-bit A+B+Cin; exact packed truth and TC Z/conflict semantics for retained witnesses; "
            "all ordinary/switch cell masks for schedules within max_schedule_cells, uniform-per-level "
            "otherwise; locally Pareto all-parenthesization GP transfer DP with exact multi-output node sharing"
        ),
        "cost_model": {
            "ordinary_gate": [1, 1],
            "xor_xnor": [3, 2],
            "bit_switch_driver": [2, 1],
            "wire_split_make_index_concat": [0, 0],
            "bus_rule": "ignore Z; simultaneous active drivers must agree; all-Z data plane is zero",
        },
        "test_domain": {
            "variables": VARIABLES,
            "rows": ASSIGNMENTS,
            "complete_u8_u8_u1": True,
        },
        "schedule_audit": schedule_audit,
        "transfer_dp": transfer_stats,
        "global_dp": global_stats,
        "enumerated_complete_witnesses": len(witnesses),
        "canonical_structural_node_count": len(factory.nodes),
        "pareto": summarized,
        "best_gate_at_or_below_delay": best_by_delay,
        "strict_beat_515_thresholds": thresholds,
        "score_below_515_witnesses": [
            item for item in summarized if int(item["energy"]) < 515
        ],
        "claims": {
            "global_boolean_lower_bound": False,
            "structured_family_lower_bound_only": True,
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(certificate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return certificate


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("interval_dp_certificate.json"),
    )
    parser.add_argument("--max-schedule-cells", type=int, default=15)
    args = parser.parse_args()
    certificate = run(args.output, args.max_schedule_cells)
    print(
        json.dumps(
            {
                "enumerated_complete_witnesses": certificate["enumerated_complete_witnesses"],
                "canonical_structural_node_count": certificate["canonical_structural_node_count"],
                "best_gate_at_or_below_delay": certificate["best_gate_at_or_below_delay"],
                "score_below_515_count": len(certificate["score_below_515_witnesses"]),
                "output": str(args.output),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
