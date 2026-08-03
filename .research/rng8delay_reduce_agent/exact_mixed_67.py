"""Exact 67-cycle mixed native/Switch depth-two audit for the RNG.

The model jointly chooses the steady-state XOR2 DAG and its tick-zero labels.
It is deliberately independent from the save generator and never starts the
game or reads/writes the live save.

For an active first-layer pair, an ordinary positive XOR rail costs three
gates.  If that pair feeds a final XOR, one additional primitive produces the
complementary rail.  A final XOR is implemented by two mutually-exclusive Bit
Switches and costs four gates at one further delay.  A direct raw/mode leaf
feeding such a final XOR needs one shared NOT rail.  Distinct (seed, state)
mode leaves each cost one OR gate.  Thus the exact combinational objective is

    mode_or + 3*pair + dual_pair + direct_not
            + 3*final_native_xor + 4*final_switch_xor + terminal_split

and the complete gate count adds the reviewed 172-gate zero-state shell.

The zero-initialized two-phase protocol spends tick zero idle and tick one
loading ``T*seed``.  Its direct load pulse reaches the Architecture Input at
delay four.  Only feedback rows in ``B`` have a prescribed load label (the
corresponding row of ``T``); a C-only row is unobserved during load.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import dataclass
import hashlib
import importlib.util
import json
from pathlib import Path
import random
import sys
import threading
import time
from typing import Any, Iterable, Sequence


BITS = 32
FIXED_SHELL = 172
TARGET_GATE = 452
TARGET_DELAY = 8
TARGET_CYCLES = 67
LOGIC_BUDGET = TARGET_GATE - FIXED_SHELL
REFERENCE_XOR = 59
ALLOW_TERMINAL_SPLIT = False

DEFAULT_EXCLUDED_LINES = (
    15404,
    67862,
    67865,
    67975,
    67980,
    68049,
    68125,
    68139,
    68140,
    68356,
    147298,
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def bits(mask: int) -> tuple[int, ...]:
    return tuple(bit for bit in range(BITS) if mask >> bit & 1)


def matrix(record: dict[str, Any], key: str) -> tuple[int, ...]:
    values = record[key]
    if not isinstance(values, list) or len(values) != BITS:
        raise ValueError(f"{key} must contain 32 rows")
    return tuple(int(str(value), 16) for value in values)


@dataclass(frozen=True)
class Option:
    name: str
    pairs: tuple[int, ...]
    direct_state: int | None
    final: bool


@dataclass
class DirectSite:
    row: int
    option_index: int
    state: int
    choice: int
    labels: tuple[int, ...]
    zero: int
    final: bool


@dataclass
class Encoding:
    wcnf: Any
    pool: Any
    row_options: dict[int, tuple[Option, ...]]
    choice_vars: dict[tuple[int, int], int]
    pair_active: dict[int, int]
    pair_dual: dict[int, int]
    pair_labels: dict[tuple[int, int], int]
    orientations: dict[tuple[int, int, int], int]
    direct_sites: dict[tuple[int, int], DirectSite]
    direct_not_used: dict[tuple[int, int], int]
    mappings: dict[tuple[int, int], int]
    final_native: dict[tuple[int, int], int]
    final_switch: dict[tuple[int, int], int]
    terminal_split: dict[tuple[int, int], int]
    cost_terms: dict[str, tuple[tuple[int, int], ...]]


class MemoryMonitor:
    def __init__(self) -> None:
        self.peak = 0
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def __enter__(self):
        try:
            import psutil
        except ImportError:
            psutil = None

        if psutil is not None:
            process = psutil.Process()

            def resident_bytes() -> int:
                return process.memory_info().rss

        else:
            # Keep the audit dependency-free on Windows.  This fallback is
            # only used when psutil is absent from the project environment.
            import ctypes
            from ctypes import wintypes

            class ProcessMemoryCounters(ctypes.Structure):
                _fields_ = [
                    ("cb", wintypes.DWORD),
                    ("PageFaultCount", wintypes.DWORD),
                    ("PeakWorkingSetSize", ctypes.c_size_t),
                    ("WorkingSetSize", ctypes.c_size_t),
                    ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                    ("PagefileUsage", ctypes.c_size_t),
                    ("PeakPagefileUsage", ctypes.c_size_t),
                ]

            get_current_process = ctypes.windll.kernel32.GetCurrentProcess
            get_process_memory_info = ctypes.windll.psapi.GetProcessMemoryInfo
            get_current_process.restype = wintypes.HANDLE
            get_process_memory_info.argtypes = (
                wintypes.HANDLE,
                ctypes.POINTER(ProcessMemoryCounters),
                wintypes.DWORD,
            )
            get_process_memory_info.restype = wintypes.BOOL

            def resident_bytes() -> int:
                counters = ProcessMemoryCounters()
                counters.cb = ctypes.sizeof(counters)
                if not get_process_memory_info(
                    get_current_process(),
                    ctypes.byref(counters),
                    counters.cb,
                ):
                    return 0
                return int(counters.WorkingSetSize)

        def sample() -> None:
            while not self._stop.wait(0.05):
                self.peak = max(self.peak, resident_bytes())
            self.peak = max(self.peak, resident_bytes())

        self._thread = threading.Thread(target=sample, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, _type, _value, _traceback) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join()


def options_for_row(row: int, pair_partitions) -> tuple[Option, ...]:
    support = bits(row)
    weight = len(support)
    if weight == 1:
        direct = Option("direct", (), support[0], False)
        mediated = tuple(
            Option(
                f"mediated:{row | (1 << other):08x}",
                (row | (1 << other),),
                other,
                True,
            )
            for other in range(BITS)
            if other != support[0]
        )
        return (direct, *mediated)
    if weight == 2:
        left, right = support
        direct = Option("direct", (row,), None, False)
        mediated = tuple(
            Option(
                f"mediated:{((1 << left) | (1 << common)):08x}^"
                f"{((1 << right) | (1 << common)):08x}",
                tuple(
                    sorted(
                        (
                            (1 << left) | (1 << common),
                            (1 << right) | (1 << common),
                        )
                    )
                ),
                None,
                True,
            )
            for common in range(BITS)
            if common not in support
        )
        return (direct, *mediated)
    if weight == 3:
        result = []
        for (pair,) in pair_partitions(row):
            direct = bits(row ^ pair)[0]
            result.append(
                Option(f"heavy:{pair:08x}+q{direct}", (pair,), direct, True)
            )
        return tuple(result)
    if weight == 4:
        return tuple(
            Option(
                f"heavy:{left:08x}^{right:08x}",
                tuple(sorted((left, right))),
                None,
                True,
            )
            for left, right in pair_partitions(row)
        )
    raise ValueError(f"unsupported steady row {row:08x} weight {weight}")


def append_at_most_one(wcnf, literals: Sequence[int]) -> None:
    for left in range(len(literals)):
        for right in range(left + 1, len(literals)):
            wcnf.append([-literals[left], -literals[right]])


def append_exactly_one(wcnf, literals: Sequence[int]) -> None:
    wcnf.append(list(literals))
    append_at_most_one(wcnf, literals)


def append_conditional_bit(
    wcnf, guard: int, literal: int, expected: int
) -> None:
    wcnf.append([-guard, literal if expected else -literal])


def append_conditional_xor(
    wcnf, guard: int, left: int, right: int, expected: int
) -> None:
    if expected:
        wcnf.append([-guard, -left, -right])
        wcnf.append([-guard, left, right])
    else:
        wcnf.append([-guard, -left, right])
        wcnf.append([-guard, left, -right])


def build_encoding(
    dual,
    init,
    T: tuple[int, ...],
    B: tuple[int, ...],
    C: tuple[int, ...],
) -> Encoding:
    from pysat.formula import IDPool, WCNF

    pool = IDPool()
    wcnf = WCNF()
    targets_by_row: dict[int, set[int]] = {
        steady: set() for steady in dict.fromkeys((*B, *C))
    }
    for target, steady in zip(T, B, strict=True):
        targets_by_row[steady].add(target)

    row_options = {
        row: options_for_row(row, dual.pair_partitions)
        for row in sorted(targets_by_row)
    }
    choice_vars: dict[tuple[int, int], int] = {}
    for row, options in row_options.items():
        choices = []
        for index in range(len(options)):
            variable = pool.id(("choice", row, index))
            choice_vars[(row, index)] = variable
            choices.append(variable)
        append_exactly_one(wcnf, choices)

    final_native: dict[tuple[int, int], int] = {}
    final_switch: dict[tuple[int, int], int] = {}
    terminal_split: dict[tuple[int, int], int] = {}
    for row, options in row_options.items():
        for index, option in enumerate(options):
            if not option.final:
                continue
            choice = choice_vars[(row, index)]
            native = pool.id(("final_native", row, index))
            switch = pool.id(("final_switch", row, index))
            final_native[(row, index)] = native
            final_switch[(row, index)] = switch
            # A selected final uses exactly one physical implementation.
            wcnf.append([-native, choice])
            wcnf.append([-switch, choice])
            wcnf.append([-choice, native, switch])
            wcnf.append([-native, -switch])

    # A weight-two B row may keep its shared pair completely raw/fast and
    # perform the one-shot seed correction only on the row's state-input
    # terminal.  This decouples the pair's reusable steady rail from its load
    # label.  A balanced seed parity plus one OR costs 3*(w-1)+1 and reaches
    # the terminal within delay 7 for label weight at most eight.
    terminal_split_cost: dict[tuple[int, int], int] = {}
    for row, options in row_options.items():
        if not ALLOW_TERMINAL_SPLIT:
            continue
        targets = targets_by_row[row]
        if row.bit_count() != 2 or len(targets) != 1:
            continue
        target = next(iter(targets))
        weight = target.bit_count()
        if not 1 <= weight <= 8:
            continue
        for index, option in enumerate(options):
            if option.final or option.pairs != (row,) or option.direct_state is not None:
                continue
            choice = choice_vars[(row, index)]
            split = pool.id(("terminal_split", row, index))
            terminal_split[(row, index)] = split
            terminal_split_cost[(row, index)] = 3 * (weight - 1) + 1
            wcnf.append([-split, choice])

    pair_causes: dict[int, list[int]] = defaultdict(list)
    dual_causes: dict[int, list[int]] = defaultdict(list)
    for row, options in row_options.items():
        for index, option in enumerate(options):
            choice = choice_vars[(row, index)]
            for pair in option.pairs:
                pair_causes[pair].append(choice)
                if option.final:
                    dual_causes[pair].append(final_switch[(row, index)])

    pair_active = {
        pair: pool.id(("pair_active", pair)) for pair in sorted(pair_causes)
    }
    pair_dual = {
        pair: pool.id(("pair_dual", pair)) for pair in sorted(dual_causes)
    }
    for pair, causes in pair_causes.items():
        active = pair_active[pair]
        for cause in causes:
            wcnf.append([-cause, active])
        wcnf.append([-active, *dict.fromkeys(causes)])
    for pair, causes in dual_causes.items():
        dual_var = pair_dual[pair]
        for cause in causes:
            wcnf.append([-cause, dual_var])
        wcnf.append([-dual_var, *dict.fromkeys(causes)])

    mapping_causes: dict[tuple[int, int], list[int]] = defaultdict(list)
    orientations: dict[tuple[int, int, int], int] = {}
    pair_labels: dict[tuple[int, int], int] = {}
    for pair, active in pair_active.items():
        states = bits(pair)
        if len(states) != 2:
            raise AssertionError("non-pair admitted to first layer")
        pin_rows = []
        for pin, state in enumerate(states):
            pin_vars = []
            for seed in range(BITS):
                variable = pool.id(("orientation", pair, pin, seed))
                orientations[(pair, pin, seed)] = variable
                pin_vars.append(variable)
                wcnf.append([-variable, active])
                mapping_causes[(seed, state)].append(variable)
            append_at_most_one(wcnf, pin_vars)
            pin_rows.append(pin_vars)
        for seed in range(BITS):
            left = pin_rows[0][seed]
            right = pin_rows[1][seed]
            label = pool.id(("pair_label", pair, seed))
            pair_labels[(pair, seed)] = label
            wcnf.append([-left, label])
            wcnf.append([-right, label])
            wcnf.append([-label, left, right])
            wcnf.append([-left, -right])

    for (row, index), split in terminal_split.items():
        option = row_options[row][index]
        for pair in option.pairs:
            for seed in range(BITS):
                wcnf.append([-split, -pair_labels[(pair, seed)]])

    # A native XOR adds two delay after its operands.  A pair with a nonzero
    # load label contains a mode OR and arrives at 4+1+2=7, so it would make
    # the final arrive at 9.  Native finals are therefore legal exactly when
    # every pair operand has a zero load label; direct operands still arrive
    # by 5 and do not need an additional restriction.
    for row, options in row_options.items():
        for index, option in enumerate(options):
            native = final_native.get((row, index))
            if native is None:
                continue
            for pair in option.pairs:
                for seed in range(BITS):
                    wcnf.append([-native, -pair_labels[(pair, seed)]])

    direct_sites: dict[tuple[int, int], DirectSite] = {}
    direct_not_causes: dict[tuple[int, int], list[int]] = defaultdict(list)
    for row, options in row_options.items():
        for index, option in enumerate(options):
            if option.direct_state is None:
                continue
            choice = choice_vars[(row, index)]
            labels = tuple(
                pool.id(("direct_label", row, index, seed))
                for seed in range(BITS)
            )
            append_at_most_one(wcnf, labels)
            for seed, label in enumerate(labels):
                wcnf.append([-label, choice])
                mapping_causes[(seed, option.direct_state)].append(label)
            zero = pool.id(("direct_zero", row, index))
            wcnf.append([-zero, choice])
            for label in labels:
                wcnf.append([-zero, -label])
            wcnf.append([-choice, zero, *labels])
            site = DirectSite(
                row,
                index,
                option.direct_state,
                choice,
                labels,
                zero,
                option.final,
            )
            direct_sites[(row, index)] = site
            if option.final:
                switch = final_switch[(row, index)]

                def add_switch_cause(key: tuple[int, int], rail: int) -> None:
                    cause = pool.id(("direct_not_cause", row, index, key[1]))
                    wcnf.append([-cause, switch])
                    wcnf.append([-cause, rail])
                    wcnf.append([-switch, -rail, cause])
                    direct_not_causes[key].append(cause)

                add_switch_cause((option.direct_state, -1), zero)
                for seed, label in enumerate(labels):
                    add_switch_cause((option.direct_state, seed), label)

    # Constrain the shared tick-zero label of every generated steady row.
    for row, options in row_options.items():
        for index, option in enumerate(options):
            choice = choice_vars[(row, index)]
            site = direct_sites.get((row, index))
            for target in targets_by_row[row]:
                for seed in range(BITS):
                    signals = [pair_labels[(pair, seed)] for pair in option.pairs]
                    if site is not None:
                        signals.append(site.labels[seed])
                    split = terminal_split.get((row, index))
                    if len(signals) == 1:
                        expected = target >> seed & 1
                        clause = [
                            -choice,
                            signals[0] if expected else -signals[0],
                        ]
                        if split is not None:
                            clause.insert(1, split)
                        wcnf.append(clause)
                    elif len(signals) == 2:
                        expected = target >> seed & 1
                        left, right = signals
                        clauses = (
                            ((-left, -right), (left, right))
                            if expected
                            else ((-left, right), (left, -right))
                        )
                        for terms in clauses:
                            clause = [-choice, *terms]
                            if split is not None:
                                clause.insert(1, split)
                            wcnf.append(clause)
                    else:
                        raise AssertionError(
                            f"option {row:08x}/{option.name} has {len(signals)} rails"
                        )

    mappings = {
        key: pool.id(("mapping", *key)) for key in sorted(mapping_causes)
    }
    for key, causes in mapping_causes.items():
        used = mappings[key]
        for cause in causes:
            wcnf.append([-cause, used])
        wcnf.append([-used, *dict.fromkeys(causes)])

    direct_not_used = {
        key: pool.id(("direct_not", *key))
        for key in sorted(direct_not_causes)
    }
    for key, causes in direct_not_causes.items():
        used = direct_not_used[key]
        for cause in causes:
            wcnf.append([-cause, used])
        wcnf.append([-used, *dict.fromkeys(causes)])

    cost_terms: dict[str, tuple[tuple[int, int], ...]] = {
        "mode_or": tuple((variable, 1) for variable in mappings.values()),
        "pair_xor": tuple((variable, 3) for variable in pair_active.values()),
        "dual_pair_extra": tuple((variable, 1) for variable in pair_dual.values()),
        "direct_not": tuple((variable, 1) for variable in direct_not_used.values()),
        "final_native": tuple((variable, 3) for variable in final_native.values()),
        "final_switch": tuple(
            (variable, 4) for variable in final_switch.values()
        ),
        "terminal_split": tuple(
            (terminal_split[key], cost)
            for key, cost in terminal_split_cost.items()
        ),
    }
    for terms in cost_terms.values():
        for variable, weight in terms:
            wcnf.append([-variable], weight=weight)

    return Encoding(
        wcnf,
        pool,
        row_options,
        choice_vars,
        pair_active,
        pair_dual,
        pair_labels,
        orientations,
        direct_sites,
        direct_not_used,
        mappings,
        final_native,
        final_switch,
        terminal_split,
        cost_terms,
    )


def enabled(positive: set[int], variable: int) -> bool:
    return variable in positive


def decode_and_verify(
    init,
    T: tuple[int, ...],
    B: tuple[int, ...],
    C: tuple[int, ...],
    encoding: Encoding,
    model: Sequence[int],
    optimum: int,
) -> dict[str, Any]:
    positive = {literal for literal in model if literal > 0}
    choices: dict[int, tuple[int, Option]] = {}
    for row, options in encoding.row_options.items():
        selected = [
            (index, option)
            for index, option in enumerate(options)
            if enabled(positive, encoding.choice_vars[(row, index)])
        ]
        if len(selected) != 1:
            raise AssertionError(f"row {row:08x} does not select one topology")
        choices[row] = selected[0]

    final_implementations: dict[tuple[int, int], str] = {}
    for key, variable in encoding.final_native.items():
        if enabled(positive, variable):
            final_implementations[key] = "native"
    for key, variable in encoding.final_switch.items():
        if enabled(positive, variable):
            if key in final_implementations:
                raise AssertionError("final selects native and Switch")
            final_implementations[key] = "switch"
    selected_terminal_splits = {
        key
        for key, variable in encoding.terminal_split.items()
        if enabled(positive, variable)
    }

    active_pairs = {
        pair for pair, variable in encoding.pair_active.items() if enabled(positive, variable)
    }
    dual_pairs = {
        pair for pair, variable in encoding.pair_dual.items() if enabled(positive, variable)
    }
    pair_pin_seed: dict[int, tuple[int | None, int | None]] = {}
    pair_load_label: dict[int, int] = {}
    for pair in sorted(active_pairs):
        pin_values = []
        for pin in range(2):
            values = [
                seed
                for seed in range(BITS)
                if enabled(positive, encoding.orientations[(pair, pin, seed)])
            ]
            if len(values) > 1:
                raise AssertionError("pair pin has multiple seed labels")
            pin_values.append(None if not values else values[0])
        pair_pin_seed[pair] = (pin_values[0], pin_values[1])
        pair_load_label[pair] = sum(
            0 if seed is None else 1 << seed for seed in pin_values
        )

    direct_labels: dict[tuple[int, int], int] = {}
    selected_direct_rails = []
    for key, site in encoding.direct_sites.items():
        if not enabled(positive, site.choice):
            continue
        seeds = [
            seed for seed, variable in enumerate(site.labels) if enabled(positive, variable)
        ]
        if len(seeds) > 1:
            raise AssertionError("direct site has multiple labels")
        label = 0 if not seeds else 1 << seeds[0]
        direct_labels[key] = label
        selected_direct_rails.append(
            {
                "steady_row": f"{site.row:08x}",
                "option": encoding.row_options[site.row][site.option_index].name,
                "state_bit": site.state,
                "seed_bit": None if not seeds else seeds[0],
                "needs_not": final_implementations.get(key) == "switch",
            }
        )

    for target, steady in zip(T, B, strict=True):
        index, option = choices[steady]
        actual = 0
        for pair in option.pairs:
            actual ^= pair_load_label[pair]
        actual ^= direct_labels.get((steady, index), 0)
        if (steady, index) in selected_terminal_splits:
            if actual != 0:
                raise AssertionError("terminal split pair is not raw")
            actual = target
        if actual != target:
            raise AssertionError(
                f"tick-zero mismatch {steady:08x}: {actual:08x} != {target:08x}"
            )
        realized = 0
        for pair in option.pairs:
            realized ^= pair
        if option.direct_state is not None:
            realized ^= 1 << option.direct_state
        if realized != steady:
            raise AssertionError("steady-state topology does not realize row")
        if final_implementations.get((steady, index)) == "native":
            if any(pair_load_label[pair] for pair in option.pairs):
                raise AssertionError("native final has a late pair operand")

    if init.compose(C, T) != init.A or init.compose(T, C) != B:
        raise AssertionError("steady matrix identity failed")
    seeds = [0, 1, 2, 0x12345678, 0xFFFFFFFF, 0x80000000]
    generator = random.Random(20260803)
    seeds.extend(generator.getrandbits(BITS) for _ in range(64))
    for seed in seeds:
        natural = seed
        encoded = init.apply_matrix(T, seed)
        for _ in range(65):
            natural = init.xorshift32(natural)
            actual = init.apply_matrix(C, encoded)
            if actual != natural:
                raise AssertionError("67-cycle stream mismatch")
            encoded = init.apply_matrix(B, encoded)

    category_costs = {
        category: sum(
            weight for variable, weight in terms if enabled(positive, variable)
        )
        for category, terms in encoding.cost_terms.items()
    }
    logic_cost = sum(category_costs.values())
    if logic_cost != optimum:
        raise AssertionError(f"decoded cost {logic_cost} != RC2 optimum {optimum}")
    native_count = category_costs["final_native"] // 3
    switch_count = category_costs["final_switch"] // 4
    final_count = native_count + switch_count
    ordinary_xor = len(active_pairs) + final_count
    mappings = [
        {"seed": seed, "state": state}
        for (seed, state), variable in sorted(encoding.mappings.items())
        if enabled(positive, variable)
    ]
    direct_not_keys = [
        {"state": state, "seed": None if seed < 0 else seed}
        for (state, seed), variable in sorted(encoding.direct_not_used.items())
        if enabled(positive, variable)
    ]
    return {
        "metrics": {
            "shell": FIXED_SHELL,
            "logic": logic_cost,
            "gate": FIXED_SHELL + logic_cost,
            "delay": TARGET_DELAY,
            "cycles": TARGET_CYCLES,
            "energy": (FIXED_SHELL + logic_cost) * TARGET_DELAY * TARGET_CYCLES,
            "within_target": FIXED_SHELL + logic_cost <= TARGET_GATE,
            "ordinary_xor": ordinary_xor,
            "ordinary_excess_over_reference": ordinary_xor - REFERENCE_XOR,
            "pair_count": len(active_pairs),
            "dual_pair_count": len(dual_pairs),
            "direct_not_count": len(direct_not_keys),
            "final_native_xor_count": native_count,
            "final_switch_xor_count": switch_count,
            "mode_or_count": len(mappings),
            "terminal_split_count": len(selected_terminal_splits),
        },
        "category_costs": category_costs,
        "selected_options": {
            f"{row:08x}": option.name
            for row, (_index, option) in sorted(choices.items())
        },
        "final_implementations": {
            f"{row:08x}": implementation
            for (row, _index), implementation in sorted(final_implementations.items())
        },
        "terminal_splits": [
            {
                "steady_row": f"{row:08x}",
                "target_label": f"{next(iter({target for target, steady in zip(T, B, strict=True) if steady == row})):08x}",
            }
            for row, _index in sorted(selected_terminal_splits)
        ],
        "selected_pairs": [f"{pair:08x}" for pair in sorted(active_pairs)],
        "dual_pairs": [f"{pair:08x}" for pair in sorted(dual_pairs)],
        "pair_pin_seed_bits": {
            f"{pair:08x}": list(values)
            for pair, values in sorted(pair_pin_seed.items())
        },
        "pair_load_labels": {
            f"{pair:08x}": f"{label:08x}"
            for pair, label in sorted(pair_load_label.items())
        },
        "direct_rails": selected_direct_rails,
        "direct_not_rails": direct_not_keys,
        "mode_pairs": mappings,
    }


def solve_record(
    dual,
    init,
    record: dict[str, Any],
    solver_names: Sequence[str],
    rc2_options: dict[str, Any],
) -> dict[str, Any]:
    from pysat.examples.rc2 import RC2
    from pysat.solvers import Solver

    T, B, C = (matrix(record, key) for key in ("T", "B", "C"))
    encoding = build_encoding(dual, init, T, B, C)
    started = time.perf_counter()
    digest = hashlib.sha256()
    for clause in encoding.wcnf.hard:
        digest.update(" ".join(str(literal) for literal in clause).encode("ascii"))
        digest.update(b" 0\n")
    hard_solver_results = []
    first_hard_model = None
    with MemoryMonitor() as monitor:
        for solver_name in solver_names:
            solver_started = time.perf_counter()
            with Solver(
                name=solver_name, bootstrap_with=encoding.wcnf.hard
            ) as solver:
                satisfiable = solver.solve()
                hard_model = solver.get_model() if satisfiable else None
            hard_solver_results.append(
                {
                    "solver": solver_name,
                    "status": "sat" if satisfiable else "unsat",
                    "elapsed_seconds": round(
                        time.perf_counter() - solver_started, 6
                    ),
                }
            )
            if first_hard_model is None and hard_model is not None:
                first_hard_model = hard_model
        statuses = {result["status"] for result in hard_solver_results}
        if len(statuses) != 1:
            raise AssertionError(f"hard solver mismatch: {hard_solver_results}")
        if first_hard_model is None:
            model = None
            optimum = None
        else:
            with RC2(
                encoding.wcnf, solver=solver_names[0], **rc2_options
            ) as optimizer:
                model = optimizer.compute()
                optimum = optimizer.cost if model is not None else None
    elapsed = time.perf_counter() - started
    result: dict[str, Any] = {
        "variable_count_before_rc2": encoding.pool.top,
        "hard_clause_count": len(encoding.wcnf.hard),
        "soft_clause_count": len(encoding.wcnf.soft),
        "hard_cnf_sha256": digest.hexdigest(),
        "hard_solver_results": hard_solver_results,
        "elapsed_seconds": round(elapsed, 6),
        "peak_working_set_mb": round(monitor.peak / 1024 / 1024, 3),
        "optimum_logic_cost": optimum,
    }
    if model is None:
        result["status"] = "hard_unsat"
        targets = T
        steady = B
        witnesses = [
            {
                "occurrence": index,
                "plane": "feedback",
                "bit": index,
                "steady_row": f"{steady[index]:08x}",
                "target_label": f"{target:08x}",
                "target_weight": target.bit_count(),
            }
            for index, target in enumerate(targets)
            if target.bit_count() > 4
        ]
        result["analytic_certificate"] = {
            "maximum_realizable_label_weight": 4,
            "reason": (
                "a raw/mode pin has label weight <=1; a first-layer pair "
                "has weight <=2; an 8-delay final Switch XOR combines at "
                "most two such pair/direct rails"
            ),
            "maximum_required_label_weight": max(
                target.bit_count() for target in targets
            ),
            "witness_count": len(witnesses),
            "witnesses": witnesses,
        }
        return result
    result["status"] = "candidate" if optimum <= LOGIC_BUDGET else "over_budget"
    result["certificate"] = decode_and_verify(
        init, T, B, C, encoding, model, optimum
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source",
        type=Path,
        default=Path(".research/rng_or_frontier/or-hitting-target229-r7-x59.jsonl"),
    )
    parser.add_argument(
        "--bounds",
        type=Path,
        default=Path(".research/rng_or_frontier/or-hitting-target229-r7-x59.csv"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            ".research/rng8delay_reduce_agent/rank2-frontier-exact-67.json"
        ),
    )
    parser.add_argument("--first", type=int, default=1)
    parser.add_argument("--last", type=int)
    parser.add_argument("--solvers", nargs="+", default=("g4",))
    parser.add_argument("--max-heavy", type=int, default=44)
    parser.add_argument(
        "--ignore-bounds",
        action="store_true",
        help="audit every JSONL record and synthesize ordinal bound metadata",
    )
    parser.add_argument(
        "--exclude-lines",
        nargs="*",
        type=int,
        default=DEFAULT_EXCLUDED_LINES,
        help="original CSV line identifiers assigned to another auditor",
    )
    parser.add_argument("--stop-on-budget", action="store_true")
    parser.add_argument("--adapt", action="store_true")
    parser.add_argument("--exhaust", action="store_true")
    parser.add_argument("--minz", action="store_true")
    parser.add_argument("--trim", type=int, default=1)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    source = args.source if args.source.is_absolute() else root / args.source
    bounds_path = args.bounds if args.bounds.is_absolute() else root / args.bounds
    output = args.output if args.output.is_absolute() else root / args.output
    dual = load_module(
        "rng_65_nonminimal_dual",
        root
        / "examples/rng/research/archive/rng_cost387/search_basis_dualmode.py",
    )
    init = load_module(
        "rng_65_nonminimal_init",
        root
        / "examples/rng/research/archive/rng_init_reuse/verify_init_reuse.py",
    )
    records = [
        json.loads(line)
        for line in source.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    import csv

    if args.ignore_bounds:
        bounds = [
            {
                "line": str(index),
                "xor": str(record.get("lower", {}).get("greedy_xor", -1)),
                "or_lower_bound": str(record.get("lower", {}).get("mode_or_lower", -1)),
                "heavy_or_lower_bound": str(record.get("lower", {}).get("mode_or_lower", -1)),
                "target_or": str(LOGIC_BUDGET),
            }
            for index, record in enumerate(records, 1)
        ]
        excluded = frozenset()
    else:
        with bounds_path.open(encoding="utf-8-sig", newline="") as stream:
            bounds = list(csv.DictReader(stream))
        if len(records) != len(bounds):
            raise ValueError("candidate JSONL and bounds CSV counts differ")
        excluded = frozenset(args.exclude_lines)
    selected_records = [
        (dataset_index, int(bound["line"]), record, bound)
        for dataset_index, (record, bound) in enumerate(zip(records, bounds, strict=True), 1)
        if (args.ignore_bounds or int(bound["heavy_or_lower_bound"]) <= args.max_heavy)
        and int(bound["line"]) not in excluded
    ]
    if not args.ignore_bounds:
        selected_records.sort(
            key=lambda item: (
                int(item[3]["heavy_or_lower_bound"]),
                int(item[3]["or_lower_bound"]),
                item[1],
            )
        )
    last = len(selected_records) if args.last is None else min(args.last, len(selected_records))
    indexed = selected_records[args.first - 1 : last]
    started = time.perf_counter()
    results = []
    stopped = False
    rc2_options = {
        "adapt": args.adapt,
        "exhaust": args.exhaust,
        "minz": args.minz,
        "trim": args.trim,
    }
    for dataset_index, source_line, record, bound in indexed:
        result = solve_record(dual, init, record, args.solvers, rc2_options)
        result["source_line"] = source_line
        result["dataset_index"] = dataset_index
        result["bounds"] = {
            key: int(value) for key, value in bound.items()
        }
        result["provenance"] = {
            key: record[key]
            for key in ("center", "depth", "move1", "move2", "hash", "lower")
            if key in record
        }
        result["T"] = record["T"]
        result["B"] = record["B"]
        result["C"] = record["C"]
        results.append(result)
        print(
            f"line={source_line} status={result['status']} "
            f"logic={result['optimum_logic_cost']} "
            f"rss={result['peak_working_set_mb']}MB "
            f"seconds={result['elapsed_seconds']}",
            flush=True,
        )
        if args.stop_on_budget and result["status"] == "candidate":
            stopped = True
            break

    best = min(
        (
            (result["optimum_logic_cost"], result["source_line"])
            for result in results
            if result["optimum_logic_cost"] is not None
        ),
        default=None,
    )
    document = {
        "schema": 1,
        "status": (
            "candidate"
            if any(result["status"] == "candidate" for result in results)
            else "range_unsat"
        ),
        "scope": {
            "source": str(source),
            "bounds": str(bounds_path),
            "bounds_ignored": args.ignore_bounds,
            "first_selected_record": args.first,
            "last_selected_record": args.first + len(results) - 1,
            "candidate_count": len(results),
            "eligible_candidate_count": len(selected_records),
            "max_heavy_or_lower_bound": args.max_heavy,
            "excluded_original_lines": sorted(excluded),
            "stopped_on_budget": stopped,
            "load_tick_output": "unobserved",
            "load_tick_state": "T*seed",
            "phase_protocol": "tick0 idle, tick1 load, tick2..66 output",
            "terminal_split_enabled": ALLOW_TERMINAL_SPLIT,
            "shell": FIXED_SHELL,
            "logic_budget": LOGIC_BUDGET,
            "target": [TARGET_GATE, TARGET_DELAY, TARGET_CYCLES],
            "cost_formula": (
                "mode_or + 3*pair + dual_pair + direct_not + "
                "3*final_native_xor + 4*final_switch_xor + terminal_split"
            ),
            "topology": "all depth-two XOR2 covers, including non-minimal mediated weight-1/2 rows",
            "c_only_load_labels": "unconstrained and eligible for direct-rail reuse",
        },
        "solver": {"names": list(args.solvers), **rc2_options},
        "best": (
            None
            if best is None
            else {"logic_cost": best[0], "gate": FIXED_SHELL + best[0], "source_line": best[1]}
        ),
        "elapsed_seconds": round(time.perf_counter() - started, 6),
        "records": results,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in document.items() if key != "records"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
