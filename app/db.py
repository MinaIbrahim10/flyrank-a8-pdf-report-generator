import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "report.db"


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(
        DB_PATH,
        timeout=30,
    )

    connection.row_factory = sqlite3.Row

    return connection


def initialize_database() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer TEXT NOT NULL,
                product TEXT NOT NULL,
                amount REAL NOT NULL CHECK(amount >= 0),
                created_at TEXT NOT NULL
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS reports (
                id TEXT PRIMARY KEY,
                path TEXT NOT NULL,
                created_at TEXT NOT NULL,
                idempotency_key TEXT
            )
            """
        )

        columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(reports)"
            ).fetchall()
        }

        if "idempotency_key" not in columns:
            connection.execute(
                """
                ALTER TABLE reports
                ADD COLUMN idempotency_key TEXT
                """
            )

        connection.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS
            idx_reports_idempotency_key
            ON reports(idempotency_key)
            WHERE idempotency_key IS NOT NULL
            """
        )

        connection.commit()
