"""
parse_tree.py - Concrete Parse Tree Node representation for LL(1) parsing.
Used to represent the complete syntactic derivation tree before AST simplification.
"""

from typing import List, Optional, Any

class ParseTreeNode:
    def __init__(self, symbol: str, is_terminal: bool = False, value: Optional[Any] = None, line: int = 0, column: int = 0):
        self.symbol = symbol
        self.is_terminal = is_terminal
        self.value = value
        self.line = line
        self.column = column
        self.children: List['ParseTreeNode'] = []

    def add_child(self, child: 'ParseTreeNode') -> 'ParseTreeNode':
        self.children.append(child)
        return child

    def to_dict(self) -> dict:
        """Returns recursive dictionary representation for visualization."""
        node_label = f"{self.symbol}: {self.value}" if self.is_terminal and self.value is not None else self.symbol
        return {
            "name": node_label,
            "children": [c.to_dict() for c in self.children]
        }

    def format_tree(self, prefix: str = "", is_last: bool = True) -> str:
        """Academic ASCII tree rendering."""
        connector = "└── " if is_last else "├── "
        label = f"{self.symbol} ('{self.value}')" if self.is_terminal and self.value is not None else self.symbol
        lines = [prefix + connector + label]
        
        new_prefix = prefix + ("    " if is_last else "│   ")
        for i, child in enumerate(self.children):
            last = (i == len(self.children) - 1)
            lines.append(child.format_tree(new_prefix, last))
        return "\n".join(lines)

    def __repr__(self) -> str:
        return f"ParseTreeNode({self.symbol}, children={len(self.children)})"
