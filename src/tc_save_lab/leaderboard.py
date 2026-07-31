"""Read public Turing Complete level leaderboard pages and derive Pareto targets."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
import json
import re
import time
from urllib.request import Request, urlopen


BASE_URL = "https://turingcomplete.game"
ROW_PATTERN = re.compile(r"<tr\b[^>]*>(.*?)</tr>", re.IGNORECASE | re.DOTALL)
PROFILE_PATTERN = re.compile(
    r'href=["\']/profile/(\d+)["\'][^>]*>(.*?)</a>',
    re.IGNORECASE | re.DOTALL,
)
CELL_PATTERN = re.compile(r"<td\b[^>]*>(.*?)</td>", re.IGNORECASE | re.DOTALL)
TAG_PATTERN = re.compile(r"<[^>]+>")
INTEGER_PATTERN = re.compile(r"\d[\d,]*")


@dataclass(frozen=True)
class LeaderboardRow:
    profile_id: int
    username: str
    gate: int
    delay: int
    energy: int
    cycle: int | None = None
    rank: int | None = None

    def dimensions(self) -> tuple[int, ...]:
        if self.cycle is None:
            return self.gate, self.delay
        return self.gate, self.delay, self.cycle


def _text(fragment: str) -> str:
    value = TAG_PATTERN.sub(" ", fragment)
    return " ".join(unescape(value).split())


def _integer(fragment: str) -> int | None:
    matches = INTEGER_PATTERN.findall(_text(fragment))
    if not matches:
        return None
    # Large values are abbreviated in the visible cell and repeated exactly
    # inside a tooltip.  The exact tooltip value is the last integer.
    return int(matches[-1].replace(",", ""))


def parse_level_leaderboard_html(payload: str) -> tuple[LeaderboardRow, ...]:
    """Parse component and programming leaderboard tables from public HTML."""

    has_cycle = bool(re.search(r">\s*CYCLE\s*<", payload, re.IGNORECASE))
    rows: list[LeaderboardRow] = []
    last_rank: int | None = None
    for row_html in ROW_PATTERN.findall(payload):
        profile = PROFILE_PATTERN.search(row_html)
        if profile is None:
            continue
        cells = CELL_PATTERN.findall(row_html)
        expected_cells = 6 if has_cycle else 5
        if len(cells) < expected_cells:
            continue
        rank = _integer(cells[0])
        if rank is not None:
            last_rank = rank
        numeric = [_integer(cell) for cell in cells[2:]]
        if any(value is None for value in numeric):
            continue
        values = [int(value) for value in numeric if value is not None]
        if has_cycle:
            gate, delay, cycle, energy = values[:4]
        else:
            gate, delay, energy = values[:3]
            cycle = None
        expected_energy = gate * delay * (cycle if cycle is not None else 1)
        if energy != expected_energy:
            raise ValueError(
                "leaderboard energy formula mismatch: "
                f"gate={gate}, delay={delay}, cycle={cycle}, energy={energy}"
            )
        rows.append(
            LeaderboardRow(
                profile_id=int(profile.group(1)),
                username=_text(profile.group(2)),
                gate=gate,
                delay=delay,
                cycle=cycle,
                energy=energy,
                rank=last_rank,
            )
        )
    if not rows:
        raise ValueError("leaderboard page contains no score rows")
    return tuple(rows)


def pareto_front(rows: tuple[LeaderboardRow, ...]) -> tuple[LeaderboardRow, ...]:
    """Return unique rows not dominated in gate/delay[/cycle] dimensions."""

    unique: dict[tuple[int, ...], LeaderboardRow] = {}
    for row in rows:
        unique.setdefault(row.dimensions(), row)
    result: list[LeaderboardRow] = []
    for dimensions, row in unique.items():
        dominated = any(
            other != dimensions
            and all(left <= right for left, right in zip(other, dimensions))
            and any(left < right for left, right in zip(other, dimensions))
            for other in unique
        )
        if not dominated:
            result.append(row)
    return tuple(sorted(result, key=lambda row: (row.energy, row.dimensions())))


def fetch_level_leaderboard(level: str, *, timeout: float = 60.0) -> tuple[LeaderboardRow, ...]:
    url = f"{BASE_URL}/leaderboard/{level}"
    request = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 tc-save-lab/0.1",
            "Accept": "text/html,application/xhtml+xml",
            "Connection": "close",
        },
    )
    with urlopen(request, timeout=timeout) as response:
        payload = response.read().decode("utf-8")
    return parse_level_leaderboard_html(payload)


def collect_level_leaderboards(
    levels: tuple[str, ...],
    *,
    pause_seconds: float = 1.2,
    timeout: float = 60.0,
) -> dict[str, object]:
    if pause_seconds < 0:
        raise ValueError("pause_seconds cannot be negative")
    if timeout <= 0:
        raise ValueError("timeout must be positive")
    records: dict[str, object] = {}
    errors: dict[str, str] = {}
    for index, level in enumerate(levels):
        if index and pause_seconds:
            time.sleep(pause_seconds)
        try:
            rows = fetch_level_leaderboard(level, timeout=timeout)
        except Exception as exc:  # Network failures belong in the report.
            errors[level] = f"{type(exc).__name__}: {exc}"
            continue
        front = pareto_front(rows)
        records[level] = {
            "url": f"{BASE_URL}/leaderboard/{level}",
            "row_count": len(rows),
            "page_cap_suspected": len(rows) == 1000,
            "global_energy_rank1": asdict(min(rows, key=lambda row: row.energy)),
            "visible_best_gate": asdict(min(rows, key=lambda row: (row.gate, row.energy))),
            "visible_best_delay": asdict(min(rows, key=lambda row: (row.delay, row.energy))),
            "visible_pareto": [asdict(row) for row in front],
            "scope_note": (
                "The level page exposes one energy-ranked entry per user. "
                "Alternative gate/delay points can exist only on profile pages."
            ),
        }
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "source": f"{BASE_URL}/leaderboard/{{level}}",
        "scope": (
            "global_energy_rank1 is the current public minimum-energy row; visible gate, "
            "delay and Pareto fields only cover rows returned by the capped energy-ranked page"
        ),
        "levels": records,
        "errors": errors,
    }


def write_level_leaderboards(
    levels: tuple[str, ...],
    output: Path,
    *,
    pause_seconds: float = 1.2,
    timeout: float = 60.0,
) -> dict[str, object]:
    report = collect_level_leaderboards(
        levels,
        pause_seconds=pause_seconds,
        timeout=timeout,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", "utf-8")
    return report
