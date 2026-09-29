"""
analyzer.py - Semantic Analyzer for Mini-SQL.
Validates table existence, column resolution, WHERE/ORDER BY column existence,
and type compatibility against the SQLite database schema.
"""

from typing import Dict, List, Optional, Tuple, Any
from ast_module.nodes import QueryNode
from database.database import get_table_schema

class SemanticError(Exception):
    """Raised when semantic validation fails on a syntactically valid AST."""
    def __init__(self, message: str, error_type: str = "SEMANTIC_ERROR"):
        self.message = message
        self.error_type = error_type
        super().__init__(f"Semantic Error: {message}")

class SemanticResult:
    def __init__(self, is_valid: bool, errors: List[str], resolved_columns: List[str], table_name: str, column_types: Dict[str, str]):
        self.is_valid = is_valid
        self.errors = errors
        self.resolved_columns = resolved_columns
        self.table_name = table_name
        self.column_types = column_types

    def __repr__(self) -> str:
        status = "VALID" if self.is_valid else f"INVALID ({len(self.errors)} errors)"
        return f"SemanticResult({status}, table='{self.table_name}', columns={self.resolved_columns})"

class SemanticAnalyzer:
    def __init__(self, schema: Optional[Dict[str, Dict[str, str]]] = None):
        self.schema = schema if schema is not None else get_table_schema()

    def analyze(self, query: QueryNode) -> SemanticResult:
        errors: List[str] = []
        table_name = query.from_node.table_name
        
        # 1. Validate Table Existence
        if table_name not in self.schema:
            available = ", ".join(sorted(self.schema.keys())) if self.schema else "None"
            errors.append(f"Unknown table '{table_name}'. Available tables: {available}")
            return SemanticResult(
                is_valid=False,
                errors=errors,
                resolved_columns=[],
                table_name=table_name,
                column_types={}
            )

        table_columns = self.schema[table_name]
        resolved_columns: List[str] = []

        # 2. Validate SELECT Columns
        if query.select_node.is_star:
            resolved_columns = list(table_columns.keys())
        else:
            for col in query.select_node.columns:
                if col not in table_columns:
                    avail_cols = ", ".join(table_columns.keys())
                    errors.append(f"Unknown column '{col}' in SELECT clause for table '{table_name}'. Available columns: {avail_cols}")
                else:
                    resolved_columns.append(col)

        # 3. Validate WHERE Clause Columns and Types
        if query.where_node:
            for cond in query.where_node.conditions:
                col = cond.column
                if col not in table_columns:
                    avail_cols = ", ".join(table_columns.keys())
                    errors.append(f"Unknown column '{col}' in WHERE condition for table '{table_name}'. Available columns: {avail_cols}")
                else:
                    col_type = table_columns[col].upper()
                    val = cond.value
                    val_type = cond.value_type

                    # Type compatibility check
                    if col_type in ("INTEGER", "REAL", "NUMERIC", "FLOAT"):
                        if val_type == "STRING":
                            errors.append(
                                f"Type mismatch in condition for column '{col}': column is of type {col_type}, "
                                f"but comparison value is STRING ('{val}')"
                            )
                    elif col_type in ("TEXT", "VARCHAR", "CHAR"):
                        if val_type in ("INTEGER", "DECIMAL"):
                            errors.append(
                                f"Type mismatch in condition for column '{col}': column is of type {col_type}, "
                                f"but comparison value is numeric ({val})"
                            )

        # 4. Validate ORDER BY Clause Column
        if query.order_node:
            ord_col = query.order_node.column
            if ord_col not in table_columns:
                avail_cols = ", ".join(table_columns.keys())
                errors.append(f"Unknown column '{ord_col}' in ORDER BY clause for table '{table_name}'. Available columns: {avail_cols}")

        is_valid = len(errors) == 0
        return SemanticResult(
            is_valid=is_valid,
            errors=errors,
            resolved_columns=resolved_columns,
            table_name=table_name,
            column_types=table_columns
        )
