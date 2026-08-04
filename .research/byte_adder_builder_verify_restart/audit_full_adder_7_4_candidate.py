"""Fail-closed physical audit for the accepted-looking 7/4 Full Adder artifact.

This tool is deliberately non-deploying.  It may read any v15 Full Adder
candidate, but it only writes derived evidence below the isolated research
intake directory.  It never writes ``levels.txt``, the formal save, or the
repository candidate tree, and it never starts Turing Complete.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict, deque
from dataclasses import asdict
from hashlib import sha256
from itertools import product
import json
import os
from pathlib import Path
import subprocess
from typing import Iterable

from tc_save_lab.analysis import analyze_circuit, wire_points
from tc_save_lab.codec import decode_v15, encode_v15
from tc_save_lab.model import Circuit
from tc_save_lab.pins import I, O, T, positioned_pins
from tc_save_lab.simulate import simulate_combinational
from tc_save_lab.sprite_geometry import (
    DEFAULT_COMPONENT_SPRITE_ROOT,
    SPRITE_NAME_BY_COMPONENT_KIND,
    audit_sprite_geometry,
)


SCHEMA = "full-adder-7-4-physical-candidate-audit-v1"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
INTAKE_ROOT = (
    PROJECT_ROOT
    / ".research"
    / "byte_adder_builder_verify_restart"
    / "full_adder_7_4_intake"
)
FORMAL_SAVE = (
    Path.home()
    / "AppData"
    / "Roaming"
    / "Turing Complete"
    / "schematics"
    / "full_adder"
    / "Default"
    / "circuit.data"
)

# This is the independently synthesized primitive artifact currently present
# in the formal Full Adder save: two AND, one OR, and four NOR gates.  Keeping
# this audit exact prevents a kind-15 self-reference or a header-only 7/4 claim
# from slipping through the preparation gate.
EXPECTED_KIND_COUNTS = {4: 2, 7: 1, 9: 4, 60: 3, 69: 2}
PRIMITIVE_COST_DELAY = {
    3: (1, 1),   # NOT
    4: (1, 1),   # AND
    6: (1, 1),   # NAND
    7: (1, 1),   # OR
    9: (1, 1),   # NOR
    10: (3, 2),  # XOR
    11: (3, 2),  # XNOR
    12: (2, 1),  # Switch (not expected in this exact artifact)
}
SOURCE_KIND = 60
SINK_KIND = 69
EXPECTED_INPUT_LABELS = ("Input 0", "Input 1", "Input 2")
EXPECTED_OUTPUT_LABELS = ("Sum", "Carry")


class AuditError(RuntimeError):
    """A candidate failed one of the fail-closed acceptance checks."""


class _UnionFind:
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


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def _sha256_bytes(payload: bytes) -> str:
    return sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _assert_game_not_running() -> None:
    """Refuse to audit while the game is running; never launch it."""

    if os.name != "nt":
        return
    creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    completed = subprocess.run(
        [
            "tasklist",
            "/FI",
            "IMAGENAME eq Turing Complete.exe",
            "/FO",
            "CSV",
            "/NH",
        ],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        errors="replace",
        creationflags=creation_flags,
    )
    if '"turing complete.exe"' in completed.stdout.lower():
        raise AuditError("Turing Complete is running; refusing the offline audit")


def _network_model(circuit: Circuit) -> dict[str, object]:
    """Reconstruct endpoint-connected nets and weighted primitive arrivals."""

    _require(bool(circuit.wires), "candidate has no wires")
    union_find = _UnionFind(len(circuit.wires))
    endpoint_owners: dict[tuple[int, int], list[int]] = defaultdict(list)
    wire_endpoints: list[tuple[tuple[int, int], tuple[int, int]]] = []
    for wire_index, wire in enumerate(circuit.wires):
        points = wire_points(wire)
        endpoints = (points[0], points[-1])
        wire_endpoints.append(endpoints)
        endpoint_owners[endpoints[0]].append(wire_index)
        endpoint_owners[endpoints[1]].append(wire_index)
    for owners in endpoint_owners.values():
        for wire_index in owners[1:]:
            union_find.union(owners[0], wire_index)

    network_by_position: dict[tuple[int, int], int] = {}
    for wire_index, endpoints in enumerate(wire_endpoints):
        network = union_find.find(wire_index)
        for endpoint in endpoints:
            previous = network_by_position.get(endpoint)
            if previous is not None:
                _require(
                    union_find.find(previous) == union_find.find(network),
                    f"endpoint {endpoint!r} resolves to inconsistent networks",
                )
            network_by_position[endpoint] = network

    pins_by_network: dict[int, list[object]] = defaultdict(list)
    component_input_networks: dict[int, list[int]] = defaultdict(list)
    component_output_networks: dict[int, list[int]] = defaultdict(list)
    for component_index, component in enumerate(circuit.components):
        pins = positioned_pins(component, component_index)
        _require(bool(pins), f"component kind {component.kind} has no pin schema")
        for pin in pins:
            network = network_by_position.get(pin.position)
            _require(
                network is not None,
                f"component {component.permanent_id} pin {pin.name} is unconnected",
            )
            network = union_find.find(network)
            pins_by_network[network].append(pin)
            if pin.direction == I:
                component_input_networks[component_index].append(network)
            elif pin.direction in {O, T}:
                component_output_networks[component_index].append(network)

    network_driver: dict[int, int] = {}
    network_receivers: dict[int, list[int]] = defaultdict(list)
    for network, pins in pins_by_network.items():
        drivers = [pin for pin in pins if pin.direction in {O, T}]
        receivers = [pin for pin in pins if pin.direction == I]
        _require(len(drivers) == 1, f"network {network} has {len(drivers)} drivers")
        _require(bool(receivers), f"network {network} has no receiver")
        network_driver[network] = drivers[0].component_index
        network_receivers[network].extend(pin.component_index for pin in receivers)

    dependencies: dict[int, set[int]] = defaultdict(set)
    successors: dict[int, set[int]] = defaultdict(set)
    for receiver, networks in component_input_networks.items():
        for network in networks:
            driver = network_driver[network]
            _require(driver != receiver, f"component {receiver} directly feeds itself")
            dependencies[receiver].add(driver)
            successors[driver].add(receiver)

    gate_indices = {
        index
        for index, component in enumerate(circuit.components)
        if component.kind in PRIMITIVE_COST_DELAY
    }
    source_indices = {
        index
        for index, component in enumerate(circuit.components)
        if component.kind == SOURCE_KIND
    }
    sink_indices = {
        index
        for index, component in enumerate(circuit.components)
        if component.kind == SINK_KIND
    }
    _require(
        gate_indices | source_indices | sink_indices == set(range(len(circuit.components))),
        "candidate contains a non-reviewed component kind",
    )

    arrivals = {index: 0 for index in source_indices}
    pending = set(gate_indices)
    topological_gate_order: list[int] = []
    while pending:
        ready = sorted(
            index
            for index in pending
            if dependencies[index] and dependencies[index] <= arrivals.keys()
        )
        _require(bool(ready), "primitive dependency graph is cyclic or source-less")
        for index in ready:
            component = circuit.components[index]
            primitive_delay = PRIMITIVE_COST_DELAY[component.kind][1]
            arrivals[index] = max(arrivals[parent] for parent in dependencies[index]) + primitive_delay
            topological_gate_order.append(index)
            pending.remove(index)

    output_arrivals: dict[str, int] = {}
    for index in sorted(sink_indices):
        component = circuit.components[index]
        _require(
            len(dependencies[index]) == 1,
            f"output {component.user_label!r} does not have one upstream component",
        )
        parent = next(iter(dependencies[index]))
        _require(parent in arrivals, f"output {component.user_label!r} is not driven by logic")
        output_arrivals[component.user_label] = arrivals[parent]

    live_components = set(sink_indices)
    queue = deque(sink_indices)
    while queue:
        receiver = queue.popleft()
        for driver in dependencies.get(receiver, ()):
            if driver not in live_components:
                live_components.add(driver)
                queue.append(driver)
    dead_gates = sorted(gate_indices - live_components)
    _require(not dead_gates, f"candidate contains dead primitive components {dead_gates!r}")

    primitive_gate_cost = sum(
        PRIMITIVE_COST_DELAY[circuit.components[index].kind][0]
        for index in gate_indices
    )
    return {
        "logical_network_count": len(pins_by_network),
        "primitive_gate_cost": primitive_gate_cost,
        "replayed_max_delay": max(output_arrivals.values()),
        "output_arrivals": dict(sorted(output_arrivals.items())),
        "topological_gate_permanent_ids": [
            circuit.components[index].permanent_id for index in topological_gate_order
        ],
        "dead_primitive_count": 0,
        "single_driver_network_count": len(network_driver),
    }


def _truth_protocol(circuit: Circuit) -> list[dict[str, object]]:
    vectors: list[dict[str, object]] = []
    for input0, input1, carry_in in product((0, 1), repeat=3):
        actual = simulate_combinational(
            circuit,
            {
                "Input 0": input0,
                "Input 1": input1,
                "Input 2": carry_in,
            },
        )
        total = input0 + input1 + carry_in
        expected = {"Sum": total & 1, "Carry": (total >> 1) & 1}
        _require(
            actual == expected,
            f"truth mismatch for {(input0, input1, carry_in)!r}: "
            f"actual={actual!r}, expected={expected!r}",
        )
        vectors.append(
            {
                "inputs": [input0, input1, carry_in],
                "actual": actual,
                "expected": expected,
                "pass": True,
            }
        )
    return vectors


def _sprite_hashes(circuit: Circuit, sprite_root: Path) -> dict[str, str]:
    names = {
        SPRITE_NAME_BY_COMPONENT_KIND[component.kind]
        for component in circuit.components
    }
    return {
        name: _sha256_file(sprite_root / name)
        for name in sorted(names)
    }


def verify_candidate(
    source_path: Path,
    source_bytes: bytes,
    *,
    sprite_root: Path = DEFAULT_COMPONENT_SPRITE_ROOT,
) -> tuple[Circuit, dict[str, object]]:
    """Verify a complete exact 7/4 primitive candidate without writing it."""

    _require(bool(source_bytes) and source_bytes[0] == 15, "candidate is not v15")
    circuit = decode_v15(source_bytes)
    _require(encode_v15(circuit) == source_bytes, "v15 decode/encode is not byte-identical")

    rebuilt = Circuit.from_dict(circuit.to_dict())
    rebuilt_bytes = encode_v15(rebuilt)
    _require(rebuilt_bytes == source_bytes, "canonical JSON deterministic rebuild differs")

    _require(
        (circuit.gate, circuit.delay, circuit.energy) == (7, 4, 28),
        f"declared score is not 7/4/28: {(circuit.gate, circuit.delay, circuit.energy)!r}",
    )
    kind_counts = dict(sorted(Counter(component.kind for component in circuit.components).items()))
    _require(kind_counts == EXPECTED_KIND_COUNTS, f"unexpected component kinds: {kind_counts!r}")
    _require(15 not in kind_counts, "candidate recursively contains com_full_adder")
    _require(30 not in kind_counts, "candidate contains native com_add")

    inputs = sorted(
        component.user_label
        for component in circuit.components
        if component.kind == SOURCE_KIND
    )
    outputs = sorted(
        component.user_label
        for component in circuit.components
        if component.kind == SINK_KIND
    )
    _require(inputs == sorted(EXPECTED_INPUT_LABELS), f"unexpected input labels: {inputs!r}")
    _require(outputs == sorted(EXPECTED_OUTPUT_LABELS), f"unexpected output labels: {outputs!r}")
    _require(
        all(
            component.immutable == (component.kind in {SOURCE_KIND, SINK_KIND})
            for component in circuit.components
        ),
        "immutable partition is not exactly the five level ports",
    )

    analysis = analyze_circuit(circuit, format_version=15)
    connectivity = analysis["connectivity"]
    for field in (
        "unsupported_component_kind_counts",
        "unconnected_pin_count",
        "multi_driver_network_count",
        "undriven_network_count",
        "sinkless_network_count",
        "width_mismatch_network_count",
        "cycle_component_count",
    ):
        value = connectivity[field]
        _require(not value, f"connectivity failure {field}={value!r}")

    geometry = audit_sprite_geometry(circuit, sprite_root)
    for field in (
        "unsupported_component_kinds",
        "component_overlap_cells",
        "wire_collisions",
        "wire_interior_pin_contacts",
    ):
        value = getattr(geometry, field)
        _require(not value, f"sprite geometry failure {field}={value!r}")

    network = _network_model(circuit)
    _require(network["primitive_gate_cost"] == 7, "replayed primitive gate cost is not 7")
    _require(network["replayed_max_delay"] == 4, "replayed primitive delay is not 4")
    _require(
        connectivity["unit_logic_depth"] == 4,
        f"connectivity unit depth is not 4: {connectivity['unit_logic_depth']!r}",
    )
    vectors = _truth_protocol(circuit)

    report = {
        "schema": SCHEMA,
        "status": "verified",
        "scope": {
            "game_was_not_started": True,
            "formal_save_was_not_modified": True,
            "levels_was_not_modified": True,
            "repository_candidate_was_not_written": True,
            "deployment_supported": False,
        },
        "source": {
            "path": str(source_path.resolve()),
            "bytes": len(source_bytes),
            "sha256": _sha256_bytes(source_bytes),
            "format_version": source_bytes[0],
        },
        "score": {
            "declared": [circuit.gate, circuit.delay, circuit.energy],
            "replayed": [network["primitive_gate_cost"], network["replayed_max_delay"], 28],
        },
        "structure": {
            "component_count": len(circuit.components),
            "wire_count": len(circuit.wires),
            "component_kind_counts": kind_counts,
            "native_com_full_adder_count": kind_counts.get(15, 0),
            "native_com_add_count": kind_counts.get(30, 0),
            "duplicate_permanent_ids": analysis["duplicate_permanent_ids"],
        },
        "truth_protocol": {
            "vectors": len(vectors),
            "mismatch_count": 0,
            "rows": vectors,
        },
        "timing_and_ownership": network,
        "connectivity": connectivity,
        "geometry": {
            **asdict(geometry),
            "sprite_sha256": _sprite_hashes(circuit, sprite_root),
        },
        "serialization": {
            "v15_roundtrip_byte_identical": True,
            "canonical_json_deterministic_rebuild_byte_identical": True,
            "rebuilt_sha256": _sha256_bytes(rebuilt_bytes),
        },
    }
    return circuit, report


def _assert_isolated_output(output_dir: Path) -> Path:
    root = INTAKE_ROOT.resolve()
    output = output_dir.resolve()
    try:
        output.relative_to(root)
    except ValueError as exc:
        raise AuditError(f"output directory must be below isolated intake root {root}") from exc
    formal_root = FORMAL_SAVE.parents[2].resolve()
    try:
        output.relative_to(formal_root)
    except ValueError:
        pass
    else:  # pragma: no cover - excluded by the intake-root requirement
        raise AuditError("refusing to write below the formal save tree")
    return output


def _write_json(path: Path, payload: object) -> bytes:
    data = (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    path.write_bytes(data)
    return data


def main(argv: Iterable[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "candidate",
        nargs="?",
        type=Path,
        default=FORMAL_SAVE,
        help="v15 Full Adder circuit.data to audit (default: current formal save, read-only)",
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--expected-sha256")
    parser.add_argument("--sprite-root", type=Path, default=DEFAULT_COMPONENT_SPRITE_ROOT)
    args = parser.parse_args(list(argv) if argv is not None else None)

    _assert_game_not_running()
    source_path = args.candidate.resolve()
    source_bytes = source_path.read_bytes()
    if args.expected_sha256:
        _require(
            _sha256_bytes(source_bytes) == args.expected_sha256.lower(),
            "candidate SHA-256 does not match --expected-sha256",
        )
    circuit, report = verify_candidate(
        source_path,
        source_bytes,
        sprite_root=args.sprite_root.resolve(),
    )

    output_dir = _assert_isolated_output(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=False)
    decoded_bytes = _write_json(output_dir / "candidate.decoded.json", circuit.to_dict())
    rebuilt_bytes = encode_v15(Circuit.from_dict(circuit.to_dict()))
    (output_dir / "candidate.rebuilt.data").write_bytes(rebuilt_bytes)
    report["derived_artifacts"] = {
        "candidate_decoded_json": {
            "path": str((output_dir / "candidate.decoded.json").resolve()),
            "sha256": _sha256_bytes(decoded_bytes),
        },
        "candidate_rebuilt_data": {
            "path": str((output_dir / "candidate.rebuilt.data").resolve()),
            "sha256": _sha256_bytes(rebuilt_bytes),
        },
    }
    report_bytes = _write_json(output_dir / "audit.json", report)
    _assert_game_not_running()
    print(
        json.dumps(
            {
                "status": "verified",
                "source_sha256": report["source"]["sha256"],
                "audit": str((output_dir / "audit.json").resolve()),
                "audit_sha256": _sha256_bytes(report_bytes),
                "score": report["score"],
                "truth_vectors": report["truth_protocol"]["vectors"],
                "geometry_zero": True,
                "connectivity_zero": True,
                "formal_save_written": False,
                "levels_written": False,
                "game_started": False,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
