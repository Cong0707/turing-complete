"""Synthesize a two-level XOR2/XOR3 network for the RNG transition matrix.

This is an offline feasibility model for a strict one-input architecture.  A
single U32 Word Switch presents raw ``seed`` on tick zero and a permutation of
the 32 bit-state registers afterwards.  Choosing ``T = P^-1 A`` makes the
visible output the switched word itself and leaves the shared feedback network
with exactly the 32 rows of the xorshift32 matrix ``A``.

The model below restricts every first-level node to XOR2 or the reviewed
12-gate/2-delay XOR3 macro.  Each target is either a selected first-level XOR3
or a second-level XOR2/XOR3 over disjoint first-level blocks.  It is a useful
constructive upper-bound search, not a global lower-bound proof.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Iterable

from pysat.examples.rc2 import RC2
from pysat.formula import IDPool, WCNF


BITS = 32
MASK = (1 << BITS) - 1
XOR2_COST = 3
XOR3_COST = 12
STATE_AND_CONTROL_COST = 32 * 5 + 64 + 5 + 1
NETWORK_BUDGET = 430 - STATE_AND_CONTROL_COST


def xorshift32(value: int) -> int:
    value ^= value >> 13
    value ^= (value << 17) & MASK
    value ^= value >> 5
    return value & MASK


def matrix_from_function() -> tuple[int, ...]:
    return tuple(
        sum(
            ((xorshift32(1 << source) >> output) & 1) << source
            for source in range(BITS)
        )
        for output in range(BITS)
    )


A = matrix_from_function()


def bits(mask: int) -> tuple[int, ...]:
    return tuple(index for index in range(BITS) if (mask >> index) & 1)


def set_partitions(
    items: tuple[int, ...], block_count: int, maximum_block_size: int = 3
) -> Iterable[tuple[int, ...]]:
    """Yield canonical unordered set partitions as bit masks."""

    blocks: list[list[int]] = []

    def visit(index: int) -> Iterable[tuple[int, ...]]:
        if index == len(items):
            if len(blocks) == block_count:
                yield tuple(sum(1 << value for value in block) for block in blocks)
            return

        value = items[index]
        for block in blocks:
            if len(block) >= maximum_block_size:
                continue
            block.append(value)
            yield from visit(index + 1)
            block.pop()

        if len(blocks) < block_count:
            blocks.append([value])
            yield from visit(index + 1)
            blocks.pop()

    yield from visit(0)


@dataclass(frozen=True)
class Decomposition:
    target_index: int
    final_kind: str
    blocks: tuple[int, ...]

    @property
    def final_cost(self) -> int:
        if self.final_kind == "direct":
            return 0
        if self.final_kind == "xor2":
            return XOR2_COST
        if self.final_kind == "xor3":
            return XOR3_COST
        raise AssertionError(self.final_kind)

    @property
    def intermediates(self) -> tuple[int, ...]:
        return tuple(block for block in self.blocks if block.bit_count() > 1)


def decompositions(target_index: int, target: int) -> tuple[Decomposition, ...]:
    support = bits(target)
    result: list[Decomposition] = []

    if len(support) == 3:
        result.append(Decomposition(target_index, "direct", (target,)))

    for count, kind in ((2, "xor2"), (3, "xor3")):
        for partition in set_partitions(support, count):
            result.append(Decomposition(target_index, kind, partition))

    unique = {
        (item.final_kind, tuple(sorted(item.blocks))): item for item in result
    }
    return tuple(
        unique[key]
        for key in sorted(unique, key=lambda value: (value[0], value[1]))
    )


def intermediate_cost(mask: int) -> int:
    weight = mask.bit_count()
    if weight == 2:
        return XOR2_COST
    if weight == 3:
        return XOR3_COST
    raise ValueError(f"unsupported first-level mask {mask:08x} with weight {weight}")


def solve() -> dict[str, object]:
    target_decompositions = tuple(
        decompositions(index, target) for index, target in enumerate(A)
    )
    if any(not choices for choices in target_decompositions):
        raise RuntimeError("at least one A row has no depth-two decomposition")

    pool = IDPool()
    formula = WCNF()
    intermediate_masks = sorted(
        {
            mask
            for choices in target_decompositions
            for choice in choices
            for mask in choice.intermediates
        }
    )
    intermediate_vars = {
        mask: pool.id(("intermediate", mask)) for mask in intermediate_masks
    }
    decomposition_vars: dict[Decomposition, int] = {}

    for choices in target_decompositions:
        variables: list[int] = []
        for choice in choices:
            variable = pool.id(
                (
                    "decomposition",
                    choice.target_index,
                    choice.final_kind,
                    choice.blocks,
                )
            )
            decomposition_vars[choice] = variable
            variables.append(variable)
            for mask in choice.intermediates:
                formula.append([-variable, intermediate_vars[mask]])
            if choice.final_cost:
                formula.append([-variable], weight=choice.final_cost)
        formula.append(variables)

    for mask, variable in intermediate_vars.items():
        formula.append([-variable], weight=intermediate_cost(mask))

    with RC2(formula, solver="g4", adapt=True, exhaust=True, incr=False) as solver:
        model = solver.compute()
        optimum = solver.cost
    if model is None:
        raise RuntimeError("weighted model unexpectedly has no solution")
    positive = {literal for literal in model if literal > 0}

    selected_intermediates = tuple(
        mask for mask, variable in intermediate_vars.items() if variable in positive
    )
    selected_choices: list[Decomposition] = []
    for choices in target_decompositions:
        active = [
            choice for choice in choices if decomposition_vars[choice] in positive
        ]
        if not active:
            raise RuntimeError("RC2 model omitted a target decomposition")
        selected_choices.append(min(active, key=lambda item: item.final_cost))

    recomputed_cost = sum(intermediate_cost(mask) for mask in selected_intermediates)
    recomputed_cost += sum(choice.final_cost for choice in selected_choices)
    if recomputed_cost != optimum:
        raise RuntimeError(
            f"model cost mismatch: selected={recomputed_cost}, optimum={optimum}"
        )

    for target, choice in zip(A, selected_choices):
        combined = 0
        for block in choice.blocks:
            combined ^= block
            if block.bit_count() > 1 and block not in selected_intermediates:
                raise RuntimeError("selected decomposition uses an absent intermediate")
        if combined != target:
            raise RuntimeError(
                f"decomposition mismatch: {combined:08x} != {target:08x}"
            )

    total_gate = STATE_AND_CONTROL_COST + optimum
    return {
        "schema": 1,
        "scope": (
            "strict one Architecture Input/Output; one U32 Word Switch; "
            "disjoint-support depth-two XOR2/XOR3 feedback network"
        ),
        "status": "within-budget" if optimum <= NETWORK_BUDGET else "over-budget",
        "fixed_gate": STATE_AND_CONTROL_COST,
        "network_budget": NETWORK_BUDGET,
        "network_gate": optimum,
        "total_gate": total_gate,
        "predicted_delay": 9,
        "predicted_cycles": 66,
        "target_row_weight_histogram": {
            str(weight): sum(row.bit_count() == weight for row in A)
            for weight in sorted({row.bit_count() for row in A})
        },
        "intermediate_count": len(selected_intermediates),
        "intermediates": [
            {
                "mask_hex": f"{mask:08x}",
                "support": list(bits(mask)),
                "kind": f"xor{mask.bit_count()}",
                "gate": intermediate_cost(mask),
            }
            for mask in selected_intermediates
        ],
        "targets": [
            {
                "index": index,
                "target_hex": f"{target:08x}",
                "final_kind": choice.final_kind,
                "final_gate": choice.final_cost,
                "blocks_hex": [f"{block:08x}" for block in choice.blocks],
            }
            for index, (target, choice) in enumerate(zip(A, selected_choices))
        ],
        "model_counts": {
            "candidate_intermediates": len(intermediate_masks),
            "candidate_decompositions": sum(
                len(choices) for choices in target_decompositions
            ),
            "variables": pool.top,
            "hard_clauses": len(formula.hard),
            "soft_clauses": len(formula.soft),
        },
        "limitations": [
            "Only disjoint-support decompositions are enumerated.",
            "Only XOR2 and the reviewed 12-gate/2-delay XOR3 macro are allowed.",
            "An over-budget result is not a global impossibility proof.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    result = solve()
    payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if arguments.output:
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        arguments.output.write_text(payload, encoding="utf-8")
        result["output_sha256"] = sha256(payload.encode()).hexdigest()
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
