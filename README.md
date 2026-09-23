# QuestLint

QuestLint is a command-line static analyzer for Lua source files.

## Install from source

Requires Python 3.11 or newer.

```sh
python -m pip install -e .
questlint scripts
```

QuestLint uses tree-sitter-lua and accepts the Lua syntax recognized by that grammar; the initial compatibility baseline is Lua 5.1 syntax.

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

Configuration is documented in [CONFIGURATION.md](docs/CONFIGURATION.md). Current rules include QL101, QL201–QL205, QL301, QL401–QL404, and QL601–QL603. See [the rule reference](docs/RULES.md).

Use `-- questlint-disable-next-line QL201` or paired `questlint-disable` /
`questlint-enable` comments to suppress specified non-syntax rules. JSON output
contains `version`, `files_checked`, and a deterministic diagnostics list.
Analysis is per-file; state-machine analysis and SARIF are not implemented.
