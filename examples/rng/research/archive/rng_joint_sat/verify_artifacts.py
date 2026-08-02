"""Fast independent replay of the joint-SAT research artifacts."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def read(name: str) -> dict[str, object]:
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def main() -> None:
    symbolic = load_module("joint_artifact_symbolic", HERE / "symbolic_joint_smt.py")
    weighted = load_module("joint_artifact_weighted", HERE / "joint_weighted_search.py")
    init = load_module(
        "joint_artifact_init", ROOT / ".research/rng_init_reuse/verify_init_reuse.py"
    )

    optimum = read("symbolic_n4_optimum.json")
    if optimum["status"] != "sat" or optimum["certificate"]["metrics"]["logic_cost"] != 14:
        raise AssertionError("4-bit SAT optimum artifact changed")
    symbolic.verify(optimum["certificate"])

    lower = read("symbolic_n4_budget13.json")
    if lower["status"] != "unsat" or lower["logic_budget"] != 13:
        raise AssertionError("4-bit lower-bound artifact changed")

    known = read("weighted_known_dag_230.json")
    metrics = known["certificate"]["metrics"]
    if known["status"] != "sat" or (metrics["xor"], metrics["or"], metrics["logic_cost"]) != (61, 47, 230):
        raise AssertionError("full-width known-DAG smoke artifact changed")
    weighted.verify_certificate(init, known["certificate"])

    arbitrary = read("symbolic_n32_budget221_15s.json")
    if arbitrary["status"] != "unknown" or arbitrary.get("reason") != "timeout":
        raise AssertionError("32-bit arbitrary-T measurement changed")
    family = read("symbolic_radius1_budget221_30s.json")
    if (
        family["status"] != "unknown"
        or family.get("reason") != "timeout"
        or family.get("basis_family_size") != 6
    ):
        raise AssertionError("32-bit radius-one measurement changed")

    print("4-bit symbolic joint model: SAT logic=14, UNSAT logic<=13")
    print("32-bit known DAG replay: XOR=61 OR=47 logic=230 gate=396")
    print("32-bit target runs: no candidate; both bounded runs timed out")


if __name__ == "__main__":
    main()
