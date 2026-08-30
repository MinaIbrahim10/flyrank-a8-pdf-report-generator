from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone

from .db import connection, initialize_database

PRODUCTS = (
    ("Wireless Headphones", 89.99),
    ("Mechanical Keyboard", 119.00),
    ("Ergonomic Mouse", 54.50),
    ("USB-C Dock", 139.95),
    ("4K Webcam", 99.00),
    ("Laptop Stand", 47.75),
)
FIRST_NAMES = ("Amelia", "Noah", "Olivia", "Liam", "Sophia", "Ethan", "Maya", "Lucas", "Nora", "Omar")
LAST_NAMES = ("Bennett", "Carter", "Haddad", "Kim", "Morgan", "Patel", "Reed", "Santos", "Taylor", "Wilson")


def build_orders() -> list[tuple[int, str, str, float, str]]:
    rng = random.Random(20260831)
    today = datetime.now(timezone.utc).date()
    rows = []
    for order_id in range(1, 201):
        product, base_price = PRODUCTS[rng.randrange(len(PRODUCTS))]
        quantity = rng.choices((1, 2, 3), weights=(72, 23, 5), k=1)[0]
        customer = f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"
        days_ago = rng.randrange(0, 30)
        hour, minute = rng.randrange(8, 22), rng.randrange(60)
        created = datetime.combine(today - timedelta(days=days_ago), datetime.min.time(), tzinfo=timezone.utc)
        created += timedelta(hours=hour, minutes=minute)
        rows.append((order_id, customer, product, round(base_price * quantity, 2), created.isoformat()))
    return rows


def seed() -> None:
    initialize_database()
    with connection() as conn:
        conn.execute("DELETE FROM orders")
        conn.executemany(
            "INSERT INTO orders (id, customer, product, amount, created_at) VALUES (?, ?, ?, ?, ?)",
            build_orders(),
        )
    print("Seeded exactly 200 orders.")


if __name__ == "__main__":
    seed()

