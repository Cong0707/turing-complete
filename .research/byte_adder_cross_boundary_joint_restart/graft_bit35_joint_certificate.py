"""Deterministically graft a verified bit-3:5 joint certificate into the 80/7 DAG.

The script never touches a game save or a deployable candidate.  It consumes a
SAT certificate only after the separate 96-row verifier has accepted that exact
file, replaces the audited 17-gate region, and replays the complete 2^17 Byte
Adder domain through the resulting Factory DAG.

Synthesized ``SWITCH`` components need a small representation conversion.  In
the exact certificate a Switch output is a source with a value and a driven
bit; in a Factory DAG the complete set of Switch drivers on one physical net is
serialized as one ``BUS`` node.  Consequently this importer materializes every
unique Switch-output bus exactly once and never creates a partially overlapping
driver group.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any, Iterable


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
AUTHORITATIVE_DAG = (
    ROOT / ".research" / "byte_adder_root" / "byte-adder-hybrid-phasefold-g80-d7.json"
)
CUT_AUDIT = HERE / "bit35_joint_cut_audit.json"
REPLAY_SUPPORT = ROOT / ".research" / "byte_adder_root" / "graft_abc_mapped_residual.py"
DEFAULT_CERTIFICATE = (
    HERE / "bit35_joint_phase_driver_positive_g17_n15_c5d2k3_t1_s1.json"
)
DEFAULT_INDEPENDENT_VERIFY = (
    HERE / "bit35_joint_phase_driver_positive_g17_independent_verify.json"
)
DEFAULT_OUTPUT = HERE / "bit35_joint_grafted_full_dag.json"

AUTHORITATIVE_SHA256 = "71625de2b86ea03127415802dbc68f605ac16d69da6d9e8b3ade35db317ec884"
CUT_AUDIT_SHA256 = "4edbfc5cb3faa412a8c1eaf93925b30a99895b000c83101d63905a2ef9830df7"
TRUTH_DOMAIN_SHA256 = "1c9768429735b2f87bca12bb62dad82624f45a419b80ea6b5470655764c34b60"

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
SOURCE_NODE_IDS: dict[str, int | None] = {
    "a3": 8,
    "b3": 9,
    "a4": 10,
    "b4": 11,
    "C3": 56,
    "P5": 36,
    "G3": 28,
    "Q3": 29,
    "P3": 30,
    "G4": 31,
    "Q4": 32,
    "P4": 33,
    "0": None,
    "1": None,
}
SOURCE_ARRIVALS = (0, 0, 0, 0, 3, 2, 1, 1, 2, 1, 1, 2, 0, 0)
TARGET_NAMES = ("S3", "S4", "C5", "T5", "S5")
TARGET_OLD_IDS = {"S3": 83, "S4": 86, "C5": 62, "T5": 63, "S5": 65}
TARGET_DEADLINES = {"S3": 5, "S4": 7, "C5": 4, "T5": 5, "S5": 6}
PRIMARY_OUTPUT_NAMES = ("S0", "S1", "S2", "S3", "S4", "S5", "S6", "S7", "C8")
EXPECTED_PRIMARY_OUTPUTS = (49, 77, 81, 83, 86, 65, 73, 88, 75)
EXPECTED_REGION_IDS = (57, 58, 59, 60, 61, 62, 63, 64, 65, 82, 83, 84, 85, 86)
EXPECTED_EXTERNAL_FANOUT = {
    "62": ["node:69"],
    "63": ["node:72"],
    "65": ["output:S5"],
    "83": ["output:S3"],
    "86": ["output:S4"],
}
ALLOWED_CERTIFICATE_SCHEMAS = {
    "tc-byte-adder-bit35-joint-strict-z-exact-v1",
    "tc-byte-adder-bit35-joint-c5-normal-form-shard-v1",
    "tc-byte-adder-bit35-joint-phase-driver-shard-v1",
}
GATE_COST = {"NOT": 1, "AND": 1, "OR": 1, "NAND": 1, "NOR": 1, "XOR": 3}
GATE_DELAY = {"NOT": 1, "AND": 1, "OR": 1, "NAND": 1, "NOR": 1, "XOR": 2}
INDEPENDENT_FATAL_KEYS = (
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


def portable(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(resolved).replace("\\", "/")


def atomic_write(path: Path, payload: dict[str, Any]) -> str:
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(encoded)
    temporary.replace(path)
    return sha256(encoded).hexdigest()


def load_replay_support():
    spec = importlib.util.spec_from_file_location("bit35_full_replay_support", REPLAY_SUPPORT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load replay support {REPLAY_SUPPORT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def validate_authority(
    authority_path: Path, authority: dict[str, Any], support: Any
) -> dict[str, Any]:
    if file_sha256(authority_path) != AUTHORITATIVE_SHA256:
        raise RuntimeError("authoritative DAG byte hash changed")
    review = support.validate_authoritative_dag(authority)
    metrics = review["metrics"]
    if (metrics["gate"], metrics["delay"], metrics["energy"]) != (80, 7, 560):
        raise RuntimeError(f"authoritative metrics changed: {metrics}")
    if tuple(metrics["output_arrivals"]) != (4, 4, 7, 5, 7, 6, 7, 7, 7):
        raise RuntimeError("authoritative output arrivals changed")
    outputs = tuple(int(value) for value in authority["factory_dag"]["outputs"])
    if outputs != EXPECTED_PRIMARY_OUTPUTS:
        raise RuntimeError(f"authoritative primary outputs changed: {outputs}")
    return review


def validate_cut_audit(path: Path, audit: dict[str, Any]) -> None:
    if file_sha256(path) != CUT_AUDIT_SHA256:
        raise RuntimeError("bit3:5 cut audit byte hash changed")
    if audit.get("schema") != "tc-byte-adder-bit35-joint-cut-audit-v1":
        raise RuntimeError("unexpected bit3:5 cut audit schema")
    if audit.get("authoritative_dag_sha256") != AUTHORITATIVE_SHA256:
        raise RuntimeError("cut audit references another authoritative DAG")
    region = audit.get("replaceable_region", {})
    if tuple(region.get("node_ids", ())) != EXPECTED_REGION_IDS:
        raise RuntimeError("replaceable region IDs changed")
    if (
        int(region.get("weighted_gate", -1)),
        int(region.get("component_count", -1)),
        int(region.get("switch_components", -1)),
    ) != (17, 15, 2):
        raise RuntimeError("replaceable region accounting changed")
    if audit.get("external_fanout") != EXPECTED_EXTERNAL_FANOUT:
        raise RuntimeError("replaceable region external fanout changed")
    accounting = audit.get("accounting", {})
    if int(accounting.get("fixed_shell_with_paid_sources", -1)) != 63:
        raise RuntimeError("fixed shell is no longer 63 gates")


def validate_independent_verification(
    verification_path: Path,
    verification: dict[str, Any],
    certificate_path: Path,
) -> None:
    if verification.get("schema") != "tc-byte-adder-bit35-joint-independent-verify-v1":
        raise RuntimeError("unexpected independent verification schema")
    if verification.get("status") != "pass":
        raise RuntimeError("96-row independent verification did not pass")
    certificate_hash = file_sha256(certificate_path)
    if verification.get("certificate_sha256") != certificate_hash:
        raise RuntimeError("independent verification belongs to another certificate")
    truth = verification.get("truth_domain", {})
    if int(truth.get("rows", -1)) != 96:
        raise RuntimeError("independent verification did not replay 96 rows")
    if truth.get("truth_domain_sha256") != TRUTH_DOMAIN_SHA256:
        raise RuntimeError("independent verification truth-domain hash changed")
    checks = verification.get("checks", {})
    failures = {key: checks.get(key) for key in INDEPENDENT_FATAL_KEYS if checks.get(key) != 0}
    if failures:
        raise RuntimeError(f"independent verification has fatal checks: {failures}")


def validate_certificate(certificate: dict[str, Any]) -> tuple[int, int, int]:
    if certificate.get("schema") not in ALLOWED_CERTIFICATE_SCHEMAS:
        raise RuntimeError(f"unsupported certificate schema: {certificate.get('schema')!r}")
    expected = {
        "status": "sat",
        "target_names": list(TARGET_NAMES),
        "output_deadlines": [TARGET_DEADLINES[name] for name in TARGET_NAMES],
        "assignments": 96,
        "truth_domain_sha256": TRUTH_DOMAIN_SHA256,
    }
    for key, value in expected.items():
        if certificate.get(key) != value:
            raise RuntimeError(f"certificate metadata {key} changed")

    network = certificate.get("network")
    output_buses = certificate.get("output_buses")
    if not isinstance(network, list) or len(network) != int(certificate.get("components", -1)):
        raise RuntimeError("certificate network/component count mismatch")
    if not isinstance(output_buses, list) or len(output_buses) != len(TARGET_NAMES):
        raise RuntimeError("certificate output bus count mismatch")

    weighted_gate = 0
    switch_count = 0
    xor_count = 0
    source_count = len(SOURCE_NAMES)
    for slot, item in enumerate(network):
        source = source_count + slot
        kind = str(item.get("kind"))
        if int(item.get("slot", -1)) != slot or int(item.get("source", -1)) != source:
            raise RuntimeError(f"certificate slot/source mismatch at slot {slot}")
        if kind == "SWITCH":
            cost = 2
            switch_count += 1
        elif kind in GATE_COST:
            cost = GATE_COST[kind]
            xor_count += kind == "XOR"
        else:
            raise RuntimeError(f"unsupported certificate kind {kind!r}")
        if int(item.get("cost", -1)) != cost:
            raise RuntimeError(f"certificate cost mismatch at slot {slot}")
        weighted_gate += cost

        left = tuple(int(value) for value in item.get("left_bus", ()))
        right = tuple(int(value) for value in item.get("right_bus", ()))
        if not left or (kind != "NOT" and not right) or (kind == "NOT" and right):
            raise RuntimeError(f"certificate arity mismatch at slot {slot}")
        for bus in (left, right):
            if len(bus) != len(set(bus)) or tuple(sorted(bus)) != bus:
                raise RuntimeError(f"certificate bus is not a strict sorted set at slot {slot}")
            if any(value < 0 or value >= source for value in bus):
                raise RuntimeError(f"certificate has a forward reference at slot {slot}")

    for output, raw_bus in zip(TARGET_NAMES, output_buses, strict=True):
        bus = tuple(int(value) for value in raw_bus)
        if not bus or len(bus) != len(set(bus)) or tuple(sorted(bus)) != bus:
            raise RuntimeError(f"certificate output bus {output} is not a strict sorted set")
        if any(value < 0 or value >= source_count + len(network) for value in bus):
            raise RuntimeError(f"certificate output bus {output} is out of range")

    if weighted_gate != int(certificate.get("actual_gate", -1)):
        raise RuntimeError("certificate actual_gate differs from decoded network")
    if weighted_gate > int(certificate.get("gate_bound", -1)):
        raise RuntimeError("certificate exceeds its declared gate bound")
    if certificate.get("actual_switches") is not None and switch_count != int(
        certificate["actual_switches"]
    ):
        raise RuntimeError("certificate actual_switches differs from decoded network")
    if certificate.get("actual_xors") is not None and xor_count != int(
        certificate["actual_xors"]
    ):
        raise RuntimeError("certificate actual_xors differs from decoded network")
    return weighted_gate, switch_count, xor_count


def stable_topological_order(
    nodes: dict[int, dict[str, Any]], outputs: Iterable[int], rank: dict[int, int]
) -> list[int]:
    live: set[int] = set()
    pending = list(outputs)
    while pending:
        node_id = int(pending.pop())
        if node_id in live:
            continue
        node = nodes.get(node_id)
        if node is None:
            raise RuntimeError(f"graft references missing node {node_id}")
        live.add(node_id)
        pending.extend(int(value) for value in node.get("args", ()))

    indegree = {node_id: 0 for node_id in live}
    consumers: dict[int, list[int]] = defaultdict(list)
    for node_id in live:
        for predecessor in nodes[node_id].get("args", ()):
            predecessor = int(predecessor)
            if predecessor not in live:
                raise RuntimeError(f"live node {node_id} references non-live node {predecessor}")
            indegree[node_id] += 1
            consumers[predecessor].append(node_id)

    ready = sorted((node_id for node_id, degree in indegree.items() if degree == 0), key=rank.get)
    ordered: list[int] = []
    while ready:
        node_id = ready.pop(0)
        ordered.append(node_id)
        for consumer in sorted(consumers[node_id], key=rank.get):
            indegree[consumer] -= 1
            if indegree[consumer] == 0:
                ready.append(consumer)
                ready.sort(key=rank.get)
    if len(ordered) != len(live):
        raise RuntimeError("graft graph is cyclic")
    return ordered


def annotate_nodes(
    nodes: dict[int, dict[str, Any]], ordered_ids: list[int]
) -> list[dict[str, Any]]:
    arrivals: dict[int, int] = {}
    result: list[dict[str, Any]] = []
    for node_id in ordered_ids:
        node = dict(nodes[node_id])
        op = str(node["op"])
        args = [int(value) for value in node.get("args", ())]
        if any(value not in arrivals for value in args):
            raise RuntimeError(f"node {node_id} is not topological during annotation")
        if op in {"INPUT", "CONST"}:
            if args:
                raise RuntimeError(f"source node {node_id} has arguments")
            cost = delay = arrival = 0
            may_z = False
        elif op == "BUS":
            if not args or len(args) % 2:
                raise RuntimeError(f"BUS node {node_id} has incomplete drivers")
            cost = len(args)
            delay = 1
            arrival = max(arrivals[value] for value in args) + 1
            may_z = True
            resolved = str(node.get("resolved_network", f"bus_node_{node_id}"))
            node["resolved_network"] = resolved
            node["drivers"] = [
                {"enable": args[index], "data": args[index + 1], "owner": resolved}
                for index in range(0, len(args), 2)
            ]
        elif op in GATE_COST:
            expected_arity = 1 if op == "NOT" else 2
            if len(args) != expected_arity:
                raise RuntimeError(f"gate node {node_id} has wrong arity")
            cost = GATE_COST[op]
            delay = GATE_DELAY[op]
            arrival = max(arrivals[value] for value in args) + delay
            may_z = False
        else:
            raise RuntimeError(f"unsupported DAG operation {op!r}")
        node.update(
            {
                "id": node_id,
                "args": args,
                "cost": cost,
                "step_delay": delay,
                "arrival": arrival,
                "may_z": may_z,
            }
        )
        arrivals[node_id] = arrival
        result.append(node)
    return result


def build(
    authority_path: Path,
    cut_audit_path: Path,
    certificate_path: Path,
    independent_verification_path: Path,
    *,
    max_gate: int | None = None,
    max_delay: int = 7,
    max_energy: int | None = None,
) -> dict[str, Any]:
    paths = tuple(
        Path(path).resolve()
        for path in (
            authority_path,
            cut_audit_path,
            certificate_path,
            independent_verification_path,
        )
    )
    for path in paths:
        if not path.is_file():
            raise FileNotFoundError(path)
    authority_path, cut_audit_path, certificate_path, independent_verification_path = paths

    support = load_replay_support()
    authority = json.loads(authority_path.read_text(encoding="utf-8"))
    cut_audit = json.loads(cut_audit_path.read_text(encoding="utf-8"))
    certificate = json.loads(certificate_path.read_text(encoding="utf-8"))
    independent = json.loads(independent_verification_path.read_text(encoding="utf-8"))
    authority_review = validate_authority(authority_path, authority, support)
    validate_cut_audit(cut_audit_path, cut_audit)
    validate_independent_verification(
        independent_verification_path, independent, certificate_path
    )
    joint_gate, switch_count, xor_count = validate_certificate(certificate)

    original_nodes = tuple(authority["factory_dag"]["nodes"])
    original_by_id = {int(node["id"]): dict(node) for node in original_nodes}
    if len(original_by_id) != len(original_nodes):
        raise RuntimeError("authoritative DAG has duplicate node IDs")
    region_ids = set(EXPECTED_REGION_IDS)
    nodes = {
        node_id: dict(node)
        for node_id, node in original_by_id.items()
        if node_id not in region_ids
    }
    shell_ids = set(nodes)
    shell_gate = sum(int(node["cost"]) for node in nodes.values())
    if shell_gate != 63:
        raise RuntimeError(f"retained shell gate changed: {shell_gate}")

    next_id = max(original_by_id) + 1
    generated_ids: list[int] = []
    generated_kind_counts: Counter[str] = Counter()
    source_node_ids: dict[int, int] = {}
    switch_specs: dict[int, tuple[tuple[int, ...], tuple[int, ...]]] = {}
    switch_bus_nodes: dict[tuple[int, ...], int] = {}
    constant_nodes: dict[str, int] = {}
    source_count = len(SOURCE_NAMES)

    for index, name in enumerate(SOURCE_NAMES):
        node_id = SOURCE_NODE_IDS[name]
        if node_id is None:
            continue
        if node_id not in nodes:
            raise RuntimeError(f"paid source {name} node {node_id} is not retained")
        if int(nodes[node_id]["arrival"]) != SOURCE_ARRIVALS[index]:
            raise RuntimeError(f"paid source {name} arrival changed")
        source_node_ids[index] = node_id

    def allocate(node: dict[str, Any]) -> int:
        nonlocal next_id
        node_id = next_id
        next_id += 1
        if node_id in nodes:
            raise RuntimeError(f"new node ID collision at {node_id}")
        node = {"id": node_id, **node}
        nodes[node_id] = node
        generated_ids.append(node_id)
        generated_kind_counts[str(node["op"])] += 1
        return node_id

    def resolve_source(source: int) -> int:
        found = source_node_ids.get(source)
        if found is not None:
            return found
        if 0 <= source < source_count and SOURCE_NAMES[source] in {"0", "1"}:
            label = SOURCE_NAMES[source]
            found = constant_nodes.get(label)
            if found is None:
                found = allocate(
                    {
                        "op": "CONST",
                        "args": [],
                        "cost": 0,
                        "step_delay": 0,
                        "arrival": 0,
                        "may_z": False,
                        "label": label,
                    }
                )
                constant_nodes[label] = found
            source_node_ids[source] = found
            return found
        if source in switch_specs:
            return resolve_bus((source,))
        raise RuntimeError(f"certificate source {source} has not been materialized")

    def resolve_bus(bus: tuple[int, ...]) -> int:
        if not bus:
            raise RuntimeError("cannot materialize an empty certificate bus")
        if len(bus) == 1 and bus[0] not in switch_specs:
            return resolve_source(bus[0])
        if any(source not in switch_specs for source in bus):
            raise RuntimeError(f"multi-driver bus contains a non-Switch source: {bus}")
        found = switch_bus_nodes.get(bus)
        if found is not None:
            return found
        args: list[int] = []
        for source in bus:
            left, right = switch_specs[source]
            args.extend((resolve_bus(left), resolve_bus(right)))
        node_id = allocate(
            {
                "op": "BUS",
                "args": args,
                "cost": len(args),
                "step_delay": 1,
                "arrival": 0,
                "may_z": True,
                "label": f"bit35:switch_sources:{','.join(map(str, bus))}",
                "resolved_network": f"bus_node_{next_id}",
                "drivers": [],
            }
        )
        # allocate() used the pre-increment value of next_id as node_id.
        nodes[node_id]["resolved_network"] = f"bus_node_{node_id}"
        switch_bus_nodes[bus] = node_id
        for source in bus:
            source_node_ids[source] = node_id
        return node_id

    network = certificate["network"]
    for slot, item in enumerate(network):
        source = source_count + slot
        kind = str(item["kind"])
        left = tuple(int(value) for value in item["left_bus"])
        right = tuple(int(value) for value in item["right_bus"])
        if kind == "SWITCH":
            switch_specs[source] = (left, right)
            continue
        left_id = resolve_bus(left)
        args = [left_id]
        if kind != "NOT":
            args.append(resolve_bus(right))
        node_id = allocate(
            {
                "op": kind,
                "args": args,
                "cost": GATE_COST[kind],
                "step_delay": GATE_DELAY[kind],
                "arrival": 0,
                "may_z": False,
                "label": f"bit35:slot:{slot}:source:{source}",
            }
        )
        source_node_ids[source] = node_id

    target_node_ids: dict[str, int] = {}
    for name, raw_bus in zip(TARGET_NAMES, certificate["output_buses"], strict=True):
        target_node_ids[name] = resolve_bus(tuple(int(value) for value in raw_bus))

    if set(source_node_ids).intersection(switch_specs) != set(switch_specs):
        missing = sorted(set(switch_specs) - set(source_node_ids))
        raise RuntimeError(f"certificate has unmaterialized Switch components: {missing}")
    groups = list(switch_bus_nodes)
    for left_index, left in enumerate(groups):
        for right in groups[left_index + 1 :]:
            overlap = set(left) & set(right)
            if overlap:
                raise RuntimeError(f"translated Switch BUS groups partially overlap: {left}, {right}")
    covered_switches = set().union(*(set(group) for group in groups)) if groups else set()
    if covered_switches != set(switch_specs):
        raise RuntimeError("translated BUS groups do not cover every Switch exactly once")

    replacement_ids = {
        TARGET_OLD_IDS[name]: target_node_ids[name] for name in TARGET_NAMES
    }
    patch_counts: Counter[int] = Counter()
    for node_id in sorted(shell_ids):
        node = nodes[node_id]
        patched_args = []
        for raw in node.get("args", ()):
            predecessor = int(raw)
            if predecessor in replacement_ids:
                patch_counts[predecessor] += 1
                predecessor = replacement_ids[predecessor]
            elif predecessor in region_ids:
                raise RuntimeError(
                    f"unexpected retained node {node_id} references removed region node {predecessor}"
                )
            patched_args.append(predecessor)
        node["args"] = patched_args
        if node.get("op") == "BUS":
            resolved = str(node.get("resolved_network", f"bus_node_{node_id}"))
            node["drivers"] = [
                {
                    "enable": patched_args[index],
                    "data": patched_args[index + 1],
                    "owner": resolved,
                }
                for index in range(0, len(patched_args), 2)
            ]
    expected_patch_counts = Counter({62: 1, 63: 1})
    if patch_counts != expected_patch_counts:
        raise RuntimeError(f"external node patch count changed: {dict(patch_counts)}")

    original_outputs = tuple(int(value) for value in authority["factory_dag"]["outputs"])
    output_names_by_old_id = {
        TARGET_OLD_IDS[name]: name for name in ("S3", "S4", "S5")
    }
    output_patch_counts: Counter[str] = Counter()
    output_ids: list[int] = []
    for old_id in original_outputs:
        name = output_names_by_old_id.get(old_id)
        if name is None:
            output_ids.append(old_id)
        else:
            output_ids.append(target_node_ids[name])
            output_patch_counts[name] += 1
    if output_patch_counts != Counter({"S3": 1, "S4": 1, "S5": 1}):
        raise RuntimeError("primary-output patch count changed")

    rank: dict[int, int] = {
        int(node["id"]): index for index, node in enumerate(original_nodes)
    }
    rank.update(
        {node_id: len(original_nodes) + index for index, node_id in enumerate(generated_ids)}
    )
    ordered_ids = stable_topological_order(nodes, output_ids, rank)
    live_ids = set(ordered_ids)
    dead_shell = sorted(shell_ids - live_ids)
    dead_generated = sorted(set(generated_ids) - live_ids)
    if dead_shell or dead_generated:
        raise RuntimeError(
            f"graft produced dead nodes: shell={dead_shell[:8]}, generated={dead_generated[:8]}"
        )
    ordered_nodes = annotate_nodes(nodes, ordered_ids)
    annotated = {int(node["id"]): node for node in ordered_nodes}

    _states, metrics, replay = support.evaluate_nodes(tuple(ordered_nodes), tuple(output_ids))
    semantic = replay["semantic"]
    if semantic["mismatch_union_count"]:
        raise RuntimeError(f"full replay has truth mismatches: {semantic}")
    if semantic["conflict_assignment_count"]:
        raise RuntimeError(f"full replay has BUS conflicts: {semantic}")
    if any(semantic["z_assignment_count_by_output"]):
        raise RuntimeError(f"full replay has undriven primary outputs: {semantic}")
    expected_complete_gate = 63 + joint_gate
    if int(metrics["gate"]) != expected_complete_gate:
        raise RuntimeError(
            f"complete gate {metrics['gate']} != fixed shell 63 + joint {joint_gate}"
        )
    if max_gate is not None and int(metrics["gate"]) > max_gate:
        raise RuntimeError(f"complete gate {metrics['gate']} exceeds limit {max_gate}")
    if int(metrics["delay"]) > max_delay:
        raise RuntimeError(f"complete delay {metrics['delay']} exceeds limit {max_delay}")
    if max_energy is not None and int(metrics["energy"]) > max_energy:
        raise RuntimeError(f"complete energy {metrics['energy']} exceeds limit {max_energy}")
    for name, deadline in TARGET_DEADLINES.items():
        actual = int(annotated[target_node_ids[name]]["arrival"])
        if actual > deadline:
            raise RuntimeError(f"grafted target {name}@{actual} misses deadline {deadline}")

    hash_payload: dict[str, Any] = {
        "outputs": output_ids,
        "nodes": ordered_nodes,
        "live_node_count": len(ordered_nodes),
    }
    hash_payload["sha256"] = canonical_sha256(hash_payload)
    old_bus_ids = [
        int(node["id"]) for node in original_nodes if str(node["op"]) == "BUS"
    ]
    new_bus_ids = [
        node_id for node_id in generated_ids if str(annotated[node_id]["op"]) == "BUS"
    ]
    all_bus_ids = [
        int(node["id"]) for node in ordered_nodes if str(node["op"]) == "BUS"
    ]
    payload: dict[str, Any] = {
        "schema": "tc-byte-adder-bit35-joint-graft-v1",
        "status": "sat",
        "family": "authoritative 80/7 shell plus verified bit3:5 joint exact certificate",
        "source": {
            "authoritative_dag": portable(authority_path),
            "authoritative_dag_sha256": file_sha256(authority_path),
            "authoritative_factory_dag_sha256": authority["factory_dag"]["sha256"],
            "cut_audit": portable(cut_audit_path),
            "cut_audit_sha256": file_sha256(cut_audit_path),
            "certificate": portable(certificate_path),
            "certificate_sha256": file_sha256(certificate_path),
            "independent_96_row_verification": portable(independent_verification_path),
            "independent_96_row_verification_sha256": file_sha256(
                independent_verification_path
            ),
            "graft_script": portable(Path(__file__)),
            "graft_script_sha256": file_sha256(Path(__file__)),
            "full_replay_support": portable(REPLAY_SUPPORT),
            "full_replay_support_sha256": file_sha256(REPLAY_SUPPORT),
        },
        "cut": {
            "removed_node_ids": list(EXPECTED_REGION_IDS),
            "removed_weighted_gate": 17,
            "retained_shell_node_count": len(shell_ids),
            "retained_shell_gate": shell_gate,
            "external_node_patch_counts": {
                str(key): value for key, value in sorted(patch_counts.items())
            },
            "primary_output_patch_counts": dict(sorted(output_patch_counts.items())),
        },
        "certificate_accounting": {
            "schema": certificate["schema"],
            "gate_bound": int(certificate["gate_bound"]),
            "components": len(network),
            "weighted_gate": joint_gate,
            "switches": switch_count,
            "xors": xor_count,
            "truth_domain_rows": 96,
            "truth_domain_sha256": TRUTH_DOMAIN_SHA256,
            "independent_verification_status": independent["status"],
        },
        "translation": {
            "source_names": list(SOURCE_NAMES),
            "source_node_ids": {
                SOURCE_NAMES[index]: source_node_ids[index]
                for index in range(source_count)
                if index in source_node_ids
            },
            "target_old_node_ids": TARGET_OLD_IDS,
            "target_node_ids": target_node_ids,
            "target_arrivals": {
                name: int(annotated[node_id]["arrival"])
                for name, node_id in target_node_ids.items()
            },
            "target_deadlines": TARGET_DEADLINES,
            "generated_node_ids": generated_ids,
            "generated_node_count": len(generated_ids),
            "generated_kind_counts": dict(sorted(generated_kind_counts.items())),
            "switch_source_groups": [
                {
                    "certificate_sources": list(group),
                    "factory_bus_node_id": switch_bus_nodes[group],
                }
                for group in groups
            ],
            "switch_group_count": len(groups),
            "switch_component_count": switch_count,
            "node_id_policy": "new nodes in decoded demand order after max authoritative node ID",
        },
        "metrics": metrics,
        "semantic": semantic,
        "physical": {
            "authoritative_bus_node_ids": old_bus_ids,
            "removed_authoritative_bus_node_ids": sorted(region_ids.intersection(old_bus_ids)),
            "retained_authoritative_bus_node_ids": sorted(set(old_bus_ids) - region_ids),
            "new_bus_node_ids": new_bus_ids,
            "grafted_bus_node_ids": all_bus_ids,
            "partial_driver_reuse_possible": False,
            "physical_net_partition_violation_count": 0,
            "reason": "certificate partition passed independently and each disjoint Switch source group maps to one owned BUS node",
        },
        "dead_node_audit": {
            "dead_shell_node_count": 0,
            "dead_generated_node_count": 0,
            "reachable_node_count": len(ordered_nodes),
            "serialized_node_count": len(ordered_nodes),
        },
        "authority_review": {
            "metrics": authority_review["metrics"],
            "semantic": authority_review["semantic"],
            "byte_hash_pinned": True,
        },
        "full_replay": {
            "variables": 17,
            "rows": 1 << 17,
            "complete_u8_u8_u1": True,
            "mismatch_union_count": semantic["mismatch_union_count"],
            "conflict_assignment_count": semantic["conflict_assignment_count"],
            "primary_output_z_counts": semantic["z_assignment_count_by_output"],
            "output_vector_sha256": semantic["output_vector_sha256"],
        },
        "factory_dag": hash_payload,
    }
    support.validate_top_level(payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dag", type=Path, default=AUTHORITATIVE_DAG)
    parser.add_argument("--cut-audit", type=Path, default=CUT_AUDIT)
    parser.add_argument("--certificate", type=Path, default=DEFAULT_CERTIFICATE)
    parser.add_argument(
        "--independent-verification", type=Path, default=DEFAULT_INDEPENDENT_VERIFY
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--max-gate", type=int)
    parser.add_argument("--max-delay", type=int, default=7)
    parser.add_argument("--max-energy", type=int)
    args = parser.parse_args()

    first = build(
        args.dag,
        args.cut_audit,
        args.certificate,
        args.independent_verification,
        max_gate=args.max_gate,
        max_delay=args.max_delay,
        max_energy=args.max_energy,
    )
    second = build(
        args.dag,
        args.cut_audit,
        args.certificate,
        args.independent_verification,
        max_gate=args.max_gate,
        max_delay=args.max_delay,
        max_energy=args.max_energy,
    )
    first_bytes = (json.dumps(first, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    second_bytes = (json.dumps(second, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    if first_bytes != second_bytes:
        raise RuntimeError("deterministic rebuild mismatch")
    output_sha = atomic_write(args.output.resolve(), first)
    summary = {
        "output": str(args.output.resolve()),
        "sha256": output_sha,
        "certificate_sha256": first["source"]["certificate_sha256"],
        "independent_96_row_verification_sha256": first["source"][
            "independent_96_row_verification_sha256"
        ],
        "metrics": first["metrics"],
        "semantic": first["semantic"],
        "target_node_ids": first["translation"]["target_node_ids"],
        "target_arrivals": first["translation"]["target_arrivals"],
        "full_replay_rows": first["full_replay"]["rows"],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
