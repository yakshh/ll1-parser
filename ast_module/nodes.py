"""
nodes.py - Abstract Syntax Tree (AST) node definitions for Mini-SQL.
Provides clean semantic representation of queries and tree formatting.
"""

from typing import List, Optional, Any

class ASTNode:
    """Base class for all AST nodes."""
    def format_tree(self, prefix: str = "", is_last: bool = True) -> str:
        raise NotImplementedError

    def to_dict(self) -> dict:
        raise NotImplementedError

class ConditionNode(ASTNode):
    def __init__(self, column: str, operator: str, value: Any, value_type: str):
        self.column = column
        self.operator = operator
        self.value = value
        self.value_type = value_type

    def format_tree(self, prefix: str = "", is_last: bool = True) -> str:
        connector = "└── " if is_last else "├── "
        lines = [prefix + connector + "Condition"]
        child_pfx = prefix + ("    " if is_last else "│   ")
        lines.append(f"{child_pfx}├── {self.column}")
        lines.append(f"{child_pfx}├── {self.operator}")
        val_display = f"'{self.value}'" if self.value_type == "STRING" else str(self.value)
        lines.append(f"{child_pfx}└── {val_display}")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        val_display = f"'{self.value}'" if self.value_type == "STRING" else str(self.value)
        return {
            "name": "Condition",
            "children": [
                {"name": str(self.column), "children": []},
                {"name": str(self.operator), "children": []},
                {"name": val_display, "children": []}
            ]
        }

    def __repr__(self) -> str:
        return f"{self.column} {self.operator} {repr(self.value)}"

class WhereNode(ASTNode):
    def __init__(self, conditions: List[ConditionNode], logical_ops: Optional[List[str]] = None):
        self.conditions = conditions
        self.logical_ops = logical_ops or []

    def format_tree(self, prefix: str = "", is_last: bool = True) -> str:
        connector = "└── " if is_last else "├── "
        lines = [prefix + connector + "Where"]
        child_pfx = prefix + ("    " if is_last else "│   ")
        for i, cond in enumerate(self.conditions):
            last_c = (i == len(self.conditions) - 1)
            lines.append(cond.format_tree(child_pfx, last_c))
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "name": "Where",
            "children": [c.to_dict() for c in self.conditions]
        }

class SelectNode(ASTNode):
    def __init__(self, is_star: bool, columns: List[str]):
        self.is_star = is_star
        self.columns = columns

    def format_tree(self, prefix: str = "", is_last: bool = True) -> str:
        connector = "└── " if is_last else "├── "
        lines = [prefix + connector + "Select"]
        child_pfx = prefix + ("    " if is_last else "│   ")
        if self.is_star:
            lines.append(f"{child_pfx}└── *")
        else:
            for i, col in enumerate(self.columns):
                c_conn = "└── " if i == len(self.columns) - 1 else "├── "
                lines.append(f"{child_pfx}{c_conn}{col}")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        col_items = ["*"] if self.is_star else self.columns
        return {
            "name": "Select",
            "children": [{"name": c, "children": []} for c in col_items]
        }

class FromNode(ASTNode):
    def __init__(self, table_name: str):
        self.table_name = table_name

    def format_tree(self, prefix: str = "", is_last: bool = True) -> str:
        connector = "└── " if is_last else "├── "
        lines = [prefix + connector + "From"]
        child_pfx = prefix + ("    " if is_last else "│   ")
        lines.append(f"{child_pfx}└── {self.table_name}")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "name": "From",
            "children": [{"name": self.table_name, "children": []}]
        }

class OrderByNode(ASTNode):
    def __init__(self, column: str, direction: str = "ASC"):
        self.column = column
        self.direction = direction

    def format_tree(self, prefix: str = "", is_last: bool = True) -> str:
        connector = "└── " if is_last else "├── "
        lines = [prefix + connector + "OrderBy"]
        child_pfx = prefix + ("    " if is_last else "│   ")
        lines.append(f"{child_pfx}├── {self.column}")
        lines.append(f"{child_pfx}└── {self.direction}")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "name": "OrderBy",
            "children": [
                {"name": self.column, "children": []},
                {"name": self.direction, "children": []}
            ]
        }

class QueryNode(ASTNode):
    def __init__(
        self,
        select_node: SelectNode,
        from_node: FromNode,
        where_node: Optional[WhereNode] = None,
        order_node: Optional[OrderByNode] = None
    ):
        self.select_node = select_node
        self.from_node = from_node
        self.where_node = where_node
        self.order_node = order_node

    def format_tree(self, prefix: str = "", is_last: bool = True) -> str:
        lines = ["Query"]
        children = [self.select_node, self.from_node]
        if self.where_node:
            children.append(self.where_node)
        if self.order_node:
            children.append(self.order_node)

        for i, child in enumerate(children):
            last = (i == len(children) - 1)
            lines.append(child.format_tree("", last))
        return "\n".join(lines)

    def to_dict(self) -> dict:
        children = [self.select_node.to_dict(), self.from_node.to_dict()]
        if self.where_node:
            children.append(self.where_node.to_dict())
        if self.order_node:
            children.append(self.order_node.to_dict())
        return {
            "name": "Query",
            "children": children
        }
