---
name: zeta-vue-page
description: Create a new Vue 3 page or component following zetaterminal brutalist design system and Composition API patterns. Use when adding pages, UI components, or frontend features.
---

# Zeta Terminal — New Vue Page

## Brutalist Design System (HARD CONSTRAINTS)

**Colors — CSS variables ONLY, never hardcode hex:**
```css
var(--bg-primary)     /* #050505 */
var(--bg-secondary)   /* #0A0A0A */
var(--accent)         /* #DC2626 — sparingly */
var(--text-primary)   /* #F5F5F5 */
var(--text-muted)     /* #888888 */
var(--border)         /* #1A1A1A */
```

**Typography — utility classes ONLY:**
- `.font-anton` — Hero headings (ALL CAPS preferred)
- `.font-oswald` — UI labels, navigation, body
- `.font-mono` — Numbers, data values, code

**Forbidden:**
- `rounded-full` or border-radius > 6px
- Box shadows, gradients, glassmorphism
- Icon libraries — use `→` (`&rarr;`) for arrows
- Light mode
- Emoji in UI

## Page Template

```vue
<template>
  <div class="p-6 space-y-6">
    <!-- Header -->
    <div class="border-b border-[var(--border)] pb-4">
      <h1 class="font-anton text-3xl uppercase tracking-wider text-[var(--text-primary)]">
        PAGE TITLE
      </h1>
      <p class="font-oswald text-[var(--text-muted)] mt-1">
        Description text
      </p>
    </div>

    <!-- Content -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Input Panel -->
      <div class="bg-[var(--bg-secondary)] border border-[var(--border)] rounded p-4">
        <h2 class="font-oswald text-lg text-[var(--text-primary)] mb-4">PARAMETERS</h2>
        <!-- Form inputs here -->
      </div>

      <!-- Results Panel -->
      <div class="bg-[var(--bg-secondary)] border border-[var(--border)] rounded p-4">
        <h2 class="font-oswald text-lg text-[var(--text-primary)] mb-4">RESULTS</h2>
        <!-- Results display here -->
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { getApiBaseUrl } from '@/utils/apiBase'
import { getApiHeaders } from '@/utils/apiHeaders'

// State
const loading = ref(false)
const error = ref<string | null>(null)

// API call pattern
async function calculate() {
  loading.value = true
  error.value = null
  try {
    const response = await fetch(`${getApiBaseUrl()}/api/domain/endpoint`, {
      method: 'POST',
      headers: getApiHeaders(),
      body: JSON.stringify({ /* params */ }),
    })
    if (!response.ok) {
      const data = await response.json()
      throw new Error(data.detail || 'Request failed')
    }
    const result = await response.json()
    // Process result
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Unknown error'
    console.error('Calculation failed:', e)
  } finally {
    loading.value = false
  }
}
</script>
```

## UI Components

**Buttons:**
```html
<button class="btn btn-primary">CALCULATE →</button>
<button class="btn btn-outline">RESET</button>
```

**Input fields:**
```html
<label class="font-oswald text-sm text-[var(--text-muted)]">PARAMETER</label>
<input
  v-model.number="value"
  type="number"
  class="w-full bg-[var(--bg-primary)] border border-[var(--border)] rounded px-3 py-2 font-mono text-[var(--text-primary)] focus:border-[var(--accent)] outline-none"
/>
```

**Data display:**
```html
<span class="font-mono text-[var(--text-primary)]">{{ value.toFixed(4) }}</span>
```

**Loading state:**
```html
<div v-if="loading" class="font-oswald text-[var(--text-muted)] animate-pulse">
  CALCULATING...
</div>
```

**Error display:**
```html
<div v-if="error" class="border border-red-600 rounded p-3 text-red-400 font-mono text-sm">
  {{ error }}
</div>
```

## Route Registration

Add to `frontend/src/router/index.ts`:

```typescript
{
  path: '/new-page',
  name: 'NewPage',
  component: () => import('@/pages/NewPage.vue'),
  meta: { title: 'New Page', icon: '→' }
}
```

## Checklist Before Done

- [ ] `<script setup lang="ts">` — no Options API
- [ ] No hardcoded hex colors — CSS variables only
- [ ] No hardcoded URLs — `getApiBaseUrl()` + `getApiHeaders()`
- [ ] `.font-anton` for headings, `.font-oswald` for UI, `.font-mono` for data
- [ ] No `rounded-full`, no shadows, no gradients
- [ ] border-radius ≤ 6px (use `rounded` = 4px)
- [ ] Error handling with user-friendly message
- [ ] Loading state shown during API calls
- [ ] Route registered in router/index.ts
- [ ] `npx eslint` passes on new file

## Reference Files

- Page example: `frontend/src/pages/Portfolio.vue`, `frontend/src/pages/BondValuation.vue`
- Styles source of truth: `frontend/src/assets/styles/main.css`
- API utilities: `frontend/src/utils/apiBase.ts`, `frontend/src/utils/apiHeaders.ts`
- Router: `frontend/src/router/index.ts`
- Store example: `frontend/src/stores/theme.ts`
