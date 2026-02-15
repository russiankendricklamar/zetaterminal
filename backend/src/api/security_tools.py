"""
Security Tools Router — VirusTotal, AbuseIPDB, URLScan.io, IP2WHOIS,
                        ipinfo.io, IP2Location, BigDataCloud

Prefix: /api/security
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from src.services.security_tools_service import (
    ipinfo_lookup,
    ip2location_lookup,
    bigdatacloud_lookup,
    virustotal_scan_url,
    virustotal_analysis,
    abuseipdb_check,
    urlscan_submit,
    urlscan_result,
    ip2whois_lookup,
)

router = APIRouter()


# ─── IP Geolocation ──────────────────────────────────────────────────────────

@router.get("/ipinfo/{ip}")
async def ip_info(ip: str):
    """IP geolocation from ipinfo.io."""
    try:
        return await ipinfo_lookup(ip)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ip2location/{ip}")
async def ip2loc(ip: str):
    """IP geolocation from IP2Location."""
    try:
        return await ip2location_lookup(ip)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bigdatacloud/{ip}")
async def bdc(ip: str):
    """IP geolocation from BigDataCloud."""
    try:
        return await bigdatacloud_lookup(ip)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── VirusTotal ───────────────────────────────────────────────────────────────

class UrlScanRequest(BaseModel):
    url: str


@router.post("/virustotal/scan-url")
async def vt_scan(req: UrlScanRequest):
    """Submit a URL for VirusTotal scanning."""
    try:
        return await virustotal_scan_url(req.url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/virustotal/analysis/{analysis_id}")
async def vt_analysis(analysis_id: str):
    """Get VirusTotal analysis result."""
    try:
        return await virustotal_analysis(analysis_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── AbuseIPDB ────────────────────────────────────────────────────────────────

@router.get("/abuseipdb/{ip}")
async def abuse_check(ip: str):
    """Check IP against AbuseIPDB."""
    try:
        return await abuseipdb_check(ip)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── URLScan.io ───────────────────────────────────────────────────────────────

@router.post("/urlscan/submit")
async def uscan_submit(req: UrlScanRequest):
    """Submit URL to URLScan.io."""
    try:
        return await urlscan_submit(req.url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/urlscan/result/{uuid}")
async def uscan_result(uuid: str):
    """Get URLScan.io result."""
    try:
        return await urlscan_result(uuid)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── IP2WHOIS ─────────────────────────────────────────────────────────────────

@router.get("/whois/{domain}")
async def whois(domain: str):
    """WHOIS lookup for a domain."""
    try:
        return await ip2whois_lookup(domain)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health():
    return {"status": "ok", "service": "security"}
