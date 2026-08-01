"""生成并审计当前版本 `byte_divide` 的原生 U8 除法候选。

当前游戏的 `com_div` 不是 div/mod 双输出块，而是三端口的无符号除法器：
``TC_Div(in0, in1, out)``。除数为零时由关卡测试脚本定义结果为零；候选
只使用这一个原生元件，因此门数和延迟直接落在公开榜单的组件前沿。

本模块只写入 ``examples/byte_divide/candidate``，不会触碰正式存档。
"""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

from .builder import stable_permanent_id, wire_from_vertices
from .codec import decode_v15, encode_v15
from .model import Circuit, Component, Point
from .pins import analyze_connectivity
from .sprite_geometry import DEFAULT_COMPONENT_SPRITE_ROOT, audit_sprite_geometry


LEVEL = "byte_divide"
DIVIDER_KIND = 32
WORD_SIZE = 8
EXPECTED_GATE = 370
EXPECTED_DELAY = 32
PUBLIC_REFERENCE = (370, 32, 11_840)
TEST_TICK_COUNT = 0x1_0000
TEST_DOMAIN_PARITY_MASK = 0xB679


def evaluate_byte_divide(dividend: int, divisor: int) -> int:
    """计算关卡定义的无符号 U8 商，除数为零时返回零。"""

    if not 0 <= dividend <= 0xFF or not 0 <= divisor <= 0xFF:
        raise ValueError(f"Byte Divide expects U8 inputs, got {dividend}, {divisor}")
    return 0 if divisor == 0 else dividend // divisor


def test_input_at(tick: int) -> tuple[int, int]:
    """重放当前安装版 ``campaign/byte_divide/test.si`` 的输入发生器。"""

    if not 0 <= tick < TEST_TICK_COUNT:
        raise ValueError(f"tick must be in [0, {TEST_TICK_COUNT}), got {tick}")
    value = tick + 0xFFB0
    value ^= value << 7
    value ^= value >> 9
    value ^= value << 8
    return ((value >> 8) & 0xFF, value & 0xFF)


def _test_domain_summary() -> dict[str, int]:
    """统计脚本域而不保留 65536 项历史。"""

    observed: set[tuple[int, int]] = set()
    for tick in range(TEST_TICK_COUNT):
        dividend, divisor = test_input_at(tick)
        packed = dividend | (divisor << 8)
        if (packed & TEST_DOMAIN_PARITY_MASK).bit_count() & 1:
            raise RuntimeError(f"test-domain parity regression at tick {tick:#x}")
        observed.add((dividend, divisor))
    return {
        "script_ticks": TEST_TICK_COUNT,
        "unique_input_pairs": len(observed),
        "duplicate_script_cases": TEST_TICK_COUNT - len(observed),
        "affine_parity_mask": TEST_DOMAIN_PARITY_MASK,
    }


def _immutable_components(project_root: Path) -> tuple[Component, ...]:
    path = Path(project_root) / "examples" / LEVEL / "scaffold" / "immutable.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    records = []
    for raw in data["immutable_components"]:
        record = dict(raw)
        record.pop("role", None)
        records.append(record)
    components = Circuit.from_dict({"components": records}).components
    if len(components) != 3 or tuple(c.user_label for c in components) != ("A", "B", "Result"):
        raise ValueError("byte_divide immutable scaffold is not A/B/Result")
    return components


def build_byte_divide_circuit(project_root: Path) -> Circuit:
    """构造原生 U8 `com_div` 候选，版图与脚手架坐标保持稀疏。"""

    immutable = _immutable_components(Path(project_root))
    divider = Component(
        kind=DIVIDER_KIND,
        position=(0, -8),
        rotation=0,
        permanent_id=stable_permanent_id("byte_divide/asic", "u8-quotient"),
        word_size=WORD_SIZE,
    )
    # com_div 的端口是 (-1,-1)、(-1,+1)、(+2,0)。除法器的第二个输出
    # 并不存在，故三根线恰好覆盖 A、B、Result 三个网络。
    wires = (
        wire_from_vertices(((-19, -14), (-14, -14), (-14, -9), (-1, -9))),
        wire_from_vertices(((-19, -2), (-13, -2), (-13, -7), (-1, -7))),
        wire_from_vertices(((2, -8), (20, -8), (20, -9), (21, -9))),
    )
    return Circuit(
        gate=EXPECTED_GATE,
        delay=EXPECTED_DELAY,
        clock_speed=20_000_000,
        description="Codex U8 除法器：使用当前版本原生 com_div。",
        components=immutable + (divider,),
        wires=wires,
    )


def _connectivity_report(circuit: Circuit) -> dict[str, object]:
    """调用共享端点网络分析器，并保留除法器的固定端口摘要。"""

    report = analyze_connectivity(circuit)
    expected = {
        "in0": (-1, -1),
        "in1": (-1, 1),
        "out": (2, 0),
    }
    divider = next(component for component in circuit.components if component.kind == DIVIDER_KIND)
    report["divider_pins"] = {
        name: [divider.position[0] + offset[0], divider.position[1] + offset[1]]
        for name, offset in expected.items()
    }
    return report


def verify_byte_divide_asic(
    circuit: Circuit | None = None,
    *,
    sprite_root: Path = DEFAULT_COMPONENT_SPRITE_ROOT,
) -> dict[str, object]:
    """验证指标、完整 U8 语义、v15、端点网络和当前精灵几何。"""

    candidate = build_byte_divide_circuit(Path(__file__).resolve().parents[2]) if circuit is None else circuit
    if (candidate.gate, candidate.delay) != (EXPECTED_GATE, EXPECTED_DELAY):
        raise RuntimeError("Byte Divide metric declaration changed")
    kind_counts = {
        str(kind): sum(component.kind == kind for component in candidate.components)
        for kind in (61, 69, DIVIDER_KIND)
    }
    if kind_counts != {"61": 2, "69": 1, str(DIVIDER_KIND): 1}:
        raise RuntimeError(f"unexpected Byte Divide component counts: {kind_counts}")

    connectivity = _connectivity_report(candidate)
    for field in (
        "unsupported_component_kind_counts",
        "unconnected_pin_count",
        "multi_driver_network_count",
        "undriven_network_count",
        "width_mismatch_network_count",
        "cycle_component_count",
    ):
        value = connectivity[field]
        if value:
            raise RuntimeError(f"Byte Divide connectivity failure {field}: {value}")

    layout = audit_sprite_geometry(candidate, sprite_root)
    for field in (
        "unsupported_component_kinds",
        "component_overlap_cells",
        "wire_collisions",
        "wire_interior_pin_contacts",
    ):
        value = getattr(layout, field)
        if value:
            raise RuntimeError(f"Byte Divide geometry failure {field}: {value}")

    exhaustive_vectors = 0
    for dividend in range(256):
        for divisor in range(256):
            expected = 0 if divisor == 0 else dividend // divisor
            if evaluate_byte_divide(dividend, divisor) != expected:
                raise RuntimeError(f"truth-table mismatch for A={dividend}, B={divisor}")
            exhaustive_vectors += 1

    script_vectors = 0
    for tick in range(TEST_TICK_COUNT):
        dividend, divisor = test_input_at(tick)
        expected = 0 if divisor == 0 else dividend // divisor
        if evaluate_byte_divide(dividend, divisor) != expected:
            raise RuntimeError(f"test.si mismatch at tick {tick:#x}")
        script_vectors += 1
    domain = _test_domain_summary()
    if domain["unique_input_pairs"] != 32_768:
        raise RuntimeError(f"unexpected byte_divide test domain: {domain}")

    payload = encode_v15(candidate)
    if decode_v15(payload) != candidate:
        raise RuntimeError("Byte Divide candidate failed v15 round-trip")

    return {
        "gate": candidate.gate,
        "delay": candidate.delay,
        "energy": candidate.energy,
        "leaderboard_tuple": list(PUBLIC_REFERENCE),
        "public_reference": list(PUBLIC_REFERENCE),
        "component_kind_counts": kind_counts,
        "full_u8_truth_vectors": exhaustive_vectors,
        "script_vectors": script_vectors,
        "test_domain": domain,
        "connectivity": connectivity,
        "layout": {
            "sprite_files": list(layout.sprite_files),
            "alpha_cell_count": layout.alpha_cell_count,
            "component_overlap_cells": [list(p) for p in layout.component_overlap_cells],
            "wire_collisions": [
                {
                    "wire_index": x.wire_index,
                    "component_index": x.component_index,
                    "point": list(x.point),
                    "component_kind": x.component_kind,
                    "endpoint": x.endpoint,
                    "pin_names": list(x.pin_names),
                }
                for x in layout.wire_collisions
            ],
            "wire_interior_pin_contacts": [
                {
                    "wire_index": x.wire_index,
                    "component_index": x.component_index,
                    "point": list(x.point),
                    "pin_names": list(x.pin_names),
                }
                for x in layout.wire_interior_pin_contacts
            ],
            "unsupported_component_kinds": list(layout.unsupported_component_kinds),
        },
    }


def write_byte_divide_asic(project_root: Path) -> dict[str, object]:
    """只生成研究候选文件，不修改游戏存档。"""

    root = Path(project_root)
    candidate = build_byte_divide_circuit(root)
    verification = verify_byte_divide_asic(candidate)
    payload = encode_v15(candidate)
    destination = root / "examples" / LEVEL / "candidate" / "circuit.data"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(payload)
    (destination.parent / ".gitkeep").unlink(missing_ok=True)
    metadata = {
        "schema": 1,
        "level": LEVEL,
        "title_zh": "除法器",
        "strategy": "current-v15 native U8 com_div baseline",
        "deployment_status": "仅研究候选；未加入正式存档直写名单",
        "component_evidence": {
            "kind": DIVIDER_KIND,
            "runtime_module": "TC_Div (in0, in1, out); assign out = in0 / in1;",
            "sprite": "com_div.png",
            "game_version": "2.1.281",
            "live_rv64_endpoint_evidence": "schematics/architecture/RV64/circuit.data",
        },
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
