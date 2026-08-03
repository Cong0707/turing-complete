"""Generate a reproducible structural inventory for selected public Hub items.

This script only reads already downloaded public packages.  It decodes current
and supported legacy circuit formats, records every file hash, and expands the
declared gate cost through the package's Custom-component dependency graph.
"""

from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

from tc_save_lab.codec import decode_circuit


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PUBLIC_ROOT = ROOT / ".research" / "byte_adder_public"
LIST_PATH = HERE / "hub-list-public-metadata.json"
OUTPUT_PATH = HERE / "selected-hub-analysis.json"
HUB_IDS = (19, 55, 59, 88, 225)
CUSTOM_KIND = 78
INPUT_KIND = 79
OUTPUT_KIND = 81


CLASSIFICATIONS = {
    19: {
        "role": "32-bit carry-select wrapper around eight U8 Add primitives",
        "byte_adder_relevance": (
            "The package contains no embedded U8 gate topology. Its eight kind-30 "
            "instances carry serialized 154/4 cost overrides, independently "
            "corroborating the public four-delay U8 point."
        ),
    },
    55: {
        "role": "hierarchical U8 carry-lookahead adder",
        "byte_adder_relevance": (
            "The main 228/9 circuit consists of one 172/9 CLA carry core and eight "
            "7/4 sum-only full-adder children. It is structurally real but is "
            "dominated by the public Byte Adder frontier."
        ),
    },
    59: {
        "role": "four-bit carry-lookahead adder",
        "byte_adder_relevance": (
            "Its input ports are U4, not U8. It is an old Overture-named reference "
            "and not a recovered modern eight-bit leaderboard topology."
        ),
    },
    88: {
        "role": "direct gate-level U8 ripple adder",
        "byte_adder_relevance": (
            "This is the complete public 56/18 low-gate baseline: 16 AND, 8 OR, "
            "and 32 NOR gates, with no Custom dependencies."
        ),
    },
    225: {
        "role": "three-way 32-bit comparator",
        "byte_adder_relevance": (
            "Despite the name 'adds', it contains Equal, LessU, and LessS and is "
            "not an adder."
        ),
    },
}


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def circuit_base_record(path: Path, circuit) -> dict[str, object]:
    payload = path.read_bytes()
    custom_instances = Counter(
        component.custom_id
        for component in circuit.components
        if component.kind == CUSTOM_KIND and component.custom_id
    )
    overrides = [
        {
            "component_index": index,
            "kind": component.kind,
            "word_size": component.word_size,
            "cost_gate": component.cost_gate,
            "cost_delay": component.cost_delay,
        }
        for index, component in enumerate(circuit.components)
        if component.cost_gate >= 0 or component.cost_delay > 0
    ]
    add_instances = [
        {
            "component_index": index,
            "word_size": component.word_size,
            "position": list(component.position),
            "cost_gate": component.cost_gate,
            "cost_delay": component.cost_delay,
        }
        for index, component in enumerate(circuit.components)
        if component.kind == 30
    ]
    ports = [
        {
            "direction": "input" if component.kind == INPUT_KIND else "output",
            "label": component.user_label,
            "word_size": component.word_size,
            "position": list(component.position),
            "permanent_id": component.permanent_id,
        }
        for component in circuit.components
        if component.kind in {INPUT_KIND, OUTPUT_KIND}
    ]
    return {
        "path": relative(path),
        "bytes": len(payload),
        "sha256": sha256(payload).hexdigest(),
        "format_version": payload[0],
        "header_gate": circuit.gate,
        "header_delay": circuit.delay,
        "header_energy": circuit.energy,
        "custom_id": circuit.custom_id,
        "declared_dependencies": list(circuit.dependencies),
        "component_count": len(circuit.components),
        "wire_count": len(circuit.wires),
        "component_kind_counts": {
            str(kind): count
            for kind, count in sorted(Counter(c.kind for c in circuit.components).items())
        },
        "custom_instance_counts": {
            str(custom_id): count for custom_id, count in sorted(custom_instances.items())
        },
        "serialized_cost_overrides": overrides,
        "add_instances": add_instances,
        "ports": ports,
    }


def analyze_hub(hub_id: int, listing: dict[int, dict[str, object]]) -> dict[str, object]:
    hub_root = PUBLIC_ROOT / f"hub-{hub_id}"
    metadata_path = hub_root / "metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    circuit_paths = sorted(hub_root.rglob("circuit.data"))
    circuits = {path: decode_circuit(path.read_bytes()) for path in circuit_paths}

    by_id: dict[int, tuple[Path, object]] = {}
    duplicate_ids: dict[str, list[str]] = {}
    for path, circuit in circuits.items():
        if not circuit.custom_id:
            continue
        if circuit.custom_id in by_id:
            duplicate_ids.setdefault(str(circuit.custom_id), [relative(by_id[circuit.custom_id][0])]).append(
                relative(path)
            )
        else:
            by_id[circuit.custom_id] = (path, circuit)

    state: dict[int, int] = {}
    recursive_gates: dict[int, int | None] = {}
    cycles: list[list[int]] = []
    stack: list[int] = []

    def resolve(custom_id: int) -> int | None:
        if state.get(custom_id) == 2:
            return recursive_gates.get(custom_id)
        if state.get(custom_id) == 1:
            start = stack.index(custom_id) if custom_id in stack else 0
            cycles.append(stack[start:] + [custom_id])
            return None
        entry = by_id.get(custom_id)
        if entry is None:
            return None
        _path, circuit = entry
        state[custom_id] = 1
        stack.append(custom_id)
        children = Counter(
            c.custom_id for c in circuit.components if c.kind == CUSTOM_KIND and c.custom_id
        )
        child_values = {child_id: resolve(child_id) for child_id in children}
        stack.pop()
        state[custom_id] = 2
        if any(value is None for value in child_values.values()):
            recursive_gates[custom_id] = None
            return None
        child_header_gate = sum(
            count * by_id[child_id][1].gate for child_id, count in children.items()
        )
        local_gate = circuit.gate - child_header_gate
        result = local_gate + sum(
            count * int(child_values[child_id]) for child_id, count in children.items()
        )
        recursive_gates[custom_id] = result
        return result

    records: list[dict[str, object]] = []
    for path, circuit in circuits.items():
        base = circuit_base_record(path, circuit)
        children = Counter(
            c.custom_id for c in circuit.components if c.kind == CUSTOM_KIND and c.custom_id
        )
        missing = sorted(child_id for child_id in children if child_id not in by_id)
        direct_child_header_gate = sum(
            count * by_id[child_id][1].gate
            for child_id, count in children.items()
            if child_id in by_id
        )
        recursive_gate = resolve(circuit.custom_id) if circuit.custom_id else circuit.gate
        base.update(
            {
                "missing_custom_dependencies": missing,
                "direct_child_header_gate": direct_child_header_gate,
                "local_gate_excluding_children": circuit.gate - direct_child_header_gate,
                "recursive_gate": recursive_gate,
                "recursive_gate_matches_header": recursive_gate == circuit.gate,
                "recursive_delay": circuit.delay,
                "recursive_delay_source": (
                    "serialized game score for the complete hierarchy; child delays are "
                    "not arithmetically summed because output-specific arrival paths matter"
                ),
            }
        )
        records.append(base)

    main_path = hub_root / "main" / "circuit.data"
    main = next(record for record in records if record["path"] == relative(main_path))
    public = listing.get(hub_id, {})
    response_path = hub_root / "response.bin"
    return {
        "hub_id": hub_id,
        "public_name": public.get("name", metadata.get("hub_name")),
        "public_description": public.get("description", metadata.get("hub_description")),
        "author": public.get("author"),
        "author_id": public.get("author_id"),
        "response_bytes": response_path.stat().st_size,
        "response_sha256": digest(response_path),
        "package_sha256": metadata.get("package_sha256"),
        "classification": CLASSIFICATIONS[hub_id],
        "duplicate_custom_ids": duplicate_ids,
        "dependency_cycles": cycles,
        "circuit_file_count": len(records),
        "main": main,
        "circuits": records,
    }


def main() -> None:
    listed = json.loads(LIST_PATH.read_text(encoding="utf-8"))
    listing = {int(item["hub_id"]): item for item in listed}
    result = {
        "schema": "turing-complete-byte-adder-selected-public-hubs-v1",
        "scope": "public Hub items 19, 55, 59, 88, and 225; read-only offline analysis",
        "hub_ids": list(HUB_IDS),
        "hubs": [analyze_hub(hub_id, listing) for hub_id in HUB_IDS],
    }
    payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    encoded = payload.encode("utf-8")
    OUTPUT_PATH.write_bytes(encoded)
    print(
        json.dumps(
            {
                "output": relative(OUTPUT_PATH),
                "bytes": len(encoded),
                "sha256": sha256(encoded).hexdigest(),
                "hub_count": len(result["hubs"]),
                "circuit_count": sum(hub["circuit_file_count"] for hub in result["hubs"]),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
