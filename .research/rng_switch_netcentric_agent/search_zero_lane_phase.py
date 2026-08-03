"""Search the fixed RNG phase DAG with zero-valued unused Word-Switch lanes.

The reviewed fixed-DAG solver charges one shared ``AND(lane, not_ready)`` for
every seed bit used by a late correction.  That AND is unnecessary when the
same seed has no direct-mode use: the corresponding steady Word-Switch lane
can be tied to constant zero, so the resolved lane already equals ``seed`` on
load and zero afterwards.

This wrapper preserves the upstream function and timing model exactly and
changes only its final pseudo-Boolean cost constraint to

``late pairs + seeds used both directly and late``.

It never starts the game or touches the save.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import sys
from typing import Any

import z3


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
UPSTREAM = ROOT / ".research" / "rng_word_switch_physical"
UPSTREAM_SOLVER = UPSTREAM / "solve_corrected_phase.py"
EXPECTED_UPSTREAM_SHA256 = "34873b70e27dfc5c72464369af781081648cbbae6c0de77cad6c0f10f695acde"

if str(UPSTREAM) not in sys.path:
    sys.path.insert(0, str(UPSTREAM))
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

import solve_corrected_phase as phase  # noqa: E402


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def selectable_nodes() -> tuple[int, ...]:
    """Recover exactly the node keys used to name upstream direct variables."""

    first_nodes, second_nodes = phase.classify_b_cone()
    nodes: set[int] = set()
    for node in first_nodes:
        gate = phase.rng.GATE_BY_OUTPUT[node]
        nodes.update((gate.left, gate.right))
    for node in second_nodes:
        gate = phase.rng.GATE_BY_OUTPUT[node]
        nodes.update((gate.left, gate.right))
    nodes.update(phase.rng.B)
    return tuple(sorted(nodes))


def solve_zero_lane(
    budget: int,
    timeout_ms: int,
    memory_mb: int,
) -> dict[str, object]:
    actual_hash = file_sha256(UPSTREAM_SOLVER)
    if actual_hash != EXPECTED_UPSTREAM_SHA256:
        raise RuntimeError(
            "upstream solver changed; review the cost-hook assumptions: "
            f"{actual_hash} != {EXPECTED_UPSTREAM_SHA256}"
        )

    nodes = selectable_nodes()
    original_pble = z3.PbLe
    hook_calls = 0

    def zero_lane_pble(arguments: list[tuple[Any, int]], bound: int) -> Any:
        nonlocal hook_calls
        hook_calls += 1
        late_seed_terms: dict[int, Any] = {}
        late_pair_terms: list[tuple[Any, int]] = []
        for variable, weight in arguments:
            name = str(variable)
            if name.startswith("late_seed_used_"):
                seed = int(name.removeprefix("late_seed_used_"))
                late_seed_terms[seed] = variable
            else:
                late_pair_terms.append((variable, weight))
        if set(late_seed_terms) != set(range(phase.BITS)):
            raise RuntimeError("unexpected upstream PbLe term layout")
        pulse_terms = []
        for seed, late_used in sorted(late_seed_terms.items()):
            direct_used = z3.Or(
                *(z3.Bool(f"direct_used_s{seed}_{node:08x}") for node in nodes)
            )
            pulse_terms.append((z3.And(late_used, direct_used), 1))
        return original_pble([*pulse_terms, *late_pair_terms], bound)

    z3.PbLe = zero_lane_pble
    try:
        status, certificate, reason = phase.solve(budget, timeout_ms, memory_mb)
    finally:
        z3.PbLe = original_pble
    if hook_calls != 1:
        raise RuntimeError(f"expected one upstream PbLe call, got {hook_calls}")

    result: dict[str, object] = {
        "schema": 1,
        "model": "fixed 61-XOR phase DAG with physical U32 input/Switch and zero steady lanes",
        "status": status,
        "reason": reason,
        "correction_budget": budget,
        "timeout_ms": timeout_ms,
        "memory_mb": memory_mb,
        "upstream_solver": str(UPSTREAM_SOLVER),
        "upstream_sha256": actual_hash,
        "cost_formula": "late_pair_count + |late_seed intersect direct_seed|",
        "base_gate": 413,
        "delay": 9,
        "cycles": 66,
    }
    if certificate is None:
        return result

    # The upstream verifier checks the complete load/steady GF(2) behavior.
    # Give it its historical accounting only for that independent replay.
    replay = deepcopy(certificate)
    replay["correction_budget"] = replay["correction_cost"]
    phase.verify(replay)

    direct_seeds = {int(seed) for seed, _node in certificate["direct_pairs"]}
    late_seeds = {int(seed) for seed in certificate["late_seed_bits"]}
    late_pair_count = len(certificate["late_pairs"])
    pulse_seeds = sorted(direct_seeds & late_seeds)
    zero_lane_seeds = sorted(set(range(phase.BITS)) - direct_seeds)
    new_cost = late_pair_count + len(pulse_seeds)
    if new_cost > budget:
        raise AssertionError(f"hook returned over-budget witness: {new_cost} > {budget}")
    if {int(seed) for seed, _node in certificate["late_pairs"]} != late_seeds:
        raise AssertionError("late pair/seed sets differ")

    result.update(
        {
            "correction_cost": new_cost,
            "total_gate": 413 + new_cost,
            "declared_energy": (413 + new_cost) * 9 * 66,
            "direct_seed_count": len(direct_seeds),
            "late_seed_count": len(late_seeds),
            "late_pair_count": late_pair_count,
            "pulse_seed_bits": pulse_seeds,
            "zero_lane_seed_bits": zero_lane_seeds,
            "upstream_historical_cost": certificate["correction_cost"],
            "certificate": certificate,
            "functional_replay": "passed upstream exact label verifier",
        }
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--budget", type=int, required=True)
    parser.add_argument("--timeout-ms", type=int, default=180_000)
    parser.add_argument("--memory-mb", type=int, default=640)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = solve_zero_lane(args.budget, args.timeout_ms, args.memory_mb)
    encoded = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    args.output.write_text(encoded, encoding="utf-8")
    print(
        json.dumps(
            {
                "status": payload["status"],
                "correction_cost": payload.get("correction_cost"),
                "total_gate": payload.get("total_gate"),
                "reason": payload["reason"],
            },
            ensure_ascii=False,
        )
    )
    return 2 if payload["status"] == "unknown" else 0


if __name__ == "__main__":
    raise SystemExit(main())
