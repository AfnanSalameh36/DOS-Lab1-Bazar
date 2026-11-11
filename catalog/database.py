
import os
import sqlite3
from pathlib import Path

DB_PATH = Path(
    os.environ.get(
        "CATALOG_DB_PATH",
        str(Path(__file__).resolve().parent / "catalog.db")
    )
)


def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                topic TEXT NOT NULL,
                price REAL NOT NULL CHECK(price >= 0),
                quantity INTEGER NOT NULL CHECK(quantity >= 0)
            )
        """)

        books = [
            (1, "How to get a good grade in DOS in 40 minutes a day",
             "distributed systems", 40, 10),

            (2, "RPCs for Noobs",
             "distributed systems", 50, 5),

            (3, "Xen and the Art of Surviving Undergraduate School",
             "undergraduate school", 30, 8),

            (4, "Cooking for the Impatient Undergrad",
             "undergraduate school", 25, 12)
        ]

        conn.executemany("""
            INSERT OR IGNORE INTO books
            (id, title, topic, price, quantity)
            VALUES (?, ?, ?, ?, ?)
        """, books)


def search_books(topic):
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT id, title
            FROM books
            WHERE LOWER(topic) = LOWER(?)
        """, (topic,)).fetchall()

        return [dict(row) for row in rows]


def get_book(item_id):
    with get_connection() as conn:
        row = conn.execute("""
            SELECT title, quantity, price
            FROM books
            WHERE id = ?
        """, (item_id,)).fetchone()

        return dict(row) if row else None


def update_book(item_id, quantity_delta=None, price=None):
    with get_connection() as conn:

        if quantity_delta is not None:
            cursor = conn.execute("""
                UPDATE books
                SET quantity = quantity + ?
                WHERE id = ?
                AND quantity + ? >= 0
            """, (quantity_delta, item_id, quantity_delta))

        else:
            cursor = conn.execute("""
                UPDATE books
                SET price = ?
                WHERE id = ?
            """, (price, item_id))

        if cursor.rowcount == 0:
            exists = conn.execute(
                "SELECT 1 FROM books WHERE id = ?",
                (item_id,)
            ).fetchone()

            if exists is None:
                return "not_found", None

            return "insufficient_stock", None

        row = conn.execute("""
            SELECT id, title, quantity, price
            FROM books
            WHERE id = ?
        """, (item_id,)).fetchone()

        return "success", dict(row)
