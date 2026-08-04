"""Generate the exact g18/o6/s6 two-Switch mid-BUS topology matrix.

The component order is ``NOT,NOR,OR,OR,SW,SW,K1,K2,SWx4``.  The two
ordinary slots can consume the two preceding Switch outputs as one resolved
BUS, and the four later Switches can consume either ordinary result.  The
five ordinary kinds in each ordered slot give an exact 5x5 partition.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import itertools
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORKER = HERE / "physical_exact.py"
AUDITOR = HERE / "audit_s567c8_g18_o6_s6_midbus_two_slot.py"
POSITIVE_SCRIPT = HERE / "verify_s567c8_g18_o6_s6_midbus_positive_regression.py"
POSITIVE_RESULT = HERE / "s567c8_g18_o6_s6_midbus_positive_s7c8.json"
FIXED_PREFIX = ("NOT", "NOR", "OR", "OR", "SWITCH", "SWITCH")
FIXED_SUFFIX = ("SWITCH",) * 4
ORDINARY_KINDS = ("NOT", "AND", "OR", "NAND", "NOR")
ALL_PAIRS = tuple(itertools.product(ORDINARY_KINDS, repeat=2))
PAIR_PRIORITY = (("OR", "OR"),) + tuple(
    pair for pair in ALL_PAIRS if pair != ("OR", "OR")
)


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def constraint_bytes(fixed_kinds: tuple[str, ...]) -> bytes:
    return json.dumps(
        fixed_kinds,
        ensure_ascii=True,
        separators=(",", ":"),
    ).encode("ascii")


def value_record(
    *,
    first: str,
    second: str,
    result_root: str,
) -> tuple[dict[str, object], dict[str, str]]:
    fixed = (*FIXED_PREFIX, first, second, *FIXED_SUFFIX)
    constraint_sha = sha256(constraint_bytes(fixed)).hexdigest()
    suffix = f"{first.lower()}-{second.lower()}"
    name = f"s567c8-d5-g18-o06-s06-midbus-{suffix}"
    value: dict[str, object] = {
        "name": name,
        "domain": "s34567c8_leaf",
        "outputs": "S5,S6,S7,C8",
        "gate": 18,
        "delay": 5,
        "components": 12,
        "ordinary": 6,
        "switches": 6,
        "xors": 0,
        "fixed_kinds": ",".join(fixed),
        "constraint_sha256": constraint_sha,
        "split_slots": 1,
        "shard_count": 1,
        "shard_index": 0,
        "solver": "cadical195",
        "output": f"{result_root}/{name}.json",
    }
    return value, {"name": name, "sha256": constraint_sha}


def build(args: argparse.Namespace) -> dict[str, object]:
    result_root = (
        ".research/byte_adder_phase_shortcut_restart/server-results/"
        f"{args.name}"
    )
    values: list[dict[str, object]] = []
    constraints: list[dict[str, str]] = []
    for first, second in PAIR_PRIORITY:
        value, constraint = value_record(
            first=first,
            second=second,
            result_root=result_root,
        )
        values.append(value)
        constraints.append(constraint)

    constraint_set = json.dumps(
        constraints,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    dependencies = (
        ROOT / ".research/byte_adder_ling_theory_agent/exact_free_ling_pair_sat.py",
        ROOT
        / ".research/byte_adder_boolean_superopt_agent/exact_adder_block_sat.py",
        ROOT / ".research/rng_468_joint_macro/joint_parity_cnf.py",
    )
    positive = json.loads(POSITIVE_RESULT.read_text(encoding="utf-8"))
    if (
        positive.get("status") != "verified-positive-regression"
        or positive.get("verification", {}).get("verified") is not True
    ):
        raise RuntimeError("positive regression is not verified")
    fixed_topology = [
        *FIXED_PREFIX,
        "ordinary-kind-slot",
        "ordinary-kind-slot",
        *FIXED_SUFFIX,
    ]
    return {
        "schema": "tc-byte-adder-remote-sweep-v1",
        "name": args.name,
        "description": (
            "Exact g18/o6/s6 class with fixed NOT,NOR,OR,OR prefix, two "
            "early Switches, two adjacent ordinary-kind slots, and four "
            "terminal Switches"
        ),
        "proof_scope": {
            "mode": "matrix",
            "domain": "s34567c8_leaf",
            "outputs": ["S5", "S6", "S7", "C8"],
            "gate": 18,
            "max_delay": 5,
            "components": 12,
            "ordinary": 6,
            "switches": 6,
            "xors": 0,
            "fixed_prefix": list(FIXED_PREFIX[:4]),
            "early_switch_slots_zero_based": [4, 5],
            "variable_ordinary_slots_zero_based": [6, 7],
            "terminal_switch_slots_zero_based": [8, 9, 10, 11],
            "ordinary_kinds": list(ORDINARY_KINDS),
            "ordered_kind_pairs": 25,
            "pair_execution_order": [list(pair) for pair in PAIR_PRIORITY],
            "fixed_topology": fixed_topology,
            "gate_cost_identity": "6*1 + 6*2 = 18",
            "bus_access_contract": {
                "slot6_can_select_switch_slots": [4, 5],
                "slot7_can_select_switch_slots": [4, 5],
                "slot7_can_select_slot6": True,
                "identical_switch_driver_set_may_fanout": True,
                "partial_driver_set_overlap_forbidden": True,
            },
            "coverage": "complete-5x5-partition-of-midbus-two-slot-class",
            "constraint_encoding": "compact-json-string-list-v1",
            "constraint_set_sha256": sha256(constraint_set).hexdigest(),
            "worker_sha256": file_sha256(WORKER),
            "dependency_sha256": {
                str(path.relative_to(ROOT)).replace("\\", "/"): file_sha256(path)
                for path in dependencies
            },
            "auditor": {
                "path": str(AUDITOR.relative_to(ROOT)).replace("\\", "/"),
                "sha256": file_sha256(AUDITOR),
            },
            "positive_regression": {
                "script": str(POSITIVE_SCRIPT.relative_to(ROOT)).replace("\\", "/"),
                "script_sha256": file_sha256(POSITIVE_SCRIPT),
                "artifact": str(POSITIVE_RESULT.relative_to(ROOT)).replace("\\", "/"),
                "artifact_sha256": file_sha256(POSITIVE_RESULT),
                "status": positive["status"],
                "outputs": positive["regression"]["output_names"],
                "rows": positive["verification"]["rows"],
                "actual_gate": positive["verification"]["actual_gate"],
                "actual_max_delay": positive["verification"]["actual_max_delay"],
                "competitive_candidate": False,
            },
            "terminal_statuses": ["sat", "unsat"],
            "unknown_is_not_unsat": True,
            "complete_byte_adder_if_sat": {
                "fixed_low_and_paid_high": 73,
                "s3_s4_cost": 11,
                "this_tail_cost": 18,
                "total_gate": 102,
                "delay": 5,
                "energy": 510,
            },
            "scope_exclusions": [
                "other ordinary/Switch slot orders",
                "other first-four ordinary orders or multisets",
                "XOR or other gate/component decompositions",
                "paid-source shell and residual interface rewrites",
                "the global g18 topology space",
            ],
        },
        "script": "physical_exact.py",
        "working_directory": "../..",
        "workers": args.workers,
        "timeout_seconds": args.timeout,
        "memory_mb_per_process": args.memory_mb,
        "cpu_set": "0-31",
        "nice": 5,
        "stop_on_first_sat": True,
        "values": values,
        "arguments": [
            "--domain",
            "{domain}",
            "--outputs",
            "{outputs}",
            "--gate-bound",
            "{gate}",
            "--max-delay",
            "{delay}",
            "--components",
            "{components}",
            "--switches",
            "{switches}",
            "--xors",
            "{xors}",
            "--fixed-kinds",
            "{fixed_kinds}",
            "--split-slots",
            "{split_slots}",
            "--shard-count",
            "{shard_count}",
            "--shard-index",
            "{shard_index}",
            "--solver",
            "{solver}",
            "--timeout",
            "0",
            "--output",
            "{output}",
        ],
        "log_directory": f"server-runs/{args.name}/logs",
        "result_directory": f"server-runs/{args.name}/run-results",
        "summary": f"server-runs/{args.name}/sweep-summary.json",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--name",
        default="ubuntu_s567c8_g18_o6_s6_midbus_matrix_w1",
    )
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--timeout", type=float, default=900.0)
    parser.add_argument("--memory-mb", type=int, default=1536)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.workers <= 2:
        raise ValueError("this sweep is capped at two workers")
    if args.memory_mb < 1024:
        raise ValueError("memory budget below the already validated 1024 MiB floor")
    payload = build(args)
    encoded = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(encoded, encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(args.output),
                "jobs": len(payload["values"]),
                "workers": payload["workers"],
                "memory_mb_per_process": payload["memory_mb_per_process"],
                "timeout_seconds": payload["timeout_seconds"],
                "constraint_set_sha256": payload["proof_scope"][
                    "constraint_set_sha256"
                ],
                "file_sha256": file_sha256(args.output),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
