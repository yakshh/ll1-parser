"""
theory_ll1.py - Independent Educational LL(1) Theory Demonstration.
Implements the canonical arithmetic grammar:
    E  -> T E'
    E' -> + T E' | ε
    T  -> id
Demonstrates:
  1. Grammar definition
  2. Programmatic FIRST sets calculation
  3. Programmatic FOLLOW sets calculation
  4. Programmatic LL(1) Parsing Table construction
  5. Step-by-step stack parsing trace for input: "id + id"
  6. Final ACCEPT result
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from typing import List, Dict, Any
from grammar.grammar import Grammar, Production, EPSILON, EOF_SYMBOL
from grammar.first_follow import FirstFollowCalculator
from grammar.parsing_table import ParsingTable
from parser.ll1_parser import LL1Parser
from lexer.tokens import Token, TOKEN_EOF

def get_arithmetic_grammar() -> Grammar:
    """Returns the canonical educational arithmetic LL(1) grammar."""
    non_terminals = {"E", "E'", "T"}
    terminals = {"+", "id"}

    raw_productions = [
        ("E", ("T", "E'")),
        ("E'", ("+", "T", "E'")),
        ("E'", (EPSILON,)),
        ("T", ("id",)),
    ]

    prods = []
    for idx, (lhs, rhs) in enumerate(raw_productions, start=1):
        actual_rhs = () if rhs == (EPSILON,) else rhs
        prods.append(Production(id=idx, lhs=lhs, rhs=actual_rhs))

    return Grammar(
        start_symbol="E",
        non_terminals=non_terminals,
        terminals=terminals,
        productions=prods
    )

def tokenize_theory_input(input_str: str) -> List[Token]:
    """Tokenizes educational arithmetic string like 'id + id'."""
    raw_tokens = input_str.strip().split()
    tokens = []
    line = 1
    col = 1
    for t in raw_tokens:
        if t in ("+", "id"):
            tokens.append(Token(type=t, value=t, line=line, column=col))
            col += len(t) + 1
        else:
            raise ValueError(f"Unknown educational token: '{t}'")
    tokens.append(Token(type=TOKEN_EOF, value="$", line=line, column=col))
    return tokens

def run_educational_demo(input_expr: str = "id + id") -> Dict[str, Any]:
    """Runs complete end-to-end LL(1) demonstration on the arithmetic grammar."""
    grammar = get_arithmetic_grammar()
    calc = FirstFollowCalculator(grammar)
    table = ParsingTable(grammar, calc)
    tokens = tokenize_theory_input(input_expr)

    parser = LL1Parser(grammar, table)
    parse_tree, trace = parser.parse(tokens)

    return {
        "grammar": grammar,
        "first_sets": calc.first,
        "follow_sets": calc.follow,
        "first_follow_formatted": calc.format_sets(),
        "is_ll1": table.is_ll1(),
        "conflicts": table.conflicts,
        "table_formatted": table.format_table(),
        "tokens": tokens,
        "trace": trace,
        "accepted": True
    }

if __name__ == "__main__":
    demo = run_educational_demo("id + id")
    print("=== EDUCATIONAL LL(1) DEMONSTRATION ===")
    print(demo["first_follow_formatted"])
    print("\n" + demo["table_formatted"])
    print("\n=== STEP-BY-STEP PARSING TRACE (id + id) ===")
    print(f"{'Step':<5} | {'Stack':<20} | {'Remaining Input':<20} | {'Action'}")
    print("-" * 75)
    for row in demo["trace"]:
        print(f"{row['step']:<5} | {row['stack']:<20} | {row['remaining_input']:<20} | {row['action']}")
