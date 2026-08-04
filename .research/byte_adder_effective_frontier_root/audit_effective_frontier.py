"""Audit the score rows that Byte Adder components actually import.

The executable ships default costs, but a completed upstream level replaces
that default with the score rows persisted in ``levels.txt``.  This audit
keeps three different facts separate:

* executable default cost;
* score rows genuinely registered by the game;
* research witnesses which are physical but not registered yet.

The script is read-only with respect to the game save.  It writes only the
explicit ``--output`` path and never launches Turing Complete.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Iterable


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CATALOG = (
    ROOT
    / ".research"
    / "byte_adder_component_byproduct_catalog"
    / "component-catalog-v1.json"
)
DEFAULT_LEVELS = (
    Path.home() / "AppData" / "Roaming" / "Turing Complete" / "levels.txt"
)
DEFAULT_OUTPUT = HERE / "effective-frontier-audit.json"


@dataclass(frozen=True, order=True, slots=True)
class Score:
    gate: int
    delay: int
    sample_count: int

    @property
    def energy(self) -> int:
        return self.gate * self.delay

    def record(self) -> dict[str, int]:
        return {
            "gate": self.gate,
            "delay": self.delay,
            "sample_count": self.sample_count,
            "energy": self.energy,
        }


def file_sha(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def canonical_sha(value: object) -> str:
    raw = json.dumps(
        value, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return sha256(raw).hexdigest()


def parse_score_field(raw: str) -> list[Score]:
    rows: list[Score] = []
    for token in raw.split("|"):
        token = token.strip()
        if not token:
            continue
        fields = token.split("&")
        if len(fields) != 3:
            raise ValueError(f"invalid score token: {token!r}")
        rows.append(Score(*(int(field) for field in fields)))
    return rows


def parse_levels(path: Path) -> dict[str, dict[str, Any]]:
    levels: dict[str, dict[str, Any]] = {}
    with path.open("r", encoding="utf-8", newline="") as handle:
        for line_number, raw_line in enumerate(handle, 1):
            if not raw_line.strip():
                continue
            fields = next(csv.reader([raw_line]))
            if len(fields) not in {3, 4}:
                raise ValueError(
                    f"{path}:{line_number}: expected 3 or 4 CSV fields, got {len(fields)}"
                )
            name, completed_raw, schematic = fields[:3]
            if completed_raw not in {"true", "false"}:
                raise ValueError(
                    f"{path}:{line_number}: invalid completion flag {completed_raw!r}"
                )
            if name in levels:
                raise ValueError(f"{path}:{line_number}: duplicate level {name!r}")
            levels[name] = {
                "completed": completed_raw == "true",
                "schematic": schematic,
                "scores": parse_score_field(fields[3]) if len(fields) == 4 else [],
                "line_number": line_number,
            }
    return levels


def pareto(scores: Iterable[Score]) -> list[Score]:
    unique = sorted(set(scores))
    result = []
    for candidate in unique:
        dominated = any(
            other.gate <= candidate.gate
            and other.delay <= candidate.delay
            and (other.gate < candidate.gate or other.delay < candidate.delay)
            for other in unique
        )
        if not dominated:
            result.append(candidate)
    return result


def score_pairs(scores: Iterable[Score]) -> list[tuple[int, int]]:
    return [(item.gate, item.delay) for item in scores]


def catalog_score_rows(raw: Iterable[dict[str, Any]]) -> list[Score]:
    return [
        Score(int(item["gate"]), int(item["delay"]), int(item.get("count", 1)))
        for item in raw
    ]


def build(catalog_path: Path, levels_path: Path) -> dict[str, Any]:
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    levels = parse_levels(levels_path)
    components = []
    mismatches = []
    registered_kind_count = 0

    for item in catalog["components"]:
        kind = int(item["kind"])
        unlock_levels = list(item["availability"]["unlocked_by"])
        level_rows = [
            (name, levels[name]) for name in unlock_levels if name in levels
        ]
        registered = []
        registered_sources = []
        for name, level in level_rows:
            if level["completed"] and level["scores"]:
                registered.extend(level["scores"])
                registered_sources.append(name)

        default = Score(
            int(item["cost"]["current_exe_default"]["gate"]),
            int(item["cost"]["current_exe_default"]["delay"]),
            1,
        )
        effective = pareto(registered) if registered else [default]
        catalog_imported = pareto(
            catalog_score_rows(item["cost"]["effective_imported_frontier"])
        )
        catalog_effective = Score(
            int(item["cost"]["effective_now"]["gate"]),
            int(item["cost"]["effective_now"]["delay"]),
            1,
        )
        expected_catalog = catalog_imported if catalog_imported else [default]

        checks = {
            "registered_rows_match_catalog_import": (
                score_pairs(pareto(registered)) == score_pairs(catalog_imported)
            ),
            "effective_rows_match_catalog": (
                score_pairs(effective) == score_pairs(expected_catalog)
                and (catalog_effective.gate, catalog_effective.delay)
                in score_pairs(expected_catalog)
            ),
        }
        if registered:
            registered_kind_count += 1
        if not all(checks.values()):
            mismatches.append(
                {
                    "kind": kind,
                    "symbol_name": item["symbol_name"],
                    "checks": checks,
                }
            )

        components.append(
            {
                "kind": kind,
                "symbol_name": item["symbol_name"],
                "display_name": item["prototype_display_name"],
                "semantic_role": item["semantic_role"],
                "unlock_levels": unlock_levels,
                "registered_sources": registered_sources,
                "default": default.record(),
                "registered_rows": [score.record() for score in registered],
                "effective_frontier": [score.record() for score in effective],
                "effective_source": "registered_save_rows" if registered else "exe_default",
                "catalog_checks": checks,
                "native_hidden_wireable_outputs_found": bool(
                    item["native_hidden_wireable_outputs_found"]
                ),
                "flat_expansion_available": bool(item["flat_expansion"]["available"]),
                "dominance": item["dominance"]["classification"],
            }
        )

    research_full_adder = [
        {
            "gate": 7,
            "delay": 4,
            "energy": 28,
            "status": "formal_candidate_present_but_not_registered",
            "candidate_sha256": (
                "9f83306a02ed064f7eb834b874daf786202651e73beb8d0f7ce3050f221572b2"
            ),
            "physical_use": "explicit seven-gate expansion exposes internal byproducts",
        },
        {
            "gate": 10,
            "delay": 3,
            "energy": 30,
            "status": "materialized_research_candidate_but_not_registered",
            "candidate_sha256": (
                "18b8e25952d00499f093bdad61f70a5374205bf2d71074e70881d899f04ea4a5"
            ),
            "physical_use": (
                "six ordinary gates plus two Switches; late designated input has "
                "two-level arcs"
            ),
        },
        {
            "gate": 17,
            "delay": 2,
            "energy": 34,
            "status": "strict_physical_witness_not_yet_materialized_as_level_candidate",
            "witness_sha256": (
                "c9cfc91124202330d00175289022177ebde56280897034c020823d707ed4698d"
            ),
            "physical_use": (
                "five ordinary gates, six Switches and two zero-cost normalizers"
            ),
        },
    ]
    combined_full_adder = pareto(
        [Score(16, 8, 1)]
        + [Score(row["gate"], row["delay"], 1) for row in research_full_adder]
    )

    result = {
        "schema": "tc-byte-adder-effective-component-frontier-audit-v1",
        "status": "pass" if not mismatches else "fail",
        "scope": {
            "game_launched": False,
            "save_modified": False,
            "levels_read_only": True,
            "allowed_component_kind_count": len(components),
        },
        "dependencies": {
            "component_catalog": {
                "path": str(catalog_path.resolve()),
                "sha256": file_sha(catalog_path),
            },
            "levels": {
                "path": str(levels_path.resolve()),
                "sha256": file_sha(levels_path),
            },
        },
        "summary": {
            "component_kind_count": len(components),
            "registered_kind_count": registered_kind_count,
            "default_kind_count": len(components) - registered_kind_count,
            "catalog_mismatch_count": len(mismatches),
            "all_native_hidden_wireable_outputs_false": not any(
                row["native_hidden_wireable_outputs_found"] for row in components
            ),
        },
        "components": components,
        "catalog_mismatches": mismatches,
        "full_adder_research_frontier": {
            "currently_registered": [{"gate": 16, "delay": 8, "energy": 128}],
            "unregistered_physical_witnesses": research_full_adder,
            "frontier_after_genuine_registration": [
                score.record() for score in combined_full_adder
            ],
            "atomic_selection_rule": (
                "one component instance selects one registered gate/delay row; "
                "rows cannot be mixed into a fictitious 7/3 component"
            ),
        },
        "decisions": {
            "do_not_price_full_adder_as_7_4_or_10_3_native_yet": True,
            "explicit_inline_witnesses_remain_usable": True,
            "registered_rows_replace_exe_defaults": True,
            "research_witness_is_not_server_registration": True,
        },
    }
    result["artifact_sha256"] = canonical_sha(result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=CATALOG)
    parser.add_argument("--levels", type=Path, default=DEFAULT_LEVELS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = build(args.catalog, args.levels)
    encoded = (json.dumps(result, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(encoded)
    print(
        json.dumps(
            {
                "status": result["status"],
                "output": str(args.output.resolve()),
                "sha256": sha256(encoded).hexdigest(),
                "artifact_sha256": result["artifact_sha256"],
                "component_kinds": result["summary"]["component_kind_count"],
                "catalog_mismatches": result["summary"]["catalog_mismatch_count"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
