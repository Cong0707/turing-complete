#!/usr/bin/env python3
"""Exactly solve the 61 delay-8-safe rows of the over=3 joint matrix.

The three oversized rows are deliberately excluded before option generation.
This avoids the exponential support universe that made the full model exceed
the memory budget.  A memory guard terminates the process before 900 MiB.
"""

from __future__ import annotations

import argparse
from collections import Counter
import ctypes
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import threading
import time


ROOT = Path(__file__).resolve().parents[2]
ENGINE_PATH = ROOT / ".research" / "rng65_joint_basis_agent" / "synthesize_mixed_switch_dag.py"


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


def working_set_bytes() -> int:
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    psapi = ctypes.WinDLL("psapi", use_last_error=True)
    kernel32.GetCurrentProcess.argtypes = []
    kernel32.GetCurrentProcess.restype = ctypes.c_void_p
    psapi.GetProcessMemoryInfo.argtypes = [
        ctypes.c_void_p,
        ctypes.POINTER(ProcessMemoryCounters),
        ctypes.c_ulong,
    ]
    psapi.GetProcessMemoryInfo.restype = ctypes.c_int
    counters = ProcessMemoryCounters()
    counters.cb = ctypes.sizeof(counters)
    process = kernel32.GetCurrentProcess()
    if not psapi.GetProcessMemoryInfo(process, ctypes.byref(counters), counters.cb):
        raise ctypes.WinError(ctypes.get_last_error())
    return int(counters.WorkingSetSize)


def memory_guard(limit_mb: int, marker: Path) -> tuple[threading.Event, list[int]]:
    stopped = threading.Event()
    peak = [working_set_bytes()]

    def monitor() -> None:
        while not stopped.wait(0.05):
            current = working_set_bytes()
            peak[0] = max(peak[0], current)
            if current > limit_mb * 1024 * 1024:
                marker.write_text(
                    json.dumps(
                        {
                            "status": "memory-limit",
                            "limit_mb": limit_mb,
                            "working_set_bytes": current,
                            "peak_working_set_bytes": peak[0],
                        },
                        indent=2,
                    )
                    + "\n",
                    encoding="ascii",
                )
                os._exit(99)

    threading.Thread(target=monitor, name="memory-guard", daemon=True).start()
    return stopped, peak


def load_engine():
    spec = importlib.util.spec_from_file_location("rng_mixed_switch_engine", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load mixed Switch DAG engine")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_good_targets(path: Path) -> tuple[tuple[int, ...], tuple[int, ...]]:
    document = json.loads(path.read_text(encoding="utf-8"))
    raw_targets = document.get("targets")
    metrics = document.get("metrics")
    if not isinstance(raw_targets, list) or len(raw_targets) != 64:
        raise ValueError("certificate must contain 64 targets")
    if not isinstance(metrics, list) or len(metrics) != 64:
        raise ValueError("certificate must contain 64 row metrics")
    targets = tuple(int(str(value), 16) for value in raw_targets)
    selected = tuple(
        index
        for index, metric in enumerate(metrics)
        if isinstance(metric, dict) and not bool(metric.get("over_delay8_xor"))
    )
    if len(selected) != 61:
        raise AssertionError(f"expected 61 good rows, got {len(selected)}")
    return tuple(targets[index] for index in selected), selected


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--certificate", type=Path, required=True)
    parser.add_argument("--solver", default="g4")
    parser.add_argument("--memory-limit-mb", type=int, default=900)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    marker = args.output.with_suffix(args.output.suffix + ".memory.json")
    if marker.exists():
        marker.unlink()
    stopped, peak = memory_guard(args.memory_limit_mb, marker)
    engine = load_engine()
    targets, selected_indices = load_good_targets(args.certificate)

    build_started = time.perf_counter()
    universe, variants, options = engine.build_options(targets)
    build_seconds = time.perf_counter() - build_started
    print(
        f"built universe={len(universe)} variants={sum(map(len, variants.values()))} "
        f"options={len(options)} seconds={build_seconds:.3f}",
        flush=True,
    )
    optimum, selected, stats = engine.solve(targets, options, solver_name=args.solver)
    dag, outputs = engine.select_replay_dag(targets, selected)
    gate = sum(engine.GATE_COST[option.kind] for option in dag)
    if gate > optimum:
        raise AssertionError("trimmed DAG exceeds MaxSAT optimum")
    peak[0] = max(peak[0], working_set_bytes())
    stopped.set()

    payload = {
        "schema": 1,
        "status": "sat-optimum-restricted-family",
        "scope": (
            "61 mixed-Kraft-safe targets only; exact cancellation-free shared "
            "XOR2/Switch-XOR3 family; the three oversized rows are excluded"
        ),
        "certificate": str(args.certificate),
        "certificate_sha256": hashlib.sha256(args.certificate.read_bytes()).hexdigest(),
        "engine": str(ENGINE_PATH.relative_to(ROOT)),
        "engine_sha256": hashlib.sha256(ENGINE_PATH.read_bytes()).hexdigest(),
        "selected_target_indices": selected_indices,
        "excluded_target_indices": sorted(set(range(64)) - set(selected_indices)),
        "search": {
            "support_universe": len(universe),
            "variant_count": sum(map(len, variants.values())),
            "option_count": len(options),
            "build_seconds": build_seconds,
            **stats,
            "raw_optimum_gate": optimum,
            "trimmed_gate": gate,
            "memory_limit_mb": args.memory_limit_mb,
            "peak_working_set_bytes": peak[0],
        },
        "logic_gate": gate,
        "budget_292_already_exceeded": gate > 292,
        "counts": dict(sorted(Counter(option.kind for option in dag).items())),
        "maximum_arrival": max(output.arrival for output in outputs),
        "outputs": [
            {
                "mask": f"{output.mask:016x}",
                "arrival": output.arrival,
                "drive": output.drive,
            }
            for output in outputs
        ],
        "dag": [engine.option_json(index, option) for index, option in enumerate(dag)],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="ascii")
    print(
        json.dumps(
            {
                "status": payload["status"],
                "logic_gate": gate,
                "counts": payload["counts"],
                "maximum_arrival": payload["maximum_arrival"],
                "peak_working_set_bytes": peak[0],
                "budget_292_already_exceeded": payload["budget_292_already_exceeded"],
            },
            indent=2,
        ),
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
