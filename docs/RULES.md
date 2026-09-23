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
