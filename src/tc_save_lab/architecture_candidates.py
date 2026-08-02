"""Registry for reviewed architecture-level ASIC candidates."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from .binary_search_asic import write_binary_search_asic
from .capitalize_asic import write_capitalize_asic
from .circumference_asic import write_circumference_asic
from .maze_asic import write_maze_asic
from .mod4_asic import write_mod_4_asic
from .nim_asic import write_nim_asic
from .rng_natural_ram_asic import write_rng_natural_ram_asic


ArchitectureWriter = Callable[[Path], dict[str, object]]


ARCHITECTURE_CANDIDATES: dict[str, ArchitectureWriter] = {
    "binary_search": write_binary_search_asic,
    "capitalize": write_capitalize_asic,
    "circumference": write_circumference_asic,
    "mod_4": write_mod_4_asic,
    "maze": write_maze_asic,
    "nim": write_nim_asic,
    "rng": write_rng_natural_ram_asic,
}


def build_architecture_candidates(
    project_root: Path,
    *,
    levels: tuple[str, ...] = (),
) -> dict[str, object]:
    selected = tuple(dict.fromkeys(levels)) if levels else tuple(ARCHITECTURE_CANDIDATES)
    missing = sorted(set(selected) - ARCHITECTURE_CANDIDATES.keys())
    if missing:
        raise ValueError(f"关卡没有已审查的架构候选：{', '.join(missing)}")
    records = [ARCHITECTURE_CANDIDATES[level](project_root) for level in selected]
    return {"candidate_count": len(records), "candidates": records}
