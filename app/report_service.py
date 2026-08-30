import hashlib
import sqlite3
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.db import get_connection, initialize_database
from app.pdf_renderer import REPORTS_DIR, render_report_pdf
from app.report_data import get_report_data


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def _daily_key(
    days: int,
    now: datetime,
) -> str:
    return (
        f"sales:"
        f"{now.date().isoformat()}:"
        f"days={days}"
    )


def _record_to_metadata(
    row,
) -> dict[str, Any]:
    path = (
        REPORTS_DIR.parent
        / row["path"]
    )

    metadata: dict[str, Any] = {
        "id": row["id"],
        "status": (
            "done"
            if path.exists()
            else "missing"
        ),
        "created_at": row["created_at"],
        "filename": path.name,
        "file": (
            f"/reports/"
            f"{row['id']}"
            f"/file"
        ),
    }

    if path.exists():
        metadata.update(
            {
                "file_size_bytes":
                    path.stat().st_size,
                "sha256":
                    _sha256_file(path),
            }
        )

    return metadata


def find_existing_report(
    idempotency_key: str,
) -> dict[str, Any] | None:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                id,
                path,
                created_at,
                idempotency_key
            FROM reports
            WHERE idempotency_key = ?
            LIMIT 1
            """,
            (idempotency_key,),
        ).fetchone()

    if row is None:
        return None

    return _record_to_metadata(row)


def generate_report(
    days: int = 30,
    force: bool = False,
) -> tuple[dict[str, Any], bool]:
    initialize_database()

    now = datetime.now(
        timezone.utc
    )

    idempotency_key = (
        None
        if force
        else _daily_key(
            days,
            now,
        )
    )

    if idempotency_key:
        existing = find_existing_report(
            idempotency_key
        )

        if existing is not None:
            existing["reused"] = True
            existing["days"] = days

            return existing, False

    report_id = str(
        uuid.uuid4()
    )

    filename = (
        f"sales-report-"
        f"{now.strftime('%Y-%m-%d')}-"
        f"{report_id[:8]}.pdf"
    )

    output_path = (
        REPORTS_DIR
        / filename
    )

    started = time.perf_counter()

    report_data = get_report_data(
        days=days
    )

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

    file_size = (
        output_path.stat().st_size
    )

    checksum = _sha256_file(
        output_path
    )

    created_at = now.isoformat()

    relative_path = str(
        output_path.relative_to(
            REPORTS_DIR.parent
        )
    )

    try:
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO reports (
                    id,
                    path,
                    created_at,
                    idempotency_key
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    report_id,
                    relative_path,
                    created_at,
                    idempotency_key,
                ),
            )

            connection.commit()

    except sqlite3.IntegrityError:
        if output_path.exists():
            output_path.unlink()

        if idempotency_key:
            existing = find_existing_report(
                idempotency_key
            )

            if existing is not None:
                existing["reused"] = True
                existing["days"] = days

                return existing, False

        raise

    return (
        {
            "id": report_id,
            "status": "done",
            "created_at": created_at,
            "days": days,
            "filename": filename,
            "path": relative_path,
            "file": (
                f"/reports/"
                f"{report_id}"
                f"/file"
            ),
            "generation_ms":
                duration_ms,
            "file_size_bytes":
                file_size,
            "sha256":
                checksum,
            "reused":
                False,
        },
        True,
    )


def get_report_record(
    report_id: str,
) -> dict[str, Any] | None:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                id,
                path,
                created_at,
                idempotency_key,
                status,
                error,
                days,
                generation_ms,
                file_size_bytes,
                sha256,
                started_at,
                finished_at
            FROM reports
            WHERE id = ?
            """,
            (report_id,),
        ).fetchone()

    if row is None:
        return None

    path = (
        REPORTS_DIR.parent
        / row["path"]
    )

    metadata: dict[str, Any] = {
        "id": row["id"],
        "status": row["status"] or "done",
        "created_at": row["created_at"],
        "days": row["days"],
        "filename": path.name,
        "file": (
            f"/reports/"
            f"{row['id']}"
            f"/file"
        ),
        "started_at": row["started_at"],
        "finished_at": row["finished_at"],
        "generation_ms": row["generation_ms"],
        "file_size_bytes": row["file_size_bytes"],
        "sha256": row["sha256"],
        "error": row["error"],
    }

    if (
        path.exists()
        and metadata["file_size_bytes"] is None
    ):
        metadata["file_size_bytes"] = (
            path.stat().st_size
        )

    if (
        path.exists()
        and metadata["sha256"] is None
    ):
        metadata["sha256"] = (
            _sha256_file(path)
        )

    return metadata

def get_report_path(
    report_id: str,
) -> Path | None:
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
        return None

    path = (
        REPORTS_DIR.parent
        / row["path"]
    ).resolve()

    reports_root = (
        REPORTS_DIR.resolve()
    )

    try:
        path.relative_to(
            reports_root
        )
    except ValueError:
        return None

    if not path.exists():
        return None

    return path
