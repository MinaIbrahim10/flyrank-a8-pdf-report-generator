from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

ROOT = Path(__file__).resolve().parent.parent


def database_path() -> Path:
    return Path(os.getenv("REPORT_DB_PATH", ROOT / "report.db"))


def reports_dir() -> Path:
    return Path(os.getenv("REPORTS_DIR", ROOT / "reports"))


@contextmanager
def connection() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(database_path(), timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 30000")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def initialize_database() -> None:
    database_path().parent.mkdir(parents=True, exist_ok=True)
    reports_dir().mkdir(parents=True, exist_ok=True)
    with connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY,
                customer TEXT NOT NULL,
                product TEXT NOT NULL,
                amount REAL NOT NULL CHECK (amount >= 0),
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT,
                created_at TEXT NOT NULL,
                report_date TEXT,
                status TEXT NOT NULL DEFAULT 'generating'
                    CHECK (status IN ('generating', 'ready')),
                order_count INTEGER,
                total_revenue REAL
            );

            CREATE UNIQUE INDEX IF NOT EXISTS one_normal_report_per_day
                ON reports(report_date) WHERE report_date IS NOT NULL;
            """
        )

