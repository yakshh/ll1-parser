"""
grammar.py - Grammar representation and Mini-SQL grammar definition.
Defines Production, Grammar classes and the explicit LL(1) Mini-SQL grammar.
"""

from dataclasses import dataclass
from typing import List, Set, Tuple

EPSILON = "ε"
EOF_SYMBOL = "$"

@dataclass(frozen=True)
class Production:
    id: int
    lhs: str
    rhs: Tuple[str, ...]

    def __repr__(self) -> str:
        rhs_str = " ".join(self.rhs) if self.rhs else EPSILON
        return f"({self.id}) {self.lhs} -> {rhs_str}"

class Grammar:
    def __init__(self, start_symbol: str, non_terminals: Set[str], terminals: Set[str], productions: List[Production]):
        self.start_symbol = start_symbol
        self.non_terminals = non_terminals
        self.terminals = terminals
        self.productions = productions
        self._prods_by_lhs = {}
        for p in self.productions:
            self._prods_by_lhs.setdefault(p.lhs, []).append(p)

    def get_productions_for(self, non_terminal: str) -> List[Production]:
        return self._prods_by_lhs.get(non_terminal, [])

    def is_terminal(self, symbol: str) -> bool:
        return symbol in self.terminals or symbol == EOF_SYMBOL

    def is_non_terminal(self, symbol: str) -> bool:
        return symbol in self.non_terminals

def get_mini_sql_grammar() -> Grammar:
    """
    Constructs and returns the formal Mini-SQL Grammar designed specifically
    for LL(1) predictive parsing.
    """
    non_terminals = {
        "Query",
        "SelectList",
        "ColumnList",
        "ColumnListTail",
        "TableClause",
        "WhereClause",
        "Condition",
        "SimpleCond",
        "BoolTail",
        "Operator",
        "Value",
        "OrderClause",
        "OrderDirection",
        "SemicolonOpt"
    }

    terminals = {
        "SELECT", "FROM", "WHERE", "ORDER", "BY", "ASC", "DESC", "AND", "OR",
        "STAR", "COMMA", "SEMICOLON",
        "EQ", "NEQ", "GT", "LT", "GTE", "LTE",
        "ID", "NUMBER", "STRING"
    }

    raw_productions = [
        # Query
        ("Query", ("SELECT", "SelectList", "FROM", "TableClause", "WhereClause", "OrderClause", "SemicolonOpt")),

        # SelectList
        ("SelectList", ("STAR",)),
        ("SelectList", ("ColumnList",)),

        # ColumnList
        ("ColumnList", ("ID", "ColumnListTail")),

        # ColumnListTail
        ("ColumnListTail", ("COMMA", "ID", "ColumnListTail")),
        ("ColumnListTail", (EPSILON,)),

        # TableClause
        ("TableClause", ("ID",)),

        # WhereClause
        ("WhereClause", ("WHERE", "Condition")),
        ("WhereClause", (EPSILON,)),

        # Condition & BoolTail (Supports AND/OR while staying strictly LL(1))
        ("Condition", ("SimpleCond", "BoolTail")),
        ("SimpleCond", ("ID", "Operator", "Value")),
        ("BoolTail", ("AND", "SimpleCond", "BoolTail")),
        ("BoolTail", ("OR", "SimpleCond", "BoolTail")),
        ("BoolTail", (EPSILON,)),

        # Operator
        ("Operator", ("EQ",)),
        ("Operator", ("NEQ",)),
        ("Operator", ("GT",)),
        ("Operator", ("LT",)),
        ("Operator", ("GTE",)),
        ("Operator", ("LTE",)),

        # Value
        ("Value", ("NUMBER",)),
        ("Value", ("STRING",)),

        # OrderClause
        ("OrderClause", ("ORDER", "BY", "ID", "OrderDirection")),
        ("OrderClause", (EPSILON,)),

        # OrderDirection
        ("OrderDirection", ("ASC",)),
        ("OrderDirection", ("DESC",)),
        ("OrderDirection", (EPSILON,)),

        # SemicolonOpt
        ("SemicolonOpt", ("SEMICOLON",)),
        ("SemicolonOpt", (EPSILON,))
    ]

    prods = []
    for idx, (lhs, rhs) in enumerate(raw_productions, start=1):
        actual_rhs = () if rhs == (EPSILON,) else rhs
        prods.append(Production(id=idx, lhs=lhs, rhs=actual_rhs))

    return Grammar(
        start_symbol="Query",
        non_terminals=non_terminals,
        terminals=terminals,
        productions=prods
    )
