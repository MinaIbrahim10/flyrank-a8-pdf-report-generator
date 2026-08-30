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

        migrations = {
            "idempotency_key":
                "ALTER TABLE reports ADD COLUMN idempotency_key TEXT",
            "status":
                "ALTER TABLE reports ADD COLUMN status TEXT DEFAULT 'done'",
            "error":
                "ALTER TABLE reports ADD COLUMN error TEXT",
            "days":
                "ALTER TABLE reports ADD COLUMN days INTEGER DEFAULT 30",
            "generation_ms":
                "ALTER TABLE reports ADD COLUMN generation_ms REAL",
            "file_size_bytes":
                "ALTER TABLE reports ADD COLUMN file_size_bytes INTEGER",
            "sha256":
                "ALTER TABLE reports ADD COLUMN sha256 TEXT",
            "started_at":
                "ALTER TABLE reports ADD COLUMN started_at TEXT",
            "finished_at":
                "ALTER TABLE reports ADD COLUMN finished_at TEXT",
        }

        for column, sql in migrations.items():
            if column not in columns:
                connection.execute(sql)

        connection.execute(
            """
            UPDATE reports
            SET status = 'done'
            WHERE status IS NULL
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
