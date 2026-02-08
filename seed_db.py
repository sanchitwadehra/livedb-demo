"""Create and seed the SQLite database for the demo app."""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "app.sqlite")


def seed():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("DROP TABLE IF EXISTS orders")
    c.execute("DROP TABLE IF EXISTS users")

    c.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            age INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'active'
        )
    """)

    c.execute("""
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            product TEXT NOT NULL,
            total REAL NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)

    c.executemany("INSERT INTO users VALUES (?,?,?,?,?)", [
        (1, "Alice Smith", "alice@example.com", 28, "active"),
        (2, "Bob Johnson", "bob@example.com", 35, "active"),
        (3, "Charlie Brown", "charlie@example.com", 22, "inactive"),
        (4, "Diana Ross", "diana@example.com", 45, "active"),
        (5, "Eve Wilson", "eve@example.com", 19, "active"),
        (6, "Frank Miller", "frank@example.com", 52, "inactive"),
        (7, "Grace Lee", "grace@example.com", 31, "active"),
        (8, "Henry Davis", "henry@example.com", 27, "active"),
        (9, "Ivy Chen", "ivy@example.com", 24, "active"),
        (10, "Jack White", "jack@example.com", 38, "inactive"),
    ])

    c.executemany("INSERT INTO orders VALUES (?,?,?,?,?)", [
        (1, 1, "Laptop", 999.99, "2026-01-15"),
        (2, 1, "Mouse", 29.99, "2026-01-20"),
        (3, 2, "Keyboard", 149.99, "2026-01-22"),
        (4, 3, "Monitor", 399.99, "2026-02-01"),
        (5, 4, "Headphones", 199.99, "2026-02-03"),
        (6, 5, "Webcam", 79.99, "2026-02-04"),
        (7, 7, "USB Hub", 49.99, "2026-02-05"),
        (8, 8, "Laptop Stand", 89.99, "2026-02-06"),
        (9, 9, "External SSD", 129.99, "2026-02-07"),
        (10, 2, "Desk Lamp", 45.99, "2026-02-08"),
    ])

    conn.commit()
    conn.close()
    print(f"Seeded {DB_PATH}: 10 users, 10 orders")


if __name__ == "__main__":
    seed()
