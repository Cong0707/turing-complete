#!/usr/bin/env python3
"""Exact low-memory invariants for the arbitrary-T 65-cycle Kraft model.

This script is deliberately independent of the save writer and the game.  It
reconstructs the 32-bit xorshift matrix, proves the small-distance graph facts
used by the support-forest argument, and emits a machine-readable certificate.

All matrices are over GF(2), represented by little-endian row bitmasks.
"""

from __future__ import annotations

from hashlib import sha256
import itertools
import json
from pathlib import Path
from typing import Iterable, Sequence


BITS = 32
MASK = (1 << BITS) - 1
IDENTITY = tuple(1 << bit for bit in range(BITS))
DEFAULT_OUTPUT = Path(__file__).with_suffix(".json")


def xorshift32(value: int) -> int:
    value ^= value >> 13
    value &= MASK
    value ^= (value << 17) & MASK
    value &= MASK
    value ^= value >> 5
    return value & MASK


def matrix_from_function() -> tuple[int, ...]:
    columns = tuple(xorshift32(1 << bit) for bit in range(BITS))
    return tuple(
        sum(((columns[source] >> target) & 1) << source for source in range(BITS))
        for target in range(BITS)
    )


def apply_row(row: int, matrix: Sequence[int]) -> int:
    result = 0
    while row:
        low = row & -row
        result ^= matrix[low.bit_length() - 1]
        row ^= low
    return result


def compose(left: Sequence[int], right: Sequence[int]) -> tuple[int, ...]:
    return tuple(apply_row(row, right) for row in left)


def rank(matrix: Sequence[int]) -> int:
    rows = list(matrix)
    pivot = 0
    for column in range(BITS):
        selected = next(
            (index for index in range(pivot, len(rows)) if rows[index] >> column & 1),
            None,
        )
        if selected is None:
            continue
        rows[pivot], rows[selected] = rows[selected], rows[pivot]
        for index in range(len(rows)):
            if index != pivot and rows[index] >> column & 1:
                rows[index] ^= rows[pivot]
        pivot += 1
    return pivot


def matrix_digest(matrix: Sequence[int]) -> str:
    return sha256(b"".join(row.to_bytes(4, "little") for row in matrix)).hexdigest()


def maximum_clique(vertices: Sequence[int], edges: set[tuple[int, int]]) -> tuple[int, ...]:
    best: tuple[int, ...] = ()
    for mask in range(1 << len(vertices)):
        if mask.bit_count() <= len(best):
            continue
        candidate = tuple(vertices[index] for index in range(len(vertices)) if mask >> index & 1)
        if all(tuple(sorted(pair)) in edges for pair in itertools.combinations(candidate, 2)):
            best = candidate
    return best


def maximum_matching(edges: Sequence[tuple[int, int]]) -> tuple[tuple[int, int], ...]:
    best: tuple[tuple[int, int], ...] = ()
    for mask in range(1 << len(edges)):
        if mask.bit_count() <= len(best):
            continue
        selected = tuple(edge for index, edge in enumerate(edges) if mask >> index & 1)
        endpoints = tuple(vertex for edge in selected for vertex in edge)
        if len(set(endpoints)) == len(endpoints):
            best = selected
    return best


def polynomial_mod(value: int, modulus: int) -> int:
    modulus_degree = modulus.bit_length() - 1
    while value and value.bit_length() - 1 >= modulus_degree:
        value ^= modulus << (value.bit_length() - 1 - modulus_degree)
    return value


def polynomial_gcd(left: int, right: int) -> int:
    while right:
        left, right = right, polynomial_mod(left, right)
    return left


def field_multiply(left: int, right: int, modulus: int) -> int:
    result = 0
    while right:
        if right & 1:
            result ^= left
        right >>= 1
        left <<= 1
        if left >> BITS:
            left ^= modulus
    return result


def field_power(value: int, exponent: int, modulus: int) -> int:
    result = 1
    while exponent:
        if exponent & 1:
            result = field_multiply(result, value, modulus)
        value = field_multiply(value, value, modulus)
        exponent >>= 1
    return result


def solve_column_basis(columns: Sequence[int], target: int) -> int:
    rows = [
        sum(((columns[column] >> row) & 1) << column for column in range(BITS))
        | (((target >> row) & 1) << BITS)
        for row in range(BITS)
    ]
    for column in range(BITS):
        selected = next(index for index in range(column, BITS) if rows[index] >> column & 1)
        rows[column], rows[selected] = rows[selected], rows[column]
        for index in range(BITS):
            if index != column and rows[index] >> column & 1:
                rows[index] ^= rows[column]
    return sum(((rows[index] >> BITS) & 1) << index for index in range(BITS))


def characteristic_polynomial(matrix: Sequence[int]) -> tuple[int, int]:
    # e_0 is cyclic.  Its 32 Krylov columns therefore form a basis, and the
    # unique degree-32 annihilating relation is both minpoly and charpoly.
    krylov = []
    value = 1
    for _ in range(BITS + 1):
        krylov.append(value)
        value = sum(((row & value).bit_count() & 1) << bit for bit, row in enumerate(matrix))
    if rank(tuple(krylov[:BITS])) != BITS:
        raise AssertionError("e_0 is not cyclic")
    coefficients = solve_column_basis(krylov[:BITS], krylov[BITS])
    polynomial = (1 << BITS) | coefficients

    # Verify p(A)=0 on every standard basis vector, not only on e_0.
    for source in range(BITS):
        powers = []
        value = 1 << source
        for _ in range(BITS + 1):
            powers.append(value)
            value = sum(
                ((row & value).bit_count() & 1) << bit
                for bit, row in enumerate(matrix)
            )
        result = powers[BITS]
        for exponent in range(BITS):
            if coefficients >> exponent & 1:
                result ^= powers[exponent]
        if result:
            raise AssertionError("characteristic polynomial does not annihilate A")
    return polynomial, coefficients


def threshold_certificate(
    k_rows: Sequence[int], cap2_indices: Sequence[int], low_weight_limit: int
) -> dict[str, object]:
    target_indices = tuple(
        index for index in cap2_indices if k_rows[index].bit_count() > 2 * low_weight_limit
    )
    threshold = 2 * low_weight_limit
    compatible = tuple(
        (left, right)
        for left, right in itertools.combinations(target_indices, 2)
        if (k_rows[left] ^ k_rows[right]).bit_count() <= threshold
    )
    edge_set = {tuple(sorted(edge)) for edge in compatible}
    clique = maximum_clique(target_indices, edge_set)
    matching = maximum_matching(compatible)
    if len(clique) > 2:
        raise AssertionError("the simple forest bound expects compatibility clique <= 2")

    edge_count = len(target_indices)
    matching_number = len(matching)
    high_lower_bound = next(
        high_count
        for high_count in range(BITS + 1)
        if edge_count
        <= (high_count - 1)
        + high_count
        + min(high_count, matching_number)
    )
    return {
        "low_D_weight_limit": low_weight_limit,
        "high_D_weight_at_least": low_weight_limit + 1,
        "target_indices": list(target_indices),
        "target_weights": [k_rows[index].bit_count() for index in target_indices],
        "target_count": edge_count,
        "compatibility_distance_limit": threshold,
        "compatibility_edges": [
            [left, right, (k_rows[left] ^ k_rows[right]).bit_count()]
            for left, right in compatible
        ],
        "maximum_clique": list(clique),
        "maximum_clique_size": len(clique),
        "maximum_matching": [list(edge) for edge in matching],
        "maximum_matching_size": matching_number,
        "forest_edge_upper_bound_formula": "(h-1)+h+min(h,matching_number)",
        "high_D_row_count_lower_bound": high_lower_bound,
    }


def singleton_orbit_certificate(
    start: int, matrix: Sequence[int], *, maximum_d_weight: int = 12
) -> dict[str, object]:
    """Propagate a singleton C row through forced unit rows of B.

    If C_i=e_j, then D_j=K_i.  Whenever wt(D_j)>=9, the feedback
    Kraft inequality and invertibility of B force row B_j to be a unit row,
    hence D_j*A must be another row of D.  Every D row has weight at most 12.
    Reaching weight <=8 ends this particular obstruction; exceeding 12 proves
    that the starting singleton is impossible.
    """

    values: list[int] = []
    value = start
    for _ in range(BITS + 1):
        values.append(value)
        weight = value.bit_count()
        if weight <= 8:
            outcome = "not_obstructed_after_reaching_weight_at_most_8"
            break
        if weight > maximum_d_weight:
            outcome = "impossible_weight_exceeds_12"
            break
        value = apply_row(value, matrix)
    else:  # pragma: no cover - A is primitive and the recorded tracks are short
        raise AssertionError("unexpectedly long singleton orbit")
    return {
        "orbit_rows": [f"0x{item:08x}" for item in values],
        "orbit_weights": [item.bit_count() for item in values],
        "outcome": outcome,
        "singleton_impossible": outcome == "impossible_weight_exceeds_12",
    }


def build_certificate() -> dict[str, object]:
    a = matrix_from_function()
    a_plus_i = tuple(row ^ IDENTITY[index] for index, row in enumerate(a))
    k = compose(a, a_plus_i)
    if rank(a) != BITS or rank(a_plus_i) != BITS or rank(k) != BITS:
        raise AssertionError("A, A+I, and K must be invertible")

    capacities = tuple((16 - row.bit_count()) // 4 for row in a)
    cap2_indices = tuple(index for index, capacity in enumerate(capacities) if capacity == 2)
    if cap2_indices != tuple(range(12, 27)):
        raise AssertionError("unexpected capacity-2 row set")
    if min(k[index].bit_count() for index in cap2_indices) != 9:
        raise AssertionError("unexpected minimum K weight")

    thresholds = tuple(
        threshold_certificate(k, cap2_indices, low_limit)
        for low_limit in range(1, 6)
    )
    tail_bounds = {
        item["high_D_weight_at_least"]: item["high_D_row_count_lower_bound"]
        for item in thresholds
    }
    d_weight_sum_lower_bound = BITS + sum(
        int(tail_bounds.get(weight, 0)) for weight in range(2, 7)
    )

    singleton_indices = (4, 5, *cap2_indices)
    singleton_orbits = {
        index: singleton_orbit_certificate(k[index], a)
        for index in singleton_indices
    }
    allowed_cap2_singletons = tuple(
        index
        for index in cap2_indices
        if not singleton_orbits[index]["singleton_impossible"]
    )
    if allowed_cap2_singletons != (25,):
        raise AssertionError("unexpected capacity-2 singleton survivor")
    if not all(singleton_orbits[index]["singleton_impossible"] for index in (4, 5)):
        raise AssertionError("rows 4 and 5 should reject singleton support")
    forced_extra_c_entries = (len(cap2_indices) - len(allowed_cap2_singletons)) + 2
    c_total_weight_lower_bound = BITS + forced_extra_c_entries

    polynomial, coefficients = characteristic_polynomial(a)
    x = 0b10
    irreducible_checks = {
        "x^(2^32)_mod_p": field_power(x, 1 << BITS, polynomial),
        "gcd(p,x^(2^16)+x)": polynomial_gcd(
            polynomial, field_power(x, 1 << 16, polynomial) ^ x
        ),
    }
    if irreducible_checks != {"x^(2^32)_mod_p": x, "gcd(p,x^(2^16)+x)": 1}:
        raise AssertionError("Rabin irreducibility checks failed")
    order = (1 << BITS) - 1
    prime_divisors = (3, 5, 17, 257, 65537)
    primitive_residues = {
        divisor: field_power(x, order // divisor, polynomial)
        for divisor in prime_divisors
    }
    if any(residue == 1 for residue in primitive_residues.values()):
        raise AssertionError("primitive-polynomial check failed")

    char_weight = polynomial.bit_count()
    cycle_space_dimension_lower_bound = (char_weight - 1).bit_length()
    b_total_weight_lower_bound = BITS - 1 + cycle_space_dimension_lower_bound

    return {
        "schema": 1,
        "model": "arbitrary invertible T, 65-cycle delay-9 Kraft necessary conditions",
        "equations": [
            "B=T*A*T^-1",
            "D=T*(A+I)",
            "C=A*T^-1",
            "D*A=B*D",
            "C*D=A*(A+I)",
        ],
        "matrix": {
            "A_sha256": matrix_digest(a),
            "K_sha256": matrix_digest(k),
            "rank_A": rank(a),
            "rank_A_plus_I": rank(a_plus_i),
            "rank_K": rank(k),
            "A_row_weights": [row.bit_count() for row in a],
            "K_rows": [f"0x{row:08x}" for row in k],
            "K_row_weights": [row.bit_count() for row in k],
            "C_row_capacities": list(capacities),
            "capacity_2_indices": list(cap2_indices),
        },
        "distance_forest_bounds": list(thresholds),
        "consequences": {
            "D_weight_tail_lower_bounds": {
                f"rows_with_weight_at_least_{weight}": int(count)
                for weight, count in sorted(tail_bounds.items())
            },
            "D_total_weight_lower_bound": d_weight_sum_lower_bound,
            "rows_with_D_weight_at_least_5": tail_bounds[5],
            "rows_with_B_weight_at_most_2": tail_bounds[5],
            "rows_with_B_weight_3_upper_bound": BITS - tail_bounds[5],
        },
        "lossless_search_normalization": {
            "statement": (
                "choose a perfect matching of invertible C and simultaneously permute "
                "q coordinates so that every C row contains its diagonal entry"
            ),
            "capacity_2_rows_extra_columns_at_most": 1,
            "capacity_3_rows_extra_columns_at_most": 2,
            "preserves": [
                "C row weights",
                "paired feedback loads 4*wt(B_i)+wt(D_i) up to row permutation",
                "D*A=B*D and C*D=K",
            ],
        },
        "normalized_singleton_propagation": {
            "reasoning": [
                "any singleton C_i=e_j implies D_j=K_i; normalization is not required",
                "all D rows have weight at most 12 because B is invertible and 4*wt(B_i)+wt(D_i)<=16",
                "wt(D_j) in [9,12] forces wt(B_j)=1 and therefore D_j*A equals another D row",
                "an orbit value of weight above 12 is a contradiction; weight at most 8 ends this obstruction",
            ],
            "checked_indices": list(singleton_indices),
            "orbits": {
                str(index): singleton_orbits[index] for index in singleton_indices
            },
            "capacity_2_singleton_allowed_indices": list(allowed_cap2_singletons),
            "capacity_2_rows_forced_to_weight_2": [
                index for index in cap2_indices if index not in allowed_cap2_singletons
            ],
            "capacity_3_singleton_forbidden_indices": [4, 5],
            "forced_extra_C_entries": forced_extra_c_entries,
            "C_total_weight_lower_bound": c_total_weight_lower_bound,
        },
        "general_triangle_pruning": {
            "identity": "A*C=C*B",
            "q_j": "floor((16-wt(D_j))/4)",
            "necessary_inequality": "wt((A*C)_i) <= sum(q_j for j in supp(C_i))",
            "justification": "triangle inequality on (C*B)_i plus wt(B_j)<=q_j",
        },
        "similarity_invariants": {
            "characteristic_polynomial_hex": f"0x{polynomial:x}",
            "characteristic_polynomial_exponents": [
                exponent for exponent in range(BITS + 1) if polynomial >> exponent & 1
            ],
            "characteristic_polynomial_weight": char_weight,
            "cyclic_vector": "0x00000001",
            "irreducible_checks": {
                key: f"0x{value:x}" for key, value in irreducible_checks.items()
            },
            "primitive_order": order,
            "primitive_prime_divisor_residues": {
                str(key): f"0x{value:x}" for key, value in primitive_residues.items()
            },
            "trace_A": (coefficients >> 31) & 1,
            "det_A": coefficients & 1,
            "det_A_plus_I": polynomial.bit_count() & 1,
            "B_digraph_strongly_connected": True,
            "B_total_row_weight_lower_bound_from_cycle_space": b_total_weight_lower_bound,
            "cycle_space_argument": (
                "irreducibility makes the B digraph strongly connected; the 11 nonzero "
                "charpoly coefficients need at least 11 distinct cycle-cover witnesses, "
                "while an m-edge strongly connected digraph has cycle-space dimension "
                "m-32+1"
            ),
        },
        "status": (
            "strict necessary lower bounds only; they do not contradict the Kraft caps, "
            "so arbitrary-T feasibility remains open"
        ),
    }


def main() -> None:
    document = build_certificate()
    payload = json.dumps(document, indent=2, sort_keys=True) + "\n"
    DEFAULT_OUTPUT.write_text(payload, encoding="utf-8")
    print(payload, end="")


if __name__ == "__main__":
    main()
