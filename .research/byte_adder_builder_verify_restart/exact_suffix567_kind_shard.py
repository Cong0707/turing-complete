"""First-slot-kind shards for the exact nine-gate suffix567 SAT model.

The reviewed worker has no kind-shard CLI, so this thin wrapper injects only a
unit constraint for each requested ``slot:KIND`` pair.  The truth tables and
all SAT encoding logic remain sourced from the existing reviewed modules.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SUFFIX = ROOT / ".research/byte_adder_advanced_switch_cells_agent/exact_suffix567_phase_sat.py"


def _load():
    spec = importlib.util.spec_from_file_location("suffix567_kind_shard_source", SUFFIX)
    if spec is None or spec.loader is None:
        raise RuntimeError(SUFFIX)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    suffix = _load()
    source_path = Path(suffix.SOURCE)
    text = source_path.read_text(encoding="utf-8")
    begin = text.index("def truth_tables(")
    end = text.index("def weighted_bound", begin)
    text = text[:begin] + suffix.CUSTOM_TRUTH + "\n\n" + text[end:]
    text = text.replace(
        '"schema": "exact-paid-gp-ling-pair-v1",',
        '"schema": "exact-suffix567-shared-phase-v1",',
    )

    parser_marker = '    parser.add_argument("--solver", default="cadical195")\n'
    parser_insert = (
        '    parser.add_argument("--slot-kind", action="append", default=[], '
        'help="force SLOT:KIND; repeatable")\n'
        + parser_marker
    )
    if text.count(parser_marker) != 1:
        raise RuntimeError("solver parser marker changed")
    text = text.replace(parser_marker, parser_insert)

    bound_marker = "    weighted_bound(enc, kinds, args.gate_bound)\n"
    bound_insert = '''    forced_slot_kinds = {}
    for raw_constraint in args.slot_kind:
        try:
            raw_slot, raw_kind = raw_constraint.split(":", 1)
            slot = int(raw_slot)
            kind = raw_kind.upper()
        except (AttributeError, TypeError, ValueError) as error:
            raise ValueError(f"invalid --slot-kind {raw_constraint!r}") from error
        if not 0 <= slot < args.components:
            raise ValueError(f"slot index outside component range: {slot}")
        if kind not in G.KINDS:
            raise ValueError(f"unsupported forced kind: {kind}")
        if slot in forced_slot_kinds and forced_slot_kinds[slot] != kind:
            raise ValueError(f"conflicting forced kinds for slot {slot}")
        forced_slot_kinds[slot] = kind
        enc.clause((kinds[slot][G.KINDS.index(kind)],))
    args.forced_slot_kinds = {
        str(slot): kind for slot, kind in sorted(forced_slot_kinds.items())
    }

    weighted_bound(enc, kinds, args.gate_bound)
'''
    if text.count(bound_marker) != 1:
        raise RuntimeError("weighted-bound marker changed")
    text = text.replace(bound_marker, bound_insert)

    payload_marker = '        "output_deadlines": state.get("output_deadlines"),\n'
    payload_insert = (
        payload_marker
        + '        "forced_slot_kinds": getattr(args, "forced_slot_kinds", {}),\n'
    )
    if text.count(payload_marker) != 1:
        raise RuntimeError("payload marker changed")
    text = text.replace(payload_marker, payload_insert)

    namespace = {
        "__name__": "__main__",
        "__file__": str(source_path),
        "__package__": None,
    }
    try:
        exec(compile(text, str(source_path), "exec"), namespace)
    except SystemExit as exc:
        return int(exc.code or 0)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
