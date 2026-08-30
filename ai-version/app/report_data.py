import sqlite3
from datetime import date, timedelta


def build_report_data(connection: sqlite3.Connection) -> dict:
    summary = connection.execute(
        "SELECT COUNT(*) AS total_orders, COALESCE(SUM(amount), 0) AS total_revenue FROM orders"
    ).fetchone()
    top_products = connection.execute(
        """
        SELECT product, COUNT(*) AS order_count, ROUND(SUM(amount), 2) AS revenue
        FROM orders
        GROUP BY product
        ORDER BY revenue DESC, product ASC
        LIMIT 5
        """
    ).fetchall()

    start = (date.today() - timedelta(days=6)).isoformat()
    orders_per_day = connection.execute(
        """
        WITH RECURSIVE days(day) AS (
            SELECT date(?)
            UNION ALL
            SELECT date(day, '+1 day') FROM days WHERE day < date('now', 'localtime')
        )
        SELECT days.day, COUNT(orders.id) AS order_count
        FROM days
        LEFT JOIN orders ON date(orders.created_at) = days.day
        GROUP BY days.day
        ORDER BY days.day
        """,
        (start,),
    ).fetchall()
    orders = connection.execute(
        "SELECT id, customer, product, amount, created_at FROM orders ORDER BY created_at DESC, id DESC"
    ).fetchall()

    return {
        "total_orders": summary["total_orders"],
        "total_revenue": summary["total_revenue"],
        "top_products": [dict(row) for row in top_products],
        "orders_per_day": [dict(row) for row in orders_per_day],
        "orders": [dict(row) for row in orders],
    }

