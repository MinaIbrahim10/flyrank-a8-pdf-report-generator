from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .config import TEMPLATE_DIR


def render_html(data: dict, generated_at: datetime) -> str:
    environment = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = environment.get_template("report.html")
    return template.render(**data, generated_at=generated_at)


async def create_pdf(html: str, destination: Path) -> None:
    from playwright.async_api import async_playwright

    destination.parent.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        try:
            page = await browser.new_page()
            await page.set_content(html, wait_until="networkidle")
            await page.pdf(
                path=str(destination),
                format="A4",
                print_background=True,
                margin={"top": "16mm", "right": "13mm", "bottom": "16mm", "left": "13mm"},
            )
        finally:
            await browser.close()
