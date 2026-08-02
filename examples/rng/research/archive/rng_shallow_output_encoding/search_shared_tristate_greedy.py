"""Low-memory local search for a real shared Switch/Z xorshift32 core."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import random
import time
from typing import Sequence

import solve_mixed_cover as common
import solve_shared_tristate_complete as complete


@dataclass(frozen=True)
class Evaluation:
    cost: int
    forms: frozenset[int]
    macros: tuple[tuple[tuple[object, ...], tuple[int, int, int]], ...]
    nors: frozenset[tuple[int, int]]
    ands: frozenset[tuple[int, int]]


def cover_ands(
    macro_sources: Sequence[tuple[int, int, int]],
) -> frozenset[tuple[int, int]]:
    requirements = tuple(
        frozenset(complete.signal_pairs(sources)) for sources in macro_sources
    )
    selected: set[tuple[int, int]] = set()
    while True:
        unmet = [requirement for requirement in requirements if not requirement & selected]
        if not unmet:
            break
        candidates = {pair for requirement in unmet for pair in requirement}
        best = max(
            candidates,
            key=lambda pair: (
                sum(pair in requirement for requirement in unmet),
                -pair[0],
                -pair[1],
            ),
        )
        selected.add(best)
    for pair in sorted(tuple(selected), reverse=True):
        trial = selected - {pair}
        if all(requirement & trial for requirement in requirements):
            selected = trial
    return frozenset(selected)


def evaluate(
    selection: Sequence[int],
    options: Sequence[Sequence[tuple[int, tuple[int, ...]]]],
    concrete: dict[tuple[int, int], tuple[int, ...]],
) -> Evaluation:
    forms = frozenset(
        form
        for output, index in enumerate(selection)
        for form in options[output][index][1]
    )
    macros: dict[tuple[object, ...], tuple[int, int, int]] = {}
    for form in forms:
        if form.bit_count() == 3:
            macros[("form", form)] = tuple(
                1 << bit for bit in range(32) if form >> bit & 1
            )
    final_xor2 = 0
    for output, index in enumerate(selection):
        arity, _required = options[output][index]
        if arity == 2:
            final_xor2 += 1
        elif arity == 3:
            macros[("final", output, index)] = concrete[output, index]

    macro_items = tuple(sorted(macros.items(), key=lambda item: repr(item[0])))
    nors = frozenset(
        pair
        for _key, sources in macro_items
        for pair in complete.signal_pairs(sources)
    )
    ands = cover_ands([sources for _key, sources in macro_items])
    first_xor2 = sum(form.bit_count() == 2 for form in forms)
    cost = (
        3 * (first_xor2 + final_xor2)
        + 8 * len(macro_items)
        + len(nors)
        + len(ands)
    )
    return Evaluation(cost, forms, macro_items, nors, ands)


def search(xor3_limit: int, restarts: int, seed: int) -> dict[str, object]:
    started = time.perf_counter()
    model = complete.load_complete_model()
    rows, options = complete.bounded_options(model, xor3_limit)
    concrete = {
        (output, index): complete.recover_sources(rows[output], *option)
        for output, choices in enumerate(options)
        for index, option in enumerate(choices)
    }
    ranked = tuple(
        tuple(
            sorted(
                range(len(choices)),
                key=lambda index: (
                    complete.local_option_cost(*choices[index]),
                    len(choices[index][1]),
                    choices[index][1],
                ),
            )
        )
        for choices in options
    )
    rng = random.Random(seed)
    best_selection: tuple[int, ...] | None = None
    best_evaluation: Evaluation | None = None
    evaluations = 0

    for restart in range(restarts):
        if restart == 0:
            selection = [order[0] for order in ranked]
        elif restart == 1:
            selection = [
                min(
                    range(len(choices)),
                    key=lambda index: (
                        choices[index][0] == 3,
                        complete.local_option_cost(*choices[index]),
                        len(choices[index][1]),
                        choices[index][1],
                    ),
                )
                for choices in options
            ]
        elif restart == 2:
            selection = [
                min(
                    range(len(choices)),
                    key=lambda index: (
                        sum(form.bit_count() == 3 for form in choices[index][1]),
                        len(choices[index][1]),
                        choices[index][0] == 3,
                        complete.local_option_cost(*choices[index]),
                    ),
                )
                for choices in options
            ]
        else:
            selection = [
                order[min(int(rng.expovariate(0.7)), min(15, len(order) - 1))]
                for order in ranked
            ]
        current = evaluate(selection, options, concrete)
        evaluations += 1
        for _sweep in range(12):
            changed = False
            order = list(range(32))
            rng.shuffle(order)
            for output in order:
                old = selection[output]
                candidate_best = current
                candidate_index = old
                for index in ranked[output]:
                    if index == old:
                        continue
                    selection[output] = index
                    trial = evaluate(selection, options, concrete)
                    evaluations += 1
                    if trial.cost < candidate_best.cost:
                        candidate_best = trial
                        candidate_index = index
                selection[output] = candidate_index
                if candidate_index != old:
                    current = candidate_best
                    changed = True
            if not changed:
                break

        if best_evaluation is None or current.cost < best_evaluation.cost:
            best_selection = tuple(selection)
            best_evaluation = current
            print(
                f"best restart={restart} core={current.cost} "
                f"forms={len(current.forms)} macros={len(current.macros)} "
                f"nor={len(current.nors)} and={len(current.ands)}",
                flush=True,
            )

    assert best_selection is not None and best_evaluation is not None
    orientation = {
        key: min(set(complete.signal_pairs(sources)) & best_evaluation.ands)
        for key, sources in best_evaluation.macros
    }
    outputs = []
    for output, index in enumerate(best_selection):
        arity, required = options[output][index]
        outputs.append(
            {
                "output": output,
                "target": f"{rows[output]:08x}",
                "final_arity": arity,
                "sources": [f"{source:08x}" for source in concrete[output, index]],
                "required_first_forms": [f"{form:08x}" for form in required],
                "macro_key": None if arity != 3 else ["final", output, index],
            }
        )
    macros = dict(best_evaluation.macros)
    verification = complete.verify(
        rows,
        best_evaluation.forms,
        macros,
        orientation,
        best_evaluation.nors,
        best_evaluation.ands,
        outputs,
    )
    first_xor2 = sum(form.bit_count() == 2 for form in best_evaluation.forms)
    first_xor3 = sum(form.bit_count() == 3 for form in best_evaluation.forms)
    final_xor2 = sum(entry["final_arity"] == 2 for entry in outputs)
    final_xor3 = sum(entry["final_arity"] == 3 for entry in outputs)
    return {
        "status": "candidate",
        "scope": "bounded cancellation-capable shared Switch/Z local search",
        "xor3_options_per_output": xor3_limit,
        "restarts": restarts,
        "seed": seed,
        "evaluations": evaluations,
        "elapsed_seconds": time.perf_counter() - started,
        "certificate": {
            "schema": 1,
            "target_rows": [f"{row:08x}" for row in rows],
            "selection": list(best_selection),
            "selected_first_forms": [f"{form:08x}" for form in sorted(best_evaluation.forms)],
            "xor3_macros": [
                {
                    "key": list(key),
                    "sources": [f"{source:08x}" for source in sources],
                    "and_pair": [f"{source:08x}" for source in orientation[key]],
                }
                for key, sources in best_evaluation.macros
            ],
            "shared_nor_controls": [
                [f"{left:08x}", f"{right:08x}"]
                for left, right in sorted(best_evaluation.nors)
            ],
            "shared_and_controls": [
                [f"{left:08x}", f"{right:08x}"]
                for left, right in sorted(best_evaluation.ands)
            ],
            "outputs": outputs,
            "metrics": {
                "first_xor2": first_xor2,
                "first_xor3": first_xor3,
                "final_xor2": final_xor2,
                "final_xor3": final_xor3,
                "xor3_switch_gate": 8 * len(best_evaluation.macros),
                "shared_nor_gate": len(best_evaluation.nors),
                "shared_and_gate": len(best_evaluation.ands),
                "core_gate": best_evaluation.cost,
                "core_delay": 4,
                "within_200": best_evaluation.cost <= 200,
                "full_rng_gate": 230 + best_evaluation.cost,
            },
            "verification": verification,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--xor3-per-output", type=int, default=64)
    parser.add_argument("--restarts", type=int, default=16)
    parser.add_argument("--seed", type=lambda value: int(value, 0), default=0x5A7A7E)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = search(args.xor3_per_output, args.restarts, args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["certificate"]["metrics"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
