"""Materialize the strict physical 10/3 FullAdder witness below .research.

This builder is deliberately non-deploying.  It derives a standalone v15
candidate from the already audited 7/4 research copy only to preserve the
five immutable FullAdder ports.  It never reads or writes levels.txt, never
writes the formal save, and never launches Turing Complete.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import asdict, replace
from hashlib import sha256
import json
from pathlib import Path
from typing import Iterable

from tc_save_lab.analysis import wire_points
from tc_save_lab.builder import stable_permanent_id, wire_from_vertices
from tc_save_lab.codec import decode_v15, encode_v15
from tc_save_lab.model import Circuit, Component, Point
from tc_save_lab.pins import positioned_pins
from tc_save_lab.sprite_geometry import DEFAULT_COMPONENT_SPRITE_ROOT, audit_sprite_geometry


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = HERE / "full_adder_10_3"
BASELINE = (
    ROOT
    / ".research"
    / "byte_adder_builder_verify_restart"
    / "full_adder_7_4_intake"
    / "formal_9f83306a_r1"
    / "candidate.rebuilt.data"
)
BASELINE_SHA256 = "9f83306a02ed064f7eb834b874daf786202651e73beb8d0f7ce3050f221572b2"
EXACT_WITNESS = (
    ROOT
    / ".research"
    / "byte_adder_component_byproduct_catalog"
    / "exact_pretarget_physical_cases"
    / "fa_g10_d3_strict_p8_n0.json"
)
SEED_IDENTITY = "full-adder:strict-physical:10/3:v1"


GATE_KIND = {"AND": 4, "NAND": 6, "OR": 7}
GATE_COST = {"AND": 1, "NAND": 1, "OR": 1, "BUS": 4}
GATE_DELAY = {"AND": 1, "NAND": 1, "OR": 1, "BUS": 1}
EXPECTED_KIND_COUNTS = {4: 1, 6: 4, 7: 1, 12: 2, 60: 3, 69: 2}


def _digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _write_json(path: Path, payload: object) -> str:
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    path.write_bytes(encoded)
    return sha256(encoded).hexdigest()


def _node(
    node_id: int,
    op: str,
    args: Iterable[int],
    *,
    arrival: int,
    label: str = "",
    may_z: bool = False,
    **extra: object,
) -> dict[str, object]:
    item: dict[str, object] = {
        "id": node_id,
        "op": op,
        "args": list(args),
        "cost": 0 if op == "INPUT" else GATE_COST[op],
        "step_delay": 0 if op == "INPUT" else GATE_DELAY[op],
        "arrival": arrival,
        "may_z": may_z,
        "label": label,
    }
    item.update(extra)
    return item


def build_factory_payload() -> dict[str, object]:
    nodes = [
        _node(0, "INPUT", (), arrival=0, label="Input 0", truth_mask_hex="aa"),
        _node(1, "INPUT", (), arrival=0, label="Input 1", truth_mask_hex="cc"),
        _node(2, "INPUT", (), arrival=0, label="Input 2", truth_mask_hex="f0"),
        _node(
            3,
            "OR",
            (0, 2),
            arrival=1,
            label="V=A|C",
            truth_mask_hex="fa",
            phase="positive AC generate-or-propagate envelope",
            byproduct="V",
        ),
        _node(
            4,
            "NAND",
            (0, 2),
            arrival=1,
            label="N=~(A&C)",
            truth_mask_hex="5f",
            phase="negative AC generate",
            byproduct="N",
        ),
        _node(
            5,
            "NAND",
            (3, 4),
            arrival=2,
            label="Q=~(V&N)=XNOR(A,C)",
            truth_mask_hex="a5",
            phase="even parity selector",
            byproduct="Q",
        ),
        _node(
            6,
            "AND",
            (3, 4),
            arrival=2,
            label="P=V&N=XOR(A,C)",
            truth_mask_hex="5a",
            phase="odd parity selector",
            byproduct="P",
        ),
        _node(
            7,
            "NAND",
            (1, 3),
            arrival=2,
            label="R=~(B&V)",
            truth_mask_hex="37",
            phase="negative B/V term",
            byproduct="R",
        ),
        _node(
            8,
            "BUS",
            (5, 1, 6, 7),
            arrival=3,
            label="SUM",
            may_z=True,
            truth_mask_hex="96",
            driven_mask_hex="ff",
            conflict_mask_hex="00",
            resolved_network="sum_bus",
            owner="sum_bus",
            drivers=[
                {
                    "enable": 5,
                    "data": 1,
                    "owner": "sum_bus",
                    "partial_driver": "SQ",
                    "driven_mask_hex": "a5",
                    "one_mask_hex": "84",
                    "z_mask_hex": "5a",
                },
                {
                    "enable": 6,
                    "data": 7,
                    "owner": "sum_bus",
                    "partial_driver": "SP",
                    "driven_mask_hex": "5a",
                    "one_mask_hex": "12",
                    "z_mask_hex": "a5",
                },
            ],
            phase="Q/P complementary resolved Sum",
            byproduct="SUM",
        ),
        _node(
            9,
            "NAND",
            (4, 7),
            arrival=3,
            label="CARRY=~(N&R)",
            truth_mask_hex="e8",
            phase="positive majority",
            byproduct="CARRY",
        ),
    ]
    outputs = [8, 9]
    hash_payload = {
        "outputs": outputs,
        "nodes": nodes,
        "live_node_count": len(nodes),
    }
    dag_hash = sha256(_canonical(hash_payload)).hexdigest()
    return {
        "schema": "full-adder-strict-physical-factory-dag-v1",
        "status": "sat",
        "family": "Complementary Q/P Switch-resolved Sum with NAND majority Carry",
        "formula": {
            "inputs": {"A": 0, "B": 1, "C": 2},
            "V": "OR(A,C)",
            "N": "NAND(A,C)",
            "Q": "NAND(V,N)",
            "P": "AND(V,N)",
            "SQ": "SWITCH(enable=Q,data=B)",
            "R": "NAND(B,V)",
            "SP": "SWITCH(enable=P,data=R)",
            "SUM": "BUS(SQ,SP)",
            "CARRY": "NAND(N,R)",
        },
        "metrics": {
            "gate": 10,
            "delay": 3,
            "energy": 30,
            "paid_physical_components": 8,
            "ordinary_gate_components": 6,
            "switch_components": 2,
            "normalizer_components": 0,
            "output_arrivals": {"Sum": 3, "Carry": 3},
        },
        "semantic": {
            "assignments": 8,
            "input_case_bit_order": ["Input 0", "Input 1", "Input 2"],
            "sum_truth_mask_hex": "96",
            "carry_truth_mask_hex": "e8",
            "sum_driven_mask_hex": "ff",
            "sum_conflict_mask_hex": "00",
            "q_or_p_complete_mask_hex": "ff",
            "q_and_p_overlap_mask_hex": "00",
        },
        "physical": {
            "resolved_bus_count": 1,
            "resolved_bus_owner": "sum_bus",
            "tri_state_driver_count": 2,
            "driver_sets_form_wire_net_partition": True,
            "normalizer_count": 0,
            "primary_outputs_fully_driven": True,
        },
        "factory_dag": {
            "outputs": outputs,
            "nodes": nodes,
            "live_node_count": len(nodes),
            "sha256": dag_hash,
            "sha256_form": "sorted-compact-ascii",
        },
    }


def _pin(components: tuple[Component, ...], index: int, name: str) -> Point:
    matches = [
        pin.position
        for pin in positioned_pins(components[index], index)
        if pin.name == name
    ]
    if len(matches) != 1:
        raise RuntimeError(f"component {index} has no unique pin {name!r}")
    return matches[0]


def _compress(vertices: list[Point]) -> tuple[Point, ...]:
    compact: list[Point] = []
    for point in vertices:
        if not compact or compact[-1] != point:
            compact.append(point)
    changed = True
    while changed and len(compact) >= 3:
        changed = False
        reduced = [compact[0]]
        for index in range(1, len(compact) - 1):
            left, point, right = reduced[-1], compact[index], compact[index + 1]
            d0 = (point[0] - left[0], point[1] - left[1])
            d1 = (right[0] - point[0], right[1] - point[1])
            if d0[0] * d1[1] == d0[1] * d1[0] and (d0[0] == 0) == (d1[0] == 0):
                changed = True
                continue
            reduced.append(point)
        reduced.append(compact[-1])
        compact = reduced
    return tuple(compact)


def _pin_trunks(components: tuple[Component, ...]) -> tuple[dict[Point, int], dict[Point, Point]]:
    trunks: dict[Point, int] = {}
    escapes: dict[Point, Point] = {}
    used: set[int] = set()
    port_trunks = {
        "Input 0": -12,
        "Input 1": -11,
        "Input 2": -10,
        "Sum": 10,
        "Carry": 9,
    }
    for component_index, component in enumerate(components):
        pins = tuple(positioned_pins(component, component_index))
        if component.user_label in port_trunks:
            if len(pins) != 1:
                raise RuntimeError("reviewed FullAdder port no longer has one pin")
            trunks[pins[0].position] = port_trunks[component.user_label]
            escapes[pins[0].position] = pins[0].position
            continue
        left = sorted(
            (pin for pin in pins if pin.position[0] < component.position[0]),
            key=lambda pin: (pin.position[1], pin.name),
        )
        right = sorted(
            (pin for pin in pins if pin.position[0] > component.position[0]),
            key=lambda pin: (pin.position[1], pin.name),
        )
        center = sorted(
            (pin for pin in pins if pin.position[0] == component.position[0]),
            key=lambda pin: (pin.position[1], pin.name),
        )
        for rank, pin in enumerate(left):
            trunks[pin.position] = component.position[0] - 3 - rank
            escapes[pin.position] = pin.position
        for rank, pin in enumerate(right):
            trunks[pin.position] = component.position[0] + 4 + rank
            escapes[pin.position] = pin.position
        for rank, pin in enumerate(center):
            trunks[pin.position] = component.position[0] - 4 - rank
            escapes[pin.position] = (pin.position[0], pin.position[1] + 1)
    for point, trunk in trunks.items():
        if trunk in used:
            raise RuntimeError(f"routing trunk collision at x={trunk} for pin {point}")
        used.add(trunk)
    return trunks, escapes


def _route(
    components: tuple[Component, ...],
    networks: dict[str, list[Point]],
) -> tuple[tuple[object, ...], list[dict[str, object]]]:
    trunks, escapes = _pin_trunks(components)
    minimum_y = min(
        pin.position[1]
        for index, component in enumerate(components)
        for pin in positioned_pins(component, index)
    )
    lanes = {
        name: minimum_y - 24 - ordinal * 3
        for ordinal, name in enumerate(sorted(networks))
    }
    wires = []
    routes: list[dict[str, object]] = []
    for name in sorted(networks):
        points = networks[name]
        if len(points) < 2:
            raise RuntimeError(f"logical network {name!r} has no receiver")
        source = points[0]
        for sink in points[1:]:
            lane = lanes[name]
            source_escape = escapes[source]
            sink_escape = escapes[sink]
            vertices = _compress(
                [
                    source,
                    source_escape,
                    (trunks[source], source_escape[1]),
                    (trunks[source], lane),
                    (trunks[sink], lane),
                    (trunks[sink], sink_escape[1]),
                    sink_escape,
                    sink,
                ]
            )
            wire = wire_from_vertices(vertices)
            wires.append(wire)
            routes.append(
                {
                    "network": name,
                    "source": list(source),
                    "sink": list(sink),
                    "vertices": [list(point) for point in vertices],
                }
            )
    edge_owner: dict[tuple[Point, Point], str] = {}
    for wire, route in zip(wires, routes, strict=True):
        points = wire_points(wire)
        for left, right in zip(points, points[1:]):
            edge = (left, right) if left <= right else (right, left)
            previous = edge_owner.get(edge)
            if previous is not None and previous != route["network"]:
                raise RuntimeError(f"foreign network edge overlap on {edge}")
            edge_owner.setdefault(edge, str(route["network"]))
    return tuple(wires), routes


def materialize(payload: dict[str, object]) -> tuple[Circuit, dict[str, object], list[dict[str, object]]]:
    if _digest(BASELINE) != BASELINE_SHA256:
        raise RuntimeError("audited 7/4 research baseline hash changed")
    baseline = decode_v15(BASELINE.read_bytes())
    ports = tuple(component for component in baseline.components if component.immutable)
    labels = {component.user_label for component in ports}
    if labels != {"Input 0", "Input 1", "Input 2", "Sum", "Carry"}:
        raise RuntimeError(f"FullAdder port scaffold changed: {labels!r}")
    label_index = {component.user_label: index for index, component in enumerate(ports)}
    dag = payload["factory_dag"]
    dag_hash = str(dag["sha256"])
    identity = f"{SEED_IDENTITY}:{dag_hash}"
    mutables: list[Component] = []
    node_components: dict[int, int] = {}
    bus_switches: dict[int, tuple[int, ...]] = {}

    def append(component: Component) -> int:
        index = len(ports) + len(mutables)
        mutables.append(component)
        return index

    for node in dag["nodes"]:
        node_id = int(node["id"])
        op = str(node["op"])
        if op in GATE_KIND:
            node_components[node_id] = append(
                Component(
                    GATE_KIND[op],
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

    rows = tuple(index * 14 - ((len(mutables) - 1) * 14) // 2 for index in range(len(mutables)))
    placed = tuple(
        replace(component, position=(48 + slot * 40, rows[slot]))
        for slot, component in enumerate(mutables)
    )
    components = tuple([*ports, *placed])
    if len({component.permanent_id for component in components}) != len(components):
        raise RuntimeError("duplicate permanent IDs in materialized candidate")

    node_sources: dict[int, list[tuple[int, str]]] = {}
    input_label_by_id = {
        int(node["id"]): str(node["label"])
        for node in dag["nodes"]
        if node["op"] == "INPUT"
    }
    for node_id, label in input_label_by_id.items():
        node_sources[node_id] = [(label_index[label], "value")]
    for node_id, component_index in node_components.items():
        node_sources[node_id] = [(component_index, "out")]
    for node_id, switches in bus_switches.items():
        node_sources[node_id] = [(index, "out") for index in switches]

    members: dict[str, list[Point]] = defaultdict(list)
    pin_records: dict[str, list[dict[str, object]]] = defaultdict(list)

    def add(node_id: int, component_index: int, pin_name: str, role: str) -> None:
        network = f"node:{node_id}"
        point = _pin(components, component_index, pin_name)
        if point not in members[network]:
            members[network].append(point)
            pin = next(
                pin
                for pin in positioned_pins(components[component_index], component_index)
                if pin.name == pin_name
            )
            pin_records[network].append(
                {
                    "component_index": component_index,
                    "component_permanent_id": components[component_index].permanent_id,
                    "component_kind": components[component_index].kind,
                    "component_label": components[component_index].user_label,
                    "pin": pin_name,
                    "pin_direction": pin.direction,
                    "position": list(point),
                    "role": role,
                }
            )

    for node_id, sources in node_sources.items():
        for component_index, pin_name in sources:
            add(node_id, component_index, pin_name, "driver")
    for node in dag["nodes"]:
        node_id = int(node["id"])
        op = str(node["op"])
        args = [int(value) for value in node.get("args", ())]
        if op in GATE_KIND:
            component_index = node_components[node_id]
            for pin_name, argument in zip(("in0", "in1"), args, strict=True):
                add(argument, component_index, pin_name, "receiver")
        elif op == "BUS":
            for driver, switch in enumerate(bus_switches[node_id]):
                add(args[driver * 2], switch, "enable", "receiver")
                add(args[driver * 2 + 1], switch, "in", "receiver")
    outputs = [int(value) for value in dag["outputs"]]
    add(outputs[0], label_index["Sum"], "value", "receiver")
    add(outputs[1], label_index["Carry"], "value", "receiver")

    wires, routes = _route(components, dict(members))
    candidate = replace(
        baseline,
        custom_id=0,
        hub_id=0,
        design=b"",
        description="Research-only strict physical FullAdder 10/3 witness",
        gate=10,
        delay=3,
        components=components,
        wires=wires,
    )
    mapping = {
        "schema": "full-adder-10-3-real-pin-mapping-v1",
        "factory_dag_sha256": dag_hash,
        "candidate_component_count": len(components),
        "candidate_wire_count": len(wires),
        "ports": label_index,
        "node_components": {str(key): value for key, value in sorted(node_components.items())},
        "bus_switches": {
            str(key): list(value) for key, value in sorted(bus_switches.items())
        },
        "networks": [
            {
                "label": network,
                "node_id": int(network.split(":", 1)[1]),
                "pins": pin_records[network],
            }
            for network in sorted(pin_records, key=lambda value: int(value.split(":", 1)[1]))
        ],
        "routes": routes,
    }
    return candidate, mapping, routes


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    payload = build_factory_payload()
    factory_path = OUT / "factory_dag.json"
    factory_sha = _write_json(factory_path, payload)
    candidate, mapping, _routes = materialize(payload)
    candidate_path = OUT / "candidate.circuit.data"
    candidate_bytes = encode_v15(candidate)
    candidate_path.write_bytes(candidate_bytes)
    if encode_v15(decode_v15(candidate_bytes)) != candidate_bytes:
        raise RuntimeError("candidate v15 roundtrip is not byte-identical")
    decoded_sha = _write_json(OUT / "candidate.decoded.json", candidate.to_dict())
    mapping_sha = _write_json(OUT / "pin_mapping.json", mapping)

    kind_counts = dict(sorted(Counter(component.kind for component in candidate.components).items()))
    if kind_counts != EXPECTED_KIND_COUNTS:
        raise RuntimeError(f"unexpected materialized kind counts {kind_counts!r}")
    geometry = audit_sprite_geometry(candidate, DEFAULT_COMPONENT_SPRITE_ROOT)
    if (
        geometry.unsupported_component_kinds
        or geometry.component_overlap_cells
        or geometry.wire_collisions
        or geometry.wire_interior_pin_contacts
    ):
        raise RuntimeError(f"materialized sprite geometry failure: {geometry!r}")

    seven_audit = BASELINE.with_name("audit.json")
    manifest = {
        "schema": "full-adder-10-3-materialization-manifest-v1",
        "status": "materialized_pending_independent_audit",
        "scope": {
            "research_only": True,
            "formal_save_modified": False,
            "levels_txt_modified": False,
            "repository_candidate_modified": False,
            "game_started": False,
        },
        "artifacts": {
            "factory_dag": {"path": str(factory_path), "sha256": factory_sha},
            "candidate": {
                "path": str(candidate_path),
                "bytes": len(candidate_bytes),
                "sha256": sha256(candidate_bytes).hexdigest(),
            },
            "candidate_decoded": {
                "path": str(OUT / "candidate.decoded.json"),
                "sha256": decoded_sha,
            },
            "real_pin_mapping": {
                "path": str(OUT / "pin_mapping.json"),
                "sha256": mapping_sha,
            },
            "exact_solver_witness": {
                "path": str(EXACT_WITNESS),
                "sha256": _digest(EXACT_WITNESS),
            },
        },
        "score": {"gate": 10, "delay": 3, "energy": 30},
        "structure": {
            "component_kind_counts": {str(key): value for key, value in kind_counts.items()},
            "paid_component_count": 8,
            "ordinary_gate_count": 6,
            "switch_count": 2,
            "normalizer_count": 0,
            "resolved_sum_bus_owner": "sum_bus",
        },
        "byproduct_and_phase_contract": [
            {
                "node": node["id"],
                "name": node.get("byproduct", node["label"]),
                "truth_mask_hex": node.get("truth_mask_hex"),
                "arrival": node["arrival"],
                "phase": node.get("phase"),
                "owner": node.get("owner", f"node:{node['id']}"),
                "partial_drivers": node.get("drivers", []),
            }
            for node in payload["factory_dag"]["nodes"]
        ],
        "correspondence_to_7_4": {
            "candidate_path": str(BASELINE),
            "candidate_sha256": BASELINE_SHA256,
            "audit_path": str(seven_audit),
            "audit_sha256": _digest(seven_audit),
            "shared_port_truth": {"Sum": "96", "Carry": "e8"},
            "seven_four": {
                "score": [7, 4],
                "ordinary_gate_components": 7,
                "switch_components": 0,
                "output_arrivals": {"Sum": 4, "Carry": 4},
                "output_driver_style": "single-driver ordinary outputs",
            },
            "ten_three": {
                "score": [10, 3],
                "ordinary_gate_components": 6,
                "switch_components": 2,
                "output_arrivals": {"Sum": 3, "Carry": 3},
                "output_driver_style": "two complementary partial drivers for Sum; single NAND driver for Carry",
            },
            "pareto_relation": "nondominated: 7<10 while 4>3",
        },
        "materializer": {
            "path": str(Path(__file__).resolve()),
            "sha256": _digest(Path(__file__).resolve()),
        },
        "geometry": asdict(geometry),
    }
    manifest_sha = _write_json(OUT / "materialization_manifest.json", manifest)
    print(json.dumps({
        "factory_dag": str(factory_path),
        "factory_dag_sha256": factory_sha,
        "candidate": str(candidate_path),
        "candidate_sha256": sha256(candidate_bytes).hexdigest(),
        "pin_mapping": str(OUT / "pin_mapping.json"),
        "pin_mapping_sha256": mapping_sha,
        "manifest": str(OUT / "materialization_manifest.json"),
        "manifest_sha256": manifest_sha,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
