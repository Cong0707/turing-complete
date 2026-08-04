#!/usr/bin/env python3
"""Compose a projected 729-row tail SAT into a production high30 witness.

The tail solver exposes six reviewed S3/S4 family nodes and two paid NOR
phases as free sources.  This intake tool restores all eleven paid prefix
components, remaps the projected tail onto the native 27-source D5 boundary,
and then inserts the two legacy constant indices required by the production
486-row witness ABI.  The constants are never referenced by the composed DAG.

Acceptance is deliberately redundant: the native witness is replayed over the
729-row value/driven quotient and the complete 2^17 domain, then the translated
production witness is independently replayed over 486 and 2^17 rows by the
fixed73 verifier.  Derived files are published only after every replay passes.
"""

from __future__ import annotations

import argparse
import copy
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import re
import sys
from typing import Any, Iterable


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TAIL_WORKER_PATH = (
    ROOT
    / ".research/byte_adder_phase_shortcut_restart/"
    "exact_tail729_with_s34_family1_two_phase_free.py"
)
NEGATIVE_VERIFIER_PATH = (
    ROOT
    / ".research/byte_adder_av_reduced_forward/"
    "verify_negative_high_d5_physical_witness.py"
)
PRODUCTION_VERIFIER_PATH = HERE / "verify_fixed73_high29_physical_witness.py"

TAIL_SCHEMA = "exact-s34-family1-two-phase-physical729-tail-v1"
TAIL_BASE_SCHEMA = "exact-negative-high-d5-physical-shard-v1"
TAIL_OUTPUTS = ("S5", "S6", "S7", "C8")
FULL_OUTPUTS = ("S3", "S4", *TAIL_OUTPUTS)
PREFIX_COMPONENTS = 11
PREFIX_GATE = 13
TAIL_GATE = 17
HIGH_GATE = 30
MAX_DELAY = 5
HEX64 = re.compile(r"[0-9a-f]{64}")
DECOMPOSITIONS = {
    (9, 8, 0),
    (10, 7, 0),
    (11, 6, 0),
    (12, 5, 0),
}


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


tail_worker = _load_module("tail729_high30_intake_worker", TAIL_WORKER_PATH)
negative = _load_module("tail729_high30_negative_verifier", NEGATIVE_VERIFIER_PATH)
production = _load_module("tail729_high30_production_verifier", PRODUCTION_VERIFIER_PATH)

COST = dict(production.EXACT_COST)
DELAY = dict(production.EXACT_DELAY)
NEGATIVE_SOURCES = tuple(negative.SOURCE_NAMES)
NEGATIVE_SOURCE_COUNT = len(NEGATIVE_SOURCES)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def portable(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(resolved).replace("\\", "/")


def normalized(payload: object) -> object:
    return json.loads(json.dumps(payload, ensure_ascii=False))


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_bytes())
    require(isinstance(payload, dict), f"JSON root is not an object: {path}")
    return payload


def certificate(path: Path) -> dict[str, str]:
    return {"path": portable(path), "sha256": digest(path)}


def _canonical_sides(
    kind: str, left: Iterable[int], right: Iterable[int]
) -> tuple[list[int], list[int]]:
    left_values = sorted(set(int(value) for value in left))
    right_values = sorted(set(int(value) for value in right))
    if kind == "NOT" or kind == "SWITCH":
        return left_values, right_values
    left_mask = sum(1 << source for source in left_values)
    right_mask = sum(1 << source for source in right_values)
    if left_mask < right_mask:
        return left_values, right_values
    return right_values, left_values


def build_prefix(profile: str) -> dict[str, Any]:
    require(profile in tail_worker.PHASE_PROFILES, f"unknown phase profile: {profile}")
    require(
        tuple(tail_worker.base.build_domain().names) == NEGATIVE_SOURCES,
        "native 729-row source ABI changed",
    )
    record = tail_worker._load_family_record()
    family = record["network"]
    local_names = (*tail_worker.base.physical.domain_s3456_leaf().names, "0", "1")
    global_by_name = {name: index for index, name in enumerate(NEGATIVE_SOURCES)}
    local_map: dict[int, int] = {
        index: global_by_name[name]
        for index, name in enumerate(local_names)
        if name not in {"0", "1"}
    }
    network: list[dict[str, Any]] = []

    def remap_bus(raw: object, label: str) -> list[int]:
        require(isinstance(raw, list), f"{label} is not a list")
        try:
            result = [local_map[int(source)] for source in raw]
        except (KeyError, TypeError, ValueError) as exc:
            raise RuntimeError(f"{label} uses a constant or unknown source") from exc
        require(result == sorted(set(result)), f"{label} is not canonical")
        return result

    for expected_slot, raw in enumerate(family):
        require(raw.get("slot") == expected_slot, "family slots are not contiguous")
        local_source = len(local_names) + expected_slot
        require(raw.get("source") == local_source, "family source numbering changed")
        kind = str(raw.get("kind"))
        require(kind in COST, f"unsupported family kind: {kind}")
        source = NEGATIVE_SOURCE_COUNT + expected_slot
        left = remap_bus(raw.get("left_bus"), f"family u{expected_slot}.left")
        right = remap_bus(raw.get("right_bus"), f"family u{expected_slot}.right")
        network.append(
            {
                "slot": expected_slot,
                "source": source,
                "kind": kind,
                "left_bus": left,
                "right_bus": right,
                "cost": COST[kind],
                "depth_upper_bound": int(raw["depth_upper_bound"]),
            }
        )
        local_map[local_source] = source

    output_buses = [
        remap_bus(bus, f"family output {index}")
        for index, bus in enumerate(record["output_buses"])
    ]
    arrivals = [negative.SOURCE_ARRIVALS[name] for name in NEGATIVE_SOURCES]
    for item in network:
        inputs = [*item["left_bus"], *item["right_bus"]]
        actual = max(arrivals[source] for source in inputs) + DELAY[item["kind"]]
        require(
            actual <= int(item["depth_upper_bound"]) <= MAX_DELAY,
            f"family timing changed at slot {item['slot']}",
        )
        arrivals.append(actual)

    phase_sources: dict[str, int] = {}
    phase_records: list[dict[str, Any]] = []
    for offset, (name, left_name, right_name) in enumerate(
        tail_worker.PHASE_PROFILES[profile]
    ):
        slot = len(network)
        require(slot == 9 + offset, "paid phase slot changed")
        left, right = _canonical_sides(
            "NOR", (global_by_name[left_name],), (global_by_name[right_name],)
        )
        source = NEGATIVE_SOURCE_COUNT + slot
        arrival = max(arrivals[value] for value in (*left, *right)) + DELAY["NOR"]
        item = {
            "slot": slot,
            "source": source,
            "kind": "NOR",
            "left_bus": left,
            "right_bus": right,
            "cost": COST["NOR"],
            "depth_upper_bound": arrival,
        }
        network.append(item)
        arrivals.append(arrival)
        phase_sources[name] = source
        phase_records.append({"name": name, **item})

    require(len(network) == PREFIX_COMPONENTS, "prefix component count changed")
    require(sum(item["cost"] for item in network) == PREFIX_GATE, "prefix gate changed")
    exported = {
        f"s34_family1_u{slot}": NEGATIVE_SOURCE_COUNT + slot
        for slot in tail_worker.EXPECTED_USEFUL_SLOTS
    }
    paid_sources = {**exported, **phase_sources}
    return {
        "network": network,
        "output_buses": output_buses,
        "paid_sources": paid_sources,
        "node_arrivals": arrivals[NEGATIVE_SOURCE_COUNT:],
        "family_record": record,
        "phase_records": phase_records,
    }


def validate_run(run_path: Path, tail_path: Path, tail: dict[str, Any]) -> dict[str, Any]:
    run = load_json(run_path)
    require(run.get("schema") == "tail729-high30-suffix-shard-run-v1", "run schema changed")
    require(run.get("status") == "sat", "run record is not SAT")
    require(run.get("returncode") == 0, "SAT run did not return zero")
    require(run.get("timed_out") is False, "SAT run is marked timed out")
    require(run.get("validation_errors") == [], "SAT run has validation errors")
    artifacts = run.get("artifacts")
    require(isinstance(artifacts, dict), "run artifact metadata missing")
    require(artifacts.get("result_sha256") == digest(tail_path), "run/result SHA mismatch")

    decomposition = run.get("decomposition")
    require(isinstance(decomposition, dict), "run decomposition missing")
    expected = {
        "gate_bound": TAIL_GATE,
        "components": tail.get("components"),
        "ordinary": tail.get("ordinary"),
        "switches": tail.get("exact_switches"),
        "xors": tail.get("exact_xors"),
    }
    require(decomposition == expected, "run/result decomposition mismatch")

    run_shard = run.get("suffix_shard")
    tail_shard = tail.get("shard")
    require(isinstance(run_shard, dict) and isinstance(tail_shard, dict), "shard metadata missing")
    for run_key, tail_key in (
        ("split_slots", "split_slots"),
        ("shard_count", "shard_count"),
        ("shard_index", "shard_index"),
        ("universe_count", "suffix_universe_count"),
        ("universe_sha256", "suffix_universe_sha256"),
    ):
        require(run_shard.get(run_key) == tail_shard.get(tail_key), f"shard mismatch: {run_key}")
    assigned = tail_shard.get("assigned_suffix_signatures")
    require(isinstance(assigned, list), "assigned suffix signatures missing")
    encoded = json.dumps(assigned, sort_keys=True, separators=(",", ":")).encode()
    require(run_shard.get("assigned_count") == len(assigned), "assigned suffix count mismatch")
    require(run_shard.get("assigned_sha256") == sha256(encoded).hexdigest(), "assigned suffix SHA mismatch")
    return run


def validate_tail(tail_path: Path, *, profile: str) -> tuple[dict[str, Any], Any, dict[str, Any]]:
    tail = load_json(tail_path)
    expected = {
        "schema": TAIL_SCHEMA,
        "base_schema": TAIL_BASE_SCHEMA,
        "status": "sat",
        "domain": negative.DOMAIN,
        "rows": negative.DOMAIN_ROWS,
        "boolean_value_rows": negative.BOOLEAN_ROWS,
        "physical_value_driven_rows": negative.DOMAIN_ROWS,
        "output_names": list(TAIL_OUTPUTS),
        "gate_bound": TAIL_GATE,
        "max_delay": MAX_DELAY,
        "constructive_constants": False,
        "physical_nets": True,
        "public_outputs_must_be_driven": True,
    }
    for key, value in expected.items():
        require(tail.get(key) == value, f"tail metadata mismatch at {key}")

    components = int(tail.get("components", -1))
    switches = int(tail.get("exact_switches", -1))
    xors = int(tail.get("exact_xors", -1))
    require((components, switches, xors) in DECOMPOSITIONS, "unexpected tail decomposition")
    require(tail.get("ordinary") == components - switches - xors, "tail ordinary count changed")
    require(tail.get("actual_gate") == TAIL_GATE, "tail actual gate is not 17")
    require(tail.get("extended_dependency_sha256") == tail_worker.dependency_sha256(), "tail dependency hashes changed")

    projected_domain, provenance = tail_worker.build_domain_with_provenance(profile)
    require(tuple(projected_domain.names) == tuple(tail.get("free_sources", ())), "tail free-source order changed")
    expected_arrivals = {
        name: projected_domain.arrivals[name] for name in projected_domain.names
    }
    require(tail.get("source_arrivals") == expected_arrivals, "tail source arrivals changed")
    require(normalized(provenance) == tail.get("free_source_projection"), "tail projection provenance changed")

    network = tail.get("network")
    output_buses = tail.get("output_buses")
    require(isinstance(network, list) and len(network) == components, "tail network length changed")
    require(isinstance(output_buses, list) and len(output_buses) == len(TAIL_OUTPUTS), "tail outputs missing")
    fixed_kinds = tail.get("fixed_kinds")
    require(isinstance(fixed_kinds, list) and len(fixed_kinds) == components, "tail fixed kinds missing")
    recomputed_gate = 0
    recomputed_switches = recomputed_xors = 0
    local_count = len(projected_domain.names)
    for slot, item in enumerate(network):
        require(isinstance(item, dict), f"tail slot {slot} is not an object")
        require(item.get("slot") == slot, "tail slots are not contiguous")
        require(item.get("source") == local_count + slot, "tail source numbering changed")
        kind = str(item.get("kind"))
        require(kind in COST and fixed_kinds[slot] in {"*", kind}, f"tail kind changed at {slot}")
        require(item.get("cost") == COST[kind], f"tail cost changed at {slot}")
        recomputed_gate += COST[kind]
        recomputed_switches += kind == "SWITCH"
        recomputed_xors += kind == "XOR"
    require(recomputed_gate == TAIL_GATE, "tail network cost differs from 17")
    require(recomputed_switches == switches and recomputed_xors == xors, "tail kind counts changed")

    verification = tail.get("verification")
    require(isinstance(verification, dict), "tail verification metadata missing")
    for field in (
        "mismatch_count",
        "bus_conflict_count",
        "undriven_output_count",
        "physical_net_partition_violation_count",
        "depth_upper_bound_violation_count",
        "output_deadline_violation_count",
    ):
        require(verification.get(field) == 0, f"tail failed {field}")
    require(int(verification.get("actual_max_delay", MAX_DELAY + 1)) <= MAX_DELAY, "tail exceeds D5")
    return tail, projected_domain, provenance


def remap_tail(
    tail: dict[str, Any], projected_names: tuple[str, ...], prefix: dict[str, Any]
) -> tuple[list[dict[str, Any]], list[list[int]]]:
    free_map = {name: index for index, name in enumerate(NEGATIVE_SOURCES)}
    free_map.update(prefix["paid_sources"])
    require(set(projected_names) == set(free_map), "projected paid-source set changed")
    local_map = {index: free_map[name] for index, name in enumerate(projected_names)}
    next_source = NEGATIVE_SOURCE_COUNT + PREFIX_COMPONENTS
    network: list[dict[str, Any]] = []

    def remap_bus(raw: object, label: str) -> list[int]:
        require(isinstance(raw, list), f"{label} is not a list")
        try:
            result = [local_map[int(source)] for source in raw]
        except (KeyError, TypeError, ValueError) as exc:
            raise RuntimeError(f"{label} contains a forward or unknown source") from exc
        require(result == sorted(set(result)), f"{label} is not canonical after remap")
        return result

    for local_slot, raw in enumerate(tail["network"]):
        kind = str(raw["kind"])
        global_slot = PREFIX_COMPONENTS + local_slot
        source = next_source + local_slot
        item = {
            "slot": global_slot,
            "source": source,
            "kind": kind,
            "left_bus": remap_bus(raw["left_bus"], f"tail slot {local_slot}.left"),
            "right_bus": remap_bus(raw["right_bus"], f"tail slot {local_slot}.right"),
            "cost": COST[kind],
            "depth_upper_bound": int(raw["depth_upper_bound"]),
        }
        network.append(item)
        local_map[len(projected_names) + local_slot] = source
    outputs = [
        remap_bus(bus, f"tail output {index}")
        for index, bus in enumerate(tail["output_buses"])
    ]
    return network, outputs


def _projection(output_names: tuple[str, ...]) -> tuple[dict[str, Any], tuple[Any, ...]]:
    full = production._full_domain()
    full_values, full_driven, full_targets, _all_mask, boundary_mismatch = full
    require(boundary_mismatch == 0, "fixed-shell nC7 identity changed")
    quotient = negative._derive_physical_quotient(
        full_values, full_driven, full_targets, output_names
    )
    require(quotient["boolean_rows"] == negative.BOOLEAN_ROWS, "Boolean quotient changed")
    require(quotient["physical_rows"] == negative.DOMAIN_ROWS, "physical quotient changed")
    return quotient, full


def build_negative_payload(
    tail_path: Path,
    tail: dict[str, Any],
    projected_names: tuple[str, ...],
    prefix: dict[str, Any],
    run_path: Path,
    run: dict[str, Any],
) -> dict[str, Any]:
    tail_network, tail_outputs = remap_tail(tail, projected_names, prefix)
    network = [*copy.deepcopy(prefix["network"]), *tail_network]
    output_buses = [*copy.deepcopy(prefix["output_buses"]), *tail_outputs]
    switches = sum(item["kind"] == "SWITCH" for item in network)
    xors = sum(item["kind"] == "XOR" for item in network)
    gate = sum(COST[item["kind"]] for item in network)
    require(gate == HIGH_GATE, f"combined high window is {gate}, expected 30")
    quotient, _full = _projection(FULL_OUTPUTS)
    payload: dict[str, Any] = {
        "schema": negative.SCHEMA,
        "status": "sat",
        "domain": negative.DOMAIN,
        "rows": negative.DOMAIN_ROWS,
        "boolean_value_rows": negative.BOOLEAN_ROWS,
        "physical_value_driven_rows": negative.DOMAIN_ROWS,
        "truth_projection_sha256": quotient["projection_sha256"],
        "output_names": list(FULL_OUTPUTS),
        "free_sources": list(NEGATIVE_SOURCES),
        "constructive_constants": False,
        "source_arrivals": dict(negative.SOURCE_ARRIVALS),
        "source_driven_profiles": quotient["source_driven_profiles"],
        "gate_bound": HIGH_GATE,
        "max_delay": MAX_DELAY,
        "components": len(network),
        "ordinary": len(network) - switches - xors,
        "exact_switches": switches,
        "exact_xors": xors,
        "fixed_kinds": [item["kind"] for item in network],
        "solver": f"composed-{tail.get('solver', 'source-witness')}",
        "variables": int(tail.get("variables", 0)),
        "clauses": int(tail.get("clauses", 0)),
        "solve_seconds": float(tail.get("solve_seconds", 0.0)),
        "physical_nets": True,
        "public_outputs_must_be_driven": True,
        "shard": tail.get("shard"),
        "timer_errors": list(tail.get("timer_errors", ())),
        "dependency_sha256": negative._dependency_hashes(),
        "actual_gate": gate,
        "network": network,
        "output_buses": output_buses,
        "verification": {},
        "composition": {
            "schema": "s34-family1-two-phase-tail729-high30-composition-v1",
            "tail_witness": certificate(tail_path),
            "run_record": certificate(run_path),
            "run_name": run["name"],
            "tail_worker": certificate(TAIL_WORKER_PATH),
            "negative_verifier": certificate(NEGATIVE_VERIFIER_PATH),
            "production_verifier": certificate(PRODUCTION_VERIFIER_PATH),
            "prefix_components": PREFIX_COMPONENTS,
            "prefix_gate": PREFIX_GATE,
            "tail_gate": TAIL_GATE,
            "paid_source_mapping": prefix["paid_sources"],
            "no_constant_source_used": True,
            "global_partition_rechecked": True,
        },
    }
    translated = negative._translate_for_replay(payload)
    structure = production._validate_structure(
        translated, fixture=False, max_residual_gate=production.MAX_RESIDUAL_GATE_LIMIT
    )
    payload["verification"] = {
        "mismatch_count": 0,
        "bus_conflict_count": 0,
        "undriven_output_count": 0,
        "physical_net_partition_violation_count": 0,
        "actual_output_arrivals": structure["output_arrivals"],
        "actual_max_delay": max(structure["output_arrivals"], default=0),
        "depth_upper_bound_violation_count": 0,
        "output_deadline_violation_count": 0,
    }
    structural = {"network": network, "output_buses": output_buses}
    payload["structural_sha256"] = sha256(
        json.dumps(structural, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return payload


def verify_negative_witness(path: Path, *, fixture: bool = False) -> dict[str, Any]:
    """Compatibility-fixed 729 verifier using the reviewed high30 gate limit."""

    path = path.resolve()
    payload = load_json(path)
    output_names = negative._validate_metadata(payload, fixture=fixture)
    translated = negative._translate_for_replay(payload)
    structure = production._validate_structure(
        translated,
        fixture=fixture,
        max_residual_gate=production.MAX_RESIDUAL_GATE_LIMIT,
    )
    production._verify_metadata(translated, structure)
    quotient, full = _projection(output_names)
    require(
        payload.get("truth_projection_sha256") == quotient["projection_sha256"],
        "truth projection SHA differs from the independent quotient",
    )
    require(
        payload.get("source_driven_profiles") == quotient["source_driven_profiles"],
        "source-driven profiles differ from the independent quotient",
    )
    quotient_values = dict(quotient["values"])
    quotient_driven = dict(quotient["drivens"])
    quotient_values.update({"0": 0, "1": quotient["all_mask"]})
    quotient_driven.update(
        {"0": quotient["all_mask"], "1": quotient["all_mask"]}
    )
    physical_replay = production._replay_report(
        label="independent-729-row-physical-quotient",
        rows=negative.DOMAIN_ROWS,
        values=quotient_values,
        targets=quotient["targets"],
        all_mask=quotient["all_mask"],
        structure=structure,
        driven=quotient_driven,
    )
    full_values, full_driven, full_targets, full_all, _boundary_mismatch = full
    full_replay = production._replay_report(
        label="independent-complete-u8-u8-u1-domain",
        rows=production.FULL_ROWS,
        values=full_values,
        targets=full_targets,
        all_mask=full_all,
        structure=structure,
        driven=full_driven,
    )
    return normalized(
        {
            "schema": "tail729-high30-native-independent-verification-v1",
            "status": "verified",
            "mode": "fixture" if fixture else "production",
            "competitive_contract": not fixture,
            "witness": {
                **certificate(path),
                "schema": payload["schema"],
                "domain": payload["domain"],
                "output_names": list(output_names),
            },
            "projection": {
                "complete_input_rows": production.FULL_ROWS,
                "boolean_value_rows": quotient["boolean_rows"],
                "physical_value_driven_rows": quotient["physical_rows"],
                "truth_projection_sha256": quotient["projection_sha256"],
                "source_driven_profiles": quotient["source_driven_profiles"],
            },
            "structure": {
                key: value
                for key, value in structure.items()
                if key not in {"network", "output_buses"}
            },
            "physical_quotient_replay": physical_replay,
            "full_replay": full_replay,
            "metadata_recomputed_equal": True,
            "verifier": {
                "path": portable(Path(__file__)),
                "sha256": digest(Path(__file__)),
                "production_replay_backend": certificate(PRODUCTION_VERIFIER_PATH),
                "sat_worker_imported_for_provenance_only": True,
            },
        }
    )


def _write_temporary(path: Path, payload: dict[str, Any]) -> bytes:
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode()
    require(not path.exists(), f"refusing to overwrite {path}")
    path.write_bytes(encoded)
    require(path.read_bytes() == encoded, f"temporary write changed: {path}")
    return encoded


def _write_final(path: Path, payload: dict[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    encoded = _write_temporary(temporary, payload)
    temporary.replace(path)
    require(path.read_bytes() == encoded, f"final write changed: {path}")


def compose(
    *, tail_path: Path, run_path: Path, output_dir: Path, profile: str
) -> dict[str, Any]:
    tail_path = tail_path.resolve()
    run_path = run_path.resolve()
    output_dir = output_dir.resolve()
    require(output_dir.is_relative_to(HERE), "output directory is outside the intake line")
    require(not output_dir.exists(), f"refusing to reuse output directory: {output_dir}")
    output_dir.mkdir(parents=True)

    negative_final = output_dir / "negative_high30_729_witness.json"
    production_final = output_dir / "production_high30_witness.json"
    negative_temp = output_dir / ".negative_high30_729_witness.json.tmp"
    production_temp = output_dir / ".production_high30_witness.json.tmp"
    try:
        tail, projected_domain, _provenance = validate_tail(tail_path, profile=profile)
        run = validate_run(run_path, tail_path, tail)
        prefix = build_prefix(profile)
        negative_payload = build_negative_payload(
            tail_path,
            tail,
            tuple(projected_domain.names),
            prefix,
            run_path,
            run,
        )
        negative_bytes = _write_temporary(negative_temp, negative_payload)
        native_review = verify_negative_witness(negative_temp)

        production_payload = negative._translate_for_replay(negative_payload)
        production_payload["translation"] = {
            "schema": "negative-high30-to-fixed73-production-abi-v1",
            "native_witness_sha256": sha256(negative_bytes).hexdigest(),
            "inserted_constant_indices": [27, 28],
            "constant_source_reference_count": 0,
        }
        production_bytes = _write_temporary(production_temp, production_payload)
        production_review = production.verify_witness(production_temp, fixture=False)

        negative_temp.replace(negative_final)
        production_temp.replace(production_final)
        require(negative_final.read_bytes() == negative_bytes, "native witness changed on publish")
        require(production_final.read_bytes() == production_bytes, "production witness changed on publish")
        native_review = verify_negative_witness(negative_final)
        production_review = production.verify_witness(production_final, fixture=False)

        native_review_path = output_dir / "negative_high30_729_verification.json"
        production_review_path = output_dir / "production_high30_verification.json"
        _write_final(native_review_path, native_review)
        _write_final(production_review_path, production_review)
        summary = {
            "schema": "tail729-high30-composition-summary-v1",
            "status": "verified",
            "profile": profile,
            "competitive_contract": True,
            "source_tail": certificate(tail_path),
            "source_run": certificate(run_path),
            "native_witness": certificate(negative_final),
            "production_witness": certificate(production_final),
            "native_review": certificate(native_review_path),
            "production_review": certificate(production_review_path),
            "score": {
                "residual_gate": production_review["structure"]["gate"],
                "complete_gate": production_review["fixed_interface"][
                    "fixed_total_gate"
                ]
                + production_review["structure"]["gate"],
                "complete_delay": production_review["fixed_interface"][
                    "complete_delay_target"
                ],
                "complete_energy": (
                    production_review["fixed_interface"]["fixed_total_gate"]
                    + production_review["structure"]["gate"]
                )
                * production_review["fixed_interface"]["complete_delay_target"],
            },
            "checks": {
                "physical_rows": native_review["physical_quotient_replay"]["rows"],
                "boolean_rows": production_review["reduced_replay"]["rows"],
                "full_rows": production_review["full_replay"]["rows"],
                "physical_partition_violations": production_review["structure"][
                    "physical_net_partition_violation_count"
                ],
                "dead_components": production_review["structure"][
                    "dead_component_output_count"
                ],
                "native_729_mismatch_union": native_review[
                    "physical_quotient_replay"
                ]["mismatch_union_count"],
                "native_729_conflicts": native_review["physical_quotient_replay"][
                    "bus_conflict_count"
                ],
                "native_729_z": sum(
                    native_review["physical_quotient_replay"][
                        "z_assignment_count_by_output"
                    ]
                ),
                "production_486_mismatch_union": production_review[
                    "reduced_replay"
                ]["mismatch_union_count"],
                "production_full_mismatch_union": production_review["full_replay"][
                    "mismatch_union_count"
                ],
            },
            "formal_save_read": False,
            "formal_save_written": False,
            "repository_candidate_written": False,
            "game_started": False,
        }
        summary_path = output_dir / "composition_summary.json"
        _write_final(summary_path, summary)
        summary["summary"] = certificate(summary_path)
        return summary
    except Exception:
        for path in (negative_temp, production_temp):
            if path.exists():
                path.unlink()
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tail", type=Path, required=True)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--profile", choices=tuple(tail_worker.PHASE_PROFILES), default="primary")
    args = parser.parse_args(argv)
    summary = compose(
        tail_path=args.tail,
        run_path=args.run,
        output_dir=args.output_dir,
        profile=args.profile,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
