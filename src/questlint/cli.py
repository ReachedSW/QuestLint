import argparse
from pathlib import Path

from questlint.core.analyzer import Analyzer
from questlint.core.config import ConfigError, Settings, discover_config, load_config
from questlint.core.source import SourceFile
from questlint.reporters.json import render
from questlint.reporters.sarif import render as render_sarif
from questlint.reporters.text import format_diagnostic, summary
from questlint.version import __version__

SKIP_DIRECTORIES = {".git", "build", "dist", ".venv", "__pycache__"}


def discover(paths: list[str], excludes: tuple[str, ...] = ()) -> list[Path]:
    files: set[Path] = set()
    for item in paths:
        path = Path(item)
        if path.is_file() and path.suffix == ".lua":
            files.add(path)
        elif path.is_dir():
            files.update(
                p
                for p in path.rglob("*.lua")
                if not any(part in SKIP_DIRECTORIES for part in p.parts)
                and not any(
                    p.relative_to(path).as_posix().startswith(pattern.rstrip("*").rstrip("/"))
                    for pattern in excludes
                )
            )
    return sorted(files, key=lambda path: str(path))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="questlint", description="Static analysis for Lua source files."
    )
    parser.add_argument("paths", nargs="+", help="Lua files or directories to lint")
    parser.add_argument("--version", action="version", version=f"questlint {__version__}")
    parser.add_argument("--format", choices=["text", "json", "sarif"], default="text")
    parser.add_argument("--config", type=Path)
    parser.add_argument("--select", action="append", default=[])
    parser.add_argument("--ignore", action="append", default=[])
    parser.add_argument("--exclude", action="append", default=[])
    parser.add_argument("--quiet", action="store_true", help="Suppress diagnostics and summary")
    parser.add_argument("--verbose", action="store_true", help="Show checked file paths")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        config = load_config(args.config or discover_config(args.paths))
        settings = Settings(
            **{
                **config.__dict__,
                "select": tuple(args.select) or config.select,
                "ignore": config.ignore + tuple(args.ignore),
                "exclude": config.exclude + tuple(args.exclude),
            }
        )
        analyzer = Analyzer(settings=settings)
        analyzer.registry.select(settings.select, settings.ignore)
    except (ConfigError, ValueError) as error:
        print(f"questlint: {error}")
        return 2
    files = discover(args.paths, settings.exclude)
    diagnostics = []
    try:
        for path in files:
            if args.verbose and not args.quiet:
                print(f"checking {path}")
            diagnostics.extend(analyzer.analyze(SourceFile(path, path.read_text(encoding="utf-8"))))
    except (OSError, UnicodeError) as error:
        print(f"questlint: {error}")
        return 2
    if not args.quiet:
        if args.format == "json":
            print(render(len(files), diagnostics))
        elif args.format == "sarif":
            print(render_sarif(diagnostics))
        else:
            for diagnostic in diagnostics:
                print(format_diagnostic(diagnostic))
            print(summary(len(files), diagnostics))
    return 1 if diagnostics else 0
