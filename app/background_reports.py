import hashlib
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.db import get_connection
from app.pdf_renderer import REPORTS_DIR, render_report_pdf
from app.report_data import get_report_data


def create_pending_report(
    days: int = 30,
) -> dict[str, Any]:
    report_id = str(uuid.uuid4())

    now = datetime.now(timezone.utc)

    filename = (
        f"sales-report-"
        f"{now.strftime('%Y-%m-%d')}-"
        f"{report_id[:8]}.pdf"
    )

    relative_path = (
        Path("reports")
        / filename
    )

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO reports (
                id,
                path,
                created_at,
                status,
                days
            )
            VALUES (?, ?, ?, 'pending', ?)
            """,
            (
                report_id,
                str(relative_path),
                now.isoformat(),
                days,
            ),
        )

        connection.commit()

    return {
        "id": report_id,
        "status": "pending",
        "days": days,
        "file": (
            f"/reports/"
            f"{report_id}"
            f"/file"
        ),
    }


def mark_started(
    report_id: str,
) -> str:
    started_at = datetime.now(
        timezone.utc
    ).isoformat()

    with get_connection() as connection:
        connection.execute(
            """
            UPDATE reports
            SET
                status = 'processing',
                started_at = ?,
                error = NULL
            WHERE id = ?
            """,
            (
                started_at,
                report_id,
            ),
        )

        connection.commit()

    return started_at


def load_report_data(
    days: int,
) -> dict[str, Any]:
    return get_report_data(
        days=days
    )


def render_background_pdf(
    report_id: str,
    report_data: dict[str, Any],
) -> dict[str, Any]:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT path
            FROM reports
            WHERE id = ?
            """,
            (report_id,),
        ).fetchone()

    if row is None:
        raise RuntimeError(
            f"Report {report_id} not found"
        )

    output_path = (
        REPORTS_DIR.parent
        / row["path"]
    )

    started = time.perf_counter()

    render_report_pdf(
        report_data,
        output_path,
    )

    duration_ms = round(
        (
            time.perf_counter()
            - started
        )
        * 1000,
        2,
    )

    digest = hashlib.sha256(
        output_path.read_bytes()
    ).hexdigest()

    return {
        "path": str(output_path),
        "duration_ms": duration_ms,
        "file_size_bytes":
            output_path.stat().st_size,
        "sha256": digest,
    }


def mark_done(
    report_id: str,
    artifact: dict[str, Any],
) -> dict[str, Any]:
    finished_at = datetime.now(
        timezone.utc
    ).isoformat()

    with get_connection() as connection:
        connection.execute(
            """
            UPDATE reports
            SET
                status = 'done',
                generation_ms = ?,
                file_size_bytes = ?,
                sha256 = ?,
                finished_at = ?,
                error = NULL
            WHERE id = ?
            """,
            (
                artifact["duration_ms"],
                artifact["file_size_bytes"],
                artifact["sha256"],
                finished_at,
                report_id,
            ),
        )

        connection.commit()

    return {
        "id": report_id,
        "status": "done",
        "finished_at": finished_at,
    }


def mark_failed(
    report_id: str,
    error: str,
) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE reports
            SET
                status = 'failed',
                error = ?,
                finished_at = ?
            WHERE id = ?
            """,
            (
                error[:2000],
                datetime.now(
                    timezone.utc
                ).isoformat(),
                report_id,
            ),
        )

        connection.commit()
