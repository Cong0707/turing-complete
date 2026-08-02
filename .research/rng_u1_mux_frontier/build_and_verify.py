"""Build and exhaustively audit the 350/10/67 U1-MUX RNG candidate.

This is an isolated research generator.  It never reads or writes the live
save and it never starts Turing Complete.  It starts from the independently
verified 468/8/67 encoded-state DAG, then implements every second-layer XOR as
a width-one native MUX::

    mux(select=x, in0=y, in1=NOT y) == x XOR y

Only the data operand needs both rails.  Choosing the data side of all 34 XORs
is therefore a minimum vertex-cover problem.  The deterministic exact optimum
used here has 13 of the 27 first-layer complement rails and three of five shared direct-leaf complement
rails.  Every ordinary XOR is still charged 3 gates / 2 delay; the MUX is
charged from the current RNG level override as 1 gate / 3 delay.
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

GATE = 350
DELAY = 10
CYCLES = 67
ENERGY = GATE * DELAY * CYCLES
REFERENCE = 402 * 9 * 67
KEY = "architecture/codex-rng-u1-mux-frontier"
STATE_KEY = "architecture/codex-rng-encoded"

GATE_COST = {
    3: 1,   # NOT
    4: 1,   # AND
    6: 1,   # NAND
    7: 1,   # OR
    13: 5,  # Delay Bit
    42: 1,  # U1 MUX under the current RNG level override
}
DELAY_COST = {
    3: 1,
    4: 1,
    6: 1,
    7: 1,
    13: 4,
    42: 3,
}

def _install_mux_geometry() -> None:
    """Teach the shared conservative router the current U1 MUX bounds."""

    base._FOOTPRINT_BOXES.setdefault(4, (-1, -2, 2, 2))
    base._FOOTPRINT_BOXES.setdefault(6, (-1, -2, 2, 2))
    base._FOOTPRINT_BOXES.setdefault(42, (-1, -2, 2, 2))


@dataclass(frozen=True)
class Rail:
    positive: Point
    negative: Point | None


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


Vertex = tuple[object, ...]


def _canonical_direct_keys(
    second_gates: tuple[base.XorGate, ...],
) -> tuple[
    dict[tuple[int, int], tuple[int, int]],
    dict[tuple[int, int], tuple[base.XorGate, int]],
]:
    """Collapse each B-only/C-only direct leaf pair onto its mode rail."""

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

    canonical: dict[tuple[int, int], tuple[int, int]] = {}
    for values in keys_by_node.values():
        raw = [key for key in values if key[1] == 0]
        mode = [key for key in values if key[1] != 0]
        if len(raw) != 1 or len(mode) != 1:
            raise AssertionError(f"direct pair is not one raw plus one mode: {values}")
        canonical[raw[0]] = mode[0]
        canonical[mode[0]] = mode[0]

    direct_consumer: dict[tuple[int, int], tuple[base.XorGate, int]] = {}
    for gate in second_gates:
        for side, node in enumerate((gate.left, gate.right)):
            if node in base.FIRST_LAYER:
                continue
            key = _direct_leaf_key(gate, side, node)
            if key == canonical[key]:
                direct_consumer[canonical[key]] = (gate, side)
    if set(direct_consumer) != set(canonical.values()):
        raise AssertionError("every shared mode rail needs one B-only placement anchor")
    return canonical, direct_consumer


def _fanin_vertex(
    gate: base.XorGate,
    side: int,
    node: int,
    canonical_direct_key: dict[tuple[int, int], tuple[int, int]],
) -> Vertex:
    if node in base.FIRST_LAYER:
        return ("first", node)
    return ("direct", *canonical_direct_key[_direct_leaf_key(gate, side, node)])


def _minimum_complement_cover(
    second_gates: tuple[base.XorGate, ...],
    canonical_direct_key: dict[tuple[int, int], tuple[int, int]],
) -> tuple[frozenset[Vertex], tuple[tuple[Vertex, Vertex, int], ...]]:
    """Solve the exact data-side choice as an unweighted vertex cover."""

    full_edges = tuple(
        (
            _fanin_vertex(gate, 0, gate.left, canonical_direct_key),
            _fanin_vertex(gate, 1, gate.right, canonical_direct_key),
            gate.output,
        )
        for gate in second_gates
    )
    edge_pairs = tuple(
        sorted(
            (tuple(sorted((left, right))) for left, right, _ in full_edges),
            key=repr,
        )
    )

    from functools import lru_cache

    @lru_cache(maxsize=None)
    def solve(edges: tuple[tuple[Vertex, Vertex], ...]) -> frozenset[Vertex]:
        if not edges:
            return frozenset()
        degree = Counter(vertex for edge in edges for vertex in edge)
        left, right = max(
            edges,
            key=lambda edge: (
                degree[edge[0]] + degree[edge[1]],
                repr(edge),
            ),
        )

        def branch(vertex: Vertex) -> frozenset[Vertex]:
            remaining = tuple(edge for edge in edges if vertex not in edge)
            return solve(remaining) | {vertex}

        options = (branch(left), branch(right))
        return min(options, key=lambda value: (len(value), tuple(sorted(map(repr, value)))))

    cover = solve(edge_pairs)
    if len(cover) != 16:
        raise AssertionError(f"minimum complement cover changed: {len(cover)}")
    if any(left not in cover and right not in cover for left, right, _ in full_edges):
        raise AssertionError("minimum complement cover leaves an XOR edge uncovered")
    return cover, full_edges


def _build_components() -> tuple[
    tuple[Component, ...],
    dict[str, object],
]:
    first_gates = tuple(gate for gate in base.GATES if gate.depth == 1)
    second_gates = tuple(gate for gate in base.GATES if gate.depth == 2)
    first_index = {gate.output: index for index, gate in enumerate(first_gates)}
    second_index = {gate.output: index for index, gate in enumerate(second_gates)}
    canonical_direct_key, direct_consumer = _canonical_direct_keys(second_gates)
    complement_cover, cover_edges = _minimum_complement_cover(
        second_gates, canonical_direct_key
    )

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

    # Every first-layer node has an explicit three-gate positive XOR rail:
    #   either = OR(a,b), not_both = NAND(a,b)
    #   XOR = AND(either,not_both)
    # Only cover vertices add the fourth XNOR=NAND(either,not_both) gate.
    dual_cells: dict[int, dict[str, Component]] = {}
    for index, gate in enumerate(first_gates):
        y = _first_y(index)
        cell = {
            "either": _component(f"dual-{gate.output:08x}-either", 7, (-170, y - 4)),
            "not_both": _component(f"dual-{gate.output:08x}-not-both", 6, (-170, y + 4)),
            "xor": _component(f"dual-{gate.output:08x}-xor", 4, (-125, y - 4)),
        }
        if ("first", gate.output) in complement_cover:
            cell["xnor"] = _component(
                f"dual-{gate.output:08x}-xnor", 6, (-125, y + 4)
            )
        dual_cells[gate.output] = cell

    direct_keys = sorted(set(canonical_direct_key.values()))
    selected_direct_keys = {
        (int(vertex[1]), int(vertex[2]))
        for vertex in complement_cover
        if vertex[0] == "direct"
    }
    direct_nots = {
        key: _component(
            f"direct-not-state-{base.bits(key[0])[0]}-seed-{key[1]:08x}",
            3,
            (-30, _second_y(second_index[direct_consumer[key][0].output])),
        )
        for key in sorted(selected_direct_keys)
    }

    muxes: dict[int, Component] = {}
    for index, gate in enumerate(second_gates):
        y = _second_y(index)
        muxes[gate.output] = _component(
            f"mux-u1-{gate.output:08x}", 42, (30, y), word_size=1
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
        *(direct_nots[key] for key in sorted(direct_nots)),
        *(muxes[gate.output] for gate in second_gates),
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
        "complement_cover": complement_cover,
        "cover_edges": cover_edges,
        "muxes": muxes,
        "byte_makers": byte_makers,
        "word_maker": word_maker,
        "first_gates": first_gates,
        "second_gates": second_gates,
    }


def build_candidate() -> Circuit:
    components, parts = _build_components()

    # The original conservative router already knows every reused component.
    # Add conservative current-v15 sprite bounds for explicit cells and U1 MUX.
    _install_mux_geometry()
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
    complement_cover = parts["complement_cover"]
    muxes = parts["muxes"]
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
        for output in (cell["xor"], *(cell[key] for key in ("xnor",) if key in cell)):
            wires.append(route(base._pin(cell["either"], "out"), base._pin(output, "in0")))
            wires.append(route(base._pin(cell["not_both"], "out"), base._pin(output, "in1")))
        rails[gate.output] = Rail(
            base._pin(cell["xor"], "out"),
            base._pin(cell["xnor"], "out") if "xnor" in cell else None,
        )

    canonical_rails: dict[tuple[int, int], Rail] = {}
    for key in sorted(set(canonical_direct_key.values())):
        node, seed_form = key
        positive = base._mode_source(
            seed_form,
            node,
            state_sources=state_sources,
            mode_sources=mode_sources,
        )
        inverter = direct_nots.get(key)
        if inverter is not None:
            wires.append(route(positive, base._pin(inverter, "in")))
        canonical_rails[key] = Rail(
            positive,
            None if inverter is None else base._pin(inverter, "out"),
        )
    direct_rails = {
        key: canonical_rails[canonical]
        for key, canonical in canonical_direct_key.items()
    }

    mux_outputs: dict[int, Point] = {}
    for gate in second_gates:
        fanin_rails = []
        for side, node in enumerate((gate.left, gate.right)):
            if node in rails:
                fanin_rails.append(rails[node])
            else:
                fanin_rails.append(direct_rails[_direct_leaf_key(gate, side, node)])
        vertices = (
            _fanin_vertex(gate, 0, gate.left, canonical_direct_key),
            _fanin_vertex(gate, 1, gate.right, canonical_direct_key),
        )
        # Prefer the right data side for deterministic routing when both cover
        # vertices are selected.  Exactly one selected endpoint is sufficient.
        data_side = 1 if vertices[1] in complement_cover else 0
        selector_side = 1 - data_side
        data = fanin_rails[data_side]
        selector = fanin_rails[selector_side]
        if data.negative is None:
            raise AssertionError(f"MUX data operand lacks complement: {vertices[data_side]}")
        mux = muxes[gate.output]
        wires.append(route(selector.positive, base._pin(mux, "select")))
        wires.append(route(data.positive, base._pin(mux, "in0")))
        wires.append(route(data.negative, base._pin(mux, "in1")))
        mux_outputs[gate.output] = base._pin(mux, "out")

    def connect_target(target: int, sink: Point) -> None:
        if target in mux_outputs:
            wires.append(route(mux_outputs[target], sink))
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
            "Codex RNG ASIC: exact minimum complement cover and U1 MUX "
            "second-layer XOR"
        ),
        components=components,
        wires=tuple(wires),
    )


def _mux_truth_table() -> list[dict[str, int]]:
    rows = []
    for x in (0, 1):
        for y in (0, 1):
            result = y if x == 0 else 1 ^ y
            if result != (x ^ y):
                raise AssertionError(f"unsafe MUX XOR row x={x} y={y}")
            rows.append({"select": x, "in0": y, "in1": 1 ^ y, "out": result})
    return rows


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


def _audit_mux_networks(circuit: Circuit) -> dict[str, object]:
    rows = _mux_truth_table()
    network_pins, _ = _compile_networks(circuit)
    for network, pins in network_pins.items():
        drivers = [pin for pin in pins if pin.direction in {O, TRISTATE}]
        if len(drivers) > 1:
            raise AssertionError(f"MUX candidate network {network} has multiple drivers")
    muxes = [component for component in circuit.components if component.kind == 42]
    if len(muxes) != 34 or any(component.word_size != 1 for component in muxes):
        raise AssertionError("candidate must contain exactly 34 width-one kind-42 MUXes")
    return {
        "serialized_kind": 42,
        "serialized_word_size": 1,
        "pin_semantics": "select=0 -> in0; select=1 -> in1; ordinary driven output",
        "exhaustive_macro_rows": rows,
        "mux_count": len(muxes),
        "multi_driver_network_count": 0,
        "z_generated_by_mux": False,
    }


def _native_score(
    circuit: Circuit,
    *,
    mux_delay: int = 3,
    expected_delay: int = DELAY,
) -> dict[str, object]:
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
        component_delay = (
            mux_delay
            if circuit.components[index].kind == 42
            else DELAY_COST.get(circuit.components[index].kind, 0)
        )
        arrival[index] = incoming + component_delay

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
    if delay != expected_delay:
        raise AssertionError(f"native timing {delay} != {expected_delay}")
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
                "component_delay": mux_delay if component.kind == 42 else DELAY_COST.get(component.kind, 0),
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
        "mux_delay": mux_delay,
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


def _verify_gf2_full_space() -> dict[str, object]:
    """Prove the encoded recurrence on a basis, hence on all 2^32 states."""

    if base.compose(base.C, base.T) != base.A:
        raise AssertionError("C*T != A")
    if base.compose(base.T, base.C) != base.B:
        raise AssertionError("T*C != B")
    if base.compose(base.T, base.T_INVERSE) != base.IDENTITY:
        raise AssertionError("T*T^-1 != I")
    checked_outputs = 0
    for bit in range(base.WORD_BITS):
        seed = 1 << bit
        expected = seed
        encoded = base.apply_matrix(base.T, seed)
        for _ in range(65):
            expected = base.apply_matrix(base.A, expected)
            actual = base.apply_matrix(base.C, encoded)
            if actual != expected:
                raise AssertionError(f"GF(2) output mismatch on basis bit {bit}")
            encoded = base.apply_matrix(base.B, encoded)
            checked_outputs += 1
    return {
        "field": "GF(2)",
        "basis_vectors": 32,
        "iterations_per_basis": 65,
        "checked_outputs": checked_outputs,
        "identities": ["C*T=A", "T*C=B", "T*T^-1=I"],
        "full_space_conclusion": "linearity extends the basis proof to every U32 seed",
    }


def _audit_z_boundary(circuit: Circuit) -> dict[str, object]:
    """Ensure no MUX pin can receive a tristate driver or multi-driver bus."""

    network_pins, pin_network = _compile_networks(circuit)
    audited = 0
    driver_kinds: Counter[int] = Counter()
    for index, component in enumerate(circuit.components):
        if component.kind != 42:
            continue
        for name in ("select", "in0", "in1"):
            network = pin_network[(index, name)]
            drivers = [
                pin
                for pin in network_pins[network]
                if pin.direction in {O, TRISTATE}
            ]
            if len(drivers) != 1 or drivers[0].direction != O:
                raise AssertionError(
                    f"MUX {index} {name} is not singly driven by an ordinary output"
                )
            if drivers[0].component_kind in {62}:
                raise AssertionError("architecture tristate input reaches a MUX directly")
            driver_kinds[drivers[0].component_kind] += 1
            audited += 1
        out_network = pin_network[(index, "out")]
        output_pin = next(
            pin
            for pin in network_pins[out_network]
            if pin.component_index == index and pin.name == "out"
        )
        if output_pin.direction != O:
            raise AssertionError("kind-42 output unexpectedly became tristate")
    if audited != 34 * 3:
        raise AssertionError(f"audited {audited} MUX inputs instead of 102")
    return {
        "mux_input_pin_count": audited,
        "all_mux_inputs_single_ordinary_driver": True,
        "mux_output_direction": "ordinary output",
        "mux_input_driver_kind_counts": {
            str(kind): count for kind, count in sorted(driver_kinds.items())
        },
        "z_leak_count": 0,
        "multi_driver_count": 0,
    }


def _layout(circuit: Circuit) -> dict[str, object]:
    # Cached candidates bypass build_candidate(), so install the same reviewed
    # bounds here before invoking the shared conservative geometry audit.
    _install_mux_geometry()
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
        "selected_complement_groups": 3,
        "unselected_complement_groups": 2,
        "not_gate_count": 3,
        "pairs": rows,
    }


def _cover_certificate() -> dict[str, object]:
    second_gates = tuple(gate for gate in base.GATES if gate.depth == 2)
    canonical, _ = _canonical_direct_keys(second_gates)
    cover, edges = _minimum_complement_cover(second_gates, canonical)
    first = sorted(int(vertex[1]) for vertex in cover if vertex[0] == "first")
    direct = sorted(
        (int(vertex[1]), int(vertex[2]))
        for vertex in cover
        if vertex[0] == "direct"
    )
    rows = []
    for left, right, output in edges:
        data = right if right in cover else left
        selector = left if data == right else right
        rows.append(
            {
                "output": f"{output:08x}",
                "selector_vertex": repr(selector),
                "data_vertex": repr(data),
            }
        )
    return {
        "problem": "one complemented data endpoint must cover each second-layer XOR edge",
        "vertex_count": len({vertex for edge in edges for vertex in edge[:2]}),
        "edge_count": len(edges),
        "exact_minimum_cover_size": len(cover),
        "first_layer_complement_count": len(first),
        "direct_group_complement_count": len(direct),
        "first_layer_complements": [f"{value:08x}" for value in first],
        "direct_group_complements": [
            {"state": f"{state:08x}", "seed": f"{seed:08x}"}
            for state, seed in direct
        ],
        "orientations": rows,
    }


def _gate_table(circuit: Circuit) -> dict[str, object]:
    counts = Counter(component.kind for component in circuit.components)
    expected = {
        3: 4,
        4: 27,
        6: 40,
        7: 75,
        13: 34,
        16: 4,
        17: 4,
        42: 34,
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
        "27 positive XOR cells (3 each)": 27 * 3,
        "13 selected first-layer complements": 13,
        "3 selected direct-leaf NOT": 3,
        "34 width-one MUX": 34,
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
            "U1 MUX": "1 gate / 3 delay from imported byte_mux 34/3 frontier",
            "Delay Bit": "5 gate / 4 delay",
            "positive XOR": "three explicit primitives / 3 gate / 2 delay",
            "selected complement": "one extra NAND or NOT / 1 gate / 1 delay",
        },
    }


def main() -> None:
    circuit = build_candidate()
    gate_table = _gate_table(circuit)
    cover = _cover_certificate()
    mux = _audit_mux_networks(circuit)
    z_audit = _audit_z_boundary(circuit)
    native_score = _native_score(circuit, mux_delay=3, expected_delay=10)
    default_fallback_score = _native_score(circuit, mux_delay=4, expected_delay=11)
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
    if connectivity["multi_driver_network_count"] != 0:
        raise AssertionError("MUX candidate contains a multiple-driver network")
    layout = _layout(circuit)
    stream = _verify_all_seeds(circuit)
    gf2 = _verify_gf2_full_space()
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
        "reference": [402, 9, 67, REFERENCE],
        "improvement": REFERENCE - ENERGY,
        "uses_ram": False,
        "all_delay_init_data_zero": all(
            component.init_data == 0 for component in circuit.components if component.kind == 13
        ),
        "component_count": len(circuit.components),
        "wire_count": len(circuit.wires),
        "gate_table": gate_table,
        "complement_cover": cover,
        "load_dont_care_reuse": _dont_care_reuse_certificate(),
        "mux": mux,
        "z_audit": z_audit,
        "native_score": native_score,
        "default_prototype_fallback": {
            "leaderboard_tuple": [GATE, default_fallback_score["delay"], CYCLES],
            "energy": GATE * default_fallback_score["delay"] * CYCLES,
            "native_score": default_fallback_score,
            "competitive": False,
        },
        "cost_provenance": {
            "component": "com_mux",
            "kind": 42,
            "word_size": 1,
            "profile_frontier_snapshot": "examples/byte_mux/level.json score_history=34&3&1|",
            "unlock_evidence": "campaign/byte_mux/meta.txt unlocks_components=[com_mux]",
            "runtime_dispatch": "kind42 is outside default bitmap; imported component cost is used when present",
            "gate_formula": "b*(w//8)+(w%8) for remainder<=3; w=1 gives 1",
            "delay_formula": "b; imported byte_mux delay=3 gives U1 MUX delay=3",
            "fallback": "without imported component cost, default prototype is 1 gate / 4 delay",
        },
        "connectivity": connectivity,
        "layout": layout,
        "stream": stream,
        "gf2": gf2,
        "timing_explanation": (
            "Delay 4 + mode OR 1 + explicit positive/complement cell 2 + imported U1 MUX 3 = 10"
        ),
        "evidence_boundary": (
            "v15 structure, exact MUX macro, topology, 256x67 ticks, GF(2), Z boundary "
            "and geometry are offline verified; game/server must confirm imported 1/3 MUX cost"
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
                "muxes": result["mux"]["mux_count"],
                "z_leaks": result["z_audit"]["z_leak_count"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
