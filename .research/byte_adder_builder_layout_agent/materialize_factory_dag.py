"""Generic current-v15 materializer for reviewed Byte Adder Factory DAG JSON.

Default operation is research-only: write a candidate, semantic proxy, and
machine certificate below ``.research``.  ``--deploy`` is the only mode which
replaces ``examples/byte_adder/candidate/circuit.data`` and the live
``schematics/byte_adder/Default/circuit.data``.  Deployment never creates a
backup and refuses to run while Turing Complete is open.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass, replace
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any, Iterable

from tc_save_lab.codec import decode_v15, encode_v15
from tc_save_lab.foundry import _assert_game_not_running
from tc_save_lab.model import Circuit, Component, Point
from tc_save_lab.pins import I, O, T, analyze_connectivity, positioned_pins
from tc_save_lab.sprite_geometry import DEFAULT_COMPONENT_SPRITE_ROOT, audit_sprite_geometry
from tc_save_lab.builder import stable_permanent_id


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import hub79_bootstrap as physical
from route_byte_adder import Connection


ASSIGNMENTS = 1 << 17
ALL = (1 << ASSIGNMENTS) - 1
DEFAULT_REPOSITORY_CANDIDATE = ROOT / "examples" / "byte_adder" / "candidate" / "circuit.data"
DEFAULT_FORMAL_SAVE = (
    Path.home()
    / "AppData"
    / "Roaming"
    / "Turing Complete"
    / "schematics"
    / "byte_adder"
    / "Default"
    / "circuit.data"
)


@dataclass(frozen=True)
class GateSpec:
    kind: int
    cost: int
    delay: int
    arity: int


GATE_SPECS = {
    "NOT": GateSpec(3, 1, 1, 1),
    "AND": GateSpec(4, 1, 1, 2),
    "NAND": GateSpec(6, 1, 1, 2),
    "OR": GateSpec(7, 1, 1, 2),
    "NOR": GateSpec(9, 1, 1, 2),
    "XOR": GateSpec(10, 3, 2, 2),
    "XNOR": GateSpec(11, 3, 2, 2),
}


@dataclass(frozen=True)
class PackedSignal:
    bits: tuple[int, ...]
    driven: int
    depth: int
    conflict: int = 0


def _normal(bits: Iterable[int], depth: int, conflict: int = 0) -> PackedSignal:
    return PackedSignal(tuple(value & ALL for value in bits), ALL, depth, conflict & ALL)


def _resolve(drivers: list[PackedSignal]) -> PackedSignal:
    width = max(len(driver.bits) for driver in drivers)
    ones = [0] * width
    zeros = [0] * width
    driven = 0
    conflict = 0
    depth = 0
    for driver in drivers:
        depth = max(depth, driver.depth)
        driven |= driver.driven
        conflict |= driver.conflict
        for bit in range(width):
            value = driver.bits[bit] if bit < len(driver.bits) else 0
            ones[bit] |= driver.driven & value
            zeros[bit] |= driver.driven & (~value & ALL)
    for one, zero in zip(ones, zeros):
        conflict |= one & zero
    return PackedSignal(tuple(ones), driven & ALL, depth, conflict & ALL)


def _rooted(path: Path | str) -> Path:
    path = Path(path)
    return path.resolve() if path.is_absolute() else (ROOT / path).resolve()


def _load_module(path: Path, prefix: str):
    name = f"{prefix}_{sha256(str(path).encode()).hexdigest()[:12]}"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load Python module {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _certificate_references(value: Any) -> list[tuple[str, str]]:
    result: list[tuple[str, str]] = []
    if isinstance(value, dict):
        certificate = value.get("certificate")
        digest = value.get("certificate_sha256")
        if isinstance(certificate, str) and isinstance(digest, str):
            result.append((certificate, digest.lower()))
        for nested in value.values():
            result.extend(_certificate_references(nested))
    elif isinstance(value, list):
        for nested in value:
            result.extend(_certificate_references(nested))
    return result


def review_dag(
    dag_source: Path,
    *,
    builder_path: Path | None = None,
    builder_witness: Path | None = None,
) -> tuple[dict[str, Any], dict[int, dict[str, Any]], dict[str, Any]]:
    dag_source = _rooted(dag_source)
    persisted = json.loads(dag_source.read_text(encoding="utf-8"))
    if persisted.get("status") != "sat":
        raise RuntimeError(f"Factory DAG is not a SAT result: {persisted.get('status')!r}")

    generator_replay_equal: bool | None = None
    builder_hash: str | None = None
    builder_witness_hash: str | None = None
    if builder_witness is not None and builder_path is None:
        raise RuntimeError("--builder-witness requires --builder")
    if builder_path is not None:
        builder_path = _rooted(builder_path)
        module = _load_module(builder_path, "byte_adder_factory_builder")
        if not hasattr(module, "build"):
            raise RuntimeError(f"builder {builder_path} has no build() function")
        if builder_witness is None:
            generated = module.build()
        else:
            builder_witness = _rooted(builder_witness)
            if not builder_witness.is_file():
                raise RuntimeError(f"builder witness is missing: {builder_witness}")
            generated = module.build(builder_witness)
            builder_witness_hash = sha256(builder_witness.read_bytes()).hexdigest()
        generator_replay_equal = generated == persisted
        if not generator_replay_equal:
            raise RuntimeError("persisted Factory DAG differs from its current generator")
        builder_hash = sha256(builder_path.read_bytes()).hexdigest()

    metrics = persisted.get("metrics")
    semantic = persisted.get("semantic")
    factory_dag = persisted.get("factory_dag")
    if not isinstance(metrics, dict) or not isinstance(semantic, dict) or not isinstance(factory_dag, dict):
        raise RuntimeError("Factory DAG JSON lacks metrics, semantic, or factory_dag")
    if semantic.get("truth_table_rows") != ASSIGNMENTS:
        raise RuntimeError("Factory DAG does not cover the complete U8/U8/U1 domain")
    if (
        semantic.get("mismatch_union_count")
        or semantic.get("conflict_assignment_count")
        or any(semantic.get("z_assignment_count_by_output", (1,)))
    ):
        raise RuntimeError(f"Factory semantic certificate is not clean: {semantic!r}")

    nodes = factory_dag.get("nodes")
    outputs_raw = factory_dag.get("outputs")
    if not isinstance(nodes, list) or not isinstance(outputs_raw, list):
        raise RuntimeError("factory_dag nodes/outputs are missing")
    by_id = {int(node["id"]): node for node in nodes}
    if len(by_id) != len(nodes):
        raise RuntimeError("duplicate node id in Factory DAG")
    if factory_dag.get("live_node_count") != len(nodes):
        raise RuntimeError("Factory DAG live node count mismatch")
    if metrics.get("reachable_nodes") != len(nodes):
        raise RuntimeError("metrics reachable node count mismatch")

    expected_inputs = {
        *{f"a{bit}" for bit in range(8)},
        *{f"b{bit}" for bit in range(8)},
        "cin",
    }
    actual_inputs = {node.get("label") for node in nodes if node.get("op") == "INPUT"}
    if actual_inputs != expected_inputs:
        raise RuntimeError(
            f"Factory input contract mismatch: missing={expected_inputs-actual_inputs!r}, "
            f"extra={actual_inputs-expected_inputs!r}"
        )

    arrivals: dict[int, int] = {}
    reviewed_cost = 0
    bus_ids = []
    bus_resolved_name_forms: Counter[str] = Counter()
    tri_state_output_count = 0
    for node in nodes:
        node_id = int(node["id"])
        op = str(node["op"])
        args = tuple(int(value) for value in node.get("args", ()))
        if any(argument not in arrivals for argument in args):
            raise RuntimeError(f"node {node_id} is not topologically serialized")
        if op in {"CONST", "INPUT"}:
            expected_cost = 0
            expected_delay = 0
            expected_arrival = 0
            if args:
                raise RuntimeError(f"source node {node_id} unexpectedly has fanins")
            if op == "CONST" and str(node.get("label")) not in {"0", "1"}:
                raise RuntimeError(f"unsupported constant label at node {node_id}")
        elif op in GATE_SPECS:
            spec = GATE_SPECS[op]
            if len(args) != spec.arity:
                raise RuntimeError(f"node {node_id} {op} arity changed")
            expected_cost = spec.cost
            expected_delay = spec.delay
            expected_arrival = max(arrivals[argument] for argument in args) + spec.delay
        elif op == "BUS":
            if not args or len(args) % 2:
                raise RuntimeError(f"BUS {node_id} needs one or more complete drivers")
            driver_count = len(args) // 2
            expected_cost = driver_count * 2
            expected_delay = 1
            expected_arrival = max(arrivals[argument] for argument in args) + 1
            bus_ids.append(node_id)
            tri_state_output_count += driver_count
            serialized_resolved_name = node.get("resolved_network")
            allowed_resolved_names = {
                f"bus_node_{node_id}": "bus-node",
                f"bus_{node_id}": "bus-short",
            }
            if serialized_resolved_name is None:
                resolved_name = f"bus_node_{node_id}"
                bus_resolved_name_forms["implicit-bus-node"] += 1
            elif serialized_resolved_name in allowed_resolved_names:
                resolved_name = str(serialized_resolved_name)
                bus_resolved_name_forms[allowed_resolved_names[resolved_name]] += 1
            else:
                raise RuntimeError(f"BUS {node_id} resolved-network label changed")
            drivers = node.get("drivers")
            if drivers is not None:
                if len(drivers) != driver_count:
                    raise RuntimeError(f"BUS {node_id} serialized driver count changed")
                for driver_index, driver in enumerate(drivers):
                    if (
                        int(driver["enable"]) != args[driver_index * 2]
                        or int(driver["data"]) != args[driver_index * 2 + 1]
                        or driver.get("owner") != resolved_name
                    ):
                        raise RuntimeError(f"BUS {node_id} driver ownership changed")
        else:
            raise RuntimeError(f"unsupported Factory operation {op!r}")
        if (
            int(node.get("cost", -1)) != expected_cost
            or int(node.get("step_delay", -1)) != expected_delay
            or int(node.get("arrival", -1)) != expected_arrival
        ):
            raise RuntimeError(f"node {node_id} cost/delay annotation mismatch")
        if bool(node.get("may_z")) != (op == "BUS"):
            raise RuntimeError(f"node {node_id} may_z annotation mismatch")
        arrivals[node_id] = expected_arrival
        reviewed_cost += expected_cost

    outputs = tuple(int(value) for value in outputs_raw)
    if len(outputs) != 9 or any(output not in by_id for output in outputs):
        raise RuntimeError("Factory DAG must expose eight sum bits and one carry bit")
    output_arrivals = [arrivals[output] for output in outputs]
    gate = int(metrics.get("gate", -1))
    delay = int(metrics.get("delay", -1))
    energy = int(metrics.get("energy", -1))
    if reviewed_cost != gate or max(output_arrivals) != delay or gate * delay != energy:
        raise RuntimeError(
            f"Factory score mismatch: recomputed={reviewed_cost}/{max(output_arrivals)}/"
            f"{reviewed_cost*max(output_arrivals)}, serialized={gate}/{delay}/{energy}"
        )
    if list(metrics.get("output_arrivals", ())) != output_arrivals:
        raise RuntimeError("Factory output arrival vector mismatch")

    hash_payload = {
        "outputs": list(outputs),
        "nodes": nodes,
        "live_node_count": factory_dag["live_node_count"],
    }
    # Several Factory lineages are currently in use.  Prefix builders hash a
    # compact insertion-order serialization, Boolean-superopt builders use a
    # sorted human-spaced serialization, and newer forward builders use sorted
    # compact JSON.  Accept only these reviewed canonical forms rather than
    # silently dropping the structural hash check.
    factory_hash_candidates = {
        "compact-ascii": sha256(
            json.dumps(
                hash_payload,
                ensure_ascii=True,
                separators=(",", ":"),
            ).encode()
        ).hexdigest(),
        "sorted-unicode": sha256(
            json.dumps(
                hash_payload,
                ensure_ascii=False,
                sort_keys=True,
            ).encode()
        ).hexdigest(),
        "sorted-compact": sha256(
            json.dumps(
                hash_payload,
                sort_keys=True,
                separators=(",", ":"),
            ).encode()
        ).hexdigest(),
    }
    serialized_factory_hash = str(factory_dag.get("sha256", "")).lower()
    matching_hash_forms = [
        name
        for name, digest in factory_hash_candidates.items()
        if digest == serialized_factory_hash
    ]
    if not matching_hash_forms:
        raise RuntimeError(
            "Factory DAG structural serialization hash mismatch: "
            f"serialized={serialized_factory_hash!r}, "
            f"reviewed={factory_hash_candidates!r}"
        )
    factory_hash = serialized_factory_hash

    certificate_results = []
    for reference, expected_hash in _certificate_references(persisted):
        path = _rooted(reference)
        if not path.is_file():
            raise RuntimeError(f"referenced certificate is missing: {path}")
        actual_hash = sha256(path.read_bytes()).hexdigest()
        if actual_hash != expected_hash:
            raise RuntimeError(f"referenced certificate hash mismatch: {path}")
        certificate_results.append(
            {
                "path": str(path.relative_to(ROOT)).replace("\\", "/"),
                "sha256": actual_hash,
            }
        )

    review = {
        "dag_source": str(dag_source.relative_to(ROOT)).replace("\\", "/"),
        "dag_source_sha256": sha256(dag_source.read_bytes()).hexdigest(),
        "builder": (
            str(builder_path.relative_to(ROOT)).replace("\\", "/")
            if builder_path is not None
            else None
        ),
        "builder_sha256": builder_hash,
        "builder_witness": (
            str(builder_witness.relative_to(ROOT)).replace("\\", "/")
            if builder_witness is not None
            else None
        ),
        "builder_witness_sha256": builder_witness_hash,
        "generator_replay_equal": generator_replay_equal,
        "factory_dag_sha256": factory_hash,
        "factory_dag_hash_form": matching_hash_forms[0],
        "structural_sha256": metrics.get("structural_sha256"),
        "referenced_certificates": certificate_results,
        "recursive_cost_delay_verified": True,
        "bus_node_count": len(bus_ids),
        "bus_resolved_name_forms": dict(sorted(bus_resolved_name_forms.items())),
        "tri_state_output_count": tri_state_output_count,
    }
    return persisted, by_id, review


def _variable(index: int) -> int:
    if index < 3:
        return int.from_bytes(bytes([(0xAA, 0xCC, 0xF0)[index]]) * (ASSIGNMENTS // 8), "little")
    block = 1 << (index - 3)
    data = (bytes(block) + bytes([0xFF]) * block) * (ASSIGNMENTS // (16 * block))
    return int.from_bytes(data, "little")


def logical_states(nodes: tuple[dict[str, Any], ...]) -> dict[int, dict[str, int]]:
    variables = {
        **{f"a{bit}": _variable(bit) for bit in range(8)},
        **{f"b{bit}": _variable(8 + bit) for bit in range(8)},
        "cin": _variable(16),
    }
    result: dict[int, dict[str, int]] = {}
    for node in nodes:
        node_id = int(node["id"])
        op = node["op"]
        args = [result[int(value)] for value in node.get("args", ())]
        if op == "CONST":
            bits = ALL if str(node["label"]) == "1" else 0
            state = {"bits": bits, "driven": ALL, "conflict": 0, "depth": 0}
        elif op == "INPUT":
            state = {
                "bits": variables[node["label"]],
                "driven": ALL,
                "conflict": 0,
                "depth": 0,
            }
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
            else:
                raise AssertionError(op)
            state = {
                "bits": bits & ALL,
                "driven": ALL,
                "conflict": conflict & ALL,
                "depth": max(value["depth"] for value in args) + GATE_SPECS[op].delay,
            }
        if state["depth"] != int(node["arrival"]):
            raise RuntimeError(f"packed logical replay depth mismatch at node {node_id}")
        result[node_id] = state
    return result


def _component_pin(components: tuple[Component, ...], index: int, name: str) -> Point:
    values = [
        pin.position
        for pin in positioned_pins(components[index], index)
        if pin.name == name
    ]
    if len(values) != 1:
        raise RuntimeError(f"component {index} lacks exactly one pin {name!r}")
    return values[0]


def build_physical(
    payload: dict[str, Any],
    by_id: dict[int, dict[str, Any]],
) -> tuple[Circuit, tuple[Connection, ...], dict[str, Any]]:
    dag_hash = payload["factory_dag"]["sha256"]
    identity = f"byte_adder:factory-dag:{dag_hash}"
    immutable = physical._scaffold()
    label_index = {component.user_label: index for index, component in enumerate(immutable)}
    mutables: list[Component] = []

    def append(component: Component) -> int:
        index = len(immutable) + len(mutables)
        mutables.append(component)
        return index

    a_split = append(
        Component(17, (0, 0), 0, stable_permanent_id(identity, "a-split"), word_size=8)
    )
    b_split = append(
        Component(17, (0, 0), 0, stable_permanent_id(identity, "b-split"), word_size=8)
    )
    node_components: dict[int, int] = {}
    bus_switches: dict[int, tuple[int, ...]] = {}
    for node in payload["factory_dag"]["nodes"]:
        node_id = int(node["id"])
        op = node["op"]
        if op == "CONST":
            kind = 2 if str(node["label"]) == "1" else 1
            node_components[node_id] = append(
                Component(kind, (0, 0), 0, stable_permanent_id(identity, f"const-{node_id}"))
            )
        elif op in GATE_SPECS:
            node_components[node_id] = append(
                Component(
                    GATE_SPECS[op].kind,
                    (0, 0),
                    0,
                    stable_permanent_id(identity, f"node-{node_id}-{op.lower()}"),
                )
            )
        elif op == "BUS":
            driver_count = len(node["args"]) // 2
            bus_switches[node_id] = tuple(
                append(
                    Component(
                        12,
                        (0, 0),
                        0,
                        stable_permanent_id(identity, f"bus-{node_id}-driver-{driver}"),
                    )
                )
                for driver in range(driver_count)
            )
    merger = append(
        Component(16, (0, 0), 0, stable_permanent_id(identity, "sum-merger"), word_size=8)
    )

    rows = tuple(
        index * 12 - ((len(mutables) - 1) * 12) // 2
        for index in range(len(mutables))
    )
    placed = tuple(
        replace(component, position=(48 + slot * 40, rows[slot]))
        for slot, component in enumerate(mutables)
    )
    components = tuple([*immutable, *placed])
    if len({component.permanent_id for component in components}) != len(components):
        raise RuntimeError("materialized candidate has duplicate permanent IDs")

    members: dict[str, list[Point]] = defaultdict(list)
    node_pin_refs: dict[int, tuple[int, str]] = {}
    inputs = {
        node["label"]: int(node["id"])
        for node in payload["factory_dag"]["nodes"]
        if node["op"] == "INPUT"
    }
    for bit in range(8):
        node_pin_refs[inputs[f"a{bit}"]] = (a_split, f"out{bit}")
        node_pin_refs[inputs[f"b{bit}"]] = (b_split, f"out{bit}")
    node_pin_refs[inputs["cin"]] = (label_index["Carry in"], "value")
    for node_id, component_index in node_components.items():
        node_pin_refs[node_id] = (component_index, "out")
    for node_id, switches in bus_switches.items():
        node_pin_refs[node_id] = (switches[0], "out")

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
            source_index, source_name = node_pin_refs[node_id]
            add_node(node_id, _component_pin(components, source_index, source_name))
    for node_id, node in by_id.items():
        op = node["op"]
        args = tuple(int(value) for value in node.get("args", ()))
        if op in GATE_SPECS:
            component_index = node_components[node_id]
            input_names = ("in",) if GATE_SPECS[op].arity == 1 else ("in0", "in1")
            for name, argument in zip(input_names, args):
                add_node(argument, _component_pin(components, component_index, name))
        elif op == "BUS":
            for driver, switch in enumerate(bus_switches[node_id]):
                add_node(args[driver * 2], _component_pin(components, switch, "enable"))
                add_node(args[driver * 2 + 1], _component_pin(components, switch, "in"))

    outputs = tuple(int(value) for value in payload["factory_dag"]["outputs"])
    for bit, node_id in enumerate(outputs[:8]):
        add_node(node_id, _component_pin(components, merger, f"in{bit}"))
    add_node(outputs[8], _component_pin(components, label_index["Carry out"], "value"))

    point_owner: dict[Point, str] = {}
    connections: list[Connection] = []
    for label, points in sorted(members.items()):
        if len(points) < 2:
            raise RuntimeError(f"materialized network {label!r} has no receiver")
        for point in points:
            previous = point_owner.get(point)
            if previous is not None and previous != label:
                raise RuntimeError(f"pin point {point!r} belongs to two logical networks")
            point_owner[point] = label
        connections.extend(Connection(label, points[0], point) for point in points[1:])

    wires = physical._channel_route(components, tuple(connections))
    baseline = decode_v15(
        (ROOT / "examples" / "byte_adder" / "baseline" / "circuit.data").read_bytes()
    )
    metrics = payload["metrics"]
    candidate = replace(
        baseline,
        custom_id=0,
        hub_id=0,
        design=b"",
        gate=int(metrics["gate"]),
        delay=int(metrics["delay"]),
        description=f"Codex Factory DAG {metrics['gate']}/{metrics['delay']} byte adder",
        components=components,
        wires=wires,
    )
    mapping = {
        "label_index": label_index,
        "a_split": a_split,
        "b_split": b_split,
        "merger": merger,
        "node_components": node_components,
        "bus_switches": bus_switches,
        "node_pin_refs": node_pin_refs,
    }
    return candidate, tuple(connections), mapping


def evaluate_proxy(proxy_path: Path) -> tuple[Circuit, Any, dict[int, PackedSignal], dict[tuple[int, str], PackedSignal]]:
    engine = physical._load_engine()
    engine.CIRCUIT_PATH = proxy_path
    circuit, compiled = engine.compile_circuit()
    variables = tuple(_variable(index) for index in range(17))
    outputs: dict[tuple[int, str], PackedSignal] = {}
    networks: dict[int, PackedSignal] = {}
    for index, component in enumerate(circuit.components):
        if component.kind == 79:
            if component.user_label == "A":
                bits = variables[:8]
            elif component.user_label == "B":
                bits = variables[8:16]
            elif component.user_label == "Cin":
                bits = (variables[16],) + (0,) * 7
            else:
                raise RuntimeError(f"unknown Byte Adder source {component.user_label!r}")
            outputs[(index, "in")] = _normal(bits, 0)
        elif component.kind in {1, 2}:
            outputs[(index, "out")] = _normal((ALL if component.kind == 2 else 0,), 0)

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
                networks[network] = _resolve(
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
                    else _normal((0,) * pin.width, 0)
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
                result = {"out": _normal((~bit("in") & ALL,), input_depth + 1, input_conflict)}
            elif kind == 4:
                result = {"out": _normal((bit("in0") & bit("in1"),), input_depth + 1, input_conflict)}
            elif kind == 6:
                result = {"out": _normal((~(bit("in0") & bit("in1")) & ALL,), input_depth + 1, input_conflict)}
            elif kind == 7:
                result = {"out": _normal((bit("in0") | bit("in1"),), input_depth + 1, input_conflict)}
            elif kind == 9:
                result = {"out": _normal((~(bit("in0") | bit("in1")) & ALL,), input_depth + 1, input_conflict)}
            elif kind == 10:
                result = {"out": _normal((bit("in0") ^ bit("in1"),), input_depth + 2, input_conflict)}
            elif kind == 11:
                result = {"out": _normal((~(bit("in0") ^ bit("in1")) & ALL,), input_depth + 2, input_conflict)}
            elif kind == 12:
                result = {
                    "out": PackedSignal((bit("in"),), bit("enable"), input_depth + 1, input_conflict)
                }
            elif kind == 16:
                result = {
                    "out": _normal(
                        tuple(bit(f"in{offset}") for offset in range(8)),
                        input_depth,
                        input_conflict,
                    )
                }
            elif kind == 17:
                result = {
                    f"out{offset}": _normal((bit("in", offset),), input_depth, input_conflict)
                    for offset in range(8)
                }
            else:
                raise RuntimeError(f"unsupported materialized component kind {kind}")
            outputs.update({(index, name): signal for name, signal in result.items()})
            pending.remove(index)
            progress = True
        if not progress:
            raise RuntimeError(f"packed physical evaluation stalled: {sorted(pending)!r}")
    for network, pins in compiled.network_pins.items():
        if network in networks:
            continue
        drivers = [pin for pin in pins if pin.direction in {O, T}]
        if drivers and all((pin.component_index, pin.name) in outputs for pin in drivers):
            networks[network] = _resolve(
                [outputs[(pin.component_index, pin.name)] for pin in drivers]
            )
    return circuit, compiled, networks, outputs


def audit_candidate(
    candidate: Circuit,
    connections: tuple[Connection, ...],
    payload: dict[str, Any],
    by_id: dict[int, dict[str, Any]],
    mapping: dict[str, Any],
    *,
    proxy_path: Path,
) -> dict[str, Any]:
    encoded = encode_v15(candidate)
    if decode_v15(encoded) != candidate:
        raise RuntimeError("v15 round trip changed the materialized candidate")
    kind_counts = Counter(component.kind for component in candidate.components)
    if kind_counts[30]:
        raise RuntimeError("illegal native com_add kind 30 appears in materialized candidate")
    reviewed_gate = sum(
        kind_counts[spec.kind] * spec.cost for spec in GATE_SPECS.values()
    ) + kind_counts[12] * 2
    metrics = payload["metrics"]
    if (
        reviewed_gate != int(metrics["gate"])
        or candidate.delay != int(metrics["delay"])
        or candidate.energy != int(metrics["energy"])
    ):
        raise RuntimeError("materialized cost/delay differs from Factory metrics")

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
            raise RuntimeError(f"materialized connectivity failure {field}: {connectivity[field]!r}")
    geometry = audit_sprite_geometry(candidate, DEFAULT_COMPONENT_SPRITE_ROOT)
    if (
        geometry.unsupported_component_kinds
        or geometry.component_overlap_cells
        or geometry.wire_collisions
        or geometry.wire_interior_pin_contacts
    ):
        raise RuntimeError(f"materialized sprite geometry failure: {geometry!r}")

    expected_tri_state = sum(len(node["args"]) // 2 for node in by_id.values() if node["op"] == "BUS")
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

    logical = logical_states(tuple(payload["factory_dag"]["nodes"]))
    proxy_path.parent.mkdir(parents=True, exist_ok=True)
    proxy_path.write_bytes(encode_v15(physical._proxy_for_semantics(candidate)))
    _proxy, compiled, networks, _component_outputs = evaluate_proxy(proxy_path)
    label_index = mapping["label_index"]
    node_pin_refs = dict(mapping["node_pin_refs"])
    cin_node = next(
        node_id
        for node_id, node in by_id.items()
        if node["op"] == "INPUT" and node["label"] == "cin"
    )
    node_pin_refs[cin_node] = (label_index["Carry in"], "in")
    node_mismatches = []
    for node_id, state in logical.items():
        component_index, pin_name = node_pin_refs[node_id]
        network = compiled.pin_network[(component_index, pin_name)]
        signal = networks[network]
        fields = []
        if signal.bits[0] != state["bits"]:
            fields.append("bits")
        if signal.driven != state["driven"]:
            fields.append("driven")
        if signal.conflict != state["conflict"]:
            fields.append("conflict")
        if signal.depth != state["depth"]:
            fields.append("depth")
        if fields:
            node_mismatches.append({"node": node_id, "fields": fields})
    if node_mismatches:
        raise RuntimeError(f"physical node replay mismatch: {node_mismatches[:4]!r}")

    bus_stats = []
    seen_bus_networks = set()
    for node_id, node in by_id.items():
        if node["op"] != "BUS":
            continue
        switches = mapping["bus_switches"][node_id]
        output_networks = {compiled.pin_network[(switch, "out")] for switch in switches}
        if len(output_networks) != 1:
            raise RuntimeError(f"BUS {node_id} Switch outputs are physically split")
        network = next(iter(output_networks))
        if network in seen_bus_networks:
            raise RuntimeError(f"BUS {node_id} aliases another BUS network")
        seen_bus_networks.add(network)
        pins = compiled.network_pins[network]
        tri_drivers = [pin for pin in pins if pin.direction == T]
        ordinary_drivers = [pin for pin in pins if pin.direction == O]
        if len(tri_drivers) != len(switches) or ordinary_drivers:
            raise RuntimeError(f"BUS {node_id} physical driver set differs from Factory DAG")
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
    if any(item["conflict_assignment_count"] for item in bus_stats):
        raise RuntimeError("materialized BUS has conflicting drivers")

    merger = mapping["merger"]
    output_nodes = tuple(int(value) for value in payload["factory_dag"]["outputs"])
    output_arrivals = []
    for bit, node_id in enumerate(output_nodes[:8]):
        signal = networks[compiled.pin_network[(merger, f"in{bit}")]]
        if signal.bits[0] != logical[node_id]["bits"] or signal.driven != ALL:
            raise RuntimeError(f"sum bit {bit} differs from reviewed output")
        output_arrivals.append(signal.depth)
    carry_sink = label_index["Carry out"]
    carry_signal = networks[compiled.pin_network[(carry_sink, "out")]]
    output_arrivals.append(carry_signal.depth)
    if output_arrivals != list(metrics["output_arrivals"]):
        raise RuntimeError("physical output arrival vector differs from Factory DAG")

    sum_sink = label_index["Output"]
    sum_signal = networks[compiled.pin_network[(sum_sink, "out")]]
    variables = tuple(_variable(index) for index in range(17))
    carry = variables[16]
    expected_sum = []
    for left, right in zip(variables[:8], variables[8:16]):
        propagate = left ^ right
        expected_sum.append(propagate ^ carry)
        carry = (left & right) | (propagate & carry)
    if sum_signal.bits[:8] != tuple(expected_sum) or carry_signal.bits[0] != carry:
        raise RuntimeError("materialized candidate fails complete Byte Adder truth table")
    if sum_signal.driven != ALL or carry_signal.driven != ALL:
        raise RuntimeError("materialized primary output is high-impedance")
    packed_conflicts = sum(signal.conflict.bit_count() for signal in networks.values())
    if packed_conflicts:
        raise RuntimeError(f"materialized candidate has {packed_conflicts} packed conflicts")
    global_depth = max(signal.depth for signal in networks.values())
    if global_depth != int(metrics["delay"]):
        raise RuntimeError(f"materialized recursive depth is {global_depth}, expected {metrics['delay']}")

    return {
        "candidate_bytes": encoded,
        "candidate_sha256": sha256(encoded).hexdigest(),
        "component_count": len(candidate.components),
        "wire_count": len(candidate.wires),
        "component_kind_counts": {str(key): value for key, value in sorted(kind_counts.items())},
        "reviewed_gate": reviewed_gate,
        "native_com_add_count": kind_counts[30],
        "connectivity": {
            "unconnected_pin_count": connectivity["unconnected_pin_count"],
            "unsafe_multi_driver_network_count": connectivity["multi_driver_network_count"],
            "undriven_network_count": connectivity["undriven_network_count"],
            "sinkless_network_count": connectivity["sinkless_network_count"],
            "width_mismatch_network_count": connectivity["width_mismatch_network_count"],
            "cycle_component_count": connectivity["cycle_component_count"],
            "topology_only_unit_depth": connectivity["unit_logic_depth"],
            "topology_depth_note": "non-Z-aware graph depth; packed tri-state depth is authoritative",
        },
        "geometry": {
            "unsupported_component_kinds": list(geometry.unsupported_component_kinds),
            "component_overlap_cells": len(geometry.component_overlap_cells),
            "wire_collisions": len(geometry.wire_collisions),
            "wire_interior_pin_contacts": len(geometry.wire_interior_pin_contacts),
        },
        "resolved_networks": resolved,
        "semantic": {
            "vectors_checked": ASSIGNMENTS,
            "node_replay_count": len(logical),
            "node_replay_mismatch_count": len(node_mismatches),
            "bus_nodes": bus_stats,
            "packed_conflict_cases": packed_conflicts,
            "output_arrivals": output_arrivals,
            "global_depth": global_depth,
            "sum_depth": sum_signal.depth,
            "carry_depth": carry_signal.depth,
            "sum_correct": True,
            "carry_correct": True,
        },
        "v15_round_trip_verified": True,
    }


def materialize(
    dag_source: Path,
    *,
    builder_path: Path | None = None,
    builder_witness: Path | None = None,
    output_dir: Path | None = None,
    deploy: bool = False,
    repository_candidate: Path = DEFAULT_REPOSITORY_CANDIDATE,
    formal_save: Path = DEFAULT_FORMAL_SAVE,
) -> dict[str, Any]:
    dag_source = _rooted(dag_source)
    if builder_path is not None:
        builder_path = _rooted(builder_path)
    if builder_witness is not None:
        builder_witness = _rooted(builder_witness)
    if output_dir is None:
        source_tag = sha256(dag_source.read_bytes()).hexdigest()[:8]
        output_dir = HERE / "materialized" / f"{dag_source.stem}-{source_tag}"
    else:
        output_dir = _rooted(output_dir)
    repository_candidate = _rooted(repository_candidate)
    formal_save = _rooted(formal_save)

    payload, by_id, source_review = review_dag(
        dag_source,
        builder_path=builder_path,
        builder_witness=builder_witness,
    )
    candidate, connections, mapping = build_physical(payload, by_id)
    proxy_path = output_dir / "semantic_proxy.circuit.data"
    audit = audit_candidate(
        candidate,
        connections,
        payload,
        by_id,
        mapping,
        proxy_path=proxy_path,
    )
    encoded = audit.pop("candidate_bytes")
    research_candidate = output_dir / "candidate" / "circuit.data"
    research_candidate.parent.mkdir(parents=True, exist_ok=True)
    research_candidate.write_bytes(encoded)
    if decode_v15(research_candidate.read_bytes()) != candidate:
        raise RuntimeError("research candidate changed after write")

    deployment = {
        "requested": deploy,
        "repository_candidate": str(repository_candidate).replace("\\", "/"),
        "repository_candidate_written": False,
        "formal_save": str(formal_save).replace("\\", "/"),
        "formal_save_written": False,
        "backup_created": False,
        "game_started": False,
    }
    if deploy:
        _assert_game_not_running()
        repository_candidate.parent.mkdir(parents=True, exist_ok=True)
        repository_candidate.write_bytes(encoded)
        if repository_candidate.read_bytes() != encoded:
            raise RuntimeError("repository candidate differs after deployment")
        if not formal_save.parent.is_dir():
            raise RuntimeError(f"formal Byte Adder save directory is missing: {formal_save.parent}")
        formal_save.write_bytes(encoded)
        _assert_game_not_running()
        if formal_save.read_bytes() != encoded or decode_v15(formal_save.read_bytes()) != candidate:
            raise RuntimeError("formal Byte Adder save differs after deployment")
        deployment["repository_candidate_written"] = True
        deployment["formal_save_written"] = True

    certificate = {
        "schema": "turing-complete-byte-adder-factory-dag-materialization-v1",
        "source_review": source_review,
        "serialized_score": {
            "gate": int(payload["metrics"]["gate"]),
            "delay": int(payload["metrics"]["delay"]),
            "energy": int(payload["metrics"]["energy"]),
        },
        **audit,
        "research_candidate": str(research_candidate).replace("\\", "/"),
        "research_candidate_matches": True,
        "deployment": deployment,
    }
    certificate_path = output_dir / "machine_certificate.json"
    certificate_path.write_text(
        json.dumps(certificate, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(certificate, ensure_ascii=False, indent=2))
    return certificate


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="将完整 Byte Adder Factory DAG JSON 物化为当前 v15 电路；默认不部署。"
    )
    parser.add_argument("dag_json", type=Path, help="包含 factory_dag 的完整 JSON")
    parser.add_argument("--builder", type=Path, help="可选 build() 生成器，用于逐对象重放核对")
    parser.add_argument(
        "--builder-witness",
        type=Path,
        help="可选 witness 路径；传入时调用 build(witness_path)，且必须同时使用 --builder",
    )
    parser.add_argument("--output-dir", type=Path, help="研究输出目录；默认按源文件名和哈希生成")
    parser.add_argument(
        "--deploy",
        action="store_true",
        help="显式直接覆盖仓库候选和正式存档；不创建备份",
    )
    parser.add_argument(
        "--repository-candidate",
        type=Path,
        default=DEFAULT_REPOSITORY_CANDIDATE,
        help="--deploy 时覆盖的仓库候选路径",
    )
    parser.add_argument(
        "--formal-save",
        type=Path,
        default=DEFAULT_FORMAL_SAVE,
        help="--deploy 时覆盖的正式存档路径",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    materialize(
        args.dag_json,
        builder_path=args.builder,
        builder_witness=args.builder_witness,
        output_dir=args.output_dir,
        deploy=args.deploy,
        repository_candidate=args.repository_candidate,
        formal_save=args.formal_save,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
