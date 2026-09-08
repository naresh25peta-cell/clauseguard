"""
api.py — FastAPI web server exposing ClauseGuard functionality as REST endpoints.

This is an alternative to the CLI runner (cli.py). Useful for:
  - Testing via Swagger UI at http://localhost:8000/docs
  - Exposing the same functionality behind a chat-style interface later

Endpoints:
  POST /setup-db              Create database tables
  POST /seed-db               Insert sample NominationRules
  POST /check-cn              Upload a CN PDF and get compliance scores
  POST /scan-msa              Upload an MSA PDF and get risk ratings
  GET  /results/cn            View all past CN extraction results
  GET  /results/msa           View all past MSA risk results
"""
import os
import tempfile
from fastapi import FastAPI, UploadFile, File, Query
from fastapi.responses import JSONResponse
from clauseguard.database.schema import create_tables, get_connection

app = FastAPI(
    title="ClauseGuard",
    description="LLM-powered contract clause extraction, scoring, and risk scanning.",
    version="0.1.0",
)


# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

@app.post("/setup-db", summary="Create database tables")
def setup_db():
    """Create all SQLite tables. Safe to call multiple times (uses IF NOT EXISTS)."""
    create_tables()
    return {"status": "ok", "message": "Database tables created."}


@app.post("/seed-db", summary="Insert sample NominationRules")
def seed_db():
    """Populate NominationRules with sample data for testing."""
    from clauseguard.database.seed import seed
    seed()
    return {"status": "ok", "message": "Sample rules seeded."}


# ---------------------------------------------------------------------------
# CN PDF — extraction + scoring
# ---------------------------------------------------------------------------

@app.post("/check-cn", summary="Extract and score a CN PDF")
async def check_cn(
    file:           UploadFile = File(..., description="CN PDF file to analyse"),
    agreement_guid: str        = Query(..., description="AgreementGuid from deal context (e.g. AGR-001)"),
    trade_group_id: str        = Query(..., description="TradeGroupId from deal context (e.g. TG-100)"),
):
    """
    Upload a Cargo Nomination PDF.
    Returns extracted fields and LLM compliance scores against NominationRules.

    AgreementGuid and TradeGroupId are required query params — they are identity
    columns from the deal context, not extracted from the PDF itself.
    """
    from clauseguard.extraction.pdf_extractor import extract_fields
    from clauseguard.nomination.comparator import compare_and_score

    suffix = os.path.splitext(file.filename or "upload.pdf")[1] or ".pdf"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        extracted = extract_fields(tmp_path)
        results   = compare_and_score(file.filename or "upload.pdf", extracted,
                                      agreement_guid, trade_group_id)
    finally:
        os.unlink(tmp_path)

    return {
        "filename":  file.filename,
        "extracted": extracted,
        "scores":    results,
    }


# ---------------------------------------------------------------------------
# MSA PDF — risk scanner
# ---------------------------------------------------------------------------

@app.post("/scan-msa", summary="Scan an MSA PDF for risk clauses")
async def scan_msa_endpoint(
    file: UploadFile = File(..., description="MSA PDF file to scan"),
    use_case: str    = Query(
        default="periodic",
        description="periodic | cmo_check | draft_validation",
    ),
):
    """
    Upload a Master Sales Agreement PDF.
    Returns clause-by-clause Red / Amber / Green risk ratings.
    """
    from clauseguard.msa.risk_scanner import scan_msa

    valid = {"periodic", "cmo_check", "draft_validation"}
    if use_case not in valid:
        return JSONResponse(
            status_code=422,
            content={"error": f"use_case must be one of {sorted(valid)}"},
        )

    suffix = os.path.splitext(file.filename or "upload.pdf")[1] or ".pdf"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        results = scan_msa(tmp_path, use_case=use_case)
    finally:
        os.unlink(tmp_path)

    # Summary counts
    from collections import Counter
    counts = Counter(r["rating"] for r in results)

    return {
        "filename": file.filename,
        "use_case": use_case,
        "summary":  {"Red": counts.get("Red", 0), "Amber": counts.get("Amber", 0), "Green": counts.get("Green", 0)},
        "clauses":  results,
    }


# ---------------------------------------------------------------------------
# History / audit endpoints
# ---------------------------------------------------------------------------

@app.get("/results/cn", summary="View all past CN extraction results")
def get_cn_results(limit: int = Query(default=50, ge=1, le=500)):
    """Return the most recent CN extraction + scoring results from the database."""
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("""
        SELECT FileName, AgreementGuid, TradeGroupId, FieldName,
               ExtractedValue, LLMScore, RunAt
        FROM   CNExtractions
        ORDER  BY RunAt DESC
        LIMIT  ?
    """, (limit,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {"count": len(rows), "results": rows}


@app.get("/results/msa", summary="View all past MSA risk results")
def get_msa_results(limit: int = Query(default=50, ge=1, le=500)):
    """Return the most recent MSA risk scan results from the database."""
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("""
        SELECT FileName, ClauseRef, RiskRating, Reasoning, UseCase, RunAt
        FROM   MSARiskResults
        ORDER  BY RunAt DESC
        LIMIT  ?
    """, (limit,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {"count": len(rows), "results": rows}
