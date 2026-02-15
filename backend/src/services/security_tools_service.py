"""
Security Tools Service — VirusTotal, AbuseIPDB, URLScan.io, IP2WHOIS,
                         ipinfo.io, IP2Location, BigDataCloud

Network security and IP intelligence utilities.
"""

import os
from typing import Dict, Any

from src.services.cache_service import cache_get, cache_set, make_cache_key
from src.utils.http_client import get_session

VIRUSTOTAL_KEY = os.getenv("VIRUSTOTAL_API_KEY", "")
ABUSEIPDB_KEY = os.getenv("ABUSEIPDB_API_KEY", "")
URLSCAN_KEY = os.getenv("URLSCAN_API_KEY", "")
IP2WHOIS_KEY = os.getenv("IP2WHOIS_API_KEY", "")
IPINFO_TOKEN = os.getenv("IPINFO_TOKEN", "")
IP2LOCATION_KEY = os.getenv("IP2LOCATION_API_KEY", "")


# ─── ipinfo.io ────────────────────────────────────────────────────────────────

async def ipinfo_lookup(ip: str) -> Dict[str, Any]:
    """Get IP geolocation from ipinfo.io."""
    key = make_cache_key("ipinfo", ip)
    cached = cache_get(key)
    if cached is not None:
        return cached

    url = f"https://ipinfo.io/{ip}"
    params = {"token": IPINFO_TOKEN} if IPINFO_TOKEN else {}
    session = await get_session()
    async with session.get(url, params=params) as resp:
        resp.raise_for_status()
        data = await resp.json(content_type=None)

    data["provider"] = "ipinfo"
    cache_set(key, data, ttl_seconds=3600)
    return data


# ─── IP2Location ──────────────────────────────────────────────────────────────

async def ip2location_lookup(ip: str) -> Dict[str, Any]:
    """Get IP geolocation from IP2Location."""
    key = make_cache_key("ip2loc", ip)
    cached = cache_get(key)
    if cached is not None:
        return cached

    params = {"key": IP2LOCATION_KEY, "ip": ip, "format": "json"}
    session = await get_session()
    async with session.get("https://api.ip2location.io/", params=params) as resp:
        resp.raise_for_status()
        data = await resp.json(content_type=None)

    data["provider"] = "ip2location"
    cache_set(key, data, ttl_seconds=3600)
    return data


# ─── BigDataCloud ─────────────────────────────────────────────────────────────

async def bigdatacloud_lookup(ip: str) -> Dict[str, Any]:
    """Get IP geolocation from BigDataCloud (free tier)."""
    key = make_cache_key("bdc", ip)
    cached = cache_get(key)
    if cached is not None:
        return cached

    params = {"ip": ip, "localityLanguage": "en"}
    session = await get_session()
    async with session.get(
        "https://api.bigdatacloud.net/data/ip-geolocation-full",
        params=params
    ) as resp:
        resp.raise_for_status()
        data = await resp.json(content_type=None)

    data["provider"] = "bigdatacloud"
    cache_set(key, data, ttl_seconds=3600)
    return data


# ─── VirusTotal ───────────────────────────────────────────────────────────────

async def virustotal_scan_url(url_to_scan: str) -> Dict[str, Any]:
    """Submit a URL for scanning to VirusTotal."""
    import base64
    headers = {"x-apikey": VIRUSTOTAL_KEY}
    session = await get_session()
    async with session.post(
        "https://www.virustotal.com/api/v3/urls",
        headers=headers,
        data={"url": url_to_scan}
    ) as resp:
        resp.raise_for_status()
        data = await resp.json(content_type=None)

    return {
        "analysis_id": data.get("data", {}).get("id", ""),
        "type": data.get("data", {}).get("type", ""),
        "url": url_to_scan,
        "provider": "virustotal",
    }


async def virustotal_analysis(analysis_id: str) -> Dict[str, Any]:
    """Get VirusTotal analysis result."""
    key = make_cache_key("vt", "analysis", analysis_id)
    cached = cache_get(key)
    if cached is not None:
        return cached

    headers = {"x-apikey": VIRUSTOTAL_KEY}
    session = await get_session()
    async with session.get(
        f"https://www.virustotal.com/api/v3/analyses/{analysis_id}",
        headers=headers
    ) as resp:
        resp.raise_for_status()
        data = await resp.json(content_type=None)

    attrs = data.get("data", {}).get("attributes", {})
    stats = attrs.get("stats", {})
    result = {
        "analysis_id": analysis_id,
        "status": attrs.get("status", ""),
        "stats": {
            "malicious": stats.get("malicious", 0),
            "suspicious": stats.get("suspicious", 0),
            "harmless": stats.get("harmless", 0),
            "undetected": stats.get("undetected", 0),
            "timeout": stats.get("timeout", 0),
        },
        "provider": "virustotal",
    }
    if result["status"] == "completed":
        cache_set(key, result, ttl_seconds=3600)
    return result


# ─── AbuseIPDB ────────────────────────────────────────────────────────────────

async def abuseipdb_check(ip: str) -> Dict[str, Any]:
    """Check an IP against AbuseIPDB."""
    key = make_cache_key("abuse", ip)
    cached = cache_get(key)
    if cached is not None:
        return cached

    headers = {"Key": ABUSEIPDB_KEY, "Accept": "application/json"}
    params = {"ipAddress": ip, "maxAgeInDays": "90", "verbose": ""}
    session = await get_session()
    async with session.get(
        "https://api.abuseipdb.com/api/v2/check",
        headers=headers,
        params=params
    ) as resp:
        resp.raise_for_status()
        data = await resp.json(content_type=None)

    d = data.get("data", {})
    result = {
        "ip": d.get("ipAddress", ip),
        "is_public": d.get("isPublic", True),
        "abuse_confidence_score": d.get("abuseConfidenceScore", 0),
        "country_code": d.get("countryCode", ""),
        "isp": d.get("isp", ""),
        "domain": d.get("domain", ""),
        "total_reports": d.get("totalReports", 0),
        "num_distinct_users": d.get("numDistinctUsers", 0),
        "last_reported_at": d.get("lastReportedAt", ""),
        "provider": "abuseipdb",
    }
    cache_set(key, result, ttl_seconds=1800)
    return result


# ─── URLScan.io ───────────────────────────────────────────────────────────────

async def urlscan_submit(url_to_scan: str) -> Dict[str, Any]:
    """Submit a URL for scanning to URLScan.io."""
    headers = {"API-Key": URLSCAN_KEY, "Content-Type": "application/json"}
    body = {"url": url_to_scan, "visibility": "public"}
    session = await get_session()
    async with session.post(
        "https://urlscan.io/api/v1/scan/",
        headers=headers,
        json=body
    ) as resp:
        resp.raise_for_status()
        data = await resp.json(content_type=None)

    return {
        "uuid": data.get("uuid", ""),
        "url": data.get("url", url_to_scan),
        "result_url": data.get("result", ""),
        "api_url": data.get("api", ""),
        "visibility": data.get("visibility", ""),
        "provider": "urlscan",
    }


async def urlscan_result(uuid: str) -> Dict[str, Any]:
    """Get URLScan.io scan result."""
    key = make_cache_key("urlscan", "result", uuid)
    cached = cache_get(key)
    if cached is not None:
        return cached

    session = await get_session()
    async with session.get(f"https://urlscan.io/api/v1/result/{uuid}/") as resp:
        if resp.status == 404:
            return {"status": "pending", "uuid": uuid, "provider": "urlscan"}
        resp.raise_for_status()
        data = await resp.json(content_type=None)

    page = data.get("page", {})
    verdicts = data.get("verdicts", {}).get("overall", {})
    result = {
        "uuid": uuid,
        "status": "completed",
        "page": {
            "url": page.get("url", ""),
            "domain": page.get("domain", ""),
            "ip": page.get("ip", ""),
            "country": page.get("country", ""),
            "server": page.get("server", ""),
            "status_code": page.get("status", 0),
        },
        "verdicts": {
            "malicious": verdicts.get("malicious", False),
            "score": verdicts.get("score", 0),
            "categories": verdicts.get("categories", []),
        },
        "screenshot_url": data.get("task", {}).get("screenshotURL", ""),
        "provider": "urlscan",
    }
    cache_set(key, result, ttl_seconds=3600)
    return result


# ─── IP2WHOIS ─────────────────────────────────────────────────────────────────

async def ip2whois_lookup(domain: str) -> Dict[str, Any]:
    """WHOIS lookup for a domain."""
    key = make_cache_key("whois", domain)
    cached = cache_get(key)
    if cached is not None:
        return cached

    params = {"key": IP2WHOIS_KEY, "domain": domain}
    session = await get_session()
    async with session.get("https://api.ip2whois.com/v2", params=params) as resp:
        resp.raise_for_status()
        data = await resp.json(content_type=None)

    data["provider"] = "ip2whois"
    cache_set(key, data, ttl_seconds=86400)
    return data
