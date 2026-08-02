"""Search a depth-two xorshift32 network with shared Switch-XOR3 controls.

This is an offline research model.  It refines the atomic XOR2/XOR3 model in
``search_depth2_mixed.py`` by expanding every XOR3 into the reviewed minimum
tri-state implementation:

* four Bit Switches, costing eight gates in total;
* NOR for all three input pairs;
* AND for one of the three input pairs.

The three pair-NOR functions and the selected pair-AND function may be shared
between XOR3 instances when their Boolean functions are identical.  Equality
is canonicalized over the full 32-bit input domain, including changes of basis
inside the same two-dimensional linear span.

The search is heuristic.  Its option universe is the cancellation-aware,
atomic-cost dominance reduction used by ``solve_mixed_bound.py``.  Therefore a
found circuit is a valid upper bound, but failure is not an UNSAT certificate
for arbitrary Switch covers or for sharing-favoured options removed by that
atomic-cost reduction.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from functools import lru_cache
import json
import math
from pathlib import Path
import random
import sys
import time
from typing import Iterable


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import search_depth2_mixed as mixed  # noqa: E402
from solve_mixed_rc2 import build_minimal_options, option_records  # noqa: E402


DEFAULT_OUTPUT = HERE / "shared_switch_xor3_candidate.json"


# A control key identifies the indicator of one coset of a codimension-two
# subspace.  The first three words are the sorted nonzero members of the
# two-dimensional span.  label=0 is NOR(a,b), while label=a^b is AND(a,b).
ControlKey = tuple[int, int, int, int]


@dataclass(frozen=True, slots=True)
class Option:
    final_gate_cost: int
    required_forms: tuple[int, ...]
    sources: tuple[int, ...]

    @property
    def final_base_cost(self) -> int:
        if self.final_gate_cost == 12:
            return 8
        return self.final_gate_cost


def pair_control_key(left: int, right: int, and_gate: bool) -> ControlKey:
    if not left or not right or left == right:
        raise AssertionError("XOR3 pair inputs must be distinct nonzero forms")
    span = sorted((left, right, left ^ right))
    return (span[0], span[1], span[2], left ^ right if and_gate else 0)


@lru_cache(maxsize=100_000)
def xor3_controls(
    sources: tuple[int, int, int]
) -> tuple[tuple[ControlKey, ...], tuple[ControlKey, ...]]:
    if len(set(sources)) != 3:
        raise AssertionError("XOR3 sources are not distinct")
    nors: list[ControlKey] = []
    ands: list[ControlKey] = []
    for left_index, right_index in ((0, 1), (0, 2), (1, 2)):
        left = sources[left_index]
        right = sources[right_index]
        nors.append(pair_control_key(left, right, False))
        ands.append(pair_control_key(left, right, True))
    return tuple(nors), tuple(ands)


def sources_for(
    target: int, final_gate_cost: int, required: tuple[int, ...]
) -> tuple[int, ...]:
    arity = {0: 1, 3: 2, 12: 3}[final_gate_cost]
    residual = target
    for value in required:
        residual ^= value
    raw = tuple(1 << bit for bit in range(mixed.BITS) if (residual >> bit) & 1)
    sources = tuple(sorted((*required, *raw)))
    if len(sources) != arity or len(set(sources)) != arity:
        raise AssertionError(
            f"cannot reconstruct arity {arity}: target={target:08x}, "
            f"required={required}, residual={residual:08x}"
        )
    reconstructed = 0
    for value in sources:
        reconstructed ^= value
    if reconstructed != target:
        raise AssertionError("reconstructed final sources do not match target")
    return sources


def build_options() -> tuple[dict[int, int], tuple[tuple[Option, ...], ...]]:
    primary_cost, minimal = build_minimal_options()
    records = option_records(minimal)
    rows = mixed.target_rows()
    options = tuple(
        tuple(
            Option(cost, required, sources_for(rows[output], cost, required))
            for cost, required in output_records
        )
        for output, output_records in enumerate(records)
    )
    return primary_cost, options


def first_form_sources(value: int) -> tuple[int, int, int]:
    if value.bit_count() != 3:
        raise AssertionError("only weight-three forms use Switch-XOR3")
    return tuple(
        1 << bit for bit in range(mixed.BITS) if (value >> bit) & 1
    )  # type: ignore[return-value]


def greedy_and_cover(
    clauses: Iterable[tuple[ControlKey, ...]]
) -> tuple[ControlKey, ...]:
    unique = tuple(dict.fromkeys(tuple(sorted(set(clause))) for clause in clauses))
    uncovered = set(range(len(unique)))
    selected: list[ControlKey] = []
    incidence: dict[ControlKey, set[int]] = {}
    for index, clause in enumerate(unique):
        for key in clause:
            incidence.setdefault(key, set()).add(index)
    while uncovered:
        key = min(
            incidence,
            key=lambda candidate: (
                -len(incidence[candidate] & uncovered), candidate
            ),
        )
        hit = incidence[key] & uncovered
        if not hit:
            raise AssertionError("AND-cover greedy search made no progress")
        selected.append(key)
        uncovered.difference_update(hit)
    # Reverse deletion makes the deterministic greedy cover inclusion-minimal.
    for key in tuple(reversed(selected)):
        trial = [value for value in selected if value != key]
        if all(any(value in clause for value in trial) for clause in unique):
            selected.remove(key)
    return tuple(sorted(selected))


def exact_and_cover(
    clauses: Iterable[tuple[ControlKey, ...]], state_limit: int = 500_000
) -> tuple[ControlKey, ...]:
    """Return an exact minimum key cover, split by incidence components."""

    unique = tuple(dict.fromkeys(tuple(sorted(set(clause))) for clause in clauses))
    if not unique:
        return ()
    key_to_clauses: dict[ControlKey, set[int]] = {}
    for index, clause in enumerate(unique):
        for key in clause:
            key_to_clauses.setdefault(key, set()).add(index)

    remaining = set(range(len(unique)))
    components: list[set[int]] = []
    while remaining:
        start = remaining.pop()
        component = {start}
        frontier = [start]
        while frontier:
            clause_index = frontier.pop()
            for key in unique[clause_index]:
                for neighbour in key_to_clauses[key]:
                    if neighbour in remaining:
                        remaining.remove(neighbour)
                        component.add(neighbour)
                        frontier.append(neighbour)
        components.append(component)

    answer: list[ControlKey] = []
    states_used = 0
    for component in components:
        local_clauses = tuple(sorted(component))
        local_position = {old: new for new, old in enumerate(local_clauses)}
        local_keys = sorted(
            {key for old in local_clauses for key in unique[old]}
        )
        cover_masks: dict[ControlKey, int] = {}
        for key in local_keys:
            mask = 0
            for old in key_to_clauses[key] & component:
                mask |= 1 << local_position[old]
            cover_masks[key] = mask
        clauses_by_position = tuple(
            unique[old] for old in local_clauses
        )
        memo: dict[int, tuple[ControlKey, ...]] = {0: ()}

        def solve(uncovered: int) -> tuple[ControlKey, ...]:
            nonlocal states_used
            cached = memo.get(uncovered)
            if cached is not None:
                return cached
            states_used += 1
            if states_used > state_limit:
                raise RuntimeError(
                    f"exact AND-cover state limit {state_limit} exceeded"
                )
            positions = [
                index
                for index in range(len(local_clauses))
                if (uncovered >> index) & 1
            ]
            # Branch on the clause whose keys cover the fewest remaining
            # clauses in total.  This is deterministic and effective on the
            # sparse sharing graphs produced by the selected XOR3 nodes.
            position = min(
                positions,
                key=lambda index: (
                    sum(
                        (cover_masks[key] & uncovered).bit_count()
                        for key in clauses_by_position[index]
                    ),
                    index,
                ),
            )
            best: tuple[ControlKey, ...] | None = None
            ordered_keys = sorted(
                clauses_by_position[position],
                key=lambda key: (
                    -(cover_masks[key] & uncovered).bit_count(), key
                ),
            )
            for key in ordered_keys:
                rest = solve(uncovered & ~cover_masks[key])
                candidate = tuple(sorted((key, *rest)))
                if best is None or (len(candidate), candidate) < (len(best), best):
                    best = candidate
            assert best is not None
            memo[uncovered] = best
            return best

        answer.extend(solve((1 << len(local_clauses)) - 1))
    return tuple(sorted(answer))


@dataclass(frozen=True, slots=True)
class Score:
    total_gate: int
    first_base_gate: int
    final_base_gate: int
    nor_gate: int
    and_gate: int
    selected_forms: tuple[int, ...]
    nor_controls: tuple[ControlKey, ...]
    and_controls: tuple[ControlKey, ...]
    xor3_nodes: tuple[tuple[int, int, int], ...]


def score_selection(
    selection: tuple[Option, ...], exact: bool = False
) -> Score:
    forms = tuple(
        sorted(
            {
                value
                for option in selection
                for value in option.required_forms
            }
        )
    )
    first_base = sum(3 if value.bit_count() == 2 else 8 for value in forms)
    final_base = sum(option.final_base_cost for option in selection)
    nodes: list[tuple[int, int, int]] = []
    for value in forms:
        if value.bit_count() == 3:
            nodes.append(first_form_sources(value))
    for option in selection:
        if option.final_gate_cost == 12:
            nodes.append(option.sources)  # type: ignore[arg-type]
    nor_controls: set[ControlKey] = set()
    and_clauses: list[tuple[ControlKey, ...]] = []
    for node in nodes:
        nors, ands = xor3_controls(node)
        nor_controls.update(nors)
        and_clauses.append(ands)
    and_controls = (
        exact_and_cover(and_clauses) if exact else greedy_and_cover(and_clauses)
    )
    total = first_base + final_base + len(nor_controls) + len(and_controls)
    return Score(
        total,
        first_base,
        final_base,
        len(nor_controls),
        len(and_controls),
        forms,
        tuple(sorted(nor_controls)),
        and_controls,
        tuple(nodes),
    )


def atomic_cost(selection: tuple[Option, ...], primary_cost: dict[int, int]) -> int:
    forms = {
        value for option in selection for value in option.required_forms
    }
    return sum(primary_cost[value] for value in forms) + sum(
        option.final_gate_cost for option in selection
    )


def candidate_pools(
    options: tuple[tuple[Option, ...], ...],
    primary_cost: dict[int, int],
    pool_size: int,
    random_size: int,
    generator: random.Random,
    initial: tuple[Option, ...] | None,
) -> tuple[tuple[Option, ...], ...]:
    result = []
    for output, output_options in enumerate(options):
        ranked = sorted(
            output_options,
            key=lambda option: (
                option.final_gate_cost
                + sum(primary_cost[value] for value in option.required_forms),
                len(option.required_forms),
                option.required_forms,
            ),
        )
        chosen = list(ranked[:pool_size])
        # Keep every XOR2/direct option; there are at most 91 per row and they
        # often become useful only through global first-form sharing.
        chosen.extend(
            option for option in output_options if option.final_gate_cost != 12
        )
        if len(output_options) > random_size:
            chosen.extend(generator.sample(output_options, random_size))
        else:
            chosen.extend(output_options)
        if initial is not None:
            chosen.append(initial[output])
        result.append(tuple(dict.fromkeys(chosen)))
    return tuple(result)


def search(
    options: tuple[tuple[Option, ...], ...],
    primary_cost: dict[int, int],
    restarts: int,
    sweeps: int,
    pool_size: int,
    random_size: int,
    seed: int,
    initial: tuple[Option, ...] | None,
) -> tuple[tuple[Option, ...], Score]:
    generator = random.Random(seed)
    pools = candidate_pools(
        options, primary_cost, pool_size, random_size, generator, initial
    )
    best_selection: tuple[Option, ...] | None = None
    best_score: Score | None = None
    started = time.perf_counter()

    for restart in range(restarts):
        if restart == 0 and initial is not None:
            current = initial
        elif restart == 0:
            current = tuple(
                min(
                    output_options,
                    key=lambda option: (
                        option.final_gate_cost
                        + sum(
                            primary_cost[value]
                            for value in option.required_forms
                        ),
                        option.required_forms,
                    ),
                )
                for output_options in options
            )
        else:
            current = tuple(generator.choice(pool) for pool in pools)
        current_score = score_selection(current)
        current_exact = score_selection(current, exact=True)
        if best_score is None or current_exact.total_gate < best_score.total_gate:
            best_selection = current
            best_score = current_exact
            print(
                f"best_gate={best_score.total_gate} "
                f"atomic_gate={atomic_cost(current, primary_cost)} "
                f"restart={restart} sweep=initial "
                f"elapsed_s={time.perf_counter()-started:.3f}",
                flush=True,
            )
        temperature = 8.0

        for sweep in range(sweeps):
            order = list(range(mixed.BITS))
            generator.shuffle(order)
            changed = False
            for output in order:
                candidates = list(pools[output])
                generator.shuffle(candidates)
                # Evaluate a bounded subset per coordinate.  The lowest local
                # cost candidates remain first after the random prefix is
                # restored, while random members preserve exploration.
                if len(candidates) > pool_size + random_size:
                    candidates = candidates[: pool_size + random_size]
                local_best = current
                local_score = current_score
                base = list(current)
                for candidate in candidates:
                    if candidate == current[output]:
                        continue
                    base[output] = candidate
                    trial = tuple(base)
                    trial_score = score_selection(trial)
                    delta = trial_score.total_gate - current_score.total_gate
                    if trial_score.total_gate < local_score.total_gate or (
                        trial_score.total_gate == local_score.total_gate
                        and generator.random() < 0.02
                    ):
                        local_best = trial
                        local_score = trial_score
                    base[output] = current[output]
                if local_best is not current:
                    current = local_best
                    current_score = local_score
                    changed = True
                elif temperature > 0.2 and candidates:
                    candidate = generator.choice(candidates)
                    if candidate != current[output]:
                        base = list(current)
                        base[output] = candidate
                        trial = tuple(base)
                        trial_score = score_selection(trial)
                        delta = trial_score.total_gate - current_score.total_gate
                        if delta <= 0 or generator.random() < math.exp(
                            -delta / temperature
                        ):
                            current = trial
                            current_score = trial_score
                            changed = True
            temperature *= 0.82
            exact_score = score_selection(current, exact=True)
            if best_score is None or exact_score.total_gate < best_score.total_gate:
                best_selection = current
                best_score = exact_score
                print(
                    f"best_gate={best_score.total_gate} "
                    f"atomic_gate={atomic_cost(current, primary_cost)} "
                    f"restart={restart} sweep={sweep} "
                    f"elapsed_s={time.perf_counter()-started:.3f}",
                    flush=True,
                )
            if best_score.total_gate <= 201:
                assert best_selection is not None
                return best_selection, best_score
            if not changed and temperature <= 0.2:
                break
    assert best_selection is not None and best_score is not None
    return best_selection, best_score


def load_disjoint_seed(
    path: Path, options: tuple[tuple[Option, ...], ...]
) -> tuple[Option, ...]:
    """Load a certificate emitted by ``search_disjoint_depth2.py``."""

    data = json.loads(path.read_text(encoding="utf-8"))
    rows = mixed.target_rows()
    outputs = data.get("outputs")
    if not isinstance(outputs, list) or len(outputs) != mixed.BITS:
        raise AssertionError("disjoint seed has the wrong output count")
    result: list[Option] = []
    for index, entry in enumerate(outputs):
        target = int(entry["target"], 16)
        if entry["row"] != index or target != rows[index]:
            raise AssertionError("disjoint seed target rows changed")
        arity = int(entry["final_arity"])
        final_cost = {0: 0, 2: 3, 3: 12}[arity]
        sources = tuple(sorted(int(value, 16) for value in entry["blocks"]))
        required = tuple(value for value in sources if value.bit_count() >= 2)
        option = Option(final_cost, required, sources)
        if option not in options[index]:
            raise AssertionError(
                f"disjoint seed option y{index} is outside the reduced universe"
            )
        result.append(option)
    return tuple(result)


def key_json(key: ControlKey) -> dict[str, object]:
    return {
        "span": [f"{value:08x}" for value in key[:3]],
        "coset_zero_label": f"{key[3]:08x}",
        "kind": "NOR" if key[3] == 0 else "AND",
    }


def certificate(
    selection: tuple[Option, ...], score: Score, primary_cost: dict[int, int], args
) -> dict[str, object]:
    rows = mixed.target_rows()
    exact = score_selection(selection, exact=True)
    if exact != score:
        raise AssertionError("reported score is not the exact selected score")
    for target, option in zip(rows, selection):
        value = 0
        for source in option.sources:
            value ^= source
        if value != target:
            raise AssertionError("selected decomposition is incorrect")
    return {
        "schema": 1,
        "model": "depth-two XOR2 / shared-control Switch-XOR3 heuristic",
        "scope": (
            "atomic-cost minimal DNF options; valid upper-bound search, not a "
            "complete arbitrary-Switch UNSAT model"
        ),
        "combination_delay": 4,
        "gate_cost": exact.total_gate,
        "target_gate_cost": 201,
        "target_met": exact.total_gate <= 201,
        "cost_breakdown": {
            "first_level_base": exact.first_base_gate,
            "final_level_base": exact.final_base_gate,
            "unique_pair_nor": exact.nor_gate,
            "minimum_pair_and": exact.and_gate,
            "atomic_xor2_xor3_cost": atomic_cost(selection, primary_cost),
        },
        "counts": {
            "selected_first_forms": len(exact.selected_forms),
            "xor3_nodes": len(exact.xor3_nodes),
            "unique_pair_nor": len(exact.nor_controls),
            "selected_pair_and": len(exact.and_controls),
        },
        "search": {
            "kind": "randomized coordinate descent upper bound",
            "seed": args.seed,
            "restarts": args.restarts,
            "sweeps": args.sweeps,
            "pool_size": args.pool_size,
            "random_size": args.random_size,
            "initial_disjoint": (
                str(args.initial_disjoint) if args.initial_disjoint else None
            ),
        },
        "selected_first_forms": [f"{value:08x}" for value in exact.selected_forms],
        "outputs": [
            {
                "index": index,
                "target": f"{rows[index]:08x}",
                "final_gate_cost_atomic": option.final_gate_cost,
                "final_base_gate": option.final_base_cost,
                "required_first_forms": [
                    f"{value:08x}" for value in option.required_forms
                ],
                "sources": [f"{value:08x}" for value in option.sources],
            }
            for index, option in enumerate(selection)
        ],
        "xor3_nodes": [
            {
                "sources": [f"{value:08x}" for value in node],
                "nor_controls": [key_json(key) for key in xor3_controls(node)[0]],
                "and_choices": [key_json(key) for key in xor3_controls(node)[1]],
                "selected_and": next(
                    key_json(key)
                    for key in xor3_controls(node)[1]
                    if key in exact.and_controls
                ),
            }
            for node in exact.xor3_nodes
        ],
        "unique_nor_controls": [key_json(key) for key in exact.nor_controls],
        "selected_and_controls": [key_json(key) for key in exact.and_controls],
    }


def verify_existing(path: Path) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != 1:
        raise AssertionError("unsupported certificate schema")
    rows = mixed.target_rows()
    outputs = data["outputs"]
    if len(outputs) != mixed.BITS:
        raise AssertionError("certificate output count changed")
    selected: list[Option] = []
    for index, entry in enumerate(outputs):
        target = int(entry["target"], 16)
        if index != entry["index"] or target != rows[index]:
            raise AssertionError("certificate target rows changed")
        cost = int(entry["final_gate_cost_atomic"])
        required = tuple(int(value, 16) for value in entry["required_first_forms"])
        sources = tuple(int(value, 16) for value in entry["sources"])
        if sources != sources_for(target, cost, required):
            raise AssertionError("certificate source reconstruction changed")
        selected.append(Option(cost, required, sources))
    primary_cost, _options = build_options()
    exact = score_selection(tuple(selected), exact=True)
    if exact.total_gate != data["gate_cost"]:
        raise AssertionError("certificate gate cost changed")
    if atomic_cost(tuple(selected), primary_cost) != data["cost_breakdown"][
        "atomic_xor2_xor3_cost"
    ]:
        raise AssertionError("certificate atomic cost changed")
    print(f"verified {path}: gate={exact.total_gate}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--verify-existing", type=Path)
    parser.add_argument("--restarts", type=int, default=8)
    parser.add_argument("--sweeps", type=int, default=12)
    parser.add_argument("--pool-size", type=int, default=96)
    parser.add_argument("--random-size", type=int, default=96)
    parser.add_argument("--initial-disjoint", type=Path)
    parser.add_argument("--seed", type=lambda value: int(value, 0), default=0x53A17C4)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.verify_existing is not None:
        verify_existing(args.verify_existing)
        return
    started = time.perf_counter()
    primary_cost, options = build_options()
    print(
        f"built_s={time.perf_counter()-started:.3f} "
        f"options={sum(map(len, options))}",
        flush=True,
    )
    initial = (
        load_disjoint_seed(args.initial_disjoint, options)
        if args.initial_disjoint is not None
        else None
    )
    if initial is not None:
        initial_score = score_selection(initial, exact=True)
        print(
            f"initial_disjoint_gate={initial_score.total_gate} "
            f"atomic_gate={atomic_cost(initial, primary_cost)}",
            flush=True,
        )
    selection, score = search(
        options,
        primary_cost,
        args.restarts,
        args.sweeps,
        args.pool_size,
        args.random_size,
        args.seed,
        initial,
    )
    payload = certificate(selection, score, primary_cost, args)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="ascii")
    print(
        f"result_gate={score.total_gate} target_met={score.total_gate <= 201} "
        f"wrote={args.output}",
        flush=True,
    )


if __name__ == "__main__":
    main()
