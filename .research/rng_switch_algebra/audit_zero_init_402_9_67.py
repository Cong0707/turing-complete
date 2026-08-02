"""Generate and audit the zero-initialized 402/9/67 RNG candidate.

This script never reads or writes the live save and never launches the game.
Unlike the retracted 396/9/66 experiment, every Delay Bit is required to start
at zero.  Two phase bits implement the sequence

    (input, output) = (0, 0), (1, 0), (0, 1), (0, 1), ...

so tick zero is idle, tick one loads the seed, and ticks 2..66 emit the 65
required values.
"""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from tc_save_lab.builder import stable_permanent_id  # noqa: E402
from tc_save_lab.codec import decode_v15, encode_v15  # noqa: E402
from tc_save_lab.rng_encoded_asic import (  # noqa: E402
    EXPECTED_CYCLES,
    EXPECTED_DELAY,
    EXPECTED_GATE,
    build_rng_encoded_asic,
    verify_rng_encoded_asic,
    xorshift32,
)
from tc_save_lab.simulate import (  # noqa: E402
    initial_clocked_memory,
    simulate_clocked_ticks,
)


HERE = Path(__file__).resolve().parent
OUTPUT_DATA = HERE / "zero_init_402_9_67.data"
OUTPUT_JSON = HERE / "zero_init_402_9_67.json"
GENERATOR = SRC / "tc_save_lab" / "rng_encoded_asic.py"
RUNTIME_EVIDENCE = (
    "examples/rng/research/archive/rng_single_output_protocol/"
    "2026-08-02-单输出协议与零初态初始化.md"
)


def phase_certificate(circuit) -> dict[str, object]:
    key = "architecture/codex-rng-encoded"
    pulse_id = stable_permanent_id(key, "load-pulse-delay")
    output_id = stable_permanent_id(key, "output-active-delay")
    memory = initial_clocked_memory(circuit)
    snapshots = [[memory[pulse_id], memory[output_id]]]
    trace = simulate_clocked_ticks(
        circuit,
        inputs={"Seed": 1},
        tick_count=3,
        memory=memory,
    )
    snapshots.extend(
        [result.memory[pulse_id], result.memory[output_id]] for result in trace
    )
    expected = [[0, 0], [1, 0], [0, 1], [0, 1]]
    if snapshots != expected:
        raise RuntimeError(f"phase sequence {snapshots} != {expected}")
    expected_outputs = [{}, {}, {"RNG output": xorshift32(1)}]
    actual_outputs = [result.outputs for result in trace]
    if actual_outputs != expected_outputs:
        raise RuntimeError(
            f"three-tick output sequence {actual_outputs} != {expected_outputs}"
        )
    return {
        "state_order": ["load_pulse", "output_active"],
        "state_before_tick0_and_after_each_tick": snapshots,
        "io_control_before_ticks_0_1_2": [[0, 0], [1, 0], [0, 1]],
        "tick0": "idle; input disabled; output disabled; state remains zero",
        "tick1": "input enabled; output disabled; state captures T(seed)",
        "tick2_plus": "input disabled; output enabled; state advances by B",
    }


def main() -> None:
    circuit = build_rng_encoded_asic()
    if (circuit.gate, circuit.delay, EXPECTED_CYCLES) != (402, 9, 67):
        raise RuntimeError(
            "generator no longer describes the reviewed 402/9/67 topology"
        )
    if (EXPECTED_GATE, EXPECTED_DELAY) != (402, 9):
        raise RuntimeError("generator metric constants changed")
    delay_initial_values = [
        component.init_data for component in circuit.components if component.kind == 13
    ]
    if len(delay_initial_values) != 34 or any(delay_initial_values):
        raise RuntimeError(
            "runtime-aligned candidate requires exactly 34 zero-initialized Delay Bits"
        )

    verification = verify_rng_encoded_asic(circuit)
    phase = phase_certificate(circuit)
    payload = encode_v15(circuit)
    if decode_v15(payload) != circuit:
        raise RuntimeError("v15 round trip failed")

    OUTPUT_DATA.write_bytes(payload)
    result = {
        "schema": 1,
        "status": "offline-verified-runtime-aligned-candidate",
        "deployment_allowed_for_game_validation": True,
        "artifact": OUTPUT_DATA.name,
        "sha256": sha256(payload).hexdigest(),
        "generator_sha256": sha256(GENERATOR.read_bytes()).hexdigest(),
        "leaderboard_tuple_prediction": [402, 9, 67],
        "energy_prediction": 402 * 9 * 67,
        "reference_energy_431_9_66": 431 * 9 * 66,
        "energy_margin": 431 * 9 * 66 - 402 * 9 * 67,
        "uses_ram": False,
        "all_delay_bits_zero_initialized": True,
        "delay_bit_count": len(delay_initial_values),
        "decisive_runtime_initialization_evidence": RUNTIME_EVIDENCE,
        "phase_certificate": phase,
        "verification": verification,
        "evidence_boundary": (
            "logic, zero-initialized phase sequence, v15 round trip, connectivity, "
            "sprite geometry, and 256-seed output streams are offline verified; "
            "the game and server must recompute the final tuple"
        ),
    }
    OUTPUT_JSON.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": result["status"],
                "leaderboard_tuple_prediction": result[
                    "leaderboard_tuple_prediction"
                ],
                "energy_prediction": result["energy_prediction"],
                "energy_margin": result["energy_margin"],
                "all_delay_bits_zero_initialized": result[
                    "all_delay_bits_zero_initialized"
                ],
                "phase_states": phase["state_before_tick0_and_after_each_tick"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
