# Configuration

QuestLint discovers the first `.questlint.toml` found by walking upward from the
first input path (or its parent). `--config PATH` disables discovery. Defaults
are used first, then config, then CLI options; CLI `--ignore` adds to config
ignores and CLI `--select` replaces config selection.

```toml
[questlint]
select = ["QL1", "QL2", "QL3", "QL4", "QL6"]
ignore = ["QL205"]
exclude = ["vendor/**", "generated/**"]
max_nesting = 5
max_function_lines = 80
max_complexity = 15
max_file_lines = 1000

[globals]
allowed = ["game", "player", "server"]

[state_machine]
enabled = true
initial = "idle"
terminal_states = ["completed", "failed"]
```

Rule selectors are IDs (`QL201`) or prefixes (`QL2`). Invalid selectors and
invalid TOML are command errors. Excludes use slash-separated paths relative to
each scanned directory, on every platform.

State analysis is enabled by `state_machine.enabled` or by a state annotation.
The config `initial` takes precedence over `---@initial`; terminal states are
excluded from QL504.
