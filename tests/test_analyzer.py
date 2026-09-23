from pathlib import Path

from questlint.core.analyzer import Analyzer
from questlint.core.config import Settings
from questlint.core.source import SourceFile


def lint(text: str):
    return Analyzer().analyze(SourceFile(Path("sample.lua"), text))


def ids(text: str) -> list[str]:
    return [diagnostic.rule_id for diagnostic in lint(text)]


def test_valid_lua_parses_without_diagnostics() -> None:
    assert ids('local name = "Lua"\nprint(name)\n') == []


def test_syntax_error_has_location() -> None:
    diagnostic = lint("function broken(\n  print('x')\nend\n")[0]
    assert diagnostic.rule_id == "QL101"
    assert diagnostic.line >= 1
    assert diagnostic.column >= 1


def test_accidental_global_and_standard_global() -> None:
    found = lint("score = 3\nprint(score)\n")
    assert [d.rule_id for d in found] == ["QL201"]


def test_shadow_and_unused_local() -> None:
    found = lint(
        "local value = 1\nif true then\n local value = 2\n print(value)\nend\nprint(value)\n"
    )
    assert [d.rule_id for d in found] == ["QL203"]


def test_unused_and_used_local() -> None:
    found = lint("local stale = compute()\nlocal used = 3\nprint(used)\n")
    assert [d.rule_id for d in found] == ["QL204"]
    assert found[0].message == 'local "stale" is never read'


def test_unused_parameter_and_conventional_unused_name() -> None:
    found = lint("function update(player, delta, _unused)\n print(player)\nend\n")
    assert [d.rule_id for d in found] == ["QL201", "QL205"]
    assert found[-1].message == 'parameter "delta" is never read'


def test_duplicate_table_keys() -> None:
    found = lint('local options = { timeout = 1, ["timeout"] = 2 }\nprint(options)\n')
    assert [d.rule_id for d in found] == ["QL301"]


def test_nested_function_and_loop_scope() -> None:
    found = lint("for item in pairs({}) do\n local copy = item\n print(copy)\nend\n")
    assert found == []


def test_custom_globals_and_suppression() -> None:
    analyzer = Analyzer(settings=Settings(globals_allowed=frozenset({"game"})))
    found = analyzer.analyze(
        SourceFile(Path("sample.lua"), "game = 1\n-- questlint-disable-next-line QL201\napi = 2\n")
    )
    assert found == []


def test_block_suppression_isolated_and_validated() -> None:
    found = lint(
        "-- questlint-disable QL201\nfirst = 1\n"
        "-- questlint-enable QL201\nsecond = 2\n"
        "-- questlint-disable-next-line QL999\nthird = 3\n"
    )
    assert [diagnostic.rule_id for diagnostic in found] == ["QL201", "QL001", "QL201"]


def test_constant_false_and_file_metric() -> None:
    found = Analyzer(settings=Settings(max_file_lines=1)).analyze(
        SourceFile(Path("sample.lua"), "if false then\nprint('x')\nend\n")
    )
    assert [diagnostic.rule_id for diagnostic in found] == ["QL603", "QL403"]


def test_state_graph_rules_and_cycle() -> None:
    source = """---@state idle
---@state idle
---@state combat
---@state done
---@initial idle
---@transition idle -> combat
---@transition combat -> idle
---@transition combat -> missing
"""
    found = lint(source)
    assert [diagnostic.rule_id for diagnostic in found] == ["QL501", "QL503", "QL504", "QL502"]


def test_state_graph_configured_initial_and_terminal() -> None:
    analyzer = Analyzer(
        settings=Settings(
            state_machine_enabled=True,
            state_machine_initial="idle",
            terminal_states=frozenset({"done"}),
        )
    )
    found = analyzer.analyze(
        SourceFile(
            Path("sample.lua"), "---@state idle\n---@state done\n---@transition idle -> done\n"
        )
    )
    assert found == []


def test_state_graph_missing_initial_and_malformed_annotation() -> None:
    found = lint("---@state idle\n---@transition idle -> idle\n---@state bad name\n")
    assert [diagnostic.rule_id for diagnostic in found] == ["QL505", "QL001"]
