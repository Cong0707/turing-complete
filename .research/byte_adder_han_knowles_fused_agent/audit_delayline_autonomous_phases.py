"""Enumerate small autonomous Delay Line phase generators for Byte Adder.

The searched state machines contain one to three zero-initialized bit Delay
Lines.  Every next-state rail is one constant, state wire, state inversion, or
one binary ordinary/XOR gate over two distinct state rails.  The total update
logic is limited to three weighted gates.  Every machine is simulated by its
exact finite-state trajectory and expanded over all 131072 tested cycles.

The generated state rails and one-gate state decodes are compared with every
live signal of the reviewed 80/7 DAG.  State rails are additionally combined
with every current live signal by one ordinary gate and by a conflict-free,
fully-driven two-Switch BUS.  This is an offline audit; no save is read.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
from typing import Callable

import audit_byte_adder_delayline_sequence as base


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "delayline_autonomous_phase_audit.json"
ROWS = base.ROWS
MASK = base.TRUTH_MASK


@dataclass(frozen=True)
class Update:
    expression: str
    cost: int
    delay: int
    function: Callable[[int], int]


@dataclass(frozen=True)
class PhaseRecipe:
    delays: int
    update_gate: int
    update_delay: int
    updates: tuple[str, ...]
    output: str
    decode_gate: int
    decode_delay: int
    preperiod: int
    period: int

    @property
    def gate(self) -> int:
        return 5 * self.delays + self.update_gate + self.decode_gate

    def key(self) -> tuple[object, ...]:
        return (
            self.gate,
            self.decode_delay,
            self.update_delay,
            self.delays,
            self.updates,
            self.output,
        )

    def serialized(self) -> dict[str, object]:
        timing_status = "UNKNOWN"
        exact_delay = None
        if self.delays == 1:
            update = self.updates[0]
            if update in {"0", "1", "q0"}:
                exact_delay = max(4, self.decode_delay + 4 if self.decode_gate else 4)
                timing_status = "PROVEN"
            elif update == "NOT(q0)":
                exact_delay = max(5, self.decode_delay + 4 if self.decode_gate else 5)
                timing_status = "PROVEN"
        return {
            "delay_line_count": self.delays,
            "delay_line_gate": 5 * self.delays,
            "update_gate": self.update_gate,
            "update_delay": self.update_delay,
            "updates": list(self.updates),
            "output": self.output,
            "decode_gate": self.decode_gate,
            "decode_delay": self.decode_delay,
            "total_gate": self.gate,
            "preperiod": self.preperiod,
            "period": self.period,
            "native_feedback_timing_status": timing_status,
            "native_feedback_delay": exact_delay,
        }


BIT_OPS: dict[str, tuple[int, int, Callable[[int, int], int]]] = {
    "AND": (1, 1, lambda left, right: left & right),
    "OR": (1, 1, lambda left, right: left | right),
    "NAND": (1, 1, lambda left, right: 1 - (left & right)),
    "NOR": (1, 1, lambda left, right: 1 - (left | right)),
    "XOR": (3, 2, lambda left, right: left ^ right),
    "XNOR": (3, 2, lambda left, right: 1 - (left ^ right)),
}


PACKED_OPS = {
    "AND": lambda left, right: left & right,
    "OR": lambda left, right: left | right,
    "NAND": lambda left, right: ~(left & right) & MASK,
    "NOR": lambda left, right: ~(left | right) & MASK,
    "XOR": lambda left, right: left ^ right,
    "XNOR": lambda left, right: ~(left ^ right) & MASK,
}


def updates(width: int) -> tuple[Update, ...]:
    result = [
        Update("0", 0, 0, lambda _state: 0),
        Update("1", 0, 0, lambda _state: 1),
    ]
    for bit in range(width):
        result.append(
            Update(f"q{bit}", 0, 0, lambda state, bit=bit: (state >> bit) & 1)
        )
        result.append(
            Update(
                f"NOT(q{bit})",
                1,
                1,
                lambda state, bit=bit: 1 - ((state >> bit) & 1),
            )
        )
    for left in range(width):
        for right in range(left + 1, width):
            for op, (cost, delay, function) in BIT_OPS.items():
                result.append(
                    Update(
                        f"{op}(q{left},q{right})",
                        cost,
                        delay,
                        lambda state,
                        left=left,
                        right=right,
                        function=function: function(
                            (state >> left) & 1, (state >> right) & 1
                        ),
                    )
                )
    return tuple(result)


def trajectory(width: int, selected: tuple[Update, ...]) -> tuple[tuple[int, ...], int]:
    seen: dict[int, int] = {}
    states = []
    state = 0
    while state not in seen:
        seen[state] = len(states)
        states.append(state)
        following = 0
        for bit, update in enumerate(selected):
            following |= update.function(state) << bit
        state = following
    return tuple(states), seen[state]


def pack_eventual(values: tuple[int, ...], preperiod: int) -> int:
    prefix = values[:preperiod]
    repeating = values[preperiod:]
    if not repeating:
        raise RuntimeError("finite state trajectory lacks a cycle")
    result = sum(value << offset for offset, value in enumerate(prefix))
    remaining = ROWS - len(prefix)
    period = len(repeating)
    block = sum(value << offset for offset, value in enumerate(repeating))
    quotient, remainder = divmod(remaining, period)
    if quotient:
        geometric = ((1 << (period * quotient)) - 1) // ((1 << period) - 1)
        result |= (block * geometric) << len(prefix)
    for offset in range(remainder):
        result |= repeating[offset] << (len(prefix) + quotient * period + offset)
    return result


def cycle_states(
    states: dict[int, base.PackedState], sequence: list[int]
) -> dict[int, int]:
    result = {node_id: 0 for node_id in states}
    for cycle, assignment in enumerate(sequence):
        marker = 1 << cycle
        for node_id, state in states.items():
            if (state.bits >> assignment) & 1:
                result[node_id] |= marker
    return result


def enumerate_phases() -> tuple[
    dict[int, PhaseRecipe], dict[str, object], dict[int, set[str]]
]:
    phases: dict[int, PhaseRecipe] = {}
    aliases: dict[int, set[str]] = {}
    width_rows = []
    for width in range(1, 4):
        choices = updates(width)
        machine_count = 0
        rail_count = 0
        decoded_count = 0
        for selected in product(choices, repeat=width):
            update_gate = sum(value.cost for value in selected)
            if update_gate > 3:
                continue
            machine_count += 1
            update_delay = max(value.delay for value in selected)
            path, preperiod = trajectory(width, selected)
            rail_values = [
                pack_eventual(
                    tuple((state >> bit) & 1 for state in path), preperiod
                )
                for bit in range(width)
            ]
            common = {
                "delays": width,
                "update_gate": update_gate,
                "update_delay": update_delay,
                "updates": tuple(value.expression for value in selected),
                "preperiod": preperiod,
                "period": len(path) - preperiod,
            }
            for bit, truth in enumerate(rail_values):
                rail_count += 1
                recipe = PhaseRecipe(
                    **common,
                    output=f"q{bit}",
                    decode_gate=0,
                    decode_delay=0,
                )
                alias = f"w{width}:{recipe.updates}:q{bit}"
                aliases.setdefault(truth, set()).add(alias)
                previous = phases.get(truth)
                if previous is None or recipe.key() < previous.key():
                    phases[truth] = recipe

            for left in range(width):
                for right in range(left + 1, width):
                    for op, (cost, delay, _function) in BIT_OPS.items():
                        decoded_count += 1
                        truth = PACKED_OPS[op](
                            rail_values[left], rail_values[right]
                        )
                        recipe = PhaseRecipe(
                            **common,
                            output=f"{op}(q{left},q{right})",
                            decode_gate=cost,
                            decode_delay=delay,
                        )
                        alias = f"w{width}:{recipe.updates}:{recipe.output}"
                        aliases.setdefault(truth, set()).add(alias)
                        previous = phases.get(truth)
                        if previous is None or recipe.key() < previous.key():
                            phases[truth] = recipe
        width_rows.append(
            {
                "delay_line_count": width,
                "update_function_count_per_rail": len(choices),
                "machines_with_update_gate_at_most_3": machine_count,
                "state_rail_candidates_before_semantic_dedup": rail_count,
                "decoded_candidates_before_semantic_dedup": decoded_count,
            }
        )
    summary = {
        "grammar": {
            "delay_line_count": [1, 2, 3],
            "initial_state": "all zero",
            "per_rail_updates": [
                "constant 0/1",
                "state wire",
                "NOT(state wire)",
                "one AND/OR/NAND/NOR/XOR/XNOR of two distinct state rails",
            ],
            "maximum_total_update_gate": 3,
            "one_gate_decodes_enumerated": True,
        },
        "widths": width_rows,
        "unique_full_sequence_phase_count": len(phases),
        "unique_state_rail_phase_count": sum(
            recipe.decode_gate == 0 for recipe in phases.values()
        ),
        "unique_decoded_phase_count": sum(
            recipe.decode_gate != 0 for recipe in phases.values()
        ),
    }
    return phases, summary, aliases


def target_names(
    nodes: dict[int, dict[str, object]], outputs: tuple[int, ...]
) -> dict[int, str]:
    output_labels = {
        node_id: f"S{offset}" if offset < 8 else "Cout"
        for offset, node_id in enumerate(outputs)
    }
    return {
        node_id: output_labels.get(node_id, base.state_name(node))
        for node_id, node in nodes.items()
    }


def ordinary_current_closure(
    current: dict[int, int], names: dict[int, str]
) -> dict[int, dict[str, object]]:
    closure: dict[int, dict[str, object]] = {}

    def remember(truth: int, row: dict[str, object]) -> None:
        previous = closure.get(truth)
        key = (int(row["gate"]), str(row))
        if previous is None or key < (int(previous["gate"]), str(previous)):
            closure[truth] = row

    for node_id, truth in current.items():
        remember(
            ~truth & MASK,
            {"kind": "NOT", "source": names[node_id], "source_id": node_id, "gate": 1},
        )
    ids = tuple(current)
    for left_offset, left_id in enumerate(ids):
        for right_id in ids[left_offset + 1 :]:
            for op in ("AND", "OR", "NAND", "NOR"):
                remember(
                    PACKED_OPS[op](current[left_id], current[right_id]),
                    {
                        "kind": op,
                        "left": names[left_id],
                        "left_id": left_id,
                        "right": names[right_id],
                        "right_id": right_id,
                        "gate": 1,
                    },
                )
    return closure


def search_matches(
    phases: dict[int, PhaseRecipe],
    nodes: dict[int, dict[str, object]],
    states: dict[int, base.PackedState],
    outputs: tuple[int, ...],
    current: dict[int, int],
) -> dict[str, object]:
    names = target_names(nodes, outputs)
    exact_targets: dict[int, list[int]] = {}
    for node_id, truth in current.items():
        exact_targets.setdefault(truth, []).append(node_id)
    direct = []
    for truth, recipe in phases.items():
        for node_id in exact_targets.get(truth, ()):
            direct.append(
                {
                    "target_id": node_id,
                    "target": names[node_id],
                    "inverted": False,
                    "phase": recipe.serialized(),
                }
            )
        for node_id in exact_targets.get(~truth & MASK, ()):
            direct.append(
                {
                    "target_id": node_id,
                    "target": names[node_id],
                    "inverted": True,
                    "phase": recipe.serialized(),
                }
            )

    current_closure = ordinary_current_closure(current, names)
    raw_matches = []
    dominated_matches = []
    for phase_truth, recipe in phases.items():
        if recipe.decode_gate or phase_truth in {0, MASK}:
            continue
        for current_id, current_truth in current.items():
            if states[current_id].arrival > 4:
                continue
            for op in ("AND", "OR", "NAND", "NOR"):
                result = PACKED_OPS[op](phase_truth, current_truth)
                for target_id in exact_targets.get(result, ()):
                    if current_id == target_id:
                        continue
                    row = {
                        "target_id": target_id,
                        "target": names[target_id],
                        "target_is_output": target_id in outputs,
                        "kind": op,
                        "current_source_id": current_id,
                        "current_source": names[current_id],
                        "current_source_arrival": states[current_id].arrival,
                        "phase": recipe.serialized(),
                        "total_incremental_gate": recipe.gate + 1,
                        "output_path_delay": 5,
                    }
                    simpler = current_closure.get(result)
                    if simpler is not None:
                        row["dominated_by_current_one_gate"] = simpler
                        dominated_matches.append(row)
                    else:
                        raw_matches.append(row)

    # A stronger one-gate test lets the other input be any current function.
    # The fixed cofactor of AND/OR/NAND/NOR must still agree where phase alone
    # determines the result.  This proves impossibility without synthesizing F.
    cofactor_rows = []
    for target_id in outputs:
        target = current[target_id]
        for phase_truth, recipe in phases.items():
            if recipe.decode_gate or phase_truth in {0, MASK}:
                continue
            witnesses = {
                "AND": (target & (~phase_truth & MASK)).bit_count(),
                "OR": (phase_truth & (~target & MASK)).bit_count(),
                "NAND": ((~target & MASK) & (~phase_truth & MASK)).bit_count(),
                "NOR": (target & phase_truth).bit_count(),
            }
            feasible = [op for op, mismatches in witnesses.items() if not mismatches]
            if feasible:
                cofactor_rows.append(
                    {
                        "target_id": target_id,
                        "target": names[target_id],
                        "phase": recipe.serialized(),
                        "feasible_outer_gates": feasible,
                        "fixed_cofactor_mismatch_counts": witnesses,
                    }
                )

    return {
        "direct_live_target_match_count": len(direct),
        "direct_output_match_count": sum(
            row["target_id"] in outputs for row in direct
        ),
        "direct_matches": direct,
        "state_phase_plus_existing_current_one_gate_raw_match_count": (
            len(raw_matches) + len(dominated_matches)
        ),
        "state_phase_plus_existing_current_one_gate_undominated_match_count": len(
            raw_matches
        ),
        "state_phase_plus_existing_current_one_gate_undominated_output_count": sum(
            row["target_is_output"] for row in raw_matches
        ),
        "undominated_matches": raw_matches,
        "dominated_match_count": len(dominated_matches),
        "dominated_matches": dominated_matches,
        "arbitrary_current_residual_outer_gate_feasible_record_count": len(
            cofactor_rows
        ),
        "arbitrary_current_residual_outer_gate_feasible_unique_outputs": sorted(
            {row["target"] for row in cofactor_rows}
        ),
        "arbitrary_current_residual_outer_gate_feasible_outputs": cofactor_rows,
    }


def bus2_output_search(
    phases: dict[int, PhaseRecipe],
    nodes: dict[int, dict[str, object]],
    states: dict[int, base.PackedState],
    outputs: tuple[int, ...],
    current: dict[int, int],
) -> dict[str, object]:
    names = target_names(nodes, outputs)
    useful_phase_values = {
        truth: recipe
        for truth, recipe in phases.items()
        if recipe.decode_gate == 0 and recipe.delays == 1 and truth not in {0, MASK}
    }
    sources: dict[int, dict[str, object]] = {}
    for node_id, truth in current.items():
        if states[node_id].arrival <= 4:
            sources.setdefault(
                truth,
                {"kind": "current", "name": names[node_id], "node_id": node_id},
            )
    for truth, recipe in useful_phase_values.items():
        sources.setdefault(
            truth,
            {"kind": "phase", "name": recipe.output, "phase": recipe.serialized()},
        )
    sources.setdefault(0, {"kind": "constant", "name": "CONST0"})
    sources.setdefault(MASK, {"kind": "constant", "name": "CONST1"})

    source_rows = tuple((truth, row) for truth, row in sources.items())
    drivers: dict[tuple[int, int, int], dict[str, object]] = {}
    for enable, enable_row in source_rows:
        for data, data_row in source_rows:
            key = (enable & data, enable & (~data & MASK), enable)
            drivers.setdefault(
                key,
                {"enable": enable_row, "data": data_row},
            )

    hits = []
    for target_id in outputs:
        target = current[target_id]
        compatible = []
        for (ones, zeros, driven), recipe in drivers.items():
            if ones & (~target & MASK) or zeros & target:
                continue
            compatible.append((ones, zeros, driven, recipe))
        for left_offset, left in enumerate(compatible):
            for right in compatible[left_offset:]:
                if (left[2] | right[2]) != MASK or (left[0] | right[0]) != target:
                    continue
                uses_phase = any(
                    endpoint["kind"] == "phase"
                    for driver in (left[3], right[3])
                    for endpoint in (driver["enable"], driver["data"])
                )
                if not uses_phase:
                    continue
                target_reused = any(
                    endpoint.get("node_id") == target_id
                    for driver in (left[3], right[3])
                    for endpoint in (driver["enable"], driver["data"])
                )
                hits.append(
                    {
                        "target_id": target_id,
                        "target": names[target_id],
                        "left_driver": left[3],
                        "right_driver": right[3],
                        "target_reused_as_bus_pin": target_reused,
                    }
                )
    return {
        "source_count_after_truth_dedup": len(sources),
        "driver_count_after_truth_dedup": len(drivers),
        "phase_using_bus2_output_match_count": len(hits),
        "phase_using_bus2_nonrecursive_output_match_count": sum(
            not row["target_reused_as_bus_pin"] for row in hits
        ),
        "matches": hits,
    }


def full_sequence_phase_inventory(
    phases: dict[int, PhaseRecipe], aliases: dict[int, set[str]]
) -> list[dict[str, object]]:
    rows = []
    for truth, recipe in sorted(phases.items(), key=lambda item: item[1].key()):
        packed = truth.to_bytes(ROWS // 8, "little")
        rows.append(
            {
                "sequence_sha256": sha256(packed).hexdigest(),
                "one_count": truth.bit_count(),
                "minimum_recipe": recipe.serialized(),
                "equivalent_recipe_count": len(aliases[truth]),
            }
        )
    return rows


def main() -> int:
    sequence = [base.live_xorshift(cycle) for cycle in range(ROWS)]
    if len(set(sequence)) != ROWS:
        raise RuntimeError("live sequence ceased to be bijective")
    nodes, states, outputs, baseline_semantic = base.evaluate_dag()
    current = cycle_states(states, sequence)
    phases, enumeration, aliases = enumerate_phases()
    matches = search_matches(phases, nodes, states, outputs, current)
    bus2 = bus2_output_search(phases, nodes, states, outputs, current)

    parity = sum((cycle & 1) << cycle for cycle in range(ROWS))
    parity_recipe = phases.get(parity)
    if parity_recipe is None:
        raise RuntimeError("NOT-feedback parity phase was not enumerated")
    parity_quadrants = []
    for offset, node_id in enumerate(outputs):
        target = current[node_id]
        parity_quadrants.append(
            {
                "target": f"S{offset}" if offset < 8 else "Cout",
                "phase0_target0": ((~parity & MASK) & (~target & MASK)).bit_count(),
                "phase0_target1": ((~parity & MASK) & target).bit_count(),
                "phase1_target0": (parity & (~target & MASK)).bit_count(),
                "phase1_target1": (parity & target).bit_count(),
            }
        )
    if any(
        set(row.values()) != {row["target"], 32768}
        for row in parity_quadrants
    ):
        raise RuntimeError("parity/output quadrant regression changed")

    payload = {
        "schema": "tc-byte-adder-autonomous-delayline-phase-audit-v1",
        "status": "complete",
        "test_si_sha256": base.digest(base.TEST_SI),
        "baseline_dag_sha256": base.digest(base.BASELINE_DAG),
        "cycles": ROWS,
        "baseline_semantic": baseline_semantic,
        "enumeration": enumeration,
        "phase_inventory": full_sequence_phase_inventory(phases, aliases),
        "matches": matches,
        "bus2_output_search": bus2,
        "not_feedback_parity": {
            "equation": "q[0]=0; q[t+1]=NOT(q[t]); therefore q[t]=t mod 2",
            "recipe": parity_recipe.serialized(),
            "output_quadrants": parity_quadrants,
            "outer_one_gate_with_arbitrary_current_residual_possible": False,
        },
        "timing_scope": {
            "one_delay_not_feedback": (
                "5: Delay Line 4 plus NOT feedback 1, matching the archived RNG "
                "phase-control accounting"
            ),
            "one_delay_post_ordinary_gate": 5,
            "multi_delay_feedback_timing": "UNKNOWN",
            "reason": (
                "No multi-delay phase produced an undominated graft; a native "
                "feedback-SCC score replay was not needed to accept a candidate."
            ),
        },
        "conclusions": {
            "unique_full_sequence_phases": enumeration[
                "unique_full_sequence_phase_count"
            ],
            "direct_live_target_matches": matches["direct_live_target_match_count"],
            "direct_output_matches": matches["direct_output_match_count"],
            "undominated_phase_plus_one_gate_live_target_matches": matches[
                "state_phase_plus_existing_current_one_gate_undominated_match_count"
            ],
            "undominated_phase_plus_one_gate_output_matches": matches[
                "state_phase_plus_existing_current_one_gate_undominated_output_count"
            ],
            "not_feedback_parity_outer_gate_arbitrary_residual_output_matches": 0,
            "all_phase_outer_gate_arbitrary_residual_feasible_records": matches[
                "arbitrary_current_residual_outer_gate_feasible_record_count"
            ],
            "all_phase_outer_gate_arbitrary_residual_feasible_unique_outputs": len(
                matches[
                    "arbitrary_current_residual_outer_gate_feasible_unique_outputs"
                ]
            ),
            "phase_bus2_nonrecursive_output_matches": bus2[
                "phase_using_bus2_nonrecursive_output_match_count"
            ],
        },
    }
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode(
        "utf-8"
    )
    OUTPUT.write_bytes(encoded)
    print(
        json.dumps(
            {
                "output": str(OUTPUT),
                "sha256": sha256(encoded).hexdigest(),
                "conclusions": payload["conclusions"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
