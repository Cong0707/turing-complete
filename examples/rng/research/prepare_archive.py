"""Build the reviewable RNG research archive used by the postmortem.

Large solver traces and reverse-engineering databases stay outside Git.  This
script preserves authored source, reports, compact certificates, and circuit
artifacts while writing a manifest that makes the selection reproducible.
"""

from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import shutil


SOURCE_ROOT = Path(r"D:\Develop\Other\turing-complete\.research")
ARCHIVE_ROOT = Path(__file__).resolve().parent / "archive"
MANIFEST_PATH = Path(__file__).resolve().parent / "archive-manifest.json"
MAX_FILE_SIZE = 2 * 1024 * 1024

INCLUDED_SUFFIXES = {
    ".aig",
    ".assembly",
    ".blif",
    ".c",
    ".cpp",
    ".csv",
    ".data",
    ".h",
    ".hpp",
    ".hs",
    ".json",
    ".md",
    ".out",
    ".ps1",
    ".py",
    ".rom",
    ".sh",
    ".sv",
    ".tc",
    ".toml",
    ".tsv",
    ".txt",
    ".v",
    ".yaml",
    ".yml",
}
EXCLUDED_PARTS = {"__pycache__", "_vendor", ".venv", ".git"}


def digest(path: Path) -> str:
    value = sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def score_bypass_evidence(relative: Path) -> bool:
    """Keep only static engine evidence from the invalid score-bypass branch."""

    parts = relative.parts
    if not parts or parts[0] != "rng_score_bypass":
        return True
    return (
        len(parts) >= 4
        and parts[1] == "ida"
        and parts[2] in {"ram", "score_network"}
        and relative.suffix.lower() in {".c", ".md", ".json"}
    )


def exclusion_reason(path: Path, relative: Path) -> str | None:
    if any(part in EXCLUDED_PARTS for part in relative.parts):
        return "generated-or-vendored-directory"
    if not score_bypass_evidence(relative):
        return "invalid-score-or-auth-experiment"
    if path.suffix.lower() not in INCLUDED_SUFFIXES:
        return "binary-or-regenerable-extension"
    if path.stat().st_size > MAX_FILE_SIZE:
        return "large-regenerable-artifact"
    return None


def main() -> None:
    if ARCHIVE_ROOT.exists() and any(ARCHIVE_ROOT.iterdir()):
        raise RuntimeError(f"archive destination is not empty: {ARCHIVE_ROOT}")
    ARCHIVE_ROOT.mkdir(parents=True, exist_ok=True)

    included: list[dict[str, object]] = []
    excluded = Counter()
    excluded_bytes = Counter()
    roots = sorted(path for path in SOURCE_ROOT.glob("rng_*") if path.is_dir())
    for root in roots:
        for source in sorted(path for path in root.rglob("*") if path.is_file()):
            relative = source.relative_to(SOURCE_ROOT)
            reason = exclusion_reason(source, relative)
            size = source.stat().st_size
            if reason:
                excluded[reason] += 1
                excluded_bytes[reason] += size
                continue
            destination = ARCHIVE_ROOT / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            included.append(
                {
                    "path": relative.as_posix(),
                    "bytes": size,
                    "sha256": digest(destination),
                }
            )

    manifest = {
        "schema": 1,
        "source_root": str(SOURCE_ROOT),
        "archive_root": "examples/rng/research/archive",
        "source_directory_count": len(roots),
        "included_file_count": len(included),
        "included_bytes": sum(int(item["bytes"]) for item in included),
        "maximum_included_file_bytes": MAX_FILE_SIZE,
        "included": included,
        "excluded_summary": {
            reason: {
                "file_count": excluded[reason],
                "bytes": excluded_bytes[reason],
            }
            for reason in sorted(excluded)
        },
    }
    MANIFEST_PATH.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({key: value for key, value in manifest.items() if key != "included"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
