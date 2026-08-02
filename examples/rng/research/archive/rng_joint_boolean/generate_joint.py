"""Generate and audit joint Boolean forms for the encoded RNG network.

This research-only script imports the checked certificate from
``rng_encoded_asic`` and emits a combinational BLIF network.  Primary inputs
are the architecture seed pins ``s*`` and encoded state delay outputs ``q*``.
The generated full extension exactly matches the current 47-OR/61-XOR
implementation for all 64-input assignments; protocol equivalence is checked
separately on the two legal modes.
"""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
import random
import sys


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from tc_save_lab.rng_encoded_asic import (  # noqa: E402
    B,
    C,
    DIRECT,
    FIRST_LAYER,
    FIRST_LEAF_SEEDS,
    GATES,
    GATE_BY_OUTPUT,
    T,
    WORD_BITS,
    _seed_form_of_fanin,
    apply_matrix,
)


def _bits(value: int) -> tuple[int, ...]:
    return tuple(index for index in range(WORD_BITS) if value >> index & 1)


def _mode_name(seed_form: int, state_form: int) -> str:
    state = _bits(state_form)
    if len(state) != 1:
        raise AssertionError(f"state leaf is not a bit: {state_form:08x}")
    if not seed_form:
        return f"q{state[0]}"
    seed = _bits(seed_form)
    if len(seed) != 1:
        raise AssertionError(f"seed leaf is not a bit: {seed_form:08x}")
    return f"m_s{seed[0]}_q{state[0]}"


def build_full_extension() -> tuple[list[tuple[str, str, str, str]], list[str], list[str]]:
    """Return gates plus feedback/output signal names for the current network."""

    gates: list[tuple[str, str, str, str]] = []
    mode_names: dict[tuple[int, int], str] = {}

    def mode(seed_form: int, state_form: int) -> str:
        name = _mode_name(seed_form, state_form)
        if seed_form and name not in mode_names.values():
            seed_bit = _bits(seed_form)[0]
            state_bit = _bits(state_form)[0]
            gates.append(("OR", name, f"s{seed_bit}", f"q{state_bit}"))
            mode_names[(seed_bit, state_bit)] = name
        return name

    signals: dict[int, str] = {1 << bit: f"q{bit}" for bit in range(WORD_BITS)}
    for gate in GATES:
        if gate.depth == 1:
            state = _bits(gate.output)
            seeds = FIRST_LEAF_SEEDS[gate.output]
            left = mode(0 if seeds[0] is None else 1 << seeds[0], 1 << state[0])
            right = mode(0 if seeds[1] is None else 1 << seeds[1], 1 << state[1])
        else:
            fanins: list[str] = []
            for side, fanin in enumerate((gate.left, gate.right)):
                if fanin in FIRST_LAYER:
                    fanins.append(signals[fanin])
                else:
                    fanins.append(mode(_seed_form_of_fanin(fanin, gate.output, side), fanin))
            left, right = fanins
        output = f"x_{gate.output:08x}"
        gates.append(("XOR", output, left, right))
        signals[gate.output] = output

    feedback: list[str] = []
    for bit, target in enumerate(B):
        if target in GATE_BY_OUTPUT:
            feedback.append(signals[target])
        else:
            feedback.append(mode(T[bit], target))
    outputs = [signals[target] for target in C]

    counts = Counter(kind for kind, *_ in gates)
    if counts != {"OR": 47, "XOR": 61}:
        raise AssertionError(f"unexpected source counts: {counts}")
    return gates, feedback, outputs


def write_blif(path: Path) -> None:
    gates, feedback, outputs = build_full_extension()
    lines = [
        ".model rng_joint_full",
        ".inputs " + " ".join([*(f"s{i}" for i in range(WORD_BITS)), *(f"q{i}" for i in range(WORD_BITS))]),
        ".outputs " + " ".join([*(f"fb{i}" for i in range(WORD_BITS)), *(f"out{i}" for i in range(WORD_BITS))]),
    ]
    for kind, output, left, right in gates:
        lines.append(f".names {left} {right} {output}")
        if kind == "OR":
            lines.extend(("1- 1", "-1 1"))
        elif kind == "XOR":
            lines.extend(("10 1", "01 1"))
        else:
            raise AssertionError(kind)
    for index, signal in enumerate(feedback):
        lines.extend((f".names {signal} fb{index}", "1 1"))
    for index, signal in enumerate(outputs):
        lines.extend((f".names {signal} out{index}", "1 1"))
    lines.append(".end")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="ascii")


def _evaluate_source(seed: int, state: int) -> tuple[int, int]:
    gates, feedback, outputs = build_full_extension()
    values = {f"s{i}": seed >> i & 1 for i in range(WORD_BITS)}
    values.update({f"q{i}": state >> i & 1 for i in range(WORD_BITS)})
    for kind, output, left, right in gates:
        a, b = values[left], values[right]
        values[output] = a | b if kind == "OR" else a ^ b
    fb = sum(values[signal] << bit for bit, signal in enumerate(feedback))
    out = sum(values[signal] << bit for bit, signal in enumerate(outputs))
    return fb, out


def verify_source() -> None:
    rng = random.Random(0x20260802)
    vectors = [0, 1, 2, 0xFFFFFFFF, 0x12345678]
    vectors.extend(rng.getrandbits(32) for _ in range(1000))
    for value in vectors:
        load_fb, _ = _evaluate_source(value, 0)
        if load_fb != apply_matrix(T, value):
            raise AssertionError(f"load mismatch {value:08x}: {load_fb:08x}")
        steady_fb, steady_out = _evaluate_source(0, value)
        if steady_fb != apply_matrix(B, value):
            raise AssertionError(f"steady B mismatch {value:08x}: {steady_fb:08x}")
        if steady_out != apply_matrix(C, value):
            raise AssertionError(f"steady C mismatch {value:08x}: {steady_out:08x}")
    print(f"source protocol verification: {len(vectors)} load + steady vectors passed")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--blif", type=Path, default=Path(__file__).with_name("rng_joint_full.blif"))
    args = parser.parse_args()
    verify_source()
    write_blif(args.blif)
    print(f"wrote {args.blif}")


if __name__ == "__main__":
    main()
