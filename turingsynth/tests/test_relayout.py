from __future__ import annotations

from types import SimpleNamespace
import unittest

from turingsynth.relayout import _channel_gap_for_failure


def _pin(component: str) -> SimpleNamespace:
    return SimpleNamespace(component=component)


class ChannelExpansionTests(unittest.TestCase):
    def test_forward_failure_expands_after_source_rank(self) -> None:
        net = SimpleNamespace(
            source=_pin("source"),
            sinks=(_pin("sink"),),
            additional_sources=(),
        )
        self.assertEqual(
            _channel_gap_for_failure(net, {"source": 2, "sink": 5}, {}),
            2,
        )

    def test_backward_failure_expands_before_source_rank(self) -> None:
        net = SimpleNamespace(
            source=_pin("source"),
            sinks=(_pin("near"), _pin("far")),
            additional_sources=(),
        )
        self.assertEqual(
            _channel_gap_for_failure(
                net,
                {"source": 5, "near": 4, "far": 3},
                {},
            ),
            4,
        )

    def test_mixed_failure_balances_adjacent_gaps(self) -> None:
        net = SimpleNamespace(
            source=_pin("source"),
            sinks=(_pin("right"),),
            additional_sources=(_pin("left"),),
        )
        ranks = {"source": 6, "left": 5, "right": 7}
        self.assertEqual(_channel_gap_for_failure(net, ranks, {}), 5)
        self.assertEqual(
            _channel_gap_for_failure(net, ranks, {5: 1, 6: 0}),
            6,
        )


if __name__ == "__main__":
    unittest.main()
