import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

os.environ.setdefault(
    "INNGEST_DEV",
    "http://127.0.0.1:8288",
)

from fastapi.testclient import TestClient

from app.main import app
from app.db import get_connection
from scripts.seed import seed_orders


client = TestClient(app)


def reset_reports():
    with get_connection() as connection:
        connection.execute(
            "DELETE FROM reports"
        )

        connection.commit()


def test_health():
    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    assert response.json()["status"] == "ok"


def test_unknown_report_returns_404():
    response = client.get(
        "/reports/not-real"
    )

    assert response.status_code == 404


def test_report_list_endpoint():
    response = client.get(
        "/reports?limit=5"
    )

    assert response.status_code == 200

    body = response.json()

    assert "count" in body
    assert "reports" in body


def test_invalid_report_status_filter():
    response = client.get(
        "/reports?status=banana"
    )

    assert response.status_code == 400


def test_sync_report_idempotency():
    seed_orders(count=200)
    reset_reports()

    first = client.post(
        "/reports?days=30"
    )

    assert first.status_code == 201

    second = client.post(
        "/reports?days=30"
    )

    assert second.status_code == 200

    first_body = first.json()
    second_body = second.json()

    assert (
        first_body["id"]
        == second_body["id"]
    )

    forced = client.post(
        "/reports?days=30&force=true"
    )

    assert forced.status_code == 201

    assert (
        forced.json()["id"]
        != second_body["id"]
    )
