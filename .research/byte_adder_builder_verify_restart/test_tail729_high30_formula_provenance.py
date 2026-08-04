from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest

from pysat.formula import CNF


HERE = Path(__file__).resolve().parent


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


formula = load("test_tail729_formula_worker", HERE / "tail729_high30_formula_worker.py")
audit = load("test_tail729_sweep_auditor", HERE / "audit_tail729_high30_primary_sweep.py")


class Tail729FormulaProvenanceTests(unittest.TestCase):
    def test_cnf_fingerprint_is_deterministic_and_order_sensitive(self):
        first = CNF(from_clauses=[[1, -2], [2]])
        second = CNF(from_clauses=[[1, -2], [2]])
        reordered = CNF(from_clauses=[[2], [1, -2]])
        left = formula.fingerprint_cnf(first)
        right = formula.fingerprint_cnf(second)
        changed = formula.fingerprint_cnf(reordered)
        self.assertEqual(left, right)
        self.assertNotEqual(left["sha256"], changed["sha256"])
        self.assertEqual(left["variables"], 2)
        self.assertEqual(left["clauses"], 2)
        self.assertEqual(left["literals"], 3)

    def test_fingerprinting_solver_delegates(self):
        cnf = CNF(from_clauses=[[1]])
        with formula.FingerprintingSolver(
            name="glucose42", bootstrap_with=cnf, formula_only=False
        ) as solver:
            self.assertTrue(solver.solve())
            self.assertIsNotNone(solver.get_model())

    def test_expected_sweep_has_64_unique_formula_specs(self):
        jobs = audit.expected_jobs()
        self.assertEqual(len(jobs), 64)
        self.assertEqual(len({job["name"] for job in jobs}), 64)
        self.assertEqual(len({job["formula_spec_sha256"] for job in jobs}), 64)
        self.assertEqual(
            {job["decomposition_name"] for job in jobs},
            {
                "g17_o01_s08_x0",
                "g17_o03_s07_x0",
                "g17_o05_s06_x0",
                "g17_o07_s05_x0",
            },
        )


if __name__ == "__main__":
    unittest.main()
