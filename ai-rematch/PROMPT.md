# Improved AI Rematch Prompt

Build a complete PDF report generator backend using Python, FastAPI, SQLite,
Jinja2, Playwright, and Chromium.

Work only inside the ai-rematch folder. Do not inspect, copy, or modify the
implementation in the main project or ai-version.

Use a database named report.db.

Create an orders table with:
id, customer, product, amount, and created_at.

Create a deterministic seed script with exactly 200 realistic shop orders from
around 6 products. Running the seed script multiple times must always leave
exactly 200 rows instead of adding duplicates.

Create one report data layer that includes these required SQL results:
- total order count
- total revenue
- top 5 products by revenue
- orders per day for the last 7 days

Also provide the complete order list for the PDF.

Generate a professional A4 PDF from an HTML template using Playwright and
Chromium.

The PDF must include:
- title and generated date
- total orders
- total revenue
- top 5 products
- last 7 days summary
- long table containing all orders
- repeating table headers on following pages
- rows that never split across pages
- page numbers

It must be at least 2 pages.

Implement:

POST /reports
Generate the report synchronously, store the PDF on disk, save its metadata in
SQLite, and return HTTP 201 with the id and file link.

GET /reports/{id}
Return report metadata and the file link.

GET /reports/{id}/file
Serve the stored PDF.

Unknown report ids must return 404.

Implement daily idempotency at the database level, not only with an application
lookup. A second normal POST on the same day must return the same report with
HTTP 200.

Support force=true to bypass idempotency and generate a new report with HTTP 201.

Use safe parameterized SQL.

Use nice PDF filenames.

Store generated PDFs under reports/ and never put PDF bytes inside JSON.

Add report.db and generated reports to .gitignore.

Use pytest for automated tests and test at least:
- seed stays exactly 200 after two runs
- new report generation
- duplicate request returns the same id
- force=true returns a different id
- metadata endpoint
- real PDF download
- unknown id returns 404

Make the API base URL configurable in test utilities instead of assuming a
single port.

Pin dependency versions in requirements.txt.

Write a complete README containing:
- project purpose and pipeline
- setup and seed commands
- run commands
- all four aggregation SQL queries
- API examples
- explanation of synchronous generation and when it should move to a
  background job
- explanation of what idempotency protects against
- one realistic cost of missing idempotency
- test commands
- generated artifact/gitignore explanation

Run the seed twice, tests, Python compilation, and real PDF generation yourself.

At the end report exactly:
- files created
- checks performed
- tests passed/failed
- PDF page count
- anything you had to decide that was not specified
