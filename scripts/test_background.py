import json
import time
import urllib.error
import urllib.request


BASE = "http://127.0.0.1:8001"


def request_json(method: str, url: str):
    request = urllib.request.Request(
        url,
        method=method,
    )

    with urllib.request.urlopen(
        request,
        timeout=60,
    ) as response:
        return (
            response.status,
            json.loads(response.read()),
        )


print("=== CREATE BACKGROUND REPORT ===")

started = time.perf_counter()

status, created = request_json(
    "POST",
    f"{BASE}/reports/background?days=30",
)

request_time = time.perf_counter() - started

print("HTTP status:", status)
print("Request time:", f"{request_time:.3f}s")
print(
    json.dumps(
        created,
        indent=2,
    )
)

assert status == 202
assert created["status"] == "pending"
assert created["id"]

report_id = created["id"]

print()
print("PASS: POST returned 202 Accepted")
print("PASS: report starts as pending")

print()
print("=== POLL REPORT STATUS ===")

final = None
seen_statuses = []

for attempt in range(1, 31):
    status, report = request_json(
        "GET",
        f"{BASE}/reports/{report_id}",
    )

    current = report["status"]

    if current not in seen_statuses:
        seen_statuses.append(current)

    print(
        f"Attempt {attempt:02d}: "
        f"status={current}"
    )

    if current == "done":
        final = report
        break

    if current == "failed":
        print(
            json.dumps(
                report,
                indent=2,
            )
        )

        raise RuntimeError(
            f"Background report failed: "
            f"{report.get('error')}"
        )

    time.sleep(1)

if final is None:
    raise RuntimeError(
        "Timed out waiting for report"
    )

print()
print("PASS: report reached done")
print(
    "Observed statuses:",
    " -> ".join(seen_statuses),
)

print()
print("=== FINAL METADATA ===")

print(
    json.dumps(
        final,
        indent=2,
    )
)

assert final["file_size_bytes"]
assert final["file_size_bytes"] > 20_000
assert final["sha256"]
assert len(final["sha256"]) == 64
assert final["finished_at"]

print()
print("PASS: final artifact metadata exists")

print()
print("=== DOWNLOAD GENERATED PDF ===")

target = "/tmp/a8-background-report.pdf"

urllib.request.urlretrieve(
    f"{BASE}/reports/{report_id}/file",
    target,
)

with open(target, "rb") as handle:
    magic = handle.read(5)

assert magic == b"%PDF-"

print("PASS: downloaded real PDF")
print("File:", target)

print()
print("=== BACKGROUND TIMING ===")

print(
    f"POST returned in {request_time:.3f}s"
)

if request_time < 0.75:
    print(
        "PASS: request returned quickly "
        "without waiting for PDF generation"
    )
else:
    print(
        "INFO: request returned before completion, "
        "but local enqueue overhead was "
        f"{request_time:.3f}s"
    )

print()
print("STRETCH BACKGROUND PASS")
