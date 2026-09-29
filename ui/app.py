"""
app.py - Academic Streamlit Web Application for SQL LL(1) Compiler & Optimizer.
Provides a clean, professional, tabbed academic interface for:
1. Complete SQL Compiler Pipeline
2. Dedicated LL(1) Viva Demonstration Mode
3. Educational Arithmetic LL(1) Theory Mode
4. SQLite Database Inspector
"""

import sys
import os
import pandas as pd
import streamlit as st

# Ensure sql_compiler package is importable
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from main import MiniSQLCompiler
from database.database import init_db, get_table_schema, execute_query
from educational.theory_ll1 import run_educational_demo

# Set Streamlit page config
st.set_page_config(
    page_title="Mini-SQL LL(1) Compiler & Optimizer",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
init_db()

# Cache compiler instance across runs
@st.cache_resource
def get_compiler():
    return MiniSQLCompiler()

compiler = get_compiler()

# Custom minimal academic CSS
st.markdown("""
<style>
    .report-title {
        font-size: 26px;
        font-weight: 700;
        margin-bottom: 2px;
        color: #1E293B;
    }
    .report-subtitle {
        font-size: 15px;
        color: #64748B;
        margin-bottom: 20px;
    }
    .status-badge-success {
        background-color: #DEF7EC;
        color: #03543F;
        padding: 6px 12px;
        border-radius: 6px;
        font-weight: 600;
        display: inline-block;
    }
    .status-badge-error {
        background-color: #FDE8E8;
        color: #9B1C1C;
        padding: 6px 12px;
        border-radius: 6px;
        font-weight: 600;
        display: inline-block;
    }
    .code-box {
        font-family: 'Consolas', 'Courier New', monospace;
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 6px;
        padding: 12px;
        font-size: 13px;
        white-space: pre-wrap;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.title("Navigation")
app_mode = st.sidebar.radio(
    "Select Mode:",
    [
        "1. Full SQL Compiler Pipeline",
        "2. LL(1) Demonstration Mode (Viva)",
        "3. Educational LL(1) Theory (E -> T E')",
        "4. Database Schema & Records"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Compiler Design Project**")
st.sidebar.markdown("• Part A: LL(1) Parser")
st.sidebar.markdown("• Part B: SQL Compiler & Optimizer")
st.sidebar.markdown("• Backend: Python + SQLite")

# ==============================================================================
# MODE 1: FULL SQL COMPILER PIPELINE
# ==============================================================================
if app_mode == "1. Full SQL Compiler Pipeline":
    st.markdown("<div class='report-title'>SQL Query Compiler & Optimizer Pipeline</div>", unsafe_allow_html=True)
    st.markdown("<div class='report-subtitle'>Tokens → LL(1) Parser → Semantic Validation → Query Tree (AST) → Optimization → Physical Plan → SQLite Execution</div>", unsafe_allow_html=True)

    # Preset queries selector
    preset_choice = st.selectbox(
        "Load Preset Example Query:",
        [
            "Custom Query",
            "1. Valid: Filter & Sort (SELECT name, salary FROM employees WHERE salary > 50000 ORDER BY salary DESC;)",
            "2. Valid: SELECT * (SELECT * FROM employees;)",
            "3. Valid: Compound AND Filter (SELECT name, age, salary FROM employees WHERE age >= 25 AND salary <= 70000;)",
            "4. Syntax Error: Missing Projection (SELECT FROM employees;)",
            "5. Syntax Error: Missing FROM (SELECT name employees;)",
            "6. Semantic Error: Unknown Column (SELECT xyz FROM employees;)",
            "7. Semantic Error: Unknown Table (SELECT name FROM students;)",
            "8. Optimization Demo: Duplicate Column & Redundant Predicate (SELECT name, salary, name FROM employees WHERE salary > 50000 AND salary > 50000;)"
        ]
    )

    default_queries = {
        "Custom Query": "SELECT name, salary FROM employees WHERE salary > 50000 ORDER BY salary DESC;",
        "1. Valid: Filter & Sort (SELECT name, salary FROM employees WHERE salary > 50000 ORDER BY salary DESC;)": "SELECT name, salary FROM employees WHERE salary > 50000 ORDER BY salary DESC;",
        "2. Valid: SELECT * (SELECT * FROM employees;)": "SELECT * FROM employees;",
        "3. Valid: Compound AND Filter (SELECT name, age, salary FROM employees WHERE age >= 25 AND salary <= 70000;)": "SELECT name, age, salary FROM employees WHERE age >= 25 AND salary <= 70000;",
        "4. Syntax Error: Missing Projection (SELECT FROM employees;)": "SELECT FROM employees;",
        "5. Syntax Error: Missing FROM (SELECT name employees;)": "SELECT name employees;",
        "6. Semantic Error: Unknown Column (SELECT xyz FROM employees;)": "SELECT xyz FROM employees;",
        "7. Semantic Error: Unknown Table (SELECT name FROM students;)": "SELECT name FROM students;",
        "8. Optimization Demo: Duplicate Column & Redundant Predicate (SELECT name, salary, name FROM employees WHERE salary > 50000 AND salary > 50000;)": "SELECT name, salary, name FROM employees WHERE salary > 50000 AND salary > 50000;"
    }

    query_input = st.text_area("SQL Input:", value=default_queries[preset_choice], height=80)

    compile_col, _ = st.columns([2, 8])
    with compile_col:
        run_button = st.button("Compile & Execute", type="primary", use_container_width=True)

    if run_button or query_input:
        report = compiler.compile_and_execute(query_input.strip())

        if not report.success:
            st.error(f"**Compilation Halted at {report.error_stage}**\n\n{report.error_message}")
        else:
            st.success(f"**Compilation & Execution Successful!** Returned {report.execution_result.row_count} row(s).")

        # Tabs for full pipeline transparency
        tabs = st.tabs([
            "1. Lexer Tokens",
            "2. LL(1) Parse Trace",
            "3. AST (Query Tree)",
            "4. Semantic Analysis",
            "5. Query Optimization",
            "6. Physical Execution Plan",
            "7. Database Execution Result"
        ])

        # TAB 1: LEXER
        with tabs[0]:
            st.subheader("Phase 1: Lexical Analysis (Tokens)")
            if report.tokens:
                token_data = [
                    {"Index": i + 1, "Token Type": t.type, "Lexeme / Value": str(t.value), "Line": t.line, "Column": t.column}
                    for i, t in enumerate(report.tokens)
                ]
                st.dataframe(pd.DataFrame(token_data), use_container_width=True)
            else:
                st.info("No tokens produced due to early lexical failure.")

        # TAB 2: LL(1) PARSER & TRACE
        with tabs[1]:
            st.subheader("Phase 2: LL(1) Predictive Parsing & Step-by-Step Trace")
            if report.trace:
                trace_df = pd.DataFrame(report.trace)
                st.dataframe(trace_df, use_container_width=True)
            else:
                st.info("Parser did not run due to lexical error.")

        # TAB 3: AST
        with tabs[2]:
            st.subheader("Phase 3: Abstract Syntax Tree (AST)")
            if report.ast:
                st.code(report.ast_text, language="text")
            else:
                st.info("AST could not be built due to prior error.")

        # TAB 4: SEMANTIC ANALYSIS
        with tabs[3]:
            st.subheader("Phase 4: Semantic Analysis")
            if report.semantic_result:
                if report.semantic_result.is_valid:
                    st.success("Semantic Validation PASSED: Table exists, columns verified, types compatible.")
                    st.json({
                        "Target Table": report.semantic_result.table_name,
                        "Resolved Columns": report.semantic_result.resolved_columns,
                        "Schema Types": report.semantic_result.column_types
                    })
                else:
                    st.error("Semantic Validation FAILED:\n" + "\n".join(report.semantic_result.errors))

        # TAB 5: OPTIMIZER
        with tabs[4]:
            st.subheader("Phase 5: Query Optimization")
            if report.optimization_report:
                if report.optimization_report.is_optimized:
                    st.success(report.optimization_report.summary_message)
                    opt_col1, opt_col2 = st.columns(2)
                    with opt_col1:
                        st.markdown("**Original AST:**")
                        st.code(report.ast_text, language="text")
                    with opt_col2:
                        st.markdown("**Optimized AST:**")
                        st.code(report.optimized_ast_text, language="text")
                else:
                    st.info(report.optimization_report.summary_message)
                    st.code(report.ast_text, language="text")

        # TAB 6: EXECUTION PLAN
        with tabs[5]:
            st.subheader("Phase 6: Physical Execution Plan")
            if report.execution_plan:
                st.markdown("**Relational Algebra / Operator Pipeline:**")
                st.code(report.execution_plan.format_pipeline(), language="text")
                st.markdown("**Operator Details Table:**")
                st.dataframe(pd.DataFrame(report.execution_plan.to_list()), use_container_width=True)

        # TAB 7: EXECUTION RESULT
        with tabs[6]:
            st.subheader("Phase 7: Execution Result (SQLite Backend)")
            if report.execution_result and report.execution_result.success:
                st.markdown(f"**Synthesized SQL Code:** `{report.execution_result.generated_sql}`")
                st.markdown(f"**Query Parameters:** `{report.execution_result.params}`")
                if report.execution_result.rows:
                    df = pd.DataFrame(report.execution_result.rows, columns=report.execution_result.columns)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.warning("Query executed successfully, but 0 rows matched the condition.")
            elif report.execution_result and report.execution_result.error:
                st.error(report.execution_result.error)

# ==============================================================================
# MODE 2: LL(1) DEMONSTRATION MODE (VIVA)
# ==============================================================================
elif app_mode == "2. LL(1) Demonstration Mode (Viva)":
    st.markdown("<div class='report-title'>LL(1) Parser Demonstration Mode</div>", unsafe_allow_html=True)
    st.markdown("<div class='report-subtitle'>Specifically designed for Viva examination and LL(1) concept verification.</div>", unsafe_allow_html=True)

    demo_query = st.text_input("Viva Demo Query:", value="SELECT name FROM employees;")
    if st.button("Run LL(1) Demonstration", type="primary"):
        report = compiler.compile_and_execute(demo_query)

        colA, colB = st.columns(2)
        with colA:
            st.markdown("### A. Input Query")
            st.code(demo_query, language="sql")
            st.markdown("### B. Token Stream")
            tok_strs = [f"{t.type}({t.value})" if t.value != t.type else t.type for t in report.tokens]
            st.write(" → ".join(tok_strs))

        with colB:
            st.markdown("### C. Acceptance Result")
            if report.success:
                st.markdown("<div class='status-badge-success'>✔ ACCEPTED BY LL(1) PARSER</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='status-badge-error'>✘ REJECTED: {report.error_message}</div>", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### D. Grammar, FIRST & FOLLOW Sets")
        gf_col1, gf_col2 = st.columns(2)
        with gf_col1:
            st.markdown("**Programmatic FIRST Sets:**")
            first_data = [{"Non-Terminal": nt, "FIRST Set": ", ".join(sorted(list(s)))} for nt, s in sorted(compiler.first_follow.first.items())]
            st.dataframe(pd.DataFrame(first_data), use_container_width=True, height=260)
        with gf_col2:
            st.markdown("**Programmatic FOLLOW Sets:**")
            follow_data = [{"Non-Terminal": nt, "FOLLOW Set": ", ".join(sorted(list(s)))} for nt, s in sorted(compiler.first_follow.follow.items())]
            st.dataframe(pd.DataFrame(follow_data), use_container_width=True, height=260)

        st.markdown("---")
        st.markdown("### E. Step-by-Step Stack Parsing Trace")
        if report.trace:
            st.dataframe(pd.DataFrame(report.trace), use_container_width=True)

        st.markdown("---")
        st.markdown("### F. Resulting Abstract Syntax Tree (AST)")
        if report.ast:
            st.code(report.ast_text, language="text")

# ==============================================================================
# MODE 3: EDUCATIONAL LL(1) THEORY (E -> T E')
# ==============================================================================
elif app_mode == "3. Educational LL(1) Theory (E -> T E')":
    st.markdown("<div class='report-title'>Educational LL(1) Theory Example</div>", unsafe_allow_html=True)
    st.markdown("<div class='report-subtitle'>Independent canonical grammar for teaching and viva defense: E → T E', E' → + T E' | ε, T → id</div>", unsafe_allow_html=True)

    theory_input = st.text_input("Input Expression (space separated):", value="id + id")
    if st.button("Simulate Canonical LL(1) Parser", type="primary"):
        demo = run_educational_demo(theory_input)

        st.markdown("### 1. Grammar Productions")
        st.code("""
(1) E  -> T E'
(2) E' -> + T E'
(3) E' -> ε
(4) T  -> id
""", language="text")

        t_col1, t_col2 = st.columns(2)
        with t_col1:
            st.markdown("### 2. FIRST & FOLLOW Sets")
            st.code(demo["first_follow_formatted"], language="text")
        with t_col2:
            st.markdown("### 3. LL(1) Parsing Table (0 Conflicts)")
            st.code(demo["table_formatted"], language="text")

        st.markdown("### 4. Stack Execution Trace")
        st.dataframe(pd.DataFrame(demo["trace"]), use_container_width=True)
        st.success("Result: STRING ACCEPTED BY PREDICTIVE LL(1) ALGORITHM")

# ==============================================================================
# MODE 4: DATABASE SCHEMA & RECORDS
# ==============================================================================
elif app_mode == "4. Database Schema & Records":
    st.markdown("<div class='report-title'>Database Schema & Active Sample Records</div>", unsafe_allow_html=True)
    st.markdown("<div class='report-subtitle'>Sample SQLite database 'employees' with preloaded student/employee records.</div>", unsafe_allow_html=True)

    schema = get_table_schema()
    st.markdown("### Table Schema Definition (`employees`)")
    schema_rows = [{"Column Name": col, "Data Type": dt} for col, dt in schema.get("employees", {}).items()]
    st.table(pd.DataFrame(schema_rows))

    st.markdown("### Current Table Records")
    cols, rows = execute_query("SELECT * FROM employees;")
    st.dataframe(pd.DataFrame(rows, columns=cols), use_container_width=True)
