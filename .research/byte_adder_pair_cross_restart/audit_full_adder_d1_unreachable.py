"""Enumerate the complete delay-1 physical function class for FullAdder Sum."""

from __future__ import annotations

from hashlib import sha256
import itertools
import json
from pathlib import Path


FULL = 0xFF
SUM = 0x96
MAJ = 0xE8
OUTPUT = Path(__file__).with_name("full_adder_d1_unreachable_audit.json")


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def main() -> None:
    raw = {
        "Input 0": 0xAA,
        "Input 1": 0xCC,
        "Input 2": 0xF0,
        "constant 0": 0x00,
        "constant 1": 0xFF,
    }
    ordinary: dict[int, list[str]] = {}

    def keep(mask: int, expression: str) -> None:
        ordinary.setdefault(mask & FULL, []).append(expression)

    for name, value in raw.items():
        keep(~value, f"NOT({name})")
    for (left_name, left), (right_name, right) in itertools.combinations_with_replacement(
        raw.items(), 2
    ):
        keep(left & right, f"AND({left_name},{right_name})")
        keep(left | right, f"OR({left_name},{right_name})")
        keep(~(left & right), f"NAND({left_name},{right_name})")
        keep(~(left | right), f"NOR({left_name},{right_name})")

    driver_rows = []
    compatible = []
    for enable_name, enable in raw.items():
        for data_name, data in raw.items():
            driven = enable
            value = enable & data
            mismatch = driven & (value ^ SUM)
            covered_sum_ones = driven & value & SUM
            row = {
                "enable": enable_name,
                "data": data_name,
                "driven_hex": f"{driven:02x}",
                "value_hex": f"{value:02x}",
                "mismatch_hex": f"{mismatch:02x}",
                "covered_sum_one_rows_hex": f"{covered_sum_ones:02x}",
                "compatible_with_sum_where_driven": mismatch == 0,
            }
            driver_rows.append(row)
            if mismatch == 0:
                compatible.append(row)

    covered_by_all_compatible = 0
    driven_by_all_compatible = 0
    for row in compatible:
        covered_by_all_compatible |= int(row["covered_sum_one_rows_hex"], 16)
        driven_by_all_compatible |= int(row["driven_hex"], 16)

    raw_sum_hits = [name for name, value in raw.items() if value == SUM]
    ordinary_sum_hits = ordinary.get(SUM, [])
    uncovered_sum_ones = SUM & ~covered_by_all_compatible & FULL
    direct_bus_fully_driven_possible = (
        uncovered_sum_ones == 0 and driven_by_all_compatible == FULL
    )
    normalized_bus_possible = uncovered_sum_ones == 0
    status = (
        "verified_unreachable"
        if not raw_sum_hits
        and not ordinary_sum_hits
        and not direct_bus_fully_driven_possible
        and not normalized_bus_possible
        else "failed"
    )

    payload = {
        "schema": "full-adder-delay1-physical-unreachability-audit-v1",
        "status": status,
        "claim": (
            "FullAdder is unreachable at delay<=1 because its Sum parity mask "
            "0x96 is absent from every possible delay-1 primary output form."
        ),
        "target": {
            "sum_hex": f"{SUM:02x}",
            "carry_hex": f"{MAJ:02x}",
            "delay_bound": 1,
            "primary_outputs_fully_driven": True,
        },
        "completeness": {
            "raw_sources": len(raw),
            "ordinary_gate_instances_enumerated": 5 + 4 * 15,
            "distinct_ordinary_truth_masks": len(ordinary),
            "raw_switch_enable_data_pairs": len(driver_rows),
            "xors_excluded": "XOR has primitive delay 2 and cannot be live at a delay-1 output",
            "ordinary_inputs": "arrival-1 ordinary gates can consume only raw inputs/constants",
            "switch_inputs": "arrival-1 Switch enable/data can consume only raw inputs/constants",
            "normalizer": (
                "a zero-delay Maker/Splitter may normalize a delay-1 Switch BUS, "
                "so both direct and normalized BUS policies are checked"
            ),
            "physical_bus_argument": (
                "a wrong-valued enabled driver cannot be repaired by another driver: "
                "it would cause either a mismatch or a forbidden 0/1 conflict"
            ),
        },
        "raw_sources_hex": {name: f"{value:02x}" for name, value in raw.items()},
        "ordinary_truth_masks_hex": [f"{mask:02x}" for mask in sorted(ordinary)],
        "raw_sum_hits": raw_sum_hits,
        "ordinary_sum_hits": ordinary_sum_hits,
        "switch_driver_audit": {
            "pairs": driver_rows,
            "compatible_pair_count": len(compatible),
            "compatible_pairs": compatible,
            "covered_sum_one_rows_hex": f"{covered_by_all_compatible:02x}",
            "required_sum_one_rows_hex": f"{SUM:02x}",
            "uncovered_sum_one_rows_hex": f"{uncovered_sum_ones:02x}",
            "driven_rows_hex": f"{driven_by_all_compatible:02x}",
            "direct_strict_bus_possible": direct_bus_fully_driven_possible,
            "maker_splitter_normalized_bus_possible": normalized_bus_possible,
        },
        "conclusion": {
            "sum_reachable_at_d1": False,
            "full_adder_reachable_at_d1": False,
            "carry_analysis_needed": False,
        },
        "auditor": {
            "path": str(Path(__file__).resolve()),
            "sha256": digest(Path(__file__).resolve()),
        },
    }
    if status != "verified_unreachable":
        raise RuntimeError("delay-1 enumeration did not establish unreachability")
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    OUTPUT.write_bytes(encoded)
    print(
        json.dumps(
            {
                "status": status,
                "output": str(OUTPUT),
                "sha256": sha256(encoded).hexdigest(),
                "ordinary_truth_masks": len(ordinary),
                "compatible_switch_pairs": len(compatible),
                "uncovered_sum_one_rows_hex": f"{uncovered_sum_ones:02x}",
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
