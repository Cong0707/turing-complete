"""Score one- and two-gate extensions of exact S3/S4 paid phase families.

The full high29 SAT search is expensive and most unconstrained kind layouts
time out.  This utility is a deterministic filter for the exact S3/S4 phase
families produced by ``enumerate_s34_internal_phase_family.py``.  For every
family it replays the physical Switch/Z network over all 486 correlated high
rows, enumerates every distinct ordinary truth function available at D4 from
always-driven D3 sources, and measures how many rows remain uncovered after
at most two terminal Switch drivers for each of S5/S6/S7/C8.

The score is deliberately only a topology heuristic.  It does not claim that
independent per-output driver covers can share one physical net or that the
complete high29 budget is SAT.  Promising prefixes still have to go through
the authoritative physical solver and the production verification pipeline.

This program is save-independent and never starts Turing Complete.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import importlib.util
import itertools
import json
from pathlib import Path
import sys
from typing import Iterable


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PHYSICAL_PATH = ROOT / ".research/byte_adder_phase_shortcut_restart/physical_exact.py"
DEFAULT_FAMILIES = HERE / "s34-internal-phase-family-r1.json"
TARGET_NAMES = ("S5", "S6", "S7", "C8")
ORDINARY = ("NOT", "AND", "OR", "NAND", "NOR")


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


physical = _load_module("s34_extension_physical", PHYSICAL_PATH)


def _digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _pack(values: Iterable[bool]) -> int:
    return sum(int(value) << row for row, value in enumerate(values))


def _resolve(
    values: list[int], drivens: list[int], bus: list[int], mask: int
) -> tuple[int, int]:
    active_one = 0
    active_zero = 0
    for source in bus:
        active_one |= drivens[source] & values[source]
        active_zero |= drivens[source] & (mask ^ values[source])
    conflict = active_one & active_zero
    if conflict:
        raise ValueError(f"BUS conflict on {conflict.bit_count()} rows")
    return active_one, active_one | active_zero


def _apply(kind: str, left: int, right: int, mask: int) -> int:
    if kind == "NOT":
        return mask ^ left
    if kind == "AND":
        return left & right
    if kind == "OR":
        return left | right
    if kind == "NAND":
        return mask ^ (left & right)
    if kind == "NOR":
        return mask ^ (left | right)
    raise ValueError(kind)


def _replay_family(full_domain, s34_domain, record: dict[str, object]):
    """Replay record indices in their original S3/S4 source order."""

    mask = (1 << full_domain.rows) - 1
    full_by_name = dict(zip(full_domain.names, full_domain.columns, strict=True))
    values = [_pack(full_by_name[name]) for name in s34_domain.names] + [0, mask]
    drivens = [mask] * len(values)
    arrivals = [s34_domain.arrivals[name] for name in s34_domain.names] + [0, 0]

    for expected_slot, item in enumerate(record["network"]):
        if int(item["slot"]) != expected_slot:
            raise ValueError("non-topological family record")
        left, _left_driven = _resolve(values, drivens, item["left_bus"], mask)
        right, _right_driven = _resolve(values, drivens, item["right_bus"], mask)
        kind = str(item["kind"])
        if kind == "SWITCH":
            value = left & right
            driven = left
        else:
            value = _apply(kind, left, right, mask)
            driven = mask
        inputs = [*item["left_bus"], *item["right_bus"]]
        arrival = max((arrivals[source] for source in inputs), default=0) + 1
        if arrival > int(item["depth_upper_bound"]):
            raise ValueError("family record violates recursive arrival")
        values.append(value)
        drivens.append(driven)
        arrivals.append(arrival)

    for output_index, output_bus in enumerate(record["output_buses"]):
        value, driven = _resolve(values, drivens, output_bus, mask)
        target = full_domain.targets[output_index]
        if driven != mask or value != target:
            raise ValueError(f"family output {output_index} failed 486-row replay")
    return values, drivens, arrivals


def _unique_signals(items: Iterable[tuple[str, int]]) -> tuple[tuple[str, int], ...]:
    by_truth: dict[int, str] = {}
    for label, truth in items:
        by_truth.setdefault(truth, label)
    return tuple((label, truth) for truth, label in by_truth.items())


def _ordinary_extensions(
    sources: tuple[tuple[str, int], ...], existing: set[int], mask: int
) -> tuple[tuple[str, int], ...]:
    found: dict[int, str] = {}
    for left_label, left in sources:
        truth = mask ^ left
        if truth not in existing:
            found.setdefault(truth, f"NOT({left_label})")
    for left_index, (left_label, left) in enumerate(sources):
        for right_label, right in sources[left_index:]:
            expressions = (
                ("AND", left & right),
                ("OR", left | right),
                ("NAND", mask ^ (left & right)),
                ("NOR", mask ^ (left | right)),
            )
            for kind, truth in expressions:
                if truth not in existing:
                    found.setdefault(truth, f"{kind}({left_label},{right_label})")
    return tuple((label, truth) for truth, label in found.items())


def _valid_enables(signals: tuple[int, ...], target: int) -> tuple[int, ...]:
    unique = tuple(dict.fromkeys(signals))
    return tuple(
        enable
        for enable in unique
        if enable and any((enable & (data ^ target)) == 0 for data in unique)
    )


def _driver_score(signals: tuple[int, ...], target: int, mask: int) -> dict[str, int]:
    enables = _valid_enables(signals, target)
    best_one = max((enable.bit_count() for enable in enables), default=0)
    best_two = best_one
    for left_index, left in enumerate(enables):
        for right in enables[left_index:]:
            best_two = max(best_two, (left | right).bit_count())
    return {
        "valid_enable_count": len(enables),
        "uncovered_with_one_switch": domain_rows(mask) - best_one,
        "uncovered_with_two_switches": domain_rows(mask) - best_two,
    }


def domain_rows(mask: int) -> int:
    return mask.bit_count()


def _metrics(
    signals: tuple[int, ...], targets: dict[str, int], mask: int
) -> dict[str, object]:
    per_output = {
        name: _driver_score(signals, target, mask)
        for name, target in targets.items()
    }
    uncovered = {
        name: int(score["uncovered_with_two_switches"])
        for name, score in per_output.items()
    }
    return {
        "per_output": per_output,
        "two_switch_uncovered": uncovered,
        "sum_two_switch_uncovered": sum(uncovered.values()),
        "max_two_switch_uncovered": max(uncovered.values()),
        "fully_covered_output_count": sum(value == 0 for value in uncovered.values()),
    }


def _family_score(
    domain,
    s34_domain,
    record: dict[str, object],
    top: int,
    pair_pool_limit: int,
    pair_top: int,
) -> dict[str, object]:
    mask = (1 << domain.rows) - 1
    values, drivens, arrivals = _replay_family(domain, s34_domain, record)
    source_count = len(s34_domain.names) + 2
    labels = [*s34_domain.names, "0", "1"] + [
        f"u{slot}" for slot in range(len(record["network"]))
    ]
    kinds = [None] * source_count + [str(item["kind"]) for item in record["network"]]

    base_terminal = [
        (name, _pack(column))
        for name, column in zip(domain.names, domain.columns, strict=True)
        if domain.arrivals[name] <= 4
    ]
    base_terminal.extend((("0", 0), ("1", mask)))
    paid_terminal = [
        (labels[index], values[index])
        for index in range(source_count, len(values))
        if kinds[index] in ORDINARY and arrivals[index] <= 4 and drivens[index] == mask
    ]
    terminal = _unique_signals((*base_terminal, *paid_terminal))

    base_d3 = [
        (name, _pack(column))
        for name, column in zip(domain.names, domain.columns, strict=True)
        if domain.arrivals[name] <= 3
    ]
    base_d3.extend((("0", 0), ("1", mask)))
    paid_d3 = [
        (labels[index], values[index])
        for index in range(source_count, len(values))
        if kinds[index] in ORDINARY and arrivals[index] <= 3 and drivens[index] == mask
    ]
    d3_sources = _unique_signals((*base_d3, *paid_d3))
    terminal_truths = tuple(truth for _label, truth in terminal)
    extensions = _ordinary_extensions(d3_sources, set(terminal_truths), mask)

    targets = {
        name: domain.targets[domain.output_names.index(name)] for name in TARGET_NAMES
    }
    baseline = _metrics(terminal_truths, targets, mask)
    by_name = {
        name: _pack(column)
        for name, column in zip(domain.names, domain.columns, strict=True)
    }
    rare = mask ^ (by_name["nC3"] | by_name["A34n"])
    final_rare = rare
    for name in ("P3", "P4", "P5", "P6", "P7"):
        final_rare &= by_name[name]

    scored_with_truth: list[tuple[dict[str, object], int]] = []
    for expression, truth in extensions:
        metrics = _metrics((*terminal_truths, truth), targets, mask)
        item = {
            "expression": expression,
            "truth_sha256": sha256(truth.to_bytes(61, "little")).hexdigest(),
            **metrics,
            "improvement": int(baseline["sum_two_switch_uncovered"])
            - int(metrics["sum_two_switch_uncovered"]),
            "rare_hamming_distance": (truth ^ rare).bit_count(),
            "not_rare_hamming_distance": (truth ^ (mask ^ rare)).bit_count(),
            "final_rare_hamming_distance": (truth ^ final_rare).bit_count(),
            "equals_rare": truth == rare,
            "equals_not_rare": truth == (mask ^ rare),
            "equals_nC7": truth == by_name["nC7"],
            "equals_C7": truth == (mask ^ by_name["nC7"]),
        }
        scored_with_truth.append((item, truth))

    def single_key(entry: tuple[dict[str, object], int]):
        item, _truth = entry
        return (
            item["sum_two_switch_uncovered"],
            item["max_two_switch_uncovered"],
            -item["fully_covered_output_count"],
            item["rare_hamming_distance"],
            item["expression"],
        )

    scored_with_truth.sort(key=single_key)
    scored = [item for item, _truth in scored_with_truth]

    # Two independent D4 ordinary gates are the exact paid shape of o2/s8.
    # Full 1118^2 enumeration is unnecessary for a directional filter, so the
    # pool combines globally strong functions, output-specialists, and phases
    # closest to rare/not-rare.  Every selected pair is still scored exactly.
    selected: dict[int, dict[str, object]] = {}

    def take(entries: Iterable[tuple[dict[str, object], int]], count: int) -> None:
        for item, truth in itertools.islice(entries, count):
            if len(selected) >= pair_pool_limit:
                break
            selected.setdefault(truth, item)

    global_quota = max(1, pair_pool_limit * 3 // 8)
    output_quota = max(1, pair_pool_limit * 3 // (8 * len(TARGET_NAMES)))
    rare_quota = max(1, pair_pool_limit // 10)
    not_rare_quota = max(1, pair_pool_limit // 16)
    final_rare_quota = max(
        1,
        pair_pool_limit
        - global_quota
        - output_quota * len(TARGET_NAMES)
        - rare_quota
        - not_rare_quota,
    )

    take(scored_with_truth, global_quota)
    for output in TARGET_NAMES:
        take(
            sorted(
                scored_with_truth,
                key=lambda entry: (
                    entry[0]["two_switch_uncovered"][output],
                    entry[0]["sum_two_switch_uncovered"],
                    entry[0]["expression"],
                ),
            ),
            output_quota,
        )
    take(
        sorted(scored_with_truth, key=lambda entry: entry[0]["rare_hamming_distance"]),
        rare_quota,
    )
    take(
        sorted(scored_with_truth, key=lambda entry: entry[0]["not_rare_hamming_distance"]),
        not_rare_quota,
    )
    take(
        sorted(scored_with_truth, key=lambda entry: entry[0]["final_rare_hamming_distance"]),
        final_rare_quota,
    )
    for item, truth in scored_with_truth:
        if len(selected) >= pair_pool_limit:
            break
        selected.setdefault(truth, item)
    pair_pool = tuple((item, truth) for truth, item in selected.items())[:pair_pool_limit]

    pair_scores: list[dict[str, object]] = []
    for (left_item, left_truth), (right_item, right_truth) in itertools.combinations(
        pair_pool, 2
    ):
        metrics = _metrics(
            (*terminal_truths, left_truth, right_truth), targets, mask
        )
        pair_scores.append(
            {
                "expressions": [left_item["expression"], right_item["expression"]],
                "truth_sha256": [
                    left_item["truth_sha256"],
                    right_item["truth_sha256"],
                ],
                **metrics,
                "improvement": int(baseline["sum_two_switch_uncovered"])
                - int(metrics["sum_two_switch_uncovered"]),
                "contains_rare": bool(left_item["equals_rare"] or right_item["equals_rare"]),
                "contains_not_rare": bool(
                    left_item["equals_not_rare"] or right_item["equals_not_rare"]
                ),
                "best_rare_hamming_distance": min(
                    int(left_item["rare_hamming_distance"]),
                    int(right_item["rare_hamming_distance"]),
                ),
            }
        )
    pair_scores.sort(
        key=lambda item: (
            item["sum_two_switch_uncovered"],
            item["max_two_switch_uncovered"],
            -item["fully_covered_output_count"],
            item["best_rare_hamming_distance"],
            item["expressions"],
        )
    )
    return {
        "model_index": record["model_index"],
        "phase_family_sha256": record["phase_family_sha256"],
        "terminal_signal_count": len(terminal),
        "d3_source_count": len(d3_sources),
        "distinct_one_gate_extensions": len(extensions),
        "pair_pool_count": len(pair_pool),
        "exact_scored_pair_count": len(pair_scores),
        "rare_row_count": rare.bit_count(),
        "final_rare_row_count": final_rare.bit_count(),
        "baseline": baseline,
        "top_extensions": scored[:top],
        "top_extension_pairs": pair_scores[:pair_top],
    }


def score(args: argparse.Namespace) -> dict[str, object]:
    source = json.loads(args.families.read_text(encoding="utf-8"))
    if source.get("schema") != "s34-internal-phase-family-enumeration-v1":
        raise ValueError("unexpected phase-family schema")
    domain = physical.domain_s34567c8_leaf()
    s34_domain = physical.domain_s3456_leaf()
    families = [
        _family_score(
            domain,
            s34_domain,
            record,
            args.top,
            args.pair_pool,
            args.pair_top,
        )
        for record in source["records"]
    ]
    global_top = sorted(
        (
            {"model_index": family["model_index"], **candidate}
            for family in families
            for candidate in family["top_extensions"]
        ),
        key=lambda item: (
            item["sum_two_switch_uncovered"],
            item["max_two_switch_uncovered"],
            -item["fully_covered_output_count"],
            item["rare_hamming_distance"],
            item["model_index"],
            item["expression"],
        ),
    )[: args.top]
    global_top_pairs = sorted(
        (
            {"model_index": family["model_index"], **candidate}
            for family in families
            for candidate in family["top_extension_pairs"]
        ),
        key=lambda item: (
            item["sum_two_switch_uncovered"],
            item["max_two_switch_uncovered"],
            -item["fully_covered_output_count"],
            item["best_rare_hamming_distance"],
            item["model_index"],
            item["expressions"],
        ),
    )[: args.pair_top]
    result = {
        "schema": "s34-internal-phase-extension-score-v2",
        "status": "complete",
        "scope": {
            "rows": domain.rows,
            "families": len(families),
            "candidate_gate_arrival": 4,
            "terminal_switch_arrival": 5,
            "per_output_switch_limit": 2,
            "pair_pool_limit": args.pair_pool,
            "physical_tail_sat_claimed": False,
            "score_is_topology_heuristic": True,
        },
        "dependency_sha256": {
            str(args.families.resolve().relative_to(ROOT)).replace("\\", "/"): _digest(args.families),
            str(PHYSICAL_PATH.relative_to(ROOT)).replace("\\", "/"): _digest(PHYSICAL_PATH),
            str(Path(__file__).resolve().relative_to(ROOT)).replace("\\", "/"): _digest(Path(__file__).resolve()),
        },
        "families": families,
        "global_top_extensions": global_top,
        "global_top_extension_pairs": global_top_pairs,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(
        (json.dumps(result, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--families", type=Path, default=DEFAULT_FAMILIES)
    parser.add_argument("--top", type=int, default=32)
    parser.add_argument("--pair-pool", type=int, default=64)
    parser.add_argument("--pair-top", type=int, default=32)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = score(args)
    print(
        json.dumps(
            {
                "status": result["status"],
                "families": len(result["families"]),
                "global_top_extensions": result["global_top_extensions"][:5],
                "global_top_extension_pairs": result["global_top_extension_pairs"][:5],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
