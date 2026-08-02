"""Exact low-memory colored-tree search for the shallow RNG encoding.

This is an offline research tool.  It models a row-weight-at-most-two,
invertible C as a tree whose 32 edges are labelled by the rows of xorshift A.
If vertex v has root-path label set R_v, then

    T[v] = xor(A[label] for label in R_v).

Instead of searching the tree directly, choose one edge of difference A[i]
for each label i between vectors of weight at most four.  The A[i] are a
basis, so these 32 differently labelled edges cannot contain a cycle.  An
endpoint union of at most 33 vertices is therefore exactly one spanning tree.

The B row of state s is the non-root odd boundary of the selected edges whose
labels occur in s.  Invalid boundary assignments are learned lazily; each cut
contains at most one activation literal and four selected-edge literals.

The tool only reads an optional research JSONL hint and writes its certificate
under the explicitly supplied output path.  It has no game/save imports.
"""

from __future__ import annotations

import argparse
from collections import Counter, deque
import ctypes
from itertools import combinations
import json
import os
from pathlib import Path
import random
import threading
import time
from typing import Sequence

from pysat.solvers import Solver


N = 32
MASK = (1 << N) - 1


def xorshift32(value: int) -> int:
    value ^= value >> 13
    value &= MASK
    value ^= (value << 17) & MASK
    value ^= value >> 5
    return value & MASK


def matrix_from_function(function) -> tuple[int, ...]:
    return tuple(
        sum(((function(1 << source) >> output) & 1) << source for source in range(N))
        for output in range(N)
    )


A = matrix_from_function(xorshift32)


def rank(rows: Sequence[int]) -> int:
    pivots: dict[int, int] = {}
    for original in rows:
        row = original
        while row:
            pivot = row.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = row
                break
            row ^= pivots[pivot]
    return len(pivots)


def low_weight_states() -> tuple[int, ...]:
    return tuple(
        sum(1 << bit for bit in support)
        for weight in range(5)
        for support in combinations(range(N), weight)
    )


def support(mask: int) -> tuple[int, ...]:
    result = []
    while mask:
        low = mask & -mask
        result.append(low.bit_length() - 1)
        mask ^= low
    return tuple(result)


def apply_row(row: int, matrix: Sequence[int]) -> int:
    result = 0
    while row:
        low = row & -row
        result ^= matrix[low.bit_length() - 1]
        row ^= low
    return result


def compose(left: Sequence[int], right: Sequence[int]) -> tuple[int, ...]:
    return tuple(apply_row(row, right) for row in left)


def apply_matrix(matrix: Sequence[int], value: int) -> int:
    return sum(
        ((row & value).bit_count() & 1) << output
        for output, row in enumerate(matrix)
    )


def working_set_bytes() -> int:
    if os.name != "nt":
        try:
            import resource

            return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024
        except (ImportError, OSError):
            return 0
    from ctypes import wintypes

    class Counters(ctypes.Structure):
        _fields_ = [
            ("cb", wintypes.DWORD),
            ("PageFaultCount", wintypes.DWORD),
            ("PeakWorkingSetSize", ctypes.c_size_t),
            ("WorkingSetSize", ctypes.c_size_t),
            ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
            ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
            ("PagefileUsage", ctypes.c_size_t),
            ("PeakPagefileUsage", ctypes.c_size_t),
        ]

    counters = Counters()
    counters.cb = ctypes.sizeof(counters)
    query = ctypes.WinDLL("kernel32", use_last_error=True).K32GetProcessMemoryInfo
    query.argtypes = [wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD]
    query.restype = wintypes.BOOL
    handle = ctypes.WinDLL("kernel32", use_last_error=True).GetCurrentProcess()
    if not query(handle, ctypes.byref(counters), counters.cb):
        return 0
    return int(counters.WorkingSetSize)


def load_hint(path: Path | None) -> tuple[tuple[int, int], ...] | None:
    if path is None:
        return None
    text = path.read_text(encoding="utf-8")
    record = None
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        payload = None
    if isinstance(payload, dict):
        if "certificate" in payload and isinstance(payload["certificate"], dict):
            payload = payload["certificate"]
        if "C" in payload:
            record = payload
    else:
        for line in text.splitlines():
            if line.strip():
                candidate = json.loads(line)
                if "C" in candidate:
                    record = candidate
    if record is None:
        raise ValueError(f"no C record in {path}")
    result = []
    for row_hex in record["C"]:
        row = int(row_hex, 16)
        vertices = support(row)
        if len(vertices) == 1:
            result.append((0, vertices[0] + 1))
        elif len(vertices) == 2:
            result.append((vertices[0] + 1, vertices[1] + 1))
        else:
            raise ValueError("hint C is not shallow")
    return tuple(result)


def boundary(
    labels: Sequence[int], selected: Sequence[tuple[int, int]]
) -> tuple[int, ...]:
    odd: set[int] = set()
    for label in labels:
        for endpoint in selected[label]:
            if endpoint in odd:
                odd.remove(endpoint)
            else:
                odd.add(endpoint)
    odd.discard(0)
    return tuple(sorted(odd))


def verify_tree(selected: Sequence[tuple[int, int]]) -> dict[str, object]:
    if len(selected) != N:
        raise AssertionError("expected one edge per label")
    for label, (left, right) in enumerate(selected):
        if left ^ right != A[label]:
            raise AssertionError("edge difference does not match label")
        if left.bit_count() > 4 or right.bit_count() > 4:
            raise AssertionError("heavy endpoint selected")
    vertices = {endpoint for edge in selected for endpoint in edge}
    if 0 not in vertices or len(vertices) != N + 1:
        raise AssertionError("selected endpoint union is not a rooted tree")

    adjacency: dict[int, list[tuple[int, int]]] = {vertex: [] for vertex in vertices}
    for label, (left, right) in enumerate(selected):
        adjacency[left].append((right, label))
        adjacency[right].append((left, label))
    queue = deque([0])
    path_state = {0: 0}
    while queue:
        vertex = queue.popleft()
        for neighbour, label in adjacency[vertex]:
            if neighbour in path_state:
                continue
            path_state[neighbour] = path_state[vertex] ^ A[label]
            queue.append(neighbour)
    if set(path_state) != vertices:
        raise AssertionError("selected endpoint graph is disconnected")
    if any(vertex != state for vertex, state in path_state.items()):
        raise AssertionError("endpoint name disagrees with root-path state")

    ordered = tuple(sorted(vertices - {0}))
    index = {state: position for position, state in enumerate(ordered)}
    C = []
    for left, right in selected:
        row = 0
        if left:
            row ^= 1 << index[left]
        if right:
            row ^= 1 << index[right]
        C.append(row)
    T = ordered
    B = compose(T, C)
    if compose(C, T) != A:
        raise AssertionError("C*T != A")
    if compose(T, C) != B:
        raise AssertionError("T*C != B")
    if max(row.bit_count() for row in C) > 2:
        raise AssertionError("C is not shallow")
    if max(row.bit_count() for row in T) > 4:
        raise AssertionError("T is heavy")
    if max(row.bit_count() for row in B) > 4:
        raise AssertionError("B is heavy")
    if any(t.bit_count() > b.bit_count() for t, b in zip(T, B)):
        raise AssertionError("tick-zero label capacity failed")

    seeds = [0, 1, 2, 0x12345678, MASK]
    seeds.extend(random.Random(0x5A1109).getrandbits(32) for _ in range(64))
    for seed in seeds:
        encoded = apply_matrix(T, seed)
        natural = seed
        for _ in range(65):
            natural = xorshift32(natural)
            if apply_matrix(C, encoded) != natural:
                raise AssertionError("visible replay failed")
            encoded = apply_matrix(B, encoded)

    def histogram(rows: Sequence[int]) -> dict[str, int]:
        return {
            str(weight): count
            for weight, count in sorted(Counter(row.bit_count() for row in rows).items())
        }

    return {
        "vertices": [f"{row:08x}" for row in ordered],
        "edges": [[f"{left:08x}", f"{right:08x}"] for left, right in selected],
        "C": [f"{row:08x}" for row in C],
        "T": [f"{row:08x}" for row in T],
        "B": [f"{row:08x}" for row in B],
        "row_weight_histograms": {
            "C": histogram(C),
            "T": histogram(T),
            "B": histogram(B),
        },
        "verified_seed_count": len(seeds),
        "verified_outputs_per_seed": 65,
    }


def solve(args: argparse.Namespace) -> dict[str, object]:
    started = time.perf_counter()
    if rank(A) != N:
        raise AssertionError("transition rows are not a basis")
    states = low_weight_states()
    state_set = set(states)

    # Each undirected option is represented once by left < right.
    options: list[tuple[tuple[int, int], ...]] = []
    for difference in A:
        options.append(
            tuple(
                (left, left ^ difference)
                for left in states
                if left < (left ^ difference) and (left ^ difference) in state_set
            )
        )

    edge_var: list[tuple[int, ...]] = []
    endpoints: dict[int, tuple[int, int]] = {}
    next_var = 1
    for color_options in options:
        variables = tuple(range(next_var, next_var + len(color_options)))
        next_var += len(color_options)
        edge_var.append(variables)
        endpoints.update(zip(variables, color_options))

    used_states = tuple(sorted({value for pair in endpoints.values() for value in pair}))
    node_var = {state: next_var + index for index, state in enumerate(used_states)}
    next_var += len(used_states)

    stopped = threading.Event()
    stop_reason = [None]
    peak = [working_set_bytes()]
    solver_ref: list[Solver | None] = [None]

    def watchdog() -> None:
        deadline = started + args.timeout_seconds
        limit = args.memory_mb * 1024 * 1024
        while not stopped.wait(0.05):
            current = working_set_bytes()
            peak[0] = max(peak[0], current)
            if current > limit:
                stop_reason[0] = "memory_limit"
            elif time.perf_counter() >= deadline:
                stop_reason[0] = "timeout"
            if stop_reason[0] is not None:
                solver = solver_ref[0]
                if solver is not None:
                    solver.interrupt()
                return

    thread = threading.Thread(target=watchdog, daemon=True)
    thread.start()

    iterations = 0
    learned_cuts = 0
    best_bad = N + 1
    best_summary = None
    selected: tuple[tuple[int, int], ...] | None = None
    status = "unknown"

    try:
        with Solver(name="minicard") as solver:
            solver_ref[0] = solver
            for variables in edge_var:
                solver.add_clause(list(variables))
                solver.add_atmost(list(variables), 1)
            for variable, (left, right) in endpoints.items():
                solver.add_clause([-variable, node_var[left]])
                solver.add_clause([-variable, node_var[right]])
            solver.add_atmost(list(node_var.values()), N + 1)
            root_edges = [
                variable
                for variable, pair in endpoints.items()
                if 0 in pair
            ]
            solver.add_clause(root_edges)

            # Phase hints are optional and affect search order only.  The old
            # tree may contain heavy endpoints, so retain only legal options.
            hint = load_hint(args.hint)
            if hint is not None:
                # Recover hint endpoint states from its rooted, labelled tree.
                adjacency = [[] for _ in range(N + 1)]
                for label, (left, right) in enumerate(hint):
                    adjacency[left].append((right, label))
                    adjacency[right].append((left, label))
                queue = deque([0])
                named = {0: 0}
                while queue:
                    vertex = queue.popleft()
                    for neighbour, label in adjacency[vertex]:
                        if neighbour not in named:
                            named[neighbour] = named[vertex] ^ A[label]
                            queue.append(neighbour)
                selected_phases = []
                for label, (left, right) in enumerate(hint):
                    pair = tuple(sorted((named[left], named[right])))
                    try:
                        index = options[label].index(pair)
                    except ValueError:
                        continue
                    selected_phases.append(edge_var[label][index])
                selected_set = set(selected_phases)
                hinted_vertices = set(named.values())
                phases = [
                    variable if variable in selected_set else -variable
                    for variables in edge_var
                    for variable in variables
                ]
                phases.extend(
                    variable if state in hinted_vertices else -variable
                    for state, variable in node_var.items()
                )
                solver.set_phases(phases)

            while stop_reason[0] is None:
                iterations += 1
                answer = solver.solve_limited(expect_interrupt=True)
                if answer is None:
                    break
                if not answer:
                    status = "unsat"
                    break
                truth = {literal for literal in solver.get_model() if literal > 0}
                chosen_vars = [
                    next(variable for variable in variables if variable in truth)
                    for variables in edge_var
                ]
                trial = tuple(endpoints[variable] for variable in chosen_vars)
                vertices = {endpoint for edge in trial for endpoint in edge}
                bad = []
                for state in vertices - {0}:
                    labels = support(state)
                    b = boundary(labels, trial)
                    if not state.bit_count() <= len(b) <= 4:
                        bad.append((state, labels, b))
                if len(bad) < best_bad:
                    best_bad = len(bad)
                    best_summary = {
                        "iteration": iterations,
                        "bad_count": len(bad),
                        "endpoint_count": len(vertices),
                        "bad": [
                            {
                                "state": f"{state:08x}",
                                "T_weight": state.bit_count(),
                                "B_weight": len(b),
                                "B_boundary": [f"{value:08x}" for value in b],
                            }
                            for state, _labels, b in sorted(bad)
                        ],
                    }
                    print(json.dumps(best_summary), flush=True)
                if not bad:
                    selected = trial
                    status = "sat"
                    break
                for state, labels, _b in bad:
                    clause = [-node_var[state]]
                    clause.extend(-chosen_vars[label] for label in labels)
                    solver.add_clause(clause)
                    learned_cuts += 1
                if args.max_iterations and iterations >= args.max_iterations:
                    stop_reason[0] = "iteration_limit"
                    break
    finally:
        stopped.set()
        thread.join(timeout=1.0)
        peak[0] = max(peak[0], working_set_bytes())

    report: dict[str, object] = {
        "schema": 1,
        "status": status if stop_reason[0] is None else "unknown",
        "reason_unknown": stop_reason[0],
        "scope": "exact colored tree, T/B<=4, tick-zero capacity; lazy B cuts",
        "transition_rank": rank(A),
        "low_weight_state_count": len(states),
        "used_state_count": len(used_states),
        "edge_option_counts": [len(value) for value in options],
        "edge_variable_count": sum(map(len, edge_var)),
        "node_variable_count": len(node_var),
        "variable_count": next_var - 1,
        "iterations": iterations,
        "learned_boundary_cuts": learned_cuts,
        "best_bad_count": best_bad,
        "best_summary": best_summary,
        "timeout_seconds": args.timeout_seconds,
        "memory_limit_mb": args.memory_mb,
        "peak_working_set_mb": peak[0] / 1048576,
        "elapsed_seconds": time.perf_counter() - started,
        "hint": None if args.hint is None else str(args.hint),
    }
    if selected is not None:
        report["certificate"] = verify_tree(selected)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--hint", type=Path)
    parser.add_argument("--timeout-seconds", type=float, default=600.0)
    parser.add_argument("--memory-mb", type=int, default=680)
    parser.add_argument("--max-iterations", type=int, default=0)
    args = parser.parse_args()
    result = solve(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    summary = {key: value for key, value in result.items() if key != "certificate"}
    print(json.dumps(summary, indent=2), flush=True)
    return 0 if result["status"] in {"sat", "unsat"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
