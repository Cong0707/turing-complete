"""Freeze SHA and submission lists for the completed broad C5 proof set."""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SHA_OUTPUT = HERE / "bit34_broad_c5_SHA256SUMS.txt"
SUBMIT_OUTPUT = HERE / "bit34_broad_c5_submit_files.txt"

TOP_LEVEL_NAMES = (
    "2026-08-04-strict-C3-bit34-broad-C5正常形g13完备UNSAT.md",
    "2026-08-04-bit34-broad-C5正常形独立静态覆盖审计.md",
    "2026-08-04-bit34-broad-C5远端230片终态独立审计.md",
    "bit34_broad_c5_normal_form.py",
    "exact_bit34_broad_c5_normal_form_shard.py",
    "verify_bit34_broad_c5_positive_regression.py",
    "bit34_broad_c5_positive_g14.json",
    "bit34_broad_c5_positive_g14_independent_verify.json",
    "summarize_bit34_broad_c5_shards.py",
    "bit34_broad_c5_smoke_n00_n02_complete.json",
    "remote_broad_c5_sweep_stop_on_sat.py",
    "generate_bit34_broad_c5_remote.py",
    "bit34_d7_g13_broad_c5_normal_form_workers3.json",
    "bit34_d7_g13_broad_c5_normal_form_workers3_manifest.json",
    "bit34_d7_g13_broad_c5_remote_validate.json",
    "bit34-d7-g13-broad-c5-normal-form-workers3-summary.json",
    "summarize_bit34_broad_c5_shards.py",
    "bit34_d7_g13_broad_c5_normal_form_complete.json",
    "verify_bit34_broad_c5_remote_summary.py",
    "bit34_d7_g13_broad_c5_remote_transport_verify.json",
    "generate_bit34_broad_c5_completion.py",
    "bit34_d7_g13_broad_c5_remote_completion_manifest.json",
    "generate_bit34_broad_c5_freeze.py",
)
DEPENDENCIES = (
    HERE / "exact_bit34_joint_sat.py",
    ROOT
    / ".research"
    / "byte_adder_pair_macro_exact"
    / "exact_paid_physical_search_core.py",
    ROOT
    / ".research"
    / "byte_adder_pair_macro_exact"
    / "exact_paid_physical_core.py",
    ROOT
    / ".research"
    / "byte_adder_pair_macro_exact"
    / "exact_paid_physical_cnf.py",
    ROOT / ".research" / "byte_adder_remote_compute" / "remote_sweep.py",
    HERE / "remote_sweep_stop_on_sat.py",
    HERE / "verify_bit34_certificate.py",
)


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def atomic_text(path: Path, text: str) -> None:
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(text, encoding="utf-8", newline="\n")
    temporary.replace(path)


def main() -> int:
    top_level = [HERE / name for name in dict.fromkeys(TOP_LEVEL_NAMES)]
    smoke = sorted((HERE / "broad_c5_smoke").glob("*.json"))
    results = sorted(
        (
            HERE
            / "remote_results"
            / "bit34_d7_g13_broad_c5_normal_form"
        ).glob("*.json")
    )
    runner_log = (
        HERE
        / "remote_results"
        / "bit34_d7_g13_broad_c5_normal_form_runner.log"
    )
    if len(smoke) != 7:
        raise RuntimeError(f"expected 7 smoke files, got {len(smoke)}")
    if len(results) != 230:
        raise RuntimeError(f"expected 230 remote result files, got {len(results)}")
    paths = [*top_level, *smoke, runner_log, *results, *DEPENDENCIES]
    missing = [str(path) for path in paths if not path.is_file()]
    if missing:
        raise RuntimeError(f"freeze inputs missing: {missing}")
    relative_paths = [relative(path) for path in paths]
    if len(relative_paths) != len(set(relative_paths)):
        raise RuntimeError("freeze input list contains duplicate paths")

    submit_lines = [
        "# Broad strict-C3 bit34 proof/report/search artifacts",
        *(relative(path) for path in top_level),
        *(relative(path) for path in smoke),
        relative(runner_log),
        *(relative(path) for path in results),
        relative(SHA_OUTPUT),
        relative(SUBMIT_OUTPUT),
        "",
        "# Frozen replay dependencies; include if absent from the target commit",
        *(relative(path) for path in DEPENDENCIES),
        "",
        "# Shared tracked history updated by this checkpoint",
        "examples/byte_adder/history/字节加法器.md",
    ]
    atomic_text(SUBMIT_OUTPUT, "\n".join(submit_lines) + "\n")

    sha_paths = [*paths, SUBMIT_OUTPUT]
    sha_lines = [
        "# SHA-256 for the completed strict-C3 bit34 broad-C5 proof set.",
        "# The shared append-only history is excluded because sibling tasks may append.",
    ]
    sha_lines.extend(
        f"{file_sha256(path)}  {relative(path)}" for path in sha_paths
    )
    atomic_text(SHA_OUTPUT, "\n".join(sha_lines) + "\n")
    print(
        f"sha_entries={len(sha_paths)} sha256={file_sha256(SHA_OUTPUT)} "
        f"submit_entries={len(submit_lines)} "
        f"submit_sha256={file_sha256(SUBMIT_OUTPUT)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
