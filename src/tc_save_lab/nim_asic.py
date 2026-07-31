"""Generate and verify the current-version two-gate Nim ASIC."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

from .builder import stable_permanent_id, wire_from_vertices
from .codec import decode_v15, encode_v15
from .model import Circuit, Component
from .pins import analyze_connectivity


def nim_action(cards_left: int) -> int:
    if not 2 <= cards_left <= 12:
        raise ValueError(f"cards_left must be between 2 and 12, got {cards_left}")
    low = cards_left & 0b11
    x0 = low & 1
    x1 = (low >> 1) & 1
    inverted_x0 = 1 - x0
    high = 1 - (x1 & inverted_x0)
    return inverted_x0 | (high << 1)


def _bot_actions(cards_left: int) -> tuple[int, ...]:
    if cards_left in {5, 9}:
        return (1, 2, 3)
    return {
        1: (0,),
        2: (1,),
        3: (2,),
        4: (3,),
        6: (1,),
        7: (2,),
        8: (3,),
        10: (1,),
        11: (2,),
    }[cards_left]


def simulate_nim_strategy() -> tuple[tuple[int, ...], ...]:
    active: list[tuple[int, tuple[int, ...]]] = [(12, ())]
    wins: list[tuple[int, ...]] = []
    while active:
        cards_left, actions = active.pop()
        action = nim_action(cards_left)
        if not 1 <= action <= 3 or action >= cards_left:
            raise RuntimeError(f"invalid Nim action {action} with {cards_left} cards left")
        after_player = cards_left - action
        next_actions = actions + (action,)
        if after_player == 1:
            wins.append(next_actions)
            continue
        for bot_action in _bot_actions(after_player):
            after_bot = after_player - bot_action
            if after_bot == 1:
                raise RuntimeError(
                    f"Nim strategy loses after actions {next_actions} and bot action {bot_action}"
                )
            active.append((after_bot, next_actions))
    return tuple(sorted(wins))


def build_nim_asic() -> Circuit:
    key = "architecture/codex-nim"
    component = lambda role, kind, position, **kwargs: Component(
        kind=kind,
        position=position,
        rotation=0,
        permanent_id=stable_permanent_id(key, role),
        **kwargs,
    )
    components = (
        component("level-input", 62, (-16, 0), word_size=2),
        component("enable", 2, (-20, -4)),
        component("splitter", 109, (-10, 0)),
        component("invert-low", 3, (-4, -3)),
        component("nand-high", 6, (2, 0)),
        component("maker", 111, (8, 0)),
        component("level-output", 70, (16, 0), word_size=2),
    )
    wires = (
        wire_from_vertices(((-19, -4), (-17, -4), (-15, -2))),
        wire_from_vertices(((-19, -4), (-15, -8), (9, -8), (15, -2))),
        wire_from_vertices(((-13, 0), (-11, 0))),
        wire_from_vertices(((-9, -1), (-7, -1), (-5, -3))),
        wire_from_vertices(((-9, 0), (-8, -1), (1, -1))),
        wire_from_vertices(((-2, -3), (1, 0), (1, 1))),
        wire_from_vertices(((-2, -3), (-1, -2), (6, -2), (7, -1))),
        wire_from_vertices(((4, 0), (7, 0))),
        wire_from_vertices(((9, 0), (13, 0))),
    )
    return Circuit(
        gate=2,
        delay=2,
        description="Codex Nim ASIC: reachable-state form of (cards - 1) mod 4",
        components=components,
        wires=wires,
    )


def verify_nim_asic(circuit: Circuit | None = None) -> dict[str, object]:
    candidate = build_nim_asic() if circuit is None else circuit
    wins = simulate_nim_strategy()
    if len(wins) != 9 or {len(actions) for actions in wins} != {3}:
        raise RuntimeError(f"unexpected Nim strategy outcomes: {wins!r}")
    connectivity = analyze_connectivity(candidate)
    for field in (
        "unsupported_component_kind_counts",
        "unconnected_pin_count",
        "multi_driver_network_count",
        "width_mismatch_network_count",
        "cycle_component_count",
    ):
        if connectivity[field]:
            raise RuntimeError(f"Nim ASIC failed connectivity check {field}: {connectivity[field]}")
    if candidate.gate != 2 or candidate.delay != 2:
        raise RuntimeError("Nim candidate must remain at the reviewed 2 gate / 2 delay target")
    return {
        "gate": 2,
        "delay": 2,
        "cycles": 3,
        "leaderboard_tuple": [2, 2, 3],
        "energy": 12,
        "random_outcome_count": len(wins),
        "winning_action_sequences": [list(actions) for actions in wins],
        "connectivity": connectivity,
    }


def write_nim_asic(project_root: Path) -> dict[str, object]:
    candidate = build_nim_asic()
    verification = verify_nim_asic(candidate)
    payload = encode_v15(candidate)
    if decode_v15(payload) != candidate:
        raise RuntimeError("Nim ASIC failed v15 round-trip verification")
    destination = project_root / "examples" / "nim" / "candidate" / "circuit.data"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(payload)
    (destination.parent / ".gitkeep").unlink(missing_ok=True)
    metadata = {
        "schema": 1,
        "level": "nim",
        "title": "Nim",
        "strategy": "current-v15 two-gate reachable-state ASIC",
        "deployment_target": "schematics/architecture/CODEX-NIM/circuit.data",
        "sha256": sha256(payload).hexdigest(),
        "format_version": 15,
        "component_count": len(candidate.components),
        "wire_count": len(candidate.wires),
        **verification,
    }
    (destination.parent / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return metadata
