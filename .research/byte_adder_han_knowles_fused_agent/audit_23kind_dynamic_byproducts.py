"""Audit sequence-domain byproducts of every pre-Byte-Adder component kind.

The static 23-kind component catalog is treated as the runtime contract.  This
script extends it over the exact 131072-cycle Byte Adder protocol and searches
a deliberately finite, replayable dynamic grammar:

* one-tick history of every live 80/7 data-plane node;
* all previously enumerated 1--3 Delay-Line autonomous phases;
* one ordinary component combining one dynamic rail and one current rail;
* AND3/OR3 and FullAdder placements with a dynamic late input;
* bit/word Switch enable phases, Z-to-zero normalization, and two-driver BUS;
* Maker/Splitter lane normalization and lane-parallel word operations;
* joint FullAdder and ripple-suffix outputs with connected-cut accounting.

This is not a global synthesis proof.  It is an exhaustive certificate for the
grammar above.  No game save or candidate is read or modified, and the game is
not launched.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import time
from typing import Iterable

import audit_byte_adder_delayline_sequence as base
import audit_delayline_autonomous_phases as autonomous


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
COMPONENT_CATALOG = ROOT / ".research" / "byte_adder_component_byproduct_catalog" / (
    "component-catalog-v1.json"
)
STATIC_TRUTH_CATALOG = ROOT / ".research" / (
    "byte_adder_component_byproduct_catalog"
) / "truth-byproduct-catalog-v1.json"
BASELINE = ROOT / ".research" / "byte_adder_root" / (
    "byte-adder-hybrid-phasefold-g80-d7.json"
)
OUTPUT = HERE / "byte_adder_23kind_dynamic_byproduct_audit.json"

ROWS = base.ROWS
MASK = base.TRUTH_MASK
BYTE_COUNT = ROWS // 8
OUTPUT_NAMES = tuple([f"S{bit}" for bit in range(8)] + ["Cout"])
PACKED_OPS = autonomous.PACKED_OPS


@dataclass(frozen=True)
class Rail:
    name: str
    truth: int
    driven: int
    gate: int
    arrival: int | None
    source_nodes: tuple[int, ...]
    family: str
    detail: dict[str, object]


@dataclass(frozen=True)
class Target:
    name: str
    truth: int
    driven: int
    arrival: int | None
    node_id: int | None
    category: str


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def packed_digest(value: int) -> str:
    return sha256(value.to_bytes(BYTE_COUNT, "little")).hexdigest()


def compact_rail(rail: Rail) -> dict[str, object]:
    return {
        "name": rail.name,
        "family": rail.family,
        "gate": rail.gate,
        "arrival": rail.arrival,
        "source_nodes": list(rail.source_nodes),
        "ones": rail.truth.bit_count(),
        "driven_cycles": rail.driven.bit_count(),
        "truth_sha256": packed_digest(rail.truth),
        "detail": rail.detail,
    }


def live_sequence() -> list[int]:
    sequence = [base.live_xorshift(cycle) for cycle in range(ROWS)]
    if len(set(sequence)) != ROWS or sequence[0] != 0 or sequence.count(0) != 1:
        raise RuntimeError("live Int xorshift is not the expected complete permutation")
    return sequence


def assignment_to_cycle(value: int, sequence: list[int]) -> int:
    source = value.to_bytes(BYTE_COUNT, "little")
    packed = bytearray(BYTE_COUNT)
    for cycle, assignment in enumerate(sequence):
        bit = (source[assignment >> 3] >> (assignment & 7)) & 1
        packed[cycle >> 3] |= bit << (cycle & 7)
    return int.from_bytes(packed, "little")


def input_node_map(nodes: dict[int, dict[str, object]]) -> dict[str, int]:
    return {
        str(node["label"]): node_id
        for node_id, node in nodes.items()
        if node["op"] == "INPUT"
    }


def output_name_map(outputs: tuple[int, ...]) -> dict[int, str]:
    return {node_id: OUTPUT_NAMES[index] for index, node_id in enumerate(outputs)}


def dependencies(
    nodes: dict[int, dict[str, object]], node_id: int, memo: dict[int, set[int]]
) -> set[int]:
    if node_id in memo:
        return memo[node_id]
    result = {node_id}
    for source in nodes[node_id].get("args", ()):
        result.update(dependencies(nodes, int(source), memo))
    memo[node_id] = result
    return result


def retained_gate_for_cut(
    nodes: dict[int, dict[str, object]],
    outputs: tuple[int, ...],
    targets: set[int],
    sources: set[int],
) -> tuple[int, list[int]]:
    retained: set[int] = set()
    stack = list(outputs) + list(sources)
    while stack:
        node_id = stack.pop()
        if node_id in targets and node_id not in sources:
            continue
        if node_id in retained:
            continue
        retained.add(node_id)
        stack.extend(int(value) for value in nodes[node_id].get("args", ()))
    gate = sum(int(nodes[node_id]["cost"]) for node_id in retained)
    return gate, sorted(retained)


def recompute_arrivals(
    nodes: dict[int, dict[str, object]],
    outputs: tuple[int, ...],
    replacements: dict[int, int],
) -> tuple[list[int], int]:
    arrivals: dict[int, int] = {}
    for node_id, node in nodes.items():
        if node_id in replacements:
            arrivals[node_id] = replacements[node_id]
            continue
        args = [int(value) for value in node.get("args", ())]
        if node["op"] in {"INPUT", "CONST"}:
            arrivals[node_id] = 0
        else:
            missing = [source for source in args if source not in arrivals]
            if missing:
                raise ValueError(
                    f"replacement introduces non-topological dependency at {node_id}: {missing}"
                )
            arrivals[node_id] = max(arrivals[source] for source in args) + int(
                node["step_delay"]
            )
    result = [arrivals[node_id] for node_id in outputs]
    return result, max(result)


def score_cut(
    *,
    nodes: dict[int, dict[str, object]],
    outputs: tuple[int, ...],
    target_arrivals: dict[int, int] | None,
    target_ids: Iterable[int],
    source_ids: Iterable[int],
    added_gate: int,
    dependency_memo: dict[int, set[int]],
) -> dict[str, object]:
    targets = set(target_ids)
    sources = set(source_ids)
    recursive_sources = sorted(
        source
        for source in sources
        if any(target in dependencies(nodes, source, dependency_memo) for target in targets)
    )
    if recursive_sources:
        return {
            "status": "UNKNOWN",
            "reason": "candidate source depends on replaced target",
            "recursive_source_nodes": recursive_sources,
        }
    retained_gate, retained_nodes = retained_gate_for_cut(
        nodes, outputs, targets, sources
    )
    baseline_gate = sum(int(node["cost"]) for node in nodes.values())
    result: dict[str, object] = {
        "status": "PROVEN_GATE",
        "target_node_ids": sorted(targets),
        "source_node_ids": sorted(sources),
        "retained_gate": retained_gate,
        "deleted_current_gate": baseline_gate - retained_gate,
        "added_gate": added_gate,
        "candidate_total_gate": retained_gate + added_gate,
        "retained_node_count": len(retained_nodes),
    }
    if target_arrivals is None:
        result.update(
            {
                "timing_status": "UNKNOWN",
                "reason": "dynamic source native timing is not proven",
            }
        )
        return result
    try:
        output_arrivals, delay = recompute_arrivals(nodes, outputs, target_arrivals)
    except ValueError as exc:
        result.update(
            {
                "timing_status": "UNKNOWN",
                "reason": str(exc),
            }
        )
        return result
    result.update(
        {
            "timing_status": "PROVEN_FEEDFORWARD",
            "output_arrivals": output_arrivals,
            "candidate_delay": delay,
            "candidate_energy": (retained_gate + added_gate) * delay,
        }
    )
    return result


def make_targets(
    *,
    nodes: dict[int, dict[str, object]],
    states: dict[int, base.PackedState],
    outputs: tuple[int, ...],
    cycle_truth: dict[int, int],
    cycle_driven: dict[int, int],
) -> tuple[list[Target], list[int], list[dict[str, object]]]:
    labels = input_node_map(nodes)
    carry_truth = [cycle_truth[labels["cin"]]]
    for bit in range(8):
        left = cycle_truth[labels[f"a{bit}"]]
        right = cycle_truth[labels[f"b{bit}"]]
        previous = carry_truth[-1]
        carry_truth.append((left & right) | ((left ^ right) & previous))

    output_labels = output_name_map(outputs)
    targets = [
        Target(
            output_labels[node_id],
            cycle_truth[node_id],
            cycle_driven[node_id],
            states[node_id].arrival,
            node_id,
            "public_output",
        )
        for node_id in outputs
    ]
    carry_rows = []
    for index, truth in enumerate(carry_truth):
        matches = [
            node_id
            for node_id in nodes
            if cycle_truth[node_id] == truth
        ]
        active_matches = [
            node_id for node_id in matches if cycle_driven[node_id] == MASK
        ]
        carry_rows.append(
            {
                "carry": f"C{index}",
                "ones": truth.bit_count(),
                "sequence_sha256": packed_digest(truth),
                "data_plane_matching_node_ids": matches,
                "active_matching_node_ids": active_matches,
                "preferred_named_node_id": matches[0] if len(matches) == 1 else None,
            }
        )
        targets.append(
            Target(
                f"C{index}",
                truth,
                MASK,
                min((states[node].arrival for node in matches), default=None),
                matches[0] if len(matches) == 1 else None,
                "named_carry",
            )
        )
    return targets, carry_truth, carry_rows


def current_rails(
    nodes: dict[int, dict[str, object]],
    states: dict[int, base.PackedState],
    cycle_truth: dict[int, int],
    cycle_driven: dict[int, int],
) -> tuple[list[Rail], dict[int, list[int]]]:
    aliases: dict[int, list[int]] = {}
    for node_id in nodes:
        aliases.setdefault(cycle_truth[node_id], []).append(node_id)
    rails = []
    for truth, node_ids in aliases.items():
        best = min(node_ids, key=lambda node: (states[node].arrival, node))
        rails.append(
            Rail(
                name=f"current:n{best}",
                truth=truth,
                driven=cycle_driven[best],
                gate=0,
                arrival=states[best].arrival,
                source_nodes=(best,),
                family="current",
                detail={
                    "representative_node_id": best,
                    "alias_node_ids": sorted(node_ids),
                    "op": nodes[best]["op"],
                },
            )
        )
    rails.extend(
        [
            Rail("CONST0", 0, MASK, 0, 0, (), "constant", {"kind": 1}),
            Rail("CONST1", MASK, MASK, 0, 0, (), "constant", {"kind": 2}),
        ]
    )
    rails.sort(key=lambda rail: (rail.arrival or 0, rail.name))
    return rails, aliases


def history_rails(current: list[Rail]) -> tuple[list[Rail], dict[str, object]]:
    by_truth: dict[int, Rail] = {}
    candidates = 0
    for source in current:
        if source.family != "current":
            continue
        candidates += 1
        truth = (source.truth << 1) & MASK
        arrival = None if source.arrival is None else source.arrival + 4
        rail = Rail(
            name=f"history({source.name})",
            truth=truth,
            driven=MASK,
            gate=5,
            arrival=arrival,
            source_nodes=source.source_nodes,
            family="history",
            detail={
                "component_kind": 13,
                "initial_state": 0,
                "equation": "Result(t)=0 for t=0; data_plane(Input(t-1)) thereafter",
                "input_was_partial": source.driven != MASK,
                "z_to_zero": source.driven != MASK,
            },
        )
        previous = by_truth.get(truth)
        key = (rail.gate, rail.arrival if rail.arrival is not None else 10**9, rail.name)
        if previous is None or key < (
            previous.gate,
            previous.arrival if previous.arrival is not None else 10**9,
            previous.name,
        ):
            by_truth[truth] = rail
    return list(by_truth.values()), {
        "candidate_count_before_sequence_dedup": candidates,
        "unique_sequence_count": len(by_truth),
        "delay_line_gate_each": 5,
        "component_delay_each": 4,
        "timing_cut": False,
        "cycle_zero_output": 0,
    }


def phase_rails() -> tuple[list[Rail], dict[str, object]]:
    phases, enumeration, aliases = autonomous.enumerate_phases()
    rails = []
    for truth, recipe in phases.items():
        serialized = recipe.serialized()
        rails.append(
            Rail(
                name=f"phase:{packed_digest(truth)[:16]}",
                truth=truth,
                driven=MASK,
                gate=recipe.gate,
                arrival=serialized["native_feedback_delay"],
                source_nodes=(),
                family="phase",
                detail={
                    **serialized,
                    "semantic_alias_count": len(aliases[truth]),
                },
            )
        )
    return rails, enumeration


def target_indexes(targets: list[Target]) -> tuple[dict[int, list[Target]], dict[str, Target]]:
    by_truth: dict[int, list[Target]] = {}
    by_name = {}
    for target in targets:
        by_truth.setdefault(target.truth, []).append(target)
        by_name[target.name] = target
    return by_truth, by_name


def direct_matches(rails: list[Rail], targets: list[Target]) -> dict[str, object]:
    by_truth, _ = target_indexes(targets)
    exact = []
    complement = []
    for rail in rails:
        for target in by_truth.get(rail.truth, ()):
            exact.append({"asset": compact_rail(rail), "target": target.name})
        for target in by_truth.get((~rail.truth) & MASK, ()):
            complement.append({"asset": compact_rail(rail), "target": target.name})
    return {
        "exact_match_count": len(exact),
        "complement_match_count": len(complement),
        "exact_matches": exact,
        "complement_matches": complement,
    }


def current_one_gate_closure(current: list[Rail]) -> dict[int, dict[str, object]]:
    closure: dict[int, dict[str, object]] = {}

    def remember(truth: int, row: dict[str, object]) -> None:
        previous = closure.get(truth)
        if previous is None or (row["gate"], str(row)) < (
            previous["gate"],
            str(previous),
        ):
            closure[truth] = row

    for source in current:
        remember(source.truth, {"gate": 0, "kind": "WIRE", "source": source.name})
        remember(
            (~source.truth) & MASK,
            {"gate": 1, "kind": "NOT", "source": source.name},
        )
    for offset, left in enumerate(current):
        for right in current[offset + 1 :]:
            for op in ("AND", "OR", "NAND", "NOR"):
                remember(
                    PACKED_OPS[op](left.truth, right.truth),
                    {
                        "gate": 1,
                        "kind": op,
                        "left": left.name,
                        "right": right.name,
                    },
                )
    return closure


def best_cut_for_single_target(
    *,
    target: Target,
    source_nodes: tuple[int, ...],
    added_gate: int,
    arrival: int | None,
    nodes: dict[int, dict[str, object]],
    outputs: tuple[int, ...],
    dependency_memo: dict[int, set[int]],
) -> dict[str, object] | None:
    if target.node_id is None:
        return None
    return score_cut(
        nodes=nodes,
        outputs=outputs,
        target_arrivals=None if arrival is None else {target.node_id: arrival},
        target_ids=[target.node_id],
        source_ids=source_nodes,
        added_gate=added_gate,
        dependency_memo=dependency_memo,
    )


def dynamic_one_component_search(
    *,
    dynamic: list[Rail],
    current: list[Rail],
    targets: list[Target],
    nodes: dict[int, dict[str, object]],
    outputs: tuple[int, ...],
    dependency_memo: dict[int, set[int]],
) -> dict[str, object]:
    by_truth, _ = target_indexes(targets)
    static_closure = current_one_gate_closure(current)
    operations = {
        "AND": {"kind": 4, "gate": 1, "delay": 1},
        "NAND": {"kind": 6, "gate": 1, "delay": 1},
        "OR": {"kind": 7, "gate": 1, "delay": 1},
        "NOR": {"kind": 9, "gate": 1, "delay": 1},
        "XOR": {"kind": 10, "gate": 3, "delay": 2},
        # Native kind 11 is 5/4; its legal G/K/Q expansion is 3/2.
        "XNOR": {"kind": 11, "gate": 3, "delay": 2, "native": {"gate": 5, "delay": 4}},
    }
    counts = {"NOT": 0, **{name: 0 for name in operations}}
    hits: list[dict[str, object]] = []
    undominated_nonrecursive = 0

    def emit(
        result: int,
        op: str,
        left: Rail,
        right: Rail | None,
        component_gate: int,
        step_delay: int,
        kind: int,
        extra: dict[str, object] | None = None,
    ) -> None:
        nonlocal undominated_nonrecursive
        matched = by_truth.get(result)
        if not matched:
            return
        counts[op] += len(matched)
        arrival = None
        input_arrivals = [left.arrival]
        if right is not None:
            input_arrivals.append(right.arrival)
        if all(value is not None for value in input_arrivals):
            arrival = max(int(value) for value in input_arrivals) + step_delay
        sources = tuple(sorted(set(left.source_nodes + (() if right is None else right.source_nodes))))
        added_gate = left.gate + (0 if right is None else right.gate) + component_gate
        for target in matched:
            dominated = static_closure.get(result)
            cut = best_cut_for_single_target(
                target=target,
                source_nodes=sources,
                added_gate=added_gate,
                arrival=arrival,
                nodes=nodes,
                outputs=outputs,
                dependency_memo=dependency_memo,
            )
            recursive = cut is not None and cut.get("status") == "UNKNOWN" and (
                cut.get("reason") == "candidate source depends on replaced target"
            )
            if dominated is None and not recursive:
                undominated_nonrecursive += 1
            hits.append(
                {
                    "target": target.name,
                    "target_node_id": target.node_id,
                    "operation": op,
                    "component_kind": kind,
                    "left": compact_rail(left),
                    "right": None if right is None else compact_rail(right),
                    "added_gate": added_gate,
                    "arrival": arrival,
                    "dominated_by_current_at_most_one_gate": dominated,
                    "connected_cut": cut,
                    **(extra or {}),
                }
            )

    for left in dynamic:
        emit(
            (~left.truth) & MASK,
            "NOT",
            left,
            None,
            1,
            1,
            3,
        )
        for right in current:
            for op, metadata in operations.items():
                emit(
                    PACKED_OPS[op](left.truth, right.truth),
                    op,
                    left,
                    right,
                    int(metadata["gate"]),
                    int(metadata["delay"]),
                    int(metadata["kind"]),
                    {"native_cost_if_different": metadata.get("native")},
                )
    hits.sort(
        key=lambda row: (
            row["dominated_by_current_at_most_one_gate"] is not None,
            row["connected_cut"] is not None
            and row["connected_cut"].get("status") == "UNKNOWN",
            row["added_gate"],
            row["arrival"] if row["arrival"] is not None else 10**9,
            row["target"],
            row["operation"],
        )
    )
    return {
        "grammar": "one dynamic rail, optionally one current data-plane rail, one public ordinary component",
        "dynamic_rail_count": len(dynamic),
        "current_truth_class_count_including_constants": len(current),
        "operation_target_match_counts": counts,
        "match_count": len(hits),
        "undominated_nonrecursive_match_count": undominated_nonrecursive,
        "matches": hits,
    }


def short_arc_three_input_search(
    *,
    dynamic: list[Rail],
    input_nodes: dict[str, int],
    cycle_truth: dict[int, int],
    targets: list[Target],
) -> dict[str, object]:
    by_truth, _ = target_indexes(targets)
    hits = []
    counts = {"AND3": 0, "OR3": 0}
    for bit in range(8):
        left_id = input_nodes[f"a{bit}"]
        right_id = input_nodes[f"b{bit}"]
        left = cycle_truth[left_id]
        right = cycle_truth[right_id]
        for late in dynamic:
            for name, op, kind in (
                ("AND3", lambda a, b, c: a & b & c, 5),
                ("OR3", lambda a, b, c: a | b | c, 8),
            ):
                result = op(left, right, late.truth)
                matched = by_truth.get(result)
                if not matched:
                    continue
                counts[name] += len(matched)
                arrival = None if late.arrival is None else max(1, late.arrival) + 1
                for target in matched:
                    hits.append(
                        {
                            "target": target.name,
                            "component_kind": kind,
                            "function": name,
                            "early_pair": [f"a{bit}", f"b{bit}"],
                            "late_input": compact_rail(late),
                            "flat_expansion_gate": late.gate + 2,
                            "native_component_gate": late.gate + 3,
                            "output_arrival_with_late_short_arc": arrival,
                            "arc_depths": {f"a{bit}": 2, f"b{bit}": 2, late.name: 1},
                        }
                    )
    return {
        "grammar": "flat two-gate AND3/OR3 with (a_i,b_i) paired early and one dynamic late input",
        "searched_placements": 8 * len(dynamic) * 2,
        "target_match_counts": counts,
        "matches": hits,
    }


def full_adder_values(left: int, right: int, carry: int) -> dict[str, int]:
    generate = left & right
    kill = ~(left | right) & MASK
    propagate = ~(generate | kill) & MASK
    transfer = propagate & carry
    no_transfer = ~(propagate | carry) & MASK
    result = ~(transfer | no_transfer) & MASK
    carry_out = generate | transfer
    return {
        "G": generate,
        "K": kill,
        "P": propagate,
        "T": transfer,
        "N": no_transfer,
        "SUM": result,
        "CARRY": carry_out,
    }


def full_adder_arrivals(carry_arrival: int | None) -> dict[str, int] | None:
    if carry_arrival is None:
        return None
    generate = kill = 1
    propagate = 2
    transfer = no_transfer = max(propagate, carry_arrival) + 1
    result = max(transfer, no_transfer) + 1
    carry = max(generate, transfer) + 1
    return {
        "G": generate,
        "K": kill,
        "P": propagate,
        "T": transfer,
        "N": no_transfer,
        "SUM": result,
        "CARRY": carry,
    }


def full_adder_dynamic_search(
    *,
    carry_sources: list[Rail],
    input_nodes: dict[str, int],
    cycle_truth: dict[int, int],
    targets: list[Target],
    carry_truth: list[int],
    outputs: tuple[int, ...],
    nodes: dict[int, dict[str, object]],
    dependency_memo: dict[int, set[int]],
) -> dict[str, object]:
    by_truth, by_name = target_indexes(targets)
    sideproduct_hits = []
    joint_hits = []
    current_correct_rows = []
    prefix_gate = {"G": 1, "K": 1, "P": 3, "T": 4, "N": 4, "SUM": 6, "CARRY": 5}

    for bit in range(8):
        left = cycle_truth[input_nodes[f"a{bit}"]]
        right = cycle_truth[input_nodes[f"b{bit}"]]
        for source in carry_sources:
            values = full_adder_values(left, right, source.truth)
            arrivals = full_adder_arrivals(source.arrival)
            for role, truth in values.items():
                for target in by_truth.get(truth, ()):
                    if source.family == "current":
                        continue
                    sideproduct_hits.append(
                        {
                            "bit": bit,
                            "role": role,
                            "target": target.name,
                            "carry_source": compact_rail(source),
                            "prefix_added_gate": source.gate + prefix_gate[role],
                            "arrival": None if arrivals is None else arrivals[role],
                        }
                    )
            sum_target = by_name[f"S{bit}"]
            carry_target = by_name[f"C{bit + 1}"]
            if values["SUM"] != sum_target.truth or values["CARRY"] != carry_target.truth:
                continue
            sum_arrival = None if arrivals is None else arrivals["SUM"]
            carry_arrival = None if arrivals is None else arrivals["CARRY"]
            target_ids = [outputs[bit]]
            replacement_arrivals = (
                None
                if sum_arrival is None
                else {outputs[bit]: sum_arrival}
            )
            if carry_target.node_id is not None:
                target_ids.append(carry_target.node_id)
                if sum_arrival is not None and carry_arrival is not None:
                    assert replacement_arrivals is not None
                    replacement_arrivals[carry_target.node_id] = carry_arrival
            cut = score_cut(
                nodes=nodes,
                outputs=outputs,
                target_arrivals=replacement_arrivals,
                target_ids=target_ids,
                source_ids=source.source_nodes,
                added_gate=source.gate + 7,
                dependency_memo=dependency_memo,
            )
            row = {
                "bit": bit,
                "carry_source": compact_rail(source),
                "targets": [f"S{bit}", f"C{bit + 1}"],
                "added_gate": source.gate + 7,
                "output_arrivals": None
                if arrivals is None
                else {"SUM": sum_arrival, "CARRY": carry_arrival},
                "late_input_arc_depth": 2,
                "connected_cut": cut,
            }
            if source.family == "current":
                current_correct_rows.append(row)
            else:
                joint_hits.append(row)

    return {
        "grammar": "7-gate G/K/P/T/N/SUM/CARRY expansion; a_i,b_i early, candidate carry-in late",
        "carry_source_count": len(carry_sources),
        "searched_placements": 8 * len(carry_sources),
        "dynamic_joint_exact_match_count": len(joint_hits),
        "dynamic_sideproduct_target_match_count": len(sideproduct_hits),
        "dynamic_joint_exact_matches": joint_hits,
        "dynamic_sideproduct_matches": sideproduct_hits,
        "current_correct_carry_short_arc_rows": current_correct_rows,
        "prefix_gate_by_role": prefix_gate,
    }


def ripple_suffixes(
    *,
    current: list[Rail],
    carry_truth: list[int],
    outputs: tuple[int, ...],
    nodes: dict[int, dict[str, object]],
    dependency_memo: dict[int, set[int]],
) -> list[dict[str, object]]:
    rows = []
    for start in range(8):
        candidates = [rail for rail in current if rail.truth == carry_truth[start]]
        for source in candidates:
            carry_arrival = source.arrival
            generated_arrivals = []
            if carry_arrival is not None:
                for _bit in range(start, 8):
                    carry_arrival = max(2, carry_arrival) + 2
                    generated_arrivals.append(carry_arrival)
            target_ids = list(outputs[start:])
            target_arrivals = None
            if generated_arrivals:
                target_arrivals = {
                    outputs[index]: generated_arrivals[index - start]
                    for index in range(start, 8)
                }
                target_arrivals[outputs[8]] = generated_arrivals[-1]
            cut = score_cut(
                nodes=nodes,
                outputs=outputs,
                target_arrivals=target_arrivals,
                target_ids=target_ids,
                source_ids=source.source_nodes,
                added_gate=7 * (8 - start),
                dependency_memo=dependency_memo,
            )
            rows.append(
                {
                    "start_bit": start,
                    "carry_in": f"C{start}",
                    "carry_source": compact_rail(source),
                    "replaced_outputs": list(OUTPUT_NAMES[start:]),
                    "full_adder_count": 8 - start,
                    "added_gate": 7 * (8 - start),
                    "generated_output_arrivals": generated_arrivals or None,
                    "connected_cut": cut,
                }
            )
    return rows


def normalizer_audit(
    *,
    nodes: dict[int, dict[str, object]],
    states: dict[int, base.PackedState],
    cycle_truth: dict[int, int],
    cycle_driven: dict[int, int],
    carry_truth: list[int],
) -> dict[str, object]:
    partial_rows = []
    for node_id, node in nodes.items():
        if cycle_driven[node_id] == MASK:
            continue
        carry_matches = [
            f"C{index}" for index, truth in enumerate(carry_truth) if truth == cycle_truth[node_id]
        ]
        partial_rows.append(
            {
                "node_id": node_id,
                "op": node["op"],
                "arrival": states[node_id].arrival,
                "z_cycles": ROWS - cycle_driven[node_id].bit_count(),
                "data_plane_ones": cycle_truth[node_id].bit_count(),
                "carry_data_plane_matches": carry_matches,
                "normalized_value_sha256": packed_digest(cycle_truth[node_id]),
                "normalized_driven_cycles": ROWS,
                "normalizer_gate": 0,
                "normalizer_delay": 0,
                "physical_owner_barrier": True,
                "direct_cut_useful": False,
                "direct_cut_reason": "the zero-cost active clone still depends on the original partial node",
            }
        )

    switch_drivers = []
    for node_id, node in nodes.items():
        if node["op"] != "BUS":
            continue
        args = [int(value) for value in node["args"]]
        for offset in range(0, len(args), 2):
            enable, data = args[offset : offset + 2]
            value = cycle_truth[enable] & cycle_truth[data]
            driven = cycle_truth[enable]
            switch_drivers.append(
                {
                    "bus_node_id": node_id,
                    "enable_node_id": enable,
                    "data_node_id": data,
                    "value_sha256": packed_digest(value),
                    "driven_cycles": driven.bit_count(),
                    "z_cycles": ROWS - driven.bit_count(),
                    "arrival": max(states[enable].arrival, states[data].arrival) + 1,
                    "owner": f"bus_node_{node_id}",
                    "independently_normalizable_after_bus_merge": False,
                }
            )

    carry_bus_nodes = [
        row["node_id"] for row in partial_rows if row["carry_data_plane_matches"]
    ]
    return {
        "partial_live_node_count": len(partial_rows),
        "partial_live_nodes": partial_rows,
        "switch_driver_count": len(switch_drivers),
        "switch_drivers": switch_drivers,
        "joint_carry_normalizer": {
            "source_node_ids": carry_bus_nodes,
            "source_carries": [
                row["carry_data_plane_matches"][0]
                for row in partial_rows
                if row["carry_data_plane_matches"]
            ],
            "construction": "Maker4(partial carry data planes) -> Splitter4",
            "gate": 0,
            "delay": 0,
            "all_outputs_active": True,
            "conflict_cycles": 0,
            "owner_barrier": True,
            "score_effect": "no Boolean cone is deleted because every normalized lane depends on its source BUS",
        },
        "z_to_zero_rules": {
            "ordinary_component_input": "Z data plane is read as 0 and output is active",
            "delay_line_input": "Z is stored as 0 and becomes active Result on the next tick",
            "maker_splitter": "Z lane/word data becomes active 0 at zero gate and zero delay",
            "conflict": "never normalized; conflict is invalid/halt and must propagate or be forbidden",
        },
    }


def cofactor_phase_search(phases: list[Rail], targets: list[Target]) -> dict[str, object]:
    selected_targets = [
        target
        for target in targets
        if target.category == "public_output"
        or (target.category == "named_carry" and target.name != "C0")
    ]
    records = []
    for phase in phases:
        if phase.truth in {0, MASK}:
            continue
        for target in selected_targets:
            witness = {
                "AND": (target.truth & (~phase.truth & MASK)).bit_count(),
                "OR": (phase.truth & (~target.truth & MASK)).bit_count(),
                "NAND": ((~target.truth & MASK) & (~phase.truth & MASK)).bit_count(),
                "NOR": (target.truth & phase.truth).bit_count(),
            }
            for op, mismatches in witness.items():
                if mismatches:
                    continue
                care = phase.truth if op in {"AND", "NAND"} else (~phase.truth & MASK)
                dc = (~care) & MASK
                records.append(
                    {
                        "target": target.name,
                        "outer_gate": op,
                        "phase": compact_rail(phase),
                        "residual_care_cycle_count": care.bit_count(),
                        "residual_dc_cycle_count": dc.bit_count(),
                        "first_dc_cycle": (dc & -dc).bit_length() - 1 if dc else None,
                        "last_dc_cycle": dc.bit_length() - 1 if dc else None,
                        "terminal_cycle_is_cofactor_dc": bool(
                            (dc >> (ROWS - 1)) & 1
                        ),
                        "terminal_test_induced_dc_present": False,
                        "dc_origin": "outer-gate insensitive cofactor, not test termination",
                    }
                )
    by_phase: dict[tuple[str, str], list[str]] = {}
    for record in records:
        key = (record["phase"]["truth_sha256"], record["outer_gate"])
        by_phase.setdefault(key, []).append(record["target"])
    shared = [
        {
            "phase_truth_sha256": key[0],
            "outer_gate": key[1],
            "targets": sorted(values),
            "target_count": len(values),
        }
        for key, values in by_phase.items()
    ]
    shared.sort(key=lambda row: (-row["target_count"], row["outer_gate"], row["phase_truth_sha256"]))
    return {
        "feasible_record_count": len(records),
        "records": records,
        "shared_phase_groups": shared,
        "all_17_targets_notfirst_and": any(
            row["target_count"] == 17 and row["outer_gate"] == "AND" for row in shared
        ),
    }


def word_lane_audit(
    *,
    phases: list[Rail],
    input_nodes: dict[str, int],
    cycle_truth: dict[int, int],
    outputs: tuple[int, ...],
    carry_truth: list[int],
) -> dict[str, object]:
    bundles: dict[str, tuple[int, ...]] = {
        "A": tuple(cycle_truth[input_nodes[f"a{bit}"]] for bit in range(8)),
        "B": tuple(cycle_truth[input_nodes[f"b{bit}"]] for bit in range(8)),
        "SUM": tuple(cycle_truth[outputs[bit]] for bit in range(8)),
        "CARRY1_8": tuple(carry_truth[bit + 1] for bit in range(8)),
    }
    bundles["HISTORY_A"] = tuple((value << 1) & MASK for value in bundles["A"])
    bundles["HISTORY_B"] = tuple((value << 1) & MASK for value in bundles["B"])
    targets = {name: value for name, value in bundles.items() if name in {"A", "B", "SUM", "CARRY1_8"}}

    not_hits = []
    for source_name, lanes in bundles.items():
        result = tuple((~lane) & MASK for lane in lanes)
        for target_name, target_lanes in targets.items():
            if result == target_lanes:
                not_hits.append({"source": source_name, "target": target_name})

    nand_hits = []
    items = list(bundles.items())
    for left_offset, (left_name, left) in enumerate(items):
        for right_name, right in items[left_offset:]:
            result = tuple(~(a & b) & MASK for a, b in zip(left, right))
            for target_name, target_lanes in targets.items():
                if result == target_lanes:
                    nand_hits.append(
                        {"left": left_name, "right": right_name, "target": target_name}
                    )

    useful_phases = [
        phase
        for phase in phases
        if phase.detail["delay_line_count"] == 1
        and phase.detail["decode_gate"] == 0
        and phase.truth not in {0, MASK}
    ]
    switch_hits = []
    for phase in useful_phases:
        for source_name, lanes in bundles.items():
            result = tuple(phase.truth & lane for lane in lanes)
            for target_name, target_lanes in targets.items():
                if result == target_lanes:
                    switch_hits.append(
                        {
                            "phase": compact_rail(phase),
                            "source": source_name,
                            "target": target_name,
                            "word_switch_gate": 16,
                            "shared_phase_gate": phase.gate,
                            "normalizer_gate": 0,
                            "total_gate": phase.gate + 16,
                            "whole_word_z_cycles_before_normalizer": ROWS
                            - phase.truth.bit_count(),
                        }
                    )

    return {
        "bundles": list(bundles),
        "not_word_kind18": {
            "gate": 8,
            "delay": 1,
            "lane_independent": True,
            "exact_joint_hits": not_hits,
        },
        "nand_word_kind21": {
            "gate": 8,
            "delay": 1,
            "lane_independent": True,
            "exact_joint_hits": nand_hits,
        },
        "switch_word_kind25": {
            "gate": 16,
            "delay": 1,
            "shared_enable": True,
            "whole_word_driven_flag": True,
            "exact_joint_hits_after_zero_cost_normalizer": switch_hits,
        },
        "maker_splitter_kinds": [16, 17, 109, 110, 111, 112],
        "cross_lane_logic_found": False,
        "width_discount_found": False,
        "reason": "word NOT/NAND/Switch costs are exactly the sum of their bit lanes; Maker/Splitter add no cross-lane Boolean function",
    }


def switch_and_bus_search(
    *,
    phases: list[Rail],
    current: list[Rail],
    targets: list[Target],
) -> dict[str, object]:
    useful_phases = [
        rail
        for rail in phases
        if rail.detail["delay_line_count"] == 1
        and rail.detail["decode_gate"] == 0
        and rail.truth not in {0, MASK}
    ]
    source_by_truth: dict[int, Rail] = {}
    for source in current:
        if source.arrival is not None and source.arrival <= 4:
            source_by_truth.setdefault(source.truth, source)
    for source in useful_phases:
        source_by_truth.setdefault(source.truth, source)
    sources = list(source_by_truth.values())

    drivers: dict[tuple[int, int, int], dict[str, object]] = {}
    for enable in sources:
        for data in sources:
            ones = enable.truth & data.truth
            zeros = enable.truth & (~data.truth & MASK)
            key = (ones, zeros, enable.truth)
            previous = drivers.get(key)
            phase_assets = {
                rail.name: rail.gate
                for rail in (enable, data)
                if rail.family == "phase"
            }
            gate = 2 + sum(phase_assets.values())
            arrival = None
            if enable.arrival is not None and data.arrival is not None:
                arrival = max(enable.arrival, data.arrival) + 1
            row = {
                "enable": enable,
                "data": data,
                "gate": gate,
                "arrival": arrival,
                "uses_phase": bool(phase_assets),
            }
            if previous is None or (
                gate,
                arrival if arrival is not None else 10**9,
                enable.name,
                data.name,
            ) < (
                previous["gate"],
                previous["arrival"] if previous["arrival"] is not None else 10**9,
                previous["enable"].name,
                previous["data"].name,
            ):
                drivers[key] = row

    driver_rows = [(*key, value) for key, value in drivers.items()]
    physical_hits = []
    normalized_hits = []
    physical_count = normalized_count = 0
    physical_nonrecursive_count = normalized_nonrecursive_count = 0
    for target in targets:
        if target.category not in {"public_output", "named_carry"}:
            continue
        compatible_physical = [
            row
            for row in driver_rows
            if not (row[0] & (~target.truth & MASK))
            and not (row[1] & target.truth)
        ]
        compatible_normalized = [
            row for row in driver_rows if not (row[0] & (~target.truth & MASK))
        ]

        for mode, compatible in (
            ("physical", compatible_physical),
            ("normalized", compatible_normalized),
        ):
            for offset, left in enumerate(compatible):
                for right in compatible[offset:]:
                    left_ones, left_zeros, left_driven, left_recipe = left
                    right_ones, right_zeros, right_driven, right_recipe = right
                    if not (left_recipe["uses_phase"] or right_recipe["uses_phase"]):
                        continue
                    if (left_ones & right_zeros) or (right_ones & left_zeros):
                        continue
                    ones = left_ones | right_ones
                    if ones != target.truth:
                        continue
                    if mode == "physical":
                        if (left_driven | right_driven) != target.driven:
                            continue
                        if (left_zeros | right_zeros) != (target.driven & (~target.truth & MASK)):
                            continue
                    endpoint_nodes = set(
                        left_recipe["enable"].source_nodes
                        + left_recipe["data"].source_nodes
                        + right_recipe["enable"].source_nodes
                        + right_recipe["data"].source_nodes
                    )
                    recursive = target.node_id is not None and target.node_id in endpoint_nodes
                    phase_assets = {
                        rail.name: rail.gate
                        for recipe in (left_recipe, right_recipe)
                        for rail in (recipe["enable"], recipe["data"])
                        if rail.family == "phase"
                    }
                    gate = 4 + sum(phase_assets.values())
                    arrivals = [left_recipe["arrival"], right_recipe["arrival"]]
                    arrival = max(arrivals) if all(value is not None for value in arrivals) else None
                    record = {
                        "target": target.name,
                        "mode": "two-Switch BUS" if mode == "physical" else "two-Switch BUS -> zero-cost normalizer",
                        "left": {
                            "enable": left_recipe["enable"].name,
                            "data": left_recipe["data"].name,
                        },
                        "right": {
                            "enable": right_recipe["enable"].name,
                            "data": right_recipe["data"].name,
                        },
                        "gate": gate,
                        "arrival": arrival,
                        "recursive_target_pin": recursive,
                        "source_node_ids": sorted(endpoint_nodes),
                    }
                    if mode == "physical":
                        physical_count += 1
                        physical_nonrecursive_count += not recursive
                        if len(physical_hits) < 256:
                            physical_hits.append(record)
                    else:
                        normalized_count += 1
                        normalized_nonrecursive_count += not recursive
                        if len(normalized_hits) < 256:
                            normalized_hits.append(record)
    return {
        "source_truth_class_count": len(sources),
        "one_delay_phase_count": len(useful_phases),
        "driver_truth_class_count": len(drivers),
        "physical_exact_match_count": physical_count,
        "normalized_exact_match_count": normalized_count,
        "nonrecursive_physical_exact_match_count": physical_nonrecursive_count,
        "nonrecursive_normalized_exact_match_count": normalized_nonrecursive_count,
        "physical_matches_capped_at_256": physical_hits,
        "normalized_matches_capped_at_256": normalized_hits,
        "nonrecursive_physical_match_count_in_stored_rows": sum(
            not row["recursive_target_pin"] for row in physical_hits
        ),
        "nonrecursive_normalized_match_count_in_stored_rows": sum(
            not row["recursive_target_pin"] for row in normalized_hits
        ),
        "scope": "two conflict-free Switch drivers; sources are current rails with arrival<=4 plus all one-Delay state phases",
    }


def component_inventory(catalog: dict[str, object]) -> list[dict[str, object]]:
    family_by_kind = {
        1: ["cycle-constant"],
        2: ["cycle-constant"],
        3: ["dynamic unary", "Z-to-active"],
        4: ["dynamic binary", "Z-to-active"],
        5: ["late-input short arc", "flat pair byproduct"],
        6: ["dynamic binary", "Z-to-active"],
        7: ["dynamic binary", "Z-to-active"],
        8: ["late-input short arc", "flat pair byproduct"],
        9: ["dynamic binary", "Z-to-active"],
        10: ["dynamic binary", "G/K/P flat byproducts"],
        11: ["dynamic binary", "G/K/Q flat byproducts", "native dominated"],
        12: ["enable phase", "partial driver", "BUS", "normalizer"],
        13: ["history", "warm-up", "Z-to-zero", "autonomous phase"],
        15: ["joint SUM/CARRY", "late-input D2", "G/K/P/T/N byproducts"],
        16: ["word lane", "zero-delay normalizer", "owner barrier"],
        17: ["word lane", "zero-delay normalizer", "owner barrier"],
        18: ["word lane parallel", "Z-to-active"],
        21: ["word lane parallel", "Z-to-active"],
        25: ["shared enable phase", "whole-word Z", "word BUS", "normalizer"],
        109: ["word lane", "zero-delay normalizer", "owner barrier"],
        110: ["word lane", "zero-delay normalizer", "owner barrier"],
        111: ["word lane", "zero-delay normalizer", "owner barrier"],
        112: ["word lane", "zero-delay normalizer", "owner barrier"],
    }
    rows = []
    for component in catalog["components"]:
        kind = int(component["kind"])
        rows.append(
            {
                "kind": kind,
                "symbol_name": component["symbol_name"],
                "semantic_role": component["semantic_role"],
                "effective_cost": component["cost"]["effective_now"],
                "public_inputs": component["native_public_inputs"],
                "public_outputs": component["native_public_outputs"],
                "hidden_wireable_outputs": component["native_hidden_wireable_outputs_found"],
                "dynamic_asset_families": family_by_kind[kind],
            }
        )
    if set(family_by_kind) != {row["kind"] for row in rows} or len(rows) != 23:
        raise RuntimeError("23-kind dynamic inventory does not match the static catalog")
    return rows


def main() -> int:
    started = time.monotonic()
    for path in (COMPONENT_CATALOG, STATIC_TRUTH_CATALOG, BASELINE, base.TEST_SI):
        if not path.is_file():
            raise FileNotFoundError(path)
    component_catalog = json.loads(COMPONENT_CATALOG.read_text(encoding="utf-8"))
    static_catalog = json.loads(STATIC_TRUTH_CATALOG.read_text(encoding="utf-8"))
    inventory = component_inventory(component_catalog)

    print("evaluating baseline and live cycle permutation", flush=True)
    nodes, states, outputs, semantic = base.evaluate_dag()
    sequence = live_sequence()
    cycle_truth = {
        node_id: assignment_to_cycle(state.bits, sequence)
        for node_id, state in states.items()
    }
    cycle_driven = {
        node_id: assignment_to_cycle(state.driven, sequence)
        for node_id, state in states.items()
    }
    targets, carry_truth, carry_rows = make_targets(
        nodes=nodes,
        states=states,
        outputs=outputs,
        cycle_truth=cycle_truth,
        cycle_driven=cycle_driven,
    )
    input_nodes = input_node_map(nodes)
    current, current_aliases = current_rails(
        nodes, states, cycle_truth, cycle_driven
    )
    history, history_summary = history_rails(current)
    phases, phase_enumeration = phase_rails()
    dynamic = phases + history
    dependency_memo: dict[int, set[int]] = {}

    print("searching direct history/phase matches", flush=True)
    history_direct = direct_matches(history, targets)
    phase_direct = direct_matches(phases, targets)
    print("searching one-component dynamic closure", flush=True)
    one_component = dynamic_one_component_search(
        dynamic=dynamic,
        current=current,
        targets=targets,
        nodes=nodes,
        outputs=outputs,
        dependency_memo=dependency_memo,
    )
    print("searching short-arc three-input and FullAdder placements", flush=True)
    three_input = short_arc_three_input_search(
        dynamic=dynamic,
        input_nodes=input_nodes,
        cycle_truth=cycle_truth,
        targets=targets,
    )
    fulladder = full_adder_dynamic_search(
        carry_sources=current + dynamic,
        input_nodes=input_nodes,
        cycle_truth=cycle_truth,
        targets=targets,
        carry_truth=carry_truth,
        outputs=outputs,
        nodes=nodes,
        dependency_memo=dependency_memo,
    )
    ripple = ripple_suffixes(
        current=current,
        carry_truth=carry_truth,
        outputs=outputs,
        nodes=nodes,
        dependency_memo=dependency_memo,
    )
    print("auditing normalizers, word lanes, phase cofactors, and BUS", flush=True)
    normalizer = normalizer_audit(
        nodes=nodes,
        states=states,
        cycle_truth=cycle_truth,
        cycle_driven=cycle_driven,
        carry_truth=carry_truth,
    )
    phase_cofactors = cofactor_phase_search(phases, targets)
    word = word_lane_audit(
        phases=phases,
        input_nodes=input_nodes,
        cycle_truth=cycle_truth,
        outputs=outputs,
        carry_truth=carry_truth,
    )
    bus = switch_and_bus_search(phases=phases, current=current, targets=targets)

    dynamic_carry_hits = [
        row
        for row in one_component["matches"]
        if row["target"].startswith("C")
        and row["dominated_by_current_at_most_one_gate"] is None
        and not (
            row["connected_cut"] is not None
            and row["connected_cut"].get("status") == "UNKNOWN"
        )
    ]
    score_improving_dynamic_cuts = [
        row
        for row in one_component["matches"]
        if row["connected_cut"] is not None
        and row["connected_cut"].get("candidate_total_gate", 10**9) < 80
        and row["connected_cut"].get("candidate_energy", 10**9) < 560
    ]
    ripple_score_improving = [
        row
        for row in ripple
        if row["connected_cut"].get("candidate_total_gate", 10**9) < 80
        and row["connected_cut"].get("candidate_energy", 10**9) < 560
    ]

    report = {
        "schema": "tc-byte-adder-23kind-sequence-dynamic-byproduct-audit-v1",
        "status": "COMPLETE",
        "scope": {
            "finite_grammar_exhaustive": True,
            "global_synthesis_unsat_claimed": False,
            "game_launched": False,
            "save_or_candidate_read_or_modified": False,
            "history_file_modified": False,
        },
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "dependencies": {
            "component_catalog": {"path": str(COMPONENT_CATALOG), "sha256": digest(COMPONENT_CATALOG)},
            "static_truth_catalog": {"path": str(STATIC_TRUTH_CATALOG), "sha256": digest(STATIC_TRUTH_CATALOG)},
            "baseline": {"path": str(BASELINE), "sha256": digest(BASELINE)},
            "test_si": {"path": str(base.TEST_SI), "sha256": digest(base.TEST_SI)},
        },
        "protocol": {
            "cycles": ROWS,
            "first_cycle": 0,
            "last_cycle": ROWS - 1,
            "xorshift_semantics": "wide Int through all three XOR/shift statements; one low-17-bit mask only at extraction",
            "complete_assignment_permutation": True,
            "zero_assignment_cycles": [0],
            "sequence_u24le_sha256": sha256(
                b"".join(value.to_bytes(3, "little") for value in sequence)
            ).hexdigest(),
        },
        "component_inventory": inventory,
        "component_kind_count": len(inventory),
        "all_hidden_wireable_outputs_false": all(
            not row["hidden_wireable_outputs"] for row in inventory
        ),
        "baseline": {
            **semantic,
            "live_node_count": len(nodes),
            "current_cycle_truth_class_count": len(current_aliases),
            "outputs": list(OUTPUT_NAMES),
        },
        "named_carry_chain": carry_rows,
        "assets": {
            "history": {
                **history_summary,
                "direct_targets": history_direct,
            },
            "autonomous_phase": {
                "enumeration": phase_enumeration,
                "unique_phase_count": len(phases),
                "direct_targets": phase_direct,
                "cofactor_residuals": phase_cofactors,
            },
            "normalizer_and_z": normalizer,
            "word_lane": word,
            "switch_bus": bus,
        },
        "dynamic_searches": {
            "one_component": one_component,
            "and3_or3_short_arc": three_input,
            "full_adder_joint": fulladder,
            "full_adder_ripple_suffix": ripple,
        },
        "decisive_results": {
            "history_direct_named_or_output_match_count": history_direct["exact_match_count"],
            "phase_direct_named_or_output_match_count": phase_direct["exact_match_count"],
            "undominated_nonrecursive_one_component_match_count": one_component[
                "undominated_nonrecursive_match_count"
            ],
            "undominated_nonrecursive_dynamic_carry_matches": dynamic_carry_hits,
            "score_improving_dynamic_connected_cut_count": len(score_improving_dynamic_cuts),
            "score_improving_dynamic_connected_cuts": score_improving_dynamic_cuts,
            "score_improving_ripple_suffix_count": len(ripple_score_improving),
            "score_improving_ripple_suffixes": ripple_score_improving,
            "normalizable_partial_carry_count": sum(
                bool(row["carry_data_plane_matches"])
                for row in normalizer["partial_live_nodes"]
            ),
            "word_width_discount_found": word["width_discount_found"],
            "dynamic_fulladder_joint_match_count": fulladder[
                "dynamic_joint_exact_match_count"
            ],
            "nonrecursive_phase_bus_physical_match_count": bus[
                "nonrecursive_physical_exact_match_count"
            ],
            "nonrecursive_phase_bus_normalized_match_count": bus[
                "nonrecursive_normalized_exact_match_count"
            ],
        },
        "interpretation": {
            "positive_asset": "Maker/Splitter can jointly turn the four partial carry BUS data planes into active C1/C3/C5/C7 owners at 0/0, but the clones depend on those BUSes and do not delete their cones.",
            "history_rule": "Every history rail includes the physical Delay cost 5 and arrival +4; no timeout or failed recipe is treated as UNSAT.",
            "fulladder_rule": "The legal 7/4 ordinary-gate expansion exposes G/K/P/T/N and gives the late carry input a two-gate path to both public outputs; native kind15 remains 16/8 in the current imported frontier.",
            "word_rule": "Word primitives add shared packaging/enable ownership but no cross-lane Boolean discount under the current score formulas.",
            "replacement_rule": "Only nonrecursive exact matches with connected-cut and full arrival propagation may be score candidates; implications, recursive clones, and cofactor feasibility are assets rather than replacements.",
        },
    }
    OUTPUT.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"output={OUTPUT}", flush=True)
    print(f"sha256={digest(OUTPUT)}", flush=True)
    print(json.dumps(report["decisive_results"], ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
