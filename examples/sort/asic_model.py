"""美味排行的 16 级流式插入排序 ASIC 行为模型。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


WORD_BITS = 8
WORD_MAX = (1 << WORD_BITS) - 1
ITEM_COUNT = 16


@dataclass(frozen=True)
class SortCycle:
    """单个时钟周期结束后的可复现状态。"""

    phase: str
    incoming: int
    output: int
    registers: tuple[int, ...]


def _check_byte(value: int) -> None:
    if not 0 <= value <= WORD_MAX:
        raise ValueError(f"value must be an unsigned byte, got {value}")


def insertion_cycle(
    registers: tuple[int, ...], incoming: int
) -> tuple[tuple[int, ...], int]:
    """把一个字节插入降序寄存器链，并返回链尾被挤出的最小值。"""

    if len(registers) != ITEM_COUNT:
        raise ValueError(f"expected {ITEM_COUNT} registers, got {len(registers)}")
    _check_byte(incoming)

    carry = incoming
    next_registers = list(registers)
    for index, stored in enumerate(next_registers):
        _check_byte(stored)
        if stored < carry:
            next_registers[index], carry = carry, stored
    return tuple(next_registers), carry


def sort_stream(values: Iterable[int]) -> tuple[tuple[int, ...], tuple[SortCycle, ...]]:
    """用 16 次装载和 16 次冲刷完成排序，总计固定 32 个周期。"""

    inputs = tuple(values)
    if len(inputs) != ITEM_COUNT:
        raise ValueError(f"expected {ITEM_COUNT} input values, got {len(inputs)}")
    for value in inputs:
        _check_byte(value)

    registers = (0,) * ITEM_COUNT
    trace: list[SortCycle] = []

    for value in inputs:
        registers, output = insertion_cycle(registers, value)
        trace.append(SortCycle("load", value, output, registers))

    outputs: list[int] = []
    for _ in range(ITEM_COUNT):
        registers, output = insertion_cycle(registers, WORD_MAX)
        outputs.append(output)
        trace.append(SortCycle("flush", WORD_MAX, output, registers))

    return tuple(outputs), tuple(trace)
