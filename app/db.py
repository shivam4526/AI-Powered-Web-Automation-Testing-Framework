from __future__ import annotations

import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "instance" / "ecommerce.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                full_name TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                price REAL NOT NULL,
                category TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS cart_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY (product_id) REFERENCES products(id)
            );
            """
        )

        user_count = conn.execute("SELECT COUNT(*) AS count FROM users").fetchone()["count"]
        if user_count == 0:
            conn.execute(
                "INSERT INTO users (username, password, full_name) VALUES (?, ?, ?)",
                ("demouser", "Password123", "Demo User"),
            )

        product_count = conn.execute("SELECT COUNT(*) AS count FROM products").fetchone()["count"]
        if product_count == 0:
            products = [
                ("Laptop Pro 14", "Performance laptop for developers", 1299.0, "Electronics"),
                ("Noise Cancelling Headphones", "Focus-friendly headphones", 199.0, "Electronics"),
                ("Ergonomic Chair", "Supportive chair for long work sessions", 349.0, "Furniture"),
                ("Mechanical Keyboard", "Tactile keyboard with RGB lighting", 129.0, "Accessories"),
                ("USB-C Dock", "Docking station with multiple ports", 89.0, "Accessories"),
            ]
            conn.executemany(
                "INSERT INTO products (name, description, price, category) VALUES (?, ?, ?, ?)",
                products,
            )

        conn.commit()


def get_products(search: str = "") -> list[dict]:
    query = "SELECT id, name, description, price, category FROM products"
    params: tuple[str, ...] = ()
    if search:
        query += " WHERE LOWER(name) LIKE ? OR LOWER(description) LIKE ? OR LOWER(category) LIKE ?"
        like_value = f"%{search.lower()}%"
        params = (like_value, like_value, like_value)
    query += " ORDER BY id"

    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(row) for row in rows]


def add_to_cart(username: str, product_id: int, quantity: int = 1) -> None:
    with get_connection() as conn:
        existing = conn.execute(
            "SELECT id, quantity FROM cart_items WHERE username = ? AND product_id = ?",
            (username, product_id),
        ).fetchone()
        if existing:
            conn.execute(
                "UPDATE cart_items SET quantity = ? WHERE id = ?",
                (existing["quantity"] + quantity, existing["id"]),
            )
        else:
            conn.execute(
                "INSERT INTO cart_items (username, product_id, quantity) VALUES (?, ?, ?)",
                (username, product_id, quantity),
            )
        conn.commit()


def get_cart(username: str) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT c.id, c.product_id, c.quantity, p.name, p.price
            FROM cart_items c
            JOIN products p ON p.id = c.product_id
            WHERE c.username = ?
            ORDER BY c.id
            """,
            (username,),
        ).fetchall()
    items = []
    for row in rows:
        item = dict(row)
        item["line_total"] = round(item["price"] * item["quantity"], 2)
        items.append(item)
    return items


def clear_cart(username: str) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM cart_items WHERE username = ?", (username,))
        conn.commit()
