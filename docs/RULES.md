# Rules

## QL101 syntax-error

Reports malformed Lua without crashing.

```lua
function broken(
```

```lua
function valid()
end
```

## QL201 accidental-global-assignment

Warns for a straightforward assignment that omits `local`; standard Lua globals are allowed.

```lua
player_count = 10
```

```lua
local player_count = 10
```

## QL203 shadowed-local

Warns when an inner lexical scope redeclares an outer local.

```lua
local value = 1
if ready then local value = 2 end
```

```lua
local value = 1
if ready then local next_value = 2 end
```

## QL204 unused-local

Warns for a local that is never read.

```lua
local result = work()
```

```lua
local result = work()
print(result)
```

## QL205 unused-function-parameter

Warns for an unread parameter, except conventional names beginning with `_`.

```lua
function update(player, delta) print(player) end
```

```lua
function update(player, _delta) print(player) end
```

## QL301 duplicate-table-key

Warns when a table literal repeats an identifier or string key.

```lua
local settings = { timeout = 10, timeout = 20 }
```

```lua
local settings = { timeout = 10, retries = 2 }
```

## Control flow

- **QL401 unreachable-code** reports a statement after `return` or `break` in the same block.
- **QL402 empty-branch** reports an empty `if`/`elseif`/`else` block.
- **QL403 constant-condition** reports clearly non-executing literal `false` or `nil` conditions in `if` and `while`.
- **QL404 excessive-nesting** reports control flow deeper than `max_nesting`; if, elseif, while, repeat, for, and do contribute.

## Maintainability

- **QL601 function-too-complex** starts at 1 and adds one per if, elseif, while, repeat, or for.
- **QL602 function-too-long** uses the parser source span and `max_function_lines`.
- **QL603 file-too-long** uses physical source lines and `max_file_lines`.

## QL001 invalid-suppression

Reports malformed suppression comments, unknown rule IDs, and malformed state annotations. Syntax errors (QL101) are never suppressed.

## State graphs

- **QL501 duplicate-state** reports a repeated `---@state` name.
- **QL502 transition-to-missing-state** reports an edge whose target is not declared.
- **QL503 unreachable-state** reports a state not reached by BFS from a valid initial state.
- **QL504 state-without-exit** reports a non-terminal state with no outgoing edge.
- **QL505 initial-state-missing** reports missing or undeclared initial states.
