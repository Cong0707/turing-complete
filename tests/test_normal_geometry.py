from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import shutil
import tempfile
import unittest

from tc_save_lab.builder import RECIPES, build_recipe, wire_from_vertices
from tc_save_lab.codec import decode_v15, encode_v15
from tc_save_lab.pins import analyze_connectivity
from tc_save_lab.sprite_geometry import (
    DEFAULT_COMPONENT_SPRITE_ROOT,
    audit_sprite_geometry,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TARGETS = {
    "decoder_3": 16,
    "counting_signals": 16,
    "xor_gate": 4,
    "xnor": 4,
}


class NormalCandidateGeometryTests(unittest.TestCase):
    def _rebuilt_payload(self, level: str) -> tuple[bytes, dict[str, object]]:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = PROJECT_ROOT / "examples" / level
            target = root / "examples" / level
            shutil.copytree(source / "baseline", target / "baseline")
            shutil.copytree(source / "scaffold", target / "scaffold")
            record = build_recipe(root, level)
            return (target / "candidate" / "circuit.data").read_bytes(), record

    def test_candidates_match_their_generators_and_logic_proofs(self) -> None:
        for level, vector_count in TARGETS.items():
            with self.subTest(level=level):
                payload, record = self._rebuilt_payload(level)
                candidate_path = PROJECT_ROOT / "examples" / level / "candidate" / "circuit.data"
                self.assertEqual(payload, candidate_path.read_bytes())
                circuit = decode_v15(payload)
                self.assertEqual(decode_v15(encode_v15(circuit)), circuit)
                self.assertEqual(record["exhaustive_test_vectors"], vector_count)
                connectivity = analyze_connectivity(circuit)
                self.assertEqual(connectivity["unconnected_pin_count"], 0)
                self.assertEqual(connectivity["multi_driver_network_count"], 0)
                self.assertEqual(connectivity["width_mismatch_network_count"], 0)
                self.assertEqual(connectivity["cycle_component_count"], 0)
                self.assertEqual(
                    (circuit.gate, circuit.delay),
                    (RECIPES[level].declared_gate, RECIPES[level].declared_delay),
                )
                self.assertLessEqual(connectivity["unit_logic_depth"], circuit.delay)

    @unittest.skipUnless(
        DEFAULT_COMPONENT_SPRITE_ROOT.is_dir(),
        "当前机器未安装 Turing Complete 组件精灵，跳过真实几何审计",
    )
    def test_candidates_pass_the_current_sprite_alpha_audit(self) -> None:
        for level in TARGETS:
            with self.subTest(level=level):
                candidate_path = PROJECT_ROOT / "examples" / level / "candidate" / "circuit.data"
                audit = audit_sprite_geometry(
                    decode_v15(candidate_path.read_bytes()),
                    DEFAULT_COMPONENT_SPRITE_ROOT,
                )
                self.assertEqual(audit.unsupported_component_kinds, ())
                self.assertEqual(audit.component_overlap_cells, ())
                self.assertEqual(audit.wire_collisions, ())
                self.assertEqual(audit.wire_interior_pin_contacts, ())

    @unittest.skipUnless(
        DEFAULT_COMPONENT_SPRITE_ROOT.is_dir(),
        "当前机器未安装 Turing Complete 组件精灵，跳过真实几何审计",
    )
    def test_alpha_audit_rejects_input_body_and_nonendpoint_port_crossing(self) -> None:
        """The two failure modes observed in old XOR/XNOR routes stay detectable."""

        path = PROJECT_ROOT / "examples" / "xnor" / "candidate" / "circuit.data"
        circuit = decode_v15(path.read_bytes())
        bad_wire = wire_from_vertices(
            ((-13, -1), (-13, 3), (-7, 3), (-6, 4))
        )
        audit = audit_sprite_geometry(
            replace(circuit, wires=(bad_wire, *circuit.wires[1:])),
            DEFAULT_COMPONENT_SPRITE_ROOT,
        )
        self.assertTrue(audit.wire_collisions)
        self.assertTrue(audit.wire_interior_pin_contacts)
