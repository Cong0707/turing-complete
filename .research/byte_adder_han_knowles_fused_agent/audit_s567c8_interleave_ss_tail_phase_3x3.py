"""Audit the strict 3x3 tail-phase kind matrix for an interleaved o2/s8 family.

Covered topology (ten topological components):

    SWITCH, SWITCH, K1, K2, SWITCH, SWITCH, SWITCH, SWITCH, SWITCH, SWITCH

where K1 and K2 independently range over NOT/NOR/OR.  The underlying exact
worker retains unrestricted input BUS selection, Switch Z semantics, conflict
clauses, physical-net partitioning, public-output driven constraints, D5
timing, and dead-component clauses.

The exact worker hashes its LF JSON string before ``Path.write_text``.  On
Windows the on-disk file uses CRLF, so this auditor deliberately verifies both
the byte-exact on-disk SHA256 and the LF-normalized content SHA256.
"""

from __future__ import annotations

from hashlib import sha256
import itertools
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PHYSICAL_EXACT = (
    ROOT / ".research/byte_adder_phase_shortcut_restart/physical_exact.py"
)
DEFAULT_OUTPUT = HERE / "s567c8_interleave_ss_tail_phase_3x3_audit.json"
KINDS = ("NOT", "NOR", "OR")
PREFIX = ("SWITCH", "SWITCH")
SUFFIX = ("SWITCH",) * 6


# (kind1, kind2): (file name, on-disk CRLF SHA256, normalized-LF SHA256)
EXPECTED = {
    ("NOT", "NOT"): (
        "s567c8_g18_o2s8_interleave_ss_not_not_s6_glucose300.json",
        "d34e1823d739e2936de071f91ca77ba4a80470a0d44958d22e9595ab4c362b4e",
        "3d7307dc7b285b914ddc16715d6ee05dacd04fdc9b25e66846fac45985c8fd49",
    ),
    ("NOT", "NOR"): (
        "s567c8_g18_o2s8_interleave_ss_not_nor_s6_glucose300.json",
        "7fa4f2c1963851b14fd58d5047ad9c38601e1bf1063009106154bb338a980b3a",
        "5579cdeb03503a2ac44b528b3371b531af159d72798600f784a6a821cadad68a",
    ),
    ("NOT", "OR"): (
        "s567c8_g18_o2s8_interleave_ss_not_or_s6_cadical195.json",
        "11309d924b475f9a148c44faa831767d6e0f102a843c5354f60fe43451f3bc4d",
        "51fbbb8f65b3e40b9ef9ed6cc74042c40dbc229ab0fa58f0191660a1dfeb1eb8",
    ),
    ("NOR", "NOT"): (
        "s567c8_g18_o2s8_interleave_ss_nor_not_s6_cadical195.json",
        "b55686105313473a0c64be060b298f31248f2383408f53453d6a831deec594f8",
        "7def5f4898b85c20e7889a74119323d667af17d0266f622519c7207c7edaabe2",
    ),
    ("NOR", "NOR"): (
        "s567c8_g18_o2s8_interleave_ss_nor_nor_s6_glucose300.json",
        "57d4faf3b2560e583f0f3561d4c0a692a2472a98313d0710866c1db2f41dad0c",
        "675008a1c44d63e28d60c46ca3eb5d07cefbaa72603429673330f0997f4b685d",
    ),
    ("NOR", "OR"): (
        "s567c8_g18_o2s8_interleave_ss_nor_or_s6_glucose300.json",
        "4d6488b5854dea30a347e7c56845eee4399c26affc5f0e785dd7052848e69081",
        "d2c56a2d54b317a12b5783e954c2df1f4f743492e39e32edc9fe4e8862c77c50",
    ),
    ("OR", "NOT"): (
        "s567c8_g18_o2s8_interleave_ss_or_not_s6_glucose300.json",
        "7a81845cd688f8701de67b9cc0cfa4090a42c1843769b4966ee7752c7eb67a9f",
        "ef0ed5572d2c5a3560522cc26bf667aca57dc9d42a1ac21c8a14d350485cb7dc",
    ),
    ("OR", "NOR"): (
        "s567c8_g18_o2s8_interleave_ss_or_nor_s6_glucose300.json",
        "b606f475d997c38dcfbee62cd4d76b782218d93b75dc98f9fa85a4cef1d9a85e",
        "575cd8e45411d9915647c81becf9c20157e30941f0e6680447bc1cdc9c4bae75",
    ),
    ("OR", "OR"): (
        "s567c8_g18_o2s8_interleave_ss_or_or_s6_cadical195.json",
        "e64eca536cfb5a38a4b7516a5ca6919ed2f07da212136afed6604dd02d693a8d",
        "08925e7f28617137763e4cdafb95030d96a7baec17fb92ec5d0f239dffe7fe19",
    ),
}

EXPECTED_PHYSICAL_EXACT_SHA256 = (
    "c48a96e55d8c5076418999f5fa5ee95e9f8207c03f138cd4bccf48908a69c071"
)


def relative(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT)).replace("\\", "/")


def main() -> int:
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUTPUT
    expected_pairs = tuple(itertools.product(KINDS, repeat=2))
    missing = []
    invalid = []
    non_unsat = []
    records = []
    dependency_reference = None

    if set(EXPECTED) != set(expected_pairs):
        raise AssertionError("expected map does not cover the 3x3 matrix")

    physical_sha = sha256(PHYSICAL_EXACT.read_bytes()).hexdigest()
    if physical_sha != EXPECTED_PHYSICAL_EXACT_SHA256:
        invalid.append(
            {
                "path": relative(PHYSICAL_EXACT),
                "reason": "physical_exact_sha256_mismatch",
                "expected": EXPECTED_PHYSICAL_EXACT_SHA256,
                "actual": physical_sha,
            }
        )

    for pair in expected_pairs:
        file_name, expected_disk_sha, expected_lf_sha = EXPECTED[pair]
        path = HERE / file_name
        if not path.is_file():
            missing.append({"pair": list(pair), "path": relative(path)})
            continue
        raw = path.read_bytes()
        disk_sha = sha256(raw).hexdigest()
        normalized = raw.replace(b"\r\n", b"\n")
        lf_sha = sha256(normalized).hexdigest()
        try:
            payload = json.loads(raw)
        except Exception as exc:
            invalid.append(
                {
                    "pair": list(pair),
                    "path": relative(path),
                    "reason": f"json_decode:{exc!r}",
                }
            )
            continue

        expected_fixed = [*PREFIX, *pair, *SUFFIX]
        checks = {
            "on_disk_sha256": disk_sha == expected_disk_sha,
            "normalized_lf_sha256": lf_sha == expected_lf_sha,
            "schema": payload.get("schema") == "exact-fast-negative-physical-shard-v2",
            "domain": payload.get("domain") == "s34567c8_leaf",
            "rows": payload.get("rows") == 486,
            "outputs": payload.get("output_names") == ["S5", "S6", "S7", "C8"],
            "gate_bound": payload.get("gate_bound") == 18,
            "max_delay": payload.get("max_delay") == 5,
            "components": payload.get("components") == 10,
            "ordinary": payload.get("ordinary") == 2,
            "switches": payload.get("exact_switches") == 8,
            "xors": payload.get("exact_xors") == 0,
            "fixed_kinds": payload.get("fixed_kinds") == expected_fixed,
            "physical_nets": payload.get("physical_nets") is True,
            "public_outputs_must_be_driven": (
                payload.get("public_outputs_must_be_driven") is True
            ),
            "timer_errors": payload.get("timer_errors") == [],
            "no_sat_network": "network" not in payload,
        }
        failed_checks = sorted(name for name, ok in checks.items() if not ok)
        if failed_checks:
            invalid.append(
                {
                    "pair": list(pair),
                    "path": relative(path),
                    "reason": "failed_checks",
                    "checks": failed_checks,
                }
            )
        if payload.get("status") != "unsat":
            non_unsat.append(
                {
                    "pair": list(pair),
                    "path": relative(path),
                    "status": payload.get("status"),
                }
            )

        dependencies = payload.get("dependency_sha256")
        if dependency_reference is None:
            dependency_reference = dependencies
        elif dependencies != dependency_reference:
            invalid.append(
                {
                    "pair": list(pair),
                    "path": relative(path),
                    "reason": "dependency_sha256_mismatch_across_records",
                }
            )

        records.append(
            {
                "pair": list(pair),
                "path": relative(path),
                "status": payload.get("status"),
                "solver": payload.get("solver"),
                "solve_seconds": payload.get("solve_seconds"),
                "variables": payload.get("variables"),
                "clauses": payload.get("clauses"),
                "on_disk_sha256": disk_sha,
                "normalized_lf_sha256": lf_sha,
                "checks_ok": not failed_checks,
            }
        )

    if dependency_reference:
        for relative_path, expected_sha in dependency_reference.items():
            dependency = ROOT / relative_path
            actual_sha = (
                sha256(dependency.read_bytes()).hexdigest()
                if dependency.is_file()
                else None
            )
            if actual_sha != expected_sha:
                invalid.append(
                    {
                        "path": relative_path,
                        "reason": "live_dependency_sha256_mismatch",
                        "expected": expected_sha,
                        "actual": actual_sha,
                    }
                )

    duplicate_pairs = sorted(
        pair
        for pair in expected_pairs
        if sum(record["pair"] == list(pair) for record in records) != 1
    )
    complete = not missing and not invalid and not non_unsat and not duplicate_pairs
    source_sha = sha256(Path(__file__).read_bytes()).hexdigest()
    payload = {
        "schema": "s567c8-interleave-ss-tail-phase-3x3-audit-v1",
        "status": "unsat-covered" if complete else "incomplete",
        "topology": ["SWITCH", "SWITCH", "K1", "K2", *SUFFIX],
        "kind_alphabet": list(KINDS),
        "ordered_pair_count": len(expected_pairs),
        "selected_evidence_count": len(records),
        "missing": missing,
        "invalid": invalid,
        "non_unsat": non_unsat,
        "duplicate_pair": [list(pair) for pair in duplicate_pairs],
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
        "line_endings": {
            "on_disk": "CRLF",
            "worker_stdout_sha_basis": "LF JSON before Path.write_text",
            "both_hashes_verified": True,
        },
        "records": records,
        "dependency_sha256": dependency_reference,
        "physical_exact_sha256": physical_sha,
        "auditor_sha256": source_sha,
        "scope_exclusions": [
            "K1 or K2 is AND or NAND",
            "ordinary components occupy positions other than slots 2 and 3",
            "ordinary/Switch decompositions other than o2/s8",
            "XOR components",
            "gate cost below or above exact 18",
        ],
        "conclusion": (
            "For topology SWITCH,SWITCH,K1,K2,SWITCHx6, every ordered pair "
            "K1,K2 in {NOT,NOR,OR} is strictly UNSAT in the full physical "
            "486-row D5 model.  This is a 3x3 restricted kind-matrix result, "
            "not a complete interleaved-o2/s8 lower bound."
        ),
    }
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(encoded)
    print(
        json.dumps(
            {
                "status": payload["status"],
                "ordered_pair_count": len(expected_pairs),
                "selected_evidence_count": len(records),
                "missing": len(missing),
                "invalid": len(invalid),
                "non_unsat": len(non_unsat),
                "duplicate_pair": len(duplicate_pairs),
                "output": str(output.resolve()),
                "sha256": sha256(encoded).hexdigest(),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if complete else 1


if __name__ == "__main__":
    raise SystemExit(main())
