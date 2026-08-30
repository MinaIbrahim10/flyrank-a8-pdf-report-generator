from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.responses import FileResponse

from .db import connection, initialize_database, reports_dir
from .pdf import generate_pdf
from .report_data import get_report_data

app = FastAPI(title="Shop PDF Report Generator", version="1.0.0")


@app.on_event("startup")
def startup() -> None:
    initialize_database()


def report_response(row: sqlite3.Row, request: Request) -> dict:
    return {
        "id": row["id"],
        "filename": row["filename"],
        "created_at": row["created_at"],
        "order_count": row["order_count"],
        "total_revenue": row["total_revenue"],
        "file_url": str(request.url_for("download_report", report_id=row["id"])),
    }


@app.post("/reports", status_code=201)
def create_report(request: Request, response: Response, force: bool = Query(False)):
    now = datetime.now(timezone.utc)
    report_date = None if force else now.date().isoformat()
    created = False
    with connection() as conn:
        try:
            cursor = conn.execute(
                "INSERT INTO reports (created_at, report_date) VALUES (?, ?)",
                (now.isoformat(), report_date),
            )
            report_id = cursor.lastrowid
            created = True
        except sqlite3.IntegrityError:
            row = conn.execute(
                "SELECT * FROM reports WHERE report_date = ? AND status = ?", (report_date, "ready")
            ).fetchone()
            if row is None:
                raise HTTPException(status_code=409, detail="Today's report is currently being generated")
            response.status_code = 200
            return report_response(row, request)

    filename = f"shop-orders-{now:%Y-%m-%d}-{report_id}.pdf"
    destination = reports_dir() / filename
    try:
        with connection() as conn:
            data = get_report_data(conn)
        generate_pdf({**data, "generated_at": now.strftime("%B %d, %Y at %H:%M UTC")}, destination)
        with connection() as conn:
            conn.execute(
                """UPDATE reports SET filename = ?, status = 'ready', order_count = ?, total_revenue = ?
                   WHERE id = ?""",
                (filename, data["total_order_count"], data["total_revenue"], report_id),
            )
            row = conn.execute("SELECT * FROM reports WHERE id = ?", (report_id,)).fetchone()
    except Exception:
        destination.unlink(missing_ok=True)
        with connection() as conn:
            conn.execute("DELETE FROM reports WHERE id = ? AND status = 'generating'", (report_id,))
        raise
    response = report_response(row, request)
    return response


@app.get("/reports/{report_id}")
def get_report(report_id: int, request: Request):
    with connection() as conn:
        row = conn.execute(
            "SELECT * FROM reports WHERE id = ? AND status = ?", (report_id, "ready")
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return report_response(row, request)


@app.get("/reports/{report_id}/file", name="download_report")
def download_report(report_id: int):
    with connection() as conn:
        row = conn.execute(
            "SELECT filename FROM reports WHERE id = ? AND status = ?", (report_id, "ready")
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Report not found")
    path = reports_dir() / row["filename"]
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Report file not found")
    return FileResponse(path, media_type="application/pdf", filename=row["filename"])
