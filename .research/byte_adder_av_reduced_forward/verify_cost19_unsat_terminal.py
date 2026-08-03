"""Audit a completed cost-19 carry-retime UNSAT terminal artifact.

This verifies terminal classification and provenance, not a DRAT proof.  It
rejects watchdog timeouts, partial case sets, parameter drift, hash mismatch,
and non-zero runner exits before recording an exact UNSAT result.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
EXPECTED_SOURCES = ["C1", "A12", "N12", "G2", "A34", "N34", "G4", "A56", "V56"]
EXPECTED_ARRIVALS = {
    "C1": 2,
    "A12": 2,
    "N12": 2,
    "G2": 1,
    "A34": 2,
    "N34": 2,
    "G4": 1,
    "A56": 2,
    "V56": 2,
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def option(command: list[str], name: str) -> str:
    require(name in command, f"runner command lacks {name}")
    index = command.index(name)
    require(index + 1 < len(command), f"runner command has no value for {name}")
    return command[index + 1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("exact", type=Path)
    parser.add_argument("run_result", type=Path)
    parser.add_argument("--solver-script", type=Path, required=True)
    parser.add_argument("--ordinary", type=int, required=True)
    parser.add_argument("--switches", type=int, required=True)
    parser.add_argument("--xors", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    exact_path = args.exact.resolve()
    run_path = args.run_result.resolve()
    solver_path = args.solver_script.resolve()
    output = args.output.resolve()
    for path, label in ((exact_path, "exact"), (run_path, "run result"), (solver_path, "solver")):
        require(path.is_relative_to(HERE), f"{label} must remain under {HERE}: {path}")
        require(path.is_file(), f"missing {label}: {path}")
    require(output.is_relative_to(HERE), f"output must remain under {HERE}: {output}")
    require(not output.exists(), f"refusing to overwrite {output}")

    exact_raw = exact_path.read_bytes()
    run_raw = run_path.read_bytes()
    solver_raw = solver_path.read_bytes()
    exact = json.loads(exact_raw)
    run = json.loads(run_raw)
    exact_hash = sha256(exact_raw).hexdigest()

    components = args.ordinary + args.switches + args.xors
    weighted_cost = args.ordinary + 2 * args.switches + 3 * args.xors
    require(weighted_cost == 19, f"unexpected weighted cost: {weighted_cost}")
    require(exact.get("schema") == "exact-q12-q34-carry-retime-v1", "unexpected schema")
    require(exact.get("status") == "unsat", "exact artifact is not UNSAT")
    require(exact.get("interface") == "q12_q34_carry_retime", "unexpected interface")
    require(exact.get("case_indices") == list(range(540)), "case set is not complete 0..539")
    require(exact.get("free_sources") == EXPECTED_SOURCES, "source interface drift")
    require(exact.get("source_arrivals") == EXPECTED_ARRIVALS, "source arrival drift")
    require(exact.get("gate_bound") == 19, "gate bound drift")
    require(exact.get("max_delay") == 4, "delay bound drift")
    require(exact.get("components") == components, "component count drift")
    require(exact.get("exact_switches") == args.switches, "Switch count drift")
    require(exact.get("exact_xors") == args.xors, "XOR count drift")
    require(exact.get("solver") == "cadical195", "solver drift")
    require(exact.get("physical_nets") is True, "physical-net enforcement missing")
    require(exact.get("output_deadlines") == [4, 4, 4], "output deadline drift")
    require("network" not in exact, "UNSAT artifact unexpectedly contains a witness")

    require(run.get("state") == "completed", "runner did not complete")
    require(run.get("status") == "unsat", "runner status is not UNSAT")
    require(run.get("return_code") == 0, "runner return code is non-zero")
    require(run.get("output_sha256") == exact_hash, "runner/exact SHA mismatch")
    value = run.get("value", {})
    require(value.get("cost") == 19, "runner cost drift")
    require(value.get("ordinary") == args.ordinary, "runner ordinary count drift")
    require(value.get("switches") == args.switches, "runner Switch count drift")
    require(value.get("xors") == args.xors, "runner XOR count drift")
    require(value.get("components") == components, "runner component count drift")
    command = run.get("command")
    require(isinstance(command, list), "runner command is missing")
    require(option(command, "--timeout") == "0", "child timeout was not disabled")
    require(option(command, "--gate-bound") == "19", "command gate bound drift")
    require(option(command, "--max-delay") == "4", "command delay drift")
    require(option(command, "--components") == str(components), "command component drift")
    require(option(command, "--switches") == str(args.switches), "command Switch drift")
    require(option(command, "--xors") == str(args.xors), "command XOR drift")

    record = {
        "schema": "cost19-unsat-terminal-audit-v1",
        "结论": "严格终态 UNSAT；不是外层 timeout",
        "exact_artifact": {
            "path": str(exact_path),
            "sha256": exact_hash,
            "status": exact["status"],
            "case_count": len(exact["case_indices"]),
            "variables": exact["variables"],
            "clauses": exact["clauses"],
            "solve_seconds": exact["solve_seconds"],
        },
        "runner": {
            "path": str(run_path),
            "sha256": sha256(run_raw).hexdigest(),
            "state": run["state"],
            "status": run["status"],
            "return_code": run["return_code"],
            "elapsed_seconds": run["elapsed_seconds"],
            "child_timeout": 0,
        },
        "decomposition": {
            "ordinary": args.ordinary,
            "switches": args.switches,
            "xors": args.xors,
            "components": components,
            "weighted_cost": weighted_cost,
            "max_delay": 4,
        },
        "solver_script": {
            "path": str(solver_path),
            "sha256": sha256(solver_raw).hexdigest(),
        },
        "checks": {
            "complete_540_cases": True,
            "physical_nets": True,
            "runner_completed": True,
            "runner_output_hash_matches": True,
            "nonzero_or_timeout_promoted_to_unsat": False,
        },
        "limitation": "终态审计验证参数、覆盖范围和 provenance；求解器未输出 DRAT proof。",
    }
    encoded = (json.dumps(record, ensure_ascii=False, indent=2) + "\n").encode()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(encoded)
    print(json.dumps(record, ensure_ascii=False, indent=2))
    print(f"sha256={sha256(encoded).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
