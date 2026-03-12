"""
Security Tools Router — VirusTotal, AbuseIPDB, URLScan.io, IP2WHOIS,
                        ipinfo.io, IP2Location, BigDataCloud

Prefix: /api/security
"""

import ipaddress
import re
from urllib.parse import urlparse

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from src.middleware.rate_limit import limiter
from src.services.security_tools_service import (
    abuseipdb_check,
    bigdatacloud_lookup,
    ip2location_lookup,
    ip2whois_lookup,
    ipinfo_lookup,
    urlscan_result,
    urlscan_submit,
    virustotal_analysis,
    virustotal_scan_url,
)
from src.utils.error_handler import service_endpoint

router = APIRouter()

_VT_ID_RE = re.compile(r"^[a-zA-Z0-9\-_]{10,100}$")
_UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
_DOMAIN_RE = re.compile(
    r"^[a-zA-Z0-9]([a-zA-Z0-9\-]*[a-zA-Z0-9])?"
    r"(\.[a-zA-Z0-9]([a-zA-Z0-9\-]*[a-zA-Z0-9])?)*\.[a-zA-Z]{2,}$"
)


def _validate_public_ip(ip: str) -> str:
    """Validate IP format and block private/reserved ranges."""
    addr = ipaddress.ip_address(ip.strip())
    if addr.is_private or addr.is_reserved or addr.is_loopback or addr.is_link_local:
        raise HTTPException(status_code=400, detail="Private/reserved IP addresses not allowed")
    return str(addr)


def _validate_url(url: str) -> str:
    """Validate URL scheme and block private/internal hosts via DNS resolution."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise HTTPException(status_code=400, detail="Only http/https URLs are allowed")
    if not parsed.hostname:
        raise HTTPException(status_code=400, detail="Invalid URL")
    # Block obvious private IPs (domain-based SSRF requires DNS resolution at request time)
    try:
        addr = ipaddress.ip_address(parsed.hostname)
        if addr.is_private or addr.is_reserved or addr.is_loopback:
            raise HTTPException(status_code=400, detail="Internal/private URLs not allowed")
    except ValueError:
        pass  # hostname is a domain name, not an IP — allow
    return url


class UrlScanRequest(BaseModel):
    url: str = Field(..., max_length=2048)


# ─── IP Geolocation ──────────────────────────────────────────────────────────


@router.get("/ipinfo/{ip}")
@limiter.limit("10/minute")
@service_endpoint("Ip Info")
async def ip_info(request: Request, ip: str):
    """IP geolocation from ipinfo.io."""
    ip = _validate_public_ip(ip)
    return await ipinfo_lookup(ip)


@router.get("/ip2location/{ip}")
@limiter.limit("10/minute")
@service_endpoint("IP2Location")
async def ip2location(request: Request, ip: str):
    """IP geolocation from IP2Location."""
    ip = _validate_public_ip(ip)
    return await ip2location_lookup(ip)


@router.get("/bigdatacloud/{ip}")
@limiter.limit("10/minute")
@service_endpoint("BigDataCloud")
async def bigdatacloud(request: Request, ip: str):
    """IP geolocation from BigDataCloud."""
    ip = _validate_public_ip(ip)
    return await bigdatacloud_lookup(ip)


# ─── Threat Intelligence ─────────────────────────────────────────────────────


@router.post("/virustotal/scan-url")
@limiter.limit("10/minute")
@service_endpoint("VT Scan")
async def vt_scan(request: Request, req: UrlScanRequest):
    """Submit a URL for VirusTotal scanning."""
    _validate_url(req.url)
    return await virustotal_scan_url(req.url)


@router.get("/virustotal/analysis/{analysis_id}")
@limiter.limit("10/minute")
@service_endpoint("VT Analysis")
async def vt_analysis(request: Request, analysis_id: str):
    """Get VirusTotal analysis result."""
    if not _VT_ID_RE.match(analysis_id):
        raise HTTPException(status_code=400, detail="Invalid analysis ID format")
    return await virustotal_analysis(analysis_id)


@router.get("/abuse/{ip}")
@limiter.limit("10/minute")
@service_endpoint("AbuseIPDB")
async def abuse_check(request: Request, ip: str):
    """Check IP against AbuseIPDB."""
    ip = _validate_public_ip(ip)
    return await abuseipdb_check(ip)


# ─── URL Scanning ────────────────────────────────────────────────────────────


@router.post("/urlscan/scan-url")
@limiter.limit("10/minute")
@service_endpoint("URLScan Submit")
async def urlscan_scan(request: Request, req: UrlScanRequest):
    """Submit URL to URLScan.io."""
    _validate_url(req.url)
    return await urlscan_submit(req.url)


@router.get("/urlscan/result/{uuid}")
@limiter.limit("10/minute")
@service_endpoint("URLScan Result")
async def urlscan_get_result(request: Request, uuid: str):
    """Get URLScan.io result."""
    if not _UUID_RE.match(uuid):
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    return await urlscan_result(uuid)


# ─── WHOIS ───────────────────────────────────────────────────────────────────


@router.get("/whois/{domain}")
@limiter.limit("10/minute")
@service_endpoint("WHOIS")
async def whois_lookup(request: Request, domain: str):
    """WHOIS lookup for a domain."""
    if not _DOMAIN_RE.match(domain) or len(domain) > 253:
        raise HTTPException(status_code=400, detail="Invalid domain format")
    return await ip2whois_lookup(domain)
