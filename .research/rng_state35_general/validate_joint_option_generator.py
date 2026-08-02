"""Brute-force cross-check of the mixed-network option generator/reducer."""

from __future__ import annotations

from collections import defaultdict
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import time

import joint_shared_controls as shared


STATE_BITS = 8
OUTPUT = Path(__file__).resolve().parent / "joint-option-generator-n8-verified.json"


def old_reduce(target: int, options: tuple[shared.Option, ...]) -> tuple[shared.Option, ...]:
    if target.bit_count() == 2:
        return tuple(option for option in options if option.kind == "direct")
    alternatives = tuple(option for option in options if option.kind in ("direct", "xor2"))
    kept = []
    for option in options:
        if option.kind != "switch_xor3":
            kept.append(option)
            continue
        present = frozenset(option.required_forms)
        dominated = False
        for alternative in alternatives:
            added = tuple(form for form in alternative.required_forms if form not in present)
            if any(form.bit_count() != 2 for form in added):
                continue
            if alternative.final_base_gate + shared.PAIR_GATE * len(added) <= shared.SWITCH_XOR3_BASE_GATE:
                dominated = True
                break
        if not dominated:
            kept.append(option)
    return tuple(kept)


def old_relaxed(options: tuple[shared.Option, ...]) -> tuple[shared.Option, ...]:
    by_kind: dict[str, dict[tuple[int, ...], shared.Option]] = {}
    for option in options:
        by_kind.setdefault(option.kind, {}).setdefault(option.required_forms, option)
    minimal = []
    for records in by_kind.values():
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
    kept = []
    for option in minimal:
        if option.kind != "switch_xor3":
            kept.append(option)
            continue
        present = frozenset(option.required_forms)
        if any(
            alternative.final_base_gate
            + sum(
                shared.PAIR_GATE if form.bit_count() == 2 else shared.SWITCH_XOR3_BASE_GATE
                for form in alternative.required_forms
                if form not in present
            )
            <= shared.SWITCH_XOR3_BASE_GATE
            for alternative in cheaper
        ):
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


def raw_options(
    target: int,
    sources: tuple[int, ...],
    forms: frozenset[int],
    switch_map: dict[int, set[tuple[int, int, int]]],
) -> tuple[shared.Option, ...]:
    source_set = frozenset(sources)
    options: set[shared.Option] = set()
    if target in forms:
        options.add(shared.Option("direct", (target,), (target,)))
    for left in sources:
        right = target ^ left
        if left < right and right in source_set:
            used = tuple(sorted(value for value in (left, right) if value in forms))
            options.add(shared.Option("xor2", used, (left, right)))
    if target.bit_count() >= 4:
        for triple in switch_map[target]:
            used = tuple(value for value in triple if value in forms)
            options.add(shared.Option("switch_xor3", used, triple))
    return tuple(
        sorted(
            options,
            key=lambda option: (
                option.final_base_gate
                + sum(
                    shared.PAIR_GATE if value.bit_count() == 2 else shared.SWITCH_XOR3_BASE_GATE
                    for value in option.required_forms
                ),
                option.kind,
                option.required_forms,
                option.sources,
            ),
        )
    )


def main() -> int:
    started = time.perf_counter()
    sources, forms = shared.first_forms(STATE_BITS)
    switch_map: dict[int, set[tuple[int, int, int]]] = defaultdict(set)
    for triple in combinations(sources, 3):
        switch_map[triple[0] ^ triple[1] ^ triple[2]].add(triple)

    targets = tuple(
        target
        for target in range(1, 1 << STATE_BITS)
        if 2 <= target.bit_count() <= 6
    )
    digest = sha256()
    raw_total = physical_total = relaxed_total = 0
    for target in targets:
        if target.bit_count() >= 4:
            generated = set(shared.switch_source_triples(target, STATE_BITS))
            if generated != switch_map[target]:
                raise AssertionError(f"Switch-XOR3 enumeration mismatch for {target:02x}")
        raw = raw_options(target, sources, forms, switch_map)
        physical_reference = old_reduce(target, raw)
        physical_fast = shared.reduce_options(target, raw)
        if physical_fast != physical_reference:
            raise AssertionError(f"physical dominance mismatch for {target:02x}")
        relaxed_reference = old_relaxed(physical_reference)
        relaxed_fast = shared.relaxed_reduce_options(physical_fast)
        if relaxed_fast != relaxed_reference:
            raise AssertionError(f"relaxed dominance mismatch for {target:02x}")
        raw_total += len(raw)
        physical_total += len(physical_fast)
        relaxed_total += len(relaxed_fast)
        digest.update(
            f"{target:02x} {len(raw)} {len(physical_fast)} {len(relaxed_fast)}\n".encode("ascii")
        )

    result = {
        "schema": 1,
        "status": "VERIFIED",
        "state_bits": STATE_BITS,
        "source_count": len(sources),
        "target_count": len(targets),
        "brute_source_triple_count": sum(len(value) for value in switch_map.values()),
        "raw_option_count": raw_total,
        "physical_option_count": physical_total,
        "relaxed_option_count": relaxed_total,
        "checks": [
            "switch_source_triples equals brute combinations(sources,3)",
            "optimized physical dominance equals original all-alternatives scan",
            "optimized relaxed dominance equals original all-alternatives scan",
        ],
        "count_digest_sha256": digest.hexdigest(),
        "runtime_seconds": time.perf_counter() - started,
        "peak_working_set_mb": shared.current_rss_bytes() / 1048576,
    }
    encoded = (json.dumps(result, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    OUTPUT.write_bytes(encoded)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
