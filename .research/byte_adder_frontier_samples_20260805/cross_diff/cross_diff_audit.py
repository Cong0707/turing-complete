"""Deterministic structural cross-diff for the two user 103/5 samples.

The script reads existing full-truth audits and the reviewed Patchouli 84/6
Factory DAG.  It does not decode or write circuit.data, launch the game, or
perform synthesis/search.
"""

from __future__ import annotations

from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
SAMPLE_ROOT = HERE.parent
REPO = HERE.parents[2]
DERIVED = SAMPLE_ROOT / "derived"
A_PATH = DERIVED / "switch-103-5-a-audit.json"
B_PATH = DERIVED / "switch-103-5-b-audit.json"
AUTH_PATH = (
    REPO
    / ".research"
    / "byte84_patchouli_image"
    / "byte-adder-patchouli84-s5-five-gate-full.json"
)
OUTPUT = HERE / "cross-diff-certificate.json"

ROWS = 1 << 17
TABLE_BYTES = ROWS // 8
ALL = (1 << ROWS) - 1


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def truth_hash(value: int) -> str:
    return sha256(value.to_bytes(TABLE_BYTES, "little")).hexdigest()


def variable(index: int) -> int:
    run = 1 << index
    block = ((1 << run) - 1) << run
    result = 0
    for offset in range(0, ROWS, 2 * run):
        result |= block << offset
    return result


def authority_states(payload: dict[str, Any]) -> tuple[dict[int, tuple[int, int]], dict[tuple[str, int], list[dict[str, Any]]]]:
    variables = tuple(variable(index) for index in range(17))
    states: dict[int, tuple[int, int]] = {}
    by_signal: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
    for node in payload["factory_dag"]["nodes"]:
        node_id = int(node["id"])
        op = str(node["op"])
        args = [int(value) for value in node["args"]]
        if op == "INPUT":
            bits, driven = variables[node_id - 1], ALL
        else:
            values = [states[value][0] for value in args]
            if op == "AND":
                bits, driven = values[0] & values[1], ALL
            elif op == "OR":
                bits, driven = values[0] | values[1], ALL
            elif op == "NAND":
                bits, driven = (~(values[0] & values[1])) & ALL, ALL
            elif op == "NOR":
                bits, driven = (~(values[0] | values[1])) & ALL, ALL
            elif op == "XOR":
                bits, driven = values[0] ^ values[1], ALL
            elif op == "BUS":
                bits = 0
                driven = 0
                for enable, data in zip(values[0::2], values[1::2], strict=True):
                    bits |= enable & data
                    driven |= enable
            else:
                raise AssertionError(f"unsupported authority op {op}")
        states[node_id] = (bits, driven)
        by_signal[(truth_hash(bits), ((~driven) & ALL).bit_count())].append(
            {
                "id": node_id,
                "op": op,
                "label": str(node.get("label", "")),
                "arrival": int(node["arrival"]),
            }
        )
    return states, by_signal


def component_cost(component: dict[str, Any]) -> int:
    return 2 if component["op"] == "SWITCH" else 0 if component["op"] in {
        "INPUT",
        "OUTPUT",
        "MAKER2",
        "MAKER8",
        "SPLITTER2",
        "SPLITTER8",
    } else 1


def network_signals(payload: dict[str, Any]) -> dict[int, tuple[tuple[str, int], ...]]:
    return {
        int(network["network"]): tuple(
            (str(item["sha256"]).lower(), int(network["z_rows"]))
            for item in network["truth"]
        )
        for network in payload["networks"]
    }


def input_signature(component: dict[str, Any], signals: dict[int, tuple[tuple[str, int], ...]]) -> tuple[Any, ...]:
    return tuple(
        sorted(
            (pin, (("ZERO", 0),) if network is None else signals[int(network)])
            for pin, network in component["input_networks"].items()
        )
    )


def output_signature(component: dict[str, Any]) -> tuple[Any, ...]:
    return tuple(
        (
            output["pin"],
            tuple(
                (str(item["sha256"]).lower(), int(output["z_rows"]))
                for item in output["truth"]
            ),
        )
        for output in component["outputs"]
    )


def component_arrival(component: dict[str, Any]) -> int:
    return max((int(output["depth"]) for output in component["outputs"]), default=0)


def component_summary(component: dict[str, Any]) -> dict[str, Any]:
    return {
        "index": int(component["index"]),
        "permanent_id": str(component["permanent_id"]),
        "op": str(component["op"]),
        "position": [int(value) for value in component["position"]],
        "cost": component_cost(component),
        "arrival": component_arrival(component),
        "semantic_labels": sorted(
            {
                str(label)
                for output in component["outputs"]
                for item in output["truth"]
                for label in item["semantic_labels"]
            }
        ),
    }


def reduced_contract() -> dict[str, Any]:
    states = {
        "Q": (0, 1, 0),
        "P": (0, 0, 1),
        "G": (1, 0, 0),
    }
    rows: list[dict[str, int | str]] = []
    for c4 in (0, 1):
        for state4, (g4, q4, p4) in states.items():
            for state5, (g5, q5, p5) in states.items():
                c5 = g4 | (p4 & c4)
                c6 = g5 | (p5 & c5)
                d45 = g5 | int(not (q4 | q5))
                r0 = 1 - d45

                e_a = g4 | int(not p5)
                r_a = int(not (c4 | e_a))
                e_b = g4 | g5
                r_b = int(not (c4 | e_b))
                h_b = int(not (q4 | p5))
                n27_b = c4 | int(not p4)

                n73_a = int(not (c4 & p4))
                n76_a = int((not g4) or p5)
                n75_a = int(not (n76_a & e_a))
                s5_a = (n73_a & n75_a) | ((c4 & p4) & e_a)
                s5_b = (r_b & p5) | (q4 & p5) | (h_b & n27_b)
                c6_a = d45 & (e_a | c4)
                c6_b = d45 & (e_b | c4)
                rows.append(
                    {
                        "c4": c4,
                        "state4": state4,
                        "state5": state5,
                        "p5": p5,
                        "expected_s5": c5 ^ p5,
                        "expected_c6": c6,
                        "s5_a": s5_a,
                        "s5_b": s5_b,
                        "c6_a": c6_a,
                        "c6_b": c6_b,
                        "d45": d45,
                        "r0": r0,
                        "r_a": r_a,
                        "r_b": r_b,
                        "h_b": h_b,
                        "n27_b": n27_b,
                        "c6_a_driven": e_a | c4,
                        "c6_b_driven": e_b | c4,
                    }
                )

    mismatch = lambda key, expected: sum(row[key] != row[expected] for row in rows)
    assert mismatch("s5_a", "expected_s5") == 0
    assert mismatch("s5_b", "expected_s5") == 0
    assert mismatch("c6_a", "expected_c6") == 0
    assert mismatch("c6_b", "expected_c6") == 0
    assert all((row["p5"] & row["r_a"]) == (row["p5"] & row["r_b"]) for row in rows)
    assert all((row["r0"] | row["r_a"]) == (1 - row["expected_c6"]) for row in rows)
    assert all((row["r0"] | row["r_b"]) == (1 - row["expected_c6"]) for row in rows)

    truth_columns = {
        key: "".join(str(row[key]) for row in rows)
        for key in (
            "expected_s5",
            "expected_c6",
            "r0",
            "r_a",
            "r_b",
            "h_b",
            "n27_b",
        )
    }
    return {
        "one_hot_rows": len(rows),
        "mismatch": {
            "A_S5": mismatch("s5_a", "expected_s5"),
            "B_S5": mismatch("s5_b", "expected_s5"),
            "A_C6": mismatch("c6_a", "expected_c6"),
            "B_C6": mismatch("c6_b", "expected_c6"),
            "P5_and_RA_vs_P5_and_RB": sum(
                (row["p5"] & row["r_a"]) != (row["p5"] & row["r_b"])
                for row in rows
            ),
        },
        "RA_vs_RB_differing_rows": sum(row["r_a"] != row["r_b"] for row in rows),
        "negative_cover_mismatch": {
            "R0_or_RA_vs_not_C6": sum(
                (row["r0"] | row["r_a"]) != (1 - row["expected_c6"])
                for row in rows
            ),
            "R0_or_RB_vs_not_C6": sum(
                (row["r0"] | row["r_b"]) != (1 - row["expected_c6"])
                for row in rows
            ),
        },
        "reduced_C6_z_rows": {
            "A": sum(not row["c6_a_driven"] for row in rows),
            "B": sum(not row["c6_b_driven"] for row in rows),
        },
        "truth_column_sha256": {
            key: sha256(value.encode("ascii")).hexdigest()
            for key, value in truth_columns.items()
        },
    }


def main() -> None:
    a = load(A_PATH)
    b = load(B_PATH)
    authority = load(AUTH_PATH)
    for tag, payload in (("A", a), ("B", b)):
        assert payload["declared"] == {"gate": 103, "delay": 5, "energy": 515}
        assert payload["derived"]["gate"] == 103
        assert payload["derived"]["max_output_depth"] == 5
        assert payload["derived"]["truth_rows"] == ROWS
        assert payload["derived"]["mismatch_count"] == 0
        assert payload["derived"]["bus_conflict_rows"] == 0
        source = Path(payload["source"]["path"])
        assert file_sha256(source).lower() == str(payload["source"]["sha256"]).lower(), tag
    assert authority["metrics"]["gate"] == 84
    assert authority["metrics"]["delay"] == 6
    assert authority["metrics"]["energy"] == 504

    a_components = {str(item["permanent_id"]): item for item in a["components"]}
    b_components = {str(item["permanent_id"]): item for item in b["components"]}
    a_signals = network_signals(a)
    b_signals = network_signals(b)
    shared_pids = a_components.keys() & b_components.keys()
    a_only = sorted(
        (item for pid, item in a_components.items() if pid not in b_components),
        key=lambda item: int(item["index"]),
    )
    b_only = sorted(
        (item for pid, item in b_components.items() if pid not in a_components),
        key=lambda item: int(item["index"]),
    )
    rewired: list[dict[str, Any]] = []
    exact_shared = 0
    for pid in sorted(shared_pids, key=lambda value: int(a_components[value]["index"])):
        left = a_components[pid]
        right = b_components[pid]
        same_inputs = input_signature(left, a_signals) == input_signature(right, b_signals)
        same_outputs = output_signature(left) == output_signature(right)
        if same_inputs and same_outputs:
            exact_shared += 1
        else:
            rewired.append(
                {
                    "permanent_id": pid,
                    "A_index": int(left["index"]),
                    "B_index": int(right["index"]),
                    "op": str(left["op"]),
                    "position": [int(value) for value in left["position"]],
                    "same_input_signal_signature": same_inputs,
                    "same_output_signal_signature": same_outputs,
                }
            )

    a_by_index = {int(item["index"]): item for item in a["components"]}
    b_by_index = {int(item["index"]): item for item in b["components"]}
    cut = {
        "A": {
            "helper_indices": [74, 83],
            "completion_indices": [73, 75, 76, 77, 78],
        },
        "B": {
            "helper_indices": [42, 53, 83],
            "completion_indices": [29, 37, 39],
        },
    }
    for tag, by_index, unique in (("A", a_by_index, a_only), ("B", b_by_index, b_only)):
        helper = cut[tag]["helper_indices"]
        completion = cut[tag]["completion_indices"]
        cut[tag]["helper_cost"] = sum(component_cost(by_index[index]) for index in helper)
        cut[tag]["completion_cost"] = sum(
            component_cost(by_index[index]) for index in completion
        )
        used = set(helper) | set(completion)
        cut[tag]["common_unique_shell_cost"] = sum(
            component_cost(item) for item in unique if int(item["index"]) not in used
        )
        cut[tag]["unique_total_cost"] = sum(component_cost(item) for item in unique)

    authority_state, authority_by_signal = authority_states(authority)
    expected_authority_outputs = [int(value) for value in authority["factory_dag"]["outputs"]]
    assert max(int(node["arrival"]) for node in authority["factory_dag"]["nodes"] if int(node["id"]) in expected_authority_outputs) == 6

    exact_matches: dict[str, list[dict[str, Any]]] = {"A": [], "B": []}
    for tag, unique in (("A", a_only), ("B", b_only)):
        for component in unique:
            for output in component["outputs"]:
                for item in output["truth"]:
                    key = (str(item["sha256"]).lower(), int(output["z_rows"]))
                    for match in authority_by_signal.get(key, []):
                        exact_matches[tag].append(
                            {
                                "sample_component_index": int(component["index"]),
                                "sample_op": str(component["op"]),
                                "sample_arrival": int(output["depth"]),
                                "authority_node": match,
                            }
                        )

    # Fixed identities for the three useful reason/byproduct rails.
    node67 = authority_state[67][0]
    r0_hash = truth_hash((~node67) & ALL)
    r_b_bits = (~(authority_state[31][0] | authority_state[65][0])) & ALL
    r_b_hash = truth_hash(r_b_bits)
    r_a_hash = truth_hash(authority_state[63][0] & r_b_bits)

    def component_hash(payload: dict[str, Any], index: int) -> str:
        item = payload["components"][index]["outputs"][0]["truth"][0]
        return str(item["sha256"]).lower()

    assert component_hash(a, 84) == r0_hash
    assert component_hash(b, 80) == r0_hash
    assert component_hash(b, 53) == r_b_hash
    assert component_hash(a, 83) == r_a_hash

    raw_sources = {
        "A": {
            "path": str(a["source"]["path"]),
            "sha256": str(a["source"]["sha256"]).lower(),
        },
        "B": {
            "path": str(b["source"]["path"]),
            "sha256": str(b["source"]["sha256"]).lower(),
        },
    }
    certificate = {
        "schema": "byte-adder-103d5-ab-structural-cross-diff-v1",
        "status": "verified_no_unconditional_102d5_splice",
        "scope": "read-only derived audits, fixed truth algebra, authoritative 84/6 DAG",
        "sources": {
            "raw_samples": raw_sources,
            "derived_A": {"path": str(A_PATH), "sha256": file_sha256(A_PATH)},
            "derived_B": {"path": str(B_PATH), "sha256": file_sha256(B_PATH)},
            "authority_84d6": {"path": str(AUTH_PATH), "sha256": file_sha256(AUTH_PATH)},
        },
        "functional_baseline": {
            "A": a["derived"],
            "B": b["derived"],
            "authority_metrics": authority["metrics"],
        },
        "physical_and_signal_diff": {
            "A_component_count": len(a["components"]),
            "B_component_count": len(b["components"]),
            "shared_permanent_id_count": len(shared_pids),
            "shared_exact_signal_interface_count": exact_shared,
            "shared_rewired_count": len(rewired),
            "shared_rewired": rewired,
            "A_only_count": len(a_only),
            "B_only_count": len(b_only),
            "A_only_gate_cost": sum(component_cost(item) for item in a_only),
            "B_only_gate_cost": sum(component_cost(item) for item in b_only),
            "A_only": [component_summary(item) for item in a_only],
            "B_only": [component_summary(item) for item in b_only],
            "resolved_C6_z_rows": {"A": 24576, "B": 36864},
        },
        "one_gate_ledger": {
            "cut_definition": (
                "The requested high-tail saving is the high-side S5 completion "
                "across the C6 producer window; it is not the bit6:7 common suffix."
            ),
            "common_unique_shell_cost_each": 16,
            "A_helper": {
                "cost": cut["A"]["helper_cost"],
                "formulas": [
                    "EA = G4 OR NOT(P5)",
                    "RA = NOT(C4 OR EA)",
                ],
                "saving_vs_B_helper": 1,
            },
            "B_helper": {
                "cost": cut["B"]["helper_cost"],
                "formulas": [
                    "EB = G4 OR G5",
                    "RB = NOT(C4 OR EB)",
                    "HB = NOT(Q4 OR P5)",
                ],
            },
            "A_S5_completion": {
                "cost": cut["A"]["completion_cost"],
                "shape": "3 ordinary gates plus 2 Switches",
            },
            "B_S5_completion": {
                "cost": cut["B"]["completion_cost"],
                "shape": "3 Switches",
                "saving_vs_A_completion": 1,
            },
            "total": {
                "A": cut["A"]["unique_total_cost"],
                "B": cut["B"]["unique_total_cost"],
            },
        },
        "fixed_boolean_contract": reduced_contract(),
        "splice_verdict": {
            "unconditional_complete_102d5": False,
            "reason": (
                "The apparent 24-gate hybrid counts A's two-gate helper with B's "
                "six-gate S5 completion, but the latter consumes HB and B's Q4/n27B "
                "phase interface. HB is paid inside B's three-gate helper and is absent "
                "from A's helper ABI. RA may replace RB only under the P5 data care "
                "domain; that identity does not supply the other missing rails."
            ),
            "omitted_paid_signal": "HB = NOT(Q4 OR P5)",
            "additional_interface_mismatch": [
                "B completion consumes Q4 while A materializes V4=NOT(Q4)",
                "B completion consumes n27B=C4 OR NOT(P4); A exposes a different S4 phase pair",
                "A and B C6 have equal Boolean data but different driven/Z domains",
            ],
            "claim_boundary": (
                "This rejects only a zero-adapter structural splice. It is not a lower "
                "bound against a newly co-designed or resynthesized 102/5 circuit."
            ),
        },
        "authority_84d6_transfer": {
            "exact_existing_function_matches": exact_matches,
            "reason_byproducts": [
                {
                    "name": "R0",
                    "formula": "NOT(D45)",
                    "sample_nodes": ["A84", "B80"],
                    "arrival": 3,
                    "sha256": r0_hash,
                    "authority_status": "not currently materialized; costs one extra gate from node67",
                },
                {
                    "name": "RB",
                    "formula": "NOT(B23 OR G345)",
                    "sample_node": "B53",
                    "arrival": 4,
                    "sha256": r_b_hash,
                    "authority_status": "one paid NOR from authoritative nodes31/65",
                },
                {
                    "name": "RA",
                    "formula": "P5 AND RB",
                    "sample_node": "A83",
                    "arrival": 4,
                    "sha256": r_a_hash,
                    "authority_status": "consumer-restricted reason; not a free full negative carry",
                },
            ],
            "conditional_early_phase": (
                "A T4/R4/S4 and B S4 equal authoritative functions but are one level "
                "earlier only because the samples receive C4 at depth3; authority C4 is depth4."
            ),
            "deterministic_gate_saving_on_current_84d6": 0,
        },
    }
    assert certificate["physical_and_signal_diff"]["shared_permanent_id_count"] == 69
    assert certificate["physical_and_signal_diff"]["shared_exact_signal_interface_count"] == 63
    assert certificate["physical_and_signal_diff"]["shared_rewired_count"] == 6
    assert certificate["physical_and_signal_diff"]["A_only_gate_cost"] == 25
    assert certificate["physical_and_signal_diff"]["B_only_gate_cost"] == 25
    assert cut["A"]["common_unique_shell_cost"] == 16
    assert cut["B"]["common_unique_shell_cost"] == 16
    assert cut["A"]["helper_cost"] == 2 and cut["B"]["helper_cost"] == 3
    assert cut["A"]["completion_cost"] == 7 and cut["B"]["completion_cost"] == 6
    OUTPUT.write_text(
        json.dumps(certificate, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": certificate["status"],
        "shared": len(shared_pids),
        "rewired": len(rewired),
        "A_only_gate": certificate["physical_and_signal_diff"]["A_only_gate_cost"],
        "B_only_gate": certificate["physical_and_signal_diff"]["B_only_gate_cost"],
        "unconditional_102d5": False,
        "authority_deterministic_saving": 0,
        "output": str(OUTPUT),
    }, indent=2))


if __name__ == "__main__":
    main()
