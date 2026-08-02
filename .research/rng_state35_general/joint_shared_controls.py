"""Joint physical-cost audit for sparse 35-state RNG candidates.

The depth-two library is:

* scalar XOR2: 3 gates / 2 delay;
* scalar Switch-XOR3: four Bit Switches (8 gates) plus three NOR
  controls and one of three AND controls / 2 delay;
* identical first-level forms and identical control truth tables are shared.

The option generator is cancellation-complete for first-level linear forms of
weight two or three and a final XOR2 or Switch-XOR3.  A relaxed run gives all
Switch-XOR3 controls away for free and is therefore a strict lower bound.  A
physical run charges the exact global union of NOR/AND controls.

Research only: this module does not import save/game code and does not use RAM.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import asdict, dataclass
import ctypes
from functools import lru_cache
from hashlib import sha256
from itertools import combinations
import json
import os
from pathlib import Path
import sys
import threading
import time
from typing import Iterable, Sequence

from pysat.examples.rc2 import RC2
from pysat.formula import IDPool, WCNF


HERE = Path(__file__).resolve().parent
VISIBLE = 32
SHELL_GATE = 213
CORE_BUDGET = 430 - SHELL_GATE
PAIR_GATE = 3
SWITCH_XOR3_BASE_GATE = 8

sys.path.insert(0, str(HERE))
import audit_pair_cover as pair_audit  # noqa: E402


ControlKey = tuple[int, int, int, int]


@dataclass(frozen=True, slots=True)
class Option:
    kind: str
    required_forms: tuple[int, ...]
    sources: tuple[int, ...]

    @property
    def final_base_gate(self) -> int:
        return {"direct": 0, "xor2": PAIR_GATE, "switch_xor3": SWITCH_XOR3_BASE_GATE}[self.kind]


@dataclass(frozen=True, slots=True)
class Score:
    core_gate: int
    first_pair_gate: int
    first_switch_base_gate: int
    final_xor2_gate: int
    final_switch_base_gate: int
    nor_gate: int
    and_gate: int
    selected_forms: tuple[int, ...]
    switch_nodes: tuple[tuple[int, int, int], ...]
    nor_controls: tuple[ControlKey, ...]
    and_controls: tuple[ControlKey, ...]


def pair_control_key(left: int, right: int, *, and_gate: bool) -> ControlKey:
    if not left or not right or left == right:
        raise AssertionError("control inputs must be distinct nonzero forms")
    span = sorted((left, right, left ^ right))
    return (span[0], span[1], span[2], left ^ right if and_gate else 0)


@lru_cache(maxsize=200_000)
def xor3_controls(
    sources: tuple[int, int, int],
) -> tuple[tuple[ControlKey, ...], tuple[ControlKey, ...]]:
    if len(set(sources)) != 3 or any(not value for value in sources):
        raise AssertionError("Switch-XOR3 sources must be distinct and nonzero")
    nors = []
    ands = []
    for left_index, right_index in ((0, 1), (0, 2), (1, 2)):
        left, right = sources[left_index], sources[right_index]
        nors.append(pair_control_key(left, right, and_gate=False))
        ands.append(pair_control_key(left, right, and_gate=True))
    return tuple(nors), tuple(ands)


def verify_conflict_free_macro(sources: tuple[int, int, int]) -> None:
    """Verify the reviewed four-driver XOR3 truth table.

    More than one zero-valued driver is active at 000.  This is electrically
    conflict-free rather than literally one-hot: every active driver agrees
    with parity, and every parity-one case has a driver.
    """

    for and_pair in ((0, 1), (0, 2), (1, 2)):
        remaining = ({0, 1, 2} - set(and_pair)).pop()
        for case in range(8):
            values = tuple((case >> bit) & 1 for bit in range(3))
            parity = values[0] ^ values[1] ^ values[2]
            driven = []
            for left, right, data in ((0, 1, 2), (0, 2, 1), (1, 2, 0)):
                if not values[left] and not values[right]:
                    driven.append(values[data])
            if values[and_pair[0]] and values[and_pair[1]]:
                driven.append(values[remaining])
            if any(value != parity for value in driven):
                raise AssertionError("Switch-XOR3 has a conflicting driver")
            if parity and not driven:
                raise AssertionError("Switch-XOR3 does not drive a parity-one case")


@lru_cache(maxsize=8)
def first_forms(state_bits: int) -> tuple[tuple[int, ...], frozenset[int]]:
    units = tuple(1 << bit for bit in range(state_bits))
    pairs = tuple(left | right for left, right in combinations(units, 2))
    triples = tuple(a | b | c for a, b, c in combinations(units, 3))
    forms = frozenset((*pairs, *triples))
    return tuple(sorted((*units, *forms))), forms


@lru_cache(maxsize=512)
def switch_source_triples(target: int, state_bits: int) -> tuple[tuple[int, int, int], ...]:
    """Enumerate every distinct source triple of support at most three.

    Target coordinates have odd incidence (one or three sources), while
    cancellation coordinates outside the target have even incidence (two
    sources).  This pattern enumeration is complete and avoids an O(S^2)
    scan over all 7,175 possible sources.
    """

    target_bits = tuple(bit for bit in range(state_bits) if target >> bit & 1)
    outside_bits = tuple(bit for bit in range(state_bits) if not (target >> bit & 1))
    weight = len(target_bits)
    answer: set[tuple[int, int, int]] = set()
    max_repeats = (9 - weight) // 2

    def assign(
        tasks: Sequence[tuple[int, tuple[tuple[int, ...], ...]]],
        index: int,
        masks: tuple[int, int, int],
    ) -> None:
        if index == len(tasks):
            widths = tuple(value.bit_count() for value in masks)
            if any(width < 1 or width > 3 for width in widths):
                return
            ordered = tuple(sorted(masks))
            if len(set(ordered)) != 3:
                return
            if ordered[0] ^ ordered[1] ^ ordered[2] != target:
                raise AssertionError("source pattern does not reconstruct target")
            answer.add(ordered)  # type: ignore[arg-type]
            return
        bit, patterns = tasks[index]
        unit = 1 << bit
        for pattern in patterns:
            updated = list(masks)
            valid = True
            for lane in pattern:
                updated[lane] |= unit
                if updated[lane].bit_count() > 3:
                    valid = False
                    break
            if valid:
                assign(tasks, index + 1, tuple(updated))  # type: ignore[arg-type]

    singleton_patterns = ((0,), (1,), (2,))
    pair_patterns = ((0, 1), (0, 2), (1, 2))
    for repeats in range(max_repeats + 1):
        for triple_count in range(min(weight, repeats) + 1):
            outside_count = repeats - triple_count
            if outside_count > len(outside_bits):
                continue
            for triple_bits in combinations(target_bits, triple_count):
                triple_set = set(triple_bits)
                base = 0
                for bit in triple_bits:
                    base |= 1 << bit
                remaining = tuple(bit for bit in target_bits if bit not in triple_set)
                for external in combinations(outside_bits, outside_count):
                    tasks = tuple(
                        [(bit, singleton_patterns) for bit in remaining]
                        + [(bit, pair_patterns) for bit in external]
                    )
                    assign(tasks, 0, (base, base, base))
    return tuple(sorted(answer))


def enumerate_options(target: int, state_bits: int) -> tuple[Option, ...]:
    sources, forms = first_forms(state_bits)
    source_set = frozenset(sources)
    options: set[Option] = set()
    if target in forms:
        options.add(Option("direct", (target,), (target,)))

    for left in sources:
        right = target ^ left
        if left < right and right in source_set:
            used = tuple(sorted(value for value in (left, right) if value in forms))
            options.add(Option("xor2", used, (left, right)))

    # For support two or three, a direct/XOR2 realization costs at most six
    # control-free gates.  A final Switch-XOR3 costs eight before controls, so
    # it is strictly dominated even when every one of its controls is shared.
    if target.bit_count() >= 4:
        for triple in switch_source_triples(target, state_bits):
            used = tuple(value for value in triple if value in forms)
            options.add(Option("switch_xor3", used, triple))

    if not options:
        raise AssertionError(f"target {target:x} has no legal option")
    for option in options:
        value = 0
        for source in option.sources:
            value ^= source
        if value != target:
            raise AssertionError("option does not reconstruct target")
        if len(option.sources) != {"direct": 1, "xor2": 2, "switch_xor3": 3}[option.kind]:
            raise AssertionError("option arity mismatch")
    ordered = tuple(
        sorted(
            options,
            key=lambda item: (
                item.final_base_gate
                + sum(PAIR_GATE if value.bit_count() == 2 else SWITCH_XOR3_BASE_GATE for value in item.required_forms),
                item.kind,
                item.required_forms,
                item.sources,
            ),
        )
    )
    return reduce_options(target, ordered)


def reduce_options(target: int, options: tuple[Option, ...]) -> tuple[Option, ...]:
    """Apply sharing-safe physical dominance reductions.

    A weight-two target is always cheaper as its direct scalar XOR2.  A final
    Switch-XOR3 is dominated when a direct/XOR2 alternative needs at most its
    eight base gates and every newly introduced form is an XOR2 pair.  Such a
    replacement cannot introduce NOR/AND controls, so the reduction remains
    valid even under global control sharing.
    """

    if target.bit_count() == 2:
        direct = tuple(option for option in options if option.kind == "direct")
        if len(direct) != 1:
            raise AssertionError("weight-two target lost its direct XOR2")
        return direct

    alternatives = tuple(option for option in options if option.kind in ("direct", "xor2"))
    triggers = dominance_triggers(alternatives, allow_uncovered_triples=False)
    kept = []
    for option in options:
        if option.kind != "switch_xor3":
            kept.append(option)
            continue
        if not requirements_triggered(option.required_forms, triggers):
            kept.append(option)
    if not kept:
        raise AssertionError("dominance reduction removed every option")
    return tuple(kept)


def dominance_triggers(
    alternatives: Sequence[Option],
    *,
    allow_uncovered_triples: bool,
) -> frozenset[frozenset[int]]:
    """Compile replacement tests into minimal already-present requirements.

    A trigger ``Q`` means that an alternative costs no more than the eight-gate
    final Switch whenever every form in ``Q`` is already present.  Final XOR2
    alternatives have at most two required first-level forms, so enumerating
    all covered subsets is constant work per alternative.  This is equivalent
    to the former all-alternatives scan but avoids quadratic option reduction.
    """

    triggers: set[frozenset[int]] = set()
    for alternative in alternatives:
        required = alternative.required_forms
        for covered_count in range(len(required) + 1):
            for covered_tuple in combinations(required, covered_count):
                covered = frozenset(covered_tuple)
                uncovered = tuple(form for form in required if form not in covered)
                if not allow_uncovered_triples and any(form.bit_count() != 2 for form in uncovered):
                    continue
                added_gate = sum(
                    PAIR_GATE if form.bit_count() == 2 else SWITCH_XOR3_BASE_GATE
                    for form in uncovered
                )
                if alternative.final_base_gate + added_gate <= SWITCH_XOR3_BASE_GATE:
                    triggers.add(covered)
    return frozenset(
        trigger
        for trigger in triggers
        if not any(other < trigger for other in triggers)
    )


def requirements_triggered(
    present: Sequence[int],
    triggers: frozenset[frozenset[int]],
) -> bool:
    available = frozenset(present)
    return any(trigger <= available for trigger in triggers)


def relaxed_reduce_options(options: tuple[Option, ...]) -> tuple[Option, ...]:
    """Remove terms dominated when all XOR3 controls are free.

    In the relaxation, source triples with the same required first-form set
    have identical cost.  A strict superset requirement of the same final kind
    is redundant.  Cross-kind replacement may also add a weight-three first
    form at its relaxed eight-gate base because its controls are free here.
    """

    by_kind: dict[str, dict[tuple[int, ...], Option]] = {}
    for option in options:
        by_kind.setdefault(option.kind, {}).setdefault(option.required_forms, option)
    minimal = []
    for kind, records in by_kind.items():
        requirements = frozenset(records)
        for required, option in records.items():
            redundant = any(
                subset in requirements
                for size in range(len(required))
                for subset in combinations(required, size)
            )
            if not redundant:
                minimal.append(option)

    cheaper = tuple(option for option in minimal if option.kind in ("direct", "xor2"))
    triggers = dominance_triggers(cheaper, allow_uncovered_triples=True)
    kept = []
    for option in minimal:
        if option.kind != "switch_xor3":
            kept.append(option)
            continue
        if requirements_triggered(option.required_forms, triggers):
            continue
        kept.append(option)
    return tuple(
        sorted(
            kept,
            key=lambda option: (
                option.final_base_gate,
                option.kind,
                option.required_forms,
                option.sources,
            ),
        )
    )


def load_candidate(path: Path, hidden: int) -> tuple[tuple[int, ...], tuple[int, ...]]:
    return pair_audit.load_and_verify(path, hidden)


def minimum_and_cover(nodes: Iterable[tuple[int, int, int]]) -> tuple[ControlKey, ...]:
    clauses = tuple(dict.fromkeys(tuple(sorted(xor3_controls(node)[1])) for node in nodes))
    if not clauses:
        return ()
    keys = tuple(sorted({key for clause in clauses for key in clause}))
    pool = IDPool()
    variables = {key: pool.id(("and", key)) for key in keys}
    formula = WCNF()
    for clause in clauses:
        formula.append([variables[key] for key in clause])
    for variable in variables.values():
        formula.append([-variable], weight=1)
    with RC2(formula, solver="g4", adapt=True, exhaust=True, incr=False) as rc2:
        model = rc2.compute()
        optimum = rc2.cost
    if model is None:
        raise AssertionError("AND cover unexpectedly UNSAT")
    positive = {literal for literal in model if literal > 0}
    selected = tuple(key for key, variable in variables.items() if variable in positive)
    if len(selected) != optimum:
        raise AssertionError("AND cover cost mismatch")
    return tuple(sorted(selected))


def score_selection(selection: Sequence[Option], *, include_controls: bool) -> Score:
    forms = tuple(sorted({form for option in selection for form in option.required_forms}))
    switch_nodes = [
        tuple(1 << bit for bit in range(form.bit_length()) if form >> bit & 1)
        for form in forms
        if form.bit_count() == 3
    ]
    switch_nodes.extend(
        option.sources for option in selection if option.kind == "switch_xor3"
    )
    typed_nodes = tuple(tuple(node) for node in switch_nodes)
    for node in typed_nodes:
        verify_conflict_free_macro(node)  # type: ignore[arg-type]
    nor_controls = tuple(
        sorted({key for node in typed_nodes for key in xor3_controls(node)[0]})
    )
    and_controls = minimum_and_cover(typed_nodes) if include_controls else ()
    first_pair = PAIR_GATE * sum(form.bit_count() == 2 for form in forms)
    first_switch = SWITCH_XOR3_BASE_GATE * sum(form.bit_count() == 3 for form in forms)
    final_xor2 = PAIR_GATE * sum(option.kind == "xor2" for option in selection)
    final_switch = SWITCH_XOR3_BASE_GATE * sum(
        option.kind == "switch_xor3" for option in selection
    )
    nor_gate = len(nor_controls) if include_controls else 0
    and_gate = len(and_controls) if include_controls else 0
    return Score(
        first_pair + first_switch + final_xor2 + final_switch + nor_gate + and_gate,
        first_pair,
        first_switch,
        final_xor2,
        final_switch,
        nor_gate,
        and_gate,
        forms,
        typed_nodes,  # type: ignore[arg-type]
        nor_controls,
        and_controls,
    )


def load_pair_cover_seed(
    cover_path: Path,
    options_by_target: dict[int, tuple[Option, ...]],
) -> tuple[Option, ...]:
    data = json.loads(cover_path.read_text(encoding="utf-8"))
    selection = []
    for entry in data["targets"]:
        target = int(entry["row"], 16)
        weight = int(entry["weight"])
        pairs = tuple(int(value, 16) for value in entry["pairs"])
        if weight == 2:
            option = Option("direct", (target,), (target,))
        else:
            residual = target
            for pair in pairs:
                residual ^= pair
            raw = tuple(1 << bit for bit in range(residual.bit_length()) if residual >> bit & 1)
            kind = "switch_xor3" if weight >= 5 else "xor2"
            sources = tuple(sorted((*pairs, *raw)))
            option = Option(kind, tuple(sorted(pairs)), sources)
        if option not in options_by_target[target]:
            raise AssertionError(f"pair-cover seed option missing for {target:x}")
        selection.append(option)
    return tuple(selection)


def current_rss_bytes() -> int:
    if os.name != "nt":
        return 0

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
    psapi.GetProcessMemoryInfo.argtypes = [
        ctypes.c_void_p,
        ctypes.POINTER(Counters),
        ctypes.c_ulong,
    ]
    psapi.GetProcessMemoryInfo.restype = ctypes.c_int
    if not psapi.GetProcessMemoryInfo(
        kernel32.GetCurrentProcess(), ctypes.byref(counters), counters.cb
    ):
        return 0
    return int(counters.WorkingSetSize)


def key_json(key: ControlKey, width: int) -> dict[str, object]:
    digits = (width + 3) // 4
    return {
        "span": [f"{value:0{digits}x}" for value in key[:3]],
        "coset_zero_label": f"{key[3]:0{digits}x}",
        "kind": "NOR" if key[3] == 0 else "AND",
    }


def score_json(score: Score, width: int) -> dict[str, object]:
    digits = (width + 3) // 4
    value = asdict(score)
    value["selected_forms"] = [f"{form:0{digits}x}" for form in score.selected_forms]
    value["switch_nodes"] = [
        [f"{source:0{digits}x}" for source in node] for node in score.switch_nodes
    ]
    value["nor_controls"] = [key_json(key, width) for key in score.nor_controls]
    value["and_controls"] = [key_json(key, width) for key in score.and_controls]
    return value


def switch_truth_table(
    node: tuple[int, int, int],
    selected_and_controls: frozenset[ControlKey],
    width: int,
) -> dict[str, object]:
    pairs = ((0, 1, 2), (0, 2, 1), (1, 2, 0))
    matching = [
        (left, right, data, pair_control_key(node[left], node[right], and_gate=True))
        for left, right, data in pairs
        if pair_control_key(node[left], node[right], and_gate=True)
        in selected_and_controls
    ]
    if not matching:
        raise AssertionError("Switch-XOR3 node has no selected AND control")
    and_left, and_right, and_data, and_key = min(matching)
    rows = []
    for case in range(8):
        values = tuple((case >> bit) & 1 for bit in range(3))
        drivers = []
        active_values = []
        for left, right, data in pairs:
            enable = not values[left] and not values[right]
            driven = values[data] if enable else None
            if driven is not None:
                active_values.append(driven)
            drivers.append(
                {
                    "name": f"NOR(s{left},s{right})->s{data}",
                    "enable": enable,
                    "driven_value": driven,
                }
            )
        enable = bool(values[and_left] and values[and_right])
        driven = values[and_data] if enable else None
        if driven is not None:
            active_values.append(driven)
        drivers.append(
            {
                "name": f"AND(s{and_left},s{and_right})->s{and_data}",
                "enable": enable,
                "driven_value": driven,
            }
        )
        if len(set(active_values)) > 1:
            raise AssertionError("truth table contains opposing active drivers")
        parity = values[0] ^ values[1] ^ values[2]
        logical = active_values[0] if active_values else 0
        if logical != parity:
            raise AssertionError("Z-as-zero bus value does not equal parity")
        rows.append(
            {
                "inputs": list(values),
                "drivers": drivers,
                "active_driver_count": len(active_values),
                "active_values": active_values,
                "bus_state": "Z" if not active_values else str(active_values[0]),
                "logical_value_Z_as_zero": logical,
                "parity": parity,
                "conflict": False,
            }
        )
    digits = (width + 3) // 4
    return {
        "sources": [f"{source:0{digits}x}" for source in node],
        "selected_and_control": key_json(and_key, width),
        "truth_table": rows,
    }


def switch_truth_tables(score: Score, width: int) -> list[dict[str, object]]:
    selected = frozenset(score.and_controls)
    return [
        switch_truth_table(node, selected, width)
        for node in tuple(dict.fromkeys(score.switch_nodes))
    ]


def formula_digest(formula: WCNF) -> str:
    digest = sha256()
    for clause in formula.hard:
        digest.update(b"h ")
        digest.update(" ".join(map(str, clause)).encode("ascii"))
        digest.update(b" 0\n")
    for clause, weight in zip(formula.soft, formula.wght):
        digest.update(f"s {weight} ".encode("ascii"))
        digest.update(" ".join(map(str, clause)).encode("ascii"))
        digest.update(b" 0\n")
    return digest.hexdigest()


def solve(
    targets: tuple[int, ...],
    options: tuple[tuple[Option, ...], ...],
    *,
    physical: bool,
    solver_name: str,
    timeout_seconds: float,
    memory_mb: int,
) -> tuple[dict[str, object], tuple[Option, ...] | None, Score | None]:
    pool = IDPool()
    formula = WCNF()
    forms = tuple(
        sorted({form for choices in options for option in choices for form in option.required_forms})
    )
    form_var = {form: pool.id(("form", form)) for form in forms}
    option_vars: list[list[int]] = []
    option_records: list[tuple[int, int, Option, int]] = []
    control_var: dict[ControlKey, int] = {}

    def control(key: ControlKey) -> int:
        variable = control_var.get(key)
        if variable is None:
            variable = pool.id(("control", key))
            control_var[key] = variable
        return variable

    for form, variable in form_var.items():
        base = PAIR_GATE if form.bit_count() == 2 else SWITCH_XOR3_BASE_GATE
        formula.append([-variable], weight=base)
        if physical and form.bit_count() == 3:
            node = tuple(1 << bit for bit in range(form.bit_length()) if form >> bit & 1)
            nors, ands = xor3_controls(node)  # type: ignore[arg-type]
            for key in nors:
                formula.append([-variable, control(key)])
            formula.append([-variable, *(control(key) for key in ands)])

    for output, choices in enumerate(options):
        variables = []
        for option_index, option in enumerate(choices):
            variable = pool.id(("option", output, option_index))
            variables.append(variable)
            option_records.append((output, option_index, option, variable))
            for form in option.required_forms:
                formula.append([-variable, form_var[form]])
            if option.final_base_gate:
                formula.append([-variable], weight=option.final_base_gate)
            if physical and option.kind == "switch_xor3":
                nors, ands = xor3_controls(option.sources)  # type: ignore[arg-type]
                for key in nors:
                    formula.append([-variable, control(key)])
                formula.append([-variable, *(control(key) for key in ands)])
        formula.append(variables)
        option_vars.append(variables)

    if physical:
        for variable in control_var.values():
            formula.append([-variable], weight=1)

    digest = formula_digest(formula)
    peak = [current_rss_bytes()]
    interrupted = threading.Event()
    memory_interrupted = threading.Event()
    stop = threading.Event()
    model = None
    optimum = None
    started = time.perf_counter()
    with RC2(formula, solver=solver_name, adapt=True, exhaust=True, incr=False) as rc2:
        def interrupt(memory: bool) -> None:
            if memory:
                memory_interrupted.set()
            interrupted.set()
            try:
                rc2.oracle.interrupt()
            except Exception:
                pass

        def watch() -> None:
            deadline = time.monotonic() + timeout_seconds
            limit = memory_mb * 1048576
            while not stop.wait(0.10):
                current = current_rss_bytes()
                peak[0] = max(peak[0], current)
                if current > limit:
                    interrupt(True)
                    return
                if time.monotonic() >= deadline:
                    interrupt(False)
                    return

        watcher = threading.Thread(target=watch, daemon=True)
        watcher.start()
        try:
            model = rc2.compute()
            if model is not None and not interrupted.is_set():
                optimum = int(rc2.cost)
        finally:
            stop.set()
            watcher.join(timeout=1)
            peak[0] = max(peak[0], current_rss_bytes())
    elapsed = time.perf_counter() - started
    status = "OPTIMUM" if optimum is not None else "UNKNOWN" if interrupted.is_set() else "UNSAT"
    metadata: dict[str, object] = {
        "status": status,
        "mode": "physical-shared-controls" if physical else "free-controls-relaxation",
        "solver": solver_name,
        "optimum_core_gate": optimum,
        "core_budget": CORE_BUDGET,
        "within_430": optimum is not None and SHELL_GATE + optimum <= 430,
        "formula": {
            "variables": pool.top,
            "hard_clauses": len(formula.hard),
            "soft_clauses": len(formula.soft),
            "sha256": digest,
            "candidate_forms": len(forms),
            "candidate_options": sum(map(len, options)),
            "candidate_controls": len(control_var),
        },
        "limits": {
            "timeout_seconds": timeout_seconds,
            "memory_mb": memory_mb,
            "interrupted": interrupted.is_set(),
            "memory_interrupted": memory_interrupted.is_set(),
        },
        "runtime": {
            "seconds": elapsed,
            "peak_working_set_mb": peak[0] / 1048576,
        },
    }
    if model is None or optimum is None:
        return metadata, None, None

    positive = {literal for literal in model if literal > 0}
    selection = []
    for output, choices in enumerate(options):
        active = [
            option
            for option_index, option in enumerate(choices)
            if option_vars[output][option_index] in positive
        ]
        if not active:
            raise AssertionError(f"output {output} has no active option")
        selection.append(
            min(
                active,
                key=lambda option: (
                    option.final_base_gate,
                    option.kind,
                    option.required_forms,
                    option.sources,
                ),
            )
        )
    score = score_selection(selection, include_controls=physical)
    if score.core_gate != optimum:
        raise AssertionError(f"extracted score {score.core_gate} != RC2 optimum {optimum}")
    for target, option in zip(targets, selection):
        value = 0
        for source in option.sources:
            value ^= source
        if value != target:
            raise AssertionError("selected option replay failed")
    return metadata, tuple(selection), score


def option_json(target: int, option: Option, width: int) -> dict[str, object]:
    digits = (width + 3) // 4
    return {
        "target": f"{target:0{digits}x}",
        "target_weight": target.bit_count(),
        "kind": option.kind,
        "final_base_gate": option.final_base_gate,
        "required_first_forms": [f"{form:0{digits}x}" for form in option.required_forms],
        "sources": [f"{source:0{digits}x}" for source in option.sources],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--hidden", type=int, default=3)
    parser.add_argument("--cover-seed", type=Path)
    parser.add_argument("--mode", choices=("relaxed", "physical"), required=True)
    parser.add_argument("--solver", default="g4")
    parser.add_argument("--timeout-seconds", type=float, default=600.0)
    parser.add_argument("--memory-mb", type=int, default=680)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 64 <= args.memory_mb <= 700:
        parser.error("--memory-mb must be in [64,700]")
    if args.hidden < 1:
        parser.error("--hidden must be positive")

    started = time.perf_counter()
    h_rows, o_rows = load_candidate(args.candidate, args.hidden)
    targets = tuple(sorted({row for row in (*h_rows, *o_rows) if row.bit_count() >= 2}))
    state_bits = VISIBLE + args.hidden
    raw_options = tuple(enumerate_options(target, state_bits) for target in targets)
    options_by_target = dict(zip(targets, raw_options))
    options = (
        tuple(relaxed_reduce_options(value) for value in raw_options)
        if args.mode == "relaxed"
        else raw_options
    )
    option_seconds = time.perf_counter() - started
    print(
        f"built raw_options={sum(map(len, raw_options))} "
        f"solve_options={sum(map(len, options))} targets={len(targets)} "
        f"seconds={option_seconds:.3f}",
        flush=True,
    )

    seed_payload = None
    if args.cover_seed is not None:
        seed = load_pair_cover_seed(args.cover_seed, options_by_target)
        seed_score = score_selection(seed, include_controls=True)
        seed_payload = {
            "score": score_json(seed_score, state_bits),
            "total_gate": SHELL_GATE + seed_score.core_gate,
            "switch_truth_tables": switch_truth_tables(seed_score, state_bits),
            "selection": [
                option_json(target, option, state_bits)
                for target, option in zip(targets, seed)
            ],
        }
        print(
            f"pair-cover physical upper core={seed_score.core_gate} "
            f"total={SHELL_GATE + seed_score.core_gate}",
            flush=True,
        )

    metadata, selection, score = solve(
        targets,
        options,
        physical=args.mode == "physical",
        solver_name=args.solver,
        timeout_seconds=args.timeout_seconds,
        memory_mb=args.memory_mb,
    )
    payload: dict[str, object] = {
        "schema": 1,
        "source": str(args.candidate),
        "source_sha256": sha256(args.candidate.read_bytes()).hexdigest(),
        "model": "complete cancellation-aware depth-two XOR2/shared-control Switch-XOR3",
        "state_bits": state_bits,
        "target_count": len(targets),
        "target_weight_histogram": {
            str(weight): sum(target.bit_count() == weight for target in targets)
            for weight in sorted({target.bit_count() for target in targets})
        },
        "cost_contract": {
            "shell_gate": SHELL_GATE,
            "core_budget": CORE_BUDGET,
            "scalar_xor2": [3, 2],
            "u3_word_xor": [9, 2],
            "scalar_three_input_switch_xor3_unshared": [12, 2],
            "scalar_switch_xor3_switch_base": [8, 1],
            "NOR_AND_control": [1, 1],
            "ram": False,
        },
        "option_build_seconds": option_seconds,
        "raw_option_counts": [len(value) for value in raw_options],
        "solve_option_counts": [len(value) for value in options],
        "pair_cover_seed_upper": seed_payload,
        "solve": metadata,
    }
    if selection is not None and score is not None:
        payload["certificate"] = {
            "score": score_json(score, state_bits),
            "total_gate": SHELL_GATE + score.core_gate,
            "within_430": SHELL_GATE + score.core_gate <= 430,
            "switch_truth_tables": (
                switch_truth_tables(score, state_bits)
                if args.mode == "physical"
                else []
            ),
            "selection": [
                option_json(target, option, state_bits)
                for target, option in zip(targets, selection)
            ],
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    args.output.write_bytes(encoded)
    print(
        json.dumps(
            {
                "status": metadata["status"],
                "mode": metadata["mode"],
                "optimum_core_gate": metadata["optimum_core_gate"],
                "peak_working_set_mb": metadata["runtime"]["peak_working_set_mb"],
                "output_sha256": sha256(encoded).hexdigest(),
            },
            indent=2,
        ),
        flush=True,
    )
    return 0 if metadata["status"] == "OPTIMUM" else 30


if __name__ == "__main__":
    raise SystemExit(main())
