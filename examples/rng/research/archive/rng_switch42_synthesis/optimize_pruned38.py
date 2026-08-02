"""Exact two-level XOR2/XOR3 cover model for active-tradeoff points.

The historical default point has four identically-zero hidden states.  A
candidate can also be loaded from a ``search_active_state_tradeoff`` log.
Hidden coordinates that are identically zero from the strict zero initial
state are removed before all unordered partitions are generated:

* pair group: native XOR2, cost 3, delay 2;
* triple group: verified Switch XOR3, cost 12, delay 2;
* two groups: final native XOR2, cost 3, another delay 2;
* three groups: final Switch XOR3, cost 12, another delay 2.

All pair/triple groups are globally shared.  Thus a SAT result is a complete
logical network certificate for this restricted library, while UNSAT at a
budget is an exact exclusion of the library for this state point.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
import re
import time

from z3 import Bool, If, Or, PbEq, PbLe, Solver, is_true


VISIBLE = 32
MASK32 = (1 << VISIBLE) - 1

X_ROWS = tuple(
    int(value, 16)
    for value in (
        "000,000,001,010,084,002,001,001,000,200,000,001,000,204,000,000,"
        "000,080,206,001,010,004,006,000,001,010,004,000,000,000,284,000"
    ).split(",")
)
D_ROWS = tuple(
    int(value, 16)
    for value in (
        "00001100080,20004840000,20204400000,00000000000,01002200100,"
        "00000000000,00000000000,00200022000,00000000000,20400404000"
    ).split(",")
)

LOG_PATTERN = re.compile(
    r"^(?P<prefix>.*?)\bX=(?P<x>[0-9a-fA-F]+(?:,[0-9a-fA-F]+)*)"
    r"\s+D=(?P<d>[0-9a-fA-F]+(?:,[0-9a-fA-F]+)*)\s*$"
)
STAT_PATTERN = re.compile(
    r"\b(unsupported|excess4|max|base|active_hidden|optimistic_total_gate|"
    r"switch_proxy_total|defect|total)=(-?\d+)"
)


@dataclass(frozen=True)
class Candidate:
    x_rows: tuple[int, ...]
    d_rows: tuple[int, ...]
    source_lines: tuple[int, ...] = ()
    reported_stats: tuple[tuple[str, int], ...] = ()

    @property
    def reported(self) -> dict[str, int]:
        return dict(self.reported_stats)


def validate_candidate(candidate: Candidate) -> None:
    if len(candidate.x_rows) != VISIBLE:
        raise ValueError(f"candidate has {len(candidate.x_rows)} X rows, expected {VISIBLE}")
    hidden = len(candidate.d_rows)
    if hidden == 0:
        raise ValueError("candidate must contain at least one hidden row")
    hidden_mask = (1 << hidden) - 1
    state_mask = (1 << (VISIBLE + hidden)) - 1
    if any(row < 0 or row & ~hidden_mask for row in candidate.x_rows):
        raise ValueError(f"X row exceeds the {hidden}-bit hidden-state width")
    if any(row < 0 or row & ~state_mask for row in candidate.d_rows):
        raise ValueError(f"D row exceeds the {VISIBLE + hidden}-bit state width")


def default_candidate() -> Candidate:
    return Candidate(X_ROWS, D_ROWS)


def load_log_candidates(path: Path, selection: str) -> tuple[Candidate, ...]:
    """Parse the last candidate or every distinct candidate from a search log."""
    parsed: list[Candidate] = []
    for line_number, line in enumerate(path.read_text(encoding="ascii").splitlines(), 1):
        match = LOG_PATTERN.match(line.strip())
        if not match:
            continue
        candidate = Candidate(
            tuple(int(value, 16) for value in match.group("x").split(",")),
            tuple(int(value, 16) for value in match.group("d").split(",")),
            (line_number,),
            tuple((key, int(value)) for key, value in STAT_PATTERN.findall(match.group("prefix"))),
        )
        validate_candidate(candidate)
        parsed.append(candidate)
    if not parsed:
        raise ValueError(f"no active-tradeoff candidates found in {path}")
    if selection == "last":
        return (parsed[-1],)
    if selection != "all":
        raise ValueError(f"unsupported candidate selection: {selection}")

    # Search logs print the current best again on exit.  Solve every distinct
    # X/D point once while retaining all source line numbers as provenance.
    unique: dict[tuple[tuple[int, ...], tuple[int, ...]], Candidate] = {}
    for candidate in parsed:
        key = candidate.x_rows, candidate.d_rows
        previous = unique.get(key)
        if previous is None:
            unique[key] = candidate
        else:
            unique[key] = Candidate(
                candidate.x_rows,
                candidate.d_rows,
                previous.source_lines + candidate.source_lines,
                candidate.reported_stats,
            )
    return tuple(unique.values())


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


def apply_row(row: int, matrix: tuple[int, ...]) -> int:
    result = 0
    while row:
        low = row & -row
        result ^= matrix[low.bit_length() - 1]
        row ^= low
    return result


def apply_matrix(matrix: tuple[int, ...], value: int) -> int:
    return sum(((row & value).bit_count() & 1) << index for index, row in enumerate(matrix))


def reachable_hidden_rows(full_h: tuple[int, ...], hidden: int) -> tuple[int, ...]:
    """Return hidden coordinates nonzero on H^t [seed; 0], for any t/seed."""
    symbolic = tuple(1 << index for index in range(VISIBLE)) + (0,) * hidden
    active: set[int] = set()
    # Cayley-Hamilton makes the first state_bits powers sufficient.
    for _ in range(len(full_h)):
        active.update(
            index
            for index in range(hidden)
            if symbolic[VISIBLE + index]
        )
        symbolic = tuple(apply_row(row, symbolic) for row in full_h)
    return tuple(sorted(active))


def build_pruned(
    x_rows: tuple[int, ...] = X_ROWS,
    d_rows: tuple[int, ...] = D_ROWS,
) -> tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]:
    candidate = Candidate(x_rows, d_rows)
    validate_candidate(candidate)
    a_rows = transition_rows()
    output = tuple((1 << index) | (x_rows[index] << VISIBLE) for index in range(VISIBLE))
    top = tuple(
        apply_row(a_rows[index], output) ^ apply_row(x_rows[index], d_rows)
        for index in range(VISIBLE)
    )
    full_h = top + d_rows
    active_hidden = reachable_hidden_rows(full_h, len(d_rows))
    kept_columns = tuple(range(VISIBLE)) + tuple(VISIBLE + index for index in active_hidden)

    def project(row: int) -> int:
        return sum(((row >> old) & 1) << new for new, old in enumerate(kept_columns))

    h_rows = tuple(project(full_h[index]) for index in kept_columns)
    o_rows = tuple(project(row) for row in output)
    return h_rows, o_rows, active_hidden


def verify_sequences(h_rows: tuple[int, ...], o_rows: tuple[int, ...]) -> None:
    for seed in range(256):
        state = apply_matrix(h_rows, seed)
        natural = seed
        for cycle in range(65):
            natural = xorshift32(natural)
            if apply_matrix(o_rows, state) != natural:
                raise AssertionError(f"sequence mismatch seed={seed} cycle={cycle}")
            state = apply_matrix(h_rows, state)


def gf2_basis(vectors: tuple[int, ...] | list[int]) -> tuple[int, ...]:
    pivots: dict[int, int] = {}
    for vector in vectors:
        reduced = vector
        while reduced:
            pivot = reduced.bit_length() - 1
            if pivot in pivots:
                reduced ^= pivots[pivot]
            else:
                pivots[pivot] = reduced
                break
    return tuple(pivots[pivot] for pivot in sorted(pivots, reverse=True))


def cross_care_audit(
    h_rows: tuple[int, ...],
    o_rows: tuple[int, ...],
) -> dict[str, int]:
    """Optimistic H/O sharing classes on states common to cycles 1..64.

    Ignoring the H-only tick 0 and O-only tick 65 can only merge more
    functions, so the resulting gate-output count remains a sound lower
    bound for the complete 66-cycle circuit.
    """
    columns = tuple(1 << index for index in range(VISIBLE))
    timed_columns: list[tuple[int, ...]] = [columns]
    for _ in range(65):
        columns = tuple(apply_matrix(h_rows, column) for column in columns)
        timed_columns.append(columns)
    basis = gf2_basis([
        column
        for cycle in range(1, 65)
        for column in timed_columns[cycle]
    ])

    def signature(row: int) -> int:
        return sum(
            ((row & vector).bit_count() & 1) << index
            for index, vector in enumerate(basis)
        )

    wire_signatures = {signature(1 << bit) for bit in range(len(h_rows))}
    target_signatures = {signature(row) for row in h_rows + o_rows}
    nonwire = target_signatures - wire_signatures - {0}
    return {
        "cycles_first": 1,
        "cycles_last": 64,
        "reachable_rank": len(basis),
        "distinct_target_classes": len(target_signatures),
        "distinct_wire_classes": len(wire_signatures),
        "distinct_nonwire_target_classes": len(nonwire),
        "logic_gate_lower_bound": 3 * len(nonwire),
    }


@lru_cache(maxsize=None)
def partitions(support: tuple[int, ...]) -> tuple[tuple[tuple[int, ...], ...], ...]:
    """All canonical set partitions into <=3 blocks, each of size <=3."""
    result: set[tuple[tuple[int, ...], ...]] = set()

    def visit(index: int, blocks: list[list[int]]) -> None:
        if index == len(support):
            canonical = tuple(sorted(tuple(block) for block in blocks))
            if len(canonical) <= 3 and all(len(block) <= 3 for block in canonical):
                result.add(canonical)
            return
        value = support[index]
        for block in blocks:
            if len(block) < 3:
                block.append(value)
                visit(index + 1, blocks)
                block.pop()
        if len(blocks) < 3:
            blocks.append([value])
            visit(index + 1, blocks)
            blocks.pop()

    visit(0, [])
    return tuple(sorted(result))


def block_mask(block: tuple[int, ...]) -> int:
    return sum(1 << bit for bit in block)


def option_final_cost(option: tuple[tuple[int, ...], ...]) -> int:
    if len(option) == 1:
        return 0
    if len(option) == 2:
        return 3
    if len(option) == 3:
        return 12
    raise AssertionError("invalid partition")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--budget", type=int, default=202)
    parser.add_argument("--timeout-ms", type=int, default=120000)
    parser.add_argument("--max-memory-mb", type=int, default=768)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    h_rows, o_rows, active_hidden = build_pruned()
    verify_sequences(h_rows, o_rows)
    target_rows = tuple(sorted({row for row in h_rows + o_rows if row.bit_count() >= 2}))
    if max(row.bit_count() for row in target_rows) > 9:
        raise AssertionError("three-group library only supports parity weight <=9")

    target_options: dict[int, tuple[tuple[tuple[int, ...], ...], ...]] = {}
    groups: set[int] = set()
    for target in target_rows:
        support = tuple(bit for bit in range(len(h_rows)) if (target >> bit) & 1)
        options = partitions(support)
        if not options:
            raise AssertionError(f"no legal partition for target {target:x}")
        target_options[target] = options
        for option in options:
            for block in option:
                if len(block) >= 2:
                    groups.add(block_mask(block))

    group_vars = {group: Bool(f"g_{group:x}") for group in sorted(groups)}
    option_vars: dict[tuple[int, int], object] = {}
    solver = Solver()
    solver.set(timeout=args.timeout_ms, max_memory=args.max_memory_mb)
    cost_terms = []
    for group, variable in group_vars.items():
        cost_terms.append((variable, 3 if group.bit_count() == 2 else 12))

    for target, options in target_options.items():
        variables = []
        for index, option in enumerate(options):
            variable = Bool(f"o_{target:x}_{index}")
            option_vars[target, index] = variable
            variables.append(variable)
            for block in option:
                if len(block) >= 2:
                    solver.add(Or(~variable, group_vars[block_mask(block)]))
            final_cost = option_final_cost(option)
            if final_cost:
                cost_terms.append((variable, final_cost))
        solver.add(PbEq([(variable, 1) for variable in variables], 1))

    solver.add(PbLe(cost_terms, args.budget))
    started = time.monotonic()
    status = solver.check()
    elapsed = time.monotonic() - started
    result: dict[str, object] = {
        "schema": 1,
        "scope": "pruned 38-state exact two-level XOR2/Switch-XOR3 shared cover",
        "status": str(status),
        "seconds": elapsed,
        "timeout_ms": args.timeout_ms,
        "max_memory_mb": args.max_memory_mb,
        "logic_budget": args.budget,
        "fixed_gate": 38 * 5 + 32 + 6,
        "target_gate_max": 430,
        "active_original_hidden_rows": list(active_hidden),
        "verified_sequences": {"seeds": 256, "outputs_per_seed": 65},
        "target_summary": {
            "distinct_nontrivial": len(target_rows),
            "weight_distribution": {
                str(weight): sum(row.bit_count() == weight for row in target_rows)
                for weight in sorted({row.bit_count() for row in target_rows})
            },
            "pair_or_triple_group_universe": len(groups),
            "partition_options": sum(len(options) for options in target_options.values()),
        },
        "H_rows_hex": [f"{row:010x}" for row in h_rows],
        "O_rows_hex": [f"{row:010x}" for row in o_rows],
    }
    if str(status) == "unknown":
        result["reason"] = solver.reason_unknown()
    elif str(status) == "sat":
        model = solver.model()
        selected_groups = [group for group, variable in group_vars.items() if is_true(model.eval(variable))]
        selected_options = {}
        logic_cost = sum(3 if group.bit_count() == 2 else 12 for group in selected_groups)
        for target, options in target_options.items():
            chosen = next(
                index for index in range(len(options))
                if is_true(model.eval(option_vars[target, index]))
            )
            option = options[chosen]
            logic_cost += option_final_cost(option)
            selected_options[f"{target:010x}"] = [
                [*block] for block in option
            ]
        if logic_cost > args.budget:
            raise AssertionError("extracted cover exceeds budget")
        result["solution"] = {
            "logic_gate": logic_cost,
            "total_gate": 38 * 5 + 32 + 6 + logic_cost,
            "delay": 9,
            "cycles": 66,
            "selected_groups": [
                {
                    "mask_hex": f"{group:010x}",
                    "support": [bit for bit in range(38) if (group >> bit) & 1],
                    "kind": "XOR2" if group.bit_count() == 2 else "Switch-XOR3",
                    "gate": 3 if group.bit_count() == 2 else 12,
                }
                for group in selected_groups
            ],
            "target_partitions": selected_options,
        }

    encoded = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode("ascii")
    args.output.write_bytes(encoded)
    print(json.dumps({
        "status": result["status"],
        "seconds": elapsed,
        "targets": len(target_rows),
        "groups": len(groups),
        "options": result["target_summary"]["partition_options"],
        "solution": result.get("solution"),
        "sha256": sha256(encoded).hexdigest(),
    }, indent=2))


if __name__ == "__main__":
    main()
