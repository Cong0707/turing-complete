#!/usr/bin/env python3
"""Normalize any complete Byte Adder Factory DAG into an auditable ledger.

The ledger is architecture-neutral within the reviewed Factory primitive ABI.
It embeds the complete candidate payload and records independently recomputed
contracts for primitive topology, truth vectors, recursive arrival, driven/Z
state, BUS ownership, and the routing checks required before deployment.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
AUDITOR_PATH = HERE / "audit_factory_candidate.py"
MATERIALIZER_PATH = (
    ROOT / ".research/byte_adder_builder_layout_agent/materialize_factory_dag.py"
)
SCHEMA = "byte-adder-complete-candidate-ledger-v1"
ROWS = 1 << 17
STATE_BYTES = ROWS // 8
HEX64 = set("0123456789abcdef")


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


auditor = _load_module("generic_candidate_ledger_auditor", AUDITOR_PATH)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def canonical_sha(payload: object) -> str:
    encoded = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode()
    return sha256(encoded).hexdigest()


def portable(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(resolved).replace("\\", "/")


def rooted(path: str | Path) -> Path:
    value = Path(path)
    return value.resolve() if value.is_absolute() else (ROOT / value).resolve()


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_bytes())
    require(isinstance(payload, dict), f"JSON root is not an object: {path}")
    return payload


def _primitive_records(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    records = []
    for node in nodes:
        record: dict[str, Any] = {
            "id": int(node["id"]),
            "op": str(node["op"]),
            "args": [int(value) for value in node.get("args", ())],
            "cost": int(node["cost"]),
            "step_delay": int(node["step_delay"]),
        }
        if node.get("op") in {"INPUT", "CONST"}:
            record["label"] = str(node.get("label", ""))
        if node.get("op") == "BUS":
            record["resolved_network"] = node.get(
                "resolved_network", f"bus_node_{int(node['id'])}"
            )
            record["drivers"] = [
                {
                    "enable": int(driver["enable"]),
                    "data": int(driver["data"]),
                    "owner": str(driver["owner"]),
                }
                for driver in node.get("drivers", ())
            ]
        records.append(record)
    return records


def _state_contract(
    nodes: list[dict[str, Any]], states: dict[int, Any], outputs: list[int]
) -> dict[str, Any]:
    stream = sha256(b"byte-adder-complete-node-value-driven-state-v1\0")
    profiles = []
    for node in nodes:
        node_id = int(node["id"])
        state = states[node_id]
        stream.update(node_id.to_bytes(8, "little", signed=False))
        stream.update(len(state.bits).to_bytes(4, "little", signed=False))
        value_hash = sha256()
        for bits in state.bits:
            encoded = int(bits).to_bytes(STATE_BYTES, "little", signed=False)
            stream.update(encoded)
            value_hash.update(encoded)
        driven = int(state.driven).to_bytes(STATE_BYTES, "little", signed=False)
        conflict = int(state.conflict).to_bytes(STATE_BYTES, "little", signed=False)
        stream.update(driven)
        stream.update(conflict)
        stream.update(int(state.depth).to_bytes(4, "little", signed=False))
        profiles.append(
            {
                "id": node_id,
                "value_sha256": value_hash.hexdigest(),
                "driven_assignment_count": int(state.driven).bit_count(),
                "z_assignment_count": ROWS - int(state.driven).bit_count(),
                "conflict_assignment_count": int(state.conflict).bit_count(),
                "arrival": int(state.depth),
            }
        )
    return {
        "rows": ROWS,
        "node_state_sha256": stream.hexdigest(),
        "node_profiles": profiles,
        "output_profiles": [profiles[[item["id"] for item in profiles].index(node)] for node in outputs],
        "all_primary_outputs_driven": all(states[node].driven.bit_count() == ROWS for node in outputs),
    }


def _owner_contract(nodes: list[dict[str, Any]]) -> dict[str, Any]:
    buses = []
    owners = set()
    for node in nodes:
        if node.get("op") != "BUS":
            continue
        node_id = int(node["id"])
        owner = str(node.get("resolved_network", f"bus_node_{node_id}"))
        require(owner not in owners, f"duplicate BUS owner: {owner}")
        owners.add(owner)
        drivers = node.get("drivers")
        if drivers is None:
            args = [int(value) for value in node["args"]]
            drivers = [
                {"enable": args[index], "data": args[index + 1], "owner": owner}
                for index in range(0, len(args), 2)
            ]
        normalized = [
            {
                "enable": int(driver["enable"]),
                "data": int(driver["data"]),
                "owner": str(driver["owner"]),
            }
            for driver in drivers
        ]
        require(all(driver["owner"] == owner for driver in normalized), "BUS driver owner changed")
        buses.append({"node": node_id, "owner": owner, "drivers": normalized})
    return {
        "bus_count": len(buses),
        "driver_count": sum(len(bus["drivers"]) for bus in buses),
        "owner_partition_sha256": canonical_sha(buses),
        "owners_unique": True,
        "expected_physical_partition_violation_count": 0,
        "buses": buses,
    }


def _routing_contract() -> dict[str, Any]:
    policy = {
        "materializer": {
            "path": portable(MATERIALIZER_PATH),
            "sha256": digest(MATERIALIZER_PATH),
        },
        "independent_auditor": {
            "path": portable(AUDITOR_PATH),
            "sha256": digest(AUDITOR_PATH),
        },
        "required_v15_round_trip_byte_identical": True,
        "required_deterministic_rebuild_byte_identical": True,
        "required_native_com_add_count": 0,
        "required_connectivity_zero_fields": [
            "unconnected_pin_count",
            "unsafe_multi_driver_network_count",
            "undriven_network_count",
            "sinkless_network_count",
            "width_mismatch_network_count",
            "cycle_component_count",
        ],
        "required_geometry_zero_fields": [
            "unsupported_component_kind_count",
            "component_overlap_cell_count",
            "wire_collision_count",
            "wire_interior_pin_contact_count",
        ],
        "formal_deployment_scope": "formal-save-only",
        "backup_allowed": False,
        "game_launch_allowed": False,
    }
    return {**policy, "routing_policy_sha256": canonical_sha(policy)}


def _contracts(
    payload: dict[str, Any], states: dict[int, Any], review: dict[str, Any]
) -> dict[str, Any]:
    dag = payload["factory_dag"]
    nodes = list(dag["nodes"])
    outputs = [int(value) for value in dag["outputs"]]
    primitives = _primitive_records(nodes)
    arrivals = [
        {"id": int(node["id"]), "arrival": int(node["arrival"])} for node in nodes
    ]
    return {
        "component_primitives": {
            "supported_ops": sorted({str(node["op"]) for node in nodes}),
            "component_count": len(nodes),
            "primitive_sha256": canonical_sha(primitives),
            "records": primitives,
        },
        "truth": {
            "rows": ROWS,
            "output_names": [*[f"S{bit}" for bit in range(8)], "C8"],
            "output_nodes": outputs,
            "output_vector_sha256": review["output_vector_sha256"],
            "mismatch_count": 0,
        },
        "arrival": {
            "output_arrivals": list(payload["metrics"]["output_arrivals"]),
            "global_delay": int(payload["metrics"]["delay"]),
            "arrival_sha256": canonical_sha(arrivals),
            "records": arrivals,
        },
        "driven_z": _state_contract(nodes, states, outputs),
        "owner_partition": _owner_contract(nodes),
        "routing": _routing_contract(),
        "score": {
            "gate": int(review["gate"]),
            "delay": int(review["delay"]),
            "energy": int(review["energy"]),
            "energy_equals_gate_times_delay": True,
        },
    }


def _stable_review(review: dict[str, Any]) -> dict[str, Any]:
    """Drop only the enclosing JSON byte hash; source.sha256 owns that claim."""

    return {key: value for key, value in review.items() if key != "dag_sha256"}


def _review_embedded(payload: dict[str, Any]) -> tuple[dict[int, Any], dict[str, Any]]:
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        suffix=".json",
        prefix="generic_candidate_ledger_",
        dir=HERE,
        delete=False,
    ) as handle:
        temporary = Path(handle.name)
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    try:
        _payload, _by_id, states, review = auditor.review_dag(temporary)
        return states, review
    finally:
        temporary.unlink(missing_ok=True)


def build_ledger(candidate_path: Path) -> dict[str, Any]:
    candidate_path = candidate_path.resolve()
    payload, _by_id, states, review = auditor.review_dag(candidate_path)
    contracts = _contracts(payload, states, review)
    core: dict[str, Any] = {
        "schema": SCHEMA,
        "status": "ready",
        "complete_candidate": True,
        "source": {
            "path": portable(candidate_path),
            "sha256": digest(candidate_path),
            "schema": payload.get("schema"),
            "factory_dag_sha256": payload["factory_dag"]["sha256"],
        },
        "candidate_payload": payload,
        "contracts": contracts,
        "independent_review": _stable_review(review),
    }
    core["ledger_sha256"] = canonical_sha(core)
    return json.loads(json.dumps(core, ensure_ascii=False))


def validate_ledger(ledger_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    ledger_path = ledger_path.resolve()
    ledger = load_json(ledger_path)
    require(ledger.get("schema") == SCHEMA, "unsupported generic candidate ledger schema")
    require(ledger.get("status") == "ready", "candidate ledger is not ready")
    require(ledger.get("complete_candidate") is True, "ledger is not a complete candidate")
    serialized_hash = ledger.get("ledger_sha256")
    core = dict(ledger)
    core.pop("ledger_sha256", None)
    require(serialized_hash == canonical_sha(core), "candidate ledger SHA changed")

    payload = ledger.get("candidate_payload")
    require(isinstance(payload, dict), "embedded candidate payload missing")
    states, review = _review_embedded(payload)
    recomputed = _contracts(payload, states, review)
    require(ledger.get("contracts") == recomputed, "candidate ledger contracts changed")
    require(
        ledger.get("independent_review") == _stable_review(review),
        "candidate ledger review changed",
    )

    source = ledger.get("source")
    require(isinstance(source, dict), "candidate source certificate missing")
    source_path = rooted(str(source.get("path")))
    require(source_path.is_file(), f"candidate source is missing: {source_path}")
    require(source.get("sha256") == digest(source_path), "candidate source SHA changed")
    require(load_json(source_path) == payload, "embedded candidate differs from source")
    require(source.get("factory_dag_sha256") == payload["factory_dag"]["sha256"], "Factory DAG SHA changed")
    return ledger, review


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path = path.resolve()
    require(path.is_relative_to(HERE), f"ledger output is outside research line: {path}")
    require(not path.exists(), f"refusing to overwrite {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode()
    temporary.write_bytes(encoded)
    temporary.replace(path)
    require(path.read_bytes() == encoded, f"ledger write changed: {path}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    create = subparsers.add_parser("create")
    create.add_argument("candidate", type=Path)
    create.add_argument("--output", type=Path, required=True)
    verify = subparsers.add_parser("verify")
    verify.add_argument("ledger", type=Path)
    args = parser.parse_args(argv)
    if args.command == "create":
        ledger = build_ledger(args.candidate)
        write_json(args.output, ledger)
        result = {
            "status": "ready",
            "ledger": portable(args.output),
            "sha256": digest(args.output),
            "ledger_sha256": ledger["ledger_sha256"],
            "score": ledger["contracts"]["score"],
        }
    else:
        ledger, review = validate_ledger(args.ledger)
        result = {
            "status": "verified",
            "ledger": portable(args.ledger),
            "sha256": digest(args.ledger),
            "ledger_sha256": ledger["ledger_sha256"],
            "vectors_checked": review["vectors_checked"],
            "score": ledger["contracts"]["score"],
        }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
