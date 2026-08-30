import random
import sqlite3
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.db import get_connection, initialize_database
from app.pdf_renderer import render_report_pdf
from app.report_data import get_report_data
from scripts.seed import CUSTOMERS, PRODUCTS, seed_orders


BENCHMARK_COUNT = 5000
BENCHMARK_PDF = ROOT / "reports" / "benchmark-5000.pdf"


def seed_benchmark_rows(count: int) -> float:
    random.seed(42)

    initialize_database()

    started = time.perf_counter()

    now = datetime.now(timezone.utc)

    rows = []

    for _ in range(count):
        seconds_back = random.randint(
            0,
            30 * 24 * 60 * 60,
        )

        created_at = (
            now
            - timedelta(seconds=seconds_back)
        ).isoformat()

        rows.append(
            (
                random.choice(CUSTOMERS),
                random.choice(PRODUCTS),
                round(random.uniform(5, 200), 2),
                created_at,
            )
        )

    with get_connection() as connection:
        connection.execute(
            "DELETE FROM orders"
        )

        connection.execute(
            "DELETE FROM sqlite_sequence WHERE name='orders'"
        )

        connection.executemany(
            """
            INSERT INTO orders (
                customer,
                product,
                amount,
                created_at
            )
            VALUES (?, ?, ?, ?)
            """,
            rows,
        )

        connection.commit()

    return time.perf_counter() - started


def count_orders() -> int:
    with get_connection() as connection:
        return connection.execute(
            "SELECT COUNT(*) FROM orders"
        ).fetchone()[0]


def main() -> None:
    print("=== SEED 5000 ROWS ===")

    seed_time = seed_benchmark_rows(
        BENCHMARK_COUNT
    )

    count = count_orders()

    print("Rows:", count)
    print(
        "Seed time:",
        f"{seed_time:.3f}s",
    )

    assert count == BENCHMARK_COUNT

    print()
    print("=== AGGREGATION BENCHMARK ===")

    started = time.perf_counter()

    report = get_report_data(
        days=30
    )

    aggregation_time = (
        time.perf_counter()
        - started
    )

    print(
        "Aggregation time:",
        f"{aggregation_time:.4f}s",
    )

    print(
        "Total orders:",
        report["summary"]["total_orders"],
    )

    print(
        "Total revenue:",
        f"${report['summary']['total_revenue']:.2f}",
    )

    assert (
        report["summary"]["total_orders"]
        == BENCHMARK_COUNT
    )

    print()
    print("=== PDF BENCHMARK ===")

    started = time.perf_counter()

    render_report_pdf(
        report,
        BENCHMARK_PDF,
    )

    pdf_time = (
        time.perf_counter()
        - started
    )

    size = BENCHMARK_PDF.stat().st_size

    print(
        "PDF generation time:",
        f"{pdf_time:.3f}s",
    )

    print(
        "PDF size:",
        f"{size / 1024:.1f} KB",
    )

    assert size > 20_000

    total = (
        seed_time
        + aggregation_time
        + pdf_time
    )

    print()
    print("=== BENCHMARK SUMMARY ===")

    print(
        f"Rows: {BENCHMARK_COUNT}"
    )

    print(
        f"Seed: {seed_time:.3f}s"
    )

    print(
        f"Aggregation: {aggregation_time:.4f}s"
    )

    print(
        f"PDF: {pdf_time:.3f}s"
    )

    print(
        f"Total measured: {total:.3f}s"
    )

    print()
    print("=== RESTORE NORMAL DATASET ===")

    seed_orders(
        count=200
    )

    restored = count_orders()

    print(
        "Restored rows:",
        restored,
    )

    assert restored == 200

    print()
    print("PASS: 5000-row benchmark completed")
    print("PASS: dataset restored to 200 rows")


if __name__ == "__main__":
    main()
