"""Certify a structured noncommuting frontier for persistent-seed RNG 66/8.

This is a necessary-timing frontier, not a physical circuit.  It never reads
or writes the live save and never starts the game.
"""

from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import random


N = 32
MASK = (1 << N) - 1
OUT = Path(__file__).with_name("structured_shear_66_frontier.json")

SHEARS = (("L", 22), ("R", 27), ("L", 27), ("R", 27), ("R", 17))
TRANSVECTIONS = (
    (14, 19),
    (13, 18),
    (30, 8),
    (20, 25),
    (16, 1),
    (31, 9),
    (21, 26),
    (12, 3),
)


def xorshift32(value: int) -> int:
    value &= MASK
    value ^= value >> 13
    value &= MASK
    value ^= (value << 17) & MASK
    value &= MASK
    value ^= value >> 5
    return value & MASK


def identity() -> list[int]:
    return [1 << row for row in range(N)]


def columns_to_rows(columns: list[int]) -> list[int]:
    return [
        sum(((columns[column] >> row) & 1) << column for column in range(N))
        for row in range(N)
    ]


def apply_matrix(rows: list[int], value: int) -> int:
    return sum(((row & value).bit_count() & 1) << bit for bit, row in enumerate(rows))


def apply_row(row: int, matrix: list[int]) -> int:
    result = 0
    while row:
        low = row & -row
        result ^= matrix[low.bit_length() - 1]
        row ^= low
    return result


def multiply(left: list[int], right: list[int]) -> list[int]:
    return [apply_row(row, right) for row in left]


def invert(rows: list[int]) -> list[int]:
    work = list(rows)
    result = identity()
    for column in range(N):
        pivot = next(
            (row for row in range(column, N) if work[row] >> column & 1),
            None,
        )
        if pivot is None:
            raise ValueError("singular GF(2) matrix")
        work[column], work[pivot] = work[pivot], work[column]
        result[column], result[pivot] = result[pivot], result[column]
        for row in range(N):
            if row != column and work[row] >> column & 1:
                work[row] ^= work[column]
                result[row] ^= result[column]
    if work != identity():
        raise AssertionError("GF(2) inverse reduction failed")
    return result


def shear(direction: str, distance: int) -> list[int]:
    result = identity()
    if direction == "L":
        for row in range(distance, N):
            result[row] ^= 1 << (row - distance)
    elif direction == "R":
        for row in range(N - distance):
            result[row] ^= 1 << (row + distance)
    else:
        raise ValueError(f"unknown shear direction {direction!r}")
    return result


def transvection(destination: int, source: int) -> list[int]:
    if destination == source:
        raise ValueError("transvection needs distinct coordinates")
    result = identity()
    result[destination] ^= 1 << source
    return result


A = columns_to_rows([xorshift32(1 << bit) for bit in range(N)])
A_PLUS_I = [A[row] ^ (1 << row) for row in range(N)]


def derive(C: list[int]) -> tuple[list[int], list[int], list[int]]:
    encoding = invert(C)
    B = multiply(multiply(encoding, A), C)
    D = multiply(encoding, A_PLUS_I)
    return encoding, B, D


def score(C: list[int]) -> dict[str, object]:
    _encoding, B, D = derive(C)
    metrics = [4 * B[row].bit_count() + D[row].bit_count() for row in range(N)]
    return {
        "over": sum(metric > 16 for metric in metrics),
        "excess": sum(max(0, metric - 16) for metric in metrics),
        "maximum": max(metrics),
        "B_plus_D_weight": sum(row.bit_count() for row in B + D),
        "C_weight": sum(row.bit_count() for row in C),
        "C_maximum_row_weight": max(row.bit_count() for row in C),
    }


def build_frontier() -> tuple[list[int], list[dict[str, object]]]:
    C = identity()
    history: list[dict[str, object]] = [{"step": "identity", "score": score(C)}]
    for direction, distance in SHEARS:
        C = multiply(shear(direction, distance), C)
        history.append({
            "step": f"left shear {direction}{distance}",
            "score": score(C),
        })
    for destination, source in TRANSVECTIONS:
        C = multiply(C, transvection(destination, source))
        history.append({
            "step": f"right transvection E({destination},{source})",
            "score": score(C),
        })
    return C, history


def replay(C: list[int], encoding: list[int], B: list[int], D: list[int]) -> dict[str, object]:
    seeds = list(range(1, 258))
    seeds += [1 << bit for bit in range(N)]
    rng = random.Random(0x6608_C0DE)
    seeds += [rng.randrange(1, 1 << N) for _ in range(64)]
    seeds = list(dict.fromkeys(seed & MASK for seed in seeds if seed & MASK))

    checked = 0
    for seed in seeds:
        q = 0
        natural = seed
        for _tick in range(1, 66):
            q = apply_matrix(B, q) ^ apply_matrix(D, seed)
            natural = xorshift32(natural)
            output = apply_matrix(C, q) ^ seed
            if output != natural:
                raise AssertionError(
                    f"protocol mismatch seed={seed:08x} tick={_tick}: "
                    f"{output:08x}!={natural:08x}"
                )
            invariant = apply_matrix(encoding, natural ^ seed)
            if q != invariant:
                raise AssertionError("encoded-state invariant failed")
            checked += 1
    return {
        "seed_count": len(seeds),
        "outputs_per_seed": 65,
        "checked_outputs": checked,
        "all_nonzero_game_seed_domain_sampled": True,
        "passed": True,
    }


def hex_rows(rows: list[int]) -> list[str]:
    return [f"{row:08x}" for row in rows]


def main() -> None:
    C, history = build_frontier()
    encoding, B, D = derive(C)
    I = identity()
    if multiply(C, encoding) != I or multiply(encoding, C) != I:
        raise AssertionError("C and encoding are not mutual inverses")
    if multiply(B, encoding) != multiply(encoding, A):
        raise AssertionError("B*encoding != encoding*A")
    if D != multiply(encoding, A_PLUS_I):
        raise AssertionError("D != encoding*(A+I)")
    if max(row.bit_count() for row in C) > 3:
        raise AssertionError("output matrix C violates the delay-8 necessary bound")

    metrics = [4 * B[row].bit_count() + D[row].bit_count() for row in range(N)]
    violations = [
        {
            "row": row,
            "B": f"{B[row]:08x}",
            "D": f"{D[row]:08x}",
            "B_weight": B[row].bit_count(),
            "D_weight": D[row].bit_count(),
            "metric": metrics[row],
            "excess": metrics[row] - 16,
        }
        for row in range(N)
        if metrics[row] > 16
    ]
    final_score = score(C)
    if final_score != {
        "over": 8,
        "excess": 38,
        "maximum": 30,
        "B_plus_D_weight": 193,
        "C_weight": 68,
        "C_maximum_row_weight": 3,
    }:
        raise AssertionError(f"structured frontier score changed: {final_score}")

    result = {
        "schema": 1,
        "status": "verified mixed-Kraft frontier; not a physical DAG candidate",
        "model": "66-cycle persistent seed: q'=Bq xor Dseed; y=Cq xor seed",
        "construction": {
            "C_start": "I",
            "left_shears": [f"{direction}{distance}" for direction, distance in SHEARS],
            "right_transvections_destination_source": [list(move) for move in TRANSVECTIONS],
            "multiplication_order": (
                "shears use C<-S*C in listed order; transvections use C<-C*E(dst,src) "
                "in listed order; E has row dst=e_dst xor e_src"
            ),
        },
        "score_history": history,
        "final_score": final_score,
        "metric_histogram": dict(sorted(Counter(metrics).items())),
        "violating_rows": violations,
        "matrices": {
            "C_output": hex_rows(C),
            "encoding_T0": hex_rows(encoding),
            "B_feedback_state": hex_rows(B),
            "D_seed_injection": hex_rows(D),
            "alternate_solver_parameter_T_equals_D": hex_rows(D),
        },
        "identities": [
            "C*T0=I",
            "T0*C=I",
            "B*T0=T0*A",
            "D=T0*(A+I)",
        ],
        "timing": {
            "state_arrival": 4,
            "seed_arrival": 0,
            "xor_delay": 2,
            "feedback_ordinary_xor2_necessary": "4*wt(B_i)+wt(D_i)<=16",
            "output_ordinary_xor2_necessary": "4*wt(C_i)+1<=16",
            "output_rows_satisfying": 32,
            "feedback_rows_satisfying": 24,
            "feedback_rows_needing_switch_or_recode": 8,
        },
        "protocol_replay": replay(C, encoding, B, D),
        "score_budget": {
            "normal_frontier": [401, 9, 67],
            "normal_frontier_energy": 401 * 9 * 67,
            "target": [457, 8, 66],
            "state_and_ready_gate": 32 * 5 + 5,
            "maximum_logic_gate_for_strict_improvement": 292,
            "warning": "matrix support score is not a physical logic gate count",
        },
        "scope_limit": (
            "Eight feedback rows still violate ordinary-XOR2 timing.  A real candidate requires "
            "a conflict-free undirected Switch/Z or new recoding repair plus a <=292-gate shared DAG."
        ),
        "game_started": False,
        "live_save_read_or_written": False,
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "final_score": final_score,
        "violating_rows": [item["row"] for item in violations],
        "protocol_replay": result["protocol_replay"],
        "output_sha256": sha256(OUT.read_bytes()).hexdigest(),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
