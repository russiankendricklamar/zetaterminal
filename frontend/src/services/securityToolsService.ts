/**
 * Security Tools Service — VirusTotal, AbuseIPDB, URLScan.io, IP2WHOIS,
 *                          ipinfo.io, IP2Location, BigDataCloud
 *
 * Network security and IP intelligence utilities.
 */

const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

async function fetchJson<T>(url: string): Promise<T> {
  const resp = await fetch(url)
  if (!resp.ok) throw new Error(`HTTP ${resp.status}: ${resp.statusText}`)
  return resp.json()
}

async function postJson<T>(url: string, body: unknown): Promise<T> {
  const resp = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!resp.ok) throw new Error(`HTTP ${resp.status}: ${resp.statusText}`)
  return resp.json()
}

// ─── Types ──────────────────────────────────────────────────────────────────

export interface IpInfoResult {
  ip: string
  hostname?: string
  city?: string
  region?: string
  country?: string
  loc?: string
  org?: string
  postal?: string
  timezone?: string
  provider: 'ipinfo'
}

export interface Ip2LocationResult {
  ip: string
  country_code?: string
  country_name?: string
  region_name?: string
  city_name?: string
  latitude?: number
  longitude?: number
  zip_code?: string
  time_zone?: string
  asn?: string
  as?: string
  is_proxy?: boolean
  provider: 'ip2location'
}

export interface BigDataCloudResult {
  ip?: string
  localityLanguageRequested?: string
  country?: { isoAlpha2: string; name: string }
  city?: { name: string }
  location?: { latitude: number; longitude: number }
  network?: { organisation: string }
  provider: 'bigdatacloud'
}

export interface VirusTotalScanResult {
  analysis_id: string
  type: string
  url: string
  provider: 'virustotal'
}

export interface VirusTotalAnalysis {
  analysis_id: string
  status: string
  stats: {
    malicious: number
    suspicious: number
    harmless: number
    undetected: number
    timeout: number
  }
  provider: 'virustotal'
}

export interface AbuseIpDbResult {
  ip: string
  is_public: boolean
  abuse_confidence_score: number
  country_code: string
  isp: string
  domain: string
  total_reports: number
  num_distinct_users: number
  last_reported_at: string
  provider: 'abuseipdb'
}

export interface UrlScanSubmitResult {
  uuid: string
  url: string
  result_url: string
  api_url: string
  visibility: string
  provider: 'urlscan'
}

export interface UrlScanResult {
  uuid: string
  status: 'pending' | 'completed'
  page?: {
    url: string
    domain: string
    ip: string
    country: string
    server: string
    status_code: number
  }
  verdicts?: {
    malicious: boolean
    score: number
    categories: string[]
  }
  screenshot_url?: string
  provider: 'urlscan'
}

export interface WhoisResult {
  domain?: string
  domain_id?: string
  status?: string
  create_date?: string
  update_date?: string
  expire_date?: string
  registrar?: { name: string }
  registrant?: { organization: string; country: string }
  nameservers?: string[]
  provider: 'ip2whois'
  [key: string]: unknown
}

// ─── IP Geolocation ─────────────────────────────────────────────────────────

export function ipInfoLookup(ip: string): Promise<IpInfoResult> {
  return fetchJson(`${API_BASE}/api/security/ipinfo/${encodeURIComponent(ip)}`)
}

export function ip2LocationLookup(ip: string): Promise<Ip2LocationResult> {
  return fetchJson(`${API_BASE}/api/security/ip2location/${encodeURIComponent(ip)}`)
}

export function bigDataCloudLookup(ip: string): Promise<BigDataCloudResult> {
  return fetchJson(`${API_BASE}/api/security/bigdatacloud/${encodeURIComponent(ip)}`)
}

// ─── VirusTotal ─────────────────────────────────────────────────────────────

export function virusTotalScanUrl(url: string): Promise<VirusTotalScanResult> {
  return postJson(`${API_BASE}/api/security/virustotal/scan-url`, { url })
}

export function virusTotalAnalysis(analysisId: string): Promise<VirusTotalAnalysis> {
  return fetchJson(`${API_BASE}/api/security/virustotal/analysis/${encodeURIComponent(analysisId)}`)
}

// ─── AbuseIPDB ──────────────────────────────────────────────────────────────

export function abuseIpDbCheck(ip: string): Promise<AbuseIpDbResult> {
  return fetchJson(`${API_BASE}/api/security/abuseipdb/${encodeURIComponent(ip)}`)
}

// ─── URLScan.io ─────────────────────────────────────────────────────────────

export function urlScanSubmit(url: string): Promise<UrlScanSubmitResult> {
  return postJson(`${API_BASE}/api/security/urlscan/submit`, { url })
}

export function urlScanResult(uuid: string): Promise<UrlScanResult> {
  return fetchJson(`${API_BASE}/api/security/urlscan/result/${encodeURIComponent(uuid)}`)
}

// ─── IP2WHOIS ───────────────────────────────────────────────────────────────

export function whoisLookup(domain: string): Promise<WhoisResult> {
  return fetchJson(`${API_BASE}/api/security/whois/${encodeURIComponent(domain)}`)
}
