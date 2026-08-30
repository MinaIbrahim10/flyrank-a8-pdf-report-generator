import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

BASE = os.getenv(
    "BASE_URL",
    "http://127.0.0.1:8001",
)


def get_json(path: str):
    with urllib.request.urlopen(
        BASE + path,
        timeout=30,
    ) as response:
        return (
            response.status,
            json.loads(
                response.read()
            ),
        )


print("=== GET /reports ===")

status, result = get_json(
    "/reports?limit=5"
)

print(
    json.dumps(
        result,
        indent=2,
    )
)

assert status == 200
assert result["count"] <= 5
assert isinstance(
    result["reports"],
    list,
)

print()
print("PASS: report list endpoint works")


print()
print("=== FILTER DONE REPORTS ===")

status, done = get_json(
    "/reports?limit=10&status=done"
)

assert status == 200

for report in done["reports"]:
    assert (
        report["status"]
        == "done"
    )

print(
    f"Done reports returned: "
    f"{done['count']}"
)

print(
    "PASS: status filter works"
)


print()
print("=== INVALID FILTER ===")

try:
    get_json(
        "/reports?status=banana"
    )
except urllib.error.HTTPError as error:
    assert error.code == 400

    print(
        "PASS: invalid status -> 400"
    )
else:
    raise RuntimeError(
        "Expected HTTP 400"
    )


print()
print(
    "EXTRA REPORT LIST PASS"
)
