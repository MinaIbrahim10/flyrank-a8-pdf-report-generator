# Shop PDF report generator

Requires Python 3.10+ and Playwright's Chromium browser.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
python seed.py
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for the interactive API. Create a report with
`POST /reports`; use `POST /reports?force=true` to bypass the daily duplicate check.
PDFs are written to `reports/`, and report metadata plus shop data are stored in
`shop.db`. Both are ignored by git.

Run the automated checks with `pytest`.
