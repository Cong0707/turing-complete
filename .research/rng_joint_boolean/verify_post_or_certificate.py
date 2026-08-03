#!/usr/bin/env python3
"""Independently verify a SAT certificate from search_post_or_fixed.py."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from tc_save_lab.rng_encoded_asic import T, bits  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    document = json.loads(args.path.read_text(encoding="utf-8"))
    if document.get("status") != "sat":
        raise SystemExit("certificate verifier requires a SAT result")
    certificate = document["certificate"]

    leaf_atoms = {
        (int(item["seed"]), int(item["state"]))
        for item in certificate["leaf_atoms"]
    }
    post_atoms = {
        (int(item["seed"]), int(item["pair"], 16))
        for item in certificate["post_atoms"]
    }
    required_leaf: set[tuple[int, int]] = set()
    required_post: set[tuple[int, int]] = set()
    pair_modes = certificate["pair_modes"]
    for pair_hex, record in pair_modes.items():
        pair = int(pair_hex, 16)
        state_bits = bits(pair)
        if len(state_bits) != 2:
            raise AssertionError("pair mode key is not weight two")
        label = int(record["pre_label"], 16)
        if record["mode"] == "raw-post":
            if label:
                raise AssertionError("raw pair has a pre label")
        elif record["mode"] == "pre-xor":
            pins = record["pin_seed_bits"]
            if len(pins) != 2:
                raise AssertionError("pre pair does not have two pin records")
            actual = 0
            for state, seed in zip(state_bits, pins, strict=True):
                if seed is not None:
                    seed = int(seed)
                    actual ^= 1 << seed
                    required_leaf.add((seed, state))
            if actual != label or label.bit_count() > 2:
                raise AssertionError("pre pair label/orientation mismatch")
        else:
            raise AssertionError("unknown pair implementation mode")

    labels_by_output: dict[int, list[int]] = {index: [] for index in range(32)}
    for occurrence in certificate["B_occurrences"]:
        tag = str(occurrence["tag"])
        if not tag.startswith("B") or "-" not in tag:
            raise AssertionError("invalid B occurrence tag")
        output = int(tag[1 : tag.index("-")])
        label = int(occurrence["effective_label"], 16)
        labels_by_output[output].append(label)
        steady = int(occurrence["steady"], 16)
        if occurrence["kind"] == "unit":
            state_bits = bits(steady)
            if len(state_bits) != 1 or label.bit_count() > 1:
                raise AssertionError("unit occurrence is not a unit label")
            if label:
                required_leaf.add((bits(label)[0], state_bits[0]))
        elif occurrence["kind"] == "pair":
            mode = pair_modes[f"{steady:08x}"]
            post_seed = occurrence.get("post_seed_bit")
            if mode["mode"] == "raw-post":
                if label.bit_count() > 1:
                    raise AssertionError("post pair label is not a unit")
                expected_post = None if not label else bits(label)[0]
                if post_seed != expected_post:
                    raise AssertionError("post choice and effective label differ")
                if expected_post is not None:
                    required_post.add((expected_post, steady))
            else:
                if label != int(mode["pre_label"], 16) or post_seed is not None:
                    raise AssertionError("pre pair occurrence changed its global label")
        else:
            raise AssertionError("unknown occurrence kind")

    for output, labels in labels_by_output.items():
        if len(labels) not in (1, 2):
            raise AssertionError(f"B{output} has {len(labels)} physical fanins")
        actual = 0
        for label in labels:
            actual ^= label
        if actual != T[output]:
            raise AssertionError(
                f"B{output} load label {actual:08x} != T {T[output]:08x}"
            )

    if required_leaf != leaf_atoms:
        raise AssertionError("leaf OR union differs from certificate")
    if required_post != post_atoms:
        raise AssertionError("post OR union differs from certificate")
    or_count = len(leaf_atoms) + len(post_atoms)
    if or_count != certificate["or_count"]:
        raise AssertionError("OR count mismatch")
    fixed_xor = int(document["fixed_xor"])
    expected_total = 172 + fixed_xor * 3 + or_count
    if expected_total != certificate["total_gate"]:
        raise AssertionError("total gate mismatch")
    if int(document["delay"]) != 9:
        raise AssertionError("certificate is not a 9-delay construction")
    print(json.dumps({
        "status": "verified",
        "B_rows": 32,
        "occurrences": sum(len(values) for values in labels_by_output.values()),
        "leaf_or": len(leaf_atoms),
        "post_or": len(post_atoms),
        "or_count": or_count,
        "xor_count": fixed_xor,
        "total_gate": expected_total,
        "delay": 9,
        "cycles": int(document["cycles"]),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
