"""Exact low-memory SMT search for a delay-nine sparse initialization basis.

For a nonsingular binary matrix whose rows have weight at most two, each
connected component of the row-support graph is a tree with one singleton
row.  Up to a free permutation of encoded state coordinates, write it as

    q[root] = x[root]
    q[v]    = x[v] xor x[parent[v]].

This script searches those rooted forests directly.  It neither imports the
save writer nor touches the game process or formal candidate path.
"""

from __future__ import annotations

import argparse
from collections import deque
import json
from pathlib import Path
import random
from typing import Iterable, Sequence

import z3


N = 32
MASK = (1 << N) - 1
IDENTITY = tuple(1 << bit for bit in range(N))


def xorshift32(value: int) -> int:
    value &= MASK
    value ^= value >> 13
    value ^= (value << 17) & MASK
    value ^= value >> 5
    return value & MASK


def matrix_from_function(function) -> tuple[int, ...]:
    return tuple(
        sum(((function(1 << source) >> target) & 1) << source for source in range(N))
        for target in range(N)
    )


A = matrix_from_function(xorshift32)


def apply_row(row: int, matrix: Sequence[int]) -> int:
    result = 0
    while row:
        bit = row & -row
        result ^= matrix[bit.bit_length() - 1]
        row ^= bit
    return result


def compose(left: Sequence[int], right: Sequence[int]) -> tuple[int, ...]:
    return tuple(apply_row(row, right) for row in left)


def apply_matrix(matrix: Sequence[int], value: int) -> int:
    return sum(((row & value).bit_count() & 1) << bit for bit, row in enumerate(matrix))


def xor_all(values: Iterable[z3.BoolRef]) -> z3.BoolRef:
    values = tuple(values)
    if not values:
        return z3.BoolVal(False)
    result = values[0]
    for value in values[1:]:
        result = z3.Xor(result, value)
    return result


def forest_from_sparse_rows(rows: Sequence[int]) -> tuple[int, ...]:
    """Orient an unordered tree/singleton row basis into canonical parents."""

    adjacency = [set() for _ in range(N)]
    roots: set[int] = set()
    for row in rows:
        support = [bit for bit in range(N) if row >> bit & 1]
        if len(support) == 1:
            roots.add(support[0])
        elif len(support) == 2:
            first, second = support
            adjacency[first].add(second)
            adjacency[second].add(first)
        else:
            raise ValueError("sparse T row is neither singleton nor pair")

    parent = [-2] * N
    for root in sorted(roots):
        if parent[root] != -2:
            raise ValueError("two singleton roots occur in one component")
        parent[root] = -1
        queue = deque([root])
        while queue:
            node = queue.popleft()
            for child in adjacency[node]:
                if child == parent[node]:
                    continue
                if parent[child] != -2:
                    raise ValueError("pair rows contain a cycle")
                parent[child] = node
                queue.append(child)
    if any(value == -2 for value in parent):
        raise ValueError("component has no singleton root")
    return tuple(parent)


def matrices_from_parent(parent: Sequence[int]) -> tuple[tuple[int, ...], ...]:
    T = tuple(
        (1 << node) if p < 0 else (1 << node) ^ (1 << p)
        for node, p in enumerate(parent)
    )
    ancestors = []
    for node in range(N):
        row = 0
        current = node
        while current >= 0:
            bit = 1 << current
            if row & bit:
                raise ValueError("parent cycle")
            row |= bit
            current = parent[current]
        ancestors.append(row)
    # T^-1 row x[node] is the xor of q along node's ancestor chain.
    T_inverse = tuple(ancestors)
    C = compose(A, T_inverse)
    B = tuple(C[node] if p < 0 else C[node] ^ C[p] for node, p in enumerate(parent))
    return T, T_inverse, B, C


def pair_options(row: int) -> tuple[frozenset[int], ...]:
    support = [1 << bit for bit in range(N) if row >> bit & 1]
    if len(support) == 3:
        return tuple(frozenset((row ^ lone,)) for lone in support)
    if len(support) == 4:
        first, second, third, fourth = support
        return (
            frozenset((first | second, third | fourth)),
            frozenset((first | third, second | fourth)),
            frozenset((first | fourth, second | third)),
        )
    return ()


def greedy_depth_two(rows: Sequence[int]) -> tuple[int, tuple[int, ...]]:
    targets = frozenset(rows)
    if 0 in targets or any(row.bit_count() > 4 for row in targets):
        return 1000, ()
    selected = {row for row in targets if row.bit_count() == 2}
    finals = frozenset(row for row in targets if row.bit_count() >= 3)

    def covered(row: int, pairs: set[int]) -> bool:
        return any(option <= pairs for option in pair_options(row))

    while True:
        unmet = [row for row in finals if not covered(row, selected)]
        if not unmet:
            break
        actions = {
            option - selected
            for row in unmet
            for option in pair_options(row)
            if option - selected
        }
        action = max(
            actions,
            key=lambda item: (
                sum(covered(row, selected | set(item)) for row in unmet) / len(item),
                sum(covered(row, selected | set(item)) for row in unmet),
                -len(item),
                tuple(-value for value in sorted(item)),
            ),
        )
        selected.update(action)
    return len(selected) + len(finals), tuple(sorted(selected))


def verify(parent: Sequence[int], T: Sequence[int], B: Sequence[int], C: Sequence[int]) -> None:
    rebuilt_T, T_inverse, rebuilt_B, rebuilt_C = matrices_from_parent(parent)
    assert tuple(T) == rebuilt_T
    assert tuple(B) == rebuilt_B and tuple(C) == rebuilt_C
    assert compose(T, T_inverse) == IDENTITY
    assert compose(C, T) == A
    assert compose(T, C) == B
    for seed in [0, 1, 2, 0x12345678, MASK, *(random.Random(0x9901).getrandbits(32) for _ in range(251))]:
        q = apply_matrix(T, seed)
        natural = seed
        for _ in range(65):
            natural = xorshift32(natural)
            assert apply_matrix(C, q) == natural
            q = apply_matrix(B, q)


def solve(args: argparse.Namespace) -> dict[str, object]:
    start_parent: tuple[int, ...] | None = None
    if args.start_json:
        payload = json.loads(args.start_json.read_text(encoding="utf-8"))
        start_parent = forest_from_sparse_rows(tuple(int(value, 16) for value in payload["T"]))

    solver = z3.Solver()
    solver.set(timeout=args.timeout_ms, max_memory=args.max_memory_mb)
    root = [z3.Bool(f"root_{node}") for node in range(N)]
    edge = [
        [z3.Bool(f"edge_{node}_{candidate}") for candidate in range(N)]
        for node in range(N)
    ]
    depth = [z3.Int(f"depth_{node}") for node in range(N)]
    ancestor = [
        [z3.Bool(f"ancestor_{node}_{candidate}") for candidate in range(N)]
        for node in range(N)
    ]

    for node in range(N):
        solver.add(edge[node][node] == False)
        solver.add(z3.PbEq([(root[node], 1), *((edge[node][p], 1) for p in range(N) if p != node)], 1))
        solver.add(depth[node] >= 0, depth[node] < N)
        solver.add(z3.Implies(root[node], depth[node] == 0))
        for p in range(N):
            if p != node:
                solver.add(z3.Implies(edge[node][p], depth[node] == depth[p] + 1))

    for node in range(N):
        for candidate in range(N):
            if node == candidate:
                solver.add(ancestor[node][candidate])
            else:
                solver.add(
                    ancestor[node][candidate]
                    == z3.Or(
                        *(z3.And(edge[node][p], ancestor[p][candidate]) for p in range(N) if p != node)
                    )
                )

    c_bit = [[None for _ in range(N)] for _ in range(N)]
    for output, row in enumerate(A):
        support = [source for source in range(N) if row >> source & 1]
        for encoded in range(N):
            c_bit[output][encoded] = xor_all(ancestor[source][encoded] for source in support)
        solver.add(z3.PbLe([(value, 1) for value in c_bit[output]], 4))

    b_bit = [[None for _ in range(N)] for _ in range(N)]
    for output in range(N):
        for encoded in range(N):
            parent_value = z3.Or(
                *(z3.And(edge[output][p], c_bit[p][encoded]) for p in range(N) if p != output)
            )
            b_bit[output][encoded] = z3.Xor(c_bit[output][encoded], parent_value)
        solver.add(z3.PbLe([(value, 1) for value in b_bit[output]], 4))

    nonroots = z3.Sum([z3.If(value, 0, 1) for value in root])
    solver.add(nonroots <= args.max_init_xor)
    unit_b = [z3.PbEq([(value, 1) for value in row], 1) for row in b_bit]
    if args.target_necessary:
        # Every C row is non-unit, and each forest edge contributes a distinct
        # B target not present in C.  Before extra pair intermediates, any
        # r+L<=77 candidate therefore needs 32 + 2*r - unit_B <= 77.
        solver.add(32 + 2 * nonroots - z3.Sum([z3.If(value, 1, 0) for value in unit_b]) <= 77)
        solver.add(z3.PbLe([(value, 1) for value in unit_b], 8))
        allowed_unit_edges = {
            2: 19,
            3: 20,
            4: 21,
            5: 22,
            6: 23,
            7: 24,
            8: 25,
            9: 26,
            19: 2,
            20: 3,
            21: 4,
            22: 5,
            23: 6,
            24: 7,
            25: 8,
            26: 9,
        }
        for node, is_unit in enumerate(unit_b):
            peer = allowed_unit_edges.get(node)
            solver.add(z3.Implies(is_unit, False if peer is None else edge[node][peer]))
    if start_parent is not None and args.radius is not None:
        changed = []
        for node, p in enumerate(start_parent):
            same = root[node] if p < 0 else edge[node][p]
            changed.append(z3.If(same, 0, 1))
        solver.add(z3.Sum(changed) <= args.radius)

    status = solver.check()
    result: dict[str, object] = {
        "status": str(status),
        "timeout_ms": args.timeout_ms,
        "max_memory_mb": args.max_memory_mb,
        "max_init_xor": args.max_init_xor,
        "target_necessary": args.target_necessary,
        "radius": args.radius,
        "start_json": None if args.start_json is None else str(args.start_json),
        "reason_unknown": solver.reason_unknown() if status == z3.unknown else None,
        "statistics": str(solver.statistics()),
    }
    if status != z3.sat:
        return result

    model = solver.model()
    parent = tuple(
        -1
        if z3.is_true(model.eval(root[node], model_completion=True))
        else next(
            p
            for p in range(N)
            if p != node and z3.is_true(model.eval(edge[node][p], model_completion=True))
        )
        for node in range(N)
    )
    T, _T_inverse, B, C = matrices_from_parent(parent)
    verify(parent, T, B, C)
    xor_count, pairs = greedy_depth_two((*B, *C))
    init_xor = sum(p >= 0 for p in parent)
    gate = 198 + 3 * (init_xor + xor_count)
    result["candidate"] = {
        "parent": list(parent),
        "T": [f"{row:08x}" for row in T],
        "B": [f"{row:08x}" for row in B],
        "C": [f"{row:08x}" for row in C],
        "selected_pair_gates": [f"{row:08x}" for row in pairs],
        "metrics": {
            "init_xor": init_xor,
            "steady_greedy_xor": xor_count,
            "xor_total": init_xor + xor_count,
            "gate": gate,
            "delay": 9,
            "cycles": 66,
            "energy": gate * 9 * 66,
            "beats_256014": gate * 9 * 66 < 256014,
        },
        "verification": {
            "C*T=A": True,
            "T*C=B": True,
            "seed_count": 256,
            "outputs_per_seed": 65,
        },
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-json", type=Path)
    parser.add_argument("--radius", type=int)
    parser.add_argument("--max-init-xor", type=int, default=28)
    parser.add_argument("--target-necessary", action="store_true")
    parser.add_argument("--timeout-ms", type=int, default=180_000)
    parser.add_argument("--max-memory-mb", type=int, default=768)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = solve(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "candidate"}, indent=2))
    if "candidate" in result:
        print(json.dumps(result["candidate"]["metrics"], indent=2))
    return 0 if result["status"] in {"sat", "unsat"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
