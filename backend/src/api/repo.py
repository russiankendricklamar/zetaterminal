"""
REPO Analysis API router.

POST /analyze — upload CSV/Excel, run full pipeline
GET  /health   — service health check
"""

import io
import logging

import pandas as pd
from fastapi import APIRouter, File, HTTPException, UploadFile

from src.services.repo_service import run_full_pipeline

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/analyze")
async def analyze_repo(file: UploadFile = File(...)):
    """Accept a CSV or Excel file and return full REPO analysis."""
    if file.filename is None:
        raise HTTPException(status_code=400, detail="No file provided")

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ("csv", "xlsx", "xls"):
        raise HTTPException(status_code=400, detail="Unsupported file format. Use CSV or Excel.")

    try:
        content = await file.read()
        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File too large (max 10 MB)")
        if ext == "csv":
            df = pd.read_csv(io.BytesIO(content))
        else:
            df = pd.read_excel(io.BytesIO(content))
    except Exception as e:
        logger.error("Failed to parse uploaded file: %s", e)
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {e}")

    if df.empty:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    try:
        result = run_full_pipeline(df)
    except Exception as e:
        logger.error("REPO pipeline failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")

    return result


@router.get("/health")
async def health():
    return {"status": "ok", "service": "repo"}
