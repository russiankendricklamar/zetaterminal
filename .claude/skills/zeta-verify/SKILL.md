---
name: zeta-verify
description: Run full verification suite for zetaterminal — linting, type checking, security audit, and code quality checks. Use before commits, after major changes, or when asked to verify/check the project.
---

# Zeta Terminal — Verification

Run all checks in sequence. Stop and fix CRITICAL issues before proceeding.

## Step 1: Python Linting (Ruff)

```bash
cd /Users/egorgalkin/zetaterminal/backend && ruff check src/
```

**Fix:** `ruff check --fix src/` for auto-fixable issues.

**CRITICAL if:** `F821` (undefined name), `S105` (hardcoded password), `S104` (bind all interfaces)

## Step 2: TypeScript/Vue Linting (ESLint)

```bash
cd /Users/egorgalkin/zetaterminal/frontend && npx eslint src/
```

**Fix:** `npx eslint --fix src/` for auto-fixable issues.

**CRITICAL if:** `no-debugger` errors, `vue/no-use-v-if-with-v-for`

## Step 3: TypeScript Type Check

```bash
cd /Users/egorgalkin/zetaterminal/frontend && npx vue-tsc --noEmit
```

**CRITICAL if:** any type errors — must be zero.

## Step 4: Python Import Check

```bash
cd /Users/egorgalkin/zetaterminal/backend && python -c "from src.main import app; print('OK')"
```

**CRITICAL if:** ImportError — backend won't start.

## Step 5: Security Scan

```bash
cd /Users/egorgalkin/zetaterminal/backend && ruff check src/ --select S
```

Check for:
- [ ] `S105` — hardcoded password strings → move to env vars
- [ ] `S104` — binding 0.0.0.0 → OK for Render, flag elsewhere
- [ ] `S314` — XML parsing → use `defusedxml` if processing untrusted XML
- [ ] `S112` — try-except-continue → ensure errors are logged

**Frontend:**
- [ ] No API keys in source code: `grep -r "sk-\|api_key\|password\|secret\|token" frontend/src/`
- [ ] No `v-html` with user input (XSS)
- [ ] All API calls use `getApiBaseUrl()`, no hardcoded URLs

## Step 6: Console.log Audit

```bash
grep -rn "console\.log" /Users/egorgalkin/zetaterminal/frontend/src/ --include="*.vue" --include="*.ts" | grep -v node_modules
```

Replace with `console.warn` or `console.error` if needed, or remove.

## Step 7: Design System Compliance (spot check)

```bash
# Hardcoded colors
grep -rn "#[0-9a-fA-F]\{6\}" /Users/egorgalkin/zetaterminal/frontend/src/ --include="*.vue" | grep -v "var(--" | grep -v "main.css" | head -20

# Forbidden patterns
grep -rn "rounded-full\|box-shadow\|linear-gradient\|glassmorphism" /Users/egorgalkin/zetaterminal/frontend/src/ --include="*.vue" | head -10
```

## Verification Report Format

After running all steps, report:

```
## Zeta Terminal Verification Report

| Check | Status | Issues |
|-------|--------|--------|
| Ruff (Python) | ✅/❌ | X errors |
| ESLint (Vue/TS) | ✅/❌ | X errors, Y warnings |
| TypeScript | ✅/❌ | X type errors |
| Python imports | ✅/❌ | — |
| Security | ✅/❌ | X findings |
| Console.log | ✅/❌ | X occurrences |
| Design system | ✅/❌ | X violations |

**CRITICAL:** [list or "none"]
**Recommendation:** [proceed / fix before commit]
```

## When to Run

- **Before every commit** — at minimum Steps 1-4
- **Before PR** — all 7 steps
- **After major refactoring** — all 7 steps
- **Quick check** — Steps 1-2 only
