"""Certify cost bounds for the constant-seed RNG with T = I.

This research-only script does not touch the live save or start the game.  It
builds three explicit XOR2 straight-line programs, checks their 64 linear
targets, and emits the delay/gate/energy bounds used by identity_lower_bound.md.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
import random


BITS = 32
MASK = (1 << BITS) - 1
XOR_GATE = 3
XOR_DELAY = 2
DELAY_BIT_GATE = 5
DELAY_BIT_DELAY = 4
CYCLES = 65


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


@dataclass(frozen=True)
class Signal:
    form: int
    q_depth: int | None
    seed_depth: int | None


class Network:
    def __init__(self) -> None:
        self.q = tuple(Signal(1 << bit, 0, None) for bit in range(BITS))
        self.seed = tuple(
            Signal(1 << (BITS + bit), None, 0) for bit in range(BITS)
        )
        self.gates: list[tuple[Signal, Signal, Signal]] = []

    def xor(self, left: Signal, right: Signal) -> Signal:
        def next_depth(a: int | None, b: int | None) -> int | None:
            depths = [depth for depth in (a, b) if depth is not None]
            return max(depths) + 1 if depths else None

        result = Signal(
            left.form ^ right.form,
            next_depth(left.q_depth, right.q_depth),
            next_depth(left.seed_depth, right.seed_depth),
        )
        self.gates.append((result, left, right))
        return result

    def transform(self, inputs: tuple[Signal, ...]) -> tuple[Signal, ...]:
        first = tuple(
            self.xor(inputs[bit], inputs[bit + 13]) if bit < 19 else inputs[bit]
            for bit in range(BITS)
        )
        second = tuple(
            self.xor(first[bit], first[bit - 17]) if bit >= 17 else first[bit]
            for bit in range(BITS)
        )
        return tuple(
            self.xor(second[bit], second[bit + 5]) if bit < 27 else second[bit]
            for bit in range(BITS)
        )

    def balanced_xor(self, leaves: list[Signal]) -> Signal:
        if not leaves:
            raise ValueError("balanced_xor needs at least one leaf")
        level = list(leaves)
        while len(level) > 1:
            following = []
            for index in range(0, len(level) - 1, 2):
                following.append(self.xor(level[index], level[index + 1]))
            if len(level) & 1:
                following.append(level[-1])
            level = following
        return level[0]


def expected_targets() -> tuple[tuple[int, ...], tuple[int, ...]]:
    outputs = tuple(row | (row << BITS) for row in A)
    feedback = tuple(
        row | ((row ^ (1 << bit)) << BITS) for bit, row in enumerate(A)
    )
    return feedback, outputs


def verify_targets(
    name: str, feedback: tuple[Signal, ...], outputs: tuple[Signal, ...]
) -> None:
    expected_feedback, expected_outputs = expected_targets()
    if tuple(signal.form for signal in feedback) != expected_feedback:
        raise AssertionError(f"{name}: feedback forms differ")
    if tuple(signal.form for signal in outputs) != expected_outputs:
        raise AssertionError(f"{name}: output forms differ")


def build_naive() -> tuple[Network, tuple[Signal, ...], tuple[Signal, ...]]:
    network = Network()
    aq = network.transform(network.q)
    aseed = network.transform(network.seed)
    outputs = tuple(network.xor(q, seed) for q, seed in zip(aq, aseed))
    feedback = tuple(
        network.xor(output, seed) for output, seed in zip(outputs, network.seed)
    )
    verify_targets("naive", feedback, outputs)
    return network, feedback, outputs


def build_gate_optimized() -> tuple[Network, tuple[Signal, ...], tuple[Signal, ...]]:
    network = Network()
    paired = tuple(network.xor(q, seed) for q, seed in zip(network.q, network.seed))
    outputs = network.transform(paired)
    feedback = tuple(
        network.xor(output, seed) for output, seed in zip(outputs, network.seed)
    )
    verify_targets("gate-optimized", feedback, outputs)
    return network, feedback, outputs


def build_delay_optimized() -> tuple[Network, tuple[Signal, ...], tuple[Signal, ...]]:
    network = Network()
    paired = tuple(network.xor(q, seed) for q, seed in zip(network.q, network.seed))
    outputs = network.transform(paired)
    feedback = []
    for bit, row in enumerate(A):
        leaves = [network.q[bit]]
        leaves.extend(
            paired[source]
            for source in range(BITS)
            if source != bit and (row >> source) & 1
        )
        feedback.append(network.balanced_xor(leaves))
    result = tuple(feedback)
    verify_targets("delay-optimized", result, outputs)
    return network, result, outputs


def build_q_depth_three() -> tuple[Network, tuple[Signal, ...], tuple[Signal, ...]]:
    """Build every target as an asymmetric q-tree plus a seed-only subtree."""

    network = Network()
    feedback = []
    outputs = []
    for bit, row in enumerate(A):
        support = [source for source in range(BITS) if (row >> source) & 1]

        output_seed = network.balanced_xor([network.seed[source] for source in support])
        outputs.append(
            network.balanced_xor([network.q[source] for source in support] + [output_seed])
        )

        feedback_seed_support = [source for source in support if source != bit]
        feedback_seed = network.balanced_xor(
            [network.seed[source] for source in feedback_seed_support]
        )
        feedback.append(
            network.balanced_xor(
                [network.q[source] for source in support] + [feedback_seed]
            )
        )

    result_feedback = tuple(feedback)
    result_outputs = tuple(outputs)
    verify_targets("q-depth-three", result_feedback, result_outputs)
    return network, result_feedback, result_outputs


def metrics(
    name: str,
    network: Network,
    feedback: tuple[Signal, ...],
    outputs: tuple[Signal, ...],
) -> dict[str, int | str]:
    targets = feedback + outputs
    q_depth = max(signal.q_depth or 0 for signal in targets)
    seed_depth = max(signal.seed_depth or 0 for signal in targets)
    delay = max(
        DELAY_BIT_DELAY + XOR_DELAY * q_depth,
        XOR_DELAY * seed_depth,
    )
    xor_count = len(network.gates)
    gate = BITS * DELAY_BIT_GATE + XOR_GATE * xor_count
    return {
        "name": name,
        "xor": xor_count,
        "gate": gate,
        "q_xor_depth": q_depth,
        "seed_xor_depth": seed_depth,
        "delay": delay,
        "cycles": CYCLES,
        "energy": gate * delay * CYCLES,
    }


def verify_protocol() -> int:
    generator = random.Random(20260801)
    seeds = (0, 1, 2, 0x12345678, MASK) + tuple(
        generator.getrandbits(BITS) for _ in range(64)
    )
    feedback, outputs = expected_targets()
    for seed in seeds:
        q = 0
        natural = seed
        for _ in range(CYCLES):
            combined = q | (seed << BITS)
            visible = sum(
                ((row & combined).bit_count() & 1) << bit
                for bit, row in enumerate(outputs)
            )
            q = sum(
                ((row & combined).bit_count() & 1) << bit
                for bit, row in enumerate(feedback)
            )
            natural = xorshift32(natural)
            if visible != natural or q != (natural ^ seed):
                raise AssertionError(f"protocol mismatch for seed {seed:08x}")
    return len(seeds)


def lower_bound() -> dict[str, object]:
    maximum_row_weight = max(row.bit_count() for row in A)
    witness_bit = next(bit for bit, row in enumerate(A) if row.bit_count() == 7)
    witness = A[witness_bit]

    # Delay <= 11 would allow at most three XOR2 levels after a Delay Bit and
    # at most five XOR2 levels after a zero-delay architecture input.  Unfold
    # any DAG for the witness output into a binary formula.  Seven q leaves and
    # seven seed leaves then exceed the binary Kraft capacity.
    q_levels_at_delay_11 = (11 - DELAY_BIT_DELAY) // XOR_DELAY
    seed_levels_at_delay_11 = 11 // XOR_DELAY
    kraft_numerator = 7 * (1 << (seed_levels_at_delay_11 - q_levels_at_delay_11)) + 7
    kraft_denominator = 1 << seed_levels_at_delay_11
    if kraft_numerator <= kraft_denominator:
        raise AssertionError("Kraft delay lower bound no longer holds")

    feedback, outputs = expected_targets()
    targets = feedback + outputs
    if len(set(targets)) != 64 or any(row.bit_count() <= 1 for row in targets):
        raise AssertionError("64-target gate lower bound no longer holds")
    minimum_xor = 64
    minimum_gate = BITS * DELAY_BIT_GATE + XOR_GATE * minimum_xor
    minimum_delay = 12
    return {
        "maximum_A_row_weight": maximum_row_weight,
        "witness_output_bit": witness_bit,
        "witness_A_row": f"{witness:08x}",
        "witness_q_inputs": witness.bit_count(),
        "witness_seed_inputs": witness.bit_count(),
        "delay_11_q_xor_levels": q_levels_at_delay_11,
        "delay_11_seed_xor_levels": seed_levels_at_delay_11,
        "kraft_load": f"{kraft_numerator}/{kraft_denominator}",
        "minimum_delay": minimum_delay,
        "distinct_nonunit_targets": len(set(targets)),
        "minimum_xor": minimum_xor,
        "minimum_gate": minimum_gate,
        "cycles": CYCLES,
        "minimum_energy": minimum_gate * minimum_delay * CYCLES,
        "leader_energy": 256_014,
        "gap_above_leader": minimum_gate * minimum_delay * CYCLES - 256_014,
        "current_energy": 261_360,
        "gap_above_current": minimum_gate * minimum_delay * CYCLES - 261_360,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    constructions = []
    for name, builder in (
        ("naive-two-A", build_naive),
        ("gate-optimized-p=A-input", build_gate_optimized),
        ("q-depth-three-seed-depth-six", build_q_depth_three),
        ("delay-optimized-balanced-feedback", build_delay_optimized),
    ):
        network, feedback, outputs = builder()
        constructions.append(metrics(name, network, feedback, outputs))

    document = {
        "scope": "T=I, 32 Delay Bits, XOR2-only combinational network",
        "model": {
            "q_initial": 0,
            "feedback": "A*q xor (A+I)*s",
            "output": "A*q xor A*s",
            "cycles": CYCLES,
        },
        "verified_seed_count": verify_protocol(),
        "constructions": constructions,
        "strict_lower_bound": lower_bound(),
        "conclusion": "T=I cannot beat either 261360 current energy or 256014 leader energy",
    }
    encoded = json.dumps(document, indent=2) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="ascii")
    print(encoded, end="")


if __name__ == "__main__":
    main()
