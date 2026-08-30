import json
import os
import sys
import time
from pathlib import Path

import urllib.error
import urllib.request


BASE = os.getenv("BASE_URL", "http://127.0.0.1:8000")


def request_json(
    method: str,
    url: str,
):
    request = urllib.request.Request(
        url,
        method=method,
    )

    with urllib.request.urlopen(
        request,
        timeout=60,
    ) as response:
        body = json.loads(
            response.read()
        )

        return (
            response.status,
            body,
        )


def main() -> None:
    print(
        "Testing health endpoint..."
    )

    status, health = request_json(
        "GET",
        f"{BASE}/health",
    )

    assert status == 200
    assert health["status"] == "ok"

    print(
        "PASS: health endpoint"
    )

    print()
    print(
        "Generating report..."
    )

    started = time.perf_counter()

    status, report = request_json(
        "POST",
        f"{BASE}/reports?days=30",
    )

    elapsed = (
        time.perf_counter()
        - started
    )

    assert status == 201
    assert report["id"]
    assert report["file"]
    assert report["status"] == "done"
    assert (
        report["file_size_bytes"]
        > 20_000
    )
    assert len(report["sha256"]) == 64

    print(
        f"PASS: POST /reports -> {status}"
    )

    print(
        f"Visible wait: {elapsed:.2f}s"
    )

    print(
        json.dumps(
            report,
            indent=2,
        )
    )

    report_id = report["id"]

    print()
    print(
        "Fetching metadata..."
    )

    status, metadata = request_json(
        "GET",
        f"{BASE}/reports/{report_id}",
    )

    assert status == 200
    assert metadata["id"] == report_id

    print(
        "PASS: GET report metadata"
    )

    print()
    print(
        "Downloading PDF..."
    )

    target = Path(
        "/tmp/a8-stage4-report.pdf"
    )

    urllib.request.urlretrieve(
        f"{BASE}"
        f"/reports/"
        f"{report_id}"
        f"/file",
        target,
    )

    assert target.exists()
    assert (
        target.stat().st_size
        > 20_000
    )

    magic = target.read_bytes()[:5]

    assert magic == b"%PDF-"

    print(
        "PASS: downloaded real PDF"
    )

    print(
        f"Downloaded size: "
        f"{target.stat().st_size / 1024:.1f} KB"
    )

    print()
    print(
        "Testing unknown report..."
    )

    try:
        request_json(
            "GET",
            f"{BASE}/reports/"
            f"does-not-exist",
        )
    except urllib.error.HTTPError as error:
        assert (
            error.code == 404
        )

        print(
            "PASS: unknown report -> 404"
        )
    else:
        raise RuntimeError(
            "Expected 404"
        )

    print()
    print(
        "STAGE 4 PASS"
    )


if __name__ == "__main__":
    main()
