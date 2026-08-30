from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Any


def get_report_data(conn: sqlite3.Connection) -> dict[str, Any]:
    today = datetime.now(timezone.utc).date()
    start = today - timedelta(days=6)

    total_order_count = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    total_revenue = conn.execute("SELECT COALESCE(SUM(amount), 0) FROM orders").fetchone()[0]
    top_products = conn.execute(
        """
        SELECT product, COUNT(*) AS order_count, ROUND(SUM(amount), 2) AS revenue
        FROM orders GROUP BY product ORDER BY revenue DESC, product ASC LIMIT 5
        """
    ).fetchall()
    daily_rows = conn.execute(
        """
        SELECT DATE(created_at) AS day, COUNT(*) AS order_count,
               ROUND(SUM(amount), 2) AS revenue
        FROM orders
        WHERE DATE(created_at) BETWEEN ? AND ?
        GROUP BY DATE(created_at) ORDER BY day ASC
        """,
        (start.isoformat(), today.isoformat()),
    ).fetchall()
    by_day = {row["day"]: dict(row) for row in daily_rows}
    daily_summary = []
    for offset in range(7):
        day = (start + timedelta(days=offset)).isoformat()
        daily_summary.append(by_day.get(day, {"day": day, "order_count": 0, "revenue": 0.0}))
    orders = conn.execute(
        "SELECT id, customer, product, amount, created_at FROM orders ORDER BY created_at DESC, id DESC"
    ).fetchall()
    return {
        "total_order_count": total_order_count,
        "total_revenue": round(float(total_revenue), 2),
        "top_products": [dict(row) for row in top_products],
        "daily_summary": daily_summary,
        "orders": [dict(row) for row in orders],
    }

