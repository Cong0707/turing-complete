#!/usr/bin/env python3
"""只读审计最新版 Byte Adder 的测试域与输入置换。"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from datetime import datetime, timezone
from pathlib import Path


MASK17 = (1 << 17) - 1
EXPECTED_HASHES = {
    "Turing Complete.exe": "c93f5e8e826050c3f92e2b3891d26fcdfc933658614185cb9b2eb6a34c5b8d1c",
    "campaign/byte_adder/test.si": "0f9d4d118ad66058259d5a2f2fbd08cd3c5886c8a490b636167ac41c7718b941",
    "campaign/byte_adder/meta.txt": "220f4f950d413f4c35f3057ea0223e5bc4a12c3033fbb7bc9c691243edd3ebad",
}
EXPECTED_VECTOR_SHA256 = "2fd98014c77e2d2e05cc92dfa85f9a4a155c0644ae9554967f34dffae6328605"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_text(text: str, fragments: tuple[str, ...], owner: str) -> None:
    for fragment in fragments:
        if fragment not in text:
            raise RuntimeError(f"{owner} 缺少运行时证据片段: {fragment!r}")


def require_bytes(blob: bytes, fragments: tuple[str, ...], owner: str) -> None:
    for fragment in fragments:
        if fragment.encode("utf-8") not in blob:
            raise RuntimeError(f"{owner} 缺少运行时证据片段: {fragment!r}")


def input_word(tick: int) -> int:
    if not 0 <= tick <= MASK17:
        raise ValueError("tick 必须位于 0..0x1ffff")
    value = tick
    value ^= value << 6
    value ^= value >> 11
    value ^= value << 9
    return value & MASK17


def gf2_rank(columns: list[int], width: int) -> int:
    basis = [0] * width
    rank = 0
    for original in columns:
        value = original & ((1 << width) - 1)
        while value:
            pivot = value.bit_length() - 1
            if basis[pivot]:
                value ^= basis[pivot]
                continue
            basis[pivot] = value
            rank += 1
            break
    return rank


def autonomous_lasso_bound(outputs: list[int]) -> dict[str, int]:
    """给出忽略外部输入的确定性状态机重放此前缀所需最少轨迹状态数。"""

    reverse = outputs[::-1]
    size = len(reverse)
    z = [0] * size
    left = 0
    right = 0
    for index in range(1, size):
        if index < right:
            z[index] = min(right - index, z[index - left])
        while index + z[index] < size and reverse[z[index]] == reverse[index + z[index]]:
            z[index] += 1
        if index + z[index] > right:
            left = index
            right = index + z[index]

    repeated_suffix = max(z[1:])
    period = z.index(repeated_suffix, 1)
    preperiod = size - period - repeated_suffix
    trajectory_states = preperiod + period
    return {
        "longest_reusable_final_suffix_length": repeated_suffix,
        "witness_preperiod": preperiod,
        "witness_period": period,
        "minimum_distinct_trajectory_states": trajectory_states,
        "minimum_binary_state_bits": (trajectory_states - 1).bit_length(),
    }


def audit_runtime(game_root: Path) -> dict[str, object]:
    paths = {
        "Turing Complete.exe": game_root / "Turing Complete.exe",
        "campaign/byte_adder/test.si": game_root / "campaign" / "byte_adder" / "test.si",
        "campaign/byte_adder/meta.txt": game_root / "campaign" / "byte_adder" / "meta.txt",
    }
    observed_hashes = {name: sha256(path) for name, path in paths.items()}
    if observed_hashes != EXPECTED_HASHES:
        raise RuntimeError(
            "安装版已变化，必须重新审阅资产后再更新证书: "
            + json.dumps(observed_hashes, sort_keys=True)
        )

    test_source = paths["campaign/byte_adder/test.si"].read_text(encoding="utf-8")
    meta_source = paths["campaign/byte_adder/meta.txt"].read_text(encoding="utf-8")
    executable = paths["Turing Complete.exe"].read_bytes()

    require_text(
        meta_source,
        (
            "kind = combinational",
            "unlocks_components = [com_add]",
            "`Also, this level has a lot of tests.",
        ),
        "byte_adder/meta.txt",
    )
    require_text(
        test_source,
        (
            "var x = tick",
            "x ^= x << 6",
            "x ^= x >> 11",
            "x ^= x << 9",
            "a: U8 (x & 0xff)",
            "b: U8 ((x >> 8) & 0xff)",
            "carry_in: U1 (x >> 16) & 1",
            "if output.output_is_z",
            "var sum = Int input.a + Int input.b + Int input.carry_in",
            "if Int output.output != (Int sum & 0xff)",
            "if Int output.carry_out != car",
            "if tick == 0x1ffff",
            "return win",
        ),
        "byte_adder/test.si",
    )
    require_bytes(
        executable,
        (
            "var tick = -1",
            ".tick = -1",
            ".level_input = get_input(.tick + 1)",
            "let result = check_output(.tick + 1, .level_input, .level_output)",
            ".tick += 1 // Do this late as it signals to the front end that it can update",
        ),
        "Turing Complete.exe",
    )

    return {
        "game_root": str(game_root),
        "sha256": observed_hashes,
        "level_kind": "combinational",
        "tick_initial_value": -1,
        "get_input_argument": ".tick + 1",
        "check_output_argument": ".tick + 1",
        "winning_tick": MASK17,
        "checked_tick_interval_inclusive": [0, MASK17],
        "checked_tick_count": 1 << 17,
    }


def audit_input_schedule() -> dict[str, object]:
    words = [input_word(tick) for tick in range(1 << 17)]
    packed = b"".join(struct.pack("<I", value) for value in words)
    vector_sha256 = hashlib.sha256(packed).hexdigest()
    if vector_sha256 != EXPECTED_VECTOR_SHA256:
        raise RuntimeError(f"输入向量哈希变化: {vector_sha256}")

    tuples = {
        (value & 0xFF, (value >> 8) & 0xFF, (value >> 16) & 1)
        for value in words
    }
    expected_tuples = {
        (a, b, carry)
        for carry in range(2)
        for b in range(256)
        for a in range(256)
    }
    if tuples != expected_tuples:
        raise RuntimeError("实际输入三元组不是完整的 U8 x U8 x U1 域")

    columns = [input_word(1 << bit) for bit in range(17)]
    rank = gf2_rank(columns, 17)
    if rank != 17 or len(set(words)) != 1 << 17:
        raise RuntimeError("17 位输入扰动不是置换")

    expected_outputs = [
        (((value & 0xFF) + ((value >> 8) & 0xFF) + ((value >> 16) & 1)) & 0x1FF)
        for value in words
    ]
    output_sha256 = hashlib.sha256(
        b"".join(struct.pack("<H", value) for value in expected_outputs)
    ).hexdigest()
    lasso = autonomous_lasso_bound(expected_outputs)

    return {
        "formula": (
            "y = low17((((tick xor (tick << 6)) xor "
            "((tick xor (tick << 6)) >> 11)) xor "
            "(((tick xor (tick << 6)) xor ((tick xor (tick << 6)) >> 11)) << 9)))"
        ),
        "projection": {
            "a": "y[7:0]",
            "b": "y[15:8]",
            "carry_in": "y[16]",
        },
        "vector_encoding": "tick 顺序的 131072 个 little-endian U32 low17 值",
        "vector_sha256": vector_sha256,
        "unique_low17_count": len(set(words)),
        "low17_min": min(words),
        "low17_max": max(words),
        "gf2_linear_rank": rank,
        "domain_tuple_count": len(tuples),
        "expected_domain_tuple_count": len(expected_tuples),
        "complete_u8_u8_u1_domain": tuples == expected_tuples,
        "untested_domain_tuple_count": len(expected_tuples - tuples),
        "expected_output_encoding": "每拍 9 位 (carry_out << 8) | sum 的 little-endian U16",
        "expected_output_vector_sha256": output_sha256,
        "expected_output_unique_value_count": len(set(expected_outputs)),
        "input_independent_autonomous_replay_bound": {
            **lasso,
            "meaning": (
                "忽略全部关卡输入的确定性状态机，其复位后轨迹必为前缀加周期；"
                "要产生完整答案前缀，至少需要这些不同轨迹状态。"
            ),
            "scope": "不约束同时读取当前输入的混合状态电路。",
        },
        "first_low17_values_hex": [f"{value:05x}" for value in words[:16]],
        "basis_columns_hex": [f"{value:05x}" for value in columns],
    }


def fetch_leaderboard_snapshot() -> dict[str, object]:
    from tc_save_lab.leaderboard import fetch_level_leaderboard, pareto_front

    rows = fetch_level_leaderboard("byte_adder")
    front = pareto_front(rows)
    return {
        "url": "https://turingcomplete.game/leaderboard/byte_adder",
        "captured_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "visible_row_count": len(rows),
        "page_cap_suspected": len(rows) == 1000,
        "energy_rank1": {
            "username": rows[0].username,
            "gate": rows[0].gate,
            "delay": rows[0].delay,
            "energy": rows[0].energy,
        },
        "visible_pareto": [
            {
                "username": row.username,
                "gate": row.gate,
                "delay": row.delay,
                "energy": row.energy,
            }
            for row in front
        ],
        "scope": "公开页面只证明已接受成绩，不公开服务端测试资产或重算日志。",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--game-root",
        type=Path,
        default=Path(r"D:\Game\Steam\steamapps\common\Turing Complete"),
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument("--fetch-leaderboard", action="store_true")
    args = parser.parse_args()

    schedule = audit_input_schedule()
    certificate: dict[str, object] = {
        "schema": 1,
        "generated_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "runtime": audit_runtime(args.game_root),
        "input_schedule": schedule,
        "specialization_boundary": {
            "input_subset_specialization": "排除：131072 个 U8 x U8 x U1 三元组全部且仅出现一次。",
            "fixed_order_specialization": (
                "逻辑上仍可构造依赖复位后 tick 顺序的状态机，但它必须正确重放完整 131072 步；"
                "本证书未证明这种状态机在 103/5 前沿下可获利。"
            ),
            "remote_asset_identity": (
                "本机不能读取服务端 test.si；服务端与本地资产逐字节一致不能由此证书证明。"
            ),
        },
    }
    if args.fetch_leaderboard:
        certificate["leaderboard"] = fetch_leaderboard_snapshot()

    rendered = json.dumps(certificate, ensure_ascii=False, indent=2) + "\n"
    if args.output is None:
        print(rendered, end="")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
