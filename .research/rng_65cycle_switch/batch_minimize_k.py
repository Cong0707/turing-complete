"""Batch-audit fixed covers for the 66-cycle U32-Switch phase model."""

from __future__ import annotations

import argparse
import gc
import importlib.util
import json
from pathlib import Path
import sys
import time
from typing import Any


HERE = Path(__file__).resolve().parent


def load_solver():
    path = HERE / "solve_fixed_cover.py"
    spec = importlib.util.spec_from_file_location("rng66_fixed", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["rng66_fixed"] = module
    spec.loader.exec_module(module)
    return module


def compact(payload: dict[str, Any], index: int) -> dict[str, Any]:
    return {
        "record_index": index,
        "status": payload["status"],
        "xor_count": payload.get("xor_count"),
        "max_bit_switches": payload.get("max_bit_switches"),
        "bit_switch_count": payload.get("bit_switch_count"),
        "gate": payload.get("gate"),
        "energy": payload.get("energy"),
        "elapsed_seconds": payload.get("elapsed_seconds"),
        "reason_unknown": payload.get("reason_unknown"),
        "T_sha_key": "".join(payload.get("T", ()))[:64],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--xor", type=int, required=True)
    parser.add_argument("--max-switches", type=int, required=True)
    parser.add_argument("--strict-switches", type=int, required=True)
    parser.add_argument("--timeout-ms", type=int, default=30_000)
    parser.add_argument("--record-limit", type=int)
    parser.add_argument("--start-index", type=int, default=0)
    parser.add_argument("--bijective", action="store_true")
    parser.add_argument("--stop-on-strict", action="store_true")
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--certificate", type=Path, required=True)
    args = parser.parse_args()

    solver = load_solver()
    raw_records = solver.read_records(args.input)
    records: list[tuple[int, dict[str, Any]]] = []
    for index, record in enumerate(raw_records):
        try:
            T = solver.matrix(record, "T")
            B = solver.matrix(record, "B")
            C = solver.matrix(record, "C")
            cover = solver.cover_from_record(record, B, C)
        except (KeyError, ValueError, AssertionError):
            continue
        if cover.xor_count == args.xor:
            records.append((index, record))
    records = records[args.start_index :]
    if args.record_limit is not None:
        records = records[: args.record_limit]

    args.checkpoint.parent.mkdir(parents=True, exist_ok=True)
    checkpoint = args.checkpoint.open("w", encoding="utf-8", newline="\n")
    started = time.perf_counter()
    counts = {"sat": 0, "unsat": 0, "unknown": 0}
    best: dict[str, Any] | None = None
    best_index: int | None = None
    processed = 0

    for position, (record_index, record) in enumerate(records, start=1):
        payload = solver.solve_record(
            record,
            max_switches=args.max_switches,
            timeout_ms=args.timeout_ms,
            contract="old-feedback",
            bijective_mapping=args.bijective,
        )
        processed += 1
        status = str(payload["status"])
        counts[status if status in counts else "unknown"] += 1

        if status == "sat":
            # The target-bound solver already supplies a witness.  Tighten k
            # monotonically to obtain the exact minimum for this fixed cover.
            upper = int(payload["bit_switch_count"])
            lower = 0
            minimum_payload = payload
            while lower < upper:
                middle = (lower + upper) // 2
                trial = solver.solve_record(
                    record,
                    max_switches=middle,
                    timeout_ms=args.timeout_ms,
                    contract="old-feedback",
                    bijective_mapping=args.bijective,
                )
                if trial["status"] == "sat":
                    upper = int(trial["bit_switch_count"])
                    minimum_payload = trial
                elif trial["status"] == "unsat":
                    lower = middle + 1
                else:
                    # Unknown cannot establish a minimum.  Preserve the valid
                    # upper witness but mark the certificate accordingly.
                    minimum_payload["minimum_proved"] = False
                    minimum_payload["minimum_blocker"] = trial.get("reason_unknown")
                    break
            else:
                minimum_payload["minimum_proved"] = True
                minimum_payload["proved_unsat_below"] = upper - 1
            payload = minimum_payload
            if best is None or (
                int(payload["bit_switch_count"]), int(payload["gate"])
            ) < (int(best["bit_switch_count"]), int(best["gate"])):
                best = payload
                best_index = record_index
                args.certificate.write_text(
                    json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )

        record_summary = compact(payload, record_index)
        checkpoint.write(json.dumps(record_summary, separators=(",", ":")) + "\n")
        checkpoint.flush()
        if not position % 25 or status == "sat":
            print(
                f"processed={position}/{len(records)} status={status} "
                f"best_k={None if best is None else best['bit_switch_count']}",
                flush=True,
            )
        if best is not None and int(best["bit_switch_count"]) <= args.strict_switches:
            if args.stop_on_strict:
                break
        del payload
        gc.collect()

    checkpoint.close()
    document: dict[str, Any] = {
        "schema": 1,
        "model": "66-cycle fixed-cover U32 Word Switch plus late Bit Switch",
        "input": str(args.input),
        "requested_xor": args.xor,
        "bijective_word_lane_mapping": args.bijective,
        "max_switches": args.max_switches,
        "strict_switches": args.strict_switches,
        "selected_record_count": len(records),
        "processed_record_count": processed,
        "status_counts": counts,
        "elapsed_seconds": round(time.perf_counter() - started, 6),
        "status": (
            "strict_candidate"
            if best is not None and int(best["bit_switch_count"]) <= args.strict_switches
            else "tie_or_frontier"
            if best is not None
            else "no_sat_within_bound"
        ),
    }
    if best is not None:
        document["best_record_index"] = best_index
        document["best"] = {
            key: best.get(key)
            for key in (
                "xor_count", "bit_switch_count", "gate", "delay", "cycles",
                "energy", "minimum_proved", "proved_unsat_below",
                "offline_verification",
            )
        }
    args.output.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(document, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
