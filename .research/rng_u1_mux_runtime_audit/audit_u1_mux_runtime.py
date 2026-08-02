"""Read-only audit of the RNG width-one MUX score assumption.

The script reads the current save profile, the deployed/candidate circuit and
the already captured IDA pseudocode.  It never starts Turing Complete and never
writes to the save tree.  Its only output file is result.json beside this file.
"""

from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys


HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parents[1]
SRC = PROJECT_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from tc_save_lab.codec import decode_v15  # noqa: E402


SAVE_ROOT = Path(r"C:\Users\cong\AppData\Roaming\Turing Complete")
GAME_EXE = Path(
    r"D:\Game\Steam\steamapps\common\Turing Complete\Turing Complete.exe"
)
LEVELS = SAVE_ROOT / "levels.txt"
DEPLOYED = SAVE_ROOT / "schematics" / "architecture" / "CODEX-RNG" / "circuit.data"
BYTE_MUX = SAVE_ROOT / "schematics" / "byte_mux" / "Default" / "circuit.data"
CANDIDATE = PROJECT_ROOT / ".research" / "rng_u1_mux_frontier" / "candidate.data"
CANDIDATE_REPORT = PROJECT_ROOT / ".research" / "rng_u1_mux_frontier" / "result.json"
SCORE_CAPTURE = PROJECT_ROOT / ".research" / "rng_score_runtime" / "score-functions.json"
OUTPUT = HERE / "result.json"

EXPECTED_EXE_SHA256 = "c93f5e8e826050c3f92e2b3891d26fcdfc933658614185cb9b2eb6a34c5b8d1c"
EXPECTED_SCORE_CAPTURE_SHA256 = "8b4541b956c859acb6a0bd9764edcc094b7336405b6e30fa3d11edde01146375"
MUX_KIND = 42


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_level_frontier(text: str, level: str) -> dict[str, object]:
    pattern = re.compile(
        rf'"{re.escape(level)}",(true|false),"([^"]*)",(\d+)&(\d+)&(\d+)\|'
    )
    match = pattern.search(text)
    if match is None:
        raise AssertionError(f"level frontier not found: {level}")
    return {
        "solved": match.group(1) == "true",
        "schematic": match.group(2),
        "gate": int(match.group(3)),
        "delay": int(match.group(4)),
        "score": int(match.group(5)),
    }


def imported_gate_cost(kind: int, word_size: int, imported_gate: int) -> int:
    """Exact integer branch used by get_gate_cost for kind 42 et al."""

    if kind != MUX_KIND:
        raise ValueError("this audit only models kind 42")
    quotient, remainder = divmod(imported_gate, 8)
    if remainder > 3:
        return (quotient + 1) * word_size + remainder - 8
    return quotient * word_size + remainder


def imported_delay_cost(kind: int, imported_delay: int) -> int:
    """Kind 42 returns the imported delay unchanged in the captured runtime."""

    if kind != MUX_KIND:
        raise ValueError("this audit only models kind 42")
    return imported_delay


def require_runtime_evidence(capture: dict[str, object]) -> dict[str, object]:
    functions = {
        item["name"]: item
        for item in capture["functions"]
        if isinstance(item, dict) and isinstance(item.get("name"), str)
    }
    gate_name = "get_gate_cost__modelZscores_u2232"
    delay_name = "get_delay_cost__modelZscores_u2270"
    gate = functions[gate_name]
    delay = functions[delay_name]
    gate_code = gate["pseudocode"]
    delay_code = delay["pseudocode"]

    for needle in (
        "case 0x2Au:",
        "if ( a3 % 8 > 3 )",
        "v13 = a3 / 8 + 1;",
        "v15 = a3 / 8 * v20;",
        "v14 = v15 + a3 % 8;",
    ):
        if needle not in gate_code:
            raise AssertionError(f"gate-cost evidence missing: {needle}")
    for needle in (
        "if ( a1 >= 0x26u )",
        "0x84048000000000i64",
        "v28 = a3;",
    ):
        if needle not in delay_code:
            raise AssertionError(f"delay-cost evidence missing: {needle}")

    if not ((1 << MUX_KIND) & 0x84048000000000):
        raise AssertionError("kind 42 is not in the captured direct-delay bit mask")
    return {
        "gate_function": {"name": gate_name, "address": gate["address"]},
        "delay_function": {"name": delay_name, "address": delay["address"]},
        "kind42_in_direct_delay_mask": True,
    }


def circuit_record(path: Path) -> tuple[object, dict[str, object]]:
    payload = path.read_bytes()
    circuit = decode_v15(payload)
    counts = Counter(component.kind for component in circuit.components)
    mux_widths = Counter(
        component.word_size for component in circuit.components if component.kind == MUX_KIND
    )
    return circuit, {
        "path": str(path),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "bytes": len(payload),
        "format_version": payload[0],
        "stored_gate": circuit.gate,
        "stored_delay": circuit.delay,
        "component_count": len(circuit.components),
        "wire_count": len(circuit.wires),
        "component_kind_counts": {str(key): value for key, value in sorted(counts.items())},
        "kind42_word_sizes": {str(key): value for key, value in sorted(mux_widths.items())},
        "custom_id": circuit.custom_id,
        "design_bytes": len(circuit.design),
        "dependency_count": len(circuit.dependencies),
    }


def main() -> None:
    required = (
        GAME_EXE,
        LEVELS,
        DEPLOYED,
        BYTE_MUX,
        CANDIDATE,
        CANDIDATE_REPORT,
        SCORE_CAPTURE,
    )
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"required audit inputs missing: {missing}")

    exe_hash = sha256(GAME_EXE)
    capture_hash = sha256(SCORE_CAPTURE)
    if exe_hash != EXPECTED_EXE_SHA256:
        raise AssertionError(f"game executable changed: {exe_hash}")
    if capture_hash != EXPECTED_SCORE_CAPTURE_SHA256:
        raise AssertionError(f"score capture changed: {capture_hash}")

    level_text = LEVELS.read_text(encoding="utf-8")
    byte_mux_frontier = parse_level_frontier(level_text, "byte_mux")
    rng_frontier = parse_level_frontier(level_text, "rng")
    if (byte_mux_frontier["gate"], byte_mux_frontier["delay"]) != (34, 3):
        raise AssertionError(f"byte_mux frontier changed: {byte_mux_frontier}")

    capture = json.loads(SCORE_CAPTURE.read_text(encoding="utf-8"))
    runtime_evidence = require_runtime_evidence(capture)
    candidate_report = json.loads(CANDIDATE_REPORT.read_text(encoding="utf-8"))

    deployed_circuit, deployed_record = circuit_record(DEPLOYED)
    candidate_circuit, candidate_record = circuit_record(CANDIDATE)
    byte_mux_circuit, byte_mux_record = circuit_record(BYTE_MUX)
    deployed_bytes = DEPLOYED.read_bytes()
    candidate_bytes = CANDIDATE.read_bytes()
    if deployed_bytes != candidate_bytes:
        raise AssertionError("deployed RNG is not byte-identical to the audited candidate")
    if deployed_circuit != candidate_circuit:
        raise AssertionError("decoded deployed/candidate circuits differ")

    muxes = [component for component in candidate_circuit.components if component.kind == MUX_KIND]
    if len(muxes) != 34 or any(component.word_size != 1 for component in muxes):
        raise AssertionError("candidate is not the expected 34 x U1 kind-42 MUX circuit")
    claimed_tuple = tuple(candidate_report["leaderboard_tuple"])
    if claimed_tuple != (350, 10, 67):
        raise AssertionError(f"candidate report changed: {claimed_tuple}")

    imported_gate = int(byte_mux_frontier["gate"])
    imported_delay = int(byte_mux_frontier["delay"])
    u1_gate = imported_gate_cost(MUX_KIND, 1, imported_gate)
    u1_delay = imported_delay_cost(MUX_KIND, imported_delay)
    if (u1_gate, u1_delay) != (6, 3):
        raise AssertionError(f"unexpected U1 MUX runtime cost: {(u1_gate, u1_delay)}")

    claimed_mux_gate = 1
    corrected_gate = candidate_circuit.gate + len(muxes) * (u1_gate - claimed_mux_gate)
    corrected_delay = candidate_circuit.delay
    cycles = claimed_tuple[2]
    corrected_energy = corrected_gate * corrected_delay * cycles
    if (corrected_gate, corrected_delay, cycles, corrected_energy) != (520, 10, 67, 348400):
        raise AssertionError("corrected score arithmetic changed")

    width_table = {
        str(width): {
            "gate": imported_gate_cost(MUX_KIND, width, imported_gate),
            "delay": imported_delay_cost(MUX_KIND, imported_delay),
        }
        for width in range(1, 9)
    }

    result = {
        "schema": 1,
        "status": "rejected: candidate score ledger contradicts current runtime",
        "read_only": True,
        "game_started": False,
        "inputs": {
            "game_exe": {"path": str(GAME_EXE), "sha256": exe_hash},
            "levels": {"path": str(LEVELS), "sha256": sha256(LEVELS)},
            "score_capture": {"path": str(SCORE_CAPTURE), "sha256": capture_hash},
            "candidate_report": {
                "path": str(CANDIDATE_REPORT),
                "sha256": sha256(CANDIDATE_REPORT),
            },
        },
        "profile_frontiers": {"byte_mux": byte_mux_frontier, "rng": rng_frontier},
        "runtime_evidence": runtime_evidence,
        "runtime_formula": {
            "gate": "q=imported_gate div 8; r=imported_gate mod 8; r>3 ? (q+1)*width+r-8 : q*width+r",
            "delay_kind42": "imported_delay",
            "imported_byte_mux": [imported_gate, imported_delay],
            "kind42_width_table": width_table,
        },
        "circuits": {
            "candidate": candidate_record,
            "deployed": deployed_record,
            "byte_mux_file": byte_mux_record,
            "candidate_equals_deployed": True,
            "byte_mux_file_header_is_not_profile_frontier": [
                byte_mux_circuit.gate,
                byte_mux_circuit.delay,
            ],
        },
        "finding": {
            "mux_count": len(muxes),
            "mux_word_size": 1,
            "claimed_u1_mux": [1, 3],
            "runtime_u1_mux": [u1_gate, u1_delay],
            "claimed_rng": list(claimed_tuple),
            "corrected_rng": [corrected_gate, corrected_delay, cycles],
            "claimed_energy": int(candidate_report["energy"]),
            "corrected_energy": corrected_energy,
            "verified_reference": [402, 9, 67],
            "verified_reference_energy": 402 * 9 * 67,
            "corrected_candidate_minus_reference": corrected_energy - 402 * 9 * 67,
        },
        "identity_risk": {
            "custom_id": candidate_circuit.custom_id,
            "design_bytes": len(candidate_circuit.design),
            "assessment": "standalone v15 payload; loading/submission identity requires separate game verification",
        },
        "conclusion": (
            "The 34 U1 MUX candidate may be structurally valid, but the current executable "
            "charges each kind-42 width-one MUX as 6/3, not 1/3. Its corrected score is "
            "520/10/67, so it is not an RNG leaderboard frontier."
        ),
    }
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["finding"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
