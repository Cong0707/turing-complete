"""Audit low-nibble state sharing with a factored C4 boundary.

The 32-gate core uses the fast 19-gate bits0:1 prefix, then lets N2 own both
S2 and the scalar C3.  The 34-gate interface adds only the two group
descriptors R23 and P23 and intentionally does not materialize either C4
product or a resolved C4 bus.

This is a fixed 512-row replay.  It is not a topology search.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import itertools
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "low34-factored-c4-audit-v1.json"


@dataclass(frozen=True)
class Driver:
    active: bool
    value: int


@dataclass(frozen=True)
class Bus:
    value: int
    driven: bool
    conflict: bool


def switch(enable: int, data: int) -> Driver:
    return Driver(active=bool(enable), value=int(bool(data)))


def resolve(*drivers: Driver) -> Bus:
    active = [driver.value for driver in drivers if driver.active]
    return Bus(
        value=int(any(active)),
        driven=bool(active),
        conflict=bool(active) and min(active) != max(active),
    )


def expected_low(a: int, b: int, cin: int) -> tuple[int, ...]:
    total = a + b + cin
    return (*(total >> index & 1 for index in range(4)), total >> 4 & 1)


def evaluate(a: int, b: int, cin: int) -> dict[str, object]:
    bits_a = [(a >> index) & 1 for index in range(4)]
    bits_b = [(b >> index) & 1 for index in range(4)]

    # Audited 19-gate fast prefix.
    v0 = bits_a[0] | bits_b[0]
    ng0 = 1 - (bits_a[0] & bits_b[0])
    p0 = v0 & ng0
    d0 = cin | p0
    n0 = 1 - (cin & p0)
    s0 = d0 & n0
    c1 = 1 - (n0 & ng0)

    v1 = bits_a[1] | bits_b[1]
    ng1 = 1 - (bits_a[1] & bits_b[1])
    p1 = v1 & ng1
    d1 = c1 | p1
    n1 = 1 - (c1 & p1)
    s1 = d1 & n1

    t0 = cin & v0
    e01 = 1 - (ng0 & ng1)
    c2_bus = resolve(switch(t0, v1), switch(e01, v1))
    c2 = c2_bus.value

    # Seven-gate bit2.  N2 is paid by S2 and reused by the carry output.
    v2 = bits_a[2] | bits_b[2]
    ng2 = 1 - (bits_a[2] & bits_b[2])
    p2 = v2 & ng2
    d2 = c2 | p2
    n2 = 1 - (c2 & p2)
    s2 = d2 & n2
    c3 = 1 - (n2 & ng2)

    # Six-gate bit3.  nG3/N3 is the free late negative C4 factorization.
    v3 = bits_a[3] | bits_b[3]
    ng3 = 1 - (bits_a[3] & bits_b[3])
    p3 = v3 & ng3
    d3 = c3 | p3
    n3 = 1 - (c3 & p3)
    s3 = d3 & n3
    c4_late_negative = 1 - (ng3 & n3)

    # Two paid descriptors expose an early factored C4 interface.
    r23 = 1 - (ng2 & ng3)  # G2 OR G3
    p23 = p2 & p3
    fast_product = r23 & v3
    slow_product = p23 & c2
    c4_factored = fast_product | slow_product

    return {
        "low32": (s0, s1, s2, s3, c4_late_negative),
        "low34": (s0, s1, s2, s3, c4_factored),
        "c2_bus": c2_bus,
        "factors": (r23, v3, p23, c2),
        "products": (fast_product, slow_product),
    }


def main() -> int:
    mismatch_low32 = 0
    mismatch_low34 = 0
    c2_conflict = 0
    c2_driven = 0
    product_overlap = 0
    output_rows: list[tuple[int, ...]] = []
    factor_rows: list[tuple[int, ...]] = []

    for a, b, cin in itertools.product(range(16), range(16), range(2)):
        observed = evaluate(a, b, cin)
        expected = expected_low(a, b, cin)
        low32 = tuple(observed["low32"])
        low34 = tuple(observed["low34"])
        fast_product, slow_product = observed["products"]

        mismatch_low32 += int(low32 != expected)
        mismatch_low34 += int(low34 != expected)
        c2_conflict += int(observed["c2_bus"].conflict)
        c2_driven += int(observed["c2_bus"].driven)
        product_overlap += int(bool(fast_product and slow_product))
        output_rows.append(low34)
        factor_rows.append(tuple(observed["factors"]))

    output_canonical = json.dumps(output_rows, separators=(",", ":")).encode("ascii")
    factor_canonical = json.dumps(factor_rows, separators=(",", ":")).encode("ascii")
    payload = {
        "schema": "tc-byte-adder-low34-factored-c4-audit-v1",
        "method": "fixed 512-row replay; no topology search",
        "rows": len(output_rows),
        "gate_ledger": {
            "fast_bits0_1_and_C2": 19,
            "bit2_state_sum_and_shared_C3": 7,
            "bit3_state_sum_and_late_negative_factors": 6,
            "late_split_total": 32,
            "R23_and_P23_descriptors": 2,
            "factored_total": 34,
            "optional_fast_and_slow_products": 2,
            "materialized_positive_reason_total": 36,
            "optional_scalar_C4_final_OR": 1,
            "scalar_C4_total": 37,
        },
        "arrival": {
            "S0": 4,
            "S1": 6,
            "C2": 3,
            "N2": 4,
            "S2": 5,
            "C3": 5,
            "N3": 6,
            "S3": 7,
            "late_negative_nG3": 1,
            "late_negative_N3": 6,
            "R23": 2,
            "V3": 1,
            "P23": 3,
            "factored_C2": 3,
            "optional_fast_product": 3,
            "optional_slow_product": 4,
            "optional_scalar_C4": 5,
        },
        "interface": {
            "late_32_gate": "C4 = NAND(nG3,N3)",
            "early_34_gate": "C4 = (R23*V3) OR (P23*C2)",
            "R23": "NAND(nG2,nG3) = G2 OR G3",
            "P23": "P2*P3",
            "products_are_materialized": False,
        },
        "semantic": {
            "low32_mismatch_rows": mismatch_low32,
            "low34_mismatch_rows": mismatch_low34,
            "C2_bus_driven_rows": c2_driven,
            "C2_bus_Z_rows": len(output_rows) - c2_driven,
            "C2_bus_conflict_rows": c2_conflict,
            "factored_product_overlap_rows": product_overlap,
            "output_truth_sha256": sha256(output_canonical).hexdigest(),
            "factor_truth_sha256": sha256(factor_canonical).hexdigest(),
        },
        "score_contract": {
            "authoritative_frontier": {"gate": 84, "delay": 6, "energy": 504},
            "strict_D7_gate_ceiling": 71,
            "remaining_high_budget_with_low32": 39,
            "remaining_high_budget_with_low34": 37,
            "remaining_high_budget_with_low36": 35,
            "remaining_high_budget_with_low37": 34,
        },
        "conclusion": {
            "complete_71_D7_found": False,
            "low32_late_split_found": True,
            "low34_early_factored_interface_found": True,
            "statement": (
                "The 34-gate boundary publishes every C4 factor by D3 without "
                "materializing either product or a resolved C4 bus.  A complete "
                "strict D7 improvement still requires a directly compatible high "
                "block of at most 37 gates."
            ),
        },
        "game_started": False,
        "save_read_or_modified": False,
    }

    assert mismatch_low32 == 0
    assert mismatch_low34 == 0
    assert c2_conflict == 0
    assert product_overlap == 0

    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(OUTPUT)
    print(json.dumps(payload["gate_ledger"], ensure_ascii=False))
    print(json.dumps(payload["arrival"], ensure_ascii=False))
    print(json.dumps(payload["semantic"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
