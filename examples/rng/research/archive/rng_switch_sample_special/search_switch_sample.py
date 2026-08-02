#!/usr/bin/env python3
r"""Exact finite-care audit for the 42-state RNG Switch repair idea.

The script never opens the game or a player save.  It reconstructs the fixed
256-test protocol, verifies the recorded 42-state frontier, models kind-12
Bit Switch outputs as true tri-state drivers, and exhaustively checks the
smallest useful Switch/nonlinear repair families on the live care set.

Run from the repository root:

    .\.venv\Scripts\python.exe \
      .research\rng_switch_sample_special\search_switch_sample.py \
      --output .research\rng_switch_sample_special\certificate.json
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import itertools
import json
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[2]
FRONTIER = (
    ROOT
    / ".research"
    / "rng_42state_direct"
    / "linear42_audit"
    / "frontier_excess3_verified.json"
)
MASK32 = (1 << 32) - 1
STATE_BITS = 42
LOAD_TESTS = 256
OUTPUT_TICKS = 65
FEEDBACK_TICKS = 64
SEED_MULTIPLIER = 0x4848F09881D3DDD1
MASK64 = (1 << 64) - 1


class ShortCircuit(ValueError):
    """Raised when active tri-state drivers disagree."""


@dataclass(frozen=True)
class Resolved:
    value: int
    is_z: bool


def bit_switch(enable: int, data: int) -> int | None:
    """Kind 12: input0 is enable; disabled output is Z, not active zero."""

    if enable not in (0, 1) or data not in (0, 1):
        raise ValueError("Bit Switch inputs must be bits")
    return data if enable else None


def resolve_bus(*drivers: int | None) -> Resolved:
    """Resolve one game network, ignoring Z and rejecting 0/1 conflicts."""

    active = [value for value in drivers if value is not None]
    if not active:
        return Resolved(0, True)
    if any(value != active[0] for value in active[1:]):
        raise ShortCircuit(f"conflicting active drivers: {active}")
    return Resolved(active[0], False)


def xorshift32(value: int) -> int:
    value ^= value >> 13
    value ^= (value << 17) & MASK32
    value ^= value >> 5
    return value & MASK32


def live_seed(test_id: int) -> int:
    mixed = ((test_id + 1) * SEED_MULTIPLIER) & MASK64
    return 1 + mixed % 0xFFFFFFFE


def apply_matrix(rows: tuple[int, ...], value: int) -> int:
    return sum(
        (((row & value).bit_count() & 1) << index)
        for index, row in enumerate(rows)
    )


def gf2_rank(values: Iterable[int]) -> int:
    basis: dict[int, int] = {}
    for original in values:
        value = original
        while value:
            pivot = value.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = value
                break
            value ^= basis[pivot]
    return len(basis)


def row_signature(row: int, leaves: tuple[int, ...]) -> int:
    result = 0
    while row:
        low = row & -row
        result ^= leaves[low.bit_length() - 1]
        row ^= low
    return result


@dataclass(frozen=True)
class Signal:
    signature: int
    expression: str
    cost: int
    depth: int


def primitive_signals(leaves: tuple[int, ...], full_mask: int) -> tuple[Signal, ...]:
    """Raw/constants plus every NOT and two-input cheap one-delay gate.

    Constants are included only to make impossibility searches stronger.  They
    are never assigned a negative or hidden cost.
    """

    raw = [Signal(value, f"q[{index}]", 0, 0) for index, value in enumerate(leaves)]
    raw.extend((Signal(0, "0", 0, 0), Signal(full_mask, "1", 0, 0)))
    generated: list[Signal] = list(raw)
    for signal in raw:
        generated.append(
            Signal(full_mask ^ signal.signature, f"NOT({signal.expression})", 1, 1)
        )
    for left, right in itertools.combinations(raw, 2):
        a = left.signature
        b = right.signature
        generated.extend(
            (
                Signal(a & b, f"AND({left.expression},{right.expression})", 1, 1),
                Signal(a | b, f"OR({left.expression},{right.expression})", 1, 1),
                Signal(
                    full_mask ^ (a & b),
                    f"NAND({left.expression},{right.expression})",
                    1,
                    1,
                ),
                Signal(
                    full_mask ^ (a | b),
                    f"NOR({left.expression},{right.expression})",
                    1,
                    1,
                ),
            )
        )

    # Keep one deterministic cheapest representative per exact care signature.
    unique: dict[int, Signal] = {}
    for signal in generated:
        old = unique.get(signal.signature)
        if old is None or (signal.cost, signal.depth, signal.expression) < (
            old.cost,
            old.depth,
            old.expression,
        ):
            unique[signal.signature] = signal
    return tuple(unique.values())


def build_points(h_rows: tuple[int, ...]) -> tuple[
    tuple[int, ...], tuple[int, ...], tuple[int, ...]
]:
    seeds = tuple(live_seed(test_id) for test_id in range(LOAD_TESTS))
    states = tuple(apply_matrix(h_rows, seed) for seed in seeds)
    steady_ticks: list[tuple[int, ...]] = []
    for _ in range(OUTPUT_TICKS):
        steady_ticks.append(states)
        states = tuple(apply_matrix(h_rows, state) for state in states)
    output_points = tuple(value for tick in steady_ticks for value in tick)
    feedback_points = seeds + tuple(
        value for tick in steady_ticks[:FEEDBACK_TICKS] for value in tick
    )
    return seeds, output_points, feedback_points


def verify_sequence(
    h_rows: tuple[int, ...], o_rows: tuple[int, ...], seeds: tuple[int, ...]
) -> None:
    for seed in seeds:
        state = apply_matrix(h_rows, seed)
        natural = seed
        for _ in range(OUTPUT_TICKS):
            natural = xorshift32(natural)
            actual = apply_matrix(o_rows, state)
            if actual != natural:
                raise AssertionError(
                    f"sequence mismatch seed={seed:08x}: {actual:08x}!={natural:08x}"
                )
            state = apply_matrix(h_rows, state)


def signatures(points: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(
        sum(((value >> bit) & 1) << index for index, value in enumerate(points))
        for bit in range(STATE_BITS)
    )


def support_histogram(row: int, points: tuple[int, ...]) -> list[int]:
    support = tuple(bit for bit in range(STATE_BITS) if (row >> bit) & 1)
    counts = [0] * (1 << len(support))
    for value in points:
        pattern = sum(((value >> bit) & 1) << index for index, bit in enumerate(support))
        counts[pattern] += 1
    return counts


def nested_two_gate_hits(
    primitives: tuple[Signal, ...],
    raw: tuple[Signal, ...],
    target_by_signature: dict[int, list[str]],
    full_mask: int,
) -> list[dict[str, object]]:
    """Enumerate outer cheap gate(raw, one-gate) circuits of cost <= 2."""

    hits: list[dict[str, object]] = []
    for inner in primitives:
        if inner.cost != 1:
            continue
        for leaf in raw:
            a = leaf.signature
            b = inner.signature
            results = (
                ("AND", a & b),
                ("OR", a | b),
                ("NAND", full_mask ^ (a & b)),
                ("NOR", full_mask ^ (a | b)),
            )
            for operation, result in results:
                for target in target_by_signature.get(result, ()):
                    hits.append(
                        {
                            "target": target,
                            "expression": (
                                f"{operation}({leaf.expression},{inner.expression})"
                            ),
                        }
                    )
    return hits


def driver_search(
    primitives: tuple[Signal, ...], target: int
) -> tuple[int, list[dict[str, object]]]:
    """Enumerate every primitive enable/data pair for one Switch driver.

    A driver is usable on a target bus only if it never actively disagrees
    with the target.  It must also become active somewhere; otherwise an
    arbitrary number of such drivers cannot cover target-one points.
    """

    examples: list[dict[str, object]] = []
    count = 0
    for enable in primitives:
        if enable.signature == 0:
            continue
        for data in primitives:
            if enable.signature & (data.signature ^ target):
                continue
            count += 1
            if len(examples) < 8:
                examples.append(
                    {
                        "enable": enable.expression,
                        "data": data.expression,
                        "covered_ones": (enable.signature & target).bit_count(),
                    }
                )
    return count, examples


def subset_counts(primitives: tuple[Signal, ...], target: int, full_mask: int) -> dict[str, int]:
    """Certificate for outer AND/OR/NAND/NOR of two primitive signals."""

    complement = full_mask ^ target

    def proper_subsets(wanted: int) -> int:
        return sum(
            signal.signature not in (0, wanted)
            and not (signal.signature & (full_mask ^ wanted))
            for signal in primitives
        )

    def proper_supersets(wanted: int) -> int:
        return sum(
            signal.signature not in (wanted, full_mask)
            and not (wanted & (full_mask ^ signal.signature))
            for signal in primitives
        )

    return {
        "target_proper_primitive_subsets": proper_subsets(target),
        "target_proper_primitive_supersets": proper_supersets(target),
        "complement_proper_primitive_subsets": proper_subsets(complement),
        "complement_proper_primitive_supersets": proper_supersets(complement),
    }


def audit_care(
    name: str,
    points: tuple[int, ...],
    rows: tuple[int, ...],
    target_prefix: str,
    bad_indices: tuple[int, ...] = (),
) -> dict[str, object]:
    full_mask = (1 << len(points)) - 1
    leaves = signatures(points)
    primitives = primitive_signals(leaves, full_mask)
    raw = tuple(
        Signal(value, f"q[{index}]", 0, 0) for index, value in enumerate(leaves)
    ) + (Signal(0, "0", 0, 0), Signal(full_mask, "1", 0, 0))

    target_signatures = tuple(row_signature(row, leaves) for row in rows)
    target_by_signature: dict[int, list[str]] = {}
    for index, (row, signature) in enumerate(zip(rows, target_signatures)):
        if row.bit_count() >= 2:
            target_by_signature.setdefault(signature, []).append(f"{target_prefix}[{index}]")

    direct_hits = []
    for index, (row, target) in enumerate(zip(rows, target_signatures)):
        if row.bit_count() < 2:
            continue
        for signal in primitives:
            if signal.cost <= 1 and signal.signature == target:
                direct_hits.append(
                    {
                        "target": f"{target_prefix}[{index}]",
                        "row": f"{row:011x}",
                        "expression": signal.expression,
                        "cost": signal.cost,
                    }
                )

    nested_hits = nested_two_gate_hits(
        primitives, raw, target_by_signature, full_mask
    )
    bad = []
    for index in bad_indices:
        row = rows[index]
        target = target_signatures[index]
        driver_count, driver_examples = driver_search(primitives, target)
        bad.append(
            {
                "index": index,
                "row_hex": f"{row:011x}",
                "support": [
                    bit for bit in range(STATE_BITS) if (row >> bit) & 1
                ],
                "support_pattern_counts": support_histogram(row, points),
                "primitive_switch_driver_pairs_checked": (
                    sum(signal.signature != 0 for signal in primitives)
                    * len(primitives)
                ),
                "primitive_switch_driver_count": driver_count,
                "primitive_switch_driver_examples": driver_examples,
                "depth2_three_cheap_gate_outer_filter": subset_counts(
                    primitives, target, full_mask
                ),
            }
        )

    return {
        "name": name,
        "point_count": len(points),
        "point_unique_count": len(set(points)),
        "point_linear_rank": gf2_rank(points),
        "primitive_signal_count": len(primitives),
        "nontrivial_target_count": sum(row.bit_count() >= 2 for row in rows),
        "distinct_nontrivial_target_count": len(
            {row for row in rows if row.bit_count() >= 2}
        ),
        "distinct_nontrivial_target_signature_count": len(
            {
                signature
                for row, signature in zip(rows, target_signatures)
                if row.bit_count() >= 2
            }
        ),
        "wire_or_one_cheap_gate_hits": direct_hits,
        "nested_two_cheap_gate_hits": nested_hits,
        "bad_rows": bad,
    }


def verify_certificate(result: dict[str, object]) -> None:
    feedback = result["care_audits"]["feedback"]
    if feedback["primitive_signal_count"] != 3490:
        raise AssertionError("primitive signal universe changed")
    if feedback["wire_or_one_cheap_gate_hits"]:
        raise AssertionError("unexpected one-gate nontrivial target")
    if feedback["nested_two_cheap_gate_hits"]:
        raise AssertionError("unexpected two-gate nontrivial target")
    for row in feedback["bad_rows"]:
        if row["primitive_switch_driver_count"]:
            raise AssertionError("bad row unexpectedly has a legal Switch driver")
        if any(count == 0 for count in row["support_pattern_counts"]):
            raise AssertionError("bad support is not exhaustive")
        if any(row["depth2_three_cheap_gate_outer_filter"].values()):
            raise AssertionError("bad row unexpectedly passed depth-two outer filter")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("certificate.json"),
    )
    parser.add_argument(
        "--verify-existing",
        type=Path,
        help="recompute the complete audit and compare with an existing certificate",
    )
    args = parser.parse_args()

    frontier_bytes = FRONTIER.read_bytes()
    frontier = json.loads(frontier_bytes)
    h_rows = tuple(int(value, 16) for value in frontier["H_rows_hex"])
    o_rows = tuple(int(value, 16) for value in frontier["O_rows_hex"])
    if len(h_rows) != STATE_BITS or len(o_rows) != 32:
        raise AssertionError("frontier dimensions changed")

    seeds, output_points, feedback_points = build_points(h_rows)
    verify_sequence(h_rows, o_rows, seeds)
    all_targets = o_rows + h_rows
    distinct_nontrivial = {row for row in all_targets if row.bit_count() >= 2}
    intersection_points = output_points[: FEEDBACK_TICKS * LOAD_TESTS]
    intersection_leaves = signatures(intersection_points)
    compatible_h_o = []
    for h_index, h_row in enumerate(h_rows):
        if h_row.bit_count() < 2:
            continue
        h_signature = row_signature(h_row, intersection_leaves)
        for o_index, o_row in enumerate(o_rows):
            if o_row.bit_count() < 2:
                continue
            if h_signature == row_signature(o_row, intersection_leaves):
                compatible_h_o.append([h_index, o_index])
    result = {
        "schema": 1,
        "frontier": {
            "path": str(FRONTIER.relative_to(ROOT)).replace("\\", "/"),
            "sha256": hashlib.sha256(frontier_bytes).hexdigest(),
            "bad_H_rows": [3, 7, 14],
        },
        "protocol": {
            "seed_count": len(seeds),
            "seed_unique_count": len(set(seeds)),
            "outputs_per_seed": OUTPUT_TICKS,
            "feedback_transitions_per_seed": FEEDBACK_TICKS,
            "sequence_verification": "PASS",
        },
        "switch_model": {
            "disabled": "Z",
            "enabled": "actively drives data",
            "all_Z_data_plane": 0,
            "active_0_and_1": "SHORT_CIRCUIT",
            "direct_driver_rule": "enable implies data == target on every care point",
        },
        "linear_accounting": {
            "target_rows": len(all_targets),
            "distinct_nontrivial_targets": len(distinct_nontrivial),
            "recorded_claimed_xor_count": 61,
            "feedback_distinct_nontrivial_functions": 39,
            "output_distinct_nontrivial_functions": 30,
            "feedback_output_compatible_pairs_on_shared_steady_care": compatible_h_o,
            "pure_xor_distinct_final_gate_lower_bound": 69,
            "phase_or": 32,
            "state_delay_bits": 42,
            "ready_delay_plus_not": 6,
            "pure_xor_gate_lower_bound_before_intermediates": (
                42 * 5 + 6 + 32 + 3 * 69
            ),
            "gate_limit": 430,
        },
        "care_audits": {
            "output": audit_care(
                "steady output ticks 0..64", output_points, o_rows, "O"
            ),
            "feedback": audit_care(
                "load plus steady ticks 0..63",
                feedback_points,
                h_rows,
                "H",
                (3, 7, 14),
            ),
        },
        "conclusions": [
            "The recorded 61-XOR accounting is not a realizable linear DAG for these H/O rows: 69 distinct nontrivial final forms already require 69 distinct XOR outputs before pair intermediates.",
            "No nontrivial H/O target equals a wire, one cheap gate, or a nested two-cheap-gate formula on its exact live care set.",
            "Each bad row observes all 32 assignments of its five support leaves, so support-preserving sample specialization cannot change parity-5.",
            "For every bad row, no Switch whose enable and data are raw or one-cheap-gate signals can ever become active while agreeing with the target. Therefore no bus made from such drivers can implement the row.",
            "No bad row is an outer AND/OR/NAND/NOR of two raw-or-one-gate primitive signals; the exact subset/superset filters are empty for both target polarities.",
        ],
    }
    verify_certificate(result)
    if result["care_audits"]["feedback"][
        "distinct_nontrivial_target_signature_count"
    ] != 39:
        raise AssertionError("feedback function count changed")
    if result["care_audits"]["output"][
        "distinct_nontrivial_target_signature_count"
    ] != 30:
        raise AssertionError("output function count changed")
    if compatible_h_o:
        raise AssertionError("an H/O final signal unexpectedly became shareable")

    if args.verify_existing is not None:
        old = json.loads(args.verify_existing.read_text(encoding="utf-8"))
        if old != result:
            raise AssertionError("existing certificate differs from recomputation")
        print(f"verified {args.verify_existing}")
        return

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(
        json.dumps(
            {
                "sequence": "PASS",
                "feedback_points": len(feedback_points),
                "output_points": len(output_points),
                "distinct_nontrivial_targets": len(distinct_nontrivial),
                "pure_xor_gate_lower_bound": result["linear_accounting"][
                    "pure_xor_gate_lower_bound_before_intermediates"
                ],
                "bad_switch_driver_counts": [
                    row["primitive_switch_driver_count"]
                    for row in result["care_audits"]["feedback"]["bad_rows"]
                ],
            },
            indent=2,
        )
    )
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
