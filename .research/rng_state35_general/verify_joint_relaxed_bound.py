"""Independently replay a lazy joint-cost lower-bound certificate."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import threading
import time

from pysat.examples.rc2 import RC2
from pysat.formula import WCNF

import joint_relaxed_bound as audit
import joint_shared_controls as shared


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("certificate", type=Path)
    parser.add_argument("--timeout-seconds", type=float, default=300.0)
    parser.add_argument("--memory-mb", type=int, default=680)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 64 <= args.memory_mb <= 700:
        parser.error("--memory-mb must be in [64,700]")

    certificate_bytes = args.certificate.read_bytes()
    certificate = json.loads(certificate_bytes)
    source = Path(certificate["source"])
    if sha256(source.read_bytes()).hexdigest() != certificate["source_sha256"]:
        raise AssertionError("candidate SHA-256 mismatch")
    state_bits = int(certificate["state_bits"])
    hidden = state_bits - shared.VISIBLE
    h_rows, o_rows = shared.load_candidate(source, hidden)
    targets = tuple(sorted({row for row in (*h_rows, *o_rows) if row.bit_count() >= 2}))
    (
        families,
        form_var,
        type_var,
        var_cost,
        variable_count,
        raw_total,
        reduced_total,
        compact_literals,
    ) = audit.build_families(targets, state_bits, memory_mb=args.memory_mb)

    reported = certificate["solve"]
    formula_meta = reported["formula"]
    expected_counts = {
        "variables": variable_count,
        "raw_options": raw_total,
        "reduced_options": reduced_total,
        "compact_option_literals": compact_literals,
        "first_forms": len(form_var),
        "final_types": len(type_var),
        "variable_map_sha256": audit.variable_map_digest(form_var, type_var, var_cost),
    }
    for key, value in expected_counts.items():
        if formula_meta[key] != value:
            raise AssertionError(f"formula metadata mismatch for {key}")

    fingerprint = audit.FormulaFingerprint()
    for variable, weight in sorted(var_cost.items()):
        fingerprint.soft(-variable, weight)
    cuts = []
    for index, record in enumerate(reported["cut_certificate"]):
        family_index = int(record["target_index"])
        if not 0 <= family_index < len(families):
            raise AssertionError(f"cut {index} target index out of range")
        family = families[family_index]
        if record["target"] != f"{family.target:09x}":
            raise AssertionError(f"cut {index} target row mismatch")
        clause = [int(variable) for variable in record["clause"]]
        if clause != sorted(set(clause)) or any(not 1 <= variable <= variable_count for variable in clause):
            raise AssertionError(f"cut {index} is not a canonical positive clause")
        hitting = set(clause)
        if not all(
            audit.option_is_hit(family, option_index, hitting)
            for option_index in range(family.option_count)
        ):
            raise AssertionError(f"cut {index} is not implied by target coverage")
        cuts.append(clause)
        fingerprint.clause(clause)
    if len(cuts) != formula_meta["lazy_clauses"]:
        raise AssertionError("cut count mismatch")
    if fingerprint.hexdigest() != formula_meta["sha256"]:
        raise AssertionError("formula SHA-256 mismatch")

    formula = WCNF()
    for clause in cuts:
        formula.append(clause)
    for variable, weight in sorted(var_cost.items()):
        formula.append([-variable], weight=weight)
    interrupted = threading.Event()
    memory_interrupted = threading.Event()
    stop = threading.Event()
    peak = [shared.current_rss_bytes()]
    deadline = time.monotonic() + args.timeout_seconds
    optimum = None
    model = None
    with RC2(formula, solver="g4", adapt=True, exhaust=True, incr=False) as rc2:
        def watch() -> None:
            while not stop.wait(0.10):
                current = shared.current_rss_bytes()
                peak[0] = max(peak[0], current)
                if current > args.memory_mb * 1048576:
                    memory_interrupted.set()
                    interrupted.set()
                    rc2.oracle.interrupt()
                    return
                if time.monotonic() >= deadline:
                    interrupted.set()
                    rc2.oracle.interrupt()
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
            peak[0] = max(peak[0], shared.current_rss_bytes())
    if interrupted.is_set() or model is None or optimum is None:
        status = "UNKNOWN"
    else:
        status = "VERIFIED"
        if optimum != formula_meta["last_master_optimum"]:
            raise AssertionError("replayed RC2 optimum mismatch")
        if optimum <= int(reported["bound"]):
            raise AssertionError("certificate does not exclude its claimed bound")
        if reported["proven_core_lower_bound"] != optimum:
            raise AssertionError("reported lower bound is weaker or inconsistent")

    result = {
        "schema": 1,
        "status": status,
        "certificate": str(args.certificate.resolve()),
        "certificate_sha256": sha256(certificate_bytes).hexdigest(),
        "candidate_sha256": certificate["source_sha256"],
        "verified_cut_count": len(cuts),
        "verified_option_count": reduced_total,
        "replayed_weak_master_optimum": optimum,
        "physical_total_lower_bound": shared.SHELL_GATE + optimum if optimum is not None else None,
        "peak_working_set_mb": peak[0] / 1048576,
        "interrupted": interrupted.is_set(),
        "memory_interrupted": memory_interrupted.is_set(),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(result, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    args.output.write_bytes(encoded)
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)
    return 0 if status == "VERIFIED" else 30


if __name__ == "__main__":
    raise SystemExit(main())
