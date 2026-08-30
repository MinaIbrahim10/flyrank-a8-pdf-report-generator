import os

os.environ.setdefault(
    "INNGEST_DEV",
    "http://127.0.0.1:8288",
)

from app.inngest_jobs import functions


print("=== REGISTERED INNGEST FUNCTIONS ===")

for function in functions:
    print(
        getattr(
            function,
            "_opts",
            function,
        )
    )

assert len(functions) == 2

names = [
    getattr(
        function,
        "__name__",
        "",
    )
    for function in functions
]

assert "generate_pdf_report" in names
assert "scheduled_monday_report" in names

print()
print("PASS: 2 Inngest functions registered")
print("PASS: scheduled Monday report function registered")
print("Cron: 0 8 * * 1")
