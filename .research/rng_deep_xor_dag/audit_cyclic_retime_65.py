"""Exact 65-cycle phase audit for the cyclic no-RAM RNG DAG.

At tick zero the single input seed must already produce the first visible RNG
word and the first encoded feedback state:

    visible_0 = A * seed
    feedback_0 = T * A * seed

Later ticks use the steady matrices ``C`` and ``B``.  Each legal OR injection
site is represented by a 64-bit influence vector: low bits are feedback B,
high bits are visible C.  The audit minimizes each independent seed column
exactly within the requested per-seed bound, emits every physical placement,
and replays all 256 runtime seeds for 65 visible outputs.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import hashlib
import importlib.util
from itertools import combinations
import json
from pathlib import Path
import sys


BITS = 32
MASK = (1 << BITS) - 1


def load_base(path: Path):
    spec = importlib.util.spec_from_file_location("rng_deep_cyclic_base", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@dataclass(frozen=True)
class Use65:
    kind: str
    target: int
    pin: int
    output_bit: int
    remaining_xor: int


@dataclass(frozen=True)
class Site65:
    source: int
    uses: tuple[Use65, ...]
    influence: int
    source_depth: int
    remaining_xor: int


def apply_row(row: int, matrix: tuple[int, ...]) -> int:
    result = 0
    remaining = row
    while remaining:
        bit = remaining & -remaining
        result ^= matrix[bit.bit_length() - 1]
        remaining ^= bit
    return result


def compose(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(apply_row(row, right) for row in left)


def apply_matrix(matrix: tuple[int, ...], value: int) -> int:
    return sum(((row & value).bit_count() & 1) << output for output, row in enumerate(matrix))


def xorshift32(value: int) -> int:
    value ^= value >> 13
    value &= MASK
    value ^= (value << 17) & MASK
    value &= MASK
    value ^= value >> 5
    return value & MASK


def actual_test_seeds() -> tuple[int, ...]:
    modulus = 0xFFFFFFFE
    multiplier = 0x4848F09881D3DDD1
    return tuple(
        1 + ((((test_id + 1) * multiplier) & 0xFFFFFFFFFFFFFFFF) % modulus)
        for test_id in range(256)
    )


def output_influence(base, gates, feedback, visible, selected_uses: tuple[Use65, ...]) -> int:
    perturb = {signal: 0 for signal in range(BITS + len(gates))}
    selected_gate_pins = {
        (use.target, use.pin) for use in selected_uses if use.kind == "gate"
    }
    result = 0
    for use in selected_uses:
        if use.kind == "feedback":
            result ^= 1 << use.output_bit
        elif use.kind == "visible":
            result ^= 1 << (BITS + use.output_bit)
    for gate in gates:
        left = perturb[gate.left] ^ int((gate.output, 0) in selected_gate_pins)
        right = perturb[gate.right] ^ int((gate.output, 1) in selected_gate_pins)
        perturb[gate.output] = left ^ right
    for bit, signal in enumerate(feedback):
        if perturb[signal]:
            result ^= 1 << bit
    for bit, signal in enumerate(visible):
        if perturb[signal]:
            result ^= 1 << (BITS + bit)
    return result


def enumerate_sites(base, gates, depths, feedback, visible) -> tuple[Site65, ...]:
    consumers: dict[int, list[tuple[int, int]]] = {}
    for gate in gates:
        consumers.setdefault(gate.left, []).append((gate.output, 0))
        consumers.setdefault(gate.right, []).append((gate.output, 1))

    sinks = frozenset((*feedback, *visible))
    remaining = {signal: 0 if signal in sinks else -10_000 for signal in depths}
    for gate in reversed(gates):
        if remaining[gate.output] < 0:
            continue
        for source in (gate.left, gate.right):
            remaining[source] = max(remaining[source], 1 + remaining[gate.output])

    uses_by_source: dict[int, list[Use65]] = {}
    for source, entries in consumers.items():
        for target, pin in entries:
            rem = 1 + remaining[target]
            if depths[source] + rem <= 2:
                uses_by_source.setdefault(source, []).append(
                    Use65("gate", target, pin, -1, rem)
                )
    for bit, source in enumerate(feedback):
        if depths[source] <= 2:
            uses_by_source.setdefault(source, []).append(
                Use65("feedback", -1, -1, bit, 0)
            )
    for bit, source in enumerate(visible):
        if depths[source] <= 2:
            uses_by_source.setdefault(source, []).append(
                Use65("visible", -1, -1, bit, 0)
            )

    sites = []
    for source, uses in sorted(uses_by_source.items()):
        # The largest fanout here is small; all subsets are required because a
        # single physical OR may feed any selected consumers of its source.
        for count in range(1, len(uses) + 1):
            for subset in combinations(uses, count):
                influence = output_influence(base, gates, feedback, visible, subset)
                if influence:
                    sites.append(
                        Site65(
                            source,
                            tuple(subset),
                            influence,
                            depths[source],
                            max(use.remaining_xor for use in subset),
                        )
                    )
    return tuple(sites)


def shortest(target: int, sites: tuple[Site65, ...], maximum: int) -> tuple[int, tuple[int, ...]] | None:
    representatives: dict[int, int] = {}
    for index, site in enumerate(sites):
        representatives.setdefault(site.influence, index)
    masks = tuple(sorted(representatives))
    physical = tuple(representatives[mask] for mask in masks)
    if target in representatives:
        return 1, (representatives[target],)

    half = maximum // 2
    table: dict[int, tuple[int, ...]] = {0: ()}
    for count in range(1, half + 1):
        for combo in combinations(range(len(masks)), count):
            value = 0
            for index in combo:
                value ^= masks[index]
            old = table.get(value)
            if old is None or len(combo) < len(old):
                table[value] = combo
    best = None
    for value, left in table.items():
        right = table.get(value ^ target)
        if right is None:
            continue
        merged = tuple(sorted(set(left) ^ set(right)))
        check = 0
        for index in merged:
            check ^= masks[index]
        if check != target or len(merged) > maximum:
            continue
        if best is None or len(merged) < len(best):
            best = merged
    if best is None:
        return None
    return len(best), tuple(physical[index] for index in best)


def audit_prefix(base, prefix: int, maximum: int, or_budget: int | None) -> dict[str, object]:
    gates, forms, depths, visible, feedback, T = base.build(prefix)
    B = tuple(forms[signal] for signal in feedback)
    C = tuple(forms[signal] for signal in visible)
    identity = tuple(1 << bit for bit in range(BITS))
    A = identity
    for direction, amount in base.STAGES:
        A = base.stage_rows(A, direction, amount)
    TA = compose(T, A)
    if compose(C, T) != A or compose(T, C) != B:
        raise AssertionError("steady matrix identities failed")

    sites = enumerate_sites(base, gates, depths, feedback, visible)
    assignments = []
    lower_bound_only = []
    total_or = 0

    def proved_seed_columns(*extra: int) -> list[int]:
        """Return every seed column contributing to the cumulative bound."""

        return sorted(
            {
                *(item["seed"] for item in assignments),
                *(item["seed"] for item in lower_bound_only),
                *extra,
            }
        )

    for seed in range(BITS):
        feedback_column = sum(((row >> seed) & 1) << bit for bit, row in enumerate(TA))
        visible_column = sum(((row >> seed) & 1) << bit for bit, row in enumerate(A))
        target = feedback_column | (visible_column << BITS)
        found = shortest(target, sites, maximum)
        if found is None:
            failed_lower_bound = maximum + 1
            cumulative_lower_bound = total_or + failed_lower_bound
            if or_budget is not None and cumulative_lower_bound > or_budget:
                return {
                    "schema": 1,
                    "status": "unsat-or-budget",
                    "model": "65-cycle cyclic retime with joint tick-zero B/C labels",
                    "prefix_stage_count": prefix,
                    "xor_count": len(gates),
                    "or_budget": or_budget,
                    "proved_or_lower_bound": cumulative_lower_bound,
                    "proved_seed_columns": proved_seed_columns(seed),
                    "per_seed_minimum": [item["or_count"] for item in assignments],
                    "lower_bound_only": lower_bound_only,
                    "failed_seed": seed,
                    "failed_seed_lower_bound": failed_lower_bound,
                    "failed_target": f"{target:016x}",
                    "site_count": len(sites),
                    "unique_influence_count": len({site.influence for site in sites}),
                    "maximum_sites_per_seed": maximum,
                    "completeness": (
                        "All XOR-combinations of legal site influence masks through "
                        f"size {maximum} were enumerated for the failed seed; all earlier "
                        "reported seed minima are exact. Different seed bits cannot share "
                        "one physical one-bit OR."
                    ),
                    "assignments": assignments,
                    "certificate_sha256": hashlib.sha256(
                        json.dumps(assignments, sort_keys=True, separators=(",", ":")).encode("ascii")
                    ).hexdigest(),
                }
            if or_budget is not None:
                lower_bound_only.append(
                    {
                        "seed": seed,
                        "target": f"{target:016x}",
                        "or_lower_bound": failed_lower_bound,
                    }
                )
                total_or = cumulative_lower_bound
                continue
            return {
                "schema": 1,
                "status": "unreachable-within-bound",
                "prefix_stage_count": prefix,
                "failed_seed": seed,
                "target": f"{target:016x}",
                "site_count": len(sites),
                "unique_influence_count": len({site.influence for site in sites}),
                "maximum_sites_per_seed": maximum,
            }
        count, chosen = found
        total_or += count
        assignments.append(
            {
                "seed": seed,
                "target": f"{target:016x}",
                "feedback_target": f"{feedback_column:08x}",
                "visible_target": f"{visible_column:08x}",
                "or_count": count,
                "sites": [
                    {
                        "source": site.source,
                        "source_form": f"{forms[site.source]:08x}",
                        "source_depth": site.source_depth,
                        "remaining_xor": site.remaining_xor,
                        "influence": f"{site.influence:016x}",
                        "uses": [asdict(use) for use in site.uses],
                    }
                    for site in (sites[index] for index in chosen)
                ],
            }
        )
        if or_budget is not None and total_or > or_budget:
            return {
                "schema": 1,
                "status": "unsat-or-budget",
                "model": "65-cycle cyclic retime with joint tick-zero B/C labels",
                "prefix_stage_count": prefix,
                "xor_count": len(gates),
                "or_budget": or_budget,
                "proved_or_lower_bound": total_or,
                "proved_seed_columns": proved_seed_columns(),
                "per_seed_minimum": [item["or_count"] for item in assignments],
                "site_count": len(sites),
                "unique_influence_count": len({site.influence for site in sites}),
                "maximum_sites_per_seed": maximum,
                "completeness": (
                    "For every reported seed column, all XOR-combinations of legal "
                    f"site influence masks through size {maximum} were enumerated. "
                    "Different seed bits cannot share one physical one-bit OR."
                ),
                "assignments": assignments,
                "lower_bound_only": lower_bound_only,
                "certificate_sha256": hashlib.sha256(
                    json.dumps(assignments, sort_keys=True, separators=(",", ":")).encode("ascii")
                ).hexdigest(),
            }

    for item in assignments:
        actual = 0
        for site in item["sites"]:
            actual ^= int(site["influence"], 16)
        if actual != int(item["target"], 16):
            raise AssertionError("64-bit phase replay failed")

    seeds = actual_test_seeds()
    seed_bytes = b"".join(seed.to_bytes(4, "little") for seed in seeds)
    seed_hash = hashlib.sha256(seed_bytes).hexdigest()
    if seed_hash != "d8ef931e5eb213217aa4faedc43783f0875e52607f991e89080c6046aad1e24b":
        raise AssertionError("runtime seed vector changed")
    for seed in seeds:
        natural = xorshift32(seed)
        encoded = apply_matrix(TA, seed)
        if apply_matrix(A, seed) != natural:
            raise AssertionError("tick-zero visible value mismatch")
        for _ in range(1, 65):
            natural = xorshift32(natural)
            visible_value = apply_matrix(C, encoded)
            if visible_value != natural:
                raise AssertionError("steady visible sequence mismatch")
            encoded = apply_matrix(B, encoded)

    xor_count = len(gates)
    logic = 3 * xor_count + total_or
    gate_count = 166 + logic
    return {
        "schema": 1,
        "status": "sat-exact-within-bound",
        "model": "65-cycle cyclic retime with joint tick-zero B/C labels",
        "prefix_stage_count": prefix,
        "stage_order": [list(stage) for stage in (*base.STAGES[prefix:], *base.STAGES[:prefix])],
        "visible_boundary_after_stage": len(base.STAGES) - prefix,
        "xor_count": xor_count,
        "or_count": total_or,
        "logic_cost": logic,
        "fixed_shell_gate": 166,
        "gate": gate_count,
        "delay": 10,
        "cycles": 65,
        "energy": gate_count * 10 * 65,
        "target_energy": 431 * 9 * 66,
        "beats_431_9_66": gate_count * 10 * 65 < 431 * 9 * 66,
        "site_count": len(sites),
        "unique_influence_count": len({site.influence for site in sites}),
        "maximum_sites_per_seed": maximum,
        "T": [f"{row:08x}" for row in T],
        "TA": [f"{row:08x}" for row in TA],
        "B": [f"{row:08x}" for row in B],
        "C": [f"{row:08x}" for row in C],
        "A": [f"{row:08x}" for row in A],
        "gate_dag": [asdict(gate) for gate in gates],
        "assignments": assignments,
        "verification": {
            "matrix_identities": ["C*T=A", "T*C=B"],
            "tick_zero_feedback": "T*A*seed",
            "tick_zero_visible": "A*seed",
            "runtime_seeds": 256,
            "outputs_per_seed": 65,
            "seed_vector_sha256": seed_hash,
        },
        "certificate_sha256": hashlib.sha256(
            json.dumps(assignments, sort_keys=True, separators=(",", ":")).encode("ascii")
        ).hexdigest(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--prefix", type=int, default=1, choices=range(4))
    parser.add_argument("--max-sites-per-seed", type=int, default=4)
    parser.add_argument("--or-budget", type=int)
    args = parser.parse_args()
    base = load_base(Path(__file__).with_name("audit_cyclic_retime.py"))
    result = audit_prefix(base, args.prefix, args.max_sites_per_seed, args.or_budget)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {key: value for key, value in result.items() if key not in {"T", "TA", "A", "B", "C", "gate_dag", "assignments"}},
            indent=2,
        )
    )
    return 0 if result["status"].startswith("sat") else 2


if __name__ == "__main__":
    raise SystemExit(main())
