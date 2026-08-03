"""Audit mapped joint RNG netlists with current Turing Complete costs.

The old ABC artifacts in this directory were never connected to the save
generator.  This script gives them a narrow, reproducible audit: parse the
gate-level Verilog, replay the two legal one-shot protocol modes, and compute
weighted arrival times for both the 67-cycle and 66-cycle control shells.
It does not read or write the live save and never starts the game.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import random
import re
import sys
from typing import Iterable


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SRC = ROOT / "src"
ARCHIVE = ROOT / "examples" / "rng" / "research" / "archive" / "rng_joint_boolean"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from tc_save_lab.rng_encoded_asic import (  # noqa: E402
    B,
    C,
    T,
    WORD_BITS,
    apply_matrix,
)


CELL_RE = re.compile(
    r"^\s*(AND|NAND|NOR|NOT|OR|XNOR|XOR|BUF)\s+\w+"
    r"\(\.A\(([^)]+)\),\s*(?:\.B\(([^)]+)\),\s*)?\.Y\(([^)]+)\)\);\s*$"
)
GATE_COST = {
    "AND": 1,
    "NAND": 1,
    "NOR": 1,
    "NOT": 1,
    "OR": 1,
    "XNOR": 3,
    "XOR": 3,
    "BUF": 0,
}
DELAY_COST = {
    "AND": 1,
    "NAND": 1,
    "NOR": 1,
    "NOT": 1,
    "OR": 1,
    "XNOR": 2,
    "XOR": 2,
    "BUF": 0,
}


@dataclass(frozen=True)
class Cell:
    kind: str
    left: str
    right: str | None
    output: str


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse(path: Path) -> tuple[Cell, ...]:
    cells = []
    for line_number, line in enumerate(path.read_text(encoding="ascii").splitlines(), 1):
        match = CELL_RE.match(line)
        if match:
            cells.append(Cell(match.group(1), match.group(2), match.group(3), match.group(4)))
        elif re.match(r"^\s*[A-Z]+\s+g\d+\(", line):
            raise ValueError(f"unsupported cell syntax at {path}:{line_number}: {line}")
    if not cells:
        raise ValueError(f"no cells parsed from {path}")
    return tuple(cells)


def evaluate(cells: Iterable[Cell], seed: int, state: int) -> tuple[int, int]:
    values = {f"s{bit}": seed >> bit & 1 for bit in range(WORD_BITS)}
    values.update({f"q{bit}": state >> bit & 1 for bit in range(WORD_BITS)})
    for cell in cells:
        left = values[cell.left]
        right = values[cell.right] if cell.right is not None else None
        if cell.kind == "AND":
            value = left & right
        elif cell.kind == "NAND":
            value = 1 ^ (left & right)
        elif cell.kind == "NOR":
            value = 1 ^ (left | right)
        elif cell.kind == "NOT":
            value = 1 ^ left
        elif cell.kind == "OR":
            value = left | right
        elif cell.kind == "XNOR":
            value = 1 ^ (left ^ right)
        elif cell.kind == "XOR":
            value = left ^ right
        elif cell.kind == "BUF":
            value = left
        else:  # pragma: no cover - parse() already restricts kinds
            raise AssertionError(cell.kind)
        values[cell.output] = value
    feedback = sum(values[f"fb{bit}"] << bit for bit in range(WORD_BITS))
    output = sum(values[f"out{bit}"] << bit for bit in range(WORD_BITS))
    return feedback, output


def verify(cells: tuple[Cell, ...]) -> dict[str, int]:
    vectors = [0, 1, 2, 0x12345678, 0xFFFFFFFF]
    vectors.extend(1 << bit for bit in range(WORD_BITS))
    generator = random.Random(0x4A4F494E54)
    vectors.extend(generator.getrandbits(32) for _ in range(2048))
    for value in vectors:
        load_feedback, _ = evaluate(cells, value, 0)
        if load_feedback != apply_matrix(T, value):
            raise AssertionError(
                f"load mismatch {value:08x}: {load_feedback:08x} != "
                f"{apply_matrix(T, value):08x}"
            )
        steady_feedback, steady_output = evaluate(cells, 0, value)
        expected_feedback = apply_matrix(B, value)
        expected_output = apply_matrix(C, value)
        if (steady_feedback, steady_output) != (expected_feedback, expected_output):
            raise AssertionError(
                f"steady mismatch {value:08x}: "
                f"{steady_feedback:08x}/{steady_output:08x} != "
                f"{expected_feedback:08x}/{expected_output:08x}"
            )
    return {"legal_mode_vector_count": len(vectors) * 2}


def timing(cells: tuple[Cell, ...], *, seed_arrival: int, state_arrival: int = 4) -> dict[str, object]:
    arrival = {f"s{bit}": seed_arrival for bit in range(WORD_BITS)}
    arrival.update({f"q{bit}": state_arrival for bit in range(WORD_BITS)})
    parent: dict[str, str] = {}
    kind_by_output: dict[str, str] = {}
    for cell in cells:
        inputs = [cell.left] if cell.right is None else [cell.left, cell.right]
        predecessor = max(inputs, key=arrival.__getitem__)
        arrival[cell.output] = arrival[predecessor] + DELAY_COST[cell.kind]
        parent[cell.output] = predecessor
        kind_by_output[cell.output] = cell.kind

    feedback = {f"fb{bit}": arrival[f"fb{bit}"] for bit in range(WORD_BITS)}
    outputs = {f"out{bit}": arrival[f"out{bit}"] for bit in range(WORD_BITS)}
    terminal = max((*feedback, *outputs), key=arrival.__getitem__)
    path = []
    signal = terminal
    while signal in parent:
        path.append(
            {
                "signal": signal,
                "kind": kind_by_output[signal],
                "arrival": arrival[signal],
            }
        )
        signal = parent[signal]
    path.append({"signal": signal, "kind": "PI", "arrival": arrival[signal]})
    path.reverse()
    return {
        "seed_arrival": seed_arrival,
        "state_arrival": state_arrival,
        "maximum_feedback_arrival": max(feedback.values()),
        "maximum_output_arrival": max(outputs.values()),
        "maximum_arrival": arrival[terminal],
        "critical_terminal": terminal,
        "critical_path": path,
    }


def audit(path: Path) -> dict[str, object]:
    cells = parse(path)
    counts = Counter(cell.kind for cell in cells)
    logic_gate = sum(GATE_COST[cell.kind] for cell in cells)
    return {
        "path": str(path),
        "sha256": sha256(path),
        "cell_count": len(cells),
        "kind_counts": dict(sorted(counts.items())),
        "logic_gate": logic_gate,
        "verification": verify(cells),
        "timing": {
            "67_cycle_load_pulse_seed_at_4": timing(cells, seed_arrival=4),
            "66_cycle_one_shot_not_ready_seed_at_5": timing(cells, seed_arrival=5),
            "persistent_seed_at_0": timing(cells, seed_arrival=0),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--output", type=Path, default=HERE / "weighted-netlist-audit.json")
    args = parser.parse_args()
    paths = args.paths or sorted(ARCHIVE.glob("full_*.v"))
    result = {
        "schema": 1,
        "status": "verified mapped netlists; no live save access",
        "current_costs": {"gate": GATE_COST, "delay": DELAY_COST},
        "netlists": [audit(path.resolve()) for path in paths],
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
