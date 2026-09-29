"""
tokens.py - Token definitions and representation for Mini-SQL.
Contains TokenType constants and Token dataclass with line/column information.
"""

from dataclasses import dataclass
from typing import Any

# Keywords
KEYWORD_SELECT = "SELECT"
KEYWORD_FROM = "FROM"
KEYWORD_WHERE = "WHERE"
KEYWORD_ORDER = "ORDER"
KEYWORD_BY = "BY"
KEYWORD_ASC = "ASC"
KEYWORD_DESC = "DESC"
KEYWORD_AND = "AND"
KEYWORD_OR = "OR"

KEYWORDS = {
    "SELECT": KEYWORD_SELECT,
    "FROM": KEYWORD_FROM,
    "WHERE": KEYWORD_WHERE,
    "ORDER": KEYWORD_ORDER,
    "BY": KEYWORD_BY,
    "ASC": KEYWORD_ASC,
    "DESC": KEYWORD_DESC,
    "AND": KEYWORD_AND,
    "OR": KEYWORD_OR,
}

# Symbols
TOKEN_STAR = "STAR"
TOKEN_COMMA = "COMMA"
TOKEN_SEMICOLON = "SEMICOLON"

# Comparison Operators
TOKEN_EQ = "EQ"       # =
TOKEN_NEQ = "NEQ"     # != or <>
TOKEN_GT = "GT"       # >
TOKEN_LT = "LT"       # <
TOKEN_GTE = "GTE"     # >=
TOKEN_LTE = "LTE"     # <=

# Values and Identifiers
TOKEN_ID = "ID"
TOKEN_NUMBER = "NUMBER"
TOKEN_STRING = "STRING"

# End of input
TOKEN_EOF = "$"

@dataclass
class Token:
    type: str
    value: Any
    line: int
    column: int

    def __repr__(self) -> str:
        if self.type in (TOKEN_ID, TOKEN_NUMBER, TOKEN_STRING):
            return f"{self.type}({self.value})"
        return f"{self.type}"

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "value": str(self.value),
            "line": self.line,
            "column": self.column
        }
