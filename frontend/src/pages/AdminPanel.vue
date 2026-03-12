<template>
  <div class="admin-panel">
    <!-- Header -->
    <div class="admin-header">
      <h1 class="font-anton admin-title">
        ADMIN PANEL
      </h1>
      <span class="font-mono admin-subtitle">SYSTEM CONTROL</span>
    </div>

    <!-- Tabs -->
    <div class="tab-bar">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        class="tab-btn font-oswald"
        :class="{ active: activeTab === tab.id }"
        @click="activeTab = tab.id"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- Tab Content -->
    <div class="tab-content">
      <!-- ─── USERS ─────────────────────────────────────────────────── -->
      <div
        v-if="activeTab === 'users'"
        class="panel-section"
      >
        <div class="section-toolbar">
          <span class="font-mono section-count">{{ users.length }} users</span>
          <button
            class="btn btn-outline btn-sm"
            @click="loadUsers"
          >
            REFRESH
          </button>
        </div>
        <div class="table-wrap custom-scrollbar">
          <table class="data-table">
            <thead>
              <tr>
                <th class="font-mono">
                  ID
                </th>
                <th class="font-mono">
                  USERNAME
                </th>
                <th class="font-mono">
                  EMAIL
                </th>
                <th class="font-mono">
                  ROLE
                </th>
                <th class="font-mono">
                  STATUS
                </th>
                <th class="font-mono">
                  INVITE CODE
                </th>
                <th class="font-mono">
                  CREATED
                </th>
                <th class="font-mono">
                  ACTIONS
                </th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="u in users"
                :key="u.id"
                :class="{ 'row-pending': u.status === 'pending' }"
              >
                <td class="font-mono">
                  {{ u.id }}
                </td>
                <td class="font-mono">
                  {{ u.username }}
                </td>
                <td class="font-mono td-truncate">
                  {{ u.email }}
                </td>
                <td>
                  <span
                    class="badge font-mono"
                    :class="u.role === 'admin' ? 'badge-accent' : 'badge-muted'"
                  >
                    {{ u.role.toUpperCase() }}
                  </span>
                </td>
                <td>
                  <span
                    class="badge font-mono"
                    :class="{
                      'badge-ok': u.status === 'active',
                      'badge-warn': u.status === 'pending',
                      'badge-err': u.status === 'blocked',
                    }"
                  >
                    {{ u.status.toUpperCase() }}
                  </span>
                </td>
                <td class="font-mono">
                  {{ u.invite_code }}
                </td>
                <td class="font-mono td-date">
                  {{ formatDate(u.created_at) }}
                </td>
                <td class="td-actions">
                  <button
                    v-if="u.status !== 'blocked'"
                    class="action-btn font-mono action-block"
                    @click="toggleBlock(u)"
                  >
                    BLOCK
                  </button>
                  <button
                    v-else
                    class="action-btn font-mono action-unblock"
                    @click="toggleBlock(u)"
                  >
                    UNBLOCK
                  </button>
                  <button
                    class="action-btn font-mono"
                    :class="u.role === 'admin' ? 'action-demote' : 'action-promote'"
                    @click="toggleRole(u)"
                  >
                    {{ u.role === 'admin' ? 'DEMOTE' : 'PROMOTE' }}
                  </button>
                  <button
                    class="action-btn font-mono action-kick"
                    @click="doKick(u)"
                  >
                    KICK
                  </button>
                  <button
                    v-if="u.status !== 'blocked'"
                    class="action-btn font-mono action-ban"
                    @click="doBan(u)"
                  >
                    BAN
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- IP Bans -->
        <div class="ip-bans-section">
          <div class="font-mono sub-heading">
            IP BANS ({{ ipBans.length }})
          </div>
          <div class="ip-ban-add">
            <input
              v-model="newBanIp"
              class="ban-input font-mono"
              placeholder="IP address"
            >
            <input
              v-model="newBanReason"
              class="ban-input font-mono ban-reason"
              placeholder="Reason (optional)"
            >
            <button
              class="action-btn font-mono action-ban"
              @click="doIpBan"
            >
              IP BAN
            </button>
          </div>
          <div
            v-if="ipBans.length"
            class="table-wrap custom-scrollbar"
          >
            <table class="data-table">
              <thead>
                <tr>
                  <th class="font-mono">
                    IP
                  </th>
                  <th class="font-mono">
                    REASON
                  </th>
                  <th class="font-mono">
                    BANNED BY
                  </th>
                  <th class="font-mono">
                    DATE
                  </th>
                  <th class="font-mono">
                    ACTION
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="b in ipBans"
                  :key="b.id"
                >
                  <td class="font-mono">
                    {{ b.ip_address }}
                  </td>
                  <td class="font-mono">
                    {{ b.reason || '---' }}
                  </td>
                  <td class="font-mono">
                    {{ b.banned_by || '---' }}
                  </td>
                  <td class="font-mono td-date">
                    {{ formatDate(b.created_at) }}
                  </td>
                  <td>
                    <button
                      class="action-btn font-mono action-unblock"
                      @click="doIpUnban(b.ip_address)"
                    >
                      UNBAN
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- ─── MONITORING ────────────────────────────────────────────── -->
      <div
        v-if="activeTab === 'monitoring'"
        class="panel-section"
      >
        <div class="section-toolbar">
          <span class="font-mono section-count">{{ services.length }} services</span>
          <span class="font-mono auto-refresh-label">AUTO-REFRESH 30s</span>
          <button
            class="btn btn-outline btn-sm"
            @click="loadHealth"
          >
            REFRESH
          </button>
        </div>
        <div class="services-grid">
          <div
            v-for="svc in services"
            :key="svc.name"
            class="service-card"
            :class="'svc-' + svc.status"
          >
            <div class="svc-header">
              <span
                class="svc-dot"
                :class="'dot-' + svc.status"
              />
              <span class="font-oswald svc-name">{{ svc.name }}</span>
            </div>
            <div class="svc-details">
              <span class="font-mono svc-status">{{ svc.status.toUpperCase() }}</span>
              <span class="font-mono svc-ms">{{ svc.response_ms }}ms</span>
            </div>
            <div
              v-if="svc.error"
              class="font-mono svc-error"
            >
              {{ svc.error }}
            </div>
          </div>
        </div>
      </div>

      <!-- ─── API ────────────────────────────────────────────────────── -->
      <div
        v-if="activeTab === 'api'"
        class="panel-section"
      >
        <div class="section-toolbar">
          <span class="font-mono section-count">API MANAGEMENT</span>
        </div>

        <!-- Connected Services -->
        <div class="api-block">
          <div class="font-mono sub-heading">
            CONNECTED SERVICES
          </div>
          <div class="services-grid compact">
            <div
              v-for="srv in connectedServices"
              :key="srv.id"
              class="service-card compact-card"
            >
              <div class="svc-header">
                <span
                  class="svc-dot"
                  :class="srv.connected ? 'dot-ok' : 'dot-down'"
                />
                <span class="font-oswald svc-name">{{ srv.name }}</span>
              </div>
              <span
                class="font-mono"
                :class="srv.connected ? 'svc-active' : 'svc-offline'"
              >
                {{ srv.connected ? 'ACTIVE' : 'OFFLINE' }}
              </span>
            </div>
          </div>
        </div>

        <!-- Backend API Health -->
        <div class="api-block">
          <div class="font-mono sub-heading">
            BACKEND API HEALTH
          </div>
          <div class="services-grid compact">
            <div
              v-for="(ok, svc) in apiHealthStatus"
              :key="svc"
              class="service-card compact-card"
            >
              <div class="svc-header">
                <span
                  class="svc-dot"
                  :class="ok ? 'dot-ok' : 'dot-down'"
                />
                <span
                  class="font-mono svc-name"
                  style="font-size:11px"
                >{{ svc }}</span>
              </div>
              <span
                class="font-mono"
                :class="ok ? 'svc-active' : 'svc-offline'"
              >{{ ok ? 'OK' : 'DOWN' }}</span>
            </div>
          </div>
          <button
            class="btn btn-outline btn-sm"
            style="margin-top:12px"
            @click="checkApiHealth"
          >
            REFRESH HEALTH
          </button>
        </div>
      </div>

      <!-- ─── SECURITY ───────────────────────────────────────────────── -->
      <div
        v-if="activeTab === 'security'"
        class="panel-section"
      >
        <div class="security-sub-tabs">
          <button
            v-for="st in sec.securitySubTabs"
            :key="st.id"
            class="sub-tab-item font-mono"
            :class="{ active: sec.securitySubTab.value === st.id }"
            @click="sec.securitySubTab.value = st.id"
          >
            {{ st.name }}
          </button>
        </div>

        <div
          v-if="sec.securityError.value"
          class="security-error-banner font-mono"
        >
          {{ sec.securityError.value }}
        </div>

        <!-- IP Lookup -->
        <div
          v-show="sec.securitySubTab.value === 'ip-lookup'"
          class="sec-tab-content"
        >
          <div class="sec-input-row">
            <input
              v-model="sec.ipInput.value"
              class="sec-input font-mono"
              placeholder="IP address (e.g. 8.8.8.8)"
              @keyup.enter="sec.runIpLookup()"
            >
            <button
              class="action-btn font-mono action-promote"
              :disabled="sec.ipLoading.value || !sec.ipInput.value.trim()"
              @click="sec.runIpLookup()"
            >
              {{ sec.ipLoading.value ? 'LOADING...' : 'LOOKUP' }}
            </button>
          </div>
          <div
            v-if="sec.ipLoading.value"
            class="font-mono sec-loading"
          >
            LOADING...
          </div>
          <div
            v-if="sec.hasIpResults.value"
            class="sec-results-grid"
          >
            <div
              v-if="sec.ipInfoData.value"
              class="sec-result-card"
            >
              <div class="font-mono sub-heading">
                IPINFO.IO
              </div>
              <div class="sec-fields">
                <div class="sec-field">
                  <span class="sec-label font-mono">IP</span><span class="sec-value font-mono">{{ sec.ipInfoData.value.ip }}</span>
                </div>
                <div class="sec-field">
                  <span class="sec-label font-mono">COUNTRY</span><span class="sec-value font-mono">{{ sec.ipInfoData.value.country || '---' }}</span>
                </div>
                <div class="sec-field">
                  <span class="sec-label font-mono">CITY</span><span class="sec-value font-mono">{{ sec.ipInfoData.value.city || '---' }}</span>
                </div>
                <div class="sec-field">
                  <span class="sec-label font-mono">ORG</span><span class="sec-value font-mono">{{ sec.ipInfoData.value.org || '---' }}</span>
                </div>
                <div class="sec-field">
                  <span class="sec-label font-mono">TIMEZONE</span><span class="sec-value font-mono">{{ sec.ipInfoData.value.timezone || '---' }}</span>
                </div>
              </div>
            </div>
            <div
              v-if="sec.ip2locData.value"
              class="sec-result-card"
            >
              <div class="font-mono sub-heading">
                IP2LOCATION
              </div>
              <div class="sec-fields">
                <div class="sec-field">
                  <span class="sec-label font-mono">IP</span><span class="sec-value font-mono">{{ sec.ip2locData.value.ip }}</span>
                </div>
                <div class="sec-field">
                  <span class="sec-label font-mono">COUNTRY</span><span class="sec-value font-mono">{{ sec.ip2locData.value.country_name || '---' }}</span>
                </div>
                <div class="sec-field">
                  <span class="sec-label font-mono">CITY</span><span class="sec-value font-mono">{{ sec.ip2locData.value.city_name || '---' }}</span>
                </div>
                <div class="sec-field">
                  <span class="sec-label font-mono">ISP</span><span class="sec-value font-mono">{{ sec.ip2locData.value.as || '---' }}</span>
                </div>
                <div class="sec-field">
                  <span class="sec-label font-mono">PROXY</span><span class="sec-value font-mono">{{ sec.ip2locData.value.is_proxy ? 'YES' : 'NO' }}</span>
                </div>
              </div>
            </div>
            <div
              v-if="sec.bdcData.value"
              class="sec-result-card"
            >
              <div class="font-mono sub-heading">
                BIGDATACLOUD
              </div>
              <div class="sec-fields">
                <div class="sec-field">
                  <span class="sec-label font-mono">COUNTRY</span><span class="sec-value font-mono">{{ sec.bdcData.value.country?.name || '---' }}</span>
                </div>
                <div class="sec-field">
                  <span class="sec-label font-mono">CITY</span><span class="sec-value font-mono">{{ sec.bdcData.value.city?.name || '---' }}</span>
                </div>
                <div class="sec-field">
                  <span class="sec-label font-mono">ORG</span><span class="sec-value font-mono">{{ sec.bdcData.value.network?.organisation || '---' }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- URL Scanner -->
        <div
          v-show="sec.securitySubTab.value === 'url-scanner'"
          class="sec-tab-content"
        >
          <div class="sec-input-row">
            <input
              v-model="sec.urlInput.value"
              class="sec-input font-mono"
              placeholder="URL (e.g. https://example.com)"
              @keyup.enter="sec.runUrlScan()"
            >
            <button
              class="action-btn font-mono action-promote"
              :disabled="sec.urlLoading.value || !sec.urlInput.value.trim()"
              @click="sec.runUrlScan()"
            >
              {{ sec.urlLoading.value ? 'SCANNING...' : 'SCAN' }}
            </button>
          </div>
          <div
            v-if="sec.urlLoading.value"
            class="font-mono sec-loading"
          >
            SCANNING URL...
          </div>
          <div
            v-if="sec.vtScan.value || sec.urlScanData.value"
            class="sec-results-grid two-col"
          >
            <div class="sec-result-card">
              <div class="font-mono sub-heading">
                VIRUSTOTAL
              </div>
              <div class="sec-fields">
                <div
                  v-if="sec.vtPolling.value"
                  class="font-mono sec-polling"
                >
                  POLLING... ({{ sec.vtPollCount.value }}s)
                </div>
                <template v-if="sec.vtAnalysisData.value">
                  <div class="sec-field">
                    <span class="sec-label font-mono">STATUS</span><span class="sec-value font-mono">{{ sec.vtAnalysisData.value.status.toUpperCase() }}</span>
                  </div>
                  <div class="sec-field">
                    <span class="sec-label font-mono">MALICIOUS</span><span
                      class="sec-value font-mono"
                      style="color:var(--accent)"
                    >{{ sec.vtAnalysisData.value.stats.malicious }}</span>
                  </div>
                  <div class="sec-field">
                    <span class="sec-label font-mono">SUSPICIOUS</span><span
                      class="sec-value font-mono"
                      style="color:#fb923c"
                    >{{ sec.vtAnalysisData.value.stats.suspicious }}</span>
                  </div>
                  <div class="sec-field">
                    <span class="sec-label font-mono">HARMLESS</span><span
                      class="sec-value font-mono"
                      style="color:#22C55E"
                    >{{ sec.vtAnalysisData.value.stats.harmless }}</span>
                  </div>
                  <div class="sec-field">
                    <span class="sec-label font-mono">UNDETECTED</span><span class="sec-value font-mono">{{ sec.vtAnalysisData.value.stats.undetected }}</span>
                  </div>
                </template>
              </div>
            </div>
            <div class="sec-result-card">
              <div class="font-mono sub-heading">
                URLSCAN.IO
              </div>
              <div class="sec-fields">
                <div
                  v-if="sec.urlScanPolling.value"
                  class="font-mono sec-polling"
                >
                  POLLING... ({{ sec.urlScanPollCount.value }}s)
                </div>
                <template v-if="sec.urlScanResultData.value?.page">
                  <div class="sec-field">
                    <span class="sec-label font-mono">DOMAIN</span><span class="sec-value font-mono">{{ sec.urlScanResultData.value.page.domain }}</span>
                  </div>
                  <div class="sec-field">
                    <span class="sec-label font-mono">IP</span><span class="sec-value font-mono">{{ sec.urlScanResultData.value.page.ip }}</span>
                  </div>
                  <div class="sec-field">
                    <span class="sec-label font-mono">COUNTRY</span><span class="sec-value font-mono">{{ sec.urlScanResultData.value.page.country }}</span>
                  </div>
                  <div class="sec-field">
                    <span class="sec-label font-mono">STATUS</span><span class="sec-value font-mono">{{ sec.urlScanResultData.value.page.status_code }}</span>
                  </div>
                </template>
                <template v-if="sec.urlScanResultData.value?.verdicts">
                  <div class="sec-field">
                    <span class="sec-label font-mono">MALICIOUS</span>
                    <span
                      class="sec-value font-mono"
                      :style="{ color: sec.urlScanResultData.value.verdicts.malicious ? 'var(--accent)' : '#22C55E' }"
                    >
                      {{ sec.urlScanResultData.value.verdicts.malicious ? 'YES' : 'NO' }}
                    </span>
                  </div>
                </template>
              </div>
            </div>
          </div>
        </div>

        <!-- IP Abuse -->
        <div
          v-show="sec.securitySubTab.value === 'ip-abuse'"
          class="sec-tab-content"
        >
          <div class="sec-input-row">
            <input
              v-model="sec.abuseIpInput.value"
              class="sec-input font-mono"
              placeholder="IP address for abuse check"
              @keyup.enter="sec.runAbuseCheck()"
            >
            <button
              class="action-btn font-mono action-promote"
              :disabled="sec.abuseLoading.value || !sec.abuseIpInput.value.trim()"
              @click="sec.runAbuseCheck()"
            >
              {{ sec.abuseLoading.value ? 'LOADING...' : 'CHECK' }}
            </button>
          </div>
          <div
            v-if="sec.abuseLoading.value"
            class="font-mono sec-loading"
          >
            LOADING...
          </div>
          <div
            v-if="sec.abuseResult.value"
            class="sec-results-grid single-col"
          >
            <div class="sec-result-card">
              <div class="font-mono sub-heading">
                ABUSEIPDB REPORT
              </div>
              <div class="abuse-score-wrap">
                <div
                  class="abuse-score-circle"
                  :style="{ borderColor: sec.abuseScoreColor.value }"
                >
                  <span
                    class="abuse-score-value font-mono"
                    :style="{ color: sec.abuseScoreColor.value }"
                  >{{ sec.abuseResult.value.abuse_confidence_score }}</span>
                  <span class="abuse-score-label font-mono">CONFIDENCE</span>
                </div>
              </div>
              <div class="sec-fields">
                <div class="sec-field">
                  <span class="sec-label font-mono">IP</span><span class="sec-value font-mono">{{ sec.abuseResult.value.ip }}</span>
                </div>
                <div class="sec-field">
                  <span class="sec-label font-mono">SCORE</span><span
                    class="sec-value font-mono"
                    :style="{ color: sec.abuseScoreColor.value }"
                  >{{ sec.abuseResult.value.abuse_confidence_score }}%</span>
                </div>
                <div class="sec-field">
                  <span class="sec-label font-mono">TOTAL REPORTS</span><span class="sec-value font-mono">{{ sec.abuseResult.value.total_reports }}</span>
                </div>
                <div class="sec-field">
                  <span class="sec-label font-mono">ISP</span><span class="sec-value font-mono">{{ sec.abuseResult.value.isp || '---' }}</span>
                </div>
                <div class="sec-field">
                  <span class="sec-label font-mono">COUNTRY</span><span class="sec-value font-mono">{{ sec.abuseResult.value.country_code || '---' }}</span>
                </div>
                <div class="sec-field">
                  <span class="sec-label font-mono">LAST REPORTED</span><span class="sec-value font-mono">{{ sec.abuseResult.value.last_reported_at || 'NEVER' }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- WHOIS -->
        <div
          v-show="sec.securitySubTab.value === 'whois'"
          class="sec-tab-content"
        >
          <div class="sec-input-row">
            <input
              v-model="sec.whoisInput.value"
              class="sec-input font-mono"
              placeholder="Domain (e.g. example.com)"
              @keyup.enter="sec.runWhois()"
            >
            <button
              class="action-btn font-mono action-promote"
              :disabled="sec.whoisLoading.value || !sec.whoisInput.value.trim()"
              @click="sec.runWhois()"
            >
              {{ sec.whoisLoading.value ? 'LOADING...' : 'LOOKUP' }}
            </button>
          </div>
          <div
            v-if="sec.whoisLoading.value"
            class="font-mono sec-loading"
          >
            LOADING...
          </div>
          <div
            v-if="sec.whoisResult.value"
            class="sec-results-grid single-col"
          >
            <div class="sec-result-card">
              <div class="font-mono sub-heading">
                WHOIS — {{ sec.whoisResult.value.domain || sec.whoisInput.value }}
              </div>
              <div class="sec-fields">
                <div class="sec-field">
                  <span class="sec-label font-mono">DOMAIN</span><span class="sec-value font-mono">{{ sec.whoisResult.value.domain || '---' }}</span>
                </div>
                <div class="sec-field">
                  <span class="sec-label font-mono">REGISTRAR</span><span class="sec-value font-mono">{{ sec.whoisResult.value.registrar?.name || '---' }}</span>
                </div>
                <div class="sec-field">
                  <span class="sec-label font-mono">CREATED</span><span class="sec-value font-mono">{{ sec.whoisResult.value.create_date || '---' }}</span>
                </div>
                <div class="sec-field">
                  <span class="sec-label font-mono">EXPIRES</span><span class="sec-value font-mono">{{ sec.whoisResult.value.expire_date || '---' }}</span>
                </div>
                <div
                  v-if="sec.whoisResult.value.registrant"
                  class="sec-field"
                >
                  <span class="sec-label font-mono">REGISTRANT</span><span class="sec-value font-mono">{{ sec.whoisResult.value.registrant.organization || '---' }}</span>
                </div>
                <div
                  v-if="sec.whoisResult.value.nameservers?.length"
                  class="sec-field"
                >
                  <span class="sec-label font-mono">NS</span>
                  <span class="sec-value font-mono">{{ sec.whoisResult.value.nameservers.join(', ') }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ─── REQUESTS ──────────────────────────────────────────────── -->
      <div
        v-if="activeTab === 'requests'"
        class="panel-section"
      >
        <div class="section-toolbar">
          <span class="font-mono section-count">{{ requests.length }} recent</span>
          <span class="font-mono auto-refresh-label">AUTO-REFRESH 10s</span>
          <button
            class="btn btn-outline btn-sm"
            @click="loadRequests"
          >
            REFRESH
          </button>
        </div>
        <div
          v-if="activeRequests.length"
          class="active-requests-block"
        >
          <div class="font-mono sub-heading">
            ACTIVE REQUESTS ({{ activeRequests.length }})
          </div>
          <div class="table-wrap custom-scrollbar">
            <table class="data-table">
              <thead>
                <tr>
                  <th class="font-mono">
                    ID
                  </th>
                  <th class="font-mono">
                    METHOD
                  </th>
                  <th class="font-mono">
                    PATH
                  </th>
                  <th class="font-mono">
                    IP
                  </th>
                  <th class="font-mono">
                    ELAPSED
                  </th>
                  <th class="font-mono">
                    ACTION
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="ar in activeRequests"
                  :key="ar.request_id"
                >
                  <td class="font-mono">
                    {{ ar.request_id }}
                  </td>
                  <td class="font-mono">
                    {{ ar.method }}
                  </td>
                  <td class="font-mono td-truncate">
                    {{ ar.path }}
                  </td>
                  <td class="font-mono">
                    {{ ar.client_ip }}
                  </td>
                  <td class="font-mono">
                    {{ ar.elapsed_ms }}ms
                  </td>
                  <td>
                    <button
                      class="action-btn font-mono action-cancel"
                      @click="doCancel(ar.request_id)"
                    >
                      CANCEL
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div class="table-wrap custom-scrollbar">
          <table class="data-table">
            <thead>
              <tr>
                <th class="font-mono">
                  TIME
                </th>
                <th class="font-mono">
                  IP
                </th>
                <th class="font-mono">
                  METHOD
                </th>
                <th class="font-mono">
                  PATH
                </th>
                <th class="font-mono">
                  STATUS
                </th>
                <th class="font-mono">
                  DURATION
                </th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="r in requests"
                :key="r.request_id"
                :class="{ 'row-error': r.status_code >= 400 }"
              >
                <td class="font-mono td-date">
                  {{ formatTime(r.timestamp) }}
                </td>
                <td class="font-mono">
                  {{ r.client_ip }}
                </td>
                <td class="font-mono">
                  {{ r.method }}
                </td>
                <td class="font-mono td-truncate">
                  {{ r.path }}
                </td>
                <td>
                  <span
                    class="badge font-mono"
                    :class="{
                      'badge-ok': r.status_code < 300,
                      'badge-warn': r.status_code >= 300 && r.status_code < 400,
                      'badge-err': r.status_code >= 400,
                    }"
                  >{{ r.status_code }}</span>
                </td>
                <td class="font-mono">
                  {{ r.duration_ms }}ms
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- ─── ERRORS ────────────────────────────────────────────────── -->
      <div
        v-if="activeTab === 'errors'"
        class="panel-section"
      >
        <div class="section-toolbar">
          <span class="font-mono section-count">{{ errors.length }} errors</span>
          <button
            class="btn btn-outline btn-sm"
            @click="loadErrors"
          >
            REFRESH
          </button>
        </div>
        <div class="errors-list">
          <div
            v-for="e in errors"
            :key="e.request_id + e.timestamp"
            class="error-card"
          >
            <div
              class="error-header"
              @click="toggleError(e.request_id)"
            >
              <span class="badge badge-err font-mono">{{ e.status_code }}</span>
              <span class="font-mono error-method">{{ e.method }}</span>
              <span class="font-mono error-path">{{ e.path }}</span>
              <span class="font-mono error-time">{{ formatTime(e.timestamp) }}</span>
              <span class="font-mono error-ip">{{ e.client_ip }}</span>
              <span class="font-mono error-chevron">{{ expandedErrors.has(e.request_id) ? '&minus;' : '+' }}</span>
            </div>
            <div class="font-mono error-message">
              {{ e.error }}
            </div>
            <div
              v-if="expandedErrors.has(e.request_id) && e.traceback_short"
              class="error-traceback"
            >
              <pre class="font-mono">{{ e.traceback_short }}</pre>
            </div>
          </div>
          <div
            v-if="!errors.length"
            class="empty-state font-mono"
          >
            NO ERRORS RECORDED
          </div>
        </div>
      </div>

      <!-- ─── SYSTEM ────────────────────────────────────────────────── -->
      <div
        v-if="activeTab === 'system'"
        class="panel-section"
      >
        <div class="section-toolbar">
          <button
            class="btn btn-outline btn-sm"
            @click="loadSystem"
          >
            REFRESH
          </button>
        </div>
        <div
          v-if="systemInfo"
          class="system-grid"
        >
          <div class="sys-card">
            <div class="font-mono sys-label">
              PYTHON
            </div>
            <div class="font-mono sys-value">
              {{ systemInfo.python_version.split(' ')[0] }}
            </div>
          </div>
          <div class="sys-card">
            <div class="font-mono sys-label">
              PLATFORM
            </div>
            <div class="font-mono sys-value sys-value-sm">
              {{ systemInfo.platform }}
            </div>
          </div>
          <div class="sys-card">
            <div class="font-mono sys-label">
              UPTIME
            </div>
            <div class="font-mono sys-value">
              {{ formatUptime(systemInfo.uptime_seconds) }}
            </div>
          </div>
          <div class="sys-card">
            <div class="font-mono sys-label">
              MEMORY
            </div>
            <div class="font-mono sys-value">
              {{ systemInfo.memory_mb }} MB
            </div>
          </div>
          <div class="sys-card">
            <div class="font-mono sys-label">
              DB POOL SIZE
            </div>
            <div class="font-mono sys-value">
              {{ systemInfo.db_pool.size }}
            </div>
          </div>
          <div class="sys-card">
            <div class="font-mono sys-label">
              DB CHECKED OUT
            </div>
            <div class="font-mono sys-value">
              {{ systemInfo.db_pool.checked_out }}
            </div>
          </div>
          <div class="sys-card">
            <div class="font-mono sys-label">
              DB OVERFLOW
            </div>
            <div class="font-mono sys-value">
              {{ systemInfo.db_pool.overflow }}
            </div>
          </div>
        </div>
        <div
          v-else
          class="empty-state font-mono"
        >
          LOADING...
        </div>
      </div>

      <!-- ─── TESTS ──────────────────────────────────────────────────── -->
      <div
        v-if="activeTab === 'tests'"
        class="panel-section"
      >
        <div class="section-toolbar">
          <span class="font-mono section-count">{{ testSuites.length }} suites</span>
          <select
            v-model="selectedSuite"
            class="font-mono test-select"
          >
            <option :value="null">
              ALL SUITES
            </option>
            <option
              v-for="s in testSuites"
              :key="s.name"
              :value="s.name"
            >
              {{ s.name }}
            </option>
          </select>
          <button
            class="btn btn-accent btn-sm"
            :disabled="testRunning"
            @click="runTestSuite(selectedSuite)"
          >
            {{ testRunning ? 'RUNNING...' : 'RUN TESTS' }}
          </button>
          <button
            class="btn btn-outline btn-sm"
            @click="loadTestSuites"
          >
            REFRESH
          </button>
        </div>

        <div
          v-if="testResults"
          class="test-results"
        >
          <div class="sys-grid">
            <div class="sys-card">
              <div class="font-mono sys-label">
                STATUS
              </div>
              <div
                class="font-mono sys-value"
                :style="{ color: testResults.status === 'pass' ? '#22c55e' : '#DC2626' }"
              >
                {{ testResults.status.toUpperCase() }}
              </div>
            </div>
            <div class="sys-card">
              <div class="font-mono sys-label">
                PASSED
              </div>
              <div
                class="font-mono sys-value"
                style="color: #22c55e"
              >
                {{ testResults.passed }}
              </div>
            </div>
            <div class="sys-card">
              <div class="font-mono sys-label">
                FAILED
              </div>
              <div
                class="font-mono sys-value"
                :style="{ color: testResults.failed > 0 ? '#DC2626' : 'var(--text-secondary)' }"
              >
                {{ testResults.failed }}
              </div>
            </div>
            <div class="sys-card">
              <div class="font-mono sys-label">
                ERRORS
              </div>
              <div
                class="font-mono sys-value"
                :style="{ color: testResults.errors > 0 ? '#f59e0b' : 'var(--text-secondary)' }"
              >
                {{ testResults.errors }}
              </div>
            </div>
          </div>
          <div class="font-mono test-summary">
            {{ testResults.summary }}
          </div>
          <pre class="font-mono test-output custom-scrollbar">{{ testResults.output }}</pre>
        </div>
        <div
          v-else-if="testRunning"
          class="empty-state font-mono"
        >
          RUNNING TESTS...
        </div>
        <div
          v-else
          class="empty-state font-mono"
        >
          SELECT SUITE AND RUN →
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import {
  fetchUsers,
  updateUserStatus,
  updateUserRole,
  fetchHealth,
  fetchRequests,
  fetchActiveRequests,
  cancelRequest,
  fetchErrors,
  fetchSystemInfo,
  kickUser,
  banUser,
  fetchIpBans,
  createIpBan,
  deleteIpBan,
  fetchTestSuites,
  runTests,
  type AdminUser,
  type ServiceHealth,
  type RequestRecord,
  type ActiveRequest,
  type ErrorRecord,
  type SystemInfo,
  type IpBanRecord,
} from '@/services/adminService'
import { checkAllApiHealth } from '@/services/apiConfigService'
import { useSecurityTools } from '@/composables/useSecurityTools'

const sec = useSecurityTools()

const tabs = [
  { id: 'users', label: 'USERS' },
  { id: 'monitoring', label: 'MONITORING' },
  { id: 'api', label: 'API' },
  { id: 'security', label: 'SECURITY' },
  { id: 'requests', label: 'REQUESTS' },
  { id: 'errors', label: 'ERRORS' },
  { id: 'system', label: 'SYSTEM' },
  { id: 'tests', label: 'TESTS' },
]

const activeTab = ref('users')

const users = ref<AdminUser[]>([])
const services = ref<ServiceHealth[]>([])
const requests = ref<RequestRecord[]>([])
const activeRequests = ref<ActiveRequest[]>([])
const errors = ref<ErrorRecord[]>([])
const systemInfo = ref<SystemInfo | null>(null)

// Tests
const testSuites = ref<{ name: string; file: string }[]>([])
const testResults = ref<{
  status: string; passed: number; failed: number; errors: number;
  summary: string; output: string; suite: string
} | null>(null)
const testRunning = ref(false)
const selectedSuite = ref<string | null>(null)
const expandedErrors = reactive(new Set<string>())
const ipBans = ref<IpBanRecord[]>([])
const newBanIp = ref('')
const newBanReason = ref('')
const apiHealthStatus = ref<Record<string, boolean>>({})

const connectedServices = ref([
  { id: 1, name: 'Cbonds API', connected: false },
  { id: 2, name: 'RuData Reference', connected: false },
  { id: 3, name: 'Bloomberg Data', connected: false },
  { id: 4, name: 'MOEX ISS', connected: true },
  { id: 5, name: 'Alpha Vantage', connected: false },
  { id: 6, name: 'Twelve Data', connected: false },
  { id: 7, name: 'Polygon.io', connected: false },
  { id: 8, name: 'FRED', connected: false },
  { id: 9, name: 'CoinGecko', connected: false },
  { id: 10, name: 'NewsAPI', connected: false },
  { id: 11, name: 'Hugging Face', connected: false },
  { id: 12, name: 'Frankfurter (ECB)', connected: true },
  { id: 13, name: 'Bank of Russia', connected: true },
  { id: 14, name: 'Nager.Date', connected: true },
])

let healthTimer: ReturnType<typeof setInterval> | null = null
let requestsTimer: ReturnType<typeof setInterval> | null = null

// ── Loaders ─────────────────────────────────────────────────────────────────

async function loadUsers() {
  try { users.value = await fetchUsers() } catch { /* silent */ }
}

async function loadHealth() {
  try {
    const resp = await fetchHealth()
    services.value = resp.services
  } catch { /* silent */ }
}

async function loadRequests() {
  try {
    const [reqs, active] = await Promise.all([
      fetchRequests({ limit: 100 }),
      fetchActiveRequests(),
    ])
    requests.value = reqs
    activeRequests.value = active
  } catch { /* silent */ }
}

async function loadErrors() {
  try { errors.value = await fetchErrors() } catch { /* silent */ }
}

async function loadSystem() {
  try { systemInfo.value = await fetchSystemInfo() } catch { /* silent */ }
}

async function loadIpBans() {
  try { ipBans.value = await fetchIpBans() } catch { /* silent */ }
}

async function checkApiHealth() {
  try { apiHealthStatus.value = await checkAllApiHealth() } catch { /* silent */ }
}

async function loadTestSuites() {
  try {
    const data = await fetchTestSuites()
    testSuites.value = data.suites
  } catch { /* silent */ }
}

async function runTestSuite(suite?: string | null) {
  testRunning.value = true
  testResults.value = null
  try {
    testResults.value = await runTests(suite)
  } catch { /* silent */ }
  testRunning.value = false
}

// ── Actions ─────────────────────────────────────────────────────────────────

async function toggleBlock(user: AdminUser) {
  const newStatus = user.status === 'blocked' ? 'active' : 'blocked'
  try {
    await updateUserStatus(user.id, newStatus)
    await loadUsers()
  } catch { /* silent */ }
}

async function toggleRole(user: AdminUser) {
  const newRole = user.role === 'admin' ? 'user' : 'admin'
  try {
    await updateUserRole(user.id, newRole)
    await loadUsers()
  } catch { /* silent */ }
}

async function doKick(user: AdminUser) {
  try {
    await kickUser(user.id)
    await loadUsers()
  } catch { /* silent */ }
}

async function doBan(user: AdminUser) {
  try {
    await banUser(user.id)
    await loadUsers()
  } catch { /* silent */ }
}

async function doIpBan() {
  const ip = newBanIp.value.trim()
  if (!ip) return
  try {
    await createIpBan(ip, newBanReason.value.trim() || undefined)
    newBanIp.value = ''
    newBanReason.value = ''
    await loadIpBans()
  } catch { /* silent */ }
}

async function doIpUnban(ip: string) {
  try {
    await deleteIpBan(ip)
    await loadIpBans()
  } catch { /* silent */ }
}

async function doCancel(requestId: string) {
  try {
    await cancelRequest(requestId)
    await loadRequests()
  } catch { /* silent */ }
}

function toggleError(id: string) {
  if (expandedErrors.has(id)) {
    expandedErrors.delete(id)
  } else {
    expandedErrors.add(id)
  }
}

// ── Formatters ──────────────────────────────────────────────────────────────

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit', year: '2-digit' })
}

function formatTime(ts: number): string {
  return new Date(ts * 1000).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

function formatUptime(seconds: number): string {
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  return `${h}h ${m}m`
}

// ── Lifecycle ───────────────────────────────────────────────────────────────

onMounted(() => {
  loadUsers()
  loadHealth()
  loadRequests()
  loadErrors()
  loadSystem()
  loadIpBans()
  checkApiHealth()
  loadTestSuites()

  healthTimer = setInterval(loadHealth, 30_000)
  requestsTimer = setInterval(loadRequests, 10_000)
})

onUnmounted(() => {
  if (healthTimer) clearInterval(healthTimer)
  if (requestsTimer) clearInterval(requestsTimer)
})
</script>

<style scoped>
.admin-panel {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

/* Header */
.admin-header {
  display: flex;
  align-items: baseline;
  gap: 16px;
  margin-bottom: 24px;
  border-bottom: 2px solid var(--accent, #DC2626);
  padding-bottom: 12px;
}

.admin-title {
  font-size: 28px;
  color: var(--text-primary, #F5F5F5);
  letter-spacing: 0.05em;
}

.admin-subtitle {
  font-size: 11px;
  color: var(--text-muted, #888);
  letter-spacing: 0.1em;
}

/* Tabs */
.tab-bar {
  display: flex;
  gap: 2px;
  margin-bottom: 20px;
  border-bottom: 1px solid var(--border, #1A1A1A);
}

.tab-btn {
  background: transparent;
  border: none;
  color: var(--text-muted, #888);
  font-size: 12px;
  letter-spacing: 0.08em;
  padding: 10px 20px;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}

.tab-btn:hover {
  color: var(--text-primary, #F5F5F5);
}

.tab-btn.active {
  color: var(--accent, #DC2626);
  border-bottom-color: var(--accent, #DC2626);
}

/* Section */
.panel-section {
  animation: fade-in 0.2s ease;
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

.section-toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.section-count {
  font-size: 10px;
  color: var(--text-muted, #888);
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.auto-refresh-label {
  font-size: 9px;
  color: var(--text-muted, #888);
  letter-spacing: 0.1em;
  opacity: 0.6;
}

.btn-sm {
  padding: 4px 12px;
  font-size: 10px;
  letter-spacing: 0.08em;
}

.btn-outline {
  background: transparent;
  border: 1px solid var(--border, #1A1A1A);
  color: var(--text-muted, #888);
  cursor: pointer;
  transition: all 0.2s;
}

.btn-outline:hover {
  border-color: var(--accent, #DC2626);
  color: var(--accent, #DC2626);
}

.sub-heading {
  font-size: 11px;
  color: var(--accent, #DC2626);
  letter-spacing: 0.1em;
  margin-bottom: 8px;
}

/* Tables */
.table-wrap {
  overflow-x: auto;
  margin-bottom: 16px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 11px;
}

.data-table th {
  text-align: left;
  font-size: 9px;
  color: var(--text-muted, #888);
  letter-spacing: 0.1em;
  padding: 8px 10px;
  border-bottom: 1px solid var(--border, #1A1A1A);
  white-space: nowrap;
}

.data-table td {
  padding: 8px 10px;
  border-bottom: 1px solid var(--border, #1A1A1A);
  color: var(--text-primary, #F5F5F5);
  white-space: nowrap;
}

.data-table tbody tr:hover {
  background: rgba(255, 255, 255, 0.02);
}

.row-pending {
  background: rgba(220, 38, 38, 0.06);
}

.row-error {
  background: rgba(220, 38, 38, 0.04);
}

.td-truncate {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.td-date {
  font-size: 10px;
  color: var(--text-muted, #888);
}

.td-actions {
  display: flex;
  gap: 6px;
}

/* Badges */
.badge {
  display: inline-block;
  padding: 2px 6px;
  font-size: 9px;
  letter-spacing: 0.08em;
  border: 1px solid;
}

.badge-ok {
  color: #22C55E;
  border-color: #22C55E;
}

.badge-warn {
  color: #F59E0B;
  border-color: #F59E0B;
}

.badge-err {
  color: var(--accent, #DC2626);
  border-color: var(--accent, #DC2626);
}

.badge-accent {
  color: var(--accent, #DC2626);
  border-color: var(--accent, #DC2626);
}

.badge-muted {
  color: var(--text-muted, #888);
  border-color: var(--border, #1A1A1A);
}

/* Action buttons */
.action-btn {
  background: transparent;
  border: 1px solid var(--border, #1A1A1A);
  color: var(--text-muted, #888);
  padding: 2px 8px;
  font-size: 9px;
  letter-spacing: 0.06em;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  border-color: var(--accent, #DC2626);
  color: var(--accent, #DC2626);
}

.action-block:hover {
  border-color: var(--accent, #DC2626);
  color: var(--accent, #DC2626);
}

.action-unblock:hover {
  border-color: #22C55E;
  color: #22C55E;
}

.action-promote:hover {
  border-color: #F59E0B;
  color: #F59E0B;
}

.action-demote:hover {
  border-color: var(--text-muted, #888);
  color: var(--text-muted, #888);
}

.action-cancel:hover {
  border-color: var(--accent, #DC2626);
  color: var(--accent, #DC2626);
}

/* Services Grid */
.services-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 12px;
}

.service-card {
  border: 1px solid var(--border, #1A1A1A);
  padding: 14px;
  transition: border-color 0.2s;
}

.service-card:hover {
  border-color: #262626;
}

.svc-ok {
  border-left: 3px solid #22C55E;
}

.svc-degraded {
  border-left: 3px solid #F59E0B;
}

.svc-down {
  border-left: 3px solid var(--accent, #DC2626);
}

.svc-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.svc-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.dot-ok {
  background: #22C55E;
}

.dot-degraded {
  background: #F59E0B;
}

.dot-down {
  background: var(--accent, #DC2626);
}

.svc-name {
  font-size: 12px;
  color: var(--text-primary, #F5F5F5);
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.svc-details {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.svc-status {
  font-size: 10px;
  letter-spacing: 0.1em;
  color: var(--text-muted, #888);
}

.svc-ms {
  font-size: 10px;
  color: var(--text-muted, #888);
}

.svc-error {
  margin-top: 6px;
  font-size: 9px;
  color: var(--accent, #DC2626);
  word-break: break-all;
}

/* Errors */
.errors-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.error-card {
  border: 1px solid var(--border, #1A1A1A);
  border-left: 3px solid var(--accent, #DC2626);
}

.error-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  cursor: pointer;
  transition: background 0.2s;
}

.error-header:hover {
  background: rgba(255, 255, 255, 0.02);
}

.error-method {
  font-size: 10px;
  color: var(--text-primary, #F5F5F5);
}

.error-path {
  font-size: 10px;
  color: var(--text-muted, #888);
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.error-time {
  font-size: 9px;
  color: var(--text-muted, #888);
}

.error-ip {
  font-size: 9px;
  color: var(--text-muted, #888);
}

.error-chevron {
  color: var(--text-muted, #888);
  font-size: 14px;
  width: 16px;
  text-align: center;
}

.error-message {
  padding: 0 12px 8px;
  font-size: 10px;
  color: var(--accent, #DC2626);
}

.error-traceback {
  border-top: 1px solid var(--border, #1A1A1A);
  padding: 10px 12px;
  background: var(--bg-secondary, #0A0A0A);
}

.error-traceback pre {
  font-size: 10px;
  color: var(--text-muted, #888);
  white-space: pre-wrap;
  word-break: break-all;
  margin: 0;
}

/* System */
.system-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 12px;
}

.sys-card {
  border: 1px solid var(--border, #1A1A1A);
  padding: 16px;
}

.sys-label {
  font-size: 9px;
  color: var(--text-muted, #888);
  letter-spacing: 0.1em;
  margin-bottom: 6px;
}

.sys-value {
  font-size: 16px;
  color: var(--text-primary, #F5F5F5);
}

.sys-value-sm {
  font-size: 10px;
  word-break: break-all;
}

/* Active requests block */
.active-requests-block {
  margin-bottom: 20px;
  border: 1px solid rgba(220, 38, 38, 0.3);
  padding: 12px;
}

/* Empty state */
.empty-state {
  text-align: center;
  padding: 40px;
  color: var(--text-muted, #888);
  font-size: 11px;
  letter-spacing: 0.1em;
}

/* Responsive */
@media (max-width: 768px) {
  .admin-panel {
    padding: 16px;
  }

  .tab-bar {
    overflow-x: auto;
    flex-wrap: nowrap;
  }

  .tab-btn {
    padding: 8px 14px;
    font-size: 10px;
    flex-shrink: 0;
  }

  .services-grid,
  .system-grid {
    grid-template-columns: 1fr;
  }
}

/* IP Bans */
.ip-bans-section {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid var(--border, #1A1A1A);
}

.ip-ban-add {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.ban-input {
  background: var(--bg-secondary, #0A0A0A);
  border: 1px solid var(--border, #1A1A1A);
  color: var(--text-primary, #F5F5F5);
  padding: 6px 10px;
  font-size: 11px;
  flex: 1;
}

.ban-reason {
  flex: 2;
}

.ban-input:focus {
  outline: none;
  border-color: var(--accent, #DC2626);
}

/* API tab */
.api-block {
  margin-bottom: 24px;
}

.services-grid.compact {
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 8px;
}

.compact-card {
  padding: 10px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.compact-card .svc-header {
  margin-bottom: 0;
}

.svc-active {
  font-size: 9px;
  color: #22C55E;
  letter-spacing: 0.1em;
}

.svc-offline {
  font-size: 9px;
  color: var(--text-muted, #888);
  letter-spacing: 0.1em;
}

/* Security tab */
.security-sub-tabs {
  display: flex;
  gap: 2px;
  margin-bottom: 20px;
  border-bottom: 1px solid var(--border, #1A1A1A);
}

.sub-tab-item {
  padding: 10px 16px;
  background: transparent;
  border: none;
  color: var(--text-muted, #888);
  font-size: 10px;
  letter-spacing: 0.08em;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
  text-transform: uppercase;
}

.sub-tab-item:hover {
  color: var(--text-primary, #F5F5F5);
}

.sub-tab-item.active {
  color: var(--accent, #DC2626);
  border-bottom-color: var(--accent, #DC2626);
}

.security-error-banner {
  background: rgba(220, 38, 38, 0.08);
  border: 1px solid rgba(220, 38, 38, 0.3);
  padding: 8px 12px;
  margin-bottom: 16px;
  color: var(--accent, #DC2626);
  font-size: 11px;
}

.sec-input-row {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.sec-input {
  flex: 1;
  background: var(--bg-secondary, #0A0A0A);
  border: 1px solid var(--border, #1A1A1A);
  color: var(--text-primary, #F5F5F5);
  padding: 8px 12px;
  font-size: 12px;
}

.sec-input:focus {
  outline: none;
  border-color: var(--accent, #DC2626);
}

.sec-loading {
  font-size: 11px;
  color: var(--accent, #DC2626);
  letter-spacing: 0.1em;
  margin-bottom: 12px;
  animation: sec-pulse 1.2s ease-in-out infinite;
}

.sec-polling {
  font-size: 10px;
  color: #F59E0B;
  letter-spacing: 0.05em;
  margin-bottom: 6px;
  animation: sec-pulse 1.2s ease-in-out infinite;
}

@keyframes sec-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.sec-results-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.sec-results-grid.two-col {
  grid-template-columns: repeat(2, 1fr);
}

.sec-results-grid.single-col {
  grid-template-columns: 1fr;
  max-width: 600px;
}

.sec-result-card {
  border: 1px solid var(--border, #1A1A1A);
  padding: 12px;
}

.sec-fields {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.sec-field {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
}

.sec-label {
  font-size: 9px;
  color: var(--text-muted, #888);
  letter-spacing: 0.05em;
  white-space: nowrap;
  flex-shrink: 0;
}

.sec-value {
  font-size: 11px;
  color: var(--text-primary, #F5F5F5);
  text-align: right;
  word-break: break-all;
}

.abuse-score-wrap {
  display: flex;
  justify-content: center;
  margin: 8px 0 16px;
}

.abuse-score-circle {
  width: 90px;
  height: 90px;
  border: 2px solid var(--text-muted, #888);
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
}

.abuse-score-value {
  font-size: 28px;
  font-weight: 700;
  line-height: 1;
}

.abuse-score-label {
  font-size: 7px;
  color: var(--text-muted, #888);
  letter-spacing: 0.1em;
}

/* New action button styles */
.action-kick:hover {
  border-color: #F59E0B;
  color: #F59E0B;
}

.action-ban:hover {
  border-color: var(--accent, #DC2626);
  color: var(--accent, #DC2626);
  background: rgba(220, 38, 38, 0.1);
}

@media (max-width: 768px) {
  .sec-results-grid,
  .sec-results-grid.two-col {
    grid-template-columns: 1fr;
  }

  .ip-ban-add {
    flex-direction: column;
  }
}

/* ── Tests ──────────────────────────────────────────────────────────────── */
.test-select {
  background: var(--bg-secondary);
  border: 1px solid var(--border-medium);
  color: var(--text-primary);
  padding: 6px 10px;
  border-radius: 4px;
  font-size: 12px;
}

.test-results {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.test-summary {
  color: var(--text-secondary);
  font-size: 13px;
  padding: 8px 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-dark);
  border-radius: 4px;
}

.test-output {
  background: var(--bg-primary);
  border: 1px solid var(--border-dark);
  border-radius: 4px;
  padding: 12px;
  font-size: 11px;
  line-height: 1.5;
  color: var(--text-secondary);
  max-height: 400px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-all;
}
</style>
