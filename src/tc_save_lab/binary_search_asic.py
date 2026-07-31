"""Generate and verify the current-version ASIC solution for Code Breaker."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path

from .builder import stable_permanent_id, wire_from_vertices
from .codec import decode_v15, encode_v15
from .model import Circuit, Component, Point
from .pins import I, O, T, analyze_connectivity, positioned_pins


WORD_BITS = 8
WORD_MAX = (1 << WORD_BITS) - 1
INITIAL_STATE = 0x7F
PRIMITIVE_GATE_COUNT = 37
STATE_DELAY_GATE_COST = 5
EXPECTED_GATE = PRIMITIVE_GATE_COUNT + WORD_BITS * STATE_DELAY_GATE_COST
EXPECTED_DELAY = 8
EXPECTED_MAXIMUM_CYCLES = 9
PUBLIC_LEADERBOARD = (92, 6, 9, 4968)
EXPECTED_TERMINALS = tuple((*range(0, WORD_MAX - 1, 2), WORD_MAX))


@dataclass(frozen=True)
class SearchPath:
    """One complete, reachable branch of the level's interval process."""

    feedback: tuple[int, ...]
    terminal: int
    guesses: tuple[int, ...]

    @property
    def cycles(self) -> int:
        return len(self.guesses)


@dataclass(frozen=True)
class GateDefinition:
    """One gate in the ABC area-mapped next-state network."""

    output: str
    kind: int
    fanins: tuple[str, ...]


# This is the 37-gate ABC mapping preserved in .research/binary-search-next-area.v.
# Signal s0 is the least-significant state bit and n0..n7 are the next-state bits.
GATE_DEFINITIONS = (
    GateDefinition("w08", 3, ("over",)),
    GateDefinition("w09", 4, ("s1", "s0")),
    GateDefinition("w10", 6, ("s1", "s0")),
    GateDefinition("w11", 4, ("s2", "w09")),
    GateDefinition("w12", 4, ("s3", "w11")),
    GateDefinition("w13", 6, ("s3", "w11")),
    GateDefinition("w14", 4, ("s4", "w12")),
    GateDefinition("w15", 6, ("s5", "w14")),
    GateDefinition("w16", 7, ("s7", "w15")),
    GateDefinition("w17", 6, ("s6", "w16")),
    GateDefinition("w18", 7, ("s6", "w15")),
    GateDefinition("w19", 7, ("over", "w18")),
    GateDefinition("n6", 6, ("w17", "w19")),
    GateDefinition("w20", 4, ("s0", "w08")),
    GateDefinition("w21", 4, ("w08", "w11")),
    GateDefinition("w22", 4, ("w08", "w14")),
    GateDefinition("w23", 7, ("s5", "w22")),
    GateDefinition("n5", 4, ("w18", "w23")),
    GateDefinition("w24", 7, ("s5", "w13")),
    GateDefinition("w25", 6, ("s4", "w24")),
    GateDefinition("w26", 7, ("s4", "w13")),
    GateDefinition("w27", 7, ("over", "w26")),
    GateDefinition("n4", 6, ("w25", "w27")),
    GateDefinition("w28", 7, ("s3", "w21")),
    GateDefinition("n3", 4, ("w26", "w28")),
    GateDefinition("w29", 7, ("s3", "w10")),
    GateDefinition("w30", 6, ("s2", "w29")),
    GateDefinition("w31", 7, ("s2", "w10")),
    GateDefinition("w32", 7, ("over", "w31")),
    GateDefinition("n2", 6, ("w30", "w32")),
    GateDefinition("w33", 7, ("s1", "w20")),
    GateDefinition("n1", 4, ("w31", "w33")),
    GateDefinition("w34", 7, ("s0", "over")),
    GateDefinition("n0", 6, ("w10", "w34")),
    GateDefinition("w35", 4, ("s6", "s5")),
    GateDefinition("w36", 4, ("w22", "w35")),
    GateDefinition("n7", 7, ("s7", "w36")),
)


def next_state(state: int, over: int) -> int:
    """Return the next balanced midpoint encoded by the reachable state word."""

    if not 0 <= state <= WORD_MAX:
        raise ValueError(f"state must be an unsigned byte, got {state}")
    if over not in (0, 1):
        raise ValueError(f"feedback must be 0 or 1, got {over}")

    # Reachable non-terminal words are a decision prefix, one zero delimiter,
    # and a suffix of ones.  The delimiter therefore identifies the only bit
    # that is set on an upward branch and the preceding bit cleared on either
    # branch.  This preserves feedback order instead of reversing it.
    delimiter = (state + 1) & ~state & WORD_MAX
    clear_previous = delimiter >> 1
    return ((state ^ clear_previous) | (delimiter if not over else 0)) & WORD_MAX


def evaluate_synthesized_next_state(state: int, over: int) -> int:
    """Evaluate the exact primitive-gate network used by the generated circuit."""

    if not 0 <= state <= WORD_MAX:
        raise ValueError(f"state must be an unsigned byte, got {state}")
    if over not in (0, 1):
        raise ValueError(f"feedback must be 0 or 1, got {over}")

    values = {"over": over}
    values.update({f"s{bit}": (state >> bit) & 1 for bit in range(WORD_BITS)})
    for gate in GATE_DEFINITIONS:
        inputs = tuple(values[name] for name in gate.fanins)
        if gate.kind == 3:
            result = 1 - inputs[0]
        elif gate.kind == 4:
            result = inputs[0] & inputs[1]
        elif gate.kind == 6:
            result = 1 - (inputs[0] & inputs[1])
        elif gate.kind == 7:
            result = inputs[0] | inputs[1]
        else:  # pragma: no cover - guarded by the reviewed constant table
            raise RuntimeError(f"unsupported mapped gate kind {gate.kind}")
        values[gate.output] = result
    return sum(values[f"n{bit}"] << bit for bit in range(WORD_BITS))


def enumerate_search_paths() -> tuple[SearchPath, ...]:
    """Exhaust every feedback path that the current ``test.si`` can produce."""

    paths: list[SearchPath] = []

    def visit(
        lower: int,
        upper: int,
        state: int,
        feedback: tuple[int, ...],
        guesses: tuple[int, ...],
    ) -> None:
        current_guesses = guesses + (state,)
        if lower == upper:
            if state != lower:
                raise RuntimeError(
                    f"terminal state mismatch: interval={lower}, state={state}"
                )
            paths.append(SearchPath(feedback, lower, current_guesses))
            return

        midpoint = (lower + upper) // 2
        if state != midpoint:
            raise RuntimeError(
                f"unbalanced guess for [{lower}, {upper}]: {state} != {midpoint}"
            )

        if state < upper:
            visit(
                state + 1,
                upper,
                next_state(state, 0),
                feedback + (0,),
                current_guesses,
            )
        if state > lower:
            visit(
                lower,
                state - 1,
                next_state(state, 1),
                feedback + (1,),
                current_guesses,
            )

    visit(0, WORD_MAX, INITIAL_STATE, (), ())
    return tuple(paths)


def _gate_depths() -> dict[str, int]:
    depths = {"over": 0, **{f"s{bit}": 0 for bit in range(WORD_BITS)}}
    for gate in GATE_DEFINITIONS:
        depths[gate.output] = max(depths[name] for name in gate.fanins) + 1
    return depths


def _pin(component: Component, name: str) -> Point:
    matches = [pin.position for pin in positioned_pins(component) if pin.name == name]
    if len(matches) != 1:
        raise RuntimeError(f"component kind {component.kind} has no unique pin {name!r}")
    return matches[0]


def _output_pin(component: Component) -> Point:
    matches = [
        pin.position
        for pin in positioned_pins(component)
        if pin.direction in {O, T}
    ]
    if len(matches) != 1:
        raise RuntimeError(f"component kind {component.kind} has no unique output")
    return matches[0]


def _route(source: Point, sink: Point) -> tuple[Point, ...]:
    if source == sink:
        raise RuntimeError(f"cannot route a zero-length connection at {source}")
    dx = sink[0] - source[0]
    dy = sink[1] - source[1]
    if dx == 0 or dy == 0 or abs(dx) == abs(dy):
        return source, sink
    return source, (sink[0], source[1]), sink


def build_binary_search_asic() -> Circuit:
    """Build the 37-gate balanced-search state machine using modern parts."""

    key = "architecture/codex-binary-search"

    def component(
        role: str,
        kind: int,
        position: tuple[int, int],
        **kwargs: object,
    ) -> Component:
        return Component(
            kind=kind,
            position=position,
            rotation=0,
            permanent_id=stable_permanent_id(key, role),
            **kwargs,
        )

    level_input = component("level-input", 62, (-40, -60), word_size=1)
    input_enable = component("input-enable", 2, (-41, -62))
    delay_components = {
        bit: component(
            f"state-bit-{bit}",
            13,
            (-20, bit * 10 - 35),
            init_data=int(bit < WORD_BITS - 1),
        )
        for bit in range(WORD_BITS)
    }
    state_maker = component("state-maker", 16, (105, 0))
    output_enable = component("output-enable", 2, (108, -2))
    level_output = component("level-output", 70, (111, 0), word_size=8)

    depths = _gate_depths()
    gates_by_depth: dict[int, list[GateDefinition]] = {}
    for gate in GATE_DEFINITIONS:
        gates_by_depth.setdefault(depths[gate.output], []).append(gate)

    gate_components: dict[str, Component] = {}
    for depth, gates in sorted(gates_by_depth.items()):
        y_origin = -((len(gates) - 1) * 6) // 2
        for index, gate in enumerate(gates):
            gate_components[gate.output] = component(
                f"gate-{gate.output}",
                gate.kind,
                (depth * 12, y_origin + index * 6),
            )

    components = (
        level_input,
        input_enable,
        *(delay_components[bit] for bit in range(WORD_BITS)),
        state_maker,
        output_enable,
        level_output,
        *(gate_components[gate.output] for gate in GATE_DEFINITIONS),
    )

    signal_sources = {"over": _pin(level_input, "value")}
    signal_sources.update(
        {f"s{bit}": _pin(delay_components[bit], "out") for bit in range(WORD_BITS)}
    )
    signal_sources.update(
        {name: _output_pin(gate) for name, gate in gate_components.items()}
    )

    wires = [
        wire_from_vertices(_route(_output_pin(input_enable), _pin(level_input, "control"))),
        wire_from_vertices(_route(_output_pin(output_enable), _pin(level_output, "control"))),
        wire_from_vertices(_route(_pin(state_maker, "out"), _pin(level_output, "value"))),
    ]
    for gate in GATE_DEFINITIONS:
        destination = gate_components[gate.output]
        input_names = ("in",) if gate.kind == 3 else ("in0", "in1")
        for fanin, input_name in zip(gate.fanins, input_names):
            wires.append(
                wire_from_vertices(
                    _route(signal_sources[fanin], _pin(destination, input_name))
                )
            )
    for bit in range(WORD_BITS):
        wires.append(
            wire_from_vertices(
                _route(signal_sources[f"s{bit}"], _pin(state_maker, f"in{bit}"))
            )
        )
        wires.append(
            wire_from_vertices(
                _route(signal_sources[f"n{bit}"], _pin(delay_components[bit], "in"))
            )
        )

    return Circuit(
        gate=EXPECTED_GATE,
        delay=EXPECTED_DELAY,
        description=(
            "Codex Code Breaker ASIC: balanced midpoint state machine, "
            "37 mapped gates and eight initialized state bits"
        ),
        components=components,
        wires=tuple(wires),
    )


def verify_binary_search_asic(circuit: Circuit | None = None) -> dict[str, object]:
    candidate = build_binary_search_asic() if circuit is None else circuit
    paths = enumerate_search_paths()
    terminals = [path.terminal for path in paths]
    if tuple(sorted(terminals)) != EXPECTED_TERMINALS:
        raise RuntimeError(
            "feedback tree does not match the reachable randomized terminal set"
        )

    transition_pairs: set[tuple[int, int]] = set()
    for path in paths:
        for state, over in zip(path.guesses, path.feedback):
            transition_pairs.add((state, over))
            synthesized = evaluate_synthesized_next_state(state, over)
            expected = next_state(state, over)
            if synthesized != expected:
                raise RuntimeError(
                    f"mapped transition mismatch: state={state}, over={over}, "
                    f"expected={expected}, got={synthesized}"
                )

    for state in range(WORD_MAX + 1):
        for over in (0, 1):
            synthesized = evaluate_synthesized_next_state(state, over)
            expected = next_state(state, over)
            if synthesized != expected:
                raise RuntimeError(
                    f"full-domain mapped mismatch: state={state}, over={over}, "
                    f"expected={expected}, got={synthesized}"
                )

    cycle_histogram = Counter(path.cycles for path in paths)
    if max(cycle_histogram) != EXPECTED_MAXIMUM_CYCLES:
        raise RuntimeError(f"cycle regression: {dict(cycle_histogram)!r}")

    connectivity = analyze_connectivity(candidate)
    for field in (
        "unsupported_component_kind_counts",
        "unconnected_pin_count",
        "multi_driver_network_count",
        "width_mismatch_network_count",
        "cycle_component_count",
    ):
        if connectivity[field]:
            raise RuntimeError(
                f"Code Breaker ASIC failed connectivity check {field}: "
                f"{connectivity[field]}"
            )

    kind_counts = Counter(component.kind for component in candidate.components)
    expected_logic_counts = Counter(gate.kind for gate in GATE_DEFINITIONS)
    actual_logic_counts = Counter(
        {kind: kind_counts[kind] for kind in expected_logic_counts}
    )
    if actual_logic_counts != expected_logic_counts:
        raise RuntimeError(
            f"mapped primitive count changed: {actual_logic_counts!r} != "
            f"{expected_logic_counts!r}"
        )
    if kind_counts[13] != WORD_BITS or kind_counts[78]:
        raise RuntimeError(f"unexpected state/custom components: {kind_counts!r}")
    if candidate.dependencies:
        raise RuntimeError("Code Breaker ASIC must not depend on an old architecture")
    if (candidate.gate, candidate.delay) != (EXPECTED_GATE, EXPECTED_DELAY):
        raise RuntimeError(
            f"candidate metric declaration changed: {candidate.gate}/{candidate.delay}"
        )

    return {
        "gate": candidate.gate,
        "delay": candidate.delay,
        "minimum_cycles": min(cycle_histogram),
        "maximum_cycles": max(cycle_histogram),
        "cycle_histogram": dict(sorted(cycle_histogram.items())),
        "terminal_count": len(paths),
        "verified_transition_count": len(transition_pairs),
        "full_domain_vector_count": (WORD_MAX + 1) * 2,
        "leaderboard_tuple": [candidate.gate, candidate.delay, max(cycle_histogram)],
        "energy": candidate.gate * candidate.delay * max(cycle_histogram),
        "public_leaderboard_reference": list(PUBLIC_LEADERBOARD),
        "component_kind_counts": dict(sorted(kind_counts.items())),
        "connectivity": connectivity,
    }


def write_binary_search_asic(project_root: Path) -> dict[str, object]:
    candidate = build_binary_search_asic()
    verification = verify_binary_search_asic(candidate)
    payload = encode_v15(candidate)
    if decode_v15(payload) != candidate:
        raise RuntimeError("Code Breaker ASIC failed v15 round-trip verification")

    destination = (
        project_root / "examples" / "binary_search" / "candidate" / "circuit.data"
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(payload)
    metadata = {
        "schema": 1,
        "level": "binary_search",
        "title": "Code Breaker",
        "strategy": "current-v15 balanced-midpoint finite-state ASIC",
        "validation_status": "offline-verified; game runtime and scoring pending",
        "deployment_target": "schematics/architecture/CODEX-BINARY-SEARCH/circuit.data",
        "sha256": sha256(payload).hexdigest(),
        "format_version": 15,
        "component_count": len(candidate.components),
        "wire_count": len(candidate.wires),
        **verification,
    }
    (destination.parent / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return metadata
