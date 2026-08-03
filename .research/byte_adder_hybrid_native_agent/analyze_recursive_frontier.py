"""Freeze the legal-width recursive Add cost arithmetic for Byte Adder.

This script deliberately does not claim that a residual gate budget is a circuit.
It records only the native scaling law, legal serial partitions, and the residual
budget left by one U4 Add when walking the observed public Pareto chain.
"""

from __future__ import annotations

import json
from itertools import combinations_with_replacement
from math import ceil
from pathlib import Path


OUT = Path(__file__).with_name("recursive_frontier_certificate.json")
LEGAL_WIDTHS = (1, 2, 4, 8)
SPLITTABLE_WIDTHS = (1, 2, 4)


def scaled_cost(base_gate: int, base_delay: int, width: int) -> tuple[int, int]:
    if width not in LEGAL_WIDTHS:
        raise ValueError(f"width {width} is not materializable before Byte Adder")
    gate = ceil(base_gate * width / 8)
    delay = max(min(width, 4), ceil(base_delay * width / 8))
    return gate, delay


def partitions(total: int = 8) -> list[tuple[int, ...]]:
    result: list[tuple[int, ...]] = []
    for length in range(2, total + 1):
        for parts in combinations_with_replacement(SPLITTABLE_WIDTHS, length):
            if sum(parts) == total:
                result.append(parts)
    return result


def main() -> None:
    bootstrap = (154, 4)
    split_rows = []
    for parts in partitions():
        costs = [scaled_cost(*bootstrap, width) for width in parts]
        split_rows.append({
            "parts": list(parts),
            "segment_costs": [{"gate": g, "delay": d} for g, d in costs],
            "serial_gate": sum(g for g, _ in costs),
            "serial_delay": sum(d for _, d in costs),
        })
    split_rows.sort(key=lambda row: (row["serial_gate"], row["serial_delay"], row["parts"]))

    public_chain = [
        (154, 4),
        (103, 5),
        (88, 6),
        (79, 7),
        (74, 8),
        (71, 9),
        (68, 10),
        (67, 11),
        (65, 12),
        (63, 13),
        (62, 14),
        (61, 15),
        (59, 16),
        (57, 17),
        (56, 18),
    ]
    transitions = []
    for previous, target in zip(public_chain, public_chain[1:]):
        u4_gate, u4_delay = scaled_cost(*previous, 4)
        transitions.append({
            "previous_u8": {"gate": previous[0], "delay": previous[1]},
            "scaled_u4": {"gate": u4_gate, "delay": u4_delay},
            "target_u8": {"gate": target[0], "delay": target[1]},
            "residual_gate": target[0] - u4_gate,
            "target_minus_u4_delay": target[1] - u4_delay,
            "status": "arithmetic residual only; no DAG implied",
        })

    certificate = {
        "formula": {
            "gate": "ceil(base_gate * width / 8)",
            "delay": "max(min(width, 4), ceil(base_delay * width / 8))",
        },
        "legal_widths_before_byte_adder": list(LEGAL_WIDTHS),
        "bootstrap_154_4_scaled": {
            str(width): {"gate": g, "delay": d}
            for width in LEGAL_WIDTHS
            for g, d in [scaled_cost(*bootstrap, width)]
        },
        "bootstrap_serial_partitions": split_rows,
        "best_non_u8_serial_partition": split_rows[0],
        "observed_public_chain_u4_residuals": transitions,
        "scope": [
            "No U3/U5/U6/U7 materialization is assumed.",
            "Serial partition delay is the sum along the carry chain.",
            "Residual gate and delay numbers are not construction certificates.",
            "A complete DAG, truth-table replay, timing proof, and geometry proof are still required.",
        ],
    }
    OUT.write_text(json.dumps(certificate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
