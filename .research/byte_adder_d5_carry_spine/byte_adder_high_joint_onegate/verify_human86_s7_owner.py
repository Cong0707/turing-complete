"""Verify the 86/6 S7 owner merge against the audited human 87/6 circuit.

This script is read-only.  It does not encode a circuit, touch the live save,
or start the game.  It evaluates the source circuit over all 131072 inputs and
then substitutes the proposed two-driver S7 owner at the bitset level.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
ARCH_RESTART = REPO_ROOT / ".research" / "byte_adder_architecture_restart"
sys.path.insert(0, str(ARCH_RESTART))
sys.path.insert(0, str(REPO_ROOT / "src"))

from audit_human_87 import (  # noqa: E402
    ALL_ROWS,
    ROW_COUNT,
    _compile,
    _evaluate,
    _invert,
    _known_relations,
    decode_v15,
)


DEFAULT_SOURCE = ARCH_RESTART / "source_human87" / "circuit.data"
DEFAULT_OUTPUT = HERE / "human86-s7-owner-certificate.json"
EXPECTED_SOURCE_SHA256 = (
    "a0d2928aa5fe5a747637c3a6955345bb18dfccc88c7824bb8514ee2f5c54f29c"
)


def _architecture_state_rows() -> list[dict[str, int | str]]:
    states = {
        "K": (1, 0, 0),
        "P": (0, 1, 0),
        "G": (0, 0, 1),
    }
    rows: list[dict[str, int | str]] = []
    for state6, (q6, p6, g6) in states.items():
        for state7, (_q7, p7, g7) in states.items():
            for c6 in (0, 1):
                np6 = 1 - p6
                n207 = c6 | np6
                n278 = 1 - (q6 | p7)
                n258 = q6 & p7
                u = n278 | n258
                n285 = 1 - (c6 | g6 | g7)
                driver0_one = u & n207
                driver0_zero = u & (1 - n207)
                driver1_one = n285 & p7
                driver1_zero = n285 & (1 - p7)
                output = driver0_one | driver1_one
                driven = u | n285
                conflict = (driver0_one & driver1_zero) | (
                    driver1_one & driver0_zero
                )
                carry7 = g6 | (p6 & c6)
                expected = p7 ^ carry7
                rows.append(
                    {
                        "bit6": state6,
                        "bit7": state7,
                        "C6": c6,
                        "U": u,
                        "n207": n207,
                        "n285": n285,
                        "P7": p7,
                        "S7": output,
                        "expected": expected,
                        "driven": driven,
                        "conflict": conflict,
                    }
                )
    if any(
        row["S7"] != row["expected"]
        or row["conflict"]
        or (row["expected"] and not row["driven"])
        for row in rows
    ):
        raise RuntimeError("18-state architecture proof failed")
    return rows


def _network(compiled, component_index: int, pin_name: str) -> int:
    return compiled.pin_networks[(component_index, pin_name)]


def _signal(values, driven, compiled, component_index: int, pin_name: str = "out") -> int:
    network = _network(compiled, component_index, pin_name)
    return values[network][0] & driven[network][0] & ALL_ROWS


def verify(source: Path) -> dict[str, object]:
    payload = source.read_bytes()
    source_sha256 = hashlib.sha256(payload).hexdigest()
    if source_sha256 != EXPECTED_SOURCE_SHA256:
        raise RuntimeError(
            "source hash changed: "
            f"expected {EXPECTED_SOURCE_SHA256}, got {source_sha256}"
        )

    circuit = decode_v15(payload)
    compiled = _compile(circuit)
    inputs, values, driven, arrivals, _switch_rows, source_conflict = _evaluate(
        circuit, compiled
    )
    relations = _known_relations(inputs)
    architecture_states = _architecture_state_rows()

    # Stable component identities from human-87-audit.json.
    q6 = _signal(values, driven, compiled, 61)
    g6 = _signal(values, driven, compiled, 62)
    np6 = _signal(values, driven, compiled, 60)
    p7 = _signal(values, driven, compiled, 67)
    g7 = _signal(values, driven, compiled, 68)
    c6 = _signal(values, driven, compiled, 58)
    n207 = _signal(values, driven, compiled, 64)
    n258 = _signal(values, driven, compiled, 70)
    n278 = _signal(values, driven, compiled, 73)
    n285 = _signal(values, driven, compiled, 74)

    # Keep these checks explicit so a changed source topology cannot silently
    # inherit labels from the old audit.
    formula_checks = {
        "nP6=NOT(P6)": np6 == _invert(inputs["A"][6] ^ inputs["B"][6]),
        "n278=NOR(Q6,P7)": n278 == _invert(q6 | p7),
        "n258=AND(Q6,P7)": n258 == (q6 & p7),
        "n207=OR(C6,nP6)": n207 == (c6 | np6),
        "n285=NOR(C6,G6,G7)": n285 == _invert(c6 | g6 | g7),
    }
    if not all(formula_checks.values()):
        raise RuntimeError(f"source formula check failed: {formula_checks}")

    # New U is one ordinary OR at arrival 4.  The two Switches remain a single
    # resolved S7 owner and therefore must be checked as drivers, not only as
    # a Boolean OR expression.
    u = n278 | n258
    driver0_one = u & n207
    driver0_zero = u & _invert(n207)
    driver1_one = n285 & p7
    driver1_zero = n285 & _invert(p7)
    proposed_one = driver0_one | driver1_one
    proposed_driven = u | n285
    proposed_conflict = (driver0_one & driver1_zero) | (
        driver1_one & driver0_zero
    )

    # _known_relations is keyed by bitset, so retrieve S7 directly without
    # depending on dict insertion details.
    expected_s7 = next(
        bitset for bitset, names in relations.items() if "S7" in names
    )
    old_s7_network = _network(compiled, 66, "out")
    old_s7_one = values[old_s7_network][0] & driven[old_s7_network][0] & ALL_ROWS
    old_s7_driven = driven[old_s7_network][0] & ALL_ROWS

    mismatch = proposed_one ^ expected_s7
    old_difference = proposed_one ^ old_s7_one
    expected_one_undriven = expected_s7 & _invert(proposed_driven)

    arrival_contract = {
        "n278": arrivals[73],
        "n258": arrivals[70],
        "U": max(arrivals[73], arrivals[70]) + 1,
        "n207": arrivals[64],
        "n285": arrivals[74],
        "P7": arrivals[67],
    }
    arrival_contract["SW(U,n207)"] = max(
        arrival_contract["U"], arrival_contract["n207"]
    ) + 1
    arrival_contract["SW(n285,P7)"] = max(
        arrival_contract["n285"], arrival_contract["P7"]
    ) + 1

    if mismatch or old_difference or proposed_conflict or expected_one_undriven:
        raise RuntimeError("proposed S7 owner failed full-domain verification")
    if max(arrival_contract["SW(U,n207)"], arrival_contract["SW(n285,P7)"]) != 6:
        raise RuntimeError(f"arrival contract changed: {arrival_contract}")

    certificate = {
        "schema": "byte-adder-human86-s7-owner-certificate-v1",
        "source": {
            "path": str(source),
            "bytes": len(payload),
            "sha256": source_sha256,
            "declared_score": {
                "gate": circuit.gate,
                "delay": circuit.delay,
                "energy": circuit.energy,
            },
        },
        "replacement": {
            "removed_cost": 2,
            "added_cost": 1,
            "score": {"gate": 86, "delay": 6, "energy": 516},
            "U": "OR(n278,n258)",
            "S7": "BUS(SW(U,n207),SW(n285,P7))",
        },
        "formula_checks": formula_checks,
        "arrival": arrival_contract,
        "architecture_domain": {
            "rows": len(architecture_states),
            "mismatch_rows": sum(
                row["S7"] != row["expected"] for row in architecture_states
            ),
            "conflict_rows": sum(row["conflict"] for row in architecture_states),
            "expected_one_undriven_rows": sum(
                bool(row["expected"] and not row["driven"])
                for row in architecture_states
            ),
            "active_one_rows": sum(row["S7"] for row in architecture_states),
            "active_zero_rows": sum(
                bool(row["driven"] and not row["S7"])
                for row in architecture_states
            ),
            "z_zero_rows": sum(not row["driven"] for row in architecture_states),
            "table": architecture_states,
        },
        "full_domain": {
            "rows": ROW_COUNT,
            "source_conflict_rows": source_conflict.bit_count(),
            "mismatch_rows": mismatch.bit_count(),
            "different_from_old_S7_rows": old_difference.bit_count(),
            "new_owner_conflict_rows": proposed_conflict.bit_count(),
            "expected_one_undriven_rows": expected_one_undriven.bit_count(),
            "old_S7_one_rows": old_s7_one.bit_count(),
            "new_S7_one_rows": proposed_one.bit_count(),
            "old_S7_driven_rows": old_s7_driven.bit_count(),
            "new_S7_driven_rows": proposed_driven.bit_count(),
            "old_S7_z_rows": ROW_COUNT - old_s7_driven.bit_count(),
            "new_S7_z_rows": ROW_COUNT - proposed_driven.bit_count(),
            "new_driver0_active_one_rows": driver0_one.bit_count(),
            "new_driver0_active_zero_rows": driver0_zero.bit_count(),
            "new_driver1_active_one_rows": driver1_one.bit_count(),
            "new_driver1_active_zero_rows": driver1_zero.bit_count(),
        },
        "component_replacement": {
            "reuse_switch_component": 66,
            "replace_switch_component_71_with_kind_7_OR": True,
            "keep_switch_component": 72,
            "existing_n258_component": 70,
            "existing_n278_component": 73,
            "existing_n207_component": 64,
            "existing_n285_component": 74,
        },
    }
    return certificate


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    certificate = verify(args.source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(certificate, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(certificate, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
