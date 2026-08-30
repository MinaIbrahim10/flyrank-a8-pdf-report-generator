from contextlib import asynccontextmanager

import inngest
import inngest.fast_api

from fastapi import (
    FastAPI,
    HTTPException,
    Query,
    Response,
    status,
)
from fastapi.responses import (
    FileResponse,
)

from app.db import initialize_database
from app.background_reports import create_pending_report
from app.inngest_jobs import (
    functions as inngest_functions,
    inngest_client,
)
from app.report_service import (
    generate_report,
    get_report_path,
    get_report_record,
    list_reports,
    generate_report_csv,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title="PDF Report Generator",
    description=(
        "FlyRank Backend Track A8 — "
        "SQL to PDF reporting pipeline"
    ),
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service":
            "pdf-report-generator",
    }


@app.post("/reports")
def create_report(
    response: Response,
    days: int = Query(
        default=30,
        ge=1,
        le=365,
        description=(
            "Number of days to include "
            "in the report."
        ),
    ),
    force: bool = Query(
        default=False,
        description=(
            "Generate a new report even "
            "if today's report exists."
        ),
    ),
):
    try:
        report, created = generate_report(
            days=days,
            force=force,
        )

        response.status_code = (
            status.HTTP_201_CREATED
            if created
            else status.HTTP_200_OK
        )

        return report

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                "Report generation failed: "
                f"{error}"
            ),
        ) from error



@app.post(
    "/reports/background",
    status_code=status.HTTP_202_ACCEPTED,
)
async def create_background_report(
    days: int = Query(
        default=30,
        ge=1,
        le=365,
    ),
):
    report = create_pending_report(
        days=days
    )

    try:
        event_ids = await inngest_client.send(
            inngest.Event(
                name="report/generate",
                data={
                    "report_id": report["id"],
                    "days": days,
                },
            )
        )

    except Exception as error:
        from app.background_reports import mark_failed

        mark_failed(
            report["id"],
            f"Failed to enqueue job: {error}",
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to enqueue "
                "background report"
            ),
        ) from error

    report["event_ids"] = event_ids

    return report



@app.get("/reports")
def read_reports(
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    status_filter: str | None = Query(
        default=None,
        alias="status",
    ),
):
    allowed_statuses = {
        "pending",
        "processing",
        "done",
        "failed",
    }

    if (
        status_filter is not None
        and status_filter not in allowed_statuses
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid status filter. "
                "Use pending, processing, done, or failed."
            ),
        )

    reports = list_reports(
        limit=limit,
        status_filter=status_filter,
    )

    return {
        "count": len(reports),
        "reports": reports,
    }


@app.get("/reports/{report_id}")
def read_report(
    report_id: str,
):
    report = get_report_record(
        report_id
    )

    if report is None:
        raise HTTPException(
            status_code=404,
            detail="Report not found",
        )

    return report



@app.get(
    "/reports/{report_id}/csv"
)
def download_report_csv(
    report_id: str,
):
    path = generate_report_csv(
        report_id
    )

    if path is None:
        raise HTTPException(
            status_code=404,
            detail="Report not found",
        )

    return FileResponse(
        path=path,
        media_type="text/csv",
        filename=path.name,
    )


@app.get(
    "/reports/{report_id}/file"
)
def download_report(
    report_id: str,
):
    path = get_report_path(
        report_id
    )

    if path is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Report file not found"
            ),
        )

    return FileResponse(
        path=path,
        media_type="application/pdf",
        filename=path.name,
    )


inngest.fast_api.serve(
    app,
    inngest_client,
    inngest_functions,
)
