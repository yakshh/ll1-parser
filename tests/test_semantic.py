"""
test_semantic.py - Tests for Semantic Analysis on Mini-SQL AST.
Tests validation of table names, column names, and type compatibility.
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from lexer.lexer import tokenize
from grammar.grammar import get_mini_sql_grammar
from parser.ll1_parser import LL1Parser
from ast_module.builder import ASTBuilder
from semantic.analyzer import SemanticAnalyzer

class TestSemantic(unittest.TestCase):
    def setUp(self):
        self.grammar = get_mini_sql_grammar()
        self.parser = LL1Parser(self.grammar)
        # Mock schema for testing
        self.mock_schema = {
            "employees": {
                "id": "INTEGER",
                "name": "TEXT",
                "age": "INTEGER",
                "salary": "REAL",
                "department": "TEXT"
            }
        }
        self.analyzer = SemanticAnalyzer(schema=self.mock_schema)

    def _get_ast(self, sql: str):
        tokens = tokenize(sql)
        tree, _ = self.parser.parse(tokens)
        return ASTBuilder(tree).build()

    def test_valid_semantic(self):
        ast = self._get_ast("SELECT name, salary FROM employees WHERE salary > 50000;")
        res = self.analyzer.analyze(ast)
        self.assertTrue(res.is_valid)
        self.assertEqual(len(res.errors), 0)

    def test_unknown_table(self):
        ast = self._get_ast("SELECT name FROM students;")
        res = self.analyzer.analyze(ast)
        self.assertFalse(res.is_valid)
        self.assertTrue(any("Unknown table 'students'" in err for err in res.errors))

    def test_unknown_column(self):
        ast = self._get_ast("SELECT xyz FROM employees;")
        res = self.analyzer.analyze(ast)
        self.assertFalse(res.is_valid)
        self.assertTrue(any("Unknown column 'xyz'" in err for err in res.errors))

    def test_type_mismatch(self):
        # salary is REAL, but comparing with STRING 'high'
        ast = self._get_ast("SELECT name FROM employees WHERE salary > 'high';")
        res = self.analyzer.analyze(ast)
        self.assertFalse(res.is_valid)
        self.assertTrue(any("Type mismatch" in err for err in res.errors))

if __name__ == "__main__":
    unittest.main()
