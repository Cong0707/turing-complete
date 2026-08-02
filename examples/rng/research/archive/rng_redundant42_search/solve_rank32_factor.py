"""Bounded Z3 search for a rank-32 42-state RNG lifting.

This searches the restricted family where the ten redundant natural-state
rows are selected from ``u_i = x_i XOR x_(i+13)``.  The 42-state transition
and 32 visible rows are parameterized as

    O = [I | V]
    E = [A + V R; R]
    H = E O = [E | E V]

so ``H [I;0] = E``, ``H E = E A``, and ``O E = A`` hold identically.  Z3
only has to enforce that every row of H and O has support at most four.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import time

from z3 import And, AtMost, BitVec, BitVecVal, Extract, Not, Or, Solver, sat


BITS = 32
AUX = 10
MASK = (1 << BITS) - 1


def xorshift32(value: int) -> int:
    value ^= value >> 13
    value ^= (value << 17) & MASK
    value ^= value >> 5
    return value & MASK


def transition_rows() -> tuple[int, ...]:
    rows = [0] * BITS
    for source in range(BITS):
        output = xorshift32(1 << source)
        for target in range(BITS):
            rows[target] |= ((output >> target) & 1) << source
    return tuple(rows)


A = transition_rows()
SPARSE_MASKS = tuple(mask for mask in range(1 << AUX) if mask.bit_count() <= 3)


def parse_frontier(path: Path) -> tuple[tuple[int, ...], ...]:
    candidates: list[tuple[int, ...]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.search(r"\brows=([0-9,]+)$", line)
        if match:
            rows = tuple(int(value) for value in match.group(1).split(","))
            if len(rows) != AUX or len(set(rows)) != AUX:
                raise ValueError(f"invalid frontier row: {line}")
            candidates.append(rows)
    return tuple(candidates)


def parse_pair_frontier(path: Path) -> tuple[tuple[int, ...], ...]:
    candidates: list[tuple[int, ...]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.search(r"\bR=([0-9a-f,]+)$", line)
        if match:
            rows = tuple(int(value, 16) for value in match.group(1).split(","))
            if (
                len(rows) != AUX
                or len(set(rows)) != AUX
                or any(not 2 <= row.bit_count() <= 4 for row in rows)
            ):
                raise ValueError(f"invalid pair frontier row: {line}")
            candidates.append(rows)
    return tuple(candidates)


def xor_selected(rows: tuple[int, ...], mask: int) -> int:
    value = 0
    for index, row in enumerate(rows):
        if (mask >> index) & 1:
            value ^= row
    return value


def bitvec_weight_at_most(value: object, limit: int) -> object:
    bits = tuple(Extract(bit, bit, value) == 1 for bit in range(AUX))
    if limit < 0:
        return False
    if limit == 0:
        return And(*(Not(bit) for bit in bits))
    if limit >= AUX:
        return True
    return AtMost(*bits, limit)


def solve_candidate(
    redundant: tuple[int, ...], timeout_ms: int
) -> tuple[str, dict[str, object] | None, float]:
    if len(redundant) != AUX:
        raise ValueError(f"expected {AUX} redundant rows, got {len(redundant)}")
    domains: list[tuple[tuple[int, int], ...]] = []
    for target in A:
        domain = tuple(
            (mask, target ^ xor_selected(redundant, mask))
            for mask in SPARSE_MASKS
            if (target ^ xor_selected(redundant, mask)).bit_count() <= 4
        )
        if not domain:
            return "support-unsat", None, 0.0
        domains.append(domain)

    labels = tuple(BitVec(f"v_{index}", AUX) for index in range(BITS))
    solver = Solver()
    solver.set(timeout=timeout_ms)

    for index, domain in enumerate(domains):
        choices = []
        for mask, residual in domain:
            parity = BitVecVal(0, AUX)
            for source in range(BITS):
                if (residual >> source) & 1:
                    parity = parity ^ labels[source]
            choices.append(
                And(
                    labels[index] == mask,
                    bitvec_weight_at_most(parity, 4 - residual.bit_count()),
                )
            )
        solver.add(Or(*choices))

    for row in redundant:
        parity = BitVecVal(0, AUX)
        for source in range(BITS):
            if (row >> source) & 1:
                parity = parity ^ labels[source]
        solver.add(bitvec_weight_at_most(parity, 4 - row.bit_count()))

    started = time.monotonic()
    result = solver.check()
    elapsed = time.monotonic() - started
    if result != sat:
        return str(result), None, elapsed

    model = solver.model()
    v_rows = tuple(model.eval(label).as_long() for label in labels)
    e_rows = tuple(
        target ^ xor_selected(redundant, v_rows[index])
        for index, target in enumerate(A)
    ) + redundant

    # Keep certificate construction explicit; Python XOR is clearer than a
    # clever reduction here and this path runs only after SAT.
    h_rows_list: list[int] = []
    for row in e_rows:
        parity = 0
        for source in range(BITS):
            if (row >> source) & 1:
                parity ^= v_rows[source]
        h_rows_list.append(row | (parity << BITS))
    o_rows = tuple((1 << index) | (v_rows[index] << BITS) for index in range(BITS))

    if any(row.bit_count() > 4 for row in h_rows_list + list(o_rows)):
        raise AssertionError("Z3 model violates the row-support bound")

    certificate = {
        "redundant_rows_hex": [f"{row:08x}" for row in redundant],
        "V_rows_hex": [f"{row:03x}" for row in v_rows],
        "E_rows_hex": [f"{row:08x}" for row in e_rows],
        "H_rows_hex_42bit": [f"{row:011x}" for row in h_rows_list],
        "O_rows_hex_42bit": [f"{row:011x}" for row in o_rows],
        "max_H_weight": max(row.bit_count() for row in h_rows_list),
        "max_O_weight": max(row.bit_count() for row in o_rows),
    }
    return "sat", certificate, elapsed


def main() -> None:
    parser = argparse.ArgumentParser()
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--frontier", type=Path)
    source.add_argument("--pair-frontier", type=Path)
    parser.add_argument("--timeout-ms", type=int, default=2_000)
    parser.add_argument("--limit", type=int, default=1_000)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    if args.timeout_ms <= 0 or args.limit <= 0:
        parser.error("--timeout-ms and --limit must be positive")

    if args.frontier:
        candidates = tuple(
            tuple((1 << index) ^ (1 << (index + 13)) for index in selected)
            for selected in parse_frontier(args.frontier)
        )[: args.limit]
    else:
        candidates = parse_pair_frontier(args.pair_frontier)[: args.limit]
    results: list[dict[str, object]] = []
    for index, redundant in enumerate(candidates, 1):
        status, certificate, elapsed = solve_candidate(redundant, args.timeout_ms)
        row_text = ",".join(f"{row:08x}" for row in redundant)
        print(
            f"[{index}/{len(candidates)}] R={row_text} "
            f"status={status} seconds={elapsed:.3f}",
            flush=True,
        )
        results.append(
            {
                "redundant_rows_hex": [f"{row:08x}" for row in redundant],
                "status": status,
                "seconds": elapsed,
            }
        )
        if certificate is not None:
            payload = {"status": "sat", "certificate": certificate, "attempts": results}
            if args.output:
                args.output.write_text(
                    json.dumps(payload, indent=2) + "\n", encoding="utf-8"
                )
            return

    payload = {"status": "no-sat-candidate", "attempts": results}
    if args.output:
        args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
