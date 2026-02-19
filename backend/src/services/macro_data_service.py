"""
Macro Data Service — FRED, Frankfurter (ECB), Bank of Russia, SEC EDGAR, OpenFIGI

Proxies macroeconomic and regulatory data from five providers.
"""

import os
import xml.etree.ElementTree as ET
from typing import Optional, Dict, Any, List
from src.utils.http_client import get_session

from src.services.cache_service import cache_get, cache_set, make_cache_key

FRED_KEY = os.getenv("FRED_API_KEY", "")
FRED_BASE = "https://api.stlouisfed.org/fred"

FRANKFURTER_BASE = "https://api.frankfurter.app"

CBR_DAILY_URL = "https://www.cbr.ru/scripts/XML_daily.asp"
CBR_KEY_RATE_URL = "https://www.cbr.ru/DailyInfoWebServ/DailyInfo.asmx"

SEC_BASE = "https://data.sec.gov"
SEC_USER_AGENT = os.getenv("SEC_USER_AGENT", "StochasticDashboard/1.0 (contact@example.com)")

OPENFIGI_KEY = os.getenv("OPENFIGI_API_KEY", "")
OPENFIGI_URL = "https://api.openfigi.com/v3/mapping"


# ─── FRED ─────────────────────────────────────────────────────────────────────

async def fred_series_observations(
    series_id: str,
    limit: int = 100,
    sort_order: str = "desc",
    observation_start: Optional[str] = None,
    observation_end: Optional[str] = None,
) -> Dict[str, Any]:
    """Get observations for a FRED series (GDP, CPI, UNRATE, etc.)."""
    key = make_cache_key("fred", "obs", series_id, limit, sort_order, observation_start)
    cached = cache_get(key)
    if cached is not None:
        return cached

    params: Dict[str, Any] = {
        "series_id": series_id,
        "api_key": FRED_KEY,
        "file_type": "json",
        "limit": limit,
        "sort_order": sort_order,
    }
    if observation_start:
        params["observation_start"] = observation_start
    if observation_end:
        params["observation_end"] = observation_end

    session = await get_session()
    async with session.get(f"{FRED_BASE}/series/observations", params=params) as resp:
        resp.raise_for_status()
        data = await resp.json(content_type=None)

    observations = []
    for obs in data.get("observations", []):
        val = obs.get("value", ".")
        observations.append({
            "date": obs.get("date", ""),
            "value": float(val) if val != "." else None,
        })

    result = {
        "series_id": series_id,
        "count": data.get("count", 0),
        "observations": observations,
        "provider": "fred",
    }
    cache_set(key, result, ttl_seconds=3600)
    return result


async def fred_search(query: str, limit: int = 20) -> Dict[str, Any]:
    """Search FRED series by keyword."""
    key = make_cache_key("fred", "search", query, limit)
    cached = cache_get(key)
    if cached is not None:
        return cached

    params = {
        "search_text": query,
        "api_key": FRED_KEY,
        "file_type": "json",
        "limit": limit,
    }
    session = await get_session()
    async with session.get(f"{FRED_BASE}/series/search", params=params) as resp:
        resp.raise_for_status()
        data = await resp.json(content_type=None)

    series_list = []
    for s in data.get("seriess", []):
        series_list.append({
            "id": s.get("id", ""),
            "title": s.get("title", ""),
            "frequency": s.get("frequency", ""),
            "units": s.get("units", ""),
            "observation_start": s.get("observation_start", ""),
            "observation_end": s.get("observation_end", ""),
            "popularity": s.get("popularity", 0),
        })

    result = {"query": query, "series": series_list, "provider": "fred"}
    cache_set(key, result, ttl_seconds=3600)
    return result


# ─── Frankfurter (ECB exchange rates) ────────────────────────────────────────

async def ecb_latest_rates(base: str = "EUR") -> Dict[str, Any]:
    """Get latest ECB exchange rates."""
    key = make_cache_key("ecb", "latest", base)
    cached = cache_get(key)
    if cached is not None:
        return cached

    session = await get_session()
    async with session.get(f"{FRANKFURTER_BASE}/latest", params={"base": base}) as resp:
        resp.raise_for_status()
        data = await resp.json(content_type=None)

    result = {
        "base": data.get("base", base),
        "date": data.get("date", ""),
        "rates": data.get("rates", {}),
        "provider": "frankfurter",
    }
    cache_set(key, result, ttl_seconds=1800)
    return result


async def ecb_historical_rates(
    base: str = "EUR",
    start_date: str = "2024-01-01",
    end_date: Optional[str] = None,
    symbols: Optional[str] = None,
) -> Dict[str, Any]:
    """Get historical ECB exchange rates."""
    key = make_cache_key("ecb", "hist", base, start_date, end_date, symbols)
    cached = cache_get(key)
    if cached is not None:
        return cached

    url = f"{FRANKFURTER_BASE}/{start_date}"
    if end_date:
        url += f"..{end_date}"

    params: Dict[str, Any] = {"base": base}
    if symbols:
        params["symbols"] = symbols

    session = await get_session()
    async with session.get(url, params=params) as resp:
        resp.raise_for_status()
        data = await resp.json(content_type=None)

    result = {
        "base": data.get("base", base),
        "start_date": data.get("start_date", start_date),
        "end_date": data.get("end_date", end_date or ""),
        "rates": data.get("rates", {}),
        "provider": "frankfurter",
    }
    cache_set(key, result, ttl_seconds=1800)
    return result


# ─── Bank of Russia ───────────────────────────────────────────────────────────

async def cbr_daily_rates() -> Dict[str, Any]:
    """Get CBR daily FX rates (parses XML)."""
    key = make_cache_key("cbr", "daily_rates")
    cached = cache_get(key)
    if cached is not None:
        return cached

    session = await get_session()
    async with session.get(CBR_DAILY_URL) as resp:
        resp.raise_for_status()
        raw = await resp.read()

    text = raw.decode("windows-1251")
    root = ET.fromstring(text)

    date_attr = root.attrib.get("Date", "")
    rates = []
    for valute in root.findall("Valute"):
        num_code = valute.findtext("NumCode", "")
        char_code = valute.findtext("CharCode", "")
        nominal = int(valute.findtext("Nominal", "1"))
        name = valute.findtext("Name", "")
        value_str = valute.findtext("Value", "0").replace(",", ".")
        vunit_str = valute.findtext("VunitRate", value_str).replace(",", ".")
        rates.append({
            "num_code": num_code,
            "char_code": char_code,
            "nominal": nominal,
            "name": name,
            "value": float(value_str),
            "vunit_rate": float(vunit_str),
        })

    result = {"date": date_attr, "rates": rates, "provider": "cbr"}
    cache_set(key, result, ttl_seconds=3600)
    return result


async def cbr_key_rate() -> Dict[str, Any]:
    """Get current CBR key rate via SOAP endpoint."""
    key = make_cache_key("cbr", "key_rate")
    cached = cache_get(key)
    if cached is not None:
        return cached

    soap_body = """<?xml version="1.0" encoding="utf-8"?>
    <soap12:Envelope xmlns:soap12="http://www.w3.org/2003/05/soap-envelope"
                     xmlns:web="http://web.cbr.ru/">
      <soap12:Body>
        <web:KeyRateXML>
          <web:fromDate>2024-01-01</web:fromDate>
          <web:ToDate>2026-12-31</web:ToDate>
        </web:KeyRateXML>
      </soap12:Body>
    </soap12:Envelope>"""

    headers = {"Content-Type": "application/soap+xml; charset=utf-8"}
    session = await get_session()
    async with session.post(CBR_KEY_RATE_URL, data=soap_body, headers=headers) as resp:
        resp.raise_for_status()
        text = await resp.text()

    # Parse the SOAP XML response
    history = []
    try:
        root = ET.fromstring(text)
        # Navigate SOAP envelope to find KeyRate elements
        for kr in root.iter():
            if kr.tag.endswith("KR"):
                dt = ""
                rate = 0.0
                for child in kr:
                    if child.tag.endswith("DT"):
                        dt = (child.text or "").strip()
                    elif child.tag.endswith("Rate"):
                        rate = float((child.text or "0").strip())
                if dt:
                    history.append({"date": dt, "rate": rate})
    except ET.ParseError:
        pass

    current_rate = history[-1]["rate"] if history else 0.0

    result = {
        "current_rate": current_rate,
        "history": history,
        "provider": "cbr",
    }
    cache_set(key, result, ttl_seconds=3600)
    return result


# ─── CBR Extended: RUONIA, Precious Metals, Deposit/Credit Rates ─────────────

async def cbr_ruonia(
    from_date: str = "2024-01-01",
    to_date: str = "2026-12-31",
) -> Dict[str, Any]:
    """Get RUONIA rates from CBR SOAP API."""
    key = make_cache_key("cbr", "ruonia", from_date, to_date)
    cached = cache_get(key)
    if cached is not None:
        return cached

    soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
    <soap12:Envelope xmlns:soap12="http://www.w3.org/2003/05/soap-envelope"
                     xmlns:web="http://web.cbr.ru/">
      <soap12:Body>
        <web:RuoniaXML>
          <web:fromDate>{from_date}</web:fromDate>
          <web:ToDate>{to_date}</web:ToDate>
        </web:RuoniaXML>
      </soap12:Body>
    </soap12:Envelope>"""

    headers = {"Content-Type": "application/soap+xml; charset=utf-8"}
    session = await get_session()
    async with session.post(CBR_KEY_RATE_URL, data=soap_body, headers=headers) as resp:
        resp.raise_for_status()
        text = await resp.text()

    rates: List[Dict[str, Any]] = []
    try:
        root = ET.fromstring(text)
        for el in root.iter():
            if el.tag.endswith("ro"):
                dt = ""
                rate = 0.0
                vol = 0.0
                for child in el:
                    tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
                    if tag == "D0":
                        dt = (child.text or "").strip()
                    elif tag == "ruo":
                        rate = float((child.text or "0").strip())
                    elif tag == "vol":
                        vol = float((child.text or "0").strip())
                if dt:
                    rates.append({"date": dt, "rate": rate, "volume": vol})
    except ET.ParseError:
        pass

    current_rate = rates[-1]["rate"] if rates else 0.0
    result = {"current_rate": current_rate, "history": rates, "provider": "cbr"}
    cache_set(key, result, ttl_seconds=3600)
    return result


async def cbr_precious_metals(
    from_date: str = "2024-01-01",
    to_date: str = "2026-12-31",
) -> Dict[str, Any]:
    """Get precious metals prices from CBR SOAP API."""
    key = make_cache_key("cbr", "metals", from_date, to_date)
    cached = cache_get(key)
    if cached is not None:
        return cached

    soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
    <soap12:Envelope xmlns:soap12="http://www.w3.org/2003/05/soap-envelope"
                     xmlns:web="http://web.cbr.ru/">
      <soap12:Body>
        <web:DragMetDynamicXML>
          <web:fromDate>{from_date}</web:fromDate>
          <web:ToDate>{to_date}</web:ToDate>
        </web:DragMetDynamicXML>
      </soap12:Body>
    </soap12:Envelope>"""

    headers = {"Content-Type": "application/soap+xml; charset=utf-8"}
    session = await get_session()
    async with session.post(CBR_KEY_RATE_URL, data=soap_body, headers=headers) as resp:
        resp.raise_for_status()
        text = await resp.text()

    metals: List[Dict[str, Any]] = []
    try:
        root = ET.fromstring(text)
        for el in root.iter():
            if el.tag.endswith("DrgMet"):
                entry: Dict[str, Any] = {}
                for child in el:
                    tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
                    val = (child.text or "").strip()
                    if tag == "DateMet":
                        entry["date"] = val
                    elif tag == "CodMet":
                        entry["code"] = int(val) if val else 0
                    elif tag == "price":
                        entry["price"] = float(val) if val else 0.0
                if entry.get("date"):
                    metals.append(entry)
    except ET.ParseError:
        pass

    # Group by code: 1=Gold, 2=Silver, 3=Platinum, 4=Palladium
    metal_names = {1: "Золото", 2: "Серебро", 3: "Платина", 4: "Палладий"}
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for m in metals:
        name = metal_names.get(m.get("code", 0), f"Metal_{m.get('code')}")
        grouped.setdefault(name, []).append({"date": m["date"], "price": m.get("price", 0)})

    result = {"metals": grouped, "provider": "cbr"}
    cache_set(key, result, ttl_seconds=3600)
    return result


async def cbr_deposit_rates(
    from_date: str = "2024-01-01",
    to_date: str = "2026-12-31",
) -> Dict[str, Any]:
    """Get average deposit rates from CBR SOAP API (DepoDynamicXML)."""
    key = make_cache_key("cbr", "depo_rates", from_date, to_date)
    cached = cache_get(key)
    if cached is not None:
        return cached

    soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
    <soap12:Envelope xmlns:soap12="http://www.w3.org/2003/05/soap-envelope"
                     xmlns:web="http://web.cbr.ru/">
      <soap12:Body>
        <web:DepoDynamicXML>
          <web:fromDate>{from_date}</web:fromDate>
          <web:ToDate>{to_date}</web:ToDate>
        </web:DepoDynamicXML>
      </soap12:Body>
    </soap12:Envelope>"""

    headers = {"Content-Type": "application/soap+xml; charset=utf-8"}
    session = await get_session()
    async with session.post(CBR_KEY_RATE_URL, data=soap_body, headers=headers) as resp:
        resp.raise_for_status()
        text = await resp.text()

    rates: List[Dict[str, Any]] = []
    try:
        root = ET.fromstring(text)
        for el in root.iter():
            if el.tag.endswith("Depo"):
                entry: Dict[str, Any] = {}
                for child in el:
                    tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
                    val = (child.text or "").strip()
                    if tag == "DateDepo":
                        entry["date"] = val
                    elif tag == "Overnight":
                        entry["overnight"] = float(val) if val else None
                if entry.get("date"):
                    rates.append(entry)
    except ET.ParseError:
        pass

    result = {"rates": rates, "provider": "cbr"}
    cache_set(key, result, ttl_seconds=3600)
    return result


async def cbr_repo_rates(
    from_date: str = "2024-01-01",
    to_date: str = "2026-12-31",
) -> Dict[str, Any]:
    """Get repo debt data from CBR SOAP API (RepoDebtXML)."""
    key = make_cache_key("cbr", "repo", from_date, to_date)
    cached = cache_get(key)
    if cached is not None:
        return cached

    soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
    <soap12:Envelope xmlns:soap12="http://www.w3.org/2003/05/soap-envelope"
                     xmlns:web="http://web.cbr.ru/">
      <soap12:Body>
        <web:RepoDebtXML>
          <web:fromDate>{from_date}</web:fromDate>
          <web:ToDate>{to_date}</web:ToDate>
        </web:RepoDebtXML>
      </soap12:Body>
    </soap12:Envelope>"""

    headers = {"Content-Type": "application/soap+xml; charset=utf-8"}
    session = await get_session()
    async with session.post(CBR_KEY_RATE_URL, data=soap_body, headers=headers) as resp:
        resp.raise_for_status()
        text = await resp.text()

    entries: List[Dict[str, Any]] = []
    try:
        root = ET.fromstring(text)
        for el in root.iter():
            if el.tag.endswith("Repo"):
                entry: Dict[str, Any] = {}
                for child in el:
                    tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
                    val = (child.text or "").strip()
                    if tag == "dt":
                        entry["date"] = val
                    elif tag == "debt":
                        entry["debt"] = float(val) if val else 0.0
                    elif tag == "debt_fix":
                        entry["debt_fix"] = float(val) if val else 0.0
                if entry.get("date"):
                    entries.append(entry)
    except ET.ParseError:
        pass

    result = {"entries": entries, "provider": "cbr"}
    cache_set(key, result, ttl_seconds=3600)
    return result


# ─── SEC EDGAR ────────────────────────────────────────────────────────────────

async def sec_company_filings(cik: str) -> Dict[str, Any]:
    """Get SEC company filings by CIK number."""
    cik_padded = cik.zfill(10)
    key = make_cache_key("sec", "filings", cik_padded)
    cached = cache_get(key)
    if cached is not None:
        return cached

    headers = {"User-Agent": SEC_USER_AGENT, "Accept": "application/json"}
    url = f"{SEC_BASE}/submissions/CIK{cik_padded}.json"
    session = await get_session()
    async with session.get(url, headers=headers) as resp:
        resp.raise_for_status()
        data = await resp.json(content_type=None)

    recent = data.get("filings", {}).get("recent", {})
    filings = []
    forms = recent.get("form", [])
    dates = recent.get("filingDate", [])
    descriptions = recent.get("primaryDocDescription", [])
    accessions = recent.get("accessionNumber", [])

    for i in range(min(50, len(forms))):
        filings.append({
            "form": forms[i] if i < len(forms) else "",
            "filing_date": dates[i] if i < len(dates) else "",
            "description": descriptions[i] if i < len(descriptions) else "",
            "accession_number": accessions[i] if i < len(accessions) else "",
        })

    result = {
        "cik": cik_padded,
        "name": data.get("name", ""),
        "tickers": data.get("tickers", []),
        "exchanges": data.get("exchanges", []),
        "sic": data.get("sic", ""),
        "sic_description": data.get("sicDescription", ""),
        "filings": filings,
        "provider": "sec_edgar",
    }
    cache_set(key, result, ttl_seconds=3600)
    return result


async def sec_company_facts(cik: str) -> Dict[str, Any]:
    """Get SEC XBRL company facts."""
    cik_padded = cik.zfill(10)
    key = make_cache_key("sec", "facts", cik_padded)
    cached = cache_get(key)
    if cached is not None:
        return cached

    headers = {"User-Agent": SEC_USER_AGENT, "Accept": "application/json"}
    url = f"{SEC_BASE}/api/xbrl/companyfacts/CIK{cik_padded}.json"
    session = await get_session()
    async with session.get(url, headers=headers) as resp:
        resp.raise_for_status()
        data = await resp.json(content_type=None)

    result = {
        "cik": cik_padded,
        "entity_name": data.get("entityName", ""),
        "facts": data.get("facts", {}),
        "provider": "sec_edgar",
    }
    cache_set(key, result, ttl_seconds=3600)
    return result


async def sec_full_text_search(
    query: str,
    date_range: str = "",
    forms: str = "",
    limit: int = 20,
) -> Dict[str, Any]:
    """Full-text search of SEC EDGAR filings via EFTS."""
    key = make_cache_key("sec", "search", query, date_range, forms, limit)
    cached = cache_get(key)
    if cached is not None:
        return cached

    params: Dict[str, Any] = {
        "q": query,
        "dateRange": date_range or "custom",
        "startdt": "2020-01-01",
        "enddt": "2026-12-31",
    }
    if forms:
        params["forms"] = forms

    headers = {"User-Agent": SEC_USER_AGENT, "Accept": "application/json"}
    session = await get_session()
    async with session.get("https://efts.sec.gov/LATEST/search-index", params=params, headers=headers) as resp:
        resp.raise_for_status()
        data = await resp.json(content_type=None)

    hits = data.get("hits", {}).get("hits", [])
    filings = []
    for hit in hits[:limit]:
        src = hit.get("_source", {})
        filings.append({
            "file_num": src.get("file_num", ""),
            "form_type": src.get("form_type", ""),
            "entity_name": src.get("entity_name", ""),
            "file_date": src.get("file_date", ""),
            "period_of_report": src.get("period_of_report", ""),
            "file_description": src.get("file_description", ""),
            "display_names": src.get("display_names", []),
        })

    result = {"query": query, "total": data.get("hits", {}).get("total", {}).get("value", 0), "filings": filings, "provider": "sec_edgar"}
    cache_set(key, result, ttl_seconds=1800)
    return result


# ─── OpenFIGI ─────────────────────────────────────────────────────────────────

async def openfigi_map(
    jobs: List[Dict[str, str]]
) -> List[Dict[str, Any]]:
    """Map identifiers via OpenFIGI (e.g. ISIN → FIGI).

    Each job: {"idType": "ID_ISIN", "idValue": "US0378331005"}
    """
    key = make_cache_key("figi", str(jobs))
    cached = cache_get(key)
    if cached is not None:
        return cached

    headers: Dict[str, str] = {"Content-Type": "application/json"}
    if OPENFIGI_KEY:
        headers["X-OPENFIGI-APIKEY"] = OPENFIGI_KEY

    session = await get_session()
    async with session.post(OPENFIGI_URL, json=jobs, headers=headers) as resp:
        resp.raise_for_status()
        data = await resp.json(content_type=None)

    result = data if isinstance(data, list) else []
    cache_set(key, result, ttl_seconds=86400)
    return result
