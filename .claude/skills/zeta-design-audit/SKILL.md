---
name: zeta-design-audit
description: Quick design system compliance check for zetaterminal Vue pages and components. Catches hardcoded colors, wrong fonts, excessive border-radius, and other brutalist violations.
---

# Zeta Terminal — Design Audit

Quick check that a page/component follows the brutalist design system.

## Step 1: Hardcoded Colors

Search the file for hex colors outside CSS variables:

```bash
# Find hardcoded colors (should be zero outside main.css)
grep -n "#[0-9a-fA-F]\{3,8\}" <file> | grep -v "var(--"
```

**Pass:** All colors use `var(--bg-primary)`, `var(--accent-red)`, etc.
**Exception:** Semantic data colors in JS objects (chart config) — `#22c55e`, `#DC2626` — are OK.

## Step 2: Typography

Check font usage:

- [ ] H1/page title: `.font-anton` + `uppercase` + `tracking-wider`
- [ ] UI labels, buttons: `.font-oswald` + `uppercase`
- [ ] Numbers, data, metadata: `.font-mono`
- [ ] No raw `font-family:` in scoped styles (use utility classes)

## Step 3: Forbidden Patterns

Search for violations:

```bash
# Border radius violations
grep -n "rounded-full\|rounded-xl\|rounded-2xl\|rounded-3xl\|border-radius.*[0-9]\{2,\}px" <file>

# Shadows and effects
grep -n "box-shadow\|drop-shadow\|backdrop-blur\|glassmorphism\|linear-gradient" <file>

# Emoji in template
grep -Pn "[\x{1F300}-\x{1F9FF}]" <file>
```

**Pass:** Zero matches (except in comments).

## Step 4: Layout Classes

Check that the page uses design system classes:

- [ ] Top wrapper: `.page-container` or `p-6 space-y-6`
- [ ] Section headers: `.section-header` + `.section-title`
- [ ] Cards: `.brutalist-card`, `.panel`, `.data-panel`, `.stat-card`
- [ ] Grids: `.grid-2`, `.grid-3`, `.grid-4`, `.dashboard-layout--*`
- [ ] Tables: `.brutalist-table`
- [ ] Buttons: `.btn .btn-primary`, `.btn .btn-outline`

**Red flag:** large `<style scoped>` blocks that duplicate main.css classes.

## Step 5: Component Patterns

- [ ] `<script setup lang="ts">` (not Options API)
- [ ] `getApiBaseUrl()` for API calls
- [ ] `getApiHeaders()` for auth headers
- [ ] Loading: `.animate-pulse` with UPPERCASE text
- [ ] Error: red border + `font-mono text-sm text-red-400`
- [ ] Empty: `.empty-state` with `.empty-text`

## Step 6: Responsive

- [ ] No fixed widths > 400px without media query fallback
- [ ] Grid collapses to 1 column on mobile
- [ ] Touch targets min 44x44px (`.touch-target`)
- [ ] `.mobile-hidden` for desktop-only elements

## Quick Report

```
## Design Check: [file]

| Check | Status |
|-------|--------|
| Colors | OK / X violations |
| Typography | OK / X violations |
| Forbidden patterns | OK / X violations |
| Layout classes | OK / custom styles |
| Components | OK / X issues |
| Responsive | OK / not checked |

**Verdict:** COMPLIANT / NEEDS FIXES
```

## Common Fixes

**Wrong:**
```html
<div style="background: #1a1a1a; border-radius: 12px;">
```

**Right:**
```html
<div class="brutalist-card">
```

**Wrong:**
```html
<h1 style="font-family: Oswald">Title</h1>
```

**Right:**
```html
<h1 class="font-anton text-3xl uppercase tracking-wider text-[var(--text-primary)]">TITLE</h1>
```

**Wrong:**
```html
<span class="text-gray-400">{{ price }}</span>
```

**Right:**
```html
<span class="font-mono text-[var(--text-primary)]">{{ price.toFixed(4) }}</span>
```
