"""Independently audit the 90-shard FullAdder gate<=9, delay<=3 closure."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
CASES = HERE / "fa_g9_d3_physical_closure"
MANIFEST = CASES / "manifest.json"
OUTPUT = CASES / "independent_audit.json"
SOLVER = HERE / "exact_pretarget_physical.py"
DRIVER = HERE / "run_fa_g9_d3_physical_closure.py"


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    require(manifest["status"] == "proved_unsat", "closure manifest is not proved_unsat")
    rows = manifest["cases"]
    expected = {
        (policy, paid, normalizers)
        for policy in ("strict", "zfalse")
        for paid in range(1, 10)
        for normalizers in range(5)
    }
    actual = {
        (str(row["policy"]), int(row["paid_components"]), int(row["normalizers"]))
        for row in rows
    }
    require(len(rows) == 90 and len(actual) == 90, "closure rows are missing or duplicated")
    require(actual == expected, "closure Cartesian product is incomplete")

    reviewed = []
    for row in rows:
        policy = str(row["policy"])
        paid = int(row["paid_components"])
        normalizers = int(row["normalizers"])
        path = CASES / str(row["artifact"])
        require(path.is_file(), f"case artifact missing: {path}")
        require(digest(path) == row["artifact_sha256"], f"case artifact hash drift: {path.name}")
        case = json.loads(path.read_text(encoding="utf-8"))
        expected_fields = {
            "schema": "tc-pretarget-exact-physical-v1",
            "status": "unsat",
            "target": "full-adder",
            "gate_bound": 9,
            "max_delay": 3,
            "components": paid + normalizers,
            "exact_normalizers": normalizers,
            "allow_z_false": policy == "zfalse",
            "physical_nets": True,
        }
        for key, value in expected_fields.items():
            require(case.get(key) == value, f"{path.name}: {key} drift")
        require(case["case_sha256"] == row["case_sha256"], f"{path.name}: case SHA drift")
        require(case.get("reason_unknown") is None, f"{path.name}: unknown reason present")
        semantics = case["semantics"]
        require(semantics["normalizer_complete_normal_form"] == "normalizer inputs contain only Switch output pins", f"{path.name}: normalizer form drift")
        require(semantics["physical_driver_sets_form_wire_net_partitions"] is True, f"{path.name}: abstract bus slipped in")
        require(semantics["multi_driver_conflict_forbidden"] is True, f"{path.name}: conflicts allowed")
        reviewed.append(
            {
                "artifact": path.name,
                "sha256": digest(path),
                "policy": policy,
                "paid_components": paid,
                "normalizers": normalizers,
                "total_components": paid + normalizers,
                "variables": case["variables"],
                "clauses": case["clauses"],
                "solve_seconds": case["solve_seconds"],
                "status": "unsat",
            }
        )

    strict = sum(row["policy"] == "strict" for row in reviewed)
    zfalse = sum(row["policy"] == "zfalse" for row in reviewed)
    require((strict, zfalse) == (45, 45), "policy counts differ from 45/45")
    output = {
        "schema": "full-adder-g9-d3-exact-physical-closure-independent-audit-v1",
        "status": "verified_unsat",
        "claim": "Every enumerated FullAdder gate<=9, delay<=3 physical shard is UNSAT.",
        "coverage": {
            "shards": 90,
            "strict_shards": strict,
            "target_zero_may_be_z_shards": zfalse,
            "paid_components": [1, 9],
            "normalizers": [0, 4],
            "unknown_count": 0,
            "sat_count": 0,
            "unsat_count": 90,
            "full_cartesian_product_recomputed": True,
        },
        "normalizer_completeness": {
            "bound": 4,
            "derivation": "floor(gate_bound / Switch_cost) = floor(9/2) = 4",
            "useful_normalizer_requires_distinct_physical_switch_output_net": True,
        },
        "dependencies": {
            "manifest": {"path": str(MANIFEST), "sha256": digest(MANIFEST)},
            "solver": {"path": str(SOLVER), "sha256": digest(SOLVER)},
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
    print(json.dumps({
        "status": output["status"],
        "output": str(OUTPUT),
        "output_sha256": sha256(encoded).hexdigest(),
        "coverage": output["coverage"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
