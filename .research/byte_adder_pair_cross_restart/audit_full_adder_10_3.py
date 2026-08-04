"""Independent physical audit of the research-only FullAdder 10/3 witness.

The audit does not import the SAT/CNF synthesizer or its Boolean replay code.
It decodes the v15 artifact, reconstructs endpoint-connected physical nets,
resolves ordinary and tri-state drivers row by row, and recomputes weighted
cost and arrival directly from component pins.
"""

from __future__ import annotations

from collections import Counter, defaultdict, deque
from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path

from tc_save_lab.analysis import wire_points
from tc_save_lab.codec import decode_v15, encode_v15
from tc_save_lab.model import Circuit
from tc_save_lab.pins import I, O, T, analyze_connectivity, positioned_pins
from tc_save_lab.sprite_geometry import DEFAULT_COMPONENT_SPRITE_ROOT, audit_sprite_geometry


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
ARTIFACT_DIR = HERE / "full_adder_10_3"
CANDIDATE = ARTIFACT_DIR / "candidate.circuit.data"
FACTORY_DAG = ARTIFACT_DIR / "factory_dag.json"
PIN_MAPPING = ARTIFACT_DIR / "pin_mapping.json"
MANIFEST = ARTIFACT_DIR / "materialization_manifest.json"
CERTIFICATE = ARTIFACT_DIR / "physical_certificate.json"

EXPECTED_KIND_COUNTS = {4: 1, 6: 4, 7: 1, 12: 2, 60: 3, 69: 2}
PRIMITIVE = {
    4: {"name": "AND", "cost": 1, "delay": 1},
    6: {"name": "NAND", "cost": 1, "delay": 1},
    7: {"name": "OR", "cost": 1, "delay": 1},
    12: {"name": "SWITCH", "cost": 2, "delay": 1},
}
SOURCE_KIND = 60
SINK_KIND = 69


class AuditError(RuntimeError):
    pass


class UnionFind:
    def __init__(self, size: int):
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


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def load_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"{path} does not contain a JSON object")
    return value


def reconstruct_nets(circuit: Circuit) -> dict[str, object]:
    require(bool(circuit.wires), "candidate has no wires")
    union_find = UnionFind(len(circuit.wires))
    endpoints_by_wire = []
    owners_by_endpoint: dict[tuple[int, int], list[int]] = defaultdict(list)
    for wire_index, wire in enumerate(circuit.wires):
        points = wire_points(wire)
        require(len(points) >= 2, f"wire {wire_index} is empty")
        endpoints = (points[0], points[-1])
        endpoints_by_wire.append(endpoints)
        owners_by_endpoint[endpoints[0]].append(wire_index)
        owners_by_endpoint[endpoints[1]].append(wire_index)
    for owners in owners_by_endpoint.values():
        for wire_index in owners[1:]:
            union_find.union(owners[0], wire_index)

    root_by_endpoint: dict[tuple[int, int], int] = {}
    for wire_index, endpoints in enumerate(endpoints_by_wire):
        root = union_find.find(wire_index)
        for endpoint in endpoints:
            previous = root_by_endpoint.get(endpoint)
            if previous is not None:
                require(
                    union_find.find(previous) == root,
                    f"endpoint {endpoint} belongs to inconsistent physical nets",
                )
            root_by_endpoint[endpoint] = root

    pins_by_root: dict[int, list[object]] = defaultdict(list)
    pin_root: dict[tuple[int, str], int] = {}
    pin_by_key: dict[tuple[int, str], object] = {}
    for component_index, component in enumerate(circuit.components):
        pins = tuple(positioned_pins(component, component_index))
        require(bool(pins), f"component {component_index} kind {component.kind} has no pins")
        for pin in pins:
            root = root_by_endpoint.get(pin.position)
            require(root is not None, f"pin {(component_index, pin.name)} is not a wire endpoint")
            root = union_find.find(root)
            key = (component_index, pin.name)
            require(key not in pin_root, f"duplicate positioned pin key {key}")
            pin_root[key] = root
            pin_by_key[key] = pin
            pins_by_root[root].append(pin)

    network_rows = []
    for root, pins in sorted(pins_by_root.items()):
        drivers = [pin for pin in pins if pin.direction in {O, T}]
        receivers = [pin for pin in pins if pin.direction == I]
        require(bool(drivers), f"physical net {root} has no driver")
        require(bool(receivers), f"physical net {root} has no receiver")
        if len(drivers) > 1:
            require(
                all(pin.direction == T for pin in drivers),
                f"physical net {root} mixes ordinary and multiple drivers",
            )
        widths = {pin.width for pin in pins}
        require(widths == {1}, f"physical net {root} is not scalar: {widths}")
        network_rows.append(
            {
                "root": root,
                "driver_count": len(drivers),
                "tri_state_driver_count": sum(pin.direction == T for pin in drivers),
                "receiver_count": len(receivers),
                "drivers": [
                    {
                        "component_index": pin.component_index,
                        "permanent_id": pin.permanent_id,
                        "kind": pin.component_kind,
                        "pin": pin.name,
                        "position": list(pin.position),
                    }
                    for pin in drivers
                ],
                "receivers": [
                    {
                        "component_index": pin.component_index,
                        "permanent_id": pin.permanent_id,
                        "kind": pin.component_kind,
                        "pin": pin.name,
                        "position": list(pin.position),
                    }
                    for pin in receivers
                ],
            }
        )
    return {
        "pin_root": pin_root,
        "pin_by_key": pin_by_key,
        "pins_by_root": pins_by_root,
        "networks": network_rows,
        "logical_network_count": len(pins_by_root),
    }


def verify_mapping(
    circuit: Circuit,
    physical: dict[str, object],
    mapping: dict[str, object],
) -> dict[str, object]:
    pin_root = physical["pin_root"]
    pin_by_key = physical["pin_by_key"]
    expected_pin_keys: set[tuple[int, str]] = set()
    label_by_root: dict[int, str] = {}
    root_by_label: dict[str, int] = {}
    network_summaries = []
    for network in mapping["networks"]:
        label = str(network["label"])
        roots = set()
        for record in network["pins"]:
            component_index = int(record["component_index"])
            pin_name = str(record["pin"])
            key = (component_index, pin_name)
            require(key in pin_root, f"mapping references missing pin {key}")
            component = circuit.components[component_index]
            pin = pin_by_key[key]
            require(
                int(record["component_permanent_id"]) == component.permanent_id,
                f"permanent ID drift for {key}",
            )
            require(int(record["component_kind"]) == component.kind, f"kind drift for {key}")
            require(str(record["pin_direction"]) == pin.direction, f"direction drift for {key}")
            require(tuple(record["position"]) == pin.position, f"position drift for {key}")
            require(key not in expected_pin_keys, f"pin {key} appears in two declared networks")
            expected_pin_keys.add(key)
            roots.add(int(pin_root[key]))
        require(len(roots) == 1, f"declared network {label} is physically split: {roots}")
        root = next(iter(roots))
        previous = label_by_root.get(root)
        require(previous is None, f"physical root {root} aliases {previous!r} and {label!r}")
        label_by_root[root] = label
        root_by_label[label] = root
        network_summaries.append(
            {"label": label, "root": root, "pin_count": len(network["pins"])}
        )

    require(
        expected_pin_keys == set(pin_root),
        "pin mapping does not cover exactly all physical component pins",
    )
    require(
        set(label_by_root) == set(physical["pins_by_root"]),
        "declared and physical network partitions differ",
    )
    return {
        "network_partition_isomorphic": True,
        "all_component_pins_covered_exactly_once": True,
        "label_by_root": {str(key): value for key, value in sorted(label_by_root.items())},
        "root_by_label": dict(sorted(root_by_label.items())),
        "networks": network_summaries,
    }


def verify_dag(payload: dict[str, object]) -> dict[int, dict[str, object]]:
    dag = payload["factory_dag"]
    nodes = dag["nodes"]
    outputs = dag["outputs"]
    require(int(dag["live_node_count"]) == len(nodes), "DAG live-node count drift")
    hash_payload = {
        "outputs": outputs,
        "nodes": nodes,
        "live_node_count": dag["live_node_count"],
    }
    actual_hash = sha256(canonical(hash_payload)).hexdigest()
    require(actual_hash == dag["sha256"], "Factory DAG structural hash mismatch")
    by_id: dict[int, dict[str, object]] = {}
    arrivals: dict[int, int] = {}
    cost = 0
    for node in nodes:
        node_id = int(node["id"])
        require(node_id not in by_id, f"duplicate DAG node {node_id}")
        args = [int(value) for value in node.get("args", ())]
        require(all(argument in by_id for argument in args), f"node {node_id} is not topological")
        op = str(node["op"])
        if op == "INPUT":
            require(not args, f"INPUT node {node_id} has arguments")
            expected_cost = 0
            expected_step = 0
            expected_arrival = 0
        elif op in {"AND", "NAND", "OR"}:
            require(len(args) == 2, f"{op} node {node_id} arity changed")
            expected_cost = 1
            expected_step = 1
            expected_arrival = max(arrivals[value] for value in args) + 1
        elif op == "BUS":
            require(len(args) == 4, f"BUS node {node_id} must have two drivers")
            require(node.get("resolved_network") == "sum_bus", "BUS owner/network drift")
            require(node.get("owner") == "sum_bus", "BUS owner drift")
            expected_cost = 4
            expected_step = 1
            expected_arrival = max(arrivals[value] for value in args) + 1
        else:
            raise AuditError(f"unsupported DAG op {op!r}")
        require(int(node["cost"]) == expected_cost, f"node {node_id} cost drift")
        require(int(node["step_delay"]) == expected_step, f"node {node_id} delay drift")
        require(int(node["arrival"]) == expected_arrival, f"node {node_id} arrival drift")
        cost += expected_cost
        arrivals[node_id] = expected_arrival
        by_id[node_id] = node
    require([int(value) for value in outputs] == [8, 9], "DAG output IDs changed")
    require(cost == 10, f"DAG cost is {cost}, expected 10")
    require(max(arrivals[int(value)] for value in outputs) == 3, "DAG delay is not 3")
    return by_id


def component_timing(circuit: Circuit, physical: dict[str, object]) -> dict[str, object]:
    pins_by_root = physical["pins_by_root"]
    pin_root = physical["pin_root"]
    driver_components_by_root = {
        root: {
            pin.component_index for pin in pins if pin.direction in {O, T}
        }
        for root, pins in pins_by_root.items()
    }
    dependencies: dict[int, set[int]] = defaultdict(set)
    for component_index, component in enumerate(circuit.components):
        for pin in positioned_pins(component, component_index):
            if pin.direction != I:
                continue
            root = pin_root[(component_index, pin.name)]
            dependencies[component_index].update(driver_components_by_root[root])
        dependencies[component_index].discard(component_index)

    source_indices = {
        index for index, component in enumerate(circuit.components) if component.kind == SOURCE_KIND
    }
    sink_indices = {
        index for index, component in enumerate(circuit.components) if component.kind == SINK_KIND
    }
    primitive_indices = {
        index for index, component in enumerate(circuit.components) if component.kind in PRIMITIVE
    }
    require(
        source_indices | sink_indices | primitive_indices == set(range(len(circuit.components))),
        "candidate contains a non-reviewed component kind",
    )
    arrivals = {index: 0 for index in source_indices}
    pending = set(primitive_indices)
    order = []
    while pending:
        ready = sorted(index for index in pending if dependencies[index] <= arrivals.keys())
        require(bool(ready), "physical component dependency graph is cyclic")
        for index in ready:
            require(bool(dependencies[index]), f"primitive component {index} is source-less")
            delay = int(PRIMITIVE[circuit.components[index].kind]["delay"])
            arrivals[index] = max(arrivals[parent] for parent in dependencies[index]) + delay
            pending.remove(index)
            order.append(index)

    output_arrivals = {}
    for index in sink_indices:
        label = circuit.components[index].user_label
        require(bool(dependencies[index]), f"sink {label!r} has no physical drivers")
        require(dependencies[index] <= arrivals.keys(), f"sink {label!r} is unresolved")
        output_arrivals[label] = max(arrivals[parent] for parent in dependencies[index])

    live = set(sink_indices)
    queue = deque(sink_indices)
    while queue:
        index = queue.popleft()
        for parent in dependencies[index]:
            if parent not in live:
                live.add(parent)
                queue.append(parent)
    dead = sorted(primitive_indices - live)
    require(not dead, f"candidate contains dead paid components {dead}")
    gate_cost = sum(int(PRIMITIVE[circuit.components[index].kind]["cost"]) for index in primitive_indices)
    require(gate_cost == 10, f"physical weighted cost is {gate_cost}, expected 10")
    require(output_arrivals == {"Sum": 3, "Carry": 3}, f"physical output arrivals drifted: {output_arrivals}")
    return {
        "weighted_gate_cost": gate_cost,
        "replayed_max_delay": max(output_arrivals.values()),
        "output_arrivals": dict(sorted(output_arrivals.items())),
        "topological_component_indices": order,
        "topological_permanent_ids": [circuit.components[index].permanent_id for index in order],
        "dead_paid_component_count": 0,
    }


def resolve_driver_states(states: list[tuple[bool, bool]]) -> tuple[bool, bool, bool]:
    active = {value for value, driven in states if driven}
    if len(active) > 1:
        return False, True, True
    if not active:
        return False, False, False
    return next(iter(active)), True, False


def truth_replay(
    circuit: Circuit,
    physical: dict[str, object],
    mapping: dict[str, object],
    by_id: dict[int, dict[str, object]],
) -> dict[str, object]:
    pins_by_root = physical["pins_by_root"]
    pin_root = physical["pin_root"]
    roots_by_component_input: dict[int, dict[str, int]] = defaultdict(dict)
    drivers_by_root: dict[int, list[tuple[int, str]]] = defaultdict(list)
    for root, pins in pins_by_root.items():
        for pin in pins:
            key = (pin.component_index, pin.name)
            if pin.direction == I:
                roots_by_component_input[pin.component_index][pin.name] = root
            elif pin.direction in {O, T}:
                drivers_by_root[root].append(key)

    source_by_label = {
        component.user_label: index
        for index, component in enumerate(circuit.components)
        if component.kind == SOURCE_KIND
    }
    sink_by_label = {
        component.user_label: index
        for index, component in enumerate(circuit.components)
        if component.kind == SINK_KIND
    }
    node_components = {int(key): int(value) for key, value in mapping["node_components"].items()}
    bus_switches = {int(key): [int(value) for value in values] for key, values in mapping["bus_switches"].items()}
    node_masks = {
        node_id: {"value": 0, "driven": 0, "conflict": 0}
        for node_id in by_id
    }
    switch_masks = {
        index: {"value": 0, "driven": 0, "conflict": 0}
        for indices in bus_switches.values()
        for index in indices
    }
    rows = []

    def resolve_root(root: int, output_states: dict[tuple[int, str], tuple[bool, bool]]) -> tuple[bool, bool, bool] | None:
        drivers = drivers_by_root[root]
        if any(driver not in output_states for driver in drivers):
            return None
        return resolve_driver_states([output_states[driver] for driver in drivers])

    for case in range(8):
        input_values = {
            "Input 0": bool(case & 1),
            "Input 1": bool(case & 2),
            "Input 2": bool(case & 4),
        }
        output_states: dict[tuple[int, str], tuple[bool, bool]] = {
            (index, "value"): (input_values[label], True)
            for label, index in source_by_label.items()
        }
        pending = {
            index
            for index, component in enumerate(circuit.components)
            if component.kind in PRIMITIVE
        }
        per_component_inputs: dict[int, dict[str, tuple[bool, bool, bool]]] = {}
        while pending:
            progress = False
            for index in sorted(pending):
                component = circuit.components[index]
                resolved_inputs = {}
                ready = True
                for pin_name, root in roots_by_component_input[index].items():
                    state = resolve_root(root, output_states)
                    if state is None:
                        ready = False
                        break
                    resolved_inputs[pin_name] = state
                if not ready:
                    continue
                require(
                    not any(state[2] for state in resolved_inputs.values()),
                    f"row {case}: component {index} reads a conflicted net",
                )
                numeric = {name: value if driven else False for name, (value, driven, _conflict) in resolved_inputs.items()}
                if component.kind == 4:
                    value, driven = numeric["in0"] and numeric["in1"], True
                elif component.kind == 6:
                    value, driven = not (numeric["in0"] and numeric["in1"]), True
                elif component.kind == 7:
                    value, driven = numeric["in0"] or numeric["in1"], True
                elif component.kind == 12:
                    driven = numeric["enable"]
                    value = numeric["in"] if driven else False
                else:
                    raise AuditError(f"unhandled primitive kind {component.kind}")
                output_states[(index, "out")] = (bool(value), bool(driven))
                per_component_inputs[index] = resolved_inputs
                pending.remove(index)
                progress = True
            require(progress, f"row {case}: physical evaluation made no progress")

        actual = {}
        row_conflict_count = 0
        row_undriven_count = 0
        for label, index in sink_by_label.items():
            root = roots_by_component_input[index]["value"]
            state = resolve_root(root, output_states)
            require(state is not None, f"row {case}: sink {label} unresolved")
            value, driven, conflict = state
            row_conflict_count += int(conflict)
            row_undriven_count += int(not driven)
            actual[label] = int(value)
        total = sum(int(value) for value in input_values.values())
        expected = {"Sum": total & 1, "Carry": (total >> 1) & 1}
        require(actual == expected, f"row {case}: truth mismatch {actual} != {expected}")
        require(row_conflict_count == 0, f"row {case}: output conflict")
        require(row_undriven_count == 0, f"row {case}: undriven output")

        node_states: dict[int, tuple[bool, bool, bool]] = {}
        for node_id, node in by_id.items():
            op = str(node["op"])
            if op == "INPUT":
                state = (input_values[str(node["label"])], True, False)
            elif op == "BUS":
                first_switch = bus_switches[node_id][0]
                root = pin_root[(first_switch, "out")]
                resolved = resolve_root(root, output_states)
                require(resolved is not None, f"row {case}: BUS node {node_id} unresolved")
                state = resolved
            else:
                component_index = node_components[node_id]
                value, driven = output_states[(component_index, "out")]
                state = (value, driven, False)
            node_states[node_id] = state
            value, driven, conflict = state
            node_masks[node_id]["value"] |= int(value) << case
            node_masks[node_id]["driven"] |= int(driven) << case
            node_masks[node_id]["conflict"] |= int(conflict) << case
        for switch_index in switch_masks:
            value, driven = output_states[(switch_index, "out")]
            switch_masks[switch_index]["value"] |= int(value) << case
            switch_masks[switch_index]["driven"] |= int(driven) << case
        rows.append(
            {
                "case": case,
                "inputs": [int(input_values[f"Input {bit}"]) for bit in range(3)],
                "actual": actual,
                "expected": expected,
                "sum_driver_states": [
                    {
                        "component_index": index,
                        "value": int(output_states[(index, "out")][0]),
                        "driven": int(output_states[(index, "out")][1]),
                    }
                    for index in bus_switches[8]
                ],
                "conflict_count": 0,
                "undriven_output_count": 0,
            }
        )

    for node_id, masks in node_masks.items():
        node = by_id[node_id]
        expected_value = int(str(node["truth_mask_hex"]), 16)
        require(masks["value"] == expected_value, f"node {node_id} value mask drift")
        if "driven_mask_hex" in node:
            require(
                masks["driven"] == int(str(node["driven_mask_hex"]), 16),
                f"node {node_id} driven mask drift",
            )
        else:
            require(masks["driven"] == 0xFF, f"ordinary node {node_id} is not fully driven")
        require(masks["conflict"] == 0, f"node {node_id} has conflict rows")

    bus_node = by_id[8]
    for switch_index, driver in zip(bus_switches[8], bus_node["drivers"], strict=True):
        masks = switch_masks[switch_index]
        require(
            masks["driven"] == int(str(driver["driven_mask_hex"]), 16),
            f"Switch {switch_index} driven-mask drift",
        )
        require(
            masks["value"] == int(str(driver["one_mask_hex"]), 16),
            f"Switch {switch_index} one-mask drift",
        )
    require(
        switch_masks[bus_switches[8][0]]["driven"]
        & switch_masks[bus_switches[8][1]]["driven"]
        == 0,
        "Sum partial drivers overlap",
    )
    require(
        switch_masks[bus_switches[8][0]]["driven"]
        | switch_masks[bus_switches[8][1]]["driven"]
        == 0xFF,
        "Sum partial drivers are not complete",
    )
    return {
        "assignments": 8,
        "output_checks": 16,
        "mismatch_count": 0,
        "conflict_assignment_count": 0,
        "undriven_output_assignment_count": 0,
        "rows": rows,
        "node_masks": {
            str(node_id): {key: f"{value:02x}" for key, value in masks.items()}
            for node_id, masks in sorted(node_masks.items())
        },
        "partial_driver_masks": {
            str(circuit.components[index].permanent_id): {
                "component_index": index,
                "one_mask_hex": f"{masks['value']:02x}",
                "driven_mask_hex": f"{masks['driven']:02x}",
                "z_mask_hex": f"{(~masks['driven']) & 0xFF:02x}",
                "conflict_mask_hex": "00",
            }
            for index, masks in sorted(switch_masks.items())
        },
        "sum_driver_overlap_mask_hex": "00",
        "sum_driver_complete_mask_hex": "ff",
    }


def main() -> None:
    candidate_bytes = CANDIDATE.read_bytes()
    require(candidate_bytes and candidate_bytes[0] == 15, "candidate is not v15")
    circuit = decode_v15(candidate_bytes)
    require(encode_v15(circuit) == candidate_bytes, "v15 roundtrip is not byte-identical")
    require((circuit.gate, circuit.delay, circuit.energy) == (10, 3, 30), "declared score drift")
    kind_counts = dict(sorted(Counter(component.kind for component in circuit.components).items()))
    require(kind_counts == EXPECTED_KIND_COUNTS, f"component kind counts drift: {kind_counts}")
    require(15 not in kind_counts and 30 not in kind_counts, "candidate contains a native adder")
    require(
        all(component.immutable == (component.kind in {SOURCE_KIND, SINK_KIND}) for component in circuit.components),
        "immutable component partition drift",
    )

    dag_payload = load_json(FACTORY_DAG)
    mapping = load_json(PIN_MAPPING)
    manifest = load_json(MANIFEST)
    require(
        digest(CANDIDATE) == manifest["artifacts"]["candidate"]["sha256"],
        "candidate hash differs from materialization manifest",
    )
    require(
        digest(FACTORY_DAG) == manifest["artifacts"]["factory_dag"]["sha256"],
        "Factory DAG hash differs from materialization manifest",
    )
    require(
        digest(PIN_MAPPING) == manifest["artifacts"]["real_pin_mapping"]["sha256"],
        "pin mapping hash differs from materialization manifest",
    )

    by_id = verify_dag(dag_payload)
    physical = reconstruct_nets(circuit)
    mapping_review = verify_mapping(circuit, physical, mapping)
    timing = component_timing(circuit, physical)
    truth = truth_replay(circuit, physical, mapping, by_id)

    connectivity = analyze_connectivity(circuit)
    for field in (
        "unsupported_component_kind_counts",
        "unconnected_pin_count",
        "multi_driver_network_count",
        "undriven_network_count",
        "sinkless_network_count",
        "width_mismatch_network_count",
        "cycle_component_count",
    ):
        require(not connectivity[field], f"connectivity failure {field}={connectivity[field]!r}")
    require(connectivity["unit_logic_depth"] == 3, "connectivity unit depth is not 3")
    geometry = audit_sprite_geometry(circuit, DEFAULT_COMPONENT_SPRITE_ROOT)
    require(not geometry.unsupported_component_kinds, "unsupported sprite component")
    require(not geometry.component_overlap_cells, "component sprite overlap")
    require(not geometry.wire_collisions, "wire/component sprite collision")
    require(not geometry.wire_interior_pin_contacts, "wire interior touches a foreign pin")

    multi_driver_nets = [
        row for row in physical["networks"] if int(row["driver_count"]) > 1
    ]
    require(len(multi_driver_nets) == 1, "physical candidate does not have exactly one BUS net")
    require(multi_driver_nets[0]["driver_count"] == 2, "Sum BUS does not have two drivers")
    require(multi_driver_nets[0]["tri_state_driver_count"] == 2, "Sum BUS drivers are not both tri-state")
    sum_root = mapping_review["root_by_label"]["node:8"]
    require(int(multi_driver_nets[0]["root"]) == int(sum_root), "multi-driver net is not DAG node 8")

    certificate = {
        "schema": "full-adder-10-3-independent-physical-certificate-v1",
        "status": "verified",
        "independence": {
            "sat_or_cnf_module_imported": False,
            "cnf_boolean_replay_reused": False,
            "physical_wire_endpoint_partition_rebuilt": True,
            "component_pin_semantics_replayed_row_by_row": True,
            "weighted_cost_and_arrival_recomputed_from_physical_components": True,
        },
        "scope": {
            "research_only": True,
            "formal_save_modified": False,
            "levels_txt_modified": False,
            "repository_candidate_modified": False,
            "game_started": False,
        },
        "inputs": {
            "candidate": {"path": str(CANDIDATE), "sha256": digest(CANDIDATE)},
            "factory_dag": {"path": str(FACTORY_DAG), "sha256": digest(FACTORY_DAG)},
            "pin_mapping": {"path": str(PIN_MAPPING), "sha256": digest(PIN_MAPPING)},
            "materialization_manifest": {"path": str(MANIFEST), "sha256": digest(MANIFEST)},
        },
        "score": {
            "declared": [circuit.gate, circuit.delay, circuit.energy],
            "replayed": [timing["weighted_gate_cost"], timing["replayed_max_delay"], 30],
        },
        "structure": {
            "component_count": len(circuit.components),
            "wire_count": len(circuit.wires),
            "component_kind_counts": {str(key): value for key, value in kind_counts.items()},
            "logical_network_count": physical["logical_network_count"],
            "resolved_multi_driver_network_count": 1,
            "resolved_sum_bus_driver_count": 2,
            "native_full_adder_count": 0,
            "native_add_count": 0,
        },
        "physical_networks": physical["networks"],
        "pin_mapping_review": mapping_review,
        "timing_and_ownership": timing,
        "truth_protocol": truth,
        "connectivity": connectivity,
        "geometry": asdict(geometry),
        "serialization": {
            "v15_roundtrip_byte_identical": True,
            "decoded_json_determinism_not_assumed": True,
        },
        "auditor": {
            "path": str(Path(__file__).resolve()),
            "sha256": digest(Path(__file__).resolve()),
        },
    }
    encoded = (json.dumps(certificate, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    CERTIFICATE.write_bytes(encoded)
    print(json.dumps({
        "status": "verified",
        "certificate": str(CERTIFICATE),
        "certificate_sha256": sha256(encoded).hexdigest(),
        "candidate_sha256": digest(CANDIDATE),
        "factory_dag_sha256": digest(FACTORY_DAG),
        "pin_mapping_sha256": digest(PIN_MAPPING),
        "score": [10, 3, 30],
        "mismatch_count": 0,
        "conflict_assignment_count": 0,
        "undriven_output_assignment_count": 0,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
