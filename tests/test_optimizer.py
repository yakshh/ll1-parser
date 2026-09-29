"""
test_optimizer.py - Tests for Query Optimizer.
Validates projection pruning, predicate deduplication, and honest no-op detection.
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from lexer.lexer import tokenize
from grammar.grammar import get_mini_sql_grammar
from parser.ll1_parser import LL1Parser
from ast_module.builder import ASTBuilder
from optimizer.optimizer import QueryOptimizer

class TestOptimizer(unittest.TestCase):
    def setUp(self):
        self.grammar = get_mini_sql_grammar()
        self.parser = LL1Parser(self.grammar)
        self.optimizer = QueryOptimizer()

    def _get_ast(self, sql: str):
        tokens = tokenize(sql)
        tree, _ = self.parser.parse(tokens)
        return ASTBuilder(tree).build()

    def test_duplicate_column_pruning(self):
        # SELECT name, salary, name FROM employees;
        ast = self._get_ast("SELECT name, salary, name FROM employees;")
        opt_ast, report = self.optimizer.optimize(ast)
        self.assertTrue(report.is_optimized)
        self.assertEqual(opt_ast.select_node.columns, ["name", "salary"])

    def test_redundant_predicate_elimination(self):
        # WHERE salary > 50000 AND salary > 50000
        ast = self._get_ast("SELECT name FROM employees WHERE salary > 50000 AND salary > 50000;")
        opt_ast, report = self.optimizer.optimize(ast)
        self.assertTrue(report.is_optimized)
        self.assertEqual(len(opt_ast.where_node.conditions), 1)

    def test_no_applicable_optimization(self):
        # Simple clean query without redundancy
        ast = self._get_ast("SELECT name, salary FROM employees WHERE salary > 50000;")
        opt_ast, report = self.optimizer.optimize(ast)
        self.assertFalse(report.is_optimized)
        self.assertEqual(report.summary_message, "No applicable optimization found.")

if __name__ == "__main__":
    unittest.main()
