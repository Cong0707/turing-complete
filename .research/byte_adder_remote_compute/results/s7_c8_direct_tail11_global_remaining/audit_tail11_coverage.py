#!/usr/bin/env python3
"""Audit the exact-cost-11 paid-source S7/C8 tail UNSAT cover.

The audit intentionally selects one proof object for every full-CNF triple or
slot0-kind shard.  Extra historical artifacts (notably one timed-out n8/s3
run and a duplicate local n9/x1/slot0=NOT proof) are reported but are not
allowed to satisfy or duplicate the selected cover.
"""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import re
import sys
import tarfile
from typing import Any


EVIDENCE_ROOT = Path(__file__).resolve().parent


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / ".git").exists():
            return candidate
    raise RuntimeError("repository root not found")


REPO_ROOT = find_repo_root(EVIDENCE_ROOT)
REMOTE_TREE = EVIDENCE_ROOT / ".research"
REMOTE_COMPUTE = REMOTE_TREE / "byte_adder_remote_compute"
REMOTE_OUTPUTS = (
    REMOTE_TREE
    / "byte_adder_han_knowles_fused_agent"
    / "tail11-global-results"
)
REMOTE_LOGS = (
    REMOTE_COMPUTE
    / "logs"
    / "s7_c8_direct_tail11_global_remaining_glucose_slot0"
)
REMOTE_RUN_RESULTS = (
    REMOTE_COMPUTE
    / "run-results"
    / "s7_c8_direct_tail11_global_remaining_glucose_slot0"
)
SPEC_PATH = (
    REMOTE_COMPUTE
    / "s7_c8_direct_tail11_global_remaining_glucose_slot0.json"
)
SUMMARY_PATH = (
    REMOTE_COMPUTE
    / "s7-c8-direct-tail11-global-remaining-glucose-slot0-summary.json"
)
STDOUT_PATH = REMOTE_COMPUTE / "tail11-global-runner.stdout.log"
STDERR_PATH = REMOTE_COMPUTE / "tail11-global-runner.stderr.log"

FIRST_BATCH = (
    REPO_ROOT
    / ".research"
    / "byte_adder_remote_compute"
    / "results"
    / "s7_c8_direct_tail11"
)
LOCAL_OUTPUT_ROOT = (
    REPO_ROOT / ".research" / "byte_adder_han_knowles_fused_agent"
)

TARGET_COST = 11
EXPECTED_TRIPLES = [
    (4, 1, 3),
    (5, 4, 1),
    (5, 2, 2),
    (5, 0, 3),
    (6, 5, 0),
    (6, 3, 1),
    (6, 1, 2),
    (7, 4, 0),
    (7, 2, 1),
    (7, 0, 2),
    (8, 3, 0),
    (8, 1, 1),
    (9, 2, 0),
    (9, 0, 1),
    (10, 1, 0),
    (11, 0, 0),
]

DIRECT_LOCAL = {
    (4, 1, 3): (
        "d6_tail_g11_n4_s1x3.json",
        "a62a3c7ec79391301bc1cf136f7aa0e221faa6bb2c536db2ac64a068bd9562eb",
    ),
    (5, 4, 1): (
        "d6_tail_g11_n5_s4x1.json",
        "bd6c626f814687d5c30d172487ab8c6dce0f5106c2815113e6c3d6b948391619",
    ),
    (5, 2, 2): (
        "d6_tail_g11_n5_s2x2.json",
        "8743e82fe9e9c0acbcb70c310db9ff1f2e499a1b794cf36838b342eb686e11b8",
    ),
    (5, 0, 3): (
        "d6_tail_g11_n5_x3.json",
        "549d14b0c1b910df81fcdf83f7040f1c2085c247fa0bdbf92c6d8014a82b70a7",
    ),
    (6, 5, 0): (
        "d6_tail_g11_n6_s5.json",
        "eca04b1fa87b873606ffb432da5b4df1dbc8403d8cc01d0fc6a3c674b75a12ad",
    ),
    (6, 3, 1): (
        "d6_tail_g11_n6_s3x1.json",
        "17d94a768e5b30f9408e0b015db663ad02d90d17942dadc2764056437ca4b249",
    ),
    (6, 1, 2): (
        "d6_tail_g11_n6_s1x2.json",
        "0ff7859779357f6ee7f7c55650ec5adf1da50753b18e4fcdc9729daef9f904f4",
    ),
    (7, 4, 0): (
        "d6_tail_g11_n7_s4.json",
        "5fde38404731f5856e5dc8294365cef0ef3c82480dc8069e6921e43e8ae24073",
    ),
    (7, 2, 1): (
        "d6_tail_g11_n7_s2x1.json",
        "dc5e148f74773ab986cfca00a2f420fc079a609b5879084b0e882fb56ccaa194",
    ),
    (7, 0, 2): (
        "d6_tail_g11_n7_x2.json",
        "511c8bbf6e766c53e394aeba0b9c5f157a42962a904a956c86ddfa89b7aa3227",
    ),
    (8, 1, 1): (
        "d6_tail_g11_n8_s1x1.json",
        "8083755725d98d4841358249e2ae1d2b833744b3460963e9670987796a6825ce",
    ),
}

DIRECT_FIRST_BATCH = {
    (8, 3, 0): (
        "d6_tail_g11_n8_s3_x0.json",
        "6f23274ec8f2155f39022f4938f2d007cfeaf5be1364c68f050f43fc7d95e76f",
    ),
    (9, 2, 0): (
        "d6_tail_g11_n9_s2_x0.json",
        "26c6ca167d03a83b11f4dda32044a97dc8d8ac5e69ead863b673d70a07476209",
    ),
}

EXPECTED_HASHES = {
    "remote-evidence.tar.gz": "0bce967170c833c9c053c243fd40e03b88e478241e3841f67374c16a65e78be6",
    "executed-search_d6_paid_suffix.py": "27ec73e2fb3fa40c9e34dc48af8866ef2af3cf84514d301700c0d54ef3627b43",
    "executed-exact_free_ling_pair_sat.py": "49bb2640e1cb08c6e2b9ac412a8cf56c058f27966e1dd799d1d813c8f1821017",
    "executed-exact_adder_block_sat.py": "f320ed3029b949185acd13b5462b659502a970406d1bf5047713279e152f56de",
    "executed-joint_parity_cnf.py": "a565201bf7e99f6ded6732e70d883cd9a90e5da2e42d72171f11952bb3566ca4",
    "executed-remote_sweep.py": "e01b02714242172b0a3bd4271af90151b6145411665599ba0a3390dd5d442962",
}
EXPECTED_SPEC_SHA = "ba9c2b24306d682b1f1292fc39f65e29ac7812580172e3d6ca21c9b3edf4ccd8"
EXPECTED_SUMMARY_SHA = "ac1e3540ca331a73d1ce953bf5b09048ad71817a0df8bbcdcae14ad84d0445af"
EXPECTED_FIRST_MANIFEST_SHA = "1c8af8218793c32e5d7f877c1798aa200350839788c9bd9569722b33e5d0c9be"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def repo_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path.resolve())


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


errors: list[str] = []


def require(condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def literal_assignment(source: str, name: str) -> Any:
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if any(isinstance(target, ast.Name) and target.id == name for target in targets):
                value = node.value
                return ast.literal_eval(value)
    raise KeyError(name)


def validate_output(
    path: Path,
    triple: tuple[int, int, int],
    *,
    expected_sha: str | None = None,
    slot0_kind: str | None = None,
) -> dict[str, Any]:
    n, switches, xors = triple
    require(path.is_file(), f"missing output: {repo_path(path)}")
    if not path.is_file():
        return {"path": repo_path(path), "status": "missing"}
    actual_sha = sha256(path)
    if expected_sha is not None:
        require(actual_sha == expected_sha, f"output SHA mismatch: {repo_path(path)}")
    payload = load_json(path)
    expected_fields = {
        "schema": "d6-paid-80-suffix-exact-v1",
        "mode": "tail",
        "status": "unsat",
        "gate_bound": TARGET_COST,
        "components": n,
        "exact_switches": switches,
        "exact_xors": xors,
        "slot0_kind": slot0_kind,
        "output_deadlines": [6, 6],
    }
    for key, wanted in expected_fields.items():
        require(
            payload.get(key) == wanted,
            f"{repo_path(path)}: {key}={payload.get(key)!r}, expected {wanted!r}",
        )
    require(
        n + switches + 2 * xors == TARGET_COST,
        f"selected evidence is not exact cost 11: {triple}",
    )
    return {
        "path": repo_path(path),
        "sha256": actual_sha,
        "status": payload.get("status"),
        "solve_seconds": payload.get("solve_seconds"),
        "slot0_kind": payload.get("slot0_kind"),
    }


def verify_manifest(path: Path) -> dict[str, Any]:
    require(path.is_file(), f"missing manifest: {repo_path(path)}")
    checked = 0
    failures: list[str] = []
    if path.is_file():
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            digest, relative = line.split(maxsplit=1)
            candidate = path.parent / relative.strip()
            if not candidate.is_file() or sha256(candidate) != digest:
                failures.append(relative.strip())
            checked += 1
    require(not failures, f"manifest failures: {failures}")
    return {"path": repo_path(path), "entries": checked, "failures": failures}


def validate_batch(
    *,
    spec_path: Path,
    summary_path: Path,
    stdout_path: Path,
    stderr_path: Path,
    output_root: Path,
    log_root: Path,
    run_root: Path,
    expected_spec_sha: str,
    expected_script_sha: str,
    expected_count: int,
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    spec = load_json(spec_path)
    summary = load_json(summary_path)
    require(sha256(spec_path) == expected_spec_sha, f"spec SHA mismatch: {repo_path(spec_path)}")
    require(summary.get("spec_sha256") == expected_spec_sha, "summary spec SHA mismatch")
    require(summary.get("script_sha256") == expected_script_sha, "summary script SHA mismatch")
    require(summary.get("finished") is True, "summary finished is not true")
    require(len(spec.get("values", [])) == expected_count, "unexpected spec value count")
    require(len(summary.get("results", [])) == expected_count, "unexpected summary result count")
    require(stderr_path.stat().st_size == 0, f"stderr is non-empty: {repo_path(stderr_path)}")

    spec_by_name = {item["name"]: item for item in spec["values"]}
    require(len(spec_by_name) == expected_count, "duplicate names in spec")
    summary_by_name: dict[str, dict[str, Any]] = {}
    terminal_counts: dict[str, int] = {}
    output_records: dict[str, dict[str, Any]] = {}
    non_unsat: list[str] = []

    for record in summary["results"]:
        value = record.get("value", {})
        name = value.get("name")
        require(name in spec_by_name, f"summary name absent from spec: {name}")
        if name in spec_by_name:
            require(value == spec_by_name[name], f"summary/spec value mismatch: {name}")
        require(name not in summary_by_name, f"duplicate summary name: {name}")
        summary_by_name[name] = record
        for key in ("state", "status"):
            terminal_counts[f"{key}:{record.get(key)}"] = (
                terminal_counts.get(f"{key}:{record.get(key)}", 0) + 1
            )
        if not (
            record.get("state") == "completed"
            and record.get("status") == "unsat"
            and record.get("return_code") == 0
        ):
            non_unsat.append(str(name))

        run_path = run_root / f"{name}.json"
        require(run_path.is_file(), f"missing runner record: {repo_path(run_path)}")
        if run_path.is_file():
            require(load_json(run_path) == record, f"runner/summary record mismatch: {name}")

        out_path = output_root / Path(record.get("output", "")).name
        log_path = log_root / Path(record.get("log", "")).name
        require(out_path.is_file(), f"missing batch output: {repo_path(out_path)}")
        require(log_path.is_file(), f"missing batch log: {repo_path(log_path)}")
        if out_path.is_file():
            require(sha256(out_path) == record.get("output_sha256"), f"output SHA mismatch: {name}")
        if log_path.is_file():
            require(sha256(log_path) == record.get("log_sha256"), f"log SHA mismatch: {name}")

        triple = (value.get("components"), value.get("switches"), value.get("xors"))
        output_records[name] = validate_output(
            out_path,
            triple,
            expected_sha=record.get("output_sha256"),
            slot0_kind=value.get("slot0_kind"),
        )
        if log_path.is_file():
            log_payload = load_json(log_path)
            for key, wanted in {
                "mode": "tail",
                "status": "unsat",
                "gate_bound": TARGET_COST,
                "components": triple[0],
                "exact_switches": triple[1],
                "exact_xors": triple[2],
                "slot0_kind": value.get("slot0_kind"),
                "output_deadlines": [6, 6],
            }.items():
                require(log_payload.get(key) == wanted, f"log field mismatch {name}:{key}")

        command = record.get("command", [])
        joined = " ".join(str(item) for item in command)
        for token in (
            "--mode tail",
            "--gate-bound 11",
            f"--components {triple[0]}",
            f"--switches {triple[1]}",
            f"--xors {triple[2]}",
            "--timeout 0",
        ):
            require(token in joined, f"command token missing for {name}: {token}")
        if value.get("slot0_kind") is not None:
            require(
                f"--slot0-kind {value['slot0_kind']}" in joined,
                f"slot0 command token missing: {name}",
            )

    require(set(summary_by_name) == set(spec_by_name), "summary/spec name sets differ")
    require(not non_unsat, f"non-UNSAT batch records: {non_unsat}")

    stdout_records = [
        json.loads(line)
        for line in stdout_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    require(len(stdout_records) == expected_count, "unexpected stdout JSON-line count")
    stdout_by_name = {item["value"]["name"]: item for item in stdout_records}
    require(len(stdout_by_name) == expected_count, "duplicate stdout record names")
    require(
        {name: canonical(record) for name, record in stdout_by_name.items()}
        == {name: canonical(record) for name, record in summary_by_name.items()},
        "stdout records differ from summary records",
    )

    batch_report = {
        "spec": repo_path(spec_path),
        "spec_sha256": sha256(spec_path),
        "summary": repo_path(summary_path),
        "summary_sha256": sha256(summary_path),
        "script_sha256": summary.get("script_sha256"),
        "finished": summary.get("finished"),
        "record_count": len(summary_by_name),
        "terminal_counts": terminal_counts,
        "non_unsat": non_unsat,
        "stderr_bytes": stderr_path.stat().st_size,
        "stdout_json_lines": len(stdout_records),
        "workers": summary.get("workers"),
        "timeout_seconds": summary.get("timeout_seconds"),
        "memory_mb_per_process": summary.get("memory_mb_per_process"),
        "nice": summary.get("nice"),
        "cpu_set": summary.get("cpu_set"),
        "python": summary.get("python"),
    }
    return batch_report, output_records


def allowed_slot0_kinds(
    kinds: tuple[str, ...],
    components: int,
    switches: int,
    xors: int,
) -> list[str]:
    allowed: list[str] = []
    for kind in kinds:
        used_switch = int(kind == "SWITCH")
        used_xor = int(kind == "XOR")
        remaining_switches = switches - used_switch
        remaining_xors = xors - used_xor
        if remaining_switches < 0 or remaining_xors < 0:
            continue
        if remaining_switches + remaining_xors > components - 1:
            continue
        allowed.append(kind)
    return allowed


def main() -> int:
    # Byte-for-byte provenance anchors for the archive and executed sources.
    provenance: dict[str, str] = {}
    for name, wanted in EXPECTED_HASHES.items():
        path = EVIDENCE_ROOT / name
        require(path.is_file(), f"missing provenance file: {name}")
        if path.is_file():
            actual = sha256(path)
            provenance[name] = actual
            require(actual == wanted, f"provenance SHA mismatch: {name}")

    require(sha256(SPEC_PATH) == EXPECTED_SPEC_SHA, "executed spec SHA mismatch")
    require(sha256(SUMMARY_PATH) == EXPECTED_SUMMARY_SHA, "global summary SHA mismatch")

    archive_files = archive_members = 0
    archive_path = EVIDENCE_ROOT / "remote-evidence.tar.gz"
    if archive_path.is_file():
        with tarfile.open(archive_path, "r:gz") as archive:
            members = archive.getmembers()
            archive_members = len(members)
            archive_files = sum(member.isfile() for member in members)
        require(archive_members == 58 and archive_files == 55, "unexpected archive member count")

    # Parse the executed primitive library rather than hard-coding the kind order.
    generic_source = (EVIDENCE_ROOT / "executed-joint_parity_cnf.py").read_text(encoding="utf-8")
    kinds = tuple(literal_assignment(generic_source, "KINDS"))
    costs = tuple(literal_assignment(generic_source, "COST"))
    delays = tuple(literal_assignment(generic_source, "DELAY"))
    require(
        kinds == ("NOT", "AND", "OR", "NAND", "NOR", "XOR", "SWITCH"),
        f"unexpected primitive kinds: {kinds}",
    )
    require(costs == (1, 1, 1, 1, 1, 3, 2), f"unexpected primitive costs: {costs}")
    require(delays == (1, 1, 1, 1, 1, 2, 1), f"unexpected primitive delays: {delays}")

    search_source = (EVIDENCE_ROOT / "executed-search_d6_paid_suffix.py").read_text(encoding="utf-8")
    core_source = (EVIDENCE_ROOT / "executed-exact_free_ling_pair_sat.py").read_text(encoding="utf-8")
    exact_source = (EVIDENCE_ROOT / "executed-exact_adder_block_sat.py").read_text(encoding="utf-8")
    source_contract = {
        "seven_kind_slot0_cli": 'choices=("NOT", "AND", "OR", "NAND", "NOR", "XOR", "SWITCH")' in search_source,
        "slot0_unit_clause": 'enc.cnf.append([state["kinds"][0][kind]])' in search_source,
        "deadline_6": "max_delay=6" in search_source and 'output_deadlines="".join' not in search_source,
        "two_tail_targets": '"tail": (s7, c8)' in search_source,
        "one_kind_per_slot": "enc.exactly_one(slot_kinds)" in core_source,
        "exact_switch_count": "lits=[row[G.SWITCH] for row in kinds]" in core_source,
        "exact_xor_count": "lits=[row[G.XOR] for row in kinds]" in core_source,
        "physical_net_partition": "exact._enforce_physical_net_partition(enc, buses)" in core_source,
        "dead_component_forbidden": "enc.clause(users)" in core_source,
        "weighted_gate_bound": "weighted_bound(enc, kinds, args.gate_bound)" in core_source,
        "switch_z_semantics": "value, driven = left and right, left" in core_source,
        "bus_conflict_encoding": "exact.output_bus(" in core_source,
        "physical_partition_definition": "def _enforce_physical_net_partition(" in exact_source,
    }
    # The output-deadline assignment is split over a normal string join.
    source_contract["deadline_6"] = (
        "max_delay=6" in search_source
        and 'output_deadlines=",".join("6" for _ in range(output_count))' in search_source
    )
    for key, value in source_contract.items():
        require(value, f"executed source contract check failed: {key}")

    # Enumerate every non-negative exact-cost decomposition.
    triples = []
    for components in range(1, TARGET_COST + 1):
        for xors in range(TARGET_COST + 1):
            switches = TARGET_COST - components - 2 * xors
            if switches < 0:
                continue
            if switches + xors > components:
                continue
            triples.append((components, switches, xors))
    require(triples == EXPECTED_TRIPLES, f"decomposition mismatch: {triples}")

    # Validate the global 16-shard batch.
    global_batch, global_outputs = validate_batch(
        spec_path=SPEC_PATH,
        summary_path=SUMMARY_PATH,
        stdout_path=STDOUT_PATH,
        stderr_path=STDERR_PATH,
        output_root=REMOTE_OUTPUTS,
        log_root=REMOTE_LOGS,
        run_root=REMOTE_RUN_RESULTS,
        expected_spec_sha=EXPECTED_SPEC_SHA,
        expected_script_sha=EXPECTED_HASHES["executed-search_d6_paid_suffix.py"],
        expected_count=16,
    )
    require(global_batch["summary_sha256"] == EXPECTED_SUMMARY_SHA, "global summary SHA changed")

    # Validate the earlier two full-CNF remote proofs and their 15-file manifest.
    first_manifest = FIRST_BATCH / "SHA256SUMS.txt"
    require(sha256(first_manifest) == EXPECTED_FIRST_MANIFEST_SHA, "first-batch manifest SHA mismatch")
    first_manifest_report = verify_manifest(first_manifest)
    first_spec = FIRST_BATCH / "s7_c8_direct_tail11.json"
    first_summary = FIRST_BATCH / "s7-c8-direct-tail11-summary.json"
    first_batch, first_outputs = validate_batch(
        spec_path=first_spec,
        summary_path=first_summary,
        stdout_path=FIRST_BATCH / "tail11-sweep.stdout.log",
        stderr_path=FIRST_BATCH / "tail11-sweep.stderr.log",
        output_root=FIRST_BATCH / "tail11-results",
        log_root=FIRST_BATCH / "tail11-logs",
        run_root=FIRST_BATCH / "tail11-run-results",
        expected_spec_sha="f8474f3ef8a4f84abb5bb79f0587e5b5aacf9b380c7580e5e69abbb47fcf67a7",
        expected_script_sha="d2ae098e23bf64d4ba5729b2edd2247221053680eb75577c214e0c8b23375e9e",
        expected_count=2,
    )

    # Build the selected 13 full-CNF proof cover.
    full_cnf: dict[tuple[int, int, int], dict[str, Any]] = {}
    for triple, (name, digest) in DIRECT_LOCAL.items():
        full_cnf[triple] = validate_output(
            LOCAL_OUTPUT_ROOT / name,
            triple,
            expected_sha=digest,
        )
        full_cnf[triple]["source"] = "local-full-cnf"
    for triple, (name, digest) in DIRECT_FIRST_BATCH.items():
        path = FIRST_BATCH / "tail11-results" / name
        full_cnf[triple] = validate_output(path, triple, expected_sha=digest)
        full_cnf[triple]["source"] = "remote-first-batch-full-cnf"
        require(name.removesuffix(".json").removeprefix("d6_tail_g11_") in first_outputs, f"first output absent: {name}")

    require(len(full_cnf) == 13, f"expected 13 full-CNF triples, got {len(full_cnf)}")

    # Select one mutually exclusive shard for every feasible slot0 kind.
    shard_name_prefix = {
        (9, 0, 1): "n9x1",
        (10, 1, 0): "n10s1",
        (11, 0, 0): "n11o",
    }
    partition_cover: dict[tuple[int, int, int], dict[str, dict[str, Any]]] = {}
    duplicate_partition: list[dict[str, Any]] = []
    non_unsat: list[dict[str, Any]] = []
    missing: list[Any] = []

    for triple, prefix in shard_name_prefix.items():
        allowed = allowed_slot0_kinds(kinds, *triple)
        chosen: dict[str, dict[str, Any]] = {}
        for kind in allowed:
            if triple == (9, 0, 1) and kind == "XOR":
                path = LOCAL_OUTPUT_ROOT / "d6_tail_g11_n9_x1_slot0_xor_glucose42.json"
                selected = validate_output(
                    path,
                    triple,
                    expected_sha="a839682b269d48aeae64f0e007dfe449994eb5d39d09b275ddd10d5c415dfb68",
                    slot0_kind=kind,
                )
                selected["source"] = "local-glucose42-slot0-shard"
            else:
                name = f"{prefix}_slot0_{kind.lower()}"
                if name not in global_outputs:
                    missing.append({"triple": list(triple), "slot0_kind": kind})
                    continue
                selected = dict(global_outputs[name])
                selected["source"] = "remote-global-glucose42-slot0-shard"
            if kind in chosen:
                duplicate_partition.append({"triple": list(triple), "slot0_kind": kind})
            chosen[kind] = selected
            if selected.get("status") != "unsat":
                non_unsat.append({"triple": list(triple), "slot0_kind": kind, **selected})

        if set(chosen) != set(allowed):
            missing.append(
                {
                    "triple": list(triple),
                    "expected_slot0_kinds": allowed,
                    "selected_slot0_kinds": sorted(chosen),
                }
            )
        partition_cover[triple] = chosen

    # Every decomposition must be covered once, by either a full CNF or a complete shard union.
    covered_triples = set(full_cnf) | set(partition_cover)
    for triple in triples:
        if triple not in covered_triples:
            missing.append({"triple": list(triple)})
    require(covered_triples == set(triples), "triple cover is incomplete or contains extras")
    require(not missing, f"coverage missing: {missing}")
    require(not non_unsat, f"selected non-UNSAT evidence: {non_unsat}")
    require(not duplicate_partition, f"duplicate selected shards: {duplicate_partition}")

    excluded_artifacts = []
    for path, reason in (
        (
            LOCAL_OUTPUT_ROOT / "d6_tail_g11_n8_s3.json",
            "timed-out historical run; status=unknown; replaced by first-batch full-CNF UNSAT",
        ),
        (
            LOCAL_OUTPUT_ROOT / "d6_tail_g11_n9_x1_slot0_not_glucose42.json",
            "duplicate NOT shard; remote global NOT shard selected so the proof partition stays one-to-one",
        ),
    ):
        payload = load_json(path)
        excluded_artifacts.append(
            {
                "path": repo_path(path),
                "sha256": sha256(path),
                "status": payload.get("status"),
                "reason": reason,
            }
        )

    result = {
        "schema": "tc-byte-adder-tail11-coverage-audit-v1",
        "conclusion": (
            "Within the executed paid-source, true-tristate, BUS-conflict, physical-net-partition, "
            "deadline-6 and dead-component model, every exact-cost-11 S7/C8 joint-tail "
            "decomposition is UNSAT."
        ),
        "scope_limits": [
            "not a global byte-adder lower bound",
            "does not automatically prove every cost <= 11 UNSAT",
        ],
        "model": {
            "target": "joint S7/C8 tail",
            "mode": "tail",
            "gate_bound": TARGET_COST,
            "deadline": 6,
            "primitive_kinds": list(kinds),
            "primitive_costs": dict(zip(kinds, costs, strict=True)),
            "primitive_delays": dict(zip(kinds, delays, strict=True)),
            "source_contract": source_contract,
        },
        "provenance": {
            "hashes": provenance,
            "executed_spec_sha256": sha256(SPEC_PATH),
            "global_summary_sha256": sha256(SUMMARY_PATH),
            "archive_members": archive_members,
            "archive_files": archive_files,
        },
        "decomposition": {
            "equation": "components + switches + 2*xors = 11",
            "feasibility": "switches + xors <= components",
            "count": len(triples),
            "triples": [list(triple) for triple in triples],
        },
        "batches": {
            "global_slot0": global_batch,
            "first_full_cnf": first_batch,
            "first_full_cnf_manifest": first_manifest_report,
        },
        "coverage": {
            "full_cnf": {
                "/".join(map(str, triple)): evidence
                for triple, evidence in sorted(full_cnf.items())
            },
            "slot0_partitions": {
                "/".join(map(str, triple)): {
                    "allowed_kinds": allowed_slot0_kinds(kinds, *triple),
                    "mutually_exclusive": source_contract["one_kind_per_slot"],
                    "complete": set(evidence) == set(allowed_slot0_kinds(kinds, *triple)),
                    "evidence": evidence,
                }
                for triple, evidence in sorted(partition_cover.items())
            },
            "covered_triple_count": len(covered_triples),
            "selected_evidence_count": len(full_cnf) + sum(len(items) for items in partition_cover.values()),
            "missing": missing,
            "non_unsat": non_unsat,
            "duplicate_partition": duplicate_partition,
        },
        "excluded_artifacts": excluded_artifacts,
        "errors": errors,
    }

    output_path = EVIDENCE_ROOT / "coverage-audit.json"
    output_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "decomposition_count": len(triples),
                "covered_triple_count": len(covered_triples),
                "selected_evidence_count": result["coverage"]["selected_evidence_count"],
                "global_completed_unsat": global_batch["terminal_counts"].get("status:unsat", 0),
                "missing": missing,
                "non_unsat": non_unsat,
                "duplicate_partition": duplicate_partition,
                "errors": errors,
                "output": repo_path(output_path),
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
