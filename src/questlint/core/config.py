"""Configuration loading and the deliberately small precedence model."""

import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    select: tuple[str, ...] | None = None
    ignore: tuple[str, ...] = ()
    exclude: tuple[str, ...] = ()
    globals_allowed: frozenset[str] = frozenset()
    max_nesting: int = 5
    max_function_lines: int = 80
    max_complexity: int = 15
    max_file_lines: int = 1000
    state_machine_enabled: bool = False
    state_machine_initial: str | None = None
    terminal_states: frozenset[str] = frozenset()


class ConfigError(ValueError):
    pass


def discover_config(paths: list[str], cwd: Path | None = None) -> Path | None:
    """Use the first input's parent (or cwd), walking upward to the first config."""
    start = Path(paths[0]).resolve() if paths else (cwd or Path.cwd()).resolve()
    start = start if start.is_dir() else start.parent
    for directory in (start, *start.parents):
        candidate = directory / ".questlint.toml"
        if candidate.is_file():
            return candidate
    return None


def _strings(value: object, key: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ConfigError(f"{key} must be an array of strings")
    return tuple(value)


def load_config(path: Path | None) -> Settings:
    if path is None:
        return Settings()
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise ConfigError(f"cannot read config {path}: {error}") from error
    section = data.get("questlint", {})
    globals_section = data.get("globals", {})
    state_section = data.get("state_machine", {})
    if not all(isinstance(item, dict) for item in (section, globals_section, state_section)):
        raise ConfigError("[questlint], [globals], and [state_machine] must be tables")
    max_nesting = 5
    max_function_lines = 80
    max_complexity = 15
    max_file_lines = 1000
    for key in ("max_nesting", "max_function_lines", "max_complexity", "max_file_lines"):
        if key in section:
            value = section[key]
            if not isinstance(value, int) or value < 1:
                raise ConfigError(f"{key} must be a positive integer")
            if key == "max_nesting":
                max_nesting = value
            elif key == "max_function_lines":
                max_function_lines = value
            elif key == "max_complexity":
                max_complexity = value
            else:
                max_file_lines = value
    return Settings(
        select=_strings(section["select"], "select") if "select" in section else None,
        ignore=_strings(section.get("ignore", []), "ignore"),
        exclude=_strings(section.get("exclude", []), "exclude"),
        globals_allowed=frozenset(_strings(globals_section.get("allowed", []), "globals.allowed")),
        max_nesting=max_nesting,
        max_function_lines=max_function_lines,
        max_complexity=max_complexity,
        max_file_lines=max_file_lines,
        state_machine_enabled=_bool(state_section.get("enabled", False), "state_machine.enabled"),
        state_machine_initial=_optional_string(
            state_section.get("initial"), "state_machine.initial"
        ),
        terminal_states=frozenset(
            _strings(state_section.get("terminal_states", []), "state_machine.terminal_states")
        ),
    )


def _bool(value: object, key: str) -> bool:
    if not isinstance(value, bool):
        raise ConfigError(f"{key} must be a boolean")
    return value


def _optional_string(value: object, key: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value:
        raise ConfigError(f"{key} must be a non-empty string")
    return value
