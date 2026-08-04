"""Export exact Byte Adder relations that expose Delay Line side inputs.

The level drives all 17 input bits from a bijective xorshift transform of the
cycle counter.  A one-cycle Delay Line therefore exposes a deterministic
derived function of the current input.  This exporter records two relations:

* ``history``: current inputs plus all 17 previous-cycle input bits -> the
  current nine-bit addition result;
* ``future``: current inputs -> the next cycle's nine-bit addition result,
  for investigating output retiming through Delay Lines.

The files are candidate-discovery relations, not deployment artifacts.  The
current runtime proves reset-to-zero and read-old/write-new behavior.  It also
proves that Delay Line is not a timing cut: its output arrival is the maximum
input arrival plus four.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path


WIDTH = 17
ROWS = 1 << WIDTH
MASK = ROWS - 1


def xorshift_cycle(cycle: int) -> int:
    # Match the live test.si exactly: x is a wide Int and is not truncated
    # between shifts.  Only the low 17 bits are consumed by A/B/Carry in.
    value = cycle
    value ^= value << 6
    value ^= value >> 11
    value ^= value << 9
    return value & MASK


def byte_adder_output(value: int) -> int:
    a = value & 0xFF
    b = (value >> 8) & 0xFF
    carry_in = (value >> 16) & 1
    return a + b + carry_in


def bits_lsb_first(value: int, width: int) -> str:
    return "".join("1" if (value >> bit) & 1 else "0" for bit in range(width))


def write_relation(
    path: Path,
    input_names: list[str],
    output_names: list[str],
    rows: list[tuple[int, int]],
) -> dict[str, object]:
    lines = [
        f".i {len(input_names)}",
        f".o {len(output_names)}",
        ".type fr",
        ".ilb " + " ".join(input_names),
        ".ob " + " ".join(output_names),
    ]
    seen: dict[int, int] = {}
    for input_value, output_value in rows:
        previous = seen.setdefault(input_value, output_value)
        if previous != output_value:
            raise RuntimeError(
                f"relation is not functional at {input_value:#x}: "
                f"{previous:#x} != {output_value:#x}"
            )
        lines.append(
            f"{bits_lsb_first(input_value, len(input_names))} "
            f"{bits_lsb_first(output_value, len(output_names))}"
        )
    lines.append(".e")
    encoded = ("\n".join(lines) + "\n").encode("ascii")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encoded)
    return {
        "path": str(path.resolve()),
        "sha256": sha256(encoded).hexdigest(),
        "bytes": len(encoded),
        "care_rows": len(rows),
        "unique_inputs": len(seen),
        "input_count": len(input_names),
        "output_count": len(output_names),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    output_names = [f"s{bit}" for bit in range(8)] + ["cout"]
    current_names = [f"x{bit}" for bit in range(WIDTH)]
    history_names = [f"h{bit}" for bit in range(WIDTH)]

    history_rows: list[tuple[int, int]] = []
    future_rows: list[tuple[int, int]] = []
    current_seen: set[int] = set()
    for cycle in range(ROWS):
        current = xorshift_cycle(cycle)
        previous = xorshift_cycle(cycle - 1) if cycle else 0
        current_seen.add(current)
        history_rows.append(
            (current | (previous << WIDTH), byte_adder_output(current))
        )
        # The value captured on the final source cycle is never observed: the
        # level wins immediately after checking cycle 0x1ffff.  Leaving this
        # one input combination unspecified gives it the correct don't-care
        # status instead of inventing a wraparound to cycle zero.
        if cycle < MASK:
            following = xorshift_cycle(cycle + 1)
            future_rows.append((current, byte_adder_output(following)))

    if len(current_seen) != ROWS:
        raise RuntimeError("the 17-bit xorshift transform is not bijective")
    if history_rows[0] != (0, 0):
        raise RuntimeError("cycle-zero reset witness is not all-zero")
    if xorshift_cycle(2048) != 35393:
        raise RuntimeError("xorshift no-intermediate-truncation regression failed")

    output_dir = args.output_dir.resolve()
    history = write_relation(
        output_dir / "history_relation_fr.pla",
        current_names + history_names,
        output_names,
        history_rows,
    )
    future = write_relation(
        output_dir / "future_output_relation_fr.pla",
        current_names,
        output_names,
        future_rows,
    )
    report = {
        "schema": "tc-byte-adder-delay-line-relation-v1",
        "status": "candidate-discovery-only",
        "test_protocol": {
            "cycles": ROWS,
            "first_cycle": 0,
            "last_cycle": MASK,
            "xorshift": ["x ^= x << 6", "x ^= x >> 11", "x ^= x << 9"],
            "intermediate_truncation": False,
            "cycle_2048_low17_regression": 35393,
            "xorshift_bijective": True,
            "cycle_zero_input": 0,
            "cycle_zero_expected_output": 0,
        },
        "delay_line_cost_assumption": {
            "kind": 13,
            "gate": 5,
            "arrival": 4,
            "source": "Turing Complete 2.1.292 effective component audit",
            "timing_cut": False,
            "output_arrival": "max(input arrivals) + 4",
        },
        "history_relation": history,
        "future_output_relation": future,
        "runtime_semantics": {
            "initial_state": 0,
            "cycle_zero_output": "actively driven 0",
            "update_order": "read old state, publish output, then store current input",
            "z_storage": "input Z is read as data-plane 0; next output is driven 0",
            "single_stage_sequence": "y[0]=0; y[t]=x[t-1]",
            "evidence": [
                "Turing Complete 2.1.292 kind13 codegen case",
                "campaign/double_buffer/test.si",
                "campaign/odd_ticks/test.si",
            ],
        },
        "future_relation_warning": (
            "Delay Line does not hide future-function depth; a precomputed signal "
            "with arrival d leaves the component at d+4.  The final source "
            "cycle is an external don't-care because its captured value is never read."
        ),
    }
    report_path = output_dir / "relations.json"
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
