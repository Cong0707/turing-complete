"""Verify the two-driver S7 merge in the fixed human 87/6 circuit."""

from __future__ import annotations

from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO_ROOT / "src"))

from audit_human_87 import ALL_ROWS, _compile, _evaluate, decode_v15  # noqa: E402


def resolve(drivers: list[tuple[int, int]]) -> tuple[int, int, int, int]:
    ones = zeros = driven = conflict = 0
    for enable, data in drivers:
        active = enable
        ones |= active & data
        zeros |= active & (~data & ALL_ROWS)
        driven |= active
    conflict |= ones & zeros
    return ones & ALL_ROWS, zeros & ALL_ROWS, driven & ALL_ROWS, conflict & ALL_ROWS


def main() -> int:
    source = HERE / "source_human87" / "circuit.data"
    circuit = decode_v15(source.read_bytes())
    compiled = _compile(circuit)
    _inputs, values, driven, _arrivals, _switch_rows, conflict = _evaluate(circuit, compiled)

    def net(number: int) -> int:
        return values[number][0] & driven[number][0]

    n278 = net(278)
    n258 = net(258)
    q6 = net(270)
    p7 = net(271)
    n207 = net(207)
    n285 = net(285)
    u = n278 | n258

    old = resolve([(n278, n207), (q6, p7), (n285, p7)])
    new = resolve([(u, n207), (n285, p7)])
    target = net(281)
    added_domain = n258 & ~n278

    print(f"source_conflict_rows={conflict.bit_count()}")
    print(f"added_domain_rows={added_domain.bit_count()}")
    print(f"added_domain_n207_ne_p7={(added_domain & (n207 ^ p7)).bit_count()}")
    print(f"added_domain_n207_zero={(added_domain & ~n207).bit_count()}")
    print(f"added_domain_p7_zero={(added_domain & ~p7).bit_count()}")
    print(f"old_one={old[0].bit_count()} old_driven={old[2].bit_count()} old_z={131072-old[2].bit_count()} old_conflict={old[3].bit_count()}")
    print(f"new_one={new[0].bit_count()} new_driven={new[2].bit_count()} new_z={131072-new[2].bit_count()} new_conflict={new[3].bit_count()}")
    print(f"one_difference={(old[0] ^ new[0]).bit_count()}")
    print(f"driven_difference={(old[2] ^ new[2]).bit_count()}")
    print(f"target_difference={(target ^ new[0]).bit_count()}")

    assert conflict == 0
    assert added_domain & (n207 ^ p7) == 0
    assert old[3] == 0 and new[3] == 0
    assert old[0] == new[0] == target
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
