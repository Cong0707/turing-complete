"""Guided relaxed forest search for the independent-init delay-9 route.

Unlike forest_smt.py's all-or-nothing support-four constraints, this model can
bound the number of heavy B/C rows.  A known near solution is supplied only as
Z3 initial phases, not as a neighborhood constraint, so SAT certificates remain
global over all rooted forests.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys

import z3


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("forest_base", HERE / "forest_smt.py")
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load forest_smt.py")
base = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = base
spec.loader.exec_module(base)
N = base.N


def depth_and_ancestors(parent: tuple[int, ...]):
    depth = []
    ancestors = []
    for node in range(N):
        d = 0
        mask = 0
        current = node
        while current >= 0:
            mask |= 1 << current
            current = parent[current]
            d += current >= 0
        depth.append(d)
        ancestors.append(mask)
    return tuple(depth), tuple(ancestors)


def solve(args: argparse.Namespace) -> dict[str, object]:
    payload = json.loads(args.hint_json.read_text(encoding="utf-8"))
    hint_parent = base.forest_from_sparse_rows(tuple(int(value, 16) for value in payload["T"]))
    hint_depth, hint_ancestors = depth_and_ancestors(hint_parent)

    solver = z3.Solver()
    solver.set(timeout=args.timeout_ms, max_memory=args.max_memory_mb, random_seed=args.random_seed)
    root = [z3.Bool(f"root_{node}") for node in range(N)]
    edge = [[z3.Bool(f"edge_{node}_{p}") for p in range(N)] for node in range(N)]
    depth = [z3.Int(f"depth_{node}") for node in range(N)]
    ancestor = [[z3.Bool(f"ancestor_{node}_{a}") for a in range(N)] for node in range(N)]

    for node in range(N):
        solver.add(z3.Not(edge[node][node]))
        solver.add(z3.PbEq([(root[node], 1), *((edge[node][p], 1) for p in range(N) if p != node)], 1))
        solver.add(depth[node] >= 0, depth[node] < N)
        solver.add(z3.Implies(root[node], depth[node] == 0))
        for p in range(N):
            if p != node:
                solver.add(z3.Implies(edge[node][p], depth[node] == depth[p] + 1))

        solver.set_initial_value(root[node], hint_parent[node] < 0)
        solver.set_initial_value(depth[node], hint_depth[node])
        for p in range(N):
            solver.set_initial_value(edge[node][p], hint_parent[node] == p)

    for node in range(N):
        for candidate in range(N):
            if node == candidate:
                solver.add(ancestor[node][candidate])
            else:
                solver.add(
                    ancestor[node][candidate]
                    == z3.Or(*(z3.And(edge[node][p], ancestor[p][candidate]) for p in range(N) if p != node))
                )
            solver.set_initial_value(ancestor[node][candidate], bool(hint_ancestors[node] >> candidate & 1))

    c_bit = [[None] * N for _ in range(N)]
    c_heavy = []
    for output, row in enumerate(base.A):
        support = [source for source in range(N) if row >> source & 1]
        for encoded in range(N):
            c_bit[output][encoded] = base.xor_all(ancestor[source][encoded] for source in support)
        solver.add(z3.PbLe([(value, 1) for value in c_bit[output]], args.max_row_weight))
        c_heavy.append(z3.Not(z3.PbLe([(value, 1) for value in c_bit[output]], 4)))

    b_bit = [[None] * N for _ in range(N)]
    b_heavy = []
    for output in range(N):
        for encoded in range(N):
            parent_value = z3.Or(
                *(z3.And(edge[output][p], c_bit[p][encoded]) for p in range(N) if p != output)
            )
            b_bit[output][encoded] = z3.Xor(c_bit[output][encoded], parent_value)
        solver.add(z3.PbLe([(value, 1) for value in b_bit[output]], args.max_row_weight))
        b_heavy.append(z3.Not(z3.PbLe([(value, 1) for value in b_bit[output]], 4)))

    solver.add(z3.PbLe([(value, 1) for value in (*c_heavy, *b_heavy)], args.max_heavy))
    solver.add(z3.Sum([z3.If(value, 0, 1) for value in root]) <= args.max_init_xor)
    if args.radius is not None:
        same = [root[node] if p < 0 else edge[node][p] for node, p in enumerate(hint_parent)]
        solver.add(z3.Sum([z3.If(value, 0, 1) for value in same]) <= args.radius)

    status = solver.check()
    result: dict[str, object] = {
        "scope": "all rooted forests; hint is phase-only",
        "status": str(status),
        "hint_json": str(args.hint_json),
        "max_row_weight": args.max_row_weight,
        "max_heavy": args.max_heavy,
        "max_init_xor": args.max_init_xor,
        "timeout_ms": args.timeout_ms,
        "max_memory_mb": args.max_memory_mb,
        "random_seed": args.random_seed,
        "radius": args.radius,
        "reason_unknown": solver.reason_unknown() if status == z3.unknown else None,
        "statistics": str(solver.statistics()),
    }
    if status != z3.sat:
        return result

    model = solver.model()
    parent = tuple(
        -1 if z3.is_true(model.eval(root[node], model_completion=True)) else
        next(p for p in range(N) if p != node and z3.is_true(model.eval(edge[node][p], model_completion=True)))
        for node in range(N)
    )
    T, _inverse, B, C = base.matrices_from_parent(parent)
    base.verify(parent, T, B, C)
    weights = tuple(row.bit_count() for row in (*B, *C))
    xor_count, pairs = base.greedy_depth_two((*B, *C))
    result["candidate"] = {
        "parent": list(parent),
        "T": [f"{row:08x}" for row in T],
        "B": [f"{row:08x}" for row in B],
        "C": [f"{row:08x}" for row in C],
        "selected_pair_gates": [f"{row:08x}" for row in pairs],
        "metrics": {
            "heavy": sum(weight > 4 for weight in weights),
            "linear_excess": sum(max(0, weight - 4) for weight in weights),
            "squared_excess": sum(max(0, weight - 4) ** 2 for weight in weights),
            "maximum": max(weights),
            "total_weight": sum(weights),
            "init_xor": sum(p >= 0 for p in parent),
            "steady_greedy_xor": xor_count,
        },
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hint-json", type=Path, required=True)
    parser.add_argument("--max-row-weight", type=int, default=6)
    parser.add_argument("--max-heavy", type=int, default=5)
    parser.add_argument("--max-init-xor", type=int, default=28)
    parser.add_argument("--timeout-ms", type=int, default=120_000)
    parser.add_argument("--max-memory-mb", type=int, default=480)
    parser.add_argument("--random-seed", type=int, default=0x9901)
    parser.add_argument("--radius", type=int)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = solve(args)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key not in {"statistics", "candidate"}}, indent=2))
    if "candidate" in result:
        print(json.dumps(result["candidate"]["metrics"], indent=2))
    return 0 if result["status"] in {"sat", "unsat"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
