from __future__ import annotations

from pathlib import Path
import unittest

from tc_save_lab.builder import wire_from_vertices
from tc_save_lab.model import Circuit, Component
from tc_save_lab.tower_asic import (
    DEFAULT_COMPONENT_SPRITE_ROOT,
    TowerCase,
    all_tower_cases,
    audit_sprite_geometry,
    build_tower_io_protocol_probe,
    build_tower_protocol_candidate,
    ctz,
    ctz_parity_from_action_counter,
    formula_moves,
    recursive_moves,
    verify_tower_event_model,
    verify_tower_io_protocol_probe,
)


class TowerAsicTests(unittest.TestCase):
    def test_formula_matches_independent_recursive_reference_for_all_inputs(self):
        self.assertEqual(len(all_tower_cases()), 18)
        for case in all_tower_cases():
            self.assertEqual(
                formula_moves(case),
                recursive_moves(
                    case.disk_count,
                    case.source,
                    case.destination,
                    case.spare,
                ),
                case,
            )

    def test_event_model_exhaustively_replays_all_level_inputs(self):
        result = verify_tower_event_model()
        self.assertEqual(result["case_count"], 18)
        self.assertEqual(result["event_counts"], {3: 28, 4: 60, 5: 124})
        self.assertEqual(result["cycle_counts"], {3: 29, 4: 61, 5: 125})
        self.assertEqual(result["maximum_cycles"], 125)

    def test_five_disk_schedule_overlaps_safe_input_reads_and_outputs(self):
        trace = build_tower_protocol_candidate(TowerCase(4, 0, 2))
        self.assertEqual(trace.cycle_count, 125)
        self.assertEqual(tuple(tick.input_value for tick in trace.ticks[:4]), (4, 0, 2, 1))
        self.assertEqual(trace.ticks[0].output_control, 0)
        self.assertEqual(trace.ticks[1].output_value, 0)
        self.assertEqual(trace.ticks[2].output_value, 5)
        self.assertEqual(trace.ticks[3].output_value, 2)
        self.assertEqual(trace.ticks[-1].tick, 124)
        self.assertEqual(trace.level_result.first_win_event, 124)
        self.assertTrue(trace.level_result.won)

    def test_reduced_ctz_parity_matches_every_reachable_action_counter(self):
        for action_counter in range(124):
            self.assertEqual(
                ctz_parity_from_action_counter(action_counter),
                ctz((action_counter >> 2) + 1) & 1,
                action_counter,
            )

    def test_non_deployable_probe_is_valid_current_v15_topology(self):
        result = verify_tower_io_protocol_probe()
        self.assertEqual(result["format_version"], 15)
        self.assertEqual(result["component_count"], 4)
        self.assertEqual(result["wire_count"], 3)
        self.assertFalse(result["deployable"])
        candidate = build_tower_io_protocol_probe()
        self.assertEqual(sum(component.kind == 62 for component in candidate.components), 1)
        self.assertEqual(sum(component.kind == 70 for component in candidate.components), 1)

    @unittest.skipUnless(
        DEFAULT_COMPONENT_SPRITE_ROOT.is_dir(),
        "current Turing Complete component sprites are not installed on this machine",
    )
    def test_live_sprite_alpha_audit_accepts_probe_and_rejects_body_crossing(self):
        result = verify_tower_io_protocol_probe(sprite_root=DEFAULT_COMPONENT_SPRITE_ROOT)
        self.assertIn("sprite_audit", result)

        crossing = Circuit(
            components=(Component(4, (0, 0), 0, 1),),
            wires=(wire_from_vertices(((-4, 0), (4, 0))),),
        )
        audit = audit_sprite_geometry(crossing, DEFAULT_COMPONENT_SPRITE_ROOT)
        self.assertFalse(audit.is_safe)
        self.assertGreater(len(audit.wire_collisions), 0)


if __name__ == "__main__":
    unittest.main()
