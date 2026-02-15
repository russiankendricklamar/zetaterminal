/**
 * Platform Service — Auth, Email, Storage, Media, Business, Developer
 *
 * Consolidated utility services for infrastructure and platform integrations.
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

async function putJson<T>(url: string, body: unknown): Promise<T> {
  const resp = await fetch(url, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!resp.ok) throw new Error(`HTTP ${resp.status}: ${resp.statusText}`)
  return resp.json()
}

// ─── Auth Types ─────────────────────────────────────────────────────────────

export interface Auth0TokenResult {
  access_token: string
  token_type: string
  expires_in: number
  provider: 'auth0'
}

export interface StytchAuthResult {
  user_id: string
  session_token: string
  status_code: number
  provider: 'stytch'
}

export interface MojoAuthResult {
  state_id: string
  provider: 'mojoauth'
}

export interface WarrantResult {
  result: string
  is_authorized: boolean
  provider: 'warrant'
}

// ─── Email Types ────────────────────────────────────────────────────────────

export interface SendEmailResult {
  status: string
  provider: 'sendgrid'
}

export interface EmailValidationResult {
  email: string
  status: string
  disposable?: boolean
  mx?: boolean
  is_disposable?: string
  is_free?: string
  provider: string
}

// ─── Storage Types ──────────────────────────────────────────────────────────

export interface JsonBinCreateResult {
  id: string
  name: string
  created_at: string
  provider: 'jsonbin'
}

export interface JsonBinReadResult {
  record: unknown
  provider: 'jsonbin'
}

export interface JsonBinUpdateResult {
  id: string
  version: number
  provider: 'jsonbin'
}

export interface PantryBasket {
  name?: string
  description?: string
  baskets?: string[]
  provider: 'pantry'
}

export interface PastebinResult {
  paste_url: string
  provider: 'pastebin'
}

// ─── Media Types ────────────────────────────────────────────────────────────

export interface CloudinaryUploadResult {
  public_id: string
  url: string
  format: string
  width: number
  height: number
  bytes: number
  provider: 'cloudinary'
}

export interface CloudinaryResource {
  public_id: string
  url: string
  format: string
  bytes: number
  created_at: string
}

export interface CloudinaryListResult {
  resources: CloudinaryResource[]
  total: number
  provider: 'cloudinary'
}

export interface CloudConvertJobResult {
  job_id: string
  status: string
  files?: Array<{ filename: string; url: string }>
  provider: 'cloudconvert'
}

// ─── Business Types ─────────────────────────────────────────────────────────

export interface LobAddressResult {
  primary_line: string
  city: string
  state: string
  zip_code: string
  deliverability: string
  provider: 'lob'
}

export interface VatValidationResult {
  valid: boolean
  country_code: string
  vat_number: string
  company_name: string
  company_address: string
  provider: 'vatlayer'
}

export interface KlarnaSessionResult {
  order_id: string
  status: string
  html_snippet: string
  provider: 'klarna'
}

// ─── Developer Types ────────────────────────────────────────────────────────

export interface GitHubRepo {
  name: string
  full_name: string
  description: string
  language: string
  stars: number
  forks: number
  updated_at: string
  html_url: string
}

export interface GitHubRepoListResult {
  repos: GitHubRepo[]
  total: number
  provider: 'github'
}

export interface GitHubRepoDetail {
  name: string
  full_name: string
  description: string
  language: string
  stars: number
  forks: number
  open_issues: number
  license: string
  created_at: string
  updated_at: string
  html_url: string
  provider: 'github'
}

export interface GitHubIssue {
  number: number
  title: string
  state: string
  user: string
  created_at: string
  html_url: string
  labels: string[]
}

export interface GitHubIssueListResult {
  issues: GitHubIssue[]
  total: number
  provider: 'github'
}

// ─── Auth ───────────────────────────────────────────────────────────────────

export function auth0GetToken(audience: string, grantType = 'client_credentials'): Promise<Auth0TokenResult> {
  return postJson(`${API_BASE}/api/platform/auth/auth0/token`, { audience, grant_type: grantType })
}

export function stytchAuthenticate(method: string, token: string): Promise<StytchAuthResult> {
  return postJson(`${API_BASE}/api/platform/auth/stytch/authenticate`, { method, token })
}

export function mojoAuthSendLink(email: string): Promise<MojoAuthResult> {
  return postJson(`${API_BASE}/api/platform/auth/mojoauth/send-link`, { email })
}

export function warrantCheck(
  objectType: string, objectId: string, relation: string,
  subjectType: string, subjectId: string,
): Promise<WarrantResult> {
  return postJson(`${API_BASE}/api/platform/auth/warrant/check`, {
    object_type: objectType, object_id: objectId, relation,
    subject_type: subjectType, subject_id: subjectId,
  })
}

export function warrantCreateWarrant(
  objectType: string, objectId: string, relation: string,
  subjectType: string, subjectId: string,
): Promise<WarrantResult> {
  return postJson(`${API_BASE}/api/platform/auth/warrant/create-warrant`, {
    object_type: objectType, object_id: objectId, relation,
    subject_type: subjectType, subject_id: subjectId,
  })
}

// ─── Email ──────────────────────────────────────────────────────────────────

export function sendEmail(
  toEmail: string, fromEmail: string, subject: string,
  content: string, contentType = 'text/plain',
): Promise<SendEmailResult> {
  return postJson(`${API_BASE}/api/platform/email/send`, {
    to_email: toEmail, from_email: fromEmail, subject,
    content, content_type: contentType,
  })
}

export function validateEmail(email: string): Promise<EmailValidationResult> {
  return fetchJson(`${API_BASE}/api/platform/email/validate/${encodeURIComponent(email)}`)
}

// ─── Storage ────────────────────────────────────────────────────────────────

export function jsonBinCreate(data: unknown, name?: string): Promise<JsonBinCreateResult> {
  return postJson(`${API_BASE}/api/platform/storage/jsonbin/create`, { data, name })
}

export function jsonBinRead(binId: string): Promise<JsonBinReadResult> {
  return fetchJson(`${API_BASE}/api/platform/storage/jsonbin/${encodeURIComponent(binId)}`)
}

export function jsonBinUpdate(binId: string, data: unknown): Promise<JsonBinUpdateResult> {
  return putJson(`${API_BASE}/api/platform/storage/jsonbin/${encodeURIComponent(binId)}`, { data })
}

export function pantryGetBasket(basket: string): Promise<PantryBasket> {
  return fetchJson(`${API_BASE}/api/platform/storage/pantry/${encodeURIComponent(basket)}`)
}

export function pantryCreateItem(basket: string, key: string, data: unknown): Promise<{ status: string; key: string; provider: string }> {
  return postJson(`${API_BASE}/api/platform/storage/pantry/${encodeURIComponent(basket)}/${encodeURIComponent(key)}`, { data })
}

export function pastebinCreate(
  content: string, title?: string, syntax = 'text', expiration = '1M',
): Promise<PastebinResult> {
  return postJson(`${API_BASE}/api/platform/storage/pastebin/create`, { content, title, syntax, expiration })
}

// ─── Media ──────────────────────────────────────────────────────────────────

export function cloudinaryUpload(fileUrl: string, folder = ''): Promise<CloudinaryUploadResult> {
  return postJson(`${API_BASE}/api/platform/media/cloudinary/upload`, { file_url: fileUrl, folder })
}

export function cloudinaryListResources(resourceType = 'image', maxResults = 30): Promise<CloudinaryListResult> {
  return fetchJson(`${API_BASE}/api/platform/media/cloudinary/resources?resource_type=${resourceType}&max_results=${maxResults}`)
}

export function cloudConvertConvert(
  inputUrl: string, inputFormat: string, outputFormat: string,
): Promise<CloudConvertJobResult> {
  return postJson(`${API_BASE}/api/platform/media/cloudconvert/convert`, {
    input_url: inputUrl, input_format: inputFormat, output_format: outputFormat,
  })
}

export function cloudConvertGetJob(jobId: string): Promise<CloudConvertJobResult> {
  return fetchJson(`${API_BASE}/api/platform/media/cloudconvert/job/${encodeURIComponent(jobId)}`)
}

// ─── Business ───────────────────────────────────────────────────────────────

export function lobVerifyAddress(
  line1: string, city: string, state: string, zipCode: string, country = 'US',
): Promise<LobAddressResult> {
  return postJson(`${API_BASE}/api/platform/business/lob/verify-address`, {
    line1, city, state, zip_code: zipCode, country,
  })
}

export function vatValidate(vatNumber: string): Promise<VatValidationResult> {
  return fetchJson(`${API_BASE}/api/platform/business/vat/validate?vat_number=${encodeURIComponent(vatNumber)}`)
}

export function klarnaCreateSession(
  purchaseCountry: string, purchaseCurrency: string, locale: string,
  orderAmount: number, orderLines: Array<Record<string, unknown>>,
): Promise<KlarnaSessionResult> {
  return postJson(`${API_BASE}/api/platform/business/klarna/create-session`, {
    purchase_country: purchaseCountry, purchase_currency: purchaseCurrency,
    locale, order_amount: orderAmount, order_lines: orderLines,
  })
}

// ─── Developer ──────────────────────────────────────────────────────────────

export function githubListRepos(owner: string): Promise<GitHubRepoListResult> {
  return fetchJson(`${API_BASE}/api/platform/dev/github/repos/${encodeURIComponent(owner)}`)
}

export function githubRepoDetails(owner: string, repo: string): Promise<GitHubRepoDetail> {
  return fetchJson(`${API_BASE}/api/platform/dev/github/repo/${encodeURIComponent(owner)}/${encodeURIComponent(repo)}`)
}

export function githubRepoIssues(
  owner: string, repo: string, state = 'open', perPage = 20,
): Promise<GitHubIssueListResult> {
  return fetchJson(`${API_BASE}/api/platform/dev/github/repo/${encodeURIComponent(owner)}/${encodeURIComponent(repo)}/issues?state=${state}&per_page=${perPage}`)
}

export function httpbinGet(): Promise<Record<string, unknown>> {
  return fetchJson(`${API_BASE}/api/platform/dev/httpbin/get`)
}

export function httpbinPost(payload: unknown): Promise<Record<string, unknown>> {
  return postJson(`${API_BASE}/api/platform/dev/httpbin/post`, { payload })
}
