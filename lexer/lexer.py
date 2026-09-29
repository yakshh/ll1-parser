"""
lexer.py - Handcrafted Lexical Analyzer (Tokenizer) for Mini-SQL.
Recognizes keywords, operators, identifiers, numbers, and strings with precise
line and column positions. Does NOT use any third-party parsing libraries.
"""

from typing import List
from lexer.tokens import (
    Token, KEYWORDS,
    TOKEN_STAR, TOKEN_COMMA, TOKEN_SEMICOLON,
    TOKEN_EQ, TOKEN_NEQ, TOKEN_GT, TOKEN_LT, TOKEN_GTE, TOKEN_LTE,
    TOKEN_ID, TOKEN_NUMBER, TOKEN_STRING, TOKEN_EOF
)

class LexicalError(Exception):
    """Raised when an invalid character or malformed literal is encountered."""
    def __init__(self, message: str, line: int, column: int):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Lexical Error at line {line}, col {column}: {message}")

class Lexer:
    def __init__(self, source_code: str):
        self.source = source_code
        self.length = len(source_code)
        self.pos = 0
        self.line = 1
        self.col = 1

    def _peek(self, offset: int = 0) -> str:
        idx = self.pos + offset
        if idx < self.length:
            return self.source[idx]
        return ""

    def _advance(self) -> str:
        if self.pos >= self.length:
            return ""
        ch = self.source[self.pos]
        self.pos += 1
        if ch == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def _skip_whitespace_and_comments(self) -> None:
        while self.pos < self.length:
            ch = self._peek()
            if ch.isspace():
                self._advance()
            elif ch == "-" and self._peek(1) == "-":
                # Single-line SQL comment: skip until newline
                while self.pos < self.length and self._peek() != "\n":
                    self._advance()
            else:
                break

    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []

        while self.pos < self.length:
            self._skip_whitespace_and_comments()
            if self.pos >= self.length:
                break

            start_line = self.line
            start_col = self.col
            ch = self._peek()

            # Single-character and double-character symbols/operators
            if ch == "*":
                self._advance()
                tokens.append(Token(TOKEN_STAR, "*", start_line, start_col))
            elif ch == ",":
                self._advance()
                tokens.append(Token(TOKEN_COMMA, ",", start_line, start_col))
            elif ch == ";":
                self._advance()
                tokens.append(Token(TOKEN_SEMICOLON, ";", start_line, start_col))
            elif ch == "=":
                self._advance()
                tokens.append(Token(TOKEN_EQ, "=", start_line, start_col))
            elif ch == "!":
                self._advance()
                if self._peek() == "=":
                    self._advance()
                    tokens.append(Token(TOKEN_NEQ, "!=", start_line, start_col))
                else:
                    raise LexicalError(f"Unexpected character '!' (did you mean '!=')?", start_line, start_col)
            elif ch == "<":
                self._advance()
                if self._peek() == "=":
                    self._advance()
                    tokens.append(Token(TOKEN_LTE, "<=", start_line, start_col))
                elif self._peek() == ">":
                    self._advance()
                    tokens.append(Token(TOKEN_NEQ, "<>", start_line, start_col))
                else:
                    tokens.append(Token(TOKEN_LT, "<", start_line, start_col))
            elif ch == ">":
                self._advance()
                if self._peek() == "=":
                    self._advance()
                    tokens.append(Token(TOKEN_GTE, ">=", start_line, start_col))
                else:
                    tokens.append(Token(TOKEN_GT, ">", start_line, start_col))
            elif ch == "'":
                # String literal
                tokens.append(self._read_string(start_line, start_col))
            elif ch.isdigit():
                # Number literal
                tokens.append(self._read_number(start_line, start_col))
            elif ch.isalpha() or ch == "_":
                # Identifier or Keyword
                tokens.append(self._read_identifier_or_keyword(start_line, start_col))
            else:
                raise LexicalError(f"Unexpected character '{ch}'", start_line, start_col)

        tokens.append(Token(TOKEN_EOF, "$", self.line, self.col))
        return tokens

    def _read_string(self, start_line: int, start_col: int) -> Token:
        self._advance()  # consume opening quote
        val_chars = []
        while self.pos < self.length:
            ch = self._peek()
            if ch == "'":
                if self._peek(1) == "'":
                    # Escaped single quote: ''
                    self._advance()
                    self._advance()
                    val_chars.append("'")
                else:
                    self._advance()  # consume closing quote
                    return Token(TOKEN_STRING, "".join(val_chars), start_line, start_col)
            elif ch == "\n":
                raise LexicalError("Unterminated string literal: newline found inside string", start_line, start_col)
            else:
                val_chars.append(self._advance())
        raise LexicalError("Unterminated string literal: unexpected end of input", start_line, start_col)

    def _read_number(self, start_line: int, start_col: int) -> Token:
        num_str = []
        is_float = False
        while self.pos < self.length:
            ch = self._peek()
            if ch.isdigit():
                num_str.append(self._advance())
            elif ch == "." and not is_float and self._peek(1).isdigit():
                is_float = True
                num_str.append(self._advance())
            else:
                break
        raw = "".join(num_str)
        value = float(raw) if is_float else int(raw)
        return Token(TOKEN_NUMBER, value, start_line, start_col)

    def _read_identifier_or_keyword(self, start_line: int, start_col: int) -> Token:
        chars = []
        while self.pos < self.length:
            ch = self._peek()
            if ch.isalnum() or ch == "_":
                chars.append(self._advance())
            else:
                break
        word = "".join(chars)
        upper_word = word.upper()
        if upper_word in KEYWORDS:
            return Token(KEYWORDS[upper_word], upper_word, start_line, start_col)
        return Token(TOKEN_ID, word, start_line, start_col)

def tokenize(sql: str) -> List[Token]:
    """Utility function to tokenize a SQL string."""
    return Lexer(sql).tokenize()
