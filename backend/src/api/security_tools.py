"""
Security Tools Router — VirusTotal, AbuseIPDB, URLScan.io, IP2WHOIS,
                        ipinfo.io, IP2Location, BigDataCloud

Prefix: /api/security
"""

import ipaddress

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

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


def _validate_public_ip(ip: str) -> str:
    """Validate IP format and block private/reserved ranges."""
    addr = ipaddress.ip_address(ip.strip())
    if addr.is_private or addr.is_reserved or addr.is_loopback or addr.is_link_local:
        raise HTTPException(status_code=400, detail="Private/reserved IP addresses not allowed")
    return str(addr)


# ─── IP Geolocation ──────────────────────────────────────────────────────────

@router.get("/ipinfo/{ip}")
@service_endpoint("Ip Info")
async def ip_info(ip: str):
    """IP geolocation from ipinfo.io."""
    ip = _validate_public_ip(ip)
    return await ipinfo_lookup(ip)
    """IP geolocation from IP2Location."""
    ip = _validate_public_ip(ip)
    return await ip2location_lookup(ip)
    """IP geolocation from BigDataCloud."""
    ip = _validate_public_ip(ip)
    return await bigdatacloud_lookup(ip)
    """Validate URL scheme and block private/internal hosts."""
    from urllib.parse import urlparse
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise HTTPException(status_code=400, detail="Only http/https URLs are allowed")
    if not parsed.hostname:
        raise HTTPException(status_code=400, detail="Invalid URL")
    addr = ipaddress.ip_address(parsed.hostname)
    if addr.is_private or addr.is_reserved or addr.is_loopback:
        raise HTTPException(status_code=400, detail="Internal/private URLs not allowed")
    return url


class UrlScanRequest(BaseModel):
    url: str = Field(..., max_length=2048)


@router.post("/virustotal/scan-url")
@service_endpoint("Vt Scan")
async def vt_scan(req: UrlScanRequest):
    """Submit a URL for VirusTotal scanning."""
    _validate_url(req.url)
    return await virustotal_scan_url(req.url)
    """Get VirusTotal analysis result."""
    if not _VT_ID_RE.match(analysis_id):
        raise HTTPException(status_code=400, detail="Invalid analysis ID format")
    return await virustotal_analysis(analysis_id)
    """Check IP against AbuseIPDB."""
    ip = _validate_public_ip(ip)
    return await abuseipdb_check(ip)
    """Submit URL to URLScan.io."""
    _validate_url(req.url)
    return await urlscan_submit(req.url)
    """Get URLScan.io result."""
    if not _UUID_RE.match(uuid):
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    return await urlscan_result(uuid)
    """WHOIS lookup for a domain."""
    if not _DOMAIN_RE.match(domain) or len(domain) > 253:
        raise HTTPException(status_code=400, detail="Invalid domain format")
    return await ip2whois_lookup(domain)
    return {"status": "ok", "service": "security"}
