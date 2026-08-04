"""Generate the single exact g16/o4/s6 all-Switch-tail job."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORKER = HERE / "physical_exact.py"
AUDITOR = HERE / "audit_s567c8_g16_o4_s6_all_switch_tail.py"
POSITIVE_SCRIPT = (
    HERE / "verify_s567c8_g16_o4_s6_all_switch_tail_positive_regression.py"
)
POSITIVE_RESULT = HERE / "s567c8_g16_o4_s6_all_switch_tail_positive_s7c8.json"
FIXED_KINDS = ("NOT", "NOR", "OR", "OR", *("SWITCH" for _ in range(6)))
JOB_NAME = "s567c8-d5-g16-o04-s06-all-switch-tail"


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def constraint_sha256() -> str:
    return sha256(
        json.dumps(
            FIXED_KINDS,
            ensure_ascii=True,
            separators=(",", ":"),
        ).encode("ascii")
    ).hexdigest()


def build(args: argparse.Namespace) -> dict[str, object]:
    result_root = (
        ".research/byte_adder_phase_shortcut_restart/server-results/"
        f"{args.name}"
    )
    constraint = constraint_sha256()
    value: dict[str, object] = {
        "name": JOB_NAME,
        "domain": "s34567c8_leaf",
        "outputs": "S5,S6,S7,C8",
        "gate": 16,
        "delay": 5,
        "components": 10,
        "ordinary": 4,
        "switches": 6,
        "xors": 0,
        "fixed_kinds": ",".join(FIXED_KINDS),
        "constraint_sha256": constraint,
        "split_slots": 1,
        "shard_count": 1,
        "shard_index": 0,
        "solver": "cadical195",
        "output": f"{result_root}/{JOB_NAME}.json",
    }
    constraint_records = [{"name": JOB_NAME, "sha256": constraint}]
    constraint_set = json.dumps(
        constraint_records,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    dependencies = (
        ROOT / ".research/byte_adder_ling_theory_agent/exact_free_ling_pair_sat.py",
        ROOT / ".research/byte_adder_boolean_superopt_agent/exact_adder_block_sat.py",
        ROOT / ".research/rng_468_joint_macro/joint_parity_cnf.py",
    )
    positive = json.loads(POSITIVE_RESULT.read_text(encoding="utf-8"))
    if (
        positive.get("status") != "verified-positive-regression"
        or positive.get("verification", {}).get("verified") is not True
    ):
        raise RuntimeError("positive regression is not verified")
    return {
        "schema": "tc-byte-adder-remote-sweep-v1",
        "name": args.name,
        "description": (
            "Exact fixed g16/o4/s6 NOT,NOR,OR,OR plus six-Switch topology"
        ),
        "proof_scope": {
            "mode": "fixed-topology",
            "domain": "s34567c8_leaf",
            "outputs": ["S5", "S6", "S7", "C8"],
            "gate": 16,
            "max_delay": 5,
            "components": 10,
            "ordinary": 4,
            "switches": 6,
            "xors": 0,
            "fixed_topology": list(FIXED_KINDS),
            "gate_cost_identity": "4*1 + 6*2 = 16",
            "coverage": "complete-single-fixed-g16-all-switch-tail-class",
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
                "this_tail_cost": 16,
                "total_gate": 100,
                "delay": 5,
                "energy": 500,
            },
            "scope_exclusions": [
                "any other ordinary kind/order",
                "any other ordinary/Switch phase order",
                "XOR or other gate/component decompositions",
                "paid-source shell and residual interface rewrites",
                "the global g16 topology space",
            ],
        },
        "script": "physical_exact.py",
        "working_directory": "../..",
        "workers": 1,
        "timeout_seconds": args.timeout,
        "memory_mb_per_process": args.memory_mb,
        "cpu_set": "0-31",
        "nice": 5,
        "stop_on_first_sat": True,
        "values": [value],
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
        default="ubuntu_s567c8_g16_o4_s6_all_switch_tail_w1",
    )
    parser.add_argument("--timeout", type=float, default=900.0)
    parser.add_argument("--memory-mb", type=int, default=1536)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.memory_mb < 1024:
        raise ValueError("memory budget below the validated 1024 MiB floor")
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
