"""Exact no-RAM Switch/OR audit for the radius-14 x56 RNG frontier.

The CNF jointly selects pair/unit mediation, realizes every pair tick-zero
label on its two physical state pins, counts the union of seed/state OR leaves,
and enforces the true gate budget ``3 * XOR + OR <= 221``.  Every pair cover
is enumerated completely before solving.  A SAT result is replayed through the
existing matrix and 65-tick verifier; an UNSAT result excludes that cover in
this depth-two, 10-delay topology.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time
from typing import Any, Iterable


BITS = 32
XOR_TARGET = 56
WEIGHTED_BUDGET = 221
FIXED_SHELL = 166


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def matrix(record: dict[str, Any], key: str) -> tuple[int, ...]:
    values = record[key]
    if not isinstance(values, list) or len(values) != BITS:
        raise ValueError(f"{key} must contain 32 rows")
    return tuple(int(str(value), 16) for value in values)


def bits(mask: int) -> tuple[int, ...]:
    return tuple(bit for bit in range(BITS) if mask >> bit & 1)


@dataclass(frozen=True)
class MediationOption:
    name: str
    kind: str
    pairs: tuple[int, ...]


def mediation_options(
    steady: int, selected_pairs: frozenset[int]
) -> tuple[MediationOption, ...]:
    options = [MediationOption("direct", "direct", ())]
    weight = steady.bit_count()
    if weight == 2:
        left, right = bits(steady)
        for common in range(BITS):
            if common in (left, right):
                continue
            first = (1 << left) | (1 << common)
            second = (1 << right) | (1 << common)
            if first in selected_pairs and second in selected_pairs:
                options.append(
                    MediationOption(
                        f"pair:{first:08x}^{second:08x}",
                        "pair",
                        tuple(sorted((first, second))),
                    )
                )
    elif weight == 1:
        for pair in sorted(selected_pairs):
            if pair & steady and (pair ^ steady).bit_count() == 1:
                options.append(MediationOption(f"unit:{pair:08x}", "unit", (pair,)))
    return tuple(dict.fromkeys(options))


def cnf_fingerprint(clauses: Iterable[Iterable[int]]) -> str:
    digest = hashlib.sha256()
    for clause in clauses:
        digest.update(" ".join(str(value) for value in clause).encode("ascii"))
        digest.update(b" 0\n")
    return digest.hexdigest()


def add_conditional_bit(cnf, guard: int | None, literal: int, expected: int) -> None:
    clause = [literal if expected else -literal]
    if guard is not None:
        clause.insert(0, -guard)
    cnf.append(clause)


def add_conditional_xor(
    cnf, guard: int | None, left: int, right: int, expected: int
) -> None:
    prefix = [] if guard is None else [-guard]
    if expected:
        cnf.append(prefix + [-left, -right])
        cnf.append(prefix + [left, right])
    else:
        cnf.append(prefix + [-left, right])
        cnf.append(prefix + [left, -right])


def add_residual_unit(
    cnf,
    guard: int | None,
    label_vars: tuple[int, ...],
    target: int,
    state: int,
    mapping,
) -> None:
    """Constrain target XOR pair_label to zero or one mapped seed bit."""

    differences = tuple(
        -label if target >> seed & 1 else label
        for seed, label in enumerate(label_vars)
    )
    prefix = [] if guard is None else [-guard]
    for left in range(BITS):
        for right in range(left + 1, BITS):
            cnf.append(prefix + [-differences[left], -differences[right]])
    for seed, difference in enumerate(differences):
        cnf.append(prefix + [-difference, mapping(seed, state)])


@dataclass
class Encoding:
    cnf: Any
    pool: Any
    selected_pairs: frozenset[int]
    decompositions: dict[int, tuple[int, ...]]
    row_options: dict[int, tuple[MediationOption, ...]]
    choice_vars: dict[tuple[int, int], int]
    mapping_vars: dict[tuple[int, int], int]
    label_vars: dict[tuple[int, int], int]
    orientation_vars: dict[tuple[int, int, int], int]
    active_pair_vars: dict[int, int]
    fixed_pairs: frozenset[int]
    fixed_final_count: int


def build_encoding(
    dual,
    T: tuple[int, ...],
    B: tuple[int, ...],
    C: tuple[int, ...],
    selected_pairs: frozenset[int],
    weighted_budget: int,
) -> Encoding:
    from pysat.card import CardEnc, EncType
    from pysat.formula import CNF, IDPool

    pool = IDPool()
    cnf = CNF()
    heavy = tuple(
        row for row in dict.fromkeys((*B, *C)) if row.bit_count() in (3, 4)
    )
    decompositions: dict[int, tuple[int, ...]] = {}
    for row in heavy:
        options = tuple(
            option
            for option in dual.pair_partitions(row)
            if set(option) <= selected_pairs
        )
        if len(options) != 1:
            raise ValueError(
                f"expected one heavy decomposition for {row:08x}, got {len(options)}"
            )
        decompositions[row] = options[0]

    distinct_b = tuple(dict.fromkeys(B))
    row_options = {
        steady: mediation_options(steady, selected_pairs)
        if steady.bit_count() in (1, 2)
        else (MediationOption("direct", "direct", ()),)
        for steady in distinct_b
    }
    choice_vars: dict[tuple[int, int], int] = {}
    for steady, options in row_options.items():
        if len(options) == 1:
            continue
        variables = []
        for option_index in range(len(options)):
            variable = pool.id(("choice", steady, option_index))
            choice_vars[(steady, option_index)] = variable
            variables.append(variable)
        cnf.append(variables)
        for left in range(len(variables)):
            for right in range(left + 1, len(variables)):
                cnf.append([-variables[left], -variables[right]])

    mapping_vars: dict[tuple[int, int], int] = {}

    def mapping(seed: int, state: int) -> int:
        key = (seed, state)
        if key not in mapping_vars:
            mapping_vars[key] = pool.id(("mapping", seed, state))
        return mapping_vars[key]

    label_vars = {
        (pair, seed): pool.id(("label", pair, seed))
        for pair in selected_pairs
        for seed in range(BITS)
    }
    orientation_vars: dict[tuple[int, int, int], int] = {}
    for pair in sorted(selected_pairs):
        states = bits(pair)
        if len(states) != 2:
            raise AssertionError("selected pair is not weight two")
        for pin, state in enumerate(states):
            pin_vars = []
            for seed in range(BITS):
                variable = pool.id(("orientation", pair, pin, seed))
                orientation_vars[(pair, pin, seed)] = variable
                pin_vars.append(variable)
                cnf.append([-variable, label_vars[(pair, seed)]])
                cnf.append([-variable, mapping(seed, state)])
            for left in range(BITS):
                for right in range(left + 1, BITS):
                    cnf.append([-pin_vars[left], -pin_vars[right]])
        for seed in range(BITS):
            left = orientation_vars[(pair, 0, seed)]
            right = orientation_vars[(pair, 1, seed)]
            label = label_vars[(pair, seed)]
            cnf.append([-left, -right])
            cnf.append([-label, left, right])

    fixed_pairs = set(pair for option in decompositions.values() for pair in option)
    fixed_pairs.update(row for row in C if row.bit_count() == 2)
    pair_causes: dict[int, list[int]] = {pair: [] for pair in selected_pairs}
    mediated_choice_vars: list[int] = []
    for steady, options in row_options.items():
        if len(options) == 1:
            if steady.bit_count() == 2:
                fixed_pairs.add(steady)
            continue
        for option_index, option in enumerate(options):
            guard = choice_vars[(steady, option_index)]
            if option.kind == "direct":
                if steady.bit_count() == 2:
                    pair_causes[steady].append(guard)
            else:
                mediated_choice_vars.append(guard)
                for pair in option.pairs:
                    pair_causes[pair].append(guard)

    active_pair_vars: dict[int, int] = {}
    for pair in sorted(selected_pairs - fixed_pairs):
        causes = pair_causes[pair]
        if not causes:
            continue
        active = pool.id(("active_pair", pair))
        active_pair_vars[pair] = active
        for cause in causes:
            cnf.append([-cause, active])
        cnf.append([-active, *causes])

    def label_tuple(pair: int) -> tuple[int, ...]:
        return tuple(label_vars[(pair, seed)] for seed in range(BITS))

    for target, steady in zip(T, B, strict=True):
        weight = steady.bit_count()
        if weight == 1:
            options = row_options[steady]
            for option_index, option in enumerate(options):
                guard = None if len(options) == 1 else choice_vars[(steady, option_index)]
                if option.kind == "direct":
                    if target.bit_count() != 1:
                        cnf.append([] if guard is None else [-guard])
                    else:
                        direct_seed = bits(target)[0]
                        clause = [mapping(direct_seed, bits(steady)[0])]
                        if guard is not None:
                            clause.insert(0, -guard)
                        cnf.append(clause)
                elif option.kind == "unit":
                    pair = option.pairs[0]
                    state = bits(pair ^ steady)[0]
                    add_residual_unit(
                        cnf, guard, label_tuple(pair), target, state, mapping
                    )
                else:
                    raise AssertionError("unit row has a pair-mediation option")
        elif weight == 2:
            options = row_options[steady]
            for option_index, option in enumerate(options):
                guard = None if len(options) == 1 else choice_vars[(steady, option_index)]
                if option.kind == "direct":
                    labels = label_tuple(steady)
                    for seed, label in enumerate(labels):
                        add_conditional_bit(cnf, guard, label, target >> seed & 1)
                elif option.kind == "pair":
                    left_labels = label_tuple(option.pairs[0])
                    right_labels = label_tuple(option.pairs[1])
                    for seed, (left, right) in enumerate(zip(left_labels, right_labels)):
                        add_conditional_xor(
                            cnf, guard, left, right, target >> seed & 1
                        )
                else:
                    raise AssertionError("pair row has a unit-mediation option")
        elif weight == 3:
            pair = decompositions[steady][0]
            state = bits(steady ^ pair)[0]
            add_residual_unit(cnf, None, label_tuple(pair), target, state, mapping)
        elif weight == 4:
            left, right = decompositions[steady]
            left_labels = label_tuple(left)
            right_labels = label_tuple(right)
            for seed, (left_label, right_label) in enumerate(
                zip(left_labels, right_labels)
            ):
                add_conditional_xor(
                    cnf,
                    None,
                    left_label,
                    right_label,
                    target >> seed & 1,
                )
        else:
            raise ValueError(f"unsupported B row weight {weight}")

    fixed_final_count = len(heavy)
    fixed_gate_cost = 3 * (len(fixed_pairs) + fixed_final_count)
    variable_cost_literals = sorted(mapping_vars.values())
    for active in active_pair_vars.values():
        variable_cost_literals.extend((active, active, active))
    for mediated in mediated_choice_vars:
        variable_cost_literals.extend((mediated, mediated, mediated))
    remaining_budget = weighted_budget - fixed_gate_cost
    if remaining_budget < 0:
        cnf.append([])
    else:
        cardinality = CardEnc.atmost(
            lits=variable_cost_literals,
            bound=remaining_budget,
            vpool=pool,
            encoding=EncType.seqcounter,
        )
        cnf.extend(cardinality.clauses)

    return Encoding(
        cnf,
        pool,
        selected_pairs,
        decompositions,
        row_options,
        choice_vars,
        mapping_vars,
        label_vars,
        orientation_vars,
        active_pair_vars,
        frozenset(fixed_pairs),
        fixed_final_count,
    )


def selected_option(
    positive: set[int],
    steady: int,
    options: tuple[MediationOption, ...],
    choice_vars: dict[tuple[int, int], int],
) -> MediationOption:
    if len(options) == 1:
        return options[0]
    chosen = [
        option
        for index, option in enumerate(options)
        if choice_vars[(steady, index)] in positive
    ]
    if len(chosen) != 1:
        raise AssertionError("model does not select exactly one topology")
    return chosen[0]


def decode_and_verify(
    audit,
    dual,
    init,
    T,
    B,
    C,
    encoding: Encoding,
    model: list[int],
    weighted_budget: int,
):
    positive = {literal for literal in model if literal > 0}
    mediated: dict[int, tuple[int, int]] = {}
    mediated_units: dict[int, int] = {}
    selected_choices = {}
    for steady, options in encoding.row_options.items():
        option = selected_option(positive, steady, options, encoding.choice_vars)
        selected_choices[f"{steady:08x}"] = option.name
        if option.kind == "pair":
            mediated[steady] = (option.pairs[0], option.pairs[1])
        elif option.kind == "unit":
            mediated_units[steady] = option.pairs[0]

    active_pairs = set(encoding.fixed_pairs)
    active_pairs.update(
        pair
        for pair, variable in encoding.active_pair_vars.items()
        if variable in positive
    )
    decompositions = dict(encoding.decompositions)
    decompositions.update(mediated)
    mappings = frozenset(
        key for key, variable in encoding.mapping_vars.items() if variable in positive
    )
    pair_labels = {}
    orientations = {}
    for pair in sorted(active_pairs):
        label = sum(
            1 << seed
            for seed in range(BITS)
            if encoding.label_vars[(pair, seed)] in positive
        )
        pins = []
        for pin in range(2):
            seeds = [
                seed
                for seed in range(BITS)
                if encoding.orientation_vars[(pair, pin, seed)] in positive
            ]
            if len(seeds) > 1:
                raise AssertionError("pair pin has multiple seed labels")
            pins.append(None if not seeds else seeds[0])
        pair_labels[pair] = label
        orientations[pair] = (pins[0], pins[1])

    result = dual.DualResult(
        len(mappings), mappings, pair_labels, orientations, decompositions
    )
    audit.verify_candidate(
        init,
        T,
        B,
        C,
        frozenset(active_pairs),
        decompositions,
        mediated,
        mediated_units,
        result,
    )
    xor_count = len(active_pairs) + encoding.fixed_final_count + len(mediated) + len(mediated_units)
    weighted = 3 * xor_count + len(mappings)
    if weighted > weighted_budget:
        raise AssertionError("decoded model exceeds weighted gate budget")
    return {
        "selected_pair_gates": [f"{pair:08x}" for pair in sorted(active_pairs)],
        "decompositions": {
            f"{row:08x}": [f"{pair:08x}" for pair in option]
            for row, option in sorted(decompositions.items())
        },
        "mediated_pair_targets": {
            f"{row:08x}": [f"{pair:08x}" for pair in option]
            for row, option in sorted(mediated.items())
        },
        "mediated_unit_targets": {
            f"{row:08x}": f"{pair:08x}"
            for row, pair in sorted(mediated_units.items())
        },
        "selected_choices": selected_choices,
        "pair_labels": {
            f"{pair:08x}": f"{label:08x}"
            for pair, label in sorted(pair_labels.items())
        },
        "pair_pin_seed_bits": {
            f"{pair:08x}": list(orientations[pair])
            for pair in sorted(orientations)
        },
        "mode_pairs": [
            {"seed": seed, "state": state} for seed, state in sorted(mappings)
        ],
        "metrics": {
            "xor": xor_count,
            "or": len(mappings),
            "three_xor_plus_or": weighted,
            "gate": FIXED_SHELL + weighted,
            "delay": 10,
            "cycles": 66,
        },
    }


def solve(cnf, solver_name: str):
    from pysat.solvers import Solver

    started = time.perf_counter()
    with Solver(name=solver_name, bootstrap_with=cnf.clauses) as solver:
        satisfiable = solver.solve()
        model = solver.get_model() if satisfiable else None
    return ("sat" if satisfiable else "unsat"), model, time.perf_counter() - started


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source",
        type=Path,
        default=Path(".research/rng_word_residual_search/radius14-x56-neighbors.jsonl"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(".research/rng_x56_or10/radius14-strict.json"),
    )
    parser.add_argument("--first", type=int, default=1)
    parser.add_argument("--last", type=int)
    parser.add_argument("--state-limit", type=int, default=2_000_000)
    parser.add_argument("--solution-limit", type=int, default=200_000)
    parser.add_argument("--solvers", nargs="+", default=("g4", "cadical195"))
    parser.add_argument("--stop-on-sat", action="store_true")
    parser.add_argument("--weighted-budget", type=int, default=WEIGHTED_BUDGET)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    source = args.source if args.source.is_absolute() else root / args.source
    output = args.output if args.output.is_absolute() else root / args.output
    cover_module = load_module(
        "rng_x56_strict_cover",
        root / ".research/rng_switch_bdd_cover/batch_phase_audit.py",
    )
    audit = load_module(
        "rng_x56_strict_audit",
        root / ".research/rng_or_frontier/audit_mediated.py",
    )
    dual = load_module(
        "rng_x56_strict_dual",
        root / ".research/rng_cost387/search_basis_dualmode.py",
    )
    init = load_module(
        "rng_x56_strict_init",
        root / ".research/rng_init_reuse/verify_init_reuse.py",
    )
    records = [
        json.loads(line)
        for line in source.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    last = len(records) if args.last is None else min(args.last, len(records))
    indexed = list(enumerate(records[args.first - 1 : last], args.first))
    started = time.perf_counter()
    results = []
    cover_count = 0
    sat_count = 0
    truncated_count = 0
    mismatch_count = 0
    stop = False

    for source_line, record in indexed:
        T, B, C = (matrix(record, key) for key in ("T", "B", "C"))
        if init.compose(C, T) != init.A or init.compose(T, C) != B:
            raise AssertionError(f"matrix identity failed on line {source_line}")
        if int(record.get("xor", XOR_TARGET)) != XOR_TARGET:
            raise ValueError(f"line {source_line} is not x56")
        covers, visited, truncated = cover_module.enumerate_pair_covers(
            (*B, *C),
            XOR_TARGET,
            state_limit=args.state_limit,
            solution_limit=args.solution_limit,
        )
        truncated_count += int(truncated)
        line_result = {
            "source_line": source_line,
            "T": record["T"],
            "B": record["B"],
            "C": record["C"],
            "cover_search_visited": visited,
            "cover_search_truncated": truncated,
            "cover_count": len(covers),
            "covers": [],
        }
        for cover_index, selected_pairs in enumerate(covers, 1):
            cover_count += 1
            encoding = build_encoding(
                dual, T, B, C, selected_pairs, args.weighted_budget
            )
            fingerprint = cnf_fingerprint(encoding.cnf.clauses)
            solver_results = []
            first_model = None
            for solver_name in args.solvers:
                status, model, elapsed = solve(encoding.cnf, solver_name)
                solver_results.append(
                    {
                        "solver": solver_name,
                        "status": status,
                        "elapsed_seconds": round(elapsed, 6),
                    }
                )
                if first_model is None and model is not None:
                    first_model = model
            statuses = {item["status"] for item in solver_results}
            mismatch_count += int(len(statuses) != 1)
            cover_result = {
                "cover_index": cover_index,
                "enumerated_pair_gates": [
                    f"{pair:08x}" for pair in sorted(selected_pairs)
                ],
                "variable_count": encoding.pool.top,
                "clause_count": len(encoding.cnf.clauses),
                "cnf_sha256": fingerprint,
                "solver_results": solver_results,
            }
            if solver_results[0]["status"] == "sat":
                sat_count += 1
                cover_result["certificate"] = decode_and_verify(
                    audit,
                    dual,
                    init,
                    T,
                    B,
                    C,
                    encoding,
                    first_model,
                    args.weighted_budget,
                )
                stop = args.stop_on_sat
            line_result["covers"].append(cover_result)
            if stop:
                break
        results.append(line_result)
        print(
            f"line={source_line} covers={len(line_result['covers'])}/{len(covers)} "
            f"sat={sum(x['solver_results'][0]['status'] == 'sat' for x in line_result['covers'])} "
            f"truncated={truncated}",
            flush=True,
        )
        if stop:
            break

    document = {
        "schema": 1,
        "status": (
            "incomplete"
            if truncated_count or mismatch_count
            else ("candidate" if sat_count else "unsat_complete")
        ),
        "scope": {
            "source": str(source),
            "first_line": args.first,
            "last_line": last,
            "weighted_budget": args.weighted_budget,
            "gate_target": FIXED_SHELL + args.weighted_budget,
            "delay": 10,
            "cycles": 66,
            "topology": "depth-two XOR2 plus input-Z/OR mediation",
        },
        "coverage": {
            "candidate_count": len(results),
            "cover_count": cover_count,
            "sat_count": sat_count,
            "cover_search_truncated_count": truncated_count,
            "solver_mismatch_count": mismatch_count,
            "stopped_on_sat": stop,
        },
        "limits": {
            "state_limit": args.state_limit,
            "solution_limit": args.solution_limit,
            "solvers": list(args.solvers),
        },
        "elapsed_seconds": round(time.perf_counter() - started, 6),
        "records": results,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in document.items() if key != "records"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
