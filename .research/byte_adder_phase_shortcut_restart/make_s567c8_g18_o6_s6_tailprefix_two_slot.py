"""Generate exact g18/o6/s6 tail-prefix terminal-Switch searches.

The first four ordinary kinds are frozen to the proven S7/C8 witness order
NOT,NOR,OR,OR.  Two additional ordinary-kind slots follow, then six terminal
Switch components.  ``wildcard`` emits the single exact class with both added
slots unconstrained; ``matrix`` emits the equivalent 5x5 fixed-kind partition
for solver fallback when the wildcard instance remains unknown.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORKER = HERE / "physical_exact.py"
TAIL_PREFIX = ("NOT", "NOR", "OR", "OR")
ORDINARY_KINDS = ("NOT", "AND", "OR", "NAND", "NOR")


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
    name: str,
    fixed: tuple[str, ...],
    result_root: str,
) -> tuple[dict[str, object], dict[str, str]]:
    constraint_sha = sha256(constraint_bytes(fixed)).hexdigest()
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
    if args.mode == "wildcard":
        fixed = (*TAIL_PREFIX, "*", "*", *("SWITCH" for _ in range(6)))
        name = "s567c8-d5-g18-o06-s06-tailprefix-wildcard"
        value, constraint = value_record(
            name=name,
            fixed=fixed,
            result_root=result_root,
        )
        values.append(value)
        constraints.append(constraint)
    else:
        for first in ORDINARY_KINDS:
            for second in ORDINARY_KINDS:
                fixed = (
                    *TAIL_PREFIX,
                    first,
                    second,
                    *("SWITCH" for _ in range(6)),
                )
                suffix = f"{first.lower()}-{second.lower()}"
                name = f"s567c8-d5-g18-o06-s06-tailprefix-{suffix}"
                value, constraint = value_record(
                    name=name,
                    fixed=fixed,
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
    coverage = (
        "complete-wildcard-tailprefix-two-ordinary-slot-terminal-switch-class"
        if args.mode == "wildcard"
        else "complete-5x5-partition-of-tailprefix-two-slot-class"
    )
    return {
        "schema": "tc-byte-adder-remote-sweep-v1",
        "name": args.name,
        "description": (
            "Exact g18/o6/s6 class with fixed NOT,NOR,OR,OR ordinary prefix, "
            "two added ordinary-kind slots, and six terminal Switches; "
            f"mode={args.mode}"
        ),
        "proof_scope": {
            "mode": args.mode,
            "domain": "s34567c8_leaf",
            "outputs": ["S5", "S6", "S7", "C8"],
            "gate": 18,
            "max_delay": 5,
            "components": 12,
            "ordinary": 6,
            "switches": 6,
            "xors": 0,
            "tail_prefix": list(TAIL_PREFIX),
            "variable_ordinary_slots_zero_based": [4, 5],
            "ordinary_kinds": list(ORDINARY_KINDS),
            "ordered_kind_pairs": 25,
            "fixed_topology": [
                *TAIL_PREFIX,
                "ordinary-kind-slot",
                "ordinary-kind-slot",
                *("SWITCH" for _ in range(6)),
            ],
            "wildcard_exactness": (
                "components=12, switches=6, xors=0, and six fixed terminal "
                "Switches force both wildcard slots to be ordinary"
            ),
            "coverage": coverage,
            "constraint_encoding": "compact-json-string-list-v1",
            "constraint_set_sha256": sha256(constraint_set).hexdigest(),
            "worker_sha256": file_sha256(WORKER),
            "dependency_sha256": {
                str(path.relative_to(ROOT)).replace("\\", "/"): file_sha256(
                    path
                )
                for path in dependencies
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
    parser.add_argument("--mode", choices=("wildcard", "matrix"), required=True)
    parser.add_argument("--name")
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--timeout", type=float, default=800.0)
    parser.add_argument("--memory-mb", type=int, default=1024)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.name is None:
        args.name = (
            "local_s567c8_g18_o6_s6_tailprefix_wildcard_w1"
            if args.mode == "wildcard"
            else "local_s567c8_g18_o6_s6_tailprefix_matrix_w2"
        )
    if not 1 <= args.workers <= 2:
        raise ValueError("this local sweep is capped at two workers")
    payload = build(args)
    encoded = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(encoded, encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(args.output),
                "mode": args.mode,
                "jobs": len(payload["values"]),
                "workers": payload["workers"],
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
