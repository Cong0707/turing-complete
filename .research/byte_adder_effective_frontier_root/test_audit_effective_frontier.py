from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "audit_effective_frontier.py"
SPEC = importlib.util.spec_from_file_location("audit_effective_frontier", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def test_parse_score_field() -> None:
    rows = MODULE.parse_score_field("7&4&1|10&3&1|")
    assert [(row.gate, row.delay, row.sample_count) for row in rows] == [
        (7, 4, 1),
        (10, 3, 1),
    ]


def test_parse_levels(tmp_path: Path) -> None:
    path = tmp_path / "levels.txt"
    path.write_text(
        '"full_adder",true,"Default",7&4&1|10&3&1|\n'
        '"bit_switch",true,"Default",\n'
        '"sandbox",false,"TEST"\n',
        encoding="utf-8",
    )
    levels = MODULE.parse_levels(path)
    assert levels["full_adder"]["completed"] is True
    assert [(row.gate, row.delay) for row in levels["full_adder"]["scores"]] == [
        (7, 4),
        (10, 3),
    ]
    assert levels["bit_switch"]["scores"] == []
    assert levels["sandbox"]["completed"] is False


def test_pareto_does_not_mix_rows() -> None:
    rows = [
        MODULE.Score(16, 8, 1),
        MODULE.Score(7, 4, 1),
        MODULE.Score(10, 3, 1),
        MODULE.Score(17, 2, 1),
    ]
    frontier = MODULE.pareto(rows)
    assert [(row.gate, row.delay) for row in frontier] == [(7, 4), (10, 3), (17, 2)]
