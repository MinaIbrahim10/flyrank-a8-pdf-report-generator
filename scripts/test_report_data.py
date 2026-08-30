import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.report_data import get_report_data


def main() -> None:
    report = get_report_data(days=30)

    print(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        )
    )

    summary = report["summary"]

    assert summary["total_orders"] == 200
    assert summary["total_revenue"] > 0
    assert summary["average_order_value"] > 0
    assert summary["unique_customers"] > 0
    assert len(report["top_products"]) == 5
    assert len(report["orders"]) == 200

    summed_product_revenue = sum(
        item["revenue"]
        for item in report["top_products"]
    )

    assert (
        summed_product_revenue
        <= summary["total_revenue"]
    )

    print()
    print("PASS: report aggregation is valid")
    print(
        f"Total orders: {summary['total_orders']}"
    )
    print(
        f"Total revenue: ${summary['total_revenue']:.2f}"
    )
    print(
        f"Average order: ${summary['average_order_value']:.2f}"
    )
    print(
        f"Unique customers: {summary['unique_customers']}"
    )

    top = summary["top_product_by_units"]

    if top:
        print(
            f"Top by units: {top['product']} ({top['units']})"
        )


if __name__ == "__main__":
    main()
