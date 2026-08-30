from fastapi import FastAPI

app = FastAPI(
    title="PDF Report Generator",
    description="FlyRank Backend Track A8 — SQL to PDF reporting pipeline",
    version="1.0.0",
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "pdf-report-generator",
    }
