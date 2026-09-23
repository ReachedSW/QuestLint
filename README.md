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
```

Example output:

```text
scripts/player.lua:12:5 QL204 unused-local: local "result" is never read
3 files checked, 1 warning
```

Current rules: QL101, QL201, QL203, QL204, QL205, and QL301. See [the rule reference](docs/RULES.md).

Current limitations: there is no configuration file, suppression comments, JSON/SARIF output, state-machine rules, or inter-file analysis. Analysis is per-file.
