"""Semantic-state Boolean synthesis over AIG and NAND networks.

The search is intentionally independent from the save-file and geometry layers.  It
uses packed truth tables as semantic state, which makes exhaustive search practical
for small functions and useful as a bounded dynamic program for four-input blocks.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from itertools import combinations_with_replacement
from typing import Callable, Iterable, Literal as TypingLiteral, Sequence


Library = TypingLiteral["aig", "nand"]


@dataclass(frozen=True, order=True)
class Literal:
    """A reference to a primary input, constant, or gate output."""

    source: int
    inverted: bool = False

    def flipped(self) -> "Literal":
        return Literal(self.source, not self.inverted)


@dataclass(frozen=True)
class Gate:
    """One two-input gate; its operation is selected by ``LogicNetwork.library``."""

    left: Literal
    right: Literal


@dataclass(frozen=True)
class LogicNetwork:
    """Technology-neutral result of one AIG or NAND synthesis run.

    Source 0 is constant zero, sources 1..N are primary inputs, and subsequent
    sources are gate outputs in topological order.  Constant zero is only usable by
    the search when ``include_constant`` is true.
    """

    input_count: int
    library: Library
    gates: tuple[Gate, ...]
    outputs: tuple[Literal, ...]
    include_constant: bool = False

    @property
    def gate_count(self) -> int:
        return len(self.gates)

    @property
    def mask(self) -> int:
        return (1 << (1 << self.input_count)) - 1

    def truth_tables(self) -> tuple[int, ...]:
        values = [0, *(_variable_truth_table(self.input_count, index) for index in range(self.input_count))]
        for gate_index, gate in enumerate(self.gates):
            limit = self.input_count + gate_index
            _validate_literal(gate.left, limit, self.library)
            _validate_literal(gate.right, limit, self.library)
            left = _literal_value(gate.left, values, self.mask)
            right = _literal_value(gate.right, values, self.mask)
            if self.library == "aig":
                values.append(left & right)
            else:
                values.append((~(left & right)) & self.mask)
        limit = self.input_count + len(self.gates)
        for output in self.outputs:
            _validate_literal(output, limit, self.library)
        return tuple(_literal_value(output, values, self.mask) for output in self.outputs)

    def output_depths(self) -> tuple[int, ...]:
        depths = [0] * (self.input_count + 1)
        for gate_index, gate in enumerate(self.gates):
            limit = self.input_count + gate_index
            _validate_literal(gate.left, limit, self.library)
            _validate_literal(gate.right, limit, self.library)
            depths.append(max(depths[gate.left.source], depths[gate.right.source]) + 1)
        limit = self.input_count + len(self.gates)
        for output in self.outputs:
            _validate_literal(output, limit, self.library)
        return tuple(depths[output.source] for output in self.outputs)

    @property
    def depth(self) -> int:
        depths = self.output_depths()
        return max(depths, default=0)

    def prune_unused(self) -> "LogicNetwork":
        """Remove gates outside every output cone and remap source indices."""

        gate_base = self.input_count + 1
        needed: set[int] = set()

        def visit(source: int) -> None:
            if source < gate_base or source in needed:
                return
            gate_index = source - gate_base
            if gate_index < 0 or gate_index >= len(self.gates):
                raise ValueError(f"literal source {source} is outside the network")
            needed.add(source)
            gate = self.gates[gate_index]
            visit(gate.left.source)
            visit(gate.right.source)

        for output in self.outputs:
            visit(output.source)

        remap = {source: source for source in range(gate_base)}
        kept: list[Gate] = []
        for gate_index, gate in enumerate(self.gates):
            old_source = gate_base + gate_index
            if old_source not in needed:
                continue
            remap[old_source] = gate_base + len(kept)
            kept.append(
                Gate(
                    Literal(remap[gate.left.source], gate.left.inverted),
                    Literal(remap[gate.right.source], gate.right.inverted),
                )
            )
        outputs = tuple(Literal(remap[item.source], item.inverted) for item in self.outputs)
        return replace(self, gates=tuple(kept), outputs=outputs)


@dataclass(frozen=True)
class SynthesisCandidate:
    """One non-dominated gate-count/depth result.

    ``exhaustive`` means every semantic layer up to this candidate's gate count was
    complete.  Later layers may still have been truncated in the containing report.
    """

    network: LogicNetwork
    exhaustive: bool

    @property
    def gate_count(self) -> int:
        return self.network.gate_count

    @property
    def depth(self) -> int:
        return self.network.depth

    @property
    def output_depths(self) -> tuple[int, ...]:
        return self.network.output_depths()


@dataclass(frozen=True)
class SynthesisReport:
    """Search result and enough metadata to distinguish proof from heuristic output."""

    input_count: int
    targets: tuple[int, ...]
    library: Library
    max_gates: int
    state_limit: int | None
    layer_state_counts: tuple[int, ...]
    truncated_layers: tuple[int, ...]
    candidates: tuple[SynthesisCandidate, ...]

    @property
    def exhaustive(self) -> bool:
        return not self.truncated_layers

    @property
    def exhaustive_through(self) -> int:
        """Largest consecutive gate-count layer completed without state pruning."""

        if not self.truncated_layers:
            return self.max_gates
        return self.truncated_layers[0] - 1


@dataclass(frozen=True)
class _Representative:
    literal: Literal
    depth: int


@dataclass
class _State:
    functions: dict[int, _Representative]
    gates: tuple[Gate, ...]

    def key(self) -> tuple[tuple[int, int], ...]:
        return tuple(sorted((function, item.depth) for function, item in self.functions.items()))


def make_truth_tables(
    input_count: int,
    evaluator: Callable[[tuple[int, ...]], int | Sequence[int]],
) -> tuple[int, ...]:
    """Pack a callable's outputs using input 0 as the assignment's low bit."""

    _validate_input_count(input_count)
    packed: list[int] | None = None
    for assignment in range(1 << input_count):
        bits = tuple((assignment >> index) & 1 for index in range(input_count))
        raw = evaluator(bits)
        values = (raw,) if isinstance(raw, int) else tuple(raw)
        if not values or any(value not in {0, 1} for value in values):
            raise ValueError("truth-table evaluator must return one or more bits")
        if packed is None:
            packed = [0] * len(values)
        elif len(values) != len(packed):
            raise ValueError("truth-table evaluator changed its output count")
        for output_index, value in enumerate(values):
            packed[output_index] |= value << assignment
    assert packed is not None
    return tuple(packed)


def synthesize_pareto(
    input_count: int,
    targets: Iterable[int],
    *,
    library: Library = "aig",
    max_gates: int,
    state_limit: int | None = 100_000,
    include_constant: bool = False,
) -> SynthesisReport:
    """Enumerate semantic network states and return gate/depth Pareto candidates.

    The result is exact through ``max_gates`` when ``state_limit`` is ``None`` or no
    layer reaches the supplied limit.  A finite limit turns the same search into a
    deterministic target-guided dynamic program and is reported through
    ``truncated_layers``; bounded results must not be presented as optimality proofs.
    """

    _validate_input_count(input_count)
    if library not in {"aig", "nand"}:
        raise ValueError(f"unsupported gate library {library!r}")
    if max_gates < 0:
        raise ValueError("max_gates must be non-negative")
    if state_limit is not None and state_limit <= 0:
        raise ValueError("state_limit must be positive or None")

    mask = (1 << (1 << input_count)) - 1
    target_tuple = tuple(targets)
    if not target_tuple:
        raise ValueError("at least one target truth table is required")
    if any(target < 0 or target > mask for target in target_tuple):
        raise ValueError(f"target truth tables must fit mask 0x{mask:x}")

    initial = _initial_state(input_count, library, include_constant, mask)
    states = {initial.key(): initial}
    layer_counts = [1]
    truncated_layers: list[int] = []
    found: dict[tuple[int, int], LogicNetwork] = {}
    _collect_solutions(states.values(), input_count, target_tuple, library, include_constant, mask, found)

    for layer in range(1, max_gates + 1):
        next_states: dict[tuple[tuple[int, int], ...], _State] = {}
        for state in states.values():
            for candidate in _expand_state(state, input_count, library, mask):
                next_states.setdefault(candidate.key(), candidate)
        if state_limit is not None and len(next_states) > state_limit:
            next_states = _trim_states(next_states, target_tuple, library, mask, state_limit)
            truncated_layers.append(layer)
        states = next_states
        layer_counts.append(len(states))
        _collect_solutions(states.values(), input_count, target_tuple, library, include_constant, mask, found)
        if not states:
            break

    pareto = _pareto_networks(found.values())
    return SynthesisReport(
        input_count=input_count,
        targets=target_tuple,
        library=library,
        max_gates=max_gates,
        state_limit=state_limit,
        layer_state_counts=tuple(layer_counts),
        truncated_layers=tuple(truncated_layers),
        candidates=tuple(
            SynthesisCandidate(
                network,
                not any(layer <= network.gate_count for layer in truncated_layers),
            )
            for network in pareto
        ),
    )


def _validate_input_count(input_count: int) -> None:
    if input_count < 1 or input_count > 4:
        raise ValueError("exact synthesis supports one to four inputs")


def _variable_truth_table(input_count: int, variable: int) -> int:
    result = 0
    for assignment in range(1 << input_count):
        result |= ((assignment >> variable) & 1) << assignment
    return result


def _validate_literal(literal: Literal, maximum_gate_index: int, library: Library) -> None:
    if literal.source < 0 or literal.source > maximum_gate_index:
        raise ValueError(f"literal source {literal.source} is not topologically available")
    if library == "nand" and literal.inverted:
        raise ValueError("NAND networks cannot use free inverted edges")


def _literal_value(literal: Literal, values: list[int], mask: int) -> int:
    value = values[literal.source]
    return (value ^ mask) if literal.inverted else value


def _canonical_phase(function: int, mask: int) -> tuple[int, bool]:
    complement = function ^ mask
    canonical = min(function, complement)
    return canonical, function != canonical


def _initial_state(
    input_count: int,
    library: Library,
    include_constant: bool,
    mask: int,
) -> _State:
    functions: dict[int, _Representative] = {}
    initial: list[tuple[int, Literal]] = []
    if include_constant:
        initial.append((0, Literal(0)))
    initial.extend(
        (_variable_truth_table(input_count, index), Literal(index + 1))
        for index in range(input_count)
    )
    for function, literal in initial:
        if library == "aig":
            key, inverted = _canonical_phase(function, mask)
            representative = Literal(literal.source, literal.inverted ^ inverted)
        else:
            key = function
            representative = literal
        functions.setdefault(key, _Representative(representative, 0))
    return _State(functions=functions, gates=())


def _expand_state(
    state: _State,
    input_count: int,
    library: Library,
    mask: int,
) -> Iterable[_State]:
    signals: list[tuple[int, Literal, int]] = []
    for function, representative in sorted(state.functions.items()):
        signals.append((function, representative.literal, representative.depth))
        if library == "aig":
            signals.append((function ^ mask, representative.literal.flipped(), representative.depth))
    signals.sort(key=lambda item: (item[0], item[1]))
    output_source = input_count + 1 + len(state.gates)

    for left, right in combinations_with_replacement(signals, 2):
        left_function, left_literal, left_depth = left
        right_function, right_literal, right_depth = right
        raw = left_function & right_function
        if library == "aig":
            result = raw
            key, inverted = _canonical_phase(result, mask)
            output_literal = Literal(output_source, inverted)
        else:
            result = raw ^ mask
            key = result
            output_literal = Literal(output_source)
        depth = max(left_depth, right_depth) + 1
        previous = state.functions.get(key)
        if previous is not None and previous.depth <= depth:
            continue
        functions = dict(state.functions)
        functions[key] = _Representative(output_literal, depth)
        yield _State(
            functions=functions,
            gates=state.gates + (Gate(left_literal, right_literal),),
        )


def _target_key(target: int, library: Library, mask: int) -> tuple[int, bool]:
    if library == "aig":
        return _canonical_phase(target, mask)
    return target, False


def _collect_solutions(
    states: Iterable[_State],
    input_count: int,
    targets: tuple[int, ...],
    library: Library,
    include_constant: bool,
    mask: int,
    found: dict[tuple[int, int], LogicNetwork],
) -> None:
    for state in states:
        keys = [_target_key(target, library, mask) for target in targets]
        if not all(key in state.functions for key, _ in keys):
            continue
        outputs = []
        for key, inverted in keys:
            literal = state.functions[key].literal
            outputs.append(literal.flipped() if inverted else literal)
        network = LogicNetwork(
            input_count=input_count,
            library=library,
            gates=state.gates,
            outputs=tuple(outputs),
            include_constant=include_constant,
        ).prune_unused()
        if network.truth_tables() != targets:
            raise RuntimeError("internal synthesis reconstruction mismatch")
        found.setdefault((network.gate_count, network.depth), network)


def _trim_states(
    states: dict[tuple[tuple[int, int], ...], _State],
    targets: tuple[int, ...],
    library: Library,
    mask: int,
    state_limit: int,
) -> dict[tuple[tuple[int, int], ...], _State]:
    def distance(state: _State) -> tuple[object, ...]:
        missing = 0
        hamming = 0
        functions = tuple(state.functions)
        for target in targets:
            key, _ = _target_key(target, library, mask)
            if key in state.functions:
                continue
            missing += 1
            if library == "aig":
                hamming += min(
                    min((function ^ target).bit_count(), ((function ^ mask) ^ target).bit_count())
                    for function in functions
                )
            else:
                hamming += min((function ^ target).bit_count() for function in functions)
        return missing, hamming, max(item.depth for item in state.functions.values()), state.key()

    kept = sorted(states.values(), key=distance)[:state_limit]
    return {state.key(): state for state in kept}


def _pareto_networks(networks: Iterable[LogicNetwork]) -> tuple[LogicNetwork, ...]:
    ordered = sorted(networks, key=lambda item: (item.gate_count, item.depth, item.output_depths()))
    result: list[LogicNetwork] = []
    for network in ordered:
        if any(
            previous.gate_count <= network.gate_count
            and previous.depth <= network.depth
            for previous in result
        ):
            continue
        result.append(network)
    return tuple(result)
