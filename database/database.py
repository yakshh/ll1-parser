"""
database.py - Database manager and schema provider for the SQL compiler.
Uses Python's sqlite3 to create and query the sample database.
"""

import os
import sqlite3
from typing import Dict, List, Tuple, Any

DB_PATH = os.path.join(os.path.dirname(__file__), "sample.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")

def init_db(db_path: str = DB_PATH) -> None:
    """Initializes the SQLite database with the default schema and seed data."""
    conn = sqlite3.connect(db_path, timeout=30.0)
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    conn.executescript(schema_sql)
    conn.commit()
    conn.close()

def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    """Returns an active SQLite connection, initializing if not present."""
    if not os.path.exists(db_path):
        init_db(db_path)
    return sqlite3.connect(db_path, timeout=30.0)

def get_table_schema(db_path: str = DB_PATH) -> Dict[str, Dict[str, str]]:
    """
    Returns schema metadata for all tables in the database.
    Format:
    {
        "employees": {
            "id": "INTEGER",
            "name": "TEXT",
            "age": "INTEGER",
            "department": "TEXT",
            "salary": "REAL"
        }
    }
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [row[0] for row in cursor.fetchall()]
    
    schema = {}
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table});")
        # PRAGMA table_info returns: cid, name, type, notnull, dflt_value, pk
        cols = {row[1]: (row[2].upper() if row[2] else "TEXT") for row in cursor.fetchall()}
        schema[table] = cols
    
    conn.close()
    return schema

def execute_query(sql: str, params: Tuple[Any, ...] = (), db_path: str = DB_PATH) -> Tuple[List[str], List[Tuple[Any, ...]]]:
    """
    Executes a query safely with parameters and returns (column_names, rows).
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(sql, params)
    columns = [desc[0] for desc in cursor.description] if cursor.description else []
    rows = cursor.fetchall()
    conn.close()
    return columns, rows
