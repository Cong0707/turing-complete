"""Generate a compact Yosys-SAT model for local 42-state repairs.

The generated circuit searches a bitwise Hamming ball around the verified
excess-three semiconjugacy frontier.  It is an independent encoding of the
same equations used by ``linear42_audit/repair_smt.py``.
"""

from __future__ import annotations

import argparse
from pathlib import Path


VISIBLE = 32
HIDDEN = 10
STATES = VISIBLE + HIDDEN
MASK32 = (1 << VISIBLE) - 1

X0 = (
    0x010, 0x122, 0x040, 0x004, 0x008, 0x090, 0x020, 0x040,
    0x108, 0x200, 0x080, 0x044, 0x101, 0x100, 0x200, 0x004,
    0x008, 0x011, 0x022, 0x040, 0x004, 0x008, 0x210, 0x020,
    0x040, 0x100, 0x200, 0x280, 0x000, 0x000, 0x100, 0x200,
)
D0 = (
    0x20040020001, 0x10400004002, 0x00800110008, 0x00100220010,
    0x08200040020, 0x04400080040, 0x00401100080, 0x0A000800400,
    0x20004002000, 0x08008404000,
)


def xorshift32(value: int) -> int:
    value ^= value >> 13
    value ^= (value << 17) & MASK32
    value ^= value >> 5
    return value & MASK32


def transition_rows() -> tuple[int, ...]:
    return tuple(
        sum(((xorshift32(1 << source) >> target) & 1) << source for source in range(VISIBLE))
        for target in range(VISIBLE)
    )


def xor_expr(terms: list[str], width: int) -> str:
    if not terms:
        return f"{width}'h0"
    return " ^ ".join(terms)


def generate(radius: int) -> str:
    a_rows = transition_rows()
    ports = [*(f"input [9:0] dx{i}" for i in range(VISIBLE)),
             *(f"input [41:0] dd{i}" for i in range(HIDDEN)),
             "output valid"]
    lines = ["module repair(", "  " + ",\n  ".join(ports), ");", ""]
    lines += [
        "function [6:0] pop42;",
        "  input [41:0] value; integer k; begin",
        "    pop42 = 0; for (k = 0; k < 42; k = k + 1) pop42 = pop42 + value[k];",
        "  end endfunction",
        "function [3:0] pop10;",
        "  input [9:0] value; integer k; begin",
        "    pop10 = 0; for (k = 0; k < 10; k = k + 1) pop10 = pop10 + value[k];",
        "  end endfunction",
        "",
    ]
    for i, value in enumerate(X0):
        lines.append(f"wire [9:0] x{i} = dx{i} ^ 10'h{value:03x};")
    for i, value in enumerate(D0):
        lines.append(f"wire [41:0] d{i} = dd{i} ^ 42'h{value:011x};")
    lines.append("")
    for i in range(VISIBLE):
        lines.append(f"wire [41:0] o{i} = (42'h1 << {i}) | ({{32'h0, x{i}}} << 32);")
    lines.append("")
    for row, sources in enumerate(a_rows):
        terms = [f"o{i}" for i in range(VISIBLE) if (sources >> i) & 1]
        terms += [f"(d{j} & {{42{{x{row}[{j}]}}}})" for j in range(HIDDEN)]
        lines.append(f"wire [41:0] h{row} = {xor_expr(terms, STATES)};")
    lines.append("")
    valid_terms: list[str] = []
    valid_terms += [f"(pop10(x{i}) <= 3)" for i in range(VISIBLE)]
    valid_terms += [f"(pop42(d{i}) >= 1) && (pop42(d{i}) <= 4)" for i in range(HIDDEN)]
    valid_terms += [f"(pop42(h{i}) <= 4)" for i in range(VISIBLE)]
    changed = [*(f"pop10(dx{i})" for i in range(VISIBLE)),
               *(f"pop42(dd{i})" for i in range(HIDDEN))]
    lines.append("wire [10:0] changed = " + " + ".join(changed) + ";")
    valid_terms.append(f"(changed <= {radius})")
    lines.append("assign valid = " + " &&\n               ".join(valid_terms) + ";")
    lines.append("endmodule")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--radius", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.write_text(generate(args.radius), encoding="ascii")


if __name__ == "__main__":
    main()
