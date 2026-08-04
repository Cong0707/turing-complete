"""Pure complete driver-count refinement for T5 and S5 outputs.

The 96-row truth domain proves that neither T5 nor S5 is equal to any paid
source or constant.  Consequently each output is driven either by exactly one
component output or by d>=2 Switch outputs.  This module defines the canonical
cross-product refinement of an existing C5 normal-form shard.
"""

from __future__ import annotations

from hashlib import sha256
import json


IDENTITY_SCHEMA = "tc-byte-adder-bit35-joint-phase-driver-constraint-v1"
OUTPUTS = ("T5", "S5")


def canonical_sha256(value: object) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return sha256(encoded).hexdigest()


def maximum_switches(components: int, gate_bound: int) -> int:
    if not 0 <= components <= gate_bound:
        raise ValueError("require 0 <= components <= gate_bound")
    return min(components, gate_bound - components)


def driver_count_domain(components: int, gate_bound: int) -> tuple[int, ...]:
    if components == 0:
        return ()
    maximum = maximum_switches(components, gate_bound)
    return (1, *range(2, maximum + 1))


def direct_source_equivalence() -> dict[str, list[str]]:
    names = (
        "a3",
        "b3",
        "a4",
        "b4",
        "C3",
        "P5",
        "G3",
        "Q3",
        "P3",
        "G4",
        "Q4",
        "P4",
        "0",
        "1",
    )
    source_values = [[] for _ in names]
    source_drivens = [[] for _ in names]
    targets = {name: [] for name in OUTPUTS}
    for raw in range(16):
        a3, b3, a4, b4 = ((raw >> bit) & 1 for bit in range(4))
        for p5 in (0, 1):
            for state in ("Z0", "D0", "D1"):
                c3 = int(state == "D1")
                g3 = a3 & b3
                q3 = 1 ^ (a3 | b3)
                p3 = 1 ^ (g3 | q3)
                g4 = a4 & b4
                q4 = 1 ^ (a4 | b4)
                p4 = 1 ^ (g4 | q4)
                c4 = g3 | (p3 & c3)
                c5 = g4 | (p4 & c4)
                t5 = p5 & c5
                s5 = p5 ^ c5
                values = (
                    a3,
                    b3,
                    a4,
                    b4,
                    c3,
                    p5,
                    g3,
                    q3,
                    p3,
                    g4,
                    q4,
                    p4,
                    0,
                    1,
                )
                for index, value in enumerate(values):
                    source_values[index].append(bool(value))
                    source_drivens[index].append(
                        state != "Z0" if names[index] == "C3" else True
                    )
                targets["T5"].append(bool(t5))
                targets["S5"].append(bool(s5))
    equivalent = {}
    for target_name, target in targets.items():
        equivalent[target_name] = [
            name
            for name, values, drivens in zip(
                names,
                source_values,
                source_drivens,
                strict=True,
            )
            if values == target and all(drivens)
        ]
    return equivalent


def constraint_identity(
    components: int,
    gate_bound: int,
    t5_drivers: int,
    s5_drivers: int,
) -> dict[str, object]:
    domain = driver_count_domain(components, gate_bound)
    if t5_drivers not in domain or s5_drivers not in domain:
        raise ValueError(
            f"driver counts must be in {domain}, got T5={t5_drivers} S5={s5_drivers}"
        )
    direct = direct_source_equivalence()
    if direct != {"T5": [], "S5": []}:
        raise RuntimeError(f"direct-source exclusion changed: {direct}")
    return {
        "schema": IDENTITY_SCHEMA,
        "gate_bound": gate_bound,
        "components": components,
        "maximum_switches_by_weight": maximum_switches(components, gate_bound),
        "direct_paid_source_equivalence": direct,
        "outputs": {
            "T5": {
                "output_index": 3,
                "driver_count": t5_drivers,
                "driver_kind": "any_component" if t5_drivers == 1 else "SWITCH",
            },
            "S5": {
                "output_index": 4,
                "driver_count": s5_drivers,
                "driver_kind": "any_component" if s5_drivers == 1 else "SWITCH",
            },
        },
    }


def constraint_sha256(
    components: int,
    gate_bound: int,
    t5_drivers: int,
    s5_drivers: int,
) -> str:
    return canonical_sha256(
        constraint_identity(
            components,
            gate_bound,
            t5_drivers,
            s5_drivers,
        )
    )


def pair_domain(components: int, gate_bound: int) -> tuple[tuple[int, int], ...]:
    domain = driver_count_domain(components, gate_bound)
    return tuple((t5, s5) for t5 in domain for s5 in domain)
