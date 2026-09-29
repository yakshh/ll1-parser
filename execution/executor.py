"""
executor.py - Query Execution Engine for Mini-SQL Compiler.
Executes queries against SQLite using code synthesized directly from the compiled AST.
Does NOT pass raw user input to SQLite.
"""

from typing import List, Tuple, Any, Dict, Optional
from ast_module.nodes import QueryNode
from database.database import execute_query, DB_PATH

class ExecutionResult:
    def __init__(self, columns: List[str], rows: List[Tuple[Any, ...]], generated_sql: str, params: Tuple[Any, ...], error: Optional[str] = None):
        self.columns = columns
        self.rows = rows
        self.row_count = len(rows)
        self.generated_sql = generated_sql
        self.params = params
        self.error = error
        self.success = error is None

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "columns": self.columns,
            "rows": [list(r) for r in self.rows],
            "row_count": self.row_count,
            "generated_sql": self.generated_sql,
            "params": [str(p) for p in self.params],
            "error": self.error
        }

class QueryExecutor:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path

    def generate_sql_from_ast(self, ast: QueryNode) -> Tuple[str, Tuple[Any, ...]]:
        """
        Code Generation Phase: Synthesizes a safe parameterized SQL query from the AST.
        """
        # 1. SELECT clause
        if ast.select_node.is_star:
            select_part = "SELECT *"
        else:
            select_part = f"SELECT {', '.join(ast.select_node.columns)}"

        # 2. FROM clause
        from_part = f"FROM {ast.from_node.table_name}"

        # 3. WHERE clause
        where_part = ""
        params: List[Any] = []
        if ast.where_node and ast.where_node.conditions:
            clause_parts = []
            for i, cond in enumerate(ast.where_node.conditions):
                clause_parts.append(f"{cond.column} {cond.operator} ?")
                params.append(cond.value)
            
            # Combine with AND / OR
            combined_where = []
            for i, part in enumerate(clause_parts):
                combined_where.append(part)
                if i < len(clause_parts) - 1:
                    op = ast.where_node.logical_ops[i] if i < len(ast.where_node.logical_ops) else "AND"
                    combined_where.append(op)
            where_part = "WHERE " + " ".join(combined_where)

        # 4. ORDER BY clause
        order_part = ""
        if ast.order_node:
            order_part = f"ORDER BY {ast.order_node.column} {ast.order_node.direction}"

        sql_parts = [select_part, from_part]
        if where_part:
            sql_parts.append(where_part)
        if order_part:
            sql_parts.append(order_part)

        compiled_sql = " ".join(sql_parts) + ";"
        return compiled_sql, tuple(params)

    def execute(self, ast: QueryNode) -> ExecutionResult:
        """
        Translates AST to physical SQL and executes against the SQLite database.
        """
        compiled_sql, params = self.generate_sql_from_ast(ast)
        try:
            columns, rows = execute_query(compiled_sql, params, self.db_path)
            return ExecutionResult(
                columns=columns,
                rows=rows,
                generated_sql=compiled_sql,
                params=params,
                error=None
            )
        except Exception as e:
            return ExecutionResult(
                columns=[],
                rows=[],
                generated_sql=compiled_sql,
                params=params,
                error=f"Execution Error: {str(e)}"
            )
