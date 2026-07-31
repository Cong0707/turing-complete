"""Exact bounded synthesis for small XOR-AND graphs (XAGs).

Truth tables are packed into integers.  Bit ``assignment`` is the output for
that binary input assignment, with input 0 in the least-significant position.
The synthesizer treats complemented edges as free and canonicalizes every
function together with its complement.  It is intended for one-to-four input
building blocks and deliberately stops at a caller supplied candidate limit.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from functools import cache
from itertools import combinations_with_replacement
from typing import Callable, Iterable, Literal, Mapping


XagOperation = Literal["and", "xor"]


def truth_mask(input_count: int) -> int:
    """Return the mask covering every row of an ``input_count`` truth table."""

    if not 1 <= input_count <= 4:
        raise ValueError("XAG truth tables support between 1 and 4 inputs")
    return (1 << (1 << input_count)) - 1


def input_truth_table(input_count: int, input_index: int) -> int:
    """Return the packed truth table for one input variable."""

    mask = truth_mask(input_count)
    if not 0 <= input_index < input_count:
        raise ValueError(f"input index {input_index} is outside 0..{input_count - 1}")
    result = 0
    for assignment in range(1 << input_count):
        result |= ((assignment >> input_index) & 1) << assignment
    return result & mask


def truth_table_from_callable(input_count: int, function: Callable[..., object]) -> int:
    """Pack a Python Boolean function using the module's assignment order."""

    truth_mask(input_count)
    result = 0
    for assignment in range(1 << input_count):
        values = tuple(bool((assignment >> index) & 1) for index in range(input_count))
        result |= int(bool(function(*values))) << assignment
    return result


def canonical_truth_table(table: int, input_count: int) -> tuple[int, bool]:
    """Return the complement-class representative and whether ``table`` differs."""

    mask = truth_mask(input_count)
    if table < 0 or table > mask:
        raise ValueError(f"truth table must fit in {1 << input_count} bits")
    complement = table ^ mask
    canonical = min(table, complement)
    return canonical, table != canonical


@dataclass(frozen=True)
class XagLiteral:
    """A reference to constant 0, an input, or a gate output.

    Source 0 is constant 0, sources 1..N are inputs 0..N-1, and later sources
    refer to nodes in topological order.
    """

    source: int
    inverted: bool = False

    def negate(self) -> "XagLiteral":
        return replace(self, inverted=not self.inverted)


@dataclass(frozen=True)
class XagNode:
    operation: XagOperation
    left: XagLiteral
    right: XagLiteral


@dataclass(frozen=True)
class XagCostModel:
    """Non-negative primitive costs used to rank a synthesized network."""

    and_gate_cost: int = 1
    xor_gate_cost: int = 1
    and_delay: int = 1
    xor_delay: int = 1

    def __post_init__(self) -> None:
        values = (
            self.and_gate_cost,
            self.xor_gate_cost,
            self.and_delay,
            self.xor_delay,
        )
        if any(value < 0 for value in values):
            raise ValueError("XAG costs and delays must be non-negative")

    @classmethod
    def turing_complete_primitives(cls) -> "XagCostModel":
        """Return the observed one-bit AND/XOR costs used by current recipes.

        Complemented edges remain abstract and free.  A later lowering pass
        must prove that its chosen TC primitives preserve that assumption.
        """

        return cls(and_gate_cost=1, xor_gate_cost=3, and_delay=1, xor_delay=2)


@dataclass(frozen=True)
class XagMetrics:
    gate_count: int
    and_count: int
    xor_count: int
    gate_cost: int
    delay: int

    @property
    def energy(self) -> int:
        return self.gate_cost * self.delay


@dataclass(frozen=True)
class XagNetwork:
    input_count: int
    nodes: tuple[XagNode, ...]
    output: XagLiteral

    def __post_init__(self) -> None:
        truth_mask(self.input_count)
        for offset, node in enumerate(self.nodes):
            if node.operation not in ("and", "xor"):
                raise ValueError(f"unsupported XAG operation {node.operation!r}")
            node_source = self.input_count + 1 + offset
            for literal in (node.left, node.right):
                if not 0 <= literal.source < node_source:
                    raise ValueError("XAG nodes must only reference earlier sources")
        maximum_source = self.input_count + len(self.nodes)
        if not 0 <= self.output.source <= maximum_source:
            raise ValueError("XAG output references an unavailable source")

    def truth_table(self) -> int:
        mask = truth_mask(self.input_count)
        values = [0]
        values.extend(input_truth_table(self.input_count, index) for index in range(self.input_count))

        def read(literal: XagLiteral) -> int:
            value = values[literal.source]
            return value ^ mask if literal.inverted else value

        for node in self.nodes:
            left = read(node.left)
            right = read(node.right)
            values.append(left & right if node.operation == "and" else left ^ right)
        return read(self.output)

    def metrics(self, cost_model: XagCostModel | None = None) -> XagMetrics:
        model = cost_model or XagCostModel()
        arrivals = [0] * (self.input_count + 1)
        and_count = 0
        xor_count = 0
        for node in self.nodes:
            if node.operation == "and":
                and_count += 1
                node_delay = model.and_delay
            else:
                xor_count += 1
                node_delay = model.xor_delay
            arrivals.append(max(arrivals[node.left.source], arrivals[node.right.source]) + node_delay)
        gate_cost = and_count * model.and_gate_cost + xor_count * model.xor_gate_cost
        return XagMetrics(
            gate_count=len(self.nodes),
            and_count=and_count,
            xor_count=xor_count,
            gate_cost=gate_cost,
            delay=arrivals[self.output.source],
        )


@dataclass(frozen=True)
class _Source:
    index: int


@dataclass(frozen=True)
class _Literal:
    atom: "_Source | _Gate"
    inverted: bool = False

    def negate(self) -> "_Literal":
        return replace(self, inverted=not self.inverted)


@dataclass(frozen=True)
class _Gate:
    operation: XagOperation
    left: _Literal
    right: _Literal


@cache
def _atom_key(atom: _Source | _Gate) -> tuple[object, ...]:
    if isinstance(atom, _Source):
        return ("source", atom.index)
    return ("gate", atom.operation, _literal_key(atom.left), _literal_key(atom.right))


@cache
def _literal_key(literal: _Literal) -> tuple[object, ...]:
    return (_atom_key(literal.atom), literal.inverted)


def _ordered_literals(left: _Literal, right: _Literal) -> tuple[_Literal, _Literal]:
    if _literal_key(right) < _literal_key(left):
        return right, left
    return left, right


@dataclass(frozen=True)
class _Expression:
    truth: int
    root: _Literal
    gates: frozenset[_Gate]

    @property
    def gate_count(self) -> int:
        return len(self.gates)


def _source_expression(table: int, source: int, input_count: int) -> _Expression:
    canonical, inverted = canonical_truth_table(table, input_count)
    return _Expression(canonical, _Literal(_Source(source), inverted), frozenset())


def _gate_expression(
    operation: XagOperation,
    left: _Expression,
    right: _Expression,
    left_inverted: bool,
    right_inverted: bool,
    input_count: int,
) -> _Expression:
    mask = truth_mask(input_count)
    left_literal = left.root.negate() if left_inverted else left.root
    right_literal = right.root.negate() if right_inverted else right.root

    if operation == "xor":
        # XOR input phases only change the output phase.  Pushing them to the
        # output gives one canonical structural representative.
        left_phase = left_literal.inverted
        right_phase = right_literal.inverted
        left_literal = replace(left_literal, inverted=False)
        right_literal = replace(right_literal, inverted=False)
        left_atom_truth = left.truth ^ mask if left.root.inverted else left.truth
        right_atom_truth = right.truth ^ mask if right.root.inverted else right.truth
        raw = left_atom_truth ^ right_atom_truth
        requested = raw ^ mask if left_phase ^ right_phase else raw
    else:
        left_value = left.truth ^ mask if left_inverted else left.truth
        right_value = right.truth ^ mask if right_inverted else right.truth
        raw = left_value & right_value
        requested = raw

    left_literal, right_literal = _ordered_literals(left_literal, right_literal)
    gate = _Gate(operation, left_literal, right_literal)
    canonical, _ = canonical_truth_table(requested, input_count)

    if operation == "xor":
        # ``raw`` is the value of the normalized, phase-free gate atom.
        root_inverted = raw != canonical
    else:
        root_inverted = requested != canonical
    return _Expression(
        truth=canonical,
        root=_Literal(gate, root_inverted),
        gates=left.gates | right.gates | frozenset((gate,)),
    )


def _lower_expression(expression: _Expression, input_count: int, target: int) -> XagNetwork:
    nodes: list[XagNode] = []
    gate_sources: dict[_Gate, int] = {}

    def lower_literal(literal: _Literal) -> XagLiteral:
        if isinstance(literal.atom, _Source):
            return XagLiteral(literal.atom.index, literal.inverted)
        gate = literal.atom
        source = gate_sources.get(gate)
        if source is None:
            left = lower_literal(gate.left)
            right = lower_literal(gate.right)
            source = input_count + 1 + len(nodes)
            nodes.append(XagNode(gate.operation, left, right))
            gate_sources[gate] = source
        return XagLiteral(source, literal.inverted)

    output = lower_literal(expression.root)
    canonical, target_inverted = canonical_truth_table(target, input_count)
    if canonical != expression.truth:
        raise ValueError("expression does not implement the requested truth-table class")
    if target_inverted:
        output = output.negate()
    network = XagNetwork(input_count, tuple(nodes), output)
    if network.truth_table() != target:
        raise RuntimeError("internal XAG lowering changed the truth table")
    return network


class XagSynthesisLimitError(RuntimeError):
    """Exact enumeration exceeded its explicit resource bound."""


@dataclass(frozen=True)
class XagDatabase:
    """Complete rooted XAG inventory up to ``max_gates`` when returned normally."""

    input_count: int
    max_gates: int
    _expressions: Mapping[int, tuple[_Expression, ...]]

    @property
    def truth_class_count(self) -> int:
        return len(self._expressions)

    @property
    def candidate_count(self) -> int:
        return sum(len(expressions) for expressions in self._expressions.values())

    def candidates(self, target: int) -> tuple[XagNetwork, ...]:
        canonical, _ = canonical_truth_table(target, self.input_count)
        return tuple(
            _lower_expression(expression, self.input_count, target)
            for expression in self._expressions.get(canonical, ())
        )

    def minimum(self, target: int) -> XagNetwork | None:
        candidates = self.candidates(target)
        if not candidates:
            return None
        return min(candidates, key=lambda network: (len(network.nodes), _network_key(network)))

    def pareto(
        self,
        target: int,
        cost_model: XagCostModel | None = None,
    ) -> tuple[XagNetwork, ...]:
        """Return the exact bounded ``(gate_cost, delay)`` Pareto front."""

        model = cost_model or XagCostModel()
        unique: dict[tuple[object, ...], XagNetwork] = {
            _network_key(candidate): candidate for candidate in self.candidates(target)
        }
        ranked = sorted(
            unique.values(),
            key=lambda network: (
                network.metrics(model).gate_cost,
                network.metrics(model).delay,
                len(network.nodes),
                _network_key(network),
            ),
        )
        front: list[XagNetwork] = []
        for candidate in ranked:
            metrics = candidate.metrics(model)
            if any(
                existing.metrics(model).gate_cost <= metrics.gate_cost
                and existing.metrics(model).delay <= metrics.delay
                for existing in front
            ):
                continue
            front = [
                existing
                for existing in front
                if not (
                    metrics.gate_cost <= existing.metrics(model).gate_cost
                    and metrics.delay <= existing.metrics(model).delay
                )
            ]
            front.append(candidate)
        return tuple(front)


def _network_key(network: XagNetwork) -> tuple[object, ...]:
    return (
        network.input_count,
        tuple(
            (node.operation, node.left.source, node.left.inverted, node.right.source, node.right.inverted)
            for node in network.nodes
        ),
        network.output.source,
        network.output.inverted,
    )


def enumerate_xags(
    input_count: int,
    max_gates: int,
    *,
    operations: Iterable[XagOperation] = ("and", "xor"),
    max_candidates: int = 250_000,
) -> XagDatabase:
    """Enumerate every canonical rooted XAG up to ``max_gates``.

    The enumeration is exact if this function returns.  ``max_candidates`` is
    a fail-closed guard: exceeding it raises ``XagSynthesisLimitError`` instead
    of returning an incomplete database.
    """

    truth_mask(input_count)
    if max_gates < 0:
        raise ValueError("max_gates must be non-negative")
    if max_candidates < input_count + 1:
        raise ValueError("max_candidates is too small for the primary sources")
    normalized_operations = tuple(dict.fromkeys(operations))
    if not normalized_operations or any(operation not in ("and", "xor") for operation in normalized_operations):
        raise ValueError("operations must contain only 'and' and/or 'xor'")

    by_size: list[dict[tuple[object, ...], _Expression]] = [dict() for _ in range(max_gates + 1)]
    by_truth: dict[int, dict[tuple[object, ...], _Expression]] = {}

    sources = [_source_expression(0, 0, input_count)]
    sources.extend(
        _source_expression(input_truth_table(input_count, index), index + 1, input_count)
        for index in range(input_count)
    )

    candidate_count = 0

    def add(expression: _Expression) -> bool:
        nonlocal candidate_count
        key = _literal_key(expression.root)
        truth_bucket = by_truth.setdefault(expression.truth, {})
        if key in truth_bucket:
            return False
        if candidate_count >= max_candidates:
            raise XagSynthesisLimitError(
                f"exact XAG enumeration exceeded {max_candidates} candidates "
                f"at gate bound {max_gates}"
            )
        truth_bucket[key] = expression
        by_size[expression.gate_count][key] = expression
        candidate_count += 1
        return True

    for source in sources:
        add(source)

    for gate_count in range(1, max_gates + 1):
        smaller = [
            expression
            for size in range(gate_count)
            for expression in by_size[size].values()
        ]
        for left, right in combinations_with_replacement(smaller, 2):
            for operation in normalized_operations:
                phase_pairs = ((False, False),) if operation == "xor" else (
                    (False, False),
                    (False, True),
                    (True, False),
                    (True, True),
                )
                generated: set[tuple[object, ...]] = set()
                for left_inverted, right_inverted in phase_pairs:
                    expression = _gate_expression(
                        operation,
                        left,
                        right,
                        left_inverted,
                        right_inverted,
                        input_count,
                    )
                    # A gate equal (up to a free complement) to either child or
                    # to the free constant can be removed from every use site.
                    # Keeping it only creates dominated recursive structures.
                    if expression.truth in (0, left.truth, right.truth):
                        continue
                    if expression.gate_count != gate_count:
                        continue
                    key = _literal_key(expression.root)
                    if key in generated:
                        continue
                    generated.add(key)
                    add(expression)

    frozen = {
        truth: tuple(
            sorted(
                expressions.values(),
                key=lambda expression: (expression.gate_count, _literal_key(expression.root)),
            )
        )
        for truth, expressions in by_truth.items()
    }
    return XagDatabase(input_count, max_gates, frozen)
