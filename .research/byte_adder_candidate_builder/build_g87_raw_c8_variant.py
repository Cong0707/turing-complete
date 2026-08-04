"""Build the Hub87 candidate with its raw may-Z carry connected directly.

This is deliberately a thin wrapper around the reviewed Factory builder.  It
changes only the zero-cost Maker2/Splitter2 normalization used for C8.  The
Byte Adder carry contract accepts Z as zero, while every expected-one row must
still be actively driven and conflicts remain forbidden.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from hashlib import sha256
from pathlib import Path


HERE = Path(__file__).resolve().parent
BUILDER_PATH = HERE / "build_g94_static_candidate.py"
PATCH_PATH = HERE / "s34_and_nor_xor_patch.py"
DEFAULT_OUTPUT = HERE / "byte-adder-g87-d6-raw-c8-full.json"


def _load_builder():
    spec = importlib.util.spec_from_file_location("byte_adder_g94_builder", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load builder: {BUILDER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build and fully verify the 87/6 raw-C8 physical variant."
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    builder = _load_builder()
    hooks = builder.load_formula_hooks(PATCH_PATH)

    original_normalize = builder.BuildContext.normalize_scalar

    def keep_raw_scalar(self, name, partial, filler, *, owner, region):
        del filler, owner
        node = self.resolve(partial)
        self.define(name, node, region)
        return node

    builder.BuildContext.normalize_scalar = keep_raw_scalar
    try:
        payload = builder.build_candidate(
            hooks,
            full_verify=True,
            b12_g1_recode=True,
            hub87_high_graft=True,
        )
    finally:
        builder.BuildContext.normalize_scalar = original_normalize

    metrics = payload["metrics"]
    if (metrics["gate"], metrics["delay"], metrics["energy"]) != (87, 6, 522):
        raise RuntimeError(f"raw-C8 score changed unexpectedly: {metrics}")
    semantic = payload["semantic"]
    if semantic["mismatch_union_count"] != 0:
        raise RuntimeError(f"raw-C8 truth mismatch: {semantic['mismatch_union_count']}")
    if semantic["conflict_assignment_count"] != 0:
        raise RuntimeError(
            f"raw-C8 BUS conflict: {semantic['conflict_assignment_count']}"
        )

    c8_node = payload["factory_dag"]["outputs"][8]
    by_id = {node["id"]: node for node in payload["factory_dag"]["nodes"]}
    c8 = by_id[c8_node]
    if c8["op"] != "BUS" or not c8["may_z"]:
        raise RuntimeError(f"C8 is not the expected raw may-Z BUS: {c8}")

    payload["rewrite"]["raw_c8_direct"] = True
    payload["rewrite"]["raw_c8_node"] = c8_node
    payload["rewrite"]["removed_zero_cost_normalizers"] = ["MAKER2", "SPLITTER2"]
    payload["formula_hooks"]["name"] += "+raw-c8-direct"

    encoded = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(encoded, encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(args.output),
                "sha256": sha256(encoded.encode("utf-8")).hexdigest(),
                "metrics": metrics,
                "c8_node": c8_node,
                "c8_op": c8["op"],
                "c8_may_z": c8["may_z"],
                "truth_rows": semantic["truth_table_rows"],
                "mismatch_union_count": semantic["mismatch_union_count"],
                "conflict_assignment_count": semantic["conflict_assignment_count"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
