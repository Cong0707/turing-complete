"""Materialize and exhaustively audit the hypothetical kind-15 bit0 splice.

The authoritative 80/7 Factory DAG implements ``S0`` and ``C1`` with a
10-gate asymmetric cone: S0 arrives at 4, while C1 arrives at 2.  Replacing
that cone by one accepted-price ``com_full_adder`` (7/4) saves three gates but
makes both outputs arrive at 4.  Exact recursive replay therefore yields a
77/9 candidate, not 77/7.

This program has no deployment mode.  It writes only below the isolated
research intake directory and never modifies ``levels.txt``, either formal
save, or either repository candidate.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import asdict, replace
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import re
import sys
from typing import Any, Iterable

from tc_save_lab.analysis import wire_points
from tc_save_lab.codec import decode_v15, encode_v15
from tc_save_lab.foundry import _assert_game_not_running
from tc_save_lab.model import Circuit, Component, Point
from tc_save_lab.pins import (
    I,
    O,
    T,
    PIN_SCHEMAS,
    analyze_connectivity,
    positioned_pins,
    rotate_offset,
)
from tc_save_lab.sprite_geometry import (
    DEFAULT_COMPONENT_SPRITE_ROOT,
    SPRITE_NAME_BY_COMPONENT_KIND,
    audit_sprite_geometry,
    sprite_alpha_cells,
)
from tc_save_lab.builder import stable_permanent_id


SCHEMA = "byte-adder-kind15-bit0-physical-candidate-v1"
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
MATERIALIZER_PATH = (
    ROOT / ".research/byte_adder_builder_layout_agent/materialize_factory_dag.py"
)
AUTHORITATIVE_DAG = ROOT / ".research/byte_adder_root/byte-adder-hybrid-phasefold-g80-d7.json"
AUTHORITATIVE_DAG_SHA256 = "71625de2b86ea03127415802dbc68f605ac16d69da6d9e8b3ade35db317ec884"
FULL_ADDER_AUDIT = (
    HERE / "full_adder_7_4_intake/formal_9f83306a_r1/audit.json"
)
FULL_ADDER_FORMAL = (
    Path.home()
    / "AppData/Roaming/Turing Complete/schematics/full_adder/Default/circuit.data"
)
LEVELS_PATH = Path.home() / "AppData/Roaming/Turing Complete/levels.txt"
INTAKE_ROOT = HERE / "kind15_bit0_intake"
KIND15_GEOMETRY_BASELINE = ROOT / "examples/byte_adder/baseline/circuit.data"
KIND15_GEOMETRY_BASELINE_SHA256 = "f8219a2c1dff42f8811bd105e4581b02d4164a765b550b0a8234f94418bd0570"
KIND15_SPRITE_SHA256 = "aeba47d81be3d135de5b9bd5ce5df7194c28d507eb96eb28332517f548f121f7"
KIND15_PIN_OFFSETS = {
    "carry_in": (-1, -1),
    "in0": (-1, 0),
    "in1": (-1, 1),
    "sum": (1, 0),
    "carry_out": (1, 1),
}
# The live PNG contains the short rendered leads immediately to the right of
# the logical output endpoints.  Current v15 baseline wires start at (1,y) and
# traverse (2,y), proving these alpha cells are ports rather than body masks.
KIND15_OUTPUT_LEAD_OFFSETS = frozenset({(2, 0), (2, 1)})

BIT0_CARRY_NODE = 45
BIT0_SUM_NODE = 49
BIT0_INPUT_NODES = (2, 3, 18)  # a0, b0, cin
REMOVED_BIT0_NODES = frozenset({43, 44, 46, 47, 48})
EXPECTED_KIND_COUNTS = {
    4: 15,
    6: 3,
    7: 12,
    9: 24,
    12: 8,
    15: 1,
    16: 1,
    17: 2,
    61: 3,
    69: 2,
}
EXPECTED_OUTPUT_ARRIVALS = [4, 6, 9, 7, 9, 8, 9, 9, 9]
ASSIGNMENTS = 1 << 17
ALL = (1 << ASSIGNMENTS) - 1


class AuditError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def _digest_bytes(payload: bytes) -> str:
    return sha256(payload).hexdigest()


def _digest(path: Path) -> str:
    return _digest_bytes(path.read_bytes())


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise AuditError(f"cannot load module {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


materializer = _load_module(MATERIALIZER_PATH, "kind15_bit0_base_materializer")
physical = materializer.physical
Connection = materializer.Connection


def _variable(index: int) -> int:
    return materializer._variable(index)


def _parse_frontier(levels_text: str, level: str) -> list[list[int]]:
    match = re.search(
        rf'^"{re.escape(level)}",(?:true|false),"[^"]*",(.*)$',
        levels_text,
        re.MULTILINE,
    )
    if match is None:
        raise AuditError(f"levels.txt has no {level!r} record")
    result = []
    for entry in match.group(1).split("|"):
        if not entry:
            continue
        fields = entry.split("&")
        _require(len(fields) == 3, f"invalid {level} frontier entry {entry!r}")
        result.append([int(value) for value in fields])
    return result


def review_kind15_geometry_contract() -> dict[str, Any]:
    """Pin the kind15 pin/body distinction to current served artifacts."""

    _require(
        _digest(KIND15_GEOMETRY_BASELINE) == KIND15_GEOMETRY_BASELINE_SHA256,
        "kind15 v15 geometry baseline SHA changed",
    )
    sprite_path = DEFAULT_COMPONENT_SPRITE_ROOT / "com_full_adder.png"
    _require(_digest(sprite_path) == KIND15_SPRITE_SHA256, "kind15 live sprite SHA changed")
    schema = {pin.name: pin.offset for pin in PIN_SCHEMAS[15]}
    _require(schema == KIND15_PIN_OFFSETS, f"kind15 pin schema changed: {schema!r}")
    sprite_cells = sprite_alpha_cells(sprite_path)
    _require(
        KIND15_OUTPUT_LEAD_OFFSETS <= sprite_cells,
        "kind15 live sprite no longer contains the reviewed output lead cells",
    )

    baseline = decode_v15(KIND15_GEOMETRY_BASELINE.read_bytes())
    endpoints = set()
    for wire in baseline.wires:
        points = wire_points(wire)
        endpoints.update((points[0], points[-1]))
    full_adders = [component for component in baseline.components if component.kind == 15]
    _require(len(full_adders) == 8, "kind15 geometry baseline no longer has eight full adders")
    missing_endpoint_evidence = []
    for component_index, component in enumerate(full_adders):
        _require(component.rotation == 0, "kind15 geometry baseline uses an unreviewed rotation")
        for name, offset in KIND15_PIN_OFFSETS.items():
            point = (component.position[0] + offset[0], component.position[1] + offset[1])
            if point not in endpoints:
                missing_endpoint_evidence.append((component_index, name, point))
    _require(
        not missing_endpoint_evidence,
        f"kind15 baseline lacks endpoint evidence {missing_endpoint_evidence[:4]!r}",
    )
    return {
        "schema": "kind15-v15-pin-body-mask-contract-v1",
        "baseline": str(KIND15_GEOMETRY_BASELINE.relative_to(ROOT)).replace("\\", "/"),
        "baseline_sha256": KIND15_GEOMETRY_BASELINE_SHA256,
        "baseline_full_adder_count": len(full_adders),
        "all_five_pin_offsets_have_wire_endpoints_on_every_instance": True,
        "sprite": str(sprite_path),
        "sprite_sha256": KIND15_SPRITE_SHA256,
        "pin_offsets": {name: list(offset) for name, offset in KIND15_PIN_OFFSETS.items()},
        "reviewed_output_lead_offsets": [list(value) for value in sorted(KIND15_OUTPUT_LEAD_OFFSETS)],
    }


def _partition_geometry_collisions(candidate: Circuit, geometry: Any):
    reviewed_leads = []
    unexpected = []
    for collision in geometry.wire_collisions:
        component = candidate.components[collision.component_index]
        allowed_points = {
            (
                component.position[0] + rotate_offset(offset, component.rotation)[0],
                component.position[1] + rotate_offset(offset, component.rotation)[1],
            )
            for offset in KIND15_OUTPUT_LEAD_OFFSETS
        }
        if component.kind == 15 and collision.point in allowed_points:
            reviewed_leads.append(collision)
        else:
            unexpected.append(collision)
    return tuple(reviewed_leads), tuple(unexpected)


def _packed_logic(
    nodes: tuple[dict[str, Any], ...], outputs: tuple[int, ...]
) -> tuple[dict[int, dict[str, int]], dict[str, Any]]:
    variables = {
        **{f"a{bit}": _variable(bit) for bit in range(8)},
        **{f"b{bit}": _variable(8 + bit) for bit in range(8)},
        "cin": _variable(16),
    }
    states: dict[int, dict[str, int]] = {}
    for node in nodes:
        node_id = int(node["id"])
        op = str(node["op"])
        args = [states[int(value)] for value in node.get("args", ())]
        if op == "CONST":
            state = {
                "bits": ALL if str(node["label"]) == "1" else 0,
                "driven": ALL,
                "conflict": 0,
                "depth": 0,
            }
        elif op == "INPUT":
            state = {
                "bits": variables[str(node["label"])],
                "driven": ALL,
                "conflict": 0,
                "depth": 0,
            }
        elif op in {"FULL_ADDER_SUM", "FULL_ADDER_CARRY"}:
            _require(len(args) == 3, f"{op} requires three inputs")
            left, right, carry_in = (value["bits"] for value in args)
            if op == "FULL_ADDER_SUM":
                bits = left ^ right ^ carry_in
            else:
                bits = (left & right) | (left & carry_in) | (right & carry_in)
            state = {"bits": bits & ALL, "driven": ALL, "conflict": 0, "depth": 4}
        elif op == "BUS":
            ones = 0
            zeros = 0
            driven = 0
            conflict = 0
            for offset in range(0, len(args), 2):
                enable, data = args[offset], args[offset + 1]
                active = enable["bits"]
                ones |= active & data["bits"]
                zeros |= active & (~data["bits"] & ALL)
                driven |= active
                conflict |= enable["conflict"] | data["conflict"]
            conflict |= ones & zeros
            state = {
                "bits": ones & ALL,
                "driven": driven & ALL,
                "conflict": conflict & ALL,
                "depth": max(value["depth"] for value in args) + 1,
            }
        else:
            _require(op in materializer.GATE_SPECS, f"unsupported transformed op {op!r}")
            conflict = 0
            for value in args:
                conflict |= value["conflict"]
            left = args[0]["bits"]
            right = args[1]["bits"] if len(args) == 2 else 0
            if op == "NOT":
                bits = ~left
            elif op == "AND":
                bits = left & right
            elif op == "NAND":
                bits = ~(left & right)
            elif op == "OR":
                bits = left | right
            elif op == "NOR":
                bits = ~(left | right)
            elif op == "XOR":
                bits = left ^ right
            elif op == "XNOR":
                bits = ~(left ^ right)
            else:  # pragma: no cover - guarded above
                raise AssertionError(op)
            state = {
                "bits": bits & ALL,
                "driven": ALL,
                "conflict": conflict & ALL,
                "depth": max(value["depth"] for value in args)
                + materializer.GATE_SPECS[op].delay,
            }
        _require(
            state["depth"] == int(node["arrival"]),
            f"transformed arrival mismatch at node {node_id}: {state['depth']} != {node['arrival']}",
        )
        states[node_id] = state

    actual = [states[index] for index in outputs]
    raw_variables = tuple(_variable(index) for index in range(17))
    carry = raw_variables[16]
    expected = []
    for left, right in zip(raw_variables[:8], raw_variables[8:16]):
        propagate = left ^ right
        expected.append(propagate ^ carry)
        carry = (left & right) | (propagate & carry)
    expected.append(carry)
    mismatch_masks = [state["bits"] ^ target for state, target in zip(actual, expected)]
    conflict = 0
    for state in states.values():
        conflict |= state["conflict"]
    z_masks = [(~state["driven"]) & ALL for state in actual]
    vector_payload = b"".join(
        state["bits"].to_bytes(ASSIGNMENTS // 8, "little") for state in actual
    )
    semantic = {
        "truth_table_rows": ASSIGNMENTS,
        "mismatch_count_by_output": [mask.bit_count() for mask in mismatch_masks],
        "mismatch_union_count": sum(1 for _ in ()) if not mismatch_masks else (
            __import__("functools").reduce(int.__or__, mismatch_masks, 0).bit_count()
        ),
        "conflict_assignment_count": conflict.bit_count(),
        "z_assignment_count_by_output": [mask.bit_count() for mask in z_masks],
        "output_vector_sha256": _digest_bytes(vector_payload),
    }
    return states, semantic


def transform_authoritative(payload: dict[str, Any]) -> dict[str, Any]:
    original_nodes = tuple(payload["factory_dag"]["nodes"])
    original_by_id = {int(node["id"]): node for node in original_nodes}
    _require(
        original_by_id[BIT0_CARRY_NODE]["op"] == "BUS"
        and original_by_id[BIT0_SUM_NODE]["op"] == "NOR",
        "authoritative bit0 node identities changed",
    )
    _require(
        sum(int(original_by_id[index]["cost"]) for index in {
            43, 44, 45, 46, 47, 48, 49
        }) == 10,
        "authoritative bit0 cone no longer costs 10",
    )

    arrivals: dict[int, int] = {}
    transformed_nodes: list[dict[str, Any]] = []
    for original in original_nodes:
        node_id = int(original["id"])
        if node_id in REMOVED_BIT0_NODES:
            continue
        node = dict(original)
        if node_id in {BIT0_CARRY_NODE, BIT0_SUM_NODE}:
            node.update(
                {
                    "op": (
                        "FULL_ADDER_CARRY"
                        if node_id == BIT0_CARRY_NODE
                        else "FULL_ADDER_SUM"
                    ),
                    "args": list(BIT0_INPUT_NODES),
                    "cost": 7 if node_id == BIT0_CARRY_NODE else 0,
                    "step_delay": 4,
                    "arrival": 4,
                    "may_z": False,
                    "label": "kind15:bit0",
                    "shared_component": "kind15-bit0",
                }
            )
            arrivals[node_id] = 4
        else:
            args = tuple(int(value) for value in node.get("args", ()))
            _require(
                all(argument in arrivals for argument in args),
                f"transformed node {node_id} is not topologically ordered",
            )
            if node["op"] in {"CONST", "INPUT"}:
                arrival = 0
            else:
                arrival = max(arrivals[argument] for argument in args) + int(node["step_delay"])
            node["arrival"] = arrival
            arrivals[node_id] = arrival
        transformed_nodes.append(node)

    outputs = tuple(int(value) for value in payload["factory_dag"]["outputs"])
    by_id = {int(node["id"]): node for node in transformed_nodes}
    reachable: set[int] = set()
    pending = list(outputs)
    while pending:
        node_id = pending.pop()
        if node_id in reachable:
            continue
        reachable.add(node_id)
        pending.extend(int(value) for value in by_id[node_id].get("args", ()))
    _require(reachable == set(by_id), "transformed DAG contains dead or missing nodes")

    gate = sum(int(node["cost"]) for node in transformed_nodes)
    output_arrivals = [arrivals[index] for index in outputs]
    delay = max(output_arrivals)
    _require((gate, delay) == (77, 9), f"unexpected transformed score {gate}/{delay}")
    _require(output_arrivals == EXPECTED_OUTPUT_ARRIVALS, "unexpected transformed arrival vector")
    factory_dag = {
        "outputs": list(outputs),
        "nodes": transformed_nodes,
        "live_node_count": len(transformed_nodes),
    }
    factory_dag["sha256"] = _digest_bytes(
        json.dumps(factory_dag, ensure_ascii=True, separators=(",", ":")).encode()
    )
    _states, semantic = _packed_logic(tuple(transformed_nodes), outputs)
    _require(not semantic["mismatch_union_count"], "transformed packed truth mismatch")
    _require(not semantic["conflict_assignment_count"], "transformed packed conflict")
    _require(not any(semantic["z_assignment_count_by_output"]), "transformed primary output Z")
    _require(
        semantic["output_vector_sha256"] == payload["semantic"]["output_vector_sha256"],
        "transformed output vector digest differs from authoritative DAG",
    )
    return {
        "schema": SCHEMA,
        "status": "sat-under-accepted-kind15-7-4-cost",
        "family": "authoritative 80/7 with bit0 10-gate cone replaced by native kind15",
        "source": {
            "authoritative_dag": str(AUTHORITATIVE_DAG.relative_to(ROOT)).replace("\\", "/"),
            "authoritative_dag_sha256": _digest(AUTHORITATIVE_DAG),
            "authoritative_factory_dag_sha256": payload["factory_dag"]["sha256"],
            "removed_nodes": sorted(REMOVED_BIT0_NODES),
            "replaced_output_nodes": [BIT0_SUM_NODE, BIT0_CARRY_NODE],
        },
        "cost_assumption": {
            "component_kind": 15,
            "required_acceptance_derived_frontier": [7, 4],
            "component_selection_fields": [7, 4],
            "header_fields_are_not_cost_proof": True,
        },
        "timing_delta": {
            "before": {"S0": 4, "C1": 2},
            "after": {"S0": 4, "C1": 4},
            "global_before": 7,
            "global_after": 9,
            "reason": "the replaced cone has asymmetric outputs; kind15 charges delay 4 to both",
        },
        "metrics": {
            "gate": gate,
            "delay": delay,
            "energy": gate * delay,
            "output_arrivals": output_arrivals,
            "reachable_nodes": len(transformed_nodes),
        },
        "semantic": semantic,
        "factory_dag": factory_dag,
    }


def _component_pin(components: tuple[Component, ...], index: int, name: str) -> Point:
    points = [
        pin.position
        for pin in positioned_pins(components[index], index)
        if pin.name == name
    ]
    _require(len(points) == 1, f"component {index} lacks exactly one {name!r} pin")
    return points[0]


def build_physical(
    payload: dict[str, Any], by_id: dict[int, dict[str, Any]]
) -> tuple[Circuit, tuple[Any, ...], dict[str, Any]]:
    dag_hash = payload["factory_dag"]["sha256"]
    identity = f"byte_adder:kind15-bit0:{dag_hash}"
    immutable = physical._scaffold()
    label_index = {component.user_label: index for index, component in enumerate(immutable)}
    mutables: list[Component] = []

    def append(component: Component) -> int:
        index = len(immutable) + len(mutables)
        mutables.append(component)
        return index

    a_split = append(Component(17, (0, 0), 0, stable_permanent_id(identity, "a-split"), word_size=8))
    b_split = append(Component(17, (0, 0), 0, stable_permanent_id(identity, "b-split"), word_size=8))
    full_adder = append(
        Component(
            15,
            (0, 0),
            0,
            stable_permanent_id(identity, "kind15-bit0"),
            cost_gate=7,
            cost_delay=4,
        )
    )
    node_components: dict[int, int] = {}
    bus_switches: dict[int, tuple[int, ...]] = {}
    for node in payload["factory_dag"]["nodes"]:
        node_id = int(node["id"])
        op = str(node["op"])
        if op == "CONST":
            kind = 2 if str(node["label"]) == "1" else 1
            node_components[node_id] = append(
                Component(kind, (0, 0), 0, stable_permanent_id(identity, f"const-{node_id}"))
            )
        elif op in materializer.GATE_SPECS:
            node_components[node_id] = append(
                Component(
                    materializer.GATE_SPECS[op].kind,
                    (0, 0),
                    0,
                    stable_permanent_id(identity, f"node-{node_id}-{op.lower()}"),
                )
            )
        elif op == "BUS":
            bus_switches[node_id] = tuple(
                append(
                    Component(
                        12,
                        (0, 0),
                        0,
                        stable_permanent_id(identity, f"bus-{node_id}-driver-{driver}"),
                    )
                )
                for driver in range(len(node["args"]) // 2)
            )
    merger = append(Component(16, (0, 0), 0, stable_permanent_id(identity, "sum-merger"), word_size=8))

    rows = tuple(index * 12 - ((len(mutables) - 1) * 12) // 2 for index in range(len(mutables)))
    placed = tuple(
        replace(component, position=(48 + slot * 40, rows[slot]))
        for slot, component in enumerate(mutables)
    )
    components = tuple([*immutable, *placed])
    _require(
        len({component.permanent_id for component in components}) == len(components),
        "duplicate permanent IDs in kind15 candidate",
    )

    members: dict[str, list[Point]] = defaultdict(list)
    inputs = {
        str(node["label"]): int(node["id"])
        for node in payload["factory_dag"]["nodes"]
        if node["op"] == "INPUT"
    }
    node_pin_refs: dict[int, tuple[int, str]] = {}
    for bit in range(8):
        node_pin_refs[inputs[f"a{bit}"]] = (a_split, f"out{bit}")
        node_pin_refs[inputs[f"b{bit}"]] = (b_split, f"out{bit}")
    node_pin_refs[inputs["cin"]] = (label_index["Carry in"], "value")
    for node_id, component_index in node_components.items():
        node_pin_refs[node_id] = (component_index, "out")
    for node_id, switches in bus_switches.items():
        node_pin_refs[node_id] = (switches[0], "out")
    node_pin_refs[BIT0_CARRY_NODE] = (full_adder, "carry_out")
    node_pin_refs[BIT0_SUM_NODE] = (full_adder, "sum")

    def add(label: str, point: Point) -> None:
        if point not in members[label]:
            members[label].append(point)

    def add_node(node_id: int, point: Point) -> None:
        add(f"signal:{node_id}", point)

    add("bridge:A", _component_pin(components, label_index["A"], "value"))
    add("bridge:A", _component_pin(components, a_split, "in"))
    add("bridge:B", _component_pin(components, label_index["B"], "value"))
    add("bridge:B", _component_pin(components, b_split, "in"))
    add("bridge:Output", _component_pin(components, merger, "out"))
    add("bridge:Output", _component_pin(components, label_index["Output"], "value"))

    for node_id, node in by_id.items():
        if node["op"] == "BUS":
            for switch in bus_switches[node_id]:
                add_node(node_id, _component_pin(components, switch, "out"))
        else:
            component_index, pin_name = node_pin_refs[node_id]
            add_node(node_id, _component_pin(components, component_index, pin_name))
    add_node(inputs["a0"], _component_pin(components, full_adder, "in0"))
    add_node(inputs["b0"], _component_pin(components, full_adder, "in1"))
    add_node(inputs["cin"], _component_pin(components, full_adder, "carry_in"))

    for node_id, node in by_id.items():
        op = str(node["op"])
        args = tuple(int(value) for value in node.get("args", ()))
        if op in materializer.GATE_SPECS:
            component_index = node_components[node_id]
            input_names = ("in",) if materializer.GATE_SPECS[op].arity == 1 else ("in0", "in1")
            for pin_name, argument in zip(input_names, args):
                add_node(argument, _component_pin(components, component_index, pin_name))
        elif op == "BUS":
            for driver, switch in enumerate(bus_switches[node_id]):
                add_node(args[driver * 2], _component_pin(components, switch, "enable"))
                add_node(args[driver * 2 + 1], _component_pin(components, switch, "in"))

    outputs = tuple(int(value) for value in payload["factory_dag"]["outputs"])
    for bit, node_id in enumerate(outputs[:8]):
        add_node(node_id, _component_pin(components, merger, f"in{bit}"))
    add_node(outputs[8], _component_pin(components, label_index["Carry out"], "value"))

    point_owner: dict[Point, str] = {}
    connections = []
    for label, points in sorted(members.items()):
        _require(len(points) >= 2, f"network {label!r} has no receiver")
        for point in points:
            previous = point_owner.get(point)
            _require(previous in {None, label}, f"pin point {point!r} belongs to two networks")
            point_owner[point] = label
        connections.extend(Connection(label, points[0], point) for point in points[1:])
    wires = physical._channel_route(components, tuple(connections))

    baseline = decode_v15((ROOT / "examples/byte_adder/baseline/circuit.data").read_bytes())
    metrics = payload["metrics"]
    candidate = replace(
        baseline,
        custom_id=0,
        hub_id=0,
        design=b"",
        gate=int(metrics["gate"]),
        delay=int(metrics["delay"]),
        description="Research-only kind15 bit0 splice; requires accepted full_adder 7/4 frontier",
        components=components,
        wires=wires,
    )
    mapping = {
        "label_index": label_index,
        "a_split": a_split,
        "b_split": b_split,
        "full_adder": full_adder,
        "merger": merger,
        "node_components": node_components,
        "bus_switches": bus_switches,
        "node_pin_refs": node_pin_refs,
    }
    return candidate, tuple(connections), mapping


def evaluate_proxy_kind15(proxy_path: Path):
    engine = physical._load_engine()
    engine.CIRCUIT_PATH = proxy_path
    circuit, compiled = engine.compile_circuit()
    variables = tuple(_variable(index) for index in range(17))
    outputs: dict[tuple[int, str], Any] = {}
    networks: dict[int, Any] = {}
    for index, component in enumerate(circuit.components):
        if component.kind == 79:
            if component.user_label == "A":
                bits = variables[:8]
            elif component.user_label == "B":
                bits = variables[8:16]
            elif component.user_label == "Cin":
                bits = (variables[16],) + (0,) * 7
            else:
                raise AuditError(f"unknown Byte Adder source {component.user_label!r}")
            outputs[(index, "in")] = materializer._normal(bits, 0)
        elif component.kind in {1, 2}:
            outputs[(index, "out")] = materializer._normal((ALL if component.kind == 2 else 0,), 0)

    pending = {
        index
        for index, component in enumerate(circuit.components)
        if component.kind not in {1, 2, 79, 81}
    }
    while pending:
        progress = False
        for network, pins in compiled.network_pins.items():
            if network in networks:
                continue
            drivers = [pin for pin in pins if pin.direction in {O, T}]
            if drivers and all((pin.component_index, pin.name) in outputs for pin in drivers):
                networks[network] = materializer._resolve(
                    [outputs[(pin.component_index, pin.name)] for pin in drivers]
                )
                progress = True
        for index in tuple(pending):
            component = circuit.components[index]
            input_pins = [
                pin
                for (component_index, _), pin in compiled.pins.items()
                if component_index == index and pin.direction == I
            ]
            if not all(
                (index, pin.name) not in compiled.pin_network
                or compiled.pin_network[(index, pin.name)] in networks
                for pin in input_pins
            ):
                continue
            values = {
                pin.name: (
                    networks[compiled.pin_network[(index, pin.name)]]
                    if (index, pin.name) in compiled.pin_network
                    else materializer._normal((0,) * pin.width, 0)
                )
                for pin in input_pins
            }
            input_depth = max((signal.depth for signal in values.values()), default=0)
            input_conflict = 0
            for signal in values.values():
                input_conflict |= signal.conflict

            def bit(name: str, offset: int = 0) -> int:
                signal = values[name]
                return signal.bits[offset] if offset < len(signal.bits) else 0

            kind = component.kind
            if kind == 3:
                result = {"out": materializer._normal((~bit("in") & ALL,), input_depth + 1, input_conflict)}
            elif kind == 4:
                result = {"out": materializer._normal((bit("in0") & bit("in1"),), input_depth + 1, input_conflict)}
            elif kind == 6:
                result = {"out": materializer._normal((~(bit("in0") & bit("in1")) & ALL,), input_depth + 1, input_conflict)}
            elif kind == 7:
                result = {"out": materializer._normal((bit("in0") | bit("in1"),), input_depth + 1, input_conflict)}
            elif kind == 9:
                result = {"out": materializer._normal((~(bit("in0") | bit("in1")) & ALL,), input_depth + 1, input_conflict)}
            elif kind == 10:
                result = {"out": materializer._normal((bit("in0") ^ bit("in1"),), input_depth + 2, input_conflict)}
            elif kind == 11:
                result = {"out": materializer._normal((~(bit("in0") ^ bit("in1")) & ALL,), input_depth + 2, input_conflict)}
            elif kind == 12:
                result = {
                    "out": materializer.PackedSignal(
                        (bit("in"),), bit("enable"), input_depth + 1, input_conflict
                    )
                }
            elif kind == 15:
                left, right, carry_in = bit("in0"), bit("in1"), bit("carry_in")
                result = {
                    "sum": materializer._normal((left ^ right ^ carry_in,), input_depth + 4, input_conflict),
                    "carry_out": materializer._normal(
                        ((left & right) | (left & carry_in) | (right & carry_in),),
                        input_depth + 4,
                        input_conflict,
                    ),
                }
            elif kind == 16:
                result = {
                    "out": materializer._normal(
                        tuple(bit(f"in{offset}") for offset in range(8)), input_depth, input_conflict
                    )
                }
            elif kind == 17:
                result = {
                    f"out{offset}": materializer._normal((bit("in", offset),), input_depth, input_conflict)
                    for offset in range(8)
                }
            else:
                raise AuditError(f"unsupported materialized component kind {kind}")
            outputs.update({(index, name): signal for name, signal in result.items()})
            pending.remove(index)
            progress = True
        _require(progress, f"packed physical evaluation stalled: {sorted(pending)!r}")
    for network, pins in compiled.network_pins.items():
        if network in networks:
            continue
        drivers = [pin for pin in pins if pin.direction in {O, T}]
        if drivers and all((pin.component_index, pin.name) in outputs for pin in drivers):
            networks[network] = materializer._resolve(
                [outputs[(pin.component_index, pin.name)] for pin in drivers]
            )
    return circuit, compiled, networks, outputs


def audit_physical(
    candidate: Circuit,
    connections: tuple[Any, ...],
    payload: dict[str, Any],
    by_id: dict[int, dict[str, Any]],
    mapping: dict[str, Any],
    *,
    proxy_path: Path,
) -> dict[str, Any]:
    encoded = encode_v15(candidate)
    _require(encode_v15(decode_v15(encoded)) == encoded, "v15 roundtrip is not byte-identical")
    rebuilt = Circuit.from_dict(candidate.to_dict())
    _require(encode_v15(rebuilt) == encoded, "canonical JSON rebuild differs")
    kind_counts = dict(sorted(Counter(component.kind for component in candidate.components).items()))
    _require(kind_counts == EXPECTED_KIND_COUNTS, f"unexpected physical kind counts {kind_counts!r}")
    _require(kind_counts.get(30, 0) == 0, "native com_add appears in kind15 candidate")
    full_adder_components = [component for component in candidate.components if component.kind == 15]
    _require(len(full_adder_components) == 1, "candidate must contain exactly one kind15")
    _require(
        (full_adder_components[0].cost_gate, full_adder_components[0].cost_delay) == (7, 4),
        "kind15 selection fields are not explicitly 7/4",
    )
    reviewed_gate = (
        sum(kind_counts.get(spec.kind, 0) * spec.cost for spec in materializer.GATE_SPECS.values())
        + kind_counts.get(12, 0) * 2
        + kind_counts.get(15, 0) * 7
    )
    _require(
        (reviewed_gate, candidate.delay, candidate.energy) == (77, 9, 693),
        "physical candidate header/cost differs from 77/9/693",
    )

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
        _require(not connectivity[field], f"connectivity failure {field}={connectivity[field]!r}")
    geometry_contract = review_kind15_geometry_contract()
    geometry = audit_sprite_geometry(candidate, DEFAULT_COMPONENT_SPRITE_ROOT)
    for field in (
        "unsupported_component_kinds",
        "component_overlap_cells",
        "wire_interior_pin_contacts",
    ):
        _require(not getattr(geometry, field), f"geometry failure {field}={getattr(geometry, field)!r}")
    reviewed_leads, unexpected_collisions = _partition_geometry_collisions(candidate, geometry)
    _require(
        not unexpected_collisions,
        f"unexpected geometry wire collisions {unexpected_collisions[:4]!r}",
    )

    expected_tri_state = sum(
        len(node["args"]) // 2 for node in by_id.values() if node["op"] == "BUS"
    )
    resolved = physical._audit_resolved_networks(
        candidate.components,
        candidate.wires,
        connections,
        expected_tri_state_output_count=expected_tri_state,
    )
    resolved["adversarial_foreign_label_rejected"] = physical._self_test_resolved_network_guard(
        candidate.components,
        candidate.wires,
        connections,
        expected_tri_state_output_count=expected_tri_state,
    )

    logical, semantic = _packed_logic(
        tuple(payload["factory_dag"]["nodes"]),
        tuple(int(value) for value in payload["factory_dag"]["outputs"]),
    )
    _require(semantic == payload["semantic"], "persisted transformed semantic certificate changed")
    proxy_path.parent.mkdir(parents=True, exist_ok=True)
    proxy_path.write_bytes(encode_v15(physical._proxy_for_semantics(candidate)))
    _proxy, compiled, networks, _component_outputs = evaluate_proxy_kind15(proxy_path)

    label_index = mapping["label_index"]
    node_pin_refs = dict(mapping["node_pin_refs"])
    cin_node = next(
        node_id
        for node_id, node in by_id.items()
        if node["op"] == "INPUT" and node["label"] == "cin"
    )
    node_pin_refs[cin_node] = (label_index["Carry in"], "in")
    mismatches = []
    for node_id, expected in logical.items():
        component_index, pin_name = node_pin_refs[node_id]
        network = compiled.pin_network[(component_index, pin_name)]
        actual = networks[network]
        fields = []
        if actual.bits[0] != expected["bits"]:
            fields.append("bits")
        if actual.driven != expected["driven"]:
            fields.append("driven")
        if actual.conflict != expected["conflict"]:
            fields.append("conflict")
        if actual.depth != expected["depth"]:
            fields.append("depth")
        if fields:
            mismatches.append({"node": node_id, "fields": fields})
    _require(not mismatches, f"physical node replay mismatch {mismatches[:4]!r}")

    bus_stats = []
    seen_bus_networks = set()
    for node_id, node in by_id.items():
        if node["op"] != "BUS":
            continue
        switches = mapping["bus_switches"][node_id]
        output_networks = {compiled.pin_network[(switch, "out")] for switch in switches}
        _require(len(output_networks) == 1, f"BUS {node_id} outputs are physically split")
        network = next(iter(output_networks))
        _require(network not in seen_bus_networks, f"BUS {node_id} aliases another BUS")
        seen_bus_networks.add(network)
        pins = compiled.network_pins[network]
        tri_drivers = [pin for pin in pins if pin.direction == T]
        ordinary_drivers = [pin for pin in pins if pin.direction == O]
        _require(
            len(tri_drivers) == len(switches) and not ordinary_drivers,
            f"BUS {node_id} physical owner set changed",
        )
        signal = networks[network]
        bus_stats.append(
            {
                "node": node_id,
                "driver_count": len(tri_drivers),
                "arrival": signal.depth,
                "z_assignment_count": ((~signal.driven) & ALL).bit_count(),
                "conflict_assignment_count": signal.conflict.bit_count(),
            }
        )
    _require(
        not any(item["conflict_assignment_count"] for item in bus_stats),
        "a physical BUS has conflicting drivers",
    )

    output_nodes = tuple(int(value) for value in payload["factory_dag"]["outputs"])
    merger = mapping["merger"]
    output_arrivals = []
    for bit, node_id in enumerate(output_nodes[:8]):
        signal = networks[compiled.pin_network[(merger, f"in{bit}")]]
        _require(signal.bits[0] == logical[node_id]["bits"] and signal.driven == ALL, f"S{bit} mismatch")
        output_arrivals.append(signal.depth)
    carry_sink = label_index["Carry out"]
    carry_signal = networks[compiled.pin_network[(carry_sink, "out")]]
    _require(
        carry_signal.bits[0] == logical[output_nodes[8]]["bits"] and carry_signal.driven == ALL,
        "carry output mismatch",
    )
    output_arrivals.append(carry_signal.depth)
    _require(output_arrivals == EXPECTED_OUTPUT_ARRIVALS, "physical output arrival vector changed")
    sum_sink = label_index["Output"]
    sum_signal = networks[compiled.pin_network[(sum_sink, "out")]]
    _require(sum_signal.driven == ALL, "packed Sum output is not fully driven")
    packed_conflicts = sum(signal.conflict.bit_count() for signal in networks.values())
    _require(not packed_conflicts, f"physical candidate has {packed_conflicts} packed conflicts")
    global_depth = max(signal.depth for signal in networks.values())
    _require(global_depth == 9, f"physical recursive depth is {global_depth}, not 9")

    sprite_names = sorted(
        {SPRITE_NAME_BY_COMPONENT_KIND[component.kind] for component in candidate.components}
    )
    return {
        "candidate_bytes": encoded,
        "candidate_sha256": _digest_bytes(encoded),
        "component_count": len(candidate.components),
        "wire_count": len(candidate.wires),
        "component_kind_counts": {str(key): value for key, value in kind_counts.items()},
        "reviewed_gate": reviewed_gate,
        "native_com_add_count": 0,
        "native_com_full_adder_count": 1,
        "kind15_selection_fields": [7, 4],
        "connectivity": connectivity,
        "geometry": {
            **asdict(geometry),
            "kind15_pin_body_mask_contract": geometry_contract,
            "reviewed_kind15_output_lead_contact_count": len(reviewed_leads),
            "unexpected_wire_collision_count": len(unexpected_collisions),
            "sprite_sha256": {
                name: _digest(DEFAULT_COMPONENT_SPRITE_ROOT / name) for name in sprite_names
            },
        },
        "resolved_networks": resolved,
        "semantic": {
            "vectors_checked": ASSIGNMENTS,
            "node_replay_count": len(logical),
            "node_replay_mismatch_count": 0,
            "bus_nodes": bus_stats,
            "packed_conflict_cases": 0,
            "output_arrivals": output_arrivals,
            "global_depth": global_depth,
            "sum_depth": sum_signal.depth,
            "carry_depth": carry_signal.depth,
            "sum_correct": True,
            "carry_correct": True,
            "primary_output_z_count": 0,
        },
        "serialization": {
            "v15_roundtrip_byte_identical": True,
            "canonical_json_rebuild_byte_identical": True,
        },
    }


def _assert_isolated_output(output_dir: Path) -> Path:
    output = output_dir.resolve()
    try:
        output.relative_to(INTAKE_ROOT.resolve())
    except ValueError as exc:
        raise AuditError(f"output must be below {INTAKE_ROOT.resolve()}") from exc
    return output


def _write_json(path: Path, payload: object) -> bytes:
    data = (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    path.write_bytes(data)
    return data


def main(argv: Iterable[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(list(argv) if argv is not None else None)

    _assert_game_not_running()
    _require(_digest(AUTHORITATIVE_DAG) == AUTHORITATIVE_DAG_SHA256, "authoritative 80/7 DAG SHA changed")
    full_adder_audit = json.loads(FULL_ADDER_AUDIT.read_text(encoding="utf-8"))
    _require(full_adder_audit.get("status") == "verified", "Full Adder 7/4 physical audit is not verified")
    _require(
        _digest(FULL_ADDER_FORMAL) == full_adder_audit["source"]["sha256"],
        "current Full Adder formal save differs from the physically audited artifact",
    )
    original, _original_by_id, original_review = materializer.review_dag(AUTHORITATIVE_DAG)
    transformed = transform_authoritative(original)
    by_id = {int(node["id"]): node for node in transformed["factory_dag"]["nodes"]}
    candidate, connections, mapping = build_physical(transformed, by_id)
    candidate2, connections2, _mapping2 = build_physical(transformed, by_id)
    _require(connections2 == connections, "deterministic connection rebuild differs")
    _require(encode_v15(candidate2) == encode_v15(candidate), "deterministic physical rebuild differs")

    output_dir = _assert_isolated_output(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=False)
    proxy_path = output_dir / "semantic_proxy.circuit.data"
    audit = audit_physical(
        candidate,
        connections,
        transformed,
        by_id,
        mapping,
        proxy_path=proxy_path,
    )
    candidate_bytes = audit.pop("candidate_bytes")
    candidate_path = output_dir / "candidate.circuit.data"
    candidate_path.write_bytes(candidate_bytes)
    decoded_bytes = _write_json(output_dir / "candidate.decoded.json", candidate.to_dict())
    transformed_bytes = _write_json(output_dir / "transformed_factory_dag.json", transformed)

    levels_bytes = LEVELS_PATH.read_bytes()
    levels_text = levels_bytes.decode("utf-8")
    full_adder_frontier = _parse_frontier(levels_text, "full_adder")
    byte_adder_frontier = _parse_frontier(levels_text, "byte_adder")
    acceptance_ready = any(item[:2] == [7, 4] for item in full_adder_frontier)
    report = {
        "schema": "byte-adder-kind15-bit0-materialization-audit-v1",
        "status": "verified-research-candidate",
        "scope": {
            "deployment_supported": False,
            "formal_byte_adder_written": False,
            "formal_full_adder_written": False,
            "levels_written": False,
            "repository_candidate_written": False,
            "backup_created": False,
            "game_started": False,
        },
        "source_review": original_review,
        "full_adder_7_4_prerequisite": {
            "audit": str(FULL_ADDER_AUDIT.resolve()),
            "audit_sha256": _digest(FULL_ADDER_AUDIT),
            "formal_save": str(FULL_ADDER_FORMAL.resolve()),
            "formal_save_sha256": _digest(FULL_ADDER_FORMAL),
            "physical_candidate_verified": True,
        },
        "runtime_cost_precondition": {
            "levels": str(LEVELS_PATH.resolve()),
            "levels_sha256": _digest_bytes(levels_bytes),
            "full_adder_frontier": full_adder_frontier,
            "byte_adder_frontier": byte_adder_frontier,
            "required_full_adder_frontier": [7, 4, 1],
            "acceptance_derived_kind15_7_4_ready_now": acceptance_ready,
            "deployable_now": False,
            "reason": (
                "research materialization is complete, but deployment is forbidden; additionally "
                "kind15 may be costed as 7/4 only after Full Adder level acceptance writes that frontier"
            ),
        },
        "transformation": transformed,
        "physical_audit": audit,
        "deterministic_rebuild_byte_identical": True,
        "artifacts": {
            "candidate": {"path": str(candidate_path.resolve()), "sha256": _digest_bytes(candidate_bytes)},
            "candidate_decoded": {
                "path": str((output_dir / "candidate.decoded.json").resolve()),
                "sha256": _digest_bytes(decoded_bytes),
            },
            "transformed_factory_dag": {
                "path": str((output_dir / "transformed_factory_dag.json").resolve()),
                "sha256": _digest_bytes(transformed_bytes),
            },
            "semantic_proxy": {"path": str(proxy_path.resolve()), "sha256": _digest(proxy_path)},
        },
    }
    report_bytes = _write_json(output_dir / "audit.json", report)
    _assert_game_not_running()
    print(
        json.dumps(
            {
                "status": report["status"],
                "candidate": str(candidate_path.resolve()),
                "candidate_sha256": _digest_bytes(candidate_bytes),
                "audit": str((output_dir / "audit.json").resolve()),
                "audit_sha256": _digest_bytes(report_bytes),
                "score": [candidate.gate, candidate.delay, candidate.energy],
                "output_arrivals": audit["semantic"]["output_arrivals"],
                "vectors_checked": audit["semantic"]["vectors_checked"],
                "kind15_7_4_runtime_ready_now": acceptance_ready,
                "formal_save_written": False,
                "levels_written": False,
                "repository_candidate_written": False,
                "game_started": False,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
