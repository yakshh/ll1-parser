"""
test_first_follow.py - Tests for programmatic FIRST/FOLLOW and LL(1) Parsing Table.
Validates mathematical closure, epsilon handling, and conflict detection.
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from grammar.grammar import get_mini_sql_grammar, EPSILON, EOF_SYMBOL
from grammar.first_follow import FirstFollowCalculator
from grammar.parsing_table import ParsingTable

class TestFirstFollow(unittest.TestCase):
    def setUp(self):
        self.grammar = get_mini_sql_grammar()
        self.calc = FirstFollowCalculator(self.grammar)
        self.table = ParsingTable(self.grammar, self.calc)

    def test_first_sets(self):
        # FIRST(Query) must be {SELECT}
        self.assertEqual(self.calc.first["Query"], {"SELECT"})
        
        # FIRST(SelectList) must be {STAR, ID}
        self.assertEqual(self.calc.first["SelectList"], {"STAR", "ID"})
        
        # FIRST(ColumnListTail) must include COMMA and ε
        self.assertIn("COMMA", self.calc.first["ColumnListTail"])
        self.assertIn(EPSILON, self.calc.first["ColumnListTail"])

    def test_follow_sets(self):
        # FOLLOW(Query) must include $
        self.assertIn(EOF_SYMBOL, self.calc.follow["Query"])
        
        # FOLLOW(SelectList) must include FROM
        self.assertIn("FROM", self.calc.follow["SelectList"])

    def test_ll1_conflicts(self):
        # Grammar must be strictly LL(1) with 0 conflicts
        self.assertTrue(self.table.is_ll1())
        self.assertEqual(len(self.table.conflicts), 0)

if __name__ == "__main__":
    unittest.main()
