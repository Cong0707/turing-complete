"""Bounded exact synthesis for small multi-output Boolean networks."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations_with_replacement
from typing import Callable, Iterable, Sequence


@dataclass(frozen=True)
class GateBasis:
    name: str
    operations: tuple[str, ...]
    complemented_edges: bool


NAND_BASIS = GateBasis("nand", ("nand",), False)
AIG_BASIS = GateBasis("aig", ("and",), True)
XAG_BASIS = GateBasis("xag", ("and", "xor"), True)
GATE_BASES = {basis.name: basis for basis in (NAND_BASIS, AIG_BASIS, XAG_BASIS)}


class SearchLimitExceeded(RuntimeError):
    """The fail-closed state guard interrupted an otherwise exact search."""


@dataclass(frozen=True, order=True)
class SignalRef:
    source: int
    inverted: bool = False


@dataclass(frozen=True)
class LogicNode:
    operation: str
    left: SignalRef
    right: SignalRef
    truth_table: int
    depth: int


@dataclass(frozen=True)
class LogicNetwork:
    input_count: int
    basis: GateBasis
    nodes: tuple[LogicNode, ...]
    outputs: tuple[SignalRef, ...] = ()

    @property
    def gate_count(self) -> int:
        return len(self.nodes)

    @property
    def depth(self) -> int:
        return max((self.signal_depth(output) for output in self.outputs), default=0)

    def signal_depth(self, signal: SignalRef) -> int:
        if signal.source < self.input_count:
            return 0
        return self.nodes[signal.source - self.input_count].depth

    def signal_truth_table(self, signal: SignalRef) -> int:
        if signal.source < 0 or signal.source >= self.input_count + len(self.nodes):
            raise ValueError("signal references an unavailable source")
        if signal.source < self.input_count:
            value = input_truth_table(self.input_count, signal.source)
        else:
            value = self.nodes[signal.source - self.input_count].truth_table
        return value ^ truth_table_mask(self.input_count) if signal.inverted else value

    def output_truth_tables(self) -> tuple[int, ...]:
        return tuple(self.signal_truth_table(output) for output in self.outputs)

    def evaluate(self, assignment: int | Sequence[int]) -> tuple[int, ...]:
        if isinstance(assignment, int):
            if not 0 <= assignment < 1 << self.input_count:
                raise ValueError("assignment is outside the input range")
            values = [(assignment >> index) & 1 for index in range(self.input_count)]
        else:
            values = [int(value) for value in assignment]
            if len(values) != self.input_count or any(value not in {0, 1} for value in values):
                raise ValueError("assignment must provide exactly one bit per input")

        def read(signal: SignalRef) -> int:
            return values[signal.source] ^ int(signal.inverted)

        for node in self.nodes:
            left, right = read(node.left), read(node.right)
            if node.operation == "nand":
                values.append(1 ^ (left & right))
            elif node.operation == "and":
                values.append(left & right)
            elif node.operation == "xor":
                values.append(left ^ right)
            else:
                raise ValueError(f"unknown operation {node.operation!r}")
        return tuple(read(output) for output in self.outputs)

    def prune_unused(self) -> "LogicNetwork":
        needed: set[int] = set()

        def visit(source: int) -> None:
            if source < self.input_count or source in needed:
                return
            node_index = source - self.input_count
            if node_index < 0 or node_index >= len(self.nodes):
                raise ValueError("network output references an unavailable node")
            needed.add(source)
            node = self.nodes[node_index]
            visit(node.left.source)
            visit(node.right.source)

        for output in self.outputs:
            visit(output.source)

        remap = {index: index for index in range(self.input_count)}
        nodes: list[LogicNode] = []
        for index, node in enumerate(self.nodes):
            old_source = self.input_count + index
            if old_source not in needed:
                continue
            remap[old_source] = self.input_count + len(nodes)
            nodes.append(
                LogicNode(
                    node.operation,
                    SignalRef(remap[node.left.source], node.left.inverted),
                    SignalRef(remap[node.right.source], node.right.inverted),
                    node.truth_table,
                    node.depth,
                )
            )
        outputs = tuple(SignalRef(remap[item.source], item.inverted) for item in self.outputs)
        return LogicNetwork(self.input_count, self.basis, tuple(nodes), outputs)

    def to_dict(self) -> dict[str, object]:
        def ref(item: SignalRef) -> dict[str, object]:
            return {"source": item.source, "inverted": item.inverted}

        return {
            "input_count": self.input_count,
            "basis": self.basis.name,
            "gate_count": self.gate_count,
            "depth": self.depth,
            "nodes": [
                {
                    "operation": node.operation,
                    "left": ref(node.left),
                    "right": ref(node.right),
                    "truth_table": node.truth_table,
                    "depth": node.depth,
                }
                for node in self.nodes
            ],
            "outputs": [ref(output) for output in self.outputs],
        }


@dataclass(frozen=True)
class ExactSynthesisResult:
    input_count: int
    output_truth_tables: tuple[int, ...]
    basis: GateBasis
    max_gates: int
    max_depth: int | None
    frontier: tuple[LogicNetwork, ...]
    states_by_gate_count: tuple[int, ...]
    generated_transitions: int

    @property
    def found(self) -> bool:
        return bool(self.frontier)


def truth_table_mask(input_count: int) -> int:
    if not 1 <= input_count <= 4:
        raise ValueError("exact synthesis supports one to four inputs")
    return (1 << (1 << input_count)) - 1


def input_truth_table(input_count: int, input_index: int) -> int:
    truth_table_mask(input_count)
    if not 0 <= input_index < input_count:
        raise ValueError("input index is outside the input range")
    return sum(
        ((assignment >> input_index) & 1) << assignment
        for assignment in range(1 << input_count)
    )


def truth_table_from_callable(input_count: int, function: Callable[..., int | bool]) -> int:
    truth_table_mask(input_count)
    result = 0
    for assignment in range(1 << input_count):
        inputs = tuple((assignment >> index) & 1 for index in range(input_count))
        value = int(function(*inputs))
        if value not in {0, 1}:
            raise ValueError("truth-table function must return zero or one")
        result |= value << assignment
    return result


def _resolve_basis(basis: str | GateBasis) -> GateBasis:
    if isinstance(basis, GateBasis):
        if not basis.operations or any(op not in {"nand", "and", "xor"} for op in basis.operations):
            raise ValueError("gate basis contains an unsupported operation")
        return basis
    try:
        return GATE_BASES[basis]
    except KeyError as exc:
        raise ValueError(f"unknown gate basis {basis!r}") from exc


def _canonical(table: int, mask: int, complemented: bool) -> int:
    return min(table, table ^ mask) if complemented else table


def _records(network: LogicNetwork) -> tuple[tuple[SignalRef, int, int], ...]:
    records: list[tuple[SignalRef, int, int]] = []
    mask = truth_table_mask(network.input_count)
    for source in range(network.input_count + len(network.nodes)):
        plain = SignalRef(source)
        truth, depth = network.signal_truth_table(plain), network.signal_depth(plain)
        records.append((plain, truth, depth))
        if network.basis.complemented_edges:
            records.append((SignalRef(source, True), truth ^ mask, depth))
    return tuple(records)


def _find_output(network: LogicNetwork, target: int) -> SignalRef | None:
    return next((ref for ref, truth, _ in _records(network) if truth == target), None)


def _apply(operation: str, left: int, right: int, mask: int) -> int:
    if operation == "nand":
        return (~(left & right)) & mask
    if operation == "and":
        return left & right
    if operation == "xor":
        return left ^ right
    raise ValueError(f"unsupported operation {operation!r}")


def _function_depths(network: LogicNetwork) -> tuple[tuple[int, int], ...]:
    mask = truth_table_mask(network.input_count)
    return tuple(
        sorted(
            (_canonical(node.truth_table, mask, network.basis.complemented_edges), node.depth)
            for node in network.nodes
        )
    )


def _insert_state(
    groups: dict[tuple[int, ...], list[tuple[tuple[int, ...], LogicNetwork]]],
    state: LogicNetwork,
) -> None:
    pairs = _function_depths(state)
    functions = tuple(function for function, _ in pairs)
    depths = tuple(depth for _, depth in pairs)
    frontier = groups.setdefault(functions, [])
    if any(all(old <= new for old, new in zip(old_depths, depths)) for old_depths, _ in frontier):
        return
    frontier[:] = [
        item for item in frontier
        if not all(new <= old for new, old in zip(depths, item[0]))
    ]
    frontier.append((depths, state))


def _pareto_insert(frontier: list[LogicNetwork], candidate: LogicNetwork) -> None:
    if any(
        old.gate_count <= candidate.gate_count and old.depth <= candidate.depth
        for old in frontier
    ):
        return
    frontier[:] = [
        old for old in frontier
        if not (candidate.gate_count <= old.gate_count and candidate.depth <= old.depth)
    ]
    frontier.append(candidate)
    frontier.sort(key=lambda item: (item.gate_count, item.depth))


def synthesize_exact(
    input_count: int,
    output_truth_tables: Sequence[int],
    *,
    basis: str | GateBasis = "nand",
    max_gates: int,
    max_depth: int | None = None,
    max_states: int | None = None,
) -> ExactSynthesisResult:
    """Return the exact gate/depth Pareto front inside finite search bounds.

    ``max_states`` is fail-closed: exceeding it raises instead of returning a
    partial result carrying an incorrect optimality claim.  No constants are
    implicit; AIG/XAG only make edge inversion free.
    """

    mask = truth_table_mask(input_count)
    targets = tuple(int(table) for table in output_truth_tables)
    if not targets:
        raise ValueError("at least one output truth table is required")
    if any(table < 0 or table > mask for table in targets):
        raise ValueError(f"output truth tables must fit in {mask.bit_length()} bits")
    if max_gates < 0:
        raise ValueError("max_gates must be non-negative")
    if max_depth is not None and max_depth < 0:
        raise ValueError("max_depth must be non-negative")
    if max_states is not None and max_states < 1:
        raise ValueError("max_states must be positive")

    gate_basis = _resolve_basis(basis)
    states = [LogicNetwork(input_count, gate_basis, ())]
    counts: list[int] = []
    explored = 0
    transitions = 0
    pareto: list[LogicNetwork] = []

    for gate_count in range(max_gates + 1):
        counts.append(len(states))
        explored += len(states)
        if max_states is not None and explored > max_states:
            raise SearchLimitExceeded(
                f"exact search exceeded max_states={max_states} at gate count {gate_count}"
            )

        for state in states:
            outputs = tuple(_find_output(state, target) for target in targets)
            if all(output is not None for output in outputs):
                candidate = LogicNetwork(
                    input_count,
                    gate_basis,
                    state.nodes,
                    tuple(output for output in outputs if output is not None),
                ).prune_unused()
                if candidate.output_truth_tables() != targets:
                    raise RuntimeError("internal exact-synthesis reconstruction mismatch")
                if max_depth is None or candidate.depth <= max_depth:
                    _pareto_insert(pareto, candidate)

        if gate_count == max_gates:
            break

        groups: dict[tuple[int, ...], list[tuple[tuple[int, ...], LogicNetwork]]] = {}
        for state in states:
            records = _records(state)
            available = {
                _canonical(truth, mask, gate_basis.complemented_edges)
                for _, truth, _ in records
            }
            for operation in gate_basis.operations:
                for left_record, right_record in combinations_with_replacement(records, 2):
                    left, left_truth, left_depth = left_record
                    right, right_truth, right_depth = right_record
                    truth = _apply(operation, left_truth, right_truth, mask)
                    if _canonical(truth, mask, gate_basis.complemented_edges) in available:
                        continue
                    depth = max(left_depth, right_depth) + 1
                    if max_depth is not None and depth > max_depth:
                        continue
                    node = LogicNode(operation, left, right, truth, depth)
                    _insert_state(
                        groups,
                        LogicNetwork(input_count, gate_basis, state.nodes + (node,)),
                    )
                    transitions += 1
        states = [state for key in sorted(groups) for _, state in groups[key]]

    return ExactSynthesisResult(
        input_count,
        targets,
        gate_basis,
        max_gates,
        max_depth,
        tuple(pareto),
        tuple(counts),
        transitions,
    )
