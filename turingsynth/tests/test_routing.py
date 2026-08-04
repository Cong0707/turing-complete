from __future__ import annotations

import unittest

from turingsynth.audit.physical import (
    _foreign_endpoint_contacts,
    _non_orthogonal_foreign_contacts,
)
from turingsynth.formats.model import Component
from turingsynth.mapping.native import INPUT, OUTPUT
from turingsynth.routing.astar import (
    _collector_edges,
    _direct_axis_path,
    _direct_visibility_path,
    _fanout_track_candidates,
    _fanout_edges,
    _growth_fanout_edges,
    _plan_fanout_tracks,
    _pin_access_path,
    _pin_access_point,
    _search,
    _vertices,
)


class FanoutRoutingTests(unittest.TestCase):
    def test_direct_hanan_path_is_committed_without_general_search(self) -> None:
        reserved: set[tuple[int, int]] = set()
        vertical: dict[int, list[tuple[int, int, str]]] = {}
        horizontal: dict[int, list[tuple[int, int, str]]] = {}
        path = _direct_axis_path(
            "direct",
            (0, 0),
            (8, 4),
            routing_source=(1, 0),
            routing_sink=(7, 4),
            forbidden=frozenset(),
            forbidden_edges=frozenset(),
            reserved=reserved,
            track_intervals=vertical,
            horizontal_intervals=horizontal,
            bounds=(-2, -2, 10, 6),
        )

        self.assertIsNotNone(path)
        assert path is not None
        self.assertEqual(path[0], (0, 0))
        self.assertEqual(path[-1], (8, 4))
        directions = {
            (right[0] - left[0], right[1] - left[1])
            for left, right in zip(path, path[1:])
        }
        self.assertLessEqual(len(directions), 2)
        self.assertTrue(reserved)

    def test_direct_visibility_minimizes_detour_before_turns(self) -> None:
        reserved: set[tuple[int, int]] = set()
        vertical: dict[int, list[tuple[int, int, str]]] = {}
        horizontal: dict[int, list[tuple[int, int, str]]] = {}
        path = _direct_visibility_path(
            "visibility",
            (0, 0),
            (8, 0),
            routing_source=(0, 0),
            routing_sink=(8, 0),
            forbidden=frozenset({(4, 0)}),
            forbidden_edges=frozenset(),
            reserved=reserved,
            track_intervals=vertical,
            horizontal_intervals=horizontal,
            bounds=(-4, -4, 12, 4),
        )

        self.assertIsNotNone(path)
        assert path is not None
        self.assertEqual(len(path) - 1, 10)
        self.assertEqual(len(_vertices(path)) - 2, 2)
        self.assertNotIn((4, 0), path)
        self.assertEqual(len(reserved), 2)

    def test_growth_comb_commits_prevalidated_terminal_paths(self) -> None:
        edges = _growth_fanout_edges(
            "growth",
            (0, 0),
            ((10, -4), (12, 4)),
            routing_source=(1, 0),
            routing_sinks=((9, -4), (11, 4)),
            forbidden=frozenset(),
            forbidden_edges=frozenset(),
            reserved=set(),
            track_intervals={},
            horizontal_intervals={},
        )

        feeder = next(edge for edge in edges if edge.role == "feeder")
        taps = [edge for edge in edges if edge.role == "tap"]
        self.assertEqual(feeder.planned_path, ((0, 0), (1, 0)))
        self.assertEqual(len(taps), 2)
        self.assertTrue(all(edge.planned_path is not None for edge in taps))
        self.assertTrue(
            all(
                edge.planned_path[0] == edge.source
                and edge.planned_path[-1] == edge.sink
                for edge in taps
                if edge.planned_path is not None
            )
        )

    def test_growth_comb_accepts_a_compact_adjacent_stage(self) -> None:
        edges = _growth_fanout_edges(
            "compact-growth",
            (0, 0),
            ((3, -2), (9, 2)),
            routing_source=(0, 0),
            routing_sinks=((3, -2), (9, 2)),
            forbidden=frozenset(),
            forbidden_edges=frozenset(),
            reserved=set(),
            track_intervals={},
            horizontal_intervals={},
        )

        self.assertEqual(edges[0].role, "feeder")
        terminals = [edge for edge in edges if edge.role in {"feeder", "tap"}]
        self.assertTrue(all(edge.planned_path is not None for edge in terminals))
        self.assertLessEqual(
            max(point[0] for edge in edges for point in edge.planned_path or ()),
            9,
        )

    def test_growth_comb_uses_inline_terminal_as_real_spine_endpoint(self) -> None:
        edges = _growth_fanout_edges(
            "inline-growth",
            (0, 0),
            ((8, 0), (12, 4)),
            routing_source=(1, 0),
            routing_sinks=((7, 0), (11, 4)),
            forbidden=frozenset({(7, 0)}),
            forbidden_edges=frozenset(),
            reserved=set(),
            track_intervals={},
            horizontal_intervals={},
        )

        self.assertFalse(any(edge.role == "stem" for edge in edges))
        inline_tap = next(
            edge for edge in edges if edge.role == "tap" and edge.sink == (8, 0)
        )
        self.assertEqual(inline_tap.source, (7, 0))
        self.assertTrue(
            any(
                edge.role == "spine" and (7, 0) in {edge.source, edge.sink}
                for edge in edges
            )
        )

    def test_growth_comb_may_branch_from_its_source_stem(self) -> None:
        edges = _growth_fanout_edges(
            "stem-growth",
            (0, 0),
            ((3, -2), (9, 2)),
            routing_source=(0, 0),
            routing_sinks=((3, -2), (9, 2)),
            forbidden=frozenset(),
            forbidden_edges=frozenset(),
            reserved=set(),
            track_intervals={
                1: [(-8, 8, "foreign-1")],
                2: [(-8, 8, "foreign-2")],
                3: [(-8, 8, "foreign-3")],
            },
            horizontal_intervals={0: [(1, 8, "foreign-row")]},
        )

        stem = next(edge for edge in edges if edge.role == "stem")
        branch = next(
            edge
            for edge in edges
            if edge.role == "branch" and edge.source == stem.source
        )
        self.assertEqual(stem.sink[0], 0)
        self.assertEqual(branch.source, stem.source)

    def test_local_collector_commits_prevalidated_terminal_paths(self) -> None:
        edges = _collector_edges(
            "collector",
            (0, 0),
            ((8, -4), (8, 4)),
            routing_source=(1, 0),
            routing_sinks=((7, -4), (7, 4)),
            forbidden=frozenset(),
            reserved=set(),
            track_intervals={},
            horizontal_intervals={},
            bounds=(-4, -8, 12, 8),
        )

        terminals = [edge for edge in edges if edge.role in {"feeder", "tap"}]
        self.assertEqual(len(terminals), 3)
        self.assertTrue(all(edge.planned_path is not None for edge in terminals))

    def test_collector_fallback_reserves_off_spine_sockets(self) -> None:
        terminals = ((0, 0), (4, 0), (8, 0))
        reserved: set[tuple[int, int]] = set()
        track_intervals: dict[int, list[tuple[int, int, str]]] = {}
        # Both horizontal exits are blocked at each terminal, forcing the
        # collector to use its empty-margin fallback.
        forbidden = frozenset(
            (x + offset, y)
            for x, y in terminals
            for offset in (-1, 1)
        )

        edges = _collector_edges(
            "collector",
            terminals[0],
            terminals[1:],
            routing_source=terminals[0],
            routing_sinks=terminals[1:],
            forbidden=forbidden,
            reserved=reserved,
            track_intervals=track_intervals,
            horizontal_intervals={},
            bounds=(-2, -2, 10, 10),
        )

        branches = [edge for edge in edges if edge.role == "branch"]
        self.assertEqual(len(branches), len(terminals))
        self.assertTrue(
            all(
                edge.source[0] == edge.sink[0]
                and abs(edge.source[1] - edge.sink[1]) == 2
                for edge in branches
            )
        )
        self.assertTrue({edge.sink for edge in branches} <= reserved)
        self.assertTrue(
            all(
                any(owner == "collector" for _low, _high, owner in track_intervals[x])
                for x, _y in (edge.source for edge in branches)
            )
        )

    def test_pin_access_leaves_component_on_pin_side(self) -> None:
        component = Component(
            kind=109,
            position=(-51, 14),
            rotation=0,
            permanent_id=1,
            word_size=2,
        )

        self.assertEqual(_pin_access_point(component, (-50, 14)), (-49, 14))
        self.assertEqual(_pin_access_point(component, (-52, 14)), (-53, 14))
        self.assertEqual(
            _pin_access_path(component, (-50, 14), length=2),
            ((-49, 14), (-48, 14)),
        )
        self.assertEqual(
            _pin_access_path(component, (-52, 14), length=1),
            ((-53, 14),),
        )

    def test_hub_stays_between_adjacent_component_layers(self) -> None:
        source = (-50, -13)
        sinks = ((-48, -17), (-48, -12), (-48, 0))

        edges = _fanout_edges(
            "lane0",
            source,
            sinks,
            routing_source=source,
            routing_sinks=sinks,
            forbidden=frozenset(),
            reserved=set(),
            track_intervals={},
            bounds=(-80, -40, 20, 20),
        )

        hub = edges[0].sink
        self.assertEqual(hub[0], -49)
        self.assertNotEqual(hub[0], -47)
        self.assertTrue(set(sinks) <= {edge.sink for edge in edges})
        tap_points = {
            edge.source
            for edge in edges
            if edge.sink in sinks and edge.source != source
        }
        self.assertEqual({point[0] for point in tap_points}, {-49})

    def test_multiple_groups_share_one_vertical_channel(self) -> None:
        source = (0, 0)
        sinks = tuple((4, y) for y in range(-12, 12, 2))

        edges = _fanout_edges(
            "wide-fanout",
            source,
            sinks,
            routing_source=source,
            routing_sinks=sinks,
            forbidden=frozenset(),
            reserved=set(),
            track_intervals={},
            bounds=(-20, -20, 20, 20),
        )

        hub_points = {
            point
            for edge in edges
            for point in (edge.source, edge.sink)
            if point not in sinks and point != source
        }
        self.assertGreater(len(hub_points), 1)
        self.assertEqual({point[0] for point in hub_points}, {1})

    def test_vertical_hub_cannot_land_on_foreign_horizontal_wire(self) -> None:
        horizontal = {
            0: [(-2, 6, "foreign")],
            4: [(-2, 6, "foreign")],
        }

        with self.assertRaisesRegex(RuntimeError, "touches a foreign wire"):
            _fanout_edges(
                "fanout",
                (0, 0),
                ((4, 0), (4, 4)),
                routing_source=(0, 0),
                routing_sinks=((4, 0), (4, 4)),
                forbidden=frozenset(),
                reserved=set(),
                track_intervals={},
                horizontal_intervals=horizontal,
                bounds=(-2, -2, 6, 6),
            )

    def test_single_sink_collector_uses_segmented_track(self) -> None:
        edges = _fanout_edges(
            "collector-lane",
            (0, 8),
            ((8, 0),),
            routing_source=(1, 8),
            routing_sinks=((7, 0),),
            forbidden=frozenset(),
            reserved=set(),
            track_intervals={},
            bounds=(-4, -4, 12, 12),
            channel_x=6,
        )

        self.assertEqual(
            {edge.role for edge in edges},
            {"feeder", "tap", "trunk"},
        )
        trunk = next(edge for edge in edges if edge.role == "trunk")
        self.assertEqual(trunk.source[0], 6)
        self.assertEqual(trunk.sink[0], 6)

    def test_global_tracks_may_cross_ordinary_tap_branch_interiors(self) -> None:
        assignments = _plan_fanout_tracks(
            (
                ("a", (0, 0), ((6, -2), (6, 2))),
                ("b", (0, -1), ((6, -3), (6, 1))),
            ),
            forbidden=frozenset(),
            bounds=(-4, -8, 10, 8),
        )

        # Only the electrical tap at x=1 is protected.  The horizontal branch
        # after that tap is an ordinary conductor, so b may cross it at x=2.
        self.assertEqual(assignments, {"a": 1, "b": 2})

    def test_track_leaves_two_cell_terminal_escape(self) -> None:
        assignments = _plan_fanout_tracks(
            (("fanout", (0, 0), ((6, 0), (6, 4))),),
            forbidden=frozenset({(5, 0)}),
            bounds=(-2, -2, 8, 8),
        )

        self.assertEqual(assignments, {"fanout": 1})

    def test_trapped_lead_endpoint_rejects_track_column(self) -> None:
        candidates, _direction, _track_min, _track_max = _fanout_track_candidates(
            (0, 0),
            ((8, 0), (8, 4)),
            forbidden=frozenset({(5, 0), (4, -1), (4, 1)}),
            bounds=(-2, -3, 10, 8),
        )

        # x=2 creates a lead ending at (4, 0).  Its forward, upper and lower
        # exits are blocked, while returning to (3, 0) would cross its own tap.
        self.assertNotIn(2, candidates)

    def test_ordinary_wires_may_cross_orthogonally(self) -> None:
        vertical_edges = {
            ((1, -1), (1, 0)): "vertical",
            ((1, 0), (1, 1)): "vertical",
        }
        points = _search(
            "horizontal",
            (0, 0),
            (2, 0),
            body=frozenset(),
            pins=frozenset(),
            edge_owner=vertical_edges,
            point_owner={(1, 0): {"vertical"}},
            bounds=(-2, -2, 4, 2),
        )

        self.assertEqual(points, ((0, 0), (1, 0), (2, 0)))

    def test_tap_point_is_a_hard_routing_obstacle(self) -> None:
        points = _search(
            "horizontal",
            (0, 0),
            (2, 0),
            body=frozenset(),
            pins=frozenset({(1, 0)}),
            edge_owner={},
            point_owner={(1, 0): {"vertical"}},
            bounds=(-2, -2, 4, 2),
        )

        self.assertNotIn((1, 0), points)

    def test_strict_monotonic_search_refuses_target_overshoot(self) -> None:
        with self.assertRaises(RuntimeError):
            _search(
                "blocked",
                (0, 0),
                (2, 0),
                body=frozenset({(1, 0)}),
                pins=frozenset(),
                edge_owner={},
                point_owner={},
                bounds=(-1, -1, 3, 1),
                strict_monotonic=True,
            )

        points = _search(
            "fallback",
            (0, 0),
            (2, 0),
            body=frozenset({(1, 0)}),
            pins=frozenset(),
            edge_owner={},
            point_owner={},
            bounds=(-1, -1, 3, 1),
        )
        self.assertGreater(len(points), 3)

    def test_physical_audit_rejects_foreign_wire_through_tap(self) -> None:
        contacts = _foreign_endpoint_contacts(
            (
                ((0, 0), (1, 0), (2, 0)),
                ((1, -1), (1, 0)),
            ),
            ("horizontal", "tap"),
        )

        self.assertEqual(
            contacts,
            [(0, 1, (1, 0), "horizontal", "tap")],
        )

    def test_physical_audit_allows_interior_wire_crossing(self) -> None:
        points = (
            ((0, 0), (1, 0), (2, 0)),
            ((1, -1), (1, 0), (1, 1)),
        )
        networks = ("horizontal", "vertical")

        self.assertEqual(_foreign_endpoint_contacts(points, networks), [])
        self.assertEqual(_non_orthogonal_foreign_contacts(points, networks), [])

    def test_foreign_wire_cannot_turn_at_occupied_point(self) -> None:
        occupied_edges = {
            ((-1, 0), (0, 0)): "first",
            ((0, 0), (0, 1)): "first",
        }

        with self.assertRaises(RuntimeError):
            _search(
                "second",
                (0, -1),
                (1, 0),
                body=frozenset({(-1, -1), (1, -1), (1, 1)}),
                pins=frozenset(),
                edge_owner=occupied_edges,
                point_owner={(0, 0): {"first"}},
                bounds=(-1, -1, 1, 1),
            )

    def test_physical_audit_rejects_complementary_bends(self) -> None:
        contacts = _non_orthogonal_foreign_contacts(
            (
                ((-1, 0), (0, 0), (0, 1)),
                ((0, -1), (0, 0), (1, 0)),
            ),
            ("first", "second"),
        )

        self.assertEqual(contacts, [((0, 0), 0, 1, "bend", "bend")])


if __name__ == "__main__":
    unittest.main()
