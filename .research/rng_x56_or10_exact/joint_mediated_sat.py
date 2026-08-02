"""Exact no-RAM 10-delay RNG cover/mediation/OR audit.

The model jointly chooses, without cover enumeration or beam search:

* one depth-two decomposition for every distinct weight-3/4 B/C row;
* direct or mediated realization for every weight-1/2 B row;
* every physical first-layer pair XOR used by those choices;
* the tick-zero seed label and pin orientation of every selected pair;
* the exact union of physical ``(seed bit, state bit)`` OR leaves.

The fixed shell is 166 gates.  Every XOR2 is charged 3 gates / 2 delay and
every OR leaf is charged 1 gate / 1 delay.  The SAT bound is therefore
``3 * XOR + OR <= 221`` for a 387/10/66 target.  There is no RAM, no one-gate
XOR assumption, no topology limit, and no component/global beam.

This file is research-only: it has no save writer and never starts the game.
Long audits can emit one JSON object per completed record and can interrupt a
single hard SAT call without losing the preceding records.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import ctypes
from dataclasses import asdict, dataclass
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import threading
import time
from typing import Any, Iterable, Sequence


BITS = 32
FIXED_SHELL_GATE = 166
DEFAULT_LOGIC_BUDGET = 221
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


init = load_module(
    "rng_x56_or10_exact_init",
    ROOT / ".research" / "rng_init_reuse" / "verify_init_reuse.py",
)


def bits(value: int) -> tuple[int, ...]:
    return tuple(index for index in range(BITS) if value >> index & 1)


def pair_partitions(row: int) -> tuple[tuple[int, ...], ...]:
    support = tuple(1 << bit for bit in bits(row))
    if len(support) == 3:
        return tuple((row ^ unit,) for unit in support)
    if len(support) == 4:
        a, b, c, d = support
        return (
            tuple(sorted((a | b, c | d))),
            tuple(sorted((a | c, b | d))),
            tuple(sorted((a | d, b | c))),
        )
    raise ValueError(f"row {row:08x} has unsupported weight {len(support)}")


def matrix(record: dict[str, Any], name: str) -> tuple[int, ...]:
    values = record.get(name)
    if not isinstance(values, list) or len(values) != BITS:
        raise ValueError(f"{name} must contain 32 rows")
    return tuple(int(str(value), 16) for value in values)


def actual_test_seeds() -> tuple[int, ...]:
    modulus = 0xFFFFFFFE
    multiplier = 0x4848F09881D3DDD1
    return tuple(
        1 + ((((test_id + 1) * multiplier) & 0xFFFFFFFFFFFFFFFF) % modulus)
        for test_id in range(256)
    )


def verify_256x65(T: Sequence[int], B: Sequence[int], C: Sequence[int]) -> str:
    seeds = actual_test_seeds()
    packed = b"".join(seed.to_bytes(4, "little") for seed in seeds)
    seed_hash = hashlib.sha256(packed).hexdigest()
    if seed_hash != "d8ef931e5eb213217aa4faedc43783f0875e52607f991e89080c6046aad1e24b":
        raise AssertionError("actual test seed vector hash changed")
    for seed in seeds:
        natural = seed
        encoded = init.apply_matrix(T, seed)
        for _ in range(65):
            natural = init.xorshift32(natural)
            if init.apply_matrix(C, encoded) != natural:
                raise AssertionError(f"256x65 output mismatch for seed {seed:08x}")
            encoded = init.apply_matrix(B, encoded)
    return seed_hash


def current_rss_bytes() -> int:
    if sys.platform != "win32":
        try:
            import resource

            value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            return int(value * (1024 if sys.platform != "darwin" else 1))
        except (ImportError, OSError):
            return 0

    class ProcessMemoryCounters(ctypes.Structure):
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

    counters = ProcessMemoryCounters()
    counters.cb = ctypes.sizeof(counters)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    psapi = ctypes.WinDLL("psapi", use_last_error=True)
    kernel32.GetCurrentProcess.restype = ctypes.c_void_p
    psapi.GetProcessMemoryInfo.argtypes = [
        ctypes.c_void_p,
        ctypes.POINTER(ProcessMemoryCounters),
        ctypes.c_ulong,
    ]
    psapi.GetProcessMemoryInfo.restype = ctypes.c_int
    if not psapi.GetProcessMemoryInfo(
        kernel32.GetCurrentProcess(), ctypes.byref(counters), counters.cb
    ):
        return 0
    return int(counters.WorkingSetSize)


class PeakRssSampler:
    def __init__(self, interval: float = 0.02) -> None:
        self.interval = interval
        self.peak = current_rss_bytes()
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._sample, daemon=True)

    def _sample(self) -> None:
        while not self._stop.wait(self.interval):
            self.peak = max(self.peak, current_rss_bytes())

    def __enter__(self) -> "PeakRssSampler":
        self._thread.start()
        return self

    def __exit__(self, *_args: object) -> None:
        self._stop.set()
        self._thread.join()
        self.peak = max(self.peak, current_rss_bytes())


@dataclass(frozen=True)
class StructuralMode:
    kind: str
    fanins: tuple[int, ...]
    raw_state: int | None = None


@dataclass(frozen=True)
class SolveResult:
    status: str
    elapsed_seconds: float
    variable_count: int
    clause_count: int
    clause_sha256: str
    peak_rss_bytes: int
    solver_stats: dict[str, int | float]
    xor_count: int | None = None
    or_count: int | None = None
    logic_cost: int | None = None
    selected_pairs: tuple[int, ...] = ()
    decompositions: tuple[tuple[int, tuple[int, ...]], ...] = ()
    low_modes: tuple[tuple[int, StructuralMode], ...] = ()
    pair_labels: tuple[tuple[int, int], ...] = ()
    pair_orientations: tuple[tuple[int, int | None, int | None], ...] = ()
    mappings: tuple[tuple[int, int], ...] = ()


def read_records(paths: Sequence[Path]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    seen: set[tuple[int, ...]] = set()
    for path in paths:
        for line_number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
            if not line.strip():
                continue
            record = json.loads(line)
            T = matrix(record, "T")
            if T in seen:
                continue
            seen.add(T)
            copied = dict(record)
            copied["source_path"] = str(path.resolve())
            copied["source_line"] = line_number
            records.append(copied)
    return records


def all_low_modes(steady: int) -> tuple[StructuralMode, ...]:
    support = bits(steady)
    if len(support) == 1:
        state = support[0]
        modes = [StructuralMode("direct_unit", ())]
        for common in range(BITS):
            if common == state:
                continue
            pair = steady | (1 << common)
            modes.append(StructuralMode("mediated_unit", (pair,), common))
        return tuple(modes)
    if len(support) == 2:
        left, right = support
        modes = [StructuralMode("direct_pair", (steady,))]
        for common in range(BITS):
            if common in support:
                continue
            first = (1 << left) | (1 << common)
            second = (1 << right) | (1 << common)
            modes.append(StructuralMode("mediated_pair", tuple(sorted((first, second)))))
        return tuple(modes)
    raise ValueError("low mode requested for non-low row")


def solve_record(
    T: Sequence[int],
    B: Sequence[int],
    C: Sequence[int],
    *,
    logic_budget: int,
    solver_name: str,
    budget_encoding: str,
    timeout_seconds: float = 0.0,
) -> SolveResult:
    from pysat.card import CardEnc, EncType
    from pysat.formula import IDPool
    from pysat.solvers import Solver

    if init.compose(C, T) != init.A or init.compose(T, C) != tuple(B):
        raise AssertionError("input matrix identities failed")
    if any(row == 0 or row.bit_count() > 4 for row in (*B, *C)):
        raise ValueError("rows are outside the supported depth-two family")

    started = time.perf_counter()
    pool = IDPool()
    clauses: list[list[int]] = []

    def var(name: str) -> int:
        return pool.id(name)

    def force(literal: int, value: bool) -> None:
        clauses.append([literal if value else -literal])

    def equiv_or(output: int, inputs: Iterable[int]) -> None:
        values = tuple(dict.fromkeys(inputs))
        if not values:
            force(output, False)
            return
        for value in values:
            clauses.append([-value, output])
        clauses.append([-output, *values])

    def equiv_and(output: int, left: int, right: int) -> None:
        clauses.extend(([-output, left], [-output, right], [output, -left, -right]))

    def equiv_and_not(output: int, left: int, right: int) -> None:
        clauses.extend(([-output, left], [-output, -right], [output, -left, right]))

    def exactly_one(values: Sequence[int]) -> None:
        unique = tuple(dict.fromkeys(values))
        clauses.append(list(unique))
        if len(unique) > 1:
            encoded = CardEnc.atmost(
                lits=list(unique), bound=1, vpool=pool, encoding=EncType.seqcounter
            )
            clauses.extend(encoded.clauses)

    def at_most(values: Sequence[int], bound: int) -> None:
        unique = tuple(dict.fromkeys(values))
        if len(unique) <= bound:
            return
        encoded = CardEnc.atmost(
            lits=list(unique), bound=bound, vpool=pool, encoding=EncType.seqcounter
        )
        clauses.extend(encoded.clauses)

    def guard_equal_constant(guard: int, value: int, constant: bool) -> None:
        clauses.append([-guard, value if constant else -value])

    def guard_xor_constant(
        guard: int, left: int, right: int, constant: bool
    ) -> None:
        if constant:
            clauses.extend(([-guard, left, right], [-guard, -left, -right]))
        else:
            clauses.extend(([-guard, -left, right], [-guard, left, -right]))

    def guarded_at_most_one(guard: int, values: Sequence[int]) -> None:
        # The sets contain only 32 elements.  Pairwise clauses avoid guarded
        # cardinality auxiliary variables and are propagation-strong here.
        for left_index, left in enumerate(values):
            for right in values[left_index + 1 :]:
                clauses.append([-guard, -left, -right])

    distinct_rows = tuple(dict.fromkeys((*B, *C)))
    finals = tuple(row for row in distinct_rows if row.bit_count() in (3, 4))
    final_options = {row: pair_partitions(row) for row in finals}
    b_low = tuple(row for row in B if row.bit_count() in (1, 2))
    low_modes = {row: all_low_modes(row) for row in b_low}
    c_pair_required = frozenset(row for row in C if row.bit_count() == 2)

    final_choice: dict[tuple[int, int], int] = {}
    for row in finals:
        values = []
        for option_index, _option in enumerate(final_options[row]):
            choice = var(f"final_{row:08x}_o{option_index}")
            final_choice[(row, option_index)] = choice
            values.append(choice)
        exactly_one(values)

    low_choice: dict[tuple[int, int], int] = {}
    for row in b_low:
        values = []
        for mode_index, _mode in enumerate(low_modes[row]):
            choice = var(f"low_{row:08x}_m{mode_index}")
            low_choice[(row, mode_index)] = choice
            values.append(choice)
        exactly_one(values)

    pair_structural_users: dict[int, list[int]] = defaultdict(list)
    for row in finals:
        for option_index, option in enumerate(final_options[row]):
            for pair in option:
                pair_structural_users[pair].append(final_choice[(row, option_index)])
    for row in b_low:
        for mode_index, mode in enumerate(low_modes[row]):
            for pair in mode.fanins:
                pair_structural_users[pair].append(low_choice[(row, mode_index)])
    pair_universe = frozenset((*c_pair_required, *pair_structural_users.keys()))
    selected = {pair: var(f"selected_{pair:08x}") for pair in sorted(pair_universe)}
    for pair in sorted(pair_universe):
        if pair in c_pair_required:
            force(selected[pair], True)
        else:
            equiv_or(selected[pair], pair_structural_users[pair])

    labels = {
        (pair, seed): var(f"label_{pair:08x}_s{seed}")
        for pair in sorted(pair_universe)
        for seed in range(BITS)
    }
    orientations = {
        (pair, seed): var(f"orient_{pair:08x}_s{seed}")
        for pair in sorted(pair_universe)
        for seed in range(BITS)
    }
    pin_left: dict[tuple[int, int], int] = {}
    pin_right: dict[tuple[int, int], int] = {}
    mapping_contributors: dict[tuple[int, int], list[int]] = defaultdict(list)
    for pair in sorted(pair_universe):
        pair_labels = [labels[(pair, seed)] for seed in range(BITS)]
        at_most(pair_labels, 2)
        for label in pair_labels:
            clauses.append([-label, selected[pair]])
        state_left, state_right = bits(pair)
        left_values = []
        right_values = []
        for seed in range(BITS):
            left = var(f"pin_left_{pair:08x}_s{seed}")
            right = var(f"pin_right_{pair:08x}_s{seed}")
            equiv_and(left, labels[(pair, seed)], orientations[(pair, seed)])
            equiv_and_not(right, labels[(pair, seed)], orientations[(pair, seed)])
            pin_left[(pair, seed)] = left
            pin_right[(pair, seed)] = right
            left_values.append(left)
            right_values.append(right)
            mapping_contributors[(seed, state_left)].append(left)
            mapping_contributors[(seed, state_right)].append(right)
        at_most(left_values, 1)
        at_most(right_values, 1)

    def add_residual(
        tag: str,
        guard: int,
        pair: int,
        target: int,
        raw_state: int,
    ) -> None:
        residuals = []
        for seed in range(BITS):
            residual = var(f"residual_{tag}_s{seed}")
            label = labels[(pair, seed)]
            if target >> seed & 1:
                clauses.extend(([-residual, -label], [residual, label]))
            else:
                clauses.extend(([-residual, label], [residual, -label]))
            residuals.append(residual)
            used = var(f"residual_used_{tag}_s{seed}")
            equiv_and(used, guard, residual)
            mapping_contributors[(seed, raw_state)].append(used)
        guarded_at_most_one(guard, residuals)

    # Global heavy finals are shared between B and C.  Only B occurrences add
    # tick-zero label constraints; C-only finals remain structural choices.
    b_target_by_steady = {steady: target for target, steady in zip(T, B)}
    for row in finals:
        target = b_target_by_steady.get(row)
        if target is None:
            continue
        for option_index, raw_option in enumerate(final_options[row]):
            choice = final_choice[(row, option_index)]
            if len(raw_option) == 1:
                pair = raw_option[0]
                raw_state = bits(row ^ pair)[0]
                add_residual(
                    f"heavy_{row:08x}_o{option_index}",
                    choice,
                    pair,
                    target,
                    raw_state,
                )
            else:
                left, right = raw_option
                for seed in range(BITS):
                    guard_xor_constant(
                        choice,
                        labels[(left, seed)],
                        labels[(right, seed)],
                        bool(target >> seed & 1),
                    )

    # A B low row chooses one physical output.  Direct unit/pair and every
    # same-function mediated construction are all represented exactly.
    for target, steady in zip(T, B):
        if steady.bit_count() not in (1, 2):
            continue
        for mode_index, mode in enumerate(low_modes[steady]):
            choice = low_choice[(steady, mode_index)]
            if mode.kind == "direct_unit":
                if target.bit_count() != 1:
                    force(choice, False)
                else:
                    mapping_contributors[(bits(target)[0], bits(steady)[0])].append(choice)
            elif mode.kind == "direct_pair":
                pair = mode.fanins[0]
                if target.bit_count() > 2:
                    force(choice, False)
                else:
                    for seed in range(BITS):
                        guard_equal_constant(
                            choice,
                            labels[(pair, seed)],
                            bool(target >> seed & 1),
                        )
            elif mode.kind == "mediated_unit":
                add_residual(
                    f"unit_{steady:08x}_m{mode_index}",
                    choice,
                    mode.fanins[0],
                    target,
                    int(mode.raw_state),
                )
            elif mode.kind == "mediated_pair":
                left, right = mode.fanins
                for seed in range(BITS):
                    guard_xor_constant(
                        choice,
                        labels[(left, seed)],
                        labels[(right, seed)],
                        bool(target >> seed & 1),
                    )
            else:
                raise AssertionError(f"unknown mode {mode.kind}")

    mappings: dict[tuple[int, int], int] = {}
    for atom, contributors in sorted(mapping_contributors.items()):
        used = var(f"mapping_s{atom[0]}_q{atom[1]}")
        equiv_or(used, contributors)
        mappings[atom] = used
    for seed in range(BITS):
        seed_mappings = [
            used for (mapped_seed, _state), used in mappings.items() if mapped_seed == seed
        ]
        clauses.append(seed_mappings)

    mediated_choices = [
        low_choice[(row, mode_index)]
        for row in b_low
        for mode_index, mode in enumerate(low_modes[row])
        if mode.kind.startswith("mediated_")
    ]
    encoding_by_name = {
        "seqcounter": EncType.seqcounter,
        "sortnetwrk": EncType.sortnetwrk,
        "cardnetwrk": EncType.cardnetwrk,
        "totalizer": EncType.totalizer,
        "mtotalizer": EncType.mtotalizer,
        "kmtotalizer": EncType.kmtotalizer,
    }
    selected_budget_encoding = encoding_by_name[budget_encoding]
    # Three distinct equivalent cost literals encode each real XOR2's 3-gate
    # cost without relying on the optional pypblib package.
    xor_cost_bases = [*selected.values(), *mediated_choices]
    xor_cost_literals: list[int] = []
    for index, base in enumerate(xor_cost_bases):
        for copy_index in range(3):
            copy = var(f"xor_cost_{index}_{copy_index}")
            clauses.extend(([-copy, base], [copy, -base]))
            xor_cost_literals.append(copy)
    fixed_final_cost = 3 * len(finals)
    variable_budget = logic_budget - fixed_final_cost
    cost_inputs = [*xor_cost_literals, *mappings.values()]
    if variable_budget < 0:
        clauses.append([])
    elif variable_budget < len(cost_inputs):
        budget = CardEnc.atmost(
            lits=cost_inputs,
            bound=variable_budget,
            vpool=pool,
            encoding=selected_budget_encoding,
        )
        clauses.extend(budget.clauses)

    digest = hashlib.sha256()
    for clause in clauses:
        digest.update(" ".join(str(value) for value in clause).encode("ascii"))
        digest.update(b" 0\n")
    clause_sha256 = digest.hexdigest()

    with PeakRssSampler() as memory:
        with Solver(name=solver_name, bootstrap_with=clauses) as solver:
            timer = None
            if timeout_seconds:
                timer = threading.Timer(timeout_seconds, solver.interrupt)
                timer.daemon = True
                timer.start()
            try:
                solved = (
                    solver.solve_limited(expect_interrupt=True)
                    if timeout_seconds
                    else solver.solve()
                )
            finally:
                if timer is not None:
                    timer.cancel()
            model = solver.get_model() if solved is True else None
            stats = solver.accum_stats()
    elapsed = time.perf_counter() - started
    base_result = dict(
        status="sat" if solved is True else "unsat" if solved is False else "unknown",
        elapsed_seconds=elapsed,
        variable_count=pool.top,
        clause_count=len(clauses),
        clause_sha256=clause_sha256,
        peak_rss_bytes=memory.peak,
        solver_stats={key: value for key, value in stats.items() if isinstance(value, (int, float))},
    )
    if model is None:
        return SolveResult(**base_result)

    enabled = frozenset(value for value in model if value > 0)
    chosen_pairs = tuple(sorted(pair for pair, value in selected.items() if value in enabled))
    chosen_decompositions = []
    for row in finals:
        chosen = [
            final_options[row][option_index]
            for option_index in range(len(final_options[row]))
            if final_choice[(row, option_index)] in enabled
        ]
        if len(chosen) != 1:
            raise AssertionError("final decomposition is not one-hot")
        chosen_decompositions.append((row, chosen[0]))
    chosen_low_modes = []
    for row in b_low:
        chosen = [
            low_modes[row][mode_index]
            for mode_index in range(len(low_modes[row]))
            if low_choice[(row, mode_index)] in enabled
        ]
        if len(chosen) != 1:
            raise AssertionError("low mode is not one-hot")
        chosen_low_modes.append((row, chosen[0]))
    pair_labels = tuple(
        sorted(
            (
                pair,
                sum(1 << seed for seed in range(BITS) if labels[(pair, seed)] in enabled),
            )
            for pair in chosen_pairs
        )
    )
    pair_orientations = []
    for pair, label in pair_labels:
        state_left, state_right = bits(pair)
        left_seed = next(
            (seed for seed in bits(label) if pin_left[(pair, seed)] in enabled), None
        )
        right_seed = next(
            (seed for seed in bits(label) if pin_right[(pair, seed)] in enabled), None
        )
        pair_orientations.append((pair, left_seed, right_seed))
        if left_seed is not None and (left_seed, state_left) not in mappings:
            raise AssertionError("left mapping atom was not encoded")
        if right_seed is not None and (right_seed, state_right) not in mappings:
            raise AssertionError("right mapping atom was not encoded")
    chosen_mappings = tuple(sorted(atom for atom, value in mappings.items() if value in enabled))
    mediated_count = sum(mode.kind.startswith("mediated_") for _row, mode in chosen_low_modes)
    xor_count = len(finals) + len(chosen_pairs) + mediated_count
    or_count = len(chosen_mappings)
    logic_cost = 3 * xor_count + or_count
    if logic_cost > logic_budget:
        raise AssertionError("SAT assignment exceeds logic budget")
    result = SolveResult(
        **base_result,
        xor_count=xor_count,
        or_count=or_count,
        logic_cost=logic_cost,
        selected_pairs=chosen_pairs,
        decompositions=tuple(chosen_decompositions),
        low_modes=tuple(chosen_low_modes),
        pair_labels=pair_labels,
        pair_orientations=tuple(pair_orientations),
        mappings=chosen_mappings,
    )
    verify_certificate(T, B, C, result, logic_budget=logic_budget)
    return result


def verify_certificate(
    T: Sequence[int],
    B: Sequence[int],
    C: Sequence[int],
    result: SolveResult,
    *,
    logic_budget: int,
) -> None:
    if result.status != "sat":
        raise ValueError("certificate verifier requires SAT result")
    selected = frozenset(result.selected_pairs)
    decompositions = dict(result.decompositions)
    low_modes = dict(result.low_modes)
    labels = dict(result.pair_labels)
    orientations = {
        pair: (left_seed, right_seed)
        for pair, left_seed, right_seed in result.pair_orientations
    }
    mappings = frozenset(result.mappings)
    required_mappings: set[tuple[int, int]] = set()

    for pair in selected:
        label = labels[pair]
        if label.bit_count() > 2:
            raise AssertionError("pair label exceeds two XOR pins")
        state_left, state_right = bits(pair)
        left_seed, right_seed = orientations[pair]
        actual = (0 if left_seed is None else 1 << left_seed) ^ (
            0 if right_seed is None else 1 << right_seed
        )
        if actual != label:
            raise AssertionError("pair orientation does not realize label")
        if left_seed is not None:
            required_mappings.add((left_seed, state_left))
        if right_seed is not None:
            required_mappings.add((right_seed, state_right))

    for row in frozenset((*B, *C)):
        weight = row.bit_count()
        if weight == 2 and row in C and row not in selected:
            raise AssertionError("C pair output is absent")
        if weight in (3, 4):
            option = decompositions[row]
            if not set(option) <= selected:
                raise AssertionError("heavy decomposition pair is absent")
            if len(option) == 1:
                actual = option[0] ^ (row ^ option[0])
            else:
                actual = option[0] ^ option[1]
            if actual != row:
                raise AssertionError("heavy steady decomposition is invalid")

    for target, steady in zip(T, B):
        weight = steady.bit_count()
        if weight in (1, 2):
            mode = low_modes[steady]
            if mode.kind == "direct_unit":
                if target.bit_count() != 1:
                    raise AssertionError("direct unit label is not a unit")
                required_mappings.add((bits(target)[0], bits(steady)[0]))
                actual = target
            elif mode.kind == "direct_pair":
                if mode.fanins != (steady,) or steady not in selected:
                    raise AssertionError("invalid direct pair mode")
                actual = labels[steady]
            elif mode.kind == "mediated_unit":
                pair = mode.fanins[0]
                if pair not in selected or (pair ^ steady).bit_count() != 1:
                    raise AssertionError("invalid mediated unit structure")
                residual = target ^ labels[pair]
                if residual.bit_count() > 1:
                    raise AssertionError("mediated unit residual is not a unit")
                if residual:
                    required_mappings.add((bits(residual)[0], int(mode.raw_state)))
                actual = labels[pair] ^ residual
            elif mode.kind == "mediated_pair":
                left, right = mode.fanins
                if left not in selected or right not in selected or left ^ right != steady:
                    raise AssertionError("invalid mediated pair structure")
                actual = labels[left] ^ labels[right]
            else:
                raise AssertionError("unknown low mode")
        elif weight == 3:
            pair = decompositions[steady][0]
            residual = target ^ labels[pair]
            if residual.bit_count() > 1:
                raise AssertionError("heavy residual is not a unit")
            if residual:
                raw_state = bits(steady ^ pair)[0]
                required_mappings.add((bits(residual)[0], raw_state))
            actual = labels[pair] ^ residual
        elif weight == 4:
            left, right = decompositions[steady]
            actual = labels[left] ^ labels[right]
        else:
            raise AssertionError("unsupported feedback row")
        if actual != target:
            raise AssertionError("tick-zero feedback label mismatch")

    if mappings != required_mappings:
        raise AssertionError("reported OR mapping union is not exact")
    if {seed for seed, _state in mappings} != set(range(BITS)):
        raise AssertionError("not every input seed bit is consumed")
    mediated_count = sum(mode.kind.startswith("mediated_") for mode in low_modes.values())
    xor_count = len(decompositions) + len(selected) + mediated_count
    if xor_count != result.xor_count or len(mappings) != result.or_count:
        raise AssertionError("certificate cost count mismatch")
    if 3 * xor_count + len(mappings) != result.logic_cost:
        raise AssertionError("certificate weighted cost mismatch")
    if result.logic_cost > logic_budget:
        raise AssertionError("certificate is over budget")
    if init.compose(C, T) != init.A or init.compose(T, C) != tuple(B):
        raise AssertionError("certificate matrix identity failed")


def encode_result(result: SolveResult) -> dict[str, Any]:
    value = asdict(result)
    value["peak_rss_mb"] = round(result.peak_rss_bytes / 1048576, 3)
    value["selected_pairs"] = [f"{pair:08x}" for pair in result.selected_pairs]
    value["decompositions"] = {
        f"{row:08x}": [f"{pair:08x}" for pair in option]
        for row, option in result.decompositions
    }
    value["low_modes"] = {
        f"{row:08x}": {
            "kind": mode.kind,
            "fanins": [f"{pair:08x}" for pair in mode.fanins],
            "raw_state": mode.raw_state,
        }
        for row, mode in result.low_modes
    }
    value["pair_labels"] = {
        f"{pair:08x}": f"{label:08x}" for pair, label in result.pair_labels
    }
    value["pair_orientations"] = {
        f"{pair:08x}": [left, right]
        for pair, left, right in result.pair_orientations
    }
    value["mappings"] = [
        {"seed": seed, "state": state} for seed, state in result.mappings
    ]
    return value


def audit(args: argparse.Namespace) -> dict[str, Any]:
    records = read_records(args.inputs)
    if args.start_index:
        records = records[args.start_index :]
    if args.record_limit:
        records = records[: args.record_limit]
    started = time.perf_counter()
    statuses: Counter[str] = Counter()
    results = []
    winner = None
    peak_rss = current_rss_bytes()
    if args.checkpoint is not None:
        args.checkpoint.parent.mkdir(parents=True, exist_ok=True)
        args.checkpoint.write_text("", encoding="utf-8")
    for index, record in enumerate(records):
        T, B, C = (matrix(record, name) for name in ("T", "B", "C"))
        result = solve_record(
            T,
            B,
            C,
            logic_budget=args.logic_budget,
            solver_name=args.solver,
            budget_encoding=args.budget_encoding,
            timeout_seconds=args.timeout_seconds,
        )
        statuses[result.status] += 1
        peak_rss = max(peak_rss, result.peak_rss_bytes)
        item = {
            "record": index + args.start_index,
            "source_path": record["source_path"],
            "source_line": record["source_line"],
            "radius": record.get("radius"),
            "parent": record.get("parent"),
            "dst": record.get("dst"),
            "src": record.get("src"),
            "source_greedy_xor": record.get("xor"),
            "T_sha256": hashlib.sha256(
                "".join(f"{row:08x}" for row in T).encode("ascii")
            ).hexdigest(),
            **encode_result(result),
        }
        if result.status == "sat":
            item["T"] = [f"{row:08x}" for row in T]
            item["B"] = [f"{row:08x}" for row in B]
            item["C"] = [f"{row:08x}" for row in C]
            item["verification"] = {
                "matrix_identities": True,
                "certificate_replay": True,
                "actual_test_seeds": 256,
                "ticks_per_seed": 65,
                "seed_vector_sha256": verify_256x65(T, B, C),
            }
            winner = item
            args.certificate.parent.mkdir(parents=True, exist_ok=True)
            args.certificate.write_text(json.dumps(item, indent=2) + "\n", encoding="utf-8")
            print(
                f"SAT source={record['source_line']} xor={result.xor_count} "
                f"or={result.or_count} cost={result.logic_cost}",
                flush=True,
            )
        results.append(item)
        if args.checkpoint is not None:
            with args.checkpoint.open("a", encoding="utf-8", newline="\n") as stream:
                stream.write(json.dumps(item, separators=(",", ":")) + "\n")
        print(
            f"record={index + 1}/{len(records)} status={result.status} "
            f"xor={result.xor_count} or={result.or_count} "
            f"seconds={result.elapsed_seconds:.3f} rss={result.peak_rss_bytes / 1048576:.1f}MiB",
            flush=True,
        )
        if winner is not None and args.stop_on_sat:
            break

    has_unknown = bool(statuses["unknown"])
    completed_all = len(results) == len(records) and not has_unknown
    return {
        "schema": 1,
        "status": (
            "sat"
            if winner is not None
            else "unknown"
            if has_unknown
            else "unsat-complete"
        ),
        "model": "exact joint arbitrary pair cover + mediated B weight1/2 + tick-zero OR labels",
        "complete": winner is not None or completed_all,
        "truncated": has_unknown,
        "topology_limit": None,
        "component_limit": None,
        "global_beam": None,
        "cost": {
            "fixed_shell_gate": FIXED_SHELL_GATE,
            "xor2_gate": 3,
            "xor2_delay": 2,
            "or_gate": 1,
            "or_delay": 1,
            "logic_budget": args.logic_budget,
        },
        "target": {
            "gate": FIXED_SHELL_GATE + args.logic_budget,
            "delay": 10,
            "cycles": 66,
        },
        "input_record_count": len(records),
        "processed_record_count": len(results),
        "statuses": dict(statuses),
        "solver": args.solver,
        "budget_encoding": args.budget_encoding,
        "timeout_seconds_per_record": args.timeout_seconds or None,
        "peak_rss_bytes": peak_rss,
        "peak_rss_mb": round(peak_rss / 1048576, 3),
        "elapsed_seconds": time.perf_counter() - started,
        "winner": winner,
        "records": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", type=Path, nargs="+")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--certificate", type=Path, default=HERE / "sat-certificate.json")
    parser.add_argument("--logic-budget", type=int, default=DEFAULT_LOGIC_BUDGET)
    parser.add_argument("--solver", default="g4")
    parser.add_argument(
        "--budget-encoding",
        choices=("seqcounter", "sortnetwrk", "cardnetwrk", "totalizer", "mtotalizer", "kmtotalizer"),
        default="seqcounter",
    )
    parser.add_argument("--start-index", type=int, default=0)
    parser.add_argument("--record-limit", type=int, default=0)
    parser.add_argument("--timeout-seconds", type=float, default=0.0)
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--stop-on-sat", action="store_true")
    args = parser.parse_args()
    if (
        args.logic_budget < 0
        or args.start_index < 0
        or args.record_limit < 0
        or args.timeout_seconds < 0
    ):
        parser.error("budgets and indexes must be non-negative")
    result = audit(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "records"}, indent=2))
    return 0 if result["status"] == "sat" else 2 if result["status"] == "unsat-complete" else 3


if __name__ == "__main__":
    raise SystemExit(main())
