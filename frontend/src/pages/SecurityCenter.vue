<!-- src/pages/SecurityCenter.vue — Security Tools: IP Lookup, URL Scanner, IP Abuse, WHOIS -->
<template>
  <div class="page-container">
    <!-- Header -->
    <div class="section-header">
      <div class="header-left">
        <h1 class="section-title">Security Center</h1>
        <p class="section-subtitle">IP Geolocation / URL Scanner / Abuse Check / WHOIS</p>
      </div>
    </div>

    <!-- Tab Bar -->
    <div class="tabs-navigation">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        class="tab-item"
        :class="{ active: activeTab === tab.id }"
        @click="activeTab = tab.id"
      >
        {{ tab.name }}
      </button>
    </div>

    <!-- Error Banner -->
    <div v-if="error" class="error-banner">{{ error }}</div>

    <!-- TAB 1: IP Lookup -->
    <div v-show="activeTab === 'ip-lookup'" class="tab-content">
      <div class="input-row">
        <input
          v-model="ipInput"
          class="security-input"
          placeholder="Enter IP address (e.g. 8.8.8.8)"
          @keyup.enter="runIpLookup"
        />
        <button class="btn-submit" :disabled="ipLoading || !ipInput.trim()" @click="runIpLookup">
          {{ ipLoading ? 'LOADING...' : 'LOOKUP' }}
        </button>
      </div>

      <div v-if="ipLoading" class="loading-text">LOADING...</div>

      <div v-if="hasIpResults" class="results-grid three-col">
        <!-- ipinfo.io -->
        <div v-if="ipInfoData" class="glass-card">
          <h3 class="card-title">IPINFO.IO</h3>
          <div class="result-fields">
            <div class="field-row"><span class="field-label">IP</span><span class="field-value">{{ ipInfoData.ip }}</span></div>
            <div class="field-row"><span class="field-label">COUNTRY</span><span class="field-value">{{ ipInfoData.country || '---' }}</span></div>
            <div class="field-row"><span class="field-label">CITY</span><span class="field-value">{{ ipInfoData.city || '---' }}</span></div>
            <div class="field-row"><span class="field-label">REGION</span><span class="field-value">{{ ipInfoData.region || '---' }}</span></div>
            <div class="field-row"><span class="field-label">ORG</span><span class="field-value">{{ ipInfoData.org || '---' }}</span></div>
            <div class="field-row"><span class="field-label">COORDINATES</span><span class="field-value">{{ ipInfoData.loc || '---' }}</span></div>
            <div class="field-row"><span class="field-label">TIMEZONE</span><span class="field-value">{{ ipInfoData.timezone || '---' }}</span></div>
            <div class="field-row"><span class="field-label">HOSTNAME</span><span class="field-value">{{ ipInfoData.hostname || '---' }}</span></div>
          </div>
        </div>

        <!-- ip2location -->
        <div v-if="ip2locData" class="glass-card">
          <h3 class="card-title">IP2LOCATION</h3>
          <div class="result-fields">
            <div class="field-row"><span class="field-label">IP</span><span class="field-value">{{ ip2locData.ip }}</span></div>
            <div class="field-row"><span class="field-label">COUNTRY</span><span class="field-value">{{ ip2locData.country_name || '---' }} ({{ ip2locData.country_code || '' }})</span></div>
            <div class="field-row"><span class="field-label">CITY</span><span class="field-value">{{ ip2locData.city_name || '---' }}</span></div>
            <div class="field-row"><span class="field-label">REGION</span><span class="field-value">{{ ip2locData.region_name || '---' }}</span></div>
            <div class="field-row"><span class="field-label">ISP / AS</span><span class="field-value">{{ ip2locData.as || '---' }}</span></div>
            <div class="field-row"><span class="field-label">COORDINATES</span><span class="field-value">{{ formatCoords(ip2locData.latitude, ip2locData.longitude) }}</span></div>
            <div class="field-row"><span class="field-label">TIMEZONE</span><span class="field-value">{{ ip2locData.time_zone || '---' }}</span></div>
            <div class="field-row"><span class="field-label">PROXY</span><span class="field-value">{{ ip2locData.is_proxy ? 'YES' : 'NO' }}</span></div>
          </div>
        </div>

        <!-- bigdatacloud -->
        <div v-if="bdcData" class="glass-card">
          <h3 class="card-title">BIGDATACLOUD</h3>
          <div class="result-fields">
            <div class="field-row"><span class="field-label">IP</span><span class="field-value">{{ bdcData.ip || '---' }}</span></div>
            <div class="field-row"><span class="field-label">COUNTRY</span><span class="field-value">{{ bdcData.country?.name || '---' }} ({{ bdcData.country?.isoAlpha2 || '' }})</span></div>
            <div class="field-row"><span class="field-label">CITY</span><span class="field-value">{{ bdcData.city?.name || '---' }}</span></div>
            <div class="field-row"><span class="field-label">ORGANISATION</span><span class="field-value">{{ bdcData.network?.organisation || '---' }}</span></div>
            <div class="field-row"><span class="field-label">COORDINATES</span><span class="field-value">{{ formatCoords(bdcData.location?.latitude, bdcData.location?.longitude) }}</span></div>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 2: URL Scanner -->
    <div v-show="activeTab === 'url-scanner'" class="tab-content">
      <div class="input-row">
        <input
          v-model="urlInput"
          class="security-input"
          placeholder="Enter URL (e.g. https://example.com)"
          @keyup.enter="runUrlScan"
        />
        <button class="btn-submit" :disabled="urlLoading || !urlInput.trim()" @click="runUrlScan">
          {{ urlLoading ? 'SCANNING...' : 'SCAN' }}
        </button>
      </div>

      <div v-if="urlLoading" class="loading-text">SCANNING URL...</div>

      <div v-if="vtScan || urlScanData" class="results-grid two-col">
        <!-- VirusTotal -->
        <div class="glass-card">
          <h3 class="card-title">VIRUSTOTAL</h3>
          <div v-if="vtPolling" class="polling-text">POLLING ANALYSIS... ({{ vtPollCount }}s)</div>
          <div v-if="vtAnalysisData" class="result-fields">
            <div class="field-row">
              <span class="field-label">STATUS</span>
              <span class="field-value">{{ vtAnalysisData.status.toUpperCase() }}</span>
            </div>
            <div class="field-row">
              <span class="field-label">MALICIOUS</span>
              <span class="field-value vt-malicious">{{ vtAnalysisData.stats.malicious }}</span>
            </div>
            <div class="field-row">
              <span class="field-label">SUSPICIOUS</span>
              <span class="field-value vt-suspicious">{{ vtAnalysisData.stats.suspicious }}</span>
            </div>
            <div class="field-row">
              <span class="field-label">HARMLESS</span>
              <span class="field-value vt-harmless">{{ vtAnalysisData.stats.harmless }}</span>
            </div>
            <div class="field-row">
              <span class="field-label">UNDETECTED</span>
              <span class="field-value">{{ vtAnalysisData.stats.undetected }}</span>
            </div>
            <div class="field-row">
              <span class="field-label">TIMEOUT</span>
              <span class="field-value">{{ vtAnalysisData.stats.timeout }}</span>
            </div>
          </div>
          <div v-else-if="vtScan && !vtPolling" class="result-fields">
            <div class="field-row">
              <span class="field-label">ANALYSIS ID</span>
              <span class="field-value text-truncate">{{ vtScan.analysis_id }}</span>
            </div>
          </div>
        </div>

        <!-- URLScan.io -->
        <div class="glass-card">
          <h3 class="card-title">URLSCAN.IO</h3>
          <div v-if="urlScanPolling" class="polling-text">POLLING RESULT... ({{ urlScanPollCount }}s)</div>
          <div v-if="urlScanResultData" class="result-fields">
            <div v-if="urlScanResultData.page" class="result-section">
              <div class="field-row">
                <span class="field-label">DOMAIN</span>
                <span class="field-value">{{ urlScanResultData.page.domain }}</span>
              </div>
              <div class="field-row">
                <span class="field-label">IP</span>
                <span class="field-value">{{ urlScanResultData.page.ip }}</span>
              </div>
              <div class="field-row">
                <span class="field-label">COUNTRY</span>
                <span class="field-value">{{ urlScanResultData.page.country }}</span>
              </div>
              <div class="field-row">
                <span class="field-label">SERVER</span>
                <span class="field-value">{{ urlScanResultData.page.server }}</span>
              </div>
              <div class="field-row">
                <span class="field-label">STATUS CODE</span>
                <span class="field-value">{{ urlScanResultData.page.status_code }}</span>
              </div>
            </div>
            <div v-if="urlScanResultData.verdicts" class="result-section">
              <div class="field-row">
                <span class="field-label">MALICIOUS</span>
                <span class="field-value" :class="urlScanResultData.verdicts.malicious ? 'text-danger' : 'text-safe'">
                  {{ urlScanResultData.verdicts.malicious ? 'YES' : 'NO' }}
                </span>
              </div>
              <div class="field-row">
                <span class="field-label">SCORE</span>
                <span class="field-value">{{ urlScanResultData.verdicts.score }}</span>
              </div>
              <div v-if="urlScanResultData.verdicts.categories.length" class="field-row">
                <span class="field-label">CATEGORIES</span>
                <span class="field-value">{{ urlScanResultData.verdicts.categories.join(', ') }}</span>
              </div>
            </div>
          </div>
          <div v-else-if="urlScanData && !urlScanPolling" class="result-fields">
            <div class="field-row">
              <span class="field-label">UUID</span>
              <span class="field-value text-truncate">{{ urlScanData.uuid }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 3: IP Abuse -->
    <div v-show="activeTab === 'ip-abuse'" class="tab-content">
      <div class="input-row">
        <input
          v-model="abuseIpInput"
          class="security-input"
          placeholder="Enter IP address to check abuse reports"
          @keyup.enter="runAbuseCheck"
        />
        <button class="btn-submit" :disabled="abuseLoading || !abuseIpInput.trim()" @click="runAbuseCheck">
          {{ abuseLoading ? 'LOADING...' : 'CHECK' }}
        </button>
      </div>

      <div v-if="abuseLoading" class="loading-text">LOADING...</div>

      <div v-if="abuseResult" class="results-grid single-col">
        <div class="glass-card">
          <h3 class="card-title">ABUSEIPDB REPORT</h3>
          <div class="abuse-score-wrap">
            <div class="abuse-score-circle" :style="{ borderColor: abuseScoreColor }">
              <span class="abuse-score-value" :style="{ color: abuseScoreColor }">{{ abuseResult.abuse_confidence_score }}</span>
              <span class="abuse-score-label">CONFIDENCE</span>
            </div>
          </div>
          <div class="result-fields">
            <div class="field-row">
              <span class="field-label">IP</span>
              <span class="field-value">{{ abuseResult.ip }}</span>
            </div>
            <div class="field-row">
              <span class="field-label">PUBLIC</span>
              <span class="field-value">{{ abuseResult.is_public ? 'YES' : 'NO' }}</span>
            </div>
            <div class="field-row">
              <span class="field-label">ABUSE SCORE</span>
              <span class="field-value" :style="{ color: abuseScoreColor }">{{ abuseResult.abuse_confidence_score }}%</span>
            </div>
            <div class="field-row">
              <span class="field-label">TOTAL REPORTS</span>
              <span class="field-value">{{ abuseResult.total_reports }}</span>
            </div>
            <div class="field-row">
              <span class="field-label">DISTINCT USERS</span>
              <span class="field-value">{{ abuseResult.num_distinct_users }}</span>
            </div>
            <div class="field-row">
              <span class="field-label">ISP</span>
              <span class="field-value">{{ abuseResult.isp || '---' }}</span>
            </div>
            <div class="field-row">
              <span class="field-label">DOMAIN</span>
              <span class="field-value">{{ abuseResult.domain || '---' }}</span>
            </div>
            <div class="field-row">
              <span class="field-label">COUNTRY</span>
              <span class="field-value">{{ abuseResult.country_code || '---' }}</span>
            </div>
            <div class="field-row">
              <span class="field-label">LAST REPORTED</span>
              <span class="field-value">{{ abuseResult.last_reported_at || 'NEVER' }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 4: WHOIS -->
    <div v-show="activeTab === 'whois'" class="tab-content">
      <div class="input-row">
        <input
          v-model="whoisInput"
          class="security-input"
          placeholder="Enter domain (e.g. example.com)"
          @keyup.enter="runWhois"
        />
        <button class="btn-submit" :disabled="whoisLoading || !whoisInput.trim()" @click="runWhois">
          {{ whoisLoading ? 'LOADING...' : 'LOOKUP' }}
        </button>
      </div>

      <div v-if="whoisLoading" class="loading-text">LOADING...</div>

      <div v-if="whoisResult" class="results-grid single-col">
        <div class="glass-card">
          <h3 class="card-title">WHOIS — {{ whoisResult.domain || whoisInput }}</h3>
          <div class="result-fields">
            <div class="field-row">
              <span class="field-label">DOMAIN</span>
              <span class="field-value">{{ whoisResult.domain || '---' }}</span>
            </div>
            <div class="field-row">
              <span class="field-label">DOMAIN ID</span>
              <span class="field-value">{{ whoisResult.domain_id || '---' }}</span>
            </div>
            <div class="field-row">
              <span class="field-label">STATUS</span>
              <span class="field-value">{{ whoisResult.status || '---' }}</span>
            </div>
            <div class="field-row">
              <span class="field-label">REGISTRAR</span>
              <span class="field-value">{{ whoisResult.registrar?.name || '---' }}</span>
            </div>
            <div class="field-row">
              <span class="field-label">CREATED</span>
              <span class="field-value">{{ whoisResult.create_date || '---' }}</span>
            </div>
            <div class="field-row">
              <span class="field-label">UPDATED</span>
              <span class="field-value">{{ whoisResult.update_date || '---' }}</span>
            </div>
            <div class="field-row">
              <span class="field-label">EXPIRES</span>
              <span class="field-value">{{ whoisResult.expire_date || '---' }}</span>
            </div>
            <div v-if="whoisResult.registrant" class="field-row">
              <span class="field-label">REGISTRANT ORG</span>
              <span class="field-value">{{ whoisResult.registrant.organization || '---' }}</span>
            </div>
            <div v-if="whoisResult.registrant" class="field-row">
              <span class="field-label">REGISTRANT COUNTRY</span>
              <span class="field-value">{{ whoisResult.registrant.country || '---' }}</span>
            </div>
            <div v-if="whoisResult.nameservers && whoisResult.nameservers.length" class="field-row">
              <span class="field-label">NAMESERVERS</span>
              <div class="field-value nameserver-list">
                <span v-for="ns in whoisResult.nameservers" :key="ns" class="ns-item">{{ ns }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import {
  ipInfoLookup,
  ip2LocationLookup,
  bigDataCloudLookup,
  virusTotalScanUrl,
  virusTotalAnalysis,
  abuseIpDbCheck,
  urlScanSubmit,
  urlScanResult,
  whoisLookup,
} from '@/services/securityToolsService'
import type {
  IpInfoResult,
  Ip2LocationResult,
  BigDataCloudResult,
  VirusTotalScanResult,
  VirusTotalAnalysis,
  AbuseIpDbResult,
  UrlScanSubmitResult,
  UrlScanResult,
  WhoisResult,
} from '@/services/securityToolsService'

// ─── Tabs ───────────────────────────────────────────────────────────────────
const tabs = [
  { id: 'ip-lookup', name: 'IP Lookup' },
  { id: 'url-scanner', name: 'URL Scanner' },
  { id: 'ip-abuse', name: 'IP Abuse' },
  { id: 'whois', name: 'WHOIS' },
]
const activeTab = ref('ip-lookup')
const error = ref('')

// ─── IP Lookup ──────────────────────────────────────────────────────────────
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
  error.value = ''
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
    error.value = `IP Lookup failed: ${msg}`
  } finally {
    ipLoading.value = false
  }
}

function formatCoords(lat?: number, lng?: number): string {
  if (lat == null || lng == null) return '---'
  return `${lat.toFixed(4)}, ${lng.toFixed(4)}`
}

// ─── URL Scanner ────────────────────────────────────────────────────────────
const urlInput = ref('')
const urlLoading = ref(false)

const vtScan = ref<VirusTotalScanResult | null>(null)
const vtAnalysisData = ref<VirusTotalAnalysis | null>(null)
const vtPolling = ref(false)
const vtPollCount = ref(0)

const urlScanData = ref<UrlScanSubmitResult | null>(null)
const urlScanResultData = ref<UrlScanResult | null>(null)
const urlScanPolling = ref(false)
const urlScanPollCount = ref(0)

async function runUrlScan() {
  const url = urlInput.value.trim()
  if (!url) return
  urlLoading.value = true
  error.value = ''
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
      error.value = `VirusTotal submit failed: ${vtResult.reason}`
    }

    if (usResult.status === 'fulfilled') {
      urlScanData.value = usResult.value
      pollUrlScan(usResult.value.uuid)
    } else {
      const existing = error.value
      const usErr = `URLScan submit failed: ${usResult.reason}`
      error.value = existing ? `${existing} | ${usErr}` : usErr
    }
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : String(e)
    error.value = `URL Scan failed: ${msg}`
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
      const result = await urlScanResult(uuid)
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

// ─── IP Abuse ───────────────────────────────────────────────────────────────
const abuseIpInput = ref('')
const abuseLoading = ref(false)
const abuseResult = ref<AbuseIpDbResult | null>(null)

const abuseScoreColor = computed(() => {
  if (!abuseResult.value) return '#666'
  const score = abuseResult.value.abuse_confidence_score
  if (score <= 25) return '#22C55E'
  if (score <= 50) return '#EAB308'
  if (score <= 75) return '#F97316'
  return '#DC2626'
})

async function runAbuseCheck() {
  const ip = abuseIpInput.value.trim()
  if (!ip) return
  abuseLoading.value = true
  error.value = ''
  abuseResult.value = null
  try {
    abuseResult.value = await abuseIpDbCheck(ip)
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : String(e)
    error.value = `Abuse check failed: ${msg}`
  } finally {
    abuseLoading.value = false
  }
}

// ─── WHOIS ──────────────────────────────────────────────────────────────────
const whoisInput = ref('')
const whoisLoading = ref(false)
const whoisResult = ref<WhoisResult | null>(null)

async function runWhois() {
  const domain = whoisInput.value.trim()
  if (!domain) return
  whoisLoading.value = true
  error.value = ''
  whoisResult.value = null
  try {
    whoisResult.value = await whoisLookup(domain)
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : String(e)
    error.value = `WHOIS lookup failed: ${msg}`
  } finally {
    whoisLoading.value = false
  }
}
</script>

<style scoped>
.page-container { padding: 24px 32px; max-width: 1400px; }
.section-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; }
.section-title { font-family: 'Oswald', sans-serif; font-size: 28px; font-weight: 700; text-transform: uppercase; color: #f5f5f5; letter-spacing: 2px; }
.section-subtitle { font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #666; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.05em; }

.tabs-navigation { display: flex; gap: 2px; margin-bottom: 24px; border-bottom: 1px solid #1a1a1a; }
.tab-item { padding: 10px 20px; background: transparent; border: none; color: #666; font-family: 'Oswald', sans-serif; font-size: 13px; cursor: pointer; border-bottom: 2px solid transparent; transition: all 0.2s; text-transform: uppercase; letter-spacing: 0.05em; }
.tab-item.active { color: #DC2626; border-bottom-color: #DC2626; }
.tab-item:hover { color: #f5f5f5; }

.input-row { display: flex; gap: 12px; margin-bottom: 24px; }
.security-input { flex: 1; background: #0a0a0a; border: 1px solid #333; padding: 12px 16px; color: #f5f5f5; font-family: 'JetBrains Mono', monospace; font-size: 13px; outline: none; letter-spacing: 0.05em; transition: border-color 0.2s; }
.security-input:focus { border-color: #DC2626; }
.security-input::placeholder { color: #444; text-transform: uppercase; font-size: 11px; }
.btn-submit { padding: 12px 28px; background: #DC2626; border: none; color: #000; font-family: 'Oswald', sans-serif; font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; cursor: pointer; transition: all 0.2s; white-space: nowrap; }
.btn-submit:hover { background: #EF4444; }
.btn-submit:disabled { opacity: 0.4; cursor: not-allowed; }

.error-banner { background: rgba(220,38,38,0.1); border: 1px solid #DC2626; padding: 12px 16px; margin-bottom: 20px; color: #DC2626; font-family: 'JetBrains Mono', monospace; font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; }
.loading-text { font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #DC2626; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 20px; animation: pulse-loading 1.2s ease-in-out infinite; }
@keyframes pulse-loading { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }
.polling-text { font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #EAB308; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 12px; animation: pulse-loading 1.2s ease-in-out infinite; }

.tab-content { min-height: 200px; }
.results-grid { display: grid; gap: 16px; }
.results-grid.three-col { grid-template-columns: repeat(3, 1fr); }
.results-grid.two-col { grid-template-columns: repeat(2, 1fr); }
.results-grid.single-col { grid-template-columns: 1fr; max-width: 700px; }

.glass-card { background: rgba(220,38,38,0.03); border: 1px solid rgba(220,38,38,0.15); backdrop-filter: blur(12px); padding: 20px; }
.card-title { font-family: 'Oswald', sans-serif; font-size: 13px; font-weight: 600; text-transform: uppercase; color: #DC2626; letter-spacing: 0.1em; margin-bottom: 16px; padding-bottom: 8px; border-bottom: 1px solid rgba(220,38,38,0.1); }

.result-fields { display: flex; flex-direction: column; gap: 8px; }
.result-section { display: flex; flex-direction: column; gap: 8px; margin-bottom: 8px; }
.result-section + .result-section { padding-top: 8px; border-top: 1px solid rgba(220,38,38,0.08); }
.field-row { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; }
.field-label { font-family: 'JetBrains Mono', monospace; font-size: 9px; color: #666; text-transform: uppercase; letter-spacing: 0.05em; white-space: nowrap; padding-top: 2px; flex-shrink: 0; }
.field-value { font-family: 'JetBrains Mono', monospace; font-size: 13px; color: #f5f5f5; text-align: right; word-break: break-all; }
.text-truncate { max-width: 250px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.vt-malicious { color: #DC2626; font-weight: 700; }
.vt-suspicious { color: #F97316; font-weight: 700; }
.vt-harmless { color: #22C55E; font-weight: 700; }

.abuse-score-wrap { display: flex; justify-content: center; margin-bottom: 24px; }
.abuse-score-circle { width: 120px; height: 120px; border: 3px solid #666; border-radius: 50%; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 4px; }
.abuse-score-value { font-family: 'Oswald', sans-serif; font-size: 40px; font-weight: 700; color: #f5f5f5; line-height: 1; }
.abuse-score-label { font-family: 'JetBrains Mono', monospace; font-size: 8px; color: #666; text-transform: uppercase; letter-spacing: 0.1em; }

.text-danger { color: #DC2626; font-weight: 700; }
.text-safe { color: #22C55E; font-weight: 700; }
.nameserver-list { display: flex; flex-direction: column; gap: 4px; }
.ns-item { font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #ccc; }

@media (max-width: 1024px) {
  .results-grid.three-col, .results-grid.two-col { grid-template-columns: 1fr; }
}
@media (max-width: 640px) {
  .page-container { padding: 16px; }
  .input-row { flex-direction: column; }
  .btn-submit { width: 100%; }
  .tab-item { padding: 8px 12px; font-size: 11px; }
}
</style>
