"""Search the Byte Adder high tail while reusing paid S3/S4 phases.

The authoritative 11-gate S3/S4 witness contains seven ordinary, always-
driven gates followed by two Switch drivers for S4.  This wrapper replays only
those seven ordinary gates over the full 486-row S3..S7/C8 domain and exposes
their outputs as zero-incremental-cost sources to the exact physical solver.

The two Switch outputs are deliberately not exposed: individually they may be
high impedance, so treating them as Boolean sources would be unsound.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PHYSICAL_PATH = ROOT / ".research/byte_adder_phase_shortcut_restart/physical_exact.py"
S34_WITNESS_PATH = (
    ROOT
    / ".research/byte_adder_phase_shortcut_restart/s34_g11_d5_joint_exact.json"
)
DOMAIN_NAME = "s567c8_s34_free"
TAIL_OUTPUTS = ("S5", "S6", "S7", "C8")
EXPORTED_COUNT = 7
EXPECTED_S34_SHA256 = (
    "69b0e3f1b6300da157de50f3b256f487211e9a141a0502cc71d476a895d48a36"
)
ORDINARY_KINDS = {"NOT", "AND", "OR", "NAND", "NOR"}
DELAY = {"NOT": 1, "AND": 1, "OR": 1, "NAND": 1, "NOR": 1}


def _digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


physical = _load_module("s34_free_physical_exact", PHYSICAL_PATH)


def _load_s34_witness() -> dict[str, object]:
    actual = _digest(S34_WITNESS_PATH)
    if actual != EXPECTED_S34_SHA256:
        raise RuntimeError(
            "authoritative S3/S4 witness changed: "
            f"expected {EXPECTED_S34_SHA256}, got {actual}"
        )
    payload = json.loads(S34_WITNESS_PATH.read_text(encoding="utf-8"))
    if payload.get("status") != "sat":
        raise ValueError("S3/S4 witness is not SAT")
    if tuple(payload.get("output_names", ())) != ("S3", "S4"):
        raise ValueError("unexpected S3/S4 witness outputs")
    if int(payload.get("actual_gate", -1)) != 11:
        raise ValueError("unexpected S3/S4 witness cost")
    verification = payload.get("verification", {})
    for field in (
        "mismatch_count",
        "bus_conflict_count",
        "undriven_output_count",
        "physical_net_partition_violation_count",
        "depth_upper_bound_violation_count",
        "output_deadline_violation_count",
    ):
        if int(verification.get(field, -1)) != 0:
            raise ValueError(f"S3/S4 witness failed {field}")
    return payload


def _resolve_full_driven_bus(
    columns: list[tuple[bool, ...]], bus: list[int], *, label: str
) -> tuple[bool, ...]:
    if not bus:
        raise ValueError(f"empty ordinary-gate bus: {label}")
    rows = len(columns[0])
    result: list[bool] = []
    for case in range(rows):
        active = {columns[source][case] for source in bus}
        if len(active) != 1:
            raise ValueError(f"conflicting full-driven bus {label} at row {case}")
        result.append(next(iter(active)))
    return tuple(result)


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
    raise ValueError(f"non-ordinary exported gate: {kind}")


def _source_labels(
    bus: list[int], labels: list[str], *, label: str
) -> list[str]:
    try:
        return [labels[source] for source in bus]
    except IndexError as exc:
        raise ValueError(f"non-topological source in {label}") from exc


def build_domain_with_provenance():
    """Return the extended exact domain and its audited source provenance."""

    base = physical.domain_s34567c8_leaf()
    witness = _load_s34_witness()
    witness_free = list(witness["free_sources"])
    base_by_name = dict(zip(base.names, base.columns, strict=True))
    rows = base.rows

    columns: list[tuple[bool, ...]] = []
    arrivals: list[int] = []
    labels: list[str] = []
    for name in witness_free:
        if name == "0":
            column = (False,) * rows
            arrival = 0
        elif name == "1":
            column = (True,) * rows
            arrival = 0
        else:
            if name not in base_by_name:
                raise ValueError(f"S3/S4 source {name!r} absent from full domain")
            column = base_by_name[name]
            arrival = int(base.arrivals[name])
        columns.append(tuple(column))
        arrivals.append(arrival)
        labels.append(name)

    network = list(witness["network"])
    if len(network) != 9:
        raise ValueError("expected seven ordinary gates and two S4 Switches")
    if any(str(item["kind"]) != "SWITCH" for item in network[EXPORTED_COUNT:]):
        raise ValueError("S4 tail is no longer exactly two Switch drivers")

    exported_columns: list[tuple[bool, ...]] = []
    exported_arrivals: dict[str, int] = {}
    provenance_nodes: list[dict[str, object]] = []
    local_source_count = len(witness_free)
    for slot, item in enumerate(network[:EXPORTED_COUNT]):
        if int(item["slot"]) != slot:
            raise ValueError("S3/S4 network is not topological")
        if int(item["source"]) != local_source_count + slot:
            raise ValueError("unexpected S3/S4 component source numbering")
        kind = str(item["kind"])
        if kind not in ORDINARY_KINDS:
            raise ValueError(f"cannot export {kind} as a full-driven source")
        left_bus = [int(source) for source in item["left_bus"]]
        right_bus = [int(source) for source in item["right_bus"]]
        left_names = _source_labels(left_bus, labels, label=f"u{slot}.left")
        right_names = _source_labels(right_bus, labels, label=f"u{slot}.right")
        left = _resolve_full_driven_bus(columns, left_bus, label=f"u{slot}.left")
        right = (
            (False,) * rows
            if kind == "NOT"
            else _resolve_full_driven_bus(columns, right_bus, label=f"u{slot}.right")
        )
        output = _apply_ordinary(kind, left, right)
        input_sources = left_bus if kind == "NOT" else [*left_bus, *right_bus]
        arrival = max(arrivals[source] for source in input_sources) + DELAY[kind]
        if arrival > int(item["depth_upper_bound"]):
            raise ValueError(f"u{slot} exceeds witness timing bound")

        name = f"s34_u{slot}"
        columns.append(output)
        arrivals.append(arrival)
        labels.append(name)
        exported_columns.append(output)
        exported_arrivals[name] = arrival
        provenance_nodes.append(
            {
                "name": name,
                "source_slot": slot,
                "kind": kind,
                "left_bus": left_names,
                "right_bus": right_names,
                "arrival": arrival,
                "always_driven": True,
            }
        )

    s3_index = base.output_names.index("S3")
    expected_s3 = tuple(
        bool((base.targets[s3_index] >> case) & 1) for case in range(rows)
    )
    if exported_columns[-1] != expected_s3:
        raise ValueError("exported u6 no longer equals S3 over all 486 rows")

    target_indices = tuple(base.output_names.index(name) for name in TAIL_OUTPUTS)
    names = (*base.names, *(f"s34_u{slot}" for slot in range(EXPORTED_COUNT)))
    domain_columns = (*base.columns, *exported_columns)
    domain_arrivals = {**base.arrivals, **exported_arrivals}
    domain = physical.Domain(
        names,
        domain_columns,
        tuple(base.targets[index] for index in target_indices),
        domain_arrivals,
        TAIL_OUTPUTS,
    )
    provenance = {
        "schema": "s34-free-intermediate-provenance-v1",
        "s34_witness": {
            "path": str(S34_WITNESS_PATH.relative_to(ROOT)).replace("\\", "/"),
            "sha256": _digest(S34_WITNESS_PATH),
            "paid_gate": 11,
            "paid_components": 9,
        },
        "exported_nodes": provenance_nodes,
        "excluded_nodes": [
            {
                "slot": int(item["slot"]),
                "kind": str(item["kind"]),
                "reason": "individual Switch output may be high impedance",
            }
            for item in network[EXPORTED_COUNT:]
        ],
        "rows": rows,
        "tail_outputs": TAIL_OUTPUTS,
        "u6_equals_s3": True,
    }
    return domain, provenance


def build_domain():
    return build_domain_with_provenance()[0]


def dependency_sha256() -> dict[str, str]:
    paths = (Path(__file__).resolve(), PHYSICAL_PATH, S34_WITNESS_PATH)
    return {
        str(path.relative_to(ROOT)).replace("\\", "/"): _digest(path)
        for path in paths
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate-bound", type=int, required=True)
    parser.add_argument("--max-delay", type=int, default=5)
    parser.add_argument("--components", type=int, required=True)
    parser.add_argument("--switches", type=int, required=True)
    parser.add_argument("--xors", type=int, required=True)
    parser.add_argument(
        "--fixed-kinds",
        help="comma-separated exact kind for every topological component slot",
    )
    parser.add_argument("--split-slots", type=int, default=3)
    parser.add_argument("--shard-count", type=int, default=1)
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--solver", default="glucose42")
    parser.add_argument("--timeout", type=float, default=0.0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.domain = DOMAIN_NAME
    args.outputs = None

    domain, provenance = build_domain_with_provenance()
    physical.DOMAINS[DOMAIN_NAME] = lambda: domain
    payload = physical.solve(args)
    payload["free_intermediate_provenance"] = provenance
    payload["extended_dependency_sha256"] = dependency_sha256()
    encoded = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(encoded, encoding="utf-8")
    summary = {key: value for key, value in payload.items() if key != "network"}
    summary["output"] = str(args.output)
    summary["sha256"] = sha256(encoded.encode()).hexdigest()
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if payload["status"] != "unknown" else 2


if __name__ == "__main__":
    raise SystemExit(main())
