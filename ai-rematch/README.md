# Shop PDF Report Generator

A synchronous FastAPI backend that reads shop orders from SQLite, aggregates report data once, renders a Jinja2 HTML document, and prints it as a professional A4 PDF through Playwright and Chromium. Metadata stays in SQLite; generated PDF files live in `reports/`.

## Setup and operation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
python -m app.seed
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

The seed uses a fixed random seed and deterministic IDs to replace the order set atomically with exactly 200 realistic rows. Dates are relative to the current UTC day so the seven-day report remains useful.

## Aggregation SQL

Total order count:

```sql
SELECT COUNT(*) FROM orders;
```

Total revenue:

```sql
SELECT COALESCE(SUM(amount), 0) FROM orders;
```

Top five products by revenue:

```sql
SELECT product, COUNT(*) AS order_count, ROUND(SUM(amount), 2) AS revenue
FROM orders
GROUP BY product
ORDER BY revenue DESC, product ASC
LIMIT 5;
```

Orders per day for the last seven days (the application binds the start and end dates):

```sql
SELECT DATE(created_at) AS day, COUNT(*) AS order_count,
       ROUND(SUM(amount), 2) AS revenue
FROM orders
WHERE DATE(created_at) BETWEEN ? AND ?
GROUP BY DATE(created_at)
ORDER BY day ASC;
```

All SQL values supplied at runtime use parameters.

## API

```bash
# Generate today's report (201), or reuse it (200)
curl -i -X POST http://127.0.0.1:8000/reports

# Always create a new report (201)
curl -i -X POST 'http://127.0.0.1:8000/reports?force=true'

# Read metadata and download the actual PDF
curl http://127.0.0.1:8000/reports/1
curl -o report.pdf http://127.0.0.1:8000/reports/1/file
```

Generation is synchronous: the POST returns only after Chromium has produced and stored the PDF. This is straightforward and gives immediate success/failure feedback. Move it to a durable background job when reports become slow, concurrent generation grows, or requests risk exceeding gateway timeouts; then return a job/report status resource.

Database-level daily idempotency prevents retries, double-clicks, and multiple API instances from producing duplicate normal reports. Without it, a client retry after a network timeout could render and store another expensive report; at scale, repeated Chromium work can consume CPU and increase hosting cost while also leaving confusing duplicate artifacts. `force=true` intentionally bypasses this rule.

## Tests and checks

Set `TEST_API_BASE_URL` to change the test client's base URL; it does not depend on a particular live-server port.

```bash
python -m app.seed
python -m app.seed
python -m pytest -q
python -m compileall -q app tests
```

`report.db` and `reports/` are runtime artifacts excluded by `.gitignore`. PDF bytes are served only by the file endpoint and are never embedded in JSON.
