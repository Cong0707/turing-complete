#!/usr/bin/env python3
"""Audit one duplicated first-layer pair in the fixed 61-XOR RNG DAG.

The duplicate has the same steady-state row but an independent pre-XOR
tick-zero label.  Every B consumer chooses one physical copy.  A raw copy may
still receive a per-consumer post-XOR one-bit label.  OR gates feeding equal
``(seed,state)`` leaves are shared globally, matching physical fanout.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import sys
import threading
import time

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Solver


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SRC = ROOT / "src"
for path in (HERE, SRC):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from search_post_or_fixed import PeakRssSampler  # noqa: E402
from tc_save_lab.rng_encoded_asic import (  # noqa: E402
    B,
    FIRST_LAYER,
    GATE_BY_OUTPUT,
    T,
    bits,
)


BITS = 32
FIXED_SHELL = 172
BASE_XOR = 61


def solve_duplicates(
    duplicate_pairs: frozenset[int],
    bound: int,
    timeout_seconds: float,
    solver_name: str,
    *,
    b_fanins_override: dict[int, tuple[int, ...]] | None = None,
    fixed_xor_override: int | None = None,
) -> dict[str, object]:
    if not duplicate_pairs or not duplicate_pairs <= FIRST_LAYER:
        raise ValueError("duplicate pair set is empty or outside the fixed first layer")
    started = time.monotonic()
    fixed_xor = (
        BASE_XOR + len(duplicate_pairs)
        if fixed_xor_override is None
        else fixed_xor_override
    )
    b_fanins_override = b_fanins_override or {}
    pool = IDPool()
    clauses: list[list[int]] = []

    def var(key: object) -> int:
        return pool.id(key)

    def at_most_one(values: list[int]) -> None:
        if len(values) <= 1:
            return
        clauses.extend(
            CardEnc.atmost(
                values, bound=1, vpool=pool, encoding=EncType.seqcounter
            ).clauses
        )

    def exactly_one(values: list[int]) -> None:
        if not values:
            raise AssertionError("empty exactly-one domain")
        clauses.append(values)
        at_most_one(values)

    def equiv_or(output: int, inputs: list[int]) -> None:
        unique = list(dict.fromkeys(inputs))
        if not unique:
            clauses.append([-output])
            return
        clauses.extend([-value, output] for value in unique)
        clauses.append([-output, *unique])

    def equiv_xor(output: int, left: int, right: int) -> None:
        clauses.extend((
            [-output, left, right],
            [-output, -left, -right],
            [output, -left, right],
            [output, left, -right],
        ))

    pairs = tuple(sorted(FIRST_LAYER))
    pair_set = frozenset(pairs)
    nodes_by_pair = {
        pair: tuple((pair, copy) for copy in range(2 if pair in duplicate_pairs else 1))
        for pair in pairs
    }
    raw = {
        node: var(("raw", *node))
        for nodes in nodes_by_pair.values()
        for node in nodes
    }
    pre_pin: dict[tuple[int, int, int, int], int] = {}
    pre_label: dict[tuple[int, int, int], int] = {}
    leaf_users: dict[tuple[int, int], list[int]] = defaultdict(list)
    for pair in pairs:
        state_bits = bits(pair)
        if len(state_bits) != 2:
            raise AssertionError("first-layer node is not a state pair")
        for node in nodes_by_pair[pair]:
            _, copy = node
            for side, state in enumerate(state_bits):
                side_values = []
                for seed in range(BITS):
                    pin = var(("pre-pin", pair, copy, side, seed))
                    pre_pin[pair, copy, side, seed] = pin
                    side_values.append(pin)
                    leaf_users[seed, state].append(pin)
                    clauses.append([-pin, -raw[node]])
                at_most_one(side_values)
            for seed in range(BITS):
                label = var(("pre-label", pair, copy, seed))
                pre_label[pair, copy, seed] = label
                equiv_xor(
                    label,
                    pre_pin[pair, copy, 0, seed],
                    pre_pin[pair, copy, 1, seed],
                )

    post_users: dict[tuple[int, int], list[int]] = defaultdict(list)
    occurrence_records: list[dict[str, object]] = []

    def pair_occurrence(tag: str, pair: int) -> list[int]:
        nodes = nodes_by_pair.get(pair)
        if not nodes:
            raise AssertionError(f"consumer requests absent pair {pair:08x}")
        selectors = [var(("select", tag, *node)) for node in nodes]
        exactly_one(selectors)
        all_post = []
        effective = []
        post_by_node: dict[tuple[int, int], tuple[int, ...]] = {}
        for node, selector in zip(nodes, selectors, strict=True):
            pair_value, copy = node
            post_values = []
            for seed in range(BITS):
                choice = var(("post-choice", tag, pair_value, copy, seed))
                post_values.append(choice)
                all_post.append(choice)
                post_users[pair, seed].append(choice)
                clauses.extend(([-choice, selector], [-choice, raw[node]]))
            post_by_node[node] = tuple(post_values)
        at_most_one(all_post)

        for seed in range(BITS):
            value = var(("pair-effective", tag, pair, seed))
            effective.append(value)
            for node, selector in zip(nodes, selectors, strict=True):
                _, copy = node
                choice = post_by_node[node][seed]
                candidate = var(("pair-candidate", tag, pair, copy, seed))
                # raw -> candidate == post choice
                clauses.extend((
                    [-raw[node], -candidate, choice],
                    [-raw[node], candidate, -choice],
                    # !raw -> candidate == this physical copy's pre-label
                    [raw[node], -candidate, pre_label[pair, copy, seed]],
                    [raw[node], candidate, -pre_label[pair, copy, seed]],
                    # selected copy drives the occurrence label.
                    [-selector, -value, candidate],
                    [-selector, value, -candidate],
                ))
        occurrence_records.append({
            "tag": tag,
            "kind": "pair",
            "steady": pair,
            "nodes": nodes,
            "selectors": tuple(selectors),
            "post_by_node": post_by_node,
            "effective": tuple(effective),
        })
        return effective

    def unit_occurrence(tag: str, state: int) -> list[int]:
        choices = []
        for seed in range(BITS):
            choice = var(("unit-choice", tag, state, seed))
            choices.append(choice)
            leaf_users[seed, state].append(choice)
        at_most_one(choices)
        occurrence_records.append({
            "tag": tag,
            "kind": "unit",
            "steady": 1 << state,
            "effective": tuple(choices),
        })
        return choices

    for output_index, (target, steady) in enumerate(zip(T, B, strict=True)):
        fanin_labels: list[list[int]] = []
        override = b_fanins_override.get(steady)
        if override is not None:
            if len(override) not in (1, 2):
                raise AssertionError("override fanin count must be one or two")
            combined = 0
            for fanin in override:
                combined ^= fanin
                if fanin in pair_set:
                    fanin_labels.append(
                        pair_occurrence(
                            f"B{output_index}-override{len(fanin_labels)}", fanin
                        )
                    )
                else:
                    state = bits(fanin)
                    if len(state) != 1:
                        raise AssertionError("override direct fanin is not a unit")
                    fanin_labels.append(
                        unit_occurrence(
                            f"B{output_index}-override{len(fanin_labels)}", state[0]
                        )
                    )
            if combined != steady:
                raise AssertionError("override fanins do not realize the B row")
        elif steady in pair_set:
            fanin_labels.append(pair_occurrence(f"B{output_index}-terminal", steady))
        elif steady.bit_count() == 1:
            fanin_labels.append(
                unit_occurrence(f"B{output_index}-terminal", bits(steady)[0])
            )
        else:
            gate = GATE_BY_OUTPUT.get(steady)
            if gate is None:
                raise AssertionError(f"no fixed decomposition for {steady:08x}")
            for side, fanin in enumerate((gate.left, gate.right)):
                if fanin in pair_set:
                    fanin_labels.append(
                        pair_occurrence(f"B{output_index}-side{side}", fanin)
                    )
                else:
                    state = bits(fanin)
                    if len(state) != 1:
                        raise AssertionError("direct fanin is not a unit")
                    fanin_labels.append(
                        unit_occurrence(f"B{output_index}-side{side}", state[0])
                    )
        if len(fanin_labels) not in (1, 2):
            raise AssertionError("unsupported B fanin count")
        for seed in range(BITS):
            expected = bool(target >> seed & 1)
            if len(fanin_labels) == 1:
                literal = fanin_labels[0][seed]
                clauses.append([literal if expected else -literal])
            else:
                left = fanin_labels[0][seed]
                right = fanin_labels[1][seed]
                if expected:
                    clauses.extend(([left, right], [-left, -right]))
                else:
                    clauses.extend(([-left, right], [left, -right]))

    leaf_atom = {key: var(("leaf-atom", *key)) for key in sorted(leaf_users)}
    for key, atom in leaf_atom.items():
        equiv_or(atom, leaf_users[key])
    post_atom = {key: var(("post-atom", *key)) for key in sorted(post_users)}
    for key, atom in post_atom.items():
        equiv_or(atom, post_users[key])
    cost_atoms = [*leaf_atom.values(), *post_atom.values()]
    if bound < len(cost_atoms):
        clauses.extend(
            CardEnc.atmost(
                cost_atoms,
                bound=bound,
                vpool=pool,
                encoding=EncType.mtotalizer,
            ).clauses
        )

    digest = hashlib.sha256()
    for clause in clauses:
        digest.update(" ".join(map(str, clause)).encode("ascii"))
        digest.update(b" 0\n")

    timer = None
    with PeakRssSampler() as memory:
        with Solver(name=solver_name, bootstrap_with=clauses) as sat_solver:
            if timeout_seconds:
                timer = threading.Timer(timeout_seconds, sat_solver.interrupt)
                timer.daemon = True
                timer.start()
            try:
                solved = (
                    sat_solver.solve_limited(expect_interrupt=True)
                    if timeout_seconds
                    else sat_solver.solve()
                )
            finally:
                if timer is not None:
                    timer.cancel()
            model = sat_solver.get_model() if solved is True else None
            stats = sat_solver.accum_stats()

    result: dict[str, object] = {
        "schema": 1,
        "scope": "fixed x61 DAG plus duplicated physical pairs; pre/post OR model",
        "status": "sat" if solved is True else "unsat" if solved is False else "unknown",
        "duplicate_pairs": [f"{pair:08x}" for pair in sorted(duplicate_pairs)],
        "or_bound": bound,
        "fixed_xor": fixed_xor,
        "total_gate_bound": FIXED_SHELL + fixed_xor * 3 + bound,
        "delay": 9,
        "cycles": 67,
        "elapsed_seconds": time.monotonic() - started,
        "variable_count": pool.top,
        "clause_count": len(clauses),
        "clause_sha256": digest.hexdigest(),
        "solver": solver_name,
        "solver_stats": stats,
        "peak_rss_bytes": memory.peak,
        "counts": {
            "physical_pair_nodes": sum(map(len, nodes_by_pair.values())),
            "B_occurrences": len(occurrence_records),
            "leaf_atoms": len(leaf_atom),
            "post_atoms": len(post_atom),
        },
    }
    if model is not None:
        positive = {literal for literal in model if literal > 0}
        selected_leaf = sorted(key for key, atom in leaf_atom.items() if atom in positive)
        selected_post = sorted(key for key, atom in post_atom.items() if atom in positive)
        actual_or = len(selected_leaf) + len(selected_post)
        modes = []
        for pair in pairs:
            for node in nodes_by_pair[pair]:
                _, copy = node
                mode = "raw-post" if raw[node] in positive else "pre-xor"
                label = sum(
                    1 << seed
                    for seed in range(BITS)
                    if pre_label[pair, copy, seed] in positive
                )
                pins = [
                    next((
                        seed
                        for seed in range(BITS)
                        if pre_pin[pair, copy, side, seed] in positive
                    ), None)
                    for side in range(2)
                ]
                modes.append({
                    "pair": f"{pair:08x}",
                    "copy": copy,
                    "mode": mode,
                    "pre_label": f"{label:08x}",
                    "pin_seed_bits": pins,
                })
        occurrences = []
        for record in occurrence_records:
            item = {
                "tag": record["tag"],
                "kind": record["kind"],
                "steady": f"{int(record['steady']):08x}",
                "effective_label": f"{sum(1 << seed for seed, value in enumerate(record['effective']) if value in positive):08x}",
            }
            if record["kind"] == "pair":
                selected_index = next(
                    index
                    for index, selector in enumerate(record["selectors"])
                    if selector in positive
                )
                node = record["nodes"][selected_index]
                item["selected_copy"] = node[1]
                post = record["post_by_node"][node]
                item["post_seed_bit"] = next((
                    seed for seed, value in enumerate(post) if value in positive
                ), None)
            occurrences.append(item)
        result["certificate"] = {
            "or_count": actual_or,
            "logic_gate": fixed_xor * 3 + actual_or,
            "total_gate": FIXED_SHELL + fixed_xor * 3 + actual_or,
            "leaf_atoms": [
                {"seed": seed, "state": state} for seed, state in selected_leaf
            ],
            "post_atoms": [
                {"seed": seed, "pair": f"{pair:08x}"}
                for pair, seed in selected_post
            ],
            "pair_modes": modes,
            "B_occurrences": occurrences,
        }
        if actual_or > bound:
            raise AssertionError("extracted certificate exceeds OR bound")
    return result


def solve_duplicate(
    duplicate_pair: int,
    bound: int,
    timeout_seconds: float,
    solver_name: str,
) -> dict[str, object]:
    """Backward-compatible single-copy entry point."""

    result = solve_duplicates(
        frozenset((duplicate_pair,)), bound, timeout_seconds, solver_name
    )
    result["duplicate_pair"] = f"{duplicate_pair:08x}"
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--or-bound", type=int, default=42)
    parser.add_argument("--timeout-per-case", type=float, default=60.0)
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--stop", type=int)
    parser.add_argument(
        "--output", type=Path, default=HERE / "post-or-duplicate-pair-b42.json"
    )
    args = parser.parse_args()
    pairs = tuple(sorted(FIRST_LAYER))
    stop = len(pairs) if args.stop is None else min(args.stop, len(pairs))
    if not 0 <= args.start <= stop:
        raise ValueError("invalid --start/--stop range")
    started = time.monotonic()
    cases = []
    winner = None
    for index in range(args.start, stop):
        result = solve_duplicate(
            pairs[index], args.or_bound, args.timeout_per_case, args.solver
        )
        cases.append({
            "index": index,
            "duplicate_pair": result["duplicate_pair"],
            "status": result["status"],
            "elapsed_seconds": result["elapsed_seconds"],
            "peak_rss_bytes": result["peak_rss_bytes"],
            "clause_sha256": result["clause_sha256"],
        })
        if result["status"] == "sat":
            winner = result
            break
    statuses = {
        status: sum(case["status"] == status for case in cases)
        for status in ("sat", "unsat", "unknown")
    }
    document = {
        "schema": 1,
        "scope": "all single first-layer pair duplications of the fixed x61 DAG",
        "or_bound": args.or_bound,
        "target_total_gate": FIXED_SHELL + (BASE_XOR + 1) * 3 + args.or_bound,
        "range": [args.start, stop],
        "case_count": len(pairs),
        "statuses": statuses,
        "cases": cases,
        "winner": winner,
        "elapsed_seconds": time.monotonic() - started,
    }
    args.output.write_text(
        json.dumps(document, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "range": document["range"],
        "statuses": statuses,
        "winner_gate": (
            winner.get("certificate", {}).get("total_gate")
            if isinstance(winner, dict) else None
        ),
        "elapsed_seconds": document["elapsed_seconds"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
