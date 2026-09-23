import tree_sitter_lua
from tree_sitter import Language, Parser

from questlint.parsing.model import ParsedLua


class LuaParser:
    def __init__(self) -> None:
        self._parser = Parser(Language(tree_sitter_lua.language()))

    def parse(self, text: str) -> ParsedLua:
        source = text.encode("utf-8")
        return ParsedLua(source, self._parser.parse(source))
