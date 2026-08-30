# AI Version 1 — Comparison Notes

## What the AI did better

The AI version made dependency reproducibility more explicit by pinning package
versions in `requirements.txt`. It also added `pytest` and `httpx` and used
automated pytest tests. My hand-built version originally used unpinned runtime
dependencies and stage-specific verification scripts.

## What my version did better

My version has much more complete assignment documentation. The main README
includes the reporting pipeline, the four aggregation SQL queries, API examples,
POST-to-download proof, idempotency behavior, the explanation of when PDF work
should leave the HTTP request, the cost of missing idempotency, and a screenshot
of the generated PDF.

The first AI version's README is much shorter and does not document those
assignment checkpoints in enough detail.

## What the AI decided on its own

My first prompt did not specify the SQLite database filename. The AI silently
chose `shop.db`, while my implementation uses `report.db`.

The prompt also did not tell the AI which testing style to use. It chose
`pytest` and `httpx`, while my implementation uses dedicated stage verification
scripts.

## Concrete differences

1. **Dependencies**
   - My version: runtime packages are listed without exact version pins.
   - AI version: exact versions are pinned and pytest/httpx are included.

2. **Testing**
   - My version: separate scripts verify aggregation, API behavior, downloads,
     404 handling, and idempotency.
   - AI version: conventional pytest tests; Codex reported 2 tests passing.

3. **Documentation**
   - My version: detailed assignment-oriented README with SQL, API proof,
     design explanations, and PDF screenshot.
   - AI version: short setup-oriented README.

4. **Database naming**
   - My version: `report.db`.
   - AI version: `shop.db`.
   - This was not specified in the first prompt, so the AI chose it itself.

## AI Version 1 verification

Codex reported:

- Python compilation passed
- pytest: 2 passed
- seed executed twice and stayed at 200 rows
- real Chromium PDF generation passed
- generated PDF was A4 and 7 pages
- git whitespace validation passed
- all required API routes were present

