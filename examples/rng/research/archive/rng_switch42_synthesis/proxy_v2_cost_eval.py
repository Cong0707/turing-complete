"""Fast cost proxy for the two-level XOR2/Switch-XOR3 shared cover.

This is an offline evaluator for search_active_state_tradeoff candidates.  It
uses exactly the same target construction and gate costs as optimize_pruned38,
but replaces SAT with deterministic multi-start local search.  The reported
cover is therefore a realizable upper bound inside that restricted library,
not a lower bound or an UNSAT certificate.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
import json
import math
import random
import re
import sys
import time
from typing import Iterable, Sequence


VISIBLE = 32
OR_AND_CONTROL_GATE = 32 + 6
DELAY_GATE = 5
MASK32 = (1 << VISIBLE) - 1

PROXY506_X = (
    "010,022,040,004,008,090,0e0,040,100,200,080,044,101,100,200,004,"
    "008,011,022,040,004,108,210,020,040,100,300,280,000,000,100,000"
)
PROXY506_D = (
    "20040020001,20000044002,00000110008,00100220010,02200040020,"
    "08000880040,00401100080,02000800400,20084002000,08008404000"
)

PRUNED38_X = (
    "000,000,001,010,084,002,001,001,000,200,000,001,000,204,000,000,"
    "000,080,206,001,010,004,006,000,001,010,004,000,000,000,284,000"
)
PRUNED38_D = (
    "00001100080,20004840000,20204400000,00000000000,01002200100,"
    "00000000000,00000000000,00200022000,00000000000,20400404000"
)


@dataclass(frozen=True)
class Option:
    groups: tuple[int, ...]
    final_units: int


@dataclass
class CoverResult:
    units: int
    choices: list[int]
    counts: Counter[int]
    restarts: int
    coordinate_moves: int
    pair_moves: int


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


def apply_row(row: int, matrix: Sequence[int]) -> int:
    result = 0
    while row:
        low = row & -row
        result ^= matrix[low.bit_length() - 1]
        row ^= low
    return result


def parse_hex_list(text: str, expected: int) -> tuple[int, ...]:
    values = tuple(int(value, 16) for value in text.strip().split(",") if value.strip())
    if len(values) != expected:
        raise ValueError(f"expected {expected} comma-separated hex values, got {len(values)}")
    return values


def parse_log_line(text: str) -> tuple[tuple[int, ...], tuple[int, ...]]:
    match = re.search(r"\bX=([0-9a-fA-F,]+)\s+D=([0-9a-fA-F,]+)", text)
    if not match:
        raise ValueError("input does not contain X=... D=...")
    return parse_hex_list(match.group(1), 32), parse_hex_list(match.group(2), 10)


def build_targets(x_rows: Sequence[int], d_rows: Sequence[int]) -> tuple[tuple[int, ...], int]:
    output = tuple((1 << index) | (x_rows[index] << VISIBLE) for index in range(VISIBLE))
    a_rows = transition_rows()
    top = tuple(
        apply_row(a_rows[index], output) ^ apply_row(x_rows[index], d_rows)
        for index in range(VISIBLE)
    )
    active = tuple(index for index, row in enumerate(d_rows) if row)
    kept_columns = tuple(range(VISIBLE)) + tuple(VISIBLE + index for index in active)

    def project(row: int) -> int:
        return sum(((row >> old) & 1) << new for new, old in enumerate(kept_columns))

    h_rows = tuple(project(row) for row in top) + tuple(project(d_rows[index]) for index in active)
    o_rows = tuple(project(row) for row in output)
    targets = tuple(sorted({row for row in h_rows + o_rows if row.bit_count() >= 2}))
    return targets, len(active)


def pattern_partitions(weight: int) -> tuple[tuple[tuple[int, ...], ...], ...]:
    result: set[tuple[tuple[int, ...], ...]] = set()

    def visit(index: int, blocks: list[list[int]]) -> None:
        if index == weight:
            result.add(tuple(sorted(tuple(block) for block in blocks)))
            return
        for block in blocks:
            if len(block) < 3:
                block.append(index)
                visit(index + 1, blocks)
                block.pop()
        if len(blocks) < 3:
            blocks.append([index])
            visit(index + 1, blocks)
            blocks.pop()

    visit(0, [])
    return tuple(sorted(result))


PARTITIONS = {weight: pattern_partitions(weight) for weight in range(2, 10)}


def group_cost(group: int) -> int:
    return 1 if group.bit_count() == 2 else 4


def make_options(target: int, width: int) -> tuple[Option, ...]:
    support = tuple(bit for bit in range(width) if (target >> bit) & 1)
    if not 2 <= len(support) <= 9:
        return ()
    options: list[Option] = []
    for pattern in PARTITIONS[len(support)]:
        groups = []
        for block in pattern:
            if len(block) >= 2:
                groups.append(sum(1 << support[index] for index in block))
        final_units = 0 if len(pattern) == 1 else (1 if len(pattern) == 2 else 4)
        options.append(Option(tuple(sorted(groups)), final_units))
    return tuple(options)


def option_standalone(option: Option) -> int:
    return option.final_units + sum(group_cost(group) for group in option.groups)


def cover_cost(options: Sequence[Sequence[Option]], choices: Sequence[int]) -> tuple[int, Counter[int]]:
    counts: Counter[int] = Counter()
    final = 0
    for row_options, choice in zip(options, choices):
        option = row_options[choice]
        final += option.final_units
        counts.update(option.groups)
    return final + sum(group_cost(group) for group in counts), counts


def add_option(counts: Counter[int], option: Option, direction: int) -> None:
    for group in option.groups:
        counts[group] += direction
        if counts[group] == 0:
            del counts[group]


def marginal_cost(counts: Counter[int], option: Option) -> int:
    return option.final_units + sum(group_cost(group) for group in option.groups if group not in counts)


def best_response(
    options: Sequence[Sequence[Option]],
    choices: list[int],
    counts: Counter[int],
    order: Iterable[int],
) -> int:
    moves = 0
    for target_index in order:
        row_options = options[target_index]
        old_index = choices[target_index]
        old = row_options[old_index]
        add_option(counts, old, -1)
        best_index = min(
            range(len(row_options)),
            key=lambda index: (marginal_cost(counts, row_options[index]), option_standalone(row_options[index]), index),
        )
        if best_index != old_index:
            moves += 1
            choices[target_index] = best_index
        add_option(counts, row_options[best_index], 1)
    return moves


def initialize_choices(
    options: Sequence[Sequence[Option]], rng: random.Random, mode: int
) -> tuple[list[int], Counter[int]]:
    choices = [-1] * len(options)
    counts: Counter[int] = Counter()
    order = list(range(len(options)))
    if mode:
        rng.shuffle(order)
    else:
        order.sort(key=lambda index: (len(options[index]), -len(options[index][0].groups)))
    for target_index in order:
        row_options = options[target_index]
        scored = sorted(
            (
                marginal_cost(counts, option),
                option_standalone(option),
                rng.random() if mode else index,
                index,
            )
            for index, option in enumerate(row_options)
        )
        # Random starts stay near a sensible incremental solution rather than
        # drawing uniformly from hundreds of structurally poor partitions.
        pool = scored[: min(len(scored), 1 + mode * 5)]
        choice = pool[rng.randrange(len(pool))][3] if mode else pool[0][3]
        choices[target_index] = choice
        add_option(counts, row_options[choice], 1)
    return choices, counts


def pair_improve(
    options: Sequence[Sequence[Option]], choices: list[int], counts: Counter[int], top_k: int
) -> int:
    """Try bounded exact two-target moves around the current solution."""
    moves = 0
    indices = list(range(len(options)))
    # Rows with many alternatives benefit most from a joint move.
    indices.sort(key=lambda index: len(options[index]), reverse=True)
    for offset, left_index in enumerate(indices):
        for right_index in indices[offset + 1 :]:
            left_options = options[left_index]
            right_options = options[right_index]
            old_left = left_options[choices[left_index]]
            old_right = right_options[choices[right_index]]
            add_option(counts, old_left, -1)
            add_option(counts, old_right, -1)

            left_short = sorted(
                range(len(left_options)),
                key=lambda index: (marginal_cost(counts, left_options[index]), option_standalone(left_options[index])),
            )[:top_k]
            right_short = sorted(
                range(len(right_options)),
                key=lambda index: (marginal_cost(counts, right_options[index]), option_standalone(right_options[index])),
            )[:top_k]
            best = None
            for left_choice in left_short:
                left = left_options[left_choice]
                add_option(counts, left, 1)
                for right_choice in right_short:
                    value = left.final_units + marginal_cost(counts, right_options[right_choice])
                    # left's newly opened groups were omitted from marginal_cost.
                    value += sum(group_cost(group) for group in left.groups if counts[group] == 1)
                    key = (value, left_choice, right_choice)
                    if best is None or key < best:
                        best = key
                add_option(counts, left, -1)
            assert best is not None
            _, new_left_index, new_right_index = best
            new_left = left_options[new_left_index]
            new_right = right_options[new_right_index]

            old_local = old_left.final_units + old_right.final_units
            new_local = new_left.final_units + new_right.final_units
            old_groups = set(old_left.groups) | set(old_right.groups)
            new_groups = set(new_left.groups) | set(new_right.groups)
            old_local += sum(group_cost(group) for group in old_groups if group not in counts)
            new_local += sum(group_cost(group) for group in new_groups if group not in counts)
            if new_local < old_local:
                choices[left_index] = new_left_index
                choices[right_index] = new_right_index
                add_option(counts, new_left, 1)
                add_option(counts, new_right, 1)
                moves += 1
            else:
                add_option(counts, old_left, 1)
                add_option(counts, old_right, 1)
    return moves


def solve_cover(
    options: Sequence[Sequence[Option]], restarts: int, seed: int, pair_top_k: int
) -> CoverResult:
    rng = random.Random(seed)
    best: CoverResult | None = None
    total_coordinate = 0
    total_pair = 0
    for restart in range(restarts):
        choices, counts = initialize_choices(options, rng, 0 if restart == 0 else 1 + restart % 3)
        coordinate_moves = 0
        pair_moves = 0
        for pass_index in range(20):
            order = list(range(len(options)))
            if pass_index or restart:
                rng.shuffle(order)
            changed = best_response(options, choices, counts, order)
            coordinate_moves += changed
            if not changed:
                break
        if pair_top_k and restart < max(2, restarts // 8):
            pair_moves = pair_improve(options, choices, counts, pair_top_k)
            if pair_moves:
                for _ in range(10):
                    order = list(range(len(options)))
                    rng.shuffle(order)
                    changed = best_response(options, choices, counts, order)
                    coordinate_moves += changed
                    if not changed:
                        break
        units, checked_counts = cover_cost(options, choices)
        assert checked_counts == counts
        total_coordinate += coordinate_moves
        total_pair += pair_moves
        candidate = CoverResult(units, choices.copy(), counts.copy(), restart + 1, total_coordinate, total_pair)
        if best is None or candidate.units < best.units:
            best = candidate
    assert best is not None
    best.restarts = restarts
    best.coordinate_moves = total_coordinate
    best.pair_moves = total_pair
    return best


def cheap_proxy(targets: Sequence[int], active_hidden: int) -> dict[str, object]:
    """Return calibrated inner-loop and pair-aware second-stage estimates.

    Coefficients were fitted against 305 historical valid states labeled by
    the same local-cover objective.  The weight model is O(rows); the pair
    model is O(sum support**2) and explicitly distinguishes reusable subsets.
    Both are estimates rather than realizable covers.
    """
    weight_distribution = Counter(target.bit_count() for target in targets)
    forced_pairs = {target for target in targets if target.bit_count() == 2}
    pair_frequency: Counter[int] = Counter()
    forced_hits = 0
    for target in targets:
        bits = [bit for bit in range(VISIBLE + active_hidden) if (target >> bit) & 1]
        if len(bits) >= 3:
            forced_hits += sum(pair & target == pair for pair in forced_pairs)
        for i in range(len(bits)):
            for j in range(i + 1, len(bits)):
                pair_frequency[(1 << bits[i]) | (1 << bits[j])] += 1

    # Effective per-weight coefficients after folding the standalone-cost
    # feature into the fitted weight terms.  One unit is three gates.
    weight_coefficients = {
        2: 0.984240596,
        3: 1.819465207,
        4: 1.884481679,
        5: 4.421289125,
        6: 4.747993227,
        7: 7.214848370,
        8: 10.530380694,
        9: 12.376739952,
    }
    weight_units = 9.922279531 + sum(
        weight_coefficients[weight] * weight_distribution[weight]
        for weight in range(2, 10)
    )

    pair_repeat = sum(count - 1 for count in pair_frequency.values())
    pair_ge2 = sum(count >= 2 for count in pair_frequency.values())
    pair_ge3 = sum(count >= 3 for count in pair_frequency.values())
    pair_weight_coefficients = {
        2: 1.062592456,
        3: 1.638593150,
        4: 1.755788182,
        5: 4.065578791,
        6: 4.235083046,
        7: 6.562904427,
        8: 9.424744996,
        9: 11.347225789,
    }
    pair_units = (
        6.706921541
        + sum(
            pair_weight_coefficients[weight] * weight_distribution[weight]
            for weight in range(2, 10)
        )
        + 0.031918304 * forced_hits
        - 0.013426717 * pair_repeat
        + 0.210352486 * pair_ge2
        - 0.190512249 * pair_ge3
    )
    fixed_gate = (VISIBLE + active_hidden) * DELAY_GATE + OR_AND_CONTROL_GATE
    return {
        "weight_model": {
            "logic_units_estimate": weight_units,
            "logic_gate_estimate": round(3 * weight_units),
            "total_gate_estimate": fixed_gate + round(3 * weight_units),
        },
        "pair_model": {
            "logic_units_estimate": pair_units,
            "logic_gate_estimate": round(3 * pair_units),
            "total_gate_estimate": fixed_gate + round(3 * pair_units),
        },
        "pair_features": {
            "forced_hits": forced_hits,
            "pair_incidence": sum(pair_frequency.values()),
            "pair_unique": len(pair_frequency),
            "pair_repeat": pair_repeat,
            "pair_ge2": pair_ge2,
            "pair_ge3": pair_ge3,
        },
    }


def evaluate(name: str, x_rows: Sequence[int], d_rows: Sequence[int], args: argparse.Namespace) -> dict[str, object]:
    started = time.perf_counter()
    targets, active_hidden = build_targets(x_rows, d_rows)
    maximum = max((target.bit_count() for target in targets), default=0)
    fixed_gate = (VISIBLE + active_hidden) * DELAY_GATE + OR_AND_CONTROL_GATE
    result: dict[str, object] = {
        "name": name,
        "active_hidden": active_hidden,
        "state_bits": VISIBLE + active_hidden,
        "fixed_gate": fixed_gate,
        "distinct_nontrivial_targets": len(targets),
        "weight_distribution": dict(sorted(Counter(target.bit_count() for target in targets).items())),
        "maximum_weight": maximum,
        "old_proxy_total_gate": 198 + 5 * active_hidden + 3 * len(targets)
        + 10 * sum(max(0, target.bit_count() - 4) for target in targets),
        "cheap_proxy": cheap_proxy(targets, active_hidden),
    }
    if maximum > 9:
        result["cover"] = {"status": "unsupported", "reason": "target weight exceeds 9"}
        return result
    row_options = [make_options(target, VISIBLE + active_hidden) for target in targets]
    greedy_choices, greedy_counts = initialize_choices(row_options, random.Random(0), 0)
    greedy_moves = 0
    for _ in range(8):
        changed = best_response(row_options, greedy_choices, greedy_counts, range(len(row_options)))
        greedy_moves += changed
        if not changed:
            break
    greedy_units, checked_greedy_counts = cover_cost(row_options, greedy_choices)
    assert checked_greedy_counts == greedy_counts
    result["greedy_cover"] = {
        "status": "heuristic_upper_bound",
        "logic_units": greedy_units,
        "logic_gate": greedy_units * 3,
        "total_gate": fixed_gate + greedy_units * 3,
        "selected_pair_groups": sum(group.bit_count() == 2 for group in greedy_counts),
        "selected_triple_groups": sum(group.bit_count() == 3 for group in greedy_counts),
        "coordinate_moves": greedy_moves,
    }
    cover = solve_cover(row_options, args.restarts, args.seed, args.pair_top_k)
    selected_final_units = sum(
        options[choice].final_units for options, choice in zip(row_options, cover.choices)
    )
    pair_groups = sum(group.bit_count() == 2 for group in cover.counts)
    triple_groups = sum(group.bit_count() == 3 for group in cover.counts)
    logic_gate = cover.units * 3
    result["cover"] = {
        "status": "heuristic_upper_bound",
        "logic_units": cover.units,
        "logic_gate": logic_gate,
        "total_gate": fixed_gate + logic_gate,
        "selected_final_units": selected_final_units,
        "selected_pair_groups": pair_groups,
        "selected_triple_groups": triple_groups,
        "selected_group_units": cover.units - selected_final_units,
        "restarts": cover.restarts,
        "coordinate_moves": cover.coordinate_moves,
        "pair_moves": cover.pair_moves,
    }
    result["seconds"] = time.perf_counter() - started
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--builtin", choices=("proxy506", "pruned38", "both"), default="both")
    source.add_argument("--line", help="search log line containing X=... D=...")
    source.add_argument("--line-file", help="file whose last X=... D=... line is evaluated")
    parser.add_argument("--x", help="32 comma-separated hexadecimal X masks")
    parser.add_argument("--d", help="10 comma-separated hexadecimal D rows")
    parser.add_argument("--name", default="candidate")
    parser.add_argument("--restarts", type=int, default=96)
    parser.add_argument("--pair-top-k", type=int, default=8)
    parser.add_argument("--seed", type=int, default=20260802)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    candidates: list[tuple[str, tuple[int, ...], tuple[int, ...]]] = []
    if args.x or args.d:
        if not args.x or not args.d:
            parser.error("--x and --d must be supplied together")
        candidates.append((args.name, parse_hex_list(args.x, 32), parse_hex_list(args.d, 10)))
    elif args.line:
        x_rows, d_rows = parse_log_line(args.line)
        candidates.append((args.name, x_rows, d_rows))
    elif args.line_file:
        lines = open(args.line_file, encoding="utf-8").read().splitlines()
        matching = [line for line in lines if "X=" in line and "D=" in line]
        if not matching:
            parser.error("--line-file has no X=... D=... line")
        x_rows, d_rows = parse_log_line(matching[-1])
        candidates.append((args.name, x_rows, d_rows))
    else:
        if args.builtin in ("proxy506", "both"):
            candidates.append(("proxy506", parse_hex_list(PROXY506_X, 32), parse_hex_list(PROXY506_D, 10)))
        if args.builtin in ("pruned38", "both"):
            candidates.append(("pruned38", parse_hex_list(PRUNED38_X, 32), parse_hex_list(PRUNED38_D, 10)))

    results = [evaluate(name, x_rows, d_rows, args) for name, x_rows, d_rows in candidates]
    document = {
        "schema": 1,
        "cost_unit_gate": 3,
        "library": {"XOR2_units": 1, "Switch_XOR3_units": 4, "final_1_2_3_group_units": [0, 1, 4]},
        "results": results,
    }
    if args.json:
        print(json.dumps(document, indent=2))
    else:
        for result in results:
            cover = result["cover"]
            print(
                f"{result['name']}: active={result['active_hidden']} targets={result['distinct_nontrivial_targets']} "
                f"weights={result['weight_distribution']} old={result['old_proxy_total_gate']} "
                f"weight={result['cheap_proxy']['weight_model']['total_gate_estimate']} "
                f"pair={result['cheap_proxy']['pair_model']['total_gate_estimate']} "
                f"greedy={result.get('greedy_cover', {}).get('total_gate', '-')} "
                f"cover={cover.get('total_gate', cover['status'])} "
                f"logic={cover.get('logic_gate', '-')} time={result.get('seconds', 0):.3f}s"
            )


if __name__ == "__main__":
    main()
