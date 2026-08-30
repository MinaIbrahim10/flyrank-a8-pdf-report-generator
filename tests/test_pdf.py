import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

os.environ.setdefault(
    "INNGEST_DEV",
    "http://127.0.0.1:8288",
)

from app.pdf_renderer import render_report_pdf
from app.report_data import get_report_data
from scripts.seed import seed_orders


def test_real_pdf_generation(tmp_path):
    seed_orders(count=200)

    report = get_report_data(days=30)

    target = (
        tmp_path
        / "integration-report.pdf"
    )

    render_report_pdf(
        report,
        target,
    )

    assert target.exists()

    assert (
        target.stat().st_size
        > 20_000
    )

    assert (
        target.read_bytes()[:5]
        == b"%PDF-"
    )
