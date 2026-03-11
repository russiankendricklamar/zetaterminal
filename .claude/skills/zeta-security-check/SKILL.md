---
name: zeta-security-check
description: Quick security checklist for zetaterminal code changes. Run before commits, after adding endpoints, or when handling user input. Covers OWASP, financial threats, and project-specific patterns.
---

# Zeta Terminal — Security Check

Quick security review for individual files or features. For full audit, use `zeta-security` agent.

## Step 1: Secrets Scan

Search changed files for hardcoded credentials:
- API keys, passwords, tokens, secrets in string literals
- Base64-encoded credentials
- Private keys or certificates

**Pass:** All secrets come from `os.getenv()` or `secrets_service.get_key()`.

## Step 2: Input Validation (Backend)

For any new/modified Pydantic model:

- [ ] Inherits `FinancialBaseModel` (not plain `BaseModel`) for request models
- [ ] Every numeric field has `Field(gt=..., le=...)` bounds
- [ ] Every list field has `max_length`
- [ ] Every string field has `max_length` or `pattern`
- [ ] NaN/Inf automatically rejected by FinancialBaseModel

For any new endpoint:
- [ ] Rate limit on CPU-heavy operations (`@limiter.limit("10/minute")`)
- [ ] `asyncio.to_thread()` wraps CPU-bound calculations
- [ ] 3-tier error handling: ValueError->400, RuntimeError->400, Exception->500

## Step 3: Auth Check

For any new route:
- [ ] Included with `dependencies=[Depends(require_auth)]` in main.py
- [ ] Admin-only routes check `payload.role == "admin"`
- [ ] No sensitive data returned without auth

## Step 4: SQL Safety

For any database query:
- [ ] Uses SQLAlchemy ORM methods (select, insert, update, delete)
- [ ] Or parameterized `text()` with bind params
- [ ] NO f-string or %-format in SQL strings
- [ ] User input never interpolated into queries

## Step 5: External Requests (SSRF)

For any outbound HTTP call:
- [ ] Timeout set (default: 30s)
- [ ] URL validated if user-provided
- [ ] Response size checked for large payloads
- [ ] Uses `aiohttp.ClientSession` with `raise_for_status=True`

## Step 6: Frontend Security

For any new Vue page/component:
- [ ] No `v-html` with user input (XSS risk)
- [ ] Uses `getApiBaseUrl()` for API calls
- [ ] No sensitive data in console.log
- [ ] Auth token sent via `getApiHeaders()`, not manually constructed

## Step 7: Financial Math Safety

For any calculation code:
- [ ] `np.float64` precision (not float32)
- [ ] `np.clip()` before `np.exp()` for large exponents
- [ ] Division-by-zero guards
- [ ] Result validated: `np.isfinite(result)` before returning
- [ ] Iteration/path counts bounded by validation constants

## Quick Commands

```bash
# Backend: Ruff security rules only
cd /Users/egorgalkin/zetaterminal/backend && ruff check src/ --select S

# Frontend: search for hardcoded URLs
grep -rn "http://\|https://" frontend/src/ --include="*.ts" --include="*.vue" | grep -v getApiBaseUrl | grep -v node_modules

# Search for console.log (should be warn/error only)
grep -rn "console\.log" frontend/src/ --include="*.vue" --include="*.ts" | grep -v node_modules

# Check v-html usage
grep -rn "v-html" frontend/src/ --include="*.vue"
```

## Report

After checking all steps:

```
## Security Check: [file/feature]

| Step | Status | Notes |
|------|--------|-------|
| Secrets | OK/FAIL | ... |
| Input validation | OK/FAIL | ... |
| Auth | OK/FAIL | ... |
| SQL safety | OK/FAIL | ... |
| External requests | OK/FAIL | N/A if none |
| Frontend | OK/FAIL | N/A if backend-only |
| Financial math | OK/FAIL | N/A if no calculations |

**Verdict:** SAFE TO COMMIT / NEEDS FIXES
```

## When to Use

- **Before every commit** — Steps 1-4 minimum
- **New API endpoint** — All steps
- **New external data source** — Focus on Step 5
- **New Vue page** — Focus on Steps 1, 6
- **New financial model** — Focus on Steps 2, 7
