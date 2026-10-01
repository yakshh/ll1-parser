"""
ll1_parser.py - Handcrafted Table-Driven Predictive LL(1) Parser.
Uses STACK + LOOKAHEAD + PARSING TABLE to parse SQL tokens, construct a Parse Tree,
and generate a step-by-step trace of every parser action.
"""

from typing import List, Tuple, Optional, Any
from lexer.tokens import Token, TOKEN_EOF
from grammar.grammar import Grammar, Production, EPSILON, EOF_SYMBOL
from grammar.parsing_table import ParsingTable
from parser.parse_tree import ParseTreeNode

class SyntaxErrorLL1(Exception):
    """Raised when the LL(1) parser encounters a terminal mismatch or empty table cell."""
    def __init__(self, message: str, line: int, column: int, expected: List[str], found: str):
        self.message = message
        self.line = line
        self.column = column
        self.expected = expected
        self.found = found
        super().__init__(f"Syntax Error at line {line}, col {column}: {message}")

class LL1Parser:
    def __init__(self, grammar: Grammar, parsing_table: Optional[ParsingTable] = None):
        self.grammar = grammar
        self.table = parsing_table or ParsingTable(grammar)

    def parse(self, tokens: List[Token]) -> Tuple[ParseTreeNode, List[dict]]:
        """
        Executes the table-driven LL(1) parsing algorithm on the token stream.
        Returns:
            parse_tree_root: The concrete ParseTreeNode representing the derivation.
            trace: A list of dicts recording each step of the parsing process.
        """
        if not tokens or tokens[-1].type != TOKEN_EOF:
            last_line = tokens[-1].line if tokens else 1
            last_col = tokens[-1].column if tokens else 1
            tokens = list(tokens) + [Token(TOKEN_EOF, "$", last_line, last_col)]

        root_node = ParseTreeNode(symbol=self.grammar.start_symbol)

        # Stack contains pairs of (symbol, corresponding_parse_tree_node)
        stack: List[Tuple[str, Optional[ParseTreeNode]]] = [
            (EOF_SYMBOL, None),
            (self.grammar.start_symbol, root_node)
        ]

        ip = 0  # Input pointer
        step = 1
        trace: List[dict] = []

        while len(stack) > 0:
            top_symbol, curr_node = stack[-1]
            lookahead_token = tokens[ip] if ip < len(tokens) else tokens[-1]

            # Format current stack and remaining input for trace
            stack_repr = " ".join([sym for sym, _ in stack])
            remaining_input_repr = " ".join([repr(t) for t in tokens[ip:ip + 5]])
            if ip + 5 < len(tokens):
                remaining_input_repr += " ..."

            # Case 1: Both top of stack and input are EOF -> ACCEPT
            if top_symbol == EOF_SYMBOL and lookahead_token.type == TOKEN_EOF:
                trace.append({
                    "step": step,
                    "stack": stack_repr,
                    "remaining_input": remaining_input_repr,
                    "action": "ACCEPT (Parsing successful)"
                })
                stack.pop()
                break

            # Case 2: Top of stack is a Terminal
            if self.grammar.is_terminal(top_symbol):
                if top_symbol == lookahead_token.type:
                    action_msg = f"Match {top_symbol}"
                    trace.append({
                        "step": step,
                        "stack": stack_repr,
                        "remaining_input": remaining_input_repr,
                        "action": action_msg
                    })
                    # Pop terminal from stack and update its tree node
                    stack.pop()
                    if curr_node:
                        curr_node.is_terminal = True
                        curr_node.value = lookahead_token.value
                        curr_node.line = lookahead_token.line
                        curr_node.column = lookahead_token.column

                    ip += 1
                    step += 1
                else:
                    expected_list = [top_symbol]
                    found_str = f"{lookahead_token.type}({lookahead_token.value})" if lookahead_token.value else lookahead_token.type
                    msg = f"Expected terminal '{top_symbol}', but found '{found_str}'"
                    trace.append({
                        "step": step,
                        "stack": stack_repr,
                        "remaining_input": remaining_input_repr,
                        "action": f"ERROR: {msg}"
                    })
                    raise SyntaxErrorLL1(
                        message=msg,
                        line=lookahead_token.line,
                        column=lookahead_token.column,
                        expected=expected_list,
                        found=found_str
                    )

            # Case 3: Top of stack is a Non-Terminal
            elif self.grammar.is_non_terminal(top_symbol):
                prod = self.table.get_entry(top_symbol, lookahead_token.type)
                if prod is not None:
                    # Valid production found in parsing table
                    rhs_str = " ".join(prod.rhs) if prod.rhs else EPSILON
                    action_msg = f"Output {prod.lhs} -> {rhs_str}"
                    trace.append({
                        "step": step,
                        "stack": stack_repr,
                        "remaining_input": remaining_input_repr,
                        "action": action_msg
                    })

                    stack.pop()  # Pop the non-terminal

                    # Push RHS in reverse order onto stack while building parse tree children
                    # In parse tree, children must be in forward order (left to right)
                    child_nodes = []
                    for sym in prod.rhs:
                        c_node = ParseTreeNode(symbol=sym)
                        child_nodes.append(c_node)
                        if curr_node:
                            curr_node.add_child(c_node)

                    # Push onto stack in reverse order so leftmost symbol is on top
                    for sym, c_node in reversed(list(zip(prod.rhs, child_nodes))):
                        stack.append((sym, c_node))

                    step += 1
                else:
                    # Empty cell in parsing table -> Syntax Error!
                    expected = self.table.get_expected_terminals(top_symbol)
                    found_str = f"{lookahead_token.type}({lookahead_token.value})" if lookahead_token.value else lookahead_token.type
                    # Make the common missing-FROM mistake easier to understand.
                    # The table knows that ColumnListTail can end with FROM;
                    # expose that expectation directly in the diagnostic.
                    expected_desc = " or ".join(expected) if expected else "valid token"
                    if lookahead_token.type == "ID" and "FROM" in expected:
                        expected_desc = "FROM" + (" or COMMA" if "COMMA" in expected else "")
                    msg = f"Expected {expected_desc}, but found '{found_str}' while expanding '{top_symbol}'"
                    trace.append({
                        "step": step,
                        "stack": stack_repr,
                        "remaining_input": remaining_input_repr,
                        "action": f"ERROR: {msg}"
                    })
                    raise SyntaxErrorLL1(
                        message=msg,
                        line=lookahead_token.line,
                        column=lookahead_token.column,
                        expected=expected,
                        found=found_str
                    )
            else:
                raise SyntaxErrorLL1(
                    message=f"Unknown grammar symbol '{top_symbol}' on stack",
                    line=lookahead_token.line,
                    column=lookahead_token.column,
                    expected=[],
                    found=lookahead_token.type
                )

        return root_node, trace
