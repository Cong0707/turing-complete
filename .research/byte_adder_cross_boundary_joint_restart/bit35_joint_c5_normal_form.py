"""Canonical complete C5 normal-form shard domain for the bit-3:5 joint cut.

The module is pure metadata: it has no PySAT dependency and performs no search.
For each fixed component count it partitions every legal physical C5 output
bus into a direct-source, singleton-component, or multi-Switch driver class,
with all strict component ancestors normalized before the driver group.
"""

from __future__ import annotations

from hashlib import sha256
import json


PROFILE = "d7_80_bit35_joint"
OUTPUT_DEADLINES = (5, 7, 4, 5, 6)
IDENTITY_SCHEMA = "tc-byte-adder-bit35-joint-c5-constraint-v1"


def canonical_sha256(value: object) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return sha256(encoded).hexdigest()


def maximum_switches(components: int, gate_bound: int) -> int:
    if components < 0 or gate_bound < 0 or components > gate_bound:
        raise ValueError("require 0 <= components <= gate_bound")
    # weighted gate = components + switches + 2*xors
    return min(components, gate_bound - components)


def shard_domain(components: int, gate_bound: int) -> tuple[str, ...]:
    maximum_switches(components, gate_bound)
    shards = ["source"]
    shards.extend(f"single_k{k}" for k in range(components))
    for driver_count in range(2, maximum_switches(components, gate_bound) + 1):
        shards.extend(
            f"multi_d{driver_count}_k{k}"
            for k in range(components - driver_count + 1)
        )
    return tuple(shards)


def parse_shard(
    shard: str,
    components: int,
    gate_bound: int,
) -> dict[str, int | str]:
    if shard not in shard_domain(components, gate_bound):
        raise ValueError(
            f"invalid shard {shard!r}; expected one of "
            f"{shard_domain(components, gate_bound)}"
        )
    if shard == "source":
        return {"driver_class": "source"}
    if shard.startswith("single_k"):
        return {
            "driver_class": "single_component",
            "ancestor_count": int(shard.removeprefix("single_k")),
        }
    multi, ancestor_text = shard.split("_k", 1)
    return {
        "driver_class": "multi_switch",
        "driver_count": int(multi.removeprefix("multi_d")),
        "ancestor_count": int(ancestor_text),
    }


def constraint_identity(
    shard: str,
    components: int,
    gate_bound: int,
) -> dict[str, object]:
    parsed = parse_shard(shard, components, gate_bound)
    driver_class = str(parsed["driver_class"])
    identity: dict[str, object] = {
        "schema": IDENTITY_SCHEMA,
        "profile": PROFILE,
        "gate_bound": gate_bound,
        "components": components,
        "maximum_switches_by_weight": maximum_switches(components, gate_bound),
        "shard": shard,
        "output": "C5",
        "output_index": 2,
        "joint_outputs": ["S3", "S4", "C5", "T5", "S5"],
        "driver_class": driver_class,
    }
    if driver_class == "source":
        identity.update(
            {
                "driver_count": 1,
                "allowed_driver_kind": "paid_source_or_constant",
                "forbidden_component_output_slots": list(range(components)),
                "normal_form": "C5 is driven directly by one paid source or constant",
            }
        )
    elif driver_class == "single_component":
        ancestor_count = int(parsed["ancestor_count"])
        driver_slot = ancestor_count
        identity.update(
            {
                "driver_count": 1,
                "allowed_driver_kind": "any_component_kind",
                "ancestor_count": ancestor_count,
                "ancestor_slots": list(range(ancestor_count)),
                "driver_slots": [driver_slot],
                "ancestor_user_terminal_exclusive": driver_slot + 1,
                "normal_form": (
                    "all strict component ancestors of the singleton C5 driver first; "
                    "the driver next; every C5 non-ancestor last"
                ),
            }
        )
    else:
        ancestor_count = int(parsed["ancestor_count"])
        driver_count = int(parsed["driver_count"])
        driver_slots = list(range(ancestor_count, ancestor_count + driver_count))
        identity.update(
            {
                "driver_count": driver_count,
                "allowed_driver_kind": "SWITCH",
                "ancestor_count": ancestor_count,
                "ancestor_slots": list(range(ancestor_count)),
                "driver_slots": driver_slots,
                "ancestor_user_terminal_exclusive": ancestor_count + driver_count,
                "normal_form": (
                    "all strict component ancestors of the physical C5 driver set first; "
                    "the mutually independent Switch drivers next; every C5 non-ancestor last"
                ),
            }
        )
    return identity


def constraint_sha256(shard: str, components: int, gate_bound: int) -> str:
    return canonical_sha256(constraint_identity(shard, components, gate_bound))


def shard_name(components: int, shard: str) -> str:
    return f"n{components:02d}_{shard}"


def shard_records(
    gate_bound: int,
    components: tuple[int, ...] | list[int] | range,
) -> list[dict[str, object]]:
    records = []
    for component_count in components:
        for shard in shard_domain(component_count, gate_bound):
            records.append(
                {
                    "name": shard_name(component_count, shard),
                    "components": component_count,
                    "shard": shard,
                    "constraint_sha256": constraint_sha256(
                        shard,
                        component_count,
                        gate_bound,
                    ),
                }
            )
    return records


def component_shard_counts(gate_bound: int) -> dict[str, int]:
    return {
        str(components): len(shard_domain(components, gate_bound))
        for components in range(gate_bound + 1)
    }
