#!/usr/bin/env python3
"""RETRACTED: audit a fixed local RNG sample, not the server seed space.

Do not use this script for a leaderboard candidate.  The server regenerates
random 32-bit seeds, so the captured 256-seed care set is not the test domain.
See ``RETRACTED.md`` and ``full_space_linear_audit.py``.

The script is deliberately offline.  It reconstructs the exact 256 seeds used
by the current level, replays all 65 required outputs, studies abstract DFA
state bounds, and searches how many retained encoded-state coordinates are
needed to determine any deleted coordinate on the finite care set.

It never reads or writes the player save and never starts the game.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import struct
import sys
from typing import Iterable, Sequence


HERE = Path(__file__).resolve().parent
ROOT = next(parent for parent in HERE.parents if (parent / "pyproject.toml").exists())
sys.path.insert(0, str(ROOT))

from src.tc_save_lab.rng_encoded_asic import T, apply_matrix, xorshift32  # noqa: E402


MASK32 = (1 << 32) - 1
MASK64 = (1 << 64) - 1
TEST_COUNT = 256
OUTPUTS_PER_TEST = 65
SCRIPT_RANDOM_MODULUS = 0xFFFFFFFE
XORSHIFT64_STAR_MULTIPLIER = 0x2545F4914F6CDD1
EXPECTED_SEED_VECTOR_SHA256 = (
    "d8ef931e5eb213217aa4faedc43783f0875e52607f991e89080c6046aad1e24b"
)


def xorshift64_star(value: int) -> int:
    value &= MASK64
    value ^= (value << 12) & MASK64
    value ^= value >> 25
    value ^= value >> 27
    return (value * XORSHIFT64_STAR_MULTIPLIER) & MASK64


def initial_seed(test_id: int) -> int:
    if not 0 <= test_id < TEST_COUNT:
        raise ValueError("test_id must be in 0..255")
    return 1 + xorshift64_star(test_id + 1) % SCRIPT_RANDOM_MODULUS


def bit_vector_sha256(values: Iterable[int]) -> str:
    payload = b"".join(struct.pack("<I", value & MASK32) for value in values)
    return sha256(payload).hexdigest()


@dataclass(frozen=True)
class Sample:
    test_id: int
    offset: int
    seed: int
    state: int
    output: int
    encoded_state: int


def build_samples() -> tuple[tuple[int, ...], tuple[Sample, ...]]:
    seeds = tuple(initial_seed(test_id) for test_id in range(TEST_COUNT))
    digest = bit_vector_sha256(seeds)
    if digest != EXPECTED_SEED_VECTOR_SHA256:
        raise RuntimeError(f"seed vector changed: {digest}")

    samples: list[Sample] = []
    for test_id, seed in enumerate(seeds):
        state = seed
        for offset in range(OUTPUTS_PER_TEST):
            output = xorshift32(state)
            samples.append(
                Sample(
                    test_id=test_id,
                    offset=offset,
                    seed=seed,
                    state=state,
                    output=output,
                    encoded_state=apply_matrix(T, state),
                )
            )
            state = output

    if len(samples) != TEST_COUNT * OUTPUTS_PER_TEST:
        raise AssertionError("sample count changed")
    if len({sample.state for sample in samples}) != len(samples):
        raise AssertionError("natural-state trajectories unexpectedly collide")
    if len({sample.output for sample in samples}) != len(samples):
        raise AssertionError("required output values unexpectedly collide")
    if len({sample.encoded_state for sample in samples}) != len(samples):
        raise AssertionError("encoded-state trajectories unexpectedly collide")
    return seeds, tuple(samples)


def gf2_rank(values: Sequence[int], width: int) -> int:
    basis = [0] * width
    rank = 0
    for original in values:
        value = original & ((1 << width) - 1)
        while value:
            pivot = value.bit_length() - 1
            if basis[pivot]:
                value ^= basis[pivot]
            else:
                basis[pivot] = value
                rank += 1
                break
    return rank


def ceil_log2(value: int) -> int:
    if value <= 0:
        raise ValueError("ceil_log2 requires a positive value")
    return (value - 1).bit_length()


def dfa_summary(samples: Sequence[Sample]) -> dict[str, object]:
    # With input disabled after load, current output alone distinguishes every
    # live state because all 16,640 required words are unique.
    closed_input_states = len({sample.output for sample in samples})

    # If the unchanged seed remains externally visible, states from different
    # tests may share a code.  For one fixed seed the 65 output positions are
    # still pairwise distinct, and the common offset code realizes this bound.
    per_seed_position_counts = {
        sample.test_id: len(
            {row.output for row in samples if row.test_id == sample.test_id}
        )
        for sample in samples[::OUTPUTS_PER_TEST]
    }
    persistent_seed_states = max(per_seed_position_counts.values())
    if set(per_seed_position_counts.values()) != {OUTPUTS_PER_TEST}:
        raise AssertionError("a test trajectory contains repeated required outputs")

    return {
        "input_disabled_after_load": {
            "pairwise_distinct_required_output_states": closed_input_states,
            "minimum_data_state_bits": ceil_log2(closed_input_states),
            "reason": "every live state has a different immediate 32-bit output",
        },
        "persistent_seed_as_external_side_information": {
            "minimum_position_classes": persistent_seed_states,
            "minimum_data_state_bits": ceil_log2(persistent_seed_states),
            "realizing_abstract_encoding": "shared offset 0..64 for every seed",
            "boundary": (
                "the 7-bit state bound ignores the gate and delay cost of decoding "
                "A^(offset+1)*seed"
            ),
        },
    }


def conflict_differences(
    values: Sequence[int], target_bit: int, selected_mask: int
) -> set[int]:
    """Return separating clauses for every mixed projected bucket.

    One lazy-SAT proposal can expose thousands of mixed buckets.  Adding all
    of them at once is substantially faster than the textbook one-CEGIS-row
    loop while retaining exactly the same proof argument.
    """

    seen: dict[int, list[int | None]] = {}
    differences: set[int] = set()
    for value in values:
        key = value & selected_mask
        label = (value >> target_bit) & 1
        representatives = seen.setdefault(key, [None, None])
        opposite = representatives[label ^ 1]
        if opposite is not None:
            difference = (opposite ^ value) & ~(1 << target_bit)
            if difference == 0:
                raise AssertionError("opposite labels have identical available bits")
            differences.add(difference)
        if representatives[label] is None:
            representatives[label] = value
    return differences


def labeled_conflict_differences(
    points: Sequence[tuple[int, int]], selected_mask: int
) -> set[int]:
    seen: dict[int, list[int | None]] = {}
    differences: set[int] = set()
    for value, label in points:
        key = value & selected_mask
        representatives = seen.setdefault(key, [None, None])
        opposite = representatives[label ^ 1]
        if opposite is not None:
            difference = opposite ^ value
            if difference == 0:
                raise AssertionError("opposite labels have identical features")
            differences.add(difference)
        if representatives[label] is None:
            representatives[label] = value
    return differences


def minimum_coordinate_support(
    values: Sequence[int], target_bit: int
) -> dict[str, object]:
    """Find an exact minimum retained-coordinate support with lazy SAT.

    A selected feature set determines the deleted target bit iff it intersects
    the XOR difference of every care-point pair having opposite target labels.
    Rather than materializing about 69 million pair clauses, the solver proposes
    a feature set and the verifier adds one exact separating clause per observed
    collision.  UNSAT at cardinality k is therefore a proof for all supports of
    size at most k, not a heuristic sample.
    """

    from pysat.card import CardEnc, EncType
    from pysat.formula import IDPool
    from pysat.solvers import Solver

    available = tuple(bit for bit in range(32) if bit != target_bit)
    variable_for_bit = {bit: index + 1 for index, bit in enumerate(available)}
    discovered: set[int] = set()
    solver_calls = 0
    proposals = 0

    for bound in range(len(available) + 1):
        pool = IDPool(start_from=len(available) + 1)
        cardinality = CardEnc.atmost(
            lits=list(variable_for_bit.values()),
            bound=bound,
            vpool=pool,
            encoding=EncType.seqcounter,
        )
        with Solver(name="cadical195", bootstrap_with=cardinality.clauses) as solver:
            for difference in discovered:
                solver.add_clause(
                    [
                        variable_for_bit[bit]
                        for bit in available
                        if (difference >> bit) & 1
                    ]
                )
            while True:
                solver_calls += 1
                if not solver.solve():
                    break
                model = set(literal for literal in solver.get_model() if literal > 0)
                selected = tuple(
                    bit for bit in available if variable_for_bit[bit] in model
                )
                selected_mask = sum(1 << bit for bit in selected)
                proposals += 1
                conflicts = conflict_differences(values, target_bit, selected_mask)
                if not conflicts:
                    return {
                        "target_bit": target_bit,
                        "minimum_support_size": len(selected),
                        "support_bits": list(selected),
                        "support_mask_hex": f"{selected_mask:08x}",
                        "lazy_conflict_clauses": len(discovered),
                        "solver_calls": solver_calls,
                        "verified_care_points": len(values),
                        "status": "exact-minimum",
                    }
                new_conflicts = conflicts - discovered
                if not new_conflicts:
                    raise AssertionError("solver repeated already-blocked conflicts")
                for difference in new_conflicts:
                    discovered.add(difference)
                    solver.add_clause(
                        [
                            variable_for_bit[bit]
                            for bit in available
                            if (difference >> bit) & 1
                        ]
                    )

    raise AssertionError("all 31 remaining coordinates must determine the target")


def minimum_counter_output_support(
    samples: Sequence[Sample], output_bit: int
) -> dict[str, object]:
    """Exact raw-coordinate support of one 7-bit-offset decoder output."""

    from pysat.card import CardEnc, EncType
    from pysat.formula import IDPool
    from pysat.solvers import Solver

    width = 39
    points = tuple(
        (
            sample.seed | (sample.offset << 32),
            (sample.output >> output_bit) & 1,
        )
        for sample in samples
    )
    variables = tuple(range(1, width + 1))
    discovered: set[int] = set()
    solver_calls = 0

    for bound in range(width + 1):
        pool = IDPool(start_from=width + 1)
        cardinality = CardEnc.atmost(
            lits=list(variables),
            bound=bound,
            vpool=pool,
            encoding=EncType.seqcounter,
        )
        with Solver(name="cadical195", bootstrap_with=cardinality.clauses) as solver:
            for difference in discovered:
                solver.add_clause(
                    [bit + 1 for bit in range(width) if (difference >> bit) & 1]
                )
            while True:
                solver_calls += 1
                if not solver.solve():
                    break
                model = set(literal for literal in solver.get_model() if literal > 0)
                selected = tuple(bit for bit in range(width) if bit + 1 in model)
                selected_mask = sum(1 << bit for bit in selected)
                conflicts = labeled_conflict_differences(points, selected_mask)
                if not conflicts:
                    return {
                        "output_bit": output_bit,
                        "minimum_support_size": len(selected),
                        "seed_support_bits": [bit for bit in selected if bit < 32],
                        "counter_support_bits": [bit - 32 for bit in selected if bit >= 32],
                        "support_mask_hex": f"{selected_mask:010x}",
                        "lazy_conflict_clauses": len(discovered),
                        "solver_calls": solver_calls,
                        "verified_care_points": len(points),
                        "status": "exact-minimum",
                    }
                new_conflicts = conflicts - discovered
                if not new_conflicts:
                    raise AssertionError("solver repeated counter-decoder conflicts")
                for difference in new_conflicts:
                    discovered.add(difference)
                    solver.add_clause(
                        [bit + 1 for bit in range(width) if (difference >> bit) & 1]
                    )
    raise AssertionError("all 39 features must determine a cared output")


def emit_counter_output_pla(
    path: Path, seeds: Sequence[int], samples: Sequence[Sample]
) -> dict[str, object]:
    """Emit the exact 32-seed-bit + 7-offset-bit visible-output care set."""

    lines = [
        ".i 39",
        ".o 32",
        ".ilb "
        + " ".join([*(f"s{bit}" for bit in range(32)), *(f"c{bit}" for bit in range(7))]),
        ".ob " + " ".join(f"v{bit}" for bit in range(32)),
        ".type fr",
    ]
    for sample in samples:
        input_value = sample.seed | (sample.offset << 32)
        input_bits = "".join(
            "1" if (input_value >> bit) & 1 else "0" for bit in range(39)
        )
        output_bits = "".join(
            "1" if (sample.output >> bit) & 1 else "0" for bit in range(32)
        )
        lines.append(f"{input_bits} {output_bits}")
    lines.append(".e")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="ascii")
    return {
        "path": str(path),
        "input_bits": 39,
        "output_bits": 32,
        "care_rows": len(samples),
        "sha256": sha256(path.read_bytes()).hexdigest(),
    }


def emit_counter_bit_pla(
    path: Path, samples: Sequence[Sample], output_bit: int
) -> dict[str, object]:
    if not 0 <= output_bit < 32:
        raise ValueError("output_bit must be in 0..31")
    lines = [
        ".i 39",
        ".o 1",
        ".ilb "
        + " ".join([*(f"s{bit}" for bit in range(32)), *(f"c{bit}" for bit in range(7))]),
        f".ob v{output_bit}",
        ".type fr",
    ]
    for sample in samples:
        input_value = sample.seed | (sample.offset << 32)
        input_bits = "".join(
            "1" if (input_value >> bit) & 1 else "0" for bit in range(39)
        )
        lines.append(f"{input_bits} {(sample.output >> output_bit) & 1}")
    lines.append(".e")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="ascii")
    return {
        "path": str(path),
        "input_bits": 39,
        "output_bits": 1,
        "care_rows": len(samples),
        "output_bit": output_bit,
        "sha256": sha256(path.read_bytes()).hexdigest(),
    }


def emit_deleted_state_bit_pla(
    path: Path, encoded_values: Sequence[int], target_bit: int
) -> dict[str, object]:
    available = tuple(bit for bit in range(32) if bit != target_bit)
    lines = [
        f".i {len(available)}",
        ".o 1",
        ".ilb " + " ".join(f"q{bit}" for bit in available),
        f".ob q{target_bit}",
        ".type fr",
    ]
    for value in encoded_values:
        input_bits = "".join("1" if (value >> bit) & 1 else "0" for bit in available)
        lines.append(f"{input_bits} {(value >> target_bit) & 1}")
    lines.append(".e")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="ascii")
    return {
        "path": str(path),
        "input_bits": len(available),
        "output_bits": 1,
        "care_rows": len(encoded_values),
        "target_bit": target_bit,
        "sha256": sha256(path.read_bytes()).hexdigest(),
    }


def parse_bit_selection(text: str) -> tuple[int, ...]:
    if text == "all":
        return tuple(range(32))
    result = tuple(sorted({int(field) for field in text.split(",") if field.strip()}))
    if not result or any(bit < 0 or bit >= 32 for bit in result):
        raise argparse.ArgumentTypeError("bits must be 'all' or comma-separated 0..31")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=HERE / "certificate.json")
    parser.add_argument("--pla", type=Path, default=HERE / "counter_output_care.pla")
    parser.add_argument(
        "--single-pla", type=Path, default=HERE / "counter_output_v0_care.pla"
    )
    parser.add_argument(
        "--deleted-bit-pla",
        type=Path,
        default=HERE / "deleted_state_q17_care.pla",
    )
    parser.add_argument(
        "--support-bits",
        type=parse_bit_selection,
        default=(),
        help="exact deleted-coordinate searches: all, or comma-separated bit indices",
    )
    parser.add_argument(
        "--counter-support-bits",
        type=parse_bit_selection,
        default=(),
        help="exact raw-coordinate support searches for decoder outputs 0..31",
    )
    args = parser.parse_args()

    seeds, samples = build_samples()
    encoded_values = tuple([0, *(sample.encoded_state for sample in samples)])
    if len(set(encoded_values)) != len(encoded_values):
        raise AssertionError("zero/load plus steady encoded care points collide")

    support_results = [
        minimum_coordinate_support(encoded_values, bit) for bit in args.support_bits
    ]
    certificate = {
        "schema": 1,
        "scope": "legal finite-care RNG state and decoder audit; no save/game access",
        "runtime_contract": {
            "tests": TEST_COUNT,
            "outputs_per_test": OUTPUTS_PER_TEST,
            "seed_vector_sha256": bit_vector_sha256(seeds),
            "first_seeds_hex": [f"{seed:08x}" for seed in seeds[:8]],
        },
        "care": {
            "required_output_points": len(samples),
            "unique_natural_states": len({sample.state for sample in samples}),
            "unique_required_outputs": len({sample.output for sample in samples}),
            "unique_encoded_states": len({sample.encoded_state for sample in samples}),
            "encoded_state_rank": gf2_rank(
                [sample.encoded_state for sample in samples], 32
            ),
            "output_stream_sha256": bit_vector_sha256(
                [sample.output for sample in samples]
            ),
        },
        "dfa": dfa_summary(samples),
        "deleted_coordinate_support": support_results,
        "counter_output_coordinate_support": [
            minimum_counter_output_support(samples, bit)
            for bit in args.counter_support_bits
        ],
        "counter_output_pla": emit_counter_output_pla(args.pla, seeds, samples),
        "counter_output_bit0_pla": emit_counter_bit_pla(args.single_pla, samples, 0),
        "deleted_state_bit17_pla": emit_deleted_state_bit_pla(
            args.deleted_bit_pla, encoded_values, 17
        ),
        "component_cost_boundary": {
            "delay_bit": {"gate": 5, "delay": 4},
            "ordinary_or_u1_xor": {"gate": 3, "delay": 2},
            "cheap_boolean_gate": {"gate": 1, "delay": 1},
            "seven_delay_bits_gate_floor": 35,
            "warning": (
                "DFA state-bit bounds are not score bounds; the shared output decoder "
                "and counter transition must fit the remaining real gate/delay budget"
            ),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(certificate, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(certificate, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
