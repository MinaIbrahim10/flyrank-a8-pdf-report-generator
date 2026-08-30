from datetime import datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape
from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parent.parent

TEMPLATES_DIR = ROOT / "templates"

REPORTS_DIR = ROOT / "reports"


environment = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=select_autoescape(["html", "xml"]),
)


def build_report_html(
    report_data: dict[str, Any],
) -> str:
    template = environment.get_template(
        "report.html"
    )

    generated = datetime.fromisoformat(
        report_data["generated_at"]
    )

    return template.render(
        report=report_data,
        generated_display=generated.strftime(
            "%Y-%m-%d %H:%M UTC"
        ),
    )


def render_report_pdf(
    report_data: dict[str, Any],
    output_path: Path,
) -> Path:
    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    html = build_report_html(
        report_data
    )

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=True,
        )

        try:
            page = browser.new_page()

            page.set_content(
                html,
                wait_until="networkidle",
            )

            page.emulate_media(
                media="print"
            )

            page.pdf(
                path=str(output_path),
                format="A4",
                print_background=True,
                margin={
                    "top": "12mm",
                    "right": "10mm",
                    "bottom": "18mm",
                    "left": "10mm",
                },
                display_header_footer=True,
                header_template="<div></div>",
                footer_template="""
                    <div style="
                        width:100%;
                        font-size:8px;
                        color:#9ca3af;
                        padding:0 14mm;
                        display:flex;
                        justify-content:space-between;
                        font-family:Arial,Helvetica,sans-serif;
                    ">
                        <span>
                            Decision Analytics
                        </span>

                        <span>
                            Page
                            <span class="pageNumber"></span>
                            of
                            <span class="totalPages"></span>
                        </span>
                    </div>
                """,
            )

        finally:
            browser.close()

    return output_path
