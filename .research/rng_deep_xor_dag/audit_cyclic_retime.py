"""Audit legal late-OR phase injection on cyclic xorshift retimings.

For each prefix encoding ``q = T*x`` the steady network is the same three
xorshift stages in cyclic order.  It has exactly 61 XOR gates and also exposes
the visible value at the suffix/prefix boundary.  The script enumerates every
OR placement on a state-only signal whose source depth plus remaining feedback
depth is at most two XOR levels.  This is the exact data-path condition for a
10-delay circuit:

    Delay Bit 4 + (<=2 XOR levels)*2 + OR 1 <= 10.

One OR output may fan out to any subset of the selected source signal's legal
consumers.  Its effect on the 32 feedback outputs is computed through the real
DAG, including reconvergent XOR cancellation.  Seed bits are independent, so
the minimum number of OR components is the sum of 32 exact shortest XOR-
representation problems over those influence masks.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import hashlib
from itertools import combinations
import json
from pathlib import Path


BITS = 32
MASK = (1 << BITS) - 1


@dataclass(frozen=True)
class Gate:
    output: int
    left: int
    right: int
    stage: int


@dataclass(frozen=True)
class Use:
    kind: str
    target: int
    pin: int
    output_bit: int
    remaining_xor: int


@dataclass(frozen=True)
class Site:
    source: int
    uses: tuple[Use, ...]
    influence: int
    source_depth: int
    remaining_xor: int


STAGES = (("right", 13), ("left", 17), ("right", 5))


def matrix_apply_rows(rows: tuple[int, ...], value: int) -> int:
    return sum(((row & value).bit_count() & 1) << bit for bit, row in enumerate(rows))


def stage_rows(rows: tuple[int, ...], direction: str, amount: int) -> tuple[int, ...]:
    result = list(rows)
    if direction == "right":
        for bit in range(BITS - amount):
            result[bit] ^= rows[bit + amount]
    else:
        for bit in range(amount, BITS):
            result[bit] ^= rows[bit - amount]
    return tuple(result)


def build(prefix: int):
    signals = list(range(BITS))
    forms = {bit: 1 << bit for bit in range(BITS)}
    depths = {bit: 0 for bit in range(BITS)}
    gates: list[Gate] = []
    next_signal = BITS
    rotated = (*STAGES[prefix:], *STAGES[:prefix])
    visible_after = len(STAGES) - prefix
    visible = tuple(signals) if visible_after == 0 else None
    for stage_index, (direction, amount) in enumerate(rotated):
        previous = tuple(signals)
        updated = list(previous)
        affected = range(BITS - amount) if direction == "right" else range(amount, BITS)
        for bit in affected:
            other = bit + amount if direction == "right" else bit - amount
            left, right = previous[bit], previous[other]
            output = next_signal
            next_signal += 1
            gates.append(Gate(output, left, right, stage_index))
            forms[output] = forms[left] ^ forms[right]
            depths[output] = max(depths[left], depths[right]) + 1
            updated[bit] = output
        signals = updated
        if stage_index + 1 == visible_after:
            visible = tuple(signals)
    if visible is None:
        raise AssertionError("visible boundary was not captured")
    feedback = tuple(signals)

    prefix_rows = tuple(1 << bit for bit in range(BITS))
    for direction, amount in STAGES[:prefix]:
        prefix_rows = stage_rows(prefix_rows, direction, amount)
    return tuple(gates), forms, depths, visible, feedback, prefix_rows


def output_influence(gates: tuple[Gate, ...], feedback: tuple[int, ...], selected_uses: tuple[Use, ...]) -> int:
    perturb = {signal: 0 for signal in range(BITS + len(gates))}
    output_taps = 0
    selected_gate_pins = {(use.target, use.pin) for use in selected_uses if use.kind == "gate"}
    for use in selected_uses:
        if use.kind == "output":
            output_taps ^= 1 << use.output_bit
    for gate in gates:
        left = perturb[gate.left] ^ int((gate.output, 0) in selected_gate_pins)
        right = perturb[gate.right] ^ int((gate.output, 1) in selected_gate_pins)
        perturb[gate.output] = left ^ right
    result = output_taps
    for bit, signal in enumerate(feedback):
        if perturb[signal]:
            result ^= 1 << bit
    return result


def enumerate_sites(gates: tuple[Gate, ...], depths: dict[int, int], feedback: tuple[int, ...]) -> tuple[Site, ...]:
    consumers: dict[int, list[tuple[int, int]]] = {}
    for gate in gates:
        consumers.setdefault(gate.left, []).append((gate.output, 0))
        consumers.setdefault(gate.right, []).append((gate.output, 1))

    # Longest number of gates from a signal to any feedback output.
    remaining = {signal: 0 if signal in feedback else -10_000 for signal in depths}
    for gate in reversed(gates):
        if remaining[gate.output] < 0:
            continue
        for source in (gate.left, gate.right):
            remaining[source] = max(remaining[source], 1 + remaining[gate.output])

    uses_by_source: dict[int, list[Use]] = {}
    for source, entries in consumers.items():
        for target, pin in entries:
            rem = 1 + remaining[target]
            if depths[source] + rem <= 2:
                uses_by_source.setdefault(source, []).append(Use("gate", target, pin, -1, rem))
    for output_bit, source in enumerate(feedback):
        if depths[source] <= 2:
            uses_by_source.setdefault(source, []).append(Use("output", -1, -1, output_bit, 0))

    sites = []
    for source, uses in sorted(uses_by_source.items()):
        # Fanout is tiny for this network.  Enumerating all subsets captures an
        # OR component shared across any chosen group of consumer edges.
        for count in range(1, len(uses) + 1):
            for subset in combinations(uses, count):
                influence = output_influence(gates, feedback, subset)
                if not influence:
                    continue
                sites.append(
                    Site(
                        source,
                        tuple(subset),
                        influence,
                        depths[source],
                        max(use.remaining_xor for use in subset),
                    )
                )
    return tuple(sites)


def shortest_representation(target: int, sites: tuple[Site, ...], maximum: int = 8) -> tuple[int, tuple[int, ...]] | None:
    # Equal influence masks are interchangeable for a single seed.  Keep the
    # first physical representative; a minimum never needs the same mask twice.
    representatives: dict[int, int] = {}
    for index, site in enumerate(sites):
        representatives.setdefault(site.influence, index)
    masks = tuple(sorted(representatives))
    indexes = tuple(representatives[mask] for mask in masks)
    if target in representatives:
        return 1, (representatives[target],)

    half = maximum // 2
    left: dict[int, tuple[int, ...]] = {0: ()}
    for count in range(1, half + 1):
        for combo in combinations(range(len(masks)), count):
            value = 0
            for index in combo:
                value ^= masks[index]
            previous = left.get(value)
            if previous is None or len(combo) < len(previous):
                left[value] = combo
    best = None
    for value, combo in left.items():
        other = left.get(value ^ target)
        if other is None:
            continue
        merged = tuple(sorted(set(combo) ^ set(other)))
        check = 0
        for index in merged:
            check ^= masks[index]
        if check != target or len(merged) > maximum:
            continue
        if best is None or len(merged) < len(best):
            best = merged
    if best is None:
        return None
    return len(best), tuple(indexes[index] for index in best)


def audit(prefix: int, maximum_sites_per_seed: int) -> dict[str, object]:
    gates, forms, depths, visible, feedback, T = build(prefix)
    sites = enumerate_sites(gates, depths, feedback)
    if len(gates) != 61:
        raise AssertionError("cyclic xorshift network no longer has 61 XOR gates")

    assignments = []
    total_or = 0
    for seed in range(BITS):
        target = sum(((row >> seed) & 1) << output for output, row in enumerate(T))
        found = shortest_representation(target, sites, maximum_sites_per_seed)
        if found is None:
            return {
                "schema": 1,
                "status": "unreachable",
                "prefix_stage_count": prefix,
                "failed_seed": seed,
                "site_count": len(sites),
            }
        count, chosen = found
        total_or += count
        assignments.append(
            {
                "seed": seed,
                "target": f"{target:08x}",
                "or_count": count,
                "sites": [
                    {
                        "source": site.source,
                        "source_form": f"{forms[site.source]:08x}",
                        "source_depth": site.source_depth,
                        "remaining_xor": site.remaining_xor,
                        "influence": f"{site.influence:08x}",
                        "uses": [asdict(use) for use in site.uses],
                    }
                    for site in (sites[index] for index in chosen)
                ],
            }
        )

    # Replay every seed column directly from the recorded site influences.
    for item in assignments:
        actual = 0
        for site in item["sites"]:
            actual ^= int(site["influence"], 16)
        if actual != int(item["target"], 16):
            raise AssertionError("phase influence replay failed")

    logic = 3 * len(gates) + total_or
    gate = 166 + logic
    return {
        "schema": 1,
        "status": "exact-within-bound",
        "model": "61-XOR cyclic retime plus legal late OR edge injection",
        "prefix_stage_count": prefix,
        "stage_order": [list(stage) for stage in (*STAGES[prefix:], *STAGES[:prefix])],
        "visible_boundary_after_stage": len(STAGES) - prefix,
        "xor_count": len(gates),
        "or_count": total_or,
        "logic_cost": logic,
        "gate": gate,
        "delay": 10,
        "cycles": 66,
        "energy": gate * 10 * 66,
        "beats_431_9_66": gate * 10 < 431 * 9,
        "site_count": len(sites),
        "unique_influence_count": len({site.influence for site in sites}),
        "maximum_sites_per_seed": maximum_sites_per_seed,
        "T": [f"{row:08x}" for row in T],
        "B": [f"{forms[signal]:08x}" for signal in feedback],
        "C": [f"{forms[signal]:08x}" for signal in visible],
        "gate_dag": [asdict(gate_item) for gate_item in gates],
        "assignments": assignments,
        "certificate_sha256": hashlib.sha256(
            json.dumps(assignments, sort_keys=True, separators=(",", ":")).encode("ascii")
        ).hexdigest(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-sites-per-seed", type=int, default=8)
    args = parser.parse_args()
    results = [audit(prefix, args.max_sites_per_seed) for prefix in range(4)]
    payload = {"schema": 1, "results": results}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            [
                {key: value for key, value in result.items() if key not in {"T", "B", "C", "gate_dag", "assignments"}}
                for result in results
            ],
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
