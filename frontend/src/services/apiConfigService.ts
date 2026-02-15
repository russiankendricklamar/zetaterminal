/**
 * API Config Service — Health checks and key status management
 *
 * Provides utilities for the Settings page API key management tab.
 */

import { getApiHeaders } from '@/utils/apiHeaders'

const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

export interface ApiKeyConfig {
  key: string
  label: string
  group: string
  required: boolean
  placeholder: string
}

/**
 * All managed API keys, grouped by category.
 */
export const API_KEYS_CONFIG: ApiKeyConfig[] = [
  // Market Data
  { key: 'alphaVantageKey', label: 'Alpha Vantage', group: 'Market Data', required: false, placeholder: 'your_alpha_vantage_key' },
  { key: 'twelveDataKey', label: 'Twelve Data', group: 'Market Data', required: false, placeholder: 'your_twelve_data_key' },
  { key: 'polygonKey', label: 'Polygon.io', group: 'Market Data', required: false, placeholder: 'your_polygon_key' },
  // Macro
  { key: 'fredKey', label: 'FRED API', group: 'Macro', required: false, placeholder: 'your_fred_key' },
  { key: 'openFigiKey', label: 'OpenFIGI', group: 'Macro', required: false, placeholder: 'optional_openfigi_key' },
  // Crypto
  { key: 'coinGeckoKey', label: 'CoinGecko', group: 'Crypto', required: false, placeholder: 'optional_pro_key' },
  { key: 'coinGapKey', label: 'CoinGap', group: 'Crypto', required: false, placeholder: 'your_coingap_key' },
  // News & AI
  { key: 'newsApiKey', label: 'NewsAPI', group: 'News & AI', required: false, placeholder: 'your_newsapi_key' },
  { key: 'currentsKey', label: 'Currents API', group: 'News & AI', required: false, placeholder: 'your_currents_key' },
  { key: 'huggingFaceToken', label: 'Hugging Face', group: 'News & AI', required: false, placeholder: 'hf_your_token' },
  // Security
  { key: 'virusTotalKey', label: 'VirusTotal', group: 'Security', required: false, placeholder: 'your_virustotal_key' },
  { key: 'abuseIpDbKey', label: 'AbuseIPDB', group: 'Security', required: false, placeholder: 'your_abuseipdb_key' },
  { key: 'urlScanKey', label: 'URLScan.io', group: 'Security', required: false, placeholder: 'your_urlscan_key' },
  { key: 'ip2WhoisKey', label: 'IP2WHOIS', group: 'Security', required: false, placeholder: 'your_ip2whois_key' },
  { key: 'ipInfoToken', label: 'ipinfo.io', group: 'Security', required: false, placeholder: 'your_ipinfo_token' },
  { key: 'ip2LocationKey', label: 'IP2Location', group: 'Security', required: false, placeholder: 'your_ip2location_key' },
  // Auth
  { key: 'auth0Domain', label: 'Auth0 Domain', group: 'Auth', required: false, placeholder: 'tenant.auth0.com' },
  { key: 'auth0ClientId', label: 'Auth0 Client ID', group: 'Auth', required: false, placeholder: 'client_id' },
  { key: 'auth0ClientSecret', label: 'Auth0 Secret', group: 'Auth', required: false, placeholder: 'client_secret' },
  { key: 'warrantKey', label: 'Warrant', group: 'Auth', required: false, placeholder: 'your_warrant_key' },
  { key: 'stytchProjectId', label: 'Stytch Project ID', group: 'Auth', required: false, placeholder: 'project-live-xxx' },
  { key: 'stytchSecret', label: 'Stytch Secret', group: 'Auth', required: false, placeholder: 'secret-live-xxx' },
  { key: 'mojoAuthKey', label: 'MojoAuth', group: 'Auth', required: false, placeholder: 'your_mojoauth_key' },
  // Email
  { key: 'sendgridKey', label: 'Sendgrid', group: 'Email', required: false, placeholder: 'SG.your_key' },
  { key: 'mailboxValidatorKey', label: 'MailboxValidator', group: 'Email', required: false, placeholder: 'your_mbv_key' },
  // Storage
  { key: 'jsonBinKey', label: 'JSONbin.io', group: 'Storage', required: false, placeholder: 'your_jsonbin_key' },
  { key: 'pantryBasketId', label: 'Pantry Basket ID', group: 'Storage', required: false, placeholder: 'your_pantry_id' },
  { key: 'pastebinKey', label: 'Pastebin', group: 'Storage', required: false, placeholder: 'your_pastebin_key' },
  // Media
  { key: 'cloudinaryCloudName', label: 'Cloudinary Cloud', group: 'Media', required: false, placeholder: 'your_cloud' },
  { key: 'cloudinaryApiKey', label: 'Cloudinary Key', group: 'Media', required: false, placeholder: 'your_key' },
  { key: 'cloudConvertKey', label: 'CloudConvert', group: 'Media', required: false, placeholder: 'your_cc_key' },
  // Business
  { key: 'lobKey', label: 'Lob.com', group: 'Business', required: false, placeholder: 'your_lob_key' },
  { key: 'vatLayerKey', label: 'vatlayer', group: 'Business', required: false, placeholder: 'your_vatlayer_key' },
  { key: 'klarnaUser', label: 'Klarna Username', group: 'Business', required: false, placeholder: 'your_klarna_user' },
  // Developer
  { key: 'githubToken', label: 'GitHub Token', group: 'Developer', required: false, placeholder: 'ghp_your_token' },
]

const STORAGE_KEY = 'api_keys_config'

/**
 * Save API keys to localStorage.
 */
export function saveApiKeys(keys: Record<string, string>): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(keys))
}

/**
 * Load API keys from localStorage.
 */
export function loadApiKeys(): Record<string, string> {
  const raw = localStorage.getItem(STORAGE_KEY)
  if (!raw) return {}
  try {
    return JSON.parse(raw)
  } catch {
    return {}
  }
}

/**
 * Get unique group names from the config.
 */
export function getApiKeyGroups(): string[] {
  const groups = new Set(API_KEYS_CONFIG.map(c => c.group))
  return Array.from(groups)
}

/**
 * Get keys for a specific group.
 */
export function getKeysForGroup(group: string): ApiKeyConfig[] {
  return API_KEYS_CONFIG.filter(c => c.group === group)
}

/**
 * Check backend health endpoints for all API services.
 */
export async function checkAllApiHealth(): Promise<Record<string, boolean>> {
  const services = [
    'market-feeds', 'macro-data', 'crypto-data', 'news-ai',
    'calendar', 'security',
  ]
  const results: Record<string, boolean> = {}

  await Promise.all(services.map(async (svc) => {
    try {
      const resp = await fetch(`${API_BASE}/api/${svc}/health`, { headers: getApiHeaders() })
      results[svc] = resp.ok
    } catch {
      results[svc] = false
    }
  }))

  return results
}
