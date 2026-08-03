"""Freeze the complete local <=7 S5/S6 physical UNSAT matrix."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

from make_ubuntu_sweep import decompositions
from physical_exact import dependency_sha256


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "s56_atmost7_d6_unsat_summary.json"


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def main() -> int:
    expected_dependencies = dependency_sha256()
    records = []
    for gate in range(1, 8):
        for components, ordinary, switches, xors in decompositions(gate):
            path = HERE / (
                f"local_s56_g{gate}_n{components}_s{switches}_x{xors}.json"
            )
            payload = json.loads(path.read_text(encoding="utf-8"))
            checks = {
                "status_unsat": payload.get("status") == "unsat",
                "domain_s56": payload.get("domain") == "s56",
                "rows_96": payload.get("rows") == 96,
                "gate": payload.get("gate_bound") == gate,
                "delay": payload.get("max_delay") == 6,
                "components": payload.get("components") == components,
                "ordinary": payload.get("ordinary") == ordinary,
                "switches": payload.get("exact_switches") == switches,
                "xors": payload.get("exact_xors") == xors,
                "physical_nets": payload.get("physical_nets") is True,
                "outputs_driven": payload.get("public_outputs_must_be_driven") is True,
                "dependencies": payload.get("dependency_sha256") == expected_dependencies,
                "timer_clean": payload.get("timer_errors") == [],
            }
            if not all(checks.values()):
                raise RuntimeError(f"invalid local result {path}: {checks}")
            records.append(
                {
                    "gate": gate,
                    "components": components,
                    "ordinary": ordinary,
                    "switches": switches,
                    "xors": xors,
                    "solve_seconds": payload["solve_seconds"],
                    "path": path.name,
                    "sha256": digest(path),
                }
            )
    payload = {
        "schema": "fast-negative-s56-local-bound-v1",
        "status": "unsat",
        "claim": (
            "No fully-driven physical S5/S6 network of total gate cost <=7 "
            "and delay <=6 exists on the paid fast-negative boundary"
        ),
        "care_rows": 96,
        "gate_costs_covered": list(range(1, 8)),
        "decompositions_covered": len(records),
        "switch_z_semantics": True,
        "bus_conflict_constraints": True,
        "physical_net_partition": True,
        "dependency_sha256": expected_dependencies,
        "records": records,
        "scope_warning": (
            "This is a local boundary lower bound, not a global Byte Adder "
            "lower bound; reaching 93/6 requires cross-bit or shell sharing."
        ),
    }
    encoded = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    OUTPUT.write_text(encoded, encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(OUTPUT),
                "records": len(records),
                "sha256": sha256(encoded.encode()).hexdigest(),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
