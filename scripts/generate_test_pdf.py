import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(
    0,
    str(ROOT),
)

from app.pdf_renderer import render_report_pdf
from app.report_data import get_report_data


def main() -> None:
    report_data = get_report_data(
        days=30
    )

    output = (
        ROOT
        / "reports"
        / "test.pdf"
    )

    render_report_pdf(
        report_data,
        output,
    )

    if not output.exists():
        raise RuntimeError(
            "PDF was not created"
        )

    size = output.stat().st_size

    if size < 20_000:
        raise RuntimeError(
            f"PDF looks too small: {size} bytes"
        )

    print(
        f"PASS: generated {output}"
    )

    print(
        f"PDF size: {size / 1024:.1f} KB"
    )


if __name__ == "__main__":
    main()
