#!/usr/bin/env python3
"""Search an eight-Switch high tail with audited family-1 phases as paid sources.

The authoritative physical solver is imported without modification.  This
wrapper projects only the six useful, always-driven D3/D4 ordinary nodes from
S3/S4 family model 1 into the 486-row high-tail domain.  It then adds two paid
NOR phases and asks the exact solver for S5/S6/S7/C8 using exactly eight
Switches (16 incremental gates) at D5.

The family Switch nodes are never exported as Boolean sources because each
individual output may be high impedance.
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
PHYSICAL_PATH = HERE / "physical_exact.py"
FAMILY_PATH = (
    ROOT
    / ".research/byte_adder_paper_synthesis_root/"
    "s34-internal-phase-family-r1.json"
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
TAIL_COMPONENTS = 8
TAIL_SWITCHES = 8
TAIL_GATE = 16
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


def _column_digest(column: Iterable[bool]) -> str:
    return sha256(bytes(int(value) for value in column)).hexdigest()


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


physical = _load_module(
    "s34_family1_two_phase_free_physical", PHYSICAL_PATH, EXPECTED_PHYSICAL_SHA256
)


@dataclass(frozen=True)
class Signal:
    driven: tuple[bool, ...]
    value: tuple[bool, ...]
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
    if sum(str(item["kind"]) == "SWITCH" for item in network) != 2:
        raise RuntimeError("family model-1 Switch count changed")
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


def _resolve_full_bus(
    signals: dict[int, Signal], bus: Iterable[int], *, label: str
) -> Signal:
    sources = tuple(int(source) for source in bus)
    if not sources:
        raise ValueError(f"empty full-driven BUS: {label}")
    try:
        selected = tuple(signals[source] for source in sources)
    except KeyError as exc:
        raise ValueError(f"unavailable source {exc.args[0]} in {label}") from exc
    rows = len(selected[0].value)
    values: list[bool] = []
    for case in range(rows):
        if not all(signal.driven[case] for signal in selected):
            raise ValueError(f"high-impedance input in {label} at row {case}")
        active = {signal.value[case] for signal in selected}
        if len(active) != 1:
            raise ValueError(f"conflicting input BUS {label} at row {case}")
        values.append(next(iter(active)))
    return Signal(
        (True,) * rows,
        tuple(values),
        max(signal.arrival for signal in selected),
        "+".join(signal.label for signal in selected),
    )


def _resolve_partial_bus(
    signals: dict[int, Signal], bus: Iterable[int], *, label: str
) -> Signal:
    sources = tuple(int(source) for source in bus)
    if not sources:
        raise ValueError(f"empty output BUS: {label}")
    selected = tuple(signals[source] for source in sources)
    rows = len(selected[0].value)
    values: list[bool] = []
    for case in range(rows):
        active = {
            signal.value[case] for signal in selected if signal.driven[case]
        }
        if not active:
            raise ValueError(f"undriven output BUS {label} at row {case}")
        if len(active) != 1:
            raise ValueError(f"conflicting output BUS {label} at row {case}")
        values.append(next(iter(active)))
    return Signal(
        (True,) * rows,
        tuple(values),
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


def build_domain_with_provenance(profile: str):
    if profile not in PHASE_PROFILES:
        raise ValueError(f"unknown phase profile: {profile}")
    base = physical.domain_s34567c8_leaf()
    local = physical.domain_s3456_leaf()
    record = _load_family_record()
    rows = base.rows
    base_by_name = dict(zip(base.names, base.columns, strict=True))
    local_names = (*local.names, "0", "1")
    if len(local_names) != 26:
        raise RuntimeError("reviewed family source ABI changed")

    signals: dict[int, Signal] = {}
    for source, name in enumerate(local_names):
        if name == "0":
            column = (False,) * rows
            arrival = 0
        elif name == "1":
            column = (True,) * rows
            arrival = 0
        else:
            if name not in base_by_name:
                raise ValueError(f"family source {name!r} absent from high-tail domain")
            column = tuple(base_by_name[name])
            arrival = int(base.arrivals[name])
        signals[source] = Signal((True,) * rows, column, arrival, name)

    useful = set(EXPECTED_USEFUL_SLOTS)
    exported: list[Signal] = []
    exported_records: list[dict[str, object]] = []
    network = list(record["network"])
    for expected_slot, item in enumerate(network):
        slot = int(item["slot"])
        source = int(item["source"])
        kind = str(item["kind"])
        if slot != expected_slot or source != len(local_names) + slot:
            raise RuntimeError("family model-1 network is not topological")
        left_sources = tuple(int(value) for value in item["left_bus"])
        right_sources = tuple(int(value) for value in item["right_bus"])
        left = _resolve_full_bus(signals, left_sources, label=f"u{slot}.left")
        right = _resolve_full_bus(signals, right_sources, label=f"u{slot}.right")
        input_arrival = max(left.arrival, right.arrival)
        gate_delay = int(physical.G.DELAY[physical.G.KINDS.index(kind)])
        arrival = input_arrival + gate_delay
        if arrival > int(item["depth_upper_bound"]):
            raise RuntimeError(f"family u{slot} exceeds its reviewed timing bound")

        label = f"s34_family1_u{slot}"
        if kind in ORDINARY_KINDS:
            value = _apply_ordinary(kind, left.value, right.value)
            signal = Signal((True,) * rows, value, arrival, label)
        elif kind == "SWITCH":
            signal = Signal(left.value, right.value, arrival, label)
        else:
            raise RuntimeError(f"unexpected family gate kind: {kind}")
        signals[source] = signal

        if slot in useful:
            if kind not in ORDINARY_KINDS or not all(signal.driven):
                raise RuntimeError(f"family useful slot u{slot} is not always driven")
            if arrival > MAX_DELAY - 1:
                raise RuntimeError(f"family useful slot u{slot} cannot feed a D5 Switch")
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
                    "truth_sha256": _column_digest(signal.value),
                }
            )

    if len(exported) != len(EXPECTED_USEFUL_SLOTS):
        raise RuntimeError("not all reviewed useful family nodes were exported")
    s3 = _resolve_partial_bus(signals, EXPECTED_OUTPUT_BUSES[0], label="S3")
    s4 = _resolve_partial_bus(signals, EXPECTED_OUTPUT_BUSES[1], label="S4")
    if s3.value != _target_column(base, "S3"):
        raise RuntimeError("family model-1 S3 does not extend to all 486 rows")
    if s4.value != _target_column(base, "S4"):
        raise RuntimeError("family model-1 S4 does not extend to all 486 rows")

    phase_signals: list[Signal] = []
    phase_records: list[dict[str, object]] = []
    for name, left_name, right_name in PHASE_PROFILES[profile]:
        left_column = tuple(base_by_name[left_name])
        right_column = tuple(base_by_name[right_name])
        value = _apply_ordinary("NOR", left_column, right_column)
        arrival = max(base.arrivals[left_name], base.arrivals[right_name]) + 1
        if arrival > MAX_DELAY - 1:
            raise RuntimeError(f"paid phase {name} cannot feed a D5 Switch")
        signal = Signal((True,) * rows, value, int(arrival), name)
        phase_signals.append(signal)
        phase_records.append(
            {
                "name": name,
                "kind": "NOR",
                "left": left_name,
                "right": right_name,
                "arrival": int(arrival),
                "always_driven": True,
                "truth_sha256": _column_digest(value),
            }
        )

    target_indices = tuple(base.output_names.index(name) for name in TAIL_OUTPUTS)
    paid_signals = (*exported, *phase_signals)
    names = (*base.names, *(signal.label for signal in paid_signals))
    columns = (*base.columns, *(signal.value for signal in paid_signals))
    arrivals = {
        **base.arrivals,
        **{signal.label: signal.arrival for signal in paid_signals},
    }
    domain = physical.Domain(
        names,
        columns,
        tuple(base.targets[index] for index in target_indices),
        arrivals,
        TAIL_OUTPUTS,
    )
    provenance = {
        "schema": "s34-family1-two-phase-free-source-projection-v1",
        "profile": profile,
        "rows": rows,
        "tail_outputs": TAIL_OUTPUTS,
        "family": {
            "path": str(FAMILY_PATH.relative_to(ROOT)).replace("\\", "/"),
            "sha256": EXPECTED_FAMILY_SHA256,
            "model_index": EXPECTED_MODEL_INDEX,
            "phase_family_sha256": EXPECTED_PHASE_FAMILY_SHA256,
            "paid_gate": 11,
            "paid_components": 9,
            "output_buses": [list(bus) for bus in EXPECTED_OUTPUT_BUSES],
            "s3_s4_replayed_over_486_rows": True,
        },
        "exported_family_nodes": exported_records,
        "fixed_paid_phases": phase_records,
        "excluded_family_nodes": [
            {
                "source_slot": 5,
                "reason": "arrival D5 cannot feed an incremental D5 Switch",
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
        "accounting": {
            "paid_s34_gate": 11,
            "paid_phase_gate": 2,
            "tail_gate_bound": TAIL_GATE,
            "combined_high_window_gate": 29,
            "combined_components": 19,
            "combined_switches": 10,
            "max_delay": MAX_DELAY,
        },
    }
    return domain, provenance


def dependency_sha256() -> dict[str, str]:
    paths = (Path(__file__).resolve(), PHYSICAL_PATH, FAMILY_PATH)
    return {
        str(path.relative_to(ROOT)).replace("\\", "/"): _digest(path)
        for path in paths
    }


def _validate_search_args(args: argparse.Namespace) -> None:
    if args.gate_bound != TAIL_GATE:
        raise ValueError(f"gate-bound must be {TAIL_GATE}")
    if args.max_delay != MAX_DELAY:
        raise ValueError(f"max-delay must be {MAX_DELAY}")
    if args.components != TAIL_COMPONENTS:
        raise ValueError(f"components must be {TAIL_COMPONENTS}")
    if args.switches != TAIL_SWITCHES or args.xors != 0:
        raise ValueError("this projection requires exactly eight Switches and zero XORs")
    exact_kinds = ",".join(["SWITCH"] * TAIL_COMPONENTS)
    if args.fixed_kinds is None:
        args.fixed_kinds = exact_kinds
    elif args.fixed_kinds != exact_kinds:
        raise ValueError(f"fixed-kinds must be {exact_kinds}")


def _self_check() -> dict[str, object]:
    profiles: dict[str, object] = {}
    for profile in PHASE_PROFILES:
        domain, provenance = build_domain_with_provenance(profile)
        paid_names = domain.names[len(physical.domain_s34567c8_leaf().names) :]
        profiles[profile] = {
            "rows": domain.rows,
            "outputs": domain.output_names,
            "paid_source_count": len(paid_names),
            "paid_sources": paid_names,
            "paid_source_arrivals": {
                name: domain.arrivals[name] for name in paid_names
            },
            "accounting": provenance["accounting"],
        }
    return {
        "status": "verified",
        "schema": "s34-family1-two-phase-free-self-check-v1",
        "dependency_sha256": dependency_sha256(),
        "family_model_index": EXPECTED_MODEL_INDEX,
        "family_phase_sha256": EXPECTED_PHASE_FAMILY_SHA256,
        "profiles": profiles,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-check", action="store_true")
    parser.add_argument("--phase-profile", choices=tuple(PHASE_PROFILES), default="primary")
    parser.add_argument("--gate-bound", type=int, default=TAIL_GATE)
    parser.add_argument("--max-delay", type=int, default=MAX_DELAY)
    parser.add_argument("--components", type=int, default=TAIL_COMPONENTS)
    parser.add_argument("--switches", type=int, default=TAIL_SWITCHES)
    parser.add_argument("--xors", type=int, default=0)
    parser.add_argument("--fixed-kinds")
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
    if args.output is None:
        raise ValueError("--output is required")
    _validate_search_args(args)
    domain, provenance = build_domain_with_provenance(args.phase_profile)
    domain_name = f"s567c8_s34_family1_two_phase_{args.phase_profile}_free"
    physical.DOMAINS[domain_name] = lambda: domain
    args.domain = domain_name
    args.outputs = None
    payload = physical.solve(args)
    payload["base_schema"] = payload["schema"]
    payload["schema"] = "exact-s34-family1-two-phase-free-tail-v1"
    payload["free_source_projection"] = provenance
    payload["extended_dependency_sha256"] = dependency_sha256()
    if payload["status"] == "sat":
        network = payload.get("network", ())
        if len(network) != TAIL_COMPONENTS:
            raise RuntimeError("decoded SAT witness has the wrong component count")
        if any(item.get("kind") != "SWITCH" for item in network):
            raise RuntimeError("decoded SAT witness is not an all-Switch tail")
        if int(payload.get("actual_gate", -1)) != TAIL_GATE:
            raise RuntimeError("decoded SAT witness has the wrong tail gate cost")
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
