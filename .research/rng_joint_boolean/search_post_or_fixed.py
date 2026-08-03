#!/usr/bin/env python3
"""Exact post-XOR seed-label search for the fixed 402/9/67 RNG DAG.

The historical exact model assigns one global load-time label to every
first-layer state pair and realises that label with OR gates on the XOR input
pins.  This model additionally permits a pair to be computed raw first and
then consumed through one or more ``OR(seed_i, raw_pair)`` nodes.  Such a
post-OR has the same steady value, a unit seed label during load, and can be
shared by every consumer requesting the same ``(pair, seed)`` label.

Every physical OR is counted in the exact union of:

* pre-XOR leaf atoms ``(seed bit, state bit)``;
* post-XOR atoms ``(seed bit, raw state-pair)``.

The 27 first-layer and 34 final XOR2 gates remain fixed, so OR<=45 gives a
real 400/9/67 data-plane candidate with the reviewed 172-gate shell.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import ctypes
import hashlib
import json
from pathlib import Path
import sys
import threading
import time

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Solver


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from tc_save_lab.rng_encoded_asic import (  # noqa: E402
    B,
    C,
    FIRST_LAYER,
    GATE_BY_OUTPUT,
    T,
    bits,
)


BITS = 32
FIXED_SHELL = 172
FIXED_XOR = 61


def current_rss_bytes() -> int:
    class Counters(ctypes.Structure):
        _fields_ = [
            ("cb", ctypes.c_ulong),
            ("PageFaultCount", ctypes.c_ulong),
            ("PeakWorkingSetSize", ctypes.c_size_t),
            ("WorkingSetSize", ctypes.c_size_t),
            ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
            ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
            ("PagefileUsage", ctypes.c_size_t),
            ("PeakPagefileUsage", ctypes.c_size_t),
        ]

    counters = Counters()
    counters.cb = ctypes.sizeof(counters)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    psapi = ctypes.WinDLL("psapi", use_last_error=True)
    kernel32.GetCurrentProcess.restype = ctypes.c_void_p
    psapi.GetProcessMemoryInfo.argtypes = (
        ctypes.c_void_p, ctypes.POINTER(Counters), ctypes.c_ulong
    )
    psapi.GetProcessMemoryInfo.restype = ctypes.c_int
    if not psapi.GetProcessMemoryInfo(
        kernel32.GetCurrentProcess(), ctypes.byref(counters), counters.cb
    ):
        return 0
    return int(counters.WorkingSetSize)


class PeakRssSampler:
    def __init__(self) -> None:
        self.peak = current_rss_bytes()
        self.stop = threading.Event()
        self.thread = threading.Thread(target=self._sample, daemon=True)

    def _sample(self) -> None:
        while not self.stop.wait(0.02):
            self.peak = max(self.peak, current_rss_bytes())

    def __enter__(self) -> "PeakRssSampler":
        self.thread.start()
        return self

    def __exit__(self, *_args: object) -> None:
        self.stop.set()
        self.thread.join()
        self.peak = max(self.peak, current_rss_bytes())


def solve(
    bound: int,
    timeout_seconds: float,
    solver_name: str,
    *,
    pairs_override: frozenset[int] | None = None,
    b_fanins_override: dict[int, tuple[int, ...]] | None = None,
    fixed_xor_override: int | None = None,
    scope_suffix: str = "",
) -> dict[str, object]:
    started = time.monotonic()
    pool = IDPool()
    clauses: list[list[int]] = []

    def var(key: object) -> int:
        return pool.id(key)

    def at_most_one(values: list[int]) -> None:
        if len(values) <= 1:
            return
        encoded = CardEnc.atmost(
            values, bound=1, vpool=pool, encoding=EncType.seqcounter
        )
        clauses.extend(encoded.clauses)

    def equiv_or(output: int, inputs: list[int]) -> None:
        unique = list(dict.fromkeys(inputs))
        if not unique:
            clauses.append([-output])
            return
        clauses.extend([-value, output] for value in unique)
        clauses.append([-output, *unique])

    def equiv_xor(output: int, left: int, right: int) -> None:
        clauses.extend((
            [-output, left, right],
            [-output, -left, -right],
            [output, -left, right],
            [output, left, -right],
        ))

    pairs = tuple(sorted(FIRST_LAYER if pairs_override is None else pairs_override))
    pair_set = frozenset(pairs)
    b_fanins_override = b_fanins_override or {}
    fixed_xor = FIXED_XOR if fixed_xor_override is None else fixed_xor_override
    raw = {pair: var(("raw", pair)) for pair in pairs}

    pre_pin: dict[tuple[int, int, int], int] = {}
    pre_label: dict[tuple[int, int], int] = {}
    leaf_users: dict[tuple[int, int], list[int]] = defaultdict(list)
    for pair in pairs:
        state_bits = bits(pair)
        if len(state_bits) != 2:
            raise AssertionError("first-layer node is not a state pair")
        for side, state in enumerate(state_bits):
            side_values = []
            for seed in range(BITS):
                pin = var(("pre-pin", pair, side, seed))
                pre_pin[pair, side, seed] = pin
                side_values.append(pin)
                leaf_users[seed, state].append(pin)
                # A raw pair has no pre-XOR seed mapping.
                clauses.append([-pin, -raw[pair]])
            at_most_one(side_values)
        for seed in range(BITS):
            label = var(("pre-label", pair, seed))
            pre_label[pair, seed] = label
            equiv_xor(
                label,
                pre_pin[pair, 0, seed],
                pre_pin[pair, 1, seed],
            )

    post_users: dict[tuple[int, int], list[int]] = defaultdict(list)
    occurrence_records: list[dict[str, object]] = []

    def pair_occurrence(tag: str, pair: int) -> list[int]:
        if pair not in raw:
            raise AssertionError(f"consumer requests absent pair {pair:08x}")
        post = []
        effective = []
        for seed in range(BITS):
            choice = var(("post-choice", tag, pair, seed))
            post.append(choice)
            post_users[pair, seed].append(choice)
            clauses.append([-choice, raw[pair]])
            value = var(("pair-effective", tag, pair, seed))
            effective.append(value)
            # raw -> effective == post choice
            clauses.extend((
                [-raw[pair], -value, choice],
                [-raw[pair], value, -choice],
                # !raw -> effective == the global pre-XOR label
                [raw[pair], -value, pre_label[pair, seed]],
                [raw[pair], value, -pre_label[pair, seed]],
            ))
        at_most_one(post)
        occurrence_records.append({
            "tag": tag,
            "kind": "pair",
            "steady": pair,
            "post_choices": tuple(post),
            "effective": tuple(effective),
        })
        return effective

    def unit_occurrence(tag: str, state: int) -> list[int]:
        choices = []
        for seed in range(BITS):
            choice = var(("unit-choice", tag, state, seed))
            choices.append(choice)
            leaf_users[seed, state].append(choice)
        at_most_one(choices)
        occurrence_records.append({
            "tag": tag,
            "kind": "unit",
            "steady": 1 << state,
            "effective": tuple(choices),
        })
        return choices

    # Only B has a prescribed load-time label.  C-only consumers may use the
    # same physical steady nodes but impose no additional seed logic.
    for output_index, (target, steady) in enumerate(zip(T, B, strict=True)):
        fanin_labels: list[list[int]] = []
        override = b_fanins_override.get(steady)
        if override is not None:
            if len(override) not in (1, 2):
                raise AssertionError("override fanin count must be one or two")
            combined = 0
            for fanin in override:
                combined ^= fanin
                if fanin in pair_set:
                    fanin_labels.append(
                        pair_occurrence(
                            f"B{output_index}-override{len(fanin_labels)}", fanin
                        )
                    )
                else:
                    state = bits(fanin)
                    if len(state) != 1:
                        raise AssertionError("override direct fanin is not a unit")
                    fanin_labels.append(
                        unit_occurrence(
                            f"B{output_index}-override{len(fanin_labels)}", state[0]
                        )
                    )
            if combined != steady:
                raise AssertionError("override fanins do not realize the B row")
        elif steady in pair_set:
            fanin_labels.append(pair_occurrence(f"B{output_index}-terminal", steady))
        elif steady.bit_count() == 1:
            state = bits(steady)
            fanin_labels.append(unit_occurrence(f"B{output_index}-terminal", state[0]))
        else:
            gate = GATE_BY_OUTPUT.get(steady)
            if gate is None:
                raise AssertionError(
                    f"no fixed or overridden decomposition for {steady:08x}"
                )
            for side, fanin in enumerate((gate.left, gate.right)):
                if fanin in pair_set:
                    fanin_labels.append(
                        pair_occurrence(f"B{output_index}-side{side}", fanin)
                    )
                else:
                    state = bits(fanin)
                    if len(state) != 1:
                        raise AssertionError("final direct fanin is not a unit")
                    fanin_labels.append(
                        unit_occurrence(f"B{output_index}-side{side}", state[0])
                    )
        if len(fanin_labels) not in (1, 2):
            raise AssertionError("unsupported B fanin count")
        for seed in range(BITS):
            expected = bool(target >> seed & 1)
            if len(fanin_labels) == 1:
                literal = fanin_labels[0][seed]
                clauses.append([literal if expected else -literal])
            else:
                left = fanin_labels[0][seed]
                right = fanin_labels[1][seed]
                if expected:
                    clauses.extend(([left, right], [-left, -right]))
                else:
                    clauses.extend(([-left, right], [left, -right]))

    leaf_atom = {
        key: var(("leaf-atom", *key)) for key in sorted(leaf_users)
    }
    for key, atom in leaf_atom.items():
        equiv_or(atom, leaf_users[key])
    post_atom = {
        key: var(("post-atom", *key)) for key in sorted(post_users)
    }
    for key, atom in post_atom.items():
        equiv_or(atom, post_users[key])
    cost_atoms = [*leaf_atom.values(), *post_atom.values()]
    if bound < len(cost_atoms):
        encoded = CardEnc.atmost(
            cost_atoms,
            bound=bound,
            vpool=pool,
            encoding=EncType.mtotalizer,
        )
        clauses.extend(encoded.clauses)

    digest = hashlib.sha256()
    for clause in clauses:
        digest.update(" ".join(map(str, clause)).encode("ascii"))
        digest.update(b" 0\n")

    timer = None
    with PeakRssSampler() as memory:
        with Solver(name=solver_name, bootstrap_with=clauses) as sat_solver:
            if timeout_seconds:
                timer = threading.Timer(timeout_seconds, sat_solver.interrupt)
                timer.daemon = True
                timer.start()
            try:
                solved = (
                    sat_solver.solve_limited(expect_interrupt=True)
                    if timeout_seconds else sat_solver.solve()
                )
            finally:
                if timer is not None:
                    timer.cancel()
            model = sat_solver.get_model() if solved is True else None
            stats = sat_solver.accum_stats()

    result: dict[str, object] = {
        "schema": 1,
        "scope": (
            "depth-two RNG DAG with global pre-XOR labels or per-consumer "
            "post-XOR unit labels" + (f"; {scope_suffix}" if scope_suffix else "")
        ),
        "status": "sat" if solved is True else "unsat" if solved is False else "unknown",
        "or_bound": bound,
        "fixed_xor": fixed_xor,
        "logic_bound": fixed_xor * 3 + bound,
        "total_gate_bound": FIXED_SHELL + fixed_xor * 3 + bound,
        "delay": 9,
        "cycles": 67,
        "elapsed_seconds": time.monotonic() - started,
        "variable_count": pool.top,
        "clause_count": len(clauses),
        "clause_sha256": digest.hexdigest(),
        "solver": solver_name,
        "solver_stats": stats,
        "peak_rss_bytes": memory.peak,
        "counts": {
            "pairs": len(pairs),
            "B_occurrences": len(occurrence_records),
            "leaf_atoms": len(leaf_atom),
            "post_atoms": len(post_atom),
        },
    }
    if model is not None:
        positive = {literal for literal in model if literal > 0}
        selected_leaf = sorted(key for key, atom in leaf_atom.items() if atom in positive)
        selected_post = sorted(key for key, atom in post_atom.items() if atom in positive)
        actual_or = len(selected_leaf) + len(selected_post)
        pair_modes = {}
        for pair in pairs:
            if raw[pair] in positive:
                pair_modes[f"{pair:08x}"] = {"mode": "raw-post", "pre_label": "00000000"}
            else:
                label = sum(
                    1 << seed
                    for seed in range(BITS)
                    if pre_label[pair, seed] in positive
                )
                pins = []
                for side in range(2):
                    pins.append(next((
                        seed for seed in range(BITS)
                        if pre_pin[pair, side, seed] in positive
                    ), None))
                pair_modes[f"{pair:08x}"] = {
                    "mode": "pre-xor",
                    "pre_label": f"{label:08x}",
                    "pin_seed_bits": pins,
                }
        occurrences = []
        for record in occurrence_records:
            effective = record["effective"]
            label = sum(
                1 << seed for seed, value in enumerate(effective)
                if value in positive
            )
            item = {
                "tag": record["tag"],
                "kind": record["kind"],
                "steady": f"{int(record['steady']):08x}",
                "effective_label": f"{label:08x}",
            }
            if "post_choices" in record:
                post = record["post_choices"]
                item["post_seed_bit"] = next((
                    seed for seed, value in enumerate(post)
                    if value in positive
                ), None)
            occurrences.append(item)
        result["certificate"] = {
            "or_count": actual_or,
            "logic_gate": fixed_xor * 3 + actual_or,
            "total_gate": FIXED_SHELL + fixed_xor * 3 + actual_or,
            "leaf_atoms": [
                {"seed": seed, "state": state}
                for seed, state in selected_leaf
            ],
            "post_atoms": [
                {"seed": seed, "pair": f"{pair:08x}"}
                for pair, seed in selected_post
            ],
            "pair_modes": pair_modes,
            "B_occurrences": occurrences,
        }
        if actual_or > bound:
            raise AssertionError("extracted certificate exceeds OR bound")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--or-bound", type=int, default=45)
    parser.add_argument("--timeout-seconds", type=float, default=120.0)
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument(
        "--output",
        type=Path,
        default=HERE / "post-or-fixed-b45.json",
    )
    args = parser.parse_args()
    if args.or_bound < 0 or args.timeout_seconds < 0:
        raise SystemExit("bounds must be non-negative")
    result = solve(args.or_bound, args.timeout_seconds, args.solver)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": result["status"],
        "or_bound": result["or_bound"],
        "total_gate_bound": result["total_gate_bound"],
        "certificate_or": (
            result.get("certificate", {}).get("or_count")
            if isinstance(result.get("certificate"), dict) else None
        ),
        "elapsed_seconds": result["elapsed_seconds"],
        "counts": result["counts"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
