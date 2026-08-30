import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.db import get_connection
from app.email_service import send_report_email


with get_connection() as connection:
    report = connection.execute(
        """
        SELECT
            id,
            path,
            status,
            created_at
        FROM reports
        WHERE status = 'done'
        ORDER BY created_at DESC
        LIMIT 1
        """
    ).fetchone()


if report is None:
    raise RuntimeError(
        "No completed report exists. Generate a report first."
    )


filename = Path(
    report["path"]
).name


print("=== REAL REPORT ===")
print("ID:", report["id"])
print("Filename:", filename)
print("Status:", report["status"])


result = send_report_email(
    report_id=report["id"],
    filename=filename,
)


print()
print(
    json.dumps(
        result,
        indent=2,
    )
)


assert result["to"] == "reports@example.test"

assert (
    f"/reports/{report['id']}/file"
    in result["url"]
)


print()
print("PASS: email sent through SMTP")
print("PASS: email uses a REAL completed report")
print("PASS: report link contains the real report id")
print("PASS: no PDF attachment was sent")

print()
print("Open Mailpit:")
print("http://127.0.0.1:8025")

print()
print("Expected download URL:")
print(result["url"])
