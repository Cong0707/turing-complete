"""Project Hub33's reviewed 103/5 ALU slice onto the phase high window.

The source circuit is read only.  Two exact embeddings are evaluated over all
2^17 Byte Adder assignments:

* ``low5`` maps real bits 3..7 to slice bits 0..4 and makes bits 5..7 propagate;
* ``high5`` makes slice bits 0..2 propagate and maps real bits 3..7 to 3..7.

Both embeddings therefore expose S3..S7 and C8 exactly.  The returned library
contains resolved BUS functions and ordinary/custom scalar outputs, but never
treats an individual Switch output pin as a reusable Boolean node.
"""

from __future__ import annotations

from dataclasses import dataclass
import importlib.util
from pathlib import Path
import sys
from typing import TypeAlias


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ANALYZER_PATH = (
    ROOT
    / ".research/byte_adder_conditional_sum_forward/analyze_hub33_g103_d5_slice.py"
)


def _load_analyzer():
    spec = importlib.util.spec_from_file_location("hub33_high_trace_upstream", ANALYZER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(ANALYZER_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


up = _load_analyzer()
Value: TypeAlias = int | tuple[int, ...]


@dataclass(frozen=True)
class Trace:
    output_drives: dict[int, object]
    conflicts: dict[int, int]
    network_z: dict[int, int]
    component_outputs: dict[tuple[int, str], object]
    network_drives: dict[int, object]
    component_inputs: dict[int, dict[str, object]]


def simulate_trace(compiled, compiled_children, source_values: dict[int, Value], mask: int) -> Trace:
    circuit = compiled.circuit
    output_values: dict[tuple[int, str], object] = {}
    component_inputs: dict[int, dict[str, object]] = {}
    evaluated: set[int] = set()
    for component_index, value in source_values.items():
        pin = next(pin for pin in compiled.pins[component_index] if pin.direction in {up.O, up.T})
        output_values[(component_index, pin.name)] = up.Drive(value, mask)
        evaluated.add(component_index)

    conflicts: dict[int, int] = {}
    network_z: dict[int, int] = {}
    resolved: dict[int, object] = {}

    def resolve(network: int):
        if network in resolved:
            return resolved[network]
        drivers = compiled.network_drivers.get(network, ())
        if not drivers or not all(pin.component_index in evaluated for pin in drivers):
            return None
        values = tuple(output_values[(pin.component_index, pin.name)] for pin in drivers)
        drive, conflict = up._combine_drives(values, mask)
        resolved[network] = drive
        conflicts[network] = conflict
        network_z[network] = mask ^ drive.active
        return drive

    pending = {
        index
        for index, component in enumerate(circuit.components)
        if component.kind not in {up.INPUT_KIND, up.OUTPUT_KIND}
    }
    while pending:
        progressed = False
        for component_index in tuple(pending):
            component = circuit.components[component_index]
            input_drives: dict[str, object] = {}
            for pin in compiled.pins[component_index]:
                if pin.direction != up.I:
                    continue
                network = compiled.pin_network.get((component_index, pin.name))
                if network is None:
                    break
                drive = resolve(network)
                if drive is None:
                    break
                input_drives[pin.name] = drive
            else:
                component_inputs[component_index] = input_drives
                values = {name: drive.value for name, drive in input_drives.items()}
                outputs: dict[str, object]
                if component.kind in {4, 6, 7, 9}:
                    left = values["in0"]
                    right = values["in1"]
                    if not isinstance(left, int) or not isinstance(right, int):
                        raise ValueError(f"word reached scalar gate {component_index}")
                    if component.kind == 4:
                        result = left & right
                    elif component.kind == 6:
                        result = mask ^ (left & right)
                    elif component.kind == 7:
                        result = left | right
                    else:
                        result = mask ^ (left | right)
                    outputs = {"out": up.Drive(result & mask, mask)}
                elif component.kind == 12:
                    enable = values["enable"]
                    data = values["in"]
                    if not isinstance(enable, int) or not isinstance(data, int):
                        raise ValueError(f"word reached scalar Switch {component_index}")
                    outputs = {"out": up.Drive(data, enable & mask)}
                elif component.kind == 16:
                    word = tuple(values[f"in{bit}"] for bit in range(8))
                    outputs = {"out": up.Drive(word, mask)}
                elif component.kind == up.SPLITTER4_KIND:
                    source = values["in"]
                    if not isinstance(source, tuple):
                        source = (source, 0, 0, 0)
                    source = source + (0,) * (4 - len(source))
                    outputs = {f"out{bit}": up.Drive(source[bit], mask) for bit in range(4)}
                elif component.kind == up.STATIC_INDEXER_KIND:
                    shift = int(component.settings[0]) if component.settings else 0
                    outputs = {
                        "out": up.Drive(
                            up._slice_word(values["in"], shift, component.word_size), mask
                        )
                    }
                elif component.kind == up.CUSTOM_KIND:
                    child = compiled_children[component.custom_id]
                    child_sources: dict[int, Value] = {}
                    for child_index, child_component in enumerate(child.circuit.components):
                        if child_component.kind == up.INPUT_KIND:
                            child_sources[child_index] = values[
                                f"port:{child_component.permanent_id}"
                            ]
                    child_result = simulate_trace(child, compiled_children, child_sources, mask)
                    outputs = {
                        f"port:{permanent_id}": drive
                        for permanent_id, drive in child_result.output_drives.items()
                    }
                    for network, conflict in child_result.conflicts.items():
                        if conflict:
                            conflicts[-(component_index + 1) * 1_000_000 - network] = conflict
                else:
                    raise ValueError(
                        f"unsupported evaluator kind {component.kind} at {component_index}"
                    )
                for name, drive in outputs.items():
                    output_values[(component_index, name)] = drive
                evaluated.add(component_index)
                pending.remove(component_index)
                progressed = True
        if not progressed:
            raise ValueError(f"simulation stalled: {sorted(pending)}")

    output_drives: dict[int, object] = {}
    for component_index, component in enumerate(circuit.components):
        if component.kind != up.OUTPUT_KIND:
            continue
        pin = next(pin for pin in compiled.pins[component_index] if pin.direction == up.I)
        drive = resolve(compiled.pin_network[(component_index, pin.name)])
        if drive is None:
            raise ValueError(f"unresolved output {component_index}")
        output_drives[component.permanent_id] = drive
    return Trace(
        output_drives,
        conflicts,
        network_z,
        output_values,
        resolved,
        component_inputs,
    )


def _word(bits: tuple[int, ...], width: int = 32, offset: int = 8) -> tuple[int, ...]:
    return (0,) * offset + bits + (0,) * (width - offset - len(bits))


def _embedding_sources(compiled_parent, mask: int, local_a, local_b, carry: int):
    a_word = _word(tuple(local_a))
    b_word = _word(tuple(local_b))
    and_word = tuple(left & right for left, right in zip(a_word, b_word))
    xor_word = tuple(left ^ right for left, right in zip(a_word, b_word))
    nor_word = tuple(mask ^ (left | right) for left, right in zip(a_word, b_word))
    xnor_bits = tuple(mask ^ (left ^ right) for left, right in zip(local_a, local_b))
    block_propagate = mask
    for bit in xor_word[8:16]:
        block_propagate &= bit
    external = {
        "A": a_word,
        "B": b_word,
        "AND": and_word,
        "XOR": xor_word,
        "NOR": nor_word,
        "XNOR": xnor_bits,
        "C": carry,
        "xor [7-15] and": block_propagate,
    }
    return {
        index: external[component.user_label]
        for index, component in enumerate(compiled_parent.circuit.components)
        if component.kind == up.INPUT_KIND
    }


def extract(engine, phase_named: dict[str, int]) -> tuple[dict[str, int], dict[str, object]]:
    parent = up.decode_circuit(up.PARENT_PATH.read_bytes())
    child = up.decode_circuit(up.CHILD_PATH.read_bytes())
    children = {child.custom_id: child}
    compiled_child = up.compile_circuit(child, {})
    compiled_parent = up.compile_circuit(parent, children)
    compiled_children = {child.custom_id: compiled_child}
    mask = engine.ALL
    real_a = [phase_named[f"a{bit}"] for bit in range(3, 8)]
    real_b = [phase_named[f"b{bit}"] for bit in range(3, 8)]
    c3 = phase_named["C3"]
    embeddings = {
        "low5": (
            [*real_a, 0, 0, 0],
            [*real_b, mask, mask, mask],
            tuple(range(5)),
        ),
        "high5": (
            [0, 0, 0, *real_a],
            [mask, mask, mask, *real_b],
            tuple(range(3, 8)),
        ),
    }
    functions: dict[str, int] = {}
    embedding_meta: dict[str, object] = {}
    expected = [phase_named[f"S{bit}"] for bit in range(3, 8)]

    for embedding, (local_a, local_b, sum_indices) in embeddings.items():
        sources = _embedding_sources(compiled_parent, mask, local_a, local_b, c3)
        trace = simulate_trace(compiled_parent, compiled_children, sources, mask)
        outputs = up._output_map(parent, up.Simulation(trace.output_drives, trace.conflicts, trace.network_z))
        sum_drive = outputs["sum"]
        cout_drive = outputs["cout"]
        if not isinstance(sum_drive.value, tuple) or not isinstance(cout_drive.value, int):
            raise RuntimeError("unexpected Hub33 output widths")
        observed = [sum_drive.value[index] for index in sum_indices]
        if observed != expected or cout_drive.value != phase_named["C8"]:
            raise RuntimeError(f"Hub33 {embedding} projection is not exact")
        conflict = 0
        for value in trace.conflicts.values():
            conflict |= value
        if conflict:
            raise RuntimeError(f"Hub33 {embedding} projection conflicts")

        scalar_count = 0
        switch_input_count = 0
        switch_input_truths: set[int] = set()
        for (component_index, pin_name), drive in trace.component_outputs.items():
            component = parent.components[component_index]
            # A single Switch driver is a pin with Z state, not a reusable net.
            if component.kind == 12:
                continue
            value = drive.value
            if isinstance(value, int):
                functions[f"hub33:{embedding}:c{component_index}:{pin_name}"] = value
                scalar_count += 1
            else:
                for bit, truth in enumerate(value):
                    functions[
                        f"hub33:{embedding}:c{component_index}:{pin_name}:b{bit}"
                    ] = truth
                    scalar_count += 1
        for network, drive in trace.network_drives.items():
            value = drive.value
            if isinstance(value, int):
                functions[f"hub33:{embedding}:net{network}"] = value
            else:
                for bit, truth in enumerate(value):
                    functions[f"hub33:{embedding}:net{network}:b{bit}"] = truth
        # Give the real Hub33 Switch controls stable semantic labels.  These
        # values are already represented by their resolved input networks; the
        # aliases do not make anything free or add a new Boolean function.  They
        # let targeted searches select the actual enable/data controls rather
        # than guessing from anonymous component/network positions.
        for component_index, input_drives in trace.component_inputs.items():
            if parent.components[component_index].kind != 12:
                continue
            for pin_name, semantic_name in (("enable", "enable"), ("in", "data")):
                drive = input_drives[pin_name]
                if not isinstance(drive.value, int):
                    raise ValueError(
                        f"word reached Hub33 Switch input {component_index}:{pin_name}"
                    )
                truth = drive.value
                functions[
                    f"hub33:{embedding}:switch{component_index}:{semantic_name}"
                ] = truth
                switch_input_count += 1
                switch_input_truths.add(truth)
        embedding_meta[embedding] = {
            "component_scalar_functions": scalar_count,
            "resolved_networks": len(trace.network_drives),
            "switch_input_labels": switch_input_count,
            "distinct_switch_input_functions": len(switch_input_truths),
            "conflict_rows": conflict.bit_count(),
            "sum_indices": list(sum_indices),
            "exact_outputs": ["S3", "S4", "S5", "S6", "S7", "C8"],
        }

    return functions, {
        "parent_sha256": __import__("hashlib").sha256(up.PARENT_PATH.read_bytes()).hexdigest(),
        "child_sha256": __import__("hashlib").sha256(up.CHILD_PATH.read_bytes()).hexdigest(),
        "embeddings": embedding_meta,
        "labeled_function_count": len(functions),
        "distinct_function_count": len(set(functions.values())),
    }
