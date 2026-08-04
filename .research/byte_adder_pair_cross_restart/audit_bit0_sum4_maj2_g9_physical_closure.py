"""Independently audit the 45-shard bit-0 asymmetric connected-cut closure."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
CASES = HERE / "bit0_sum4_maj2_g9_physical_closure"
MANIFEST = CASES / "manifest.json"
OUTPUT = CASES / "independent_audit.json"
SOLVER = HERE / "exact_truth_tuple_physical.py"
BASE_SOLVER = (
    HERE.parent
    / "byte_adder_component_byproduct_catalog"
    / "exact_pretarget_physical.py"
)
DRIVER = HERE / "run_bit0_sum4_maj2_g9_physical_closure.py"


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    require(manifest["status"] == "proved_unsat", "closure manifest is not proved_unsat")
    require(manifest["target"]["truth_masks_hex"] == ["96", "e8"], "target masks drift")
    require(manifest["target"]["output_max_delays"] == [4, 2], "arrival bounds drift")
    require(manifest["target"]["strict_fully_driven"] is True, "output policy drift")
    require(manifest["target"]["physical_nets"] is True, "physical nets disabled")
    require("not a global lower bound" in manifest["scope_boundary"], "scope boundary missing")

    rows = manifest["cases"]
    expected = {(paid, normalizers) for paid in range(1, 10) for normalizers in range(5)}
    actual = {
        (int(row["paid_components"]), int(row["normalizers"]))
        for row in rows
    }
    require(len(rows) == 45 and len(actual) == 45, "closure rows are missing or duplicated")
    require(actual == expected, "closure Cartesian product is incomplete")

    reviewed = []
    for row in rows:
        paid = int(row["paid_components"])
        normalizers = int(row["normalizers"])
        path = CASES / str(row["artifact"])
        require(path.is_file(), f"case artifact missing: {path}")
        require(digest(path) == row["artifact_sha256"], f"case artifact hash drift: {path.name}")
        case = json.loads(path.read_text(encoding="utf-8"))
        expected_fields = {
            "schema": "tc-arbitrary-truth-tuple-exact-physical-v1",
            "status": "unsat",
            "target": "truth-tuple",
            "input_count": 3,
            "input_ports": ["Input 0", "Input 1", "Input 2"],
            "output_ports": ["Sum", "Carry"],
            "target_truth_tables_hex": ["96", "e8"],
            "output_max_delays": [4, 2],
            "gate_bound": 9,
            "max_delay": 4,
            "components": paid + normalizers,
            "exact_normalizers": normalizers,
            "allow_z_false": False,
            "physical_nets": True,
        }
        for key, value in expected_fields.items():
            require(case.get(key) == value, f"{path.name}: {key} drift")
        require(case["case_sha256"] == row["case_sha256"], f"{path.name}: case SHA drift")
        require(case.get("reason_unknown") is None, f"{path.name}: unknown reason present")
        semantics = case["semantics"]
        require(
            semantics["normalizer_complete_normal_form"]
            == "normalizer inputs contain only Switch output pins",
            f"{path.name}: normalizer form drift",
        )
        require(
            semantics["physical_driver_sets_form_wire_net_partitions"] is True,
            f"{path.name}: abstract bus slipped in",
        )
        require(
            semantics["multi_driver_conflict_forbidden"] is True,
            f"{path.name}: conflicts allowed",
        )
        require(
            semantics["primary_output_policy"] == "fully driven on every row",
            f"{path.name}: output policy drift",
        )
        reviewed.append(
            {
                "artifact": path.name,
                "sha256": digest(path),
                "paid_components": paid,
                "normalizers": normalizers,
                "total_components": paid + normalizers,
                "variables": case["variables"],
                "clauses": case["clauses"],
                "solve_seconds": case["solve_seconds"],
                "status": "unsat",
            }
        )

    require(manifest["enumeration"]["status_counts"] == {"unsat": 45}, "status counts drift")
    output = {
        "schema": "bit0-sum4-maj2-g9-exact-physical-cut-independent-audit-v1",
        "status": "verified_unsat",
        "claim": (
            "Every enumerated strict physical shard for SUM=0x96 at arrival<=4 "
            "and MAJ=0xe8 at arrival<=2 with gate<=9 is UNSAT."
        ),
        "scope_boundary": manifest["scope_boundary"],
        "coverage": {
            "shards": 45,
            "paid_components": [1, 9],
            "normalizers": [0, 4],
            "unknown_count": 0,
            "sat_count": 0,
            "unsat_count": 45,
            "full_cartesian_product_recomputed": True,
            "strict_fully_driven": True,
            "physical_wire_net_partitions": True,
        },
        "target": {
            "truth_masks_hex": ["96", "e8"],
            "output_max_delays": [4, 2],
            "gate_bound": 9,
        },
        "normalizer_completeness": {
            "bound": 4,
            "derivation": "floor(gate_bound / Switch_cost) = floor(9/2) = 4",
            "useful_normalizer_requires_distinct_physical_switch_output_net": True,
        },
        "dependencies": {
            "manifest": {"path": str(MANIFEST), "sha256": digest(MANIFEST)},
            "solver": {"path": str(SOLVER), "sha256": digest(SOLVER)},
            "base_solver": {"path": str(BASE_SOLVER), "sha256": digest(BASE_SOLVER)},
            "driver": {"path": str(DRIVER), "sha256": digest(DRIVER)},
        },
        "cases": reviewed,
        "auditor": {
            "path": str(Path(__file__).resolve()),
            "sha256": digest(Path(__file__).resolve()),
        },
    }
    encoded = (json.dumps(output, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    OUTPUT.write_bytes(encoded)
    print(
        json.dumps(
            {
                "status": output["status"],
                "output": str(OUTPUT),
                "output_sha256": sha256(encoded).hexdigest(),
                "coverage": output["coverage"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
