"""Find a replayable shallow RNG circuit over real XOR2/XOR3/OR primitives.

This is an offline research solver.  It reads only a matrix-search JSONL file
and writes a certificate in this directory; it never imports save-writing code.

Each physical first-layer form is either XOR2 (3 gates / 2 delay) or the
reviewed XOR3 component (12 gates / 2 delay).  A feedback output may use one
additional XOR2.  Tick-zero seed labels are assigned to the actual input pins
of those forms (or to a direct state leaf), so every counted OR corresponds to
one concrete ``(seed bit, encoded-state bit)`` high-impedance mode pair.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import ctypes
from dataclasses import dataclass
import json
import os
from pathlib import Path
import random
import threading
import time
from typing import Iterable, Sequence

import z3


BITS = 32
MASK = (1 << BITS) - 1
FIXED_GATE_COST = 166
XOR2_COST = 3
XOR3_COST = 12


def xorshift32(value: int) -> int:
    value ^= value >> 13
    value &= MASK
    value ^= (value << 17) & MASK
    value &= MASK
    value ^= value >> 5
    return value & MASK


def matrix_from_function(function) -> tuple[int, ...]:
    columns = tuple(function(1 << source) for source in range(BITS))
    return tuple(
        sum(((columns[source] >> output) & 1) << source for source in range(BITS))
        for output in range(BITS)
    )


A = matrix_from_function(xorshift32)


def bits(mask: int) -> tuple[int, ...]:
    return tuple(bit for bit in range(BITS) if mask >> bit & 1)


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
    return sum(
        ((row & value).bit_count() & 1) << output
        for output, row in enumerate(matrix)
    )


@dataclass(frozen=True, order=True)
class Option:
    final_arity: int
    sources: tuple[int, ...]


def bipartitions(mask: int) -> tuple[tuple[int, int], ...]:
    """Return cancellation-free, unordered two-block partitions of mask."""

    support = bits(mask)
    anchor = support[0]
    rest = support[1:]
    result: set[tuple[int, int]] = set()
    for choice in range(1 << len(rest)):
        left = 1 << anchor
        for index, bit in enumerate(rest):
            if choice >> index & 1:
                left |= 1 << bit
        right = mask ^ left
        if right:
            result.add(tuple(sorted((left, right))))
    return tuple(sorted(result))


def output_options(mask: int, *, is_output: bool) -> tuple[Option, ...]:
    """Enumerate legal depth-one C or depth-two B implementations."""

    weight = mask.bit_count()
    if weight == 1:
        return (Option(0, (mask,)),)
    if is_output:
        if weight != 2:
            raise ValueError(f"C row {mask:08x} cannot fit one shallow XOR layer")
        return (Option(0, (mask,)),)

    result: set[Option] = set()
    if weight in (2, 3):
        result.add(Option(0, (mask,)))
    for left, right in bipartitions(mask):
        if left.bit_count() <= 3 and right.bit_count() <= 3:
            result.add(Option(2, (left, right)))
    return tuple(sorted(result))


def load_last_candidate(path: Path) -> tuple[tuple[int, ...], ...]:
    last = None
    with path.open("r", encoding="utf-8") as source:
        for line in source:
            if line.strip():
                last = json.loads(line)
    if last is None:
        raise ValueError(f"empty JSONL file: {path}")
    matrices = tuple(tuple(int(row, 16) for row in last[key]) for key in ("T", "B", "C"))
    if any(len(matrix) != BITS for matrix in matrices):
        raise ValueError("T, B and C must each have 32 rows")
    return matrices


def parity(expressions: Sequence[z3.BoolRef]) -> z3.BoolRef:
    if not expressions:
        return z3.BoolVal(False)
    if len(expressions) == 1:
        return expressions[0]
    return z3.Xor(*expressions)


def exactly_one(expressions: Sequence[z3.BoolRef]) -> z3.BoolRef:
    return z3.PbEq([(expression, 1) for expression in expressions], 1)


def working_set_bytes() -> int:
    if os.name != "nt":
        return 0
    from ctypes import wintypes

    class Counters(ctypes.Structure):
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

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.GetCurrentProcess.restype = wintypes.HANDLE
    query = kernel32.K32GetProcessMemoryInfo
    query.argtypes = [wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD]
    query.restype = wintypes.BOOL
    counters = Counters()
    counters.cb = ctypes.sizeof(counters)
    if not query(kernel32.GetCurrentProcess(), ctypes.byref(counters), counters.cb):
        return 0
    return int(counters.WorkingSetSize)


def start_watchdog(memory_mb: int) -> tuple[threading.Event, list[int]]:
    stopped = threading.Event()
    peak = [working_set_bytes()]

    def watch() -> None:
        limit = memory_mb * 1024 * 1024
        while not stopped.wait(0.25):
            current = working_set_bytes()
            peak[0] = max(peak[0], current)
            if current > limit:
                os.write(
                    2,
                    (
                        f"memory_limit_exceeded working_set_mb={current / 1048576:.1f} "
                        f"limit_mb={memory_mb}\n"
                    ).encode("ascii"),
                )
                os._exit(75)

    threading.Thread(target=watch, daemon=True).start()
    return stopped, peak


def build_option_model(
    solver: z3.Solver, B: Sequence[int], C: Sequence[int]
) -> tuple[
    tuple[tuple[Option, ...], ...],
    tuple[tuple[Option, ...], ...],
    dict[tuple[str, int, int], z3.BoolRef],
    tuple[int, ...],
    dict[int, z3.BoolRef],
]:
    b_options = tuple(output_options(row, is_output=False) for row in B)
    c_options = tuple(output_options(row, is_output=True) for row in C)
    choice = {
        (kind, output, index): z3.Bool(f"use_{kind}{output:02d}_{index:02d}")
        for kind, rows in (("b", b_options), ("c", c_options))
        for output, options in enumerate(rows)
        for index in range(len(options))
    }
    for kind, rows in (("b", b_options), ("c", c_options)):
        for output, options in enumerate(rows):
            solver.add(exactly_one([choice[kind, output, index] for index in range(len(options))]))

    forms = tuple(
        sorted(
            {
                source
                for rows in (b_options, c_options)
                for options in rows
                for option in options
                for source in option.sources
                if source.bit_count() in (2, 3)
            }
        )
    )
    selected = {form: z3.Bool(f"form_{form:08x}") for form in forms}
    form_users: dict[int, list[z3.BoolRef]] = defaultdict(list)
    for kind, rows in (("b", b_options), ("c", c_options)):
        for output, options in enumerate(rows):
            for index, option in enumerate(options):
                use = choice[kind, output, index]
                for source in option.sources:
                    if source.bit_count() in (2, 3):
                        solver.add(z3.Implies(use, selected[source]))
                        form_users[source].append(use)
    for form in forms:
        solver.add(selected[form] == z3.Or(*form_users[form]))
    return b_options, c_options, choice, forms, selected


def chosen_output_entries(
    model: z3.ModelRef,
    truth,
    B: Sequence[int],
    C: Sequence[int],
    b_options: Sequence[Sequence[Option]],
    c_options: Sequence[Sequence[Option]],
    choice: dict[tuple[str, int, int], z3.BoolRef],
) -> dict[str, list[dict[str, object]]]:
    result: dict[str, list[dict[str, object]]] = {"B": [], "C": []}
    for kind, key, matrix, rows in (
        ("b", "B", B, b_options),
        ("c", "C", C, c_options),
    ):
        for output, options in enumerate(rows):
            index = next(
                index
                for index in range(len(options))
                if truth(choice[kind, output, index])
            )
            option = options[index]
            result[key].append(
                {
                    "output": output,
                    "target": f"{matrix[output]:08x}",
                    "final_arity": option.final_arity,
                    "sources": [f"{source:08x}" for source in option.sources],
                }
            )
    return result


def solve_cover(
    T: Sequence[int],
    B: Sequence[int],
    C: Sequence[int],
    *,
    logic_bound: int,
    timeout_ms: int,
    memory_mb: int,
) -> dict[str, object]:
    started = time.perf_counter()
    stopped, peak = start_watchdog(memory_mb)
    solver = z3.Tactic("sat").solver()
    solver.set(timeout=timeout_ms, max_memory=memory_mb - 32)
    b_options, c_options, choice, forms, selected = build_option_model(solver, B, C)
    cost_terms = [
        (selected[form], XOR2_COST if form.bit_count() == 2 else XOR3_COST)
        for form in forms
    ]
    cost_terms.extend(
        (choice[kind, output, index], XOR2_COST)
        for kind, rows in (("b", b_options), ("c", c_options))
        for output, options in enumerate(rows)
        for index, option in enumerate(options)
        if option.final_arity == 2
    )
    solver.add(z3.PbLe(cost_terms, logic_bound))
    build_seconds = time.perf_counter() - started
    check = solver.check()
    solve_seconds = time.perf_counter() - started - build_seconds
    stopped.set()
    peak[0] = max(peak[0], working_set_bytes())
    report: dict[str, object] = {
        "status": str(check),
        "scope": "steady-state real XOR2/XOR3 shallow cover",
        "logic_bound": logic_bound,
        "timeout_ms": timeout_ms,
        "memory_limit_mb": memory_mb,
        "peak_working_set_mb": peak[0] / 1048576,
        "build_seconds": build_seconds,
        "solve_seconds": solve_seconds,
        "form_universe": len(forms),
        "choice_count": len(choice),
        "reason_unknown": solver.reason_unknown() if check == z3.unknown else None,
    }
    if check != z3.sat:
        return report

    model = solver.model()
    truth = lambda expression: z3.is_true(model.eval(expression, model_completion=True))
    selected_forms = tuple(form for form in forms if truth(selected[form]))
    outputs = chosen_output_entries(
        model, truth, B, C, b_options, c_options, choice
    )
    final_xor2 = sum(
        entry["final_arity"] == 2 for entries in outputs.values() for entry in entries
    )
    form_counts = Counter(form.bit_count() for form in selected_forms)
    xor2_count = form_counts[2] + final_xor2
    xor3_count = form_counts[3]
    logic_cost = XOR2_COST * xor2_count + XOR3_COST * xor3_count
    report["cover"] = {
        "T": [f"{row:08x}" for row in T],
        "B": [f"{row:08x}" for row in B],
        "C": [f"{row:08x}" for row in C],
        "selected_first_layer_forms": [f"{form:08x}" for form in selected_forms],
        "outputs": outputs,
        "metrics": {
            "first_xor2": form_counts[2],
            "first_xor3": form_counts[3],
            "final_xor2": final_xor2,
            "xor2": xor2_count,
            "xor3": xor3_count,
            "logic_gate_cost": logic_cost,
            "remaining_or_at_gate_430": 430 - FIXED_GATE_COST - logic_cost,
        },
    }
    return report


def constrain_fixed_cover(
    solver: z3.Solver,
    fixed_cover: dict[str, object],
    b_options: Sequence[Sequence[Option]],
    c_options: Sequence[Sequence[Option]],
    choice: dict[tuple[str, int, int], z3.BoolRef],
) -> None:
    for kind, key, rows in (("b", "B", b_options), ("c", "C", c_options)):
        entries = fixed_cover["outputs"][key]
        if len(entries) != BITS:
            raise ValueError(f"fixed cover {key} output count mismatch")
        for output, options in enumerate(rows):
            expected = Option(
                int(entries[output]["final_arity"]),
                tuple(int(source, 16) for source in entries[output]["sources"]),
            )
            if expected not in options:
                raise ValueError(f"fixed cover option absent for {key}[{output}]")
            for index, option in enumerate(options):
                solver.add(choice[kind, output, index] == (option == expected))


def solve(
    T: Sequence[int],
    B: Sequence[int],
    C: Sequence[int],
    *,
    gate_bound: int,
    timeout_ms: int,
    memory_mb: int,
    fixed_cover: dict[str, object] | None = None,
) -> dict[str, object]:
    started = time.perf_counter()
    stopped, peak = start_watchdog(memory_mb)
    solver = z3.Solver()
    solver.set(timeout=timeout_ms, max_memory=memory_mb - 32)

    # B rows have tick-zero labels T[row].  C rows are disabled at tick zero,
    # but their steady forms may be shared with B.
    b_options, c_options, choice, forms, selected = build_option_model(solver, B, C)
    if fixed_cover is not None:
        constrain_fixed_cover(solver, fixed_cover, b_options, c_options, choice)

    # A form input pin carries q[state] in steady mode and at most one seed
    # coordinate at tick zero.  Its linear seed label is the XOR of its pins.
    pin = {
        (form, state, seed): z3.Bool(f"pin_{form:08x}_q{state:02d}_s{seed:02d}")
        for form in forms
        for state in bits(form)
        for seed in range(BITS)
    }
    label = {
        (form, seed): z3.Bool(f"label_{form:08x}_s{seed:02d}")
        for form in forms
        for seed in range(BITS)
    }
    mode_users: dict[tuple[int, int], list[z3.BoolRef]] = defaultdict(list)
    for form in forms:
        for state in bits(form):
            pins = [pin[form, state, seed] for seed in range(BITS)]
            solver.add(z3.AtMost(*pins, 1))
            for seed, variable in enumerate(pins):
                solver.add(z3.Implies(variable, selected[form]))
                mode_users[seed, state].append(variable)
        for seed in range(BITS):
            solver.add(
                label[form, seed]
                == parity([pin[form, state, seed] for state in bits(form)])
            )

    # A unit source at a B output may independently use one shared mode-paired
    # leaf.  C labels do not matter because Architecture Output is disabled on
    # the seed-loading tick.
    raw = {}
    for output, options in enumerate(b_options):
        for index, option in enumerate(options):
            use = choice["b", output, index]
            for source_index, source in enumerate(option.sources):
                if source.bit_count() != 1:
                    continue
                state = bits(source)[0]
                variables = []
                for seed in range(BITS):
                    variable = z3.Bool(
                        f"raw_b{output:02d}_o{index:02d}_i{source_index}_s{seed:02d}"
                    )
                    raw[output, index, source_index, seed] = variable
                    solver.add(z3.Implies(variable, use))
                    mode_users[seed, state].append(variable)
                    variables.append(variable)
                solver.add(z3.AtMost(*variables, 1))

            for seed in range(BITS):
                source_labels = []
                for source_index, source in enumerate(option.sources):
                    if source.bit_count() == 1:
                        source_labels.append(raw[output, index, source_index, seed])
                    else:
                        source_labels.append(label[source, seed])
                expected = bool(T[output] >> seed & 1)
                equality = parity(source_labels) if expected else z3.Not(parity(source_labels))
                solver.add(z3.Implies(use, equality))

    mode = {
        (seed, state): z3.Bool(f"mode_s{seed:02d}_q{state:02d}")
        for seed in range(BITS)
        for state in range(BITS)
    }
    for key, variable in mode.items():
        users = mode_users.get(key, ())
        solver.add(variable == (z3.Or(*users) if users else z3.BoolVal(False)))
    for seed in range(BITS):
        solver.add(z3.Or(*(mode[seed, state] for state in range(BITS))))

    form_terms = [
        (selected[form], XOR2_COST if form.bit_count() == 2 else XOR3_COST)
        for form in forms
    ]
    final_terms = [
        (choice[kind, output, index], XOR2_COST)
        for kind, rows in (("b", b_options), ("c", c_options))
        for output, options in enumerate(rows)
        for index, option in enumerate(options)
        if option.final_arity == 2
    ]
    mode_terms = [(variable, 1) for variable in mode.values()]
    solver.add(
        z3.PbLe(form_terms + final_terms + mode_terms, gate_bound - FIXED_GATE_COST)
    )

    build_seconds = time.perf_counter() - started
    check = solver.check()
    solve_seconds = time.perf_counter() - started - build_seconds
    stopped.set()
    peak[0] = max(peak[0], working_set_bytes())
    report: dict[str, object] = {
        "status": str(check),
        "scope": "real XOR2/XOR3/OR depth-two network with physical tick-zero pin labels",
        "gate_bound": gate_bound,
        "timeout_ms": timeout_ms,
        "memory_limit_mb": memory_mb,
        "peak_working_set_mb": peak[0] / 1048576,
        "build_seconds": build_seconds,
        "solve_seconds": solve_seconds,
        "form_universe": len(forms),
        "choice_count": len(choice),
        "reason_unknown": solver.reason_unknown() if check == z3.unknown else None,
    }
    if check != z3.sat:
        return report

    model = solver.model()
    truth = lambda expression: z3.is_true(model.eval(expression, model_completion=True))
    selected_forms = tuple(form for form in forms if truth(selected[form]))
    chosen_options: dict[str, list[dict[str, object]]] = {"B": [], "C": []}
    raw_labels: dict[tuple[int, int, int], int | None] = {}
    for kind, rows in (("b", b_options), ("c", c_options)):
        for output, options in enumerate(rows):
            index = next(
                index
                for index in range(len(options))
                if truth(choice[kind, output, index])
            )
            option = options[index]
            entry: dict[str, object] = {
                "output": output,
                "target": f"{(B if kind == 'b' else C)[output]:08x}",
                "final_arity": option.final_arity,
                "sources": [f"{source:08x}" for source in option.sources],
            }
            if kind == "b":
                labels = []
                for source_index, source in enumerate(option.sources):
                    if source.bit_count() == 1:
                        assigned = next(
                            (
                                seed
                                for seed in range(BITS)
                                if truth(raw[output, index, source_index, seed])
                            ),
                            None,
                        )
                        raw_labels[output, index, source_index] = assigned
                        labels.append(0 if assigned is None else 1 << assigned)
                    else:
                        labels.append(
                            sum(
                                (1 << seed)
                                for seed in range(BITS)
                                if truth(label[source, seed])
                            )
                        )
                entry["tick_zero_source_labels"] = [f"{value:08x}" for value in labels]
            chosen_options["B" if kind == "b" else "C"].append(entry)

    form_pins = {
        f"{form:08x}": {
            str(state): next(
                (seed for seed in range(BITS) if truth(pin[form, state, seed])),
                None,
            )
            for state in bits(form)
        }
        for form in selected_forms
    }
    modes = tuple(key for key, variable in mode.items() if truth(variable))
    form_counts = Counter(form.bit_count() for form in selected_forms)
    final_xor2 = sum(
        entry["final_arity"] == 2
        for entries in chosen_options.values()
        for entry in entries
    )
    xor2_count = form_counts[2] + final_xor2
    xor3_count = form_counts[3]
    gate = FIXED_GATE_COST + XOR2_COST * xor2_count + XOR3_COST * xor3_count + len(modes)

    certificate = {
        "T": [f"{row:08x}" for row in T],
        "B": [f"{row:08x}" for row in B],
        "C": [f"{row:08x}" for row in C],
        "selected_first_layer_forms": [f"{form:08x}" for form in selected_forms],
        "form_pin_seed_bits": form_pins,
        "outputs": chosen_options,
        "mode_pairs": [
            {"seed": seed, "state": state} for seed, state in modes
        ],
        "metrics": {
            "xor2": xor2_count,
            "xor3": xor3_count,
            "or": len(modes),
            "fixed": FIXED_GATE_COST,
            "gate": gate,
            "delay": 9,
            "cycles": 66,
            "energy": gate * 9 * 66,
        },
    }
    report["candidate"] = certificate
    report["verification"] = verify_certificate(certificate)
    return report


def verify_certificate(certificate: dict[str, object]) -> dict[str, object]:
    T = tuple(int(row, 16) for row in certificate["T"])
    B = tuple(int(row, 16) for row in certificate["B"])
    C = tuple(int(row, 16) for row in certificate["C"])
    form_pins = {
        int(form, 16): {int(state): seed for state, seed in pins.items()}
        for form, pins in certificate["form_pin_seed_bits"].items()
    }
    modes = {
        (entry["seed"], entry["state"]) for entry in certificate["mode_pairs"]
    }

    if compose(C, T) != A:
        raise AssertionError("C*T != A")
    if compose(T, C) != B:
        raise AssertionError("T*C != B")

    used_modes: set[tuple[int, int]] = set()
    labels: dict[int, int] = {}
    for form, pins in form_pins.items():
        if tuple(sorted(pins)) != bits(form):
            raise AssertionError(f"form {form:08x} pin support mismatch")
        label_value = 0
        for state, seed in pins.items():
            if seed is not None:
                label_value ^= 1 << seed
                used_modes.add((seed, state))
        labels[form] = label_value

    for kind, matrix in (("B", B), ("C", C)):
        entries = certificate["outputs"][kind]
        if len(entries) != BITS:
            raise AssertionError(f"{kind} output count mismatch")
        for output, entry in enumerate(entries):
            target = int(entry["target"], 16)
            sources = tuple(int(source, 16) for source in entry["sources"])
            if entry["output"] != output or target != matrix[output]:
                raise AssertionError(f"{kind}[{output}] metadata mismatch")
            steady = 0
            for source in sources:
                steady ^= source
            if steady != target:
                raise AssertionError(f"{kind}[{output}] steady decomposition mismatch")
            expected_final = 0 if len(sources) == 1 else 2
            if entry["final_arity"] != expected_final:
                raise AssertionError(f"{kind}[{output}] final gate mismatch")
            if kind == "C":
                if any(source.bit_count() > 2 for source in sources) or len(sources) != 1:
                    raise AssertionError("C path exceeds one combination layer")
                continue

            source_labels = tuple(int(value, 16) for value in entry["tick_zero_source_labels"])
            if len(source_labels) != len(sources):
                raise AssertionError(f"B[{output}] tick-zero source count mismatch")
            tick_zero = 0
            for source, source_label in zip(sources, source_labels):
                if source.bit_count() == 1:
                    if source_label and source_label.bit_count() != 1:
                        raise AssertionError("raw state leaf carries multiple seed bits")
                    if source_label:
                        seed = bits(source_label)[0]
                        state = bits(source)[0]
                        used_modes.add((seed, state))
                elif labels.get(source) != source_label:
                    raise AssertionError("first-layer form label mismatch")
                tick_zero ^= source_label
            if tick_zero != T[output]:
                raise AssertionError(f"B[{output}] tick-zero label mismatch")

    if used_modes != modes:
        raise AssertionError("mode-pair set differs from physical pin users")

    seeds = [0, 1, 2, 0x12345678, MASK]
    seeds.extend(random.Random(0x5A3307).getrandbits(BITS) for _ in range(64))
    for seed in seeds:
        encoded = apply_matrix(T, seed)
        natural = seed
        for _ in range(65):
            natural = xorshift32(natural)
            if apply_matrix(C, encoded) != natural:
                raise AssertionError("visible output replay failed")
            encoded = apply_matrix(B, encoded)
    return {
        "matrix_identities": ["C*T=A", "T*C=B"],
        "verified_seed_count": len(seeds),
        "verified_outputs_per_seed": 65,
        "physical_mode_pair_count": len(modes),
        "server_recalculation_model": "gate list and tick-zero/steady labels, not score fields",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=Path, required=True)
    parser.add_argument("--cover-only", action="store_true")
    parser.add_argument("--logic-bound", type=int, default=232)
    parser.add_argument("--fixed-cover", type=Path)
    parser.add_argument("--gate-bound", type=int, default=430)
    parser.add_argument("--timeout-ms", type=int, default=300_000)
    parser.add_argument("--memory-mb", type=int, default=680)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    T, B, C = load_last_candidate(args.start)
    if args.cover_only:
        result = solve_cover(
            T,
            B,
            C,
            logic_bound=args.logic_bound,
            timeout_ms=args.timeout_ms,
            memory_mb=args.memory_mb,
        )
    else:
        fixed_cover = None
        if args.fixed_cover is not None:
            document = json.loads(args.fixed_cover.read_text(encoding="utf-8"))
            fixed_cover = document.get("cover", document.get("candidate", document))
        result = solve(
            T,
            B,
            C,
            gate_bound=args.gate_bound,
            timeout_ms=args.timeout_ms,
            memory_mb=args.memory_mb,
            fixed_cover=fixed_cover,
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {key: value for key, value in result.items() if key not in {"candidate", "cover"}},
            indent=2,
        )
    )
    return 0 if result["status"] in {"sat", "unsat"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
