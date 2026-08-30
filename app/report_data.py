from datetime import datetime, timedelta, timezone
from typing import Any

from app.db import get_connection


def get_report_data(days: int = 30) -> dict[str, Any]:
    if days < 1 or days > 365:
        raise ValueError("days must be between 1 and 365")

    now = datetime.now(timezone.utc)
    period_start = now - timedelta(days=days)
    last_7_days = now - timedelta(days=7)

    with get_connection() as connection:
        total_orders = connection.execute(
            """
            SELECT COUNT(*) AS total_orders
            FROM orders
            WHERE created_at >= ?
            """,
            (period_start.isoformat(),),
        ).fetchone()["total_orders"]

        revenue_row = connection.execute(
            """
            SELECT
                COALESCE(SUM(amount), 0) AS total_revenue,
                COALESCE(AVG(amount), 0) AS average_order_value,
                COUNT(DISTINCT customer) AS unique_customers
            FROM orders
            WHERE created_at >= ?
            """,
            (period_start.isoformat(),),
        ).fetchone()

        top_products = connection.execute(
            """
            SELECT
                product,
                COUNT(*) AS order_count,
                ROUND(SUM(amount), 2) AS revenue,
                ROUND(AVG(amount), 2) AS average_order_value
            FROM orders
            WHERE created_at >= ?
            GROUP BY product
            ORDER BY revenue DESC
            LIMIT 5
            """,
            (period_start.isoformat(),),
        ).fetchall()

        orders_per_day = connection.execute(
            """
            SELECT
                DATE(created_at) AS day,
                COUNT(*) AS orders,
                ROUND(SUM(amount), 2) AS revenue
            FROM orders
            WHERE created_at >= ?
            GROUP BY DATE(created_at)
            ORDER BY day ASC
            """,
            (last_7_days.isoformat(),),
        ).fetchall()

        top_by_units = connection.execute(
            """
            SELECT
                product,
                COUNT(*) AS units
            FROM orders
            WHERE created_at >= ?
            GROUP BY product
            ORDER BY units DESC, product ASC
            LIMIT 1
            """,
            (period_start.isoformat(),),
        ).fetchone()

        all_orders = connection.execute(
            """
            SELECT
                id,
                customer,
                product,
                ROUND(amount, 2) AS amount,
                created_at
            FROM orders
            WHERE created_at >= ?
            ORDER BY created_at DESC
            """,
            (period_start.isoformat(),),
        ).fetchall()

    return {
        "generated_at": now.isoformat(),
        "period_days": days,
        "period_start": period_start.isoformat(),
        "summary": {
            "total_orders": total_orders,
            "total_revenue": round(
                float(revenue_row["total_revenue"]),
                2,
            ),
            "average_order_value": round(
                float(revenue_row["average_order_value"]),
                2,
            ),
            "unique_customers": revenue_row["unique_customers"],
            "top_product_by_units": (
                {
                    "product": top_by_units["product"],
                    "units": top_by_units["units"],
                }
                if top_by_units
                else None
            ),
        },
        "top_products": [
            dict(row)
            for row in top_products
        ],
        "orders_per_day": [
            dict(row)
            for row in orders_per_day
        ],
        "orders": [
            dict(row)
            for row in all_orders
        ],
    }
