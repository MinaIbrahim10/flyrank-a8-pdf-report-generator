from fastapi import (
    FastAPI,
    HTTPException,
    Query,
    status,
)
from fastapi.responses import (
    FileResponse,
)

from app.db import initialize_database
from app.report_service import (
    generate_report,
    get_report_path,
    get_report_record,
)


app = FastAPI(
    title="PDF Report Generator",
    description=(
        "FlyRank Backend Track A8 — "
        "SQL to PDF reporting pipeline"
    ),
    version="1.0.0",
)


@app.on_event("startup")
def startup() -> None:
    initialize_database()


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service":
            "pdf-report-generator",
    }


@app.post(
    "/reports",
    status_code=status.HTTP_201_CREATED,
)
def create_report(
    days: int = Query(
        default=30,
        ge=1,
        le=365,
        description=(
            "Number of days to include "
            "in the report."
        ),
    ),
):
    try:
        return generate_report(
            days=days
        )
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                "Report generation failed: "
                f"{error}"
            ),
        ) from error


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
        media_type=(
            "application/pdf"
        ),
        filename=path.name,
    )
