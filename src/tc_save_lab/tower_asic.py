"""Offline proof tooling for the single-I/O Tower of Hanoi ASIC target.

This module intentionally does not emit ``examples/tower/candidate/circuit.data``.
The game callback behind an Architecture Input is stateful, and the remaining
counter/logic layout has not yet been proven against the current executable.
Instead this file freezes the behavior that a deployable circuit must satisfy:

* exactly one sequential Architecture Input and one Architecture Output;
* four input reads at ticks 0..3;
* 124 useful output callbacks in the five-disk case, at ticks 1..124;
* a formula-based, non-recursive minimal Hanoi sequence for every test case.

The small v15 probe is deliberately non-deployable.  It exists only to keep
the reviewed codec, pin, and real-sprite geometry paths exercised while the
full state network is still under construction.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
import struct
from typing import Iterable, Sequence
import zlib

from .analysis import wire_points
from .builder import stable_permanent_id, wire_from_vertices
from .codec import decode_v15, encode_v15
from .model import Circuit, Component, Point
from .pins import analyze_connectivity, positioned_pins, rotate_offset
from .simulate import SimulationError, simulate_clocked_trace


ARCHITECTURE_INPUT_KIND = 62
ARCHITECTURE_OUTPUT_KIND = 70
PIXELS_PER_GRID_CELL = 20
DEFAULT_COMPONENT_SPRITE_ROOT = Path(
    r"D:\Game\Steam\steamapps\common\Turing Complete\asset\component_sprites"
)

# Only the components that a future first-party Tower implementation is
# allowed to use are mapped here.  Adding a component requires a reviewed pin
# schema and its current sprite name, rather than silently falling back to a
# rectangle.
SPRITE_NAME_BY_COMPONENT_KIND: dict[int, str] = {
    1: "com_constant.png",
    2: "com_constant.png",
    3: "com_not_bit.png",
    4: "com_and_bit.png",
    5: "com_and_3_bit.png",
    6: "com_nand_bit.png",
    7: "com_or_bit.png",
    8: "com_or_3_bit.png",
    9: "com_nor_bit.png",
    10: "com_xor_bit.png",
    13: "com_delay_line_bit.png",
    15: "com_full_adder.png",
    16: "com_maker_bit_8.png",
    17: "com_splitter_bit_8.png",
    25: "com_switch_word.png",
    30: "com_add.png",
    46: "com_constant.png",
    55: "com_delay_line_word.png",
    62: "com_cc_level_input.png",
    70: "com_cc_level_output.png",
}


class TowerVerificationError(RuntimeError):
    """Raised when an asserted Tower protocol or geometry invariant fails."""


class PngAlphaError(ValueError):
    """Raised when a current component sprite cannot be decoded safely."""


@dataclass(frozen=True)
class TowerCase:
    """One of the 18 semantically distinct input combinations in ``tower``."""

    highest_disk: int
    source: int
    destination: int

    def __post_init__(self) -> None:
        if self.highest_disk not in {2, 3, 4}:
            raise ValueError("tower highest_disk must be 2, 3, or 4")
        if self.source not in {0, 1, 2}:
            raise ValueError("tower source must be a peg in 0..2")
        if self.destination not in {0, 1, 2}:
            raise ValueError("tower destination must be a peg in 0..2")
        if self.source == self.destination:
            raise ValueError("tower source and destination must differ")

    @property
    def disk_count(self) -> int:
        return self.highest_disk + 1

    @property
    def spare(self) -> int:
        return 3 - self.source - self.destination

    @property
    def input_stream(self) -> tuple[int, int, int, int]:
        """Match ``arch_get_input`` in the live ``campaign/tower/test.si``."""

        return (self.highest_disk, self.source, self.destination, self.spare)


@dataclass(frozen=True)
class TowerMove:
    """One semantic disk move, using disk zero for the smallest disk."""

    number: int
    disk: int
    source: int
    destination: int


@dataclass(frozen=True)
class TowerTick:
    """One architecture tick under the safe single-I/O schedule."""

    tick: int
    input_control: int
    input_index: int | None
    input_value: int | None
    output_control: int
    output_value: int | None
    action_index: int | None
    move_number: int | None
    phase: str | None
    required_input_indexes: tuple[int, ...]


@dataclass(frozen=True)
class TowerLevelResult:
    """Result of replaying output values through ``tower/test.si`` semantics."""

    commands: tuple[int, ...]
    plates: tuple[int, ...]
    magnet_position: int
    lifted_disk: int | None
    failed: bool
    first_win_event: int | None
    lifted_disks: tuple[int, ...]
    dropped_disks: tuple[int, ...]
    empty_lift_count: int
    invalid_commands: tuple[int, ...]

    @property
    def won(self) -> bool:
        return self.first_win_event is not None and not self.failed


@dataclass(frozen=True)
class TowerProtocolTrace:
    """Verified event trace, not a serialized game circuit."""

    case: TowerCase
    moves: tuple[TowerMove, ...]
    ticks: tuple[TowerTick, ...]
    commands: tuple[int, ...]
    level_result: TowerLevelResult

    @property
    def cycle_count(self) -> int:
        return len(self.ticks)


@dataclass(frozen=True)
class SpriteWireCollision:
    """A wire point that touches opaque sprite alpha away from a wire endpoint."""

    wire_index: int
    component_index: int
    point: Point
    component_kind: int
    endpoint: bool
    pin_names: tuple[str, ...]


@dataclass(frozen=True)
class SpriteGeometryAudit:
    """Alpha-based geometry report for a current-version circuit candidate."""

    sprite_files: tuple[str, ...]
    alpha_cell_count: int
    unsupported_component_kinds: tuple[int, ...]
    component_overlap_cells: tuple[Point, ...]
    wire_collisions: tuple[SpriteWireCollision, ...]

    @property
    def is_safe(self) -> bool:
        return not (
            self.unsupported_component_kinds
            or self.component_overlap_cells
            or self.wire_collisions
        )


def ctz(value: int) -> int:
    """Return the number of trailing zeroes in a positive integer."""

    if value <= 0:
        raise ValueError("ctz is defined here only for positive integers")
    return (value & -value).bit_length() - 1


def ctz_parity_from_action_counter(action_counter: int) -> int:
    """Return ``ctz(action_counter + 1) & 1`` using the verified five-bit form.

    A five-disk Tower run has action counters 0..123.  The move counter is the
    high five bits, so the relevant ``k = move - 1`` range is 0..30.  This
    Boolean expression avoids treating a general CTZ component as reviewed.
    """

    move_counter = action_counter >> 2
    if not 0 <= move_counter <= 30:
        raise ValueError("tower action counter must address move counters 0..30")
    bit0 = move_counter & 1
    bit1 = (move_counter >> 1) & 1
    bit2 = (move_counter >> 2) & 1
    bit3 = (move_counter >> 3) & 1
    return bit0 & ((1 - bit1) | (bit2 & (1 - bit3)))


def recursive_moves(
    disk_count: int,
    source: int,
    destination: int,
    spare: int,
) -> tuple[TowerMove, ...]:
    """Independent recursive reference implementation of the optimal sequence."""

    if disk_count < 1:
        raise ValueError("tower needs at least one disk")
    if {source, destination, spare} != {0, 1, 2}:
        raise ValueError("tower pegs must be exactly 0, 1, and 2")
    result: list[TowerMove] = []

    def visit(count: int, start: int, target: int, auxiliary: int) -> None:
        if count == 0:
            return
        visit(count - 1, start, auxiliary, target)
        result.append(
            TowerMove(
                number=len(result) + 1,
                disk=count - 1,
                source=start,
                destination=target,
            )
        )
        visit(count - 1, auxiliary, target, start)

    visit(disk_count, source, destination, spare)
    return tuple(result)


def formula_moves(case: TowerCase) -> tuple[TowerMove, ...]:
    """Generate the optimal sequence without a stack or recursion.

    The move formula operates on a virtual three-peg ring.  Its mapping makes
    the smallest disk move toward the destination for odd disk counts and
    toward the spare peg for even disk counts, exactly matching the recursive
    problem requested by the level.
    """

    virtual_pegs = (
        (case.source, case.spare, case.destination)
        if case.disk_count % 2
        else (case.source, case.destination, case.spare)
    )
    result: list[TowerMove] = []
    for move_number in range(1, 1 << case.disk_count):
        parity = ctz(move_number) & 1
        virtual_from = (move_number + 2 - parity) % 3
        virtual_to = (move_number + 1 + parity) % 3
        result.append(
            TowerMove(
                number=move_number,
                disk=ctz(move_number),
                source=virtual_pegs[virtual_from],
                destination=virtual_pegs[virtual_to],
            )
        )
    return tuple(result)


def commands_from_moves(moves: Iterable[TowerMove]) -> tuple[int, ...]:
    """Expand every disk move into the level's four magnet commands."""

    commands: list[int] = []
    for move in moves:
        commands.extend((move.source, 5, move.destination, 5))
    return tuple(commands)


def _level_has_won(case: TowerCase, plates: Sequence[int]) -> bool:
    """Mirror the deliberately unusual early-return win check in ``test.si``."""

    for position in plates:
        if position == -1:
            return True
        if position != case.destination:
            return False
    return True


def simulate_tower_script(
    case: TowerCase,
    commands: Iterable[int],
) -> TowerLevelResult:
    """Replay commands using the state transitions in ``campaign/tower/test.si``.

    This is intentionally an event-level model, not a convenience Hanoi
    solver.  It keeps the magnet and the exact smaller-disk drop check so that
    a syntactically plausible but physically invalid command stream fails.
    """

    sequence = tuple(commands)
    plates = [case.source] * case.disk_count + [-1] * (5 - case.disk_count)
    magnet_position = 0
    lifted_disk: int | None = None
    failed = False
    first_win_event: int | None = None
    lifted_disks: list[int] = []
    dropped_disks: list[int] = []
    empty_lift_count = 0
    invalid_commands: list[int] = []

    for event_number, command in enumerate(sequence, start=1):
        if command in {0, 1, 2}:
            magnet_position = command
        elif command == 5:
            if lifted_disk is None:
                candidate = next(
                    (index for index, position in enumerate(plates) if position == magnet_position),
                    None,
                )
                if candidate is None:
                    empty_lift_count += 1
                else:
                    lifted_disk = candidate
                    lifted_disks.append(candidate)
            else:
                if any(plates[index] == magnet_position for index in range(lifted_disk)):
                    failed = True
                plates[lifted_disk] = magnet_position
                dropped_disks.append(lifted_disk)
                lifted_disk = None
        else:
            # The source script's switch has no default branch.  The ASIC
            # contract is stricter: a candidate must never emit such a value.
            invalid_commands.append(command)

        if failed:
            break
        if first_win_event is None and _level_has_won(case, plates):
            first_win_event = event_number

    return TowerLevelResult(
        commands=sequence,
        plates=tuple(plates),
        magnet_position=magnet_position,
        lifted_disk=lifted_disk,
        failed=failed,
        first_win_event=first_win_event,
        lifted_disks=tuple(lifted_disks),
        dropped_disks=tuple(dropped_disks),
        empty_lift_count=empty_lift_count,
        invalid_commands=tuple(invalid_commands),
    )


def _required_input_indexes(
    case: TowerCase,
    move: TowerMove,
    phase_index: int,
) -> tuple[int, ...]:
    """State the earliest data dependency for an event in the 125-cycle plan."""

    if phase_index in {1, 3}:
        return ()
    if move.number == 1 and phase_index == 0:
        # Tick 1 can directly consume source and emit the first FROM command.
        return (1,)
    if move.number == 1 and phase_index == 2:
        # Tick 3 uses the stored destination (odd N) or the just-read spare
        # (even N), plus the disk-count parity captured at tick 0.
        return (0, 2) if case.disk_count % 2 else (0, 3)
    return (0, 1, 2, 3)


def build_tower_protocol_candidate(case: TowerCase) -> TowerProtocolTrace:
    """Build and validate the deterministic, single-I/O event candidate.

    The returned object is a protocol candidate only.  It is deliberately
    separate from ``Circuit`` so callers cannot accidentally install it as a
    game save before a full physical implementation exists.
    """

    moves = formula_moves(case)
    commands = commands_from_moves(moves)
    ticks: list[TowerTick] = []
    known_input_indexes: set[int] = set()
    input_cursor = 0

    for tick in range(len(commands) + 1):
        input_control = int(tick < 4)
        input_index: int | None = None
        input_value: int | None = None
        if input_control:
            input_index = input_cursor
            input_value = case.input_stream[input_cursor]
            known_input_indexes.add(input_cursor)
            input_cursor += 1

        if tick == 0:
            ticks.append(
                TowerTick(
                    tick=tick,
                    input_control=input_control,
                    input_index=input_index,
                    input_value=input_value,
                    output_control=0,
                    output_value=None,
                    action_index=None,
                    move_number=None,
                    phase=None,
                    required_input_indexes=(),
                )
            )
            continue

        action_index = tick - 1
        phase_index = action_index & 3
        move = moves[action_index >> 2]
        required = _required_input_indexes(case, move, phase_index)
        if not set(required).issubset(known_input_indexes):
            raise TowerVerificationError(
                f"tick {tick} emitted before reading required Tower inputs {required}"
            )
        ticks.append(
            TowerTick(
                tick=tick,
                input_control=input_control,
                input_index=input_index,
                input_value=input_value,
                output_control=1,
                output_value=commands[action_index],
                action_index=action_index,
                move_number=move.number,
                phase=("from", "lift", "to", "drop")[phase_index],
                required_input_indexes=required,
            )
        )

    if input_cursor != 4:
        raise TowerVerificationError(f"tower input cursor ended at {input_cursor}, expected 4")
    level_result = simulate_tower_script(case, commands)
    return TowerProtocolTrace(
        case=case,
        moves=moves,
        ticks=tuple(ticks),
        commands=commands,
        level_result=level_result,
    )


def all_tower_cases() -> tuple[TowerCase, ...]:
    """Return all inputs the random level generator can supply semantically."""

    return tuple(
        TowerCase(highest_disk=highest_disk, source=source, destination=destination)
        for highest_disk in (2, 3, 4)
        for source in range(3)
        for destination in range(3)
        if source != destination
    )


def verify_tower_event_model() -> dict[str, object]:
    """Exhaustively prove the protocol trace for all 18 level input cases."""

    expected_events = {3: 28, 4: 60, 5: 124}
    expected_cycles = {3: 29, 4: 61, 5: 125}
    summaries: list[dict[str, int]] = []

    for case in all_tower_cases():
        reference = recursive_moves(
            case.disk_count,
            case.source,
            case.destination,
            case.spare,
        )
        candidate = formula_moves(case)
        if candidate != reference:
            raise TowerVerificationError(
                f"formula sequence differs from recursive reference for {case!r}"
            )
        trace = build_tower_protocol_candidate(case)
        event_count = expected_events[case.disk_count]
        if len(trace.moves) != (1 << case.disk_count) - 1:
            raise TowerVerificationError("tower move count is not minimal")
        if len(trace.commands) != event_count:
            raise TowerVerificationError("tower output event count regression")
        if trace.cycle_count != expected_cycles[case.disk_count]:
            raise TowerVerificationError("tower cycle count regression")
        if tuple(tick.input_value for tick in trace.ticks[:4]) != case.input_stream:
            raise TowerVerificationError("tower input read order regression")
        if any(tick.input_control != int(tick.tick < 4) for tick in trace.ticks):
            raise TowerVerificationError("tower input control is not exact 0/1 scheduling")
        if trace.ticks[0].output_control != 0:
            raise TowerVerificationError("tower must not output during the first input read")
        if any(tick.output_control != 1 for tick in trace.ticks[1:]):
            raise TowerVerificationError("tower must output exactly once per active tick")
        if any(command not in {0, 1, 2, 5} for command in trace.commands):
            raise TowerVerificationError("tower emitted an unsupported magnet command")
        if trace.level_result.failed:
            raise TowerVerificationError("tower protocol caused an illegal disk drop")
        if trace.level_result.empty_lift_count:
            raise TowerVerificationError("tower protocol toggled an empty magnet")
        if trace.level_result.invalid_commands:
            raise TowerVerificationError("tower protocol emitted an invalid command")
        if trace.level_result.lifted_disk is not None:
            raise TowerVerificationError("tower protocol ended while holding a disk")
        if trace.level_result.first_win_event != event_count:
            raise TowerVerificationError("tower did not win exactly on its final output event")
        if trace.level_result.plates[: case.disk_count] != (case.destination,) * case.disk_count:
            raise TowerVerificationError("tower disks did not all reach the destination")
        if len(trace.level_result.lifted_disks) != len(trace.moves):
            raise TowerVerificationError("tower lift count does not match move count")
        if len(trace.level_result.dropped_disks) != len(trace.moves):
            raise TowerVerificationError("tower drop count does not match move count")
        for action_counter in range(event_count):
            expected_parity = ctz((action_counter >> 2) + 1) & 1
            actual_parity = ctz_parity_from_action_counter(action_counter)
            if actual_parity != expected_parity:
                raise TowerVerificationError("tower CTZ parity reduction regression")
        summaries.append(
            {
                "highest_disk": case.highest_disk,
                "source": case.source,
                "destination": case.destination,
                "moves": len(trace.moves),
                "events": len(trace.commands),
                "cycles": trace.cycle_count,
            }
        )

    if len(summaries) != 18:
        raise TowerVerificationError("tower test domain is not exhaustive")
    return {
        "case_count": len(summaries),
        "event_counts": expected_events,
        "cycle_counts": expected_cycles,
        "maximum_cycles": 125,
        "single_architecture_input": True,
        "single_architecture_output": True,
        "candidate_status": "protocol-only; no deployable v15 circuit emitted",
        "cases": summaries,
    }


TOWER_COUNTER_BITS = 7
TOWER_DELAY_BITS = 13
TOWER_MAXIMUM_CYCLES = 125


@dataclass(frozen=True)
class TowerFsmState:
    """The compact persistent state used by the deployable Tower design.

    ``orientation`` temporarily holds ``highest_disk & 1`` while the first
    four Architecture Input reads are in flight.  At action counter three it
    is replaced in-place by the signed physical-ring direction.  This reuse is
    what keeps the implementation at thirteen Delay Bit components.
    """

    counter: int = 0
    source: int = 0
    peg: int = 0
    orientation: int = 0
    ctz_parity: int = 0

    def __post_init__(self) -> None:
        if not 0 <= self.counter < (1 << TOWER_COUNTER_BITS):
            raise ValueError("Tower action counter must fit in seven bits")
        if self.source not in {0, 1, 2}:
            raise ValueError("Tower source must be a physical peg")
        if self.peg not in {0, 1, 2}:
            raise ValueError("Tower virtual-ring peg must be a physical peg")
        if self.orientation not in {0, 1}:
            raise ValueError("Tower orientation must be one bit")
        if self.ctz_parity not in {0, 1}:
            raise ValueError("Tower CTZ parity must be one bit")


@dataclass(frozen=True)
class TowerFsmTick:
    """One reference-model tick, including the architecture callback event."""

    before: TowerFsmState
    after: TowerFsmState
    input_value: int | None
    output_value: int | None


def _step_peg(peg: int, plus: int) -> int:
    """Move one step around the three physical pegs without using modulo parts."""

    if peg not in {0, 1, 2} or plus not in {0, 1}:
        raise ValueError("Tower peg step requires a legal peg and direction bit")
    return (peg + (1 if plus else -1)) % 3


def _direction_plus(source: int, next_peg: int) -> int:
    """Return whether ``next_peg`` is source plus one modulo three."""

    if source not in {0, 1, 2} or next_peg not in {0, 1, 2} or source == next_peg:
        raise ValueError("Tower direction needs two distinct legal pegs")
    return int(next_peg == (source + 1) % 3)


def advance_tower_fsm(state: TowerFsmState, input_value: int | None) -> TowerFsmTick:
    """Advance the compressed state machine for exactly one game tick.

    This is intentionally independent from ``formula_moves``.  It proves the
    finite-state formulation before the same equations are lowered to gates.
    ``input_value`` is required only while the architecture input control is
    asserted, i.e. counters zero through three.
    """

    counter = state.counter
    reads_input = counter < 4
    if reads_input:
        if input_value is None or not 0 <= input_value <= 0xFF:
            raise ValueError("Tower FSM needs one U8 value during its first four ticks")
    elif input_value is not None:
        raise ValueError("Tower FSM must not consume an input after tick three")

    output: int | None
    if counter == 0:
        output = None
    elif counter & 3 == 1:
        if counter == 1:
            output = input_value
        else:
            to_plus = state.orientation ^ state.ctz_parity
            output = _step_peg(state.peg, 1 - to_plus)
    elif counter & 3 == 2:
        output = 5
    elif counter & 3 == 3:
        if counter == 3:
            # At counter three peg holds destination; live input is spare.
            output = input_value if state.orientation else state.peg
        else:
            output = _step_peg(state.peg, state.orientation ^ state.ctz_parity)
    else:
        output = 5

    next_source = input_value if counter == 1 else state.source
    if counter == 0:
        next_orientation = input_value & 1
    elif counter == 3:
        first_virtual_peg = state.peg if state.orientation else input_value
        next_orientation = _direction_plus(state.source, first_virtual_peg)
    else:
        next_orientation = state.orientation

    if counter == 2:
        next_peg = input_value
    elif counter == 3:
        # Odd disk count: V[1] is spare.  Even disk count: V[1] is destination.
        next_peg = state.peg if state.orientation else input_value
    elif counter and counter & 3 == 0:
        next_peg = _step_peg(state.peg, state.orientation)
    else:
        next_peg = state.peg

    if counter & 3 == 0:
        next_parity = ctz((counter >> 2) + 1) & 1
    else:
        next_parity = state.ctz_parity

    after = TowerFsmState(
        counter=(counter + 1) & ((1 << TOWER_COUNTER_BITS) - 1),
        source=next_source,
        peg=next_peg,
        orientation=next_orientation,
        ctz_parity=next_parity,
    )
    return TowerFsmTick(
        before=state,
        after=after,
        input_value=input_value if reads_input else None,
        output_value=output,
    )


def verify_tower_fsm_model() -> dict[str, object]:
    """Exhaustively compare the compressed FSM against all Tower scripts."""

    summaries: list[dict[str, int]] = []
    for case in all_tower_cases():
        expected = commands_from_moves(formula_moves(case))
        state = TowerFsmState()
        emitted: list[int] = []
        for tick in range(len(expected) + 1):
            value = case.input_stream[tick] if tick < 4 else None
            transition = advance_tower_fsm(state, value)
            if transition.output_value is not None:
                emitted.append(transition.output_value)
            state = transition.after
        if tuple(emitted) != expected:
            raise TowerVerificationError(
                f"compressed Tower FSM diverges from formula for {case!r}"
            )
        result = simulate_tower_script(case, emitted)
        if not result.won or result.first_win_event != len(expected):
            raise TowerVerificationError(f"compressed Tower FSM does not win for {case!r}")
        summaries.append(
            {
                "highest_disk": case.highest_disk,
                "source": case.source,
                "destination": case.destination,
                "cycles": len(expected) + 1,
            }
        )
    return {
        "case_count": len(summaries),
        "delay_bits": TOWER_DELAY_BITS,
        "maximum_cycles": max(item["cycles"] for item in summaries),
        "cases": summaries,
    }


@dataclass(frozen=True)
class _TowerGate:
    signal: str
    kind: int
    fanins: tuple[str, ...]


class _TowerBooleanNet:
    """Small structurally-hashed U1 network used by the physical Tower ASIC."""

    def __init__(self) -> None:
        self.gates: list[_TowerGate] = []
        self._cache: dict[tuple[int, tuple[str, ...]], str] = {}
        self._depth: dict[str, int] = {}

    def gate(self, kind: int, *fanins: str) -> str:
        if kind not in {3, 4, 7, 10}:
            raise ValueError(f"unreviewed Tower primitive kind {kind}")
        if kind == 3:
            if len(fanins) != 1:
                raise ValueError("NOT gate needs exactly one fanin")
            normalized = fanins
        else:
            if len(fanins) != 2:
                raise ValueError("binary Tower gate needs exactly two fanins")
            normalized = tuple(sorted(fanins))
        key = (kind, normalized)
        cached = self._cache.get(key)
        if cached is not None:
            return cached
        signal = f"g{len(self.gates):03d}"
        self.gates.append(_TowerGate(signal, kind, normalized))
        self._cache[key] = signal
        self._depth[signal] = max((self._depth.get(value, 0) for value in normalized), default=0) + 1
        return signal

    def not_(self, value: str) -> str:
        return self.gate(3, value)

    def and_(self, left: str, right: str) -> str:
        return self.gate(4, left, right)

    def or_(self, left: str, right: str) -> str:
        return self.gate(7, left, right)

    def xor_(self, left: str, right: str) -> str:
        return self.gate(10, left, right)

    def and_many(self, values: Sequence[str]) -> str:
        if not values:
            raise ValueError("Tower AND reduction cannot be empty")
        result = values[0]
        for value in values[1:]:
            result = self.and_(result, value)
        return result

    def or_many(self, values: Sequence[str]) -> str:
        if not values:
            raise ValueError("Tower OR reduction cannot be empty")
        result = values[0]
        for value in values[1:]:
            result = self.or_(result, value)
        return result

    def mux(self, select: str, when_zero: str, when_one: str) -> str:
        """Return ``when_zero`` for zero select and ``when_one`` for one."""

        if when_zero == when_one:
            return when_zero
        return self.or_(
            self.and_(self.not_(select), when_zero),
            self.and_(select, when_one),
        )

    def depth(self, signal: str) -> int:
        return self._depth.get(signal, 0)

    def prune(self, roots: Iterable[str]) -> None:
        """Discard structurally-created nodes that no final connection uses."""

        by_signal = {gate.signal: gate for gate in self.gates}
        live: set[str] = set()
        pending = list(roots)
        while pending:
            signal = pending.pop()
            if signal in live:
                continue
            gate = by_signal.get(signal)
            if gate is None:
                continue
            live.add(signal)
            pending.extend(gate.fanins)
        self.gates = [gate for gate in self.gates if gate.signal in live]


@dataclass(frozen=True)
class _TowerSwitch:
    role: str
    enable: str
    value: str
    destination: str
    word_size: int = 1


def _tower_pin(component: Component, name: str) -> Point:
    matches = [pin.position for pin in positioned_pins(component) if pin.name == name]
    if len(matches) != 1:
        raise TowerVerificationError(
            f"Tower component {component.permanent_id} has no unique pin {name!r}"
        )
    return matches[0]


def _tower_escape_point(component: Component, pin: Point, *, distance: int = 8) -> Point:
    """Choose a direction that is accepted by the current sprite alpha audit."""

    step = (
        _sign(pin[0] - component.position[0]),
        _sign(pin[1] - component.position[1]),
    )
    if step == (0, 0):
        raise TowerVerificationError("Tower route endpoint cannot be at component centre")
    return (pin[0] + step[0] * distance, pin[1] + step[1] * distance)


def _tower_safe_wire(
    source_component: Component,
    source_pin: str,
    sink_component: Component,
    sink_pin: str,
    *,
    lane_y: int,
    left_bus_x: int,
    right_bus_x: int,
):
    """Route through private outer bus lanes, never through a component row.

    Every part is allocated a distinct 20-cell horizontal band.  The first and
    final eight cells follow the actual pin's outward alpha escape ray; the
    rest of the path stays in shared outer aisles.  Wires may cross each other,
    but no wire can cross another component or a non-endpoint pin.
    """

    source = _tower_pin(source_component, source_pin)
    sink = _tower_pin(sink_component, sink_pin)
    source_exit = _tower_escape_point(source_component, source)
    sink_entry = _tower_escape_point(sink_component, sink)
    return wire_from_vertices(
        (
            source,
            source_exit,
            (right_bus_x, source_exit[1]),
            (right_bus_x, lane_y),
            (left_bus_x, lane_y),
            (left_bus_x, sink_entry[1]),
            sink_entry,
            sink,
        )
    )


def _tower_step_logic(net: _TowerBooleanNet, peg: tuple[str, str], plus: str) -> tuple[str, str]:
    """Lower a physical ``+/- 1 mod 3`` peg step to reviewed bit gates."""

    peg0, peg1 = peg
    not_peg0 = net.not_(peg0)
    not_peg1 = net.not_(peg1)
    is_zero = net.and_(not_peg0, not_peg1)
    plus0 = is_zero
    plus1 = net.and_(not_peg1, peg0)
    minus0 = net.and_(peg1, not_peg0)
    minus1 = is_zero
    return (
        net.mux(plus, minus0, plus0),
        net.mux(plus, minus1, plus1),
    )


def _tower_direction_logic(
    net: _TowerBooleanNet,
    source: tuple[str, str],
    next_peg: tuple[str, str],
) -> str:
    """Lower ``next_peg == source + 1 (mod 3)`` to a compact equality test."""

    source0, source1 = source
    not_source0 = net.not_(source0)
    not_source1 = net.not_(source1)
    source_plus = (
        net.and_(not_source0, not_source1),
        net.and_(not_source1, source0),
    )
    matches = (
        net.not_(net.xor_(source_plus[0], next_peg[0])),
        net.not_(net.xor_(source_plus[1], next_peg[1])),
    )
    return net.and_(matches[0], matches[1])


def build_tower_fsm_asic() -> Circuit:
    """Build the current-version, single-I/O 125-cycle Tower ASIC.

    The candidate is intentionally a direct finite-state machine, not an old
    architecture or a recursive program.  It has one U8 Architecture Input,
    one U8 Architecture Output, exactly four input callbacks, and only
    reviewed Delay Bit, Switch Word, splitter/maker, and basic U1 gates.
    """

    key = "architecture/codex-tower-fsm-v1"
    net = _TowerBooleanNet()
    counter = tuple(f"c{bit}" for bit in range(TOWER_COUNTER_BITS))
    source = ("source0", "source1")
    peg = ("peg0", "peg1")
    orientation = "orientation"
    parity = "ctz-parity"
    input_bits = tuple(f"input{bit}" for bit in range(8))

    not_counter = tuple(net.not_(value) for value in counter)
    high_zero = net.and_many(not_counter[2:])
    equal_zero = net.and_many((not_counter[0], not_counter[1], high_zero))
    equal_one = net.and_many((counter[0], not_counter[1], high_zero))
    equal_two = net.and_many((not_counter[0], counter[1], high_zero))
    equal_three = net.and_many((counter[0], counter[1], high_zero))
    output_enable = net.not_(equal_zero)
    fallback_enable = net.not_(high_zero)
    phase_from = net.and_(counter[0], not_counter[1])
    phase_to = net.and_(counter[0], counter[1])
    phase_move = net.or_(phase_from, phase_to)
    phase_drop = net.and_(not_counter[0], not_counter[1])
    state_update = net.and_(phase_drop, output_enable)

    counter_next: list[str] = [not_counter[0]]
    carry = counter[0]
    for bit in range(1, TOWER_COUNTER_BITS):
        counter_next.append(net.xor_(counter[bit], carry))
        if bit + 1 < TOWER_COUNTER_BITS:
            carry = net.and_(counter[bit], carry)

    peg_v1 = (
        net.mux(orientation, input_bits[0], peg[0]),
        net.mux(orientation, input_bits[1], peg[1]),
    )
    first_to = (
        net.mux(orientation, peg[0], input_bits[0]),
        net.mux(orientation, peg[1], input_bits[1]),
    )
    orientation_next = _tower_direction_logic(net, source, peg_v1)
    peg_after_drop = _tower_step_logic(net, peg, orientation)
    q_next = net.and_(
        counter[2],
        net.or_(not_counter[3], net.and_(counter[4], not_counter[5])),
    )
    to_plus = net.xor_(orientation, parity)
    from_plus = net.not_(to_plus)
    generic_from = _tower_step_logic(net, peg, from_plus)
    generic_to = _tower_step_logic(net, peg, to_plus)
    command_from = (
        net.mux(equal_one, generic_from[0], input_bits[0]),
        net.mux(equal_one, generic_from[1], input_bits[1]),
    )
    command_to = (
        net.mux(equal_three, generic_to[0], first_to[0]),
        net.mux(equal_three, generic_to[1], first_to[1]),
    )
    selected_peg = (
        net.mux(phase_to, command_from[0], command_to[0]),
        net.mux(phase_to, command_from[1], command_to[1]),
    )
    command0 = net.mux(phase_move, "one", selected_peg[0])
    command1 = net.or_(
        net.and_(phase_from, command_from[1]),
        net.and_(phase_to, command_to[1]),
    )
    command2 = net.not_(phase_move)
    unused_input = net.or_many(input_bits[2:])
    forced_zero = net.and_(unused_input, "zero")

    switches = [
        _TowerSwitch("input-fallback", fallback_enable, "word-zero", "input-splitter", 8),
        *(
            _TowerSwitch(
                f"source-{bit}-input",
                equal_one,
                input_bits[bit],
                f"source-{bit}-delay",
            )
            for bit in range(2)
        ),
        *(
            _TowerSwitch(
                f"source-{bit}-feedback",
                net.not_(equal_one),
                source[bit],
                f"source-{bit}-delay",
            )
            for bit in range(2)
        ),
        *(
            _TowerSwitch(
                f"peg-{bit}-destination",
                equal_two,
                input_bits[bit],
                f"peg-{bit}-delay",
            )
            for bit in range(2)
        ),
        *(
            _TowerSwitch(
                f"peg-{bit}-virtual-one",
                equal_three,
                peg_v1[bit],
                f"peg-{bit}-delay",
            )
            for bit in range(2)
        ),
        *(
            _TowerSwitch(
                f"peg-{bit}-advance",
                state_update,
                peg_after_drop[bit],
                f"peg-{bit}-delay",
            )
            for bit in range(2)
        ),
        *(
            _TowerSwitch(
                f"peg-{bit}-feedback",
                net.not_(net.or_many((equal_two, equal_three, state_update))),
                peg[bit],
                f"peg-{bit}-delay",
            )
            for bit in range(2)
        ),
        _TowerSwitch("orientation-height", equal_zero, input_bits[0], "orientation-delay"),
        _TowerSwitch("orientation-ring", equal_three, orientation_next, "orientation-delay"),
        _TowerSwitch(
            "orientation-feedback",
            net.not_(net.or_(equal_zero, equal_three)),
            orientation,
            "orientation-delay",
        ),
        _TowerSwitch("parity-update", state_update, q_next, "parity-delay"),
        _TowerSwitch(
            "parity-feedback",
            net.not_(state_update),
            parity,
            "parity-delay",
        ),
    ]

    net.prune(
        (
            high_zero,
            fallback_enable,
            output_enable,
            *counter_next,
            orientation_next,
            q_next,
            *peg_after_drop,
            command0,
            command1,
            command2,
            forced_zero,
            *(switch.enable for switch in switches),
            *(switch.value for switch in switches),
        )
    )

    specifications: list[tuple[str, int, dict[str, object]]] = [
        ("level-input", ARCHITECTURE_INPUT_KIND, {"word_size": 8, "ui_order": -2, "user_label": "tower-input"}),
        ("word-zero", 46, {"word_size": 8, "init_data": 0}),
        ("input-splitter", 17, {"word_size": 8}),
        ("zero", 1, {}),
        ("one", 2, {}),
        *(
            (f"counter-{bit}-delay", 13, {"init_data": 0})
            for bit in range(TOWER_COUNTER_BITS)
        ),
        *( (f"source-{bit}-delay", 13, {"init_data": 0}) for bit in range(2) ),
        *( (f"peg-{bit}-delay", 13, {"init_data": 0}) for bit in range(2) ),
        ("orientation-delay", 13, {"init_data": 0}),
        ("parity-delay", 13, {"init_data": 0}),
        ("command-maker", 16, {"word_size": 8}),
        ("level-output", ARCHITECTURE_OUTPUT_KIND, {"word_size": 8, "ui_order": -2, "user_label": "tower-output"}),
        *((switch.role, 25, {"word_size": switch.word_size}) for switch in switches),
        *((f"gate-{gate.signal}", gate.kind, {}) for gate in net.gates),
    ]
    seen_roles: set[str] = set()
    components_by_role: dict[str, Component] = {}
    for index, (role, kind, kwargs) in enumerate(specifications):
        if role in seen_roles:
            raise TowerVerificationError(f"duplicate Tower component role {role!r}")
        seen_roles.add(role)
        components_by_role[role] = Component(
            kind=kind,
            position=(0, index * 20),
            rotation=0,
            permanent_id=stable_permanent_id(key, role),
            **kwargs,
        )
    components = tuple(components_by_role[role] for role, _, _ in specifications)

    signal_sources: dict[str, tuple[str, str]] = {
        "zero": ("zero", "out"),
        "one": ("one", "out"),
        "word-zero": ("word-zero", "out"),
        **{f"input{bit}": ("input-splitter", f"out{bit}") for bit in range(8)},
        **{f"c{bit}": (f"counter-{bit}-delay", "out") for bit in range(TOWER_COUNTER_BITS)},
        "source0": ("source-0-delay", "out"),
        "source1": ("source-1-delay", "out"),
        "peg0": ("peg-0-delay", "out"),
        "peg1": ("peg-1-delay", "out"),
        "orientation": ("orientation-delay", "out"),
        "ctz-parity": ("parity-delay", "out"),
        "input-fallback": ("input-fallback", "out"),
        "command-maker": ("command-maker", "out"),
        **{gate.signal: (f"gate-{gate.signal}", "out") for gate in net.gates},
    }

    left_bus_x = -80
    right_bus_x = 80
    wires = []

    def connect(source_signal: str, sink_role: str, sink_pin: str) -> None:
        try:
            source_role, source_pin = signal_sources[source_signal]
        except KeyError as exc:
            raise TowerVerificationError(f"unknown Tower signal {source_signal!r}") from exc
        lane_y = -30 - len(wires) * 4
        wires.append(
            _tower_safe_wire(
                components_by_role[source_role],
                source_pin,
                components_by_role[sink_role],
                sink_pin,
                lane_y=lane_y,
                left_bus_x=left_bus_x,
                right_bus_x=right_bus_x,
            )
        )

    connect(high_zero, "level-input", "control")
    connect("word-zero", "input-fallback", "in")
    connect(fallback_enable, "input-fallback", "enable")
    connect("input-fallback", "input-splitter", "in")
    # Architecture Input and the disabled-input zero switch are mutually
    # exclusive tri-state drivers on the splitter's U8 input network.
    lane_y = -30 - len(wires) * 4
    wires.append(
        _tower_safe_wire(
            components_by_role["level-input"],
            "value",
            components_by_role["input-splitter"],
            "in",
            lane_y=lane_y,
            left_bus_x=left_bus_x,
            right_bus_x=right_bus_x,
        )
    )

    for gate in net.gates:
        for input_pin, fanin in zip(("in",) if gate.kind == 3 else ("in0", "in1"), gate.fanins):
            connect(fanin, f"gate-{gate.signal}", input_pin)
    for bit, value in enumerate(counter_next):
        connect(value, f"counter-{bit}-delay", "in")
    for switch in switches:
        connect(switch.enable, switch.role, "enable")
        connect(switch.value, switch.role, "in")
        lane_y = -30 - len(wires) * 4
        wires.append(
            _tower_safe_wire(
                components_by_role[switch.role],
                "out",
                components_by_role[switch.destination],
                "in",
                lane_y=lane_y,
                left_bus_x=left_bus_x,
                right_bus_x=right_bus_x,
            )
        )
    for bit, value in enumerate((command0, command1, command2, forced_zero, forced_zero, forced_zero, forced_zero, forced_zero)):
        connect(value, "command-maker", f"in{bit}")
    connect("command-maker", "level-output", "value")
    connect(output_enable, "level-output", "control")

    critical_signals = (
        command0,
        command1,
        command2,
        output_enable,
        *counter_next,
        orientation_next,
        q_next,
        *peg_after_drop,
    )
    return Circuit(
        gate=len(net.gates),
        delay=max(net.depth(signal) for signal in critical_signals),
        description=(
            "Codex Tower of Hanoi ASIC v1: 13-bit compressed FSM, four sequential "
            "architecture reads, one command output per tick, and no legacy dependencies."
        ),
        components=components,
        wires=tuple(wires),
    )


def verify_tower_fsm_asic(
    circuit: Circuit | None = None,
    *,
    sprite_root: Path | None = None,
) -> dict[str, object]:
    """Prove the emitted v15 circuit against all 18 current Tower cases."""

    candidate = build_tower_fsm_asic() if circuit is None else circuit
    payload = encode_v15(candidate)
    if decode_v15(payload) != candidate:
        raise TowerVerificationError("Tower FSM ASIC failed v15 round-trip")
    if len(candidate.components) > 255:
        raise TowerVerificationError("Tower FSM ASIC exceeds the level component limit")
    if sum(component.kind == ARCHITECTURE_INPUT_KIND for component in candidate.components) != 1:
        raise TowerVerificationError("Tower FSM ASIC must have exactly one Architecture Input")
    if sum(component.kind == ARCHITECTURE_OUTPUT_KIND for component in candidate.components) != 1:
        raise TowerVerificationError("Tower FSM ASIC must have exactly one Architecture Output")
    if sum(component.kind == 13 for component in candidate.components) != TOWER_DELAY_BITS:
        raise TowerVerificationError("Tower FSM ASIC must retain exactly thirteen Delay Bits")

    connectivity = analyze_connectivity(candidate)
    for field in (
        "unsupported_component_kind_counts",
        "unconnected_pin_count",
        "multi_driver_network_count",
        "undriven_network_count",
        "sinkless_network_count",
        "width_mismatch_network_count",
        "cycle_component_count",
    ):
        if connectivity[field]:
            raise TowerVerificationError(
                f"Tower FSM ASIC failed connectivity check {field}: {connectivity[field]!r}"
            )

    summaries: list[dict[str, int]] = []
    for case in all_tower_cases():
        expected = commands_from_moves(formula_moves(case))
        inputs = tuple(
            {"tower-input": case.input_stream[tick] if tick < 4 else 0}
            for tick in range(len(expected) + 1)
        )
        try:
            trace = simulate_clocked_trace(candidate, inputs=inputs)
        except SimulationError as exc:
            raise TowerVerificationError(
                f"Tower FSM simulation failed for {case!r}"
            ) from exc
        emitted: list[int] = []
        for tick, result in enumerate(trace):
            if tick == 0:
                if result.outputs:
                    raise TowerVerificationError("Tower FSM emitted during first input read")
            else:
                if result.outputs != {"tower-output": expected[tick - 1]}:
                    raise TowerVerificationError(
                        f"Tower FSM output mismatch for {case!r} at tick {tick}: "
                        f"expected {expected[tick - 1]}, got {result.outputs}"
                    )
                emitted.append(expected[tick - 1])
        level_result = simulate_tower_script(case, emitted)
        if not level_result.won or level_result.first_win_event != len(expected):
            raise TowerVerificationError(f"Tower FSM ASIC loses Tower case {case!r}")
        summaries.append(
            {
                "highest_disk": case.highest_disk,
                "source": case.source,
                "destination": case.destination,
                "cycles": len(expected) + 1,
            }
        )

    active_sprite_root = sprite_root or DEFAULT_COMPONENT_SPRITE_ROOT
    geometry = audit_sprite_geometry(candidate, active_sprite_root)
    if not geometry.is_safe:
        raise TowerVerificationError(
            "Tower FSM ASIC failed sprite geometry audit: "
            f"unsupported={geometry.unsupported_component_kinds}, "
            f"overlap={len(geometry.component_overlap_cells)}, "
            f"wire_collisions={len(geometry.wire_collisions)}"
        )
    return {
        "case_count": len(summaries),
        "maximum_cycles": max(item["cycles"] for item in summaries),
        "component_count": len(candidate.components),
        "wire_count": len(candidate.wires),
        "gate": candidate.gate,
        "delay": candidate.delay,
        "sha256": sha256(payload).hexdigest(),
        "geometry": {
            "sprite_count": len(geometry.sprite_files),
            "alpha_cells": geometry.alpha_cell_count,
        },
        "cases": summaries,
    }


def write_tower_fsm_asic(project_root: Path) -> dict[str, object]:
    """Write the fully verified Tower FSM baseline into the project only.

    This deliberately has no formal-save side effect.  The candidate needs one
    game-side acceptance run before a direct-install target may be registered.
    """

    candidate = build_tower_fsm_asic()
    verification = verify_tower_fsm_asic(candidate)
    payload = encode_v15(candidate)
    destination = project_root / "examples" / "tower" / "candidate" / "circuit.data"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(payload)
    (destination.parent / ".gitkeep").unlink(missing_ok=True)
    metadata = {
        "schema": 1,
        "level": "tower",
        "title": "汉诺塔",
        "strategy": "current-v15 compressed finite-state ASIC",
        "deployment_target": "schematics/architecture/CODEX-TOWER/circuit.data",
        "sha256": sha256(payload).hexdigest(),
        "format_version": 15,
        "component_count": len(candidate.components),
        "wire_count": len(candidate.wires),
        "metric_status": (
            "125 周期与全部离线行为已验证；gate/delay 是候选声明值，"
            "尚未通过游戏端计分或排行榜验收。"
        ),
        "public_reference": {"gate": 125, "delay": 7, "cycles": 125},
        **verification,
    }
    (destination.parent / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return metadata


def build_tower_io_protocol_probe() -> Circuit:
    """Build a non-deployable v15 probe using exactly one current I/O pair."""

    key = "architecture/codex-tower-io-protocol-probe"

    def component(role: str, kind: int, position: Point, **kwargs: object) -> Component:
        return Component(
            kind=kind,
            position=position,
            rotation=0,
            permanent_id=stable_permanent_id(key, role),
            **kwargs,
        )

    components = (
        component("input", ARCHITECTURE_INPUT_KIND, (-30, 0), word_size=8),
        component("input-enable", 2, (-40, -12)),
        component("output", ARCHITECTURE_OUTPUT_KIND, (30, 0), word_size=8),
        component("output-enable", 2, (20, -12)),
    )
    wires = (
        wire_from_vertices(((-39, -12), (-35, -12), (-27, -4), (-29, -2))),
        wire_from_vertices(((-27, 0), (27, 0))),
        wire_from_vertices(((21, -12), (24, -12), (27, -9), (27, -4), (29, -2))),
    )
    return Circuit(
        gate=0,
        delay=0,
        description=(
            "Non-deployable Tower I/O protocol probe. It validates v15 encoding, "
            "reviewed pins, and sprite geometry only."
        ),
        components=components,
        wires=wires,
    )


def _png_rgba_rows(path: Path) -> tuple[int, int, bytes]:
    """Decode the exact RGBA8/non-interlaced PNG subset used by game sprites."""

    data = path.read_bytes()
    signature = b"\x89PNG\r\n\x1a\n"
    if not data.startswith(signature):
        raise PngAlphaError(f"not a PNG file: {path}")
    offset = len(signature)
    width = height = bit_depth = color_type = compression = filter_method = interlace = None
    idat_parts: list[bytes] = []
    saw_iend = False

    while offset < len(data):
        if offset + 12 > len(data):
            raise PngAlphaError(f"truncated PNG chunk header: {path}")
        length = struct.unpack_from(">I", data, offset)[0]
        offset += 4
        chunk_type = data[offset : offset + 4]
        offset += 4
        end = offset + length
        if end + 4 > len(data):
            raise PngAlphaError(f"truncated PNG chunk data: {path}")
        payload = data[offset:end]
        offset = end
        stored_crc = struct.unpack_from(">I", data, offset)[0]
        offset += 4
        actual_crc = zlib.crc32(chunk_type + payload) & 0xFFFFFFFF
        if actual_crc != stored_crc:
            raise PngAlphaError(f"PNG CRC mismatch in {path}")
        if chunk_type == b"IHDR":
            if len(payload) != 13 or width is not None:
                raise PngAlphaError(f"invalid IHDR in {path}")
            width, height, bit_depth, color_type, compression, filter_method, interlace = struct.unpack(
                ">IIBBBBB", payload
            )
        elif chunk_type == b"IDAT":
            idat_parts.append(payload)
        elif chunk_type == b"IEND":
            saw_iend = True
            break

    if not saw_iend or width is None or height is None:
        raise PngAlphaError(f"incomplete PNG: {path}")
    if (bit_depth, color_type, compression, filter_method, interlace) != (8, 6, 0, 0, 0):
        raise PngAlphaError(
            f"expected non-interlaced RGBA8 component sprite, got "
            f"bit_depth={bit_depth}, color_type={color_type}, interlace={interlace}: {path}"
        )
    try:
        filtered = zlib.decompress(b"".join(idat_parts))
    except zlib.error as exc:
        raise PngAlphaError(f"could not inflate PNG data: {path}") from exc
    stride = width * 4
    expected_size = height * (stride + 1)
    if len(filtered) != expected_size:
        raise PngAlphaError(
            f"unexpected PNG data size {len(filtered)}, expected {expected_size}: {path}"
        )

    rows = bytearray()
    previous = bytearray(stride)
    source_offset = 0
    for _ in range(height):
        filter_type = filtered[source_offset]
        source_offset += 1
        row = bytearray(filtered[source_offset : source_offset + stride])
        source_offset += stride
        for index in range(stride):
            left = row[index - 4] if index >= 4 else 0
            above = previous[index]
            upper_left = previous[index - 4] if index >= 4 else 0
            if filter_type == 0:
                correction = 0
            elif filter_type == 1:
                correction = left
            elif filter_type == 2:
                correction = above
            elif filter_type == 3:
                correction = (left + above) // 2
            elif filter_type == 4:
                predictor = left + above - upper_left
                distances = (abs(predictor - left), abs(predictor - above), abs(predictor - upper_left))
                correction = left if distances[0] <= distances[1] and distances[0] <= distances[2] else (
                    above if distances[1] <= distances[2] else upper_left
                )
            else:
                raise PngAlphaError(f"unsupported PNG filter {filter_type}: {path}")
            row[index] = (row[index] + correction) & 0xFF
        rows.extend(row)
        previous = row
    return width, height, bytes(rows)


@lru_cache(maxsize=None)
def sprite_alpha_cells(sprite_path: Path) -> frozenset[Point]:
    """Map non-transparent pixels of a live component sprite onto circuit cells."""

    width, height, rgba = _png_rgba_rows(sprite_path)
    if width % PIXELS_PER_GRID_CELL or height % PIXELS_PER_GRID_CELL:
        raise PngAlphaError(f"sprite is not aligned to {PIXELS_PER_GRID_CELL}px cells: {sprite_path}")
    origin_x = width // 2 - PIXELS_PER_GRID_CELL // 2
    origin_y = height // 2 - PIXELS_PER_GRID_CELL // 2
    cells: set[Point] = set()
    for y in range(height):
        row_offset = y * width * 4
        cell_y = (y - origin_y) // PIXELS_PER_GRID_CELL
        for x in range(width):
            if rgba[row_offset + x * 4 + 3] == 0:
                continue
            cell_x = (x - origin_x) // PIXELS_PER_GRID_CELL
            cells.add((cell_x, cell_y))
    if not cells:
        raise PngAlphaError(f"sprite contains no opaque pixels: {sprite_path}")
    return frozenset(cells)


def _component_sprite_path(component: Component, sprite_root: Path) -> Path:
    try:
        name = SPRITE_NAME_BY_COMPONENT_KIND[component.kind]
    except KeyError as exc:
        raise TowerVerificationError(
            f"component kind {component.kind} has no reviewed Tower sprite mapping"
        ) from exc
    path = sprite_root / name
    if not path.is_file():
        raise TowerVerificationError(f"current component sprite is missing: {path}")
    return path


def component_alpha_cells(component: Component, sprite_root: Path) -> frozenset[Point]:
    """Return world-space opaque sprite cells for a positioned component."""

    local_cells = sprite_alpha_cells(_component_sprite_path(component, sprite_root))
    return frozenset(
        (
            component.position[0] + rotate_offset(cell, component.rotation)[0],
            component.position[1] + rotate_offset(cell, component.rotation)[1],
        )
        for cell in local_cells
    )


def _sign(value: int) -> int:
    return (value > 0) - (value < 0)


def _pin_escape_cells(
    component: Component,
    pin_position: Point,
    alpha_cells: frozenset[Point],
) -> frozenset[Point]:
    """Return the alpha-only escape stem for one endpoint pin.

    Current I/O sprites draw their logical ports inside a solid circular body.
    A literal "all alpha is forbidden" rule would therefore reject an ordinary
    wire leaving the documented port.  The only permitted exception is the
    ray that begins at an actual endpoint pin and heads away from the component
    center until alpha ends.  It is computed from the live alpha mask, not from
    a guessed component bounding box.
    """

    step = (
        _sign(pin_position[0] - component.position[0]),
        _sign(pin_position[1] - component.position[1]),
    )
    if step == (0, 0):
        return frozenset()
    result: set[Point] = set()
    point = pin_position
    while point in alpha_cells:
        result.add(point)
        point = (point[0] + step[0], point[1] + step[1])
    return frozenset(result)


def audit_sprite_geometry(circuit: Circuit, sprite_root: Path) -> SpriteGeometryAudit:
    """Reject wires crossing opaque component alpha or non-endpoint pins.

    Wire-to-wire intersections are deliberately not reported: they are valid
    in the game.  An endpoint may leave a reviewed pin through only that pin's
    alpha escape stem.  Any other alpha contact, including a non-endpoint pin,
    is rejected.
    """

    alpha_owners: dict[Point, list[int]] = {}
    alpha_cells_by_component: list[frozenset[Point]] = []
    pin_names_by_component: list[dict[Point, tuple[str, ...]]] = []
    sprite_files: set[str] = set()
    unsupported: list[int] = []

    for component_index, component in enumerate(circuit.components):
        try:
            sprite_path = _component_sprite_path(component, sprite_root)
            cells = component_alpha_cells(component, sprite_root)
        except TowerVerificationError:
            unsupported.append(component.kind)
            alpha_cells_by_component.append(frozenset())
            pin_names_by_component.append({})
            continue
        alpha_cells_by_component.append(cells)
        sprite_files.add(sprite_path.name)
        for cell in cells:
            alpha_owners.setdefault(cell, []).append(component_index)
        positions: dict[Point, list[str]] = {}
        for pin in positioned_pins(component, component_index):
            positions.setdefault(pin.position, []).append(pin.name)
        pin_names_by_component.append(
            {position: tuple(names) for position, names in positions.items()}
        )

    wire_collisions: list[SpriteWireCollision] = []
    for wire_index, wire in enumerate(circuit.wires):
        points = wire_points(wire)
        endpoints = {points[0], points[-1]}
        endpoint_pins_by_component: dict[int, set[Point]] = {}
        escape_cells_by_component: dict[int, set[Point]] = {}
        for endpoint in endpoints:
            for component_index in alpha_owners.get(endpoint, ()):
                pin_names = pin_names_by_component[component_index].get(endpoint, ())
                if not pin_names:
                    continue
                component = circuit.components[component_index]
                endpoint_pins_by_component.setdefault(component_index, set()).add(endpoint)
                escape_cells_by_component.setdefault(component_index, set()).update(
                    _pin_escape_cells(
                        component,
                        endpoint,
                        alpha_cells_by_component[component_index],
                    )
                )
        for point in points:
            for component_index in alpha_owners.get(point, ()):
                pin_names = pin_names_by_component[component_index].get(point, ())
                if point in endpoint_pins_by_component.get(component_index, set()):
                    continue
                if not pin_names and point in escape_cells_by_component.get(component_index, set()):
                    continue
                component = circuit.components[component_index]
                wire_collisions.append(
                    SpriteWireCollision(
                        wire_index=wire_index,
                        component_index=component_index,
                        point=point,
                        component_kind=component.kind,
                        endpoint=point in endpoints,
                        pin_names=pin_names,
                    )
                )

    return SpriteGeometryAudit(
        sprite_files=tuple(sorted(sprite_files)),
        alpha_cell_count=sum(len(owners) for owners in alpha_owners.values()),
        unsupported_component_kinds=tuple(sorted(set(unsupported))),
        component_overlap_cells=tuple(
            sorted(point for point, owners in alpha_owners.items() if len(owners) > 1)
        ),
        wire_collisions=tuple(wire_collisions),
    )


def verify_tower_io_protocol_probe(
    *,
    sprite_root: Path | None = None,
) -> dict[str, object]:
    """Round-trip the reviewed probe and optionally audit live sprite alpha."""

    candidate = build_tower_io_protocol_probe()
    if sum(component.kind == ARCHITECTURE_INPUT_KIND for component in candidate.components) != 1:
        raise TowerVerificationError("Tower probe must have exactly one Architecture Input")
    if sum(component.kind == ARCHITECTURE_OUTPUT_KIND for component in candidate.components) != 1:
        raise TowerVerificationError("Tower probe must have exactly one Architecture Output")
    payload = encode_v15(candidate)
    if decode_v15(payload) != candidate:
        raise TowerVerificationError("Tower I/O probe failed v15 round-trip")
    connectivity = analyze_connectivity(candidate)
    for field in (
        "unsupported_component_kind_counts",
        "unconnected_pin_count",
        "multi_driver_network_count",
        "width_mismatch_network_count",
        "cycle_component_count",
    ):
        if connectivity[field]:
            raise TowerVerificationError(
                f"Tower I/O probe failed connectivity check {field}: {connectivity[field]}"
            )

    result: dict[str, object] = {
        "format_version": 15,
        "component_count": len(candidate.components),
        "wire_count": len(candidate.wires),
        "single_architecture_input": True,
        "single_architecture_output": True,
        "deployable": False,
    }
    if sprite_root is not None:
        audit = audit_sprite_geometry(candidate, sprite_root)
        if not audit.is_safe:
            raise TowerVerificationError(f"Tower I/O probe failed sprite audit: {audit!r}")
        result["sprite_audit"] = {
            "sprite_files": list(audit.sprite_files),
            "alpha_cell_count": audit.alpha_cell_count,
        }
    return result
