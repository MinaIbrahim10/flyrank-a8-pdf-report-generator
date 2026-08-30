import json
import urllib.request


BASE = "http://127.0.0.1:8001"


def post(url: str):
    request = urllib.request.Request(
        url,
        method="POST",
    )

    with urllib.request.urlopen(
        request,
        timeout=60,
    ) as response:
        return (
            response.status,
            json.loads(
                response.read()
            ),
        )


def main() -> None:
    print(
        "=== FIRST NORMAL REQUEST ==="
    )

    status1, first = post(
        f"{BASE}/reports?days=30"
    )

    print(
        "Status:",
        status1,
    )

    print(
        "ID:",
        first["id"],
    )

    print(
        "Reused:",
        first["reused"],
    )

    assert status1 in (
        200,
        201,
    )

    print()
    print(
        "=== SECOND NORMAL REQUEST ==="
    )

    status2, second = post(
        f"{BASE}/reports?days=30"
    )

    print(
        "Status:",
        status2,
    )

    print(
        "ID:",
        second["id"],
    )

    print(
        "Reused:",
        second["reused"],
    )

    assert status2 == 200

    assert (
        first["id"]
        == second["id"]
    )

    assert (
        first["file"]
        == second["file"]
    )

    assert second["reused"] is True

    print(
        "PASS: duplicate request reused same report"
    )

    print()
    print(
        "=== FORCE REQUEST ==="
    )

    status3, forced = post(
        f"{BASE}/reports"
        f"?days=30"
        f"&force=true"
    )

    print(
        "Status:",
        status3,
    )

    print(
        "ID:",
        forced["id"],
    )

    print(
        "Reused:",
        forced["reused"],
    )

    assert status3 == 201

    assert (
        forced["id"]
        != second["id"]
    )

    assert forced["reused"] is False

    print(
        "PASS: force=true generated new report"
    )

    print()
    print(
        "=== DATABASE CHECK ==="
    )

    from pathlib import Path
    import sqlite3

    db = Path(
        __file__
    ).resolve().parent.parent / "report.db"

    connection = sqlite3.connect(
        db
    )

    normal_count = connection.execute(
        """
        SELECT COUNT(*)
        FROM reports
        WHERE idempotency_key LIKE
              'sales:%:days=30'
        """
    ).fetchone()[0]

    connection.close()

    print(
        "Daily idempotent rows:",
        normal_count,
    )

    assert normal_count == 1

    print(
        "PASS: only one idempotent daily row exists"
    )

    print()
    print(
        "STAGE 5 PASS"
    )


if __name__ == "__main__":
    main()
