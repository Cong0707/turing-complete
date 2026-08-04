"""Audit the two complete sparse g17 D5 position classes.

The audited classes are deliberately disjoint from the concurrent g17/o5/s6
and g18/o2/s8 searches:

* g17/o1/s8/x0: nine components, one ordinary wildcard position (9 modes),
  with all five ordinary kinds retained by exact quotas (45 assignments).
* g17/o0/s7/x1: eight components, one fixed XOR position (8 modes), with no
  ordinary wildcard (8 assignments).

The audit is save-independent and solver-free.  It pins the authoritative
worker/dependencies and independently recomputes quotas, cost, the suffix
shard, position coverage, and concrete kind assignments.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import itertools
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PHYSICAL_EXACT = ROOT / ".research/byte_adder_phase_shortcut_restart/physical_exact.py"
DEFAULT_AUDIT = HERE / "s567c8_g17_sparse_position_universes_audit.json"
DEFAULT_MANIFEST = HERE / "s567c8_g17_sparse_position_universes_manifest.json"

ALL_KINDS = ("NOT", "AND", "OR", "NAND", "NOR", "XOR", "SWITCH")
ORDINARY_KINDS = ("NOT", "AND", "OR", "NAND", "NOR")
COST = {
    "NOT": 1,
    "AND": 1,
    "OR": 1,
    "NAND": 1,
    "NOR": 1,
    "XOR": 3,
    "SWITCH": 2,
}
OUTPUTS = ("S5", "S6", "S7", "C8")
MAX_DELAY = 5
SPLIT_SLOTS = 1
SHARD_COUNT = 1
SHARD_INDEX = 0

EXPECTED_PHYSICAL_SHA256 = (
    "c48a96e55d8c5076418999f5fa5ee95e9f8207c03f138cd4bccf48908a69c071"
)
DEPENDENCIES = {
    ROOT / ".research/byte_adder_ling_theory_agent/exact_free_ling_pair_sat.py": (
        "49bb2640e1cb08c6e2b9ac412a8cf56c058f27966e1dd799d1d813c8f1821017"
    ),
    ROOT / ".research/byte_adder_boolean_superopt_agent/exact_adder_block_sat.py": (
        "f320ed3029b949185acd13b5462b659502a970406d1bf5047713279e152f56de"
    ),
    ROOT / ".research/rng_468_joint_macro/joint_parity_cnf.py": (
        "a565201bf7e99f6ded6732e70d883cd9a90e5da2e42d72171f11952bb3566ca4"
    ),
}

CLASS_SPECS = (
    {
        "name": "g17_o1s8",
        "gate_bound": 17,
        "components": 9,
        "ordinary": 1,
        "switches": 8,
        "xors": 0,
        "expected_patterns": 9,
        "expected_concrete": 45,
    },
    {
        "name": "g17_x1s7",
        "gate_bound": 17,
        "components": 8,
        "ordinary": 0,
        "switches": 7,
        "xors": 1,
        "expected_patterns": 8,
        "expected_concrete": 8,
    },
)


def relative(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT)).replace("\\", "/")


def digest(path: Path) -> str | None:
    return sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def suffix_universe(spec: dict[str, int | str]) -> tuple[tuple[str, ...], ...]:
    width = min(int(spec["components"]), SPLIT_SLOTS)
    result: list[tuple[str, ...]] = []
    for signature in itertools.product(ALL_KINDS, repeat=width):
        switches = signature.count("SWITCH")
        xors = signature.count("XOR")
        ordinary = width - switches - xors
        if switches > int(spec["switches"]) or xors > int(spec["xors"]):
            continue
        if ordinary > int(spec["ordinary"]):
            continue
        result.append(signature)
    return tuple(result)


def quota_valid(
    assignment: tuple[str, ...], spec: dict[str, int | str]
) -> bool:
    return (
        len(assignment) == int(spec["components"])
        and assignment.count("SWITCH") == int(spec["switches"])
        and assignment.count("XOR") == int(spec["xors"])
        and sum(kind in ORDINARY_KINDS for kind in assignment)
        == int(spec["ordinary"])
        and sum(COST[kind] for kind in assignment) == int(spec["gate_bound"])
    )


def audit_o1s8(spec: dict[str, int | str]) -> dict[str, object]:
    components = int(spec["components"])
    universe = suffix_universe(spec)
    assigned = universe
    patterns: list[dict[str, object]] = []
    invalid: list[dict[str, object]] = []
    fixed_seen: set[tuple[str, ...]] = set()
    concrete_seen: set[tuple[str, ...]] = set()

    for ordinary_slot in range(components):
        fixed = ["SWITCH"] * components
        fixed[ordinary_slot] = "*"
        fixed_tuple = tuple(fixed)
        fixed_seen.add(fixed_tuple)
        allowed: list[str] = []
        rejected: list[str] = []
        for kind in ALL_KINDS:
            concrete = list(fixed)
            concrete[ordinary_slot] = kind
            concrete_tuple = tuple(concrete)
            valid = quota_valid(concrete_tuple, spec) and concrete_tuple[-1:] in assigned
            (allowed if valid else rejected).append(kind)
            if valid:
                concrete_seen.add(concrete_tuple)
        checks = {
            "fixed_switch_count": fixed.count("SWITCH") == 8,
            "wildcard_count": fixed.count("*") == 1,
            "wildcard_allowed_exactly_five_ordinary": tuple(allowed)
            == ORDINARY_KINDS,
            "shard_keeps_all_concrete_assignments": all(
                tuple(fixed[:ordinary_slot] + [kind] + fixed[ordinary_slot + 1:])[-1:]
                in assigned
                for kind in ORDINARY_KINDS
            ),
        }
        if not all(checks.values()):
            invalid.append({"ordinary_slot": ordinary_slot, "checks": checks})
        patterns.append(
            {
                "priority": ordinary_slot,
                "key": f"o{ordinary_slot}",
                "xor_slot": None,
                "ordinary_slot": ordinary_slot,
                "fixed_kinds": fixed,
                "fixed_kinds_csv": ",".join(fixed),
                "allowed_ordinary_kinds": allowed,
                "rejected_nonordinary_kinds": rejected,
                "concrete_assignment_count": len(allowed),
                "checks": checks,
            }
        )

    return {
        "patterns": patterns,
        "invalid": invalid,
        "unique_fixed_pattern_count": len(fixed_seen),
        "concrete_assignment_count": len(concrete_seen),
        "suffix_universe": universe,
        "assigned_suffix_signatures": assigned,
    }


def audit_x1s7(spec: dict[str, int | str]) -> dict[str, object]:
    components = int(spec["components"])
    universe = suffix_universe(spec)
    assigned = universe
    patterns: list[dict[str, object]] = []
    invalid: list[dict[str, object]] = []
    concrete_seen: set[tuple[str, ...]] = set()

    for xor_slot in range(components):
        fixed = ["SWITCH"] * components
        fixed[xor_slot] = "XOR"
        concrete = tuple(fixed)
        concrete_seen.add(concrete)
        checks = {
            "component_count": len(concrete) == 8,
            "fixed_switch_count": concrete.count("SWITCH") == 7,
            "fixed_xor_count": concrete.count("XOR") == 1,
            "wildcard_count": concrete.count("*") == 0,
            "quota_and_cost": quota_valid(concrete, spec),
            "suffix_shard_keeps_assignment": concrete[-1:] in assigned,
        }
        if not all(checks.values()):
            invalid.append({"xor_slot": xor_slot, "checks": checks})
        patterns.append(
            {
                "priority": xor_slot,
                "key": f"x{xor_slot}",
                "xor_slot": xor_slot,
                "ordinary_slot": None,
                "fixed_kinds": fixed,
                "fixed_kinds_csv": ",".join(fixed),
                "allowed_ordinary_kinds": [],
                "concrete_assignment_count": 1,
                "checks": checks,
            }
        )

    return {
        "patterns": patterns,
        "invalid": invalid,
        "unique_fixed_pattern_count": len(concrete_seen),
        "concrete_assignment_count": len(concrete_seen),
        "suffix_universe": universe,
        "assigned_suffix_signatures": assigned,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", type=Path, default=DEFAULT_AUDIT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args()

    physical_sha = digest(PHYSICAL_EXACT)
    dependency_actual = {relative(path): digest(path) for path in DEPENDENCIES}
    dependency_expected = {
        relative(path): expected for path, expected in DEPENDENCIES.items()
    }

    class_results: list[dict[str, object]] = []
    global_invalid: list[dict[str, object]] = []
    for spec in CLASS_SPECS:
        result = audit_o1s8(spec) if spec["name"] == "g17_o1s8" else audit_x1s7(spec)
        universe = result.pop("suffix_universe")
        assigned = result.pop("assigned_suffix_signatures")
        encoded_universe = json.dumps(
            [list(signature) for signature in universe],
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
        checks = {
            "gate_accounting": (
                int(spec["components"])
                + int(spec["switches"])
                + 2 * int(spec["xors"])
                == int(spec["gate_bound"])
            ),
            "ordinary_accounting": (
                int(spec["components"])
                - int(spec["switches"])
                - int(spec["xors"])
                == int(spec["ordinary"])
            ),
            "pattern_count": len(result["patterns"])
            == int(spec["expected_patterns"]),
            "unique_fixed_pattern_count": result["unique_fixed_pattern_count"]
            == int(spec["expected_patterns"]),
            "concrete_assignment_count": result["concrete_assignment_count"]
            == int(spec["expected_concrete"]),
            "single_shard_assigns_full_suffix_universe": assigned == universe,
            "all_pattern_checks": not result["invalid"],
        }
        if not all(checks.values()):
            global_invalid.append({"class": spec["name"], "checks": checks})
        class_results.append(
            {
                "name": spec["name"],
                "scope": {
                    "domain": "s34567c8_leaf",
                    "rows": 486,
                    "outputs": list(OUTPUTS),
                    "gate_bound": spec["gate_bound"],
                    "max_delay": MAX_DELAY,
                    "components": spec["components"],
                    "ordinary": spec["ordinary"],
                    "switches": spec["switches"],
                    "xors": spec["xors"],
                    "position_patterns": spec["expected_patterns"],
                    "concrete_kind_assignments": spec["expected_concrete"],
                },
                "shard": {
                    "split_slots": SPLIT_SLOTS,
                    "shard_count": SHARD_COUNT,
                    "shard_index": SHARD_INDEX,
                    "suffix_universe": [list(signature) for signature in universe],
                    "suffix_universe_count": len(universe),
                    "suffix_universe_sha256": sha256(encoded_universe).hexdigest(),
                    "assigned_suffix_signatures": [
                        list(signature) for signature in assigned
                    ],
                },
                "patterns": result["patterns"],
                "unique_fixed_pattern_count": result["unique_fixed_pattern_count"],
                "concrete_assignment_count": result["concrete_assignment_count"],
                "invalid": result["invalid"],
                "checks": checks,
            }
        )

    global_checks = {
        "physical_exact_sha256": physical_sha == EXPECTED_PHYSICAL_SHA256,
        "dependency_sha256": dependency_actual == dependency_expected,
        "class_count": len(class_results) == 2,
        "g17_o1s8_complete": (
            class_results[0]["unique_fixed_pattern_count"] == 9
            and class_results[0]["concrete_assignment_count"] == 45
        ),
        "g17_x1s7_complete": (
            class_results[1]["unique_fixed_pattern_count"] == 8
            and class_results[1]["concrete_assignment_count"] == 8
        ),
        "classes_are_disjoint": (
            (
                class_results[0]["scope"]["components"],
                class_results[0]["scope"]["ordinary"],
                class_results[0]["scope"]["switches"],
                class_results[0]["scope"]["xors"],
            )
            != (
                class_results[1]["scope"]["components"],
                class_results[1]["scope"]["ordinary"],
                class_results[1]["scope"]["switches"],
                class_results[1]["scope"]["xors"],
            )
        ),
        "disjoint_from_concurrent_g17_o5s6": all(
            (
                row["scope"]["components"],
                row["scope"]["ordinary"],
                row["scope"]["switches"],
                row["scope"]["xors"],
            )
            != (11, 5, 6, 0)
            for row in class_results
        ),
        "disjoint_from_concurrent_g18_o2s8": all(
            (
                row["scope"]["components"],
                row["scope"]["ordinary"],
                row["scope"]["switches"],
                row["scope"]["xors"],
            )
            != (10, 2, 8, 0)
            for row in class_results
        ),
        "no_invalid_classes": not global_invalid,
    }
    complete = all(global_checks.values())

    manifest = {
        "schema": "s567c8-g17-sparse-position-universes-manifest-v1",
        "status": "complete" if complete else "incomplete",
        "worker": {
            "path": relative(PHYSICAL_EXACT),
            "sha256": physical_sha,
            "expected_sha256": EXPECTED_PHYSICAL_SHA256,
            "dependency_sha256": dependency_actual,
        },
        "classes": class_results,
        "global_checks": global_checks,
        "invalid": global_invalid,
        "scope_exclusions": [
            "ordinary/Switch/XOR decompositions outside the two named classes",
            "gate cost other than exact 17",
            "delay other than D5",
            "a complete lower bound across every cost-17 topology",
        ],
    }
    manifest_encoded = (
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    ).encode()
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_bytes(manifest_encoded)

    audit = {
        "schema": "s567c8-g17-sparse-position-universes-audit-v1",
        "status": "complete" if complete else "incomplete",
        "manifest": relative(args.manifest),
        "manifest_sha256": sha256(manifest_encoded).hexdigest(),
        "auditor": relative(Path(__file__)),
        "auditor_sha256": digest(Path(__file__)),
        "physical_exact_sha256": physical_sha,
        "dependency_sha256": dependency_actual,
        "class_summaries": [
            {
                "name": row["name"],
                "position_patterns": len(row["patterns"]),
                "concrete_kind_assignments": row["concrete_assignment_count"],
                "invalid_count": len(row["invalid"]),
                "suffix_universe_sha256": row["shard"]["suffix_universe_sha256"],
            }
            for row in class_results
        ],
        "global_checks": global_checks,
        "invalid_count": len(global_invalid),
    }
    audit_encoded = (json.dumps(audit, ensure_ascii=False, indent=2) + "\n").encode()
    args.audit.parent.mkdir(parents=True, exist_ok=True)
    args.audit.write_bytes(audit_encoded)

    print(
        json.dumps(
            {
                "status": audit["status"],
                "class_summaries": audit["class_summaries"],
                "invalid_count": len(global_invalid),
                "manifest_sha256": sha256(manifest_encoded).hexdigest(),
                "audit_sha256": sha256(audit_encoded).hexdigest(),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if complete else 1


if __name__ == "__main__":
    raise SystemExit(main())
