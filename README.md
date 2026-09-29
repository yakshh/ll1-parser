# Mini-SQL LL(1) Compiler & Optimizer

A real, working academic implementation of a **Table-Driven Predictive LL(1) Parser** and a complete **SQL Query Compiler & Optimizer** pipeline built from scratch in Python with SQLite.

## Compiler Architecture Pipeline
```
SQL Query String
       │
       ▼
[Lexical Analyzer] ──► Token Stream with Line/Col Info
       │
       ▼
[LL(1) Predictive Parser] ──► Stack Derivation Trace + Concrete Parse Tree
       │
       ▼
[AST Builder] ──► Abstract Syntax Tree (QueryNode)
       │
       ▼
[Semantic Analyzer] ──► Schema Verification (SQLite) & Type Compatibility Check
       │
       ▼
[Query Optimizer] ──► Projection Pruning, Redundant Predicate Elimination, Sort Optimization
       │
       ▼
[Execution Planner] ──► Physical Operator Sequence (Scan → Filter → Sort → Project)
       │
       ▼
[Code Generator & Executor] ──► Safe Parameterized Execution on SQLite Backend
       │
       ▼
Final Result Set
```

## Project Structure
```
sql_compiler/
├── main.py                     # CLI entry point and unified pipeline runner
├── requirements.txt            # Python dependencies (Streamlit, Pandas)
├── README.md                   # Complete documentation
│
├── lexer/                      # Phase 1: Lexical Analysis
│   ├── tokens.py               # Token types, definitions & positions
│   └── lexer.py                # Handcrafted tokenizer
│
├── grammar/                    # Phase 2: Grammar & LL(1) Math
│   ├── grammar.py              # Formal Mini-SQL Grammar (28 productions)
│   ├── first_follow.py         # Programmatic FIRST & FOLLOW calculation
│   └── parsing_table.py        # LL(1) Table generator & conflict detector
│
├── parser/                     # Phase 3: LL(1) Parsing Engine
│   ├── parse_tree.py           # Concrete parse tree representation
│   └── ll1_parser.py           # Table-driven predictive parser with stack
│
├── ast_module/                 # Phase 4: AST Construction
│   ├── nodes.py                # AST Node hierarchy & visual tree formatter
│   └── builder.py              # ParseTree -> AST transformer
│
├── semantic/                   # Phase 5: Semantic Validation
│   └── analyzer.py             # Schema & type compatibility analyzer
│
├── optimizer/                  # Phase 6: Query Optimization
│   └── optimizer.py            # Honest before/after optimizer
│
├── execution/                  # Phase 7 & 8: Plan & Backend
│   ├── planner.py              # Physical relational execution planner
│   └── executor.py             # Parameterized SQL synthesizer & executor
│
├── database/                   # Sample Database
│   ├── database.py             # SQLite helper and schema introspection
│   ├── schema.sql              # Employees table schema & sample records
│   └── sample.db               # Active SQLite database file
│
├── educational/                # Part A: Independent LL(1) Theory
│   └── theory_ll1.py           # Canonical grammar E -> T E' demonstration
│
├── ui/                         # User Interface
│   └── app.py                  # Academic Streamlit web application
│
├── examples/                   # Sample SQL Queries
│   └── queries.sql             # Valid and invalid queries for demo
│
├── tests/                      # Automated Test Suite (100% Pass)
│   ├── test_lexer.py
│   ├── test_first_follow.py
│   ├── test_parser.py
│   ├── test_semantic.py
│   ├── test_optimizer.py
│   └── test_all.py             # Master test suite runner (19/19 tests)
│
└── docs/                       # Academic Documents
    ├── grammar.md              # Detailed LL(1) Grammar & FIRST/FOLLOW spec
    ├── ppt_content.md          # 26-slide presentation script
    ├── report.md               # 24-section formal project report
    └── viva_prep.md            # Comprehensive viva questions & answers
```

## How to Run

### 1. Run Automated Test Suite (All 19 Tests)
```bash
python tests/test_all.py
```

### 2. Run CLI Pipeline on a Query
```bash
python main.py --query "SELECT name, salary FROM employees WHERE salary > 50000 ORDER BY salary DESC;"
```

### 3. Run Educational LL(1) Theory Demo (E -> T E')
```bash
python educational/theory_ll1.py
```

### 4. Launch the Web UI
```bash
streamlit run ui/app.py
```
Then open `http://localhost:8501` in your browser.
