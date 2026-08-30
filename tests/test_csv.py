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


def test_csv_export():
    seed_orders(count=200)

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id
            FROM reports
            WHERE status = 'done'
            ORDER BY created_at DESC
            LIMIT 1
            """
        ).fetchone()

    if row is None:
        response = client.post(
            "/reports?days=30&force=true"
        )

        assert response.status_code == 201

        report_id = response.json()["id"]

    else:
        report_id = row["id"]

    response = client.get(
        f"/reports/{report_id}/csv"
    )

    assert response.status_code == 200

    assert (
        response.headers[
            "content-type"
        ].startswith("text/csv")
    )

    text = response.text

    assert (
        "id,customer,product,amount,created_at"
        in text
    )

    rows = [
        line
        for line in text.splitlines()
        if line.strip()
    ]

    assert len(rows) == 201


def test_unknown_csv_returns_404():
    response = client.get(
        "/reports/not-real/csv"
    )

    assert response.status_code == 404
