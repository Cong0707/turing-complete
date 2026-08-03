"""Prove the fixed RNG XOR DAG's minimum delay-nine phase-routing cost.

This is a research-only model.  It imports the checked-in B/C/T certificate and
does not read or write the live Turing Complete save.

The timing-safe construction family has two kinds of phase injection:

* EARLY(seed_i, q_j): seed_i directly drives a layer-one XOR input during the
  load tick; q_j drives the same net through a Bit Switch during steady state.
  Cost: 2 gates.  Selected pairs form an electrical matching by default.
  ``--relax-source-isolation`` enables a deliberately nonphysical lower-bound
  model in which repeated sources can be isolated for free.  Current
  Maker/Splitter components do not propagate Z and cannot realize that model.
* LATE(seed_i, n): OR seed_i into a node whose load-tick value is identically
  zero.  A late OR may feed only a layer-two XOR input or a final output, hence
  the seed-control path contains at most OR + one XOR.  Cost: 1 gate.

With ready Delay=4, NOT=1, Switch/OR=1 and XOR=2, both routes have total delay
at most nine.  Z3 checks the 32 exact T(seed) feedback labels and minimizes
``2 * early_pairs + late_pairs``.
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
DEFAULT_RESULT = Path(__file__).with_name("phase_cost_certificate.json")


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
    require_matching: bool,
    early_cost: int = 2,
    dimacs_output: Path | None = None,
) -> tuple[str, dict[str, Any] | None, str]:
    try:
        import z3
    except ImportError as error:  # pragma: no cover - optional research dependency
        raise SystemExit("install z3-solver in the project venv") from error

    solver = z3.Solver()
    solver.set(timeout=timeout_ms, max_memory=768)

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

    if require_matching:
        # Without zero-cost signal isolation, one source pin may belong to only
        # one independent multi-driver net.  Reuse of the same pair is fanout.
        for seed_bit in range(BITS):
            solver.add(
                z3.AtMost(
                    *(early_used[pair] for pair in early_used if pair[0] == seed_bit),
                    1,
                )
            )
        for state_bit in range(BITS):
            solver.add(
                z3.AtMost(
                    *(early_used[pair] for pair in early_used if pair[1] == state_bit),
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

    if early_cost not in (1, 2):
        raise ValueError(f"unsupported early cost {early_cost}")
    weighted = [(variable, early_cost) for variable in early_used.values()]
    weighted.extend((variable, 1) for variable in late_used.values())
    solver.add(z3.PbLe(weighted, budget))

    if dimacs_output is not None:
        dimacs_output.parent.mkdir(parents=True, exist_ok=True)
        goal = z3.Goal()
        goal.add(*solver.assertions())
        cnf_goals = z3.Then("simplify", "pb2bv", "bit-blast", "tseitin-cnf")(
            goal
        )
        if len(cnf_goals) != 1:
            raise RuntimeError(f"DIMACS conversion produced {len(cnf_goals)} goals")
        cnf_solver = z3.Solver()
        cnf_solver.add(*cnf_goals[0])
        dimacs_output.write_text(
            cnf_solver.dimacs(include_names=True), encoding="ascii"
        )

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
        "schema": 1,
        "budget": budget,
        "early_cost": early_cost,
        "phase_cost": early_cost * len(chosen_early) + len(chosen_late),
        "early_pair_count": len(chosen_early),
        "late_pair_count": len(chosen_late),
        "early_pairs": [[seed, state] for seed, state in chosen_early],
        "late_pairs": [[seed, f"{node:08x}"] for seed, node in chosen_late],
        "early_occurrences": occurrence_early,
        "late_occurrences": occurrence_late,
        "final_late_occurrences": final_late,
        "require_matching": require_matching,
    }
    return "sat", certificate, ""


def verify_certificate(certificate: dict[str, Any]) -> None:
    early_by_occurrence = {
        (int(node, 16), int(side)): int(seed)
        for node, side, seed, _state in certificate["early_occurrences"]
    }
    early_pairs = {
        (int(seed), int(state)) for seed, state in certificate["early_pairs"]
    }
    late_pairs = {
        (int(seed), int(node, 16)) for seed, node in certificate["late_pairs"]
    }
    early_cost = int(certificate.get("early_cost", 2))
    if early_cost * len(early_pairs) + len(late_pairs) != certificate["phase_cost"]:
        raise AssertionError("phase cost mismatch")
    if certificate["require_matching"]:
        if len({seed for seed, _state in early_pairs}) != len(early_pairs):
            raise AssertionError("early seed sources are not a matching")
        if len({state for _seed, state in early_pairs}) != len(early_pairs):
            raise AssertionError("early state sources are not a matching")

    first: dict[int, int] = {}
    for gate in (gate for gate in rng.GATES if gate.depth == 1):
        label = 0
        state_bits = rng.bits(gate.output)
        for side, state_bit in enumerate(state_bits):
            seed_bit = early_by_occurrence.get((gate.output, side))
            if seed_bit is not None:
                if (seed_bit, state_bit) not in early_pairs:
                    raise AssertionError("early occurrence lacks its physical pair")
                label ^= 1 << seed_bit
        first[gate.output] = label

    late_by_occurrence = {
        (tag, int(node, 16)): int(seed)
        for tag, node, seed in certificate["late_occurrences"]
    }
    final_by_index = {
        int(index): int(seed)
        for index, _node, seed in certificate["final_late_occurrences"]
    }

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
            actual = 1 << seed_bit
        if actual != wanted:
            raise AssertionError(
                f"T[{index}] mismatch: {actual:08x} != {wanted:08x}"
            )

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
    parser.add_argument(
        "--verify-existing",
        type=Path,
        help="verify every SAT certificate in an existing JSON without Z3",
    )
    parser.add_argument(
        "--relax-source-isolation",
        action="store_true",
        help="nonphysical lower bound: pretend repeated Z sources can be isolated for free",
    )
    parser.add_argument(
        "--early-or",
        action="store_true",
        help=(
            "67-cycle physical model: use one-gate ordinary OR(seed,q) leaves "
            "instead of two-gate tristate Switch leaves"
        ),
    )
    parser.add_argument(
        "--dimacs-output",
        type=Path,
        help="also export each checked budget as a DIMACS CNF before solving",
    )
    args = parser.parse_args()

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
    require_matching = not args.relax_source_isolation and not args.early_or
    early_cost = 1 if args.early_or else 2
    summary: dict[str, Any] = {
        "model": (
            "fixed B/C 61-XOR DAG; early ordinary ORs; zero-load late ORs"
            if args.early_or
            else "fixed B/C 61-XOR DAG; early switches; zero-load late ORs"
        ),
        "require_matching": require_matching,
        "early_cost": early_cost,
        "physical_realization_status": (
            "physical 67-cycle mode OR fanout; no Z isolation assumption"
            if args.early_or
            else (
                "nonphysical lower bound: current Splitters do not propagate Z"
                if args.relax_source_isolation
                else "physical source-isolation constraints enabled"
            )
        ),
        "timing": (
            {
                "early_seed": "load phase/input 4 + OR 1 + XOR 2 + XOR 2 = 9",
                "early_steady": "q Delay 4 + OR 1 + XOR 2 + XOR 2 = 9",
                "late_seed": "load phase/input 4 + OR 1 + at most one XOR 2 <= 7",
                "late_feedback": "q Delay 4 + XOR 2 + OR 1 + XOR 2 = 9",
            }
            if args.early_or
            else {
                "early_seed": "ready Delay 4 + NOT 1 + XOR 2 + XOR 2 = 9",
                "early_steady": "ready Delay 4 + Switch 1 + XOR 2 + XOR 2 = 9",
                "late_seed": "ready Delay 4 + NOT 1 + OR 1 + at most one XOR 2 <= 8",
                "late_feedback": "q Delay 4 + XOR 2 + OR 1 + XOR 2 <= 9",
            }
        ),
        "results": {},
    }
    best = None
    for budget in budgets:
        dimacs_output = args.dimacs_output
        if dimacs_output is not None and len(budgets) > 1:
            dimacs_output = dimacs_output.with_name(
                f"{dimacs_output.stem}-b{budget}{dimacs_output.suffix}"
            )
        status, certificate, reason = solve(
            budget,
            args.timeout_ms,
            require_matching=require_matching,
            early_cost=early_cost,
            dimacs_output=dimacs_output,
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
        fixed_control = 12 if args.early_or else 6
        summary["leaderboard_accounting"] = {
            "delay_bits": 160,
            "xor_61": 183,
            "phase": best["phase_cost"],
            "control": fixed_control,
            "total": 160 + 183 + best["phase_cost"] + fixed_control,
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
