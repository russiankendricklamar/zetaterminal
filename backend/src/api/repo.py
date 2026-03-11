"""
REPO Analysis API router.

POST /analyze — upload CSV/Excel, run full pipeline
GET  /health   — service health check
"""

import io

import pandas as pd
from fastapi import APIRouter, File, HTTPException, UploadFile

from src.services.repo_service import run_full_pipeline
from src.utils.error_handler import service_endpoint

router = APIRouter()


@router.post("/analyze")
@service_endpoint("Analyze Repo")
async def analyze_repo(file: UploadFile = File(...)):
    """Accept a CSV or Excel file and return full REPO analysis."""
    if file.filename is None:
        raise HTTPException(status_code=400, detail="No file provided")

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ("csv", "xlsx", "xls"):
        raise HTTPException(status_code=400, detail="Unsupported file format. Use CSV or Excel.")

    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large (max 10 MB)")
    df = pd.read_csv(io.BytesIO(content)) if ext == "csv" else pd.read_excel(io.BytesIO(content))
    if df.empty:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    result = run_full_pipeline(df)
    return result


@router.get("/health")
async def health():
    return {"status": "ok", "service": "repo"}
