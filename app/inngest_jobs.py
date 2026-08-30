import logging

import inngest

from app.background_reports import (
    create_pending_report,
    load_report_data,
    mark_done,
    mark_failed,
    mark_started,
    render_background_pdf,
)


inngest_client = inngest.Inngest(
    app_id="flyrank-a8-pdf-reports",
    logger=logging.getLogger("uvicorn"),
)


@inngest_client.create_function(
    fn_id="generate-pdf-report",
    trigger=inngest.TriggerEvent(
        event="report/generate",
    ),
)
def generate_pdf_report(
    ctx: inngest.ContextSync,
):
    report_id = str(
        ctx.event.data["report_id"]
    )

    days = int(
        ctx.event.data.get(
            "days",
            30,
        )
    )

    try:
        ctx.step.run(
            "mark-started",
            mark_started,
            report_id,
        )

        report_data = ctx.step.run(
            "query-report-data",
            load_report_data,
            days,
        )

        artifact = ctx.step.run(
            "render-and-store-pdf",
            render_background_pdf,
            report_id,
            report_data,
        )

        result = ctx.step.run(
            "finalize-report",
            mark_done,
            report_id,
            artifact,
        )

        return result

    except Exception as error:
        mark_failed(
            report_id,
            str(error),
        )

        raise


def _create_weekly_report() -> dict:
    return create_pending_report(
        days=30,
    )


@inngest_client.create_function(
    fn_id="scheduled-monday-pdf-report",
    trigger=inngest.TriggerCron(
        cron="0 8 * * 1",
    ),
)
def scheduled_monday_report(
    ctx: inngest.ContextSync,
):
    report = ctx.step.run(
        "create-pending-weekly-report",
        _create_weekly_report,
    )

    report_id = str(
        report["id"]
    )

    try:
        ctx.step.run(
            "mark-started",
            mark_started,
            report_id,
        )

        report_data = ctx.step.run(
            "query-report-data",
            load_report_data,
            30,
        )

        artifact = ctx.step.run(
            "render-and-store-pdf",
            render_background_pdf,
            report_id,
            report_data,
        )

        result = ctx.step.run(
            "finalize-report",
            mark_done,
            report_id,
            artifact,
        )

        return {
            "schedule": "0 8 * * 1",
            "report_id": report_id,
            **result,
        }

    except Exception as error:
        mark_failed(
            report_id,
            str(error),
        )

        raise


functions = [
    generate_pdf_report,
    scheduled_monday_report,
]
