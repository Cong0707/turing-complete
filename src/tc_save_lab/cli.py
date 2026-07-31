"""命令行与交互式操作入口。"""

from __future__ import annotations

from argparse import ArgumentParser, Namespace
from pathlib import Path
import json

from .campaign import initialize_examples, read_level_meta
from .codec import decode_circuit
from .analysis import analyze_examples, analyze_file
from .builder import build_known_candidates
from .scaffold import extract_campaign_scaffolds
from .storage import (
    DEFAULT_GAME_ROOT,
    DEFAULT_SAVE_ROOT,
    atomic_replace_circuit,
    export_json,
    import_json,
    inventory,
    read_progress,
    selected_circuit_path,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class ChineseArgumentParser(ArgumentParser):
    """ArgumentParser with Chinese headings for the public CLI."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        kwargs["add_help"] = False
        super().__init__(*args, **kwargs)
        self.add_argument("-h", "--help", action="help", help="显示帮助并退出")
        self._positionals.title = "子命令"
        self._optionals.title = "选项"


def _path(value: str) -> Path:
    return Path(value).expanduser().resolve()


def build_parser() -> ArgumentParser:
    parser = ChineseArgumentParser(prog="tc-save", description=__doc__)
    sub = parser.add_subparsers(dest="command")

    inspect = sub.add_parser("inspect", help="检查当前存档中的所有 circuit.data")
    inspect.add_argument("--save-root", type=_path, default=DEFAULT_SAVE_ROOT)

    init = sub.add_parser("init-examples", help="为每个主线关卡创建版本化工作目录")
    init.add_argument("--project-root", type=_path, default=PROJECT_ROOT)
    init.add_argument("--game-root", type=_path, default=DEFAULT_GAME_ROOT)
    init.add_argument("--save-root", type=_path, default=DEFAULT_SAVE_ROOT)

    scaffolds = sub.add_parser(
        "extract-scaffolds",
        help="提取每个主线关卡的不可变端口脚手架",
    )
    scaffolds.add_argument("--project-root", type=_path, default=PROJECT_ROOT)
    scaffolds.add_argument("--game-root", type=_path, default=DEFAULT_GAME_ROOT)

    analyze = sub.add_parser(
        "analyze",
        help="计算单个电路的离线几何与结构指标",
    )
    analyze.add_argument("source", type=_path)

    analyze_all = sub.add_parser(
        "analyze-examples",
        help="为所有示例关卡生成 metrics.json",
    )
    analyze_all.add_argument("--project-root", type=_path, default=PROJECT_ROOT)

    build_known = sub.add_parser(
        "build-known-candidates",
        help="生成已经审查的确定性优化候选",
    )
    build_known.add_argument("--project-root", type=_path, default=PROJECT_ROOT)

    dump = sub.add_parser("export-json", help="把支持的电路格式解析为 JSON")
    dump.add_argument("source", type=_path)
    dump.add_argument("destination", type=_path)

    build = sub.add_parser("build", help="把可编辑 JSON 编码为经过校验的 v15 电路")
    build.add_argument("source", type=_path)
    build.add_argument("destination", type=_path)

    validate = sub.add_parser("validate", help="严格解析并校验一个受支持的电路")
    validate.add_argument("source", type=_path)

    apply = sub.add_parser("apply", help="把一个候选原子写入当前选中的存档槽位")
    apply.add_argument("level")
    apply.add_argument("--candidate", type=_path)
    apply.add_argument("--game-root", type=_path, default=DEFAULT_GAME_ROOT)
    apply.add_argument("--save-root", type=_path, default=DEFAULT_SAVE_ROOT)
    apply.add_argument("--yes", action="store_true")
    return parser


def _print_json(value: object) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def _run(args: Namespace) -> int:
    if args.command == "inspect":
        records = inventory(args.save_root)
        _print_json(
            {
                "save_root": str(args.save_root),
                "circuit_count": len(records),
                "invalid_count": sum(not bool(item.get("valid_v15")) for item in records),
                "circuits": records,
            }
        )
        return 0
    if args.command == "init-examples":
        result = initialize_examples(
            args.project_root,
            args.game_root / "campaign",
            args.save_root,
        )
        _print_json({key: value for key, value in result.items() if key != "levels"})
        return 0
    if args.command == "extract-scaffolds":
        _print_json(
            extract_campaign_scaffolds(
                args.project_root,
                args.game_root / "campaign",
            )
        )
        return 0
    if args.command == "analyze":
        _print_json(analyze_file(args.source))
        return 0
    if args.command == "analyze-examples":
        _print_json(analyze_examples(args.project_root))
        return 0
    if args.command == "build-known-candidates":
        _print_json(build_known_candidates(args.project_root))
        return 0
    if args.command == "export-json":
        circuit = export_json(args.source, args.destination)
        _print_json({"destination": str(args.destination), "components": len(circuit.components), "wires": len(circuit.wires)})
        return 0
    if args.command == "build":
        circuit = import_json(args.source, args.destination)
        _print_json({"destination": str(args.destination), "components": len(circuit.components), "wires": len(circuit.wires)})
        return 0
    if args.command == "validate":
        payload = args.source.read_bytes()
        circuit = decode_circuit(payload)
        _print_json(
            {
                "valid": True,
                "format_version": payload[0],
                "gate": circuit.gate,
                "delay": circuit.delay,
                "energy": circuit.energy,
                "components": len(circuit.components),
                "wires": len(circuit.wires),
            }
        )
        return 0
    if args.command == "apply":
        progress = read_progress(args.save_root / "levels.txt")
        selected = progress.get(args.level)
        meta = read_level_meta(args.game_root / "campaign" / args.level / "meta.txt")
        if meta.get("kind") == "architecture":
            if selected is None or not selected.selected_schematic:
                raise ValueError(f"level {args.level!r} has no selected architecture")
            destination = (
                args.save_root
                / "schematics"
                / "architecture"
                / selected.selected_schematic
                / "circuit.data"
            )
            candidate = args.candidate or (
                PROJECT_ROOT
                / "examples"
                / "_architectures"
                / selected.selected_schematic
                / "candidate"
                / "circuit.data"
            )
        else:
            destination = selected_circuit_path(args.save_root, progress, args.level)
            candidate = args.candidate or PROJECT_ROOT / "examples" / args.level / "candidate" / "circuit.data"
        if not args.yes:
            answer = input(f"将 {candidate} 写入 {destination}？[y/N] ").strip().casefold()
            if answer not in {"y", "yes"}:
                print("已取消。")
                return 2
        _print_json(atomic_replace_circuit(candidate, destination))
        return 0
    raise ValueError(f"不支持的命令：{args.command}")


def _interactive(parser: ArgumentParser) -> int:
    while True:
        print("\nTuring Complete Save Lab")
        print("1. 检查正式存档")
        print("2. 初始化/刷新所有主线关卡目录")
        print("3. 提取所有关卡固定脚手架")
        print("4. 分析所有示例基线")
        print("5. 构建已审查的优化候选")
        print("6. 写回一个关卡候选")
        print("0. 退出")
        choice = input("> ").strip()
        if choice == "0":
            return 0
        if choice == "1":
            return _run(parser.parse_args(["inspect"]))
        if choice == "2":
            return _run(parser.parse_args(["init-examples"]))
        if choice == "3":
            return _run(parser.parse_args(["extract-scaffolds"]))
        if choice == "4":
            return _run(parser.parse_args(["analyze-examples"]))
        if choice == "5":
            return _run(parser.parse_args(["build-known-candidates"]))
        if choice == "6":
            level = input("关卡内部名称: ").strip()
            if level:
                return _run(parser.parse_args(["apply", level]))
        print("无效选择。")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        return _interactive(parser)
    return _run(args)
