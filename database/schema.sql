-- SQLite Database Schema and Seed Data for Mini-SQL Compiler Demo

DROP TABLE IF EXISTS employees;

CREATE TABLE employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER NOT NULL,
    department TEXT NOT NULL,
    salary REAL NOT NULL
);

INSERT INTO employees (id, name, age, department, salary) VALUES
    (1, 'Rahul', 24, 'IT', 60000.0),
    (2, 'Priya', 29, 'HR', 45000.0),
    (3, 'Amit', 31, 'IT', 75000.0),
    (4, 'Neha', 22, 'Sales', 40000.0),
    (5, 'Rohan', 27, 'IT', 55000.0),
    (6, 'Ananya', 26, 'Marketing', 48000.0),
    (7, 'Vikram', 35, 'Management', 90000.0),
    (8, 'Sneha', 28, 'Finance', 62000.0);
