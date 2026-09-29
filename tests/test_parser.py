"""
test_parser.py - Tests for LL(1) Table-Driven Predictive Parser.
Tests stack execution, valid query parsing, and descriptive syntax error messages.
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from lexer.lexer import tokenize
from grammar.grammar import get_mini_sql_grammar
from parser.ll1_parser import LL1Parser, SyntaxErrorLL1

class TestParser(unittest.TestCase):
    def setUp(self):
        self.grammar = get_mini_sql_grammar()
        self.parser = LL1Parser(self.grammar)

    def test_valid_queries(self):
        valid_queries = [
            "SELECT * FROM employees;",
            "SELECT name FROM employees;",
            "SELECT name, salary FROM employees;",
            "SELECT name FROM employees WHERE salary > 50000;",
            "SELECT name, salary FROM employees WHERE salary > 50000 ORDER BY salary DESC;",
            "SELECT id, name FROM employees WHERE age >= 25 AND salary <= 70000 ORDER BY name ASC;"
        ]
        for q in valid_queries:
            tokens = tokenize(q)
            tree, trace = self.parser.parse(tokens)
            self.assertIsNotNone(tree)
            self.assertTrue(len(trace) > 0)
            self.assertEqual(trace[-1]["action"], "ACCEPT (Parsing successful)")

    def test_syntax_error_select_from(self):
        # SELECT FROM employees; -> Missing projection column or star
        tokens = tokenize("SELECT FROM employees;")
        with self.assertRaises(SyntaxErrorLL1) as ctx:
            self.parser.parse(tokens)
        self.assertIn("Expected ID or STAR", str(ctx.exception))

    def test_syntax_error_missing_from(self):
        # SELECT name employees; -> Missing FROM keyword
        tokens = tokenize("SELECT name employees;")
        with self.assertRaises(SyntaxErrorLL1) as ctx:
            self.parser.parse(tokens)
        self.assertIn("Expected FROM", str(ctx.exception))

    def test_syntax_error_empty_table(self):
        # SELECT name FROM; -> Missing table identifier
        tokens = tokenize("SELECT name FROM;")
        with self.assertRaises(SyntaxErrorLL1) as ctx:
            self.parser.parse(tokens)
        self.assertIn("Expected ID", str(ctx.exception))

if __name__ == "__main__":
    unittest.main()
