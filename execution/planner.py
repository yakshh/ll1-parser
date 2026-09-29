"""
planner.py - Physical Execution Plan Generator for Mini-SQL Compiler.
Converts the optimized AST into an ordered sequence of physical database operations:
Table Scan -> Filter -> Sort -> Projection -> Output.
"""

from typing import List, Dict, Any, Optional
from ast_module.nodes import QueryNode

class PlanStep:
    def __init__(self, step_number: int, operator: str, details: str, cost_estimate: str = "Low"):
        self.step_number = step_number
        self.operator = operator
        self.details = details
        self.cost_estimate = cost_estimate

    def to_dict(self) -> dict:
        return {
            "step": self.step_number,
            "operator": self.operator,
            "details": self.details,
            "cost": self.cost_estimate
        }

    def __repr__(self) -> str:
        return f"Step {self.step_number}: [{self.operator}] {self.details}"

class ExecutionPlan:
    def __init__(self, steps: List[PlanStep], target_table: str, final_columns: List[str]):
        self.steps = steps
        self.target_table = target_table
        self.final_columns = final_columns

    def format_pipeline(self) -> str:
        """Academic text representation of the pipeline with downward arrows."""
        lines = []
        for i, step in enumerate(self.steps):
            lines.append(f"[{step.operator}] {step.details}")
            if i < len(self.steps) - 1:
                lines.append("       ↓")
        return "\n".join(lines)

    def to_list(self) -> List[dict]:
        return [s.to_dict() for s in self.steps]

class ExecutionPlanner:
    def __init__(self):
        pass

    def create_plan(self, ast: QueryNode) -> ExecutionPlan:
        steps: List[PlanStep] = []
        step_num = 1
        table_name = ast.from_node.table_name

        # 1. Physical Access Path: Table Scan
        steps.append(PlanStep(
            step_number=step_num,
            operator="Table Scan",
            details=f"Sequential scan on table '{table_name}'",
            cost_estimate="O(N)"
        ))
        step_num += 1

        # 2. Filter (Predicate Pushdown)
        if ast.where_node and ast.where_node.conditions:
            cond_strs = []
            for i, c in enumerate(ast.where_node.conditions):
                val_repr = f"'{c.value}'" if c.value_type == "STRING" else str(c.value)
                cond_strs.append(f"{c.column} {c.operator} {val_repr}")
            filter_expr = " AND ".join(cond_strs)
            steps.append(PlanStep(
                step_number=step_num,
                operator="Filter",
                details=f"Evaluate predicate ({filter_expr})",
                cost_estimate="O(N)"
            ))
            step_num += 1

        # 3. Sort (if ORDER BY exists)
        if ast.order_node:
            steps.append(PlanStep(
                step_number=step_num,
                operator="Sort",
                details=f"Sort tuples by '{ast.order_node.column}' ({ast.order_node.direction})",
                cost_estimate="O(K log K)"
            ))
            step_num += 1

        # 4. Projection (Column Selection)
        if ast.select_node.is_star:
            proj_cols = ["*"]
            proj_str = "All columns (*)"
        else:
            proj_cols = ast.select_node.columns
            proj_str = ", ".join(proj_cols)

        steps.append(PlanStep(
            step_number=step_num,
            operator="Projection",
            details=f"Extract columns: {proj_str}",
            cost_estimate="O(K)"
        ))
        step_num += 1

        # 5. Output / Materialization
        steps.append(PlanStep(
            step_number=step_num,
            operator="Result",
            details="Stream final materialized result set to client",
            cost_estimate="O(1)"
        ))

        return ExecutionPlan(steps=steps, target_table=table_name, final_columns=proj_cols)
