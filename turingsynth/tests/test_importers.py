from __future__ import annotations

import unittest

from turingsynth.importers.v15 import (
    _maker_affinity,
    _splitter_affinity,
    _splitter_output_affinity,
)


class V15ImporterAffinityTests(unittest.TestCase):
    def test_scalar_splitter_precedes_first_bit_lane(self) -> None:
        self.assertEqual(_splitter_output_affinity(17, "out0"), 0.0)
        self.assertEqual(_splitter_output_affinity(17, "out7"), 7.0)
        self.assertEqual(_splitter_affinity(17), -1.0)

    def test_scalar_maker_follows_last_bit_lane(self) -> None:
        self.assertEqual(_maker_affinity(16, tuple(float(i) for i in range(8))), 8.0)

    def test_chunk_splitter_uses_chunk_centers(self) -> None:
        self.assertEqual(_splitter_output_affinity(99, "out0"), 3.5)
        self.assertEqual(_splitter_output_affinity(99, "out3"), 27.5)
        self.assertEqual(_splitter_affinity(99), -4.5)


if __name__ == "__main__":
    unittest.main()
