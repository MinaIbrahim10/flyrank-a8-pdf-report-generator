import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

os.environ.setdefault(
    "INNGEST_DEV",
    "http://127.0.0.1:8288",
)

from app.db import get_connection
from app.report_data import get_report_data
from scripts.seed import seed_orders


@pytest.fixture(autouse=True)
def restore_seed():
    seed_orders(count=200)

    yield

    seed_orders(count=200)


def test_seed_is_idempotent():
    seed_orders(count=200)
    seed_orders(count=200)

    with get_connection() as connection:
        count = connection.execute(
            "SELECT COUNT(*) FROM orders"
        ).fetchone()[0]

    assert count == 200


def test_report_aggregations():
    report = get_report_data(days=30)

    assert (
        report["summary"]["total_orders"]
        == 200
    )

    assert (
        report["summary"]["total_revenue"]
        > 0
    )

    assert len(
        report["top_products"]
    ) == 5

    assert len(
        report["orders_per_day"]
    ) <= 7

    assert len(
        report["orders"]
    ) == 200
