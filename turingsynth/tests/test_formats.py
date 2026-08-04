from __future__ import annotations

import unittest

from turingsynth.formats import Circuit, Component, Wire, decode_v15, encode_v15


class V15Tests(unittest.TestCase):
    def test_round_trip(self) -> None:
        circuit = Circuit(
            custom_id=123,
            gate=1,
            delay=1,
            design=bytes(512),
            components=(Component(2, (0, 0), 0, 1),),
            wires=(Wire(0, "", (1, 0), ((0, 2),)),),
        )
        self.assertEqual(decode_v15(encode_v15(circuit)), circuit)


if __name__ == "__main__":
    unittest.main()
