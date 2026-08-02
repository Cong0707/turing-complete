"""Independent audit for the shallow-output colored-tree research results."""

from __future__ import annotations

import argparse
from collections import Counter, deque
import hashlib
import json
from math import comb, factorial
from pathlib import Path
import random
from typing import Sequence


N = 32
GROUND = N
MASK = (1 << N) - 1
HERE = Path(__file__).resolve().parent


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


def support(mask: int) -> tuple[int, ...]:
    result = []
    while mask:
        low = mask & -mask
        result.append(low.bit_length() - 1)
        mask ^= low
    return tuple(result)


def edge_from_row(row: int) -> tuple[int, int]:
    vertices = support(row)
    if len(vertices) == 1:
        return vertices[0], GROUND
    if len(vertices) == 2:
        return vertices
    raise AssertionError("C is not a shallow tree row")


def load_last_jsonl(path: Path) -> dict[str, object]:
    result = None
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            if line.strip():
                candidate = json.loads(line)
                if all(key in candidate for key in ("C", "T", "B")):
                    result = candidate
    if result is None:
        raise AssertionError("no complete center record")
    return result


def rows(payload: dict[str, object], key: str) -> tuple[int, ...]:
    result = tuple(int(value, 16) for value in payload[key])
    if len(result) != N:
        raise AssertionError(f"{key} does not have 32 rows")
    return result


def root_paths(C: Sequence[int]) -> dict[int, tuple[int, ...]]:
    adjacency = [[] for _ in range(N + 1)]
    for label, row in enumerate(C):
        left, right = edge_from_row(row)
        adjacency[left].append((right, label))
        adjacency[right].append((left, label))
    queue = deque([GROUND])
    paths = {GROUND: ()}
    while queue:
        vertex = queue.popleft()
        for neighbour, label in adjacency[vertex]:
            if neighbour not in paths:
                paths[neighbour] = paths[vertex] + (label,)
                queue.append(neighbour)
    if len(paths) != N + 1:
        raise AssertionError("center C is disconnected")
    return paths


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--center", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    center_payload = load_last_jsonl(args.center)
    C0 = rows(center_payload, "C")
    T0 = rows(center_payload, "T")
    B0 = rows(center_payload, "B")
    assert compose(C0, T0) == A
    assert compose(T0, C0) == B0
    assert max(row.bit_count() for row in C0) <= 2
    heavy = tuple(index for index, row in enumerate(T0) if row.bit_count() > 4)
    assert heavy == (11, 14)
    paths = root_paths(C0)
    assert set(paths[11]) == {12, 29}
    assert paths[14] == (16,)

    radius4_py = json.loads((HERE / "radius4-exact.json").read_text(encoding="ascii"))
    radius4_cpp = json.loads((HERE / "radius4-cpp-current.json").read_text(encoding="ascii"))
    radius5_cpp = json.loads((HERE / "radius5-exact.json").read_text(encoding="ascii"))
    t_only = json.loads((HERE / "radius4-tonly-sat.json").read_text(encoding="ascii"))
    global_hinted = json.loads(
        (HERE / "global-hinted-300s.json").read_text(encoding="ascii")
    )

    eligible4 = comb(31, 3) - comb(29, 3)
    eligible5 = comb(31, 4) - comb(29, 4)
    shapes4 = 5 ** 3
    shapes5 = 6 ** 4
    assignments4 = eligible4 * shapes4 * factorial(4)
    assignments5 = eligible5 * shapes5 * factorial(5)
    assert (eligible4, eligible5) == (841, 7714)
    assert assignments4 == 2_523_000
    assert assignments5 == 1_199_681_280

    assert radius4_py["status"] == "unsat"
    assert radius4_cpp["status"] == "unsat"
    assert radius4_py["eligible_removed_set_count"] == eligible4
    assert radius4_cpp["eligible_removed_set_count"] == eligible4
    assert radius4_py["shape_assignments"] == assignments4
    assert radius4_cpp["shape_label_assignments"] == assignments4
    assert radius4_py["offset_endpoint_branches"] == 5_292_094
    assert radius4_cpp["endpoint_offset_branches"] == 5_292_094
    assert radius4_py["complete_trees_checked"] == 0
    assert radius4_cpp["valid_leaves"] == 0

    assert radius5_cpp["status"] == "unsat"
    assert radius5_cpp["eligible_removed_set_count"] == eligible5
    assert radius5_cpp["component_tree_shape_count"] == shapes5
    assert radius5_cpp["shape_label_assignments"] == assignments5
    assert radius5_cpp["endpoint_offset_branches"] == 2_603_986_081
    assert radius5_cpp["valid_leaves"] == 0
    assert radius5_cpp["peak_working_set_mb"] < 700

    assert global_hinted["status"] == "unknown"
    assert global_hinted["reason_unknown"] == "timeout"
    assert global_hinted["iterations"] == 2
    assert global_hinted["learned_boundary_cuts"] == 5
    assert global_hinted["best_bad_count"] == 5
    assert global_hinted["peak_working_set_mb"] < 700

    certificate = t_only["certificate"]
    Ct = rows(certificate, "C")
    Tt = rows(certificate, "T")
    Bt = rows(certificate, "B")
    assert compose(Ct, Tt) == A
    assert compose(Tt, Ct) == Bt
    assert max(row.bit_count() for row in Ct) <= 2
    assert max(row.bit_count() for row in Tt) <= 4
    assert sum(left != right for left, right in zip(C0, Ct)) == 4
    bad = tuple(
        (index, Tt[index].bit_count(), Bt[index].bit_count())
        for index in range(N)
        if Bt[index].bit_count() > 4 or Tt[index].bit_count() > Bt[index].bit_count()
    )
    assert bad == ((9, 4, 6), (11, 4, 8), (14, 4, 6), (23, 4, 5), (31, 4, 6))

    seeds = [0, 1, 2, 0x12345678, MASK]
    seeds.extend(random.Random(0x5A1109).getrandbits(32) for _ in range(64))
    for seed in seeds:
        encoded = apply_matrix(Tt, seed)
        natural = seed
        for _ in range(65):
            natural = xorshift32(natural)
            assert apply_matrix(Ct, encoded) == natural
            encoded = apply_matrix(Bt, encoded)

    artifacts = (
        "search_radius.cpp",
        "search_radius4.py",
        "solve_colored_tree.py",
        "radius4-exact.json",
        "radius4-cpp-current.json",
        "radius5-exact.json",
        "radius4-tonly-sat.json",
        "global-hinted-300s.json",
    )
    report = {
        "schema": 1,
        "global_status": "OPEN",
        "neighborhood_status": "UNSAT through C-row Hamming radius 5",
        "center_heavy_T_rows": list(heavy),
        "forced_removed_labels": [16, "12_or_29"],
        "coverage": {
            "radius4": {
                "eligible_removed_sets": eligible4,
                "component_tree_shapes": shapes4,
                "label_permutations": factorial(4),
                "shape_label_assignments": assignments4,
                "endpoint_offset_branches": 5_292_094,
            },
            "radius5": {
                "eligible_removed_sets": eligible5,
                "component_tree_shapes": shapes5,
                "label_permutations": factorial(5),
                "shape_label_assignments": assignments5,
                "endpoint_offset_branches": 2_603_986_081,
            },
        },
        "independent_radius4_implementations_agree": True,
        "t_only_control": {
            "status": "SAT",
            "C_row_distance": 4,
            "maximum_T_weight": 4,
            "bad_B_rows": [list(item) for item in bad],
            "verified_seed_count": len(seeds),
            "verified_outputs_per_seed": 65,
        },
        "global_colored_tree_search": {
            "status": "OPEN",
            "iterations": global_hinted["iterations"],
            "learned_boundary_cuts": global_hinted["learned_boundary_cuts"],
            "best_bad_count": global_hinted["best_bad_count"],
            "elapsed_seconds": global_hinted["elapsed_seconds"],
            "peak_working_set_mb": global_hinted["peak_working_set_mb"],
        },
        "peak_working_set_mb": radius5_cpp["peak_working_set_mb"],
        "sha256": {name: sha256(HERE / name) for name in artifacts},
    }
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="ascii")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
