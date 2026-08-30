from __future__ import annotations

import importlib
import os
import sqlite3

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("REPORT_DB_PATH", str(tmp_path / "report.db"))
    monkeypatch.setenv("REPORTS_DIR", str(tmp_path / "reports"))
    from app import db, main
    importlib.reload(db)
    importlib.reload(main)
    from app.seed import seed
    seed()
    base_url = os.getenv("TEST_API_BASE_URL", "http://testserver.local")
    with TestClient(main.app, base_url=base_url) as test_client:
        yield test_client


def test_seed_stays_exactly_200_after_two_runs(tmp_path, monkeypatch):
    database = tmp_path / "seed.db"
    monkeypatch.setenv("REPORT_DB_PATH", str(database))
    from app.seed import seed
    seed()
    seed()
    with sqlite3.connect(database) as conn:
        assert conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0] == 200


def test_report_lifecycle_idempotency_and_real_pdf(client):
    created = client.post("/reports")
    assert created.status_code == 201
    first = created.json()

    duplicate = client.post("/reports")
    assert duplicate.status_code == 200
    assert duplicate.json()["id"] == first["id"]

    forced = client.post("/reports?force=true")
    assert forced.status_code == 201
    assert forced.json()["id"] != first["id"]

    metadata = client.get(f"/reports/{first['id']}")
    assert metadata.status_code == 200
    assert metadata.json()["order_count"] == 200
    assert metadata.json()["file_url"].startswith(str(client.base_url))

    download = client.get(f"/reports/{first['id']}/file")
    assert download.status_code == 200
    assert download.headers["content-type"] == "application/pdf"
    assert download.content.startswith(b"%PDF-")
    assert len(download.content) > 10_000


@pytest.mark.parametrize("path", ["/reports/999999", "/reports/999999/file"])
def test_unknown_report_is_404(client, path):
    assert client.get(path).status_code == 404
