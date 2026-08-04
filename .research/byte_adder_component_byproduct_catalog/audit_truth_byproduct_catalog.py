"""Independently audit the generated primitive/byproduct truth catalog.

This script reads only derived research artifacts.  It does not touch game
state, candidates, level files, or Git state.
"""

from __future__ import annotations

import argparse
import base64
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DEFAULT_INPUT = HERE / "truth-byproduct-catalog-v1.json"
DEFAULT_OUTPUT = HERE / "truth-byproduct-catalog-v1.audit.json"


def canonical_json(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def mask_digest(row_count: int, packed: bytes) -> str:
    return sha256(
        b"tc-packed-mask-v1\0" + row_count.to_bytes(8, "little") + packed
    ).hexdigest()


def replay_full_adder(proof: dict[str, object]) -> dict[str, object]:
    inputs = ("A", "B", "C")
    columns = []
    for input_index in range(3):
        value = 0
        for assignment in range(8):
            value |= ((assignment >> input_index) & 1) << assignment
        columns.append(value)
    values = [*columns, 0, 0xFF]
    arrivals = [0] * len(values)
    for slot, operation in enumerate(proof["operations"]):
        require(int(operation["slot"]) == slot, "FullAdder proof slot order changed")
        left = values[int(operation["left"])]
        right = values[int(operation["right"])]
        kind = str(operation["kind"])
        if kind == "NOT":
            value = ~left
        elif kind == "AND":
            value = left & right
        elif kind == "OR":
            value = left | right
        elif kind == "NAND":
            value = ~(left & right)
        elif kind == "NOR":
            value = ~(left | right)
        else:
            raise RuntimeError(f"unexpected FullAdder proof kind: {kind}")
        values.append(value & 0xFF)
        arrival = max(
            arrivals[int(operation["left"])],
            arrivals[int(operation["right"])],
        ) + 1
        arrivals.append(arrival)
        require(
            int(operation["source"]) == len(values) - 1,
            "FullAdder proof source numbering changed",
        )
        require(
            int(operation["arrival"]) == arrival,
            "FullAdder proof arrival mismatch",
        )
    sum_target = 0
    carry_target = 0
    for assignment in range(8):
        bits = [(assignment >> index) & 1 for index in range(3)]
        sum_target |= (bits[0] ^ bits[1] ^ bits[2]) << assignment
        carry_target |= (sum(bits) >= 2) << assignment
    outputs = [int(value) for value in proof["outputs"]]
    require(
        [values[index] for index in outputs] == [sum_target, carry_target],
        "FullAdder witness truth mismatch",
    )
    return {
        "rows": 8,
        "gate": len(proof["operations"]),
        "delay": max(arrivals[index] for index in outputs),
        "sum_truth_hex": hex(sum_target),
        "carry_truth_hex": hex(carry_target),
        "mismatch_count": 0,
    }


def audit(path: Path) -> dict[str, object]:
    raw = path.read_bytes()
    payload = json.loads(raw)
    require(payload["status"] == "pass", "catalog status is not pass")
    require(
        payload["schema"] == "tc-primitive-expansion-physical-byproduct-catalog-v1",
        "catalog schema changed",
    )

    dependency_checks = {}
    for relative, expected in payload["dependencies"].items():
        dependency = ROOT / relative
        actual = sha256(dependency.read_bytes()).hexdigest()
        require(actual == expected, f"dependency hash mismatch: {relative}")
        dependency_checks[relative] = actual

    masks = payload["packed_masks"]
    for digest, record in masks.items():
        packed = base64.b64decode(record["little_endian_base64"], validate=True)
        rows = int(record["row_count"])
        byte_count = int(record["byte_count"])
        require(len(packed) == byte_count, f"mask byte count mismatch: {digest}")
        require(mask_digest(rows, packed) == digest, f"mask SHA mismatch: {digest}")
        value = int.from_bytes(packed, "little")
        require(value >> rows == 0, f"mask has bits outside domain: {digest}")
        require(value.bit_count() == int(record["ones"]), f"mask ones mismatch: {digest}")

    domains = payload["domains"]
    domain_rows = {}
    for domain_id, record in domains.items():
        rows = int(record["row_count"])
        domain_rows[domain_id] = rows
        require(int(record["byte_count"]) == (rows + 7) // 8, "domain byte count mismatch")
        for digest in record["input_mask_sha256"].values():
            require(digest in masks, f"missing domain input mask: {digest}")
            require(int(masks[digest]["row_count"]) == rows, "domain input row mismatch")

    owner_sets = payload["owner_sets"]
    for digest, record in owner_sets.items():
        owners = record["owners"]
        require(owners == sorted(set(owners)), f"non-canonical owner set: {digest}")
        require(sha256(canonical_json(owners)).hexdigest() == digest, "owner set SHA mismatch")
        require(len(owners) == int(record["owner_count"]), "owner count mismatch")

    producer_ids = set()
    producer_count = 0
    truth_ids = set()
    source_kinds = Counter()
    role_counts = Counter()
    for truth in payload["truth_classes"]:
        truth_sha = truth["truth_sha256"]
        require(truth_sha not in truth_ids, f"duplicate truth class: {truth_sha}")
        truth_ids.add(truth_sha)
        identity = {
            "schema": truth["schema"],
            "domain_id": truth["domain_id"],
            "value_mask_sha256": truth["value_mask_sha256"],
            "driven_mask_sha256": truth["driven_mask_sha256"],
            "conflict_mask_sha256": truth["conflict_mask_sha256"],
        }
        require(sha256(canonical_json(identity)).hexdigest() == truth_sha, "truth SHA mismatch")
        domain_id = truth["domain_id"]
        require(domain_id in domains, f"missing truth domain: {domain_id}")
        rows = domain_rows[domain_id]
        for field in ("value_mask_sha256", "driven_mask_sha256", "conflict_mask_sha256"):
            digest = truth[field]
            require(digest in masks, f"missing truth mask: {digest}")
            require(int(masks[digest]["row_count"]) == rows, "truth mask row mismatch")
        boolean_identity = {
            "schema": "tc-boolean-projection-v1",
            "domain_id": domain_id,
            "value_mask_sha256": truth["value_mask_sha256"],
        }
        require(
            sha256(canonical_json(boolean_identity)).hexdigest()
            == truth["boolean_projection_sha256"],
            "Boolean projection SHA mismatch",
        )
        require(
            bool(truth["fully_driven"])
            == (int(masks[truth["driven_mask_sha256"]]["ones"]) == rows),
            "fully-driven marker mismatch",
        )
        require(
            bool(truth["conflict_free"])
            == (int(masks[truth["conflict_mask_sha256"]]["ones"]) == 0),
            "conflict-free marker mismatch",
        )

        metrics: dict[tuple[int, int, int], list[dict[str, object]]] = {}
        for producer in truth["producers"]:
            producer_id = producer["producer_id"]
            require(producer_id not in producer_ids, f"duplicate producer: {producer_id}")
            producer_ids.add(producer_id)
            producer_count += 1
            source_kinds[producer["source_kind"]] += 1
            role_counts[producer["role"]] += 1
            owner_sha = producer["owner_set_sha256"]
            require(owner_sha in owner_sets, f"missing producer owner set: {owner_sha}")
            owner_record = owner_sets[owner_sha]
            require(int(producer["gate"]) == int(owner_record["gate"]), "producer gate mismatch")
            require(
                int(producer["owner_count"]) == int(owner_record["owner_count"]),
                "producer owner count mismatch",
            )
            require(all(int(value) >= 0 for value in producer["input_arc_depths"].values()), "negative arc")
            metric = (
                int(producer["gate"]),
                int(producer["delay"]),
                int(producer["owner_count"]),
            )
            metrics.setdefault(metric, []).append(producer)
        expected_frontier = []
        for metric in sorted(metrics):
            if any(
                other != metric
                and other[0] <= metric[0]
                and other[1] <= metric[1]
                and other[2] <= metric[2]
                for other in metrics
            ):
                continue
            producers = metrics[metric]
            expected_frontier.append(
                {
                    "gate": metric[0],
                    "delay": metric[1],
                    "owner_count": metric[2],
                    "producer_ids": sorted(str(item["producer_id"]) for item in producers),
                    "owner_set_sha256s": sorted(set(str(item["owner_set_sha256"]) for item in producers)),
                    "physical_owners": sorted(
                        set(
                            str(item["physical_owner"])
                            for item in producers
                            if item["physical_owner"] is not None
                        )
                    ),
                }
            )
        require(expected_frontier == truth["pareto_gate_delay_owners"], "truth Pareto mismatch")
        require(int(truth["producer_count"]) == len(truth["producers"]), "truth producer count mismatch")

    summary = payload["summary"]
    require(int(summary["domain_count"]) == len(domains), "summary domain count mismatch")
    require(int(summary["truth_class_count"]) == len(truth_ids), "summary truth count mismatch")
    require(int(summary["producer_count"]) == producer_count, "summary producer count mismatch")
    require(int(summary["packed_mask_count"]) == len(masks), "summary mask count mismatch")
    require(int(summary["owner_set_count"]) == len(owner_sets), "summary owner count mismatch")

    primitive = payload["primitive_library"]
    minima = primitive["exhaustive_minima"]
    require(set(minima) == {"XOR", "XNOR", "AND3", "OR3"}, "minimum coverage mismatch")
    for component, expected_gate in {"XOR": 3, "XNOR": 3, "AND3": 2, "OR3": 2}.items():
        require(not any(minima[component]["lower_gate_structure_counts"]), f"bad lower minimum: {component}")
        require(int(minima[component]["minimal"]["gates"]) == expected_gate, f"bad minimum: {component}")

    required = {"NOT", "AND", "OR", "NAND", "NOR", "XOR", "XNOR", "AND3", "OR3", "FullAdder"}
    seeds = primitive["explicit_required_seeds"]
    require(required <= {row["component"] for row in seeds}, "explicit primitive coverage incomplete")
    for row in seeds:
        require(len(row["nodes"]) == int(row["gate"]), "seed gate count mismatch")
        require(len(row["truth_sha256s"]) == len(row["nodes"]), "seed truth count mismatch")
        require(all(digest in truth_ids for digest in row["truth_sha256s"]), "seed truth missing")
    native_components = {row["component"] for row in primitive["native_score_profile_producers"]}
    require(required | {"Switch"} <= native_components, "native score-profile coverage incomplete")

    fa_replay = replay_full_adder(primitive["full_adder_exact_minimum"])
    require(primitive["full_adder_exact_minimum"]["status"] == "sat", "FullAdder proof status")
    require(fa_replay["gate"] == 7 and fa_replay["delay"] == 4, "FullAdder witness metric mismatch")

    replay = payload["current_80d7"]["replay"]
    require(replay["rows"] == 131072, "80/7 row count mismatch")
    require(replay["gate"] == 80 and replay["delay"] == 7, "80/7 score mismatch")
    require(not replay["mismatch_union_count"], "80/7 output mismatch")
    require(not replay["conflict_assignment_count"], "80/7 conflict")
    require(not any(replay["z_assignment_count_by_output"]), "80/7 Z output")
    require(replay["node_count"] == 82 and replay["switch_driver_count"] == 10, "80/7 coverage mismatch")
    require(source_kinds["verified-80d7-node"] == 82, "80/7 node producer count mismatch")
    require(source_kinds["verified-80d7-switch-driver"] == 10, "80/7 driver producer count mismatch")

    current_producers = [
        producer
        for truth in payload["truth_classes"]
        for producer in truth["producers"]
        if producer["source_kind"] == "verified-80d7-switch-driver"
    ]
    require(len({row["physical_owner"] for row in current_producers}) == 10, "Switch owners are not distinct")
    require(
        all(row["metadata"].get("resolved_network_owner") for row in current_producers),
        "Switch resolved-network owner missing",
    )

    patterns = payload["current_80d7"]["embedded_expansion_hits"]
    require(len(patterns) == int(summary["embedded_expansion_hit_count"]), "pattern count mismatch")
    require(all(not row.get("mismatch_count", 0) for row in patterns), "embedded pattern mismatch")
    for row in patterns:
        if str(row["pattern"]).startswith("FullAdder-"):
            require(row["late_input_short_arcs"] == {"SUM": 2, "CARRY": 2}, "bad FullAdder short arc")
        if str(row["pattern"]).endswith("3-two-gate-tree"):
            require(row["short_arc_gate_depth"] == 1, "bad three-input short arc")
    direct_hits = payload["current_80d7"]["score_improving_direct_reuse_hits"]
    require(len(direct_hits) == int(summary["score_improving_direct_reuse_hit_count"]), "reuse count mismatch")
    require(not direct_hits, "unexpected direct score-improving reuse hit")

    return {
        "schema": "tc-primitive-expansion-physical-byproduct-catalog-audit-v1",
        "status": "pass",
        "catalog_path": str(path),
        "catalog_sha256": sha256(raw).hexdigest(),
        "dependency_sha256s": dependency_checks,
        "counts": {
            "domains": len(domains),
            "truth_classes": len(truth_ids),
            "producers": producer_count,
            "packed_masks": len(masks),
            "owner_sets": len(owner_sets),
            "current_nodes": source_kinds["verified-80d7-node"],
            "current_switch_drivers": source_kinds["verified-80d7-switch-driver"],
            "embedded_patterns": len(patterns),
            "direct_reuse_hits": len(direct_hits),
        },
        "source_kind_counts": dict(sorted(source_kinds.items())),
        "role_counts": dict(sorted(role_counts.items())),
        "full_adder_witness_replay": fa_replay,
        "current_80d7_replay": replay,
        "checks": {
            "all_packed_masks_and_sha256s_recomputed": True,
            "all_physical_and_boolean_truth_sha256s_recomputed": True,
            "all_owner_sets_and_truth_pareto_frontiers_recomputed": True,
            "all_required_primitive_families_present": True,
            "full_adder_7gate_witness_independently_replayed": True,
            "current_82_nodes_and_10_partial_drivers_accounted": True,
            "current_outputs_131072_rows_zero_mismatch_conflict_z": True,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = audit(args.input.resolve())
    encoded = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    args.output.write_bytes(encoded.encode("utf-8"))
    print(encoded, end="")
    print(f"audit_sha256={sha256(encoded.encode('utf-8')).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
