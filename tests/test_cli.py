from pathlib import Path

from questlint.cli import discover, main


def test_directory_discovery_is_recursive_and_deterministic(tmp_path: Path) -> None:
    (tmp_path / "b.lua").write_text("print('b')")
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "a.lua").write_text("print('a')")
    ignored = tmp_path / "build"
    ignored.mkdir()
    (ignored / "skip.lua").write_text("broken =")
    assert [p.relative_to(tmp_path).as_posix() for p in discover([str(tmp_path)])] == [
        "b.lua",
        "nested/a.lua",
    ]


def test_exit_codes_and_quiet(tmp_path: Path, capsys) -> None:
    valid = tmp_path / "valid.lua"
    valid.write_text("local x = 1\nprint(x)\n")
    invalid = tmp_path / "invalid.lua"
    invalid.write_text("value = 1\n")
    assert main([str(valid), "--quiet"]) == 0
    assert main([str(invalid), "--quiet"]) == 1
    assert capsys.readouterr().out == ""


def test_missing_path_is_not_an_execution_failure() -> None:
    assert main(["does-not-exist.lua", "--quiet"]) == 0
