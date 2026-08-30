from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from playwright.sync_api import sync_playwright

TEMPLATES = Path(__file__).parent / "templates"


def generate_pdf(context: dict, destination: Path) -> None:
    env = Environment(loader=FileSystemLoader(TEMPLATES), autoescape=select_autoescape(["html"]))
    env.filters["money"] = lambda value: f"${float(value):,.2f}"
    html = env.get_template("report.html").render(**context)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.set_content(html, wait_until="load")
            page.pdf(
                path=str(destination),
                format="A4",
                print_background=True,
                margin={"top": "15mm", "right": "12mm", "bottom": "18mm", "left": "12mm"},
                display_header_footer=True,
                header_template="<span></span>",
                footer_template=(
                    '<div style="font-size:9px;color:#64748b;width:100%;text-align:center">'
                    'Page <span class="pageNumber"></span> of <span class="totalPages"></span></div>'
                ),
            )
        finally:
            browser.close()

