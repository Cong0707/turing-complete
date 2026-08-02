"""Read-only native gate/delay audit for the all-U1-Word-XOR RNG candidate."""

from __future__ import annotations

import argparse
from collections import Counter, deque
import csv
from hashlib import sha256
import json
import os
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from tc_save_lab.analysis import wire_points  # noqa: E402
from tc_save_lab.codec import decode_v15, encode_v15  # noqa: E402
from tc_save_lab.pins import I, positioned_pins  # noqa: E402


COMPONENT_NAMES = {
    2: "Constant On",
    3: "NOT Bit",
    7: "OR Bit",
    10: "XOR Bit",
    13: "Delay Bit",
    16: "Maker Bit 8",
    17: "Splitter Bit 8",
    23: "XOR Word",
    46: "Constant",
    54: "RAM Load",
    56: "RAM Store",
    62: "Architecture Input",
    70: "Architecture Output",
    97: "Maker Word 4",
    99: "Splitter Word 4",
    118: "RAM",
}


def progress_frontier(path: Path, level: str) -> list[tuple[int, int, int]]:
    with path.open("r", encoding="utf-8", newline="") as stream:
        rows = list(csv.reader(stream))
    matches = [row for row in rows if len(row) == 4 and row[0] == level]
    if len(matches) != 1:
        raise RuntimeError(f"expected one {level!r} progress row, got {len(matches)}")
    return [
        tuple(int(value) for value in item.split("&"))
        for item in matches[0][3].split("|")
        if item
    ]


def component_graph(circuit):
    pins_by_position = {}
    for component_index, component in enumerate(circuit.components):
        for pin in positioned_pins(component, component_index):
            if pin.position in pins_by_position:
                raise RuntimeError(f"ambiguous pin position {pin.position}")
            pins_by_position[pin.position] = pin

    edges = {}
    for wire_index, wire in enumerate(circuit.wires):
        points = wire_points(wire)
        endpoint_pins = (pins_by_position.get(points[0]), pins_by_position.get(points[-1]))
        if any(pin is None for pin in endpoint_pins):
            raise RuntimeError(f"wire {wire_index} does not end on two pins")
        outputs = [pin for pin in endpoint_pins if pin.direction != I]
        inputs = [pin for pin in endpoint_pins if pin.direction == I]
        if len(outputs) != 1 or len(inputs) != 1:
            raise RuntimeError(f"wire {wire_index} is not output-to-input")
        source, sink = outputs[0], inputs[0]
        edges.setdefault((source.component_index, sink.component_index), []).append(
            {
                "wire_index": wire_index,
                "source_pin": source.name,
                "sink_pin": sink.name,
            }
        )
    return edges


def timing(circuit, component_delays):
    edges = component_graph(circuit)
    count = len(circuit.components)
    successors = {index: set() for index in range(count)}
    predecessors = {index: set() for index in range(count)}
    for source, sink in edges:
        successors[source].add(sink)
        predecessors[sink].add(source)

    indegree = {index: len(predecessors[index]) for index in range(count)}
    ready = deque(index for index in range(count) if indegree[index] == 0)
    order = []
    while ready:
        source = ready.popleft()
        order.append(source)
        for sink in sorted(successors[source]):
            indegree[sink] -= 1
            if indegree[sink] == 0:
                ready.append(sink)
    if len(order) != count:
        cyclic = [index for index in range(count) if indegree[index]]
        raise RuntimeError(f"component timing graph is cyclic: {cyclic}")

    incoming = {}
    arrival = {}
    chosen_predecessor = {}
    for index in order:
        if predecessors[index]:
            parent = max(sorted(predecessors[index]), key=lambda item: arrival[item])
            chosen_predecessor[index] = parent
            incoming[index] = arrival[parent]
        else:
            incoming[index] = 0
        arrival[index] = incoming[index] + component_delays[index]

    native_delay = max(incoming.values())
    max_arrival = max(arrival.values())
    if native_delay != max_arrival:
        raise RuntimeError(
            "candidate lacks a zero-delay sink for the maximum output arrival: "
            f"native={native_delay}, output={max_arrival}"
        )

    critical_terminals = [
        index
        for index in range(count)
        if not successors[index] and arrival[index] == native_delay
    ]
    preferred = [
        index
        for kind in (70, 56, 54, 118)
        for index in critical_terminals
        if circuit.components[index].kind == kind
    ]
    sink = preferred[0] if preferred else critical_terminals[0]

    path = []
    current = sink
    while True:
        component = circuit.components[current]
        entry = {
            "component_index": current,
            "kind": component.kind,
            "name": COMPONENT_NAMES[component.kind],
            "position": list(component.position),
            "component_delay": component_delays[current],
            "incoming_arrival": incoming[current],
            "output_arrival": arrival[current],
        }
        parent = chosen_predecessor.get(current)
        if parent is not None:
            entry["incoming_edges"] = edges[(parent, current)]
        path.append(entry)
        if parent is None:
            break
        current = parent
    path.reverse()

    return {
        "native_delay": native_delay,
        "maximum_output_arrival": max_arrival,
        "critical_terminal_indices": critical_terminals,
        "selected_critical_path": path,
        "edges": edges,
    }


def audit(candidate_path: Path, levels_path: Path) -> dict[str, object]:
    payload = candidate_path.read_bytes()
    circuit = decode_v15(payload)
    if candidate_path.read_bytes() != payload:
        raise RuntimeError("candidate changed during audit")
    if encode_v15(circuit) != payload:
        raise RuntimeError("candidate is not a byte-identical v15 round trip")

    xor_frontier = progress_frontier(levels_path, "xor_gate")
    if xor_frontier != [(3, 2, 1)]:
        raise RuntimeError(f"unexpected live XOR frontier: {xor_frontier}")
    xor_gate, xor_delay, _ = xor_frontier[0]

    rams = [component for component in circuit.components if component.kind == 118]
    loads = [component for component in circuit.components if component.kind == 54]
    stores = [component for component in circuit.components if component.kind == 56]
    if (len(rams), len(loads), len(stores)) != (1, 1, 1):
        raise RuntimeError("expected one RAM, one load, and one store")
    ram, load, store = rams[0], loads[0], stores[0]
    if ram.settings != (2, 512, 0) or ram.buffer_size != 8:
        raise RuntimeError(
            f"unexpected RAM fields: settings={ram.settings}, buffer={ram.buffer_size}"
        )
    if load.word_size != 32 or store.word_size != 32:
        raise RuntimeError("RAM ports are not U32")

    zero_cost_kinds = {2, 16, 17, 46, 62, 70, 97, 99}
    reviewed_kinds = zero_cost_kinds | {3, 7, 10, 13, 23, 54, 56, 118}
    unexpected = sorted({component.kind for component in circuit.components} - reviewed_kinds)
    if unexpected:
        raise RuntimeError(f"unreviewed component kinds: {unexpected}")

    word_xor_base_gate = xor_gate * 8
    word_xor_delay = xor_delay
    ram_gate = ram.buffer_size if ram.settings[0] else 50 * ram.buffer_size
    ram_delay = 512 // (ram.settings[1] + 1) if ram.settings[0] else None

    def word_xor_gate(width: int) -> int:
        quotient, remainder = divmod(width, 8)
        if remainder <= 3:
            return word_xor_base_gate * quotient + remainder
        return word_xor_base_gate * (quotient + 1) + remainder - 8

    def gate_cost(component) -> int:
        if component.kind in zero_cost_kinds:
            return 0
        if component.kind in {3, 7}:
            return 1
        if component.kind == 10:
            return xor_gate
        if component.kind == 13:
            return 5
        if component.kind == 23:
            return word_xor_gate(component.word_size)
        if component.kind == 118:
            return ram_gate
        if component.kind in {54, 56}:
            # preorder copies the backing RAM buffer length into calculated_gate.
            return ram.buffer_size
        raise AssertionError(component.kind)

    def delay_cost(component) -> int:
        if component.kind in zero_cost_kinds:
            return 0
        if component.kind in {3, 7}:
            return 1
        if component.kind == 10:
            return xor_delay
        if component.kind == 13:
            return 4
        if component.kind == 23:
            return word_xor_delay
        if component.kind == 118:
            return ram_delay
        if component.kind == 54:
            # preorder copies the backing RAM delay into load.calculated_delay.
            return ram_delay
        if component.kind == 56:
            # Store calculated_delay remains at the preorder reset value zero.
            return 0
        raise AssertionError(component.kind)

    component_gates = [gate_cost(component) for component in circuit.components]
    component_delays = [delay_cost(component) for component in circuit.components]
    native_gate = sum(component_gates)
    timing_result = timing(circuit, component_delays)
    native_delay = timing_result["native_delay"]

    counts = Counter(component.kind for component in circuit.components)
    expected_counts = {
        2: 1,
        3: 1,
        7: 47,
        13: 1,
        16: 8,
        17: 8,
        23: 76,
        46: 1,
        54: 1,
        56: 1,
        62: 1,
        70: 1,
        97: 2,
        99: 2,
        118: 1,
    }
    if counts != Counter(expected_counts):
        raise RuntimeError(f"candidate component counts changed: {dict(sorted(counts.items()))}")
    if any(
        component.word_size != 1
        for component in circuit.components
        if component.kind == 23
    ):
        raise RuntimeError("not every kind-23 component is a U1 Word XOR")
    gate_ledger = {
        "47 x OR Bit @ 1": counts[7],
        "76 x U1 XOR Word @ 1": sum(
            gate_cost(component) for component in circuit.components if component.kind == 23
        ),
        "1 x Delay Bit @ 5": counts[13] * 5,
        "1 x NOT Bit @ 1": counts[3],
        "RAM backing buffer=8": ram_gate,
        "RAM load calculated_gate=8": ram.buffer_size,
        "RAM store calculated_gate=8": ram.buffer_size,
    }
    if sum(gate_ledger.values()) != native_gate:
        raise RuntimeError("gate ledger does not sum to native total")
    if (native_gate, native_delay) != (153, 10):
        raise RuntimeError(
            f"unexpected native score {(native_gate, native_delay)}, expected (153, 10)"
        )
    if (circuit.gate, circuit.delay) != (native_gate, native_delay):
        raise RuntimeError("serialized header does not match the native score")

    edges = timing_result.pop("edges")
    arch_inputs = [index for index, component in enumerate(circuit.components) if component.kind == 62]
    if len(arch_inputs) != 1:
        raise RuntimeError("expected one Architecture Input")
    arch_input = arch_inputs[0]
    control_edges = [
        edge
        for (source, sink), values in edges.items()
        if sink == arch_input
        for edge in values
        if edge["sink_pin"] == "control"
    ]
    value_edges = [
        edge
        for (source, sink), values in edges.items()
        if source == arch_input
        for edge in values
        if edge["source_pin"] == "value"
    ]
    if not control_edges or not value_edges:
        raise RuntimeError("Architecture Input control/value propagation shell is incomplete")

    result = {
        "schema": 1,
        "candidate_path": str(candidate_path),
        "sha256": sha256(payload).hexdigest(),
        "format_version": 15,
        "declared_header": [circuit.gate, circuit.delay],
        "native_score": [native_gate, native_delay, 66],
        "native_energy": native_gate * native_delay * 66,
        "header_matches_native": [circuit.gate, circuit.delay] == [native_gate, native_delay],
        "component_count": len(circuit.components),
        "wire_count": len(circuit.wires),
        "component_kind_counts": dict(sorted(counts.items())),
        "gate_ledger": gate_ledger,
        "xor_frontier": list(xor_frontier[0]),
        "derived_word_xor_base": [word_xor_base_gate, word_xor_delay],
        "u1_word_xor_cost": [word_xor_gate(1), word_xor_delay],
        "ram": {
            "settings": list(ram.settings),
            "buffer_size": ram.buffer_size,
            "backing_cost": [ram_gate, ram_delay],
            "load_cost": [ram.buffer_size, ram_delay],
            "store_cost": [ram.buffer_size, 0],
            "load_word_size": load.word_size,
            "store_word_size": store.word_size,
        },
        "architecture_input": {
            "component_index": arch_input,
            "cost": [0, 0],
            "control_input_edges": control_edges,
            "value_output_edges": value_edges,
            "native_rule": "max(all input arrivals) + component delay -> every output",
        },
        "all_components_mutable": all(not component.immutable for component in circuit.components),
        "all_component_costs_auto": all(
            (component.cost_gate, component.cost_delay) == (-1, 0)
            for component in circuit.components
        ),
        "v15_byte_identical_round_trip": True,
        **timing_result,
    }
    return result


def main() -> None:
    default_candidate = Path(__file__).resolve().parents[1] / "candidate" / "circuit.data"
    default_levels = Path(os.environ["APPDATA"]) / "Turing Complete" / "levels.txt"
    parser = argparse.ArgumentParser()
    parser.add_argument("candidate", nargs="?", type=Path, default=default_candidate)
    parser.add_argument("--levels", type=Path, default=default_levels)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result = audit(args.candidate, args.levels)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
