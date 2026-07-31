from __future__ import annotations

from pathlib import Path
import unittest

from tc_save_lab.binary import FormatError
from tc_save_lab.codec import decode_circuit, encode_v15
from tc_save_lab.legacy_codec import decode_v7, decode_v13, decode_v14
from tc_save_lab.storage import DEFAULT_GAME_ROOT


CAMPAIGN_ROOT = DEFAULT_GAME_ROOT / "campaign"


class LegacyCodecUnitTests(unittest.TestCase):
    def test_dispatch_rejects_unknown_version(self):
        with self.assertRaises(FormatError):
            decode_circuit(b"\x0c")

    def test_legacy_teleport_wire_is_not_silently_written_as_v15(self):
        from tc_save_lab.model import Circuit, Wire

        circuit = Circuit(wires=(Wire(0, "", (1, 2), (), (3, 4)),))
        with self.assertRaises(FormatError):
            encode_v15(circuit)


@unittest.skipUnless(CAMPAIGN_ROOT.is_dir(), "local game installation is unavailable")
class InstalledCampaignLegacyTests(unittest.TestCase):
    def test_every_main_campaign_circuit_is_readable(self):
        failures: list[str] = []
        versions: set[int] = set()
        for path in sorted(CAMPAIGN_ROOT.glob("*/circuit.data")):
            payload = path.read_bytes()
            if payload[0] not in {7, 13, 14, 15}:
                continue
            versions.add(payload[0])
            try:
                decode_circuit(payload)
            except Exception as exc:  # pragma: no cover - reported with path
                failures.append(f"{path.parent.name} v{payload[0]}: {exc}")
        self.assertEqual(failures, [])
        self.assertTrue({7, 13, 14, 15}.issubset(versions))

    def test_every_supported_hint_solution_is_readable(self):
        failures: list[str] = []
        for path in sorted(CAMPAIGN_ROOT.glob("*/hint_solution.data")):
            payload = path.read_bytes()
            if payload[0] not in {7, 13, 14, 15}:
                continue
            try:
                decode_circuit(payload)
            except Exception as exc:  # pragma: no cover - reported with path
                failures.append(f"{path.parent.name} v{payload[0]}: {exc}")
        self.assertEqual(failures, [])

    def test_version_specific_decoders_match_dispatch(self):
        samples = {
            7: CAMPAIGN_ROOT / "binary_racer" / "circuit.data",
            13: CAMPAIGN_ROOT / "always_on" / "circuit.data",
            14: CAMPAIGN_ROOT / "nand_gate" / "circuit.data",
        }
        decoders = {7: decode_v7, 13: decode_v13, 14: decode_v14}
        for version, path in samples.items():
            payload = path.read_bytes()
            self.assertEqual(payload[0], version)
            self.assertEqual(decoders[version](payload), decode_circuit(payload))
