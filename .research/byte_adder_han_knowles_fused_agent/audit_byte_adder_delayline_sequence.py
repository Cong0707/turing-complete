"""Audit fixed-sequence Delay Line opportunities for the live Byte Adder.

This script is deliberately independent of the game save.  It reads the
currently installed ``test.si`` and the reviewed 80/7 Factory DAG, then writes
one JSON certificate beside this file.  In particular, the xorshift is
evaluated exactly as the script's unbounded ``Int`` operations: there is no
17-bit mask between the three XOR/shift statements.

The audit treats the final source cycles of a d-cycle future computation as
don't-cares.  Those values are captured only after the test has already used
the last observable delayed output.  The first d outputs are instead supplied
by the independently configurable ``init_data`` bits of the Delay Line chain.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Callable, Iterable


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TEST_SI = Path(
    r"D:\Game\Steam\steamapps\common\Turing Complete\campaign\byte_adder\test.si"
)
BASELINE_DAG = ROOT / ".research" / "byte_adder_root" / (
    "byte-adder-hybrid-phasefold-g80-d7.json"
)
TIMING_EVIDENCE = ROOT / "examples" / "rng" / "research" / "archive" / (
    "rng_control_simplify"
) / "native_score_audit" / "evidence.recheck.json"
TIMING_EXPLANATION = TIMING_EVIDENCE.with_name("RESULT.md")
OUTPUT = HERE / "byte_adder_delayline_sequence_audit.json"

WIDTH = 17
ROWS = 1 << WIDTH
VALUE_MASK = ROWS - 1
TRUTH_MASK = (1 << ROWS) - 1
MAX_MEANINGFUL_DELAY = 20  # floor(102 gate / 5 gate per one-bit Delay Line)


@dataclass(frozen=True)
class PackedState:
    bits: int
    driven: int
    conflict: int
    arrival: int


ORDINARY: dict[str, tuple[int, int, Callable[[int, int], int]]] = {
    "AND": (1, 1, lambda left, right: left & right),
    "OR": (1, 1, lambda left, right: left | right),
    "NAND": (1, 1, lambda left, right: ~(left & right) & TRUTH_MASK),
    "NOR": (1, 1, lambda left, right: ~(left | right) & TRUTH_MASK),
    "XOR": (3, 2, lambda left, right: left ^ right),
    "XNOR": (3, 2, lambda left, right: ~(left ^ right) & TRUTH_MASK),
}


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def live_xorshift(cycle: int) -> int:
    """Exactly reproduce the installed script before extracting low 17 bits."""

    value = cycle
    value ^= value << 6
    value ^= value >> 11
    value ^= value << 9
    return value & VALUE_MASK


def incorrectly_masked_xorshift(cycle: int) -> int:
    """The tempting but incorrect finite-width interpretation, for evidence."""

    value = cycle & VALUE_MASK
    value ^= (value << 6) & VALUE_MASK
    value ^= value >> 11
    value ^= (value << 9) & VALUE_MASK
    return value & VALUE_MASK


def parse_test_contract() -> dict[str, object]:
    text = TEST_SI.read_text(encoding="utf-8")
    required = {
        "cycle_source": r"var\s+x\s*=\s*cycle",
        "shift_left_6": r"x\s*\^=\s*x\s*<<\s*6",
        "shift_right_11": r"x\s*\^=\s*x\s*>>\s*11",
        "shift_left_9": r"x\s*\^=\s*x\s*<<\s*9",
        "a_extract": r"a:\s*U8\s*\(x\s*&\s*0xff\)",
        "b_extract": r"b:\s*U8\s*\(\(x\s*>>\s*8\)\s*&\s*0xff\)",
        "cin_extract": r"carry_in:\s*U1\s*\(x\s*>>\s*16\)\s*&\s*1",
        "sum": r"var\s+sum\s*=\s*Int\s+input\.a\s*\+\s*Int\s+input\.b\s*\+\s*Int\s+input\.carry_in",
        "last_cycle": r"cycle\s*==\s*0x1ffff",
    }
    matches = {
        name: bool(re.search(pattern, text, flags=re.MULTILINE))
        for name, pattern in required.items()
    }
    if not all(matches.values()):
        raise RuntimeError(f"installed test.si contract changed: {matches}")
    return {
        "path": str(TEST_SI),
        "sha256": digest(TEST_SI),
        "bytes": TEST_SI.stat().st_size,
        "required_source_patterns": matches,
        "first_cycle": 0,
        "last_cycle": VALUE_MASK,
        "cycles": ROWS,
    }


def variable(bit: int) -> int:
    result = 0
    block = 1 << bit
    ones = ((1 << block) - 1) << block
    for start in range(0, ROWS, 2 * block):
        result |= ones << start
    return result


def expected_output(value: int) -> int:
    return (value & 0xFF) + ((value >> 8) & 0xFF) + ((value >> 16) & 1)


def evaluate_dag() -> tuple[
    dict[int, dict[str, object]],
    dict[int, PackedState],
    tuple[int, ...],
    dict[str, object],
]:
    payload = json.loads(BASELINE_DAG.read_text(encoding="utf-8"))
    raw_nodes = tuple(payload["factory_dag"]["nodes"])
    outputs = tuple(int(value) for value in payload["factory_dag"]["outputs"])
    nodes: dict[int, dict[str, object]] = {}
    states: dict[int, PackedState] = {}
    input_bits = {
        **{f"a{bit}": bit for bit in range(8)},
        **{f"b{bit}": 8 + bit for bit in range(8)},
        "cin": 16,
    }
    input_labels: set[str] = set()

    for raw in raw_nodes:
        node = dict(raw)
        node_id = int(node["id"])
        op = str(node["op"])
        argument_ids = tuple(int(value) for value in node.get("args", ()))
        if node_id in states or any(value not in states for value in argument_ids):
            raise RuntimeError(f"DAG is not topological at node {node_id}")
        arguments = tuple(states[value] for value in argument_ids)

        if op == "INPUT":
            label = str(node["label"])
            if label not in input_bits or label in input_labels or arguments:
                raise RuntimeError(f"invalid input node {node_id}: {label!r}")
            input_labels.add(label)
            state = PackedState(variable(input_bits[label]), TRUTH_MASK, 0, 0)
            expected_cost = expected_step = 0
        elif op == "CONST":
            label = str(node["label"])
            if label not in {"0", "1"} or arguments:
                raise RuntimeError(f"invalid constant node {node_id}")
            state = PackedState(TRUTH_MASK if label == "1" else 0, TRUTH_MASK, 0, 0)
            expected_cost = expected_step = 0
        elif op == "BUS":
            if not arguments or len(arguments) % 2:
                raise RuntimeError(f"incomplete BUS node {node_id}")
            ones = zeros = driven = conflict = 0
            for offset in range(0, len(arguments), 2):
                enable, data = arguments[offset : offset + 2]
                active = enable.bits
                ones |= active & data.bits
                zeros |= active & (~data.bits & TRUTH_MASK)
                driven |= active
                conflict |= enable.conflict | data.conflict
            conflict |= ones & zeros
            expected_cost = len(arguments)
            expected_step = 1
            state = PackedState(
                ones & TRUTH_MASK,
                driven & TRUTH_MASK,
                conflict & TRUTH_MASK,
                max(value.arrival for value in arguments) + 1,
            )
        elif op == "NOT":
            if len(arguments) != 1:
                raise RuntimeError(f"invalid NOT node {node_id}")
            source = arguments[0]
            state = PackedState(
                ~source.bits & TRUTH_MASK,
                TRUTH_MASK,
                source.conflict,
                source.arrival + 1,
            )
            expected_cost = expected_step = 1
        elif op in ORDINARY:
            if len(arguments) != 2:
                raise RuntimeError(f"invalid {op} node {node_id}")
            cost, step, function = ORDINARY[op]
            conflict = arguments[0].conflict | arguments[1].conflict
            state = PackedState(
                function(arguments[0].bits, arguments[1].bits),
                TRUTH_MASK,
                conflict,
                max(value.arrival for value in arguments) + step,
            )
            expected_cost, expected_step = cost, step
        else:
            raise RuntimeError(f"unsupported DAG operation {op!r}")

        annotations = (
            int(node["cost"]),
            int(node["step_delay"]),
            int(node["arrival"]),
            bool(node["may_z"]),
        )
        expected = (expected_cost, expected_step, state.arrival, op == "BUS")
        if annotations != expected:
            raise RuntimeError(
                f"node {node_id} annotations differ: {annotations} != {expected}"
            )
        nodes[node_id] = node
        states[node_id] = state

    if input_labels != set(input_bits):
        raise RuntimeError(f"input contract differs: {input_labels!r}")

    mismatch = [0] * 9
    for assignment in range(ROWS):
        target = expected_output(assignment)
        for bit, node_id in enumerate(outputs):
            mismatch[bit] += ((states[node_id].bits >> assignment) & 1) != (
                (target >> bit) & 1
            )
    conflict_union = 0
    for state in states.values():
        conflict_union |= state.conflict
    z_counts = [
        ((~states[node_id].driven) & TRUTH_MASK).bit_count() for node_id in outputs
    ]
    if any(mismatch) or conflict_union or any(z_counts):
        raise RuntimeError(
            f"baseline semantic replay failed: mismatch={mismatch}, "
            f"conflict={conflict_union.bit_count()}, z={z_counts}"
        )
    semantic = {
        "mismatch_count_by_output": mismatch,
        "conflict_assignment_count": conflict_union.bit_count(),
        "z_assignment_count_by_output": z_counts,
        "output_arrivals": [states[value].arrival for value in outputs],
        "gate": sum(int(node["cost"]) for node in nodes.values()),
        "delay": max(states[value].arrival for value in outputs),
    }
    return nodes, states, outputs, semantic


def shifted_target_truth(
    target: Callable[[int], int], bit: int, sequence: list[int], delay: int
) -> tuple[int, int]:
    """Pack F(x[t+d]) by current assignment x[t], omitting final d sources."""

    truth = 0
    care = 0
    for cycle in range(ROWS - delay):
        assignment = sequence[cycle]
        marker = 1 << assignment
        care |= marker
        if (target(sequence[cycle + delay]) >> bit) & 1:
            truth |= marker
    return truth, care


def shifted_node_truth(
    bits: int, sequence: list[int], delay: int = 1
) -> tuple[int, int]:
    truth = 0
    care = 0
    for cycle in range(ROWS - delay):
        assignment = sequence[cycle]
        marker = 1 << assignment
        care |= marker
        if (bits >> sequence[cycle + delay]) & 1:
            truth |= marker
    return truth, care


def delayed_node_truth(
    bits: int, sequence: list[int], init: int
) -> int:
    result = (1 << sequence[0]) if init else 0
    for cycle in range(1, ROWS):
        if (bits >> sequence[cycle - 1]) & 1:
            result |= 1 << sequence[cycle]
    return result


def affine_solution(
    truth: int, care: int, sequence: list[int]
) -> dict[str, object] | None:
    """Return the unique affine form when 0 and all basis rows are cared for."""

    basis_points = (0,) + tuple(1 << bit for bit in range(WIDTH))
    if any(not ((care >> point) & 1) for point in basis_points):
        raise RuntimeError("affine fast path lost a basis care point")
    constant = truth & 1
    coefficients = 0
    for bit in range(WIDTH):
        value = (truth >> (1 << bit)) & 1
        if value ^ constant:
            coefficients |= 1 << bit
    for assignment in sequence:
        if not ((care >> assignment) & 1):
            continue
        actual = (truth >> assignment) & 1
        expected = constant ^ ((assignment & coefficients).bit_count() & 1)
        if actual != expected:
            return None
    return {
        "constant": int(constant),
        "coefficient_mask": coefficients,
        "terms": [bit for bit in range(WIDTH) if (coefficients >> bit) & 1],
    }


def anf_masks() -> tuple[tuple[int, ...], tuple[int, ...]]:
    high_masks = []
    for bit in range(WIDTH):
        step = 1 << bit
        block = ((1 << step) - 1) << step
        mask = 0
        for start in range(0, ROWS, 2 * step):
            mask |= block << start
        high_masks.append(mask)
    weight_masks = [0] * (WIDTH + 1)
    for assignment in range(ROWS):
        weight_masks[assignment.bit_count()] |= 1 << assignment
    return tuple(high_masks), tuple(weight_masks)


def anf_stats(
    truth: int, high_masks: tuple[int, ...], weight_masks: tuple[int, ...]
) -> dict[str, int]:
    coefficients = truth
    for bit, high in enumerate(high_masks):
        coefficients ^= (coefficients << (1 << bit)) & high
    degree = max(
        value for value in range(WIDTH + 1) if coefficients & weight_masks[value]
    )
    return {"degree": degree, "term_count": coefficients.bit_count()}


def state_name(node: dict[str, object]) -> str:
    label = str(node.get("label", ""))
    return label if label else f"n{int(node['id'])}"


def remember_best(
    table: dict[int, list[dict[str, object]]],
    truth: int,
    row: dict[str, object],
) -> None:
    bucket = table.setdefault(truth, [])
    bucket.append(row)


def enumerate_future_matches(
    nodes: dict[int, dict[str, object]],
    states: dict[int, PackedState],
    outputs: tuple[int, ...],
    sequence: list[int],
) -> dict[str, object]:
    care = TRUTH_MASK ^ (1 << sequence[-1])
    names = {node_id: state_name(node) for node_id, node in nodes.items()}
    target_ids = tuple(nodes)
    future = {
        node_id: shifted_node_truth(states[node_id].bits, sequence)[0]
        for node_id in target_ids
    }

    direct: dict[int, list[dict[str, object]]] = {}
    for source_id, state in states.items():
        remember_best(
            direct,
            state.bits & care,
            {
                "kind": "DIRECT",
                "source": names[source_id],
                "source_id": source_id,
                "arrival_before_delay": state.arrival,
                "arrival_after_delay": state.arrival + 4,
                "incremental_gate": 5,
            },
        )
        remember_best(
            direct,
            (~state.bits) & care,
            {
                "kind": "NOT",
                "source": names[source_id],
                "source_id": source_id,
                "arrival_before_delay": state.arrival + 1,
                "arrival_after_delay": state.arrival + 5,
                "incremental_gate": 6,
            },
        )

    one_gate: dict[int, list[dict[str, object]]] = {}
    source_ids = tuple(states)
    for source_id, state in states.items():
        remember_best(
            one_gate,
            (~state.bits) & care,
            {
                "kind": "NOT",
                "left_id": source_id,
                "left": names[source_id],
                "arrival_before_delay": state.arrival + 1,
                "arrival_after_delay": state.arrival + 5,
                "logic_gate": 1,
            },
        )
    for left_offset, left_id in enumerate(source_ids):
        left = states[left_id]
        for right_id in source_ids[left_offset + 1 :]:
            right = states[right_id]
            for op, (cost, step, function) in ORDINARY.items():
                result = function(left.bits, right.bits) & care
                remember_best(
                    one_gate,
                    result,
                    {
                        "kind": op,
                        "left_id": left_id,
                        "left": names[left_id],
                        "right_id": right_id,
                        "right": names[right_id],
                        "arrival_before_delay": max(left.arrival, right.arrival)
                        + step,
                        "arrival_after_delay": max(left.arrival, right.arrival)
                        + step
                        + 4,
                        "logic_gate": cost,
                    },
                )

    # A one-step resolved BUS can be more expressive than an ordinary gate.
    # Only arrival-zero sources can precede a Delay Line and remain within D5.
    zero_sources: list[tuple[str, int, int]] = [
        (names[node_id], node_id, state.bits)
        for node_id, state in states.items()
        if state.arrival == 0
    ]
    zero_sources.extend(
        (("CONST0", -1, 0), ("CONST1", -2, TRUTH_MASK))
    )
    drivers: list[tuple[str, int, int, int, int]] = []
    for enable_name, enable_id, enable in zero_sources:
        for data_name, data_id, data in zero_sources:
            drivers.append(
                (
                    f"SW({enable_name},{data_name})",
                    enable_id,
                    data_id,
                    enable & data,
                    enable & (~data & TRUTH_MASK),
                )
            )
    bus_matches: dict[int, list[dict[str, object]]] = {}
    for left_offset, left in enumerate(drivers):
        for right in drivers[left_offset:]:
            conflict = (left[3] & right[4]) | (left[4] & right[3])
            if conflict & care:
                continue
            result = (left[3] | right[3]) & care
            remember_best(
                bus_matches,
                result,
                {
                    "kind": "BUS2",
                    "left": left[0],
                    "right": right[0],
                    "arrival_before_delay": 1,
                    "arrival_after_delay": 5,
                    "logic_gate": 4,
                },
            )

    matched_rows = []
    for target_id in target_ids:
        key = future[target_id] & care
        rows = direct.get(key, []) + one_gate.get(key, []) + bus_matches.get(key, [])
        if rows:
            matched_rows.append(
                {
                    "target_id": target_id,
                    "target": names[target_id],
                    "target_is_output": target_id in outputs,
                    "recipes": sorted(
                        rows,
                        key=lambda row: (
                            int(row["arrival_after_delay"]),
                            int(row.get("logic_gate", row.get("incremental_gate", 0))),
                            json.dumps(row, sort_keys=True),
                        ),
                    ),
                }
            )

    # Exhaust every one-gate post-Delay graft over current live sources.  Both
    # init values are considered independently for every delayed rail.
    exact_targets: dict[int, list[int]] = {}
    for target_id, state in states.items():
        exact_targets.setdefault(state.bits, []).append(target_id)
    delayed = {
        (source_id, init): delayed_node_truth(state.bits, sequence, init)
        for source_id, state in states.items()
        for init in (0, 1)
    }
    post_matches: list[dict[str, object]] = []
    for (source_id, init), history in delayed.items():
        for current_id, current in states.items():
            for op in ("AND", "OR", "NAND", "NOR"):
                cost, step, function = ORDINARY[op]
                result = function(history, current.bits)
                for target_id in exact_targets.get(result, ()):
                    post_matches.append(
                        {
                            "target_id": target_id,
                            "target": names[target_id],
                            "kind": op,
                            "delayed_source_id": source_id,
                            "delayed_source": names[source_id],
                            "init_data": init,
                            "current_source_id": current_id,
                            "current_source": names[current_id],
                            "arrival": max(
                                states[source_id].arrival + 4,
                                current.arrival,
                            )
                            + step,
                            "incremental_gate": 5 + cost,
                        }
                    )

    output_names = [f"S{bit}" for bit in range(8)] + ["Cout"]
    return {
        "delay_cycles": 1,
        "care_rows": care.bit_count(),
        "dont_care_source_cycles": [ROWS - 1],
        "dont_care_current_assignments": [sequence[-1]],
        "target_live_node_count": len(target_ids),
        "target_output_ids": list(outputs),
        "target_output_names": output_names,
        "current_direct_function_count": len(direct),
        "current_one_gate_function_count": len(one_gate),
        "current_bus2_function_count": len(bus_matches),
        "matched_target_count": len(matched_rows),
        "matched_output_count": sum(
            bool(row["target_is_output"]) for row in matched_rows
        ),
        "matches": matched_rows,
        "post_delay_one_gate_match_count": len(post_matches),
        "post_delay_one_gate_matches": post_matches,
    }


def future_affine_audit(sequence: list[int]) -> list[dict[str, object]]:
    rows = []
    for delay in range(1, MAX_MEANINGFUL_DELAY + 1):
        bit_rows = []
        for bit in range(WIDTH):
            truth, care = shifted_target_truth(lambda value: value, bit, sequence, delay)
            solution = affine_solution(truth, care, sequence)
            bit_rows.append(
                {
                    "name": (
                        f"A{bit}" if bit < 8 else f"B{bit - 8}" if bit < 16 else "Cin"
                    ),
                    "affine": solution is not None,
                    "form": solution,
                }
            )
        output_rows = []
        for bit in range(9):
            truth, care = shifted_target_truth(expected_output, bit, sequence, delay)
            solution = affine_solution(truth, care, sequence)
            output_rows.append(
                {
                    "name": f"S{bit}" if bit < 8 else "Cout",
                    "affine": solution is not None,
                    "form": solution,
                }
            )
        rows.append(
            {
                "delay_cycles": delay,
                "care_rows": ROWS - delay,
                "dont_care_source_cycles": list(range(ROWS - delay, ROWS)),
                "future_input_bits": bit_rows,
                "future_output_bits": output_rows,
                "affine_future_input_count": sum(row["affine"] for row in bit_rows),
                "affine_future_output_count": sum(row["affine"] for row in output_rows),
            }
        )
    return rows


def future_node_anf_audit(
    nodes: dict[int, dict[str, object]],
    states: dict[int, PackedState],
    outputs: tuple[int, ...],
    sequence: list[int],
) -> dict[str, object]:
    high_masks, weight_masks = anf_masks()
    missing = sequence[-1]
    flip = 1 << missing
    rows = []
    for node_id, state in states.items():
        truth, care = shifted_node_truth(state.bits, sequence)
        if care != (TRUTH_MASK ^ flip):
            raise RuntimeError("unexpected d1 care mask")
        zero_completion = anf_stats(truth, high_masks, weight_masks)
        one_completion = anf_stats(truth ^ flip, high_masks, weight_masks)
        rows.append(
            {
                "target_id": node_id,
                "target": state_name(nodes[node_id]),
                "target_is_output": node_id in outputs,
                "target_original_arrival": state.arrival,
                "missing_assignment_value_zero": zero_completion,
                "missing_assignment_value_one": one_completion,
                "minimum_completion_degree": min(
                    zero_completion["degree"], one_completion["degree"]
                ),
            }
        )
    return {
        "delay_cycles": 1,
        "missing_source_cycle": ROWS - 1,
        "missing_current_assignment": missing,
        "completion_count": 2,
        "minimum_degree_across_all_live_targets": min(
            row["minimum_completion_degree"] for row in rows
        ),
        "maximum_degree_across_all_live_targets": max(
            row["minimum_completion_degree"] for row in rows
        ),
        "nodes": rows,
    }


def replay_delay_chains(sequence: list[int]) -> list[dict[str, object]]:
    targets = [expected_output(value) for value in sequence]
    rows = []
    for delay in range(1, MAX_MEANINGFUL_DELAY + 1):
        # Stage 0 is nearest the combinational input; stage d-1 drives output.
        state = [targets[delay - 1 - stage] for stage in range(delay)]
        mismatches = 0
        first_mismatch = None
        for cycle in range(ROWS):
            observed = state[-1]
            if observed != targets[cycle]:
                mismatches += 1
                if first_mismatch is None:
                    first_mismatch = cycle
            future_cycle = cycle + delay
            captured = targets[future_cycle] if future_cycle < ROWS else 0
            state = [captured] + state[:-1]
        rows.append(
            {
                "delay_cycles": delay,
                "rail_gate": 5 * delay,
                "rail_delay": 4 * delay,
                "source_care_rows": ROWS - delay,
                "initial_stage_values_input_to_output": [
                    targets[delay - 1 - stage] for stage in range(delay)
                ],
                "mismatch_count": mismatches,
                "first_mismatch_cycle": first_mismatch,
            }
        )
    return rows


def timing_evidence() -> dict[str, object]:
    result = {
        "delay_line_kind": 13,
        "delay_line_gate": 5,
        "delay_line_component_delay": 4,
        "native_recurrence": (
            "arrival(component outputs) = max(arrival(all component inputs)) "
            "+ component_delay"
        ),
        "delay_line_is_timing_cut": False,
        "single_delay_arrival": "input_logic_arrival + 4",
        "chain_arrival": "input_logic_arrival + 4 * number_of_delay_lines",
        "d5_consequence": (
            "For one Delay Line, logic before plus logic after it may contribute "
            "at most one ordinary delay unit in total."
        ),
    }
    evidence = []
    for path in (TIMING_EVIDENCE, TIMING_EXPLANATION):
        if path.is_file():
            evidence.append(
                {
                    "path": str(path),
                    "sha256": digest(path),
                    "bytes": path.stat().st_size,
                }
            )
    result["evidence"] = evidence
    return result


def main() -> int:
    contract = parse_test_contract()
    sequence = [live_xorshift(cycle) for cycle in range(ROWS)]
    if len(set(sequence)) != ROWS:
        raise RuntimeError("live low-17-bit xorshift transform is not bijective")
    inverse = [0] * ROWS
    for cycle, value in enumerate(sequence):
        inverse[value] = cycle
    if any(sequence[inverse[value]] != value for value in range(ROWS)):
        raise RuntimeError("inverse permutation replay failed")

    masked_sequence = [incorrectly_masked_xorshift(cycle) for cycle in range(ROWS)]
    differing = [
        cycle
        for cycle, (live, masked) in enumerate(zip(sequence, masked_sequence, strict=True))
        if live != masked
    ]
    if len(differing) != 129024 or differing[0] != 2048:
        raise RuntimeError("expected live-vs-masked regression witness changed")

    nodes, states, outputs, baseline_semantic = evaluate_dag()
    future_matches = enumerate_future_matches(nodes, states, outputs, sequence)
    affine_rows = future_affine_audit(sequence)
    anf = future_node_anf_audit(nodes, states, outputs, sequence)
    chain_replays = replay_delay_chains(sequence)
    if any(row["mismatch_count"] for row in chain_replays):
        raise RuntimeError("Delay Line chain replay failed")

    payload = {
        "schema": "tc-byte-adder-live-delayline-sequence-audit-v1",
        "status": "complete",
        "test_contract": contract,
        "sequence": {
            "width": WIDTH,
            "cycles": ROWS,
            "bijective": True,
            "cycle_zero_input": sequence[0],
            "cycle_zero_expected_output": expected_output(sequence[0]),
            "last_cycle_input": sequence[-1],
            "permutation_u32le_sha256": sha256(
                b"".join(value.to_bytes(4, "little") for value in sequence)
            ).hexdigest(),
            "live_unmasked_operations": [
                "x = cycle",
                "x ^= x << 6",
                "x ^= x >> 11",
                "x ^= x << 9",
                "x &= 0x1ffff only when extracting the 17 input bits",
            ],
            "incorrect_intermediate_mask_regression": {
                "different_cycle_count": len(differing),
                "first_different_cycle": differing[0],
                "first_live_value": sequence[differing[0]],
                "first_masked_value": masked_sequence[differing[0]],
                "first_xor_difference": sequence[differing[0]]
                ^ masked_sequence[differing[0]],
                "masked_sequence_also_bijective": len(set(masked_sequence)) == ROWS,
            },
        },
        "baseline": {
            "path": str(BASELINE_DAG),
            "sha256": digest(BASELINE_DAG),
            "live_node_count": len(nodes),
            "outputs": list(outputs),
            "semantic_replay": baseline_semantic,
        },
        "timing": timing_evidence(),
        "future_d1_live_node_search": future_matches,
        "future_d1_live_node_anf": anf,
        "future_d1_to_d20_affine": affine_rows,
        "delay_chain_full_sequence_replay": chain_replays,
        "conclusions": {
            "full_sequence_cycles_checked": ROWS,
            "future_relation_final_source_is_dont_care": True,
            "d1_future_live_node_direct_or_one_gate_or_bus2_match_count": (
                future_matches["matched_target_count"]
            ),
            "d1_future_output_direct_or_one_gate_or_bus2_match_count": (
                future_matches["matched_output_count"]
            ),
            "d1_post_delay_one_gate_live_node_match_count": future_matches[
                "post_delay_one_gate_match_count"
            ],
            "minimum_d1_future_live_node_anf_degree": anf[
                "minimum_degree_across_all_live_targets"
            ],
            "affine_future_input_forms_d1_to_d20": sum(
                row["affine_future_input_count"] for row in affine_rows
            ),
            "affine_future_output_forms_d1_to_d20": sum(
                row["affine_future_output_count"] for row in affine_rows
            ),
            "shallow_named_byproduct_retime_found": bool(
                future_matches["matched_target_count"]
                or future_matches["post_delay_one_gate_match_count"]
            ),
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
