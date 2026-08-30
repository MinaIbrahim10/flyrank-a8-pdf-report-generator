import os
import smtplib
from email.message import EmailMessage


SMTP_HOST = os.getenv(
    "SMTP_HOST",
    "127.0.0.1",
)

SMTP_PORT = int(
    os.getenv(
        "SMTP_PORT",
        "1025",
    )
)

REPORT_EMAIL_TO = os.getenv(
    "REPORT_EMAIL_TO",
    "reports@example.test",
)

REPORT_EMAIL_FROM = os.getenv(
    "REPORT_EMAIL_FROM",
    "reports@decision-analytics.local",
)

PUBLIC_BASE_URL = os.getenv(
    "PUBLIC_BASE_URL",
    "http://127.0.0.1:8001",
)


def send_report_email(
    report_id: str,
    filename: str,
) -> dict[str, str]:
    report_url = (
        f"{PUBLIC_BASE_URL}"
        f"/reports/"
        f"{report_id}"
        f"/file"
    )

    message = EmailMessage()

    message["Subject"] = (
        "Your sales report is ready"
    )

    message["From"] = (
        REPORT_EMAIL_FROM
    )

    message["To"] = (
        REPORT_EMAIL_TO
    )

    message.set_content(
        f"""Your sales report is ready.

Report:
{filename}

Download:
{report_url}

This message contains a link instead of attaching the PDF.
"""
    )

    with smtplib.SMTP(
        SMTP_HOST,
        SMTP_PORT,
        timeout=10,
    ) as smtp:
        smtp.send_message(
            message
        )

    return {
        "to": REPORT_EMAIL_TO,
        "url": report_url,
    }
