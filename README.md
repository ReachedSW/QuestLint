# QuestLint

QuestLint is a Python 3.11+ static analyzer for Lua source files. It never executes Lua.

## Install

Requires Python 3.11 or newer.

```sh
python -m pip install .
questlint scripts
```

QuestLint uses tree-sitter-lua and accepts the syntax recognized by that grammar;
the compatibility baseline is Lua 5.1.

## Usage

```text
questlint script.lua
questlint scripts/player.lua scripts/boss.lua
questlint ./scripts --format text
questlint ./scripts --format json --select QL2 --ignore QL205
```

Example output:

```text
scripts/player.lua:12:5 QL204 unused-local: local "result" is never read
3 files checked, 1 warning
```

Configuration is documented in [CONFIGURATION.md](docs/CONFIGURATION.md). Rules include QL001, QL101, QL201–QL205, QL301, QL401–QL404, QL501–QL505, and QL601–QL603. See [the rule reference](docs/RULES.md).

Use `-- questlint-disable-next-line QL201` or paired `questlint-disable` /
`questlint-enable` comments to suppress specified non-syntax rules. JSON output
contains `version`, `files_checked`, and a deterministic diagnostics list.

`--format text`, `--format json`, and `--format sarif` are supported. Generic
state graphs use `---@state`, `---@transition`, and `---@initial` comments; see
[STATE_MACHINE.md](docs/STATE_MACHINE.md). SARIF and GitHub upload guidance are
in [SARIF.md](docs/SARIF.md). Analysis remains per-file; inter-file resolution,
caching, and full Lua semantic execution are intentionally out of scope.

Run `pytest`, `ruff check .`, and `mypy src` before contributing. QuestLint is
MIT licensed; see [CONTRIBUTING.md](CONTRIBUTING.md).
