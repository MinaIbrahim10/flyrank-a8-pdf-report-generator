import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.db import get_connection, initialize_database


CUSTOMERS = [
    "Alice Johnson",
    "Daniel Weber",
    "Emma Schneider",
    "Lucas Martin",
    "Sophia Rossi",
    "Noah Schmidt",
    "Olivia Brown",
    "Elias Fischer",
    "Mia Wilson",
    "Adam Haddad",
    "Lina Khalil",
    "Sara Ibrahim",
]

PRODUCTS = [
    "AI Starter Plan",
    "Cloud Storage",
    "Analytics Pro",
    "Team Workspace",
    "Support Plus",
    "Automation Pack",
]


def random_order_date() -> str:
    now = datetime.now(timezone.utc)

    seconds_back = random.randint(
        0,
        30 * 24 * 60 * 60,
    )

    value = now - timedelta(seconds=seconds_back)

    return value.isoformat()


def seed_orders(count: int = 200) -> None:
    random.seed(42)

    initialize_database()

    with get_connection() as connection:
        # Deliberately reset the table so the seed is safe to run repeatedly.
        connection.execute("DELETE FROM orders")
        connection.execute(
            "DELETE FROM sqlite_sequence WHERE name = 'orders'"
        )

        rows = []

        for _ in range(count):
            rows.append(
                (
                    random.choice(CUSTOMERS),
                    random.choice(PRODUCTS),
                    round(random.uniform(5, 200), 2),
                    random_order_date(),
                )
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


def main() -> None:
    seed_orders()

    with get_connection() as connection:
        count = connection.execute(
            "SELECT COUNT(*) AS count FROM orders"
        ).fetchone()["count"]

        min_amount, max_amount = connection.execute(
            """
            SELECT
                MIN(amount),
                MAX(amount)
            FROM orders
            """
        ).fetchone()

        first_date, last_date = connection.execute(
            """
            SELECT
                MIN(created_at),
                MAX(created_at)
            FROM orders
            """
        ).fetchone()

    print(f"Seeded orders: {count}")
    print(f"Amount range: {min_amount:.2f} -> {max_amount:.2f}")
    print(f"Date range: {first_date} -> {last_date}")


if __name__ == "__main__":
    main()
