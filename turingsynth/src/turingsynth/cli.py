"""Command-line interface used by the top-level compile.py driver."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil

from turingsynth.pipeline import build_project
from turingsynth.relayout import relayout_v15


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="turingsynth",
        description="将可综合 Verilog 编译为可审计的 Turing Complete v15 电路。",
    )
    parser.add_argument(
        "manifest",
        nargs="?",
        type=Path,
        help="project.toml；省略时使用当前目录 project.toml",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="只删除编译器根目录下唯一的 build/",
    )
    parser.add_argument(
        "--relayout-v15",
        type=Path,
        help="导入现有 v15 电路，仅重新布局和布线",
    )
    return parser


def main(argv: list[str] | None = None, *, compiler_root: Path | None = None) -> int:
    root = Path(compiler_root or Path(__file__).resolve().parents[2]).resolve()
    args = _parser().parse_args(argv)
    build = root / "build"
    if args.clean:
        if build.exists():
            shutil.rmtree(build)
        return 0
    if args.relayout_v15 is not None:
        report = relayout_v15(root, args.relayout_v15)
    else:
        manifest = (args.manifest or Path("project.toml")).resolve()
        report = build_project(root, manifest)
    print(
        json.dumps(
            {
                "status": report["status"],
                "score": report["score"],
                "circuit": str(build / report["artifacts"]["circuit"]),
                "preview": str(build / report["artifacts"]["preview"]),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0
