#!/usr/bin/env python3
"""Check tick-zero routing for a fixed 61-XOR, 65-cycle RNG.

This research-only model leaves the checked-in steady-state B/C DAG unchanged.
The state Delay Bits start at zero, the Architecture Input is enabled only on
tick zero, and the single Architecture Output is enabled on every tick.  The
load labels therefore have to satisfy::

    feedback B nodes: T*A
    visible C nodes:  A

Two physical phase-routing families can be checked:

* ``early``: a seed bit and a switched state bit share a layer-one XOR input.
  Each distinct (seed,state) pair costs a Bit Switch (2 gates), and the pairs
  form a real source/state bipartite matching.  A zero-load late OR costs one.
  The longest path is at most delay 9.
* ``standard``: OR(seed,state) is used at a layer-one XOR input.  Repeated
  sources are ordinary fanout and each distinct pair costs one gate.  Late ORs
  remain available.  The seed-control path may reach delay 10.

The script never reads or writes a Turing Complete save and caps Z3 at 768 MB.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path
import random
import sys
from typing import Any, Sequence


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import tc_save_lab.rng_encoded_asic as rng  # noqa: E402


BITS = 32
MASK = (1 << BITS) - 1
DEFAULT_RESULT = Path(__file__).with_name("cycle65_fixed_certificate.json")
ROUTING_MODES = ("early", "standard")


def network_fingerprint() -> str:
    payload = {
        "A": [f"{row:08x}" for row in rng.A],
        "T": [f"{row:08x}" for row in rng.T],
        "B": [f"{row:08x}" for row in rng.B],
        "C": [f"{row:08x}" for row in rng.C],
        "gates": [
            [f"{gate.output:08x}", f"{gate.left:08x}", f"{gate.right:08x}", gate.depth]
            for gate in rng.GATES
        ],
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return sha256(encoded).hexdigest()


def _node_class(node: int) -> str:
    if node in rng.DIRECT:
        return "direct"
    if node in rng.FIRST_LAYER:
        return "first"
    return "second"


def _load_weight_bound(node: int) -> int:
    """Return a topology-only upper bound for either routing family.

    Each first-layer XOR has two inputs and an input occurrence can receive at
    most one seed bit.  A late OR can replace only an identically-zero load
    label with one seed bit, so it cannot raise these bounds.
    """

    return {"direct": 1, "first": 2, "second": 4}[_node_class(node)]


def static_obstructions() -> list[dict[str, Any]]:
    ta = rng.compose(rng.T, rng.A)
    result: list[dict[str, Any]] = []
    for branch, nodes, wanted_rows in (
        ("B_feedback", rng.B, ta),
        ("C_output", rng.C, rng.A),
    ):
        for index, (node, wanted) in enumerate(zip(nodes, wanted_rows)):
            bound = _load_weight_bound(node)
            weight = wanted.bit_count()
            if weight > bound:
                result.append(
                    {
                        "branch": branch,
                        "index": index,
                        "steady_node": f"{node:08x}",
                        "node_class": _node_class(node),
                        "required_label": f"{wanted:08x}",
                        "required_weight": weight,
                        "topology_weight_upper_bound": bound,
                    }
                )
    return result


def build_solver(
    routing_mode: str,
    *,
    budget: int | None,
    timeout_ms: int,
) -> tuple[Any, dict[str, Any]]:
    try:
        import z3
    except ImportError as error:  # pragma: no cover - optional dependency
        raise SystemExit("install z3-solver in the project venv") from error

    if routing_mode not in ROUTING_MODES:
        raise ValueError(f"unknown routing mode {routing_mode!r}")

    solver = z3.Solver()
    solver.set(timeout=timeout_ms, max_memory=768)

    first_gates = tuple(gate for gate in rng.GATES if gate.depth == 1)

    # A layer-one input occurrence may receive at most one direct seed bit.
    # Its steady source is the corresponding q bit encoded by the unit leaf.
    input_choice: dict[tuple[int, int, int], Any] = {}
    occurrences_by_pair: dict[tuple[int, int], list[Any]] = defaultdict(list)
    for gate in first_gates:
        state_bits = rng.bits(gate.output)
        for side, state_bit in enumerate(state_bits):
            choices = []
            for seed_bit in range(BITS):
                variable = z3.Bool(
                    f"input_{routing_mode}_{gate.output:08x}_{side}_{seed_bit}"
                )
                input_choice[(gate.output, side, seed_bit)] = variable
                occurrences_by_pair[(seed_bit, state_bit)].append(variable)
                choices.append(variable)
            solver.add(z3.AtMost(*choices, 1))

    input_used: dict[tuple[int, int], Any] = {}
    for pair, occurrences in sorted(occurrences_by_pair.items()):
        variable = z3.Bool(f"input_pair_{pair[0]}_{pair[1]}")
        input_used[pair] = variable
        solver.add(variable == z3.Or(*occurrences))

    if routing_mode == "early":
        # A source pin can belong to only one independent three-state net.
        # Repeated occurrences of the exact same pair are ordinary fanout.
        for seed_bit in range(BITS):
            solver.add(
                z3.AtMost(
                    *(variable for (seed, _state), variable in input_used.items()
                      if seed == seed_bit),
                    1,
                )
            )
        for state_bit in range(BITS):
            solver.add(
                z3.AtMost(
                    *(variable for (_seed, state), variable in input_used.items()
                      if state == state_bit),
                    1,
                )
            )

    first_label: dict[int, tuple[Any, ...]] = {}
    for gate in first_gates:
        first_label[gate.output] = tuple(
            z3.Xor(
                input_choice[(gate.output, 0, seed_bit)],
                input_choice[(gate.output, 1, seed_bit)],
            )
            for seed_bit in range(BITS)
        )

    false_label = tuple(z3.BoolVal(False) for _ in range(BITS))

    def base_label(node: int) -> tuple[Any, ...]:
        if node in rng.DIRECT:
            return false_label
        return first_label[node]

    # A consumer may use its steady node directly or a late OR version.  ORs
    # with the same (seed,node) pair are one physical component and can fan out.
    late_choice: dict[tuple[str, int], tuple[Any, ...]] = {}
    late_occurrences_by_pair: dict[tuple[int, int], list[Any]] = defaultdict(list)

    def selectable(node: int, tag: str) -> tuple[Any, ...]:
        key = (tag, node)
        choices = tuple(
            z3.Bool(f"late_{tag}_{node:08x}_{bit}") for bit in range(BITS)
        )
        late_choice[key] = choices
        solver.add(z3.AtMost(*choices, 1))
        base = base_label(node)
        is_zero = z3.And(*(z3.Not(coefficient) for coefficient in base))
        for seed_bit, choice in enumerate(choices):
            # OR is a valid linear phase injection only when its other tick-zero
            # input is identically zero for every seed.
            solver.add(z3.Implies(choice, is_zero))
            late_occurrences_by_pair[(seed_bit, node)].append(choice)
        return tuple(
            z3.Xor(base[bit], choices[bit]) for bit in range(BITS)
        )

    wanted_ta = rng.compose(rng.T, rng.A)
    consumers = (
        *(('b', index, node, wanted) for index, (node, wanted) in enumerate(zip(rng.B, wanted_ta))),
        *(('c', index, node, wanted) for index, (node, wanted) in enumerate(zip(rng.C, rng.A))),
    )

    raw_label: dict[tuple[str, int], tuple[Any, ...]] = {}
    for branch, index, target, _wanted in consumers:
        key = (branch, index)
        if target in rng.DIRECT or target in rng.FIRST_LAYER:
            raw_label[key] = base_label(target)
            continue
        gate = rng.GATE_BY_OUTPUT[target]
        left = selectable(gate.left, f"{branch}{index}_left")
        right = selectable(gate.right, f"{branch}{index}_right")
        raw_label[key] = tuple(
            z3.Xor(left[bit], right[bit]) for bit in range(BITS)
        )

    # A final late OR is legal only if the whole raw target label is zero.
    final_choice: dict[tuple[str, int], tuple[Any, ...]] = {}
    for branch, index, target, wanted in consumers:
        key = (branch, index)
        choices = tuple(
            z3.Bool(f"final_{branch}{index}_{bit}") for bit in range(BITS)
        )
        final_choice[key] = choices
        solver.add(z3.AtMost(*choices, 1))
        is_zero = z3.And(*(z3.Not(value) for value in raw_label[key]))
        for seed_bit, choice in enumerate(choices):
            solver.add(z3.Implies(choice, is_zero))
            late_occurrences_by_pair[(seed_bit, target)].append(choice)
        for seed_bit in range(BITS):
            actual = z3.Xor(raw_label[key][seed_bit], choices[seed_bit])
            solver.add(actual == bool((wanted >> seed_bit) & 1))

    late_used: dict[tuple[int, int], Any] = {}
    for pair, occurrences in sorted(late_occurrences_by_pair.items()):
        variable = z3.Bool(f"late_pair_{pair[0]}_{pair[1]:08x}")
        late_used[pair] = variable
        solver.add(variable == z3.Or(*occurrences))

    input_cost = 2 if routing_mode == "early" else 1
    weighted = [(variable, input_cost) for variable in input_used.values()]
    weighted.extend((variable, 1) for variable in late_used.values())
    if budget is not None:
        solver.add(z3.PbLe(weighted, budget))

    context = {
        "routing_mode": routing_mode,
        "budget": budget,
        "input_cost": input_cost,
        "input_choice": input_choice,
        "input_used": input_used,
        "late_choice": late_choice,
        "final_choice": final_choice,
        "late_used": late_used,
    }
    return solver, context


def solve(
    routing_mode: str,
    *,
    budget: int | None,
    timeout_ms: int,
) -> dict[str, Any]:
    import z3

    solver, context = build_solver(
        routing_mode, budget=budget, timeout_ms=timeout_ms
    )
    result = solver.check()
    payload: dict[str, Any] = {
        "status": str(result),
        "budget": budget,
        "reason": solver.reason_unknown() if result == z3.unknown else "",
    }
    if result != z3.sat:
        return payload

    model = solver.model()
    input_used = context["input_used"]
    late_used = context["late_used"]
    input_pairs = sorted(
        pair for pair, variable in input_used.items()
        if z3.is_true(model.eval(variable))
    )
    late_pairs = sorted(
        pair for pair, variable in late_used.items()
        if z3.is_true(model.eval(variable))
    )
    input_occurrences = sorted(
        [f"{node:08x}", side, seed, rng.bits(node)[side]]
        for (node, side, seed), variable in context["input_choice"].items()
        if z3.is_true(model.eval(variable))
    )
    late_occurrences = sorted(
        [tag, f"{node:08x}", bit]
        for (tag, node), choices in context["late_choice"].items()
        for bit, variable in enumerate(choices)
        if z3.is_true(model.eval(variable))
    )
    final_occurrences = sorted(
        [branch, index, bit]
        for (branch, index), choices in context["final_choice"].items()
        for bit, variable in enumerate(choices)
        if z3.is_true(model.eval(variable))
    )
    phase_cost = context["input_cost"] * len(input_pairs) + len(late_pairs)
    payload["certificate"] = {
        "phase_cost": phase_cost,
        "input_pair_cost": context["input_cost"],
        "input_pairs": [[seed, state] for seed, state in input_pairs],
        "late_pairs": [[seed, f"{node:08x}"] for seed, node in late_pairs],
        "input_occurrences": input_occurrences,
        "late_occurrences": late_occurrences,
        "final_occurrences": final_occurrences,
    }
    return payload


def apply_matrix(matrix: Sequence[int], value: int) -> int:
    return sum(
        ((row & value).bit_count() & 1) << bit
        for bit, row in enumerate(matrix)
    )


def verify_cycle_protocol() -> dict[str, Any]:
    ta = rng.compose(rng.T, rng.A)
    if rng.compose(rng.C, rng.T) != rng.A:
        raise AssertionError("C*T != A")
    if rng.compose(rng.T, rng.C) != rng.B:
        raise AssertionError("T*C != B")

    seeds = [0, 1, 2, 0x12345678, MASK]
    generator = random.Random(20260802)
    seeds.extend(generator.getrandbits(BITS) for _ in range(64))
    for seed in seeds:
        q = 0
        expected = seed
        for tick in range(65):
            if tick == 0:
                output = apply_matrix(rng.A, seed)
                next_q = apply_matrix(ta, seed)
            else:
                output = apply_matrix(rng.C, q)
                next_q = apply_matrix(rng.B, q)
            expected = rng.xorshift32(expected)
            if output != expected:
                raise AssertionError(
                    f"seed {seed:08x} tick {tick}: {output:08x} != {expected:08x}"
                )
            if next_q != apply_matrix(rng.T, expected):
                raise AssertionError("encoded next-state invariant failed")
            q = next_q
    return {
        "seed_count": len(seeds),
        "outputs_per_seed": 65,
        "tick0_output": "A*seed",
        "tick0_feedback": "T*A*seed",
        "steady_output": "C*q",
        "steady_feedback": "B*q",
    }


def verify_result(payload: dict[str, Any]) -> None:
    if payload["network_fingerprint_sha256"] != network_fingerprint():
        raise AssertionError("fixed network fingerprint changed")
    if payload["matrix_identities"] != {
        "C*T=A": True,
        "T*C=B": True,
        "tick0_feedback=T*A": True,
    }:
        raise AssertionError("matrix identity record changed")
    expected_obstructions = static_obstructions()
    if payload["static_obstructions"] != expected_obstructions:
        raise AssertionError("static obstruction record changed")
    if not expected_obstructions:
        raise AssertionError("expected at least one topology obstruction")
    for obstruction in expected_obstructions:
        if obstruction["required_weight"] <= obstruction["topology_weight_upper_bound"]:
            raise AssertionError("invalid static obstruction")
    expected_results = {
        "early_budget_88",
        "early_unbounded",
        "standard_budget_44",
        "standard_unbounded",
    }
    if set(payload["results"]) != expected_results:
        raise AssertionError("solver result set changed")
    for name, result in payload["results"].items():
        if result["status"] != "unsat":
            raise AssertionError(f"saved result {name} is not UNSAT")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout-ms", type=int, default=120_000)
    parser.add_argument("--output", type=Path, default=DEFAULT_RESULT)
    parser.add_argument(
        "--verify-existing",
        type=Path,
        help="verify a saved fixed-DAG UNSAT/topology certificate without Z3",
    )
    args = parser.parse_args()

    if args.verify_existing is not None:
        payload = json.loads(args.verify_existing.read_text(encoding="utf-8"))
        verify_cycle_protocol()
        verify_result(payload)
        print(f"verified {args.verify_existing}")
        return 0

    ta = rng.compose(rng.T, rng.A)
    payload: dict[str, Any] = {
        "schema": 1,
        "scope": "fixed current 61-XOR B/C DAG; init0; one output; 65 cycles",
        "network_fingerprint_sha256": network_fingerprint(),
        "matrix_identities": {
            "C*T=A": rng.compose(rng.C, rng.T) == rng.A,
            "T*C=B": rng.compose(rng.T, rng.C) == rng.B,
            "tick0_feedback=T*A": ta == rng.compose(rng.T, rng.A),
        },
        "cycle_protocol": verify_cycle_protocol(),
        "timing": {
            "early_seed": "phase Delay 4 + NOT 1 + XOR 2 + XOR 2 = 9",
            "early_state": "state Delay 4 + Bit Switch 1 + XOR 2 + XOR 2 = 9",
            "late_seed": "phase Delay 4 + NOT 1 + OR 1 + at most one XOR 2 <= 8",
            "late_state": "state Delay 4 + XOR 2 + OR 1 + XOR 2 <= 9",
            "standard_seed": "phase Delay 4 + NOT 1 + OR 1 + XOR 2 + XOR 2 = 10",
        },
        "accounting": {
            "fixed_base_gate": 166 + 61 * 3,
            "fixed_base_breakdown": "32 Delay Bit=160, phase Delay+NOT=6, 61 XOR=183",
            "early_delay9_phase_budget_for_gate437": 88,
            "standard_delay10_phase_budget_for_gate393": 44,
        },
        "static_bound": {
            "direct_target_max_load_weight": 1,
            "first_layer_target_max_load_weight": 2,
            "second_layer_target_max_load_weight": 4,
            "late_or_rule": "other tick-zero label must be identically zero",
            "conclusion": "a required row above its target bound makes the model infeasible at every phase budget",
            "minimum_phase_cost": "infinite (no feasible labeling in either modeled routing family)",
        },
        "static_obstructions": static_obstructions(),
        "results": {},
    }

    checks = (
        ("early_budget_88", "early", 88),
        ("early_unbounded", "early", None),
        ("standard_budget_44", "standard", 44),
        ("standard_unbounded", "standard", None),
    )
    for name, mode, budget in checks:
        result = solve(mode, budget=budget, timeout_ms=args.timeout_ms)
        payload["results"][name] = result
        suffix = "unbounded" if budget is None else f"cost <= {budget}"
        print(f"{mode} {suffix}: {result['status']}")

    verify_result(payload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(
        f"static obstructions: {len(payload['static_obstructions'])}; wrote {args.output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
