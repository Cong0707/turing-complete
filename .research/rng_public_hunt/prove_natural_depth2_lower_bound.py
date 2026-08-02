"""Certify a 216-gate lower bound for the natural two-level RNG core.

The model contains only ordinary XOR2 gates (3 gate / 2 delay) and the
reviewed Switch-based XOR3 macro (12 gate / 2 delay).  First-level gates read
raw input bits; final-level gates read raw bits or first-level results.  Forms
may cancel, so this argument is strictly wider than support partitions.

This script is research-only.  It does not import save writers, start the
game, or access the live save.
"""

from __future__ import annotations

from itertools import combinations
import json
from pathlib import Path


BITS = 32
MASK = (1 << BITS) - 1
XOR2_GATE = 3
XOR3_GATE = 12


def xorshift32(value: int) -> int:
    value ^= value >> 13
    value &= MASK
    value ^= (value << 17) & MASK
    value &= MASK
    value ^= value >> 5
    return value & MASK


def transition_rows() -> tuple[int, ...]:
    columns = tuple(xorshift32(1 << source) for source in range(BITS))
    return tuple(
        sum(((columns[source] >> output) & 1) << source for source in range(BITS))
        for output in range(BITS)
    )


def gf2_rank(rows: tuple[int, ...]) -> int:
    basis: dict[int, int] = {}
    for row in rows:
        value = row
        while value:
            pivot = value.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = value
                break
            value ^= basis[pivot]
    return len(basis)


def main() -> None:
    rows = transition_rows()
    by_weight = {
        weight: tuple(row for row in rows if row.bit_count() == weight)
        for weight in sorted({row.bit_count() for row in rows})
    }
    weight6 = by_weight[6]
    weight7 = by_weight[7]
    assert len(weight6) == 10
    assert gf2_rank(weight6) == 10
    assert len(weight7) == 2
    assert (weight7[0] & weight7[1]).bit_count() == 1

    # k: weight-6 outputs implemented by a final XOR2.  Such an output must
    # XOR two first-level weight-3 forms.  The edge vectors of k independent
    # pairwise differences span at most m-1 dimensions for m forms, hence
    # m >= k+1.  The two weight-7 outputs force two final XOR3 gates and at
    # least two distinct first-level weight-3 forms.
    cases = []
    for k in range(11):
        first_xor3 = max(2, k + 1 if k else 0)
        final_xor3_for_6 = 10 - k
        final_xor3_for_7 = 2
        base_xor3 = first_xor3 + final_xor3_for_6 + final_xor3_for_7

        # Extra XOR3 gates can optimistically replace final XOR2 gates for the
        # 12 weight-4 and 3 weight-5 outputs.  If a weight-5 output still uses
        # XOR2, at least one paid first-level XOR2 pair form is unavoidable.
        #
        # There are also five distinct weight-3 outputs.  At most
        # ``first_xor3`` of them can coincide with an already-paid first-level
        # XOR3 form.  Every remaining output needs its own final gate; charge
        # only the cheapest possible XOR2 cost to keep this a valid lower
        # bound.
        best = None
        for extra_xor3 in range(16):
            xor3 = base_xor3 + extra_xor3
            other_final_xor2 = max(0, 15 - extra_xor3)
            pair_source = int(extra_xor3 < 3)
            weight3_final = max(0, 5 - first_xor3)
            xor2 = k + other_final_xor2 + pair_source + weight3_final
            gate = XOR3_GATE * xor3 + XOR2_GATE * xor2
            item = {
                "weight6_final_xor2": k,
                "first_xor3": first_xor3,
                "weight6_final_xor3": final_xor3_for_6,
                "weight7_final_xor3": final_xor3_for_7,
                "extra_xor3": extra_xor3,
                "weight3_final_gate_lower_bound": weight3_final,
                "xor3_lower_bound": xor3,
                "xor2_lower_bound": xor2,
                "logic_gate_lower_bound": gate,
            }
            if best is None or (gate, xor3, xor2) < (
                best["logic_gate_lower_bound"],
                best["xor3_lower_bound"],
                best["xor2_lower_bound"],
            ):
                best = item
        assert best is not None
        cases.append(best)

    optimum = min(cases, key=lambda item: item["logic_gate_lower_bound"])
    assert optimum["logic_gate_lower_bound"] == 216
    assert 230 + optimum["logic_gate_lower_bound"] == 446

    certificate = {
        "schema": 1,
        "model": "cancellation-capable depth-two XOR2/Switch-XOR3 natural xorshift32",
        "costs": {"xor2": [3, 2], "switch_xor3": [12, 2]},
        "row_weight_counts": {
            str(weight): len(values) for weight, values in by_weight.items()
        },
        "weight6_rows": [f"{row:08x}" for row in weight6],
        "weight6_rank": gf2_rank(weight6),
        "weight7_rows": [f"{row:08x}" for row in weight7],
        "weight7_intersection_size": (weight7[0] & weight7[1]).bit_count(),
        "case_bounds": cases,
        "logic_gate_lower_bound": optimum["logic_gate_lower_bound"],
        "full_rng_gate_lower_bound_with_230_shell": 230
        + optimum["logic_gate_lower_bound"],
        "target_rejected": [431, 9, 66],
    }
    output = Path(__file__).with_name("natural-depth2-lower-bound.json")
    output.write_text(json.dumps(certificate, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(certificate, indent=2))


if __name__ == "__main__":
    main()
