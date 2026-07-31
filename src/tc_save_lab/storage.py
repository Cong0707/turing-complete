"""Save discovery, inventory, JSON export, and guarded atomic replacement."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import csv
import json
import os
import subprocess

from .codec import decode_v15, encode_v15
from .model import Circuit


DEFAULT_SAVE_ROOT = Path(
    os.environ.get("APPDATA", Path.home() / "AppData/Roaming")
) / "Turing Complete"


def _discover_game_root() -> Path:
    configured = os.environ.get("TC_GAME_ROOT")
    candidates = [
        Path(configured) if configured else None,
        Path(r"D:\Game\Steam\steamapps\common\Turing Complete"),
        Path(r"C:\Program Files (x86)\Steam\steamapps\common\Turing Complete"),
    ]
    return next((path for path in candidates if path and path.is_dir()), candidates[1])


DEFAULT_GAME_ROOT = _discover_game_root()


@dataclass(frozen=True)
class LevelProgress:
    level: str
    complete: bool
    selected_schematic: str
    score_history: str


def read_progress(path: Path) -> dict[str, LevelProgress]:
    records: dict[str, LevelProgress] = {}
    if not path.is_file():
        return records
    with path.open("r", encoding="utf-8", errors="strict", newline="") as stream:
        for row in csv.reader(stream):
            if not row:
                continue
            if len(row) != 4:
                raise ValueError(f"expected 4 columns in {path}, got {len(row)}: {row!r}")
            level, complete, selected, score_history = row
            records[level] = LevelProgress(
                level=level,
                complete=complete.casefold() == "true",
                selected_schematic=selected,
                score_history=score_history,
            )
    return records


def selected_circuit_path(
    save_root: Path,
    progress: dict[str, LevelProgress],
    level: str,
) -> Path:
    selected = progress.get(level)
    schematic = selected.selected_schematic if selected else "Default"
    if not schematic or schematic.casefold() == "default":
        schematic = "Default"
    return save_root / "schematics" / level / schematic / "circuit.data"


def sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def game_is_running() -> bool:
    if os.name != "nt":
        return False
    completed = subprocess.run(
        ["tasklist", "/FO", "CSV", "/NH"],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return '"turing complete.exe"' in completed.stdout.casefold()


def inspect_circuit(path: Path) -> dict[str, object]:
    payload = path.read_bytes()
    record: dict[str, object] = {
        "path": str(path),
        "size": len(payload),
        "sha256": sha256(payload).hexdigest(),
        "format_version": payload[0] if payload else None,
    }
    try:
        circuit = decode_v15(payload)
    except Exception as exc:
        record.update({"valid_v15": False, "error": str(exc)})
        return record
    record.update(
        {
            "valid_v15": True,
            "gate": circuit.gate,
            "delay": circuit.delay,
            "energy": circuit.energy,
            "component_count": len(circuit.components),
            "wire_count": len(circuit.wires),
            "custom_id": circuit.custom_id,
            "hub_id": circuit.hub_id,
        }
    )
    return record


def inventory(save_root: Path) -> list[dict[str, object]]:
    schematics = save_root / "schematics"
    if not schematics.is_dir():
        raise FileNotFoundError(f"schematics directory does not exist: {schematics}")
    return [inspect_circuit(path) for path in sorted(schematics.rglob("circuit.data"))]


def export_json(source: Path, destination: Path) -> Circuit:
    circuit = decode_v15(source.read_bytes())
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(circuit.to_dict(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return circuit


def import_json(source: Path, destination: Path) -> Circuit:
    data = json.loads(source.read_text("utf-8"))
    circuit = Circuit.from_dict(data)
    payload = encode_v15(circuit)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(payload)
    if decode_v15(destination.read_bytes()) != circuit:
        raise RuntimeError(f"written circuit failed verification: {destination}")
    return circuit


def atomic_replace_circuit(source: Path, destination: Path) -> dict[str, object]:
    if game_is_running():
        raise RuntimeError("Turing Complete.exe is running; refusing to write the save")
    payload = source.read_bytes()
    candidate = decode_v15(payload)
    if encode_v15(candidate) != payload:
        # Different valid Snappy encodings are allowed. Re-encoding still proves
        # the semantic model can be emitted and parsed before touching the save.
        decode_v15(encode_v15(candidate))
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(destination.name + ".tc-save-lab.tmp")
    try:
        with temporary.open("wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        if decode_v15(temporary.read_bytes()) != candidate:
            raise RuntimeError("temporary circuit differs from candidate")
        os.replace(temporary, destination)
        written = decode_v15(destination.read_bytes())
        if written != candidate:
            raise RuntimeError("destination verification failed after atomic replace")
    finally:
        temporary.unlink(missing_ok=True)
    return inspect_circuit(destination)
