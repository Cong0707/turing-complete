from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
SUBJECT = HERE / "generic_candidate_ledger.py"


def load_subject():
    spec = importlib.util.spec_from_file_location("test_generic_candidate_ledger_subject", SUBJECT)
    if spec is None or spec.loader is None:
        raise RuntimeError(SUBJECT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


subject = load_subject()


class GenericCandidateLedgerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.candidate = (
            subject.HERE
            / "high30_parameterization_fixture_pipeline/complete_factory_dag.json"
        )
        cls.ledger = subject.build_ledger(cls.candidate)

    def test_complete_contract_is_recomputed(self):
        contracts = self.ledger["contracts"]
        self.assertEqual(contracts["truth"]["rows"], 131072)
        self.assertEqual(contracts["truth"]["mismatch_count"], 0)
        self.assertTrue(contracts["driven_z"]["all_primary_outputs_driven"])
        self.assertEqual(
            contracts["owner_partition"][
                "expected_physical_partition_violation_count"
            ],
            0,
        )
        self.assertEqual(contracts["routing"]["required_native_com_add_count"], 0)

    def test_ledger_round_trip_validates(self):
        with tempfile.TemporaryDirectory(prefix="generic_ledger_test_", dir=subject.HERE) as tmp:
            path = Path(tmp) / "ledger.json"
            subject.write_json(path, self.ledger)
            loaded, review = subject.validate_ledger(path)
            self.assertEqual(loaded, self.ledger)
            self.assertEqual(review["vectors_checked"], 131072)

    def test_tampered_truth_sha_is_rejected(self):
        tampered = dict(self.ledger)
        tampered["contracts"] = dict(tampered["contracts"])
        tampered["contracts"]["truth"] = dict(tampered["contracts"]["truth"])
        tampered["contracts"]["truth"]["output_vector_sha256"] = "0" * 64
        with tempfile.TemporaryDirectory(prefix="generic_ledger_test_", dir=subject.HERE) as tmp:
            path = Path(tmp) / "ledger.json"
            subject.write_json(path, tampered)
            with self.assertRaisesRegex(RuntimeError, "candidate ledger SHA changed"):
                subject.validate_ledger(path)


if __name__ == "__main__":
    unittest.main()
