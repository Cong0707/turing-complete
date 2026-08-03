"""Audit zero-cost constant I/O controls for 65/66-cycle RNG shells.

The script is read-only outside its own result file.  It hashes the installed
runtime and level script, checks the statically extracted native score table,
and independently replays the 65-cycle and 66-cycle persistent-seed affine
machines over GF(2).
"""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import random
import sys


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from tc_save_lab.rng_encoded_asic import (  # noqa: E402
    A,
    B,
    IDENTITY,
    T,
    T_INVERSE,
    apply_matrix,
    compose,
    xorshift32,
)


GAME_ROOT = Path(r"D:\Game\Steam\steamapps\common\Turing Complete")
EXE = GAME_ROOT / "Turing Complete.exe"
TEST = GAME_ROOT / "campaign" / "rng" / "test.si"
META = GAME_ROOT / "campaign" / "rng" / "meta.txt"
SCORE_TABLE = (
    ROOT
    / "examples"
    / "rng"
    / "research"
    / "archive"
    / "rng_score_table"
    / "component_scores.json"
)
PREORDER = ROOT / ".research" / "rng_score_bypass" / "ida" / "ram" / "preorder.c"
OUT = Path(__file__).with_name("constant_io_shells.json")

CURRENT_FRONT = (401, 9, 67)
CURRENT_ENERGY = 401 * 9 * 67


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def xor_matrix(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(a ^ b for a, b in zip(left, right, strict=True))


def matrix_equal(left: tuple[int, ...], right: tuple[int, ...]) -> bool:
    return tuple(left) == tuple(right)


def score_records() -> tuple[dict[str, object], dict[int, dict[str, object]]]:
    payload = json.loads(SCORE_TABLE.read_text(encoding="utf-8"))
    records = {int(item["kind"]): item for item in payload["components"]}
    expected = {
        2: ("com_on", 0, 0, "default_table"),
        3: ("com_not_bit", 1, 1, "level_override_allowed"),
        12: ("com_switch_bit", 2, 1, "default_table"),
        13: ("com_delay_line_bit", 5, 4, "default_table"),
        62: ("com_level_input_switched", 0, 0, "default_table"),
        70: ("com_level_output_switched", 0, 0, "default_table"),
    }
    for kind, wanted in expected.items():
        item = records[kind]
        actual = (
            item["name"],
            int(item["default_gate"]),
            int(item["default_delay"]),
            item["score_source"],
        )
        if actual != wanted:
            raise AssertionError(f"kind {kind} score changed: {actual} != {wanted}")
    actual_exe_hash = file_sha256(EXE)
    if actual_exe_hash != payload["metadata"]["sha256"]:
        raise AssertionError("installed executable no longer matches extracted score table")
    return payload, records


def replay_affine_protocols() -> dict[str, object]:
    a_plus_i = xor_matrix(A, IDENTITY)
    d = compose(T, a_plus_i)
    c65 = compose(A, T_INVERSE)
    c66 = T_INVERSE

    identities = {
        "B*T=T*A": matrix_equal(compose(B, T), compose(T, A)),
        "C65*T=A": matrix_equal(compose(c65, T), A),
        "C66*T=I": matrix_equal(compose(c66, T), IDENTITY),
        "D=T*(A+I)": matrix_equal(d, compose(T, xor_matrix(A, IDENTITY))),
    }
    if not all(identities.values()):
        raise AssertionError(f"affine identity failure: {identities}")

    seeds = [0, 1, 2, 0x12345678, 0xFFFFFFFF]
    seeds.extend(1 << bit for bit in range(32))
    generator = random.Random(0x650066)
    while len(seeds) < 293:
        candidate = generator.getrandbits(32)
        if candidate not in seeds:
            seeds.append(candidate)

    callbacks65 = 0
    callbacks66 = 0
    for seed in seeds:
        q = 0
        expected = seed
        for _tick in range(65):
            expected = xorshift32(expected)
            output = apply_matrix(c65, q) ^ apply_matrix(A, seed)
            if output != expected:
                raise AssertionError("65-cycle affine output mismatch")
            q = apply_matrix(B, q) ^ apply_matrix(d, seed)
            callbacks65 += 1

        q = 0
        expected = seed
        # Tick zero captures the affine state and suppresses output.
        q = apply_matrix(B, q) ^ apply_matrix(d, seed)
        for _tick in range(1, 66):
            expected = xorshift32(expected)
            output = apply_matrix(c66, q) ^ seed
            if output != expected:
                raise AssertionError("66-cycle persistent-seed output mismatch")
            q = apply_matrix(B, q) ^ apply_matrix(d, seed)
            callbacks66 += 1

    return {
        "identities": identities,
        "seed_count": len(seeds),
        "callbacks_65": callbacks65,
        "callbacks_66": callbacks66,
        "state_initial_value": 0,
        "cycle65": {
            "state_recurrence": "q_next=B*q XOR T*(A+I)*seed",
            "output": "C65*q XOR A*seed",
            "C65": "A*T^-1",
            "invariant": "q_t=T*(A^t+I)*seed",
            "output_sequence": "A^(t+1)*seed for t=0..64",
        },
        "cycle66_persistent": {
            "state_recurrence": "q_next=B*q XOR T*(A+I)*seed",
            "output": "T^-1*q XOR seed",
            "invariant": "q_t=T*(A^t+I)*seed",
            "output_sequence": "suppressed at t=0; A^t*seed for t=1..65",
        },
    }


def maximum_gate(delay: int, cycles: int) -> int:
    return (CURRENT_ENERGY - 1) // (delay * cycles)


def main() -> None:
    table, records = score_records()
    affine = replay_affine_protocols()

    evidence = {
        "executable": {"path": str(EXE), "sha256": file_sha256(EXE)},
        "rng_test": {"path": str(TEST), "sha256": file_sha256(TEST)},
        "rng_meta": {"path": str(META), "sha256": file_sha256(META)},
        "score_table": {"path": str(SCORE_TABLE), "sha256": file_sha256(SCORE_TABLE)},
        "preorder_decompile": {"path": str(PREORDER), "sha256": file_sha256(PREORDER)},
    }
    relevant_costs = {
        records[kind]["name"]: {
            "kind": kind,
            "gate": int(records[kind]["default_gate"]),
            "delay": int(records[kind]["default_delay"]),
            "score_source": records[kind]["score_source"],
        }
        for kind in (2, 3, 12, 13, 62, 70)
    }

    gate65_d8 = maximum_gate(8, 65)
    gate65_d9 = maximum_gate(9, 65)
    gate66_d8 = maximum_gate(8, 66)
    result = {
        "schema": 1,
        "status": "verified zero-cost constant I/O controls and 65/66-cycle shells",
        "game_started": False,
        "live_save_read_or_written": False,
        "evidence": evidence,
        "score_table_executable_hash_matches": (
            evidence["executable"]["sha256"] == table["metadata"]["sha256"]
        ),
        "native_costs": relevant_costs,
        "timing_rule": {
            "component": "max(all input network arrivals) + component delay -> every output network",
            "architecture_input": "control arrival propagates to value, adding 0",
            "architecture_output": "terminal arrival is max(control,value), adding 0",
            "constant_on": "source arrival 0 with unlimited legal fanout",
        },
        "affine_replay": affine,
        "reference": {
            "front": list(CURRENT_FRONT),
            "energy": CURRENT_ENERGY,
            "strict_comparison_numerator": CURRENT_ENERGY - 1,
        },
        "cycle65_always_on": {
            "control_trace": "Input=1 and Output=1 on ticks 0..64",
            "control_components": [
                "one shared Constant On -> Architecture Input.control",
                "the same Constant On -> Architecture Output.control",
            ],
            "control_gate": 0,
            "control_delay": 0,
            "architecture_input_value_arrival": 0,
            "fixed_32_state_delay_gate": 160,
            "maximum_total_gate_at_delay8": gate65_d8,
            "maximum_logic_gate_at_delay8": gate65_d8 - 160,
            "maximum_total_gate_at_delay9": gate65_d9,
            "maximum_logic_gate_at_delay9": gate65_d9 - 160,
            "timing_limits": {
                "state_to_state_or_output_logic_delay_at_total8": 4,
                "seed_to_state_or_output_logic_delay_at_total8": 8,
                "state_to_state_or_output_logic_delay_at_total9": 5,
                "seed_to_state_or_output_logic_delay_at_total9": 9,
            },
        },
        "cycle66_persistent_seed_delay8": {
            "control_trace": "Input=1 on ticks 0..65; Output=0 at tick0 and 1 on ticks 1..65",
            "control_components": [
                "Constant On -> Architecture Input.control",
                "Constant On -> ready Delay Bit.in",
                "ready Delay Bit.out -> Architecture Output.control",
            ],
            "control_gate": 5,
            "control_delay": 4,
            "architecture_input_value_arrival": 0,
            "architecture_output_control_arrival": 4,
            "fixed_32_state_plus_ready_gate": 165,
            "maximum_total_gate_at_delay8": gate66_d8,
            "maximum_logic_gate_at_delay8": gate66_d8 - 165,
            "state_path_logic_delay_budget": 4,
            "seed_path_logic_delay_budget": 8,
        },
        "cycle66_one_shot_delay8_comparison": {
            "control_trace": "Input=NOT ready, Output=ready",
            "control_components": [
                "Constant On -> ready Delay Bit.in",
                "ready Delay Bit.out -> Architecture Output.control",
                "NOT ready -> Architecture Input.control",
            ],
            "control_gate": 6,
            "input_control_and_value_arrival": 5,
            "fixed_32_state_plus_control_gate": 166,
            "maximum_total_gate_at_delay8": gate66_d8,
            "maximum_logic_gate_at_delay8": gate66_d8 - 166,
            "load_data_logic_delay_budget": 3,
            "state_path_logic_delay_budget": 4,
            "comparison": "persistent seed saves one gate and five arrival units on the seed path",
        },
        "conclusions": [
            "65-cycle constant input/output control is exactly 0 gate / 0 delay",
            "66-cycle persistent-seed control shell is exactly one zero-init Delay Bit: 5 gate / 4 delay",
            "for 66/8/66 to beat 401/9/67, total gate <=457",
            "persistent 66-cycle leaves <=292 logic gates after 32 state delays and ready",
            "classic one-shot 66-cycle leaves <=293 logic gates and only 3 delay after gated input",
        ],
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": result["status"],
                "cycle65_d8": [gate65_d8, 8, 65],
                "cycle65_d9": [gate65_d9, 9, 65],
                "cycle66_d8": [gate66_d8, 8, 66],
                "affine_seed_count": affine["seed_count"],
                "output": str(OUT),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
