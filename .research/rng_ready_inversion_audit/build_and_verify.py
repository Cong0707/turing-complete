"""Independently audit the zero-init 402/9/67 RNG controller.

The script only builds the repository candidate in memory and writes research
artifacts below ``.research``.  It never reads or writes the live save and does
not start the game.
"""

from __future__ import annotations

from collections import Counter, deque
from hashlib import sha256
import json
from pathlib import Path

from tc_save_lab.analysis import wire_points
from tc_save_lab.builder import stable_permanent_id
from tc_save_lab.codec import decode_v15, encode_v15
from tc_save_lab.model import Circuit
from tc_save_lab.pins import I, analyze_connectivity, positioned_pins
from tc_save_lab.rng_encoded_asic import (
    T,
    _encoded_memory,
    _layout_safety,
    apply_matrix,
    build_rng_encoded_asic,
    xorshift32,
)
from tc_save_lab.simulate import (
    _compile,
    _simulate_clocked_tick,
    initial_clocked_memory,
)
from tc_save_lab.sprite_geometry import (
    DEFAULT_COMPONENT_SPRITE_ROOT,
    audit_sprite_geometry,
)


GATE = 402
DELAY = 9
CYCLES = 67
ENERGY = GATE * DELAY * CYCLES
KEY = "architecture/codex-rng-encoded"


def _native_score(circuit: Circuit) -> dict[str, object]:
    gate_costs = {3: 1, 7: 1, 10: 3, 13: 5, 23: 3}
    delay_costs = {3: 1, 7: 1, 10: 2, 13: 4, 23: 2}
    gate = sum(gate_costs.get(component.kind, 0) for component in circuit.components)
    if gate != GATE:
        raise RuntimeError(f"native gate total changed: {gate} != {GATE}")

    pins = {
        pin.position: pin
        for index, component in enumerate(circuit.components)
        for pin in positioned_pins(component, index)
    }
    edges: set[tuple[int, int]] = set()
    for wire in circuit.wires:
        endpoints = (pins[wire_points(wire)[0]], pins[wire_points(wire)[-1]])
        source = next(pin for pin in endpoints if pin.direction != I)
        sink = next(pin for pin in endpoints if pin.direction == I)
        edges.add((source.component_index, sink.component_index))

    successors = {index: set() for index in range(len(circuit.components))}
    predecessors = {index: set() for index in range(len(circuit.components))}
    delay_inputs = {
        index: set()
        for index, component in enumerate(circuit.components)
        if component.kind == 13
    }
    for source, sink in edges:
        # Delay outputs are new-tick sources.  Their input arrivals remain
        # timing terminals but cannot propagate through in the same tick.
        if circuit.components[sink].kind == 13:
            delay_inputs[sink].add(source)
        else:
            successors[source].add(sink)
            predecessors[sink].add(source)

    indegree = {index: len(values) for index, values in predecessors.items()}
    ready = deque(index for index, value in indegree.items() if value == 0)
    order: list[int] = []
    while ready:
        source = ready.popleft()
        order.append(source)
        for sink in successors[source]:
            indegree[sink] -= 1
            if indegree[sink] == 0:
                ready.append(sink)
    if len(order) != len(circuit.components):
        raise RuntimeError("timing graph remains cyclic after Delay boundaries")

    arrival: dict[int, int] = {}
    parent: dict[int, int] = {}
    for index in order:
        if predecessors[index]:
            predecessor = max(predecessors[index], key=arrival.__getitem__)
            parent[index] = predecessor
            incoming = arrival[predecessor]
        else:
            incoming = 0
        arrival[index] = incoming + delay_costs.get(circuit.components[index].kind, 0)

    terminals = [
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
        raise RuntimeError(f"native timing total changed: {delay} != {DELAY}")

    if terminal_type == "delay-input" and delay_inputs[terminal]:
        current = max(delay_inputs[terminal], key=arrival.__getitem__)
    else:
        current = terminal
    critical_path = []
    while True:
        component = circuit.components[current]
        critical_path.append(
            {
                "component_index": current,
                "kind": component.kind,
                "position": list(component.position),
                "component_delay": delay_costs.get(component.kind, 0),
                "arrival": arrival[current],
            }
        )
        if current not in parent:
            break
        current = parent[current]
    critical_path.reverse()
    return {
        "gate": gate,
        "delay": delay,
        "critical_terminal_type": terminal_type,
        "critical_path": critical_path,
    }


def _verify_structure(circuit: Circuit) -> dict[str, object]:
    if (circuit.gate, circuit.delay) != (GATE, DELAY):
        raise RuntimeError("serialized score header changed")
    counts = Counter(component.kind for component in circuit.components)
    expected = {
        2: 0,
        3: 1,
        7: 48,
        10: 42,
        13: 34,
        23: 19,
        62: 1,
        70: 1,
    }
    for kind, count in expected.items():
        if counts[kind] != count:
            raise RuntimeError(f"kind {kind} count changed: {counts[kind]} != {count}")
    if Counter(
        component.init_data for component in circuit.components if component.kind == 13
    ) != {0: 34}:
        raise RuntimeError("every Delay Bit must start at zero")

    connectivity = analyze_connectivity(circuit)
    for field in (
        "unsupported_component_kind_counts",
        "unconnected_pin_count",
        "multi_driver_network_count",
        "undriven_network_count",
        "width_mismatch_network_count",
        "cycle_component_count",
    ):
        if connectivity[field]:
            raise RuntimeError(f"connectivity failure {field}: {connectivity[field]}")

    layout = _layout_safety(circuit)
    if any(layout.values()):
        raise RuntimeError(f"conservative layout failure: {layout}")
    sprite = audit_sprite_geometry(circuit, DEFAULT_COMPONENT_SPRITE_ROOT)
    internal_collisions = tuple(
        collision
        for collision in sprite.wire_collisions
        if collision.component_kind not in {62, 70}
    )
    if (
        sprite.unsupported_component_kinds
        or sprite.component_overlap_cells
        or internal_collisions
        or sprite.wire_interior_pin_contacts
    ):
        raise RuntimeError("live-sprite layout failure")

    return {
        "native_score": _native_score(circuit),
        "component_kind_counts": dict(sorted(counts.items())),
        "connectivity": connectivity,
        "layout": layout,
        "live_sprite_layout": {
            "unsupported_component_kinds": list(sprite.unsupported_component_kinds),
            "component_overlap_cell_count": len(sprite.component_overlap_cells),
            "internal_wire_collision_count": len(internal_collisions),
            "wire_interior_pin_contact_count": len(sprite.wire_interior_pin_contacts),
        },
    }


def _verify_all_seeds(circuit: Circuit) -> dict[str, object]:
    compiled = _compile(circuit)
    load_pulse = next(
        component
        for component in circuit.components
        if component.permanent_id == stable_permanent_id(KEY, "load-pulse-delay")
    )
    output_active = next(
        component
        for component in circuit.components
        if component.permanent_id == stable_permanent_id(KEY, "output-active-delay")
    )
    expected_controls = (
        (0, 0, 0, 0),
        (1, 0, 1, 0),
        *((0, 1, 0, 1) for _ in range(65)),
    )
    output_count = 0

    for seed in range(256):
        memory = initial_clocked_memory(circuit)
        expected_value = seed
        for tick in range(CYCLES):
            load_value = memory[load_pulse.permanent_id]
            output_value = memory[output_active.permanent_id]
            actual_controls = (load_value, output_value, load_value, output_value)
            if actual_controls != expected_controls[tick]:
                raise RuntimeError(
                    f"control mismatch seed={seed:08x} tick={tick}: "
                    f"{actual_controls} != {expected_controls[tick]}"
                )

            result = _simulate_clocked_tick(
                circuit,
                compiled=compiled,
                inputs={"Seed": seed},
                memory=memory,
            )
            if tick < 2:
                if result.outputs:
                    raise RuntimeError(
                        f"premature output seed={seed:08x} tick={tick}: {result.outputs}"
                    )
                if tick == 0 and _encoded_memory(circuit, result.memory) != 0:
                    raise RuntimeError(f"idle tick changed state for {seed:08x}")
                if tick == 1 and _encoded_memory(circuit, result.memory) != apply_matrix(T, seed):
                    raise RuntimeError(f"seed load failed for {seed:08x}")
            else:
                expected_value = xorshift32(expected_value)
                expected_output = {"RNG output": expected_value}
                if result.outputs != expected_output:
                    raise RuntimeError(
                        f"output mismatch seed={seed:08x} tick={tick}: "
                        f"{result.outputs} != {expected_output}"
                    )
                if _encoded_memory(circuit, result.memory) != apply_matrix(T, expected_value):
                    raise RuntimeError(
                        f"state mismatch seed={seed:08x} tick={tick}"
                    )
                output_count += 1
            memory = result.memory

    return {
        "seed_count": 256,
        "tick_count": 256 * CYCLES,
        "output_count": output_count,
        "control_trace": [list(values) for values in expected_controls[:3]],
    }


def write_research_audit(project_root: Path) -> dict[str, object]:
    circuit = build_rng_encoded_asic()
    structure = _verify_structure(circuit)
    stream = _verify_all_seeds(circuit)
    payload = encode_v15(circuit)
    if decode_v15(payload) != circuit:
        raise RuntimeError("v15 round trip failed")

    output_dir = project_root / ".research" / "rng_ready_inversion_audit"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "candidate.data").write_bytes(payload)
    result = {
        "schema": 1,
        "status": "offline verified; game verification pending",
        "sha256": sha256(payload).hexdigest(),
        "leaderboard_tuple": [GATE, DELAY, CYCLES],
        "energy": ENERGY,
        "reference_energy": 256_014,
        "improvement": 256_014 - ENERGY,
        "component_count": len(circuit.components),
        "wire_count": len(circuit.wires),
        "all_delay_init_data": 0,
        "timing": {
            "seed": "load-pulse Delay 4 + OR 1 + XOR 2 + XOR 2 = 9",
            "feedback": "state Delay 4 + OR 1 + XOR 2 + XOR 2 = 9",
            "controller_to_load": "max(two Delay outputs at 4) + OR 1 + NOT 1 = 6",
            "controller_to_output": "max(two Delay outputs at 4) + OR 1 = 5",
        },
        "structure": structure,
        "stream": stream,
    }
    (output_dir / "result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return result


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2]
    print(json.dumps(write_research_audit(root), ensure_ascii=False, indent=2))
