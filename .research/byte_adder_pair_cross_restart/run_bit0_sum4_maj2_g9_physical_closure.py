"""Run the exact bit-0 SUM<=4, MAJ<=2, gate<=9 physical cut closure.

The 45 shards enumerate paid physical component counts 1..9 and exact useful
normalizer counts 0..4.  Every shard uses strict fully-driven primary outputs,
physical wire-net partitions, Switch/BUS Z semantics, and per-output arrival
bounds through ``exact_truth_tuple_physical.py``.
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
SOLVER = HERE / "exact_truth_tuple_physical.py"
BASE_SOLVER = (
    HERE.parent
    / "byte_adder_component_byproduct_catalog"
    / "exact_pretarget_physical.py"
)
DEFAULT_OUTPUT = HERE / "bit0_sum4_maj2_g9_physical_closure"
SUM_MASK = "96"
MAJ_MASK = "e8"
OUTPUT_DELAYS = (4, 2)


def _digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _case_path(output_dir: Path, paid: int, normalizers: int) -> Path:
    return output_dir / f"bit0_sum4_maj2_g9_p{paid}_n{normalizers}.json"


def _validate_case(
    path: Path,
    *,
    paid: int,
    normalizers: int,
) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    expected = {
        "schema": "tc-arbitrary-truth-tuple-exact-physical-v1",
        "target": "truth-tuple",
        "input_count": 3,
        "input_ports": ["Input 0", "Input 1", "Input 2"],
        "output_ports": ["Sum", "Carry"],
        "target_truth_tables_hex": [SUM_MASK, MAJ_MASK],
        "output_max_delays": list(OUTPUT_DELAYS),
        "gate_bound": 9,
        "max_delay": 4,
        "components": paid + normalizers,
        "exact_normalizers": normalizers,
        "allow_z_false": False,
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
    paid: int,
    normalizers: int,
    timeout: float,
    reuse: bool,
) -> dict[str, object]:
    path = _case_path(output_dir, paid, normalizers)
    if reuse and path.is_file():
        payload = _validate_case(path, paid=paid, normalizers=normalizers)
        if payload.get("status") != "unknown":
            return payload

    command = [
        str(python),
        str(SOLVER),
        "--input-count",
        "3",
        "--truth-mask",
        f"0x{SUM_MASK}",
        "--truth-mask",
        f"0x{MAJ_MASK}",
        "--output-name",
        "Sum",
        "--output-name",
        "Carry",
        "--output-max-delay",
        str(OUTPUT_DELAYS[0]),
        "--output-max-delay",
        str(OUTPUT_DELAYS[1]),
        "--gate-bound",
        "9",
        "--components",
        str(paid + normalizers),
        "--normalizers",
        str(normalizers),
        "--timeout",
        str(timeout),
        "--output",
        str(path),
    ]
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
    return _validate_case(path, paid=paid, normalizers=normalizers)


def _relative(path: Path, base: Path) -> str:
    return str(path.resolve().relative_to(base.resolve())).replace("\\", "/")


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
    jobs = [(paid, normalizers) for paid in range(1, 10) for normalizers in range(5)]
    started = time.perf_counter()
    results: list[dict[str, object]] = []
    failures: list[str] = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        pending = {
            pool.submit(
                _run_case,
                args.python.resolve(),
                output_dir,
                paid,
                normalizers,
                args.timeout,
                not args.no_reuse,
            ): (paid, normalizers)
            for paid, normalizers in jobs
        }
        for future in as_completed(pending):
            paid, normalizers = pending[future]
            try:
                payload = future.result()
            except Exception as exc:  # fail-closed batch collection
                failures.append(f"p{paid}/n{normalizers}: {exc}")
                print(f"ERROR {failures[-1]}", flush=True)
                continue
            status = str(payload["status"])
            print(
                f"{status.upper():7s} p={paid} n={normalizers} "
                f"components={paid + normalizers} sec={payload['solve_seconds']:.3f}",
                flush=True,
            )
            case_path = _case_path(output_dir, paid, normalizers)
            results.append(
                {
                    "paid_components": paid,
                    "normalizers": normalizers,
                    "total_components": paid + normalizers,
                    "status": status,
                    "solve_seconds": payload["solve_seconds"],
                    "variables": payload["variables"],
                    "clauses": payload["clauses"],
                    "case_sha256": payload["case_sha256"],
                    "artifact": _relative(case_path, output_dir),
                    "artifact_sha256": _digest(case_path),
                }
            )

    results.sort(key=lambda row: (row["paid_components"], row["normalizers"]))
    status_counts: dict[str, int] = {}
    for row in results:
        status = str(row["status"])
        status_counts[status] = status_counts.get(status, 0) + 1
    complete = not failures and len(results) == len(jobs)
    if complete and status_counts == {"unsat": len(jobs)}:
        closure_status = "proved_unsat"
    elif any(row["status"] == "sat" for row in results):
        closure_status = "counterexample_found"
    else:
        closure_status = "incomplete"

    manifest = {
        "schema": "bit0-sum4-maj2-g9-exact-physical-cut-closure-v1",
        "status": closure_status,
        "claim": (
            "No strict fully-driven implementation of the specific bit-0 "
            "truth tuple (SUM=0x96, MAJ=0xe8) exists with gate<=9, "
            "SUM arrival<=4, and MAJ arrival<=2 in the reviewed physical model."
            if closure_status == "proved_unsat"
            else "The exact bit-0 connected-cut enumeration is not an UNSAT proof."
        ),
        "scope_boundary": (
            "This is only a lower bound for the named two-output connected cut. "
            "It is not a global lower bound for the byte adder and does not rule "
            "out 79/7 via another tuple, cofactor, phase, partial-driver network, "
            "or internal byproduct."
        ),
        "target": {
            "input_count": 3,
            "input_ports": ["Input 0", "Input 1", "Input 2"],
            "output_ports": ["Sum", "Carry"],
            "truth_masks_hex": [SUM_MASK, MAJ_MASK],
            "output_max_delays": list(OUTPUT_DELAYS),
            "strict_fully_driven": True,
            "physical_nets": True,
        },
        "enumeration": {
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
            "base_path": str(BASE_SOLVER),
            "base_sha256": _digest(BASE_SOLVER),
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
    return 0 if closure_status in {"proved_unsat", "counterexample_found"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
