"""Enumerate exact 431-gate RNG cost fingerprints.

This is arithmetic only.  A matching row is a structural hypothesis, not a
proof that its circuit exists or meets the timing/protocol constraints.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


TARGET = 431


def common_bus() -> dict[str, object]:
    fixed = {
        "state_delay_u32": 32 * 5,
        "feedback_switch_u32": 32 * 2,
        "phase_delay_and_not": 5 + 1,
    }
    logic_budget = TARGET - sum(fixed.values())
    xor_only = [
        {"xor2": 67 - 4 * xor3, "xor3": xor3}
        for xor3 in range(17)
        if 67 - 4 * xor3 >= 0
    ]
    return {
        "name": "common_tristate_word_bus",
        "fixed": fixed,
        "fixed_gate": sum(fixed.values()),
        "logic_gate_budget": logic_budget,
        "logic_delay_budget": 4,
        "xor2_xor3_solutions": xor_only,
        "highlight": {"xor2": 47, "xor3": 5},
        "identity": "160 + 64 + 6 + (47*3 + 5*12) = 431",
    }


def selector_sites() -> dict[str, object]:
    # 32 state Delay, 61 XOR2, one phase Delay and one NOT.
    fixed = 32 * 5 + 61 * 3 + 5 + 1
    choices = [
        {"or": ors, "switch": switches}
        for ors in range(48)
        for switches in range(48)
        if ors + switches == 47 and fixed + ors + 2 * switches == TARGET
    ]
    return {
        "name": "encoded_47_selector_sites",
        "fixed_gate": fixed,
        "selector_gate_budget": TARGET - fixed,
        "solutions": choices,
        "identity": "349 + 12*1 + 35*2 = 431",
    }


def baseline_rewrites() -> dict[str, object]:
    # Start at verified 381 = 32 data Delay + 61 XOR2 + 32 OR + phase Delay/NOT.
    rows = []
    for extra_delay in range(11):
        for xor3_collapses in range(31):
            remainder = 50 - 5 * extra_delay - 6 * xor3_collapses
            if remainder < 0 or remainder % 2:
                continue
            rows.append(
                {
                    "extra_delay": extra_delay,
                    "xor3_replaces_two_xor2": xor3_collapses,
                    "extra_switch": remainder // 2,
                }
            )
    return {
        "name": "381_baseline_rewrite_accounting",
        "equation": "5*extra_delay + 6*xor3_collapse + 2*extra_switch = 50",
        "solutions": rows,
        "highlight": {
            "extra_delay": 4,
            "xor3_replaces_two_xor2": 5,
            "extra_switch": 0,
        },
    }


def redundant_state() -> dict[str, object]:
    return {
        "name": "42_data_state_bits",
        "components": {
            "42_state_delay": 42 * 5,
            "61_xor2": 61 * 3,
            "32_seed_or": 32,
            "phase_delay_and_not": 6,
        },
        "identity": "42*5 + 61*3 + 32 + 6 = 431",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = {
        "target_gate": TARGET,
        "warning": "cost identities only; timing and functional realizability are separate",
        "families": [common_bus(), selector_sites(), baseline_rewrites(), redundant_state()],
    }
    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
