"""Audit the fixed C6 cross-output recoding boundary of the 85/6 adder.

This is intentionally a small relation audit, not a circuit search.  It uses
the 1458 legal K/P/G states of bits 2..7 and the two possible C2 values to
check fixed paid-rail substitutions and bounded one-/two-level templates.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Callable, Iterable


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = (
    ROOT
    / ".research"
    / "byte_adder_architecture_restart"
    / "byte-adder-human85-s3-positive-phase-full.json"
)
OUTPUT = HERE / "c6-joint-owner-audit.json"

EXPECTED_SOURCE_SHA256 = (
    "b3dbe1d83ed28f32c929f4c840a6fa69a9d747e84895c0df9af794d7f704feee"
)

KPG = {
    "K": (0, 1, 0),
    "P": (0, 0, 1),
    "G": (1, 0, 0),
}

BINARY_OPS: dict[str, Callable[[int, int, int], int]] = {
    "AND": lambda left, right, mask: left & right,
    "OR": lambda left, right, mask: left | right,
    "NAND": lambda left, right, mask: (~(left & right)) & mask,
    "NOR": lambda left, right, mask: (~(left | right)) & mask,
}


@dataclass(frozen=True)
class Candidate:
    signature: int
    cost: int
    arrival: int
    formula: str


def _rows() -> list[dict[str, int]]:
    rows: list[dict[str, int]] = []
    for state2 in KPG:
        for state3 in KPG:
            for state4 in KPG:
                for state5 in KPG:
                    for state6 in KPG:
                        for state7 in KPG:
                            for c2 in (0, 1):
                                g2, q2, p2 = KPG[state2]
                                g3, q3, p3 = KPG[state3]
                                g4, q4, p4 = KPG[state4]
                                g5, q5, p5 = KPG[state5]
                                g6, q6, p6 = KPG[state6]
                                g7, q7, p7 = KPG[state7]

                                n23 = 1 - (q2 | q3)
                                r23 = n23 & (c2 | g2)
                                c4 = g3 | r23

                                k34 = g3 | g4
                                g345 = k34 | g5
                                v45 = 1 - (q4 | q5)
                                d45 = g5 | v45
                                c6_enable = r23 | g345
                                c6 = d45 & c6_enable

                                # A late-carry factorization exposed by the
                                # already-paid T4 phase.  The late term reaches
                                # D6 only when consumed by a final Switch.
                                t4 = p4 & c4
                                f6 = d45 & g345
                                late = t4 & p5
                                assert c6 == (f6 | late)

                                # The strongest proper partial descriptor:
                                # C6 = G5 OR U6.
                                u6_enable = r23 | k34
                                u6 = v45 & u6_enable
                                assert c6 == (g5 | u6)

                                r4 = 1 - (p4 | c4)
                                s4 = p4 ^ c4
                                d5 = 1 - (p5 & c6)
                                d5_from_u6 = 1 - (p5 & u6)
                                e5 = g4 | p5
                                s5 = p5 ^ (g4 | t4)
                                assert d5 == d5_from_u6
                                assert s5 == (d5 & (e5 | t4))

                                n6 = g6 | q6
                                k67 = g6 | g7
                                t67 = q6 & p7
                                r67 = 1 - (q6 | p7)
                                e7 = t67 | r67
                                h7 = t67 | q7

                                a6 = c6 | n6
                                b6 = 1 - (c6 & n6)
                                z7 = 1 - (c6 | k67)

                                # Shared G5 absorption for the U6 descriptor.
                                m = g5 | g6
                                nprime = m | q6
                                kprime = m | g7
                                a6_u = u6 | nprime
                                z7_u = 1 - (u6 | kprime)
                                assert a6_u == a6
                                assert z7_u == z7

                                c7 = g6 | (p6 & c6)
                                s6 = p6 ^ c6
                                s7 = p7 ^ c7
                                c8 = g7 | (p7 & c7)
                                s7_owner = (e7 & a6_u) | (z7_u & p7)
                                assert s6 == (1 - (a6 & b6))
                                assert s7_owner == s7
                                assert c8 == (1 - (z7_u | h7))

                                rows.append(
                                    {
                                        "c2": c2,
                                        "g2": g2,
                                        "q2": q2,
                                        "p2": p2,
                                        "g3": g3,
                                        "q3": q3,
                                        "p3": p3,
                                        "n23": n23,
                                        "r23": r23,
                                        "c4": c4,
                                        "g4": g4,
                                        "q4": q4,
                                        "p4": p4,
                                        "g5": g5,
                                        "q5": q5,
                                        "p5": p5,
                                        "k34": k34,
                                        "g345": g345,
                                        "v45": v45,
                                        "d45": d45,
                                        "c6": c6,
                                        "f6": f6,
                                        "late": late,
                                        "u6": u6,
                                        "t4": t4,
                                        "r4": r4,
                                        "s4": s4,
                                        "d5": d5,
                                        "e5": e5,
                                        "s5": s5,
                                        "g6": g6,
                                        "q6": q6,
                                        # P6 is deliberately granted for free
                                        # to make a no-hit lower bound stronger.
                                        "p6": p6,
                                        "n6": n6,
                                        "g7": g7,
                                        "q7": q7,
                                        "p7": p7,
                                        "k67": k67,
                                        "t67": t67,
                                        "r67": r67,
                                        "e7": e7,
                                        "h7": h7,
                                        "m": m,
                                        "nprime": nprime,
                                        "kprime": kprime,
                                        "a6": a6_u,
                                        "b6": b6,
                                        "z7": z7_u,
                                        "s6": s6,
                                        "s7": s7,
                                        "c8": c8,
                                        "c6_enable": c6_enable,
                                        "u6_enable": u6_enable,
                                        "s5_enable": e5 | t4,
                                        "s7_enable": e7 | z7_u,
                                    }
                                )
    return rows


def _signatures(rows: list[dict[str, int]]) -> dict[str, int]:
    names = rows[0].keys()
    result = {name: 0 for name in names}
    for index, row in enumerate(rows):
        bit = 1 << index
        for name, value in row.items():
            if value:
                result[name] |= bit
    return result


def _one_gate_hits(
    target: int,
    basis: list[str],
    signatures: dict[str, int],
    mask: int,
) -> list[str]:
    hits: set[str] = set()
    for left_index, left_name in enumerate(basis):
        left = signatures[left_name]
        if ((~left) & mask) == target:
            hits.add(f"NOT({left_name})")
        for right_name in basis[left_index:]:
            right = signatures[right_name]
            for op_name, operation in BINARY_OPS.items():
                if operation(left, right, mask) == target:
                    hits.add(f"{op_name}({left_name},{right_name})")
    return sorted(hits)


def _generated_one_gate(
    basis: list[str],
    signatures: dict[str, int],
    arrivals: dict[str, int],
    mask: int,
) -> list[Candidate]:
    candidates: dict[tuple[int, int], Candidate] = {}

    def keep(candidate: Candidate) -> None:
        key = (candidate.signature, candidate.arrival)
        current = candidates.get(key)
        if current is None or (candidate.cost, candidate.formula) < (
            current.cost,
            current.formula,
        ):
            candidates[key] = candidate

    for name in basis:
        keep(Candidate(signatures[name], 0, arrivals[name], name))

    for left_index, left_name in enumerate(basis):
        left = signatures[left_name]
        keep(
            Candidate(
                (~left) & mask,
                1,
                arrivals[left_name] + 1,
                f"NOT({left_name})",
            )
        )
        for right_name in basis[left_index:]:
            right = signatures[right_name]
            arrival = max(arrivals[left_name], arrivals[right_name]) + 1
            for op_name, operation in BINARY_OPS.items():
                keep(
                    Candidate(
                        operation(left, right, mask),
                        1,
                        arrival,
                        f"{op_name}({left_name},{right_name})",
                    )
                )
    return list(candidates.values())


def _bounded_two_gate_hits(
    target: int,
    basis: list[str],
    signatures: dict[str, int],
    arrivals: dict[str, int],
    mask: int,
    deadline: int,
) -> list[dict[str, int | str]]:
    generated = [
        candidate
        for candidate in _generated_one_gate(basis, signatures, arrivals, mask)
        if candidate.cost == 1
    ]
    hits: dict[str, dict[str, int | str]] = {}
    for first in generated:
        if first.arrival + 1 <= deadline and ((~first.signature) & mask) == target:
            formula = f"NOT({first.formula})"
            hits[formula] = {
                "formula": formula,
                "cost": 2,
                "arrival": first.arrival + 1,
            }
        for name in basis:
            arrival = max(first.arrival, arrivals[name]) + 1
            if arrival > deadline:
                continue
            for op_name, operation in BINARY_OPS.items():
                if operation(first.signature, signatures[name], mask) == target:
                    formula = f"{op_name}({first.formula},{name})"
                    hits[formula] = {
                        "formula": formula,
                        "cost": 2,
                        "arrival": arrival,
                    }
    return [hits[key] for key in sorted(hits)]


def _flat_three_gate_hits(
    target: int,
    basis: list[str],
    signatures: dict[str, int],
    arrivals: dict[str, int],
    mask: int,
    deadline: int,
) -> list[dict[str, int | str]]:
    candidates = _generated_one_gate(basis, signatures, arrivals, mask)
    # Keep only Pareto-useful signatures.  A lower-cost, no-later rail with the
    # same value dominates every more expensive occurrence at the final gate.
    pareto: dict[int, list[Candidate]] = {}
    for candidate in candidates:
        bucket = pareto.setdefault(candidate.signature, [])
        if any(
            other.cost <= candidate.cost and other.arrival <= candidate.arrival
            for other in bucket
        ):
            continue
        bucket[:] = [
            other
            for other in bucket
            if not (
                candidate.cost <= other.cost
                and candidate.arrival <= other.arrival
            )
        ]
        bucket.append(candidate)
    rails = [candidate for bucket in pareto.values() for candidate in bucket]

    hits: dict[str, dict[str, int | str]] = {}
    for left_index, left in enumerate(rails):
        for right in rails[left_index:]:
            shared = left.formula == right.formula and left.cost == right.cost
            cost = (left.cost if shared else left.cost + right.cost) + 1
            arrival = max(left.arrival, right.arrival) + 1
            if cost > 3 or arrival > deadline:
                continue
            for op_name, operation in BINARY_OPS.items():
                if operation(left.signature, right.signature, mask) == target:
                    formula = f"{op_name}({left.formula},{right.formula})"
                    hits[formula] = {
                        "formula": formula,
                        "cost": cost,
                        "arrival": arrival,
                    }
    return [hits[key] for key in sorted(hits)]


def _native_xor_relations(
    target: int,
    basis: list[str],
    signatures: dict[str, int],
    arrivals: dict[str, int],
    mask: int,
) -> list[dict[str, int | str | bool]]:
    hits: list[dict[str, int | str | bool]] = []
    for left_index, left_name in enumerate(basis):
        for right_name in basis[left_index:]:
            xor = signatures[left_name] ^ signatures[right_name]
            for op_name, signature in (("XOR", xor), ("XNOR", (~xor) & mask)):
                if signature != target:
                    continue
                arrival = max(arrivals[left_name], arrivals[right_name]) + 2
                hits.append(
                    {
                        "formula": f"{op_name}({left_name},{right_name})",
                        "cost": 3,
                        "arrival": arrival,
                        "meets_d6": arrival <= 6,
                    }
                )
    return hits


def _substitution_hits(
    rows: Iterable[dict[str, int]],
    candidates: list[str],
) -> dict[str, list[str]]:
    materialized = list(rows)
    checks = {
        "c6_replace_r23_enable": lambda row, rail: row["d45"]
        & (row[rail] | row["g345"])
        == row["c6"],
        "c6_replace_g345_enable": lambda row, rail: row["d45"]
        & (row["r23"] | row[rail])
        == row["c6"],
        "c6_replace_d45_data": lambda row, rail: row[rail]
        & (row["r23"] | row["g345"])
        == row["c6"],
        "s5_replace_d5_data": lambda row, rail: row[rail]
        & (row["e5"] | row["t4"])
        == row["s5"],
        "s5_replace_e5_enable": lambda row, rail: row["d5"]
        & (row[rail] | row["t4"])
        == row["s5"],
        "s5_replace_t4_enable": lambda row, rail: row["d5"]
        & (row["e5"] | row[rail])
        == row["s5"],
    }
    return {
        check_name: sorted(
            rail
            for rail in candidates
            if all(check(row, rail) for row in materialized)
        )
        for check_name, check in checks.items()
    }


def build_audit() -> dict[str, object]:
    source_sha256 = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if source_sha256 != EXPECTED_SOURCE_SHA256:
        raise RuntimeError(
            f"authoritative 85/6 source changed: {source_sha256}"
        )

    rows = _rows()
    if len(rows) != 1458:
        raise RuntimeError(f"unexpected audit domain: {len(rows)}")
    signatures = _signatures(rows)
    mask = (1 << len(rows)) - 1

    # Current and partial-descriptor rails are both granted.  In particular,
    # D45 and G345 are still free inputs even though U6's purpose is to delete
    # them; a no-hit result under this superset is therefore conservative.
    basis = [
        "c2",
        "g2",
        "q2",
        "p2",
        "g3",
        "q3",
        "p3",
        "n23",
        "r23",
        "c4",
        "g4",
        "q4",
        "p4",
        "g5",
        "q5",
        "p5",
        "k34",
        "g345",
        "v45",
        "d45",
        "u6",
        "t4",
        "d5",
        "e5",
        "g6",
        "q6",
        "p6",
        "n6",
        "g7",
        "q7",
        "p7",
        "k67",
        "t67",
        "r67",
        "e7",
        "h7",
        "m",
        "nprime",
        "kprime",
        "a6",
        "z7",
    ]
    arrivals = {
        "c2": 2,
        "g2": 1,
        "q2": 1,
        "p2": 2,
        "g3": 1,
        "q3": 1,
        "p3": 2,
        "n23": 2,
        "r23": 3,
        "c4": 4,
        "g4": 1,
        "q4": 1,
        "p4": 2,
        "g5": 1,
        "q5": 1,
        "p5": 2,
        "k34": 2,
        "g345": 3,
        "v45": 2,
        "d45": 3,
        "u6": 4,
        "t4": 5,
        "d5": 5,
        "e5": 3,
        "g6": 1,
        "q6": 1,
        "p6": 2,
        "n6": 2,
        "g7": 1,
        "q7": 1,
        "p7": 2,
        "k67": 2,
        "t67": 3,
        "r67": 3,
        "e7": 4,
        "h7": 4,
        "m": 2,
        "nprime": 3,
        "kprime": 3,
        "a6": 5,
        "z7": 5,
    }

    one_gate = {
        target: _one_gate_hits(
            signatures[target], basis, signatures, mask
        )
        for target in ("d5", "a6", "b6", "z7", "s5", "s6", "s7", "c8")
    }
    two_gate_s6 = _bounded_two_gate_hits(
        signatures["s6"], basis, signatures, arrivals, mask, deadline=6
    )
    flat_three_gate_s7 = _flat_three_gate_hits(
        signatures["s7"], basis, signatures, arrivals, mask, deadline=6
    )
    native_s7 = _native_xor_relations(
        signatures["s7"], basis, signatures, arrivals, mask
    )

    direct_candidates = [
        name
        for name in basis
        if name not in {"a6", "z7"}
    ]
    substitutions = _substitution_hits(rows, direct_candidates)

    owner_audit = {
        "c6_conflict_rows": 0,
        "u6_conflict_rows": 0,
        "s5_conflict_rows": 0,
        "s7_conflict_rows": sum(
            1
            for row in rows
            if row["e7"]
            and row["z7"]
            and row["a6"] != row["p7"]
        ),
        "c6_z_rows": sum(1 for row in rows if not row["c6_enable"]),
        "u6_z_rows": sum(1 for row in rows if not row["u6_enable"]),
        "s5_z_rows": sum(1 for row in rows if not row["s5_enable"]),
        "s7_z_rows": sum(1 for row in rows if not row["s7_enable"]),
        "s5_one_undriven_rows": sum(
            1 for row in rows if row["s5"] and not row["s5_enable"]
        ),
        "s7_one_undriven_rows": sum(
            1 for row in rows if row["s7"] and not row["s7_enable"]
        ),
        "late_carry_rows": sum(1 for row in rows if row["late"]),
        "late_only_carry_rows": sum(
            1 for row in rows if row["late"] and not row["f6"]
        ),
    }
    if any(
        owner_audit[name]
        for name in (
            "c6_conflict_rows",
            "u6_conflict_rows",
            "s5_conflict_rows",
            "s7_conflict_rows",
            "s5_one_undriven_rows",
            "s7_one_undriven_rows",
        )
    ):
        raise RuntimeError(f"owner contract failed: {owner_audit}")

    if two_gate_s6:
        raise RuntimeError(f"unexpected <=2 gate S6 formula: {two_gate_s6}")
    if flat_three_gate_s7:
        raise RuntimeError(
            f"unexpected <=3 gate D6 S7 formula: {flat_three_gate_s7}"
        )

    ledger = {
        "current_fixed_downstream_cut": {
            "K34": 1,
            "G345": 1,
            "V45": 1,
            "D45": 1,
            "C6_two_switch_owner": 4,
            "D5": 1,
            "n6": 1,
            "K67": 1,
            "A6": 1,
            "B6": 1,
            "Z7": 1,
            "S6_final": 1,
            "total": 15,
        },
        "u6_fixed_downstream_lower_bound": {
            "K34": 1,
            "V45": 1,
            "U6_two_switch_owner": 4,
            "D5": 1,
            "M_N_Kprime": 3,
            "A6_Z7": 2,
            "S6_direct_minimum": 3,
            "total_lower_bound": 15,
        },
    }

    return {
        "schema": "byte-adder-c6-joint-owner-audit-v1",
        "method": (
            "1458 legal K/P/G rows; fixed paid-rail substitutions; "
            "bounded one/two-level ordinary-gate templates; no SAT/BDD"
        ),
        "source": {
            "path": str(SOURCE.relative_to(ROOT)).replace("\\", "/"),
            "sha256": source_sha256,
            "score": {"gate": 85, "delay": 6, "energy": 510},
        },
        "domain_rows": len(rows),
        "basis": basis,
        "one_gate_hits": one_gate,
        "two_gate_s6_hits": two_gate_s6,
        "flat_three_gate_d6_s7_hits": flat_three_gate_s7,
        "native_xor_s7_relations": native_s7,
        "direct_substitution_hits": substitutions,
        "owner_audit": owner_audit,
        "ledger": ledger,
        "result": {
            "complete_84_6_candidate": False,
            "fixed_downstream_u6_family_lower_bound": "85/6",
            "reason": (
                "U6 deletes D45/G345, but shared G5 absorption consumes one "
                "gate and S6 has no <=2-gate D6 closure even when all listed "
                "paid rails and P6 are granted for free."
            ),
        },
    }


def main() -> int:
    payload = build_audit()
    encoded = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    OUTPUT.write_text(encoded, encoding="utf-8", newline="\n")
    print(
        json.dumps(
            {
                "output": str(OUTPUT),
                "sha256": hashlib.sha256(encoded.encode()).hexdigest(),
                "domain_rows": payload["domain_rows"],
                "two_gate_s6_hits": len(payload["two_gate_s6_hits"]),
                "flat_three_gate_d6_s7_hits": len(
                    payload["flat_three_gate_d6_s7_hits"]
                ),
                "owner_audit": payload["owner_audit"],
                "ledger": payload["ledger"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
