# State-machine analysis

QuestLint never executes Lua. State analysis is opt-in through annotations (or
`[state_machine].enabled = true`) and builds a directed graph from comments:

```lua
---@state idle
function idle() end
---@state combat
function combat() end
---@initial idle
---@transition idle -> combat
---@transition combat -> idle
```

`---@state NAME` declares a node; `---@transition FROM -> TO` declares an edge.
`---@initial NAME` selects the starting node unless configuration specifies
`state_machine.initial`. QL503 uses deterministic breadth-first traversal from
that node. `terminal_states` configures states intentionally without exits.
Malformed annotations yield QL001; ordinary Lua files with neither annotations
nor enabled state analysis do not receive QL5xx diagnostics.
