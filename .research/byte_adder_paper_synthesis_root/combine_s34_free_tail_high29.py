"""Compose an S3/S4-free tail witness into a standard high29 witness.

The tail solver treats seven already-paid ordinary S3/S4 nodes as free input
signals.  This combiner restores those nodes to their real component sources,
then independently replays the complete physical network.  A relaxed-interface
SAT is accepted only if the merged network passes global BUS partition,
liveness, Z/conflict, truth-table, cost, and recursive timing checks.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
from typing import Iterable


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PHYSICAL_PATH = ROOT / ".research/byte_adder_phase_shortcut_restart/physical_exact.py"
S34_DEFAULT = (
    ROOT
    / ".research/byte_adder_phase_shortcut_restart/s34_g11_d5_joint_exact.json"
)
EXPECTED_S34_SHA256 = (
    "69b0e3f1b6300da157de50f3b256f487211e9a141a0502cc71d476a895d48a36"
)
STANDARD_SCHEMA = "exact-fast-negative-physical-shard-v2"
STANDARD_DOMAIN = "s34567c8_leaf"
TAIL_DOMAIN = "s567c8_s34_free"
FULL_OUTPUTS = ("S3", "S4", "S5", "S6", "S7", "C8")
TAIL_OUTPUTS = ("S5", "S6", "S7", "C8")
KINDS = ("NOT", "AND", "OR", "NAND", "NOR", "XOR", "SWITCH")
COST = {"NOT": 1, "AND": 1, "OR": 1, "NAND": 1, "NOR": 1, "XOR": 3, "SWITCH": 2}
DELAY = {"NOT": 1, "AND": 1, "OR": 1, "NAND": 1, "NOR": 1, "XOR": 2, "SWITCH": 1}
ZERO_FIELDS = (
    "mismatch_count",
    "bus_conflict_count",
    "undriven_output_count",
    "physical_net_partition_violation_count",
    "depth_upper_bound_violation_count",
    "output_deadline_violation_count",
)


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


physical = _load_module("combine_s34_free_physical", PHYSICAL_PATH)


def load_witness(
    path: Path,
    *,
    outputs: tuple[str, ...],
    gate: int,
    domain: str | None = None,
) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("status") != "sat":
        raise ValueError(f"witness is not SAT: {path}")
    if tuple(payload.get("output_names", ())) != outputs:
        raise ValueError(f"unexpected witness outputs: {path}")
    if domain is not None and payload.get("domain") != domain:
        raise ValueError(f"unexpected witness domain: {path}")
    if int(payload.get("actual_gate", -1)) != gate:
        raise ValueError(f"unexpected witness gate cost: {path}")
    verification = payload.get("verification", {})
    if any(int(verification.get(field, -1)) for field in ZERO_FIELDS):
        raise ValueError(f"unclean witness verification: {path}")
    return payload


def remap_network(
    payload: dict[str, object],
    free_map: dict[str, int],
    *,
    next_source: int,
    standard_source_count: int,
) -> tuple[
    list[dict[str, object]],
    list[list[int]],
    dict[int, int],
    int,
]:
    local_free = list(payload["free_sources"])
    local_to_global: dict[int, int] = {}
    for local, name in enumerate(local_free):
        if name not in free_map:
            raise ValueError(f"unmapped free source {name!r}")
        local_to_global[local] = free_map[name]

    network: list[dict[str, object]] = []
    for expected_slot, item in enumerate(payload["network"]):
        if int(item["slot"]) != expected_slot:
            raise ValueError("source witness slots are not contiguous")
        local_source = int(item["source"])
        if local_source != len(local_free) + expected_slot:
            raise ValueError("source witness numbering is not canonical")
        kind = str(item["kind"])
        if kind not in COST:
            raise ValueError(kind)
        try:
            left = sorted(local_to_global[int(source)] for source in item["left_bus"])
            right = sorted(local_to_global[int(source)] for source in item["right_bus"])
        except KeyError as exc:
            raise ValueError("forward or unknown local source") from exc
        global_slot = next_source - standard_source_count
        network.append(
            {
                "slot": global_slot,
                "source": next_source,
                "kind": kind,
                "left_bus": left,
                "right_bus": right,
                "cost": COST[kind],
                "depth_upper_bound": int(item["depth_upper_bound"]),
            }
        )
        local_to_global[local_source] = next_source
        next_source += 1
    output_buses = [
        sorted(local_to_global[int(source)] for source in bus)
        for bus in payload["output_buses"]
    ]
    return network, output_buses, local_to_global, next_source


def build_s34_context(s34: dict[str, object]):
    domain = physical.domain_s34567c8_leaf()
    standard_names = (*domain.names, "0", "1")
    free_map = {name: index for index, name in enumerate(standard_names)}
    source_count = len(standard_names)
    network, outputs, local_map, next_source = remap_network(
        s34,
        free_map,
        next_source=source_count,
        standard_source_count=source_count,
    )
    if len(network) != 9:
        raise ValueError("S3/S4 witness no longer has nine components")
    if [item["kind"] for item in network[:7]] != [
        "NOR", "NAND", "AND", "AND", "OR", "OR", "NAND"
    ]:
        raise ValueError("S3/S4 ordinary source interface changed")
    if [item["kind"] for item in network[7:]] != ["SWITCH", "SWITCH"]:
        raise ValueError("S3/S4 Switch tail changed")
    local_source_count = len(s34["free_sources"])
    exported = {
        f"s34_u{slot}": local_map[local_source_count + slot]
        for slot in range(7)
    }
    return domain, standard_names, network, outputs, exported, next_source


def build_tail_free_map(
    standard_names: Iterable[str], exported: dict[str, int]
) -> dict[str, int]:
    result = {name: index for index, name in enumerate(standard_names)}
    overlap = set(result).intersection(exported)
    if overlap:
        raise ValueError(f"exported names collide with paid sources: {overlap}")
    result.update(exported)
    return result


def _audit_structure(
    network: list[dict[str, object]],
    output_buses: list[list[int]],
    *,
    source_count: int,
    source_arrivals: list[int],
) -> dict[str, object]:
    arrivals = list(source_arrivals)
    switch_sources: set[int] = set()
    all_buses: list[tuple[str, tuple[int, ...]]] = []
    errors: list[str] = []
    gate = switches = xors = 0
    depth_violations = 0

    for slot, item in enumerate(network):
        source = int(item["source"])
        kind = str(item["kind"])
        if int(item["slot"]) != slot or source != source_count + slot:
            errors.append(f"slot/source sequence violation at {slot}")
        if kind not in COST:
            errors.append(f"unknown kind at {slot}: {kind}")
            continue
        buses = (
            ("left", tuple(int(value) for value in item["left_bus"])),
            ("right", tuple(int(value) for value in item["right_bus"])),
        )
        for side, bus in buses:
            allow_empty = kind == "NOT" and side == "right"
            if not bus and not allow_empty:
                errors.append(f"empty {side} bus at {slot}")
            if bus != tuple(sorted(set(bus))):
                errors.append(f"noncanonical {side} bus at {slot}")
            if any(value < 0 or value >= source for value in bus):
                errors.append(f"forward source in {side} bus at {slot}")
            if len(bus) > 1 and any(value not in switch_sources for value in bus):
                errors.append(f"non-Switch resolved bus at {slot}.{side}")
            if bus:
                all_buses.append((f"slot{slot}.{side}", bus))
        left, right = buses[0][1], buses[1][1]
        if kind == "NOT" and right:
            errors.append(f"NOT has a nonempty right bus at {slot}")
        inputs = (*left, *right)
        if inputs and all(value < len(arrivals) for value in inputs):
            arrival = max(arrivals[value] for value in inputs) + DELAY[kind]
        else:
            arrival = 10**9
        arrivals.append(arrival)
        claimed = int(item["depth_upper_bound"])
        if arrival > claimed or claimed > 5:
            depth_violations += 1
        gate += COST[kind]
        switches += kind == "SWITCH"
        xors += kind == "XOR"
        if kind == "SWITCH":
            switch_sources.add(source)

    for index, bus_raw in enumerate(output_buses):
        bus = tuple(int(value) for value in bus_raw)
        if not bus or bus != tuple(sorted(set(bus))):
            errors.append(f"invalid output bus {index}")
        if any(value < 0 or value >= len(arrivals) for value in bus):
            errors.append(f"unknown output source {index}")
        if len(bus) > 1 and any(value not in switch_sources for value in bus):
            errors.append(f"non-Switch resolved output bus {index}")
        all_buses.append((f"output{index}", bus))

    partition: list[dict[str, object]] = []
    for index, (left_name, left) in enumerate(all_buses):
        left_set = set(left)
        for right_name, right in all_buses[index + 1 :]:
            right_set = set(right)
            if left_set.intersection(right_set) and left_set != right_set:
                partition.append(
                    {"left": left_name, "right": right_name, "overlap": sorted(left_set & right_set)}
                )
    used = {source for _label, bus in all_buses for source in bus}
    dead = [source for source in range(source_count, len(arrivals)) if source not in used]
    output_arrivals = [
        max(arrivals[source] for source in bus) if bus else 10**9
        for bus in output_buses
    ]
    return {
        "errors": errors,
        "gate": gate,
        "switches": switches,
        "xors": xors,
        "ordinary": len(network) - switches - xors,
        "node_arrivals": arrivals[source_count:],
        "actual_output_arrivals": output_arrivals,
        "actual_max_delay": max(output_arrivals, default=0),
        "depth_upper_bound_violation_count": depth_violations,
        "output_deadline_violation_count": sum(value > 5 for value in output_arrivals),
        "physical_net_partition_violation_count": len(partition),
        "physical_net_partition_violations": partition,
        "dead_component_output_count": len(dead),
        "dead_component_outputs": dead,
    }


def _audit_semantics(
    domain,
    network: list[dict[str, object]],
    output_buses: list[list[int]],
    output_names: tuple[str, ...],
) -> dict[str, object]:
    rows = domain.rows
    source_columns = [tuple(column) for column in domain.columns]
    source_columns.extend(((False,) * rows, (True,) * rows))
    target_indices = tuple(domain.output_names.index(name) for name in output_names)
    targets = tuple(domain.targets[index] for index in target_indices)
    mismatch_by_output = [0] * len(output_names)
    undriven_by_output = [0] * len(output_names)
    conflict = 0

    for case in range(rows):
        values = [column[case] for column in source_columns]
        drivens = [True] * len(source_columns)

        def resolve(bus: list[int]) -> tuple[bool, bool]:
            nonlocal conflict
            active = {values[source] for source in bus if drivens[source]}
            if len(active) > 1:
                conflict += 1
                return False, True
            if not active:
                return False, False
            return next(iter(active)), True

        for item in network:
            left, _left_driven = resolve(item["left_bus"])
            right, _right_driven = resolve(item["right_bus"])
            kind = item["kind"]
            if kind == "NOT":
                value, driven = not left, True
            elif kind == "AND":
                value, driven = left and right, True
            elif kind == "OR":
                value, driven = left or right, True
            elif kind == "NAND":
                value, driven = not (left and right), True
            elif kind == "NOR":
                value, driven = not (left or right), True
            elif kind == "XOR":
                value, driven = left ^ right, True
            elif kind == "SWITCH":
                value, driven = left and right, left
            else:  # guarded by the structural audit
                value, driven = False, False
            values.append(bool(value))
            drivens.append(bool(driven))
        for output, (bus, target) in enumerate(zip(output_buses, targets, strict=True)):
            value, driven = resolve(bus)
            wanted = bool((target >> case) & 1)
            mismatch_by_output[output] += value != wanted
            undriven_by_output[output] += not driven
    return {
        "mismatch_count_by_output": mismatch_by_output,
        "mismatch_count": sum(mismatch_by_output),
        "bus_conflict_count": conflict,
        "undriven_output_count_by_output": undriven_by_output,
        "undriven_output_count": sum(undriven_by_output),
    }


def combine(s34_path: Path, tail_path: Path) -> dict[str, object]:
    if digest(s34_path) != EXPECTED_S34_SHA256:
        raise ValueError("S3/S4 witness SHA256 changed")
    s34 = load_witness(s34_path, outputs=("S3", "S4"), gate=11)
    tail = load_witness(
        tail_path,
        outputs=TAIL_OUTPUTS,
        gate=18,
        domain=TAIL_DOMAIN,
    )
    provenance = tail.get("free_intermediate_provenance", {})
    if (
        provenance.get("s34_witness", {}).get("sha256") != EXPECTED_S34_SHA256
        or provenance.get("u6_equals_s3") is not True
    ):
        raise ValueError("tail lacks the exact S3/S4 free-source provenance")
    if tail.get("dependency_sha256") != physical.dependency_sha256():
        raise ValueError("tail SAT dependency hashes changed")

    domain, standard_names, first_network, first_outputs, exported, next_source = (
        build_s34_context(s34)
    )
    source_count = len(standard_names)
    tail_map = build_tail_free_map(standard_names, exported)
    second_network, second_outputs, _tail_local_map, next_source = remap_network(
        tail,
        tail_map,
        next_source=next_source,
        standard_source_count=source_count,
    )
    del next_source
    network = [*first_network, *second_network]
    output_buses = [*first_outputs, *second_outputs]
    source_arrivals = [domain.arrivals.get(name, 0) for name in standard_names]
    structure = _audit_structure(
        network,
        output_buses,
        source_count=source_count,
        source_arrivals=source_arrivals,
    )
    semantics = _audit_semantics(domain, network, output_buses, FULL_OUTPUTS)
    verification = {
        **semantics,
        "physical_net_partition_violation_count": structure[
            "physical_net_partition_violation_count"
        ],
        "physical_net_partition_violations": structure[
            "physical_net_partition_violations"
        ],
        "dead_component_output_count": structure["dead_component_output_count"],
        "dead_component_outputs": structure["dead_component_outputs"],
        "actual_output_arrivals": structure["actual_output_arrivals"],
        "actual_max_delay": structure["actual_max_delay"],
        "depth_upper_bound_violation_count": structure[
            "depth_upper_bound_violation_count"
        ],
        "output_deadline_violation_count": structure[
            "output_deadline_violation_count"
        ],
        "structural_errors": structure["errors"],
    }
    actual_gate = int(structure["gate"])
    switches = int(structure["switches"])
    xors = int(structure["xors"])
    failures = (
        semantics["mismatch_count"]
        + semantics["bus_conflict_count"]
        + semantics["undriven_output_count"]
        + structure["physical_net_partition_violation_count"]
        + structure["dead_component_output_count"]
        + structure["depth_upper_bound_violation_count"]
        + structure["output_deadline_violation_count"]
        + len(structure["errors"])
        + (actual_gate != 29)
    )
    payload: dict[str, object] = {
        "schema": STANDARD_SCHEMA,
        "status": "sat" if failures == 0 else "invalid",
        "domain": STANDARD_DOMAIN,
        "rows": domain.rows,
        "output_names": FULL_OUTPUTS,
        "free_sources": standard_names,
        "source_arrivals": dict(zip(standard_names, source_arrivals, strict=True)),
        "gate_bound": 29,
        "max_delay": 5,
        "components": len(network),
        "ordinary": len(network) - switches - xors,
        "exact_switches": switches,
        "exact_xors": xors,
        "fixed_kinds": [item["kind"] for item in network],
        "solver": "composed-s34-free-tail",
        "variables": int(tail.get("variables", 0)),
        "clauses": int(tail.get("clauses", 0)),
        "solve_seconds": float(tail.get("solve_seconds", 0.0)),
        "physical_nets": True,
        "public_outputs_must_be_driven": True,
        "shard": tail.get("shard"),
        "timer_errors": tail.get("timer_errors", []),
        "dependency_sha256": physical.dependency_sha256(),
        "actual_gate": actual_gate,
        "network": network,
        "output_buses": output_buses,
        "verification": verification,
        "composition": {
            "schema": "s34-free-tail-composition-v1",
            "s34_witness": {"path": str(s34_path), "sha256": digest(s34_path)},
            "tail_witness": {"path": str(tail_path), "sha256": digest(tail_path)},
            "physical_worker_sha256": digest(PHYSICAL_PATH),
            "combiner_sha256": digest(Path(__file__).resolve()),
            "exported_source_mapping": exported,
            "relaxed_interface_rechecked_globally": True,
        },
    }
    structural = {
        "free_sources": standard_names,
        "network": network,
        "output_buses": output_buses,
    }
    payload["structural_sha256"] = sha256(
        json.dumps(structural, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--s34", type=Path, default=S34_DEFAULT)
    parser.add_argument("--tail", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = combine(args.s34.resolve(), args.tail.resolve())
    encoded = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(encoded, encoding="utf-8")
    print(
        json.dumps(
            {
                "status": payload["status"],
                "actual_gate": payload["actual_gate"],
                "actual_max_delay": payload["verification"]["actual_max_delay"],
                "verification": payload["verification"],
                "output": str(args.output),
                "sha256": digest(args.output),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if payload["status"] == "sat" else 1


if __name__ == "__main__":
    raise SystemExit(main())
