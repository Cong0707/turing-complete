"""Exhaust the fixed 402/9/67 RNG phase-controller saving boundary.

This script is deliberately independent of the live save and game process.  It
uses the checked-in 402 candidate's exact mode-pair certificate, and proves a
stronger function-level lower bound for the zero-initialized controller than
is needed for the native one-gate component set.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from hashlib import sha256
from itertools import combinations_with_replacement, product
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from tc_save_lab.rng_encoded_asic import MODE_PAIRS, T  # noqa: E402


OUT = Path(__file__).with_name("result.json")


@dataclass(frozen=True)
class NativeCost:
    kind: str
    gate: int | str
    delay: int
    outputs: str
    relevance: str


NATIVE_COSTS = (
    NativeCost("Constant / wire / Maker / Splitter", 0, 0, "rewiring", "no state or predicate"),
    NativeCost("NOT / AND / NAND / OR / NOR Bit", 1, 1, "one Boolean", "unit-gate universe"),
    NativeCost("Decoder 1", 1, 1, "x and NOT x", "its restricted dual output is enumerated exactly"),
    NativeCost("Bit Switch", 2, 1, "one tristate", "already exceeds the <=11 residual budget"),
    NativeCost("AND3 / OR3", 2, 2, "one Boolean", "already exceeds the <=11 residual budget"),
    NativeCost("XOR / U1 Word XOR", 3, 2, "one Boolean", "user-verified current cost"),
    NativeCost("Delay Bit", 5, 4, "one stored bit", "all-zero initial state"),
    NativeCost("Delay Word U<w>", "5*w", 4, "w stored bits", "packing gives no memory discount"),
    NativeCost("Decoder 2", 11, 2, "four one-hot", "current profile frontier"),
    NativeCost("Decoder 3", 79, 12, "eight one-hot", "current profile frontier"),
)


def truth_mask(nbits: int, fn) -> int:
    result = 0
    for state in range(1 << nbits):
        result |= (int(bool(fn(state))) & 1) << state
    return result


def raw_signals(nbits: int) -> dict[str, int]:
    universe = (1 << (1 << nbits)) - 1
    result = {"0": 0, "1": universe}
    for bit in range(nbits):
        result[f"q{bit}"] = truth_mask(nbits, lambda state, bit=bit: state >> bit & 1)
    return result


def value(mask: int, state: int) -> int:
    return mask >> state & 1


def required_control(tick: int) -> tuple[int, int]:
    if tick == 0:
        return 0, 0
    if tick == 1:
        return 1, 0
    return 0, 1


def check_assignment(
    nbits: int,
    signal_masks: tuple[int, ...],
    assignment: tuple[int, ...],
) -> tuple[bool, tuple[int, ...]]:
    """Check forever by running beyond the finite-state repetition bound."""

    state = 0
    trace: list[int] = []
    horizon = 3 + (1 << nbits)
    for tick in range(horizon):
        trace.append(state)
        input_enable = value(signal_masks[assignment[nbits]], state)
        output_enable = value(signal_masks[assignment[nbits + 1]], state)
        if (input_enable, output_enable) != required_control(tick):
            return False, tuple(trace)
        next_state = 0
        for bit in range(nbits):
            next_state |= value(signal_masks[assignment[bit]], state) << bit
        state = next_state
    return True, tuple(trace)


def search_signal_pool(nbits: int, signals: dict[str, int]) -> dict[str, object]:
    names = tuple(signals)
    masks = tuple(signals.values())
    trials = 0
    for assignment in product(range(len(names)), repeat=nbits + 2):
        trials += 1
        valid, trace = check_assignment(nbits, masks, assignment)
        if valid:
            return {
                "status": "SAT",
                "trials": trials,
                "assignment": {
                    **{f"next_q{bit}": names[assignment[bit]] for bit in range(nbits)},
                    "input_enable": names[assignment[nbits]],
                    "output_enable": names[assignment[nbits + 1]],
                },
                "state_trace": list(trace),
            }
    return {"status": "UNSAT", "trials": trials}


def ideal_arbitrary_single_predicate_probe(nbits: int) -> dict[str, object]:
    """Probe the nonexistent one-gate LUT boundary.

    A SAT result is diagnostic, not a native candidate.  The real proof is the
    exact legal-component enumeration below.
    """

    raw = raw_signals(nbits)
    universe = (1 << (1 << nbits)) - 1
    function_count = universe + 1
    trials = 0
    encodings_seen: set[tuple[int, int, int]] = set()
    for predicate in range(function_count):
        signals = dict(raw)
        signals["f"] = predicate
        names = tuple(signals)
        masks = tuple(signals.values())
        for assignment in product(range(len(names)), repeat=nbits + 2):
            trials += 1
            valid, trace = check_assignment(nbits, masks, assignment)
            if len(trace) >= 3 and len({trace[0], trace[1], trace[2]}) == 3:
                encodings_seen.add((trace[0], trace[1], trace[2]))
            if valid:
                return {
                    "status": "SAT_IN_NON_NATIVE_IDEAL_MODEL",
                    "predicate_mask": predicate,
                    "trials": trials,
                    "assignment": {
                        **{f"next_q{bit}": names[assignment[bit]] for bit in range(nbits)},
                        "input_enable": names[assignment[nbits]],
                        "output_enable": names[assignment[nbits + 1]],
                    },
                    "state_trace": list(trace),
                    "encodings_seen_before_sat": len(encodings_seen),
                    "native_exclusion": (
                        "the predicate q0 AND NOT q1 needs two basic gates or "
                        "a Decoder-2 minterm; no legal one-gate LUT exists"
                    ),
                }
    return {
        "status": "UNSAT",
        "predicate_count": function_count,
        "trials": trials,
        "distinct_three_phase_encodings_reached": len(encodings_seen),
        "possible_fixed_zero_encodings": ((1 << nbits) - 1) * ((1 << nbits) - 2),
    }


def ideal_dual_polarity_probe(nbits: int = 2) -> dict[str, object]:
    """Show exactly what nonexistent one-gate primitive would beat 12 gates.

    This is not a lower-bound model: it deliberately grants both f and NOT f
    for one gate.  Its SAT witness identifies the missing OR/NOR dual-output
    primitive and prevents us from accidentally treating Decoder-1 as an
    arbitrary dual-output LUT.
    """

    raw = raw_signals(nbits)
    universe = (1 << (1 << nbits)) - 1
    trials = 0
    for predicate in range(universe + 1):
        signals = dict(raw)
        signals["f"] = predicate
        signals["NOT f"] = universe ^ predicate
        names = tuple(signals)
        masks = tuple(signals.values())
        for assignment in product(range(len(names)), repeat=nbits + 2):
            trials += 1
            valid, trace = check_assignment(nbits, masks, assignment)
            if valid:
                return {
                    "status": "SAT_IN_NON_NATIVE_IDEAL_MODEL",
                    "predicate_mask": predicate,
                    "predicate_truth_by_state_00_01_10_11": [
                        value(predicate, state) for state in range(1 << nbits)
                    ],
                    "interpretation": "f=NOR(q0,q1), NOT f=OR(q0,q1)",
                    "trials": trials,
                    "assignment": {
                        **{f"next_q{bit}": names[assignment[bit]] for bit in range(nbits)},
                        "input_enable": names[assignment[nbits]],
                        "output_enable": names[assignment[nbits + 1]],
                    },
                    "state_trace": list(trace),
                    "native_exclusion": (
                        "Decoder 1 emits x/NOT x only for one raw select input; "
                        "no legal one-gate component emits OR and NOR together"
                    ),
                }
    raise AssertionError("dual-polarity ideal model unexpectedly has no witness")


def exhaustive_exact_native_unit_gate(nbits: int = 2) -> dict[str, object]:
    raw = raw_signals(nbits)
    raw_items = tuple(raw.items())
    topologies: list[tuple[str, dict[str, int]]] = [("no-gate", dict(raw))]

    for source_name, source in raw_items:
        signals = dict(raw)
        universe = (1 << (1 << nbits)) - 1
        signals[f"not({source_name})"] = universe ^ source
        topologies.append((f"NOT({source_name})", signals))

        decoder_signals = dict(raw)
        decoder_signals[f"decoder0({source_name})"] = universe ^ source
        decoder_signals[f"decoder1({source_name})"] = source
        topologies.append((f"Decoder1({source_name})", decoder_signals))

    binary = {
        "AND": lambda left, right, universe: left & right,
        "NAND": lambda left, right, universe: universe ^ (left & right),
        "OR": lambda left, right, universe: left | right,
        "NOR": lambda left, right, universe: universe ^ (left | right),
    }
    universe = (1 << (1 << nbits)) - 1
    for (left_name, left), (right_name, right) in combinations_with_replacement(raw_items, 2):
        for gate_name, operation in binary.items():
            signals = dict(raw)
            signals[f"{gate_name}({left_name},{right_name})"] = operation(left, right, universe)
            topologies.append((f"{gate_name}({left_name},{right_name})", signals))

    trials = 0
    by_family: Counter[str] = Counter()
    for topology, signals in topologies:
        result = search_signal_pool(nbits, signals)
        trials += int(result["trials"])
        by_family[topology.split("(", 1)[0]] += int(result["trials"])
        if result["status"] == "SAT":
            return {
                "status": "SAT",
                "topology": topology,
                "assignment": result["assignment"],
                "state_trace": result["state_trace"],
                "trials": trials,
            }
    return {
        "status": "UNSAT",
        "topology_count": len(topologies),
        "trials": trials,
        "trials_by_family": dict(sorted(by_family.items())),
        "covered": [
            "no gate",
            "NOT Bit and equivalent U1 Word NOT",
            "AND/NAND/OR/NOR Bit and equivalent U1 Word gates",
            "Decoder 1 including both outputs",
        ],
    }


def verify_two_gate_witness() -> dict[str, object]:
    """Replay the current OR+NOT controller as a constructive upper bound."""

    state = 0
    rows = []
    for tick in range(10):
        load = state & 1
        output = state >> 1 & 1
        phase_any = load | output
        next_load = 1 ^ phase_any
        next_output = phase_any
        rows.append(
            {
                "tick": tick,
                "state": f"{load}{output}",
                "input_enable": load,
                "output_enable": output,
                "phase_or": phase_any,
                "next_state": f"{next_load}{next_output}",
            }
        )
        if (load, output) != required_control(tick):
            raise AssertionError("known controller witness failed")
        state = next_load | next_output << 1
    return {
        "status": "SAT",
        "memory_gate": 10,
        "logic_gate": 2,
        "total_gate": 12,
        "maximum_control_delay": 6,
        "netlist": [
            "a = OR(load_delay.out, output_delay.out)",
            "load_delay.in = NOT(a)",
            "output_delay.in = a",
            "ArchitectureInput.control = load_delay.out",
            "ArchitectureOutput.control = output_delay.out",
        ],
        "trace": rows,
    }


def gf2_rank(rows: tuple[int, ...] | list[int], width: int) -> int:
    work = list(rows)
    rank = 0
    for column in range(width - 1, -1, -1):
        pivot = next((index for index in range(rank, len(work)) if work[index] >> column & 1), None)
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        for index in range(len(work)):
            if index != rank and work[index] >> column & 1:
                work[index] ^= work[rank]
        rank += 1
    return rank


def mode_bank_certificate() -> dict[str, object]:
    pairs = tuple(sorted(MODE_PAIRS))
    if len(pairs) != 47 or len(set(pairs)) != 47:
        raise AssertionError("the checked-in 47-pair certificate changed")
    if gf2_rank(list(T), 32) != 32:
        raise AssertionError("encoded state transform is no longer invertible")

    by_seed = Counter(seed for seed, _ in pairs)
    by_state = Counter(state for _, state in pairs)
    return {
        "pair_count": len(pairs),
        "unique_pair_count": len(set(pairs)),
        "encoded_transform_rank": gf2_rank(list(T), 32),
        "all_zero_seed_trace": "all seed, encoded-state, mode-OR, and XOR data signals are numeric zero forever",
        "distinctness_proof": [
            "during load, M(i,j)=seed_i, so different i are distinguished by a basis seed",
            "during steady state, M(i,j)=q_j; invertible T makes different q coordinates independent",
            "therefore M(i,j)=M(k,l) iff (i,j)=(k,l)",
        ],
        "decoder1_exclusion": "at the all-zero data point every M is 0, so no two M outputs are complements",
        "seed_fanout": dict(sorted(by_seed.items())),
        "state_fanout": dict(sorted(by_state.items())),
        "pairs": [list(pair) for pair in pairs],
    }


def main() -> None:
    exact = exhaustive_exact_native_unit_gate(2)
    broad_two = ideal_arbitrary_single_predicate_probe(2)
    ideal_dual = ideal_dual_polarity_probe(2)
    if exact["status"] != "UNSAT":
        raise AssertionError("unexpected <=11 controller witness")

    # Three stored bits are enumerated for completeness, but their 15-gate
    # memory floor already exceeds both the 11-gate target and current 12-gate
    # controller before any combinational component is placed.
    three_encodings = {
        "stored_bits": 3,
        "fixed_zero_idle_encoding_count": 7 * 6,
        "memory_gate_floor": 15,
        "target_gate": 11,
        "status": "PRUNED_BY_STRICT_COST_LOWER_BOUND",
        "note": "42 ordered choices of distinct load/steady codes with idle fixed at 000",
    }

    witness = verify_two_gate_witness()
    modes = mode_bank_certificate()

    current_mode_phase = 47 + 12
    lower_mode_phase = modes["pair_count"] + witness["total_gate"]
    fixed_other = 32 * 5 + 61 * 3
    result = {
        "schema": 1,
        "scope": "fixed 402/9/67 encoded data plane and exact 47 mode-pair functions",
        "status": "UNSAT for any net gate saving; current 402 shell is gate-minimal in scope",
        "game_started": False,
        "live_save_read_or_written": False,
        "costs": [cost.__dict__ for cost in NATIVE_COSTS],
        "protocol": {
            "controls": ["00", "10", "01", "01", "..."],
            "all_delay_initial_values": 0,
            "cycles": 67,
            "static_delay_limit": 9,
        },
        "state_count_lower_bound": {
            "required_observable_phases": 3,
            "minimum_stored_bits": 2,
            "minimum_delay_gate": 10,
            "reason": "a deterministic one-bit machine has at most two states but the three control pairs are distinct",
        },
        "two_bit_fixed_zero_phase_encodings": [
            [0, load, steady]
            for load in range(1, 4)
            for steady in range(1, 4)
            if steady != load
        ],
        "encoding_coverage_note": (
            "the exact circuit enumeration is stronger than checking the six "
            "single-steady encodings: it also permits the fourth code and any "
            "steady-state cycle whose controls remain 01"
        ),
        "two_bit_unit_native_enumeration": exact,
        "non_native_arbitrary_single_output_probe": broad_two,
        "non_native_dual_polarity_probe": ideal_dual,
        "three_bit_encodings": three_encodings,
        "minimum_controller": witness,
        "mode_bank": modes,
        "joint_sharing_lower_bound": {
            "zero_seed_reduction": [
                "seed=0 keeps every fixed data-plane signal numeric zero forever",
                "Architecture Input Z and active zero are indistinguishable to ordinary gates; only illegal conflict can distinguish driver presence",
                "therefore any borrowed mode output is only constant zero on this required test",
                "a 47-mode bank plus <=1 private unit gate reduces to the exact native unit-gate enumeration, which is UNSAT",
            ],
            "mode_gate_floor": 47,
            "additional_controller_logic_floor": 2,
            "phase_delay_floor": 10,
            "mode_plus_phase_floor": lower_mode_phase,
            "current_mode_plus_phase": current_mode_phase,
            "maximum_net_saving": current_mode_phase - lower_mode_phase,
        },
        "fixed_402_lower_bound": {
            "32_state_delay": 32 * 5,
            "61_xor": 61 * 3,
            "47_mode_functions": 47,
            "2_phase_delay": 2 * 5,
            "phase_logic": 2,
            "total_gate": fixed_other + lower_mode_phase,
            "delay_witness": "state/phase Delay 4 + mode OR 1 + XOR 2 + XOR 2 = 9",
            "conclusion": "no <=401/9/67 candidate exists without changing the fixed data plane or protocol",
        },
        "excluded_as_non_saving": {
            "one_Bit_Switch": "2 gates; at best ties OR+NOT and has only one tristate output",
            "U2_Delay_Word": "10 gates, exactly the same memory cost as two Delay Bits",
            "U2_bitwise_gate": "at least 2 gates for two independent lanes, so packing creates no discount",
            "Decoder_2": "11 gates in the current profile before the 10-gate state memory",
            "Decoder_3": "79 gates / 12 delay in the current profile",
        },
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "exact_trials": exact["trials"],
        "relaxed_trials": broad_two["trials"],
        "fixed_gate_lower_bound": result["fixed_402_lower_bound"]["total_gate"],
        "result_sha256": sha256(OUT.read_bytes()).hexdigest(),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
