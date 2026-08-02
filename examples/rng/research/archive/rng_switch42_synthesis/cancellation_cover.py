"""Cancellation-aware depth-two XOR2/Switch-XOR3 cover for one lift candidate.

This reuses the independently checked PySAT encoder in
``rng_depth2_pysat/search.py`` while replacing its natural-state matrix with
the distinct non-wire H/O targets of a parameterized lifted-state point.
Unlike ``optimize_pruned38_pysat.py``, final gate sources may overlap and
cancel arbitrarily.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
from typing import Sequence


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

import optimize_pruned38 as lift  # noqa: E402


def load_backend():
    path = ROOT / ".research" / "rng_depth2_pysat" / "search.py"
    spec = importlib.util.spec_from_file_location("rng_depth2_cancellation_backend", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import backend {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module, path


def rows_fingerprint(rows: Sequence[int], width: int) -> str:
    byte_width = (width + 7) // 8
    raw = b"".join(value.to_bytes(byte_width, "little") for value in rows)
    return sha256(raw).hexdigest()


def install_problem(backend, rows: tuple[int, ...], state_bits: int) -> None:
    original_all_forms = backend.all_forms
    backend.BITS = state_bits
    backend.MASK = (1 << state_bits) - 1
    backend.target_rows = lambda: rows
    backend.all_forms = lambda bits=state_bits: original_all_forms(state_bits)
    backend.matrix_fingerprint = lambda values: rows_fingerprint(values, state_bits)

    def verify_certificate(certificate: dict) -> None:
        first = {
            int(record["form"], 16): record
            for record in certificate["first_level"]
        }
        cost = 0
        for value, record in first.items():
            inputs = record["inputs"]
            rebuilt = 0
            for bit in inputs:
                if not 0 <= bit < state_bits:
                    raise AssertionError(f"first form input {bit} is out of range")
                rebuilt ^= 1 << bit
            if rebuilt != value:
                raise AssertionError(f"first form {value:x} has wrong inputs")
            expected_mode = "xor2" if len(inputs) == 2 else "xor3"
            expected_cost = backend.XOR2_COST if len(inputs) == 2 else backend.XOR3_COST
            if len(inputs) not in (2, 3):
                raise AssertionError(f"first form {value:x} has illegal arity")
            if record["mode"] != expected_mode or record["cost"] != expected_cost:
                raise AssertionError(f"first form {value:x} has wrong cost/mode")
            cost += expected_cost

        outputs = certificate["outputs"]
        if len(outputs) != len(rows):
            raise AssertionError("certificate has the wrong target count")
        for output, (record, target) in enumerate(zip(outputs, rows)):
            if record["output"] != output:
                raise AssertionError("outputs are not in canonical order")
            sources = [int(value, 16) for value in record["sources"]]
            rebuilt = 0
            for source in sources:
                if source.bit_count() > 1 and source not in first:
                    raise AssertionError(
                        f"target {output}: source {source:x} is not implemented"
                    )
                rebuilt ^= source
            if rebuilt != target:
                raise AssertionError(
                    f"target {output}: got {rebuilt:x}, expected {target:x}"
                )
            mode = record["mode"]
            expected_arity = {"direct": 1, "xor2": 2, "xor3": 3}[mode]
            expected_cost = {
                "direct": 0,
                "xor2": backend.XOR2_COST,
                "xor3": backend.XOR3_COST,
            }[mode]
            if len(sources) != expected_arity or record["cost"] != expected_cost:
                raise AssertionError(f"target {output}: wrong arity/cost")
            cost += expected_cost
        if cost != certificate["cost"]:
            raise AssertionError("certificate cost mismatch")
        if cost > certificate["limit"]:
            raise AssertionError("certificate exceeds its cost limit")

    backend.verify_certificate = verify_certificate


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--candidate", choices=("last", "all"), default="last")
    parser.add_argument("--target-gate-max", type=int, default=430)
    parser.add_argument("--timeout-seconds", type=float, default=120.0)
    parser.add_argument("--memory-mb", type=int, default=700)
    parser.add_argument("--solver", default="glucose42")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    candidates = lift.load_log_candidates(args.log, args.candidate)
    if len(candidates) != 1:
        raise SystemExit("cancellation-aware runner accepts exactly one distinct candidate")
    candidate = candidates[0]
    h_rows, o_rows, active_hidden = lift.build_pruned(
        candidate.x_rows, candidate.d_rows
    )
    lift.verify_sequences(h_rows, o_rows)
    targets = tuple(sorted({row for row in h_rows + o_rows if row.bit_count() >= 2}))
    state_bits = len(h_rows)
    fixed_gate = state_bits * 5 + 32 + 6
    raw_budget = args.target_gate_max - fixed_gate
    logic_budget = raw_budget - raw_budget % 3
    if logic_budget < 0:
        raise SystemExit("fixed cost already exceeds the target")

    backend, backend_path = load_backend()
    install_problem(backend, targets, state_bits)
    return_code = backend.build_and_solve(
        logic_budget,
        None if args.timeout_seconds <= 0 else args.timeout_seconds,
        args.memory_mb,
        args.solver,
        args.output,
    )

    result = json.loads(args.output.read_text(encoding="utf-8"))
    result.update(
        {
            "schema": 1,
            "scope": "lifted-state cancellation-aware depth-two XOR2/Switch-XOR3 cover",
            "source_log": str(args.log.resolve()),
            "source_lines": list(candidate.source_lines),
            "state_bits": state_bits,
            "active_original_hidden_rows": list(active_hidden),
            "fixed_gate": fixed_gate,
            "raw_logic_budget": raw_budget,
            "effective_logic_budget": logic_budget,
            "target_gate_max": args.target_gate_max,
            "target_count": len(targets),
            "target_weight_distribution": {
                str(weight): sum(row.bit_count() == weight for row in targets)
                for weight in sorted({row.bit_count() for row in targets})
            },
            "verified_sequences": {"seeds": 256, "outputs_per_seed": 65},
            "backend": str(backend_path),
        }
    )
    encoded = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode("ascii")
    args.output.write_bytes(encoded)
    print(
        json.dumps(
            {
                "status": result["status"],
                "state_bits": state_bits,
                "targets": len(targets),
                "fixed_gate": fixed_gate,
                "logic_budget": logic_budget,
                "sha256": sha256(encoded).hexdigest(),
            },
            indent=2,
        )
    )
    if return_code not in (10, 20, 30):
        raise SystemExit(return_code)


if __name__ == "__main__":
    main()
