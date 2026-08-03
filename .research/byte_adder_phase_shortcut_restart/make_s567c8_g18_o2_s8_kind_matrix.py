"""Generate the complete ordinary-kind matrix for the g18/o2/s8 topology.

The searched topology has two ordinary components followed by eight Switch
components.  Enumerating the five physical ordinary kinds in both ordered
slots yields 25 mutually exclusive, collectively exhaustive constraints for
this topology class.  The generator records a SHA-256 for every exact
``fixed_kinds`` list so timeouts remain auditable unknowns rather than being
mistaken for UNSAT results.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORKER = HERE / "physical_exact.py"
ORDINARY_KINDS = ("NOT", "AND", "OR", "NAND", "NOR")


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def constraint_bytes(fixed_kinds: tuple[str, ...]) -> bytes:
    return json.dumps(
        fixed_kinds,
        ensure_ascii=True,
        separators=(",", ":"),
    ).encode("ascii")


def build(args: argparse.Namespace) -> dict[str, object]:
    values: list[dict[str, object]] = []
    constraint_records: list[dict[str, str]] = []
    result_root = (
        ".research/byte_adder_phase_shortcut_restart/server-results/"
        f"{args.name}"
    )
    for first in ORDINARY_KINDS:
        for second in ORDINARY_KINDS:
            fixed = (first, second, *("SWITCH" for _ in range(8)))
            fixed_text = ",".join(fixed)
            digest = sha256(constraint_bytes(fixed)).hexdigest()
            suffix = f"{first.lower()}-{second.lower()}"
            name = f"s567c8-d5-g18-o02-s08-{suffix}"
            constraint_records.append({"name": name, "sha256": digest})
            values.append(
                {
                    "name": name,
                    "domain": "s34567c8_leaf",
                    "outputs": "S5,S6,S7,C8",
                    "gate": 18,
                    "delay": 5,
                    "components": 10,
                    "ordinary": 2,
                    "switches": 8,
                    "xors": 0,
                    "fixed_kinds": fixed_text,
                    "constraint_sha256": digest,
                    "split_slots": 1,
                    "shard_count": 1,
                    "shard_index": 0,
                    "solver": "cadical195",
                    "output": f"{result_root}/{name}.json",
                }
            )

    constraint_set_bytes = json.dumps(
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
    return {
        "schema": "tc-byte-adder-remote-sweep-v1",
        "name": args.name,
        "description": (
            "Complete 5x5 ordered ordinary-kind partition of the exact "
            "g18/o2/s8 topology with eight terminal Switch components"
        ),
        "proof_scope": {
            "domain": "s34567c8_leaf",
            "outputs": ["S5", "S6", "S7", "C8"],
            "gate": 18,
            "max_delay": 5,
            "components": 10,
            "ordinary": 2,
            "switches": 8,
            "xors": 0,
            "fixed_topology": ["*", "*", *("SWITCH" for _ in range(8))],
            "ordinary_kinds": list(ORDINARY_KINDS),
            "ordered_kind_pairs": 25,
            "coverage": "complete-for-fixed-topology-class",
            "constraint_encoding": "compact-json-string-list-v1",
            "constraint_set_sha256": sha256(constraint_set_bytes).hexdigest(),
            "worker_sha256": file_sha256(WORKER),
            "dependency_sha256": {
                str(path.relative_to(ROOT)).replace("\\", "/"): file_sha256(path)
                for path in dependencies
            },
            "terminal_statuses": ["sat", "unsat"],
            "unknown_is_not_unsat": True,
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
        default="local_s567c8_g18_o2_s8_kind_matrix_w4",
    )
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--timeout", type=float, default=800.0)
    parser.add_argument("--memory-mb", type=int, default=1024)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.workers <= 32:
        raise ValueError("workers must be between 1 and 32")
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
