import sqlite3
from datetime import datetime

from app.database import initialize
from app.pdf import render_html
from app.report_data import build_report_data


def test_schema_and_report_queries(tmp_path):
    path = tmp_path / "test.db"
    initialize(path)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.executemany(
        "INSERT INTO orders (customer, product, amount, created_at) VALUES (?, ?, ?, ?)",
        [("Ada", "Mouse", 20, datetime.now().isoformat()), ("Lin", "Mouse", 30, datetime.now().isoformat()), ("Sam", "Hub", 40, datetime.now().isoformat())],
    )
    data = build_report_data(connection)
    assert data["total_orders"] == 3
    assert data["total_revenue"] == 90
    assert data["top_products"][0]["product"] == "Mouse"
    assert len(data["orders_per_day"]) == 7


def test_html_has_print_table_rules():
    data = {"total_orders": 0, "total_revenue": 0, "top_products": [], "orders_per_day": [], "orders": []}
    html = render_html(data, datetime.now().astimezone())
    assert "table-header-group" in html
    assert "break-inside: avoid" in html
    assert "Shop Orders Report" in html

