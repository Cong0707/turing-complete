"""Audit the two sparse Galois companion basis families for RNG.

The script is save-independent and never starts the game.  It studies the
66-cycle persistent-seed equations

    q' = B q + D seed
    y  = C q + seed

over GF(2).  A cyclic basis K(v)=[v, A v, ..., A^31 v] gives T=K^-1,
B=T A T^-1 and C=K.  The reverse family uses A^-1 instead.  Both make every
row of B have weight at most two.  We exhaust every member that could pass
the ordinary-XOR2 output timing condition by enumerating the first row of C,
whose map from v is bijective.

This is deliberately *not* a proof against nonlinear Switch/Z networks.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path


N = 32
MASK = (1 << N) - 1
OUT = Path(__file__).with_name("galois_companion_family.json")


def xorshift32(value: int) -> int:
    value &= MASK
    value ^= value >> 13
    value &= MASK
    value ^= (value << 17) & MASK
    value &= MASK
    value ^= value >> 5
    return value & MASK


def columns_to_rows(columns: list[int] | tuple[int, ...]) -> list[int]:
    return [
        sum(((columns[column] >> row) & 1) << column for column in range(N))
        for row in range(N)
    ]


def apply_matrix(rows: list[int] | tuple[int, ...], value: int) -> int:
    return sum(((row & value).bit_count() & 1) << bit for bit, row in enumerate(rows))


def multiply(left: list[int], right: list[int]) -> list[int]:
    result: list[int] = []
    for row in left:
        output = 0
        while row:
            low = row & -row
            output ^= right[low.bit_length() - 1]
            row ^= low
        result.append(output)
    return result


def invert(rows: list[int]) -> list[int]:
    augmented = [rows[row] | 1 << (N + row) for row in range(N)]
    for column in range(N):
        pivot = next(
            (row for row in range(column, N) if augmented[row] >> column & 1),
            None,
        )
        if pivot is None:
            raise ValueError("singular GF(2) matrix")
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        for row in range(N):
            if row != column and augmented[row] >> column & 1:
                augmented[row] ^= augmented[column]
    if [row & MASK for row in augmented] != [1 << row for row in range(N)]:
        raise AssertionError("GF(2) inverse reduction failed")
    return [row >> N for row in augmented]


def identity() -> list[int]:
    return [1 << row for row in range(N)]


A_COLUMNS = [xorshift32(1 << column) for column in range(N)]
A = columns_to_rows(A_COLUMNS)
A_INV = invert(A)
A_PLUS_I = [A[row] ^ (1 << row) for row in range(N)]


def krylov_rows(vector: int, step: list[int]) -> list[int]:
    columns: list[int] = []
    value = vector
    for _ in range(N):
        columns.append(value)
        value = apply_matrix(step, value)
    return columns_to_rows(columns)


def first_row_map(step: list[int]) -> list[int]:
    """Return rows of the linear map v -> row_0(K(v))."""

    columns = [krylov_rows(1 << bit, step)[0] for bit in range(N)]
    return columns_to_rows(columns)


def low_weight_words(maximum: int):
    yield 0
    for weight in range(1, maximum + 1):
        for bits in combinations(range(N), weight):
            yield sum(1 << bit for bit in bits)


@dataclass(frozen=True, order=True)
class CandidateScore:
    violating_rows: int
    maximum_weight: int
    excess: int
    total_weight: int
    vector: int
    first_row: int


def score_c(rows: list[int], vector: int, first_row: int) -> CandidateScore:
    weights = [row.bit_count() for row in rows]
    return CandidateScore(
        violating_rows=sum(weight > 3 for weight in weights),
        maximum_weight=max(weights),
        excess=sum(max(0, weight - 3) for weight in weights),
        total_weight=sum(weights),
        vector=vector,
        first_row=first_row,
    )


def hex_rows(rows: list[int]) -> list[str]:
    return [f"{row:08x}" for row in rows]


def audit_direction(name: str, step: list[int]) -> dict[str, object]:
    map_rows = first_row_map(step)
    map_inverse = invert(map_rows)
    if multiply(map_rows, map_inverse) != identity():
        raise AssertionError("first-row observability map is not invertible")

    best: CandidateScore | None = None
    satisfying: list[int] = []
    enumerated = 0
    for first_row in low_weight_words(3):
        vector = apply_matrix(map_inverse, first_row)
        if vector == 0:
            continue
        enumerated += 1
        C = krylov_rows(vector, step)
        if C[0] != first_row:
            raise AssertionError("first-row inversion produced the wrong vector")
        candidate = score_c(C, vector, first_row)
        if best is None or candidate < best:
            best = candidate
        if candidate.violating_rows == 0:
            satisfying.append(vector)

    if best is None:
        raise AssertionError("empty companion-family enumeration")

    vector = best.vector
    C = krylov_rows(vector, step)
    T = invert(C)
    B = multiply(multiply(T, A), C)
    D = multiply(T, A_PLUS_I)
    if multiply(T, C) != identity() or multiply(C, T) != identity():
        raise AssertionError("T and C are not mutual inverses")
    if multiply(B, T) != multiply(T, A):
        raise AssertionError("B*T != T*A")
    if D != multiply(T, A_PLUS_I):
        raise AssertionError("incorrect persistent-seed injection matrix")
    if max(row.bit_count() for row in B) > 2:
        raise AssertionError("expected a row-sparse Galois transition")

    c_weights = [row.bit_count() for row in C]
    feedback_metrics = [
        4 * B[row].bit_count() + D[row].bit_count() for row in range(N)
    ]
    return {
        "direction": name,
        "step": "A" if name == "forward" else "A^-1",
        "first_row_map_rank": N,
        "enumeration": {
            "first_row_weight_limit": 3,
            "candidate_count": enumerated,
            "expected_count": sum(
                1 for word in low_weight_words(3) if word != 0
            ),
            "satisfying_count": len(satisfying),
            "status": "UNSAT" if not satisfying else "SAT",
        },
        "closest": {
            "vector": f"{vector:08x}",
            "first_row": f"{best.first_row:08x}",
            "violating_output_rows": best.violating_rows,
            "maximum_C_row_weight": best.maximum_weight,
            "C_weight_excess_over_3": best.excess,
            "C_total_weight": best.total_weight,
            "C_weight_histogram": {
                str(weight): c_weights.count(weight) for weight in sorted(set(c_weights))
            },
            "B_total_weight": sum(row.bit_count() for row in B),
            "B_maximum_row_weight": max(row.bit_count() for row in B),
            "D_total_weight": sum(row.bit_count() for row in D),
            "feedback_kraft_violating_rows": sum(metric > 16 for metric in feedback_metrics),
            "feedback_kraft_maximum": max(feedback_metrics),
            "C": hex_rows(C),
            "T": hex_rows(T),
            "B": hex_rows(B),
            "D": hex_rows(D),
        },
    }


def main() -> None:
    directions = [
        audit_direction("forward", A),
        audit_direction("reverse", A_INV),
    ]
    result = {
        "schema": 1,
        "model": "66-cycle persistent seed: q'=Bq xor Dseed; y=Cq xor seed",
        "basis_families": [
            "K(v)=[v,Av,...,A^31v]",
            "K-(v)=[v,A^-1v,...,A^-31v]",
        ],
        "ordinary_xor2_timing": {
            "state_arrival": 4,
            "seed_arrival": 0,
            "xor_gate": 3,
            "xor_delay": 2,
            "output_necessary_condition": "4*wt(C_i)+1 <= 16, hence wt(C_i)<=3",
            "feedback_necessary_condition": "4*wt(B_i)+wt(D_i) <= 16",
        },
        "proof": [
            "the xorshift characteristic polynomial is irreducible of degree 32, so every nonzero v is cyclic",
            "for either direction, v -> row0(K(v)) is an invertible 32-bit linear map",
            "therefore every family member that could satisfy wt(C_0)<=3 is covered by enumerating all nonzero words of weight <=3",
            "each enumerated vector is then checked against all 32 output rows",
        ],
        "directions": directions,
        "status": (
            "UNSAT for both row-sparse Galois families in the ordinary-XOR2 delay-8 model"
            if all(direction["enumeration"]["satisfying_count"] == 0 for direction in directions)
            else "SAT member found"
        ),
        "scope_exclusion": (
            "This does not exclude nonlinear Bit-Switch/Z consensus covers, a different sparse similarity form, "
            "redundant state, or a non-companion noncommuting basis."
        ),
        "game_started": False,
        "live_save_read_or_written": False,
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "directions": [
            {
                "direction": item["direction"],
                "candidate_count": item["enumeration"]["candidate_count"],
                "satisfying_count": item["enumeration"]["satisfying_count"],
                "closest_violations": item["closest"]["violating_output_rows"],
                "closest_max_weight": item["closest"]["maximum_C_row_weight"],
            }
            for item in directions
        ],
        "output_sha256": sha256(OUT.read_bytes()).hexdigest(),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
