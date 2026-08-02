"""Verify the reviewed 66-cycle RNG word-bus handshake offline."""

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from tc_save_lab.analysis import wire_points  # noqa: E402
from tc_save_lab.pins import positioned_pins  # noqa: E402
from tc_save_lab.rng_asic import build_rng_asic, xorshift32  # noqa: E402
from tc_save_lab.simulate import simulate_clocked_ticks  # noqa: E402


def pins(component) -> dict[str, tuple[int, int]]:
    return {pin.name: pin.position for pin in positioned_pins(component)}


def main() -> None:
    circuit = build_rng_asic()
    architecture_input = next(component for component in circuit.components if component.kind == 62)
    architecture_output = next(component for component in circuit.components if component.kind == 70)
    feedback_switch = next(component for component in circuit.components if component.kind == 25)
    state_delay = next(component for component in circuit.components if component.kind == 55)

    assert architecture_input.word_size == feedback_switch.word_size == state_delay.word_size == 32
    assert {
        name: (position[0] - architecture_input.position[0], position[1] - architecture_input.position[1])
        for name, position in pins(architecture_input).items()
    } == {"control": (1, -2), "value": (3, 0)}
    assert {
        name: (position[0] - feedback_switch.position[0], position[1] - feedback_switch.position[1])
        for name, position in pins(feedback_switch).items()
    } == {"enable": (0, 1), "in": (-1, 0), "out": (2, 0)}

    # Both tristate outputs terminate on the same state-delay input network.
    state_input = pins(state_delay)["in"]
    incident = []
    for wire in circuit.wires:
        points = wire_points(wire)
        if state_input in (points[0], points[-1]):
            incident.append({points[0], points[-1]})
    assert {pins(architecture_input)["value"], state_input} in incident
    assert {pins(feedback_switch)["out"], state_input} in incident

    seed = 0x12345678
    trace = simulate_clocked_ticks(circuit, inputs={"Seed": seed}, tick_count=66)
    assert trace[0].outputs == {}
    expected = seed
    for tick in range(1, 66):
        expected = xorshift32(expected)
        assert trace[tick].outputs == {"RNG output": expected}

    print("kind 62: control=(+1,-2), value=(+3,0) U32 tristate")
    print("kind 25: enable=(0,+1), in=(-1,0), out=(+2,0) U32 tristate")
    print("tick 0: input drives seed, feedback Z, output disabled")
    print("ticks 1..65: input Z, feedback drives F(state), output enabled")
    print(f"verified outputs=65, final=0x{expected:08x}")


if __name__ == "__main__":
    main()
