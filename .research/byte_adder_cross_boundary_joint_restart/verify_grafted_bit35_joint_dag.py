"""Independent full-domain verifier for a grafted bit-3:5 Byte Adder DAG.

This verifier does not import the SAT encoder, the 96-row verifier, the graft
builder, or its packed-replay support.  It independently checks the pinned
authority and cut, reconstructs the certificate-to-Factory translation,
audits fixed-shell preservation and physical BUS ownership, and simulates all
131072 ``u8 + u8 + cin`` assignments.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Iterable


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
AUTHORITATIVE_DAG = (
    ROOT / ".research" / "byte_adder_root" / "byte-adder-hybrid-phasefold-g80-d7.json"
)
CUT_AUDIT = HERE / "bit35_joint_cut_audit.json"
GRAFT_SCRIPT = HERE / "graft_bit35_joint_certificate.py"
REPLAY_SUPPORT = ROOT / ".research" / "byte_adder_root" / "graft_abc_mapped_residual.py"
DEFAULT_GRAFTED = HERE / "bit35_joint_g17_grafted_full_dag.json"
DEFAULT_CERTIFICATE = (
    HERE / "bit35_joint_phase_driver_positive_g17_n15_c5d2k3_t1_s1.json"
)
DEFAULT_96_VERIFY = HERE / "bit35_joint_phase_driver_positive_g17_independent_verify.json"
DEFAULT_OUTPUT = HERE / "bit35_joint_g17_grafted_full_independent_verify.json"

AUTHORITATIVE_SHA256 = "71625de2b86ea03127415802dbc68f605ac16d69da6d9e8b3ade35db317ec884"
CUT_AUDIT_SHA256 = "4edbfc5cb3faa412a8c1eaf93925b30a99895b000c83101d63905a2ef9830df7"
TRUTH_DOMAIN_SHA256 = "1c9768429735b2f87bca12bb62dad82624f45a419b80ea6b5470655764c34b60"
ASSIGNMENTS = 1 << 17
ALL = (1 << ASSIGNMENTS) - 1

SOURCE_NAMES = (
    "a3",
    "b3",
    "a4",
    "b4",
    "C3",
    "P5",
    "G3",
    "Q3",
    "P3",
    "G4",
    "Q4",
    "P4",
    "0",
    "1",
)
SOURCE_NODE_IDS = (8, 9, 10, 11, 56, 36, 28, 29, 30, 31, 32, 33, None, None)
TARGET_NAMES = ("S3", "S4", "C5", "T5", "S5")
TARGET_OLD_IDS = {"S3": 83, "S4": 86, "C5": 62, "T5": 63, "S5": 65}
TARGET_DEADLINES = {"S3": 5, "S4": 7, "C5": 4, "T5": 5, "S5": 6}
PRIMARY_OUTPUT_NAMES = ("S0", "S1", "S2", "S3", "S4", "S5", "S6", "S7", "C8")
EXPECTED_PRIMARY_OUTPUTS = (49, 77, 81, 83, 86, 65, 73, 88, 75)
REGION_IDS = {57, 58, 59, 60, 61, 62, 63, 64, 65, 82, 83, 84, 85, 86}
INPUT_LABELS = {
    *{f"a{bit}" for bit in range(8)},
    *{f"b{bit}" for bit in range(8)},
    "cin",
}
GATE_COST = {
    "NOT": 1,
    "AND": 1,
    "OR": 1,
    "NAND": 1,
    "NOR": 1,
    "XOR": 3,
    "XNOR": 3,
}
GATE_DELAY = {
    "NOT": 1,
    "AND": 1,
    "OR": 1,
    "NAND": 1,
    "NOR": 1,
    "XOR": 2,
    "XNOR": 2,
}
FATAL_96_KEYS = (
    "metadata_error_count",
    "structural_invalid_count",
    "gate_bound_violation_count",
    "switch_count_violation_count",
    "xor_count_violation_count",
    "mismatch_count",
    "bus_conflict_count",
    "undriven_output_count",
    "physical_net_partition_violation_count",
    "dead_component_count",
    "timing_violation_count",
    "declared_level_underflow_count",
)


@dataclass(frozen=True)
class PackedState:
    bits: int
    driven: int
    conflict: int
    arrival: int


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: object) -> str:
    return sha256(
        json.dumps(value, ensure_ascii=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def atomic_write(path: Path, payload: dict[str, Any]) -> str:
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(encoded)
    temporary.replace(path)
    return sha256(encoded).hexdigest()


def variable(index: int) -> int:
    if index < 3:
        return int.from_bytes(
            bytes([(0xAA, 0xCC, 0xF0)[index]]) * (ASSIGNMENTS // 8), "little"
        )
    block = 1 << (index - 3)
    data = (bytes(block) + bytes([0xFF]) * block) * (
        ASSIGNMENTS // (16 * block)
    )
    return int.from_bytes(data, "little")


def expected_outputs() -> tuple[int, ...]:
    values = tuple(variable(index) for index in range(17))
    carry = values[16]
    outputs: list[int] = []
    for bit in range(8):
        propagate = values[bit] ^ values[8 + bit]
        outputs.append(propagate ^ carry)
        carry = (values[bit] & values[8 + bit]) | (propagate & carry)
    outputs.append(carry)
    return tuple(outputs)


def reachable(nodes: dict[int, dict[str, Any]], outputs: Iterable[int]) -> set[int]:
    live: set[int] = set()
    pending = list(outputs)
    while pending:
        node_id = int(pending.pop())
        if node_id in live:
            continue
        if node_id not in nodes:
            raise RuntimeError(f"output cone references missing node {node_id}")
        live.add(node_id)
        pending.extend(int(value) for value in nodes[node_id].get("args", ()))
    return live


def evaluate_factory(factory: dict[str, Any]) -> dict[str, Any]:
    ordered = tuple(factory.get("nodes", ()))
    outputs = tuple(int(value) for value in factory.get("outputs", ()))
    states: dict[int, PackedState] = {}
    nodes: dict[int, dict[str, Any]] = {}
    inputs_seen: set[str] = set()
    resolved_seen: set[str] = set()
    bus_ids: list[int] = []
    reviewed_gate = 0
    structural_invalid = 0
    ownership_invalid = 0

    variables = {
        **{f"a{bit}": variable(bit) for bit in range(8)},
        **{f"b{bit}": variable(8 + bit) for bit in range(8)},
        "cin": variable(16),
    }
    for offset, raw in enumerate(ordered):
        node = dict(raw)
        node_id = int(node.get("id", -1))
        if node_id in states:
            raise RuntimeError(f"duplicate Factory node ID {node_id}")
        args_ids = tuple(int(value) for value in node.get("args", ()))
        if any(value not in states for value in args_ids):
            raise RuntimeError(f"Factory node {node_id} at offset {offset} is not topological")
        args = tuple(states[value] for value in args_ids)
        op = str(node.get("op"))

        if op == "INPUT":
            label = str(node.get("label"))
            if label not in variables or label in inputs_seen or args:
                raise RuntimeError(f"bad or duplicate INPUT node {node_id}: {label!r}")
            inputs_seen.add(label)
            state = PackedState(variables[label], ALL, 0, 0)
            expected_cost = expected_delay = 0
            expected_may_z = False
        elif op == "CONST":
            label = str(node.get("label"))
            if label not in {"0", "1"} or args:
                raise RuntimeError(f"bad CONST node {node_id}")
            state = PackedState(ALL if label == "1" else 0, ALL, 0, 0)
            expected_cost = expected_delay = 0
            expected_may_z = False
        elif op == "BUS":
            if not args or len(args) % 2:
                raise RuntimeError(f"BUS node {node_id} has incomplete drivers")
            ones = zeros = driven = conflict = 0
            for index in range(0, len(args), 2):
                enable, data = args[index], args[index + 1]
                active = enable.bits
                ones |= active & data.bits
                zeros |= active & (~data.bits & ALL)
                driven |= active
                conflict |= enable.conflict | data.conflict
            conflict |= ones & zeros
            state = PackedState(
                ones & ALL,
                driven & ALL,
                conflict & ALL,
                max(value.arrival for value in args) + 1,
            )
            expected_cost = len(args_ids)
            expected_delay = 1
            expected_may_z = True
            resolved = str(node.get("resolved_network", ""))
            if resolved not in {f"bus_node_{node_id}", f"bus_{node_id}"}:
                ownership_invalid += 1
            if resolved in resolved_seen:
                ownership_invalid += 1
            resolved_seen.add(resolved)
            expected_drivers = [
                {
                    "enable": args_ids[index],
                    "data": args_ids[index + 1],
                    "owner": resolved,
                }
                for index in range(0, len(args_ids), 2)
            ]
            if node.get("drivers") != expected_drivers:
                ownership_invalid += 1
            bus_ids.append(node_id)
        elif op in GATE_COST:
            arity = 1 if op == "NOT" else 2
            if len(args) != arity:
                raise RuntimeError(f"gate node {node_id} has wrong arity")
            left = args[0].bits
            right = args[1].bits if arity == 2 else 0
            if op == "NOT":
                bits = ~left
            elif op == "AND":
                bits = left & right
            elif op == "OR":
                bits = left | right
            elif op == "NAND":
                bits = ~(left & right)
            elif op == "NOR":
                bits = ~(left | right)
            elif op == "XOR":
                bits = left ^ right
            elif op == "XNOR":
                bits = ~(left ^ right)
            else:  # pragma: no cover
                raise AssertionError(op)
            conflict = 0
            for value in args:
                conflict |= value.conflict
            expected_cost = GATE_COST[op]
            expected_delay = GATE_DELAY[op]
            expected_may_z = False
            state = PackedState(
                bits & ALL,
                ALL,
                conflict & ALL,
                max(value.arrival for value in args) + expected_delay,
            )
        else:
            raise RuntimeError(f"unsupported Factory DAG operation {op!r}")

        if int(node.get("cost", -1)) != expected_cost:
            structural_invalid += 1
        if int(node.get("step_delay", -1)) != expected_delay:
            structural_invalid += 1
        if int(node.get("arrival", -1)) != state.arrival:
            structural_invalid += 1
        if bool(node.get("may_z")) != expected_may_z:
            structural_invalid += 1
        reviewed_gate += expected_cost
        states[node_id] = state
        nodes[node_id] = node

    if inputs_seen != INPUT_LABELS:
        raise RuntimeError(
            f"Factory input contract mismatch: missing={INPUT_LABELS-inputs_seen}, "
            f"extra={inputs_seen-INPUT_LABELS}"
        )
    if len(outputs) != 9 or any(value not in states for value in outputs):
        raise RuntimeError("Factory DAG does not expose nine valid outputs")
    live = reachable(nodes, outputs)
    dead_ids = sorted(set(nodes) - live)
    actual = tuple(states[node_id] for node_id in outputs)
    expected = expected_outputs()
    mismatch_masks = [
        value.bits ^ target for value, target in zip(actual, expected, strict=True)
    ]
    mismatch_union = 0
    conflict_union = 0
    for mask in mismatch_masks:
        mismatch_union |= mask
    for node_id in live:
        conflict_union |= states[node_id].conflict
    z_masks = [(~value.driven) & ALL for value in actual]
    output_digest = sha256(
        b"".join(value.bits.to_bytes(ASSIGNMENTS // 8, "little") for value in actual)
    ).hexdigest()
    semantic = {
        "truth_table_rows": ASSIGNMENTS,
        "mismatch_count_by_output": [mask.bit_count() for mask in mismatch_masks],
        "mismatch_union_count": mismatch_union.bit_count(),
        "conflict_assignment_count": conflict_union.bit_count(),
        "z_assignment_count_by_output": [mask.bit_count() for mask in z_masks],
        "output_vector_sha256": output_digest,
    }
    output_arrivals = [states[node_id].arrival for node_id in outputs]

    structural_memo: dict[int, str] = {}

    def structural(node_id: int) -> str:
        found = structural_memo.get(node_id)
        if found is not None:
            return found
        node = nodes[node_id]
        value: list[Any] = [
            node["op"],
            node.get("label", ""),
            int(node["cost"]),
            int(node["step_delay"]),
        ]
        value.extend(structural(int(argument)) for argument in node.get("args", ()))
        found = canonical_sha256(value)
        structural_memo[node_id] = found
        return found

    structural_hash = sha256(
        "".join(structural(node_id) for node_id in outputs).encode("ascii")
    ).hexdigest()
    metrics = {
        "gate": reviewed_gate,
        "delay": max(output_arrivals),
        "energy": reviewed_gate * max(output_arrivals),
        "output_arrivals": output_arrivals,
        "reachable_nodes": len(live),
        "structural_sha256": structural_hash,
    }
    factory_hash_payload = {
        "outputs": list(outputs),
        "nodes": list(ordered),
        "live_node_count": len(ordered),
    }
    return {
        "nodes": nodes,
        "ordered": ordered,
        "outputs": outputs,
        "states": states,
        "metrics": metrics,
        "semantic": semantic,
        "structural_invalid_count": structural_invalid,
        "ownership_invalid_count": ownership_invalid,
        "dead_ids": dead_ids,
        "bus_ids": bus_ids,
        "factory_sha256": canonical_sha256(factory_hash_payload),
    }


def audit_translation(
    grafted: dict[str, Any], certificate: dict[str, Any], review: dict[str, Any]
) -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    nodes: dict[int, dict[str, Any]] = review["nodes"]
    translation = grafted.get("translation", {})
    generated_ids = {int(value) for value in translation.get("generated_node_ids", ())}
    declared_source_map = translation.get("source_node_ids", {})
    source_to_dag: dict[int, int] = {}
    for index, (name, expected_id) in enumerate(zip(SOURCE_NAMES, SOURCE_NODE_IDS, strict=True)):
        raw_id = declared_source_map.get(name)
        if expected_id is not None:
            if raw_id != expected_id:
                errors.append(f"paid source {name} maps to {raw_id!r}, expected {expected_id}")
            source_to_dag[index] = expected_id
        elif raw_id is not None:
            node_id = int(raw_id)
            node = nodes.get(node_id)
            if node is None or node.get("op") != "CONST" or str(node.get("label")) != name:
                errors.append(f"constant source {name} has invalid Factory node {raw_id!r}")
            else:
                source_to_dag[index] = node_id

    source_count = len(SOURCE_NAMES)
    network = certificate.get("network", [])
    switch_specs: dict[int, tuple[tuple[int, ...], tuple[int, ...]]] = {}
    ordinary_nodes: dict[int, int] = {}
    label_index: dict[str, list[int]] = {}
    for node_id in generated_ids:
        node = nodes.get(node_id)
        if node is None:
            errors.append(f"declared generated node {node_id} is absent")
            continue
        label_index.setdefault(str(node.get("label", "")), []).append(node_id)

    for slot, item in enumerate(network):
        source = source_count + slot
        kind = str(item.get("kind"))
        if kind == "SWITCH":
            switch_specs[source] = (
                tuple(int(value) for value in item.get("left_bus", ())),
                tuple(int(value) for value in item.get("right_bus", ())),
            )
            continue
        label = f"bit35:slot:{slot}:source:{source}"
        candidates = label_index.get(label, [])
        if len(candidates) != 1:
            errors.append(f"ordinary certificate source {source} has {len(candidates)} nodes")
            continue
        ordinary_nodes[source] = candidates[0]
        source_to_dag[source] = candidates[0]

    group_to_node: dict[tuple[int, ...], int] = {}
    switch_to_group: dict[int, tuple[int, ...]] = {}
    for record in translation.get("switch_source_groups", ()):
        group = tuple(int(value) for value in record.get("certificate_sources", ()))
        node_id = int(record.get("factory_bus_node_id", -1))
        if not group or group in group_to_node:
            errors.append(f"invalid or duplicate Switch group {group}")
            continue
        group_to_node[group] = node_id
        for source in group:
            if source in switch_to_group:
                errors.append(f"Switch source {source} occurs in multiple groups")
            switch_to_group[source] = group
            source_to_dag[source] = node_id
    if set(switch_to_group) != set(switch_specs):
        errors.append(
            f"Switch group coverage {sorted(switch_to_group)} != {sorted(switch_specs)}"
        )

    def resolve_bus(raw: Iterable[int]) -> int | None:
        bus = tuple(int(value) for value in raw)
        switch_members = [value for value in bus if value in switch_specs]
        if switch_members:
            if len(switch_members) != len(bus):
                errors.append(f"certificate bus mixes Switch and non-Switch sources: {bus}")
                return None
            node_id = group_to_node.get(bus)
            if node_id is None:
                errors.append(f"certificate Switch bus lacks exact Factory group: {bus}")
            return node_id
        if len(bus) != 1:
            errors.append(f"ordinary certificate bus is not singleton: {bus}")
            return None
        node_id = source_to_dag.get(bus[0])
        if node_id is None:
            errors.append(f"certificate bus source {bus[0]} has no Factory mapping")
        return node_id

    for slot, item in enumerate(network):
        source = source_count + slot
        kind = str(item.get("kind"))
        if kind == "SWITCH":
            continue
        node_id = ordinary_nodes.get(source)
        if node_id is None:
            continue
        left_id = resolve_bus(item.get("left_bus", ()))
        expected_args = [] if left_id is None else [left_id]
        if kind != "NOT":
            right_id = resolve_bus(item.get("right_bus", ()))
            if right_id is not None:
                expected_args.append(right_id)
        node = nodes[node_id]
        if node.get("op") != kind or node.get("args") != expected_args:
            errors.append(
                f"ordinary source {source} translated as {node.get('op')} {node.get('args')}, "
                f"expected {kind} {expected_args}"
            )

    for group, node_id in group_to_node.items():
        node = nodes.get(node_id)
        if node is None:
            errors.append(f"Switch group {group} references absent BUS node {node_id}")
            continue
        expected_args: list[int] = []
        for source in group:
            spec = switch_specs.get(source)
            if spec is None:
                continue
            enable = resolve_bus(spec[0])
            data = resolve_bus(spec[1])
            if enable is not None and data is not None:
                expected_args.extend((enable, data))
        if node.get("op") != "BUS" or node.get("args") != expected_args:
            errors.append(
                f"Switch group {group} BUS {node_id} args {node.get('args')} != {expected_args}"
            )
        expected_label = f"bit35:switch_sources:{','.join(map(str, group))}"
        if str(node.get("label")) != expected_label:
            errors.append(f"Switch group {group} label changed")

    target_node_ids = {
        name: int(value)
        for name, value in translation.get("target_node_ids", {}).items()
    }
    for name, bus in zip(TARGET_NAMES, certificate.get("output_buses", ()), strict=False):
        expected = resolve_bus(bus)
        if expected is not None and target_node_ids.get(name) != expected:
            errors.append(
                f"target {name} maps to {target_node_ids.get(name)}, expected {expected}"
            )

    referenced_certificate_sources = {
        int(value)
        for item in network
        for field in ("left_bus", "right_bus")
        for value in item.get(field, ())
    }
    referenced_certificate_sources.update(
        int(value) for bus in certificate.get("output_buses", ()) for value in bus
    )
    expected_generated = set(ordinary_nodes.values()) | set(group_to_node.values())
    for index in (12, 13):
        if index in referenced_certificate_sources and index in source_to_dag:
            expected_generated.add(source_to_dag[index])
    if generated_ids != expected_generated:
        errors.append(
            f"generated node set {sorted(generated_ids)} != translated set {sorted(expected_generated)}"
        )

    target_arrivals = translation.get("target_arrivals", {})
    for name, node_id in target_node_ids.items():
        node = nodes.get(node_id)
        if node is None:
            errors.append(f"target {name} references absent node {node_id}")
            continue
        arrival = int(node.get("arrival", -1))
        if target_arrivals.get(name) != arrival:
            errors.append(f"target {name} serialized arrival summary changed")
        if arrival > TARGET_DEADLINES[name]:
            errors.append(f"target {name}@{arrival} misses deadline {TARGET_DEADLINES[name]}")

    evidence = {
        "generated_node_ids": sorted(generated_ids),
        "ordinary_source_node_ids": {
            str(source): node_id for source, node_id in sorted(ordinary_nodes.items())
        },
        "switch_groups": [
            {"certificate_sources": list(group), "factory_bus_node_id": node_id}
            for group, node_id in group_to_node.items()
        ],
        "target_node_ids": target_node_ids,
        "target_arrivals": {
            name: review["states"][node_id].arrival
            for name, node_id in target_node_ids.items()
            if node_id in review["states"]
        },
    }
    return errors, evidence


def audit_shell(
    authority_review: dict[str, Any],
    graft_review: dict[str, Any],
    grafted: dict[str, Any],
) -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    authority_nodes = authority_review["nodes"]
    graft_nodes = graft_review["nodes"]
    shell_ids = set(authority_nodes) - REGION_IDS
    if not shell_ids.issubset(graft_nodes):
        errors.append(f"missing shell nodes: {sorted(shell_ids-set(graft_nodes))[:12]}")
    if REGION_IDS.intersection(graft_nodes):
        errors.append(f"removed region IDs remain: {sorted(REGION_IDS.intersection(graft_nodes))}")
    target_ids = {
        name: int(value)
        for name, value in grafted.get("translation", {}).get("target_node_ids", {}).items()
    }
    replacement = {62: target_ids.get("C5"), 63: target_ids.get("T5")}
    patch_counts = {62: 0, 63: 0}
    for node_id in sorted(shell_ids):
        original = authority_nodes[node_id]
        graft = graft_nodes.get(node_id)
        if graft is None:
            continue
        expected_args: list[int] = []
        for raw in original.get("args", ()):
            predecessor = int(raw)
            if predecessor in replacement:
                patch_counts[predecessor] += 1
                mapped = replacement[predecessor]
                if mapped is None:
                    errors.append(f"missing replacement for old target {predecessor}")
                    mapped = predecessor
                predecessor = mapped
            elif predecessor in REGION_IDS:
                errors.append(
                    f"unexpected shell node {node_id} references removed region {predecessor}"
                )
            expected_args.append(predecessor)
        if graft.get("args") != expected_args:
            errors.append(
                f"shell node {node_id} args {graft.get('args')} != expected {expected_args}"
            )
        for key in ("op", "cost", "step_delay", "may_z", "label", "resolved_network"):
            if graft.get(key) != original.get(key):
                errors.append(f"shell node {node_id} field {key} changed")
        if graft.get("op") == "BUS":
            resolved = str(graft.get("resolved_network"))
            expected_drivers = [
                {
                    "enable": expected_args[index],
                    "data": expected_args[index + 1],
                    "owner": resolved,
                }
                for index in range(0, len(expected_args), 2)
            ]
            if graft.get("drivers") != expected_drivers:
                errors.append(f"shell BUS node {node_id} driver metadata changed incorrectly")
    if patch_counts != {62: 1, 63: 1}:
        errors.append(f"shell patch counts changed: {patch_counts}")

    expected_outputs = list(EXPECTED_PRIMARY_OUTPUTS)
    output_replacements = {
        83: target_ids.get("S3"),
        86: target_ids.get("S4"),
        65: target_ids.get("S5"),
    }
    expected_outputs = [output_replacements.get(value, value) for value in expected_outputs]
    if list(graft_review["outputs"]) != expected_outputs:
        errors.append(
            f"primary outputs {list(graft_review['outputs'])} != expected {expected_outputs}"
        )

    shell_gate = sum(int(authority_nodes[node_id]["cost"]) for node_id in shell_ids)
    if shell_gate != 63:
        errors.append(f"independently counted shell gate is {shell_gate}, expected 63")
    original_bus_ids = {
        node_id for node_id, node in authority_nodes.items() if node.get("op") == "BUS"
    }
    retained_bus_ids = original_bus_ids - REGION_IDS
    actual_retained_bus_ids = {
        node_id
        for node_id, node in graft_nodes.items()
        if node_id in shell_ids and node.get("op") == "BUS"
    }
    if retained_bus_ids != actual_retained_bus_ids:
        errors.append("retained authoritative BUS node set changed")
    evidence = {
        "shell_node_count": len(shell_ids),
        "shell_gate": shell_gate,
        "patch_counts": {str(key): value for key, value in patch_counts.items()},
        "expected_outputs": expected_outputs,
        "retained_authoritative_bus_node_ids": sorted(retained_bus_ids),
    }
    return errors, evidence


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--grafted", type=Path, default=DEFAULT_GRAFTED)
    parser.add_argument("--certificate", type=Path, default=DEFAULT_CERTIFICATE)
    parser.add_argument("--independent-96-verification", type=Path, default=DEFAULT_96_VERIFY)
    parser.add_argument("--dag", type=Path, default=AUTHORITATIVE_DAG)
    parser.add_argument("--cut-audit", type=Path, default=CUT_AUDIT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--max-gate", type=int)
    parser.add_argument("--max-delay", type=int, default=7)
    parser.add_argument("--max-energy", type=int)
    args = parser.parse_args()

    paths = {
        "grafted": args.grafted.resolve(),
        "certificate": args.certificate.resolve(),
        "independent_96_verification": args.independent_96_verification.resolve(),
        "authoritative_dag": args.dag.resolve(),
        "cut_audit": args.cut_audit.resolve(),
    }
    for path in paths.values():
        if not path.is_file():
            raise FileNotFoundError(path)
    grafted = json.loads(paths["grafted"].read_text(encoding="utf-8"))
    certificate = json.loads(paths["certificate"].read_text(encoding="utf-8"))
    independent_96 = json.loads(
        paths["independent_96_verification"].read_text(encoding="utf-8")
    )
    authority = json.loads(paths["authoritative_dag"].read_text(encoding="utf-8"))
    cut_audit = json.loads(paths["cut_audit"].read_text(encoding="utf-8"))

    metadata_errors: list[str] = []
    source_errors: list[str] = []
    if grafted.get("schema") != "tc-byte-adder-bit35-joint-graft-v1":
        metadata_errors.append(f"unexpected graft schema {grafted.get('schema')!r}")
    if grafted.get("status") != "sat":
        metadata_errors.append("grafted payload is not SAT")
    if certificate.get("status") != "sat":
        metadata_errors.append("certificate is not SAT")
    if certificate.get("truth_domain_sha256") != TRUTH_DOMAIN_SHA256:
        metadata_errors.append("certificate truth-domain hash changed")
    if independent_96.get("schema") != "tc-byte-adder-bit35-joint-independent-verify-v1":
        metadata_errors.append("unexpected 96-row verification schema")
    if independent_96.get("status") != "pass":
        metadata_errors.append("96-row independent verification did not pass")
    if independent_96.get("certificate_sha256") != file_sha256(paths["certificate"]):
        source_errors.append("96-row verification belongs to another certificate")
    checks_96 = independent_96.get("checks", {})
    for key in FATAL_96_KEYS:
        if checks_96.get(key) != 0:
            metadata_errors.append(f"96-row fatal check {key}={checks_96.get(key)!r}")
    if file_sha256(paths["authoritative_dag"]) != AUTHORITATIVE_SHA256:
        source_errors.append("authoritative DAG byte hash changed")
    if file_sha256(paths["cut_audit"]) != CUT_AUDIT_SHA256:
        source_errors.append("cut audit byte hash changed")
    if cut_audit.get("authoritative_dag_sha256") != AUTHORITATIVE_SHA256:
        source_errors.append("cut audit references another authority")

    source = grafted.get("source", {})
    expected_source_hashes = {
        "authoritative_dag_sha256": file_sha256(paths["authoritative_dag"]),
        "cut_audit_sha256": file_sha256(paths["cut_audit"]),
        "certificate_sha256": file_sha256(paths["certificate"]),
        "independent_96_row_verification_sha256": file_sha256(
            paths["independent_96_verification"]
        ),
        "graft_script_sha256": file_sha256(GRAFT_SCRIPT),
        "full_replay_support_sha256": file_sha256(REPLAY_SUPPORT),
    }
    for key, expected in expected_source_hashes.items():
        if source.get(key) != expected:
            source_errors.append(f"graft source hash {key} changed")

    authority_review = evaluate_factory(authority["factory_dag"])
    graft_review = evaluate_factory(grafted["factory_dag"])
    authority_errors: list[str] = []
    if authority_review["metrics"] != authority.get("metrics"):
        authority_errors.append("authority metrics fail independent replay")
    if authority_review["semantic"] != authority.get("semantic"):
        authority_errors.append("authority semantics fail independent replay")
    if authority_review["factory_sha256"] != authority["factory_dag"].get("sha256"):
        authority_errors.append("authority Factory hash changed")
    if authority_review["structural_invalid_count"]:
        authority_errors.append("authority has invalid structural annotations")
    if authority_review["ownership_invalid_count"]:
        authority_errors.append("authority has invalid BUS ownership")
    if authority_review["dead_ids"]:
        authority_errors.append("authority has dead nodes")

    shell_errors, shell_evidence = audit_shell(authority_review, graft_review, grafted)
    translation_errors, translation_evidence = audit_translation(
        grafted, certificate, graft_review
    )

    factory_hash_errors: list[str] = []
    if graft_review["factory_sha256"] != grafted["factory_dag"].get("sha256"):
        factory_hash_errors.append("grafted Factory canonical hash changed")
    if int(grafted["factory_dag"].get("live_node_count", -1)) != len(
        grafted["factory_dag"].get("nodes", ())
    ):
        factory_hash_errors.append("grafted Factory live_node_count changed")
    if graft_review["metrics"] != grafted.get("metrics"):
        factory_hash_errors.append("grafted metrics differ from independent replay")
    if graft_review["semantic"] != grafted.get("semantic"):
        factory_hash_errors.append("grafted semantic summary differs from independent replay")

    certificate_gate = sum(
        2 if item.get("kind") == "SWITCH" else GATE_COST[str(item.get("kind"))]
        for item in certificate.get("network", ())
    )
    generated_ids = {
        int(value) for value in grafted.get("translation", {}).get("generated_node_ids", ())
    }
    generated_gate = sum(
        int(graft_review["nodes"][node_id]["cost"])
        for node_id in generated_ids
        if node_id in graft_review["nodes"]
    )
    expected_complete_gate = 63 + certificate_gate
    gate_error_count = 0
    if certificate_gate != int(certificate.get("actual_gate", -1)):
        gate_error_count += 1
    if generated_gate != certificate_gate:
        gate_error_count += 1
    if int(graft_review["metrics"]["gate"]) != expected_complete_gate:
        gate_error_count += 1
    if args.max_gate is not None and int(graft_review["metrics"]["gate"]) > args.max_gate:
        gate_error_count += 1

    delay_error_count = int(int(graft_review["metrics"]["delay"]) > args.max_delay)
    energy_error_count = int(
        args.max_energy is not None
        and int(graft_review["metrics"]["energy"]) > args.max_energy
    )
    semantic = graft_review["semantic"]
    mismatch_count = sum(int(value) for value in semantic["mismatch_count_by_output"])
    bus_conflict_count = int(semantic["conflict_assignment_count"])
    undriven_output_count = sum(int(value) for value in semantic["z_assignment_count_by_output"])

    declared_groups = grafted.get("translation", {}).get("switch_source_groups", ())
    group_bus_ids = {int(item["factory_bus_node_id"]) for item in declared_groups}
    generated_bus_ids = {
        node_id
        for node_id in generated_ids
        if node_id in graft_review["nodes"]
        and graft_review["nodes"][node_id].get("op") == "BUS"
    }
    physical_partition_errors = 0
    if group_bus_ids != generated_bus_ids:
        physical_partition_errors += 1
    if graft_review["ownership_invalid_count"]:
        physical_partition_errors += graft_review["ownership_invalid_count"]
    if grafted.get("physical", {}).get("physical_net_partition_violation_count") != 0:
        physical_partition_errors += 1
    if grafted.get("physical", {}).get("partial_driver_reuse_possible") is not False:
        physical_partition_errors += 1

    full_replay = grafted.get("full_replay", {})
    full_replay_metadata_errors = 0
    expected_replay_fields = {
        "variables": 17,
        "rows": ASSIGNMENTS,
        "complete_u8_u8_u1": True,
        "mismatch_union_count": semantic["mismatch_union_count"],
        "conflict_assignment_count": semantic["conflict_assignment_count"],
        "primary_output_z_counts": semantic["z_assignment_count_by_output"],
        "output_vector_sha256": semantic["output_vector_sha256"],
    }
    for key, expected in expected_replay_fields.items():
        full_replay_metadata_errors += full_replay.get(key) != expected

    checks = {
        "metadata_error_count": len(metadata_errors),
        "source_hash_error_count": len(source_errors),
        "authority_replay_error_count": len(authority_errors),
        "factory_hash_error_count": len(factory_hash_errors),
        "shell_preservation_violation_count": len(shell_errors),
        "translation_violation_count": len(translation_errors),
        "structural_invalid_count": graft_review["structural_invalid_count"],
        "weighted_gate": graft_review["metrics"]["gate"],
        "fixed_shell_gate": 63,
        "certificate_joint_gate": certificate_gate,
        "generated_joint_gate": generated_gate,
        "expected_complete_gate": expected_complete_gate,
        "gate_accounting_violation_count": gate_error_count,
        "delay": graft_review["metrics"]["delay"],
        "delay_limit": args.max_delay,
        "delay_violation_count": delay_error_count,
        "energy": graft_review["metrics"]["energy"],
        "energy_limit": args.max_energy,
        "energy_violation_count": energy_error_count,
        "mismatch_count_by_output": dict(
            zip(PRIMARY_OUTPUT_NAMES, semantic["mismatch_count_by_output"], strict=True)
        ),
        "mismatch_count": mismatch_count,
        "bus_conflict_count": bus_conflict_count,
        "undriven_count_by_output": dict(
            zip(PRIMARY_OUTPUT_NAMES, semantic["z_assignment_count_by_output"], strict=True)
        ),
        "undriven_output_count": undriven_output_count,
        "physical_net_partition_violation_count": physical_partition_errors,
        "dead_reachable_node_count": len(graft_review["dead_ids"]),
        "bus_ownership_violation_count": graft_review["ownership_invalid_count"],
        "full_replay_metadata_error_count": full_replay_metadata_errors,
    }
    fatal_keys = (
        "metadata_error_count",
        "source_hash_error_count",
        "authority_replay_error_count",
        "factory_hash_error_count",
        "shell_preservation_violation_count",
        "translation_violation_count",
        "structural_invalid_count",
        "gate_accounting_violation_count",
        "delay_violation_count",
        "energy_violation_count",
        "mismatch_count",
        "bus_conflict_count",
        "undriven_output_count",
        "physical_net_partition_violation_count",
        "dead_reachable_node_count",
        "bus_ownership_violation_count",
        "full_replay_metadata_error_count",
    )
    passed = not any(int(checks[key]) for key in fatal_keys)
    result = {
        "schema": "tc-byte-adder-bit35-joint-full-dag-independent-verify-v1",
        "status": "pass" if passed else "fail",
        "artifacts": {
            name: {"path": str(path), "sha256": file_sha256(path)}
            for name, path in paths.items()
        },
        "verifier": {
            "path": str(Path(__file__).resolve()),
            "sha256": file_sha256(Path(__file__)),
            "independent_of_graft_builder_and_replay_support": True,
        },
        "full_domain": {
            "variables": 17,
            "rows": ASSIGNMENTS,
            "complete_u8_u8_u1": True,
            "output_vector_sha256": semantic["output_vector_sha256"],
        },
        "checks": checks,
        "evidence": {
            "shell": shell_evidence,
            "translation": translation_evidence,
            "factory_dag_sha256": graft_review["factory_sha256"],
            "structural_sha256": graft_review["metrics"]["structural_sha256"],
            "bus_node_ids": graft_review["bus_ids"],
        },
        "errors": {
            "metadata": metadata_errors,
            "source_hashes": source_errors,
            "authority": authority_errors,
            "factory_hash": factory_hash_errors,
            "shell": shell_errors,
            "translation": translation_errors,
        },
    }
    output_sha = atomic_write(args.output.resolve(), result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"sha256={output_sha}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
