from __future__ import annotations

import unittest

from tc_save_lab.leaderboard import parse_level_leaderboard_html, pareto_front


COMPONENT_HTML = """
<table>
<tr><th>RANK</th><th>USER</th><th>GATE</th><th>DELAY</th><th>ENERGY</th></tr>
<tr class="rank-one"><td>1</td><td><a href="/profile/10">甲</a></td><td>38</td><td>4</td><td>152</td></tr>
<tr><td></td><td><a href="/profile/11">乙</a></td><td>31</td><td>5</td><td>155</td></tr>
<tr><td>2</td><td><a href="/profile/12">丙</a></td><td>40</td><td>5</td><td>200</td></tr>
</table>
"""

PROGRAM_HTML = """
<table>
<tr><th>RANK</th><th>USER</th><th>GATE</th><th>DELAY</th><th>CYCLE</th><th>ENERGY</th></tr>
<tr><td>1</td><td><a href="/profile/20">A</a></td><td>1,654</td><td>11</td><td>32</td><td><div>582K<span>582,208</span></div></td></tr>
</table>
"""


class LeaderboardTests(unittest.TestCase):
    def test_parses_component_rows_and_inherited_rank(self):
        rows = parse_level_leaderboard_html(COMPONENT_HTML)
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0].rank, 1)
        self.assertEqual(rows[1].rank, 1)
        self.assertEqual(rows[1].username, "乙")
        self.assertIsNone(rows[0].cycle)

    def test_parses_programming_cycle_and_grouped_numbers(self):
        row = parse_level_leaderboard_html(PROGRAM_HTML)[0]
        self.assertEqual((row.gate, row.delay, row.cycle, row.energy), (1654, 11, 32, 582208))

    def test_pareto_front_discards_dominated_rows(self):
        rows = parse_level_leaderboard_html(COMPONENT_HTML)
        front = pareto_front(rows)
        self.assertEqual({(row.gate, row.delay) for row in front}, {(38, 4), (31, 5)})

    def test_rejects_energy_formula_mismatch(self):
        broken = COMPONENT_HTML.replace("<td>152</td>", "<td>153</td>")
        with self.assertRaisesRegex(ValueError, "energy formula mismatch"):
            parse_level_leaderboard_html(broken)


if __name__ == "__main__":
    unittest.main()
