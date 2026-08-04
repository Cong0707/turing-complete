#!/usr/bin/env python3
"""Exact 729-row tail search with paid S3/S4 family-1 phases.

The reviewed negative-high worker supplies the physical value/driven quotient,
including high-Z states for nC3, V34n, V56n, V36n, and nC7.  This wrapper
replays S3/S4 family model 1 on that quotient, exports its six useful D3/D4
ordinary nodes, and adds two reviewed paid NOR phases.  No conceptual constant
is exposed to the synthesized tail.

Optional ``--fixed-phase`` constraints fix an ordinary component to singleton
paid-source inputs.  They are intended for small, constructive interleaved
topology slices, not as evidence about unconstrained high-window synthesis.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
from typing import Iterable


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE_PATH = (
    ROOT / ".research/byte_adder_av_reduced_forward/exact_negative_high_d5_sat.py"
)
PHYSICAL_PATH = HERE / "physical_exact.py"
FAMILY_PATH = (
    ROOT
    / ".research/byte_adder_paper_synthesis_root/"
    "s34-internal-phase-family-r1.json"
)
EXPECTED_BASE_SHA256 = (
    "098c7467d2cdaaefb0e3c16414b06d48644465b1b1ea7e0348cb9cdd7d791e16"
)
EXPECTED_PHYSICAL_SHA256 = (
    "c48a96e55d8c5076418999f5fa5ee95e9f8207c03f138cd4bccf48908a69c071"
)
EXPECTED_FAMILY_SHA256 = (
    "54d4170d1ab9795c11e94bc06bf119da1728b04034a24d940ea082d89a81717f"
)
EXPECTED_MODEL_INDEX = 1
EXPECTED_PHASE_FAMILY_SHA256 = (
    "8538e303d5c4b79cbc06010cc79b90d2679720b581a2469851625d449b2fbe0d"
)
EXPECTED_USEFUL_SLOTS = (0, 1, 2, 3, 4, 7)
EXPECTED_OUTPUT_BUSES = ((31,), (32, 34))
TAIL_OUTPUTS = ("S5", "S6", "S7", "C8")
MAX_DELAY = 5
ORDINARY_KINDS = {"NOT", "AND", "OR", "NAND", "NOR"}
PHASE_PROFILES = {
    "primary": (
        ("phase_nor_q6_p7", "Q6", "P7"),
        ("phase_nor_n4_p5", "N4", "P5"),
    ),
    "alternate": (
        ("phase_nor_q6_p7", "Q6", "P7"),
        ("phase_nor_p5_v34n", "P5", "V34n"),
    ),
}


def _digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _column_digest(values: Iterable[bool], drivens: Iterable[bool]) -> str:
    encoded = bytes(
        (int(value) << 1) | int(driven)
        for value, driven in zip(values, drivens, strict=True)
    )
    return sha256(encoded).hexdigest()


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


base = _load_module("s34_family1_tail729_base", BASE_PATH, EXPECTED_BASE_SHA256)
if _digest(PHYSICAL_PATH) != EXPECTED_PHYSICAL_SHA256:
    raise RuntimeError("physical_exact.py SHA changed")


@dataclass(frozen=True)
class Signal:
    value: tuple[bool, ...]
    driven: tuple[bool, ...]
    arrival: int
    label: str


def _load_family_record() -> dict[str, object]:
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
        raise RuntimeError("family model 1 is absent or duplicated")
    record = records[0]
    if record.get("phase_family_sha256") != EXPECTED_PHASE_FAMILY_SHA256:
        raise RuntimeError("family model-1 phase SHA changed")
    if tuple(record.get("useful_slots", ())) != EXPECTED_USEFUL_SLOTS:
        raise RuntimeError("family model-1 useful slots changed")
    output_buses = tuple(tuple(bus) for bus in record.get("output_buses", ()))
    if output_buses != EXPECTED_OUTPUT_BUSES:
        raise RuntimeError("family model-1 output BUSes changed")
    network = record.get("network")
    if not isinstance(network, list) or len(network) != 9:
        raise RuntimeError("family model-1 network is not nine components")
    if sum(int(item["cost"]) for item in network) != 11:
        raise RuntimeError("family model-1 gate cost changed")
    verification = record.get("verification", {})
    for field in (
        "mismatch_count",
        "bus_conflict_count",
        "undriven_output_count",
        "physical_net_partition_violation_count",
        "depth_upper_bound_violation_count",
        "output_deadline_violation_count",
    ):
        if int(verification.get(field, -1)) != 0:
            raise RuntimeError(f"family model-1 failed {field}")
    return record


def _resolve_bus(
    signals: dict[int, Signal], bus: Iterable[int], *, label: str
) -> Signal:
    sources = tuple(int(source) for source in bus)
    if not sources:
        raise ValueError(f"empty BUS: {label}")
    try:
        selected = tuple(signals[source] for source in sources)
    except KeyError as exc:
        raise ValueError(f"unavailable source {exc.args[0]} in {label}") from exc
    rows = len(selected[0].value)
    values: list[bool] = []
    drivens: list[bool] = []
    for case in range(rows):
        active = {
            signal.value[case] for signal in selected if signal.driven[case]
        }
        if len(active) > 1:
            raise ValueError(f"conflicting BUS {label} at row {case}")
        drivens.append(bool(active))
        values.append(next(iter(active)) if active else False)
    return Signal(
        tuple(values),
        tuple(drivens),
        max(signal.arrival for signal in selected),
        "+".join(signal.label for signal in selected),
    )


def _apply_ordinary(
    kind: str, left: tuple[bool, ...], right: tuple[bool, ...]
) -> tuple[bool, ...]:
    if kind == "NOT":
        return tuple(not value for value in left)
    if kind == "AND":
        return tuple(a and b for a, b in zip(left, right, strict=True))
    if kind == "OR":
        return tuple(a or b for a, b in zip(left, right, strict=True))
    if kind == "NAND":
        return tuple(not (a and b) for a, b in zip(left, right, strict=True))
    if kind == "NOR":
        return tuple(not (a or b) for a, b in zip(left, right, strict=True))
    raise ValueError(f"not an ordinary gate: {kind}")


def _target_column(domain, name: str) -> tuple[bool, ...]:
    index = domain.output_names.index(name)
    target = domain.targets[index]
    return tuple(bool((target >> case) & 1) for case in range(domain.rows))


def _family_network_signals(domain, record: dict[str, object]):
    rows = domain.rows
    base_signals = {
        name: Signal(
            tuple(domain.columns[index]),
            tuple(domain.drivens[index]),
            int(domain.arrivals[name]),
            name,
        )
        for index, name in enumerate(domain.names)
    }
    local = base.physical.domain_s3456_leaf()
    local_names = (*local.names, "0", "1")
    if len(local_names) != 26:
        raise RuntimeError("reviewed family source ABI changed")
    signals: dict[int, Signal] = {}
    for source, name in enumerate(local_names):
        if name == "0":
            signal = Signal((False,) * rows, (True,) * rows, 0, name)
        elif name == "1":
            signal = Signal((True,) * rows, (True,) * rows, 0, name)
        else:
            if name not in base_signals:
                raise ValueError(f"family source {name!r} absent from 729-row domain")
            signal = base_signals[name]
        signals[source] = signal

    exported: list[Signal] = []
    exported_records: list[dict[str, object]] = []
    useful = set(EXPECTED_USEFUL_SLOTS)
    for expected_slot, item in enumerate(record["network"]):
        slot = int(item["slot"])
        source = int(item["source"])
        kind = str(item["kind"])
        if slot != expected_slot or source != len(local_names) + slot:
            raise RuntimeError("family model-1 network is not topological")
        left_sources = tuple(int(value) for value in item["left_bus"])
        right_sources = tuple(int(value) for value in item["right_bus"])
        left = _resolve_bus(signals, left_sources, label=f"u{slot}.left")
        right = _resolve_bus(signals, right_sources, label=f"u{slot}.right")
        delay = int(base.G.DELAY[base.G.KINDS.index(kind)])
        arrival = max(left.arrival, right.arrival) + delay
        if arrival > int(item["depth_upper_bound"]):
            raise RuntimeError(f"family u{slot} exceeds its reviewed timing bound")
        label = f"s34_family1_u{slot}"
        if kind in ORDINARY_KINDS:
            value = _apply_ordinary(kind, left.value, right.value)
            signal = Signal(value, (True,) * rows, arrival, label)
        elif kind == "SWITCH":
            value = tuple(
                enable and data
                for enable, data in zip(left.value, right.value, strict=True)
            )
            signal = Signal(value, left.value, arrival, label)
        else:
            raise RuntimeError(f"unexpected family gate kind: {kind}")
        signals[source] = signal

        if slot in useful:
            if kind not in ORDINARY_KINDS or not all(signal.driven):
                raise RuntimeError(f"family useful slot u{slot} is not always driven")
            if arrival > MAX_DELAY - 1:
                raise RuntimeError(f"family useful slot u{slot} cannot feed a D5 component")
            exported.append(signal)
            exported_records.append(
                {
                    "name": label,
                    "source_slot": slot,
                    "kind": kind,
                    "left_bus": [signals[value].label for value in left_sources],
                    "right_bus": [signals[value].label for value in right_sources],
                    "arrival": arrival,
                    "always_driven": True,
                    "physical_truth_sha256": _column_digest(
                        signal.value, signal.driven
                    ),
                }
            )

    if len(exported) != len(EXPECTED_USEFUL_SLOTS):
        raise RuntimeError("not all reviewed useful family nodes were exported")
    s3 = _resolve_bus(signals, EXPECTED_OUTPUT_BUSES[0], label="S3")
    s4 = _resolve_bus(signals, EXPECTED_OUTPUT_BUSES[1], label="S4")
    if not all(s3.driven) or s3.value != _target_column(domain, "S3"):
        raise RuntimeError("family model-1 S3 fails the 729-row physical quotient")
    if not all(s4.driven) or s4.value != _target_column(domain, "S4"):
        raise RuntimeError("family model-1 S4 fails the 729-row physical quotient")
    return exported, exported_records


def build_domain_with_provenance(profile: str):
    if profile not in PHASE_PROFILES:
        raise ValueError(f"unknown phase profile: {profile}")
    original = base.build_domain()
    if original.rows != 729:
        raise RuntimeError("negative-high physical quotient is no longer 729 rows")
    record = _load_family_record()
    exported, exported_records = _family_network_signals(original, record)
    base_by_name = {
        name: Signal(
            tuple(original.columns[index]),
            tuple(original.drivens[index]),
            int(original.arrivals[name]),
            name,
        )
        for index, name in enumerate(original.names)
    }

    phases: list[Signal] = []
    phase_records: list[dict[str, object]] = []
    for name, left_name, right_name in PHASE_PROFILES[profile]:
        left = base_by_name[left_name]
        right = base_by_name[right_name]
        value = _apply_ordinary("NOR", left.value, right.value)
        arrival = max(left.arrival, right.arrival) + 1
        if arrival > MAX_DELAY - 1:
            raise RuntimeError(f"paid phase {name} cannot feed a D5 component")
        signal = Signal(value, (True,) * original.rows, arrival, name)
        phases.append(signal)
        phase_records.append(
            {
                "name": name,
                "kind": "NOR",
                "left": left_name,
                "right": right_name,
                "left_z_rows": original.rows - sum(left.driven),
                "right_z_rows": original.rows - sum(right.driven),
                "arrival": arrival,
                "always_driven": True,
                "physical_truth_sha256": _column_digest(
                    signal.value, signal.driven
                ),
            }
        )

    paid = (*exported, *phases)
    target_indices = tuple(original.output_names.index(name) for name in TAIL_OUTPUTS)
    domain = base.Domain(
        (*original.names, *(signal.label for signal in paid)),
        (*original.columns, *(signal.value for signal in paid)),
        (*original.drivens, *(signal.driven for signal in paid)),
        tuple(original.targets[index] for index in target_indices),
        {
            **original.arrivals,
            **{signal.label: signal.arrival for signal in paid},
        },
        TAIL_OUTPUTS,
    )
    provenance = {
        "schema": "s34-family1-two-phase-physical729-projection-v1",
        "profile": profile,
        "physical_rows": domain.rows,
        "boolean_value_rows": 486,
        "constructive_constants": False,
        "tail_outputs": TAIL_OUTPUTS,
        "family": {
            "path": str(FAMILY_PATH.relative_to(ROOT)).replace("\\", "/"),
            "sha256": EXPECTED_FAMILY_SHA256,
            "model_index": EXPECTED_MODEL_INDEX,
            "phase_family_sha256": EXPECTED_PHASE_FAMILY_SHA256,
            "paid_gate": 11,
            "paid_components": 9,
            "output_buses": [list(bus) for bus in EXPECTED_OUTPUT_BUSES],
            "s3_s4_replayed_over_729_rows": True,
        },
        "exported_family_nodes": exported_records,
        "fixed_paid_phases": phase_records,
        "excluded_family_nodes": [
            {
                "source_slot": 5,
                "reason": "arrival D5 cannot feed an incremental D5 component",
            },
            {
                "source_slot": 6,
                "reason": "individual Switch output may be high impedance",
            },
            {
                "source_slot": 8,
                "reason": "individual Switch output may be high impedance",
            },
        ],
    }
    return domain, provenance


def _canonical_sides(
    kind: str, left: int, right: int | None
) -> tuple[int, int | None]:
    if kind == "NOT" or right is None:
        return left, right
    if (1 << left) < (1 << right):
        return left, right
    return right, left


def _parse_fixed_phases(
    specifications: Iterable[str], names: tuple[str, ...], components: int
) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    seen_slots: set[int] = set()
    by_name = {name: index for index, name in enumerate(names)}
    for specification in specifications:
        parts = tuple(part.strip() for part in specification.split(":"))
        if len(parts) not in (3, 4) or not all(parts):
            raise ValueError(
                "fixed phase must be SLOT:NOT:LEFT or SLOT:KIND:LEFT:RIGHT"
            )
        slot = int(parts[0])
        kind = parts[1].upper()
        if not 0 <= slot < components or slot in seen_slots:
            raise ValueError(f"invalid or duplicate fixed phase slot: {slot}")
        if kind not in ORDINARY_KINDS:
            raise ValueError(f"fixed phase must be ordinary, got {kind!r}")
        expected_parts = 3 if kind == "NOT" else 4
        if len(parts) != expected_parts:
            raise ValueError(f"{kind} fixed phase has the wrong arity")
        requested = parts[2:]
        unknown = tuple(name for name in requested if name not in by_name)
        if unknown:
            raise ValueError(f"unknown fixed phase source(s): {unknown}")
        left = by_name[requested[0]]
        right = by_name[requested[1]] if len(requested) == 2 else None
        left, right = _canonical_sides(kind, left, right)
        seen_slots.add(slot)
        result.append(
            {
                "specification": specification,
                "slot": slot,
                "kind": kind,
                "left_source": left,
                "left_source_name": names[left],
                "right_source": right,
                "right_source_name": None if right is None else names[right],
            }
        )
    return result


def _force_fixed_phases(enc, state, phases: list[dict[str, object]]) -> None:
    for phase in phases:
        slot = int(phase["slot"])
        kind = str(phase["kind"])
        enc.force(state["kinds"][slot][base.G.KINDS.index(kind)], True)
        left_source = int(phase["left_source"])
        right_source = phase["right_source"]
        for source, literal in enumerate(state["left_uses"][slot]):
            enc.force(literal, source == left_source)
        for source, literal in enumerate(state["right_uses"][slot]):
            enc.force(literal, source == right_source)


def _verify_decoded_fixed_phases(
    payload: dict[str, object], phases: list[dict[str, object]]
) -> None:
    if payload.get("status") != "sat":
        return
    network = payload.get("network")
    if not isinstance(network, list):
        raise RuntimeError("decoded SAT witness has no network")
    for phase in phases:
        item = network[int(phase["slot"])]
        expected_right = (
            [] if phase["right_source"] is None else [int(phase["right_source"])]
        )
        if (
            item.get("kind") != phase["kind"]
            or item.get("left_bus") != [int(phase["left_source"])]
            or item.get("right_bus") != expected_right
        ):
            raise RuntimeError("decoded SAT witness violates a fixed phase")


def dependency_sha256() -> dict[str, str]:
    paths = (Path(__file__).resolve(), BASE_PATH, PHYSICAL_PATH, FAMILY_PATH)
    return {
        str(path.relative_to(ROOT)).replace("\\", "/"): _digest(path)
        for path in paths
    }


def solve(args: argparse.Namespace) -> dict[str, object]:
    domain, provenance = build_domain_with_provenance(args.phase_profile)
    phases = _parse_fixed_phases(args.fixed_phase, domain.names, args.components)
    original_domain = base.build_domain
    original_shard = base.physical.constrain_shard
    applied: dict[str, object] = {}

    def constrain_then_shard(enc, state, inner_args):
        applied["fixed_kinds"] = base.physical.constrain_fixed_kinds(
            enc, state, inner_args
        )
        _force_fixed_phases(enc, state, phases)
        return original_shard(enc, state, inner_args)

    base.build_domain = lambda: domain
    base.physical.constrain_shard = constrain_then_shard
    try:
        payload = base.solve(args)
    finally:
        base.build_domain = original_domain
        base.physical.constrain_shard = original_shard

    if "fixed_kinds" not in applied:
        raise RuntimeError("base worker did not reach the fixed constraint hook")
    payload["base_schema"] = payload["schema"]
    payload["schema"] = "exact-s34-family1-two-phase-physical729-tail-v1"
    payload["fixed_kinds"] = applied["fixed_kinds"]
    payload["fixed_phase_constraints"] = phases
    payload["free_source_projection"] = provenance
    payload["extended_dependency_sha256"] = dependency_sha256()
    _verify_decoded_fixed_phases(payload, phases)
    return payload


def _self_check() -> dict[str, object]:
    profiles: dict[str, object] = {}
    for profile in PHASE_PROFILES:
        domain, provenance = build_domain_with_provenance(profile)
        base_count = len(base.build_domain().names)
        paid_names = domain.names[base_count:]
        profiles[profile] = {
            "physical_rows": domain.rows,
            "outputs": domain.output_names,
            "constructive_constants": False,
            "paid_source_count": len(paid_names),
            "paid_sources": paid_names,
            "paid_source_arrivals": {
                name: domain.arrivals[name] for name in paid_names
            },
            "all_paid_sources_always_driven": all(
                all(domain.drivens[domain.names.index(name)]) for name in paid_names
            ),
            "fixed_paid_phases": provenance["fixed_paid_phases"],
        }
    return {
        "status": "verified",
        "schema": "s34-family1-two-phase-physical729-self-check-v1",
        "dependency_sha256": dependency_sha256(),
        "family_model_index": EXPECTED_MODEL_INDEX,
        "family_phase_sha256": EXPECTED_PHASE_FAMILY_SHA256,
        "profiles": profiles,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-check", action="store_true")
    parser.add_argument("--phase-profile", choices=tuple(PHASE_PROFILES), default="primary")
    parser.add_argument("--gate-bound", type=int)
    parser.add_argument("--max-delay", type=int, default=MAX_DELAY)
    parser.add_argument("--components", type=int)
    parser.add_argument("--switches", type=int)
    parser.add_argument("--xors", type=int, default=0)
    parser.add_argument("--fixed-kinds", default="")
    parser.add_argument(
        "--fixed-phase",
        action="append",
        default=[],
        help="repeatable SLOT:NOT:LEFT or SLOT:KIND:LEFT:RIGHT constraint",
    )
    parser.add_argument("--split-slots", type=int, default=1)
    parser.add_argument("--shard-count", type=int, default=1)
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--solver", default="glucose42")
    parser.add_argument("--timeout", type=float, default=0.0)
    parser.add_argument("--output", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.self_check:
        if args.output is not None:
            raise ValueError("--self-check does not write an output")
        print(json.dumps(_self_check(), ensure_ascii=False, indent=2))
        return 0
    for name in ("gate_bound", "components", "switches"):
        if getattr(args, name) is None:
            raise ValueError(f"--{name.replace('_', '-')} is required")
    if args.output is None:
        raise ValueError("--output is required")
    if args.max_delay != MAX_DELAY or args.xors != 0:
        raise ValueError("this wrapper currently requires D5 and zero XORs")
    expected_gate = args.components + args.switches + 2 * args.xors
    if args.gate_bound != expected_gate:
        raise ValueError("inconsistent component/Switch/gate decomposition")
    args.outputs = ",".join(TAIL_OUTPUTS)
    payload = solve(args)
    encoded = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(encoded, encoding="utf-8")
    summary = {key: value for key, value in payload.items() if key != "network"}
    summary["output"] = str(args.output.resolve())
    summary["sha256"] = sha256(encoded.encode()).hexdigest()
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if payload["status"] != "unknown" else 2


if __name__ == "__main__":
    raise SystemExit(main())
