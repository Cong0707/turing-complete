"""Static completeness and non-duplication preflight for the fixed g16 job."""

from __future__ import annotations

import argparse
from hashlib import sha256
import itertools
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RESEARCH = ROOT / ".research"
WORKER = HERE / "physical_exact.py"
GENERATOR = HERE / "make_s567c8_g16_o4_s6_all_switch_tail.py"
AUDITOR = HERE / "audit_s567c8_g16_o4_s6_all_switch_tail.py"
POSITIVE_SCRIPT = (
    HERE / "verify_s567c8_g16_o4_s6_all_switch_tail_positive_regression.py"
)
POSITIVE_RESULT = HERE / "s567c8_g16_o4_s6_all_switch_tail_positive_s7c8.json"
FIXED_KINDS = ("NOT", "NOR", "OR", "OR", *("SWITCH" for _ in range(6)))
EXPECTED_NAME = "s567c8-d5-g16-o04-s06-all-switch-tail"
ORDINARY_KINDS = ("NOT", "AND", "OR", "NAND", "NOR")


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def constraint_digest(fixed: tuple[str, ...]) -> str:
    return sha256(
        json.dumps(fixed, ensure_ascii=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def expand_topology(
    topology: list[object], alphabet: tuple[str, ...] = ORDINARY_KINDS
) -> set[tuple[str, ...]]:
    stars = [index for index, kind in enumerate(topology) if kind == "*"]
    if not stars:
        return {tuple(str(kind) for kind in topology)}
    expanded: set[tuple[str, ...]] = set()
    for choices in itertools.product(alphabet, repeat=len(stars)):
        item = [str(kind) for kind in topology]
        for index, choice in zip(stars, choices, strict=True):
            item[index] = choice
        expanded.add(tuple(item))
    return expanded


def extract_fixed_families(path: Path) -> set[tuple[str, ...]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return set()
    if not isinstance(payload, dict):
        return set()
    families: set[tuple[str, ...]] = set()
    for value in payload.get("values", ()):
        if not isinstance(value, dict) or not value.get("fixed_kinds"):
            continue
        fixed = value["fixed_kinds"]
        if isinstance(fixed, str):
            families.add(tuple(fixed.split(",")))
        elif isinstance(fixed, list):
            families.add(tuple(str(kind) for kind in fixed))
    fixed = payload.get("fixed_kinds")
    if isinstance(fixed, str):
        families.add(tuple(fixed.split(",")))
    elif isinstance(fixed, list):
        families.add(tuple(str(kind) for kind in fixed))
    topology = payload.get("topology")
    if isinstance(topology, list):
        alphabet = tuple(payload.get("ordinary_kind_alphabet", ORDINARY_KINDS))
        families.update(expand_topology(topology, alphabet))
    return families


def audit(spec_path: Path) -> dict[str, object]:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    proof = spec.get("proof_scope", {})
    errors: list[str] = []
    values = list(spec.get("values", ()))
    value = values[0] if len(values) == 1 else {}
    fixed = tuple(str(value.get("fixed_kinds", "")).split(","))
    output = str(value.get("output", ""))
    actual_constraint = constraint_digest(fixed)
    structural = (
        len(values) == 1
        and fixed == FIXED_KINDS
        and value.get("name") == EXPECTED_NAME
        and output.endswith(f"/{EXPECTED_NAME}.json")
        and value.get("constraint_sha256") == actual_constraint
        and value.get("domain") == "s34567c8_leaf"
        and value.get("outputs") == "S5,S6,S7,C8"
        and value.get("gate") == 16
        and value.get("delay") == 5
        and value.get("components") == 10
        and value.get("ordinary") == 4
        and value.get("switches") == 6
        and value.get("xors") == 0
        and value.get("split_slots") == 1
        and value.get("shard_count") == 1
        and value.get("shard_index") == 0
        and value.get("solver") == "cadical195"
    )
    constraint_records = [{"name": str(value.get("name")), "sha256": actual_constraint}]
    constraint_set_actual = sha256(
        json.dumps(
            constraint_records,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii")
    ).hexdigest()

    dependencies = {
        relative: ROOT / relative for relative in proof.get("dependency_sha256", {})
    }
    dependency_matches = {
        relative: path.is_file() and digest(path) == proof["dependency_sha256"][relative]
        for relative, path in dependencies.items()
    }
    auditor_info = proof.get("auditor", {})
    artifact_info = proof.get("positive_regression", {})
    positive = json.loads(POSITIVE_RESULT.read_text(encoding="utf-8"))
    positive_verification = positive.get("verification", {})
    positive_fixed = tuple(positive.get("regression", {}).get("fixed_kinds", ()))
    positive_ok = (
        artifact_info.get("script_sha256") == digest(POSITIVE_SCRIPT)
        and artifact_info.get("artifact_sha256") == digest(POSITIVE_RESULT)
        and positive.get("status") == "verified-positive-regression"
        and positive_verification.get("verified") is True
        and positive_verification.get("rows") == 486
        and positive_verification.get("actual_gate") == 16
        and positive_verification.get("actual_max_delay") == 5
        and positive_fixed == FIXED_KINDS
        and all(
            item == 0
            for key, item in positive_verification.items()
            if key.endswith("count")
        )
    )

    upstream_path = dependencies.get(
        ".research/byte_adder_ling_theory_agent/exact_free_ling_pair_sat.py"
    )
    joint_path = dependencies.get(".research/rng_468_joint_macro/joint_parity_cnf.py")
    exact_path = dependencies.get(
        ".research/byte_adder_boolean_superopt_agent/exact_adder_block_sat.py"
    )
    upstream_source = upstream_path.read_text(encoding="utf-8") if upstream_path else ""
    joint_source = joint_path.read_text(encoding="utf-8") if joint_path else ""
    exact_source = exact_path.read_text(encoding="utf-8") if exact_path else ""
    worker_source = WORKER.read_text(encoding="utf-8")
    normalized_exact_source = " ".join(exact_source.split())
    source_contracts = {
        "slot_inputs_only_see_sources_and_prior_slots": (
            "available = source_count + slot" in upstream_source
        ),
        "left_bus_multi_driver_restricted_to_switches": (
            "G._restrict_active_bus_to_switches(enc, left, source_count, kinds)"
            in upstream_source
        ),
        "right_bus_multi_driver_restricted_to_switches": (
            "G._restrict_active_bus_to_switches(enc, right, source_count, kinds)"
            in upstream_source
        ),
        "multi_driver_bus_switch_only_contract": (
            "any useful bus with two or more drivers consists only of Switch outputs"
            in joint_source
        ),
        "identical_driver_set_fanout_allowed": (
            "identical driver sets are allowed" in normalized_exact_source
        ),
        "partial_driver_overlap_forbidden": (
            "Two different physical nets cannot partially share a"
            in normalized_exact_source
        ),
        "exact_gate_cost_identity_enforced": (
            "expected_gate = args.components + args.switches + 2 * args.xors"
            in worker_source
        ),
    }

    prior_paths = sorted(
        path
        for path in RESEARCH.glob("*/*s567c8*.json")
        if path.resolve() != spec_path.resolve()
    )
    prior_families: set[tuple[str, ...]] = set()
    prior_records: list[dict[str, object]] = []
    for path in prior_paths:
        families = extract_fixed_families(path)
        overlap = {FIXED_KINDS} & families
        if families:
            prior_families.update(families)
            prior_records.append(
                {
                    "path": str(path.relative_to(ROOT)).replace("\\", "/"),
                    "family_count": len(families),
                    "overlap_count": len(overlap),
                }
            )
    han_records = [
        item
        for item in prior_records
        if "byte_adder_han_knowles_fused_agent/" in item["path"]
    ]
    non_duplication = {
        "all_scanned_prior_family_overlap_count": len({FIXED_KINDS} & prior_families),
        "scanned_json_files": len(prior_paths),
        "scanned_family_files": len(prior_records),
        "han_family_files": len(han_records),
        "han_overlap_count": sum(int(item["overlap_count"]) for item in han_records),
        "records": prior_records,
        "structural_reason": (
            "This fixed family is g16/o4/s6 with 10 components. Han/root "
            "position sweeps are g17/o5s6 or g18/o2s8; the closed phase "
            "families are g17 or g18 and therefore have different fixed tuples."
        ),
    }

    checks = {
        "schema": spec.get("schema") == "tc-byte-adder-remote-sweep-v1",
        "script": spec.get("script") == "physical_exact.py",
        "working_directory": spec.get("working_directory") == "../..",
        "single_job": len(values) == 1,
        "value_structurally_valid": structural,
        "constraint_set_matches": (
            constraint_set_actual == proof.get("constraint_set_sha256")
        ),
        "proof_topology_matches": proof.get("fixed_topology") == list(FIXED_KINDS),
        "worker_sha_matches": proof.get("worker_sha256") == digest(WORKER),
        "dependency_sha_matches": all(dependency_matches.values()),
        "auditor_sha_matches": (
            auditor_info.get("sha256") == digest(AUDITOR)
            and ROOT / auditor_info.get("path", "") == AUDITOR
        ),
        "positive_regression_verified": positive_ok,
        "source_bus_contracts_verified": all(source_contracts.values()),
        "all_scanned_prior_families_disjoint": len({FIXED_KINDS} & prior_families)
        == 0,
        "han_families_disjoint": non_duplication["han_overlap_count"] == 0,
        "workers_one": spec.get("workers") == 1,
        "memory_budget_1536_mib": spec.get("memory_mb_per_process") == 1536,
        "outer_timeout_900_seconds": spec.get("timeout_seconds") == 900.0,
        "stop_on_first_sat": spec.get("stop_on_first_sat") is True,
        "unknown_is_not_unsat": proof.get("unknown_is_not_unsat") is True,
    }
    errors.extend(key for key, passed in checks.items() if not passed)
    command = (
        "cd /root/congProjects/turing-complete-works && "
        ".venv/bin/python .research/byte_adder_remote_compute/remote_sweep.py "
        ".research/byte_adder_phase_shortcut_restart/"
        f"{spec_path.name}"
    )
    audit_command = (
        ".venv/bin/python "
        ".research/byte_adder_phase_shortcut_restart/"
        "audit_s567c8_g16_o4_s6_all_switch_tail.py "
        ".research/byte_adder_phase_shortcut_restart/"
        f"{spec_path.name} --output "
        ".research/byte_adder_phase_shortcut_restart/"
        f"{spec_path.stem}_audit.json"
    )
    return {
        "schema": "s567c8-g16-o4-s6-all-switch-tail-preflight-v1",
        "status": "ready-for-ubuntu-fixed-job" if not errors else "blocked",
        "spec": str(spec_path),
        "spec_sha256": digest(spec_path),
        "constraint_set_sha256": constraint_set_actual,
        "checks": checks,
        "errors": errors,
        "source_bus_contracts": source_contracts,
        "dependency_sha_matches": dependency_matches,
        "positive_regression": {
            "artifact": str(POSITIVE_RESULT),
            "artifact_sha256": digest(POSITIVE_RESULT),
            "status": positive.get("status"),
            "verification": positive_verification,
            "scope": "S7/C8 only; not a four-output SAT witness",
        },
        "non_duplication": non_duplication,
        "resource_budget": {
            "workers": 1,
            "memory_mb_per_process": 1536,
            "maximum_concurrent_address_space_mib": 1536,
            "outer_hard_timeout_seconds": 900,
            "jobs": 1,
            "worst_case_solver_wall_seconds": 900,
        },
        "strict_proof_scope": {
            "topology": list(FIXED_KINDS),
            "domain": "s34567c8_leaf",
            "rows": 486,
            "outputs": ["S5", "S6", "S7", "C8"],
            "gate": 16,
            "delay": 5,
            "components": 10,
            "ordinary": 4,
            "switches": 6,
            "xors": 0,
            "sat_rule": (
                "The single auditor-valid SAT payload plus matching finished "
                "runner summary is decisive."
            ),
            "unsat_rule": (
                "UNSAT only if the payload is terminal UNSAT and the finished "
                "runner summary has no timeout/error/missing result."
            ),
            "unknown_rule": (
                "Timeout, missing/invalid JSON, null/nonterminal status, worker "
                "or dependency drift, or summary mismatch remains UNKNOWN/incomplete."
            ),
            "exclusions": proof.get("scope_exclusions"),
        },
        "commands": {
            "ubuntu_launch_foreground": command,
            "terminal_audit": audit_command,
        },
        "artifact_sha256": {
            "worker": digest(WORKER),
            "generator": digest(GENERATOR),
            "auditor": digest(AUDITOR),
            "positive_script": digest(POSITIVE_SCRIPT),
            "positive_result": digest(POSITIVE_RESULT),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("spec", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = audit(args.spec.resolve())
    encoded = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0 if payload["status"] == "ready-for-ubuntu-fixed-job" else 1


if __name__ == "__main__":
    raise SystemExit(main())
