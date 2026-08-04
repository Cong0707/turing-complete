"""Independently audit the downloaded g18/o2/s8 position sweep.

This checker treats every missing payload, watchdog exit, and nonterminal
status as UNKNOWN.  It never promotes partial coverage to UNSAT.
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime
from hashlib import sha256
import itertools
import json
from pathlib import Path
import re


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DEFAULT_SWEEP = HERE / "o2s8_position_sweep_20260804"
DEFAULT_RUNNER = HERE / "run_o2s8_position_sweep.sh"
DEFAULT_WORKER = (
    ROOT / ".research/byte_adder_phase_shortcut_restart/physical_exact.py"
)
EXPECTED_WORKER_SHA256 = (
    "c48a96e55d8c5076418999f5fa5ee95e9f8207c03f138cd4bccf48908a69c071"
)
SKIPPED_PAIRS = {
    (0, 1),
    (2, 3),
    (2, 4),
    (3, 4),
    (3, 5),
    (4, 5),
    (4, 6),
    (5, 6),
    (5, 7),
    (6, 7),
}
ALL_PAIRS = set(itertools.combinations(range(10), 2))
EXPECTED_PAIRS = ALL_PAIRS - SKIPPED_PAIRS
ORDINARY_KINDS = ("NOT", "AND", "OR", "NAND", "NOR")
EXPECTED_DEPENDENCIES = {
    ".research/byte_adder_ling_theory_agent/exact_free_ling_pair_sat.py": (
        "49bb2640e1cb08c6e2b9ac412a8cf56c058f27966e1dd799d1d813c8f1821017"
    ),
    ".research/byte_adder_boolean_superopt_agent/exact_adder_block_sat.py": (
        "f320ed3029b949185acd13b5462b659502a970406d1bf5047713279e152f56de"
    ),
    ".research/rng_468_joint_macro/joint_parity_cnf.py": (
        "a565201bf7e99f6ded6732e70d883cd9a90e5da2e42d72171f11952bb3566ca4"
    ),
}


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def pair_key(pair: tuple[int, int]) -> str:
    return f"p{pair[0]}_{pair[1]}"


def fixed_for_pair(pair: tuple[int, int]) -> tuple[str, ...]:
    ordinary = set(pair)
    return tuple("*" if slot in ordinary else "SWITCH" for slot in range(10))


def parse_timestamp(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def parse_meta(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        result[key] = value
    return result


def parse_progress(path: Path) -> tuple[dict[str, tuple[str, int, str]], list[str]]:
    records: dict[str, tuple[str, int, str]] = {}
    errors: list[str] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        fields = line.split("\t")
        if len(fields) != 4:
            errors.append(f"progress line {number}: expected 4 fields")
            continue
        key, status, exit_text, classification = fields
        try:
            exit_code = int(exit_text)
        except ValueError:
            errors.append(f"progress line {number}: invalid exit code")
            continue
        if key in records:
            errors.append(f"progress line {number}: duplicate key {key}")
        records[key] = (status, exit_code, classification)
    return records, errors


def runner_checks(text: str) -> tuple[dict[str, bool], set[tuple[int, int]]]:
    runner_skips = {
        (int(first), int(second))
        for first, second in re.findall(r"\[(\d+),(\d+)\]=1", text)
    }
    checks = {
        "skip_set_exact": runner_skips == SKIPPED_PAIRS,
        "position_loop_exact": (
            "for first in $(seq 0 8); do" in text
            and "for second in $(seq $((first + 1)) 9); do" in text
        ),
        "model_exact": (
            "--domain s34567c8_leaf" in text
            and "--outputs S5,S6,S7,C8" in text
            and "--gate-bound 18 --max-delay 5" in text
            and "--components 10 --switches 8 --xors 0" in text
        ),
        "solver_exact": "--solver cadical195 --timeout 0" in text,
        "watchdog_present": (
            'timeout --signal=TERM --kill-after=60s "${WATCHDOG}s"' in text
        ),
        "timeout_classification": (
            "if [[ $rc -eq 124 || $rc -eq 137 ]]; then class=watchdog_timeout; fi"
            in text
        ),
        "missing_is_not_unsat": (
            "status=missing" in text and "timeout or a missing canonical JSON is UNKNOWN" in text
        ),
        "resume_run_marker": (
            'if [[ -f $OUT/runs/${key}.run.json ]]; then continue; fi' in text
        ),
        "stop_on_sat_marker": 'if [[ -f $OUT/SAT_FOUND ]]; then break; fi' in text,
        "atomic_run_marker": 'mv "$run.tmp" "$run"' in text,
        "atomic_sat_marker": 'mv "$OUT/SAT_FOUND.tmp" "$OUT/SAT_FOUND"' in text,
        "summary_pair_count": '"expected_new_pairs": 35' in text,
    }
    return checks, runner_skips


def payload_checks(payload: dict[str, object], fixed: tuple[str, ...]) -> dict[str, bool]:
    shard = payload.get("shard")
    if not isinstance(shard, dict):
        shard = {}
    return {
        "schema": payload.get("schema") == "exact-fast-negative-physical-shard-v2",
        "status_unsat": payload.get("status") == "unsat",
        "domain": payload.get("domain") == "s34567c8_leaf",
        "rows": payload.get("rows") == 486,
        "outputs": tuple(payload.get("output_names", ())) == ("S5", "S6", "S7", "C8"),
        "gate_bound": payload.get("gate_bound") == 18,
        "max_delay": payload.get("max_delay") == 5,
        "components": payload.get("components") == 10,
        "ordinary": payload.get("ordinary") == 2,
        "switches": payload.get("exact_switches") == 8,
        "xors": payload.get("exact_xors") == 0,
        "fixed_kinds": tuple(payload.get("fixed_kinds", ())) == fixed,
        "solver": payload.get("solver") == "cadical195",
        "physical_nets": payload.get("physical_nets") is True,
        "public_outputs_driven": payload.get("public_outputs_must_be_driven") is True,
        "split_slots": shard.get("split_slots") == 1,
        "shard_count": shard.get("shard_count") == 1,
        "shard_index": shard.get("shard_index") == 0,
        "timer_errors": payload.get("timer_errors") == [],
        "dependencies": payload.get("dependency_sha256") == EXPECTED_DEPENDENCIES,
    }


def audit(sweep: Path, runner: Path, worker: Path) -> dict[str, object]:
    summary_path = sweep / "summary.json"
    meta_path = sweep / "sweep.meta"
    progress_path = sweep / "progress.tsv"
    runs_directory = sweep / "runs"
    results_directory = sweep / "results"
    logs_directory = sweep / "logs"

    errors: list[str] = []
    for required in (summary_path, meta_path, progress_path, runner, worker):
        if not required.is_file():
            errors.append(f"required file missing: {required}")
    if errors:
        return {
            "schema": "byte-adder-s567c8-g18-o2s8-position-sweep-audit-v1",
            "status": "invalid",
            "errors": errors,
        }

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    runner_text = runner.read_text(encoding="utf-8")
    runner_static, runner_skips = runner_checks(runner_text)
    for check, passed in runner_static.items():
        if not passed:
            errors.append(f"runner static check failed: {check}")
    if digest(worker) != EXPECTED_WORKER_SHA256:
        errors.append("worker SHA256 mismatch")
    dependency_local = {
        relative: (digest(ROOT / relative) if (ROOT / relative).is_file() else None)
        for relative in EXPECTED_DEPENDENCIES
    }
    if dependency_local != EXPECTED_DEPENDENCIES:
        errors.append("local dependency SHA256 mismatch")

    meta = parse_meta(meta_path)
    meta_checks = {
        "ordinary_position_pairs": meta.get("ordinary_position_pairs") == "35",
        "watchdog": meta.get("watchdog") == "900",
        "nice": meta.get("nice") == "5",
        "max_jobs_positive": meta.get("max_jobs", "").isdigit()
        and int(meta["max_jobs"]) > 0,
        "as_kib_positive": meta.get("as_kib", "").isdigit()
        and int(meta["as_kib"]) > 0,
    }
    for check, passed in meta_checks.items():
        if not passed:
            errors.append(f"meta check failed: {check}")

    progress, progress_errors = parse_progress(progress_path)
    errors.extend(progress_errors)
    records_by_pair: dict[tuple[int, int], dict[str, object]] = {}
    summary_records = summary.get("records")
    if not isinstance(summary_records, list):
        summary_records = []
        errors.append("summary records is not a list")
    for index, record in enumerate(summary_records):
        if not isinstance(record, dict):
            errors.append(f"summary record {index}: not an object")
            continue
        positions = record.get("ordinary_positions")
        if (
            not isinstance(positions, list)
            or len(positions) != 2
            or not all(isinstance(value, int) for value in positions)
        ):
            errors.append(f"summary record {index}: invalid ordinary_positions")
            continue
        pair = (positions[0], positions[1])
        if pair in records_by_pair:
            errors.append(f"duplicate summary pair: {pair}")
        records_by_pair[pair] = record

    if set(records_by_pair) != EXPECTED_PAIRS:
        errors.append(
            "summary pair set mismatch: "
            f"missing={sorted(EXPECTED_PAIRS - set(records_by_pair))}, "
            f"extra={sorted(set(records_by_pair) - EXPECTED_PAIRS)}"
        )

    status_counts: Counter[str] = Counter()
    exit_counts: Counter[int] = Counter()
    classification_counts: Counter[str] = Counter()
    as_limit_counts: Counter[int] = Counter()
    unsat_pairs: list[list[int]] = []
    unknown_pairs: list[list[int]] = []
    sat_pairs: list[list[int]] = []
    record_audits: list[dict[str, object]] = []
    solve_seconds: list[float] = []
    elapsed_seconds: list[float] = []

    for pair in sorted(records_by_pair):
        record = records_by_pair[pair]
        key = pair_key(pair)
        fixed = fixed_for_pair(pair)
        run_path = runs_directory / f"{key}.run.json"
        result_path = results_directory / f"{key}.json"
        log_path = logs_directory / f"{key}.log"
        checks: dict[str, bool] = {
            "pair_expected": pair in EXPECTED_PAIRS,
            "fixed_kinds": tuple(str(record.get("fixed_kinds", "")).split(",")) == fixed,
            "watchdog": record.get("watchdog_seconds") == 900,
            "nice": record.get("nice") == 5,
            "as_limit_positive": isinstance(record.get("as_limit_kib"), int)
            and int(record["as_limit_kib"]) > 0,
            "run_basename": Path(str(record.get("run", ""))).name == run_path.name,
            "result_basename": Path(str(record.get("result", ""))).name == result_path.name,
            "log_basename": Path(str(record.get("log", ""))).name == log_path.name,
            "run_exists": run_path.is_file(),
            "log_exists": log_path.is_file(),
        }
        start = parse_timestamp(record.get("start_utc"))
        end = parse_timestamp(record.get("end_utc"))
        checks["timestamps"] = start is not None and end is not None and end >= start
        elapsed = (end - start).total_seconds() if start is not None and end is not None else None
        if elapsed is not None:
            elapsed_seconds.append(elapsed)

        if run_path.is_file():
            try:
                run_payload = json.loads(run_path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                run_payload = {}
                checks["run_json"] = False
            else:
                checks["run_json"] = True
                checks["summary_run_equal"] = all(
                    record.get(field) == value for field, value in run_payload.items()
                )

        local_log_sha = digest(log_path) if log_path.is_file() else None
        checks["log_sha256"] = local_log_sha == record.get("log_sha256")
        status = str(record.get("status"))
        classification = str(record.get("classification"))
        exit_code = record.get("exit_code")
        as_limit = record.get("as_limit_kib")
        status_counts[status] += 1
        classification_counts[classification] += 1
        if isinstance(exit_code, int):
            exit_counts[exit_code] += 1
        if isinstance(as_limit, int):
            as_limit_counts[as_limit] += 1

        if status == "unsat":
            unsat_pairs.append(list(pair))
            checks.update(
                {
                    "solver_exit": classification == "solver_exit",
                    "exit_zero": exit_code == 0,
                    "result_exists": result_path.is_file(),
                    "result_sha256": result_path.is_file()
                    and digest(result_path) == record.get("result_sha256"),
                }
            )
            if result_path.is_file():
                try:
                    payload = json.loads(result_path.read_text(encoding="utf-8"))
                except (OSError, ValueError):
                    checks["payload_json"] = False
                else:
                    checks["payload_json"] = True
                    for name, passed in payload_checks(payload, fixed).items():
                        checks[f"payload_{name}"] = passed
                    seconds = payload.get("solve_seconds")
                    if isinstance(seconds, (int, float)):
                        solve_seconds.append(float(seconds))
                    if log_path.is_file() and log_path.stat().st_size:
                        try:
                            log_payload = json.loads(log_path.read_text(encoding="utf-8"))
                        except (OSError, ValueError):
                            checks["log_json"] = False
                        else:
                            checks["log_json"] = True
                            checks["log_payload_equal"] = all(
                                log_payload.get(field) == value
                                for field, value in payload.items()
                            )
                            checks["log_result_sha256"] = (
                                log_payload.get("sha256") == record.get("result_sha256")
                            )
        elif status == "sat":
            sat_pairs.append(list(pair))
            checks["sat_not_expected_in_download"] = False
        else:
            unknown_pairs.append(list(pair))
            checks.update(
                {
                    "status_missing": status == "missing",
                    "watchdog_class": classification == "watchdog_timeout",
                    "timeout_exit": exit_code in {124, 137},
                    "result_absent": not result_path.exists(),
                    "result_sha256_null": record.get("result_sha256") is None,
                }
            )

        expected_progress = (status, exit_code, classification)
        checks["progress_equal"] = progress.get(key) == expected_progress
        for check, passed in checks.items():
            if not passed:
                errors.append(f"{key}: {check} failed")
        record_audits.append(
            {
                "pair": list(pair),
                "key": key,
                "classification": (
                    "terminal-unsat" if status == "unsat" else "unknown-incomplete"
                ),
                "status": status,
                "exit_code": exit_code,
                "runner_classification": classification,
                "elapsed_seconds_from_utc": elapsed,
                "as_limit_kib": as_limit,
                "result_sha256": record.get("result_sha256"),
                "log_sha256": record.get("log_sha256"),
                "checks": checks,
            }
        )

    expected_keys = {pair_key(pair) for pair in EXPECTED_PAIRS}
    expected_result_names = {
        f"{pair_key(tuple(record['pair']))}.json"
        for record in record_audits
        if record["classification"] == "terminal-unsat"
    }
    actual_run_names = {path.name for path in runs_directory.glob("*.run.json")}
    actual_result_names = {path.name for path in results_directory.glob("*.json")}
    actual_log_names = {path.name for path in logs_directory.glob("*.log")}
    directory_checks = {
        "runs_exact": actual_run_names == {f"{key}.run.json" for key in expected_keys},
        "results_exact": actual_result_names == expected_result_names,
        "logs_exact": actual_log_names == {f"{key}.log" for key in expected_keys},
        "progress_exact": set(progress) == expected_keys,
    }
    for check, passed in directory_checks.items():
        if not passed:
            errors.append(f"directory check failed: {check}")

    recomputed_status_counts = dict(sorted(status_counts.items()))
    summary_checks = {
        "schema": summary.get("schema")
        == "byte-adder-s567c8-g18-o2s8-position-sweep-v1",
        "expected_new_pairs": summary.get("expected_new_pairs") == len(EXPECTED_PAIRS),
        "completed_pairs": summary.get("completed_pairs") == len(records_by_pair),
        "status_counts": summary.get("status_counts") == recomputed_status_counts,
        "sat_found": summary.get("sat_found") == sat_pairs,
        "observed_20_unsat": len(unsat_pairs) == 20,
        "observed_15_unknown": len(unknown_pairs) == 15,
    }
    for check, passed in summary_checks.items():
        if not passed:
            errors.append(f"summary check failed: {check}")

    if errors:
        status = "invalid"
    elif sat_pairs:
        status = "sat-witnesses"
    elif unknown_pairs:
        status = "incomplete"
    elif len(unsat_pairs) == len(EXPECTED_PAIRS):
        status = "unsat-covered"
    else:
        status = "incomplete"

    return {
        "schema": "byte-adder-s567c8-g18-o2s8-position-sweep-audit-v1",
        "status": status,
        "classification_rule": "missing/watchdog/nonterminal => UNKNOWN/incomplete, never UNSAT",
        "scope": {
            "domain": "s34567c8_leaf",
            "rows": 486,
            "outputs": ["S5", "S6", "S7", "C8"],
            "gate_bound": 18,
            "max_delay": 5,
            "components": 10,
            "ordinary": 2,
            "switches": 8,
            "xors": 0,
            "ordinary_kind_alphabet": list(ORDINARY_KINDS),
            "ordered_kind_assignments_per_position": 25,
        },
        "pair_partition": {
            "all_pairs": len(ALL_PAIRS),
            "skipped_prior_pairs": len(SKIPPED_PAIRS),
            "skipped_pairs": [list(pair) for pair in sorted(SKIPPED_PAIRS)],
            "expected_new_pairs": len(EXPECTED_PAIRS),
            "seen_new_pairs": len(records_by_pair),
            "runner_skip_pairs": [list(pair) for pair in sorted(runner_skips)],
            "overlap_count": len(set(records_by_pair) & SKIPPED_PAIRS),
            "missing_pair_count": len(EXPECTED_PAIRS - set(records_by_pair)),
            "extra_pair_count": len(set(records_by_pair) - EXPECTED_PAIRS),
        },
        "coverage": {
            "terminal_unsat_positions": len(unsat_pairs),
            "unknown_positions": len(unknown_pairs),
            "sat_positions": len(sat_pairs),
            "terminal_unsat_fixed_kind_networks": len(unsat_pairs) * 25,
            "unknown_fixed_kind_networks": len(unknown_pairs) * 25,
            "unsat_pairs": unsat_pairs,
            "unknown_pairs": unknown_pairs,
            "sat_pairs": sat_pairs,
        },
        "state_counts": {
            "status": recomputed_status_counts,
            "exit_code": {str(key): value for key, value in sorted(exit_counts.items())},
            "classification": dict(sorted(classification_counts.items())),
            "as_limit_kib": {str(key): value for key, value in sorted(as_limit_counts.items())},
        },
        "timing": {
            "solve_seconds_min": min(solve_seconds) if solve_seconds else None,
            "solve_seconds_max": max(solve_seconds) if solve_seconds else None,
            "solve_seconds_sum": sum(solve_seconds),
            "record_elapsed_seconds_min": min(elapsed_seconds) if elapsed_seconds else None,
            "record_elapsed_seconds_max": max(elapsed_seconds) if elapsed_seconds else None,
            "record_elapsed_seconds_sum": sum(elapsed_seconds),
        },
        "artifacts": {
            "sweep": str(sweep),
            "summary": str(summary_path),
            "summary_sha256": digest(summary_path),
            "runner": str(runner),
            "runner_sha256": digest(runner),
            "worker": str(worker),
            "worker_sha256": digest(worker),
            "progress_sha256": digest(progress_path),
            "meta_sha256": digest(meta_path),
            "dependency_sha256": dependency_local,
        },
        "integrity": {
            "runner_static": runner_static,
            "meta": meta_checks,
            "summary": summary_checks,
            "directories": directory_checks,
            "mismatch_count": len(errors),
            "errors": errors,
        },
        "records": record_audits,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("sweep", type=Path, nargs="?", default=DEFAULT_SWEEP)
    parser.add_argument("--runner", type=Path, default=DEFAULT_RUNNER)
    parser.add_argument("--worker", type=Path, default=DEFAULT_WORKER)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = audit(args.sweep.resolve(), args.runner.resolve(), args.worker.resolve())
    encoded = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8", newline="\n")
    print(encoded, end="")
    return 0 if payload["status"] in {"sat-witnesses", "unsat-covered"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
