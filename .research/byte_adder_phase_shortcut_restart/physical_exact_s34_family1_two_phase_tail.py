#!/usr/bin/env python3
"""Fix S3/S4 family-1 plus two paid phases in the physical high29 CNF.

The authoritative ``physical_exact.py`` worker is imported without editing it.
This wrapper fixes:

* slots 0..8 to model 1 from ``s34-internal-phase-family-r1.json``;
* slot 9 to ``NOR(Q6, P7)``;
* slot 10 to ``NOR(N4, P5)``;
* slots 11..18 to Switches;
* public S3/S4 to the reviewed family output BUSes.

The resulting exact budget is 19 components, 9 ordinary gates, 10 Switches,
29 gates, and delay at most 5.  S5/S6/S7/C8 remain entirely solver-selected.
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
BASE_PATH = HERE / "physical_exact.py"
FAMILY_PATH = (
    ROOT
    / ".research/byte_adder_paper_synthesis_root/"
    "s34-internal-phase-family-r1.json"
)
EXPECTED_BASE_SHA256 = (
    "c48a96e55d8c5076418999f5fa5ee95e9f8207c03f138cd4bccf48908a69c071"
)
EXPECTED_FAMILY_SHA256 = (
    "54d4170d1ab9795c11e94bc06bf119da1728b04034a24d940ea082d89a81717f"
)
EXPECTED_MODEL_INDEX = 1
EXPECTED_PHASE_FAMILY_SHA256 = (
    "8538e303d5c4b79cbc06010cc79b90d2679720b581a2469851625d449b2fbe0d"
)
EXPECTED_DOMAIN = "s34567c8_leaf"
EXPECTED_OUTPUTS = ("S3", "S4", "S5", "S6", "S7", "C8")
EXPECTED_COMPONENTS = 19
EXPECTED_SWITCHES = 10
EXPECTED_GATE = 29
ORDINARY = ("NOT", "AND", "OR", "NAND", "NOR")


def _digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _load_module(name: str, path: Path, expected_sha256: str):
    actual = _digest(path)
    if actual != expected_sha256:
        raise RuntimeError(
            f"dependency SHA mismatch for {path}: expected {expected_sha256}, got {actual}"
        )
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BASE = _load_module("s34_family1_two_phase_base", BASE_PATH, EXPECTED_BASE_SHA256)
ORIGINAL_SOLVE = BASE.solve
ORIGINAL_BUILD = BASE.upstream.build


def _load_family_record() -> tuple[dict[str, object], dict[str, object]]:
    encoded = FAMILY_PATH.read_bytes()
    if sha256(encoded).hexdigest() != EXPECTED_FAMILY_SHA256:
        raise RuntimeError("S3/S4 family inventory SHA changed")
    payload = json.loads(encoded)
    if payload.get("schema") != "s34-internal-phase-family-enumeration-v1":
        raise RuntimeError("unexpected S3/S4 family schema")
    records = [
        record
        for record in payload.get("records", ())
        if int(record.get("model_index", -1)) == EXPECTED_MODEL_INDEX
    ]
    if len(records) != 1:
        raise RuntimeError("model 1 is absent or duplicated")
    record = records[0]
    if record.get("phase_family_sha256") != EXPECTED_PHASE_FAMILY_SHA256:
        raise RuntimeError("model-1 phase-family SHA changed")
    network = record.get("network")
    if not isinstance(network, list) or len(network) != 9:
        raise RuntimeError("model-1 network is not the reviewed nine-component witness")
    if record.get("output_buses") != [[31], [32, 34]]:
        raise RuntimeError("model-1 S3/S4 output BUSes changed")
    provenance = {
        "path": str(FAMILY_PATH.relative_to(ROOT)).replace("\\", "/"),
        "sha256": EXPECTED_FAMILY_SHA256,
        "model_index": EXPECTED_MODEL_INDEX,
        "phase_family_sha256": EXPECTED_PHASE_FAMILY_SHA256,
    }
    return record, provenance


def _force_exact_bus(enc, selectors: list[int], selected: Iterable[int]) -> None:
    selected_set = frozenset(selected)
    if any(source < 0 or source >= len(selectors) for source in selected_set):
        raise ValueError(f"invalid fixed BUS sources: {sorted(selected_set)}")
    for source, literal in enumerate(selectors):
        enc.force(literal, source in selected_set)


def _selector_mask(sources: Iterable[int]) -> int:
    return sum(1 << source for source in sources)


def _canonical_sides(
    kind: str, left: Iterable[int], right: Iterable[int]
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    left_tuple = tuple(sorted(set(left)))
    right_tuple = tuple(sorted(set(right)))
    if kind not in ORDINARY or kind == "NOT":
        return left_tuple, right_tuple
    if _selector_mask(left_tuple) < _selector_mask(right_tuple):
        return left_tuple, right_tuple
    return right_tuple, left_tuple


def _map_family_source(
    source: int,
    *,
    local_names: tuple[str, ...],
    global_by_name: dict[str, int],
    global_source_count: int,
) -> int:
    if source < len(local_names):
        return global_by_name[local_names[source]]
    slot = source - len(local_names)
    if not 0 <= slot < 9:
        raise ValueError(f"invalid model-1 component source {source}")
    return global_source_count + slot


def _force_slot(
    enc,
    state: dict[str, object],
    *,
    slot: int,
    kind: str,
    left: Iterable[int],
    right: Iterable[int],
) -> dict[str, object]:
    kinds = state["kinds"]
    left_uses = state["left_uses"]
    right_uses = state["right_uses"]
    encoded_left, encoded_right = _canonical_sides(kind, left, right)
    enc.force(kinds[slot][BASE.G.KINDS.index(kind)], True)
    _force_exact_bus(enc, left_uses[slot], encoded_left)
    _force_exact_bus(enc, right_uses[slot], encoded_right)
    return {
        "slot": slot,
        "kind": kind,
        "left_bus": list(encoded_left),
        "right_bus": list(encoded_right),
    }


def add_fixed_family_prefix(enc, state: dict[str, object]) -> dict[str, object]:
    before_variables = enc.pool.top
    before_clauses = len(enc.cnf.clauses)
    record, provenance = _load_family_record()
    names = tuple(state["names"])
    source_count = int(state["source_count"])
    if source_count != len(names):
        raise RuntimeError("source count/name mismatch")
    if len(state["kinds"]) != EXPECTED_COMPONENTS:
        raise ValueError("this wrapper requires exactly 19 components")
    global_by_name = {name: index for index, name in enumerate(names)}
    if len(global_by_name) != len(names):
        raise RuntimeError("duplicate global source names")
    local_domain = BASE.domain_s3456_leaf()
    local_names = (*local_domain.names, "0", "1")
    if len(local_names) != 26:
        raise RuntimeError("reviewed S3/S4 source ABI changed")

    fixed_slots: list[dict[str, object]] = []
    for expected_slot, item in enumerate(record["network"]):
        if int(item["slot"]) != expected_slot:
            raise RuntimeError("model-1 network is not topological")
        left = [
            _map_family_source(
                int(source),
                local_names=local_names,
                global_by_name=global_by_name,
                global_source_count=source_count,
            )
            for source in item["left_bus"]
        ]
        right = [
            _map_family_source(
                int(source),
                local_names=local_names,
                global_by_name=global_by_name,
                global_source_count=source_count,
            )
            for source in item["right_bus"]
        ]
        fixed_slots.append(
            _force_slot(
                enc,
                state,
                slot=expected_slot,
                kind=str(item["kind"]),
                left=left,
                right=right,
            )
        )

    fixed_slots.append(
        _force_slot(
            enc,
            state,
            slot=9,
            kind="NOR",
            left=(global_by_name["Q6"],),
            right=(global_by_name["P7"],),
        )
    )
    fixed_slots.append(
        _force_slot(
            enc,
            state,
            slot=10,
            kind="NOR",
            left=(global_by_name["N4"],),
            right=(global_by_name["P5"],),
        )
    )
    for slot in range(11, EXPECTED_COMPONENTS):
        enc.force(state["kinds"][slot][BASE.G.SWITCH], True)

    output_uses = state["output_uses"]
    if len(output_uses) != len(EXPECTED_OUTPUTS):
        raise RuntimeError("full high-window output ABI changed")
    mapped_outputs = []
    for output_bus in record["output_buses"]:
        mapped = [
            _map_family_source(
                int(source),
                local_names=local_names,
                global_by_name=global_by_name,
                global_source_count=source_count,
            )
            for source in output_bus
        ]
        mapped_outputs.append(mapped)
    _force_exact_bus(enc, output_uses[0], mapped_outputs[0])
    _force_exact_bus(enc, output_uses[1], mapped_outputs[1])

    return {
        "name": "fixed-s34-family1-nor-q6-p7-nor-n4-p5-terminal-switch-tail",
        "family_provenance": provenance,
        "fixed_slots": fixed_slots,
        "fixed_output_buses": {
            "S3": mapped_outputs[0],
            "S4": mapped_outputs[1],
        },
        "suffix_switch_slots": list(range(11, EXPECTED_COMPONENTS)),
        "expected_components": EXPECTED_COMPONENTS,
        "expected_switches": EXPECTED_SWITCHES,
        "expected_gate": EXPECTED_GATE,
        "base_variables": before_variables,
        "base_clauses": before_clauses,
        "added_variables": enc.pool.top - before_variables,
        "added_clauses": len(enc.cnf.clauses) - before_clauses,
    }


def verify_fixed_prefix(
    payload: dict[str, object], fixed: dict[str, object]
) -> dict[str, object]:
    errors: list[str] = []
    network = payload.get("network", [])
    for expected in fixed["fixed_slots"]:
        actual = network[expected["slot"]]
        for key in ("kind", "left_bus", "right_bus"):
            if actual[key] != expected[key]:
                errors.append(
                    f"slot {expected['slot']} {key}: expected {expected[key]!r}, "
                    f"got {actual[key]!r}"
                )
    for slot in fixed["suffix_switch_slots"]:
        if network[slot]["kind"] != "SWITCH":
            errors.append(f"slot {slot} is not SWITCH")
    outputs = dict(zip(payload["output_names"], payload["output_buses"], strict=True))
    for name, expected in fixed["fixed_output_buses"].items():
        if outputs[name] != expected:
            errors.append(f"{name} BUS: expected {expected!r}, got {outputs[name]!r}")
    return {
        "fixed_prefix_violation_count": len(errors),
        "errors": errors,
    }


def strengthened_solve(args: argparse.Namespace) -> dict[str, object]:
    if args.domain != EXPECTED_DOMAIN:
        raise ValueError(f"domain must be {EXPECTED_DOMAIN}")
    selected = tuple(filter(None, (args.outputs or "").split(",")))
    if selected and selected != EXPECTED_OUTPUTS:
        raise ValueError("this wrapper requires all S3,S4,S5,S6,S7,C8 outputs")
    if args.components != EXPECTED_COMPONENTS:
        raise ValueError("components must be 19")
    if args.switches != EXPECTED_SWITCHES or args.xors != 0:
        raise ValueError("this wrapper requires exactly 10 Switches and zero XORs")
    if args.gate_bound != EXPECTED_GATE or args.max_delay != 5:
        raise ValueError("this wrapper requires gate-bound 29 and max-delay 5")

    fixed: dict[str, object] = {}

    def strengthened_build(build_args):
        enc, state = ORIGINAL_BUILD(build_args)
        fixed.update(add_fixed_family_prefix(enc, state))
        return enc, state

    BASE.upstream.build = strengthened_build
    try:
        payload = ORIGINAL_SOLVE(args)
    finally:
        BASE.upstream.build = ORIGINAL_BUILD

    payload["base_schema"] = payload["schema"]
    payload["schema"] = "exact-fast-negative-physical-s34-family1-two-phase-tail-v1"
    payload["authoritative_worker"] = str(BASE_PATH.relative_to(ROOT)).replace(
        "\\", "/"
    )
    payload["authoritative_worker_sha256"] = EXPECTED_BASE_SHA256
    payload["wrapper"] = str(Path(__file__).resolve().relative_to(ROOT)).replace(
        "\\", "/"
    )
    payload["wrapper_sha256"] = _digest(Path(__file__))
    payload["fixed_prefix_constraint"] = fixed
    if payload["status"] == "sat":
        verification = verify_fixed_prefix(payload, fixed)
        payload["fixed_prefix_verification"] = verification
        payload["verification"]["fixed_prefix_violation_count"] = verification[
            "fixed_prefix_violation_count"
        ]
        if verification["fixed_prefix_violation_count"]:
            raise RuntimeError("decoded SAT witness violates the fixed prefix")
    return payload


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-check", action="store_true")
    parser.add_argument("--domain", default=EXPECTED_DOMAIN)
    parser.add_argument("--outputs", default=",".join(EXPECTED_OUTPUTS))
    parser.add_argument("--gate-bound", type=int, default=EXPECTED_GATE)
    parser.add_argument("--max-delay", type=int, default=5)
    parser.add_argument("--components", type=int, default=EXPECTED_COMPONENTS)
    parser.add_argument("--switches", type=int, default=EXPECTED_SWITCHES)
    parser.add_argument("--xors", type=int, default=0)
    parser.add_argument("--fixed-kinds")
    parser.add_argument("--split-slots", type=int, default=1)
    parser.add_argument("--shard-count", type=int, default=1)
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--timeout", type=float, default=0.0)
    parser.add_argument("--output", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    record, provenance = _load_family_record()
    if args.self_check:
        if args.output is not None:
            raise ValueError("--self-check does not write an output")
        print(
            json.dumps(
                {
                    "status": "verified",
                    "schema": "s34-family1-two-phase-tail-self-check-v1",
                    "wrapper_sha256": _digest(Path(__file__)),
                    "authoritative_worker_sha256": _digest(BASE_PATH),
                    "family_provenance": provenance,
                    "family_components": len(record["network"]),
                    "fixed_phases": ["NOR(Q6,P7)", "NOR(N4,P5)"],
                    "components": EXPECTED_COMPONENTS,
                    "switches": EXPECTED_SWITCHES,
                    "gate": EXPECTED_GATE,
                    "delay": 5,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0
    if args.output is None:
        raise ValueError("--output is required")
    payload = strengthened_solve(args)
    encoded = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(encoded.encode("utf-8"))
    summary = {key: value for key, value in payload.items() if key != "network"}
    summary["output"] = str(args.output.resolve())
    summary["sha256"] = sha256(encoded.encode()).hexdigest()
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if payload["status"] != "unknown" else 2


if __name__ == "__main__":
    raise SystemExit(main())
