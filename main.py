import sys
import os
import argparse
from typing import Optional, Dict, Any, List

# Ensure parent directory is accessible
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from lexer.tokens import Token
from lexer.lexer import Lexer, LexicalError
from grammar.grammar import get_mini_sql_grammar, Grammar
from grammar.first_follow import FirstFollowCalculator
from grammar.parsing_table import ParsingTable
from parser.ll1_parser import LL1Parser, SyntaxErrorLL1
from parser.parse_tree import ParseTreeNode
from ast_module.nodes import QueryNode
from ast_module.builder import ASTBuilder
from semantic.analyzer import SemanticAnalyzer, SemanticResult
from optimizer.optimizer import QueryOptimizer, OptimizationReport
from execution.planner import ExecutionPlanner, ExecutionPlan
from execution.executor import QueryExecutor, ExecutionResult
from database.database import init_db

class CompilationReport:
    """Holds full end-to-end results from every compiler phase."""
    def __init__(self, raw_sql: str):
        self.raw_sql = raw_sql
        self.success = False
        self.error_stage: Optional[str] = None
        self.error_message: Optional[str] = None
        
        self.tokens: List[Token] = []
        self.parse_tree: Optional[ParseTreeNode] = None
        self.trace: List[dict] = []
        self.ast: Optional[QueryNode] = None
        self.ast_text: str = ""
        self.semantic_result: Optional[SemanticResult] = None
        self.optimized_ast: Optional[QueryNode] = None
        self.optimized_ast_text: str = ""
        self.optimization_report: Optional[OptimizationReport] = None
        self.execution_plan: Optional[ExecutionPlan] = None
        self.execution_result: Optional[ExecutionResult] = None

class MiniSQLCompiler:
    def __init__(self):
        self.grammar: Grammar = get_mini_sql_grammar()
        self.first_follow: FirstFollowCalculator = FirstFollowCalculator(self.grammar)
        self.parsing_table: ParsingTable = ParsingTable(self.grammar, self.first_follow)
        self.parser: LL1Parser = LL1Parser(self.grammar, self.parsing_table)
        self.semantic_analyzer: SemanticAnalyzer = SemanticAnalyzer()
        self.optimizer: QueryOptimizer = QueryOptimizer()
        self.planner: ExecutionPlanner = ExecutionPlanner()
        self.executor: QueryExecutor = QueryExecutor()

    def compile_and_execute(self, sql: str) -> CompilationReport:
        report = CompilationReport(sql)

        try:
            lexer = Lexer(sql)
            report.tokens = lexer.tokenize()
        except LexicalError as e:
            report.error_stage = "LEXICAL_ERROR"
            report.error_message = str(e)
            return report

        try:
            report.parse_tree, report.trace = self.parser.parse(report.tokens)
        except SyntaxErrorLL1 as e:
            report.error_stage = "SYNTAX_ERROR"
            report.error_message = str(e)
            return report

        try:
            builder = ASTBuilder(report.parse_tree)
            report.ast = builder.build()
            report.ast_text = report.ast.format_tree()
        except Exception as e:
            report.error_stage = "AST_CONSTRUCTION_ERROR"
            report.error_message = f"Failed to construct AST: {str(e)}"
            return report

        report.semantic_result = self.semantic_analyzer.analyze(report.ast)
        if not report.semantic_result.is_valid:
            report.error_stage = "SEMANTIC_ERROR"
            report.error_message = "Semantic Validation Failed:\n  - " + "\n  - ".join(report.semantic_result.errors)
            return report

        report.optimized_ast, report.optimization_report = self.optimizer.optimize(
            report.ast, report.semantic_result
        )
        report.optimized_ast_text = report.optimized_ast.format_tree()

        report.execution_plan = self.planner.create_plan(report.optimized_ast)

        report.execution_result = self.executor.execute(report.optimized_ast)
        if not report.execution_result.success:
            report.error_stage = "EXECUTION_ERROR"
            report.error_message = report.execution_result.error
            return report

        report.success = True
        return report

def main():
    parser = argparse.ArgumentParser(description="Mini-SQL LL(1) Compiler & Optimizer")
    parser.add_argument("--query", "-q", type=str, help="SQL query to compile and run")
    parser.add_argument("--demo", action="store_true", help="Run educational LL(1) theory demo")
    args = parser.parse_args()

    if args.demo:
        from educational.theory_ll1 import run_educational_demo
        demo = run_educational_demo("id + id")
        print("=== EDUCATIONAL LL(1) THEORY DEMO ===")
        print(demo["first_follow_formatted"])
        print("\n" + demo["table_formatted"])
        print(f"\nTrace steps: {len(demo['trace'])}")
        return

    # Initialize sample database
    init_db()

    compiler = MiniSQLCompiler()
    sample_query = args.query or "SELECT name, salary FROM employees WHERE salary > 50000 ORDER BY salary DESC;"
    print(f"=== COMPILING MINI-SQL QUERY ===")
    print(f"Input: {sample_query}\n")

    report = compiler.compile_and_execute(sample_query)

    print("Phase 1: Tokens ->", [f"{t.type}({t.value})" if t.value not in (None, t.type) else t.type for t in report.tokens])

    if report.error_stage:
        print(f"\n[{report.error_stage}]")
        print(report.error_message)
        sys.exit(1)

    print(f"\nPhase 2: LL(1) Parser Trace -> Completed successfully in {len(report.trace)} steps.")
    print(f"Phase 3: AST / Query Tree:\n{report.ast_text}\n")
    print(f"Phase 4: Semantic Analysis -> VALID (Table: {report.semantic_result.table_name}, Columns: {report.semantic_result.resolved_columns})")
    print(f"Phase 5: Query Optimizer -> {report.optimization_report.summary_message}")
    print(f"Phase 6: Execution Plan:\n{report.execution_plan.format_pipeline()}\n")
    print(f"Phase 7: Execution Result -> {report.execution_result.row_count} row(s) returned:")
    print("Columns:", report.execution_result.columns)
    for r in report.execution_result.rows:
        print("  ", r)

if __name__ == "__main__":
    main()
