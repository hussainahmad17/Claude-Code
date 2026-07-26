# Step 1 — Database Setup
#   get_db()   — returns a SQLite connection with row_factory and foreign keys enabled
#   init_db()  — creates all tables using CREATE TABLE IF NOT EXISTS
#   seed_db()  — inserts sample data for development

import os
import sqlite3
from datetime import date

from werkzeug.security import generate_password_hash

# Resolve the database path relative to this file so the app works no matter
# what directory it is launched from.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "expense_tracker.db")

# Fixed category list — every expense must use one of these.
CATEGORIES = (
    "Food",
    "Transport",
    "Bills",
    "Health",
    "Entertainment",
    "Shopping",
    "Other",
)


def get_db():
    """Open a SQLite connection. The caller owns it and should close it."""
    conn = sqlite3.connect(DB_PATH)
    # Templates index rows by column name.
    conn.row_factory = sqlite3.Row
    # foreign_keys is per-connection and defaults to OFF, so set it every time.
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create the tables if they don't exist. Safe to call repeatedly."""
    conn = get_db()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                name          TEXT NOT NULL,
                email         TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at    TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                amount      REAL    NOT NULL,
                category    TEXT    NOT NULL,
                date        TEXT    NOT NULL,
                description TEXT,
                created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def seed_db():
    """Insert demo data once. Does nothing if any user already exists."""
    conn = get_db()
    try:
        if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] > 0:
            return

        cur = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Demo User", "demo@spendly.com", generate_password_hash("demo123")),
        )
        user_id = cur.lastrowid

        today = date.today()

        def day(n):
            """Return a YYYY-MM-DD date in the current month."""
            return "{:04d}-{:02d}-{:02d}".format(today.year, today.month, n)

        # Amounts are in rupees. Every category appears at least once.
        expenses = [
            (user_id, 420.0, "Food", day(2), "Groceries for the week"),
            (user_id, 185.5, "Transport", day(4), "Auto to office"),
            (user_id, 1250.0, "Bills", day(7), "Electricity bill"),
            (user_id, 640.0, "Health", day(9), "Pharmacy refill"),
            (user_id, 350.0, "Entertainment", day(12), "Cinema tickets"),
            (user_id, 2199.0, "Shopping", day(15), "Running shoes"),
            (user_id, 275.0, "Food", day(18), "Dinner with friends"),
            (user_id, 500.0, "Other", day(21), "Gift for a colleague"),
        ]
        conn.executemany(
            """
            INSERT INTO expenses (user_id, amount, category, date, description)
            VALUES (?, ?, ?, ?, ?)
            """,
            expenses,
        )
        conn.commit()
    finally:
        conn.close()
