"""Verify two local exclusions for the canonical 61-XOR B/C topology."""

from __future__ import annotations

import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / ".research" / "rng_init_reuse" / "verify_init_reuse.py"


def load_reference() -> object:
    spec = importlib.util.spec_from_file_location("rng_init_reuse_reference", SOURCE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {SOURCE}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def matrix_columns(rows: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(
        sum(((row >> column) & 1) << output for output, row in enumerate(rows))
        for column in range(32)
    )


def xor_subsets(values: tuple[int, ...]) -> set[int]:
    result = {0}
    for value in values:
        result |= {current ^ value for current in tuple(result)}
    return result


def base_incidences(reference: object) -> tuple[dict[int, int], tuple[int, ...]]:
    first_layer = tuple(sorted(reference.FIRST_LAYER))
    incidence = {row: 0 for row in first_layer}
    direct = [0] * 32

    for output_index, target in enumerate(reference.B):
        if target in reference.DIRECT:
            direct[target.bit_length() - 1] ^= 1 << output_index
            continue
        if target in reference.FIRST_LAYER:
            incidence[target] ^= 1 << output_index
            continue
        gate = reference.GATE_BY_OUTPUT[target]
        for fanin in (gate.left, gate.right):
            if fanin in reference.FIRST_LAYER:
                incidence[fanin] ^= 1 << output_index
            else:
                direct[fanin.bit_length() - 1] ^= 1 << output_index

    expanded = direct[:]
    for row, column in incidence.items():
        for bit in reference.bits(row):
            expanded[bit] ^= column
    return incidence, tuple(expanded)


def column_exclusion(reference: object) -> dict[str, object]:
    incidence, expanded = base_incidences(reference)
    local_columns: set[int] = set(incidence.values())
    local_modes = 0

    for bit in range(32):
        incident = tuple(
            column for row, column in incidence.items() if (row >> bit) & 1
        )
        modes = xor_subsets(incident)
        local_modes += len(modes)
        local_columns |= {expanded[bit] ^ mode for mode in modes}

    desired = matrix_columns(tuple(reference.T))
    covered = tuple(index for index, column in enumerate(desired) if column in local_columns)
    missing = tuple(index for index, column in enumerate(desired) if column not in local_columns)

    if covered != tuple(range(17)) or missing != tuple(range(17, 32)):
        raise AssertionError(f"canonical missing-column certificate changed: {missing}")

    return {
        "local_modes_before_dedup": local_modes + len(incidence),
        "distinct_possible_leaf_columns": len(local_columns),
        "covered_T_columns": list(covered),
        "missing_T_columns": list(missing),
        "missing_columns_hex": [f"{desired[index]:08x}" for index in missing],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    reference = load_reference()
    result = {
        "scope": (
            "canonical 61-XOR B/C topology; replace any subset of its 27 first-layer "
            "pair gates by stored leaves while keeping all base-output connections fixed"
        ),
        "reference": str(SOURCE),
        "reference_sha256": sha256(SOURCE.read_bytes()).hexdigest(),
        "column_exclusion": column_exclusion(reference),
    }
    payload = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")


if __name__ == "__main__":
    main()
