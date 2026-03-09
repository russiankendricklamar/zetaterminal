/**
 * Composable for security tools: IP Lookup, URL Scanner, IP Abuse, WHOIS.
 * Extracted from Settings.vue for reuse in AdminPanel.
 */
import { ref, computed } from 'vue'
import {
  ipInfoLookup,
  ip2LocationLookup,
  bigDataCloudLookup,
  virusTotalScanUrl,
  virusTotalAnalysis,
  abuseIpDbCheck,
  urlScanSubmit,
  urlScanResult as fetchUrlScanResult,
  whoisLookup,
} from '@/services/securityToolsService'
import type {
  IpInfoResult,
  Ip2LocationResult,
  BigDataCloudResult,
  VirusTotalScanResult,
  VirusTotalAnalysis as VTAnalysis,
  AbuseIpDbResult,
  UrlScanSubmitResult,
  UrlScanResult as USResult,
  WhoisResult,
} from '@/services/securityToolsService'

export function useSecurityTools() {
  const securitySubTab = ref('ip-lookup')
  const securityError = ref('')

  const securitySubTabs = [
    { id: 'ip-lookup', name: 'IP Lookup' },
    { id: 'url-scanner', name: 'URL Scanner' },
    { id: 'ip-abuse', name: 'IP Abuse' },
    { id: 'whois', name: 'WHOIS' },
  ]

  // IP Lookup
  const ipInput = ref('')
  const ipLoading = ref(false)
  const ipInfoData = ref<IpInfoResult | null>(null)
  const ip2locData = ref<Ip2LocationResult | null>(null)
  const bdcData = ref<BigDataCloudResult | null>(null)
  const hasIpResults = computed(() => ipInfoData.value || ip2locData.value || bdcData.value)

  async function runIpLookup() {
    const ip = ipInput.value.trim()
    if (!ip) return
    ipLoading.value = true
    securityError.value = ''
    ipInfoData.value = null
    ip2locData.value = null
    bdcData.value = null
    try {
      const [r1, r2, r3] = await Promise.allSettled([
        ipInfoLookup(ip),
        ip2LocationLookup(ip),
        bigDataCloudLookup(ip),
      ])
      ipInfoData.value = r1.status === 'fulfilled' ? r1.value : null
      ip2locData.value = r2.status === 'fulfilled' ? r2.value : null
      bdcData.value = r3.status === 'fulfilled' ? r3.value : null
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : String(e)
      securityError.value = `IP Lookup failed: ${msg}`
    } finally {
      ipLoading.value = false
    }
  }

  function formatCoords(lat?: number, lng?: number): string {
    if (lat == null || lng == null) return '---'
    return `${lat.toFixed(4)}, ${lng.toFixed(4)}`
  }

  // URL Scanner
  const urlInput = ref('')
  const urlLoading = ref(false)
  const vtScan = ref<VirusTotalScanResult | null>(null)
  const vtAnalysisData = ref<VTAnalysis | null>(null)
  const vtPolling = ref(false)
  const vtPollCount = ref(0)
  const urlScanData = ref<UrlScanSubmitResult | null>(null)
  const urlScanResultData = ref<USResult | null>(null)
  const urlScanPolling = ref(false)
  const urlScanPollCount = ref(0)

  async function runUrlScan() {
    const url = urlInput.value.trim()
    if (!url) return
    urlLoading.value = true
    securityError.value = ''
    vtScan.value = null
    vtAnalysisData.value = null
    vtPolling.value = false
    vtPollCount.value = 0
    urlScanData.value = null
    urlScanResultData.value = null
    urlScanPolling.value = false
    urlScanPollCount.value = 0

    try {
      const [vtResult, usResult] = await Promise.allSettled([
        virusTotalScanUrl(url),
        urlScanSubmit(url),
      ])
      if (vtResult.status === 'fulfilled') {
        vtScan.value = vtResult.value
        pollVirusTotal(vtResult.value.analysis_id)
      } else {
        securityError.value = `VirusTotal submit failed: ${vtResult.reason}`
      }
      if (usResult.status === 'fulfilled') {
        urlScanData.value = usResult.value
        pollUrlScan(usResult.value.uuid)
      } else {
        const existing = securityError.value
        const usErr = `URLScan submit failed: ${usResult.reason}`
        securityError.value = existing ? `${existing} | ${usErr}` : usErr
      }
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : String(e)
      securityError.value = `URL Scan failed: ${msg}`
    } finally {
      urlLoading.value = false
    }
  }

  function pollVirusTotal(analysisId: string) {
    vtPolling.value = true
    vtPollCount.value = 0
    const maxSeconds = 60
    const intervalMs = 5000
    const timer = setInterval(async () => {
      vtPollCount.value += 5
      try {
        const result = await virusTotalAnalysis(analysisId)
        if (result.status === 'completed' || vtPollCount.value >= maxSeconds) {
          vtAnalysisData.value = result
          vtPolling.value = false
          clearInterval(timer)
        }
      } catch {
        if (vtPollCount.value >= maxSeconds) {
          vtPolling.value = false
          clearInterval(timer)
        }
      }
    }, intervalMs)
  }

  function pollUrlScan(uuid: string) {
    urlScanPolling.value = true
    urlScanPollCount.value = 0
    const maxSeconds = 60
    const intervalMs = 5000
    const timer = setInterval(async () => {
      urlScanPollCount.value += 5
      try {
        const result = await fetchUrlScanResult(uuid)
        if (result.status === 'completed' || urlScanPollCount.value >= maxSeconds) {
          urlScanResultData.value = result
          urlScanPolling.value = false
          clearInterval(timer)
        }
      } catch {
        if (urlScanPollCount.value >= maxSeconds) {
          urlScanPolling.value = false
          clearInterval(timer)
        }
      }
    }, intervalMs)
  }

  // IP Abuse
  const abuseIpInput = ref('')
  const abuseLoading = ref(false)
  const abuseResult = ref<AbuseIpDbResult | null>(null)
  const abuseScoreColor = computed(() => {
    if (!abuseResult.value) return 'rgba(255,255,255,0.4)'
    const score = abuseResult.value.abuse_confidence_score
    if (score <= 25) return '#4ade80'
    if (score <= 50) return '#facc15'
    if (score <= 75) return '#fb923c'
    return '#ef4444'
  })

  async function runAbuseCheck() {
    const ip = abuseIpInput.value.trim()
    if (!ip) return
    abuseLoading.value = true
    securityError.value = ''
    abuseResult.value = null
    try {
      abuseResult.value = await abuseIpDbCheck(ip)
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : String(e)
      securityError.value = `Abuse check failed: ${msg}`
    } finally {
      abuseLoading.value = false
    }
  }

  // WHOIS
  const whoisInput = ref('')
  const whoisLoading = ref(false)
  const whoisResult = ref<WhoisResult | null>(null)

  async function runWhois() {
    const domain = whoisInput.value.trim()
    if (!domain) return
    whoisLoading.value = true
    securityError.value = ''
    whoisResult.value = null
    try {
      whoisResult.value = await whoisLookup(domain)
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : String(e)
      securityError.value = `WHOIS lookup failed: ${msg}`
    } finally {
      whoisLoading.value = false
    }
  }

  return {
    securitySubTab,
    securityError,
    securitySubTabs,
    // IP Lookup
    ipInput, ipLoading, ipInfoData, ip2locData, bdcData, hasIpResults,
    runIpLookup, formatCoords,
    // URL Scanner
    urlInput, urlLoading, vtScan, vtAnalysisData, vtPolling, vtPollCount,
    urlScanData, urlScanResultData, urlScanPolling, urlScanPollCount,
    runUrlScan,
    // IP Abuse
    abuseIpInput, abuseLoading, abuseResult, abuseScoreColor,
    runAbuseCheck,
    // WHOIS
    whoisInput, whoisLoading, whoisResult,
    runWhois,
  }
}
