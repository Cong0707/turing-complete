"""Search phase-friendly depth-three XOR DAGs for the no-RAM RNG.

The search is deliberately independent of save files and the game process.
It fixes the natural xorshift32 state and synthesizes the steady-state matrix
with a restricted, reviewable three-level XOR network:

* weight-3/4 outputs are computed at XOR depth at most two;
* weight-5/6 outputs are ``shallow XOR depth-two``;
* the two weight-7 outputs are ``depth-two XOR depth-two``.

The first two rules expose a legal late-OR site for one seed bit without
putting an OR behind three XOR levels.  The weight-7 rows are handled by a
separate phase audit; this file only minimizes the steady XOR DAG.

Every selected depth-one signal is a two-bit XOR.  Every selected depth-two
signal has weight three or four and chooses one exact decomposition into
depth-zero/depth-one signals.  The 32 distinct nontrivial output signals cost
32 XOR gates regardless of their selected decomposition, so the objective is
the number of additional pair and depth-two signals.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import time

import z3


BITS = 32
MASK = (1 << BITS) - 1


def xorshift32(value: int) -> int:
    value ^= value >> 13
    value &= MASK
    value ^= (value << 17) & MASK
    value &= MASK
    value ^= value >> 5
    return value & MASK


def matrix_from_function(function) -> tuple[int, ...]:
    return tuple(
        sum(((function(1 << source) >> output) & 1) << source for source in range(BITS))
        for output in range(BITS)
    )


A = matrix_from_function(xorshift32)
UNITS = frozenset(1 << bit for bit in range(BITS))
PAIRS = frozenset((1 << left) | (1 << right) for left in range(BITS) for right in range(left + 1, BITS))
LOW_OUTPUTS = frozenset(row for row in A if row.bit_count() <= 4)
HEAVY_OUTPUTS = frozenset(row for row in A if row.bit_count() == 7)


def support(mask: int) -> tuple[int, ...]:
    return tuple(bit for bit in range(BITS) if mask >> bit & 1)


def shallow_partitions(mask: int) -> tuple[tuple[int, int], ...]:
    """Return all unordered decompositions into unit/pair shallow signals."""
    candidates = tuple(sorted(UNITS | PAIRS))
    result = []
    for left in candidates:
        right = mask ^ left
        if left < right and right in UNITS | PAIRS:
            result.append((left, right))
    return tuple(result)


def local_output_options(row: int) -> tuple[tuple[int, int], ...]:
    """Return (shallow, depth-two residual) decompositions for weight 5/6."""
    options = []
    for shallow in sorted(UNITS | PAIRS):
        residual = row ^ shallow
        if residual.bit_count() in (3, 4) and shallow_partitions(residual):
            options.append((shallow, residual))
    return tuple(options)


def heavy_output_options(row: int) -> tuple[tuple[int, int], ...]:
    """Return cancellation-free 3+4 partitions for a weight-seven row."""
    bits = support(row)
    result = []
    for a in range(len(bits)):
        for b in range(a + 1, len(bits)):
            for c in range(b + 1, len(bits)):
                left = (1 << bits[a]) | (1 << bits[b]) | (1 << bits[c])
                right = row ^ left
                if left < right:
                    result.append((left, right))
                else:
                    result.append((right, left))
    return tuple(sorted(set(result)))


def selected_bool(model: z3.ModelRef, expression: z3.BoolRef) -> bool:
    return z3.is_true(model.eval(expression, model_completion=True))


def solve(*, intermediate_limit: int, timeout_ms: int, memory_mb: int) -> dict[str, object]:
    z3.set_param("memory_max_size", memory_mb)
    solver = z3.Solver()
    solver.set(timeout=timeout_ms, random_seed=0xD33F)

    output_options: dict[int, tuple[tuple[int, int], ...]] = {}
    for row in A:
        weight = row.bit_count()
        if weight <= 4:
            continue
        output_options[row] = heavy_output_options(row) if weight == 7 else local_output_options(row)
        if not output_options[row]:
            raise AssertionError(f"no output decomposition for {row:08x}")

    depth_two_masks = set(LOW_OUTPUTS)
    for options in output_options.values():
        for left, right in options:
            if left.bit_count() in (3, 4):
                depth_two_masks.add(left)
            if right.bit_count() in (3, 4):
                depth_two_masks.add(right)

    depth_two_partitions = {mask: shallow_partitions(mask) for mask in sorted(depth_two_masks)}
    if any(not options for options in depth_two_partitions.values()):
        raise AssertionError("a depth-two candidate has no shallow decomposition")

    pair_used = {pair: z3.Bool(f"p_{pair:08x}") for pair in sorted(PAIRS)}
    depth_two_used = {
        mask: z3.BoolVal(True) if mask in LOW_OUTPUTS else z3.Bool(f"r_{mask:08x}")
        for mask in sorted(depth_two_masks)
    }
    depth_two_choices = {
        (mask, index): z3.Bool(f"d_{mask:08x}_{index}")
        for mask, options in depth_two_partitions.items()
        for index in range(len(options))
    }
    output_choices = {
        (row, index): z3.Bool(f"o_{row:08x}_{index}")
        for row, options in output_options.items()
        for index in range(len(options))
    }

    pair_consumers: dict[int, list[z3.BoolRef]] = defaultdict(list)
    residual_consumers: dict[int, list[z3.BoolRef]] = defaultdict(list)

    for mask, options in depth_two_partitions.items():
        choices = [depth_two_choices[(mask, index)] for index in range(len(options))]
        used = depth_two_used[mask]
        solver.add(z3.PbEq([(choice, 1) for choice in choices], 1) if mask in LOW_OUTPUTS else z3.PbEq([(choice, 1) for choice in choices] + [(used, -1)], 0))
        for index, (left, right) in enumerate(options):
            choice = depth_two_choices[(mask, index)]
            for signal in (left, right):
                if signal in PAIRS:
                    solver.add(z3.Implies(choice, pair_used[signal]))
                    pair_consumers[signal].append(choice)

    for row, options in output_options.items():
        choices = [output_choices[(row, index)] for index in range(len(options))]
        solver.add(z3.PbEq([(choice, 1) for choice in choices], 1))
        for index, (left, right) in enumerate(options):
            choice = output_choices[(row, index)]
            for signal in (left, right):
                if signal in PAIRS:
                    solver.add(z3.Implies(choice, pair_used[signal]))
                    pair_consumers[signal].append(choice)
                elif signal in depth_two_used:
                    solver.add(z3.Implies(choice, depth_two_used[signal]))
                    if signal not in LOW_OUTPUTS:
                        residual_consumers[signal].append(choice)

    for pair, used in pair_used.items():
        consumers = pair_consumers.get(pair, [])
        solver.add(used == (z3.Or(consumers) if consumers else z3.BoolVal(False)))
    for mask, used in depth_two_used.items():
        if mask in LOW_OUTPUTS:
            continue
        consumers = residual_consumers.get(mask, [])
        solver.add(used == (z3.Or(consumers) if consumers else z3.BoolVal(False)))

    selected_pairs = z3.Sum([z3.If(value, 1, 0) for value in pair_used.values()])
    selected_residuals = z3.Sum(
        [z3.If(value, 1, 0) for mask, value in depth_two_used.items() if mask not in LOW_OUTPUTS]
    )
    solver.add(selected_pairs + selected_residuals <= intermediate_limit)

    started = time.perf_counter()
    status = solver.check()
    elapsed = time.perf_counter() - started
    base = {
        "schema": 1,
        "model": "natural-state phase-friendly depth-three XOR DAG",
        "status": str(status),
        "intermediate_limit": intermediate_limit,
        "elapsed_seconds": round(elapsed, 6),
        "matrix_sha256": hashlib.sha256(b"".join(row.to_bytes(4, "little") for row in A)).hexdigest(),
        "candidate_counts": {
            "pairs": len(pair_used),
            "depth_two": len(depth_two_used),
            "nonlow_outputs": len(output_options),
            "output_options": sum(len(options) for options in output_options.values()),
        },
    }
    if status != z3.sat:
        if status == z3.unknown:
            base["reason_unknown"] = solver.reason_unknown()
        return base

    model = solver.model()
    chosen_pairs = tuple(sorted(pair for pair, value in pair_used.items() if selected_bool(model, value)))
    chosen_residuals = tuple(
        sorted(mask for mask, value in depth_two_used.items() if mask not in LOW_OUTPUTS and selected_bool(model, value))
    )
    decompositions = {}
    for mask, options in depth_two_partitions.items():
        if mask not in LOW_OUTPUTS and mask not in chosen_residuals:
            continue
        indexes = [index for index in range(len(options)) if selected_bool(model, depth_two_choices[(mask, index)])]
        if len(indexes) != 1:
            raise AssertionError(f"depth-two decomposition is not one-hot for {mask:08x}")
        decompositions[f"{mask:08x}"] = [f"{value:08x}" for value in options[indexes[0]]]
    outputs = {}
    for row, options in output_options.items():
        indexes = [index for index in range(len(options)) if selected_bool(model, output_choices[(row, index)])]
        if len(indexes) != 1:
            raise AssertionError(f"output decomposition is not one-hot for {row:08x}")
        outputs[f"{row:08x}"] = [f"{value:08x}" for value in options[indexes[0]]]

    xor_count = 32 + len(chosen_pairs) + len(chosen_residuals)
    base.update(
        {
            "selected_pair_count": len(chosen_pairs),
            "selected_residual_count": len(chosen_residuals),
            "intermediate_count": len(chosen_pairs) + len(chosen_residuals),
            "xor_count": xor_count,
            "selected_pairs": [f"{value:08x}" for value in chosen_pairs],
            "depth_two_decompositions": decompositions,
            "output_decompositions": outputs,
            "low_outputs": [f"{value:08x}" for value in sorted(LOW_OUTPUTS)],
            "heavy_outputs": [f"{value:08x}" for value in sorted(HEAVY_OUTPUTS)],
        }
    )
    return base


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--intermediate-limit", type=int, default=29)
    parser.add_argument("--timeout-ms", type=int, default=300_000)
    parser.add_argument("--memory-mb", type=int, default=700)
    args = parser.parse_args()
    result = solve(
        intermediate_limit=args.intermediate_limit,
        timeout_ms=args.timeout_ms,
        memory_mb=args.memory_mb,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key not in {"selected_pairs", "depth_two_decompositions", "output_decompositions"}}, indent=2))
    return 0 if result["status"] == "sat" else 2


if __name__ == "__main__":
    raise SystemExit(main())
