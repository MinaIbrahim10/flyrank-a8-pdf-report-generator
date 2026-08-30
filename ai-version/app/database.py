import sqlite3
from contextlib import contextmanager
from pathlib import Path

from .config import DATABASE_PATH


def connect(path: Path = DATABASE_PATH) -> sqlite3.Connection:
    connection = sqlite3.connect(path, timeout=30)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


@contextmanager
def database(path: Path = DATABASE_PATH):
    connection = connect(path)
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def initialize(path: Path = DATABASE_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with database(path) as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer TEXT NOT NULL,
                product TEXT NOT NULL,
                amount REAL NOT NULL CHECK (amount >= 0),
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_date TEXT NOT NULL,
                generated_at TEXT NOT NULL,
                file_name TEXT NOT NULL UNIQUE,
                total_orders INTEGER NOT NULL,
                total_revenue REAL NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_orders_created_at
                ON orders(created_at);
            CREATE INDEX IF NOT EXISTS idx_reports_report_date
                ON reports(report_date);
            """
        )

