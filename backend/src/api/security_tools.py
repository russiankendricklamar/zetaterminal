"""
Security Tools Router — VirusTotal, AbuseIPDB, URLScan.io, IP2WHOIS,
                        ipinfo.io, IP2Location, BigDataCloud

Prefix: /api/security
"""

import ipaddress
import logging

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

logger = logging.getLogger(__name__)

router = APIRouter()


def _validate_public_ip(ip: str) -> str:
    """Validate IP format and block private/reserved ranges."""
    try:
        addr = ipaddress.ip_address(ip.strip())
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid IP address format")
    if addr.is_private or addr.is_reserved or addr.is_loopback or addr.is_link_local:
        raise HTTPException(status_code=400, detail="Private/reserved IP addresses not allowed")
    return str(addr)


# ─── IP Geolocation ──────────────────────────────────────────────────────────

@router.get("/ipinfo/{ip}")
async def ip_info(ip: str):
    """IP geolocation from ipinfo.io."""
    ip = _validate_public_ip(ip)
    try:
        return await ipinfo_lookup(ip)
    except Exception as e:
        logger.error("ipinfo lookup failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/ip2location/{ip}")
async def ip2loc(ip: str):
    """IP geolocation from IP2Location."""
    ip = _validate_public_ip(ip)
    try:
        return await ip2location_lookup(ip)
    except Exception as e:
        logger.error("ip2location lookup failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/bigdatacloud/{ip}")
async def bdc(ip: str):
    """IP geolocation from BigDataCloud."""
    ip = _validate_public_ip(ip)
    try:
        return await bigdatacloud_lookup(ip)
    except Exception as e:
        logger.error("BigDataCloud lookup failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


# ─── VirusTotal ───────────────────────────────────────────────────────────────

class UrlScanRequest(BaseModel):
    url: str


@router.post("/virustotal/scan-url")
async def vt_scan(req: UrlScanRequest):
    """Submit a URL for VirusTotal scanning."""
    try:
        return await virustotal_scan_url(req.url)
    except Exception as e:
        logger.error("VirusTotal scan failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/virustotal/analysis/{analysis_id}")
async def vt_analysis(analysis_id: str):
    """Get VirusTotal analysis result."""
    try:
        return await virustotal_analysis(analysis_id)
    except Exception as e:
        logger.error("VirusTotal analysis failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


# ─── AbuseIPDB ────────────────────────────────────────────────────────────────

@router.get("/abuseipdb/{ip}")
async def abuse_check(ip: str):
    """Check IP against AbuseIPDB."""
    ip = _validate_public_ip(ip)
    try:
        return await abuseipdb_check(ip)
    except Exception as e:
        logger.error("AbuseIPDB check failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


# ─── URLScan.io ───────────────────────────────────────────────────────────────

@router.post("/urlscan/submit")
async def uscan_submit(req: UrlScanRequest):
    """Submit URL to URLScan.io."""
    try:
        return await urlscan_submit(req.url)
    except Exception as e:
        logger.error("URLScan submit failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/urlscan/result/{uuid}")
async def uscan_result(uuid: str):
    """Get URLScan.io result."""
    try:
        return await urlscan_result(uuid)
    except Exception as e:
        logger.error("URLScan result retrieval failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


# ─── IP2WHOIS ─────────────────────────────────────────────────────────────────

@router.get("/whois/{domain}")
async def whois(domain: str):
    """WHOIS lookup for a domain."""
    try:
        return await ip2whois_lookup(domain)
    except Exception as e:
        logger.error("WHOIS lookup failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/health")
async def health():
    return {"status": "ok", "service": "security"}
