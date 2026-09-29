"""
app.py - Lightweight Academic Web UI for LL(1) Parser & SQL Compiler.
Run with: python app.py
Opens http://localhost:5050 in your browser.
"""

import os
import sys
import webbrowser
import threading
from typing import Dict, Any
from flask import Flask, request, jsonify, render_template_string

# Ensure current directory is in path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from main import MiniSQLCompiler
from database.database import init_db, get_table_schema, execute_query, DB_PATH
from educational.theory_ll1 import run_educational_demo

# Initialize database only if missing to prevent SQLite file locks
if not os.path.exists(DB_PATH):
    init_db()

# Initialize compiler
compiler = MiniSQLCompiler()

app = Flask(__name__)

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LL(1) Parser & Mini-SQL Compiler</title>
    <style>
        :root {
            --primary: #2563eb;
            --primary-hover: #1d4ed8;
            --bg: #f8fafc;
            --card-bg: #ffffff;
            --text-main: #1e293b;
            --text-muted: #64748b;
            --border: #e2e8f0;
            --success-bg: #ecfdf5;
            --success-text: #065f46;
            --error-bg: #fef2f2;
            --error-text: #991b1b;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg);
            color: var(--text-main);
            line-height: 1.5;
            padding: 24px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        header {
            margin-bottom: 20px;
            padding-bottom: 16px;
            border-bottom: 1px solid var(--border);
        }
        h1 { font-size: 26px; font-weight: 700; color: #0f172a; }
        .subtitle { font-size: 14px; color: var(--text-muted); margin-top: 4px; }
        
        /* Header Mode Buttons */
        .header-actions { margin-top: 12px; display: flex; gap: 10px; flex-wrap: wrap; }
        .btn-pill {
            background: #e2e8f0;
            border: none;
            padding: 7px 16px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            color: #334155;
        }
        .btn-pill:hover { background: #cbd5e1; }
        .btn-pill.active { background: var(--primary); color: #fff; }

        /* Card Container */
        .card {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        
        /* Sample Query Bar */
        .preset-bar {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 12px;
            flex-wrap: wrap;
        }
        .preset-label {
            font-size: 13px;
            font-weight: 600;
            color: #475569;
        }
        .preset-select {
            padding: 7px 12px;
            border: 1px solid var(--border);
            border-radius: 6px;
            font-size: 13px;
            background: #fff;
            color: #1e293b;
            min-width: 320px;
            outline: none;
        }
        .preset-select:focus { border-color: var(--primary); }

        label { font-size: 13px; font-weight: 600; color: #475569; display: block; margin-bottom: 6px; }
        textarea {
            width: 100%;
            height: 80px;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 14px;
            padding: 10px;
            border: 1px solid var(--border);
            border-radius: 6px;
            outline: none;
            resize: vertical;
            background: #ffffff;
        }
        textarea:focus { border-color: var(--primary); }
        .controls { display: flex; justify-content: flex-end; align-items: center; margin-top: 12px; }
        .btn-primary {
            background: var(--primary);
            color: #fff;
            border: none;
            padding: 9px 24px;
            border-radius: 6px;
            font-weight: 600;
            font-size: 14px;
            cursor: pointer;
            transition: background 0.2s;
        }
        .btn-primary:hover { background: var(--primary-hover); }
        
        /* Tabs */
        .tabs { display: flex; gap: 4px; border-bottom: 1px solid var(--border); margin-bottom: 16px; overflow-x: auto; }
        .tab-btn {
            background: none;
            border: none;
            padding: 10px 16px;
            font-size: 14px;
            font-weight: 600;
            color: var(--text-muted);
            cursor: pointer;
            border-bottom: 2px solid transparent;
            white-space: nowrap;
        }
        .tab-btn.active { color: var(--primary); border-bottom-color: var(--primary); }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        
        /* Monospace / Code Blocks */
        pre {
            background: #f1f5f9;
            padding: 14px;
            border-radius: 6px;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 13px;
            overflow-x: auto;
            border: 1px solid #e2e8f0;
            white-space: pre-wrap;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
            margin-top: 10px;
        }
        th, td {
            text-align: left;
            padding: 9px 12px;
            border: 1px solid var(--border);
        }
        th { background: #f8fafc; font-weight: 600; }
        tr:nth-child(even) { background: #fcfcfd; }
        
        /* Alerts & Badges */
        .alert {
            padding: 12px 16px;
            border-radius: 6px;
            font-size: 14px;
            margin-bottom: 16px;
            font-weight: 500;
        }
        .alert-success { background: var(--success-bg); color: var(--success-text); border: 1px solid #a7f3d0; }
        .alert-error { background: var(--error-bg); color: var(--error-text); border: 1px solid #fecaca; }
        .badge {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
        }
        .badge-success { background: #d1fae5; color: #065f46; }
        .badge-fail { background: #fee2e2; color: #991b1b; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Table-Driven LL(1) Parser & Mini-SQL Compiler</h1>
            <div class="subtitle">Compiler Design Project — LL(1) Predictive Parser | SQL Compiler Pipeline</div>
            <div class="header-actions">
                <button id="btnModeCompiler" class="btn-pill active" onclick="setMode('compiler')">Standard Compiler</button>
                <button id="btnModeTheory" class="btn-pill" onclick="loadTheoryDemo()">Educational Theory: E &rarr; T E&#39;</button>
                <button id="btnModeGrammar" class="btn-pill" onclick="loadGrammarView()">Mini-SQL LL(1) Table (0 Conflicts)</button>
            </div>
        </header>

        <div class="card" id="inputCard">
            <div class="preset-bar">
                <span class="preset-label">Pre-built Sample Queries:</span>
                <select id="presetSelect" class="preset-select" onchange="applyPreset()">
                    <option value="custom">-- Select a Pre-built Query --</option>
                    <option value="1">1. Filter & Descending Sort (Valid)</option>
                    <option value="2">2. Full Table Projection (SELECT *) (Valid)</option>
                    <option value="3">3. Compound Filter with AND (Valid)</option>
                    <option value="4">4. Simple Single Column Selection (Valid)</option>
                    <option value="5">5. Syntax Error: Missing Projection (SELECT FROM ...)</option>
                    <option value="6">6. Syntax Error: Missing FROM keyword</option>
                    <option value="7">7. Semantic Error: Unknown Column (SELECT xyz)</option>
                    <option value="8">8. Semantic Error: Unknown Table (FROM students)</option>
                    <option value="9">9. Optimizer Demo: Duplicate Column & Redundant Predicate</option>
                </select>
            </div>

            <label for="sqlQuery">Mini-SQL Query Input:</label>
            <textarea id="sqlQuery">SELECT name, salary FROM employees WHERE salary > 50000 ORDER BY salary DESC;</textarea>
            
            <div class="controls">
                <button class="btn-primary" onclick="compileAndRun()">Compile & Execute</button>
            </div>
        </div>

        <div id="statusAlert"></div>

        <div class="card" id="outputCard">
            <div class="tabs">
                <button class="tab-btn active" onclick="openTab(event, 'tabResult')">1. Query Results</button>
                <button class="tab-btn" onclick="openTab(event, 'tabTrace')">2. LL(1) Stack Trace</button>
                <button class="tab-btn" onclick="openTab(event, 'tabTokens')">3. Lexer Tokens</button>
                <button class="tab-btn" onclick="openTab(event, 'tabAST')">4. AST (Query Tree)</button>
                <button class="tab-btn" onclick="openTab(event, 'tabSemantic')">5. Semantic Validation</button>
                <button class="tab-btn" onclick="openTab(event, 'tabOptimizer')">6. Query Optimizer</button>
                <button class="tab-btn" onclick="openTab(event, 'tabPlan')">7. Execution Plan</button>
            </div>

            <!-- Tab 1: Query Results -->
            <div id="tabResult" class="tab-content active">
                <div id="resultOutput">Processing initial query...</div>
            </div>

            <!-- Tab 2: LL(1) Stack Trace -->
            <div id="tabTrace" class="tab-content">
                <div id="traceSummary" style="margin-bottom: 10px; font-weight: 600;"></div>
                <div style="overflow-x: auto;">
                    <table id="traceTable">
                        <thead>
                            <tr>
                                <th style="width: 60px;">Step</th>
                                <th style="width: 280px;">Parser Stack</th>
                                <th style="width: 250px;">Remaining Input</th>
                                <th>Action Taken</th>
                            </tr>
                        </thead>
                        <tbody id="traceTbody"></tbody>
                    </table>
                </div>
            </div>

            <!-- Tab 3: Tokens -->
            <div id="tabTokens" class="tab-content">
                <div style="overflow-x: auto;">
                    <table id="tokensTable">
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>Token Type</th>
                                <th>Lexeme / Value</th>
                                <th>Line</th>
                                <th>Column</th>
                            </tr>
                        </thead>
                        <tbody id="tokensTbody"></tbody>
                    </table>
                </div>
            </div>

            <!-- Tab 4: AST -->
            <div id="tabAST" class="tab-content">
                <pre id="astOutput">AST will be displayed here.</pre>
            </div>

            <!-- Tab 5: Semantic -->
            <div id="tabSemantic" class="tab-content">
                <div id="semanticOutput"></div>
            </div>

            <!-- Tab 6: Optimizer -->
            <div id="tabOptimizer" class="tab-content">
                <div id="optimizerOutput"></div>
            </div>

            <!-- Tab 7: Physical Plan -->
            <div id="tabPlan" class="tab-content">
                <pre id="planOutput"></pre>
            </div>
        </div>
    </div>

    <script>
        const PRESETS = {
            "1": "SELECT name, salary FROM employees WHERE salary > 50000 ORDER BY salary DESC;",
            "2": "SELECT * FROM employees;",
            "3": "SELECT name, age, salary FROM employees WHERE age >= 25 AND salary <= 70000 ORDER BY age ASC;",
            "4": "SELECT name FROM employees;",
            "5": "SELECT FROM employees;",
            "6": "SELECT name employees;",
            "7": "SELECT xyz FROM employees;",
            "8": "SELECT name FROM students;",
            "9": "SELECT name, salary, name FROM employees WHERE salary > 50000 AND salary > 50000;"
        };

        function escapeHtml(text) {
            if (text === null || text === undefined) return "";
            return String(text)
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        }

        function setMode(mode) {
            document.querySelectorAll('.btn-pill').forEach(b => b.classList.remove('active'));
            if (mode === 'compiler') {
                document.getElementById('btnModeCompiler').classList.add('active');
            }
        }

        function applyPreset() {
            const val = document.getElementById('presetSelect').value;
            if (PRESETS[val]) {
                document.getElementById('sqlQuery').value = PRESETS[val];
                setMode('compiler');
                const alertBox = document.getElementById('statusAlert');
                alertBox.innerHTML = "<div class='alert' style='background:#f1f5f9; color:#475569;'>Query loaded into editor. Click <strong>Compile & Execute</strong> to process.</div>";
            }
        }

        function openTab(evt, tabId) {
            const tabs = document.querySelectorAll('.tab-content');
            tabs.forEach(t => t.classList.remove('active'));
            const btns = document.querySelectorAll('.tab-btn');
            btns.forEach(b => b.classList.remove('active'));
            document.getElementById(tabId).classList.add('active');
            if (evt) evt.currentTarget.classList.add('active');
        }

        async function compileAndRun() {
            setMode('compiler');
            const sql = document.getElementById('sqlQuery').value.trim();
            const alertBox = document.getElementById('statusAlert');
            alertBox.innerHTML = "<div class='alert' style='background:#e0f2fe; color:#0369a1;'>Running LL(1) Compiler Pipeline...</div>";

            try {
                const res = await fetch('/compile', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ sql: sql })
                });
                const data = await res.json();

                if (!data.success) {
                    alertBox.innerHTML = "<div class='alert alert-error'><strong>Compilation Halted at [" + escapeHtml(data.error_stage) + "]:</strong><br>" + escapeHtml(data.error_message) + "</div>";
                } else {
                    alertBox.innerHTML = "<div class='alert alert-success'><strong>Success:</strong> Query parsed, validated, optimized, and executed! (" + data.row_count + " rows returned)</div>";
                }

                // Render Results
                renderResults(data);
                // Render Trace
                renderTrace(data.trace, data.success);
                // Render Tokens
                renderTokens(data.tokens);
                // Render AST
                document.getElementById('astOutput').textContent = data.ast_text || "AST not available.";
                // Render Semantic
                renderSemantic(data.semantic);
                // Render Optimizer
                renderOptimizer(data.optimizer, data.ast_text);
                // Render Plan
                document.getElementById('planOutput').textContent = data.plan_text || "Execution plan not available.";

            } catch (err) {
                alertBox.innerHTML = "<div class='alert alert-error'>Server Communication Error: " + escapeHtml(err.message) + "</div>";
            }
        }

        function renderResults(data) {
            const div = document.getElementById('resultOutput');
            if (!data.success) {
                div.innerHTML = "<p style='color:var(--error-text);'>No database records produced due to <strong>" + escapeHtml(data.error_stage) + "</strong>.</p>";
                return;
            }
            let html = "<p style='margin-bottom:8px;'><strong>Compiled Parameterized SQL:</strong> <code>" + escapeHtml(data.generated_sql) + "</code></p>";
            if (data.rows && data.rows.length > 0) {
                html += "<table><thead><tr>";
                data.columns.forEach(c => { html += "<th>" + escapeHtml(c) + "</th>"; });
                html += "</tr></thead><tbody>";
                data.rows.forEach(r => {
                    html += "<tr>";
                    r.forEach(v => { html += "<td>" + escapeHtml(v) + "</td>"; });
                    html += "</tr>";
                });
                html += "</tbody></table>";
            } else {
                html += "<p>Query executed successfully, but 0 matching records were found.</p>";
            }
            div.innerHTML = html;
        }

        function renderTrace(trace, isSuccess) {
            const tbody = document.getElementById('traceTbody');
            const summary = document.getElementById('traceSummary');
            tbody.innerHTML = '';
            if (!trace || trace.length === 0) {
                summary.textContent = "No trace steps recorded.";
                return;
            }
            const statusClass = isSuccess ? 'badge-success' : 'badge-fail';
            const statusText = isSuccess ? 'ACCEPTED' : 'REJECTED';
            summary.innerHTML = "Completed in <strong>" + trace.length + "</strong> stack execution steps. Parser Status: <span class='badge " + statusClass + "'>" + statusText + "</span>";
            trace.forEach(t => {
                const tr = document.createElement('tr');
                tr.innerHTML = "<td>" + t.step + "</td>" +
                               "<td><code>" + escapeHtml(t.stack) + "</code></td>" +
                               "<td><code>" + escapeHtml(t.remaining_input) + "</code></td>" +
                               "<td>" + escapeHtml(t.action) + "</td>";
                tbody.appendChild(tr);
            });
        }

        function renderTokens(tokens) {
            const tbody = document.getElementById('tokensTbody');
            tbody.innerHTML = '';
            if (!tokens || tokens.length === 0) return;
            tokens.forEach((t, i) => {
                const tr = document.createElement('tr');
                tr.innerHTML = "<td>" + (i + 1) + "</td>" +
                               "<td><strong>" + escapeHtml(t.type) + "</strong></td>" +
                               "<td>" + escapeHtml(t.value) + "</td>" +
                               "<td>" + t.line + "</td>" +
                               "<td>" + t.column + "</td>";
                tbody.appendChild(tr);
            });
        }

        function renderSemantic(sem) {
            const div = document.getElementById('semanticOutput');
            if (!sem) { div.innerHTML = "<p>Semantic analysis did not run.</p>"; return; }
            if (sem.is_valid) {
                div.innerHTML = "<div class='alert alert-success'>✔ Semantic Validation Passed: Table exists, columns verified, types compatible.</div>" +
                                "<p><strong>Table Name:</strong> <code>" + escapeHtml(sem.table_name) + "</code></p>" +
                                "<p><strong>Resolved Columns:</strong> <code>" + escapeHtml(sem.resolved_columns.join(', ')) + "</code></p>";
            } else {
                let errList = sem.errors.map(e => "<li>" + escapeHtml(e) + "</li>").join('');
                div.innerHTML = "<div class='alert alert-error'>✘ Semantic Validation Failed:</div><ul>" + errList + "</ul>";
            }
        }

        function renderOptimizer(opt, origAst) {
            const div = document.getElementById('optimizerOutput');
            if (!opt) { div.innerHTML = "<p>Optimizer did not run.</p>"; return; }
            if (opt.is_optimized) {
                div.innerHTML = "<div class='alert alert-success'>✔ Optimization Applied: " + escapeHtml(opt.message) + "</div>" +
                                "<div style='display:grid; grid-template-columns:1fr 1fr; gap:12px;'>" +
                                "<div><strong>Original AST:</strong><pre>" + escapeHtml(origAst) + "</pre></div>" +
                                "<div><strong>Optimized AST:</strong><pre>" + escapeHtml(opt.optimized_ast_text) + "</pre></div>" +
                                "</div>";
            } else {
                div.innerHTML = "<div class='alert' style='background:#f1f5f9; color:#475569;'>ℹ " + escapeHtml(opt.message) + "</div>" +
                                "<pre>" + escapeHtml(origAst) + "</pre>";
            }
        }

        // Educational Theory Demo
        async function loadTheoryDemo() {
            document.querySelectorAll('.btn-pill').forEach(b => b.classList.remove('active'));
            document.getElementById('btnModeTheory').classList.add('active');
            const alertBox = document.getElementById('statusAlert');
            alertBox.innerHTML = "<div class='alert' style='background:#e0f2fe; color:#0369a1;'>Simulating Canonical Educational LL(1) Grammar (E &rarr; T E&#39;) on input &quot;id + id&quot; ...</div>";
            try {
                const res = await fetch('/theory');
                const data = await res.json();
                alertBox.innerHTML = "<div class='alert alert-success'>Canonical LL(1) Demo: Input &quot;id + id&quot; successfully parsed and ACCEPTED with 0 conflicts!</div>";
                renderTrace(data.trace, true);
                document.querySelectorAll('.tab-btn')[1].click();
            } catch (e) {
                alertBox.innerHTML = "<div class='alert alert-error'>Failed to load theory demo: " + escapeHtml(e.message) + "</div>";
            }
        }

        // View Grammar and Parsing Table
        async function loadGrammarView() {
            document.querySelectorAll('.btn-pill').forEach(b => b.classList.remove('active'));
            document.getElementById('btnModeGrammar').classList.add('active');
            const alertBox = document.getElementById('statusAlert');
            alertBox.innerHTML = "<div class='alert' style='background:#e0f2fe; color:#0369a1;'>Loading Mini-SQL LL(1) Parsing Table ...</div>";
            try {
                const res = await fetch('/grammar');
                const data = await res.json();
                alertBox.innerHTML = "<div class='alert alert-success'>Mini-SQL Parsing Table: Strictly LL(1) with 0 Conflicts. Displaying below in Tab 4.</div>";
                document.getElementById('astOutput').textContent = data.table_text;
                document.querySelectorAll('.tab-btn')[3].click();
            } catch (e) {
                alertBox.innerHTML = "<div class='alert alert-error'>Failed to load grammar: " + escapeHtml(e.message) + "</div>";
            }
        }

        // Ready on page load (manual execution only)
        window.addEventListener('DOMContentLoaded', () => {
            const alertBox = document.getElementById('statusAlert');
            alertBox.innerHTML = "<div class='alert' style='background:#f1f5f9; color:#475569;'>Ready. Select a pre-built query or type your own, then click <strong>Compile & Execute</strong>.</div>";
        });
    </script>
</body>
</html>"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/compile", methods=["POST"])
def compile_sql():
    data = request.get_json() or {}
    sql = data.get("sql", "").strip()
    if not sql:
        return jsonify({"success": False, "error_stage": "INPUT_ERROR", "error_message": "Query cannot be empty"})

    report = compiler.compile_and_execute(sql)

    tokens_list = [t.to_dict() for t in report.tokens]
    
    response = {
        "success": report.success,
        "error_stage": report.error_stage,
        "error_message": report.error_message,
        "tokens": tokens_list,
        "trace": report.trace,
        "ast_text": report.ast_text,
        "semantic": {
            "is_valid": report.semantic_result.is_valid if report.semantic_result else False,
            "errors": report.semantic_result.errors if report.semantic_result else [],
            "table_name": report.semantic_result.table_name if report.semantic_result else "",
            "resolved_columns": report.semantic_result.resolved_columns if report.semantic_result else []
        } if report.semantic_result else None,
        "optimizer": {
            "is_optimized": report.optimization_report.is_optimized if report.optimization_report else False,
            "message": report.optimization_report.summary_message if report.optimization_report else "",
            "optimized_ast_text": report.optimized_ast_text
        } if report.optimization_report else None,
        "plan_text": report.execution_plan.format_pipeline() if report.execution_plan else "",
        "generated_sql": report.execution_result.generated_sql if report.execution_result else "",
        "columns": report.execution_result.columns if report.execution_result else [],
        "rows": [list(r) for r in report.execution_result.rows] if report.execution_result else [],
        "row_count": report.execution_result.row_count if report.execution_result else 0
    }
    return jsonify(response)

@app.route("/theory")
def educational_theory():
    demo = run_educational_demo("id + id")
    return jsonify({
        "success": True,
        "trace": demo["trace"],
        "table_text": demo["table_formatted"],
        "first_follow": demo["first_follow_formatted"]
    })

@app.route("/grammar")
def grammar_view():
    return jsonify({
        "success": True,
        "table_text": compiler.parsing_table.format_table()
    })

@app.route("/schema")
def schema_view():
    schema = get_table_schema()
    cols, rows = execute_query("SELECT * FROM employees;")
    return jsonify({
        "schema": schema,
        "columns": cols,
        "rows": [list(r) for r in rows]
    })

def open_browser():
    webbrowser.open_new("http://localhost:5050")

if __name__ == "__main__":
    port = 5050
    print("=" * 65)
    print("   TABLE-DRIVEN LL(1) PARSER & MINI-SQL COMPILER")
    print(f"   Opening Web UI at: http://localhost:{port}")
    print("=" * 65)
    
    threading.Timer(1.0, open_browser).start()
    app.run(host="127.0.0.1", port=port, debug=False)
