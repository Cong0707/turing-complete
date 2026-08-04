"""Run every exact weighted composition for one ranked source shell.

Compositions are ordered by increasing component count so the smallest CNFs
run first.  The runner stops immediately on SAT and preserves that witness for
full audit/materialization; only a complete all-UNSAT domain is reported as a
closed exact shell.
"""

from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
WORKER = HERE / "exact_ranked_private_frontier_sat.py"
DEFAULT_RANKING = HERE / "same_cost_private_frontier_ranking.json"


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def atomic_write(path: Path, payload: dict[str, Any]) -> str:
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(encoded)
    temporary.replace(path)
    return sha256(encoded).hexdigest()


def find_case(ranking: dict[str, Any], case_key: str) -> dict[str, Any]:
    matches = [
        row
        for field in ("ranked_candidates", "frozen_cases")
        for row in ranking.get(field, ())
        if row.get("case_key") == case_key
    ]
    if len(matches) != 1:
        raise RuntimeError(f"expected one ranked case {case_key!r}, got {len(matches)}")
    return matches[0]


def compositions(bound: int) -> list[dict[str, int]]:
    rows = []
    for ordinary in range(bound + 1):
        for switches in range(bound // 2 + 1):
            for xors in range(bound // 3 + 1):
                if ordinary + 2 * switches + 3 * xors == bound:
                    rows.append(
                        {
                            "ordinary": ordinary,
                            "components": ordinary + switches + xors,
                            "switches": switches,
                            "xors": xors,
                        }
                    )
    return sorted(rows, key=lambda row: (row["components"], row["xors"], row["switches"], row["ordinary"]))


def safe_name(case_key: str) -> str:
    value = "".join(character if character.isalnum() else "_" for character in case_key)
    return value.strip("_") or "case"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ranking", type=Path, default=DEFAULT_RANKING)
    parser.add_argument("--case-key", required=True)
    parser.add_argument("--source-profile", choices=("expanded", "no_private"), default="no_private")
    parser.add_argument("--solver", choices=("cadical195", "glucose42"), required=True)
    parser.add_argument("--timeout", type=float, default=180.0)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    ranking = json.loads(args.ranking.read_text(encoding="utf-8"))
    case = find_case(ranking, args.case_key)
    if not case.get("source_shell_functional_audit"):
        raise RuntimeError("ranked case lacks source-shell functional audit")
    bound = int(case["replacement_exact_bound"])
    domain = compositions(bound)
    catalogue_domain = {
        (int(row["ordinary"]), int(row["components"]), int(row["switches"]), int(row["xors"]))
        for row in case["exact_compositions"]
    }
    runner_domain = {
        (row["ordinary"], row["components"], row["switches"], row["xors"])
        for row in domain
    }
    if catalogue_domain != runner_domain:
        raise RuntimeError("ranking/runner exact composition domains differ")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    results = []
    stopped_on_sat = False
    slug = safe_name(args.case_key)
    for decomposition in domain:
        components = decomposition["components"]
        switches = decomposition["switches"]
        xors = decomposition["xors"]
        output = args.output_dir / (
            f"{slug}_{args.source_profile}_g{bound}_n{components}_s{switches}_x{xors}_{args.solver}.json"
        )
        if output.exists() and not args.force:
            result = json.loads(output.read_text(encoding="utf-8"))
            returncode = 0 if result.get("status") != "unknown" else 2
            stdout = stderr = ""
            reused = True
        else:
            completed = subprocess.run(
                [
                    sys.executable,
                    str(WORKER),
                    "--ranking", str(args.ranking),
                    "--case-key", args.case_key,
                    "--source-profile", args.source_profile,
                    "--gate-bound", str(bound),
                    "--components", str(components),
                    "--switches", str(switches),
                    "--xors", str(xors),
                    "--solver", args.solver,
                    "--timeout", str(args.timeout),
                    "--output", str(output),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                timeout=args.timeout + 120,
                check=False,
            )
            returncode = completed.returncode
            stdout = completed.stdout
            stderr = completed.stderr
            reused = False
            if not output.is_file():
                raise RuntimeError(
                    f"missing result for {decomposition}; rc={returncode}; "
                    f"stdout={stdout!r}; stderr={stderr!r}"
                )
            result = json.loads(output.read_text(encoding="utf-8"))
        status = str(result.get("status"))
        expected_projected = 80 if args.source_profile == "expanded" else int(case["projected_complete_gate"])
        actual = (
            result.get("case_key"), result.get("source_profile"),
            int(result.get("gate_bound", -1)), int(result.get("components", -1)),
            int(result.get("exact_switches", -1)), int(result.get("exact_xors", -1)),
            result.get("solver"), int(result.get("projected_complete_gate_at_bound", -1)),
            result.get("ranking_sha256"), result.get("script_sha256"),
        )
        expected = (
            args.case_key, args.source_profile, bound, components, switches, xors,
            args.solver, expected_projected, digest(args.ranking), digest(WORKER),
        )
        if actual != expected or status not in {"sat", "unsat", "unknown"}:
            raise RuntimeError(f"worker contract mismatch in {output}: {actual} != {expected}")
        record = {
            **decomposition,
            "weighted_gate": bound,
            "status": status,
            "returncode": returncode,
            "reused": reused,
            "result": output.resolve().relative_to(ROOT).as_posix(),
            "result_sha256": digest(output),
            "variables": result.get("variables"),
            "clauses": result.get("clauses"),
            "build_seconds": result.get("build_seconds"),
            "solve_seconds": result.get("solve_seconds"),
            "stdout": stdout,
            "stderr": stderr,
        }
        results.append(record)
        print(
            json.dumps(
                {
                    "case_key": args.case_key,
                    "profile": args.source_profile,
                    "solver": args.solver,
                    "decomposition": [decomposition["ordinary"], switches, xors],
                    "components": components,
                    "status": status,
                    "result_sha256": record["result_sha256"],
                },
                ensure_ascii=False,
            ),
            flush=True,
        )
        if status == "sat":
            stopped_on_sat = True
            break

    statuses = Counter(record["status"] for record in results)
    complete_unsat = len(results) == len(domain) and statuses == {"unsat": len(domain)}
    payload = {
        "schema": "byte-adder-80d7-ranked-private-frontier-sweep-v1",
        "ranking": args.ranking.resolve().relative_to(ROOT).as_posix(),
        "ranking_sha256": digest(args.ranking),
        "worker": WORKER.resolve().relative_to(ROOT).as_posix(),
        "worker_sha256": digest(WORKER),
        "runner_sha256": digest(Path(__file__).resolve()),
        "case_key": args.case_key,
        "cut_node_ids": list(map(int, case["cut_node_ids"])),
        "source_profile": args.source_profile,
        "private_frontier_id": int(case["private_frontier_id"]),
        "solver": args.solver,
        "timeout_seconds_per_case": args.timeout,
        "gate_bound": bound,
        "projected_complete_gate": 80 if args.source_profile == "expanded" else int(case["projected_complete_gate"]),
        "execution_order": "increasing components, then xors, switches, ordinary",
        "expected_decompositions": domain,
        "expected_case_count": len(domain),
        "executed_case_count": len(results),
        "complete_without_sat": complete_unsat and not stopped_on_sat,
        "stopped_on_sat": stopped_on_sat,
        "status_counts": dict(sorted(statuses.items())),
        "results": results,
    }
    summary_sha = atomic_write(args.summary, payload)
    print(
        json.dumps(
            {
                "summary": str(args.summary.resolve()),
                "summary_sha256": summary_sha,
                "case_key": args.case_key,
                "profile": args.source_profile,
                "solver": args.solver,
                "expected_case_count": len(domain),
                "executed_case_count": len(results),
                "status_counts": payload["status_counts"],
                "complete_without_sat": payload["complete_without_sat"],
                "stopped_on_sat": stopped_on_sat,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 10 if stopped_on_sat else 2 if statuses.get("unknown", 0) else 0


if __name__ == "__main__":
    raise SystemExit(main())
