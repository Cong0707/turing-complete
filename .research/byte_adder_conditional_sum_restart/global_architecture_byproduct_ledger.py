"""Build and audit a unified Byte Adder architecture/byproduct ledger.

This is a solver-free forward architecture study.  Named paper topologies are
seeds, not search boundaries.  Every candidate that enters the main ledger is
represented as a physical Factory DAG and independently replayed over all
2**17 inputs with value/driven/conflict semantics.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
import time
from typing import Any, Iterable


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT_DIR = HERE / "global_architecture_candidates"
OUTPUT = HERE / "global_architecture_byproduct_ledger.json"

ROWS = 1 << 17
ALL = (1 << ROWS) - 1
OUTPUT_NAMES = tuple([f"S{bit}" for bit in range(8)] + ["C8"])

GATE_SPECS = {
    "NOT": (1, 1, 1),
    "AND": (1, 1, 2),
    "NAND": (1, 1, 2),
    "OR": (1, 1, 2),
    "NOR": (1, 1, 2),
    "XOR": (3, 2, 2),
    "XNOR": (3, 2, 2),
}
COMMUTATIVE = {"AND", "NAND", "OR", "NOR", "XOR", "XNOR"}


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: object) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return sha256(encoded).hexdigest()


def atomic_write(path: Path, payload: object) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(encoded)
    temporary.replace(path)
    return sha256(encoded).hexdigest()


def variable(index: int) -> int:
    run = 1 << index
    period = run << 1
    pattern = ((1 << run) - 1) << run
    value = 0
    for offset in range(0, ROWS, period):
        value |= pattern << offset
    return value & ALL


INPUT_BITS = {
    **{f"a{bit}": variable(bit) for bit in range(8)},
    **{f"b{bit}": variable(8 + bit) for bit in range(8)},
    "cin": variable(16),
}


@dataclass(frozen=True)
class State:
    bits: int
    driven: int
    conflict: int
    arrival: int


@dataclass(frozen=True)
class CondBlock:
    bits: tuple[int, ...]
    sums0: tuple[int, ...]
    sums1: tuple[int, ...]
    c0: int
    nc0: int
    c1: int
    nc1: int


class Builder:
    def __init__(self, candidate_id: str) -> None:
        self.candidate_id = candidate_id
        self.nodes: list[dict[str, Any]] = []
        self.by_id: dict[int, dict[str, Any]] = {}
        self.next_id = 1
        self.cse: dict[tuple[Any, ...], int] = {}
        self.inputs: dict[str, int] = {}
        self.consts: dict[int, int] = {}
        for label in [
            *[item for bit in range(8) for item in (f"a{bit}", f"b{bit}")],
            "cin",
        ]:
            self.inputs[label] = self._add(
                "INPUT",
                (),
                0,
                0,
                label=label,
                origin="primary_input",
            )

    def _add(
        self,
        op: str,
        args: Iterable[int],
        cost: int,
        step_delay: int,
        *,
        label: str = "",
        origin: str = "",
        semantic_hint: str = "",
        resolved_network: str | None = None,
        drivers: list[dict[str, Any]] | None = None,
    ) -> int:
        args_tuple = tuple(map(int, args))
        arrival = 0 if not args_tuple else max(int(self.by_id[arg]["arrival"]) for arg in args_tuple) + step_delay
        node_id = self.next_id
        self.next_id += 1
        node: dict[str, Any] = {
            "id": node_id,
            "op": op,
            "args": list(args_tuple),
            "cost": int(cost),
            "step_delay": int(step_delay),
            "arrival": int(arrival),
            "may_z": op == "BUS",
            "label": label,
        }
        if origin:
            node["origin"] = origin
        if semantic_hint:
            node["semantic_hint"] = semantic_hint
        if resolved_network is not None:
            node["resolved_network"] = resolved_network
        if drivers is not None:
            node["drivers"] = drivers
        self.nodes.append(node)
        self.by_id[node_id] = node
        return node_id

    def const(self, value: int) -> int:
        value = int(bool(value))
        if value not in self.consts:
            self.consts[value] = self._add(
                "CONST",
                (),
                0,
                0,
                label=str(value),
                origin="free_constant_adapter",
                semantic_hint=f"CONST{value}",
            )
        return self.consts[value]

    def gate(
        self,
        op: str,
        *args: int,
        origin: str = "",
        semantic_hint: str = "",
    ) -> int:
        cost, delay, arity = GATE_SPECS[op]
        if len(args) != arity:
            raise ValueError((op, args))
        normalized = tuple(sorted(args)) if op in COMMUTATIVE else tuple(args)
        key = (op, normalized)
        existing = self.cse.get(key)
        if existing is not None:
            return existing
        result = self._add(
            op,
            normalized,
            cost,
            delay,
            origin=origin,
            semantic_hint=semantic_hint,
        )
        self.cse[key] = result
        return result

    def bus(
        self,
        pairs: Iterable[tuple[int, int]],
        *,
        origin: str = "",
        semantic_hint: str = "",
    ) -> int:
        pairs_tuple = tuple((int(enable), int(data)) for enable, data in pairs)
        if not pairs_tuple:
            raise ValueError("BUS requires at least one driver")
        owner = f"{self.candidate_id}_bus_{self.next_id}"
        args = tuple(item for pair in pairs_tuple for item in pair)
        drivers = [
            {"enable": enable, "data": data, "owner": owner}
            for enable, data in pairs_tuple
        ]
        return self._add(
            "BUS",
            args,
            2 * len(pairs_tuple),
            1,
            origin=origin,
            semantic_hint=semantic_hint,
            resolved_network=owner,
            drivers=drivers,
        )

    def mux(
        self,
        data0: int,
        data1: int,
        select: int,
        not_select: int,
        *,
        origin: str,
        semantic_hint: str = "",
    ) -> int:
        return self.bus(
            ((not_select, data0), (select, data1)),
            origin=origin,
            semantic_hint=semantic_hint,
        )

    def finalize(self, outputs: Iterable[int]) -> dict[str, Any]:
        outputs_tuple = tuple(map(int, outputs))
        live: set[int] = set()

        def visit(node_id: int) -> None:
            if node_id in live:
                return
            live.add(node_id)
            for argument in self.by_id[node_id]["args"]:
                visit(int(argument))

        for output in outputs_tuple:
            visit(output)
        nodes = [node for node in self.nodes if int(node["id"]) in live]
        factory = {
            "outputs": list(outputs_tuple),
            "nodes": nodes,
            "live_node_count": len(nodes),
        }
        factory["sha256"] = canonical_sha256(factory)
        return factory


def leaf(builder: Builder, bit: int, mode: str) -> CondBlock:
    a = builder.inputs[f"a{bit}"]
    b = builder.inputs[f"b{bit}"]
    p = builder.gate("XOR", a, b, origin="conditional_leaf", semantic_hint=f"bit{bit}.P")
    if mode == "fast":
        np = builder.gate("XNOR", a, b, origin="conditional_leaf", semantic_hint=f"bit{bit}.NP")
    elif mode == "compact":
        np = builder.gate("NOT", p, origin="conditional_leaf", semantic_hint=f"bit{bit}.NP")
    else:
        raise ValueError(mode)
    g = builder.gate("AND", a, b, origin="conditional_leaf", semantic_hint=f"bit{bit}.G")
    ng = builder.gate("NAND", a, b, origin="conditional_leaf", semantic_hint=f"bit{bit}.NG")
    q = builder.gate("OR", a, b, origin="conditional_leaf", semantic_hint=f"bit{bit}.Q")
    nq = builder.gate("NOR", a, b, origin="conditional_leaf", semantic_hint=f"bit{bit}.K")
    return CondBlock((bit,), (p,), (np,), g, ng, q, nq)


def combine_conditional(builder: Builder, low: CondBlock, high: CondBlock) -> CondBlock:
    if max(low.bits) + 1 != min(high.bits):
        raise ValueError((low.bits, high.bits))

    def variant(
        index: int,
    ) -> tuple[tuple[int, ...], int, int]:
        select = low.c0 if index == 0 else low.c1
        not_select = low.nc0 if index == 0 else low.nc1
        low_sums = low.sums0 if index == 0 else low.sums1
        high_sums = tuple(
            builder.mux(
                data0,
                data1,
                select,
                not_select,
                origin="conditional_block_combine",
                semantic_hint=f"block{min(low.bits)}_{max(high.bits)}.sum{bit}.cin{index}",
            )
            for bit, data0, data1 in zip(high.bits, high.sums0, high.sums1, strict=True)
        )
        carry = builder.mux(
            high.c0,
            high.c1,
            select,
            not_select,
            origin="conditional_block_combine",
            semantic_hint=f"block{min(low.bits)}_{max(high.bits)}.cout.cin{index}",
        )
        not_carry = builder.mux(
            high.nc0,
            high.nc1,
            select,
            not_select,
            origin="conditional_block_combine",
            semantic_hint=f"block{min(low.bits)}_{max(high.bits)}.ncout.cin{index}",
        )
        return tuple(low_sums) + high_sums, carry, not_carry

    sums0, c0, nc0 = variant(0)
    sums1, c1, nc1 = variant(1)
    return CondBlock(low.bits + high.bits, sums0, sums1, c0, nc0, c1, nc1)


def conditional_tree(builder: Builder, bits: tuple[int, ...], mode: str) -> CondBlock:
    if len(bits) == 1:
        return leaf(builder, bits[0], mode)
    split = len(bits) // 2
    return combine_conditional(
        builder,
        conditional_tree(builder, bits[:split], mode),
        conditional_tree(builder, bits[split:], mode),
    )


@lru_cache(maxsize=None)
def tree_shapes(width: int) -> tuple[Any, ...]:
    if width == 1:
        return (None,)
    result = []
    for left_width in range(1, width):
        for left in tree_shapes(left_width):
            for right in tree_shapes(width - left_width):
                result.append((left_width, left, right))
    return tuple(result)


def conditional_tree_shape(
    builder: Builder,
    bits: tuple[int, ...],
    mode: str,
    shape: Any,
) -> CondBlock:
    if len(bits) == 1:
        if shape is not None:
            raise ValueError(shape)
        return leaf(builder, bits[0], mode)
    left_width, left_shape, right_shape = shape
    return combine_conditional(
        builder,
        conditional_tree_shape(builder, bits[:left_width], mode, left_shape),
        conditional_tree_shape(builder, bits[left_width:], mode, right_shape),
    )


@lru_cache(maxsize=None)
def forest_plans(width: int) -> tuple[tuple[tuple[int, Any], ...], ...]:
    if width == 0:
        return ((),)
    result = []
    for first_width in range(1, width + 1):
        for shape in tree_shapes(first_width):
            for rest in forest_plans(width - first_width):
                result.append(((first_width, shape),) + rest)
    return tuple(result)


def select_block(
    builder: Builder,
    block: CondBlock,
    carry: int,
    not_carry: int,
    *,
    keep_not_carry: bool,
) -> tuple[tuple[int, ...], int, int | None]:
    sums = tuple(
        builder.mux(
            data0,
            data1,
            carry,
            not_carry,
            origin="actual_block_select",
            semantic_hint=f"S{bit}",
        )
        for bit, data0, data1 in zip(block.bits, block.sums0, block.sums1, strict=True)
    )
    result_carry = builder.mux(
        block.c0,
        block.c1,
        carry,
        not_carry,
        origin="actual_block_select",
        semantic_hint=f"C{max(block.bits) + 1}",
    )
    result_not_carry = None
    if keep_not_carry:
        result_not_carry = builder.mux(
            block.nc0,
            block.nc1,
            carry,
            not_carry,
            origin="actual_block_select",
            semantic_hint=f"NC{max(block.bits) + 1}",
        )
    return sums, result_carry, result_not_carry


def build_conditional_sum(candidate_id: str, mode: str, fast_first_carry: bool) -> dict[str, Any]:
    fixed_plan = (
        (1, None),
        (2, (1, None, None)),
        (4, (2, (1, None, None), (1, None, None))),
    )
    return build_conditional_sum_forest(
        candidate_id,
        mode,
        fast_first_carry,
        fixed_plan,
    )


def build_conditional_sum_forest(
    candidate_id: str,
    mode: str,
    fast_first_carry: bool,
    plan: tuple[tuple[int, Any], ...],
) -> dict[str, Any]:
    builder = Builder(candidate_id)
    cin = builder.inputs["cin"]
    if fast_first_carry:
        not_cin = builder.gate("NOT", cin, origin="actual_bit0", semantic_hint="NC0")
        a0 = builder.inputs["a0"]
        b0 = builder.inputs["b0"]
        p0 = builder.gate("XOR", a0, b0, origin="actual_bit0", semantic_hint="bit0.P")
        s0 = builder.gate("XOR", p0, cin, origin="actual_bit0", semantic_hint="S0")
        g0 = builder.gate("AND", a0, b0, origin="actual_bit0", semantic_hint="bit0.G")
        ng0 = builder.gate("NAND", a0, b0, origin="actual_bit0", semantic_hint="bit0.NG")
        q0 = builder.gate("OR", a0, b0, origin="actual_bit0", semantic_hint="bit0.Q")
        nq0 = builder.gate("NOR", a0, b0, origin="actual_bit0", semantic_hint="bit0.K")
        carry = builder.mux(g0, q0, cin, not_cin, origin="actual_bit0", semantic_hint="C1")
        not_carry = builder.mux(
            ng0,
            nq0,
            cin,
            not_cin,
            origin="actual_bit0",
            semantic_hint="NC1",
        )
    else:
        a0 = builder.inputs["a0"]
        b0 = builder.inputs["b0"]
        p0 = builder.gate("XOR", a0, b0, origin="actual_bit0", semantic_hint="bit0.P")
        s0 = builder.gate("XOR", p0, cin, origin="actual_bit0", semantic_hint="S0")
        g0 = builder.gate("AND", a0, b0, origin="actual_bit0", semantic_hint="bit0.G")
        q0 = builder.gate("OR", a0, b0, origin="actual_bit0", semantic_hint="bit0.Q")
        phase = builder.gate("OR", g0, cin, origin="actual_bit0", semantic_hint="H0")
        carry = builder.gate("AND", q0, phase, origin="actual_bit0", semantic_hint="C1")
        not_carry = builder.gate("NAND", q0, phase, origin="actual_bit0", semantic_hint="NC1")

    outputs: list[int] = [s0]
    start = 1
    for index, (width, shape) in enumerate(plan):
        bits = tuple(range(start, start + width))
        block = conditional_tree_shape(builder, bits, mode, shape)
        sums, carry, next_not = select_block(
            builder,
            block,
            carry,
            not_carry,
            keep_not_carry=index + 1 < len(plan),
        )
        outputs.extend(sums)
        if next_not is not None:
            not_carry = next_not
        start += width
    if start != 8:
        raise ValueError(plan)
    outputs.append(carry)
    return builder.finalize(outputs)


def ordinary_full_adder(
    builder: Builder,
    bit: int,
    carry: int,
    *,
    origin: str,
) -> tuple[int, int, int]:
    a = builder.inputs[f"a{bit}"]
    b = builder.inputs[f"b{bit}"]
    p = builder.gate("XOR", a, b, origin=origin, semantic_hint=f"bit{bit}.P")
    g = builder.gate("AND", a, b, origin=origin, semantic_hint=f"bit{bit}.G")
    summed = builder.gate("XOR", p, carry, origin=origin, semantic_hint=f"S{bit}")
    transfer = builder.gate("AND", p, carry, origin=origin)
    result_carry = builder.gate("OR", g, transfer, origin=origin, semantic_hint=f"C{bit + 1}")
    not_result = builder.gate("NOR", g, transfer, origin=origin, semantic_hint=f"NC{bit + 1}")
    return summed, result_carry, not_result


def actual_ripple_block(
    builder: Builder,
    bits: tuple[int, ...],
    carry: int,
    not_carry: int,
) -> tuple[tuple[int, ...], int, int]:
    del not_carry  # ordinary implementation only needs the positive rail.
    sums = []
    current = carry
    current_not = builder.gate("NOT", current, origin="ripple_seed")
    for bit in bits:
        summed, current, current_not = ordinary_full_adder(
            builder,
            bit,
            current,
            origin="actual_ripple_block",
        )
        sums.append(summed)
    return tuple(sums), current, current_not


def dual_ripple_block(builder: Builder, bits: tuple[int, ...], mode: str) -> CondBlock:
    leaves = [leaf(builder, bit, mode) for bit in bits]
    first = leaves[0]
    sums0 = [first.sums0[0]]
    sums1 = [first.sums1[0]]
    c0, nc0 = first.c0, first.nc0
    c1, nc1 = first.c1, first.nc1
    for bit in bits[1:]:
        s0, c0, nc0 = ordinary_full_adder(
            builder,
            bit,
            c0,
            origin="dual_ripple_cin0",
        )
        s1, c1, nc1 = ordinary_full_adder(
            builder,
            bit,
            c1,
            origin="dual_ripple_cin1",
        )
        sums0.append(s0)
        sums1.append(s1)
    return CondBlock(bits, tuple(sums0), tuple(sums1), c0, nc0, c1, nc1)


def bec_block(builder: Builder, bits: tuple[int, ...]) -> CondBlock:
    first = bits[0]
    a = builder.inputs[f"a{first}"]
    b = builder.inputs[f"b{first}"]
    p = builder.gate("XOR", a, b, origin="bec_cin0", semantic_hint=f"bit{first}.P")
    c0 = builder.gate("AND", a, b, origin="bec_cin0", semantic_hint=f"bit{first}.G")
    nc0 = builder.gate("NAND", a, b, origin="bec_cin0", semantic_hint=f"bit{first}.NG")
    sums0 = [p]
    for bit in bits[1:]:
        summed, c0, nc0 = ordinary_full_adder(builder, bit, c0, origin="bec_cin0")
        sums0.append(summed)
    vector0 = tuple(sums0) + (c0,)
    vector1: list[int] = [
        builder.gate("NOT", vector0[0], origin="bec_increment", semantic_hint=f"block{bits[0]}_{bits[-1]}.sum{bits[0]}.cin1")
    ]
    prefix = vector0[0]
    for offset in range(1, len(vector0)):
        hint = (
            f"block{bits[0]}_{bits[-1]}.cout.cin1"
            if offset == len(bits)
            else f"block{bits[0]}_{bits[-1]}.sum{bits[offset]}.cin1"
        )
        vector1.append(
            builder.gate("XOR", vector0[offset], prefix, origin="bec_increment", semantic_hint=hint)
        )
        if offset + 1 < len(vector0):
            prefix = builder.gate("AND", prefix, vector0[offset], origin="bec_increment")
    c1 = vector1[-1]
    nc1 = builder.gate("NOT", c1, origin="bec_increment", semantic_hint=f"block{bits[0]}_{bits[-1]}.ncout.cin1")
    return CondBlock(bits, tuple(sums0), tuple(vector1[:-1]), c0, nc0, c1, nc1)


def compositions(total: int) -> Iterable[tuple[int, ...]]:
    if total == 0:
        yield ()
        return
    for first in range(1, total + 1):
        for rest in compositions(total - first):
            yield (first,) + rest


def shape_descriptor(shape: Any) -> Any:
    if shape is None:
        return "leaf"
    left_width, left, right = shape
    return {
        "left_width": left_width,
        "left": shape_descriptor(left),
        "right": shape_descriptor(right),
    }


def plan_descriptor(plan: tuple[tuple[int, Any], ...]) -> list[dict[str, Any]]:
    return [
        {"width": width, "tree": shape_descriptor(shape)}
        for width, shape in plan
    ]


def build_block_select(
    candidate_id: str,
    partition: tuple[int, ...],
    family: str,
) -> dict[str, Any]:
    builder = Builder(candidate_id)
    cin = builder.inputs["cin"]
    ncin = builder.gate("NOT", cin, origin="block_select_root", semantic_hint="NC0")
    bit = 0
    first_bits = tuple(range(bit, bit + partition[0]))
    sums, carry, not_carry = actual_ripple_block(builder, first_bits, cin, ncin)
    outputs = list(sums)
    bit += partition[0]
    for block_index, width in enumerate(partition[1:]):
        bits = tuple(range(bit, bit + width))
        if family == "bec":
            block = bec_block(builder, bits)
        elif family == "dual_ripple":
            block = dual_ripple_block(builder, bits, "compact")
        else:
            raise ValueError(family)
        selected, carry, selected_not = select_block(
            builder,
            block,
            carry,
            not_carry,
            keep_not_carry=block_index + 1 < len(partition) - 1,
        )
        outputs.extend(selected)
        if selected_not is not None:
            not_carry = selected_not
        bit += width
    outputs.append(carry)
    return builder.finalize(outputs)


def build_majority_ripple(candidate_id: str, ling_form: bool) -> dict[str, Any]:
    builder = Builder(candidate_id)
    carry = builder.inputs["cin"]
    outputs = []
    for bit in range(8):
        a = builder.inputs[f"a{bit}"]
        b = builder.inputs[f"b{bit}"]
        p = builder.gate("XOR", a, b, origin="sum_shell", semantic_hint=f"bit{bit}.P")
        outputs.append(builder.gate("XOR", p, carry, origin="sum_shell", semantic_hint=f"S{bit}"))
        g = builder.gate("AND", a, b, origin="carry_leaf", semantic_hint=f"bit{bit}.G")
        q = builder.gate("OR", a, b, origin="carry_leaf", semantic_hint=f"bit{bit}.Q")
        if ling_form:
            pseudo = builder.gate("OR", g, carry, origin="ling_pseudocarry", semantic_hint=f"H{bit}")
            carry = builder.gate("AND", q, pseudo, origin="ling_carry", semantic_hint=f"C{bit + 1}")
        else:
            gated = builder.gate("AND", q, carry, origin="majority_carry")
            carry = builder.gate("OR", g, gated, origin="majority_carry", semantic_hint=f"C{bit + 1}")
    outputs.append(carry)
    return builder.finalize(outputs)


def build_shared_robdd(candidate_id: str) -> dict[str, Any]:
    order = tuple(["cin", *[item for bit in range(8) for item in (f"a{bit}", f"b{bit}")]])
    output_tables = [0] * 9
    for row in range(ROWS):
        values = {
            name: (row >> (len(order) - 1 - index)) & 1
            for index, name in enumerate(order)
        }
        a = sum(values[f"a{bit}"] << bit for bit in range(8))
        b = sum(values[f"b{bit}"] << bit for bit in range(8))
        total = a + b + values["cin"]
        for output in range(9):
            output_tables[output] |= ((total >> output) & 1) << row

    terminal_zero = 0
    terminal_one = 1
    next_bdd = 2
    unique: dict[tuple[int, int, int], int] = {}
    descriptors: dict[int, tuple[int, int, int]] = {}
    memo: dict[tuple[int, int], int] = {}

    def reduce_table(table: int, level: int) -> int:
        nonlocal next_bdd
        remaining = len(order) - level
        width = 1 << remaining
        if table == 0:
            return terminal_zero
        if table == (1 << width) - 1:
            return terminal_one
        key = (level, table)
        if key in memo:
            return memo[key]
        half = width >> 1
        mask = (1 << half) - 1
        low = reduce_table(table & mask, level + 1)
        high = reduce_table(table >> half, level + 1)
        if low == high:
            memo[key] = low
            return low
        unique_key = (level, low, high)
        node = unique.get(unique_key)
        if node is None:
            node = next_bdd
            next_bdd += 1
            unique[unique_key] = node
            descriptors[node] = unique_key
        memo[key] = node
        return node

    roots = tuple(reduce_table(table, 0) for table in output_tables)
    builder = Builder(candidate_id)
    signal_by_bdd = {terminal_zero: builder.const(0), terminal_one: builder.const(1)}
    not_inputs = {
        name: builder.gate("NOT", builder.inputs[name], origin="robdd_input_phase", semantic_hint=f"not({name})")
        for name in order
    }

    def materialize(node: int) -> int:
        if node in signal_by_bdd:
            return signal_by_bdd[node]
        level, low, high = descriptors[node]
        name = order[level]
        signal = builder.mux(
            materialize(low),
            materialize(high),
            builder.inputs[name],
            not_inputs[name],
            origin="shared_robdd_shannon",
            semantic_hint=f"bdd(level={level},var={name})",
        )
        signal_by_bdd[node] = signal
        return signal

    return builder.finalize(materialize(root) for root in roots)


def replay(nodes: tuple[dict[str, Any], ...]) -> dict[int, State]:
    states: dict[int, State] = {}
    networks: set[str] = set()
    for node in nodes:
        node_id = int(node["id"])
        op = str(node["op"])
        args = [states[int(value)] for value in node.get("args", ())]
        if op == "INPUT":
            state = State(INPUT_BITS[str(node["label"])], ALL, 0, 0)
            expected_cost = expected_delay = 0
        elif op == "CONST":
            state = State(ALL if str(node["label"]) == "1" else 0, ALL, 0, 0)
            expected_cost = expected_delay = 0
        elif op == "BUS":
            if len(args) < 2 or len(args) % 2:
                raise RuntimeError(f"malformed BUS {node_id}")
            owner = str(node.get("resolved_network", ""))
            if not owner or owner in networks:
                raise RuntimeError(f"BUS owner collision {node_id}: {owner!r}")
            networks.add(owner)
            serialized = node.get("drivers", ())
            if len(serialized) != len(args) // 2:
                raise RuntimeError(f"BUS driver serialization mismatch {node_id}")
            expected_drivers = [
                {
                    "enable": int(node["args"][offset]),
                    "data": int(node["args"][offset + 1]),
                    "owner": owner,
                }
                for offset in range(0, len(node["args"]), 2)
            ]
            if list(serialized) != expected_drivers:
                raise RuntimeError(f"BUS driver ownership mismatch {node_id}")
            ones = zeros = driven = conflict = 0
            for offset in range(0, len(args), 2):
                enable, data = args[offset], args[offset + 1]
                active = enable.bits
                ones |= active & data.bits
                zeros |= active & (~data.bits & ALL)
                driven |= active
                conflict |= enable.conflict | data.conflict
            conflict |= ones & zeros
            state = State(
                ones & ALL,
                driven & ALL,
                conflict & ALL,
                max(item.arrival for item in args) + 1,
            )
            expected_cost = len(args)
            expected_delay = 1
        else:
            if op not in GATE_SPECS:
                raise RuntimeError(f"unknown op {op}")
            expected_cost, expected_delay, arity = GATE_SPECS[op]
            if len(args) != arity:
                raise RuntimeError(f"arity mismatch {node_id}")
            left = args[0].bits
            right = args[1].bits if len(args) == 2 else 0
            if op == "NOT":
                bits = ~left
            elif op == "AND":
                bits = left & right
            elif op == "NAND":
                bits = ~(left & right)
            elif op == "OR":
                bits = left | right
            elif op == "NOR":
                bits = ~(left | right)
            elif op == "XOR":
                bits = left ^ right
            elif op == "XNOR":
                bits = ~(left ^ right)
            else:  # pragma: no cover
                raise AssertionError(op)
            state = State(
                bits & ALL,
                ALL,
                sum(item.conflict for item in args) & ALL,
                max(item.arrival for item in args) + expected_delay,
            )
            conflict = 0
            for item in args:
                conflict |= item.conflict
            state = State(state.bits, ALL, conflict & ALL, state.arrival)
        if (
            int(node.get("cost", -1)) != expected_cost
            or int(node.get("step_delay", -1)) != expected_delay
            or int(node.get("arrival", -1)) != state.arrival
            or bool(node.get("may_z")) != (op == "BUS")
        ):
            raise RuntimeError(f"annotation mismatch at node {node_id}")
        states[node_id] = state
    return states


def expected_functions() -> tuple[tuple[int, ...], dict[int, list[str]]]:
    registry: dict[int, set[str]] = defaultdict(set)

    def add(label: str, bits: int) -> None:
        registry[bits & ALL].add(label)

    carries = [INPUT_BITS["cin"]]
    sums = []
    leaves: list[dict[str, int]] = []
    for bit in range(8):
        a = INPUT_BITS[f"a{bit}"]
        b = INPUT_BITS[f"b{bit}"]
        g = a & b
        q = a | b
        p = a ^ b
        k = (~q) & ALL
        leaves.append({"G": g, "Q": q, "P": p, "K": k})
        add(f"bit{bit}.G", g)
        add(f"bit{bit}.NG", ~g)
        add(f"bit{bit}.Q", q)
        add(f"bit{bit}.K", k)
        add(f"bit{bit}.P", p)
        add(f"bit{bit}.NP", ~p)
        add(f"bit{bit}.sum_if_c0", p)
        add(f"bit{bit}.sum_if_c1", ~p)
        add(f"bit{bit}.carry_if_c0", g)
        add(f"bit{bit}.carry_if_c1", q)
        current = carries[-1]
        summed = p ^ current
        carry = g | (q & current)
        sums.append(summed & ALL)
        carries.append(carry & ALL)
        add(f"S{bit}", summed)
        add(f"NS{bit}", ~summed)
        add(f"C{bit}", current)
        add(f"NC{bit}", ~current)
        add(f"majority(a{bit},b{bit},C{bit})", carry)
    add("C8", carries[8])
    add("NC8", ~carries[8])

    for low in range(8):
        for high in range(low, 8):
            f0 = 0
            f1 = ALL
            any_generate = 0
            survival = ALL
            xor_propagate = ALL
            for bit in range(low, high + 1):
                leaf_values = leaves[bit]
                any_generate |= leaf_values["G"]
                survival &= leaf_values["Q"]
                xor_propagate &= leaf_values["P"]
                f0 = leaf_values["G"] | (leaf_values["Q"] & f0)
                f1 = leaf_values["G"] | (leaf_values["Q"] & f1)
            prefix = f"I[{low}:{high}]"
            add(prefix + ".F0", f0)
            add(prefix + ".F1", f1)
            add(prefix + ".NF0", ~f0)
            add(prefix + ".NF1", ~f1)
            add(prefix + ".transfer_generate", f0)
            add(prefix + ".transfer_propagate", (~f0) & f1)
            add(prefix + ".transfer_kill", ~f1)
            add(prefix + ".any_generate", any_generate)
            add(prefix + ".survival", survival)
            add(prefix + ".xor_propagate", xor_propagate)
            for external in (0, 1):
                current = ALL if external else 0
                for bit in range(low, high + 1):
                    leaf_values = leaves[bit]
                    local_sum = leaf_values["P"] ^ current
                    add(prefix + f".sum{bit}.cin{external}", local_sum)
                    current = leaf_values["G"] | (leaf_values["Q"] & current)
                add(prefix + f".cout.cin{external}", current)

    return tuple(sums + [carries[8]]), {
        key: sorted(values) for key, values in registry.items()
    }


EXPECTED_OUTPUTS, SEMANTIC_REGISTRY = expected_functions()


def packed_sha(bits: int) -> str:
    return sha256(int(bits & ALL).to_bytes(ROWS // 8, "little")).hexdigest()


def analyze_candidate(
    candidate_id: str,
    family: str,
    factory: dict[str, Any],
    *,
    provenance: dict[str, Any],
    configuration: dict[str, Any] | None = None,
) -> dict[str, Any]:
    nodes = tuple(factory["nodes"])
    outputs = tuple(map(int, factory["outputs"]))
    if len(outputs) != 9:
        raise RuntimeError(f"{candidate_id}: expected nine outputs")
    ids = [int(node["id"]) for node in nodes]
    if len(ids) != len(set(ids)):
        raise RuntimeError(f"{candidate_id}: duplicate node IDs")
    if int(factory.get("live_node_count", len(nodes))) != len(nodes):
        raise RuntimeError(f"{candidate_id}: serialized live-node count mismatch")
    seen: set[int] = set()
    input_labels = []
    for node in nodes:
        node_id = int(node["id"])
        if any(int(argument) not in seen for argument in node.get("args", ())):
            raise RuntimeError(f"{candidate_id}: non-topological argument at node {node_id}")
        if node["op"] == "INPUT":
            input_labels.append(str(node["label"]))
        seen.add(node_id)
    if set(input_labels) != set(INPUT_BITS) or len(input_labels) != len(INPUT_BITS):
        raise RuntimeError(f"{candidate_id}: primary-input coverage mismatch")
    if any(output not in seen for output in outputs):
        raise RuntimeError(f"{candidate_id}: missing output node")
    states = replay(nodes)
    by_id = {int(node["id"]): node for node in nodes}
    output_states = [states[node] for node in outputs]
    mismatches = [int((state.bits ^ expected).bit_count()) for state, expected in zip(output_states, EXPECTED_OUTPUTS, strict=True)]
    conflicts = 0
    for state in states.values():
        conflicts |= state.conflict
    output_z = [int((~state.driven & ALL).bit_count()) for state in output_states]
    true_z = [int((state.bits & ~state.driven & ALL).bit_count()) for state in output_states]
    if any(mismatches) or conflicts or any(output_z):
        raise RuntimeError(
            f"{candidate_id}: replay failed mismatch={mismatches} conflicts={conflicts.bit_count()} z={output_z}"
        )

    ancestors: dict[int, frozenset[int]] = {}

    def cone(node_id: int) -> frozenset[int]:
        if node_id not in ancestors:
            values = {node_id}
            for argument in by_id[node_id].get("args", ()):
                values.update(cone(int(argument)))
            ancestors[node_id] = frozenset(values)
        return ancestors[node_id]

    descendants: dict[int, list[str]] = defaultdict(list)
    for name, output in zip(OUTPUT_NAMES, outputs, strict=True):
        for node_id in cone(output):
            descendants[node_id].append(name)
    live_union = set().union(*(cone(output) for output in outputs))
    if live_union != set(ids):
        raise RuntimeError(f"{candidate_id}: dead serialized nodes")
    fanout: dict[int, int] = defaultdict(int)
    for node in nodes:
        for argument in node.get("args", ()):
            fanout[int(argument)] += 1

    node_records = []
    for node in nodes:
        node_id = int(node["id"])
        state = states[node_id]
        z_mask = (~state.driven) & ALL
        z_true = state.bits & z_mask
        z_false = (~state.bits) & z_mask & ALL
        cone_ids = cone(node_id)
        labels = SEMANTIC_REGISTRY.get(state.bits, [])
        node_records.append(
            {
                "id": node_id,
                "op": node["op"],
                "origin": node.get("origin"),
                "semantic_hint": node.get("semantic_hint"),
                "arrival": state.arrival,
                "local_cost": int(node["cost"]),
                "cone_gate": sum(int(by_id[item]["cost"]) for item in cone_ids),
                "cone_node_count": len(cone_ids),
                "fanout": fanout[node_id],
                "target_descendants": sorted(descendants[node_id]),
                "value_sha256": packed_sha(state.bits),
                "driven_sha256": packed_sha(state.driven),
                "conflict_rows": state.conflict.bit_count(),
                "z_rows": z_mask.bit_count(),
                "z_false_rows": z_false.bit_count(),
                "z_true_rows": z_true.bit_count(),
                "drive_mode": (
                    "conflict"
                    if state.conflict
                    else "always_driven"
                    if not z_mask
                    else "z_only_when_zero"
                    if not z_true
                    else "z_on_true"
                ),
                "semantic_labels": labels,
            }
        )

    gate = sum(int(node["cost"]) for node in nodes)
    arrivals = [state.arrival for state in output_states]
    delay = max(arrivals)
    buses = [node for node in nodes if node["op"] == "BUS"]
    return {
        "candidate_id": candidate_id,
        "family": family,
        "configuration": configuration or {},
        "provenance": provenance,
        "metrics": {
            "gate": gate,
            "delay": delay,
            "energy": gate * delay,
            "output_arrivals": arrivals,
            "live_node_count": len(nodes),
            "bus_node_count": len(buses),
            "switch_driver_count": sum(len(node["args"]) // 2 for node in buses),
            "structural_sha256": canonical_sha256(
                {"outputs": list(outputs), "nodes": list(nodes)}
            ),
        },
        "semantic": {
            "truth_table_rows": ROWS,
            "mismatch_count_by_output": mismatches,
            "mismatch_union_count": 0,
            "conflict_assignment_count": 0,
            "z_assignment_count_by_output": output_z,
            "true_z_assignment_count_by_output": true_z,
            "output_vector_sha256": canonical_sha256(
                [packed_sha(state.bits) for state in output_states]
            ),
        },
        "factory_dag": {
            "outputs": list(outputs),
            "nodes": list(nodes),
            "live_node_count": len(nodes),
            "sha256": factory.get("sha256")
            or canonical_sha256({"outputs": list(outputs), "nodes": list(nodes)}),
        },
        "byproducts": {
            "node_count": len(node_records),
            "known_semantic_node_count": sum(bool(item["semantic_labels"]) for item in node_records),
            "unknown_semantic_node_count": sum(not item["semantic_labels"] for item in node_records),
            "nodes": node_records,
        },
    }


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def source_candidates() -> list[
    tuple[str, str, Path, dict[str, Any], dict[str, Any], dict[str, Any]]
]:
    definitions: list[tuple[str, str, Path, Any, dict[str, Any]]] = [
        (
            "authoritative_ling_jackson_80_d7",
            "hybrid_ling_jackson_multioutput",
            ROOT / ".research/byte_adder_root/byte-adder-hybrid-phasefold-g80-d7.json",
            lambda data: data,
            {"role": "current_authoritative_frontier"},
        ),
        (
            "hybrid_gp_av_106_d6",
            "hybrid_gp_av_nonuniform",
            ROOT / ".research/byte_adder_depth4_global_agent/hybrid_gp_av_d6_g106.json",
            lambda data: data["runs"][0],
            {"role": "verified_d6_seed"},
        ),
        (
            "qphase_av_reduced_95_d6",
            "qphase_av_reduced_multioutput",
            ROOT / ".research/byte_adder_pair_macro_exact/byte-adder-av-reduced-g95-d6.json",
            lambda data: data,
            {
                "role": "verified_pair_cross_d6_seed",
                "not_a_global_boundary": True,
            },
        ),
        (
            "hybrid_gp_av_87_d7",
            "hybrid_gp_av_nonuniform",
            ROOT / ".research/byte_adder_depth4_global_agent/hybrid_gp_av_d7_g87.json",
            lambda data: data["runs"][0],
            {"role": "verified_d7_seed"},
        ),
        (
            "recursive_phase_prefix_89_d7",
            "arbitrary_recursive_prefix_phase",
            ROOT / ".research/byte_adder_prefix_frontier_agent/recursive-phase-prefix-frontier.json",
            lambda data: data["best_witness"],
            {"role": "paper_and_all_split_tree_seed", "not_a_global_boundary": True},
        ),
        (
            "classic_prefix_99_d7",
            "classic_prefix_seed",
            ROOT / ".research/byte_adder_prefix_frontier_agent/classic-prefix-topology-frontier.json",
            lambda data: data["global_pareto"][0],
            {"role": "classic_topology_seed", "not_a_global_boundary": True},
        ),
        (
            "bit35_joint_grafted_80_d7",
            "cross_boundary_joint_multioutput",
            ROOT
            / ".research/byte_adder_cross_boundary_joint_restart/bit35_joint_g17_grafted_full_dag.json",
            lambda data: data,
            {
                "role": "verified_cross_boundary_d7_seed",
                "not_a_global_boundary": True,
            },
        ),
    ]
    result = []
    for candidate_id, family, path, extractor, configuration in definitions:
        data = load_json(path)
        record = extractor(data)
        result.append(
            (
                candidate_id,
                family,
                path,
                record["factory_dag"],
                configuration,
                record["metrics"],
            )
        )
    return result


def validate_source_metrics(
    candidate_id: str,
    recomputed: dict[str, Any],
    serialized: dict[str, Any],
) -> dict[str, Any]:
    fields = ("gate", "delay", "energy", "output_arrivals")
    mismatches = {
        field: {
            "serialized": serialized.get(field),
            "recomputed": recomputed.get(field),
        }
        for field in fields
        if serialized.get(field) != recomputed.get(field)
    }
    if mismatches:
        raise RuntimeError(
            f"{candidate_id}: source serialized metric mismatch {mismatches}"
        )
    return {
        "status": "pass",
        "checked_fields": list(fields),
        "serialized": {field: serialized[field] for field in fields},
        "recomputed": {field: recomputed[field] for field in fields},
    }


def pareto(points: list[dict[str, Any]], keys: tuple[str, ...]) -> list[dict[str, Any]]:
    result = []
    for point in points:
        dominated = False
        for other in points:
            if other is point:
                continue
            no_worse = all(other[key] <= point[key] for key in keys)
            strict = any(other[key] < point[key] for key in keys)
            if no_worse and strict:
                dominated = True
                break
        if not dominated:
            result.append(point)
    return sorted(result, key=lambda item: tuple(item[key] for key in keys))


def seed_summaries() -> dict[str, Any]:
    modern_path = ROOT / ".research/byte_adder_modern_prefix_papers_agent/modern-prefix-results.json"
    modern = load_json(modern_path)
    named = []
    for item in modern["complete_truth_verification_per_topology"]:
        named.append(
            {
                "topology": item["point"]["topology"],
                "metrics": item["metrics"],
                "semantic": item["semantic"],
                "classification": "verified_seed_summary_without_embedded_factory_dag",
            }
        )
    hub_path = ROOT / ".research/byte_adder_conditional_sum_forward/hub33_g103_d5_slice_report.json"
    hub = load_json(hub_path)
    held_path = ROOT / ".research/byte_adder_depth4_global_agent/held-spirkl-ling-d5-d7.json"
    held = load_json(held_path)
    return {
        "named_prefix": {
            "path": str(modern_path.resolve()),
            "sha256": digest(modern_path),
            "records": named,
            "policy": "Names are seeds only; these records are not treated as lower bounds.",
        },
        "hub33_103_d5": {
            "path": str(hub_path.resolve()),
            "sha256": digest(hub_path),
            "metrics": hub["cost_delay"]["parent"],
            "truth": hub["reviewed_control_hypothesis"],
            "classification": "external_slice_seed_not_standalone_factory_candidate",
        },
        "held_spirkl_ling": {
            "path": str(held_path.resolve()),
            "sha256": digest(held_path),
            "runs": held["runs"],
            "classification": "restricted_model_seed_results_not_global_boundaries",
        },
    }


def main() -> int:
    started = time.perf_counter()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    candidates: list[dict[str, Any]] = []
    errors: list[str] = []

    conditional_search: dict[str, Any] = {
        "enumerated_forest_plans": len(forest_plans(7)),
        "mode_count": 4,
        "raw_point_count": 0,
        "pareto": [],
        "best_by_delay_bound": {},
    }
    conditional_raw: list[dict[str, Any]] = []
    conditional_winners: dict[int, tuple[dict[str, Any], dict[str, Any], str, str, bool, tuple[tuple[int, Any], ...]]] = {}
    for mode in ("fast", "compact"):
        for fast_first in (True, False):
            for plan in forest_plans(7):
                plan_json = plan_descriptor(plan)
                plan_hash = canonical_sha256(plan_json)[:12]
                temporary_id = f"conditional_forest_{mode}_{'fast' if fast_first else 'ordinary'}_{plan_hash}"
                factory = build_conditional_sum_forest(
                    temporary_id,
                    mode,
                    fast_first,
                    plan,
                )
                gate = sum(int(node["cost"]) for node in factory["nodes"])
                delay = max(
                    int(next(node for node in factory["nodes"] if int(node["id"]) == output)["arrival"])
                    for output in factory["outputs"]
                )
                point = {
                    "mode": mode,
                    "fast_first_carry": fast_first,
                    "plan": plan_json,
                    "plan_sha256": canonical_sha256(plan_json),
                    "gate": gate,
                    "delay": delay,
                    "energy": gate * delay,
                }
                conditional_raw.append(point)
                for bound in (5, 6, 7):
                    if delay > bound:
                        continue
                    prior = conditional_winners.get(bound)
                    key = (gate, delay, point["plan_sha256"], mode, not fast_first)
                    prior_key = (
                        (prior[0]["gate"], prior[0]["delay"], prior[0]["plan_sha256"], prior[2], not prior[4])
                        if prior is not None
                        else None
                    )
                    if prior is None or key < prior_key:
                        conditional_winners[bound] = (
                            point,
                            factory,
                            mode,
                            temporary_id,
                            fast_first,
                            plan,
                        )
    conditional_search["raw_point_count"] = len(conditional_raw)
    conditional_search["pareto"] = pareto(conditional_raw, ("gate", "delay"))
    for bound in (5, 6, 7):
        winner = conditional_winners.get(bound)
        if winner is None:
            conditional_search["best_by_delay_bound"][str(bound)] = None
            continue
        point, _, _, _, _, _ = winner
        conditional_search["best_by_delay_bound"][str(bound)] = point

    generated = [
        (
            "conditional_sum_fast_d5",
            "conditional_sum_nonuniform",
            build_conditional_sum("conditional_sum_fast_d5", "fast", True),
            {"leaf_mode": "direct XOR/XNOR dual rail", "actual_partition": [1, 1, 2, 4]},
        ),
        (
            "conditional_sum_compact_d6",
            "conditional_sum_nonuniform",
            build_conditional_sum("conditional_sum_compact_d6", "compact", False),
            {"leaf_mode": "shared XOR plus NOT", "actual_partition": [1, 1, 2, 4]},
        ),
        (
            "majority_ripple",
            "majority_threshold_decomposition",
            build_majority_ripple("majority_ripple", False),
            {"carry": "(a&b) | ((a|b)&cin)"},
        ),
        (
            "ling_ripple",
            "ling_pseudocarry",
            build_majority_ripple("ling_ripple", True),
            {"carry": "H=g|cin; cout=(a|b)&H"},
        ),
        (
            "shared_robdd_shannon",
            "shared_shannon_robdd",
            build_shared_robdd("shared_robdd_shannon"),
            {"variable_order": ["cin", *[item for bit in range(8) for item in (f"a{bit}", f"b{bit}")]]},
        ),
    ]

    # Add one independently replayed winner for each reachable delay bound.  A
    # winner can legitimately appear at multiple bounds; use a stable ID so
    # the artifact remains reproducible.
    added_winner_ids: set[str] = set()
    for bound in (5, 6, 7):
        winner = conditional_winners.get(bound)
        if winner is None:
            continue
        point, _, mode, _, fast_first, plan = winner
        winner_id = f"conditional_sum_forest_{mode}_{'fast' if fast_first else 'ordinary'}_{point['plan_sha256'][:12]}"
        if winner_id in added_winner_ids:
            continue
        added_winner_ids.add(winner_id)
        # Rebuild with the stable, final candidate ID.  BUS owner IDs are part
        # of the serialized physical ownership proof and must not retain the
        # temporary enumeration ID used while ranking all forest plans.
        factory = build_conditional_sum_forest(
            winner_id,
            mode,
            fast_first,
            plan,
        )
        generated.append(
            (
                winner_id,
                "conditional_sum_nonuniform_forest",
                factory,
                {
                    "leaf_mode": mode,
                    "fast_first_carry": fast_first,
                    "plan": point["plan"],
                    "enumeration": "all 429 ordered conditional forests",
                },
            )
        )

    block_search: dict[str, Any] = {}
    for family in ("bec", "dual_ripple"):
        raw = []
        factories: dict[tuple[int, ...], dict[str, Any]] = {}
        for partition in compositions(8):
            if len(partition) == 1:
                continue
            candidate_id = f"{family}_carry_select_" + "_".join(map(str, partition))
            factory = build_block_select(candidate_id, partition, family)
            gate = sum(int(node["cost"]) for node in factory["nodes"])
            delay = max(int(next(node for node in factory["nodes"] if int(node["id"]) == output)["arrival"]) for output in factory["outputs"])
            raw.append({"partition": list(partition), "gate": gate, "delay": delay, "energy": gate * delay})
            factories[partition] = factory
        family_pareto = pareto(raw, ("gate", "delay"))
        block_search[family] = {
            "enumerated_partitions": len(raw),
            "pareto": family_pareto,
            "best_by_delay_bound": {},
        }
        selected: set[tuple[int, ...]] = set()
        for bound in (5, 6, 7):
            feasible = [item for item in raw if item["delay"] <= bound]
            best = min(feasible, key=lambda item: (item["gate"], item["delay"], item["partition"])) if feasible else None
            block_search[family]["best_by_delay_bound"][str(bound)] = best
            if best is not None:
                selected.add(tuple(best["partition"]))
        for partition in sorted(selected):
            candidate_id = f"{family}_carry_select_" + "_".join(map(str, partition))
            generated.append(
                (
                    candidate_id,
                    "bec_carry_select" if family == "bec" else "dual_ripple_carry_select",
                    factories[partition],
                    {"partition": list(partition), "precompute": family},
                )
            )

    for candidate_id, family, factory, configuration in generated:
        try:
            record = analyze_candidate(
                candidate_id,
                family,
                factory,
                provenance={"kind": "generated_by_this_auditor"},
                configuration=configuration,
            )
            artifact_path = OUT_DIR / f"{candidate_id}.json"
            artifact = {
                "schema": "tc-byte-adder-global-architecture-candidate-v1",
                "status": "pass",
                **{key: value for key, value in record.items() if key != "byproducts"},
            }
            artifact_sha = atomic_write(artifact_path, artifact)
            record["artifact"] = {"path": str(artifact_path.resolve()), "sha256": artifact_sha}
            candidates.append(record)
        except Exception as exc:  # noqa: BLE001 - preserve validation failures as audit data.
            errors.append(f"{candidate_id}: {exc}")

    for (
        candidate_id,
        family,
        path,
        factory,
        configuration,
        serialized_metrics,
    ) in source_candidates():
        try:
            record = analyze_candidate(
                candidate_id,
                family,
                factory,
                provenance={
                    "kind": "existing_verified_factory_seed",
                    "path": str(path.resolve()),
                    "sha256": digest(path),
                },
                configuration=configuration,
            )
            record["source_metric_audit"] = validate_source_metrics(
                candidate_id,
                record["metrics"],
                serialized_metrics,
            )
            candidates.append(record)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{candidate_id}: {exc}")

    delay_ledger: dict[str, Any] = {}
    for bound in (5, 6, 7):
        feasible = [record for record in candidates if record["metrics"]["delay"] <= bound]
        ordered = sorted(
            feasible,
            key=lambda record: (
                record["metrics"]["gate"],
                record["metrics"]["delay"],
                record["candidate_id"],
            ),
        )
        delay_ledger[str(bound)] = {
            "candidate_count": len(ordered),
            "best": (
                {
                    "candidate_id": ordered[0]["candidate_id"],
                    "family": ordered[0]["family"],
                    **ordered[0]["metrics"],
                }
                if ordered
                else None
            ),
            "candidates": [
                {
                    "candidate_id": record["candidate_id"],
                    "family": record["family"],
                    **record["metrics"],
                }
                for record in ordered
            ],
        }

    semantic_points: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for candidate in candidates:
        for node in candidate["byproducts"]["nodes"]:
            if node["conflict_rows"] or node["z_true_rows"]:
                continue
            for label in node["semantic_labels"]:
                semantic_points[label].append(
                    {
                        "candidate_id": candidate["candidate_id"],
                        "node_id": node["id"],
                        "op": node["op"],
                        "arrival": node["arrival"],
                        "cone_gate": node["cone_gate"],
                        "drive_mode": node["drive_mode"],
                        "value_sha256": node["value_sha256"],
                    }
                )
    semantic_frontier = {
        label: pareto(points, ("arrival", "cone_gate"))
        for label, points in sorted(semantic_points.items())
    }

    truth_function_groups: dict[tuple[str, str], dict[str, Any]] = {}
    for candidate in candidates:
        for node in candidate["byproducts"]["nodes"]:
            key = (node["value_sha256"], node["drive_mode"])
            group = truth_function_groups.setdefault(
                key,
                {
                    "value_sha256": key[0],
                    "drive_mode": key[1],
                    "semantic_labels": set(),
                    "target_descendants": set(),
                    "points": [],
                },
            )
            group["semantic_labels"].update(node["semantic_labels"])
            group["target_descendants"].update(node["target_descendants"])
            group["points"].append(
                {
                    "candidate_id": candidate["candidate_id"],
                    "node_id": node["id"],
                    "arrival": node["arrival"],
                    "cone_gate": node["cone_gate"],
                    "op": node["op"],
                }
            )
    truth_function_frontier = []
    for group in truth_function_groups.values():
        frontier = pareto(group["points"], ("arrival", "cone_gate"))
        truth_function_frontier.append(
            {
                "value_sha256": group["value_sha256"],
                "drive_mode": group["drive_mode"],
                "semantic_labels": sorted(group["semantic_labels"]),
                "target_descendants": sorted(group["target_descendants"]),
                "occurrence_count": len(group["points"]),
                "pareto_points": frontier,
            }
        )
    truth_function_frontier.sort(
        key=lambda item: (item["drive_mode"], item["value_sha256"])
    )

    family_comparison: dict[str, Any] = {}
    for family in sorted({candidate["family"] for candidate in candidates}):
        family_records = [candidate for candidate in candidates if candidate["family"] == family]
        family_comparison[family] = {
            "candidate_count": len(family_records),
            "best_by_delay_bound": {
                str(bound): (
                    min(
                        (
                            candidate
                            for candidate in family_records
                            if candidate["metrics"]["delay"] <= bound
                        ),
                        key=lambda candidate: (
                            candidate["metrics"]["gate"],
                            candidate["metrics"]["delay"],
                            candidate["candidate_id"],
                        ),
                        default=None,
                    )
                )
                for bound in (5, 6, 7)
            },
        }
        for bound, candidate in list(family_comparison[family]["best_by_delay_bound"].items()):
            if candidate is not None:
                family_comparison[family]["best_by_delay_bound"][bound] = {
                    "candidate_id": candidate["candidate_id"],
                    "metrics": candidate["metrics"],
                }

    result = {
        "schema": "tc-byte-adder-global-architecture-byproduct-ledger-v1",
        "status": "pass" if not errors else "fail",
        "scope": {
            "inputs": "u8 + u8 + u1",
            "truth_rows": ROWS,
            "outputs": list(OUTPUT_NAMES),
            "paper_names_are_seeds_not_boundaries": True,
            "accepted_architecture_spaces": [
                "arbitrary Shannon/BDD",
                "majority/threshold decompositions",
                "dual rail and K/P/G encodings",
                "carry skip/select/save and BEC",
                "redundant representations",
                "nonuniform partitions",
                "multi-output Boolean networks",
                "arbitrary externally supplied physical Factory DAGs",
            ],
        },
        "cost_model": {
            "ordinary_gate": {"gate": 1, "delay": 1},
            "xor_xnor": {"gate": 3, "delay": 2},
            "switch_driver": {"gate": 2, "delay": 1},
            "bus_arrival": "max(enable,data arrivals)+1",
            "energy": "gate*delay",
            "physical_rule": "every BUS owns its complete driver set; no partial cross-BUS driver reuse",
        },
        "method": {
            "sat_solver_invoked": False,
            "full_value_driven_conflict_replay": True,
            "all_live_nodes_fingerprinted": True,
            "unknown_functions_retained_by_truth_sha256": True,
            "known_semantics": [
                "S/C and complements",
                "bit G/NG/K/P/NP/Q",
                "majority carry",
                "all contiguous-interval F(0)/F(1)",
                "interval transfer G/P/K",
                "any-generate/survival/xor-propagate",
                "all contiguous-block sum/carry cofactors",
            ],
            "node_cost": "unique backward-cone weighted gate cost",
            "node_timing": "recursive short-arc arrival from primary inputs",
        },
        "delay_ledger": delay_ledger,
        "block_partition_search": {
            **block_search,
            "conditional_sum_forests": conditional_search,
        },
        "architecture_family_comparison": family_comparison,
        "candidate_count": len(candidates),
        "candidates": candidates,
        "semantic_byproduct_frontier": semantic_frontier,
        "truth_function_frontier": {
            "unique_value_drive_classes": len(truth_function_frontier),
            "classes": truth_function_frontier,
        },
        "seed_summaries": seed_summaries(),
        "auditor": {
            "path": str(Path(__file__).resolve()),
            "sha256": digest(Path(__file__).resolve()),
        },
        "errors": errors,
    }
    output_sha = atomic_write(OUTPUT, result)
    print(
        json.dumps(
            {
                "output": str(OUTPUT.resolve()),
                "output_sha256": output_sha,
                "status": result["status"],
                "candidate_count": len(candidates),
                "delay_best": {
                    bound: item["best"] for bound, item in delay_ledger.items()
                },
                "semantic_frontier_functions": len(semantic_frontier),
                "errors": errors,
                "elapsed_seconds": time.perf_counter() - started,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
