"""Global D5 remapping for the fast-negative high-output window.

The paid shell is the reviewed fast complemented-A/V prefix.  The canonical
seven-gate S1/S2 witness is replayed and all of its internal ordinary nodes are
made available to the high window at their *actual* arrival times.  The search
then jointly realizes S3..S7/C8 with ordinary gates, original Hub79 buses, and
strict conflict-free two-Switch buses.  One producer variable is shared by all
outputs, so cross-output reuse is physical gate reuse rather than six separate
formula searches.

Two accounting modes are supported:

* paid-nc7: the 66-gate non-output shell (including nC7@4) plus S1/S2=7;
  the high window must cost <=29 for a complete <=102/5 construction.
* integrated-nc7: remove the four-gate nC7 gray cell from the paid shell;
  the high window must jointly recreate whatever C7/nC7 phase it needs in <=33.

This is an offline truth-table/SAT search.  It neither starts the game nor
reads or writes a formal save.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import asdict
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GLOBAL_PATH = HERE / "search_hub79_global_function_map.py"
S12_WITNESS = (
    ROOT / ".research/byte_adder_phase_shortcut_restart/s12_g7_d5_exact.json"
)
S56_WITNESS = (
    ROOT
    / ".research/byte_adder_phase_shortcut_forward/fast_negative_jump_s56_g9_n9_s0_x0.json"
)
S4_WITNESS = (
    ROOT / ".research/byte_adder_phase_shortcut_restart/probe_s4_g9_n7_s2_x0_d5.json"
)
S34_WITNESS = (
    ROOT / ".research/byte_adder_phase_shortcut_restart/s34_g11_d5_joint_exact.json"
)
TAIL_S7C8_WITNESS = (
    ROOT
    / ".research/byte_adder_phase_shortcut_restart/tail_s7c8_g16_fixed_kinds_d5.json"
)
HUB33_LIBRARY_PATH = HERE / "hub33_high_function_library.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


gm = load_module("phase_high_global_core", GLOBAL_PATH)


def apply_gate(kind: str, left: int, right: int | None, all_mask: int) -> int:
    if kind == "NOT":
        return (~left) & all_mask
    if right is None:
        raise ValueError(f"{kind} requires a right input")
    if kind == "AND":
        return left & right
    if kind == "OR":
        return left | right
    if kind == "NAND":
        return (~(left & right)) & all_mask
    if kind == "NOR":
        return (~(left | right)) & all_mask
    if kind == "XOR":
        return left ^ right
    raise ValueError(kind)


def replay_witness(
    path: Path,
    named_truths: dict[str, int],
    named_arrivals: dict[str, int],
    all_mask: int,
) -> tuple[list[tuple[str, int, int]], tuple[int, ...]]:
    """Replay an exact physical witness into packed full-adder truth tables."""

    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("status") != "sat":
        raise RuntimeError(f"witness is not SAT: {path}")
    names = list(payload["free_sources"])
    truths: dict[int, int] = {}
    arrivals: dict[int, int] = {}
    for index, name in enumerate(names):
        if name == "0":
            truths[index] = 0
            arrivals[index] = 0
        elif name == "1":
            truths[index] = all_mask
            arrivals[index] = 0
        else:
            truths[index] = named_truths[name]
            arrivals[index] = named_arrivals[name]

    switch_specs: dict[int, tuple[int, int, int]] = {}
    derived: list[tuple[str, int, int]] = []

    def resolve_bus(source_ids: list[int]) -> tuple[int, int]:
        if len(source_ids) == 1 and source_ids[0] in truths:
            source = source_ids[0]
            return truths[source], arrivals[source]
        ones = 0
        zeros = 0
        arrival = 0
        if not source_ids:
            return 0, 0
        for source in source_ids:
            if source not in switch_specs:
                raise RuntimeError(f"unresolved physical bus {source_ids} in {path}")
            enable, data, driver_arrival = switch_specs[source]
            ones |= enable & data
            zeros |= enable & (~data & all_mask)
            arrival = max(arrival, driver_arrival)
        if ones & zeros:
            raise RuntimeError(f"conflicting witness bus {source_ids} in {path}")
        return ones, arrival

    for item in payload["network"]:
        source = int(item["source"])
        left, left_arrival = resolve_bus(list(item["left_bus"]))
        kind = str(item["kind"])
        if kind == "SWITCH":
            right, right_arrival = resolve_bus(list(item["right_bus"]))
            switch_specs[source] = (
                left,
                right,
                max(left_arrival, right_arrival) + 1,
            )
            continue
        right = None
        right_arrival = 0
        if kind != "NOT":
            right, right_arrival = resolve_bus(list(item["right_bus"]))
        truth = apply_gate(kind, left, right, all_mask)
        step = 2 if kind == "XOR" else 1
        arrival = max(left_arrival, right_arrival) + step
        truths[source] = truth
        arrivals[source] = arrival
        derived.append((f"{path.stem}:slot{item['slot']}:{kind}", truth, arrival))

    outputs = tuple(resolve_bus(list(bus))[0] for bus in payload["output_buses"])
    return derived, outputs


def build_phase_problem(engine, mode: str):
    all_mask = engine.ALL
    a = [engine.variable(index) for index in range(8)]
    b = [engine.variable(index + 8) for index in range(8)]
    cin = engine.variable(16)
    g = [a[index] & b[index] for index in range(8)]
    q = [(~(a[index] | b[index])) & all_mask for index in range(8)]
    p = [a[index] ^ b[index] for index in range(8)]
    n = [(~g[index]) & all_mask for index in range(8)]

    carry = cin
    nc = [(~cin) & all_mask]
    for index in range(8):
        carry = g[index] | (p[index] & carry)
        nc.append((~carry) & all_mask)

    a12 = q[1] | q[2]
    v12 = n[2] & (q[2] | n[1])
    a34 = q[3] | q[4]
    v34 = n[4] & (q[4] | n[3])
    a56 = q[5] | q[6]
    v56 = n[6] & (q[6] | n[5])
    a36 = a34 | a56
    v36 = v56 & (a56 | v34)

    named: dict[str, int] = {"0": 0, "1": all_mask, "Cin": cin}
    arrivals: dict[str, int] = {"0": 0, "1": 0, "Cin": 0}
    for index in range(8):
        named[f"a{index}"] = a[index]
        named[f"b{index}"] = b[index]
        arrivals[f"a{index}"] = 0
        arrivals[f"b{index}"] = 0
        for prefix, rows, arrival in (
            ("G", g, 1),
            ("Q", q, 1),
            ("P", p, 2),
            ("N", n, 1),
        ):
            named[f"{prefix}{index}"] = rows[index]
            arrivals[f"{prefix}{index}"] = arrival
        named[f"nC{index}"] = nc[index]
        named[f"C{index}"] = (~nc[index]) & all_mask
    named["nC8"] = nc[8]
    named["C8"] = (~nc[8]) & all_mask

    for name, truth, arrival in (
        ("A12n", a12, 2),
        ("V12n", v12, 2),
        ("A34n", a34, 2),
        ("V34n", v34, 2),
        ("A56n", a56, 2),
        ("V56n", v56, 2),
        ("A36n", a36, 3),
        ("V36n", v36, 3),
        ("nC1", nc[1], 2),
        ("nC3", nc[3], 3),
        ("nC7", nc[7], 4),
    ):
        named[name] = truth
        arrivals[name] = arrival

    outputs = [(f"S{index}", p[index] ^ ((~nc[index]) & all_mask)) for index in range(3, 8)]
    outputs.append(("C8", (~nc[8]) & all_mask))
    for name, truth in outputs:
        named[name] = truth

    # Curated phase helpers and both carry polarities enlarge Hub79's 164
    # functions without attempting an intractable unrestricted closure.
    for index in range(1, 8):
        named[f"U{index}"] = p[index] & nc[index]
        named[f"Z{index}"] = (~(p[index] | nc[index])) & all_mask
        named[f"R{index}"] = p[index] | nc[index]
        named[f"T{index}"] = (~(p[index] & nc[index])) & all_mask

    paid_sources: dict[int, int] = {0: 0, all_mask: 0, cin: 0}
    source_labels: dict[int, list[str]] = {0: ["ZERO"], all_mask: ["ONE"], cin: ["Cin"]}

    def pay(name: str, arrival: int | None = None) -> None:
        truth = named[name]
        value = arrivals[name] if arrival is None else arrival
        paid_sources[truth] = min(paid_sources.get(truth, value), value)
        source_labels.setdefault(truth, []).append(name)

    # Physical inputs are always free.  The fixed shell has paid all local
    # leaves used by S1..S7, the complemented A/V prefix, nC3, and optionally
    # nC7.  N7 is deliberately not paid by the reviewed 27-gate leaf shell.
    for index in range(8):
        pay(f"a{index}", 0)
        pay(f"b{index}", 0)
    for index in range(1, 7):
        for prefix in ("G", "Q", "P", "N"):
            pay(f"{prefix}{index}")
    for prefix in ("G", "Q", "P"):
        pay(f"{prefix}7")
    for name in ("nC1", "A12n", "V12n", "nC3", "A34n", "V34n", "A56n", "V56n", "A36n", "V36n"):
        pay(name)
    if mode == "paid-nc7":
        pay("nC7")

    # Replay the canonical seven-gate D5 S1/S2 solution.  Every internal node
    # is already paid and may be shared by the high window at its real arrival.
    s12_nodes, s12_outputs = replay_witness(S12_WITNESS, named, arrivals, all_mask)
    expected_s12 = (
        p[1] ^ ((~nc[1]) & all_mask),
        p[2] ^ ((~nc[2]) & all_mask),
    )
    if s12_outputs != expected_s12:
        raise RuntimeError("canonical S1/S2 witness does not match full truth table")
    for label, truth, arrival in s12_nodes:
        named[label] = truth
        arrivals[label] = arrival
        paid_sources[truth] = min(paid_sources.get(truth, arrival), arrival)
        source_labels.setdefault(truth, []).append(label)
    for label, truth, arrival in zip(("S1", "S2"), s12_outputs, (4, 5), strict=True):
        named[label] = truth
        arrivals[label] = arrival
        paid_sources[truth] = min(paid_sources.get(truth, arrival), arrival)
        source_labels.setdefault(truth, []).append(label)

    # Add the reviewed nine-gate S5/S6 witness's intermediate functions to the
    # candidate universe (not to paid_sources).  This preserves a known useful
    # decomposition while allowing the global selector to remap/share it.
    if S56_WITNESS.is_file():
        s56_nodes, s56_outputs = replay_witness(S56_WITNESS, named, arrivals, all_mask)
        expected_s56 = (dict(outputs)["S5"], dict(outputs)["S6"])
        if s56_outputs != expected_s56:
            raise RuntimeError("reviewed S5/S6 witness does not match full truth table")
        for label, truth, arrival in s56_nodes:
            named[label] = truth
            arrivals[label] = arrival

    # The exact D5 S4 witness contributes five ordinary control functions plus
    # one strict two-driver BUS.  They are candidate functions, not paid gates;
    # making the controls explicit lets the global selector share its
    # NAND(nC3,P3) node with the two extra gates of S3.
    if S4_WITNESS.is_file():
        s4_nodes, s4_outputs = replay_witness(S4_WITNESS, named, arrivals, all_mask)
        if s4_outputs != (dict(outputs)["S4"],):
            raise RuntimeError("reviewed S4 witness does not match full truth table")
        for label, truth, arrival in s4_nodes:
            named[label] = truth
            arrivals[label] = arrival

    # The frozen joint S3/S4 certificate exposes the exact shared seven-gate
    # ordinary control cone.  The nodes remain unpaid candidates; this merely
    # gives the global selector the real cross-output sharing vocabulary.
    if S34_WITNESS.is_file():
        s34_nodes, s34_outputs = replay_witness(
            S34_WITNESS, named, arrivals, all_mask
        )
        expected_s34 = (dict(outputs)["S3"], dict(outputs)["S4"])
        if s34_outputs != expected_s34:
            raise RuntimeError("reviewed S3/S4 witness does not match full truth table")
        for label, truth, arrival in s34_nodes:
            named[label] = truth
            arrivals[label] = arrival

    # The current best S7/C8 tail uses four ordinary controls and two
    # three-driver BUSes.  Only its ordinary controls enter the function
    # universe; the six physical Switches are not silently pre-paid.
    if TAIL_S7C8_WITNESS.is_file():
        tail_nodes, tail_outputs = replay_witness(
            TAIL_S7C8_WITNESS, named, arrivals, all_mask
        )
        expected_tail = (dict(outputs)["S7"], dict(outputs)["C8"])
        if tail_outputs != expected_tail:
            raise RuntimeError("reviewed S7/C8 witness does not match full truth table")
        for label, truth, arrival in tail_nodes:
            named[label] = truth
            arrivals[label] = arrival

    fixed_gate = 73 if mode == "paid-nc7" else 69
    return named, paid_sources, source_labels, outputs, fixed_gate


def add_source1_residual_expansion(
    base_universe: set[int],
    sources: dict[int, int],
    by_target: dict[int, dict[tuple[object, ...], object]],
    all_mask: int,
) -> tuple[set[int], dict[str, int]]:
    """Add exact one-gate source functions and two-level residual decompositions.

    This is a controlled non-curated expansion.  Every new function has a
    concrete one-gate producer over paid sources.  For each original goal/library
    function ``t``, algebraic residuals find every AND/OR/NAND/NOR decomposition
    ``t=op(a,b)`` with ``a,b`` in that one-gate closure, without an O(N^2)
    pair scan.  New nodes may be shared by all six outputs.
    """

    source_rows = sorted(sources)
    source1 = set(source_rows)
    source_recipe_count = 0
    for left_index, left in enumerate(source_rows):
        target = (~left) & all_mask
        source1.add(target)
        before = len(by_target.get(target, {}))
        gm.add_recipe(by_target, gm.Recipe(target, "NOT", (left,), 1, 1))
        source_recipe_count += len(by_target.get(target, {})) > before
        for right in source_rows[left_index:]:
            deps = (left, right)
            for op, target in (
                ("AND", left & right),
                ("OR", left | right),
                ("NAND", (~(left & right)) & all_mask),
                ("NOR", (~(left | right)) & all_mask),
            ):
                source1.add(target)
                before = len(by_target.get(target, {}))
                gm.add_recipe(by_target, gm.Recipe(target, op, deps, 1, 1))
                source_recipe_count += len(by_target.get(target, {})) > before

    residual_recipe_count = 0
    for target in base_universe:
        neg_target = (~target) & all_mask
        for left in source1:
            neg_left = (~left) & all_mask
            candidates: list[tuple[str, int]] = []
            if not (target & neg_left):
                candidates.append(("AND", target | neg_left))
            if not (left & neg_target):
                candidates.append(("OR", target & neg_left))
            if not (neg_target & neg_left):
                candidates.append(("NAND", neg_target | neg_left))
            if not (left & target):
                candidates.append(("NOR", neg_target & neg_left))
            for op, right in candidates:
                if right not in source1:
                    continue
                deps = tuple(sorted((left, right)))
                before = len(by_target.get(target, {}))
                gm.add_recipe(by_target, gm.Recipe(target, op, deps, 1, 1))
                residual_recipe_count += len(by_target.get(target, {})) > before
    return source1, {
        "source1_function_count": len(source1),
        "new_source1_function_count": len(source1 - base_universe),
        "source1_producer_recipe_count": source_recipe_count,
        "source1_residual_recipe_count": residual_recipe_count,
    }


def select_mixed_bus_targets(
    named: dict[str, int],
    outputs: list[tuple[str, int]],
    profile: str,
) -> tuple[list[int], list[str]]:
    """Select a labeled target slice for the controlled mixed-BUS expansion."""

    if profile == "none":
        return [], []

    selected_names = {name for name, _truth in outputs}
    selected_names.update(
        name
        for bit in range(5, 9)
        for name in (f"C{bit}", f"nC{bit}")
        if name in named
    )
    witness_stems = tuple(
        path.stem
        for path in (S56_WITNESS, S4_WITNESS, S34_WITNESS, TAIL_S7C8_WITNESS)
        if path.is_file()
    )
    selected_names.update(
        name for name in named if name.startswith(witness_stems)
    )

    if profile == "hub33-network-functions":
        # Resolved networks already span every distinct function exported by
        # the Hub33 slice.  Keep the semantic Switch aliases in the profile so
        # the evidence names the actual enable/data controls as well; truth
        # deduplication below prevents aliases from enlarging the SAT target set.
        selected_names.update(
            name
            for name in named
            if name.startswith("hub33:")
            and (":net" in name or ":switch" in name)
        )
    elif profile == "phase-hub33-controls":
        selected_names.update(
            f"{prefix}{bit}"
            for bit in range(3, 8)
            for prefix in ("U", "Z", "R", "T")
            if f"{prefix}{bit}" in named
        )
        selected_names.update(
            name
            for name in named
            if name.startswith("hub33:")
            and (":switch" in name)
        )
    elif profile != "witness-controls":
        raise ValueError(f"unknown mixed BUS target profile: {profile}")

    target_truths = sorted({named[name] for name in selected_names})
    return target_truths, sorted(selected_names)


def seqcounter_atmost_shape(literal_count: int, bound: int) -> tuple[int, int]:
    """Return PySAT ``EncType.seqcounter`` auxiliary-variable/clause counts."""

    if literal_count < 0 or bound < 0:
        raise ValueError("literal count and bound must be non-negative")
    if bound >= literal_count:
        return 0, 0
    if bound == 0:
        return 0, literal_count
    if bound == literal_count - 1:
        return 0, 1
    auxiliary = bound * (literal_count - bound)
    clauses = (
        (2 * bound + 1) * literal_count
        - 2 * bound * (bound + 1)
    )
    return auxiliary, clauses


def estimate_producer_tiered_cnf_shape(
    recipes,
    active: list[int],
    producers: dict[int, list[int]],
    earliest: dict[int, int],
    sources: dict[int, int],
    outputs: list[tuple[str, int]],
    *,
    delay_bound: int,
    gate_bound: int,
) -> dict[str, int | bool]:
    """Reproduce PySAT's exact variable allocation without retaining the full CNF."""

    arrival_counts = {
        truth: delay_bound - max(1, earliest[truth]) + 1 for truth in producers
    }

    variable_count = len(active) + sum(arrival_counts.values())
    explicit_base_variables = variable_count
    clauses = 0
    for truth, recipe_rows in producers.items():
        for literal_count in (len(recipe_rows), arrival_counts[truth]):
            if literal_count > 1:
                auxiliary, encoded_clauses = seqcounter_atmost_shape(
                    literal_count, 1
                )
                variable_count += auxiliary
                clauses += encoded_clauses
        clauses += len(recipe_rows) + arrival_counts[truth]
    producer_cardinality_auxiliary_variables = (
        variable_count - explicit_base_variables
    )

    dependency_clauses = 0
    for index in active:
        recipe = recipes[index]
        for target_depth in range(
            max(1, earliest[recipe.target]), delay_bound + 1
        ):
            deadline = target_depth - recipe.step_delay
            for dep in recipe.deps:
                if dep in sources and sources[dep] <= deadline:
                    continue
                dependency_clauses += 1
    clauses += dependency_clauses + len(outputs)

    cost_literal_count = 0
    cost_group_variables = 0
    cost_link_clauses = 0
    for truth, recipe_rows in producers.items():
        arrival_count = arrival_counts[truth]
        variable_count += 1
        cost_literal_count += 1
        cost_group_variables += 1
        cost_link_clauses += arrival_count + 1
        maximum_cost = max(recipes[index].cost for index in recipe_rows)
        for tier in range(2, maximum_cost + 1):
            eligible_count = sum(
                1
                for index in recipe_rows
                if recipes[index].cost >= tier
            )
            if not eligible_count:
                continue
            variable_count += 1
            cost_literal_count += 1
            cost_group_variables += 1
            cost_link_clauses += eligible_count + 1
    clauses += cost_link_clauses
    before_cost_cardinality = variable_count
    cost_auxiliary, cost_cardinality_clauses = seqcounter_atmost_shape(
        cost_literal_count, gate_bound
    )
    variable_count += cost_auxiliary
    cost_cardinality_auxiliary_variables = (
        variable_count - before_cost_cardinality
    )
    clauses += cost_cardinality_clauses
    auxiliary_variables = (
        producer_cardinality_auxiliary_variables
        + cost_cardinality_auxiliary_variables
    )
    return {
        "exact_for_producer_tiered_seqcounter": True,
        "seqcounter_shape_method": "closed-form-pysat-equivalent",
        "active_recipe_variables": len(active),
        "arrival_variables": sum(arrival_counts.values()),
        "auxiliary_variables": auxiliary_variables,
        "producer_cardinality_auxiliary_variables": (
            producer_cardinality_auxiliary_variables
        ),
        "cost_cardinality_auxiliary_variables": (
            cost_cardinality_auxiliary_variables
        ),
        "cost_group_variables": cost_group_variables,
        "cost_literal_count": cost_literal_count,
        "dependency_clause_count": dependency_clauses,
        "cost_link_clause_count": cost_link_clauses,
        "cnf_variables": variable_count,
        "cnf_clauses": clauses,
    }


def solve(args: argparse.Namespace) -> dict[str, object]:
    def emit_progress(event: str, **fields: object) -> None:
        if not args.progress:
            return
        print(
            json.dumps(
                {"event": event, "monotonic_seconds": time.monotonic(), **fields},
                ensure_ascii=False,
                sort_keys=True,
            ),
            file=sys.stderr,
            flush=True,
        )

    mixed_driver_profiles = tuple(
        dict.fromkeys(
            args.mixed_bus2_driver_profile
            or ("source1-enable-base-data",)
        )
    )
    if (
        "source1-enable-source1-data" in mixed_driver_profiles
        and "source1-enable-base-data" not in mixed_driver_profiles
    ):
        raise ValueError(
            "source1-enable-source1-data is an incremental driver class and "
            "requires source1-enable-base-data"
        )
    emit_progress(
        "solve_start",
        mode=args.mode,
        target_profile=args.mixed_bus2_target_profile,
        driver_profiles=list(mixed_driver_profiles),
    )

    engine = gm.load_engine()
    circuit, compiled, networks, _component_outputs = engine.evaluate()
    named, sources, source_labels, outputs, fixed_gate = build_phase_problem(
        engine, args.mode
    )
    hub33_meta: dict[str, object] | None = None
    if not args.without_hub33_functions:
        hub33_library = load_module("phase_high_hub33_library", HUB33_LIBRARY_PATH)
        hub33_functions, hub33_meta = hub33_library.extract(engine, named)
        named.update(hub33_functions)

    initial = {0, engine.ALL, *named.values()}
    for signal in networks.values():
        initial.update(signal.bits)
    base_universe_set = initial | {((~truth) & engine.ALL) for truth in initial}
    by_target = gm.ordinary_recipes(sorted(base_universe_set), engine.ALL)
    expansion_stats = {
        "source1_function_count": 0,
        "new_source1_function_count": 0,
        "source1_producer_recipe_count": 0,
        "source1_residual_recipe_count": 0,
    }
    source1: set[int] = set()
    universe_set = set(base_universe_set)
    if args.universe_expansion == "source1-residual":
        source1, expansion_stats = add_source1_residual_expansion(
            base_universe_set, sources, by_target, engine.ALL
        )
        universe_set.update(source1)
    universe = sorted(universe_set)
    original_buses = gm.original_bus_recipes(engine, circuit, compiled, networks)
    for recipe in original_buses:
        gm.add_recipe(by_target, recipe)

    bus2_stats: dict[str, object] = {
        "targets_with_bus2": 0,
        "raw_dependency_sets": 0,
        "retained_bus2_recipes": 0,
        "bus2_coverage_count": 0,
        "max_driver_forms_in_any_coverage": 0,
        "truncated_bus2_coverage_count": 0,
        "bus2_enumeration_complete": True,
    }
    mixed_bus2_stats: dict[str, object] = {
        "mixed_bus2_scope": "disabled",
        "mixed_bus2_target_profile": args.mixed_bus2_target_profile,
        "mixed_bus2_driver_profiles": list(mixed_driver_profiles),
        "mixed_bus2_target_count": 0,
        "mixed_bus2_target_labels": [],
        "mixed_bus2_retained_recipes": 0,
        "mixed_bus2_enumeration_complete": True,
        "mixed_source1_data_bus2_scope": "disabled",
        "mixed_source1_data_bus2_retained_recipes": 0,
        "mixed_source1_data_bus2_enumeration_complete": True,
        "mixed_bus2_combined_retained_recipes": 0,
        "mixed_bus2_combined_enumeration_complete": True,
    }
    bus2 = []
    if not args.without_new_bus2:
        bus_universe = (
            universe
            if args.bus_driver_universe == "expanded"
            else sorted(base_universe_set)
        )
        bus2, bus2_stats = gm.new_two_switch_recipes(
            bus_universe, max_per_coverage=args.max_per_coverage
        )
        for recipe in bus2:
            gm.add_recipe(by_target, recipe)
    emit_progress(
        "base_bus_enumerated",
        base_universe_functions=len(base_universe_set),
        retained_bus2_recipes=len(bus2),
        bus2_enumeration_complete=bus2_stats["bus2_enumeration_complete"],
    )

    if args.mixed_bus2_target_profile != "none":
        if args.universe_expansion != "source1-residual":
            raise ValueError(
                "mixed BUS2 requires --universe-expansion source1-residual"
            )
        if args.mixed_bus2_target_profile == "all-base-bus-targets":
            if args.without_new_bus2 or args.bus_driver_universe != "base":
                raise ValueError(
                    "all-base-bus-targets requires complete base BUS2 enumeration"
                )
            mixed_targets = sorted({recipe.target for recipe in bus2})
            mixed_target_labels = [
                f"<all {len(mixed_targets)} targets with a retained base BUS2 recipe>"
            ]
        else:
            mixed_targets, mixed_target_labels = select_mixed_bus_targets(
                named, outputs, args.mixed_bus2_target_profile
            )
        # In this declared model, new source1 functions have ordinary paid-source
        # producers but are not themselves BUS targets.  A function that cannot
        # arrive by D-1 without the new mixed BUS therefore cannot drive a D
        # mixed BUS, so this pre-BUS reachability filter is exact for the scope.
        pre_bus_recipes = [
            recipe
            for target in universe
            for recipe in by_target.get(target, {}).values()
            if recipe.op
            not in {"BUS2_MIXED_ENABLE", "BUS2_MIXED_SOURCE1_DATA"}
        ]
        _pre_active, pre_bus_earliest = gm.reachable_recipes(
            pre_bus_recipes, sources, args.delay - 1
        )
        expanded_functions = [
            truth
            for truth in source1 - base_universe_set
            if pre_bus_earliest.get(truth, args.delay + 1) <= args.delay - 1
        ]
        emit_progress(
            "mixed_pre_bus_reachability",
            target_count=len(mixed_targets),
            expanded_function_count=len(expanded_functions),
        )

        mixed_bus2: list[object] = []
        enumerated_mixed_stats: dict[str, object] = {
            "mixed_bus2_scope": "disabled",
            "mixed_bus2_target_count": len(mixed_targets),
            "mixed_bus2_retained_recipes": 0,
            "mixed_bus2_enumeration_complete": True,
        }
        if "source1-enable-base-data" in mixed_driver_profiles:
            mixed_bus2, enumerated_mixed_stats = (
                gm.new_targeted_mixed_two_switch_recipes(
                    sorted(base_universe_set),
                    expanded_functions,
                    mixed_targets,
                    max_per_coverage=args.max_per_coverage,
                    all_mask=engine.ALL,
                    probe_row_count=args.mixed_bus2_probe_rows,
                    exact_verification_threshold=(
                        args.mixed_bus2_exact_threshold
                    ),
                    progress_callback=(
                        lambda row: emit_progress("mixed_target", **row)
                    ),
                )
            )

        source1_data_bus2: list[object] = []
        enumerated_source1_data_stats: dict[str, object] = {
            "mixed_source1_data_bus2_scope": "disabled",
            "mixed_source1_data_bus2_target_count": len(mixed_targets),
            "mixed_source1_data_bus2_retained_recipes": 0,
            "mixed_source1_data_bus2_enumeration_complete": True,
        }
        if "source1-enable-source1-data" in mixed_driver_profiles:
            source1_data_bus2, enumerated_source1_data_stats = (
                gm.new_targeted_source1_data_mixed_two_switch_recipes(
                    sorted(base_universe_set),
                    expanded_functions,
                    expanded_functions,
                    mixed_targets,
                    engine.ALL,
                    max_per_coverage=args.max_per_coverage,
                    probe_row_count=args.mixed_bus2_probe_rows,
                    exact_verification_threshold=(
                        args.mixed_bus2_exact_threshold
                    ),
                    progress_callback=(
                        lambda row: emit_progress("mixed_target", **row)
                    ),
                )
            )

        for recipe in (*mixed_bus2, *source1_data_bus2):
            gm.add_recipe(by_target, recipe)
        combined_complete = bool(
            enumerated_mixed_stats["mixed_bus2_enumeration_complete"]
            and enumerated_source1_data_stats[
                "mixed_source1_data_bus2_enumeration_complete"
            ]
        )
        mixed_bus2_stats = {
            "mixed_bus2_target_profile": args.mixed_bus2_target_profile,
            "mixed_bus2_driver_profiles": list(mixed_driver_profiles),
            "mixed_bus2_target_labels": mixed_target_labels,
            **enumerated_mixed_stats,
            **enumerated_source1_data_stats,
            "mixed_bus2_combined_retained_recipes": (
                len(mixed_bus2) + len(source1_data_bus2)
            ),
            "mixed_bus2_combined_enumeration_complete": combined_complete,
        }
        emit_progress(
            "mixed_enumeration_complete",
            retained_base_data_recipes=len(mixed_bus2),
            retained_source1_data_recipes=len(source1_data_bus2),
            enumeration_complete=combined_complete,
        )

    recipes = [
        recipe
        for target in universe
        for recipe in by_target.get(target, {}).values()
    ]
    emit_progress("recipes_flattened", recipe_count=len(recipes))
    active, earliest = gm.reachable_recipes(recipes, sources, args.delay)
    producers: dict[int, list[int]] = {}
    for recipe_index in active:
        producers.setdefault(recipes[recipe_index].target, []).append(recipe_index)
    emit_progress(
        "reachability_complete",
        active_recipe_count=len(active),
        producer_function_count=len(producers),
    )

    cnf_shape_estimate: dict[str, object] | None = None
    if (
        args.cost_encoding == "producer-tiered"
        and args.cardinality_encoding == "seqcounter"
    ):
        emit_progress("cnf_estimator_start")
        cnf_shape_estimate = estimate_producer_tiered_cnf_shape(
            recipes,
            active,
            producers,
            earliest,
            sources,
            outputs,
            delay_bound=args.delay,
            gate_bound=args.gate,
        )
        emit_progress(
            "cnf_estimator_complete",
            cnf_variables=cnf_shape_estimate["cnf_variables"],
            cnf_clauses=cnf_shape_estimate["cnf_clauses"],
            cost_literal_count=cnf_shape_estimate["cost_literal_count"],
        )

    started = time.monotonic()
    if args.enumerate_only:
        status = "enumerated"
        selected: list[int] = []
        declared_arrival: dict[int, int] = {}
        solver_meta: dict[str, object] = {
            "backend": "not-run",
            "solver": args.solver,
            "cost_encoding": args.cost_encoding,
            "cardinality_encoding": args.cardinality_encoding,
            "cnf_storage": args.cnf_storage,
        }
    else:
        status, selected, declared_arrival, solver_meta = gm.pysat_select(
            recipes,
            active,
            producers,
            earliest,
            sources,
            outputs,
            delay_bound=args.delay,
            gate_bound=args.gate,
            timeout_ms=args.timeout_ms,
            solver_name=args.solver,
            cost_encoding=args.cost_encoding,
            cardinality_encoding=args.cardinality_encoding,
            cnf_storage=args.cnf_storage,
        )
        if cnf_shape_estimate is not None:
            if solver_meta["cost_literal_count"] != cnf_shape_estimate["cost_literal_count"]:
                raise RuntimeError(
                    "tiered cost literal estimate mismatch: "
                    f"{solver_meta['cost_literal_count']} != "
                    f"{cnf_shape_estimate['cost_literal_count']}"
                )
            if solver_meta["cnf_variables"] != cnf_shape_estimate["cnf_variables"]:
                raise RuntimeError(
                    "tiered CNF variable estimate mismatch: "
                    f"{solver_meta['cnf_variables']} != "
                    f"{cnf_shape_estimate['cnf_variables']}"
                )
            if solver_meta["cnf_clauses"] != cnf_shape_estimate["cnf_clauses"]:
                raise RuntimeError(
                    "tiered CNF clause estimate mismatch: "
                    f"{solver_meta['cnf_clauses']} != "
                    f"{cnf_shape_estimate['cnf_clauses']}"
                )
    elapsed = time.monotonic() - started
    payload: dict[str, object] = {
        "schema": "phase-high-global-function-map-v1",
        "status": status,
        "mode": args.mode,
        "delay_bound": args.delay,
        "high_window_gate_bound": args.gate,
        "fixed_paid_gate": fixed_gate,
        "complete_gate_bound": fixed_gate + args.gate,
        "vectors": engine.ASSIGNMENTS,
        "source_sha256": hashlib.sha256(gm.SOURCE.read_bytes()).hexdigest(),
        "hub79_circuit_sha256": hashlib.sha256(gm.SOURCE.read_bytes()).hexdigest(),
        "mapper_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "global_core_script_sha256": hashlib.sha256(GLOBAL_PATH.read_bytes()).hexdigest(),
        "hub33_library_script_sha256": hashlib.sha256(
            HUB33_LIBRARY_PATH.read_bytes()
        ).hexdigest(),
        "s12_witness_sha256": hashlib.sha256(S12_WITNESS.read_bytes()).hexdigest(),
        "candidate_witness_sha256": {
            path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (S56_WITNESS, S4_WITNESS, S34_WITNESS, TAIL_S7C8_WITNESS)
            if path.is_file()
        },
        "hub33_function_library": hub33_meta,
        "universe_functions": len(universe),
        "base_universe_functions": len(base_universe_set),
        "universe_expansion": args.universe_expansion,
        "bus_driver_universe": args.bus_driver_universe,
        **mixed_bus2_stats,
        **expansion_stats,
        "paid_source_functions": len(sources),
        "ordinary_recipe_count": sum(
            recipe.op in {"NOT", "AND", "OR", "NAND", "NOR"}
            for recipe in recipes
        ),
        "original_bus_recipe_count": sum(recipe.op == "ORIGINAL_BUS" for recipe in recipes),
        **bus2_stats,
        "recipe_count": len(recipes),
        "candidate_count": len(active),
        "enumerate_only": args.enumerate_only,
        "cnf_shape_estimate": cnf_shape_estimate,
        "seconds": elapsed,
        **solver_meta,
        "outputs": [name for name, _truth in outputs],
        "proof_limit": (
            "UNSAT applies only to the stated function universe, base BUS-driver "
            "universe, and explicitly named mixed BUS target/driver profiles; "
            "SAT is a constructive complete 2^17-row upper bound."
        ),
    }
    if status != "sat":
        return payload

    actual_arrival = dict(sources)
    unresolved = set(selected)
    rows: list[dict[str, object]] = []
    conflict_free = True
    while unresolved:
        progress = False
        for index in tuple(unresolved):
            recipe = recipes[index]
            if not all(dep in actual_arrival for dep in recipe.deps):
                continue
            arrival = max((actual_arrival[dep] for dep in recipe.deps), default=0) + recipe.step_delay
            if recipe.op == "NOT":
                replay = (~recipe.deps[0]) & engine.ALL
            elif recipe.op == "AND":
                replay = recipe.deps[0] & recipe.deps[1]
            elif recipe.op == "OR":
                replay = recipe.deps[0] | recipe.deps[1]
            elif recipe.op == "NAND":
                replay = (~(recipe.deps[0] & recipe.deps[1])) & engine.ALL
            elif recipe.op == "NOR":
                replay = (~(recipe.deps[0] | recipe.deps[1])) & engine.ALL
            elif recipe.op in {
                "BUS2",
                "BUS2_MIXED_ENABLE",
                "BUS2_MIXED_SOURCE1_DATA",
                "ORIGINAL_BUS",
            }:
                drivers = (
                    recipe.detail
                    if recipe.op
                    in {"BUS2", "BUS2_MIXED_ENABLE", "BUS2_MIXED_SOURCE1_DATA"}
                    else recipe.detail[1]
                )
                ones = 0
                zeros = 0
                for enable, data in drivers:
                    ones |= enable & data
                    zeros |= enable & (~data & engine.ALL)
                conflict_free &= not bool(ones & zeros)
                replay = ones
            else:
                raise RuntimeError(recipe.op)
            if replay != recipe.target:
                raise RuntimeError(f"recipe replay mismatch: {recipe.op}")
            old_arrival = actual_arrival.get(recipe.target)
            actual_arrival[recipe.target] = (
                arrival if old_arrival is None else min(old_arrival, arrival)
            )
            rows.append(
                {
                    "recipe_index": index,
                    "function_sha256": gm.digest(recipe.target, engine.ASSIGNMENTS // 8),
                    "labels": sorted(
                        name for name, truth in named.items() if truth == recipe.target
                    )[:12],
                    "op": recipe.op,
                    "dependency_sha256": [
                        gm.digest(dep, engine.ASSIGNMENTS // 8) for dep in recipe.deps
                    ],
                    "cost": recipe.cost,
                    "declared_arrival": declared_arrival[recipe.target],
                    "actual_recipe_arrival": arrival,
                    "effective_arrival": actual_arrival[recipe.target],
                    "detail": list(recipe.detail),
                }
            )
            unresolved.remove(index)
            progress = True
        if not progress:
            raise RuntimeError("selected model contains a dependency cycle")

    output_rows = []
    for name, truth in outputs:
        arrival = actual_arrival.get(truth)
        if arrival is None or arrival > args.delay:
            raise RuntimeError(f"missing/late output {name}: {arrival}")
        output_rows.append(
            {
                "name": name,
                "function_sha256": gm.digest(truth, engine.ASSIGNMENTS // 8),
                "arrival": arrival,
            }
        )
    actual_high_gate = sum(recipes[index].cost for index in selected)
    payload.update(
        {
            "actual_high_gate": actual_high_gate,
            "actual_complete_gate": fixed_gate + actual_high_gate,
            "actual_delay": max(row["arrival"] for row in output_rows),
            "selected_node_count": len(selected),
            "selected_op_histogram": dict(
                sorted(Counter(recipes[index].op for index in selected).items())
            ),
            "verification": {
                "all_selected_functions_exact": True,
                "all_bus_drivers_conflict_free": conflict_free,
                "all_outputs_present": True,
                "complete_truth_rows": engine.ASSIGNMENTS,
                "complete_gate_at_most_102": fixed_gate + actual_high_gate <= 102,
            },
            "output_rows": output_rows,
            "selected_nodes": sorted(
                rows, key=lambda row: (row["effective_arrival"], row["function_sha256"])
            ),
            "paid_sources": [
                {
                    "function_sha256": gm.digest(truth, engine.ASSIGNMENTS // 8),
                    "arrival": arrival,
                    "labels": sorted(source_labels.get(truth, [])),
                }
                for truth, arrival in sorted(sources.items(), key=lambda item: (item[1], item[0]))
            ],
        }
    )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("paid-nc7", "integrated-nc7"), default="paid-nc7")
    parser.add_argument("--delay", type=int, default=5)
    parser.add_argument("--gate", type=int)
    parser.add_argument("--timeout-ms", type=int, default=300_000)
    parser.add_argument("--without-new-bus2", action="store_true")
    parser.add_argument("--without-hub33-functions", action="store_true")
    parser.add_argument(
        "--universe-expansion",
        choices=("curated", "source1-residual"),
        default="curated",
    )
    parser.add_argument(
        "--bus-driver-universe",
        choices=("base", "expanded"),
        default="base",
        help="expanded is exact but can be prohibitively large for source1-residual",
    )
    parser.add_argument(
        "--mixed-bus2-target-profile",
        choices=(
            "none",
            "witness-controls",
            "phase-hub33-controls",
            "hub33-network-functions",
            "all-base-bus-targets",
        ),
        default="none",
        help=(
            "add an exact targeted class with one base driver and one "
            "source1-enable/base-data driver"
        ),
    )
    parser.add_argument(
        "--mixed-bus2-driver-profile",
        action="append",
        choices=(
            "source1-enable-base-data",
            "source1-enable-source1-data",
        ),
        help=(
            "repeat to accumulate disjoint mixed driver classes; the source1-data "
            "class requires the base-data class"
        ),
    )
    parser.add_argument(
        "--mixed-bus2-probe-rows",
        type=int,
        default=1024,
        help=(
            "conservative source1-data index rows; every survivor is still checked "
            "against all truth rows"
        ),
    )
    parser.add_argument(
        "--mixed-bus2-exact-threshold",
        type=int,
        default=8,
        help="stop probe filtering at this many candidates before exact full-mask checks",
    )
    parser.add_argument("--max-per-coverage", type=int, default=32)
    parser.add_argument(
        "--enumerate-only",
        action="store_true",
        help="enumerate recipes/reachability and predict tiered seqcounter CNF without solving",
    )
    parser.add_argument(
        "--progress",
        action="store_true",
        help="emit deterministic phase/target JSON lines to stderr",
    )
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument(
        "--cost-encoding",
        choices=("grouped", "producer-tiered", "expanded"),
        default="grouped",
    )
    parser.add_argument(
        "--cardinality-encoding",
        choices=("seqcounter", "cardnetwrk", "sortnetwrk", "totalizer", "mtotalizer", "kmtotalizer"),
        default="seqcounter",
    )
    parser.add_argument(
        "--cnf-storage",
        choices=("materialized", "streaming"),
        default="materialized",
        help="streaming sends clauses directly to the solver to reduce peak memory",
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.max_per_coverage <= 0:
        parser.error("--max-per-coverage must be positive")
    if args.mixed_bus2_probe_rows < 0:
        parser.error("--mixed-bus2-probe-rows must be non-negative")
    if args.mixed_bus2_exact_threshold < 0:
        parser.error("--mixed-bus2-exact-threshold must be non-negative")
    if args.gate is None:
        args.gate = 29 if args.mode == "paid-nc7" else 33
    payload = solve(args)
    encoded = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(encoded, encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(args.output),
                "status": payload["status"],
                "mode": payload["mode"],
                "high_gate": payload.get("actual_high_gate"),
                "complete_gate": payload.get("actual_complete_gate"),
                "delay": payload.get("actual_delay"),
                "seconds": payload["seconds"],
                "recipes": payload["recipe_count"],
                "candidates": payload["candidate_count"],
                "sha256": hashlib.sha256(encoded.encode()).hexdigest(),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
