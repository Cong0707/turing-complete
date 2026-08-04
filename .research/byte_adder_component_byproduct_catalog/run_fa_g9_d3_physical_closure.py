"""Run and summarize the exact FullAdder gate<=9, delay<=3 closure.

The driver enumerates both reviewed primary-output policies, paid physical
component counts 1..9, and exact useful-normalizer counts 0..4.  Each shard
is solved by ``exact_pretarget_physical.py`` in a fresh process.  Outputs and
the final manifest stay below this research directory.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import time


HERE = Path(__file__).resolve().parent
SOLVER = HERE / "exact_pretarget_physical.py"
DEFAULT_OUTPUT = HERE / "fa_g9_d3_physical_closure"
POLICIES = (("strict", False), ("zfalse", True))


def _digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _case_path(output_dir: Path, policy: str, paid: int, normalizers: int) -> Path:
    return output_dir / f"fa_g9_d3_{policy}_p{paid}_n{normalizers}.json"


def _validate_case(
    path: Path,
    *,
    policy: str,
    paid: int,
    normalizers: int,
) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    expected = {
        "schema": "tc-pretarget-exact-physical-v1",
        "target": "full-adder",
        "gate_bound": 9,
        "max_delay": 3,
        "components": paid + normalizers,
        "exact_normalizers": normalizers,
        "allow_z_false": policy == "zfalse",
        "physical_nets": True,
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            raise RuntimeError(
                f"case parameter mismatch in {path.name}: "
                f"{key}={payload.get(key)!r}, expected {value!r}"
            )
    return payload


def _run_case(
    python: Path,
    output_dir: Path,
    policy: str,
    allow_z_false: bool,
    paid: int,
    normalizers: int,
    timeout: float,
    reuse: bool,
) -> dict[str, object]:
    path = _case_path(output_dir, policy, paid, normalizers)
    if reuse and path.is_file():
        payload = _validate_case(
            path,
            policy=policy,
            paid=paid,
            normalizers=normalizers,
        )
        if payload.get("status") != "unknown":
            return payload

    command = [
        str(python),
        str(SOLVER),
        "--target",
        "full-adder",
        "--gate-bound",
        "9",
        "--max-delay",
        "3",
        "--components",
        str(paid + normalizers),
        "--normalizers",
        str(normalizers),
        "--timeout",
        str(timeout),
        "--output",
        str(path),
    ]
    if allow_z_false:
        command.append("--allow-z-false")
    completed = subprocess.run(
        command,
        cwd=HERE.parents[1],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
        errors="replace",
        timeout=timeout + 120.0,
    )
    if completed.returncode not in {0, 2}:
        raise RuntimeError(
            f"solver failed for {path.name} with {completed.returncode}: "
            f"{completed.stderr[-2000:]}"
        )
    return _validate_case(
        path,
        policy=policy,
        paid=paid,
        normalizers=normalizers,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--python", type=Path, default=Path(sys.executable))
    parser.add_argument("--workers", type=int, default=20)
    parser.add_argument("--timeout", type=float, default=1800.0)
    parser.add_argument("--no-reuse", action="store_true")
    args = parser.parse_args()
    if not 1 <= args.workers <= 64:
        parser.error("--workers must be in 1..64")
    if args.timeout <= 0:
        parser.error("--timeout must be positive")

    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    jobs = [
        (policy, allow_z_false, paid, normalizers)
        for policy, allow_z_false in POLICIES
        for paid in range(1, 10)
        for normalizers in range(5)
    ]
    started = time.perf_counter()
    results: list[dict[str, object]] = []
    failures: list[str] = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        pending = {
            pool.submit(
                _run_case,
                args.python.resolve(),
                output_dir,
                policy,
                allow_z_false,
                paid,
                normalizers,
                args.timeout,
                not args.no_reuse,
            ): (policy, paid, normalizers)
            for policy, allow_z_false, paid, normalizers in jobs
        }
        for future in as_completed(pending):
            policy, paid, normalizers = pending[future]
            try:
                payload = future.result()
            except Exception as exc:  # fail-closed batch collection
                failures.append(f"{policy}/p{paid}/n{normalizers}: {exc}")
                print(f"ERROR {failures[-1]}", flush=True)
                continue
            status = str(payload["status"])
            print(
                f"{status.upper():7s} {policy:7s} p={paid} n={normalizers} "
                f"components={paid + normalizers} sec={payload['solve_seconds']:.3f}",
                flush=True,
            )
            results.append(
                {
                    "policy": policy,
                    "paid_components": paid,
                    "normalizers": normalizers,
                    "total_components": paid + normalizers,
                    "status": status,
                    "solve_seconds": payload["solve_seconds"],
                    "variables": payload["variables"],
                    "clauses": payload["clauses"],
                    "case_sha256": payload["case_sha256"],
                    "artifact": path_relative(
                        _case_path(output_dir, policy, paid, normalizers), output_dir
                    ),
                    "artifact_sha256": _digest(
                        _case_path(output_dir, policy, paid, normalizers)
                    ),
                }
            )

    results.sort(key=lambda row: (row["policy"], row["paid_components"], row["normalizers"]))
    status_counts: dict[str, int] = {}
    for row in results:
        status = str(row["status"])
        status_counts[status] = status_counts.get(status, 0) + 1
    manifest = {
        "schema": "full-adder-g9-d3-exact-physical-closure-v1",
        "status": (
            "proved_unsat"
            if not failures and len(results) == len(jobs) and status_counts == {"unsat": len(jobs)}
            else "incomplete_or_counterexample"
        ),
        "claim": "No FullAdder implementation exists with gate<=9 and delay<=3 in the reviewed physical library and normalizer normal form.",
        "enumeration": {
            "primary_output_policies": ["strict", "target-zero-may-be-Z"],
            "paid_component_counts": [1, 9],
            "exact_normalizer_counts": [0, 4],
            "shards_expected": len(jobs),
            "shards_completed": len(results),
            "status_counts": dict(sorted(status_counts.items())),
            "failures": failures,
        },
        "normalizer_completeness": {
            "maximum_needed": 4,
            "argument": (
                "A useful normalizer consumes at least one raw Switch-output net; "
                "physical net partitioning prevents partial driver-set overlap, and "
                "each Switch costs 2, so gate<=9 admits at most floor(9/2)=4 "
                "distinct useful normalized nets."
            ),
        },
        "solver": {
            "path": str(SOLVER),
            "sha256": _digest(SOLVER),
            "python": str(args.python.resolve()),
            "per_shard_timeout_seconds": args.timeout,
            "workers": args.workers,
        },
        "elapsed_seconds": time.perf_counter() - started,
        "cases": results,
    }
    encoded = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_bytes(encoded)
    print(f"manifest={manifest_path}", flush=True)
    print(f"manifest_sha256={sha256(encoded).hexdigest()}", flush=True)
    return 0 if manifest["status"] == "proved_unsat" else 1


def path_relative(path: Path, base: Path) -> str:
    return str(path.resolve().relative_to(base.resolve())).replace("\\", "/")


if __name__ == "__main__":
    raise SystemExit(main())
