"""Emit the deployed RNG dual-mode combinational network as Verilog.

This is a research-only generator.  The Verilog preserves the complete Boolean
extension implemented by the 47 OR plus 61 XOR netlist, so ordinary synthesis
can safely share gates exposed by decomposed XOR implementations without
depending on additional protocol don't-cares.
"""

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


def signal_name(form: int) -> str:
    return f"x_{form:08x}"


def mode_name(seed_bit: int, state_bit: int) -> str:
    return f"m_s{seed_bit}_q{state_bit}"


def mode_source(seed_form: int, state_form: int) -> str:
    if state_form.bit_count() != 1:
        raise ValueError(f"state form is not a unit: {state_form:08x}")
    state_bit = bits(state_form)[0]
    if not seed_form:
        return f"q[{state_bit}]"
    if seed_form.bit_count() != 1:
        raise ValueError(f"seed form is not a unit: {seed_form:08x}")
    return mode_name(bits(seed_form)[0], state_bit)


def emit() -> str:
    lines = [
        "module rng_mode_net(seed, q, feedback, visible);",
        "  input [31:0] seed;",
        "  input [31:0] q;",
        "  output [31:0] feedback;",
        "  output [31:0] visible;",
        "",
    ]

    for seed_bit, state_bit in sorted(MODE_PAIRS):
        name = mode_name(seed_bit, state_bit)
        lines.append(f"  wire {name} = seed[{seed_bit}] | q[{state_bit}];")
    lines.append("")

    for gate in GATES:
        if gate.depth == 1:
            state_support = bits(gate.output)
            seed_support = FIRST_LEAF_SEEDS[gate.output]
            left = mode_source(
                0 if seed_support[0] is None else 1 << seed_support[0],
                1 << state_support[0],
            )
            right = mode_source(
                0 if seed_support[1] is None else 1 << seed_support[1],
                1 << state_support[1],
            )
        else:
            sources: list[str] = []
            for side, fanin in enumerate((gate.left, gate.right)):
                if fanin in FIRST_LAYER:
                    sources.append(signal_name(fanin))
                else:
                    sources.append(
                        mode_source(
                            _seed_form_of_fanin(fanin, gate.output, side),
                            fanin,
                        )
                    )
            left, right = sources
        lines.append(f"  wire {signal_name(gate.output)} = {left} ^ {right};")
    lines.append("")

    for bit, steady_target in enumerate(B):
        if steady_target in GATE_BY_OUTPUT:
            source = signal_name(steady_target)
        else:
            source = mode_source(T[bit], steady_target)
        lines.append(f"  assign feedback[{bit}] = {source};")
    for bit, steady_target in enumerate(C):
        if steady_target in DIRECT:
            source = f"q[{bits(steady_target)[0]}]"
        else:
            source = signal_name(steady_target)
        lines.append(f"  assign visible[{bit}] = {source};")
    lines.append("endmodule")
    return "\n".join(lines) + "\n"


def main() -> None:
    output = ROOT / "rng_mode_net.v"
    output.write_text(emit(), encoding="ascii")
    print(output)


if __name__ == "__main__":
    main()
