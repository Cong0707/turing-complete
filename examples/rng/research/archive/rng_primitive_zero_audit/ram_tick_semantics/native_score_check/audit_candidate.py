"""Recompute the native RNG gate ledger and weighted component critical path."""

from __future__ import annotations

import argparse
from collections import Counter, deque
import csv
from hashlib import sha256
import json
import os
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from tc_save_lab.analysis import wire_points  # noqa: E402
from tc_save_lab.codec import decode_v15, encode_v15  # noqa: E402
from tc_save_lab.pins import I, positioned_pins  # noqa: E402


def progress_frontier(path: Path, level: str) -> list[tuple[int, int, int]]:
    with path.open("r", encoding="utf-8", newline="") as stream:
        rows = list(csv.reader(stream))
    matches = [row for row in rows if len(row) == 4 and row[0] == level]
    if len(matches) != 1:
        raise RuntimeError(f"expected one {level!r} progress row, got {len(matches)}")
    result = []
    for item in matches[0][3].split("|"):
        if item:
            result.append(tuple(int(value) for value in item.split("&")))
    return result


def component_graph(circuit):
    pins_by_position = {}
    for index, component in enumerate(circuit.components):
        for pin in positioned_pins(component, index):
            if pin.position in pins_by_position:
                raise RuntimeError(f"ambiguous pin position {pin.position}")
            pins_by_position[pin.position] = pin

    edges = {}
    for wire_index, wire in enumerate(circuit.wires):
        points = wire_points(wire)
        endpoint_pins = [pins_by_position.get(points[0]), pins_by_position.get(points[-1])]
        if any(pin is None for pin in endpoint_pins):
            raise RuntimeError(f"wire {wire_index} has a non-pin endpoint")
        outputs = [pin for pin in endpoint_pins if pin.direction != I]
        inputs = [pin for pin in endpoint_pins if pin.direction == I]
        if len(outputs) != 1 or len(inputs) != 1:
            raise RuntimeError(
                f"wire {wire_index} is not one output to one input: {endpoint_pins}"
            )
        source, sink = outputs[0], inputs[0]
        key = (source.component_index, sink.component_index)
        edges.setdefault(key, []).append(
            {
                "wire_index": wire_index,
                "source_pin": source.name,
                "sink_pin": sink.name,
            }
        )
    return edges


def weighted_critical_path(circuit, component_delays):
    edges = component_graph(circuit)
    successors = {index: set() for index in range(len(circuit.components))}
    predecessors = {index: set() for index in range(len(circuit.components))}
    for source, sink in edges:
        successors[source].add(sink)
        predecessors[sink].add(source)

    indegree = {index: len(values) for index, values in predecessors.items()}
    ready = deque(index for index, degree in indegree.items() if degree == 0)
    order = []
    while ready:
        source = ready.popleft()
        order.append(source)
        for sink in successors[source]:
            indegree[sink] -= 1
            if indegree[sink] == 0:
                ready.append(sink)
    if len(order) != len(circuit.components):
        cyclic = sorted(index for index, degree in indegree.items() if degree)
        raise RuntimeError(f"component timing graph is cyclic: {cyclic}")

    arrival = {}
    chosen_predecessor = {}
    for index in order:
        if predecessors[index]:
            parent = max(predecessors[index], key=lambda item: arrival[item])
            incoming = arrival[parent]
            chosen_predecessor[index] = parent
        else:
            incoming = 0
        arrival[index] = incoming + component_delays[index]

    terminal_nodes = [index for index in arrival if not successors[index]]
    sink = max(terminal_nodes, key=lambda index: arrival[index])
    path = []
    current = sink
    while True:
        component = circuit.components[current]
        entry = {
            "component_index": current,
            "kind": component.kind,
            "position": list(component.position),
            "component_delay": component_delays[current],
            "arrival": arrival[current],
        }
        parent = chosen_predecessor.get(current)
        if parent is not None:
            entry["incoming_edges"] = edges[(parent, current)]
        path.append(entry)
        if parent is None:
            break
        current = parent
    path.reverse()
    return arrival[sink], path


def audit(candidate_path: Path, levels_path: Path) -> dict[str, object]:
    payload = candidate_path.read_bytes()
    circuit = decode_v15(payload)
    if encode_v15(circuit) != payload:
        raise RuntimeError("candidate is not a byte-identical v15 round trip")

    xor_frontier = progress_frontier(levels_path, "xor_gate")
    if xor_frontier != [(3, 2, 1)]:
        raise RuntimeError(f"unexpected live XOR frontier: {xor_frontier}")
    xor_gate, xor_delay, _ = xor_frontier[0]
    old_rng_frontier = progress_frontier(levels_path, "rng")

    rams = [component for component in circuit.components if component.kind == 118]
    loads = [component for component in circuit.components if component.kind == 54]
    stores = [component for component in circuit.components if component.kind == 56]
    if len(rams) != 1 or len(loads) != 1 or len(stores) != 1:
        raise RuntimeError("candidate must contain one RAM, one load port, and one store port")
    ram = rams[0]
    if ram.settings != (2, 512, 0):
        raise RuntimeError(f"unexpected hidden RAM settings: {ram.settings}")
    if loads[0].word_size != 32 or stores[0].word_size != 32:
        raise RuntimeError("RAM access ports are not U32")

    zero_cost_kinds = {2, 16, 17, 46, 62, 70, 97, 99}
    allowed_kinds = zero_cost_kinds | {3, 7, 10, 13, 23, 54, 56, 118}
    unexpected = sorted({component.kind for component in circuit.components} - allowed_kinds)
    if unexpected:
        raise RuntimeError(f"unreviewed component kinds: {unexpected}")

    word_xor_base_gate = xor_gate * 8
    word_xor_delay = xor_delay

    def gate_cost(component) -> int:
        if component.kind in zero_cost_kinds:
            return 0
        if component.kind == 3:
            return 1
        if component.kind == 7:
            return 1
        if component.kind == 10:
            return xor_gate
        if component.kind == 13:
            return 5
        if component.kind == 23:
            if component.word_size != 1:
                raise RuntimeError("audit only certifies U1 Word XOR")
            return word_xor_base_gate * (component.word_size // 8) + component.word_size % 8
        if component.kind in {54, 56, 118}:
            return ram.buffer_size
        raise AssertionError(component.kind)

    def delay_cost(component) -> int:
        if component.kind in zero_cost_kinds | {54, 56, 118}:
            return 0
        if component.kind in {3, 7}:
            return 1
        if component.kind == 10:
            return xor_delay
        if component.kind == 13:
            return 4
        if component.kind == 23:
            return word_xor_delay
        raise AssertionError(component.kind)

    component_gates = [gate_cost(component) for component in circuit.components]
    component_delays = [delay_cost(component) for component in circuit.components]
    native_gate = sum(component_gates)
    native_delay, critical_path = weighted_critical_path(circuit, component_delays)
    cycles = 66
    old_best_energy = min(gate * delay * tick for gate, delay, tick in old_rng_frontier)
    native_energy = native_gate * native_delay * cycles

    kind_counts = Counter(component.kind for component in circuit.components)
    gate_ledger = {
        "or_bit": kind_counts[7] * 1,
        "xor_bit": kind_counts[10] * xor_gate,
        "xor_word_u1": kind_counts[23] * 1,
        "ready_delay": kind_counts[13] * 5,
        "not_bit": kind_counts[3] * 1,
        "ram": ram.buffer_size,
        "load_port": ram.buffer_size,
        "store_port": ram.buffer_size,
    }
    if sum(gate_ledger.values()) != native_gate:
        raise RuntimeError("gate ledger does not sum to native gate score")

    return {
        "schema": 1,
        "candidate_path": str(candidate_path),
        "sha256": sha256(payload).hexdigest(),
        "format_version": 15,
        "declared_header": [circuit.gate, circuit.delay],
        "native_score": [native_gate, native_delay, cycles],
        "native_energy": native_energy,
        "old_rng_frontier": [list(item) for item in old_rng_frontier],
        "old_best_energy": old_best_energy,
        "improvement": old_best_energy - native_energy,
        "header_matches_native": [circuit.gate, circuit.delay] == [native_gate, native_delay],
        "component_count": len(circuit.components),
        "wire_count": len(circuit.wires),
        "component_kind_counts": dict(sorted(kind_counts.items())),
        "gate_ledger": gate_ledger,
        "xor_frontier": list(xor_frontier[0]),
        "derived_word_xor_base": [word_xor_base_gate, word_xor_delay],
        "ram": {
            "settings": list(ram.settings),
            "buffer_size": ram.buffer_size,
            "scored_delay": 512 // (ram.settings[1] + 1),
            "load_word_size": loads[0].word_size,
            "store_word_size": stores[0].word_size,
        },
        "all_components_mutable": all(not component.immutable for component in circuit.components),
        "all_component_costs_auto": all(
            (component.cost_gate, component.cost_delay) == (-1, 0)
            for component in circuit.components
        ),
        "v15_byte_identical_round_trip": True,
        "critical_path": critical_path,
    }


def main() -> None:
    save_root = Path(os.environ["APPDATA"]) / "Turing Complete"
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "candidate",
        nargs="?",
        type=Path,
        default=save_root / "schematics" / "architecture" / "CODEX-RNG" / "circuit.data",
    )
    parser.add_argument("--levels", type=Path, default=save_root / "levels.txt")
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
