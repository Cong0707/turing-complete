"""Inventory every circuit in downloaded public Hub packages.

The scan is intentionally structural.  A serialized score match is only a
lead: the report also records ports, primitive Add instances, custom
dependencies, hashes, and whether recursive gate accounting is complete.
"""

from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re

from tc_save_lab.codec import decode_circuit


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DEFAULT_PUBLIC_ROOT = ROOT / ".research" / "byte_adder_public"
DEFAULT_LIST = HERE / "hub-list-public-metadata.json"
DEFAULT_OUTPUT = HERE / "downloaded-public-hub-scan.json"
CUSTOM_KIND = 78
INPUT_KIND = 79
OUTPUT_KIND = 81
TARGET_SCORES = {(103, 5), (91, 6), (88, 6), (79, 7), (154, 4)}
ADDER_PATTERN = re.compile(r"add|adder|carry|sum|cla|arithmetic|alu", re.IGNORECASE)


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def port_record(component) -> dict[str, object]:
    return {
        "direction": "input" if component.kind == INPUT_KIND else "output",
        "label": component.user_label,
        "word_size": component.word_size,
        "permanent_id": component.permanent_id,
    }


def looks_like_byte_adder(ports: list[dict[str, object]]) -> dict[str, bool]:
    inputs = [port for port in ports if port["direction"] == "input"]
    outputs = [port for port in ports if port["direction"] == "output"]
    normalized_inputs = {re.sub(r"[^a-z0-9]", "", str(port["label"]).lower()) for port in inputs}
    normalized_outputs = {re.sub(r"[^a-z0-9]", "", str(port["label"]).lower()) for port in outputs}
    exact_width_shape = sorted(int(port["word_size"]) for port in inputs) == [1, 8, 8] and sorted(
        int(port["word_size"]) for port in outputs
    ) == [1, 8]
    label_shape = (
        any(label in normalized_inputs for label in {"a", "inputa", "ina"})
        and any(label in normalized_inputs for label in {"b", "inputb", "inb"})
        and any("cin" in label or "carryin" in label for label in normalized_inputs)
        and any("sum" in label for label in normalized_outputs)
        and any("cout" in label or "carryout" in label for label in normalized_outputs)
    )
    return {"exact_width_shape": exact_width_shape, "label_shape": label_shape}


def analyze_hub(hub_root: Path, listing: dict[int, dict[str, object]]) -> dict[str, object]:
    hub_id = int(hub_root.name.removeprefix("hub-").split("-")[0])
    metadata_path = hub_root / "metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8")) if metadata_path.exists() else {}
    decoded: dict[Path, object] = {}
    errors: list[dict[str, str]] = []
    for path in sorted(hub_root.rglob("circuit.data")):
        payload = path.read_bytes()
        if not payload:
            errors.append({"path": relative(path), "error": "empty circuit.data"})
            continue
        try:
            decoded[path] = decode_circuit(payload)
        except Exception as exc:
            errors.append({"path": relative(path), "error": f"{type(exc).__name__}: {exc}"})

    by_custom_id: dict[int, tuple[Path, object]] = {}
    duplicate_custom_ids: dict[str, list[str]] = {}
    for path, circuit in decoded.items():
        if not circuit.custom_id:
            continue
        if circuit.custom_id in by_custom_id:
            duplicate_custom_ids.setdefault(
                str(circuit.custom_id), [relative(by_custom_id[circuit.custom_id][0])]
            ).append(relative(path))
        else:
            by_custom_id[circuit.custom_id] = (path, circuit)

    resolve_state: dict[int, int] = {}
    resolved_gate: dict[int, int | None] = {}

    def resolve(custom_id: int) -> int | None:
        if resolve_state.get(custom_id) == 2:
            return resolved_gate[custom_id]
        if resolve_state.get(custom_id) == 1:
            return None
        entry = by_custom_id.get(custom_id)
        if entry is None:
            return None
        circuit = entry[1]
        resolve_state[custom_id] = 1
        children = Counter(
            component.custom_id
            for component in circuit.components
            if component.kind == CUSTOM_KIND and component.custom_id
        )
        child_values = {child_id: resolve(child_id) for child_id in children}
        if any(value is None for value in child_values.values()):
            result = None
        else:
            direct_child_headers = sum(
                count * by_custom_id[child_id][1].gate for child_id, count in children.items()
            )
            local = circuit.gate - direct_child_headers
            result = local + sum(count * int(child_values[child_id]) for child_id, count in children.items())
        resolve_state[custom_id] = 2
        resolved_gate[custom_id] = result
        return result

    circuits: list[dict[str, object]] = []
    for path, circuit in decoded.items():
        payload = path.read_bytes()
        ports = [port_record(component) for component in circuit.components if component.kind in {INPUT_KIND, OUTPUT_KIND}]
        children = Counter(
            component.custom_id
            for component in circuit.components
            if component.kind == CUSTOM_KIND and component.custom_id
        )
        missing = sorted(custom_id for custom_id in children if custom_id not in by_custom_id)
        add_instances = [
            {
                "component_index": index,
                "word_size": component.word_size,
                "cost_gate": component.cost_gate,
                "cost_delay": component.cost_delay,
            }
            for index, component in enumerate(circuit.components)
            if component.kind == 30
        ]
        score = (circuit.gate, circuit.delay)
        interface = looks_like_byte_adder(ports)
        path_relevant = bool(ADDER_PATTERN.search(path.as_posix()))
        exact_score = score in TARGET_SCORES
        recursive_gate = resolve(circuit.custom_id) if circuit.custom_id else circuit.gate
        circuits.append(
            {
                "path": relative(path),
                "bytes": len(payload),
                "sha256": sha256(payload).hexdigest(),
                "format_version": payload[0],
                "header_gate": circuit.gate,
                "header_delay": circuit.delay,
                "header_energy": circuit.energy,
                "custom_id": circuit.custom_id,
                "component_count": len(circuit.components),
                "wire_count": len(circuit.wires),
                "component_kind_counts": {
                    str(kind): count for kind, count in sorted(Counter(c.kind for c in circuit.components).items())
                },
                "ports": ports,
                "interface_match": interface,
                "custom_instance_counts": {str(key): value for key, value in sorted(children.items())},
                "missing_custom_dependencies": missing,
                "recursive_gate": recursive_gate,
                "recursive_gate_matches_header": recursive_gate == circuit.gate,
                "add_instances": add_instances,
                "lead_flags": {
                    "target_score": exact_score,
                    "path_mentions_adder": path_relevant,
                    "byte_adder_interface": any(interface.values()),
                },
            }
        )

    public = listing.get(hub_id, {})
    leads = [
        record
        for record in circuits
        if any(record["lead_flags"].values())
        or record["add_instances"]
    ]
    response_path = hub_root / "response.bin"
    return {
        "hub_id": hub_id,
        "name": public.get("name", metadata.get("hub_name")),
        "description": public.get("description", metadata.get("hub_description")),
        "author": public.get("author"),
        "author_id": public.get("author_id"),
        "schematic_type": public.get("schematic_type", metadata.get("schematic_type")),
        "response_sha256": sha256(response_path.read_bytes()).hexdigest() if response_path.exists() else None,
        "metadata_sha256": sha256(metadata_path.read_bytes()).hexdigest() if metadata_path.exists() else None,
        "circuit_count": len(circuits),
        "decode_errors": errors,
        "duplicate_custom_ids": duplicate_custom_ids,
        "leads": leads,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--public-root", type=Path, default=DEFAULT_PUBLIC_ROOT)
    parser.add_argument("--listing", type=Path, default=DEFAULT_LIST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    listed = json.loads(args.listing.read_text(encoding="utf-8"))
    listing = {int(item["hub_id"]): item for item in listed}
    hubs = [
        analyze_hub(path, listing)
        for path in sorted(
            (path for path in args.public_root.glob("hub-*") if (path / "response.bin").exists()),
            key=lambda path: int(path.name[4:].split("-")[0]),
        )
    ]
    exact_score_leads = [
        {"hub_id": hub["hub_id"], "author": hub["author"], **record}
        for hub in hubs
        for record in hub["leads"]
        if record["lead_flags"]["target_score"]
    ]
    interface_leads = [
        {"hub_id": hub["hub_id"], "author": hub["author"], **record}
        for hub in hubs
        for record in hub["leads"]
        if record["lead_flags"]["byte_adder_interface"]
    ]
    result = {
        "schema": "turing-complete-downloaded-public-hub-scan-v1",
        "scope": "downloaded public Schematic Hub responses and all embedded circuit.data files",
        "target_scores": [list(score) for score in sorted(TARGET_SCORES)],
        "hub_count": len(hubs),
        "circuit_count": sum(hub["circuit_count"] for hub in hubs),
        "decode_error_count": sum(len(hub["decode_errors"]) for hub in hubs),
        "exact_score_leads": exact_score_leads,
        "interface_leads": interface_leads,
        "hubs": hubs,
    }
    payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    encoded = payload.encode("utf-8")
    args.output.write_bytes(encoded)
    print(
        json.dumps(
            {
                "output": relative(args.output),
                "bytes": len(encoded),
                "sha256": sha256(encoded).hexdigest(),
                "hub_count": result["hub_count"],
                "circuit_count": result["circuit_count"],
                "decode_error_count": result["decode_error_count"],
                "exact_score_lead_count": len(exact_score_leads),
                "interface_lead_count": len(interface_leads),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
