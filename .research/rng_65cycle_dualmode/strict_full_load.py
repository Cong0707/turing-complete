"""Exact mediated audit for a 65-cycle, no-RAM RNG candidate.

This extends ``rng_x56_or10/strict_radius14_sat.py`` without changing that
proof artifact.  On tick zero the shared network must simultaneously compute
``T*A*seed`` for the stored encoded state and ``A*seed`` for the first visible
output.  Later ticks use the ordinary ``B`` and ``C`` steady transforms.

At 10 delay and 65 cycles, beating 431/9/66 requires at most 393 gates:
``166 + 3*XOR + OR <= 393``.  Pair and unit mediation are selected jointly
with physical pair-pin labels and the exact OR-leaf union.  All XORs use the
confirmed 3-gate / 2-delay cost.  The script never starts the game or writes a
save.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import random
import sys
import time
from typing import Any


BITS = 32
XOR_TARGET = 56
WEIGHTED_BUDGET = 227
FIXED_SHELL = 166
TARGET_GATE = 393
TARGET_DELAY = 10
TARGET_CYCLES = 65


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def build_encoding_full(strict, dual, init, T, B, C, selected_pairs, budget):
    from pysat.card import CardEnc, EncType
    from pysat.formula import CNF, IDPool

    pool = IDPool()
    cnf = CNF()
    heavy = tuple(
        row for row in dict.fromkeys((*B, *C)) if row.bit_count() in (3, 4)
    )
    decompositions = {}
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

    load_state = init.compose(T, init.A)
    wanted_rows = (*load_state, *init.A)
    steady_rows = (*B, *C)
    distinct_steady = tuple(dict.fromkeys(steady_rows))
    row_options = {
        steady: strict.mediation_options(steady, selected_pairs)
        if steady.bit_count() in (1, 2)
        else (strict.MediationOption("direct", "direct", ()),)
        for steady in distinct_steady
    }
    choice_vars = {}
    for steady, options in row_options.items():
        if len(options) == 1:
            continue
        values = []
        for option_index in range(len(options)):
            variable = pool.id(("choice", steady, option_index))
            choice_vars[(steady, option_index)] = variable
            values.append(variable)
        cnf.append(values)
        for left in range(len(values)):
            for right in range(left + 1, len(values)):
                cnf.append([-values[left], -values[right]])

    mapping_vars = {}

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
    orientation_vars = {}
    for pair in sorted(selected_pairs):
        states = strict.bits(pair)
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
    pair_causes = {pair: [] for pair in selected_pairs}
    mediated_choice_vars = []
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

    active_pair_vars = {}
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

    for target, steady in zip(wanted_rows, steady_rows, strict=True):
        weight = steady.bit_count()
        if weight == 1:
            options = row_options[steady]
            for option_index, option in enumerate(options):
                guard = (
                    None
                    if len(options) == 1
                    else choice_vars[(steady, option_index)]
                )
                if option.kind == "direct":
                    if target.bit_count() != 1:
                        cnf.append([] if guard is None else [-guard])
                    else:
                        direct_seed = strict.bits(target)[0]
                        clause = [mapping(direct_seed, strict.bits(steady)[0])]
                        if guard is not None:
                            clause.insert(0, -guard)
                        cnf.append(clause)
                elif option.kind == "unit":
                    pair = option.pairs[0]
                    state = strict.bits(pair ^ steady)[0]
                    strict.add_residual_unit(
                        cnf, guard, label_tuple(pair), target, state, mapping
                    )
                else:
                    raise AssertionError("unit row has pair mediation")
        elif weight == 2:
            options = row_options[steady]
            for option_index, option in enumerate(options):
                guard = (
                    None
                    if len(options) == 1
                    else choice_vars[(steady, option_index)]
                )
                if option.kind == "direct":
                    for seed, label in enumerate(label_tuple(steady)):
                        strict.add_conditional_bit(
                            cnf, guard, label, target >> seed & 1
                        )
                elif option.kind == "pair":
                    left_labels = label_tuple(option.pairs[0])
                    right_labels = label_tuple(option.pairs[1])
                    for seed, (left, right) in enumerate(
                        zip(left_labels, right_labels, strict=True)
                    ):
                        strict.add_conditional_xor(
                            cnf, guard, left, right, target >> seed & 1
                        )
                else:
                    raise AssertionError("pair row has unit mediation")
        elif weight == 3:
            pair = decompositions[steady][0]
            state = strict.bits(steady ^ pair)[0]
            strict.add_residual_unit(
                cnf, None, label_tuple(pair), target, state, mapping
            )
        elif weight == 4:
            left, right = decompositions[steady]
            for seed, (left_label, right_label) in enumerate(
                zip(label_tuple(left), label_tuple(right), strict=True)
            ):
                strict.add_conditional_xor(
                    cnf,
                    None,
                    left_label,
                    right_label,
                    target >> seed & 1,
                )
        else:
            raise ValueError(f"unsupported steady row weight {weight}")

    fixed_final_count = len(heavy)
    fixed_gate_cost = 3 * (len(fixed_pairs) + fixed_final_count)
    cost_literals = sorted(mapping_vars.values())
    for active in active_pair_vars.values():
        cost_literals.extend((active, active, active))
    for mediated in mediated_choice_vars:
        cost_literals.extend((mediated, mediated, mediated))
    remaining = budget - fixed_gate_cost
    if remaining < 0:
        cnf.append([])
    else:
        cardinality = CardEnc.atmost(
            lits=cost_literals,
            bound=remaining,
            vpool=pool,
            encoding=EncType.seqcounter,
        )
        cnf.extend(cardinality.clauses)

    return strict.Encoding(
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


def actual_load_label(strict, steady, target, encoding, positive, pair_labels, mappings, option):
    if option.kind == "pair":
        return pair_labels[option.pairs[0]] ^ pair_labels[option.pairs[1]]
    if option.kind == "unit":
        pair = option.pairs[0]
        residual = target ^ pair_labels[pair]
        if residual.bit_count() > 1:
            raise AssertionError("mediated unit residual is not a unit")
        if residual:
            state = strict.bits(pair ^ steady)[0]
            if (strict.bits(residual)[0], state) not in mappings:
                raise AssertionError("mediated unit mapping is absent")
        return pair_labels[pair] ^ residual
    weight = steady.bit_count()
    if weight == 1:
        if target.bit_count() != 1:
            raise AssertionError("direct unit target is not a unit")
        state = strict.bits(steady)[0]
        if (strict.bits(target)[0], state) not in mappings:
            raise AssertionError("direct unit mapping is absent")
        return target
    if weight == 2:
        return pair_labels[steady]
    if weight == 3:
        pair = encoding.decompositions[steady][0]
        residual = target ^ pair_labels[pair]
        if residual.bit_count() > 1:
            raise AssertionError("weight-3 residual is not a unit")
        if residual:
            state = strict.bits(steady ^ pair)[0]
            if (strict.bits(residual)[0], state) not in mappings:
                raise AssertionError("weight-3 mapping is absent")
        return pair_labels[pair] ^ residual
    if weight == 4:
        left, right = encoding.decompositions[steady]
        return pair_labels[left] ^ pair_labels[right]
    raise AssertionError("unsupported steady row")


def decode_and_verify_full(strict, dual, init, T, B, C, encoding, model, budget):
    positive = {literal for literal in model if literal > 0}
    choices = {
        steady: strict.selected_option(
            positive, steady, options, encoding.choice_vars
        )
        for steady, options in encoding.row_options.items()
    }
    active_pairs = set(encoding.fixed_pairs)
    active_pairs.update(
        pair
        for pair, variable in encoding.active_pair_vars.items()
        if variable in positive
    )
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

    for pair, label in pair_labels.items():
        left_state, right_state = strict.bits(pair)
        left_seed, right_seed = orientations[pair]
        actual = (0 if left_seed is None else 1 << left_seed) ^ (
            0 if right_seed is None else 1 << right_seed
        )
        if actual != label:
            raise AssertionError("pair orientation does not realize its label")
        if left_seed is not None and (left_seed, left_state) not in mappings:
            raise AssertionError("left pair mapping is absent")
        if right_seed is not None and (right_seed, right_state) not in mappings:
            raise AssertionError("right pair mapping is absent")

    load_state = init.compose(T, init.A)
    wanted_rows = (*load_state, *init.A)
    steady_rows = (*B, *C)
    for target, steady in zip(wanted_rows, steady_rows, strict=True):
        actual = actual_load_label(
            strict,
            steady,
            target,
            encoding,
            positive,
            pair_labels,
            mappings,
            choices[steady],
        )
        if actual != target:
            raise AssertionError("decoded tick-zero label mismatch")

    if init.compose(C, T) != init.A or init.compose(T, C) != B:
        raise AssertionError("steady matrix identity failed")
    seeds = [0, 1, 2, 0x12345678, 0xFFFFFFFF, 0x80000000]
    generator = random.Random(20260802)
    seeds.extend(generator.getrandbits(32) for _ in range(64))
    for seed in seeds:
        natural = init.xorshift32(seed)
        encoded = init.apply_matrix(load_state, seed)
        for _ in range(1, TARGET_CYCLES):
            wanted = init.xorshift32(natural)
            actual = init.apply_matrix(C, encoded)
            if actual != wanted:
                raise AssertionError("65-cycle visible stream mismatch")
            natural = wanted
            encoded = init.apply_matrix(B, encoded)

    mediated = {
        row: option.pairs
        for row, option in choices.items()
        if option.kind == "pair"
    }
    mediated_units = {
        row: option.pairs[0]
        for row, option in choices.items()
        if option.kind == "unit"
    }
    xor_count = (
        len(active_pairs)
        + encoding.fixed_final_count
        + len(mediated)
        + len(mediated_units)
    )
    weighted = 3 * xor_count + len(mappings)
    if weighted > budget:
        raise AssertionError("decoded candidate exceeds weighted budget")
    return {
        "selected_pair_gates": [f"{value:08x}" for value in sorted(active_pairs)],
        "decompositions": {
            f"{row:08x}": [f"{value:08x}" for value in option]
            for row, option in sorted(encoding.decompositions.items())
        },
        "selected_choices": {
            f"{row:08x}": option.name for row, option in sorted(choices.items())
        },
        "pair_labels": {
            f"{row:08x}": f"{value:08x}"
            for row, value in sorted(pair_labels.items())
        },
        "pair_pin_seed_bits": {
            f"{row:08x}": list(value)
            for row, value in sorted(orientations.items())
        },
        "mode_pairs": [
            {"seed": seed, "state": state}
            for seed, state in sorted(mappings)
        ],
        "metrics": {
            "xor": xor_count,
            "or": len(mappings),
            "three_xor_plus_or": weighted,
            "gate": FIXED_SHELL + weighted,
            "delay": TARGET_DELAY,
            "cycles": TARGET_CYCLES,
            "energy": (FIXED_SHELL + weighted) * TARGET_DELAY * TARGET_CYCLES,
        },
    }


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
        default=Path(".research/rng_65cycle_dualmode/radius14-strict.json"),
    )
    parser.add_argument("--first", type=int, default=1)
    parser.add_argument("--last", type=int)
    parser.add_argument("--state-limit", type=int, default=2_000_000)
    parser.add_argument("--solution-limit", type=int, default=200_000)
    parser.add_argument("--solvers", nargs="+", default=("g4", "cadical195"))
    parser.add_argument("--stop-on-sat", action="store_true")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    strict = load_module(
        "rng_65_strict_base", root / ".research/rng_x56_or10/strict_radius14_sat.py"
    )
    dual = load_module(
        "rng_65_strict_dual", root / ".research/rng_cost387/search_basis_dualmode.py"
    )
    cover = load_module(
        "rng_65_strict_cover",
        root / ".research/rng_switch_bdd_cover/batch_phase_audit.py",
    )
    init = load_module(
        "rng_65_strict_init", root / ".research/rng_init_reuse/verify_init_reuse.py"
    )
    source = args.source if args.source.is_absolute() else root / args.source
    output = args.output if args.output.is_absolute() else root / args.output
    records = [
        json.loads(line)
        for line in source.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    last = len(records) if args.last is None else min(args.last, len(records))
    indexed = list(enumerate(records[args.first - 1 : last], args.first))
    started = time.perf_counter()
    results = []
    cover_count = sat_count = truncated_count = mismatch_count = 0
    stopped = False

    for source_line, record in indexed:
        T, B, C = (strict.matrix(record, key) for key in ("T", "B", "C"))
        if init.compose(C, T) != init.A or init.compose(T, C) != B:
            raise AssertionError(f"matrix identity failed on line {source_line}")
        covers, visited, truncated = cover.enumerate_pair_covers(
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
            encoding = build_encoding_full(
                strict,
                dual,
                init,
                T,
                B,
                C,
                selected_pairs,
                WEIGHTED_BUDGET,
            )
            solver_results = []
            first_model = None
            for solver_name in args.solvers:
                status, model, elapsed = strict.solve(encoding.cnf, solver_name)
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
                "cnf_sha256": strict.cnf_fingerprint(encoding.cnf.clauses),
                "solver_results": solver_results,
            }
            if solver_results[0]["status"] == "sat":
                sat_count += 1
                cover_result["certificate"] = decode_and_verify_full(
                    strict,
                    dual,
                    init,
                    T,
                    B,
                    C,
                    encoding,
                    first_model,
                    WEIGHTED_BUDGET,
                )
                stopped = args.stop_on_sat
            line_result["covers"].append(cover_result)
            if stopped:
                break
        results.append(line_result)
        print(
            f"line={source_line} covers={len(line_result['covers'])}/{len(covers)} "
            f"sat={sum(x['solver_results'][0]['status'] == 'sat' for x in line_result['covers'])}",
            flush=True,
        )
        if stopped:
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
            "weighted_budget": WEIGHTED_BUDGET,
            "gate_target": TARGET_GATE,
            "delay": TARGET_DELAY,
            "cycles": TARGET_CYCLES,
            "tick0_output": "A*seed",
            "tick0_state": "T*A*seed",
            "topology": "depth-two XOR2 plus input-Z/OR mediation",
            "xor_cost": [3, 2],
        },
        "coverage": {
            "candidate_count": len(results),
            "cover_count": cover_count,
            "sat_count": sat_count,
            "cover_search_truncated_count": truncated_count,
            "solver_mismatch_count": mismatch_count,
            "stopped_on_sat": stopped,
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
    print(
        json.dumps(
            {key: value for key, value in document.items() if key != "records"},
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
