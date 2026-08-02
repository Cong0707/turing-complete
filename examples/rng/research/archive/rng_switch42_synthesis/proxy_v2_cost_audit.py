"""Fast shared-cover proxy audit for RNG lifted-state candidates.

This is intentionally separate from the exact PySAT model.  It enumerates the
same legal two-level XOR2/Switch-XOR3 partitions, then uses repeated coordinate
descent over target choices to obtain a cheap feasible cover upper bound.
"""

from __future__ import annotations

from collections import Counter
from functools import lru_cache
import json
import random
from pathlib import Path


VISIBLE = 32
HIDDEN = 10
MASK32 = (1 << VISIBLE) - 1


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


def build_rows(x_rows: tuple[int, ...], d_rows: tuple[int, ...]) -> tuple[tuple[int, ...], tuple[int, ...]]:
    a_rows = transition_rows()
    output = tuple((1 << index) | (x_rows[index] << VISIBLE) for index in range(VISIBLE))
    top = tuple(
        apply_row(a_rows[index], output) ^ apply_row(x_rows[index], d_rows)
        for index in range(VISIBLE)
    )
    return top + d_rows, output


def apply_matrix(matrix: tuple[int, ...], value: int) -> int:
    return sum(((row & value).bit_count() & 1) << index for index, row in enumerate(matrix))


def verify_sequences(h_rows: tuple[int, ...], o_rows: tuple[int, ...]) -> None:
    for seed in range(256):
        state = seed
        natural = seed
        for _ in range(65):
            state = apply_matrix(h_rows, state)
            natural = xorshift32(natural)
            if apply_matrix(o_rows, state) != natural:
                raise AssertionError(f"sequence mismatch for seed {seed}")


@lru_cache(maxsize=None)
def partitions(support: tuple[int, ...]) -> tuple[tuple[tuple[int, ...], ...], ...]:
    result: set[tuple[tuple[int, ...], ...]] = set()

    def visit(index: int, blocks: list[list[int]]) -> None:
        if index == len(support):
            canonical = tuple(sorted(tuple(block) for block in blocks))
            if len(canonical) <= 3 and all(len(block) <= 3 for block in canonical):
                result.add(canonical)
            return
        bit = support[index]
        for block in blocks:
            if len(block) < 3:
                block.append(bit)
                visit(index + 1, blocks)
                block.pop()
        if len(blocks) < 3:
            blocks.append([bit])
            visit(index + 1, blocks)
            blocks.pop()

    visit(0, [])
    return tuple(sorted(result))


def mask(block: tuple[int, ...]) -> int:
    return sum(1 << bit for bit in block)


def group_cost(group: int) -> int:
    return 3 if group.bit_count() == 2 else 12


def final_cost(option: tuple[tuple[int, ...], ...]) -> int:
    return (0, 0, 3, 12)[len(option)]


def target_options(row: int) -> tuple[tuple[int, tuple[int, ...]], ...]:
    support = tuple(bit for bit in range(VISIBLE + HIDDEN) if (row >> bit) & 1)
    return tuple(
        (final_cost(option), tuple(mask(block) for block in option if len(block) >= 2))
        for option in partitions(support)
    )


def cover_cost(options: list[tuple[tuple[int, tuple[int, ...]], ...]], chosen: list[int]) -> int:
    groups = {group for target, index in zip(options, chosen) for group in target[index][1]}
    return sum(options[index][choice][0] for index, choice in enumerate(chosen)) + sum(
        group_cost(group) for group in groups
    )


def greedy_cover(rows: tuple[int, ...], attempts: int = 24) -> dict[str, object]:
    targets = tuple(sorted({row for row in rows if row.bit_count() >= 2}))
    unsupported = sum(row.bit_count() > 9 for row in targets)
    if unsupported:
        return {"status": "unsupported", "unsupported": unsupported}
    options = [target_options(row) for row in targets]

    potential = Counter()
    for target in options:
        for group in {group for _, groups in target for group in groups}:
            potential[group] += 1

    best_chosen: list[int] | None = None
    best_cost = 10**9
    rng = random.Random(0x20260802)
    for attempt in range(attempts):
        if attempt == 0:
            chosen = [
                min(
                    range(len(target)),
                    key=lambda index: target[index][0] + sum(
                        group_cost(group) / potential[group] for group in target[index][1]
                    ),
                )
                for target in options
            ]
        elif attempt == 1:
            chosen = [
                min(
                    range(len(target)),
                    key=lambda index: target[index][0] + sum(group_cost(group) for group in target[index][1]),
                )
                for target in options
            ]
        else:
            chosen = [rng.randrange(len(target)) for target in options]

        refs = Counter(group for target, index in zip(options, chosen) for group in target[index][1])
        for _ in range(20):
            changed = False
            order = list(range(len(options)))
            rng.shuffle(order)
            for target_index in order:
                old = chosen[target_index]
                old_final, old_groups = options[target_index][old]
                for group in old_groups:
                    refs[group] -= 1
                new = min(
                    range(len(options[target_index])),
                    key=lambda index: (
                        options[target_index][index][0]
                        + sum(group_cost(group) for group in options[target_index][index][1] if refs[group] == 0),
                        index,
                    ),
                )
                chosen[target_index] = new
                for group in options[target_index][new][1]:
                    refs[group] += 1
                changed |= new != old
            if not changed:
                break
        cost = cover_cost(options, chosen)
        if cost < best_cost:
            best_cost = cost
            best_chosen = chosen[:]

    assert best_chosen is not None
    groups = {
        group
        for target, index in zip(options, best_chosen)
        for group in target[index][1]
    }
    active_hidden = sum(row != 0 for row in rows[VISIBLE:VISIBLE + HIDDEN])
    fixed = 198 + 5 * active_hidden
    histogram = Counter(row.bit_count() for row in targets)
    fractional = sum(
        min(
            final + sum(group_cost(group) / potential[group] for group in option_groups)
            for final, option_groups in target
        )
        for target in options
    )
    return {
        "status": "ok",
        "active_hidden": active_hidden,
        "fixed_gate": fixed,
        "distinct_targets": len(targets),
        "weight_histogram": dict(sorted(histogram.items())),
        "fractional_logic_proxy": fractional,
        "greedy_logic_gate": best_cost,
        "greedy_total_gate": fixed + best_cost,
        "selected_pair_groups": sum(group.bit_count() == 2 for group in groups),
        "selected_triple_groups": sum(group.bit_count() == 3 for group in groups),
    }


def parse(values: str) -> tuple[int, ...]:
    return tuple(int(value, 16) for value in values.split(","))


CANDIDATES = {
    "alt_k1_total530": (
        parse("000,000,000,000,000,000,000,000,000,000,000,000,001,000,000,000,000,000,000,000,000,000,000,000,000,001,000,000,000,000,000,000"),
        parse("00142002000,00000000000,00000000000,00000000000,00000000000,00000000000,00000000000,00000000000,00000000000,00000000000"),
    ),
    "beam6_proxy497": (
        parse("002,001,020,010,008,002,000,020,000,008,000,000,004,000,000,000,000,002,001,020,010,008,002,000,020,004,008,000,000,000,000,000"),
        parse("00000084042,00100440020,00042003000,00204400200,00800300100,01001100080,00000000000,00000000000,00000000000,00000000000"),
    ),
    "current42": (
        parse("010,022,040,004,008,090,0e0,040,100,200,080,044,101,100,200,004,008,011,022,040,004,108,210,020,040,100,300,280,000,000,100,000"),
        parse("20040020001,20000044002,00000110008,00100220010,02200040020,08000880040,00401100080,02000800400,20084002000,08008404000"),
    ),
    "pruned38": (
        parse("000,000,001,010,084,002,001,001,000,200,000,001,000,204,000,000,000,080,206,001,010,004,006,000,001,010,004,000,000,000,284,000"),
        parse("00001100080,20004840000,20204400000,00000000000,01002200100,00000000000,00000000000,00200022000,00000000000,20400404000"),
    ),
    "natural32": ((0,) * VISIBLE, (0,) * HIDDEN),
}


def main() -> None:
    result = {}
    for name, (x_rows, d_rows) in CANDIDATES.items():
        h_rows, o_rows = build_rows(x_rows, d_rows)
        verify_sequences(h_rows, o_rows)
        result[name] = greedy_cover(h_rows + o_rows)
        result[name]["verified_sequences"] = {"seeds": 256, "outputs_per_seed": 65}
    output = Path(__file__).with_name("proxy_v2_cost_audit.json")
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
