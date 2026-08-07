"""Strict TOML project configuration and deterministic HDL source discovery."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from pathlib import Path
import re
import tomllib


HDL_SUFFIXES = frozenset({".v", ".sv"})
GLOB_MAGIC = re.compile(r"[*?[]")
DEFINE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*(?:=[^\s\"]*)?\Z")


@dataclass(frozen=True)
class PortBinding:
    component_label: str
    pin: str


@dataclass(frozen=True)
class ComponentConfig:
    name: str
    top: str
    sources: tuple[Path, ...]
    include_dirs: tuple[Path, ...]
    defines: tuple[str, ...]
    parameters: tuple[tuple[str, str], ...]
    dependencies: tuple[str, ...]
    logical_key: str
    display_path: str
    description: str


@dataclass(frozen=True)
class PackageConfig:
    enabled: bool = False
    level: str = ""
    filename: str = "package.pk"


@dataclass(frozen=True)
class ProjectConfig:
    manifest: Path
    name: str
    top: str
    sources: tuple[Path, ...]
    target_kind: str
    logical_key: str
    description: str
    template: Path | None
    port_bindings: dict[str, PortBinding]
    pack_widths: tuple[int, ...]
    horizontal_clearance: int
    vertical_clearance: int
    include_dirs: tuple[Path, ...] = ()
    defines: tuple[str, ...] = ()
    parameters: tuple[tuple[str, str], ...] = ()
    components: tuple[ComponentConfig, ...] = ()
    package: PackageConfig = field(default_factory=PackageConfig)

    def for_component(self, component: ComponentConfig) -> "ProjectConfig":
        """Return the ordinary Foundry build view for one reusable module."""

        return replace(
            self,
            name=component.name,
            top=component.top,
            sources=component.sources,
            target_kind="foundry",
            logical_key=component.logical_key,
            description=component.description,
            template=None,
            port_bindings={},
            include_dirs=component.include_dirs,
            defines=component.defines,
            parameters=component.parameters,
            components=(),
            package=PackageConfig(),
        )


def _nonempty(value: object, field_name: str) -> str:
    text = str(value).strip()
    if not text:
        raise ValueError(f"{field_name} cannot be empty")
    return text


def _string_list(value: object, field_name: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ValueError(f"{field_name} must be an array of strings")
    return tuple(_nonempty(item, field_name) for item in value)


def _parameters(value: object, field_name: str) -> tuple[tuple[str, str], ...]:
    if value is None:
        return ()
    if not isinstance(value, dict):
        raise ValueError(f"{field_name} must be a TOML table")
    result = []
    for name, raw in value.items():
        name = _nonempty(name, field_name)
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_$]*", name):
            raise ValueError(f"{field_name} contains invalid parameter {name!r}")
        result.append((name, _nonempty(raw, f"{field_name}.{name}")))
    return tuple(sorted(result))


def _defines(value: object, field_name: str) -> tuple[str, ...]:
    values = _string_list(value, field_name)
    invalid = [item for item in values if DEFINE.fullmatch(item) is None]
    if invalid:
        raise ValueError(f"{field_name} contains invalid definitions: {invalid!r}")
    return values


def _include_dirs(base: Path, value: object, field_name: str) -> tuple[Path, ...]:
    values = _string_list(value, field_name)
    result = tuple((base / item).resolve() for item in values)
    missing = [str(path) for path in result if not path.is_dir()]
    if missing:
        raise FileNotFoundError(f"HDL include directories are missing: {missing!r}")
    return result


def _source_files(path: Path) -> tuple[Path, ...]:
    if path.is_file():
        if path.suffix.lower() not in HDL_SUFFIXES:
            raise ValueError(f"HDL compilation unit must end in .v or .sv: {path}")
        return (path.resolve(),)
    if path.is_dir():
        return tuple(
            sorted(
                item.resolve()
                for item in path.rglob("*")
                if item.is_file() and item.suffix.lower() in HDL_SUFFIXES
            )
        )
    return ()


def _resolve_sources(base: Path, value: object, field_name: str) -> tuple[Path, ...]:
    entries = _string_list(value, field_name)
    if not entries:
        raise ValueError(f"{field_name} must be a non-empty array")
    result: list[Path] = []
    seen: set[Path] = set()
    for entry in entries:
        matches = (
            tuple(sorted(base.glob(entry)))
            if GLOB_MAGIC.search(entry)
            else ((base / entry).resolve(),)
        )
        expanded = tuple(
            source
            for match in matches
            for source in _source_files(match)
        )
        if not expanded:
            raise FileNotFoundError(
                f"{field_name} entry did not resolve to any .v/.sv file: {entry!r}"
            )
        for source in expanded:
            if source not in seen:
                seen.add(source)
                result.append(source)
    return tuple(result)


def _merge_unique(left: tuple[str, ...], right: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys((*left, *right)))


def _merge_parameters(
    left: tuple[tuple[str, str], ...], right: tuple[tuple[str, str], ...]
) -> tuple[tuple[str, str], ...]:
    return tuple(sorted({**dict(left), **dict(right)}.items()))


def _safe_archive_path(value: object, field_name: str) -> str:
    text = _nonempty(value, field_name).replace("\\", "/").strip("/")
    parts = text.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise ValueError(f"{field_name} must be a safe relative path")
    return "/".join(parts)


def load_project(path: Path) -> ProjectConfig:
    manifest = Path(path).resolve()
    raw = tomllib.loads(manifest.read_text(encoding="utf-8"))
    project = raw.get("project")
    target = raw.get("target")
    if not isinstance(project, dict) or not isinstance(target, dict):
        raise ValueError("project.toml requires [project] and [target]")
    base = manifest.parent
    sources = _resolve_sources(base, project.get("sources"), "project.sources")
    include_dirs = _include_dirs(
        base, project.get("include_dirs"), "project.include_dirs"
    )
    defines = _defines(project.get("defines"), "project.defines")
    parameters = _parameters(project.get("parameters"), "project.parameters")

    target_kind = _nonempty(target.get("kind", "foundry"), "target.kind")
    if target_kind not in {"foundry", "level"}:
        raise ValueError("target.kind must be 'foundry' or 'level'")
    template_raw = target.get("template")
    template = (base / str(template_raw)).resolve() if template_raw else None
    if target_kind == "level" and (template is None or not template.is_file()):
        raise ValueError("level target requires an existing target.template v15 file")
    bindings_raw = target.get("ports", {})
    if not isinstance(bindings_raw, dict):
        raise ValueError("target.ports must be a TOML table")
    bindings: dict[str, PortBinding] = {}
    for port_name, binding in bindings_raw.items():
        if not isinstance(binding, dict):
            raise ValueError(f"target.ports.{port_name} must be a table")
        bindings[str(port_name)] = PortBinding(
            component_label=_nonempty(binding.get("component_label"), "component_label"),
            pin=_nonempty(binding.get("pin", "value"), "pin"),
        )

    compile_raw = raw.get("compile", {})
    layout_raw = raw.get("layout", {})
    if not isinstance(compile_raw, dict) or not isinstance(layout_raw, dict):
        raise ValueError("compile and layout must be TOML tables")
    pack_widths = tuple(int(value) for value in compile_raw.get("pack_widths", [8, 4, 2]))
    if not pack_widths or any(value not in {2, 4, 8} for value in pack_widths):
        raise ValueError("compile.pack_widths may contain only 2, 4, and 8")
    if tuple(sorted(set(pack_widths), reverse=True)) != pack_widths:
        raise ValueError("compile.pack_widths must be unique and descending")

    project_top = _nonempty(project.get("top"), "project.top")
    project_name = _nonempty(project.get("name", project_top), "project.name")
    project_logical_key = _nonempty(
        target.get("logical_key", f"foundry/codex/verilog/{project_top}"),
        "target.logical_key",
    )
    components_raw = raw.get("components", [])
    if not isinstance(components_raw, list):
        raise ValueError("[[components]] entries must form an array of tables")
    components: list[ComponentConfig] = []
    for index, item in enumerate(components_raw):
        field_name = f"components[{index}]"
        if not isinstance(item, dict):
            raise ValueError(f"{field_name} must be a TOML table")
        component_top = _nonempty(item.get("top", item.get("name")), f"{field_name}.top")
        component_name = _nonempty(item.get("name", component_top), f"{field_name}.name")
        own_includes = _include_dirs(
            base, item.get("include_dirs"), f"{field_name}.include_dirs"
        )
        own_defines = _defines(item.get("defines"), f"{field_name}.defines")
        own_parameters = _parameters(item.get("parameters"), f"{field_name}.parameters")
        components.append(
            ComponentConfig(
                name=component_name,
                top=component_top,
                sources=_resolve_sources(base, item.get("sources"), f"{field_name}.sources"),
                include_dirs=tuple(dict.fromkeys((*include_dirs, *own_includes))),
                defines=_merge_unique(defines, own_defines),
                parameters=own_parameters,
                dependencies=_string_list(item.get("dependencies"), f"{field_name}.dependencies"),
                logical_key=_nonempty(
                    item.get("logical_key", f"{project_logical_key}/{component_name}"),
                    f"{field_name}.logical_key",
                ),
                display_path=_safe_archive_path(
                    item.get("display_path", f"codex/{component_name}"),
                    f"{field_name}.display_path",
                ),
                description=str(item.get("description", f"Generated component {component_name}")).strip(),
            )
        )
    names = [component.name for component in components]
    tops = [component.top for component in components]
    if len(names) != len(set(names)):
        raise ValueError("[[components]] names must be unique")
    if len(tops) != len(set(tops)):
        raise ValueError("[[components]] top modules must be unique")
    name_set = set(names)
    for component in components:
        unknown = set(component.dependencies) - name_set
        if unknown:
            raise ValueError(
                f"component {component.name!r} has unknown dependencies: {sorted(unknown)!r}"
            )
        if component.name in component.dependencies:
            raise ValueError(f"component {component.name!r} depends on itself")

    package_raw = raw.get("package", {})
    if not isinstance(package_raw, dict):
        raise ValueError("package must be a TOML table")
    package_enabled = bool(package_raw.get("enabled", bool(components)))
    package_filename = _nonempty(
        package_raw.get("filename", f"{project_top}.pk"), "package.filename"
    )
    if Path(package_filename).name != package_filename or not package_filename.lower().endswith(".pk"):
        raise ValueError("package.filename must be a plain .pk filename")

    return ProjectConfig(
        manifest=manifest,
        name=project_name,
        top=project_top,
        sources=sources,
        target_kind=target_kind,
        logical_key=project_logical_key,
        description=str(target.get("description", "Generated by turingsynth")).strip(),
        template=template,
        port_bindings=bindings,
        pack_widths=pack_widths,
        horizontal_clearance=max(5, int(layout_raw.get("horizontal_clearance", 5))),
        vertical_clearance=max(3, int(layout_raw.get("vertical_clearance", 3))),
        include_dirs=include_dirs,
        defines=defines,
        parameters=parameters,
        components=tuple(components),
        package=PackageConfig(
            enabled=package_enabled,
            level=str(package_raw.get("level", "")),
            filename=package_filename,
        ),
    )
