"""
builder.py - Converts a concrete ParseTreeNode into a clean semantic AST (QueryNode).
Extracts domain-specific information from grammar derivations.
"""

from typing import List, Optional
from parser.parse_tree import ParseTreeNode
from ast_module.nodes import (
    QueryNode, SelectNode, FromNode, WhereNode, ConditionNode, OrderByNode
)

class ASTBuilder:
    def __init__(self, parse_tree: ParseTreeNode):
        self.root = parse_tree

    def build(self) -> QueryNode:
        if self.root.symbol != "Query":
            raise ValueError(f"Expected root symbol 'Query', got '{self.root.symbol}'")

        select_node: Optional[SelectNode] = None
        from_node: Optional[FromNode] = None
        where_node: Optional[WhereNode] = None
        order_node: Optional[OrderByNode] = None

        for child in self.root.children:
            if child.symbol == "SelectList":
                select_node = self._build_select(child)
            elif child.symbol == "TableClause":
                from_node = self._build_from(child)
            elif child.symbol == "WhereClause":
                where_node = self._build_where(child)
            elif child.symbol == "OrderClause":
                order_node = self._build_order(child)

        if not select_node:
            raise ValueError("Query missing SelectList")
        if not from_node:
            raise ValueError("Query missing TableClause")

        return QueryNode(
            select_node=select_node,
            from_node=from_node,
            where_node=where_node,
            order_node=order_node
        )

    def _build_select(self, node: ParseTreeNode) -> SelectNode:
        # SelectList -> STAR | ColumnList
        first_child = node.children[0]
        if first_child.symbol == "STAR":
            return SelectNode(is_star=True, columns=[])

        # ColumnList -> ID ColumnListTail
        columns: List[str] = []
        self._collect_columns(first_child, columns)
        return SelectNode(is_star=False, columns=columns)

    def _collect_columns(self, col_list_node: ParseTreeNode, columns: List[str]) -> None:
        for child in col_list_node.children:
            if child.symbol == "ID":
                columns.append(str(child.value))
            elif child.symbol == "ColumnListTail":
                # ColumnListTail -> COMMA ID ColumnListTail | ε
                self._collect_columns(child, columns)

    def _build_from(self, node: ParseTreeNode) -> FromNode:
        # TableClause -> ID
        for child in node.children:
            if child.symbol == "ID":
                return FromNode(table_name=str(child.value))
        raise ValueError("TableClause missing table name")

    def _build_where(self, node: ParseTreeNode) -> Optional[WhereNode]:
        # WhereClause -> WHERE Condition | ε
        if not node.children:
            return None

        cond_node = None
        for child in node.children:
            if child.symbol == "Condition":
                cond_node = child
                break

        if not cond_node:
            return None

        conditions: List[ConditionNode] = []
        logical_ops: List[str] = []
        self._extract_conditions(cond_node, conditions, logical_ops)
        return WhereNode(conditions=conditions, logical_ops=logical_ops)

    def _extract_conditions(self, cond_node: ParseTreeNode, conditions: List[ConditionNode], logical_ops: List[str]) -> None:
        # Condition -> SimpleCond BoolTail
        for child in cond_node.children:
            if child.symbol == "SimpleCond":
                c = self._build_simple_cond(child)
                if c:
                    conditions.append(c)
            elif child.symbol == "BoolTail":
                self._extract_bool_tail(child, conditions, logical_ops)

    def _extract_bool_tail(self, bool_tail_node: ParseTreeNode, conditions: List[ConditionNode], logical_ops: List[str]) -> None:
        # BoolTail -> AND SimpleCond BoolTail | OR SimpleCond BoolTail | ε
        if not bool_tail_node.children:
            return

        op_name = bool_tail_node.children[0].symbol
        if op_name in ("AND", "OR"):
            logical_ops.append(op_name)

        for child in bool_tail_node.children:
            if child.symbol == "SimpleCond":
                c = self._build_simple_cond(child)
                if c:
                    conditions.append(c)
            elif child.symbol == "BoolTail":
                self._extract_bool_tail(child, conditions, logical_ops)

    def _build_simple_cond(self, node: ParseTreeNode) -> Optional[ConditionNode]:
        # SimpleCond -> ID Operator Value
        col_name = None
        op_str = None
        val_data = None
        val_type = "STRING"

        for child in node.children:
            if child.symbol == "ID":
                col_name = str(child.value)
            elif child.symbol == "Operator":
                # Operator -> EQ | NEQ | GT | LT | GTE | LTE
                if child.children:
                    op_str = str(child.children[0].value)
                else:
                    op_str = str(child.value)
            elif child.symbol == "Value":
                # Value -> NUMBER | STRING
                v_child = child.children[0] if child.children else child
                val_data = v_child.value
                val_type = "INTEGER" if isinstance(val_data, int) else ("DECIMAL" if isinstance(val_data, float) else "STRING")

        if col_name and op_str and val_data is not None:
            return ConditionNode(column=col_name, operator=op_str, value=val_data, value_type=val_type)
        return None

    def _build_order(self, node: ParseTreeNode) -> Optional[OrderByNode]:
        # OrderClause -> ORDER BY ID OrderDirection | ε
        if not node.children:
            return None

        col_name = None
        direction = "ASC"

        for child in node.children:
            if child.symbol == "ID":
                col_name = str(child.value)
            elif child.symbol == "OrderDirection":
                # OrderDirection -> ASC | DESC | ε
                if child.children:
                    direction = child.children[0].symbol

        if col_name:
            return OrderByNode(column=col_name, direction=direction)
        return None
