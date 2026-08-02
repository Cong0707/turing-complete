"""Emit the RNG dual-mode network with its protocol external don't-care set."""

from __future__ import annotations

from pathlib import Path

from tc_save_lab.rng_encoded_asic import (
    B,
    C,
    DIRECT,
    FIRST_LAYER,
    FIRST_LEAF_SEEDS,
    GATES,
    GATE_BY_OUTPUT,
    MODE_PAIRS,
    T,
    _seed_form_of_fanin,
    bits,
)


ROOT = Path(__file__).resolve().parent


def xname(form: int) -> str:
    return f"x{form:08x}"


def mname(seed_bit: int, state_bit: int) -> str:
    return f"m_s{seed_bit}_q{state_bit}"


def source(seed_form: int, state_form: int) -> str:
    state_bit = bits(state_form)[0]
    if not seed_form:
        return f"q{state_bit}"
    return mname(bits(seed_form)[0], state_bit)


def or_gate(left: str, right: str, output: str) -> list[str]:
    return [f".names {left} {right} {output}", "1- 1", "-1 1"]


def xor_gate(left: str, right: str, output: str) -> list[str]:
    return [f".names {left} {right} {output}", "10 1", "01 1"]


def alias(input_name: str, output_name: str) -> list[str]:
    return [f".names {input_name} {output_name}", "1 1"]


def emit() -> str:
    inputs = [*(f"s{i}" for i in range(32)), *(f"q{i}" for i in range(32))]
    outputs = [*(f"f{i}" for i in range(32)), *(f"v{i}" for i in range(32))]
    lines = [
        ".model rng_mode_net",
        ".inputs " + " ".join(inputs),
        ".outputs " + " ".join(outputs),
    ]

    for seed_bit, state_bit in sorted(MODE_PAIRS):
        lines.extend(or_gate(f"s{seed_bit}", f"q{state_bit}", mname(seed_bit, state_bit)))

    for gate in GATES:
        if gate.depth == 1:
            state_support = bits(gate.output)
            seed_support = FIRST_LEAF_SEEDS[gate.output]
            left = source(
                0 if seed_support[0] is None else 1 << seed_support[0],
                1 << state_support[0],
            )
            right = source(
                0 if seed_support[1] is None else 1 << seed_support[1],
                1 << state_support[1],
            )
        else:
            fanins: list[str] = []
            for side, fanin in enumerate((gate.left, gate.right)):
                if fanin in FIRST_LAYER:
                    fanins.append(xname(fanin))
                else:
                    fanins.append(source(_seed_form_of_fanin(fanin, gate.output, side), fanin))
            left, right = fanins
        lines.extend(xor_gate(left, right, xname(gate.output)))

    for bit, target in enumerate(B):
        value = xname(target) if target in GATE_BY_OUTPUT else source(T[bit], target)
        lines.extend(alias(value, f"f{bit}"))
    for bit, target in enumerate(C):
        value = f"q{bits(target)[0]}" if target in DIRECT else xname(target)
        lines.extend(alias(value, f"v{bit}"))

    # Both protocol phases are cared for: load has q=0, steady state has s=0.
    # States with at least one seed bit and one state bit set are unreachable.
    lines.extend([".exdc", ".inputs " + " ".join(inputs), ".outputs " + " ".join(outputs)])
    seed_pattern = ["-"] * 32
    lines.append(".names " + " ".join(f"s{i}" for i in range(32)) + " seed_nonzero")
    for index in range(32):
        pattern = seed_pattern.copy()
        pattern[index] = "1"
        lines.append("".join(pattern) + " 1")
    lines.append(".names " + " ".join(f"q{i}" for i in range(32)) + " state_nonzero")
    for index in range(32):
        pattern = seed_pattern.copy()
        pattern[index] = "1"
        lines.append("".join(pattern) + " 1")
    lines.extend([".names seed_nonzero state_nonzero mixed", "11 1"])
    for output in outputs:
        lines.extend(alias("mixed", output))
    lines.append(".end")
    return "\n".join(lines) + "\n"


def main() -> None:
    output = ROOT / "rng_mode_net_exdc.blif"
    output.write_text(emit(), encoding="ascii")
    print(output)


if __name__ == "__main__":
    main()
