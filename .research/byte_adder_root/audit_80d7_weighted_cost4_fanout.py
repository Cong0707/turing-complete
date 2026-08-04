"""Independent audit of the weighted-cost-four arbitrary-fanout closure.

The SAT worker is deliberately *not* imported here.  This checker reads the
reviewed Factory DAG, recomputes the S2/S4 source partitions, validates the
eight negative result records and their cross-solver CNF identity, and fully
replays all four positive-control witnesses over 131072 input rows.

The negative records do not contain proof traces.  Accordingly this audit
certifies the recorded dual-solver experiment and its exact scope; it does not
promote the result into a proof of a global 79/7 lower bound.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DEFAULT_DAG = HERE / "byte-adder-hybrid-phasefold-g80-d7.json"
DEFAULT_OUTPUT = HERE / "weighted-cost4-fanout-80d7-audit.json"
MATERIALIZER = (
    ROOT / ".research" / "byte_adder_builder_layout_agent" / "materialize_factory_dag.py"
)
FULL_ROWS = 1 << 17
MASK = (1 << FULL_ROWS) - 1

KINDS = ("NOT", "AND", "OR", "NAND", "NOR", "XOR", "SWITCH")
COST = {"NOT": 1, "AND": 1, "OR": 1, "NAND": 1, "NOR": 1, "XOR": 3, "SWITCH": 2}
DELAY = {"NOT": 1, "AND": 1, "OR": 1, "NAND": 1, "NOR": 1, "XOR": 2, "SWITCH": 1}

TARGETS = {
    "s2": {
        "node": 81,
        "sources": (4, 5, 6, 7, 22, 23, 24, 25, 45, 50, 51, 52, 54, 55, 56, 76, 77),
    },
    "s4": {
        "node": 86,
        "sources": (8, 9, 10, 11, 28, 29, 30, 31, 32, 56, 57, 59, 60, 61, 62, 82, 83),
    },
}

EXPECTED_CNF = {
    ("s2", "negative"): (2845, 28434, "3d74901cfa9efe18d6cb51d6e48f87c20d0c7efaeb13b215cc262436bda7d123"),
    ("s4", "negative"): (2845, 28791, "fc2a2c8e8b1ffa79f62534f2fdd4b5bd1b7fc972b126353a1fe082a2c0dff278"),
    ("s2", "constants"): (2931, 31162, "19c7b5dd6c6ed13c869cd079fdcebbc16b19fb3616f293e57cbf2eed95cabbb6"),
    ("s4", "constants"): (2931, 31519, "d13e13d3284bec625c18ddc763c3f52582ec3ba0cea0679a219048f7468954f6"),
    ("s2", "positive"): (6086, 58210, "7624681eb838574621304f19b75509941ce4471c31f1ed0100874704508466d2"),
    ("s4", "positive"): (6086, 58799, "84a95f766b8cfba4485bdc76ae2ddec56808bde84661f68aab044e2d0bdbf300"),
}


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_materializer():
    spec = importlib.util.spec_from_file_location(
        "byte_adder_weighted_fanout_audit_materializer", MATERIALIZER
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(MATERIALIZER)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def expected_files() -> dict[str, tuple[str, str, str]]:
    files: dict[str, tuple[str, str, str]] = {}
    for target in TARGETS:
        for solver in ("cadical195", "glucose42"):
            files[f"weighted-cost4-fanout-{target}-{solver}.json"] = (
                target,
                "negative",
                solver,
            )
            files[f"weighted-cost4-fanout-{target}-{solver}-constants.json"] = (
                target,
                "constants",
                solver,
            )
            files[f"weighted-cost4-fanout-{target}-positive-{solver}.json"] = (
                target,
                "positive",
                solver,
            )
    return files


def compact_partition(
    source_ids: tuple[int, ...], target: int, states: dict[int, dict[str, int]]
) -> tuple[int, int]:
    classes: dict[tuple[int, ...], tuple[int, int, int]] = {}
    inconsistent = 0
    for row in range(FULL_ROWS):
        signature: list[int] = []
        for node_id in source_ids:
            state = states[node_id]
            if int(state["conflict"]):
                raise RuntimeError(f"source node {node_id} contains conflicts")
            signature.extend(
                (
                    (int(state["bits"]) >> row) & 1,
                    (int(state["driven"]) >> row) & 1,
                )
            )
        target_state = states[target]
        target_value = (
            (int(target_state["bits"]) >> row) & 1,
            (int(target_state["driven"]) >> row) & 1,
            (int(target_state["conflict"]) >> row) & 1,
        )
        key = tuple(signature)
        previous = classes.get(key)
        if previous is not None and previous != target_value:
            inconsistent += 1
        classes[key] = target_value
    return len(classes), inconsistent


def resolve_packed(
    bus: list[int], values: list[int], drivens: list[int]
) -> tuple[int, int, int]:
    ones = 0
    zeros = 0
    for source in bus:
        ones |= values[source] & drivens[source]
        zeros |= (~values[source] & MASK) & drivens[source]
    return ones & MASK, (ones | zeros) & MASK, (ones & zeros) & MASK


def physical_partition_violations(buses: list[list[int]]) -> int:
    violations = 0
    for index, left in enumerate(buses):
        left_set = set(left)
        for right in buses[index + 1 :]:
            right_set = set(right)
            if left_set & right_set and left_set != right_set:
                violations += 1
    return violations


def replay_positive(
    payload: dict[str, Any], states: dict[int, dict[str, int]], errors: list[str]
) -> dict[str, Any]:
    target_name = str(payload["target"])
    target_spec = TARGETS[target_name]
    source_ids = tuple(int(value) for value in payload["source_ids"])
    values = [int(states[node_id]["bits"]) for node_id in source_ids]
    drivens = [int(states[node_id]["driven"]) for node_id in source_ids]
    arrivals = [int(states[node_id]["depth"]) for node_id in source_ids]
    source_count = len(values)
    network = list(payload.get("network", []))
    output_buses = [list(map(int, bus)) for bus in payload.get("output_buses", [])]
    all_buses: list[list[int]] = []
    conflict = 0
    actual_gate = 0
    switch_count = 0
    xor_count = 0

    for slot, item in enumerate(network):
        label = f"{target_name} slot {slot}"
        kind = str(item.get("kind"))
        left = list(map(int, item.get("left_bus", [])))
        right = list(map(int, item.get("right_bus", [])))
        all_buses.extend((left, right))
        available = source_count + slot
        if int(item.get("slot", -1)) != slot:
            errors.append(f"{label}: non-canonical slot number")
        if int(item.get("source", -1)) != available:
            errors.append(f"{label}: non-canonical source number")
        if kind not in KINDS:
            errors.append(f"{label}: unsupported kind {kind}")
            continue
        if not left or any(source < 0 or source >= available for source in left):
            errors.append(f"{label}: invalid left bus")
        if kind == "NOT":
            if right:
                errors.append(f"{label}: NOT has a right input")
        elif not right or any(source < 0 or source >= available for source in right):
            errors.append(f"{label}: invalid right bus")
        for bus_name, bus in (("left", left), ("right", right)):
            if len(bus) != len(set(bus)):
                errors.append(f"{label}: duplicate driver on {bus_name} bus")
            if len(bus) > 1:
                for source in bus:
                    if source < source_count:
                        errors.append(f"{label}: primary source on multi-driver bus")
                    elif str(network[source - source_count].get("kind")) != "SWITCH":
                        errors.append(f"{label}: non-Switch source on multi-driver bus")

        left_value, _, left_conflict = resolve_packed(left, values, drivens)
        right_value, _, right_conflict = resolve_packed(right, values, drivens)
        conflict |= left_conflict | right_conflict
        if kind == "NOT":
            value, driven = ~left_value & MASK, MASK
        elif kind == "AND":
            value, driven = left_value & right_value, MASK
        elif kind == "OR":
            value, driven = left_value | right_value, MASK
        elif kind == "NAND":
            value, driven = ~(left_value & right_value) & MASK, MASK
        elif kind == "NOR":
            value, driven = ~(left_value | right_value) & MASK, MASK
        elif kind == "XOR":
            value, driven = left_value ^ right_value, MASK
            xor_count += 1
        else:
            value, driven = left_value & right_value, left_value
            switch_count += 1

        selected = set(left) | set(right)
        actual_arrival = max((arrivals[source] for source in selected), default=0) + DELAY[kind]
        recorded_bound = int(item.get("depth_upper_bound", -1))
        if actual_arrival > recorded_bound or recorded_bound > int(payload["max_delay"]):
            errors.append(f"{label}: invalid timing bound")
        if int(item.get("cost", -1)) != COST[kind]:
            errors.append(f"{label}: recorded cost mismatch")
        actual_gate += COST[kind]
        values.append(value & MASK)
        drivens.append(driven & MASK)
        arrivals.append(actual_arrival)

    all_buses.extend(output_buses)
    partition = physical_partition_violations(all_buses)
    if partition:
        errors.append(f"{target_name}: {partition} physical-net partition violations")

    for slot in range(len(network)):
        source = source_count + slot
        live = any(
            source in list(map(int, later.get("left_bus", [])))
            or source in list(map(int, later.get("right_bus", [])))
            for later in network[slot + 1 :]
        ) or any(source in bus for bus in output_buses)
        if not live:
            errors.append(f"{target_name} slot {slot}: dead component")

    if len(output_buses) != 1 or not output_buses[0]:
        errors.append(f"{target_name}: invalid output bus count")
        output = output_driven = output_conflict = output_arrival = 0
    else:
        output = resolve_packed(output_buses[0], values, drivens)
        output, output_driven, output_conflict = output
        output_arrival = max(arrivals[source] for source in output_buses[0])
    conflict |= output_conflict
    target_bits = int(states[int(target_spec["node"])]["bits"])
    result = {
        "truth_rows": FULL_ROWS,
        "mismatch_count": (output ^ target_bits).bit_count(),
        "conflict_assignment_count": conflict.bit_count(),
        "undriven_output_count": (MASK ^ output_driven).bit_count(),
        "actual_gate": actual_gate,
        "actual_output_arrival": output_arrival,
        "switch_count": switch_count,
        "xor_count": xor_count,
        "physical_net_partition_violation_count": partition,
        "live_components": len(network),
    }
    if actual_gate != int(payload["actual_gate"]):
        errors.append(f"{target_name}: actual gate mismatch")
    if actual_gate > int(payload["gate_bound"]):
        errors.append(f"{target_name}: gate bound exceeded")
    if output_arrival > int(payload["max_delay"]):
        errors.append(f"{target_name}: delay bound exceeded")
    if switch_count != int(payload["exact_switches"]) or xor_count != int(payload["exact_xors"]):
        errors.append(f"{target_name}: exact kind count mismatch")
    for key in (
        "mismatch_count",
        "conflict_assignment_count",
        "undriven_output_count",
        "actual_gate",
        "actual_output_arrival",
    ):
        if int(payload.get("full_verification", {}).get(key, -1)) != int(result[key]):
            errors.append(f"{target_name}: stored full verification mismatch for {key}")
    if any(
        result[key]
        for key in (
            "mismatch_count",
            "conflict_assignment_count",
            "undriven_output_count",
            "physical_net_partition_violation_count",
        )
    ):
        errors.append(f"{target_name}: positive witness replay failed")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dag", type=Path, default=DEFAULT_DAG)
    parser.add_argument("--directory", type=Path, default=HERE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    errors: list[str] = []
    dag = json.loads(args.dag.read_text(encoding="utf-8"))
    materializer = load_materializer()
    states = materializer.logical_states(tuple(dag["factory_dag"]["nodes"]))
    dag_sha = file_sha256(args.dag)
    expected = expected_files()
    records: list[dict[str, Any]] = []
    pair_keys: dict[tuple[str, str], list[dict[str, Any]]] = {}

    partitions: dict[str, dict[str, int]] = {}
    for target, spec in TARGETS.items():
        compact_rows, inconsistent = compact_partition(spec["sources"], spec["node"], states)
        target_state = states[int(spec["node"])]
        fully_driven = int(target_state["driven"]) == MASK and int(target_state["conflict"]) == 0
        partitions[target] = {
            "compact_truth_rows": compact_rows,
            "inconsistent_rows": inconsistent,
            "fully_driven_conflict_free": int(fully_driven),
        }
        if compact_rows != 48 or inconsistent or not fully_driven:
            errors.append(f"{target}: source partition audit failed")

    for filename, (target, variant, solver) in sorted(expected.items()):
        path = args.directory / filename
        if not path.is_file():
            errors.append(f"missing result {filename}")
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        local_errors: list[str] = []
        negative = variant != "positive"
        expected_constants = variant == "constants"
        expected_gate = 4 if negative else 5
        expected_components = 3 if negative else 5
        expected_switches = 1 if negative else 0
        expected_status = "unsat" if negative else "sat"
        expected_vars, expected_clauses, expected_cnf = EXPECTED_CNF[(target, variant)]
        required = {
            "schema": "byte-adder-80d7-weighted-cost4-fanout-exact-v1",
            "status": expected_status,
            "source_dag_sha256": dag_sha,
            "target": target,
            "target_node": int(TARGETS[target]["node"]),
            "compact_truth_rows": 48,
            "include_constants": expected_constants,
            "gate_bound": expected_gate,
            "max_delay": 7,
            "components": expected_components,
            "exact_switches": expected_switches,
            "exact_xors": 0,
            "solver": solver,
            "variables": expected_vars,
            "clauses": expected_clauses,
            "cnf_sha256": expected_cnf,
            "physical_nets": True,
        }
        for key, value in required.items():
            if payload.get(key) != value:
                local_errors.append(f"{key}: expected {value!r}, got {payload.get(key)!r}")
        if tuple(payload.get("source_ids", ())) != TARGETS[target]["sources"]:
            local_errors.append("reviewed source pool changed")
        if Path(str(payload.get("source_dag", ""))).name != args.dag.name:
            local_errors.append("source DAG path does not name the reviewed DAG")
        for relative, recorded_sha in payload.get("dependency_sha256", {}).items():
            dependency = ROOT / Path(relative)
            if not dependency.is_file() or file_sha256(dependency) != recorded_sha:
                local_errors.append(f"dependency hash mismatch: {relative}")
        if len(payload.get("dependency_sha256", {})) != 4:
            local_errors.append("dependency inventory changed")
        replay = None
        if negative:
            if "network" in payload or "output_buses" in payload:
                local_errors.append("negative record unexpectedly contains a witness")
        else:
            replay = replay_positive(payload, states, local_errors)
            compact = payload.get("compact_verification", {})
            if any(int(compact.get(key, -1)) for key in (
                "mismatch_count",
                "bus_conflict_count",
                "undriven_output_count",
                "physical_net_partition_violation_count",
            )):
                local_errors.append("stored compact verification is not clean")
        if local_errors:
            errors.extend(f"{filename}: {message}" for message in local_errors)
        record = {
            "file": filename,
            "sha256": file_sha256(path),
            "target": target,
            "variant": variant,
            "solver": solver,
            "status": payload.get("status"),
            "variables": payload.get("variables"),
            "clauses": payload.get("clauses"),
            "cnf_sha256": payload.get("cnf_sha256"),
            "positive_replay": replay,
            "audit_pass": not local_errors,
        }
        records.append(record)
        pair_keys.setdefault((target, variant), []).append(record)

    pair_checks: list[dict[str, Any]] = []
    for (target, variant), pair in sorted(pair_keys.items()):
        identity = len(pair) == 2 and len({
            (item["variables"], item["clauses"], item["cnf_sha256"]) for item in pair
        }) == 1
        solvers = sorted(str(item["solver"]) for item in pair)
        passed = identity and solvers == ["cadical195", "glucose42"]
        if not passed:
            errors.append(f"{target}/{variant}: cross-solver CNF identity failed")
        pair_checks.append(
            {
                "target": target,
                "variant": variant,
                "solvers": solvers,
                "identical_cnf": identity,
                "audit_pass": passed,
            }
        )

    audit = {
        "schema": "byte-adder-80d7-weighted-cost4-fanout-audit-v1",
        "status": "pass" if not errors else "fail",
        "scope": {
            "negative_records": 8,
            "positive_records": 4,
            "full_truth_rows_replayed_per_positive": FULL_ROWS,
            "claim": "reviewed-source local arbitrary-fanout closure only",
            "global_79d7_lower_bound_claimed": False,
            "proof_trace_present": False,
        },
        "inputs": {
            "dag": str(args.dag.relative_to(ROOT)).replace("\\", "/"),
            "dag_sha256": dag_sha,
            "materializer": str(MATERIALIZER.relative_to(ROOT)).replace("\\", "/"),
            "materializer_sha256": file_sha256(MATERIALIZER),
        },
        "partitions": partitions,
        "records": records,
        "cross_solver_checks": pair_checks,
        "errors": errors,
    }
    args.output.write_bytes(
        (json.dumps(audit, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    )
    print(json.dumps({"output": str(args.output.resolve()), "status": audit["status"], "records": len(records), "errors": errors}, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
