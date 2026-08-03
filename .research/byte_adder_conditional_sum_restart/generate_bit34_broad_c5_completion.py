"""Generate a completion manifest for the frozen broad C5 remote sweep."""

from __future__ import annotations

import argparse
from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
import statistics

import bit34_broad_c5_normal_form as normal_form


HERE = Path(__file__).resolve().parent
SPEC = HERE / "bit34_d7_g13_broad_c5_normal_form_workers3.json"
PREPARED_MANIFEST = (
    HERE / "bit34_d7_g13_broad_c5_normal_form_workers3_manifest.json"
)
REMOTE_VALIDATE = HERE / "bit34_d7_g13_broad_c5_remote_validate.json"
REMOTE_SUMMARY = (
    HERE / "bit34-d7-g13-broad-c5-normal-form-workers3-summary.json"
)
COMPLETE_LEDGER = HERE / "bit34_d7_g13_broad_c5_normal_form_complete.json"
TRANSPORT_VERIFY = HERE / "bit34_d7_g13_broad_c5_remote_transport_verify.json"
RESULT_DIRECTORY = (
    HERE / "remote_results" / "bit34_d7_g13_broad_c5_normal_form"
)
POSITIVE = HERE / "bit34_broad_c5_positive_g14.json"
POSITIVE_INDEPENDENT = (
    HERE / "bit34_broad_c5_positive_g14_independent_verify.json"
)
SMOKE = HERE / "bit34_broad_c5_smoke_n00_n02_complete.json"
COVERAGE_AUDIT = (
    HERE / "2026-08-04-bit34-broad-C5正常形独立静态覆盖审计.md"
)
TERMINAL_AUDIT = (
    HERE / "2026-08-04-bit34-broad-C5远端230片终态独立审计.md"
)
OUTPUT = HERE / "bit34_d7_g13_broad_c5_remote_completion_manifest.json"


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_sha256(value: object) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return sha256(encoded).hexdigest()


def record(path: Path) -> dict[str, object]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": file_sha256(path),
    }


def load_object(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} does not contain a JSON object")
    return value


def atomic_json(path: Path, payload: object) -> str:
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode(
        "utf-8"
    )
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(encoded)
    temporary.replace(path)
    return sha256(encoded).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runner-pid", type=int, default=3997065)
    args = parser.parse_args()

    required = (
        SPEC,
        PREPARED_MANIFEST,
        REMOTE_VALIDATE,
        REMOTE_SUMMARY,
        COMPLETE_LEDGER,
        TRANSPORT_VERIFY,
        POSITIVE,
        POSITIVE_INDEPENDENT,
        SMOKE,
        COVERAGE_AUDIT,
        TERMINAL_AUDIT,
    )
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise RuntimeError(f"completion evidence missing: {missing}")

    spec = load_object(SPEC)
    remote_validate = load_object(REMOTE_VALIDATE)
    remote_summary = load_object(REMOTE_SUMMARY)
    complete = load_object(COMPLETE_LEDGER)
    transport = load_object(TRANSPORT_VERIFY)
    positive = load_object(POSITIVE)
    positive_independent = load_object(POSITIVE_INDEPENDENT)
    smoke = load_object(SMOKE)

    assertions = {
        "remote_validate_ok": remote_validate.get("ok") is True,
        "remote_validate_230": remote_validate.get("shards") == 230,
        "remote_summary_finished": remote_summary.get("finished") is True,
        "remote_summary_not_stopped_on_sat": (
            remote_summary.get("stopped_on_sat") is False
        ),
        "remote_summary_terminal_230": (
            remote_summary.get("terminal_result_count") == 230
        ),
        "remote_summary_total_230": remote_summary.get("total_value_count") == 230,
        "remote_summary_all_unsat": all(
            item.get("status") == "unsat"
            for item in remote_summary.get("results", [])
        ),
        "complete_coverage": complete.get("coverage_complete") is True,
        "complete_all_unsat": complete.get("all_unsat") is True,
        "complete_no_unknown": complete.get("unknown_shards") == [],
        "complete_no_errors": complete.get("errors") == [],
        "transport_ok": transport.get("ok") is True,
        "transport_230": transport.get("verified_results") == 230,
        "positive_g14_passed": positive.get("passed") is True,
        "positive_g14_gate_14": positive.get("actual_gate") == 14,
        "positive_independent_ok": (
            positive_independent.get("verification", {}).get("ok") is True
        ),
        "smoke_complete": smoke.get("coverage_complete") is True,
        "smoke_all_unsat": smoke.get("all_unsat") is True,
        "spec_sha_matches_summary": remote_summary.get("spec_sha256")
        == file_sha256(SPEC),
        "summary_sha_matches_transport": transport.get("summary_sha256")
        == file_sha256(REMOTE_SUMMARY),
    }
    failed = sorted(key for key, passed in assertions.items() if not passed)
    if failed:
        raise RuntimeError(f"completion assertions failed: {failed}")

    result_paths = sorted(RESULT_DIRECTORY.glob("*.json"))
    if len(result_paths) != 230:
        raise RuntimeError(f"expected 230 result artifacts, got {len(result_paths)}")
    result_hashes = [
        {"name": path.stem, "sha256": file_sha256(path)} for path in result_paths
    ]
    solve_seconds = [
        float(item["solve_seconds"]) for item in complete.get("results", [])
    ]
    started_at = min(
        item["started_at"] for item in remote_summary.get("results", [])
    )
    finished_at = max(
        item["finished_at"] for item in remote_summary.get("results", [])
    )
    wall_seconds = (
        datetime.fromisoformat(finished_at) - datetime.fromisoformat(started_at)
    ).total_seconds()

    payload = {
        "schema": "tc-byte-adder-bit34-broad-c5-completion-manifest-v1",
        "status": "complete-all-unsat",
        "scope": {
            "profile": "d7_80",
            "weighted_gate_bound": 13,
            "component_domain": list(range(14)),
            "switches": None,
            "xors": None,
            "output_deadlines": [5, 7, 4],
            "boundary_rows": 48,
            "physical_nets": True,
        },
        "remote": {
            "host": "root@new.xem8k5.top",
            "working_directory": (
                "/root/congProjects/turing-complete-works/.research/"
                "byte_adder_conditional_sum_restart"
            ),
            "runner_pid_observed": args.runner_pid,
            "workers": spec.get("workers"),
            "memory_mb_per_process": spec.get("memory_mb_per_process"),
            "nice": spec.get("nice"),
            "started_at": started_at,
            "finished_at": finished_at,
            "wall_seconds": wall_seconds,
            "finished": True,
            "stopped_on_sat": False,
        },
        "domain": {
            "shards": 230,
            "component_shard_counts": normal_form.component_shard_counts(13),
            "result_set_sha256": canonical_sha256(result_hashes),
        },
        "solver_statistics": {
            "solver": "cadical195",
            "terminal_unsat": 230,
            "terminal_sat": 0,
            "unknown": 0,
            "solve_seconds_sum": sum(solve_seconds),
            "solve_seconds_min": min(solve_seconds),
            "solve_seconds_median": statistics.median(solve_seconds),
            "solve_seconds_max": max(solve_seconds),
        },
        "assertions": assertions,
        "failed_assertions": failed,
        "evidence": {
            "spec": record(SPEC),
            "prepared_manifest": record(PREPARED_MANIFEST),
            "remote_validate": record(REMOTE_VALIDATE),
            "remote_summary": record(REMOTE_SUMMARY),
            "complete_ledger": record(COMPLETE_LEDGER),
            "transport_verify": record(TRANSPORT_VERIFY),
            "positive_g14": record(POSITIVE),
            "positive_g14_independent": record(POSITIVE_INDEPENDENT),
            "smoke": record(SMOKE),
            "coverage_audit": record(COVERAGE_AUDIT),
            "terminal_audit": record(TERMINAL_AUDIT),
            "generator": record(Path(__file__).resolve()),
        },
        "conclusion": {
            "weighted_gate_le_13": "unsat",
            "known_weighted_gate_14": "sat and independently replayed",
            "strict_c3_bit34_residual_optimum": 14,
            "projected_79_7_by_replacing_only_this_residual": "impossible",
            "scope_limit": (
                "This is a local paid-source bit3:4 residual optimum, not a "
                "global lower bound over every Byte Adder architecture."
            ),
        },
    }
    output_sha256 = atomic_json(OUTPUT, payload)
    print(
        json.dumps(
            {
                "status": payload["status"],
                "shards": payload["domain"]["shards"],
                "unknown": payload["solver_statistics"]["unknown"],
                "wall_seconds": wall_seconds,
                "output": str(OUTPUT),
                "output_sha256": output_sha256,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
