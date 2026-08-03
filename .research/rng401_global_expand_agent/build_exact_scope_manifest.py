"""Build a reproducible manifest for completed radius-7 exact RNG audits."""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def matrix_digest(record: dict) -> str:
    payload = "".join(
        f"{int(str(row), 16):08x}" for row in record["T"]
    ).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def source_xor(record: dict) -> int | None:
    value = record.get("xor")
    if value is None:
        value = (record.get("cover") or {}).get("greedy_xor")
    return None if value is None else int(value)


def iter_jsonl(path: Path):
    with path.open(encoding="utf-8-sig") as stream:
        for line_number, raw in enumerate(stream, 1):
            if raw.strip():
                yield line_number, json.loads(raw)


def relative(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT.resolve())).replace("\\", "/")


def set_digest(digests) -> str:
    payload = "".join(f"{digest}\n" for digest in sorted(digests)).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def main() -> int:
    mixed = ROOT / ".research" / "rng_or_frontier" / "or-hitting-heavy-candidates-r7.jsonl"
    x60_source = ROOT / ".research" / "rng_401_verified_basis" / "x60-heavy43.jsonl"
    model = ROOT / ".research" / "rng_x56_or10_exact" / "joint_mediated_sat.py"
    init_verifier = ROOT / ".research" / "rng_init_reuse" / "verify_init_reuse.py"

    result_files: dict[int, list[Path]] = {
        58: [
            ROOT / ".research" / "rng_or_frontier" / "exact-mediated-target229-r7-x58.jsonl",
        ],
        59: [
            ROOT / ".research" / "rng_or_frontier" / "exact-mediated-target229-r7-tight-x59.jsonl",
            ROOT / ".research" / "rng_or_frontier" / "exact-mediated-target229-r7-new-x59-a.jsonl",
            ROOT / ".research" / "rng_or_frontier" / "exact-mediated-target229-r7-new-x59-b.jsonl",
            HERE / "r7-x59-pending22-cd19-120s.jsonl",
        ],
        60: [
            *sorted((ROOT / ".research" / "rng_401_verified_basis").glob("*exact*.jsonl")),
            *sorted((ROOT / ".research" / "rng_401_verified_basis").glob("*cd19*.jsonl")),
            HERE / "x60-pending10-cd19-120s.jsonl",
        ],
    }
    candidate_sources = {58: mixed, 59: mixed, 60: x60_source}

    scopes = {}
    all_artifacts = {model, init_verifier, mixed, x60_source}
    for xor_count in (58, 59, 60):
        source = candidate_sources[xor_count]
        candidates: dict[str, dict] = {}
        for line_number, record in iter_jsonl(source):
            if source_xor(record) != xor_count:
                continue
            digest = matrix_digest(record)
            candidates.setdefault(digest, {
                "candidate_source_line": line_number,
                "frontier_source_line": record.get("frontier_source_line"),
                "heavy_or_lower_bound": record.get("heavy_or_lower_bound"),
                "target_or": record.get("target_or"),
                "cover_lower": (record.get("cover") or {}).get("lower"),
                "structural_weight": (record.get("structural") or {}).get("weight"),
            })

        observations: dict[str, list[dict]] = defaultdict(list)
        for path in result_files[xor_count]:
            all_artifacts.add(path)
            for line_number, record in iter_jsonl(path):
                digest = str(record.get("T_sha256", "")).lower()
                if digest not in candidates:
                    continue
                observations[digest].append({
                    "artifact": relative(path),
                    "line": line_number,
                    "record": record.get("record"),
                    "status": str(record.get("status", "missing")).lower(),
                    "clause_sha256": record.get("clause_sha256"),
                    "variable_count": record.get("variable_count"),
                    "clause_count": record.get("clause_count"),
                    "solver_seconds": record.get("elapsed_seconds"),
                    "peak_rss_mb": record.get("peak_rss_mb"),
                })

        proof = {}
        unresolved = []
        sat = []
        for digest, metadata in candidates.items():
            found = observations.get(digest, [])
            definitive_unsat = next(
                (item for item in reversed(found) if item["status"] == "unsat"), None
            )
            definitive_sat = next(
                (item for item in reversed(found) if item["status"] == "sat"), None
            )
            if definitive_sat is not None:
                sat.append(digest)
            if definitive_unsat is None and definitive_sat is None:
                unresolved.append(digest)
            proof[digest] = {
                **metadata,
                "definitive": definitive_sat or definitive_unsat,
                "observations": found,
            }

        if unresolved or sat:
            raise AssertionError(
                f"x{xor_count}: unresolved={len(unresolved)} sat={len(sat)}"
            )
        scopes[str(xor_count)] = {
            "candidate_source": relative(source),
            "candidate_unique_T": len(candidates),
            "candidate_T_set_sha256": set_digest(candidates),
            "definitive_unsat_T": len(candidates),
            "unresolved_T": 0,
            "sat_T": 0,
            "proof": proof,
        }

    artifact_hashes = {
        relative(path): {
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        for path in sorted(all_artifacts, key=lambda item: relative(item))
    }
    manifest = {
        "schema": 1,
        "claim": "radius-7 selected canonical depth-two candidate sets are exact-model UNSAT",
        "target": {"max_gate": 401, "delay": 9, "cycles": 67},
        "cost_model": {
            "fixed_shell_gate": 172,
            "logic_budget": 229,
            "xor2_gate": 3,
            "xor2_delay": 2,
            "or_leaf_gate": 1,
            "or_leaf_delay": 1,
        },
        "model": {
            "path": relative(model),
            "sha256": artifact_hashes[relative(model)]["sha256"],
            "identity_checks": ["C*T=A", "T*C=B"],
            "dynamic_replay": "256 official seeds x 65 outputs on SAT certificates",
        },
        "scope_counts": {"58": 75, "59": 203, "60": 121, "total": 399},
        "scopes": scopes,
        "artifacts": artifact_hashes,
    }
    output = HERE / "r7-exact-scope-manifest.json"
    output.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": relative(output),
        "scope_counts": manifest["scope_counts"],
        "set_hashes": {
            key: value["candidate_T_set_sha256"] for key, value in scopes.items()
        },
        "manifest_sha256": sha256_file(output),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
