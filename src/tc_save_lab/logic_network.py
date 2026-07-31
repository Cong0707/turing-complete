"""Deterministic Boolean-network IR for synthesis experiments.

The save-file model describes placed components.  This module deliberately
stays one level above placement: it represents Boolean functions as a
structurally hashed XAG/AIG, rewrites them without guessing pin geometry, and
can lower the result to a netlist containing only explicit two-input NAND
gates.  Multiple outputs live in one graph so common subexpressions are counted
once.

Complemented edges are an IR feature, not a claim that inversion is free in
Turing Complete.  Use :func:`estimate_cost` with an explicit :class:`CostModel`
or lower to :class:`NandNetwork` before comparing candidates.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from enum import Enum
from itertools import product
from typing import Iterable, Mapping, Sequence


class LogicNetworkError(ValueError):
    """Raised when a Boolean network violates the reviewed IR contract."""


class Op(str, Enum):
    CONST = "const"
    INPUT = "input"
    AND = "and"
    XOR = "xor"


@dataclass(frozen=True, order=True)
class Signal:
    """A node reference with an optional complemented edge."""

    node: int
    inverted: bool = False

    def __invert__(self) -> "Signal":
        return Signal(self.node, not self.inverted)


FALSE = Signal(0)
TRUE = Signal(0, True)


@dataclass(frozen=True)
class Node:
    op: Op
    fanins: tuple[Signal, ...] = ()
    name: str = ""


@dataclass(frozen=True)
class NamedSignal:
    name: str
    signal: Signal


@dataclass(frozen=True)
class LogicNetwork:
    """Immutable, topologically ordered XAG/AIG network."""

    nodes: tuple[Node, ...]
    outputs: tuple[NamedSignal, ...]

    def __post_init__(self) -> None:
        if not self.nodes or self.nodes[0] != Node(Op.CONST):
            raise LogicNetworkError("node 0 must be the constant-zero node")
        input_names: set[str] = set()
        for node_id, node in enumerate(self.nodes):
            if node.op == Op.CONST:
                if node_id != 0 or node.fanins or node.name:
                    raise LogicNetworkError("only node 0 may be a constant node")
                continue
            if node.op == Op.INPUT:
                if node.fanins or not node.name:
                    raise LogicNetworkError("input nodes need a name and no fanins")
                if node.name in input_names:
                    raise LogicNetworkError(f"duplicate input name {node.name!r}")
                input_names.add(node.name)
                continue
            if len(node.fanins) != 2:
                raise LogicNetworkError(f"{node.op.value} nodes need exactly two fanins")
            if any(signal.node < 0 or signal.node >= node_id for signal in node.fanins):
                raise LogicNetworkError("fanins must reference earlier nodes")
            if node.op == Op.XOR and any(signal.inverted for signal in node.fanins):
                raise LogicNetworkError("XOR input polarity must be normalized to its output")
        output_names: set[str] = set()
        for output in self.outputs:
            if not output.name or output.name in output_names:
                raise LogicNetworkError(f"invalid or duplicate output name {output.name!r}")
            if output.signal.node < 0 or output.signal.node >= len(self.nodes):
                raise LogicNetworkError(f"output {output.name!r} references an unknown node")
            output_names.add(output.name)

    @property
    def input_names(self) -> tuple[str, ...]:
        return tuple(node.name for node in self.nodes if node.op == Op.INPUT)

    @property
    def is_aig(self) -> bool:
        return all(node.op != Op.XOR for node in self.nodes)

    def evaluate(self, inputs: Mapping[str, int | bool]) -> dict[str, int]:
        expected = set(self.input_names)
        if set(inputs) != expected:
            raise LogicNetworkError(
                f"input schema mismatch: expected {sorted(expected)}, got {sorted(inputs)}"
            )
        values = [False] * len(self.nodes)
        for node_id, node in enumerate(self.nodes[1:], start=1):
            if node.op == Op.INPUT:
                values[node_id] = bool(inputs[node.name])
                continue
            left = _signal_value(node.fanins[0], values)
            right = _signal_value(node.fanins[1], values)
            values[node_id] = left and right if node.op == Op.AND else left ^ right
        return {
            output.name: int(_signal_value(output.signal, values))
            for output in self.outputs
        }

    def truth_tables(self, *, max_inputs: int = 16) -> dict[str, int]:
        """Return packed truth tables using binary-count assignment order."""

        names = self.input_names
        if len(names) > max_inputs:
            raise LogicNetworkError(
                f"truth-table expansion limited to {max_inputs} inputs, got {len(names)}"
            )
        packed = {output.name: 0 for output in self.outputs}
        for row, bits in enumerate(product((0, 1), repeat=len(names))):
            result = self.evaluate(dict(zip(names, bits)))
            for name, value in result.items():
                packed[name] |= value << row
        return packed

    def reachable_nodes(self) -> frozenset[int]:
        pending = [output.signal.node for output in self.outputs]
        reached: set[int] = set()
        while pending:
            node_id = pending.pop()
            if node_id in reached:
                continue
            reached.add(node_id)
            pending.extend(signal.node for signal in self.nodes[node_id].fanins)
        return frozenset(reached)


def _signal_value(signal: Signal, values: Sequence[bool]) -> bool:
    value = values[signal.node]
    return not value if signal.inverted else value


def _signal_key(signal: Signal) -> tuple[int, bool]:
    return signal.node, signal.inverted


class LogicBuilder:
    """Structural hashing plus sound local XAG rewrite rules."""

    def __init__(self) -> None:
        self._nodes: list[Node] = [Node(Op.CONST)]
        self._inputs: dict[str, Signal] = {}
        self._hash: dict[tuple[Op, Signal, Signal], Signal] = {}
        self._outputs: list[NamedSignal] = []
        self._output_names: set[str] = set()

    @property
    def false(self) -> Signal:
        return FALSE

    @property
    def true(self) -> Signal:
        return TRUE

    def input(self, name: str) -> Signal:
        if not name:
            raise LogicNetworkError("input name cannot be empty")
        existing = self._inputs.get(name)
        if existing is not None:
            return existing
        signal = Signal(len(self._nodes))
        self._nodes.append(Node(Op.INPUT, name=name))
        self._inputs[name] = signal
        return signal

    def _check(self, signal: Signal) -> None:
        if signal.node < 0 or signal.node >= len(self._nodes):
            raise LogicNetworkError(f"signal references unknown node {signal.node}")

    def _intern(self, op: Op, left: Signal, right: Signal) -> Signal:
        if _signal_key(right) < _signal_key(left):
            left, right = right, left
        key = (op, left, right)
        existing = self._hash.get(key)
        if existing is not None:
            return existing
        result = Signal(len(self._nodes))
        self._nodes.append(Node(op, (left, right)))
        self._hash[key] = result
        return result

    def and_(self, left: Signal, right: Signal) -> Signal:
        self._check(left)
        self._check(right)
        if left == FALSE or right == FALSE:
            return FALSE
        if left == TRUE:
            return right
        if right == TRUE:
            return left
        if left == right:
            return left
        if left == ~right:
            return FALSE

        # Absorption and its complemented form:
        # x & (x & y) = x & y; x & ~(x & y) = x & ~y.
        simplified = self._and_absorb(left, right)
        if simplified is not None:
            return simplified
        simplified = self._and_absorb(right, left)
        if simplified is not None:
            return simplified
        simplified = self._and_xor_absorb(left, right)
        if simplified is not None:
            return simplified
        simplified = self._and_xor_absorb(right, left)
        if simplified is not None:
            return simplified
        return self._intern(Op.AND, left, right)

    def _and_absorb(self, literal: Signal, expression: Signal) -> Signal | None:
        node = self._nodes[expression.node]
        if node.op != Op.AND:
            return None
        if literal not in node.fanins:
            return None
        if not expression.inverted:
            return expression
        other = node.fanins[0] if node.fanins[1] == literal else node.fanins[1]
        return self.and_(literal, ~other)

    def _and_xor_absorb(self, literal: Signal, expression: Signal) -> Signal | None:
        """Apply ``x & (x XOR y) = x & ~y`` with arbitrary edge phases."""

        node = self._nodes[expression.node]
        if node.op != Op.XOR:
            return None
        positive_literal = Signal(literal.node)
        if positive_literal not in node.fanins:
            return None
        other = node.fanins[0] if node.fanins[1] == positive_literal else node.fanins[1]
        # If literal and XOR output have equal polarity, y must be false.
        required_other = other if literal.inverted ^ expression.inverted else ~other
        return self.and_(literal, required_other)

    def nand(self, left: Signal, right: Signal) -> Signal:
        return ~self.and_(left, right)

    def or_(self, left: Signal, right: Signal) -> Signal:
        return ~self.and_(~left, ~right)

    def nor(self, left: Signal, right: Signal) -> Signal:
        return self.and_(~left, ~right)

    def xor(self, left: Signal, right: Signal) -> Signal:
        self._check(left)
        self._check(right)
        parity = left.inverted ^ right.inverted
        left = Signal(left.node)
        right = Signal(right.node)
        if left == right:
            return TRUE if parity else FALSE
        if left == FALSE:
            result = right
        elif right == FALSE:
            result = left
        else:
            result = self._xor_and_absorb(left, right)
            if result is None:
                result = self._xor_and_absorb(right, left)
            if result is None:
                result = self._xor_factor(left, right)
            if result is None:
                result = self._intern(Op.XOR, left, right)
        return ~result if parity else result

    def _xor_and_absorb(self, literal: Signal, expression: Signal) -> Signal | None:
        """Apply ``x XOR (x & y) = x & ~y``."""

        node = self._nodes[expression.node]
        if node.op != Op.AND or literal not in node.fanins:
            return None
        other = node.fanins[0] if node.fanins[1] == literal else node.fanins[1]
        return self.and_(literal, ~other)

    def _xor_factor(self, left: Signal, right: Signal) -> Signal | None:
        """Apply ``xy XOR xz = x(y XOR z)`` for an exact common literal."""

        left_node = self._nodes[left.node]
        right_node = self._nodes[right.node]
        if left_node.op != Op.AND or right_node.op != Op.AND:
            return None
        common = set(left_node.fanins) & set(right_node.fanins)
        if not common:
            return None
        shared = min(common, key=_signal_key)
        left_other = left_node.fanins[0] if left_node.fanins[1] == shared else left_node.fanins[1]
        right_other = right_node.fanins[0] if right_node.fanins[1] == shared else right_node.fanins[1]
        return self.and_(shared, self.xor(left_other, right_other))

    def xnor(self, left: Signal, right: Signal) -> Signal:
        return ~self.xor(left, right)

    def mux(self, select: Signal, when_false: Signal, when_true: Signal) -> Signal:
        if when_false == when_true:
            return when_false
        return self.or_(
            self.and_(~select, when_false),
            self.and_(select, when_true),
        )

    def and_many(self, signals: Iterable[Signal], *, balanced: bool = True) -> Signal:
        unique: set[Signal] = set()
        for signal in signals:
            self._check(signal)
            if signal == FALSE:
                return FALSE
            if signal == TRUE:
                continue
            if ~signal in unique:
                return FALSE
            unique.add(signal)
        return self._reduce(tuple(sorted(unique, key=_signal_key)), self.and_, TRUE, balanced)

    def xor_many(self, signals: Iterable[Signal], *, balanced: bool = True) -> Signal:
        counts: Counter[Signal] = Counter()
        parity = False
        for signal in signals:
            self._check(signal)
            parity ^= signal.inverted
            counts[Signal(signal.node)] += 1
        remaining = tuple(
            sorted(
                (signal for signal, count in counts.items() if count & 1 and signal != FALSE),
                key=_signal_key,
            )
        )
        result = self._reduce(remaining, self.xor, FALSE, balanced)
        return ~result if parity else result

    @staticmethod
    def _reduce(
        signals: tuple[Signal, ...],
        operation: object,
        identity: Signal,
        balanced: bool,
    ) -> Signal:
        if not signals:
            return identity
        if not callable(operation):  # pragma: no cover - internal contract
            raise TypeError("operation must be callable")
        work = list(signals)
        if not balanced:
            result = work[0]
            for signal in work[1:]:
                result = operation(result, signal)
            return result
        while len(work) > 1:
            next_level: list[Signal] = []
            for index in range(0, len(work) - 1, 2):
                next_level.append(operation(work[index], work[index + 1]))
            if len(work) & 1:
                next_level.append(work[-1])
            work = next_level
        return work[0]

    def output(self, name: str, signal: Signal) -> None:
        self._check(signal)
        if not name or name in self._output_names:
            raise LogicNetworkError(f"invalid or duplicate output name {name!r}")
        self._output_names.add(name)
        self._outputs.append(NamedSignal(name, signal))

    def build(self) -> LogicNetwork:
        return LogicNetwork(tuple(self._nodes), tuple(self._outputs))


def rewrite_network(
    network: LogicNetwork,
    *,
    basis: str = "xag",
    balance_associative: bool = True,
) -> LogicNetwork:
    """Rebuild a network with hashing, associative flattening, and basis lowering.

    ``basis="xag"`` retains XOR nodes.  ``basis="aig"`` lowers every XOR to
    three AND nodes with complemented edges.  The rewrite preserves all output
    names and the original input order.
    """

    if basis not in {"xag", "aig"}:
        raise ValueError("basis must be 'xag' or 'aig'")
    builder = LogicBuilder()
    input_map = {name: builder.input(name) for name in network.input_names}
    cache: dict[Signal, Signal] = {FALSE: FALSE, TRUE: TRUE}

    def collect(signal: Signal, op: Op) -> tuple[list[Signal], bool]:
        parity = signal.inverted if op == Op.XOR else False
        positive = Signal(signal.node)
        node = network.nodes[positive.node]
        if node.op != op or (op == Op.AND and signal.inverted):
            return [signal], False
        leaves: list[Signal] = []
        for fanin in node.fanins:
            child_leaves, child_parity = collect(fanin, op)
            leaves.extend(child_leaves)
            parity ^= child_parity
        return leaves, parity

    def lower_xor(left: Signal, right: Signal) -> Signal:
        if basis == "xag":
            return builder.xor(left, right)
        different_01 = builder.and_(left, ~right)
        different_10 = builder.and_(~left, right)
        return builder.or_(different_01, different_10)

    def visit(signal: Signal) -> Signal:
        cached = cache.get(signal)
        if cached is not None:
            return cached
        node = network.nodes[signal.node]
        if node.op == Op.INPUT:
            result = input_map[node.name]
            if signal.inverted:
                result = ~result
        elif node.op == Op.AND:
            leaves, _ = collect(signal, Op.AND)
            if len(leaves) > 1 and not signal.inverted:
                result = builder.and_many(
                    (visit(leaf) for leaf in leaves),
                    balanced=balance_associative,
                )
            else:
                positive = builder.and_(visit(node.fanins[0]), visit(node.fanins[1]))
                result = ~positive if signal.inverted else positive
        elif node.op == Op.XOR:
            leaves, parity = collect(signal, Op.XOR)
            lowered = [visit(leaf) for leaf in leaves]
            if basis == "xag":
                result = builder.xor_many(lowered, balanced=balance_associative)
            else:
                if not lowered:
                    result = FALSE
                else:
                    work = lowered
                    while len(work) > 1:
                        next_level: list[Signal] = []
                        for index in range(0, len(work) - 1, 2):
                            next_level.append(lower_xor(work[index], work[index + 1]))
                        if len(work) & 1:
                            next_level.append(work[-1])
                        work = next_level
                    result = work[0]
            if parity:
                result = ~result
        else:  # pragma: no cover - validated network
            raise LogicNetworkError(f"cannot rewrite node operation {node.op}")
        cache[signal] = result
        return result

    for output in network.outputs:
        builder.output(output.name, visit(output.signal))
    return builder.build()


def merge_networks(
    networks: Mapping[str, LogicNetwork],
    *,
    basis: str = "xag",
    balance_associative: bool = True,
) -> LogicNetwork:
    """Merge independently built networks and share equivalent subgraphs.

    Mapping keys are namespaces.  Outputs become ``"namespace.output"`` (or
    simply ``"output"`` for an empty namespace); inputs with equal names are
    intentionally unified.
    """

    builder = LogicBuilder()
    for network in networks.values():
        for name in network.input_names:
            builder.input(name)

    for namespace, source in networks.items():
        rewritten = rewrite_network(
            source,
            basis=basis,
            balance_associative=balance_associative,
        )
        cache: dict[Signal, Signal] = {FALSE: FALSE, TRUE: TRUE}

        def import_signal(signal: Signal) -> Signal:
            cached = cache.get(signal)
            if cached is not None:
                return cached
            node = rewritten.nodes[signal.node]
            if node.op == Op.INPUT:
                result = builder.input(node.name)
            elif node.op == Op.AND:
                result = builder.and_(
                    import_signal(node.fanins[0]),
                    import_signal(node.fanins[1]),
                )
            elif node.op == Op.XOR:
                result = builder.xor(
                    import_signal(node.fanins[0]),
                    import_signal(node.fanins[1]),
                )
            else:  # pragma: no cover - validated network
                raise LogicNetworkError(f"cannot import node operation {node.op}")
            if signal.inverted:
                result = ~result
            cache[signal] = result
            return result

        for output in rewritten.outputs:
            name = f"{namespace}.{output.name}" if namespace else output.name
            builder.output(name, import_signal(output.signal))
    return builder.build()


@dataclass(frozen=True)
class CostModel:
    """Simple technology model for a placed-gate candidate."""

    and_gate: int = 1
    and_delay: int = 1
    xor_gate: int = 1
    xor_delay: int = 1
    not_gate: int = 1
    not_delay: int = 1
    complemented_edges_free: bool = False

    def __post_init__(self) -> None:
        if min(
            self.and_gate,
            self.and_delay,
            self.xor_gate,
            self.xor_delay,
            self.not_gate,
            self.not_delay,
        ) < 0:
            raise ValueError("costs and delays cannot be negative")


ABSTRACT_XAG_COST = CostModel(complemented_edges_free=True)
EXPLICIT_NOT_COST = CostModel()
TURING_COMPLETE_XAG_COST = CostModel(xor_gate=3, xor_delay=2)


@dataclass(frozen=True)
class CostPoint:
    gates: int
    delay: int
    label: str = ""

    def __post_init__(self) -> None:
        if self.gates < 0 or self.delay < 0:
            raise ValueError("gate and delay costs cannot be negative")

    @property
    def energy(self) -> int:
        return self.gates * self.delay

    def dominates(self, other: "CostPoint") -> bool:
        return (
            self.gates <= other.gates
            and self.delay <= other.delay
            and (self.gates < other.gates or self.delay < other.delay)
        )


def estimate_cost(network: LogicNetwork, model: CostModel = EXPLICIT_NOT_COST) -> CostPoint:
    """Count reachable operators and shared complemented-signal materializations."""

    reached = network.reachable_nodes()
    inverted_signals: set[int] = set()
    for node_id in reached:
        for fanin in network.nodes[node_id].fanins:
            if fanin.inverted and fanin.node != 0:
                inverted_signals.add(fanin.node)
    for output in network.outputs:
        if output.signal.inverted and output.signal.node != 0:
            inverted_signals.add(output.signal.node)

    gates = 0
    positive_depth: dict[int, int] = {0: 0}
    for node_id, node in enumerate(network.nodes[1:], start=1):
        if node_id not in reached:
            continue
        if node.op == Op.INPUT:
            positive_depth[node_id] = 0
            continue

        fanin_depths = []
        for fanin in node.fanins:
            depth = positive_depth[fanin.node]
            if fanin.inverted and fanin.node != 0 and not model.complemented_edges_free:
                depth += model.not_delay
            fanin_depths.append(depth)
        if node.op == Op.AND:
            gates += model.and_gate
            positive_depth[node_id] = max(fanin_depths) + model.and_delay
        elif node.op == Op.XOR:
            gates += model.xor_gate
            positive_depth[node_id] = max(fanin_depths) + model.xor_delay
        else:  # pragma: no cover - validated network
            raise LogicNetworkError(f"unknown cost for {node.op}")

    if not model.complemented_edges_free:
        gates += len(inverted_signals) * model.not_gate

    output_depths = []
    for output in network.outputs:
        depth = positive_depth.get(output.signal.node, 0)
        if output.signal.inverted and output.signal.node != 0 and not model.complemented_edges_free:
            depth += model.not_delay
        output_depths.append(depth)
    return CostPoint(gates, max(output_depths, default=0))


def estimate_turing_cost(network: LogicNetwork) -> CostPoint:
    """Estimate current one-bit TC primitives with native polarity absorption.

    Reviewed current candidates establish these local mappings:

    - AND/NAND and input NOT cost ``1 gate / 1 delay``;
    - XOR or XNOR costs ``3 gates / 2 delay``;
    - requesting both XOR polarities shares the first two product terms and
      costs ``4 gates / 2 delay``.

    The estimate is phase-aware and shares every IR node across outputs.  It is
    still a local technology mapping: larger cuts such as majority gates or a
    separately materialized ``AND(a,b)`` reused inside ``XOR(a,b)`` can improve
    it, so final leaderboard claims require placed-circuit measurement.
    """

    demanded: dict[int, set[bool]] = {}

    def demand(signal: Signal) -> None:
        phases = demanded.setdefault(signal.node, set())
        if signal.inverted in phases:
            return
        phases.add(signal.inverted)
        for fanin in network.nodes[signal.node].fanins:
            demand(fanin)

    for output in network.outputs:
        demand(output.signal)

    gates = 0
    phase_depth: dict[Signal, int] = {FALSE: 0, TRUE: 0}
    for node_id, node in enumerate(network.nodes[1:], start=1):
        phases = demanded.get(node_id)
        if not phases:
            continue
        if node.op == Op.INPUT:
            phase_depth[Signal(node_id)] = 0
            if True in phases:
                gates += 1
                phase_depth[Signal(node_id, True)] = 1
            continue

        arrival = max(phase_depth[fanin] for fanin in node.fanins)
        if node.op == Op.AND:
            gates += len(phases)
            for inverted in phases:
                phase_depth[Signal(node_id, inverted)] = arrival + 1
        elif node.op == Op.XOR:
            gates += 3 if len(phases) == 1 else 4
            for inverted in phases:
                phase_depth[Signal(node_id, inverted)] = arrival + 2
        else:  # pragma: no cover - validated network
            raise LogicNetworkError(f"unknown TC mapping for {node.op}")

    delay = max((phase_depth[output.signal] for output in network.outputs), default=0)
    return CostPoint(gates, delay)


def pareto_front(points: Iterable[CostPoint]) -> tuple[CostPoint, ...]:
    """Return deterministic unique non-dominated gate/delay candidates."""

    unique: dict[tuple[int, int], CostPoint] = {}
    for point in points:
        key = (point.gates, point.delay)
        previous = unique.get(key)
        if previous is None or point.label < previous.label:
            unique[key] = point
    candidates = tuple(unique.values())
    front = [
        point
        for point in candidates
        if not any(other.dominates(point) for other in candidates)
    ]
    return tuple(sorted(front, key=lambda point: (point.energy, point.delay, point.gates, point.label)))


class NandOp(str, Enum):
    INPUT = "input"
    NAND = "nand"


@dataclass(frozen=True)
class NandNode:
    op: NandOp
    fanins: tuple[int, int] | tuple[()] = ()
    name: str = ""


@dataclass(frozen=True)
class NandNetwork:
    """Topological netlist whose only logic primitive is two-input NAND."""

    nodes: tuple[NandNode, ...]
    outputs: tuple[tuple[str, int], ...]

    def __post_init__(self) -> None:
        input_names: set[str] = set()
        for node_id, node in enumerate(self.nodes):
            if node.op == NandOp.INPUT:
                if node.fanins or not node.name or node.name in input_names:
                    raise LogicNetworkError("NAND inputs need unique non-empty names")
                input_names.add(node.name)
            elif node.op == NandOp.NAND:
                if len(node.fanins) != 2 or any(
                    fanin < 0 or fanin >= node_id for fanin in node.fanins
                ):
                    raise LogicNetworkError("NAND fanins must reference earlier nodes")
            else:
                raise LogicNetworkError(f"unsupported NAND operation {node.op}")
        output_names: set[str] = set()
        for name, node_id in self.outputs:
            if not name or name in output_names:
                raise LogicNetworkError(f"invalid or duplicate NAND output name {name!r}")
            if node_id < 0 or node_id >= len(self.nodes):
                raise LogicNetworkError(f"NAND output {name!r} references an unknown node")
            output_names.add(name)

    @property
    def input_names(self) -> tuple[str, ...]:
        return tuple(node.name for node in self.nodes if node.op == NandOp.INPUT)

    @property
    def gate_count(self) -> int:
        return sum(node.op == NandOp.NAND for node in self.nodes)

    @property
    def delay(self) -> int:
        depths: list[int] = []
        for node_id, node in enumerate(self.nodes):
            if node.op == NandOp.INPUT:
                depths.append(0)
            else:
                depths.append(max(depths[node.fanins[0]], depths[node.fanins[1]]) + 1)
        return max((depths[node_id] for _, node_id in self.outputs), default=0)

    def evaluate(self, inputs: Mapping[str, int | bool]) -> dict[str, int]:
        expected = set(self.input_names)
        if set(inputs) != expected:
            raise LogicNetworkError(
                f"input schema mismatch: expected {sorted(expected)}, got {sorted(inputs)}"
            )
        values: list[bool] = []
        for node in self.nodes:
            if node.op == NandOp.INPUT:
                values.append(bool(inputs[node.name]))
            else:
                left, right = node.fanins
                values.append(not (values[left] and values[right]))
        return {name: int(values[node_id]) for name, node_id in self.outputs}

    def truth_tables(self, *, max_inputs: int = 16) -> dict[str, int]:
        names = self.input_names
        if len(names) > max_inputs:
            raise LogicNetworkError(
                f"truth-table expansion limited to {max_inputs} inputs, got {len(names)}"
            )
        packed = {name: 0 for name, _ in self.outputs}
        for row, bits in enumerate(product((0, 1), repeat=len(names))):
            result = self.evaluate(dict(zip(names, bits)))
            for name, value in result.items():
                packed[name] |= value << row
        return packed


class _NandBuilder:
    def __init__(self) -> None:
        self.nodes: list[NandNode] = []
        self.inputs: dict[str, int] = {}
        self.hash: dict[tuple[int, int], int] = {}

    def input(self, name: str) -> int:
        if name in self.inputs:
            return self.inputs[name]
        node_id = len(self.nodes)
        self.nodes.append(NandNode(NandOp.INPUT, name=name))
        self.inputs[name] = node_id
        return node_id

    def nand(self, left: int, right: int) -> int:
        if right < left:
            left, right = right, left
        key = (left, right)
        if key in self.hash:
            return self.hash[key]
        node_id = len(self.nodes)
        self.nodes.append(NandNode(NandOp.NAND, key))
        self.hash[key] = node_id
        return node_id

    def not_(self, signal: int) -> int:
        return self.nand(signal, signal)


def lower_to_nand(network: LogicNetwork) -> NandNetwork:
    """Lower a constant-free XAG/AIG to shared explicit NAND gates.

    Positive and negative phases of every AND are memoized.  An AND's negative
    phase therefore costs one NAND and its positive phase reuses that result.
    XOR uses the standard four-NAND construction.  Constants are synthesized
    from the first input only when a reachable output requires one.
    """

    builder = _NandBuilder()
    input_nodes = {name: builder.input(name) for name in network.input_names}
    phase_cache: dict[Signal, int] = {}
    positive_cache: dict[int, int] = {}

    def constant(value: bool) -> int:
        key = TRUE if value else FALSE
        if key in phase_cache:
            return phase_cache[key]
        if not input_nodes:
            raise LogicNetworkError("pure NAND lowering needs an input to synthesize constants")
        seed = next(iter(input_nodes.values()))
        inverse = builder.not_(seed)
        one = builder.nand(seed, inverse)
        zero = builder.not_(one)
        phase_cache[TRUE] = one
        phase_cache[FALSE] = zero
        return one if value else zero

    def positive(node_id: int) -> int:
        cached = positive_cache.get(node_id)
        if cached is not None:
            return cached
        if node_id == 0:
            return constant(False)
        node = network.nodes[node_id]
        if node.op == Op.INPUT:
            result = input_nodes[node.name]
        elif node.op == Op.AND:
            left = lower(node.fanins[0])
            right = lower(node.fanins[1])
            negative = builder.nand(left, right)
            phase_cache[Signal(node_id, True)] = negative
            result = builder.not_(negative)
        elif node.op == Op.XOR:
            left = lower(node.fanins[0])
            right = lower(node.fanins[1])
            common = builder.nand(left, right)
            left_term = builder.nand(left, common)
            right_term = builder.nand(right, common)
            result = builder.nand(left_term, right_term)
        else:  # pragma: no cover - validated network
            raise LogicNetworkError(f"cannot lower operation {node.op}")
        positive_cache[node_id] = result
        phase_cache[Signal(node_id)] = result
        return result

    def lower(signal: Signal) -> int:
        cached = phase_cache.get(signal)
        if cached is not None:
            return cached
        if signal.node == 0:
            return constant(signal.inverted)
        if signal.inverted:
            node = network.nodes[signal.node]
            if node.op == Op.AND:
                left = lower(node.fanins[0])
                right = lower(node.fanins[1])
                result = builder.nand(left, right)
            else:
                result = builder.not_(positive(signal.node))
        else:
            result = positive(signal.node)
        phase_cache[signal] = result
        return result

    outputs = tuple((output.name, lower(output.signal)) for output in network.outputs)
    return NandNetwork(tuple(builder.nodes), outputs)


def verify_equivalent(
    reference: LogicNetwork | NandNetwork,
    candidate: LogicNetwork | NandNetwork,
    *,
    max_inputs: int = 16,
) -> int:
    """Exhaustively compare two named multi-output Boolean networks.

    Input and output order may differ, but their names must match exactly.  The
    returned count is the number of tested input vectors.
    """

    reference_inputs = set(reference.input_names)
    candidate_inputs = set(candidate.input_names)
    if reference_inputs != candidate_inputs:
        raise LogicNetworkError(
            "equivalence input schema mismatch: "
            f"reference={sorted(reference_inputs)}, candidate={sorted(candidate_inputs)}"
        )
    reference_outputs = (
        {output.name for output in reference.outputs}
        if isinstance(reference, LogicNetwork)
        else {name for name, _ in reference.outputs}
    )
    candidate_outputs = (
        {output.name for output in candidate.outputs}
        if isinstance(candidate, LogicNetwork)
        else {name for name, _ in candidate.outputs}
    )
    if reference_outputs != candidate_outputs:
        raise LogicNetworkError(
            "equivalence output schema mismatch: "
            f"reference={sorted(reference_outputs)}, candidate={sorted(candidate_outputs)}"
        )
    if len(reference_inputs) > max_inputs:
        raise LogicNetworkError(
            f"equivalence expansion limited to {max_inputs} inputs, got {len(reference_inputs)}"
        )

    names = tuple(sorted(reference_inputs))
    tested = 0
    for bits in product((0, 1), repeat=len(names)):
        inputs = dict(zip(names, bits))
        expected = reference.evaluate(inputs)
        actual = candidate.evaluate(inputs)
        if actual != expected:
            rendered = ", ".join(f"{name}={inputs[name]}" for name in names)
            raise LogicNetworkError(
                f"network mismatch at {rendered}: expected {expected}, got {actual}"
            )
        tested += 1
    return tested
