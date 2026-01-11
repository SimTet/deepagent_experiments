"""Script to create the sample SQLite database with realistic business data."""

import random
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent / "sample.db"


def create_sample_db():
    """Create sample database with departments, employees, products, and sales."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create tables
    cursor.executescript("""
        DROP TABLE IF EXISTS sales;
        DROP TABLE IF EXISTS employees;
        DROP TABLE IF EXISTS departments;
        DROP TABLE IF EXISTS products;

        CREATE TABLE departments (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            budget REAL NOT NULL,
            location TEXT
        );

        CREATE TABLE employees (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            department_id INTEGER REFERENCES departments(id),
            salary REAL NOT NULL,
            hire_date DATE NOT NULL,
            manager_id INTEGER REFERENCES employees(id)
        );

        CREATE TABLE products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            stock_quantity INTEGER NOT NULL
        );

        CREATE TABLE sales (
            id INTEGER PRIMARY KEY,
            employee_id INTEGER REFERENCES employees(id),
            product_id INTEGER REFERENCES products(id),
            amount REAL NOT NULL,
            quantity INTEGER NOT NULL,
            sale_date DATE NOT NULL,
            region TEXT
        );
    """)

    # Insert departments
    departments = [
        (1, "Engineering", 500000, "Building A"),
        (2, "Sales", 300000, "Building B"),
        (3, "Marketing", 200000, "Building B"),
        (4, "HR", 150000, "Building C"),
        (5, "Finance", 250000, "Building C"),
    ]
    cursor.executemany("INSERT INTO departments VALUES (?, ?, ?, ?)", departments)

    # Insert employees (50 employees)
    first_names = [
        "Alice", "Bob", "Charlie", "Diana", "Eve", "Frank",
        "Grace", "Henry", "Ivy", "Jack", "Karen", "Leo",
        "Maria", "Nathan", "Olivia", "Peter", "Quinn", "Rachel",
        "Sam", "Tina",
    ]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]

    random.seed(42)  # For reproducibility
    employees = []
    for i in range(1, 51):
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        dept = random.randint(1, 5)
        salary = random.randint(50000, 150000)
        hire_date = datetime(2020, 1, 1) + timedelta(days=random.randint(0, 1500))
        manager = random.randint(1, min(i - 1, 10)) if i > 1 else None
        employees.append((i, name, dept, salary, hire_date.strftime("%Y-%m-%d"), manager))

    cursor.executemany("INSERT INTO employees VALUES (?, ?, ?, ?, ?, ?)", employees)

    # Insert products
    products = [
        (1, "Laptop Pro", "Electronics", 1299.99, 150),
        (2, "Wireless Mouse", "Electronics", 49.99, 500),
        (3, "Desk Chair", "Furniture", 299.99, 75),
        (4, 'Monitor 27"', "Electronics", 399.99, 200),
        (5, "Keyboard", "Electronics", 89.99, 300),
        (6, "Standing Desk", "Furniture", 549.99, 50),
        (7, "Webcam HD", "Electronics", 79.99, 250),
        (8, "Office Lamp", "Furniture", 45.99, 400),
        (9, "USB Hub", "Electronics", 29.99, 600),
        (10, "Notebook Set", "Office Supplies", 12.99, 1000),
    ]
    cursor.executemany("INSERT INTO products VALUES (?, ?, ?, ?, ?)", products)

    # Insert sales (500 transactions over 2024)
    regions = ["North", "South", "East", "West"]
    prices = {p[0]: p[3] for p in products}

    sales = []
    for i in range(1, 501):
        emp_id = random.randint(1, 50)
        prod_id = random.randint(1, 10)
        qty = random.randint(1, 10)
        amount = prices[prod_id] * qty
        sale_date = datetime(2024, 1, 1) + timedelta(days=random.randint(0, 364))
        region = random.choice(regions)
        sales.append((i, emp_id, prod_id, amount, qty, sale_date.strftime("%Y-%m-%d"), region))

    cursor.executemany("INSERT INTO sales VALUES (?, ?, ?, ?, ?, ?, ?)", sales)

    conn.commit()
    conn.close()
    print(f"Sample database created at {DB_PATH}")
    print("Tables created: departments, employees, products, sales")
    print("  - 5 departments")
    print("  - 50 employees")
    print("  - 10 products")
    print("  - 500 sales transactions")


if __name__ == "__main__":
    create_sample_db()
