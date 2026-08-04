"""Static completeness, positive-control, and non-duplication preflight."""

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
GENERATOR = HERE / "make_s567c8_g17_o5_s6_midbus3_one_slot.py"
AUDITOR = HERE / "audit_s567c8_g17_o5_s6_midbus3_one_slot.py"
POSITIVE_SCRIPT = HERE / "verify_s567c8_g17_o5_s6_midbus3_positive_regression.py"
POSITIVE_RESULT = HERE / "s567c8_g17_o5_s6_midbus3_positive_s7c8.json"
ORDINARY_KINDS = ("NOT", "AND", "OR", "NAND", "NOR")
EXPECTED_KINDS = set(ORDINARY_KINDS)
KIND_PRIORITY = ("OR",) + tuple(kind for kind in ORDINARY_KINDS if kind != "OR")
FIXED_PREFIX = ("NOT", "NOR", "OR", "OR", "SWITCH", "SWITCH", "SWITCH")
FIXED_SUFFIX = ("SWITCH",) * 3
JOB_COUNT = 5


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
    expected_topology = (*FIXED_PREFIX, "ordinary-kind-slot", *FIXED_SUFFIX)
    kinds: set[str] = set()
    fixed_set: set[tuple[str, ...]] = set()
    names: set[str] = set()
    outputs: set[str] = set()
    constraint_records: list[dict[str, str]] = []
    value_errors: list[str] = []
    for index, value in enumerate(spec.get("values", ())):
        fixed = tuple(str(value.get("fixed_kinds", "")).split(","))
        kind = fixed[7] if len(fixed) == 11 else ""
        name = str(value.get("name"))
        output = str(value.get("output"))
        expected_name = (
            f"s567c8-d5-g17-o05-s06-midbus3-{kind.lower()}"
            if kind in EXPECTED_KINDS
            else ""
        )
        actual_constraint = constraint_digest(fixed)
        valid = (
            len(fixed) == 11
            and fixed[:7] == FIXED_PREFIX
            and kind in EXPECTED_KINDS
            and fixed[8:] == FIXED_SUFFIX
            and fixed.count("SWITCH") == 6
            and not any(item in {"XOR", "*"} for item in fixed)
            and name == expected_name
            and output.endswith(f"/{expected_name}.json")
            and value.get("constraint_sha256") == actual_constraint
            and value.get("domain") == "s34567c8_leaf"
            and value.get("outputs") == "S5,S6,S7,C8"
            and value.get("gate") == 17
            and value.get("delay") == 5
            and value.get("components") == 11
            and value.get("ordinary") == 5
            and value.get("switches") == 6
            and value.get("xors") == 0
            and value.get("split_slots") == 1
            and value.get("shard_count") == 1
            and value.get("shard_index") == 0
            and value.get("solver") == "cadical195"
        )
        if not valid:
            value_errors.append(f"invalid value index {index}: {name}")
        if kind:
            kinds.add(kind)
        fixed_set.add(fixed)
        names.add(name)
        outputs.add(output)
        constraint_records.append({"name": name, "sha256": actual_constraint})
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
        and positive_verification.get("actual_gate") == 17
        and positive_verification.get("actual_max_delay") == 5
        and positive_fixed == (*FIXED_PREFIX, "OR", *FIXED_SUFFIX)
        and all(
            value == 0
            for key, value in positive_verification.items()
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
        "slot7_can_read_switch_slots4_5_6": all(slot < 7 for slot in (4, 5, 6)),
        "slots8_9_10_can_read_slot7": all(7 < slot for slot in (8, 9, 10)),
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
        overlap = fixed_set & families
        if families:
            prior_families.update(families)
            prior_records.append(
                {
                    "path": str(path.relative_to(ROOT)).replace("\\", "/"),
                    "family_count": len(families),
                    "overlap_count": len(overlap),
                }
            )
    han_paths = [
        item
        for item in prior_records
        if "byte_adder_han_knowles_fused_agent/" in item["path"]
    ]
    non_duplication = {
        "all_scanned_prior_family_overlap_count": len(fixed_set & prior_families),
        "scanned_json_files": len(prior_paths),
        "scanned_family_files": len(prior_records),
        "han_family_files": len(han_paths),
        "han_overlap_count": sum(int(item["overlap_count"]) for item in han_paths),
        "records": prior_records,
        "structural_reason": (
            "This family has 11 components and o5/s6 with ordinary slot 7. "
            "The closed mid-BUS and terminal families have 12 components and "
            "o6/s6; Han/root position families use 10 components and o2/s8."
        ),
    }

    checks = {
        "schema": spec.get("schema") == "tc-byte-adder-remote-sweep-v1",
        "script": spec.get("script") == "physical_exact.py",
        "working_directory": spec.get("working_directory") == "../..",
        "jobs_5": len(spec.get("values", ())) == JOB_COUNT,
        "ordinary_kinds_complete": kinds == EXPECTED_KINDS,
        "fixed_constraints_unique": len(fixed_set) == JOB_COUNT,
        "names_unique": len(names) == JOB_COUNT,
        "outputs_unique": len(outputs) == JOB_COUNT,
        "values_structurally_valid": not value_errors,
        "constraint_set_matches": (
            constraint_set_actual == proof.get("constraint_set_sha256")
        ),
        "proof_topology_matches": tuple(proof.get("fixed_topology", ()))
        == expected_topology,
        "proof_kind_count": proof.get("ordered_kind_count") == JOB_COUNT,
        "proof_kind_order": proof.get("kind_execution_order") == list(KIND_PRIORITY),
        "worker_sha_matches": proof.get("worker_sha256") == digest(WORKER),
        "dependency_sha_matches": all(dependency_matches.values()),
        "auditor_sha_matches": (
            auditor_info.get("sha256") == digest(AUDITOR)
            and ROOT / auditor_info.get("path", "") == AUDITOR
        ),
        "positive_regression_verified": positive_ok,
        "source_bus_contracts_verified": all(source_contracts.values()),
        "all_scanned_prior_families_disjoint": len(fixed_set & prior_families) == 0,
        "han_families_disjoint": non_duplication["han_overlap_count"] == 0,
        "workers_one": spec.get("workers") == 1,
        "memory_budget_1536_mib": spec.get("memory_mb_per_process") == 1536,
        "outer_timeout_900_seconds": spec.get("timeout_seconds") == 900.0,
        "stop_on_first_sat": spec.get("stop_on_first_sat") is True,
        "unknown_is_not_unsat": proof.get("unknown_is_not_unsat") is True,
        "or_priority_first": tuple(spec["values"][0]["fixed_kinds"].split(","))[7]
        == "OR",
    }
    errors.extend(value_errors)
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
        "audit_s567c8_g17_o5_s6_midbus3_one_slot.py "
        ".research/byte_adder_phase_shortcut_restart/"
        f"{spec_path.name} --output "
        ".research/byte_adder_phase_shortcut_restart/"
        f"{spec_path.stem}_audit.json"
    )
    return {
        "schema": "s567c8-g17-o5-s6-midbus3-one-slot-preflight-v1",
        "status": "ready-for-ubuntu-matrix" if not errors else "blocked",
        "spec": str(spec_path),
        "spec_sha256": digest(spec_path),
        "constraint_set_sha256": constraint_set_actual,
        "checks": checks,
        "errors": errors,
        "kind_count": len(kinds),
        "fixed_constraint_count": len(fixed_set),
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
            "outer_hard_timeout_seconds_per_job": 900,
            "jobs": JOB_COUNT,
            "worst_case_solver_wall_seconds": 4500,
            "worst_case_solver_wall_hours": 1.25,
            "prior_midbus_matrix_payload_solve_seconds": 2477.015154790948,
            "prior_midbus_matrix_note": (
                "The immediately prior g18/o6/s6 mid-BUS 25-job matrix used "
                "233910 variables and 1735683 clauses per job, with payload "
                "times 34.605..207.330 s under the same 1536 MiB single-worker cap."
            ),
        },
        "strict_proof_scope": {
            "topology": list(expected_topology),
            "ordinary_kinds": JOB_COUNT,
            "domain": "s34567c8_leaf",
            "rows": 486,
            "outputs": ["S5", "S6", "S7", "C8"],
            "gate": 17,
            "delay": 5,
            "components": 11,
            "ordinary": 5,
            "switches": 6,
            "xors": 0,
            "sat_rule": (
                "One auditor-valid SAT payload plus matching finished runner "
                "summary is decisive; stop_on_first_sat permits remaining jobs missing."
            ),
            "unsat_rule": (
                "UNSAT only if all five payloads are terminal UNSAT and the "
                "finished runner summary has no timeout/error/missing result."
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
    return 0 if payload["status"] == "ready-for-ubuntu-matrix" else 1


if __name__ == "__main__":
    raise SystemExit(main())
