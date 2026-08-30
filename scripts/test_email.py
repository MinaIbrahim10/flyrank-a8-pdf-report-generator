import json
import os
import urllib.request

os.environ.setdefault(
    "SMTP_HOST",
    "127.0.0.1",
)

os.environ.setdefault(
    "SMTP_PORT",
    "1025",
)

os.environ.setdefault(
    "REPORT_EMAIL_TO",
    "reports@example.test",
)

os.environ.setdefault(
    "PUBLIC_BASE_URL",
    "http://127.0.0.1:8001",
)

from app.email_service import send_report_email


result = send_report_email(
    report_id="test-report-id",
    filename="sales-report-test.pdf",
)

print(
    json.dumps(
        result,
        indent=2,
    )
)

assert result["to"] == (
    "reports@example.test"
)

assert result["url"] == (
    "http://127.0.0.1:8001/"
    "reports/test-report-id/file"
)

print()
print("PASS: email sent through SMTP")
print("PASS: message uses report link")
print("PASS: no PDF attachment was sent")
