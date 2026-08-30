Build a backend PDF report generator using Python.

Use FastAPI and SQLite.

I want a small shop database with an orders table that has:
id, customer, product, amount, and created_at.

Create a seed script that generates around 200 orders. If I run the seed again it should not keep adding more rows, it should still have around 200 orders.

Create report data from SQL with:
- total number of orders
- total revenue
- top 5 products by revenue
- orders per day for the last 7 days

Then create an HTML report and convert it to a real PDF using Playwright and Chromium.

The PDF should look clean and professional and should contain:
- report title and generated date
- total orders and revenue
- top 5 products table
- all orders in a long table

Make sure the PDF can have multiple pages, rows are not cut between pages, and the table header repeats on the next pages.

Add these API endpoints:

POST /reports
Generate the PDF, save it to disk, save the report information in SQLite, and return the report id and a link to the file.

GET /reports/{id}
Return the report information and file link.

GET /reports/{id}/file
Return the actual PDF file.

If the report id does not exist return 404.

Also add daily duplicate protection. If I call POST /reports more than once on the same day, it should return the existing report instead of generating another one.

Add a force option so I can generate a new report even if today's report already exists.

Keep generated PDFs outside git and add the database and reports folder to .gitignore.

Please organize the code into multiple files and make it easy to run locally.
