#!/usr/bin/env python3
"""Prove that the xorshift32 matrix A+I needs at least 34 XOR2 gates.

The proof covers unrestricted fanout and cancellation.  It only assumes a
straight-line program of two-input XOR gates with the 32 primary inputs free.
All 32 rows of A+I are independent, distinct, and non-primary outputs.

With 32 gates every gate must be one of the 32 outputs.  An output gate cannot
XOR two earlier outputs, because that would make the output rows dependent.
It must therefore be a weight-two root or differ from an earlier output by one
primary input.

With 33 gates there is one additional non-output signal h.  Relax h to an
arbitrary form available from the beginning.  Every output is then either a
weight-two root, h XOR one input, an earlier output XOR one input, or an
earlier output XOR h.  Consequently every connected component of the output
graph (edges have difference one input or h) must contain a root (weight two
or distance one from h).  Exhausting every h that can affect a root or edge
finds no such graph.  This relaxation includes every real 33-gate circuit, so
the negative result is a strict lower bound.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Sequence


N = 32
MASK = (1 << N) - 1
IDENTITY = tuple(1 << bit for bit in range(N))


def xorshift32(value: int) -> int:
    value &= MASK
    value ^= value >> 13
    value ^= (value << 17) & MASK
    value ^= value >> 5
    return value & MASK


def transition_rows() -> tuple[int, ...]:
    columns = tuple(xorshift32(1 << source) for source in range(N))
    return tuple(
        sum(((columns[source] >> target) & 1) << source for source in range(N))
        for target in range(N)
    )


def rank(rows: Sequence[int]) -> int:
    pivots = [0] * N
    result = 0
    for original in rows:
        row = original
        while row:
            pivot = row.bit_length() - 1
            if pivots[pivot]:
                row ^= pivots[pivot]
            else:
                pivots[pivot] = row
                result += 1
                break
    return result


def components(
    rows: Sequence[int], h: int
) -> tuple[list[list[int]], set[int]]:
    roots = {
        index
        for index, row in enumerate(rows)
        if row.bit_count() == 2 or (row ^ h).bit_count() == 1
    }
    adjacency = [[] for _ in rows]
    for right in range(len(rows)):
        for left in range(right):
            difference = rows[left] ^ rows[right]
            if difference.bit_count() == 1 or difference == h:
                adjacency[left].append(right)
                adjacency[right].append(left)
    result = []
    seen: set[int] = set()
    for start in range(len(rows)):
        if start in seen:
            continue
        component = []
        stack = [start]
        seen.add(start)
        while stack:
            current = stack.pop()
            component.append(current)
            for neighbor in adjacency[current]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
        result.append(sorted(component))
    return result, roots


def digest_rows(rows: Sequence[int]) -> str:
    digest = hashlib.sha256()
    for row in rows:
        digest.update(int(row).to_bytes(4, "little"))
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    a = transition_rows()
    targets = tuple(row ^ IDENTITY[index] for index, row in enumerate(a))
    if rank(targets) != N:
        raise AssertionError("A+I must be invertible")
    if len(set(targets)) != N or any(row.bit_count() < 2 for row in targets):
        raise AssertionError("target rows must be distinct non-primary forms")

    # If h affects any target construction, it is either target XOR input or
    # target XOR target.  If it affects none, h=0 represents the same relaxed
    # unit-edge graph.  This finite set therefore covers all 2^32 choices.
    candidate_h = {0}
    candidate_h.update(
        targets[left] ^ targets[right]
        for right in range(N)
        for left in range(right)
    )
    candidate_h.update(row ^ (1 << bit) for row in targets for bit in range(N))

    feasible_h = []
    audit = []
    for h in sorted(candidate_h):
        groups, roots = components(targets, h)
        rootless = [group for group in groups if not roots.intersection(group)]
        if not rootless:
            feasible_h.append(h)
        audit.append(
            {
                "h": f"{h:08x}",
                "components": len(groups),
                "roots": len(roots),
                "rootless_components": len(rootless),
                "rootless_rows": sum(map(len, rootless)),
            }
        )
    if feasible_h:
        raise AssertionError(f"33-gate relaxation unexpectedly feasible: {feasible_h[:4]}")

    base_groups, base_roots = components(targets, 0)
    base_rootless = [
        group for group in base_groups if not base_roots.intersection(group)
    ]
    if not base_rootless:
        raise AssertionError("32-gate relaxation unexpectedly feasible")

    best = min(
        audit,
        key=lambda item: (
            int(item["rootless_rows"]),
            int(item["rootless_components"]),
            -int(item["roots"]),
            str(item["h"]),
        ),
    )
    distribution: dict[str, int] = {}
    for row in targets:
        key = str(row.bit_count())
        distribution[key] = distribution.get(key, 0) + 1

    certificate = {
        "schema": 1,
        "status": "unsat_at_most_33_xor2",
        "claim": "L_XOR2(A+I) >= 34",
        "model": {
            "inputs": N,
            "outputs": N,
            "gate": "two-input XOR, unrestricted fanout and cancellation",
            "relaxation_for_33": "one arbitrary auxiliary form h is free from time zero",
        },
        "target": {
            "rank": rank(targets),
            "distinct": len(set(targets)),
            "weight_distribution": distribution,
            "rows": [f"{row:08x}" for row in targets],
            "sha256": digest_rows(targets),
        },
        "gate_32": {
            "status": "unsat",
            "components": len(base_groups),
            "weight_two_roots": sorted(base_roots),
            "rootless_components": base_rootless,
        },
        "gate_33_relaxation": {
            "status": "unsat",
            "candidate_h": len(candidate_h),
            "feasible_h": 0,
            "best_relaxed_case": best,
            "audit": audit,
        },
        "persistent_cascade_consequence": {
            "identity": "U*C=A+I",
            "topology": "z=C*q; y=z+seed; w=U*y; q'=w+q",
            "minimum_xor2": "32 + L(C) + L(U) + 32 >= 64 + L(A+I) >= 98",
            "minimum_logic_gate": 98 * 3,
            "delay8_logic_budget": 292,
            "delay9_logic_budget": 242,
            "excluded": True,
            "scope": "explicit four-stage cascade only; globally interleaved B/D/C DAG remains open",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(certificate, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": certificate["status"],
                "candidate_h": len(candidate_h),
                "best_relaxed_case": best,
                "cascade_minimum_xor2": 98,
                "output": str(args.output),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
