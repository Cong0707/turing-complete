from __future__ import annotations

from pathlib import Path
import unittest

from turingsynth.config import load_project
from turingsynth.frontend.yosys import normalize_yosys_json
from turingsynth.mapping.packer import map_to_native
from turingsynth.targets import build_target_context


class MappingTests(unittest.TestCase):
    def test_eight_parallel_ands_use_one_word_gate(self) -> None:
        manifest = Path(__file__).parents[1] / "examples" / "byte_adder" / "project.toml"
        config = load_project(manifest)
        a_bits = list(range(2, 10))
        b_bits = list(range(10, 18))
        y_bits = list(range(18, 26))
        raw = {
            "modules": {
                "byte_adder": {
                    "ports": {
                        "A": {"direction": "input", "bits": a_bits},
                        "B": {"direction": "input", "bits": b_bits},
                        "Carry_in": {"direction": "input", "bits": [26]},
                        "Output": {"direction": "output", "bits": y_bits},
                        "Carry_out": {"direction": "output", "bits": ["0"]},
                    },
                    "cells": {
                        f"and_{index}": {
                            "type": "$_AND_",
                            "connections": {"A": [a_bits[index]], "B": [b_bits[index]], "Y": [y_bits[index]]},
                            "attributes": {},
                        }
                        for index in range(8)
                    },
                }
            }
        }
        logical = normalize_yosys_json(raw, config)
        target = build_target_context(config, logical)
        physical = map_to_native(config, logical, target)
        word_ands = [component for component in physical.components if component.kind == 20]
        self.assertEqual(len(word_ands), 1)
        self.assertEqual(word_ands[0].word_size, 8)
        self.assertEqual(physical.gate, 8)
        self.assertEqual(physical.delay, 1)


if __name__ == "__main__":
    unittest.main()
