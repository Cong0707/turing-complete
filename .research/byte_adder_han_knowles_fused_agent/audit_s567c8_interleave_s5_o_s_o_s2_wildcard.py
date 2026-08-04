"""Audit complete wildcard coverage for SWITCHx5,K1,SWITCH,K2,SWITCHx2."""

from __future__ import annotations

from datetime import datetime
from hashlib import sha256
import itertools
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REMOTE = HERE / "remote-results"
PHYSICAL_EXACT = ROOT / ".research/byte_adder_phase_shortcut_restart/physical_exact.py"
BASENAME = "s567c8_g18_o2s8_interleave_s5_o_s_o_s2_cadical195"
EVIDENCE = REMOTE / f"{BASENAME}.json"
LOG = REMOTE / f"{BASENAME}.log"
RUN = REMOTE / f"{BASENAME}.run.json"
DEFAULT_MANIFEST = HERE / "s567c8_interleave_s5_o_s_o_s2_wildcard_manifest.json"
DEFAULT_AUDIT = HERE / "s567c8_interleave_s5_o_s_o_s2_wildcard_audit.json"

ALL_KINDS = ("NOT", "AND", "OR", "NAND", "NOR", "XOR", "SWITCH")
ORDINARY_KINDS = ("NOT", "AND", "OR", "NAND", "NOR")
COST = {"NOT": 1, "AND": 1, "OR": 1, "NAND": 1, "NOR": 1, "XOR": 3, "SWITCH": 2}
FIXED_KINDS = (
    "SWITCH",
    "SWITCH",
    "SWITCH",
    "SWITCH",
    "SWITCH",
    "*",
    "SWITCH",
    "*",
    "SWITCH",
    "SWITCH",
)
WILDCARD_SLOTS = (5, 7)

EXPECTED = {
    "evidence": "fe0cdb48ed75213450dcca28bbd97952ffea04c5a35dfd7c846656b5fddba3a9",
    "log": "a0b2aa447af8d9703f7b571d57325bcdca27f413b599d716f092eb2504a3e196",
    "run": "c9c319f702ae59c7447373c4573ba4d3192c826da0245637bf09af965c33df68",
    "physical_exact": "c48a96e55d8c5076418999f5fa5ee95e9f8207c03f138cd4bccf48908a69c071",
    "suffix_universe": "0b0c7c64fd44259c23762e70b87484cbb06caad9125d2fd944ecc16ac01666c7",
}
EXPECTED_PID = 95609
EXPECTED_WALL_SECONDS = 111.0
EXPECTED_DEPENDENCIES = {
    ".research/byte_adder_ling_theory_agent/exact_free_ling_pair_sat.py": (
        "49bb2640e1cb08c6e2b9ac412a8cf56c058f27966e1dd799d1d813c8f1821017"
    ),
    ".research/byte_adder_boolean_superopt_agent/exact_adder_block_sat.py": (
        "f320ed3029b949185acd13b5462b659502a970406d1bf5047713279e152f56de"
    ),
    ".research/rng_468_joint_macro/joint_parity_cnf.py": (
        "a565201bf7e99f6ded6732e70d883cd9a90e5da2e42d72171f11952bb3566ca4"
    ),
}


def relative(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT)).replace("\\", "/")


def digest(path: Path) -> str | None:
    return sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def suffix_universe() -> list[list[str]]:
    return [[kind] for kind in ALL_KINDS if kind != "XOR"]


def assignment(pair: tuple[str, str]) -> tuple[str, ...]:
    result = list(FIXED_KINDS)
    result[WILDCARD_SLOTS[0]], result[WILDCARD_SLOTS[1]] = pair
    return tuple(result)


def parse_utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def main() -> int:
    audit_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_AUDIT
    manifest_path = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_MANIFEST
    missing = []
    invalid = []
    for path in (PHYSICAL_EXACT, EVIDENCE, LOG, RUN):
        if not path.is_file():
            missing.append({"path": relative(path)})

    if missing:
        audit = {
            "schema": "s567c8-interleave-s5-o-s-o-s2-wildcard-audit-v1",
            "status": "incomplete",
            "missing": missing,
            "invalid": invalid,
        }
        encoded = (json.dumps(audit, ensure_ascii=False, indent=2) + "\n").encode()
        audit_path.write_bytes(encoded)
        print(json.dumps(audit, ensure_ascii=False, indent=2))
        return 1

    raws = {
        "evidence": EVIDENCE.read_bytes(),
        "log": LOG.read_bytes(),
        "run": RUN.read_bytes(),
    }
    hashes = {name: sha256(raw).hexdigest() for name, raw in raws.items()}
    physical_sha = digest(PHYSICAL_EXACT)
    try:
        evidence = json.loads(raws["evidence"])
        log_payload = json.loads(raws["log"])
        run = json.loads(raws["run"])
    except Exception as exc:
        raise RuntimeError(f"downloaded evidence is not JSON: {exc!r}") from exc

    def check(reason: str, condition: bool, **details: object) -> None:
        if not condition:
            invalid.append({"reason": reason, **details})

    for name in ("evidence", "log", "run"):
        check(
            f"{name}_sha256",
            hashes[name] == EXPECTED[name],
            expected=EXPECTED[name],
            actual=hashes[name],
        )
        check(
            f"{name}_lf_bytes",
            b"\n" in raws[name] and b"\r\n" not in raws[name],
        )
    check(
        "physical_exact_sha256",
        physical_sha == EXPECTED["physical_exact"],
        expected=EXPECTED["physical_exact"],
        actual=physical_sha,
    )

    fields = {
        "schema": evidence.get("schema") == "exact-fast-negative-physical-shard-v2",
        "status": evidence.get("status") == "unsat",
        "domain": evidence.get("domain") == "s34567c8_leaf",
        "rows": evidence.get("rows") == 486,
        "outputs": evidence.get("output_names") == ["S5", "S6", "S7", "C8"],
        "free_source_count": len(evidence.get("free_sources", [])) == 29,
        "gate_bound": evidence.get("gate_bound") == 18,
        "max_delay": evidence.get("max_delay") == 5,
        "components": evidence.get("components") == 10,
        "ordinary": evidence.get("ordinary") == 2,
        "switches": evidence.get("exact_switches") == 8,
        "xors": evidence.get("exact_xors") == 0,
        "fixed_kinds": evidence.get("fixed_kinds") == list(FIXED_KINDS),
        "solver": evidence.get("solver") == "cadical195",
        "variables": evidence.get("variables") == 174812,
        "clauses": evidence.get("clauses") == 1340420,
        "physical_nets": evidence.get("physical_nets") is True,
        "public_outputs_must_be_driven": evidence.get("public_outputs_must_be_driven") is True,
        "timer_errors": evidence.get("timer_errors") == [],
        "dependencies": evidence.get("dependency_sha256") == EXPECTED_DEPENDENCIES,
        "no_sat_network": "network" not in evidence,
    }
    failed_fields = sorted(name for name, valid in fields.items() if not valid)
    if failed_fields:
        invalid.append({"reason": "evidence_fields", "failed": failed_fields})

    log_core = {key: value for key, value in log_payload.items() if key not in {"output", "sha256"}}
    check("log_matches_evidence", log_core == evidence)
    check("log_embedded_sha", log_payload.get("sha256") == hashes["evidence"])
    check(
        "log_output_path",
        str(log_payload.get("output", "")).replace("\\", "/").endswith(
            f"/remote-results/{BASENAME}.json"
        ),
    )

    for path_text, expected_sha in EXPECTED_DEPENDENCIES.items():
        actual_sha = digest(ROOT / path_text)
        check(
            "live_dependency_sha256",
            actual_sha == expected_sha,
            path=path_text,
            expected=expected_sha,
            actual=actual_sha,
        )

    try:
        wall_seconds = (parse_utc(run["end_utc"]) - parse_utc(run["start_utc"])).total_seconds()
    except Exception as exc:
        wall_seconds = None
        invalid.append({"reason": "run_timestamps", "error": repr(exc)})
    run_checks = {
        "pid": run.get("pid") == EXPECTED_PID,
        "exit_code": run.get("exit_code") == 0,
        "classification": run.get("classification") == "solver_exit",
        "not_watchdog": run.get("classification") != "watchdog",
        "watchdog_seconds": run.get("watchdog_seconds") == 900,
        "as_limit_kib": run.get("as_limit_kib") == 6291456,
        "nice": run.get("nice") == 5,
        "wall_seconds": wall_seconds == EXPECTED_WALL_SECONDS,
        "solve_wall_agreement": (
            wall_seconds is not None
            and abs(float(evidence.get("solve_seconds", -1000)) - wall_seconds) < 2.0
        ),
    }
    failed_run = sorted(name for name, valid in run_checks.items() if not valid)
    if failed_run:
        invalid.append({"reason": "run_record", "failed": failed_run})

    universe = suffix_universe()
    suffix_sha = sha256(
        json.dumps(universe, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    shard = evidence.get("shard") or {}
    shard_checks = {
        "split_slots": shard.get("split_slots") == 1,
        "shard_count": shard.get("shard_count") == 1,
        "shard_index": shard.get("shard_index") == 0,
        "suffix_universe_count": shard.get("suffix_universe_count") == 6,
        "suffix_universe_sha256": (
            shard.get("suffix_universe_sha256")
            == suffix_sha
            == EXPECTED["suffix_universe"]
        ),
        "all_signatures_assigned": shard.get("assigned_suffix_signatures") == universe,
    }
    failed_shard = sorted(name for name, valid in shard_checks.items() if not valid)
    if failed_shard:
        invalid.append({"reason": "shard", "failed": failed_shard})

    pairs = tuple(itertools.product(ORDINARY_KINDS, repeat=2))
    assignments = [assignment(pair) for pair in pairs]
    assignment_checks = {
        "ordered_pairs": len(pairs) == 25,
        "unique_pairs": len(set(pairs)) == 25,
        "unique_assignments": len(set(assignments)) == 25,
        "wildcard_slots": all(
            full[WILDCARD_SLOTS[0]] == pair[0]
            and full[WILDCARD_SLOTS[1]] == pair[1]
            for pair, full in zip(pairs, assignments, strict=True)
        ),
        "fixed_slots": all(
            all(FIXED_KINDS[slot] == "*" or full[slot] == FIXED_KINDS[slot] for slot in range(10))
            for full in assignments
        ),
        "switch_count": all(full.count("SWITCH") == 8 for full in assignments),
        "xor_count": all(full.count("XOR") == 0 for full in assignments),
        "gate_cost": all(sum(COST[kind] for kind in full) == 18 for full in assignments),
        "split_slot9_fixed_switch": all(full[9] == "SWITCH" for full in assignments),
        "switch_signature_assigned": ["SWITCH"] in universe,
    }
    failed_assignments = sorted(
        name for name, valid in assignment_checks.items() if not valid
    )
    if failed_assignments:
        invalid.append({"reason": "wildcard_assignments", "failed": failed_assignments})

    complete = not missing and not invalid
    manifest = {
        "schema": "s567c8-interleave-s5-o-s-o-s2-wildcard-manifest-v1",
        "status": "unsat-covered" if complete else "incomplete",
        "topology": list(FIXED_KINDS),
        "wildcard_slots": list(WILDCARD_SLOTS),
        "ordinary_kind_alphabet": list(ORDINARY_KINDS),
        "covered_ordered_pair_count": len(pairs),
        "covered_ordered_pairs": [list(pair) for pair in pairs],
        "coverage_proof": {
            "slot_exactly_one_kind": True,
            "exact_switches": 8,
            "fixed_switch_slots": [0, 1, 2, 3, 4, 6, 8, 9],
            "fixed_switch_quota_is_full": True,
            "exact_xors": 0,
            "wildcard_remaining_kinds": list(ORDINARY_KINDS),
            "gate_cost": "8*2 + 2*1 = 18",
            "split_slots": 1,
            "split_slot_index": 9,
            "split_slot_fixed_kind": "SWITCH",
            "all_suffix_signatures_assigned": True,
            "shard_restricts_wildcard_slots": False,
            "both_wildcard_slots_are_solver_free": True,
        },
        "model": {
            "domain": "s34567c8_leaf",
            "rows": 486,
            "outputs": ["S5", "S6", "S7", "C8"],
            "gate_bound": 18,
            "max_delay": 5,
            "components": 10,
            "ordinary": 2,
            "switches": 8,
            "xors": 0,
            "unrestricted_input_bus_selection": True,
            "switch_z_and_conflict_semantics": True,
            "physical_net_partition": True,
            "public_outputs_must_be_driven": True,
            "dead_component_clauses": True,
        },
        "solver_evidence": {
            "status": evidence.get("status"),
            "solver": evidence.get("solver"),
            "variables": evidence.get("variables"),
            "clauses": evidence.get("clauses"),
            "solve_seconds": evidence.get("solve_seconds"),
            "json": relative(EVIDENCE),
            "json_sha256": hashes["evidence"],
            "log": relative(LOG),
            "log_sha256": hashes["log"],
            "run_record": relative(RUN),
            "run_record_sha256": hashes["run"],
            "run_classification": run.get("classification"),
            "watchdog_seconds": run.get("watchdog_seconds"),
            "as_limit_kib": run.get("as_limit_kib"),
            "nice": run.get("nice"),
            "line_endings": "LF (Ubuntu bytes preserved after download)",
        },
        "worker": {
            "path": relative(PHYSICAL_EXACT),
            "sha256": physical_sha,
            "dependency_sha256": EXPECTED_DEPENDENCIES,
        },
        "scope_exclusions": [
            "ordinary slots other than 5 and 7",
            "ordinary/Switch decompositions other than o2/s8",
            "XOR components",
            "gate cost other than exact 18",
            "complete cost-18 lower bound across every topology",
        ],
        "conclusion": (
            "The strict wildcard UNSAT solve covers all 25 ordered ordinary-kind "
            "pairs for topology SWITCHx5,K1,SWITCH,K2,SWITCHx2. The width-1 shard "
            "concerns fixed slot 9 and omits neither wildcard."
        ),
    }
    manifest_encoded = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode()
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_bytes(manifest_encoded)
    manifest_sha = sha256(manifest_encoded).hexdigest()

    auditor_sha = sha256(Path(__file__).read_bytes()).hexdigest()
    audit = {
        "schema": "s567c8-interleave-s5-o-s-o-s2-wildcard-audit-v1",
        "status": "unsat-covered" if complete else "incomplete",
        "missing": missing,
        "invalid": invalid,
        "ordered_pair_count": len(pairs),
        "unique_assignment_count": len(set(assignments)),
        "evidence_sha256": hashes["evidence"],
        "log_sha256": hashes["log"],
        "run_record_sha256": hashes["run"],
        "physical_exact_sha256": physical_sha,
        "suffix_universe_sha256": suffix_sha,
        "manifest": relative(manifest_path),
        "manifest_sha256": manifest_sha,
        "auditor_sha256": auditor_sha,
        "checks": {
            "evidence_fields": fields,
            "run_record": run_checks,
            "shard": shard_checks,
            "wildcard_assignments": assignment_checks,
        },
    }
    audit_encoded = (json.dumps(audit, ensure_ascii=False, indent=2) + "\n").encode()
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.write_bytes(audit_encoded)
    print(
        json.dumps(
            {
                "status": audit["status"],
                "ordered_pair_count": len(pairs),
                "unique_assignment_count": len(set(assignments)),
                "missing": len(missing),
                "invalid": len(invalid),
                "manifest_sha256": manifest_sha,
                "audit_sha256": sha256(audit_encoded).hexdigest(),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if complete else 1


if __name__ == "__main__":
    raise SystemExit(main())
