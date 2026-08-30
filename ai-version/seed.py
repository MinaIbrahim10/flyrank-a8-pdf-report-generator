import random
from datetime import datetime, timedelta

from app.config import DATABASE_PATH
from app.database import database, initialize

CUSTOMERS = ["Ava Martin", "Noah Wilson", "Mia Davis", "Liam Brown", "Emma Clark", "Leo Taylor"]
PRODUCTS = {
    "Mechanical Keyboard": (79, 149),
    "Wireless Mouse": (25, 69),
    "USB-C Hub": (35, 89),
    "Laptop Stand": (29, 75),
    "Webcam": (45, 129),
    "Desk Lamp": (30, 95),
    "Headphones": (55, 199),
    "Monitor Arm": (69, 159),
}


def seed(count: int = 200) -> None:
    initialize(DATABASE_PATH)
    rng = random.Random(20250831)
    now = datetime.now().replace(microsecond=0)
    rows = []
    for _ in range(count):
        product = rng.choice(list(PRODUCTS))
        low, high = PRODUCTS[product]
        created_at = now - timedelta(days=rng.randrange(30), seconds=rng.randrange(86400))
        rows.append((rng.choice(CUSTOMERS), product, round(rng.uniform(low, high), 2), created_at.isoformat()))

    with database(DATABASE_PATH) as connection:
        connection.execute("DELETE FROM orders")
        connection.executemany(
            "INSERT INTO orders (customer, product, amount, created_at) VALUES (?, ?, ?, ?)", rows
        )
    print(f"Seeded {count} orders in {DATABASE_PATH}")


if __name__ == "__main__":
    seed()

