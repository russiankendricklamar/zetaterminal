---
name: zeta-hotfix
description: Quick bug fix workflow for zetaterminal — diagnose, fix, test, verify in minimal steps. Use when something is broken and needs a fast fix.
---

# Zeta Terminal — Hotfix

Fast-track bug fix. No architecture changes, no refactoring. Fix the bug and nothing else.

## Step 1: Diagnose (2 min max)

**Backend error?**
```bash
# Check recent logs
cd /Users/egorgalkin/zetaterminal/backend
grep -rn "error\|Error\|exception\|Exception" src/ --include="*.py" -l | head -10
```

**Frontend error?**
```bash
# Build check
cd /Users/egorgalkin/zetaterminal/frontend
npx vue-tsc --noEmit 2>&1 | head -20
npx eslint src/ --quiet 2>&1 | head -20  # errors only, no warnings
```

**Reproduce:** describe the exact input → expected output → actual output.

## Step 2: Locate

Find the exact file and line:
- Backend: Router → Service → check in that order
- Frontend: Page → Composable → Service → Store

```bash
# Search for related code
grep -rn "keyword" /Users/egorgalkin/zetaterminal/backend/src/ --include="*.py"
grep -rn "keyword" /Users/egorgalkin/zetaterminal/frontend/src/ --include="*.vue" --include="*.ts"
```

## Step 3: Fix

**Rules:**
- Change the MINIMUM number of lines
- Don't refactor surrounding code
- Don't add features
- Don't change function signatures if avoidable
- If the fix is >20 lines, reconsider — it might not be a hotfix

## Step 4: Verify

```bash
# Backend
cd /Users/egorgalkin/zetaterminal/backend
ruff check src/{changed_file}.py
python -c "from src.main import app"

# Frontend
cd /Users/egorgalkin/zetaterminal/frontend
npx eslint src/{changed_file}.vue
npx vue-tsc --noEmit
```

## Step 5: Test the fix

- Manually test the exact scenario that was broken
- If a test file exists, run it: `python -m pytest tests/test_{module}.py -v`
- If no test exists, note it for `zeta-test-writer` later

## Common Hotfix Patterns

**NaN in calculation:**
```python
# Add guard
if not np.isfinite(result):
    raise ValueError(f"Calculation produced non-finite result: {result}")
```

**API 500 error:**
```python
# Usually missing error handling
except KeyError as e:
    raise HTTPException(status_code=400, detail=f"Missing field: {e}") from e
```

**Vue reactivity not updating:**
```typescript
// BAD: mutating
data.value.items.push(newItem)

// GOOD: replacing
data.value = { ...data.value, items: [...data.value.items, newItem] }
```

**CORS error:**
Check `CORS_ORIGINS` in backend `main.py` and Render env vars.

## DO NOT

- Add new dependencies
- Change database schema
- Refactor unrelated code
- Add new features "while we're at it"
- Skip verification step
