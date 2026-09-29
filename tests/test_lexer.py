"""
test_lexer.py - Unit tests for custom Mini-SQL Lexer.
Tests valid tokenization, literal recognition, and lexical error reporting.
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from lexer.lexer import Lexer, LexicalError
from lexer.tokens import (
    KEYWORD_SELECT, KEYWORD_FROM, KEYWORD_WHERE,
    TOKEN_ID, TOKEN_NUMBER, TOKEN_STRING, TOKEN_GT, TOKEN_EOF
)

class TestLexer(unittest.TestCase):
    def test_basic_tokens(self):
        sql = "SELECT name, salary FROM employees;"
        tokens = Lexer(sql).tokenize()
        types = [t.type for t in tokens]
        self.assertEqual(types, ["SELECT", "ID", "COMMA", "ID", "FROM", "ID", "SEMICOLON", "$"])

    def test_literals_and_operators(self):
        sql = "WHERE salary >= 50000 AND department = 'IT'"
        tokens = Lexer(sql).tokenize()
        self.assertEqual(tokens[0].type, "WHERE")
        self.assertEqual(tokens[1].type, "ID")
        self.assertEqual(tokens[1].value, "salary")
        self.assertEqual(tokens[2].type, "GTE")
        self.assertEqual(tokens[3].type, "NUMBER")
        self.assertEqual(tokens[3].value, 50000)
        self.assertEqual(tokens[4].type, "AND")
        self.assertEqual(tokens[5].type, "ID")
        self.assertEqual(tokens[6].type, "EQ")
        self.assertEqual(tokens[7].type, "STRING")
        self.assertEqual(tokens[7].value, "IT")

    def test_invalid_character_error(self):
        sql = "SELECT name @ FROM employees;"
        with self.assertRaises(LexicalError) as ctx:
            Lexer(sql).tokenize()
        self.assertIn("Unexpected character '@'", str(ctx.exception))

    def test_unterminated_string_error(self):
        sql = "SELECT * FROM employees WHERE department = 'IT;"
        with self.assertRaises(LexicalError) as ctx:
            Lexer(sql).tokenize()
        self.assertIn("Unterminated string literal", str(ctx.exception))

if __name__ == "__main__":
    unittest.main()
