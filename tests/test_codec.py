from __future__ import annotations

import unittest

from tc_save_lab.binary import FormatError
from tc_save_lab.codec import decode_v15, encode_v15
from tc_save_lab.model import Circuit, Component, Wire


class CodecTests(unittest.TestCase):
    def test_round_trip_preserves_all_v15_fields(self):
        circuit = Circuit(
            custom_id=123,
            hub_id=456,
            gate=42,
            delay=3,
            menu_visible=False,
            clock_speed=12_000_000,
            dependencies=(88, 99),
            description="test",
            sync_state=2,
            score=7,
            player_data=b"abc",
            hub_description="hub",
            design=bytes(range(256)) * 2,
            components=(
                Component(
                    kind=78,
                    position=(-5, 6),
                    rotation=3,
                    permanent_id=98,
                    user_label="custom",
                    custom_string="payload",
                    settings=(1, 2),
                    buffer_size=4,
                    ui_order=-1,
                    word_size=8,
                    immutable=True,
                    cost_gate=10,
                    cost_delay=2,
                    little_endian=True,
                    init_data=12,
                    linked_components=((1, 2, "pin", 3, 4),),
                    selected_programs=(("level", "program"),),
                    custom_id=123,
                    custom_word_sizes=((12, 8),),
                ),
            ),
            wires=(Wire(0, "wire", (0, 0), ((0, 3), (2, 1))),),
        )
        self.assertEqual(decode_v15(encode_v15(circuit)), circuit)

    def test_rejects_invalid_wire_direction(self):
        circuit = Circuit(wires=(Wire(0, "", (0, 0), ((8, 1),)),))
        with self.assertRaises(FormatError):
            encode_v15(circuit)

    def test_rejects_trailing_bytes(self):
        payload = encode_v15(Circuit())
        with self.assertRaises(FormatError):
            decode_v15(payload + b"\x00")
