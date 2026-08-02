"""Compact symbolic joint model for encoded-state depth-two RNG networks.

This is the unrestricted formulation missing from the fixed-basis searches:
``T``, ``B``, ``C``, the first-layer pair dictionary, every output
decomposition, tick-zero labels, and the OR mapping bank are solver variables.
It is practical as a small-width correctness oracle.  At 32 bits the model is
intentionally time/memory bounded and currently serves as an experimental
SMT route, not a completeness proof.

No game/save modules are imported or written.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys
import time
from typing import Sequence

from z3 import (
    And,
    BitVec,
    BitVecVal,
    Bool,
    Extract,
    If,
    Implies,
    Int,
    Not,
    Or,
    Solver,
    Sum,
    Xor,
    is_true,
    sat,
    unsat,
)


def mux(index, values: Sequence):
    if not values:
        raise ValueError("mux requires at least one value")
    result = values[-1]
    for position in range(len(values) - 2, -1, -1):
        result = If(index == position, values[position], result)
    return result


def onehot(index, bits: int):
    result = BitVecVal(0, bits)
    for bit in range(bits - 1, -1, -1):
        result = If(index == bit, BitVecVal(1 << bit, bits), result)
    return result


def bit(value, index: int):
    return Extract(index, index, value) == BitVecVal(1, 1)


def parity(terms: Sequence):
    if not terms:
        return False
    result = terms[0]
    for term in terms[1:]:
        result = Xor(result, term)
    return result


def xorshift(value: int, bits: int, right1: int, left: int, right2: int) -> int:
    mask = (1 << bits) - 1
    value &= mask
    value ^= value >> right1
    value &= mask
    value ^= (value << left) & mask
    value &= mask
    value ^= value >> right2
    return value & mask


def matrix_from_function(bits: int, function) -> tuple[int, ...]:
    return tuple(
        sum(((function(1 << source) >> output) & 1) << source for source in range(bits))
        for output in range(bits)
    )


def apply_row(row: int, matrix: Sequence[int]) -> int:
    result = 0
    while row:
        low = row & -row
        result ^= matrix[low.bit_length() - 1]
        row ^= low
    return result


def compose(left: Sequence[int], right: Sequence[int]) -> tuple[int, ...]:
    return tuple(apply_row(row, right) for row in left)


def apply_matrix(matrix: Sequence[int], value: int) -> int:
    return sum(((row & value).bit_count() & 1) << index for index, row in enumerate(matrix))


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def basis_family(radius: int) -> list[dict[str, object]]:
    """Return the exact feasible row-shear ball around the two-shear basis."""

    root = Path(__file__).resolve().parents[2]
    init = load_module("symbolic_family_init", root / ".research/rng_init_reuse/verify_init_reuse.py")
    search = load_module("symbolic_family_search", root / ".research/rng_joint_search_resume/search.py")
    start = {
        "T": tuple(init.T),
        "B": tuple(init.B),
        "C": tuple(init.C),
        "operations": (),
    }
    seen = {start["T"]: start}
    frontier = [start]
    for _depth in range(radius):
        following = []
        for candidate in frontier:
            for dst in range(32):
                for src in range(32):
                    if dst == src:
                        continue
                    T, B, C = map(list, (candidate["T"], candidate["B"], candidate["C"]))
                    search.mutate(T, B, C, dst, src)
                    if any(row == 0 or row.bit_count() > 4 for row in (*T, *B, *C)):
                        continue
                    key = tuple(T)
                    if key in seen:
                        continue
                    item = {
                        "T": key,
                        "B": tuple(B),
                        "C": tuple(C),
                        "operations": candidate["operations"] + ((dst, src),),
                    }
                    seen[key] = item
                    following.append(item)
        frontier = following
    return list(seen.values())


class JointModel:
    def __init__(
        self,
        *,
        bits: int,
        pair_slots: int,
        logic_budget: int,
        right1: int,
        left_shift: int,
        right2: int,
        timeout_ms: int,
        memory_mb: int,
        fixed_basis_family: Sequence[dict[str, object]] | None = None,
    ) -> None:
        self.n = bits
        self.pmax = pair_slots
        self.logic_budget = logic_budget
        self.fixed_basis_family = fixed_basis_family
        self.A = matrix_from_function(
            bits,
            lambda value: xorshift(value, bits, right1, left_shift, right2),
        )
        self.solver = Solver()
        self.solver.set(timeout=timeout_ms, max_memory=memory_mb)

        n, pmax, solver = self.n, self.pmax, self.solver
        self.T = [BitVec(f"T_{row}", n) for row in range(n)]
        self.B = [BitVec(f"B_{row}", n) for row in range(n)]
        self.C = [BitVec(f"C_{row}", n) for row in range(n)]

        self.pair_count = Int("pair_count")
        solver.add(0 <= self.pair_count, self.pair_count <= pmax)
        self.pair_left = [Int(f"pair_{gate}_left") for gate in range(pmax)]
        self.pair_right = [Int(f"pair_{gate}_right") for gate in range(pmax)]
        self.pair_seed_left = [Int(f"pair_{gate}_seed_left") for gate in range(pmax)]
        self.pair_seed_right = [Int(f"pair_{gate}_seed_right") for gate in range(pmax)]
        self.pair_masks = [
            onehot(self.pair_left[gate], n) | onehot(self.pair_right[gate], n)
            for gate in range(pmax)
        ]
        self.pair_labels = [
            onehot(self.pair_seed_left[gate], n) ^ onehot(self.pair_seed_right[gate], n)
            for gate in range(pmax)
        ]
        for gate in range(pmax):
            active = gate < self.pair_count
            solver.add(
                Implies(
                    active,
                    And(
                        0 <= self.pair_left[gate],
                        self.pair_left[gate] < self.pair_right[gate],
                        self.pair_right[gate] < n,
                        -1 <= self.pair_seed_left[gate],
                        self.pair_seed_left[gate] < n,
                        -1 <= self.pair_seed_right[gate],
                        self.pair_seed_right[gate] < n,
                    ),
                )
            )
            solver.add(
                Implies(
                    Not(active),
                    And(
                        self.pair_left[gate] == 0,
                        self.pair_right[gate] == 1,
                        self.pair_seed_left[gate] == -1,
                        self.pair_seed_right[gate] == -1,
                    ),
                )
            )
            if gate:
                previous_key = n * self.pair_left[gate - 1] + self.pair_right[gate - 1]
                current_key = n * self.pair_left[gate] + self.pair_right[gate]
                solver.add(Implies(active, previous_key < current_key))

        outputs = 2 * n
        self.rows = self.B + self.C
        self.kind = [Int(f"out_{index}_kind") for index in range(outputs)]
        self.unit = [Int(f"out_{index}_unit") for index in range(outputs)]
        self.pair_a = [Int(f"out_{index}_pair_a") for index in range(outputs)]
        self.pair_b = [Int(f"out_{index}_pair_b") for index in range(outputs)]
        self.raw_seed = [Int(f"B_{index}_raw_seed") for index in range(n)]

        pair_mask_a = [mux(self.pair_a[index], self.pair_masks) for index in range(outputs)]
        pair_mask_b = [mux(self.pair_b[index], self.pair_masks) for index in range(outputs)]
        pair_left_a = [mux(self.pair_a[index], self.pair_left) for index in range(outputs)]
        pair_right_a = [mux(self.pair_a[index], self.pair_right) for index in range(outputs)]
        pair_label_a = [mux(self.pair_a[index], self.pair_labels) for index in range(n)]
        pair_label_b = [mux(self.pair_b[index], self.pair_labels) for index in range(n)]

        for index, row in enumerate(self.rows):
            kind, unit = self.kind[index], self.unit[index]
            pa, pb = self.pair_a[index], self.pair_b[index]
            solver.add(1 <= kind, kind <= 4)
            solver.add(
                Implies(
                    kind == 1,
                    And(0 <= unit, unit < n, row == onehot(unit, n), pa == 0, pb == 0),
                )
            )
            solver.add(
                Implies(
                    kind == 2,
                    And(0 <= pa, pa < self.pair_count, row == pair_mask_a[index], unit == 0, pb == 0),
                )
            )
            solver.add(
                Implies(
                    kind == 3,
                    And(
                        0 <= pa,
                        pa < self.pair_count,
                        0 <= unit,
                        unit < n,
                        unit != pair_left_a[index],
                        unit != pair_right_a[index],
                        row == (pair_mask_a[index] ^ onehot(unit, n)),
                        pb == 0,
                    ),
                )
            )
            solver.add(
                Implies(
                    kind == 4,
                    And(
                        0 <= pa,
                        pa < pb,
                        pb < self.pair_count,
                        pair_mask_a[index] & pair_mask_b[index] == BitVecVal(0, n),
                        row == (pair_mask_a[index] ^ pair_mask_b[index]),
                        unit == 0,
                    ),
                )
            )

        # Equal B/C target rows are one physical output node, so their chosen
        # decomposition must also be identical before we deduplicate its gate.
        for current in range(outputs):
            for previous in range(current):
                same = self.rows[current] == self.rows[previous]
                solver.add(Implies(same, self.kind[current] == self.kind[previous]))
                solver.add(
                    Implies(
                        And(same, Or(self.kind[current] == 1, self.kind[current] == 3)),
                        self.unit[current] == self.unit[previous],
                    )
                )
                solver.add(
                    Implies(
                        And(same, self.kind[current] >= 2),
                        self.pair_a[current] == self.pair_a[previous],
                    )
                )
                solver.add(
                    Implies(
                        And(same, self.kind[current] == 4),
                        self.pair_b[current] == self.pair_b[previous],
                    )
                )

        # Every selected first-layer pair is actually consumed.  This removes
        # a large family of cost-wasting symmetries without excluding a model.
        for gate in range(pmax):
            users = []
            for index in range(outputs):
                users.append(
                    And(
                        Or(self.kind[index] == 2, self.kind[index] == 3),
                        self.pair_a[index] == gate,
                    )
                )
                users.append(
                    And(
                        self.kind[index] == 4,
                        Or(self.pair_a[index] == gate, self.pair_b[index] == gate),
                    )
                )
            solver.add((gate < self.pair_count) == Or(*users))

        self.basis_choice = None
        if fixed_basis_family is None:
            # C*T=A and T*C=B.  Since xorshift A is invertible, these equations
            # also imply that T and C are invertible; no determinant circuit
            # is needed.
            for row in range(n):
                for column in range(n):
                    ct = parity([And(bit(self.C[row], k), bit(self.T[k], column)) for k in range(n)])
                    solver.add(ct if self.A[row] >> column & 1 else Not(ct))
                    tc = parity([And(bit(self.T[row], k), bit(self.C[k], column)) for k in range(n)])
                    solver.add(bit(self.B[row], column) == tc)
        else:
            if n != 32 or not fixed_basis_family:
                raise ValueError("a fixed basis family requires a non-empty 32-bit family")
            self.basis_choice = Int("basis_choice")
            solver.add(0 <= self.basis_choice, self.basis_choice < len(fixed_basis_family))
            for row in range(n):
                for name, matrix in (("T", self.T), ("B", self.B), ("C", self.C)):
                    choices = [BitVecVal(candidate[name][row], n) for candidate in fixed_basis_family]
                    solver.add(matrix[row] == mux(self.basis_choice, choices))
            relevant_pairs: set[int] = set()
            for choice, candidate in enumerate(fixed_basis_family):
                for output, row_mask in enumerate((*candidate["B"], *candidate["C"])):
                    weight = row_mask.bit_count()
                    solver.add(Implies(self.basis_choice == choice, self.kind[output] == weight))
                    if weight == 2:
                        relevant_pairs.add(row_mask)
                    elif weight == 3:
                        units = [1 << bit_index for bit_index in range(n) if row_mask >> bit_index & 1]
                        relevant_pairs.update(row_mask ^ unit for unit in units)
                    elif weight == 4:
                        units = [1 << bit_index for bit_index in range(n) if row_mask >> bit_index & 1]
                        for left_index in range(len(units)):
                            for right_index in range(left_index + 1, len(units)):
                                relevant_pairs.add(units[left_index] | units[right_index])
            allowed_masks = [BitVecVal(mask, n) for mask in sorted(relevant_pairs)]
            for gate in range(pmax):
                solver.add(
                    Implies(
                        gate < self.pair_count,
                        Or(*(self.pair_masks[gate] == mask for mask in allowed_masks)),
                    )
                )

        self.mode = [[Bool(f"mode_s{seed}_q{state}") for state in range(n)] for seed in range(n)]
        mode_users: list[list[list]] = [[[] for _ in range(n)] for _ in range(n)]
        for gate in range(pmax):
            active = gate < self.pair_count
            for seed in range(n):
                for state in range(n):
                    left_user = And(
                        active,
                        self.pair_seed_left[gate] == seed,
                        self.pair_left[gate] == state,
                    )
                    right_user = And(
                        active,
                        self.pair_seed_right[gate] == seed,
                        self.pair_right[gate] == state,
                    )
                    mode_users[seed][state].extend((left_user, right_user))

        # Tick-zero labels on the B nodes must be exactly T(seed).
        for index in range(n):
            kind = self.kind[index]
            raw = self.raw_seed[index]
            solver.add(
                Implies(
                    kind == 1,
                    And(0 <= raw, raw < n, self.T[index] == onehot(raw, n)),
                )
            )
            solver.add(Implies(kind == 2, And(raw == -1, self.T[index] == pair_label_a[index])))
            solver.add(
                Implies(
                    kind == 3,
                    And(
                        -1 <= raw,
                        raw < n,
                        self.T[index] == (pair_label_a[index] ^ onehot(raw, n)),
                    ),
                )
            )
            solver.add(Implies(kind == 4, And(raw == -1, self.T[index] == (pair_label_a[index] ^ pair_label_b[index]))))
            for seed in range(n):
                for state in range(n):
                    user = And(
                        Or(kind == 1, kind == 3),
                        raw == seed,
                        self.unit[index] == state,
                    )
                    mode_users[seed][state].append(user)

        for seed in range(n):
            for state in range(n):
                solver.add(self.mode[seed][state] == Or(*mode_users[seed][state]))

        self.final_new = [Bool(f"out_{index}_new_final") for index in range(outputs)]
        for index in range(outputs):
            earlier = [
                Or(self.kind[previous] < 3, self.rows[index] != self.rows[previous])
                for previous in range(index)
            ]
            solver.add(
                self.final_new[index]
                == And(self.kind[index] >= 3, *earlier)
            )
        self.xor_cost = self.pair_count + Sum([If(value, 1, 0) for value in self.final_new])
        self.or_cost = Sum([If(self.mode[seed][state], 1, 0) for seed in range(n) for state in range(n)])
        self.logic_cost = 3 * self.xor_cost + self.or_cost
        solver.add(self.logic_cost <= logic_budget)

    def extract(self, model) -> dict[str, object]:
        n = self.n
        T = tuple(model.eval(row, model_completion=True).as_long() for row in self.T)
        B = tuple(model.eval(row, model_completion=True).as_long() for row in self.B)
        C = tuple(model.eval(row, model_completion=True).as_long() for row in self.C)
        count = model.eval(self.pair_count).as_long()
        pairs = []
        for gate in range(count):
            pairs.append(
                {
                    "left": model.eval(self.pair_left[gate]).as_long(),
                    "right": model.eval(self.pair_right[gate]).as_long(),
                    "seed_left": model.eval(self.pair_seed_left[gate]).as_long(),
                    "seed_right": model.eval(self.pair_seed_right[gate]).as_long(),
                }
            )
        outputs = []
        for index in range(2 * n):
            outputs.append(
                {
                    "matrix": "B" if index < n else "C",
                    "index": index if index < n else index - n,
                    "row": f"{model.eval(self.rows[index]).as_long():0{(n + 3) // 4}x}",
                    "kind": model.eval(self.kind[index]).as_long(),
                    "unit": model.eval(self.unit[index]).as_long(),
                    "pair_a": model.eval(self.pair_a[index]).as_long(),
                    "pair_b": model.eval(self.pair_b[index]).as_long(),
                    **({"raw_seed": model.eval(self.raw_seed[index]).as_long()} if index < n else {}),
                }
            )
        modes = [
            {"seed": seed, "state": state}
            for seed in range(n)
            for state in range(n)
            if is_true(model.eval(self.mode[seed][state]))
        ]
        xor_cost = model.eval(self.xor_cost).as_long()
        or_cost = model.eval(self.or_cost).as_long()
        certificate = {
            "bits": n,
            "A": [f"{row:0{(n + 3) // 4}x}" for row in self.A],
            "T": [f"{row:0{(n + 3) // 4}x}" for row in T],
            "B": [f"{row:0{(n + 3) // 4}x}" for row in B],
            "C": [f"{row:0{(n + 3) // 4}x}" for row in C],
            "pairs": pairs,
            "outputs": outputs,
            "mode_pairs": modes,
            "metrics": {
                "xor": xor_cost,
                "or": or_cost,
                "logic_cost": 3 * xor_cost + or_cost,
                "logic_budget": self.logic_budget,
            },
        }
        if self.basis_choice is not None:
            choice = model.eval(self.basis_choice).as_long()
            certificate["basis_choice"] = choice
            certificate["basis_row_shears"] = [
                list(operation) for operation in self.fixed_basis_family[choice]["operations"]
            ]
        verify(certificate)
        return certificate


def verify(document: dict[str, object]) -> None:
    n = document["bits"]
    parse = lambda rows: tuple(int(row, 16) for row in rows)
    A, T, B, C = map(parse, (document["A"], document["T"], document["B"], document["C"]))
    if compose(C, T) != A or compose(T, C) != B:
        raise AssertionError("symbolic matrix certificate failed")

    pairs = document["pairs"]
    pair_masks = [(1 << item["left"]) | (1 << item["right"]) for item in pairs]
    pair_labels = [
        (0 if item["seed_left"] < 0 else 1 << item["seed_left"])
        ^ (0 if item["seed_right"] < 0 else 1 << item["seed_right"])
        for item in pairs
    ]
    modes = {(item["seed"], item["state"]) for item in document["mode_pairs"]}
    used_modes: set[tuple[int, int]] = set()
    previous_key = -1
    for item in pairs:
        key = n * item["left"] + item["right"]
        if not 0 <= item["left"] < item["right"] < n or key <= previous_key:
            raise AssertionError("pair dictionary is not canonical")
        previous_key = key
        if item["seed_left"] >= 0 and (item["seed_left"], item["left"]) not in modes:
            raise AssertionError("left pair pin mode is absent")
        if item["seed_left"] >= 0:
            used_modes.add((item["seed_left"], item["left"]))
        if item["seed_right"] >= 0 and (item["seed_right"], item["right"]) not in modes:
            raise AssertionError("right pair pin mode is absent")
        if item["seed_right"] >= 0:
            used_modes.add((item["seed_right"], item["right"]))

    seen_final: set[int] = set()
    decompositions: dict[int, tuple[int, ...]] = {}
    consumed_pairs: set[int] = set()
    xor_count = len(pairs)
    for item in document["outputs"]:
        row = int(item["row"], 16)
        kind = item["kind"]
        if kind == 1:
            actual = 1 << item["unit"]
            decomposition = (kind, item["unit"])
        elif kind == 2:
            actual = pair_masks[item["pair_a"]]
            decomposition = (kind, item["pair_a"])
            consumed_pairs.add(item["pair_a"])
        elif kind == 3:
            actual = pair_masks[item["pair_a"]] ^ (1 << item["unit"])
            decomposition = (kind, item["pair_a"], item["unit"])
            consumed_pairs.add(item["pair_a"])
        else:
            actual = pair_masks[item["pair_a"]] ^ pair_masks[item["pair_b"]]
            decomposition = (kind, item["pair_a"], item["pair_b"])
            consumed_pairs.update((item["pair_a"], item["pair_b"]))
        if actual != row or row.bit_count() != kind:
            raise AssertionError("output decomposition mismatch")
        previous = decompositions.setdefault(row, decomposition)
        if previous != decomposition:
            raise AssertionError("duplicate target uses multiple physical decompositions")
        if kind >= 3 and row not in seen_final:
            seen_final.add(row)
            xor_count += 1
        if item["matrix"] == "B":
            index = item["index"]
            if kind == 1:
                label = 1 << item["raw_seed"]
                required = (item["raw_seed"], item["unit"])
                if required not in modes:
                    raise AssertionError("direct raw mode is absent")
                used_modes.add(required)
            elif kind == 2:
                label = pair_labels[item["pair_a"]]
            elif kind == 3:
                label = pair_labels[item["pair_a"]]
                if item["raw_seed"] >= 0:
                    label ^= 1 << item["raw_seed"]
                    if (item["raw_seed"], item["unit"]) not in modes:
                        raise AssertionError("final raw mode is absent")
                    used_modes.add((item["raw_seed"], item["unit"]))
            else:
                label = pair_labels[item["pair_a"]] ^ pair_labels[item["pair_b"]]
            if label != T[index]:
                raise AssertionError("tick-zero B label mismatch")

    metrics = document["metrics"]
    if consumed_pairs != set(range(len(pairs))):
        raise AssertionError("pair dictionary contains an unused gate")
    if used_modes != modes:
        raise AssertionError("mode bank differs from the exact set of physical users")
    if xor_count != metrics["xor"] or len(modes) != metrics["or"]:
        raise AssertionError("symbolic cost certificate mismatch")
    if metrics["logic_cost"] != 3 * xor_count + len(modes) or metrics["logic_cost"] > metrics["logic_budget"]:
        raise AssertionError("symbolic weighted budget mismatch")
    mask = (1 << n) - 1
    for seed in range(min(1 << n, 69)):
        encoded = apply_matrix(T, seed)
        natural = seed
        for _ in range(2 * n + 1):
            natural = apply_matrix(A, natural) & mask
            if apply_matrix(C, encoded) != natural:
                raise AssertionError("symbolic visible sequence mismatch")
            encoded = apply_matrix(B, encoded)


def solve_once(args, budget: int) -> dict[str, object]:
    started = time.perf_counter()
    family = basis_family(args.basis_radius) if args.basis_radius is not None else None
    model = JointModel(
        bits=args.bits,
        pair_slots=args.pair_slots,
        logic_budget=budget,
        right1=args.right1,
        left_shift=args.left_shift,
        right2=args.right2,
        timeout_ms=args.timeout_ms,
        memory_mb=args.memory_mb,
        fixed_basis_family=family,
    )
    built = time.perf_counter()
    result = model.solver.check()
    checked = time.perf_counter()
    document: dict[str, object] = {
        "status": "sat" if result == sat else "unsat" if result == unsat else "unknown",
        "bits": args.bits,
        "pair_slots": args.pair_slots,
        "logic_budget": budget,
        "shifts": {"right1": args.right1, "left": args.left_shift, "right2": args.right2},
        "assertion_count": len(model.solver.assertions()),
        "build_seconds": round(built - started, 6),
        "solve_seconds": round(checked - built, 6),
        "memory_limit_mb": args.memory_mb,
        **({"basis_family_size": len(family), "basis_radius": args.basis_radius} if family is not None else {}),
    }
    if result == sat:
        document["certificate"] = model.extract(model.solver.model())
    elif result != unsat:
        document["reason"] = model.solver.reason_unknown()
    return document


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bits", type=int, default=4)
    parser.add_argument("--pair-slots", type=int)
    parser.add_argument("--logic-budget", type=int, default=40)
    parser.add_argument("--right1", type=int)
    parser.add_argument("--left-shift", type=int)
    parser.add_argument("--right2", type=int)
    parser.add_argument("--timeout-ms", type=int, default=30_000)
    parser.add_argument("--memory-mb", type=int, default=768)
    parser.add_argument("--basis-radius", type=int, choices=(0, 1, 2))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not 2 <= args.bits <= 32:
        parser.error("bits must be in [2,32]")
    if args.basis_radius is not None and args.bits != 32:
        parser.error("--basis-radius requires --bits 32")
    if args.right1 is None:
        args.right1 = 13 if args.bits == 32 else 1
    if args.left_shift is None:
        args.left_shift = 17 if args.bits == 32 else max(1, args.bits // 2)
    if args.right2 is None:
        args.right2 = 5 if args.bits == 32 else 1
    all_pairs = args.bits * (args.bits - 1) // 2
    if args.pair_slots is None:
        args.pair_slots = all_pairs if args.bits <= 8 else min(all_pairs, 30)
    if not 1 <= args.pair_slots <= all_pairs:
        parser.error(f"pair-slots must be in [1,{all_pairs}]")
    if not 64 <= args.memory_mb < 2048:
        parser.error("memory-mb must be in [64,2047]")

    document = solve_once(args, args.logic_budget)
    payload = json.dumps(document, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0 if document["status"] in {"sat", "unsat"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
