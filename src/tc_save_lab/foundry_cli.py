"""Codex 自定义元件的交互式构建与显式部署入口。"""

from __future__ import annotations

from argparse import ArgumentParser, Namespace
from pathlib import Path
import json

from .foundry import (
    build_codex_candidate_from_json,
    deploy_codex_foundry,
    plan_codex_deployment,
)
from .storage import DEFAULT_SAVE_ROOT


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class ChineseArgumentParser(ArgumentParser):
    def __init__(self, *args: object, **kwargs: object) -> None:
        kwargs["add_help"] = False
        super().__init__(*args, **kwargs)
        self.add_argument("-h", "--help", action="help", help="显示帮助并退出")
        self._positionals.title = "子命令"
        self._optionals.title = "选项"


def _path(value: str) -> Path:
    return Path(value).expanduser().resolve()


def build_parser() -> ArgumentParser:
    parser = ChineseArgumentParser(
        prog="tc-foundry",
        description=__doc__,
    )
    sub = parser.add_subparsers(dest="command")

    build = sub.add_parser("build", help="从 Circuit JSON 构建一个 Codex 自定义元件")
    build.add_argument("logical_key", help="不可变 ASCII 身份键，例如 not_gate")
    build.add_argument("display_path", help="元件工坊中的中文目录名")
    build.add_argument("source", type=_path, help="包含元件和导线的 Circuit JSON")
    build.add_argument("--project-root", type=_path, default=PROJECT_ROOT)
    build.add_argument(
        "--dependency-root",
        type=_path,
        action="append",
        help="只读依赖根；可重复指定，默认扫描当前正式 Foundry",
    )
    build.add_argument(
        "--allow-interface-change",
        action="store_true",
        help="显式允许改变已注册接口；必须同步更新所有父电路",
    )

    deploy = sub.add_parser("deploy", help="计划或显式部署全部已注册 Codex 元件")
    deploy.add_argument("--project-root", type=_path, default=PROJECT_ROOT)
    deploy.add_argument("--save-root", type=_path, default=DEFAULT_SAVE_ROOT)
    deploy.add_argument("--dry-run", action="store_true", help="只生成部署计划，不写存档")
    deploy.add_argument("--yes", action="store_true", help="跳过交互确认")
    return parser


def _print_json(value: object) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def _run(args: Namespace) -> int:
    if args.command == "build":
        dependency_roots = tuple(args.dependency_root or ())
        if not dependency_roots:
            dependency_roots = (DEFAULT_SAVE_ROOT / "schematics" / "foundry",)
        result = build_codex_candidate_from_json(
            args.project_root,
            args.logical_key,
            args.display_path,
            args.source,
            dependency_roots=dependency_roots,
            allow_interface_change=args.allow_interface_change,
        )
        _print_json(result)
        return 0
    if args.command == "deploy":
        plan = plan_codex_deployment(args.project_root, args.save_root)
        _print_json(plan.to_dict())
        if args.dry_run:
            return 0
        if not args.yes:
            answer = input(
                f"将 {len(plan.items)} 个 Codex 元件部署到 {plan.target_root}？[y/N] "
            ).strip().casefold()
            if answer not in {"y", "yes"}:
                print("已取消，正式存档未修改。")
                return 2
        _print_json(deploy_codex_foundry(plan))
        return 0
    raise ValueError(f"不支持的命令：{args.command}")


def _interactive(parser: ArgumentParser) -> int:
    while True:
        print("\nTuring Complete Codex Foundry")
        print("1. 构建自定义元件候选")
        print("2. 只读检查部署计划")
        print("3. 显式部署全部 Codex 元件")
        print("0. 退出")
        choice = input("> ").strip()
        if choice == "0":
            return 0
        if choice == "1":
            logical_key = input("稳定逻辑键（ASCII）: ").strip()
            display_path = input("中文元件目录名: ").strip()
            source = input("Circuit JSON 路径: ").strip()
            if logical_key and display_path and source:
                return _run(parser.parse_args(["build", logical_key, display_path, source]))
        if choice == "2":
            return _run(parser.parse_args(["deploy", "--dry-run"]))
        if choice == "3":
            return _run(parser.parse_args(["deploy"]))
        print("无效选择。")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        return _interactive(parser)
    return _run(args)


if __name__ == "__main__":
    raise SystemExit(main())
