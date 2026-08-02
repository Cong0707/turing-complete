"""Audit Switch-assisted repairs of the recorded 42-state RNG frontier.

This is deliberately a certificate generator, not a save-file generator.  It
reconstructs the reachable subspace, finds all linear relations valid after
the load tick, and accounts for the three weight-five feedback rows under the
exact Bit Switch/XNOR timing model.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path


VISIBLE = 32
STATES = 42
CYCLES = 65
MASK32 = (1 << VISIBLE) - 1


def xorshift32(value: int) -> int:
    value ^= value >> 13
    value ^= (value << 17) & MASK32
    value ^= value >> 5
    return value & MASK32


def apply_matrix(rows: tuple[int, ...], value: int) -> int:
    return sum(((row & value).bit_count() & 1) << index for index, row in enumerate(rows))


def row_reduce(rows: list[int], width: int) -> tuple[list[int], list[int]]:
    work = [row for row in rows if row]
    pivots: list[int] = []
    rank = 0
    for column in range(width - 1, -1, -1):
        selected = next(
            (index for index in range(rank, len(work)) if (work[index] >> column) & 1),
            None,
        )
        if selected is None:
            continue
        work[rank], work[selected] = work[selected], work[rank]
        for index in range(len(work)):
            if index != rank and ((work[index] >> column) & 1):
                work[index] ^= work[rank]
        pivots.append(column)
        rank += 1
    return work[:rank], pivots


def nullspace(rows: list[int], width: int) -> tuple[int, ...]:
    reduced, pivots = row_reduce(rows, width)
    free = [column for column in range(width) if column not in pivots]
    basis: list[int] = []
    for column in free:
        value = 1 << column
        for row, pivot in zip(reduced, pivots):
            if (row >> column) & 1:
                value |= 1 << pivot
        basis.append(value)
    return tuple(basis)


def span(basis: tuple[int, ...]) -> tuple[int, ...]:
    values = [0]
    for vector in basis:
        values.extend(value ^ vector for value in tuple(values))
    return tuple(values)


def bits(value: int) -> list[int]:
    return [index for index in range(STATES) if (value >> index) & 1]


def canonical(value: int, relations: tuple[int, ...]) -> int:
    return min(value ^ relation for relation in relations)


def load_frontier(path: Path) -> tuple[tuple[int, ...], tuple[int, ...]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return (
        tuple(int(value, 16) for value in payload["H_rows_hex"]),
        tuple(int(value, 16) for value in payload["O_rows_hex"]),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--frontier", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    h_rows, o_rows = load_frontier(args.frontier)
    if len(h_rows) != STATES or len(o_rows) != VISIBLE:
        raise AssertionError("unexpected frontier dimensions")

    reachable_vectors: list[int] = []
    for source in range(VISIBLE):
        state = 1 << source
        for _ in range(CYCLES):
            state = apply_matrix(h_rows, state)
            reachable_vectors.append(state)
    reduced, _ = row_reduce(reachable_vectors, STATES)
    annihilator_basis = nullspace(reachable_vectors, STATES)
    annihilator = span(annihilator_basis)
    if len(annihilator_basis) != STATES - len(reduced):
        raise AssertionError("rank/nullity mismatch")

    # The relations are valid for every steady state but not for raw load S.
    load_vectors = [1 << index for index in range(VISIBLE)]
    load_plus_steady_rank = len(row_reduce(reachable_vectors + load_vectors, STATES)[0])

    # Re-verify the full 256-seed protocol, not only the small historical set.
    for seed in range(256):
        state = apply_matrix(h_rows, seed)
        natural = seed
        for _ in range(CYCLES):
            natural = xorshift32(natural)
            if apply_matrix(o_rows, state) != natural:
                raise AssertionError(f"sequence mismatch for seed {seed:08x}")
            state = apply_matrix(h_rows, state)

    classes: dict[int, list[dict[str, int | str]]] = {}
    for branch, rows in (("H", h_rows), ("O", o_rows)):
        for index, row in enumerate(rows):
            key = canonical(row, annihilator)
            classes.setdefault(key, []).append(
                {"branch": branch, "index": index, "row_hex": f"{row:011x}"}
            )

    class_weight_distribution: dict[str, int] = {}
    nontrivial_classes = 0
    for representative in classes:
        weight = min((representative ^ relation).bit_count() for relation in annihilator)
        class_weight_distribution[str(weight)] = class_weight_distribution.get(str(weight), 0) + 1
        nontrivial_classes += weight >= 2

    bad_rows = []
    for index, row in enumerate(h_rows):
        minimum = min((row ^ relation for relation in annihilator), key=lambda item: item.bit_count())
        if minimum.bit_count() <= 4:
            continue
        p4_options = []
        for selector in bits(minimum):
            parity4 = minimum ^ (1 << selector)
            matches = []
            parity4_class = canonical(parity4, annihilator)
            for other_index, other_row in enumerate(h_rows):
                if canonical(other_row, annihilator) == parity4_class:
                    matches.append({"branch": "H", "index": other_index})
            for other_index, other_row in enumerate(o_rows):
                if canonical(other_row, annihilator) == parity4_class:
                    matches.append({"branch": "O", "index": other_index})
            p4_options.append(
                {
                    "selector": selector,
                    "parity4_hex": f"{parity4:011x}",
                    "existing_target_matches": matches,
                }
            )
        bad_rows.append(
            {
                "index": index,
                "row_hex": f"{row:011x}",
                "support": bits(row),
                "minimum_steady_coset_weight": minimum.bit_count(),
                "minimum_steady_coset_hex": f"{minimum:011x}",
                "parity4_options": p4_options,
            }
        )

    # For a parity4 p and selector s, XOR5 can be made at delay five by
    # producing p and !p with final XOR/XNOR gates in parallel, then selecting
    # them with two mutually-exclusive Switches.  A NOT generates !s.
    switch_template = {
        "function": "xor5 = mux(selector, not(parity4), parity4)",
        "components": {
            "parity4_pair_xor": 2,
            "parity4_final_xor": 1,
            "parity4_final_xnor": 1,
            "selector_not": 1,
            "bit_switch": 2,
        },
        "gate_cost_without_sharing": 17,
        "maximum_delay_from_raw_leaf": 5,
        "mutual_exclusion": "selector and NOT(selector)",
        "all_z_possible": False,
    }

    # Scoped lower bound: every distinct nontrivial linear target needs its
    # own XOR/XNOR result in an XOR-linear implementation, before any pair
    # intermediates or Switch repair overhead is counted.
    fixed_gate_cost = 42 * 5 + 32 + 6
    linear_final_gate_lower_bound = 3 * nontrivial_classes
    scoped_total_lower_bound = fixed_gate_cost + linear_final_gate_lower_bound

    result = {
        "schema": 1,
        "scope": "recorded 42-state frontier with exact steady reachable-space equivalence",
        "verified_sequences": {"seeds": 256, "outputs_per_seed": CYCLES},
        "reachable_subspace": {
            "steady_rank": len(reduced),
            "load_plus_steady_rank": load_plus_steady_rank,
            "annihilator_dimension": len(annihilator_basis),
            "annihilator_basis_hex": [f"{row:011x}" for row in annihilator_basis],
        },
        "target_equivalence_classes": {
            "total": len(classes),
            "nontrivial_linear": nontrivial_classes,
            "minimum_weight_distribution": class_weight_distribution,
        },
        "bad_feedback_rows": bad_rows,
        "xor5_switch_template": switch_template,
        "scoped_cost_exclusion": {
            "assumption": "all steady target functions remain linear XOR/XNOR nodes; no sample-only nonlinear resynthesis",
            "delay_bits": 210,
            "load_or": 32,
            "ready_control": 6,
            "fixed_gate_cost": fixed_gate_cost,
            "distinct_nontrivial_final_nodes": nontrivial_classes,
            "linear_final_gate_lower_bound": linear_final_gate_lower_bound,
            "pair_intermediates_and_switch_overhead_counted": 0,
            "total_gate_lower_bound": scoped_total_lower_bound,
            "target_gate_max": 430,
            "excluded": scoped_total_lower_bound > 430,
        },
        "conclusion": (
            "Switch+XNOR can realize each weight-five parity at leaf delay five, but the "
            "recorded matrix is already above gate 430 before pair intermediates and the "
            "Switch repairs are counted; a different state/output encoding is required."
        ),
    }
    encoded = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode("ascii")
    args.output.write_bytes(encoded)
    print(json.dumps({
        "sha256": sha256(encoded).hexdigest(),
        "steady_rank": len(reduced),
        "annihilator": [f"{row:011x}" for row in annihilator_basis],
        "bad_rows": [entry["index"] for entry in bad_rows],
        "nontrivial_classes": nontrivial_classes,
        "scoped_gate_lower_bound": scoped_total_lower_bound,
    }, indent=2))


if __name__ == "__main__":
    main()
