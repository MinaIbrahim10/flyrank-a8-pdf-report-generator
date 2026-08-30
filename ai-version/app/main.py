import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse

from .config import DATABASE_PATH, REPORTS_DIR
from .database import database, initialize
from .pdf import create_pdf, render_html
from .report_data import build_report_data

report_lock = asyncio.Lock()


def report_response(row, request: Request) -> dict:
    return {
        "id": row["id"],
        "report_date": row["report_date"],
        "generated_at": row["generated_at"],
        "total_orders": row["total_orders"],
        "total_revenue": row["total_revenue"],
        "file_url": str(request.url_for("get_report_file", report_id=row["id"])),
    }


def find_report(report_id: int):
    with database(DATABASE_PATH) as connection:
        return connection.execute("SELECT * FROM reports WHERE id = ?", (report_id,)).fetchone()


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize(DATABASE_PATH)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(title="Shop PDF Report Generator", lifespan=lifespan)


@app.post("/reports", status_code=201)
async def generate_report(request: Request, force: bool = Query(False)):
    async with report_lock:
        now = datetime.now().astimezone()
        today = now.date().isoformat()
        with database(DATABASE_PATH) as connection:
            if not force:
                existing = connection.execute(
                    "SELECT * FROM reports WHERE report_date = ? ORDER BY id DESC LIMIT 1", (today,)
                ).fetchone()
                if existing:
                    return report_response(existing, request)
            data = build_report_data(connection)

        stamp = now.strftime("%Y%m%d-%H%M%S-%f")
        file_name = f"shop-report-{stamp}.pdf"
        destination = REPORTS_DIR / file_name
        html = render_html(data, now)
        await create_pdf(html, destination)

        try:
            with database(DATABASE_PATH) as connection:
                cursor = connection.execute(
                    """
                    INSERT INTO reports
                        (report_date, generated_at, file_name, total_orders, total_revenue)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (today, now.isoformat(), file_name, data["total_orders"], data["total_revenue"]),
                )
                row = connection.execute("SELECT * FROM reports WHERE id = ?", (cursor.lastrowid,)).fetchone()
        except Exception:
            destination.unlink(missing_ok=True)
            raise
        return report_response(row, request)


@app.get("/reports/{report_id}")
async def get_report(report_id: int, request: Request):
    row = find_report(report_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return report_response(row, request)


@app.get("/reports/{report_id}/file", name="get_report_file")
async def get_report_file(report_id: int):
    row = find_report(report_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Report not found")
    path = REPORTS_DIR / Path(row["file_name"]).name
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Report file not found")
    return FileResponse(path, media_type="application/pdf", filename=row["file_name"])

