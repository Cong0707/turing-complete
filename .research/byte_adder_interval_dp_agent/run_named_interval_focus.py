"""Run one or more focused named-interval Byte Adder optimizations.

The broad research driver explores many unrelated families.  This wrapper
keeps memory and latency bounded by solving only the requested delay points,
then immediately persists both structural and exhaustive semantic evidence.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import interval_dp


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--delay", type=int, action="append", required=True)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("named_interval_focus.json"),
    )
    args = parser.parse_args()

    factory = interval_dp.Factory()
    leaves = interval_dp.gp_leaves(factory)
    witnesses, search = interval_dp.solve_named_interval_dag(
        factory, leaves, tuple(dict.fromkeys(args.delay))
    )
    records = []
    for witness in witnesses:
        metrics = factory.structural_metrics(witness.outputs)
        records.append(interval_dp.summarize_witness(factory, witness, metrics))
    document = {
        "schema": "byte-adder-named-interval-focus-v1",
        "delay_limits": list(dict.fromkeys(args.delay)),
        "search": search,
        "witnesses": records,
    }
    args.output.write_text(
        json.dumps(document, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "delay_limits": document["delay_limits"],
                "results": [
                    {
                        "gate": item["gate"],
                        "delay": item["delay"],
                        "energy": item["energy"],
                        "semantic": item["semantic"],
                    }
                    for item in records
                ],
                "output": str(args.output),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
