"""Extended physical-matching phase injection for the fixed RNG XOR DAG.

Compared with ``rng_phase_delay9/solve_phase_cost.py``, EARLY phase buses may
feed every timing-safe occurrence of a raw state unit in the B feedback cone:

* inputs of depth-one XOR gates used by B;
* raw-unit inputs occurring directly at depth-two B XOR gates;
* direct raw-unit B outputs.

One physical EARLY bus is identified by ``(seed_bit, state_bit)`` and may fan
out to multiple occurrences.  The buses form a matching on both seed and state
bits.  LATE ORs retain the original zero-load restriction and may appear on a
depth-two input or at a B output.

The script writes a JSON result and verifies every SAT certificate without
trusting the Z3 model after extraction.  It never reads or writes the live save.
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
DEFAULT_OUTPUT = Path(__file__).with_name("result.json")


def xor_all(z3: Any, values: list[Any]) -> Any:
    if not values:
        return z3.BoolVal(False)
    if len(values) == 1:
        return values[0]
    return z3.Xor(*values)


def classify_b_cone() -> tuple[set[int], set[int]]:
    b_second = {target for target in rng.B if target not in rng.DIRECT | rng.FIRST_LAYER}
    needed_first = {target for target in rng.B if target in rng.FIRST_LAYER}
    for target in b_second:
        gate = rng.GATE_BY_OUTPUT[target]
        needed_first.update(
            node for node in (gate.left, gate.right) if node in rng.FIRST_LAYER
        )
    return needed_first, b_second


def solve(
    *,
    require_matching: bool,
    exact_early: bool,
    early_limit: int,
    late_limit: int,
    phase_budget: int,
    timeout_ms: int,
    max_memory_mb: int,
) -> tuple[str, dict[str, Any] | None, str]:
    try:
        import z3
    except ImportError as error:  # pragma: no cover
        raise SystemExit("install z3-solver in the project venv") from error

    solver = z3.Solver()
    solver.set(timeout=timeout_ms, max_memory=max_memory_mb)
    needed_first, b_second = classify_b_cone()

    # EARLY variables are attached to physical occurrences of raw q_j.
    # Reusing the same (seed_i, q_j) at several occurrences is fanout from one
    # phase bus and costs one Switch.
    early_at: dict[str, tuple[Any, ...]] = {}
    early_node: dict[str, int] = {}
    early_occurrences_by_pair: dict[tuple[int, int], list[Any]] = defaultdict(list)

    def early_label(tag: str, node: int) -> tuple[Any, ...]:
        if node not in rng.DIRECT:
            raise AssertionError(f"EARLY source is not a unit: {node:08x}")
        if tag in early_at:
            return early_at[tag]
        state_bit = rng.bits(node)[0]
        choices = tuple(z3.Bool(f"early_{tag}_{seed}") for seed in range(BITS))
        solver.add(z3.AtMost(*choices, 1))
        early_at[tag] = choices
        early_node[tag] = node
        for seed, choice in enumerate(choices):
            early_occurrences_by_pair[(seed, state_bit)].append(choice)
        return choices

    # Global first-layer labels in the B cone.
    first_label: dict[int, tuple[Any, ...]] = {}
    for node in sorted(needed_first):
        gate = rng.GATE_BY_OUTPUT[node]
        if gate.depth != 1:
            raise AssertionError("needed_first contains a non-first-layer node")
        left = early_label(f"g_{node:08x}_0", gate.left)
        right = early_label(f"g_{node:08x}_1", gate.right)
        first_label[node] = tuple(z3.Xor(left[bit], right[bit]) for bit in range(BITS))

    early_used: dict[tuple[int, int], Any] = {}

    def finish_early_pairs() -> None:
        for pair, occurrences in sorted(early_occurrences_by_pair.items()):
            variable = z3.Bool(f"early_pair_{pair[0]}_{pair[1]}")
            early_used[pair] = variable
            solver.add(variable == z3.Or(*occurrences))

    # LATE is an ordinary OR(seed_i, node), legal only when node's entire
    # tick-zero linear label is zero.  Equal pairs share one physical OR.
    late_at: dict[str, tuple[Any, ...]] = {}
    late_node: dict[str, int] = {}
    late_occurrences_by_pair: dict[tuple[int, int], list[Any]] = defaultdict(list)

    def late_select(tag: str, node: int, base: tuple[Any, ...]) -> tuple[Any, ...]:
        choices = tuple(z3.Bool(f"late_{tag}_{seed}") for seed in range(BITS))
        solver.add(z3.AtMost(*choices, 1))
        zero = z3.And(*(z3.Not(bit) for bit in base))
        for seed, choice in enumerate(choices):
            solver.add(z3.Implies(choice, zero))
            late_occurrences_by_pair[(seed, node)].append(choice)
        late_at[tag] = choices
        late_node[tag] = node
        return tuple(z3.Xor(base[bit], choices[bit]) for bit in range(BITS))

    second_label: dict[int, tuple[Any, ...]] = {}
    for node in sorted(b_second):
        gate = rng.GATE_BY_OUTPUT[node]
        values: list[tuple[Any, ...]] = []
        for side, fanin in enumerate((gate.left, gate.right)):
            tag = f"g_{node:08x}_{side}"
            if fanin in rng.DIRECT:
                base = early_label(tag, fanin)
            else:
                base = first_label[fanin]
            values.append(late_select(tag, fanin, base))
        second_label[node] = tuple(
            z3.Xor(values[0][bit], values[1][bit]) for bit in range(BITS)
        )

    # Every B target can receive a final zero-load LATE OR.  Direct B targets
    # additionally gain an EARLY unit occurrence, which the old model omitted.
    result_label: list[tuple[Any, ...]] = []
    for index, target in enumerate(rng.B):
        tag = f"b_{index}"
        if target in rng.DIRECT:
            base = early_label(tag, target)
        elif target in rng.FIRST_LAYER:
            base = first_label[target]
        else:
            base = second_label[target]
        actual = late_select(tag, target, base)
        result_label.append(actual)
        wanted = rng.T[index]
        for bit in range(BITS):
            solver.add(actual[bit] == bool((wanted >> bit) & 1))

    finish_early_pairs()

    late_used: dict[tuple[int, int], Any] = {}
    for pair, occurrences in sorted(late_occurrences_by_pair.items()):
        variable = z3.Bool(f"late_pair_{pair[0]}_{pair[1]:08x}")
        late_used[pair] = variable
        solver.add(variable == z3.Or(*occurrences))

    # A matching is the strict electrical-isolation condition: each tri-state
    # seed source and each switched q source belongs to at most one EARLY bus.
    if require_matching:
        for seed in range(BITS):
            variables = [v for (s, _state), v in early_used.items() if s == seed]
            solver.add(z3.AtMost(*variables, 1))
        for state in range(BITS):
            variables = [v for (_seed, q), v in early_used.items() if q == state]
            solver.add(z3.AtMost(*variables, 1))

    early_variables = list(early_used.values())
    late_variables = list(late_used.values())
    if exact_early:
        solver.add(z3.PbEq([(value, 1) for value in early_variables], early_limit))
    else:
        solver.add(z3.PbLe([(value, 1) for value in early_variables], early_limit))
    solver.add(z3.PbLe([(value, 1) for value in late_variables], late_limit))
    solver.add(
        z3.PbLe(
            [(value, 2) for value in early_variables]
            + [(value, 1) for value in late_variables],
            phase_budget,
        )
    )

    status = solver.check()
    if status == z3.unknown:
        return "unknown", None, solver.reason_unknown()
    if status == z3.unsat:
        return "unsat", None, ""

    model = solver.model()
    selected_early = sorted(
        pair for pair, variable in early_used.items() if z3.is_true(model.eval(variable))
    )
    selected_late = sorted(
        pair for pair, variable in late_used.items() if z3.is_true(model.eval(variable))
    )
    early_occurrences = []
    for tag, choices in sorted(early_at.items()):
        state = rng.bits(early_node[tag])[0]
        for seed, choice in enumerate(choices):
            if z3.is_true(model.eval(choice)):
                early_occurrences.append([tag, seed, state])
    late_occurrences = []
    for tag, choices in sorted(late_at.items()):
        node = late_node[tag]
        for seed, choice in enumerate(choices):
            if z3.is_true(model.eval(choice)):
                late_occurrences.append([tag, seed, f"{node:08x}"])

    certificate = {
        "require_matching": require_matching,
        "exact_early": exact_early,
        "early_pair_count": len(selected_early),
        "late_pair_count": len(selected_late),
        "phase_cost": 2 * len(selected_early) + len(selected_late),
        "early_pairs": [[seed, state] for seed, state in selected_early],
        "late_pairs": [[seed, f"{node:08x}"] for seed, node in selected_late],
        "early_occurrences": early_occurrences,
        "late_occurrences": late_occurrences,
        "b_cone_first_nodes": [f"{node:08x}" for node in sorted(needed_first)],
        "b_cone_second_nodes": [f"{node:08x}" for node in sorted(b_second)],
    }
    return "sat", certificate, ""


def verify_certificate(
    certificate: dict[str, Any],
    *,
    early_limit: int,
    late_limit: int,
    phase_budget: int,
) -> None:
    needed_first, b_second = classify_b_cone()
    early_occurrence = {
        str(tag): (int(seed), int(state))
        for tag, seed, state in certificate["early_occurrences"]
    }
    late_occurrence = {
        str(tag): (int(seed), int(node, 16))
        for tag, seed, node in certificate["late_occurrences"]
    }
    early_pairs = {(int(seed), int(state)) for seed, state in certificate["early_pairs"]}
    late_pairs = {
        (int(seed), int(node, 16)) for seed, node in certificate["late_pairs"]
    }
    if certificate["require_matching"]:
        if len({seed for seed, _state in early_pairs}) != len(early_pairs):
            raise AssertionError("EARLY seed side is not a matching")
        if len({state for _seed, state in early_pairs}) != len(early_pairs):
            raise AssertionError("EARLY state side is not a matching")
    if len(early_pairs) > early_limit or len(late_pairs) > late_limit:
        raise AssertionError("pair count exceeds configured limit")
    if certificate["exact_early"] and len(early_pairs) != early_limit:
        raise AssertionError("exact EARLY count mismatch")
    phase_cost = 2 * len(early_pairs) + len(late_pairs)
    if phase_cost != certificate["phase_cost"] or phase_cost > phase_budget:
        raise AssertionError("phase cost mismatch")

    def early(tag: str, node: int) -> int:
        item = early_occurrence.get(tag)
        if item is None:
            return 0
        seed, state = item
        if node not in rng.DIRECT or rng.bits(node) != (state,):
            raise AssertionError(f"invalid EARLY unit at {tag}")
        if (seed, state) not in early_pairs:
            raise AssertionError(f"EARLY occurrence lacks physical pair at {tag}")
        return 1 << seed

    def late(tag: str, node: int, base: int) -> int:
        item = late_occurrence.get(tag)
        if item is None:
            return base
        seed, recorded_node = item
        if recorded_node != node or (seed, node) not in late_pairs:
            raise AssertionError(f"invalid LATE pair at {tag}")
        if base != 0:
            raise AssertionError(f"LATE input is nonzero during load at {tag}")
        return 1 << seed

    first: dict[int, int] = {}
    for node in sorted(needed_first):
        gate = rng.GATE_BY_OUTPUT[node]
        first[node] = early(f"g_{node:08x}_0", gate.left) ^ early(
            f"g_{node:08x}_1", gate.right
        )

    second: dict[int, int] = {}
    for node in sorted(b_second):
        gate = rng.GATE_BY_OUTPUT[node]
        values = []
        for side, fanin in enumerate((gate.left, gate.right)):
            tag = f"g_{node:08x}_{side}"
            base = early(tag, fanin) if fanin in rng.DIRECT else first[fanin]
            values.append(late(tag, fanin, base))
        second[node] = values[0] ^ values[1]

    for index, (target, wanted) in enumerate(zip(rng.B, rng.T)):
        tag = f"b_{index}"
        if target in rng.DIRECT:
            base = early(tag, target)
        elif target in rng.FIRST_LAYER:
            base = first[target]
        else:
            base = second[target]
        actual = late(tag, target, base)
        if actual != wanted:
            raise AssertionError(
                f"B[{index}] tick-zero label {actual:08x} != T {wanted:08x}"
            )

    used_early = set(early_occurrence.values())
    if used_early != early_pairs:
        raise AssertionError("EARLY physical pair set has unused or missing entries")
    used_late = set(late_occurrence.values())
    if used_late != late_pairs:
        raise AssertionError("LATE physical pair set has unused or missing entries")

    # Timing proof for every enabled site.
    # EARLY first input: control 5 + two XOR2 = 9.
    # EARLY second input: control 5 + one XOR2 = 7.
    # EARLY direct B: control 5.
    # LATE second input: control 6 + one XOR2 = 8; final B: control 6.
    if max(5 + 2 * 2, 5 + 2, 5, 6 + 2, 6) > 9:
        raise AssertionError("timing formulas exceed delay nine")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout-ms", type=int, default=180_000)
    parser.add_argument("--max-memory-mb", type=int, default=384)
    parser.add_argument("--early-limit", type=int, default=32)
    parser.add_argument("--late-limit", type=int, default=18)
    parser.add_argument("--phase-budget", type=int, default=82)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--verify-existing", type=Path)
    parser.add_argument(
        "--relax-matching",
        action="store_true",
        help="control experiment only: allow one seed/state source on several EARLY buses",
    )
    args = parser.parse_args()

    if args.verify_existing is not None:
        payload = json.loads(args.verify_existing.read_text(encoding="utf-8"))
        verified = 0
        for record in payload["results"].values():
            certificate = record.get("certificate")
            if certificate is not None:
                verify_certificate(
                    certificate,
                    early_limit=payload["limits"]["early"],
                    late_limit=payload["limits"]["late"],
                    phase_budget=payload["limits"]["phase_cost"],
                )
                verified += 1
        print(f"verified {verified} certificate(s)")
        if not verified:
            raise SystemExit("no SAT certificate found")
        return

    needed_first, b_second = classify_b_cone()
    payload: dict[str, Any] = {
        "schema": 1,
        "model": "fixed 61-XOR DAG, extended timing-safe unit EARLY occurrences",
        "require_matching": not args.relax_matching,
        "limits": {
            "early": args.early_limit,
            "late": args.late_limit,
            "phase_cost": args.phase_budget,
        },
        "b_cone": {
            "first_nodes": len(needed_first),
            "second_nodes": len(b_second),
            "direct_b_targets": sum(target in rng.DIRECT for target in rng.B),
        },
        "results": {},
    }
    for exact in (False, True):
        key = "at_most_32_early" if not exact else "exactly_32_early"
        status, certificate, reason = solve(
            require_matching=not args.relax_matching,
            exact_early=exact,
            early_limit=args.early_limit,
            late_limit=args.late_limit,
            phase_budget=args.phase_budget,
            timeout_ms=args.timeout_ms,
            max_memory_mb=args.max_memory_mb,
        )
        record: dict[str, Any] = {"status": status, "reason": reason}
        if certificate is not None:
            verify_certificate(
                certificate,
                early_limit=args.early_limit,
                late_limit=args.late_limit,
                phase_budget=args.phase_budget,
            )
            record["certificate"] = certificate
            print(
                f"{key}: SAT early={certificate['early_pair_count']} "
                f"late={certificate['late_pair_count']} "
                f"cost={certificate['phase_cost']}"
            )
        else:
            print(f"{key}: {status.upper()}{' (' + reason + ')' if reason else ''}")
        payload["results"][key] = record

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
