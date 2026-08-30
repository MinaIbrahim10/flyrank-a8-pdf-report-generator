import logging

import inngest

from app.background_reports import (
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
async def generate_pdf_report(
    ctx: inngest.Context,
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
        await ctx.step.run(
            "mark-started",
            mark_started,
            report_id,
        )

        report_data = await ctx.step.run(
            "query-report-data",
            load_report_data,
            days,
        )

        artifact = await ctx.step.run(
            "render-and-store-pdf",
            render_background_pdf,
            report_id,
            report_data,
        )

        result = await ctx.step.run(
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


functions = [
    generate_pdf_report,
]
