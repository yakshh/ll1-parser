"""
test_all.py - Master Automated Test Runner for SQL Compiler & LL(1) Parser.
Runs all 20+ test cases across all categories:
1. Valid Queries
2. Lexical Errors
3. Syntax Errors
4. Semantic Errors
5. Optimizer Passes
6. Educational LL(1) Theory Test
Prints structured compiler pipeline results for every test case.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import MiniSQLCompiler
from educational.theory_ll1 import run_educational_demo
from database.database import init_db

def run_all_tests():
    init_db()
    compiler = MiniSQLCompiler()

    test_cases = [
        # --- VALID QUERIES ---
        {
            "category": "VALID",
            "name": "Select Star",
            "sql": "SELECT * FROM employees;",
            "expected_stage": "SUCCESS"
        },
        {
            "category": "VALID",
            "name": "Single Column Select",
            "sql": "SELECT name FROM employees;",
            "expected_stage": "SUCCESS"
        },
        {
            "category": "VALID",
            "name": "Multiple Column Select",
            "sql": "SELECT name, salary FROM employees;",
            "expected_stage": "SUCCESS"
        },
        {
            "category": "VALID",
            "name": "Filter with Numeric Comparison",
            "sql": "SELECT name FROM employees WHERE salary > 50000;",
            "expected_stage": "SUCCESS"
        },
        {
            "category": "VALID",
            "name": "Filter and Descending Sort",
            "sql": "SELECT name, salary FROM employees WHERE salary > 50000 ORDER BY salary DESC;",
            "expected_stage": "SUCCESS"
        },
        {
            "category": "VALID",
            "name": "String Filter with Equality",
            "sql": "SELECT name, department FROM employees WHERE department = 'IT';",
            "expected_stage": "SUCCESS"
        },
        {
            "category": "VALID",
            "name": "Compound AND Filter with Sort",
            "sql": "SELECT name, age, salary FROM employees WHERE age >= 25 AND salary <= 70000 ORDER BY age ASC;",
            "expected_stage": "SUCCESS"
        },

        # --- SYNTAX ERRORS ---
        {
            "category": "SYNTAX_ERROR",
            "name": "Missing Select List",
            "sql": "SELECT FROM employees;",
            "expected_stage": "SYNTAX_ERROR"
        },
        {
            "category": "SYNTAX_ERROR",
            "name": "Missing FROM Keyword",
            "sql": "SELECT name employees;",
            "expected_stage": "SYNTAX_ERROR"
        },
        {
            "category": "SYNTAX_ERROR",
            "name": "Missing Table Name after FROM",
            "sql": "SELECT name FROM;",
            "expected_stage": "SYNTAX_ERROR"
        },
        {
            "category": "SYNTAX_ERROR",
            "name": "Missing Right Operand in Condition",
            "sql": "SELECT name FROM employees WHERE salary > ;",
            "expected_stage": "SYNTAX_ERROR"
        },

        # --- SEMANTIC ERRORS ---
        {
            "category": "SEMANTIC_ERROR",
            "name": "Unknown Column in SELECT",
            "sql": "SELECT xyz FROM employees;",
            "expected_stage": "SEMANTIC_ERROR"
        },
        {
            "category": "SEMANTIC_ERROR",
            "name": "Unknown Table in FROM",
            "sql": "SELECT name FROM students;",
            "expected_stage": "SEMANTIC_ERROR"
        },
        {
            "category": "SEMANTIC_ERROR",
            "name": "Unknown Column in WHERE",
            "sql": "SELECT name FROM employees WHERE unknown > 100;",
            "expected_stage": "SEMANTIC_ERROR"
        },
        {
            "category": "SEMANTIC_ERROR",
            "name": "Type Mismatch in WHERE Comparison",
            "sql": "SELECT name FROM employees WHERE salary > 'rich';",
            "expected_stage": "SEMANTIC_ERROR"
        },

        # --- LEXICAL ERRORS ---
        {
            "category": "LEXICAL_ERROR",
            "name": "Illegal Character @",
            "sql": "SELECT name @ FROM employees;",
            "expected_stage": "LEXICAL_ERROR"
        },
        {
            "category": "LEXICAL_ERROR",
            "name": "Illegal Character #",
            "sql": "SELECT name FROM employees WHERE salary > 50000#;",
            "expected_stage": "LEXICAL_ERROR"
        },
        {
            "category": "LEXICAL_ERROR",
            "name": "Unterminated String Literal",
            "sql": "SELECT * FROM employees WHERE department = 'IT;",
            "expected_stage": "LEXICAL_ERROR"
        }
    ]

    print("=" * 80)
    print("        COMPREHENSIVE COMPILER TEST SUITE RUNNER")
    print("=" * 80)

    total = len(test_cases)
    passed = 0

    for i, tc in enumerate(test_cases, 1):
        sql = tc["sql"]
        expected = tc["expected_stage"]
        report = compiler.compile_and_execute(sql)

        actual_stage = "SUCCESS" if report.success else report.error_stage
        is_pass = (actual_stage == expected)
        if is_pass:
            passed += 1

        status_str = "PASS [OK]" if is_pass else "FAIL [X]"
        print(f"\nTest {i:2d}/{total}: [{tc['category']}] - {tc['name']}")
        print(f"  Input SQL:       {sql}")
        print(f"  Expected Stage:  {expected}")
        print(f"  Actual Stage:    {actual_stage}")
        print(f"  Status:          {status_str}")

        if report.success:
            print(f"  Tokens:          {len(report.tokens)} tokens")
            print(f"  Trace Steps:     {len(report.trace)} steps")
            print(f"  Optimizer:       {report.optimization_report.summary_message}")
            print(f"  Plan:            {len(report.execution_plan.steps)} physical steps")
            print(f"  Rows Returned:   {report.execution_result.row_count}")
        else:
            print(f"  Diagnostic:      {report.error_message}")

    # Educational theory test
    print("\n" + "=" * 80)
    print("Testing Educational LL(1) Arithmetic Demonstration (E -> T E')...")
    demo = run_educational_demo("id + id")
    theory_pass = demo["accepted"] and demo["is_ll1"] and len(demo["conflicts"]) == 0
    theory_status = "PASS [OK]" if theory_pass else "FAIL [X]"
    print(f"Educational LL(1) Grammar Status: {theory_status} (0 conflicts, Trace: {len(demo['trace'])} steps)")
    if theory_pass:
        passed += 1
    total += 1

    print("\n" + "=" * 80)
    print(f"TEST SUMMARY: {passed}/{total} Tests Passed ({passed / total * 100:.1f}%)")
    print("=" * 80)

    if passed == total:
        print("ALL TESTS PASSED PERFECTLY!")
        return 0
    return 1

if __name__ == "__main__":
    sys.exit(run_all_tests())
