"""Generate the terminal-Switch kind shards suggested by the S7/C8 witness.

The known 16-gate S7/C8 witness uses ordinary kinds NOT, NOR, OR, OR before
six Switches.  This sweep covers every unique ordering of that four-kind
multiset followed by seven Switches for the four-output g18/o4/s7 search.
It intentionally does not claim coverage of other ordinary-kind multisets or
interleaved ordinary/Switch topologies.
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
TAIL_MULTISET = ("NOT", "NOR", "OR", "OR")
PRIORITY_ORDER = ("NOT", "NOR", "OR", "OR")


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def constraint_bytes(fixed_kinds: tuple[str, ...]) -> bytes:
    return json.dumps(
        fixed_kinds,
        ensure_ascii=True,
        separators=(",", ":"),
    ).encode("ascii")


def unique_orders() -> tuple[tuple[str, ...], ...]:
    orders = sorted(set(itertools.permutations(TAIL_MULTISET)))
    orders.remove(PRIORITY_ORDER)
    return (PRIORITY_ORDER, *orders)


def build(args: argparse.Namespace) -> dict[str, object]:
    values: list[dict[str, object]] = []
    constraint_records: list[dict[str, str]] = []
    result_root = (
        ".research/byte_adder_phase_shortcut_restart/server-results/"
        f"{args.name}"
    )
    for ordinary in unique_orders():
        fixed = (*ordinary, *("SWITCH" for _ in range(7)))
        digest = sha256(constraint_bytes(fixed)).hexdigest()
        suffix = "-".join(kind.lower() for kind in ordinary)
        name = f"s567c8-d5-g18-o04-s07-{suffix}"
        constraint_records.append({"name": name, "sha256": digest})
        values.append(
            {
                "name": name,
                "domain": "s34567c8_leaf",
                "outputs": "S5,S6,S7,C8",
                "gate": 18,
                "delay": 5,
                "components": 11,
                "ordinary": 4,
                "switches": 7,
                "xors": 0,
                "fixed_kinds": ",".join(fixed),
                "constraint_sha256": digest,
                "split_slots": 1,
                "shard_count": 1,
                "shard_index": 0,
                "solver": "cadical195",
                "output": f"{result_root}/{name}.json",
            }
        )
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
    return {
        "schema": "tc-byte-adder-remote-sweep-v1",
        "name": args.name,
        "description": (
            "All 12 unique orders of the NOT,NOR,OR,OR ordinary multiset "
            "followed by seven terminal Switch components"
        ),
        "proof_scope": {
            "domain": "s34567c8_leaf",
            "outputs": ["S5", "S6", "S7", "C8"],
            "gate": 18,
            "max_delay": 5,
            "components": 11,
            "ordinary": 4,
            "switches": 7,
            "xors": 0,
            "ordinary_multiset": list(TAIL_MULTISET),
            "fixed_topology": [
                "ordinary",
                "ordinary",
                "ordinary",
                "ordinary",
                *("SWITCH" for _ in range(7)),
            ],
            "unique_orders": 12,
            "coverage": "complete-for-tail-ordinary-multiset-terminal-switch-class",
            "constraint_encoding": "compact-json-string-list-v1",
            "constraint_set_sha256": sha256(constraint_set).hexdigest(),
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
        default="local_s567c8_g18_o4_s7_tail_multiset_w4",
    )
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--timeout", type=float, default=800.0)
    parser.add_argument("--memory-mb", type=int, default=1024)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.workers <= 4:
        raise ValueError("this local sweep is capped at four workers")
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
