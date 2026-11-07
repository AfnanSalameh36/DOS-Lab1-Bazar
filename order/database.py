
import sqlite3
from pathlib import Path
from contextlib import closing

# Store the database file inside the order folder
DATABASE_PATH = Path(__file__).resolve().parent / "orders.db"


def get_connection():
    """Create a connection to the Order database."""
    return sqlite3.connect(DATABASE_PATH, timeout=10)


def init_db():
    """Create the purchases table if it does not exist."""
    with closing(get_connection()) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER NOT NULL,
                book_title TEXT NOT NULL,
                purchased_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        connection.commit()


def save_purchase(item_id, book_title):
    """Save a successful purchase in the database."""
    with closing(get_connection()) as connection:
        cursor = connection.execute(
            """
            INSERT INTO purchases (item_id, book_title)
            VALUES (?, ?)
            """,
            (item_id, book_title)
        )
        connection.commit()
        return cursor.lastrowid
