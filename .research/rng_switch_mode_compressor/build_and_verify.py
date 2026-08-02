"""Build and exhaustively audit the 468/8/67 tristate RNG candidate.

This is an isolated research generator.  It does not read or write the live
save and it never starts Turing Complete.  The data plane keeps the reviewed
47-mode-leaf encoding, but replaces every second XOR layer with an always
driven two-Switch bus:

    Switch(x,     NOT y)
    Switch(NOT x, y)

Exactly one driver is enabled for every (x, y), so the implementation never
uses an undriven bus as logical zero.  First-layer XOR/XNOR rails are built
from four explicit one-gate primitives; no custom-component side output is
treated as free.
"""

from __future__ import annotations

from collections import Counter, defaultdict, deque
from dataclasses import dataclass, replace
from hashlib import sha256
import json
from pathlib import Path
import sys
from typing import Iterable


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from tc_save_lab.analysis import wire_points  # noqa: E402
from tc_save_lab.builder import stable_permanent_id, wire_from_vertices  # noqa: E402
from tc_save_lab.codec import decode_v15, encode_v15  # noqa: E402
from tc_save_lab.model import Circuit, Component, Point  # noqa: E402
from tc_save_lab.pins import I, O, T as TRISTATE, analyze_connectivity, positioned_pins  # noqa: E402
from tc_save_lab import rng_encoded_asic as base  # noqa: E402
from tc_save_lab.simulate import (  # noqa: E402
    _compile,
    _simulate_clocked_tick,
    initial_clocked_memory,
)
from tc_save_lab.sprite_geometry import (  # noqa: E402
    DEFAULT_COMPONENT_SPRITE_ROOT,
    audit_sprite_geometry,
)


HERE = Path(__file__).resolve().parent
OUTPUT_DATA = HERE / "candidate.data"
OUTPUT_JSON = HERE / "result.json"
CACHE_DATA = HERE / "generated-cache-switch-top-entry.data"

GATE = 468
DELAY = 8
CYCLES = 67
ENERGY = GATE * DELAY * CYCLES
REFERENCE = 431 * 9 * 66
KEY = "architecture/codex-rng-switch-mode-compressor"
STATE_KEY = "architecture/codex-rng-encoded"

GATE_COST = {
    3: 1,   # NOT
    4: 1,   # AND
    6: 1,   # NAND
    7: 1,   # OR
    12: 2,  # Bit Switch
    13: 5,  # Delay Bit
}
DELAY_COST = {
    3: 1,
    4: 1,
    6: 1,
    7: 1,
    12: 1,
    13: 4,
}

_BASE_PIN_ACCESS_CELLS = base._pin_access_cells


def _install_switch_geometry() -> None:
    """Teach the shared router that a Bit Switch enable pin exits upward."""

    base._FOOTPRINT_BOXES.setdefault(4, (-1, -2, 2, 2))
    base._FOOTPRINT_BOXES.setdefault(6, (-1, -2, 2, 2))
    base._FOOTPRINT_BOXES.setdefault(12, (-1, -1, 2, 1))

    def pin_access_cells(
        component: Component,
        pin_position: Point,
        pin_direction: str,
        footprint: frozenset[Point],
    ) -> frozenset[Point]:
        if component.kind == 12 and pin_position == base._pin(component, "enable"):
            step = base.rotate_offset((0, 1), component.rotation)
            cells: set[Point] = set()
            point = pin_position
            for _ in range(16):
                cells.add(point)
                if point not in footprint:
                    break
                point = (point[0] + step[0], point[1] + step[1])
            else:
                raise RuntimeError("unbounded Bit Switch enable corridor")
            return frozenset(cells)
        return _BASE_PIN_ACCESS_CELLS(
            component, pin_position, pin_direction, footprint
        )

    base._pin_access_cells = pin_access_cells


@dataclass(frozen=True)
class Rail:
    positive: Point
    negative: Point


@dataclass(frozen=True)
class TriValue:
    value: int
    is_z: bool
    arrival: int


class UnionFind:
    def __init__(self, size: int) -> None:
        self.parent = list(range(size))

    def find(self, value: int) -> int:
        while self.parent[value] != value:
            self.parent[value] = self.parent[self.parent[value]]
            value = self.parent[value]
        return value

    def union(self, left: int, right: int) -> None:
        left = self.find(left)
        right = self.find(right)
        if left != right:
            self.parent[right] = left


def _component(
    role: str,
    kind: int,
    position: Point,
    **kwargs: object,
) -> Component:
    return Component(
        kind=kind,
        position=position,
        rotation=0,
        permanent_id=stable_permanent_id(KEY, role),
        **kwargs,
    )


def _first_y(index: int) -> int:
    return index * 18 - 234


def _second_y(index: int) -> int:
    return index * 18 - 297


def _mode_pair_consumers() -> dict[tuple[int, int], tuple[base.XorGate, int]]:
    result: dict[tuple[int, int], tuple[base.XorGate, int]] = {}
    for gate in base.GATES:
        for side, fanin in enumerate((gate.left, gate.right)):
            if gate.depth == 1:
                seed_bit = base.FIRST_LEAF_SEEDS[gate.output][side]
                state_bit = base.bits(fanin)[0]
            elif fanin in base.FIRST_LAYER:
                continue
            else:
                seed_form = base._seed_form_of_fanin(fanin, gate.output, side)
                if not seed_form:
                    continue
                seed_bit = base.bits(seed_form)[0]
                state_bit = base.bits(fanin)[0]
            if seed_bit is None:
                continue
            pair = (seed_bit, state_bit)
            if pair in result:
                raise AssertionError(f"mode pair {pair} has multiple consumers")
            result[pair] = (gate, side)
    if frozenset(result) != base.MODE_PAIRS:
        raise AssertionError("47-mode-pair certificate changed")
    return result


def _direct_leaf_key(gate: base.XorGate, side: int, node: int) -> tuple[int, int]:
    if node not in base.DIRECT:
        raise AssertionError(f"second-layer leaf {node:08x} is not direct")
    return node, base._seed_form_of_fanin(node, gate.output, side)


DONT_CARE_GATE_PAIRS = (
    (0x80000404, 0x08008400),
    (0x00008808, 0x10010800),
    (0x00011010, 0x20001001),
    (0x00002021, 0x40002002),
    (0x00004042, 0x80004004),
)


def _build_components() -> tuple[
    tuple[Component, ...],
    dict[str, object],
]:
    first_gates = tuple(gate for gate in base.GATES if gate.depth == 1)
    second_gates = tuple(gate for gate in base.GATES if gate.depth == 2)
    first_index = {gate.output: index for index, gate in enumerate(first_gates)}
    second_index = {gate.output: index for index, gate in enumerate(second_gates)}

    level_input = _component(
        "level-input", 62, (-600, 0), word_size=32, ui_order=-2, user_label="Seed"
    )
    level_output = _component(
        "level-output",
        70,
        (180, 0),
        word_size=32,
        ui_order=-2,
        user_label="RNG output",
    )
    # State IDs deliberately stay compatible with the reviewed encoded-state
    # verifier so memory can be decoded independently of this netlist.
    load_pulse_delay = Component(
        kind=13,
        position=(-580, -390),
        rotation=0,
        permanent_id=stable_permanent_id(STATE_KEY, "load-pulse-delay"),
        init_data=0,
    )
    output_active_delay = Component(
        kind=13,
        position=(-580, -370),
        rotation=0,
        permanent_id=stable_permanent_id(STATE_KEY, "output-active-delay"),
        init_data=0,
    )
    phase_any = _component("phase-any", 7, (-550, -380))
    not_phase_any = _component("not-phase-any", 3, (-525, -380))

    seed_word_splitter = _component("seed-splitter-32", 99, (-565, 0), word_size=8)
    seed_byte_splitters = tuple(
        _component(f"seed-splitter-8-{group}", 17, (-530, group * 112 - 168))
        for group in range(4)
    )
    state_delays = tuple(
        Component(
            kind=13,
            position=(-430, bit * 14 - 217),
            rotation=0,
            permanent_id=stable_permanent_id(STATE_KEY, f"state-delay-{bit}"),
            init_data=0,
        )
        for bit in range(base.WORD_BITS)
    )

    consumers = _mode_pair_consumers()
    consumer_counts = Counter(gate.output for gate, _ in consumers.values())
    mode_ors: dict[tuple[int, int], Component] = {}
    for pair in sorted(base.MODE_PAIRS):
        consumer, side = consumers[pair]
        if consumer.depth == 1:
            y = _first_y(first_index[consumer.output])
            offset = (-4 if side == 0 else 4) if consumer_counts[consumer.output] == 2 else 0
            position = (-250, y + offset)
        else:
            position = (-70, _second_y(second_index[consumer.output]))
        mode_ors[pair] = _component(
            f"mode-or-seed-{pair[0]}-state-{pair[1]}", 7, position
        )

    # Each first-layer node is an explicit four-gate dual-rail cell:
    #   either = OR(a,b), not_both = NAND(a,b)
    #   XOR = AND(either,not_both), XNOR = NAND(either,not_both)
    # Its total cost is four, not the cost-three XOR plus a free side output.
    dual_cells: dict[int, dict[str, Component]] = {}
    for index, gate in enumerate(first_gates):
        y = _first_y(index)
        dual_cells[gate.output] = {
            "either": _component(f"dual-{gate.output:08x}-either", 7, (-170, y - 4)),
            "not_both": _component(f"dual-{gate.output:08x}-not-both", 6, (-170, y + 4)),
            "xor": _component(f"dual-{gate.output:08x}-xor", 4, (-125, y - 4)),
            "xnor": _component(f"dual-{gate.output:08x}-xnor", 6, (-125, y + 4)),
        }

    raw_direct_keys = sorted(
        {
            _direct_leaf_key(gate, side, node)
            for gate in second_gates
            for side, node in enumerate((gate.left, gate.right))
            if node not in base.FIRST_LAYER
        }
    )
    if len(raw_direct_keys) != 10:
        raise AssertionError(f"direct leaf count changed: {len(raw_direct_keys)}")
    keys_by_node: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for key in raw_direct_keys:
        keys_by_node[key[0]].append(key)
    if sorted(len(values) for values in keys_by_node.values()) != [2] * 5:
        raise AssertionError("direct leaves no longer form five raw/mode pairs")
    canonical_direct_key: dict[tuple[int, int], tuple[int, int]] = {}
    for values in keys_by_node.values():
        raw = [key for key in values if key[1] == 0]
        mode = [key for key in values if key[1] != 0]
        if len(raw) != 1 or len(mode) != 1:
            raise AssertionError(f"direct pair is not one raw plus one mode: {values}")
        canonical_direct_key[raw[0]] = mode[0]
        canonical_direct_key[mode[0]] = mode[0]
    direct_keys = sorted(set(canonical_direct_key.values()))
    if len(direct_keys) != 5:
        raise AssertionError("load don't-care sharing did not reduce direct rails to five")
    direct_consumer: dict[tuple[int, int], tuple[base.XorGate, int]] = {}
    for gate in second_gates:
        for side, node in enumerate((gate.left, gate.right)):
            if node in base.FIRST_LAYER:
                continue
            key = _direct_leaf_key(gate, side, node)
            canonical = canonical_direct_key[key]
            if key == canonical:
                direct_consumer[canonical] = (gate, side)
    if set(direct_consumer) != set(direct_keys):
        raise AssertionError("every shared mode rail needs one B-only placement anchor")
    direct_nots = {
        key: _component(
            f"direct-not-state-{base.bits(key[0])[0]}-seed-{key[1]:08x}",
            3,
            (-30, _second_y(second_index[direct_consumer[key][0].output])),
        )
        for key in direct_keys
    }

    switches: dict[int, tuple[Component, Component]] = {}
    for index, gate in enumerate(second_gates):
        y = _second_y(index)
        switches[gate.output] = (
            _component(f"switch-{gate.output:08x}-left-one", 12, (30, y - 3)),
            _component(f"switch-{gate.output:08x}-left-zero", 12, (30, y + 3)),
        )

    byte_makers = tuple(
        _component(f"result-maker-8-{group}", 16, (125, group * 112 - 168))
        for group in range(4)
    )
    word_maker = _component("result-maker-32", 97, (150, 0), word_size=32)

    components = (
        level_input,
        level_output,
        load_pulse_delay,
        output_active_delay,
        phase_any,
        not_phase_any,
        seed_word_splitter,
        *seed_byte_splitters,
        *state_delays,
        *(mode_ors[pair] for pair in sorted(mode_ors)),
        *(
            component
            for gate in first_gates
            for component in dual_cells[gate.output].values()
        ),
        *(direct_nots[key] for key in direct_keys),
        *(component for gate in second_gates for component in switches[gate.output]),
        *byte_makers,
        word_maker,
    )
    return components, {
        "level_input": level_input,
        "level_output": level_output,
        "load_pulse_delay": load_pulse_delay,
        "output_active_delay": output_active_delay,
        "phase_any": phase_any,
        "not_phase_any": not_phase_any,
        "seed_word_splitter": seed_word_splitter,
        "seed_byte_splitters": seed_byte_splitters,
        "state_delays": state_delays,
        "mode_ors": mode_ors,
        "dual_cells": dual_cells,
        "direct_nots": direct_nots,
        "canonical_direct_key": canonical_direct_key,
        "switches": switches,
        "byte_makers": byte_makers,
        "word_maker": word_maker,
        "first_gates": first_gates,
        "second_gates": second_gates,
    }


def build_candidate() -> Circuit:
    components, parts = _build_components()

    # The original conservative router already knows every reused component.
    # Add exact current-v15 sprite bounds for the three newly introduced kinds.
    _install_switch_geometry()
    route = base._build_router(components)

    level_input = parts["level_input"]
    level_output = parts["level_output"]
    load_pulse_delay = parts["load_pulse_delay"]
    output_active_delay = parts["output_active_delay"]
    phase_any = parts["phase_any"]
    not_phase_any = parts["not_phase_any"]
    seed_word_splitter = parts["seed_word_splitter"]
    seed_byte_splitters = parts["seed_byte_splitters"]
    state_delays = parts["state_delays"]
    mode_ors = parts["mode_ors"]
    dual_cells = parts["dual_cells"]
    direct_nots = parts["direct_nots"]
    canonical_direct_key = parts["canonical_direct_key"]
    switches = parts["switches"]
    byte_makers = parts["byte_makers"]
    word_maker = parts["word_maker"]
    first_gates = parts["first_gates"]
    second_gates = parts["second_gates"]

    wires = [
        route(base._pin(load_pulse_delay, "out"), base._pin(level_input, "control")),
        route(base._pin(level_input, "value"), base._pin(seed_word_splitter, "in")),
        route(base._pin(output_active_delay, "out"), base._pin(level_output, "control")),
        route(base._pin(load_pulse_delay, "out"), base._pin(phase_any, "in0")),
        route(base._pin(output_active_delay, "out"), base._pin(phase_any, "in1")),
        route(base._pin(phase_any, "out"), base._pin(not_phase_any, "in")),
        route(base._pin(not_phase_any, "out"), base._pin(load_pulse_delay, "in")),
        route(base._pin(phase_any, "out"), base._pin(output_active_delay, "in")),
    ]
    for group, splitter in enumerate(seed_byte_splitters):
        wires.append(
            route(base._pin(seed_word_splitter, f"out{group}"), base._pin(splitter, "in"))
        )

    seed_sources = {
        bit: base._pin(seed_byte_splitters[bit // 8], f"out{bit % 8}")
        for bit in range(base.WORD_BITS)
    }
    state_sources = {
        bit: base._pin(state_delays[bit], "out") for bit in range(base.WORD_BITS)
    }
    for (seed_bit, state_bit), gate in sorted(mode_ors.items()):
        wires.append(route(state_sources[state_bit], base._pin(gate, "in0")))
        wires.append(route(seed_sources[seed_bit], base._pin(gate, "in1")))
    mode_sources = {pair: base._pin(gate, "out") for pair, gate in mode_ors.items()}

    rails: dict[int, Rail] = {}
    for gate in first_gates:
        state_support = base.bits(gate.output)
        seed_support = base.FIRST_LEAF_SEEDS[gate.output]
        leaves = []
        for seed_bit, state_bit in zip(seed_support, state_support):
            leaves.append(
                base._mode_source(
                    0 if seed_bit is None else 1 << seed_bit,
                    1 << state_bit,
                    state_sources=state_sources,
                    mode_sources=mode_sources,
                )
            )
        left, right = leaves
        cell = dual_cells[gate.output]
        for stage in (cell["either"], cell["not_both"]):
            wires.append(route(left, base._pin(stage, "in0")))
            wires.append(route(right, base._pin(stage, "in1")))
        for output in (cell["xor"], cell["xnor"]):
            wires.append(route(base._pin(cell["either"], "out"), base._pin(output, "in0")))
            wires.append(route(base._pin(cell["not_both"], "out"), base._pin(output, "in1")))
        rails[gate.output] = Rail(
            base._pin(cell["xor"], "out"),
            base._pin(cell["xnor"], "out"),
        )

    canonical_rails: dict[tuple[int, int], Rail] = {}
    for key, inverter in direct_nots.items():
        node, seed_form = key
        positive = base._mode_source(
            seed_form,
            node,
            state_sources=state_sources,
            mode_sources=mode_sources,
        )
        wires.append(route(positive, base._pin(inverter, "in")))
        canonical_rails[key] = Rail(positive, base._pin(inverter, "out"))
    direct_rails = {
        key: canonical_rails[canonical]
        for key, canonical in canonical_direct_key.items()
    }

    bus_drivers: dict[int, tuple[Point, Point]] = {}
    for gate in second_gates:
        fanin_rails = []
        for side, node in enumerate((gate.left, gate.right)):
            if node in rails:
                fanin_rails.append(rails[node])
            else:
                fanin_rails.append(direct_rails[_direct_leaf_key(gate, side, node)])
        left, right = fanin_rails
        left_one, left_zero = switches[gate.output]
        # left=1 selects NOT right; left=0 selects right.  The controls are
        # complementary ordinary signals, hence exactly one Switch is active.
        wires.append(route(left.positive, base._pin(left_one, "enable")))
        wires.append(route(right.negative, base._pin(left_one, "in")))
        wires.append(route(left.negative, base._pin(left_zero, "enable")))
        wires.append(route(right.positive, base._pin(left_zero, "in")))
        bus_drivers[gate.output] = (
            base._pin(left_one, "out"),
            base._pin(left_zero, "out"),
        )

    def connect_target(target: int, sink: Point) -> None:
        if target in bus_drivers:
            for driver in bus_drivers[target]:
                wires.append(route(driver, sink))
        elif target in rails:
            wires.append(route(rails[target].positive, sink))
        elif target in base.DIRECT:
            # C[27..31] are direct encoded-state bits.  The output is disabled
            # during seed loading, so their steady-state rail is sufficient.
            wires.append(route(state_sources[base.bits(target)[0]], sink))
        else:
            raise AssertionError(f"terminal target {target:08x} is not generated")

    for bit, target in enumerate(base.B):
        if target in base.GATE_BY_OUTPUT:
            connect_target(target, base._pin(state_delays[bit], "in"))
        else:
            source = base._mode_source(
                base.T[bit],
                target,
                state_sources=state_sources,
                mode_sources=mode_sources,
            )
            wires.append(route(source, base._pin(state_delays[bit], "in")))

    for bit, target in enumerate(base.C):
        group, offset = divmod(bit, 8)
        connect_target(target, base._pin(byte_makers[group], f"in{offset}"))
    for group, maker in enumerate(byte_makers):
        wires.append(route(base._pin(maker, "out"), base._pin(word_maker, f"in{group}")))
    wires.append(route(base._pin(word_maker, "out"), base._pin(level_output, "value")))

    return Circuit(
        gate=GATE,
        delay=DELAY,
        description=(
            "Codex RNG ASIC: explicit dual-rail first layer and always-driven "
            "two-Switch second layer"
        ),
        components=components,
        wires=tuple(wires),
    )


def _tristate_truth_table() -> list[dict[str, object]]:
    rows = []
    for x in (0, 1):
        for y in (0, 1):
            x_rail = TriValue(x, False, 7)
            nx_rail = TriValue(1 ^ x, False, 7)
            y_rail = TriValue(y, False, 7)
            ny_rail = TriValue(1 ^ y, False, 7)
            drivers = (
                TriValue(ny_rail.value, x_rail.value == 0, 8),
                TriValue(y_rail.value, nx_rail.value == 0, 8),
            )
            active = [driver for driver in drivers if not driver.is_z]
            conflict = len({driver.value for driver in active}) > 1
            result = None if not active else active[0].value
            if len(active) != 1 or conflict or result != (x ^ y):
                raise AssertionError(f"unsafe Switch XOR row x={x} y={y}")
            rows.append(
                {
                    "x": x,
                    "y": y,
                    "driver_left_one": {"value": drivers[0].value, "is_z": drivers[0].is_z},
                    "driver_left_zero": {"value": drivers[1].value, "is_z": drivers[1].is_z},
                    "active_driver_count": len(active),
                    "conflict": conflict,
                    "bus": {"value": result, "is_z": False, "arrival": 8},
                }
            )
    return rows


def _fix_switch_enable_entries(circuit: Circuit) -> Circuit:
    """Route current bottom-side Switch enables vertically into the sprite.

    The generic router assumes every scalar input faces left.  In 2.1.281 the
    Bit Switch enable moved to the bottom, so a horizontal final segment crosses
    one opaque sprite cell.  Only that two-cell suffix is replaced here; all
    earlier A* routing and every logical endpoint remain unchanged.
    """

    enable_positions = {
        base._pin(component, "enable")
        for component in circuit.components
        if component.kind == 12
    }
    changed = 0
    wires = []
    for wire in circuit.wires:
        points = wire_points(wire)
        target = points[-1]
        if (
            target in enable_positions
            and len(points) >= 3
            and points[-2] == (target[0] - 1, target[1])
        ):
            if points[-3] != (target[0] - 2, target[1]):
                raise AssertionError(f"unexpected Switch enable approach: {points[-4:]}")
            vertices = (
                *points[:-2],
                (target[0] - 2, target[1] + 1),
                (target[0], target[1] + 1),
                target,
            )
            wires.append(
                wire_from_vertices(
                    vertices,
                    color=wire.color,
                    comment=wire.comment,
                )
            )
            changed += 1
        else:
            wires.append(wire)
    if changed not in {0, 68}:
        raise AssertionError(f"rerouted {changed} Switch enables instead of 0 or 68")
    return replace(circuit, wires=tuple(wires))


def _compile_networks(circuit: Circuit) -> tuple[
    dict[int, list[object]],
    dict[tuple[int, str], int],
]:
    endpoint_owners: dict[Point, list[int]] = defaultdict(list)
    endpoints: list[tuple[Point, Point]] = []
    for wire_index, wire in enumerate(circuit.wires):
        points = wire_points(wire)
        pair = (points[0], points[-1])
        endpoints.append(pair)
        endpoint_owners[pair[0]].append(wire_index)
        endpoint_owners[pair[1]].append(wire_index)
    union = UnionFind(len(circuit.wires))
    for owners in endpoint_owners.values():
        for owner in owners[1:]:
            union.union(owners[0], owner)
    position_network = {
        position: union.find(wire_index)
        for wire_index, pair in enumerate(endpoints)
        for position in pair
    }
    network_pins: dict[int, list[object]] = defaultdict(list)
    pin_network: dict[tuple[int, str], int] = {}
    for index, component in enumerate(circuit.components):
        for pin in positioned_pins(component, index):
            if pin.position not in position_network:
                continue
            network = position_network[pin.position]
            network_pins[network].append(pin)
            pin_network[(index, pin.name)] = network
    return network_pins, pin_network


def _audit_switch_networks(circuit: Circuit) -> dict[str, object]:
    rows = _tristate_truth_table()
    network_pins, _ = _compile_networks(circuit)
    multi = []
    for network, pins in network_pins.items():
        drivers = [pin for pin in pins if pin.direction in {O, TRISTATE}]
        if len(drivers) <= 1:
            continue
        sinks = [pin for pin in pins if pin.direction == I]
        if len(drivers) != 2 or any(pin.component_kind != 12 for pin in drivers):
            raise AssertionError(f"network {network} has non-Switch multiple drivers")
        if any(pin.direction != TRISTATE for pin in drivers):
            raise AssertionError(f"network {network} has an ordinary multiple driver")
        if not sinks:
            raise AssertionError(f"Switch network {network} has no sink")
        multi.append(
            {
                "network": network,
                "driver_component_indices": sorted(pin.component_index for pin in drivers),
                "sink_component_indices": sorted({pin.component_index for pin in sinks}),
            }
        )
    if len(multi) != 34:
        raise AssertionError(f"expected 34 dual-Switch networks, found {len(multi)}")
    if sum(component.kind == 12 for component in circuit.components) != 68:
        raise AssertionError("every Switch must belong to one reviewed pair")
    return {
        "semantics": "Switch output is Z iff enable != 1; bus rejects disagreeing active drivers",
        "exhaustive_macro_rows": rows,
        "all_rows_exactly_one_active_driver": True,
        "all_rows_bus_is_z_false": True,
        "multi_driver_network_count": len(multi),
        "networks": multi,
    }


def _native_score(circuit: Circuit) -> dict[str, object]:
    gate = sum(GATE_COST.get(component.kind, 0) for component in circuit.components)
    if gate != GATE:
        raise AssertionError(f"native gate count {gate} != {GATE}")

    network_pins, _ = _compile_networks(circuit)
    successors = {index: set() for index in range(len(circuit.components))}
    predecessors = {index: set() for index in range(len(circuit.components))}
    delay_inputs: dict[int, set[int]] = {
        index: set()
        for index, component in enumerate(circuit.components)
        if component.kind == 13
    }
    for pins in network_pins.values():
        drivers = [pin.component_index for pin in pins if pin.direction in {O, TRISTATE}]
        sinks = [pin.component_index for pin in pins if pin.direction == I]
        for source in drivers:
            for sink in sinks:
                if circuit.components[sink].kind == 13:
                    delay_inputs[sink].add(source)
                else:
                    successors[source].add(sink)
                    predecessors[sink].add(source)

    indegree = {index: len(values) for index, values in predecessors.items()}
    ready = deque(index for index, value in indegree.items() if value == 0)
    order = []
    while ready:
        source = ready.popleft()
        order.append(source)
        for sink in successors[source]:
            indegree[sink] -= 1
            if indegree[sink] == 0:
                ready.append(sink)
    if len(order) != len(circuit.components):
        raise AssertionError("timing graph is cyclic after Delay boundaries")

    arrival: dict[int, int] = {}
    parent: dict[int, int] = {}
    for index in order:
        if predecessors[index]:
            predecessor = max(predecessors[index], key=arrival.__getitem__)
            incoming = arrival[predecessor]
            parent[index] = predecessor
        else:
            incoming = 0
        arrival[index] = incoming + DELAY_COST.get(circuit.components[index].kind, 0)

    terminals: list[tuple[int, int, str]] = [
        (arrival[index], index, "output")
        for index in range(len(circuit.components))
        if not successors[index]
    ]
    terminals.extend(
        (
            max((arrival[source] for source in sources), default=0),
            index,
            "delay-input",
        )
        for index, sources in delay_inputs.items()
    )
    delay, terminal, terminal_type = max(terminals)
    if delay != DELAY:
        raise AssertionError(f"native timing {delay} != {DELAY}")
    if terminal_type == "delay-input":
        current = max(delay_inputs[terminal], key=arrival.__getitem__)
    else:
        current = terminal
    path = []
    while True:
        component = circuit.components[current]
        path.append(
            {
                "component_index": current,
                "kind": component.kind,
                "position": list(component.position),
                "component_gate": GATE_COST.get(component.kind, 0),
                "component_delay": DELAY_COST.get(component.kind, 0),
                "arrival": arrival[current],
            }
        )
        if current not in parent:
            break
        current = parent[current]
    path.reverse()
    return {
        "gate": gate,
        "delay": delay,
        "critical_terminal_type": terminal_type,
        "critical_path": path,
    }


def _encoded_state(memory: dict[int, int]) -> int:
    result = 0
    for bit in range(base.WORD_BITS):
        key = stable_permanent_id(STATE_KEY, f"state-delay-{bit}")
        result |= (memory[key] & 1) << bit
    return result


def _verify_all_seeds(circuit: Circuit) -> dict[str, object]:
    compiled = _compile(circuit)
    pulse_id = stable_permanent_id(STATE_KEY, "load-pulse-delay")
    output_id = stable_permanent_id(STATE_KEY, "output-active-delay")
    output_count = 0
    seeds = tuple(
        dict.fromkeys(
            (
                *base._verification_seeds(),
                *(1 << bit for bit in range(32)),
                0x7FFFFFFF,
                0x80000000,
                0xFFFFFFFE,
            )
        )
    )
    for seed in seeds:
        memory = initial_clocked_memory(circuit)
        expected = seed
        for tick in range(CYCLES):
            expected_control = (0, 0) if tick == 0 else (1, 0) if tick == 1 else (0, 1)
            actual_control = (memory[pulse_id], memory[output_id])
            if actual_control != expected_control:
                raise AssertionError(
                    f"control mismatch seed={seed:08x} tick={tick}: "
                    f"{actual_control} != {expected_control}"
                )
            result = _simulate_clocked_tick(
                circuit,
                compiled=compiled,
                inputs={"Seed": seed},
                memory=memory,
            )
            if tick < 2:
                if result.outputs:
                    raise AssertionError(f"premature output seed={seed:08x} tick={tick}")
                expected_state = 0 if tick == 0 else base.apply_matrix(base.T, seed)
            else:
                expected = base.xorshift32(expected)
                if result.outputs != {"RNG output": expected}:
                    raise AssertionError(
                        f"output mismatch seed={seed:08x} tick={tick}: "
                        f"{result.outputs} != {expected:08x}"
                    )
                expected_state = base.apply_matrix(base.T, expected)
                output_count += 1
            if _encoded_state(result.memory) != expected_state:
                raise AssertionError(f"state mismatch seed={seed:08x} tick={tick}")
            memory = result.memory
    return {
        "seed_count": len(seeds),
        "tick_count": len(seeds) * CYCLES,
        "output_count": output_count,
        "outputs_per_seed": 65,
        "coverage": "256 deterministic full-width seeds + every U32 unit basis + high-bit boundaries",
        "control_trace": [[0, 0], [1, 0], [0, 1]],
    }


def _layout(circuit: Circuit) -> dict[str, object]:
    # Cached candidates bypass build_candidate(), so install the same reviewed
    # bounds here before invoking the shared conservative geometry audit.
    _install_switch_geometry()
    layout = base._layout_safety(circuit)
    if any(layout.values()):
        raise AssertionError(f"conservative geometry failure: {layout}")
    sprite = audit_sprite_geometry(circuit, DEFAULT_COMPONENT_SPRITE_ROOT)
    internal = tuple(
        collision
        for collision in sprite.wire_collisions
        if collision.component_kind not in {62, 70}
    )
    if (
        sprite.unsupported_component_kinds
        or sprite.component_overlap_cells
        or internal
        or sprite.wire_interior_pin_contacts
    ):
        raise AssertionError(
            "sprite geometry failure: "
            f"unsupported={sprite.unsupported_component_kinds}, "
            f"overlap={len(sprite.component_overlap_cells)}, "
            f"wire={len(internal)}, pins={len(sprite.wire_interior_pin_contacts)}"
        )
    return {
        "conservative": layout,
        "sprite": {
            "unsupported_component_kinds": list(sprite.unsupported_component_kinds),
            "component_overlap_cell_count": len(sprite.component_overlap_cells),
            "internal_wire_collision_count": len(internal),
            "wire_interior_pin_contact_count": len(sprite.wire_interior_pin_contacts),
        },
    }


def _dont_care_reuse_certificate() -> dict[str, object]:
    rows = []
    covered_nodes = set()
    for feedback_target, output_target in DONT_CARE_GATE_PAIRS:
        feedback_gate = base.GATE_BY_OUTPUT[feedback_target]
        output_gate = base.GATE_BY_OUTPUT[output_target]
        if feedback_target not in base.B or feedback_target in base.C:
            raise AssertionError(f"{feedback_target:08x} is not B-only")
        if output_target not in base.C or output_target in base.B:
            raise AssertionError(f"{output_target:08x} is not C-only")
        feedback_direct = [
            (side, node)
            for side, node in enumerate((feedback_gate.left, feedback_gate.right))
            if node in base.DIRECT
        ]
        output_direct = [
            (side, node)
            for side, node in enumerate((output_gate.left, output_gate.right))
            if node in base.DIRECT
        ]
        if len(feedback_direct) != 1 or len(output_direct) != 1:
            raise AssertionError("don't-care pair lost its unique direct operand")
        feedback_side, feedback_node = feedback_direct[0]
        output_side, output_node = output_direct[0]
        if feedback_node != output_node:
            raise AssertionError("don't-care pair does not share the same q bit")
        mode_key = _direct_leaf_key(feedback_gate, feedback_side, feedback_node)
        raw_key = _direct_leaf_key(output_gate, output_side, output_node)
        if not mode_key[1] or raw_key[1]:
            raise AssertionError("don't-care pair mode/raw polarity changed")
        covered_nodes.add(feedback_node)
        rows.append(
            {
                "state_bit": base.bits(feedback_node)[0],
                "shared_mode_pair": {
                    "seed_bit": base.bits(mode_key[1])[0],
                    "state_bit": base.bits(mode_key[0])[0],
                },
                "feedback_target": f"{feedback_target:08x}",
                "feedback_membership": "B-only",
                "output_target": f"{output_target:08x}",
                "output_membership": "C-only",
                "steady_identity": "mode_leaf = state_leaf because architecture input is disabled",
                "load_safety": "C-only value is not observed and never feeds encoded-state B",
            }
        )
    if len(covered_nodes) != 5:
        raise AssertionError("don't-care certificate must cover five distinct state leaves")
    return {
        "raw_direct_leaf_count_before": 10,
        "shared_mode_rail_count_after": 5,
        "saved_not_gate": 5,
        "pairs": rows,
    }


def _gate_table(circuit: Circuit) -> dict[str, object]:
    counts = Counter(component.kind for component in circuit.components)
    expected = {
        3: 6,
        4: 27,
        6: 54,
        7: 75,
        12: 68,
        13: 34,
        16: 4,
        17: 4,
        62: 1,
        70: 1,
        97: 1,
        99: 1,
    }
    for kind, count in expected.items():
        if counts[kind] != count:
            raise AssertionError(f"kind {kind} count {counts[kind]} != {count}")
    if set(counts) != set(expected):
        raise AssertionError(f"unexpected component kinds: {sorted(set(counts) - set(expected))}")
    categories = {
        "32 state Delay Bit": 32 * 5,
        "2 phase Delay Bit": 2 * 5,
        "47 mode OR": 47,
        "27 dual XOR/XNOR cells (4 each)": 27 * 4,
        "5 shared direct-leaf NOT": 5,
        "68 Bit Switch": 68 * 2,
        "phase OR + NOT": 2,
    }
    if sum(categories.values()) != GATE:
        raise AssertionError("category gate table changed")
    return {
        "component_kind_counts": {str(kind): counts[kind] for kind in sorted(counts)},
        "category_costs": categories,
        "total": sum(categories.values()),
        "cost_model": {
            "NOT/AND/NAND/OR": "1 gate / 1 delay",
            "Bit Switch": "2 gate / 1 delay",
            "Delay Bit": "5 gate / 4 delay",
            "dual XOR/XNOR": "four explicit primitives / 4 gate / 2 delay",
        },
    }


def main() -> None:
    if CACHE_DATA.is_file():
        circuit = decode_v15(CACHE_DATA.read_bytes())
    else:
        circuit = build_candidate()
        CACHE_DATA.write_bytes(encode_v15(circuit))
    circuit = _fix_switch_enable_entries(circuit)
    CACHE_DATA.write_bytes(encode_v15(circuit))
    gate_table = _gate_table(circuit)
    tristate = _audit_switch_networks(circuit)
    native_score = _native_score(circuit)
    connectivity = analyze_connectivity(circuit)
    for field in (
        "unsupported_component_kind_counts",
        "unconnected_pin_count",
        "undriven_network_count",
        "width_mismatch_network_count",
        "cycle_component_count",
    ):
        if connectivity[field]:
            raise AssertionError(f"connectivity failure {field}: {connectivity[field]}")
    # The generic connectivity report deliberately accepts a network when all
    # of its multiple drivers are tristate.  The stricter audit above counts
    # and proves the 34 such buses, while this generic error field stays zero.
    if connectivity["multi_driver_network_count"] != 0:
        raise AssertionError("a reviewed Switch bus contains an ordinary driver")
    layout = _layout(circuit)
    stream = _verify_all_seeds(circuit)
    payload = encode_v15(circuit)
    if decode_v15(payload) != circuit:
        raise AssertionError("v15 round trip failed")
    OUTPUT_DATA.write_bytes(payload)
    result = {
        "schema": 1,
        "status": "offline-verified; game verification pending",
        "artifact": OUTPUT_DATA.name,
        "sha256": sha256(payload).hexdigest(),
        "leaderboard_tuple": [GATE, DELAY, CYCLES],
        "energy": ENERGY,
        "reference": [431, 9, 66, REFERENCE],
        "improvement": REFERENCE - ENERGY,
        "uses_ram": False,
        "all_delay_init_data_zero": all(
            component.init_data == 0 for component in circuit.components if component.kind == 13
        ),
        "component_count": len(circuit.components),
        "wire_count": len(circuit.wires),
        "gate_table": gate_table,
        "load_dont_care_reuse": _dont_care_reuse_certificate(),
        "tristate": tristate,
        "native_score": native_score,
        "connectivity": connectivity,
        "layout": layout,
        "stream": stream,
        "timing_explanation": (
            "Delay 4 + mode OR 1 + explicit dual cell 2 + Bit Switch 1 = 8"
        ),
        "evidence_boundary": (
            "v15 structure, explicit primitive costs, exact tristate macro, topology, "
            "256x67 ticks and geometry are offline verified; game/server must recompute score"
        ),
    }
    OUTPUT_JSON.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": result["status"],
                "leaderboard_tuple": result["leaderboard_tuple"],
                "energy": result["energy"],
                "improvement": result["improvement"],
                "sha256": result["sha256"],
                "components": result["component_count"],
                "wires": result["wire_count"],
                "all_switch_buses_driven": result["tristate"]["all_rows_bus_is_z_false"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
