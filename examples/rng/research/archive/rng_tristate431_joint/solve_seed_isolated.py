"""Search the fixed RNG XOR DAG with seed-isolated EARLY buses.

This is a research-only model.  It imports the checked-in B/C/T certificate and
does not read or write the live Turing Complete save.

The model assumes that each selected ``seed_i`` is already available as a U1
tri-state source.  The current level input is one U32 tri-state port, while the
game's Splitter32/Splitter8 components actively drive their outputs when that
port is Z.  Consequently a SAT result here is a conditional algebraic
certificate, not by itself a game-valid physical construction.

The timing-safe construction family has two kinds of phase injection:

* EARLY(seed_i, q_j): seed_i directly drives a layer-one XOR input during the
  load tick; q_j drives the same net through a Bit Switch during steady state.
  Cost: 2 gates.  A seed source may belong to only one independent EARLY bus.
  A q source may fan out to several Bit Switch inputs because the Switch
  outputs, not their inputs, are the mutually isolated tri-state drivers.
* LATE(seed_i, n): OR seed_i into a node whose load-tick value is identically
  zero.  A late OR may feed only a layer-two XOR input or a final output, hence
  the seed-control path contains at most OR + one XOR.  Cost: 1 gate.

With ready Delay=4, NOT=1, Switch/OR=1 and XOR=2, both routes have total delay
at most nine.  Z3 checks the 32 exact T(seed) feedback labels and minimizes
``2 * early_pairs + late_pairs``.  This script deliberately differs from the
older double-sided matching model in ``rng_phase_delay9``.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import tc_save_lab.rng_encoded_asic as rng  # noqa: E402


BITS = 32
DEFAULT_RESULT = Path(__file__).with_name("seed_isolated_certificate.json")


def xor_all(z3: Any, values: list[Any]) -> Any:
    if not values:
        return z3.BoolVal(False)
    if len(values) == 1:
        return values[0]
    return z3.Xor(*values)


def solve(
    budget: int,
    timeout_ms: int,
    *,
    exact_early: int | None,
    exact_late: int | None,
    max_late: int | None,
) -> tuple[str, dict[str, Any] | None, str]:
    try:
        import z3
    except ImportError as error:  # pragma: no cover - optional research dependency
        raise SystemExit("install z3-solver in the project venv") from error

    solver = z3.Solver()
    solver.set(timeout=timeout_ms, max_memory=640)

    first_gates = tuple(gate for gate in rng.GATES if gate.depth == 1)
    second_gates = tuple(gate for gate in rng.GATES if gate.depth == 2)

    # A layer-one input occurrence may receive one direct seed source.
    early_choice: dict[tuple[int, int, int], Any] = {}
    early_occurrences_by_pair: dict[tuple[int, int], list[Any]] = defaultdict(list)
    for gate in first_gates:
        for side, state_bit in enumerate(rng.bits(gate.output)):
            choices = []
            for seed_bit in range(BITS):
                variable = z3.Bool(f"early_{gate.output:08x}_{side}_{seed_bit}")
                early_choice[(gate.output, side, seed_bit)] = variable
                early_occurrences_by_pair[(seed_bit, state_bit)].append(variable)
                choices.append(variable)
            solver.add(z3.AtMost(*choices, 1))

    early_used: dict[tuple[int, int], Any] = {}
    for pair, occurrences in sorted(early_occurrences_by_pair.items()):
        variable = z3.Bool(f"early_pair_{pair[0]}_{pair[1]}")
        early_used[pair] = variable
        solver.add(variable == z3.Or(*occurrences))

    # One seed pin cannot drive two independent EARLY buses: that would wire
    # the buses together.  A q pin may fan out to multiple Switch inputs; each
    # Switch output remains an independent tri-state bus.
    for seed_bit in range(BITS):
        solver.add(
            z3.AtMost(
                *(early_used[pair] for pair in early_used if pair[0] == seed_bit),
                1,
            )
        )

    first_label: dict[int, tuple[Any, ...]] = {}
    for gate in first_gates:
        first_label[gate.output] = tuple(
            z3.Xor(
                early_choice[(gate.output, 0, seed_bit)],
                early_choice[(gate.output, 1, seed_bit)],
            )
            for seed_bit in range(BITS)
        )

    false_label = tuple(z3.BoolVal(False) for _ in range(BITS))

    def base_label(node: int) -> tuple[Any, ...]:
        if node in rng.DIRECT:
            return false_label
        return first_label[node]

    # Each consumer can use its steady node directly or a late OR version.
    # Equal (seed,node) pairs share one physical OR and therefore one cost.
    late_choice: dict[tuple[str, int], tuple[Any, ...]] = {}
    late_occurrences_by_pair: dict[tuple[int, int], list[Any]] = defaultdict(list)

    def selectable(node: int, tag: str) -> tuple[Any, ...]:
        key = (tag, node)
        if key in late_choice:
            return tuple(
                z3.Xor(base_label(node)[bit], late_choice[key][bit])
                for bit in range(BITS)
            )
        choices = tuple(z3.Bool(f"late_{tag}_{node:08x}_{bit}") for bit in range(BITS))
        late_choice[key] = choices
        solver.add(z3.AtMost(*choices, 1))
        # OR(seed_i, node) stays linear only when node is zero during load.
        for choice in choices:
            solver.add(z3.Implies(choice, z3.And(*(z3.Not(c) for c in base_label(node)))))
        for seed_bit, choice in enumerate(choices):
            late_occurrences_by_pair[(seed_bit, node)].append(choice)
        return tuple(
            z3.Xor(base_label(node)[bit], choices[bit]) for bit in range(BITS)
        )

    raw_feedback: list[tuple[Any, ...]] = []
    for index, target in enumerate(rng.B):
        if target in rng.DIRECT or target in rng.FIRST_LAYER:
            raw_feedback.append(base_label(target))
            continue
        gate = rng.GATE_BY_OUTPUT[target]
        left = selectable(gate.left, f"b{index}_left")
        right = selectable(gate.right, f"b{index}_right")
        raw_feedback.append(
            tuple(z3.Xor(left[bit], right[bit]) for bit in range(BITS))
        )

    # A final late OR is also timing-safe and can be shared with a late OR used
    # at a layer-two input when the steady node and seed bit are the same.
    final_choice: dict[int, tuple[Any, ...]] = {}
    for index, (target, wanted) in enumerate(zip(rng.B, rng.T)):
        choices = tuple(z3.Bool(f"final_b{index}_{bit}") for bit in range(BITS))
        final_choice[index] = choices
        solver.add(z3.AtMost(*choices, 1))
        for choice in choices:
            solver.add(
                z3.Implies(
                    choice,
                    z3.And(*(z3.Not(c) for c in raw_feedback[index])),
                )
            )
        for seed_bit, choice in enumerate(choices):
            late_occurrences_by_pair[(seed_bit, target)].append(choice)
        for seed_bit in range(BITS):
            actual = z3.Xor(raw_feedback[index][seed_bit], choices[seed_bit])
            solver.add(actual == bool((wanted >> seed_bit) & 1))

    late_used: dict[tuple[int, int], Any] = {}
    for pair, occurrences in sorted(late_occurrences_by_pair.items()):
        variable = z3.Bool(f"late_pair_{pair[0]}_{pair[1]:08x}")
        late_used[pair] = variable
        solver.add(variable == z3.Or(*occurrences))

    weighted = [(variable, 2) for variable in early_used.values()]
    weighted.extend((variable, 1) for variable in late_used.values())
    if exact_early is not None:
        solver.add(z3.PbEq([(variable, 1) for variable in early_used.values()], exact_early))
    if exact_late is not None:
        solver.add(z3.PbEq([(variable, 1) for variable in late_used.values()], exact_late))
    elif max_late is not None:
        solver.add(z3.PbLe([(variable, 1) for variable in late_used.values()], max_late))
    solver.add(z3.PbLe(weighted, budget))

    result = solver.check()
    if result == z3.unknown:
        return "unknown", None, solver.reason_unknown()
    if result == z3.unsat:
        return "unsat", None, ""

    model = solver.model()
    chosen_early = sorted(
        pair for pair, variable in early_used.items() if z3.is_true(model.eval(variable))
    )
    chosen_late = sorted(
        pair for pair, variable in late_used.items() if z3.is_true(model.eval(variable))
    )
    occurrence_early = []
    for (node, side, seed_bit), variable in sorted(early_choice.items()):
        if z3.is_true(model.eval(variable)):
            state_bit = rng.bits(node)[side]
            occurrence_early.append([f"{node:08x}", side, seed_bit, state_bit])
    occurrence_late = []
    for (tag, node), choices in sorted(late_choice.items()):
        for seed_bit, variable in enumerate(choices):
            if z3.is_true(model.eval(variable)):
                occurrence_late.append([tag, f"{node:08x}", seed_bit])
    final_late = []
    for index, choices in sorted(final_choice.items()):
        for seed_bit, variable in enumerate(choices):
            if z3.is_true(model.eval(variable)):
                final_late.append([index, f"{rng.B[index]:08x}", seed_bit])

    certificate = {
        "schema": 2,
        "budget": budget,
        "phase_cost": 2 * len(chosen_early) + len(chosen_late),
        "early_pair_count": len(chosen_early),
        "late_pair_count": len(chosen_late),
        "early_pairs": [[seed, state] for seed, state in chosen_early],
        "late_pairs": [[seed, f"{node:08x}"] for seed, node in chosen_late],
        "early_occurrences": occurrence_early,
        "late_occurrences": occurrence_late,
        "final_late_occurrences": final_late,
        "seed_isolation": True,
        "state_switch_fanout": True,
        "requested_exact_early": exact_early,
        "requested_exact_late": exact_late,
        "requested_max_late": max_late,
        "encoding_rows": [f"{row:08x}" for row in rng.T],
        "feedback_refs": [f"{row:08x}" for row in rng.B],
        "output_refs": [f"{row:08x}" for row in rng.C],
        "steady_xor_gates": [
            {
                "output": f"{gate.output:08x}",
                "left": f"{gate.left:08x}",
                "right": f"{gate.right:08x}",
                "depth": gate.depth,
            }
            for gate in rng.GATES
        ],
    }
    return "sat", certificate, ""


def verify_certificate(certificate: dict[str, Any]) -> None:
    expected_gates = [
        {
            "output": f"{gate.output:08x}",
            "left": f"{gate.left:08x}",
            "right": f"{gate.right:08x}",
            "depth": gate.depth,
        }
        for gate in rng.GATES
    ]
    if certificate.get("encoding_rows") != [f"{row:08x}" for row in rng.T]:
        raise AssertionError("encoding T rows changed")
    if certificate.get("feedback_refs") != [f"{row:08x}" for row in rng.B]:
        raise AssertionError("feedback B references changed")
    if certificate.get("output_refs") != [f"{row:08x}" for row in rng.C]:
        raise AssertionError("output C references changed")
    if certificate.get("steady_xor_gates") != expected_gates:
        raise AssertionError("steady 61-XOR DAG changed")

    early_occurrences = certificate["early_occurrences"]
    if len({(node, int(side)) for node, side, _seed, _state in early_occurrences}) != len(
        early_occurrences
    ):
        raise AssertionError("duplicate EARLY occurrence")
    early_by_occurrence = {
        (int(node, 16), int(side)): int(seed)
        for node, side, seed, _state in early_occurrences
    }
    early_pairs = {
        (int(seed), int(state)) for seed, state in certificate["early_pairs"]
    }
    late_pairs = {
        (int(seed), int(node, 16)) for seed, node in certificate["late_pairs"]
    }
    if 2 * len(early_pairs) + len(late_pairs) != certificate["phase_cost"]:
        raise AssertionError("phase cost mismatch")
    if certificate["phase_cost"] > certificate["budget"]:
        raise AssertionError("phase cost exceeds certificate budget")
    exact_early = certificate.get("requested_exact_early")
    if exact_early is not None and len(early_pairs) != exact_early:
        raise AssertionError("EARLY count does not meet requested equality")
    max_late = certificate.get("requested_max_late")
    if max_late is not None and len(late_pairs) > max_late:
        raise AssertionError("LATE count exceeds requested maximum")
    exact_late = certificate.get("requested_exact_late")
    if exact_late is not None and len(late_pairs) != exact_late:
        raise AssertionError("LATE count does not meet requested equality")
    if not certificate.get("seed_isolation"):
        raise AssertionError("certificate does not claim seed isolation")
    if len({seed for seed, _state in early_pairs}) != len(early_pairs):
        raise AssertionError("one seed source drives multiple EARLY buses")

    first: dict[int, int] = {}
    used_early_pairs: set[tuple[int, int]] = set()
    for gate in (gate for gate in rng.GATES if gate.depth == 1):
        label = 0
        state_bits = rng.bits(gate.output)
        for side, state_bit in enumerate(state_bits):
            seed_bit = early_by_occurrence.get((gate.output, side))
            if seed_bit is not None:
                if (seed_bit, state_bit) not in early_pairs:
                    raise AssertionError("early occurrence lacks its physical pair")
                used_early_pairs.add((seed_bit, state_bit))
                label ^= 1 << seed_bit
        first[gate.output] = label
    if used_early_pairs != early_pairs:
        raise AssertionError("EARLY pair set does not equal its occurrences")

    late_occurrences = certificate["late_occurrences"]
    if len({(tag, node) for tag, node, _seed in late_occurrences}) != len(
        late_occurrences
    ):
        raise AssertionError("duplicate LATE occurrence")
    late_by_occurrence = {
        (tag, int(node, 16)): int(seed)
        for tag, node, seed in late_occurrences
    }
    final_occurrences = certificate["final_late_occurrences"]
    if len({int(index) for index, _node, _seed in final_occurrences}) != len(
        final_occurrences
    ):
        raise AssertionError("duplicate final LATE occurrence")
    final_by_index = {
        int(index): int(seed)
        for index, _node, seed in final_occurrences
    }
    used_late_pairs: set[tuple[int, int]] = set()

    def base(node: int) -> int:
        return 0 if node in rng.DIRECT else first[node]

    def selected(node: int, tag: str) -> int:
        value = base(node)
        seed_bit = late_by_occurrence.get((tag, node))
        if seed_bit is None:
            return value
        if value:
            raise AssertionError("late OR input is nonzero during load")
        if (seed_bit, node) not in late_pairs:
            raise AssertionError("late occurrence lacks its physical OR pair")
        used_late_pairs.add((seed_bit, node))
        return 1 << seed_bit

    for index, (target, wanted) in enumerate(zip(rng.B, rng.T)):
        if target in rng.DIRECT or target in rng.FIRST_LAYER:
            actual = base(target)
        else:
            gate = rng.GATE_BY_OUTPUT[target]
            actual = selected(gate.left, f"b{index}_left") ^ selected(
                gate.right, f"b{index}_right"
            )
        if index in final_by_index:
            if actual:
                raise AssertionError("final late OR input is nonzero during load")
            seed_bit = final_by_index[index]
            if (seed_bit, target) not in late_pairs:
                raise AssertionError("final late OR lacks its physical pair")
            used_late_pairs.add((seed_bit, target))
            actual = 1 << seed_bit
        if actual != wanted:
            raise AssertionError(
                f"T[{index}] mismatch: {actual:08x} != {wanted:08x}"
            )
    if used_late_pairs != late_pairs:
        raise AssertionError("LATE pair set does not equal its occurrences")

    # Structural timing proof in current component delays.
    if 4 + 1 + 2 * 2 > 9:  # ready Delay + NOT + two XORs
        raise AssertionError("early seed-control path exceeds delay nine")
    if 4 + 1 + 2 * 2 > 9:  # ready Delay + Switch + two XORs
        raise AssertionError("early steady-control path exceeds delay nine")
    if 4 + 1 + 1 + 2 > 9:  # ready Delay + NOT + OR + one XOR
        raise AssertionError("late seed-control path exceeds delay nine")
    if 4 + 2 + 1 + 2 > 9:  # q Delay + layer-one XOR + OR + layer-two XOR
        raise AssertionError("late feedback path exceeds delay nine")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--budget", type=int, default=82)
    parser.add_argument("--timeout-ms", type=int, default=120_000)
    parser.add_argument("--output", type=Path, default=DEFAULT_RESULT)
    parser.add_argument("--check-lower", action="store_true")
    parser.add_argument("--exact-early", type=int)
    parser.add_argument("--exact-late", type=int)
    parser.add_argument("--max-late", type=int)
    parser.add_argument(
        "--verify-existing",
        type=Path,
        help="verify every SAT certificate in an existing JSON without Z3",
    )
    args = parser.parse_args()
    if args.exact_late is not None and args.max_late is not None:
        parser.error("--exact-late and --max-late are mutually exclusive")

    if args.verify_existing is not None:
        payload = json.loads(args.verify_existing.read_text(encoding="utf-8"))
        count = 0
        for result in payload["results"].values():
            certificate = result.get("certificate")
            if certificate is not None:
                verify_certificate(certificate)
                count += 1
        if not count:
            raise SystemExit("existing JSON contains no SAT certificate")
        print(f"verified {count} certificate(s) from {args.verify_existing}")
        return

    budgets = [args.budget - 1, args.budget] if args.check_lower else [args.budget]
    summary: dict[str, Any] = {
        "model": "fixed B/C 61-XOR DAG; early switches; zero-load late ORs",
        "source_constraints": {
            "seed": "at most one distinct EARLY bus",
            "state": "unrestricted fanout to independent Bit Switch inputs",
        },
        "count_constraints": {
            "exact_early": args.exact_early,
            "exact_late": args.exact_late,
            "max_late": args.max_late,
        },
        "physical_realization_status": (
            "conditional algebraic certificate: requires Z-preserving U32-to-U1 "
            "seed breakout not supplied by current Splitter components"
        ),
        "timing": {
            "early_seed": "ready Delay 4 + NOT 1 + XOR 2 + XOR 2 = 9",
            "early_steady": "ready Delay 4 + Switch 1 + XOR 2 + XOR 2 = 9",
            "late_seed": "ready Delay 4 + NOT 1 + OR 1 + at most one XOR 2 <= 8",
            "late_feedback": "q Delay 4 + XOR 2 + OR 1 + XOR 2 <= 9",
        },
        "results": {},
    }
    best = None
    for budget in budgets:
        status, certificate, reason = solve(
            budget,
            args.timeout_ms,
            exact_early=args.exact_early,
            exact_late=args.exact_late,
            max_late=args.max_late,
        )
        summary["results"][str(budget)] = {"status": status, "reason": reason}
        print(f"phase cost <= {budget}: {status}{' (' + reason + ')' if reason else ''}")
        if certificate is not None:
            verify_certificate(certificate)
            summary["results"][str(budget)]["certificate"] = certificate
            best = certificate
            print(
                f"  early={certificate['early_pair_count']}, "
                f"late={certificate['late_pair_count']}, "
                f"cost={certificate['phase_cost']}"
            )
    if best is not None:
        summary["leaderboard_accounting"] = {
            "delay_bits": 160,
            "xor_61": 183,
            "phase": best["phase_cost"],
            "ready_and_not": 6,
            "total": 160 + 183 + best["phase_cost"] + 6,
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
