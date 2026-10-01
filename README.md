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

## How the LL Parser version works

The project is a compiler pipeline. Each stage has one job and passes a
different representation to the next stage:

1. `lexer/lexer.py` reads characters and produces `Token` objects from
   `lexer/tokens.py`. For example, `SELECT name` becomes `SELECT`, `ID(name)`.
   It also records line and column positions so errors can point to the input.
2. `grammar/grammar.py` describes the Mini-SQL language as productions such
   as `Query -> SELECT SelectList FROM TableClause ...`. `first_follow.py`
   calculates FIRST and FOLLOW sets. `parsing_table.py` uses them to build the
   LL(1) lookup table and reports conflicts if the grammar is not predictive.
3. `parser/ll1_parser.py` is the actual table-driven parser. Its stack holds
   grammar symbols. A terminal is matched against the lookahead token; a
   non-terminal is replaced using one table entry. The same operation builds
   `parser/parse_tree.py`, a concrete derivation tree, and a trace for teaching.
4. `ast_module/builder.py` removes grammar-only nodes from the parse tree and
   creates the smaller semantic tree defined in `ast_module/nodes.py`:
   query, selected columns, table, conditions, and ordering.
5. `semantic/analyzer.py` checks meaning rather than spelling: the table and
   columns must exist, and a literal must be compatible with its column type.
   It reads actual SQLite metadata through `database/database.py`.
6. `optimizer/optimizer.py` works on a copy of the valid AST. It removes
   duplicate selected columns, removes repeated predicates, and records every
   applied rule in an optimization report.
7. `execution/planner.py` converts the optimized AST into human-readable
   physical steps: table scan, optional filter, optional sort, then projection.
8. `execution/executor.py` converts the AST—not the original string—into
   parameterized SQLite SQL. Values are sent as parameters, which is safer than
   concatenating user input. The result contains column names, rows, and count.

`main.py` constructs the grammar/table once in `MiniSQLCompiler`, then runs
these stages in order. It stops at the first failed stage and stores the phase,
message, and all successful intermediate results in `CompilationReport`.
`app.py` uses the same compiler from a Flask API and displays the tokens,
grammar information, trace, AST, optimizer output, plan, and result in a web UI.
The `educational` module is independent demonstration code for the classic
arithmetic grammar `E -> T E'`; it explains FIRST/FOLLOW and stack parsing
without requiring a SQL query.

## Reading the folder easily

The important dependency direction is:

`main/app -> lexer + grammar + parser -> AST -> semantic -> optimizer -> planner/executor -> database`

The `__init__.py` files were empty package markers and are intentionally not
needed on modern Python versions; the folders remain importable namespace
packages. `tests/` exercises each compiler phase separately, while
`database/schema.sql`, `examples/queries.sql`, and `docs/` are supporting data
and study material rather than runtime pipeline stages.

### 3. Run Educational LL(1) Theory Demo (E -> T E')
```bash
python educational/theory_ll1.py
```

### 4. Launch the Web UI
```bash
streamlit run ui/app.py
```
Then open `http://localhost:8501` in your browser.
