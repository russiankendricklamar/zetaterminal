---
name: zeta-composable
description: Create Vue 3 composables (use* hooks) for zetaterminal with TypeScript types, reactive state, and API integration. Use when extracting reusable logic from pages.
---

# Zeta Terminal — Vue 3 Composables

## When to Create a Composable

- Logic used by **2+ pages** → extract to composable
- Complex API interaction with loading/error states
- Chart/3D visualization lifecycle management
- WebSocket or polling connections

## Template

`frontend/src/composables/use{Feature}.ts`:

```typescript
import { ref, computed, onUnmounted } from 'vue'
import { getApiBaseUrl } from '@/utils/apiBase'
import { getApiHeaders } from '@/utils/apiHeaders'

interface {Feature}Params {
  param1: number
  param2: string
}

interface {Feature}Result {
  value: number
  metadata: Record<string, unknown>
}

export function use{Feature}() {
  // State
  const data = ref<{Feature}Result | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const hasData = computed(() => data.value !== null)

  // Methods
  async function calculate(params: {Feature}Params): Promise<void> {
    loading.value = true
    error.value = null

    try {
      const response = await fetch(`${getApiBaseUrl()}/api/{feature}/calculate`, {
        method: 'POST',
        headers: getApiHeaders(),
        body: JSON.stringify(params),
      })

      if (!response.ok) {
        const err = await response.json().catch(() => ({ detail: 'Request failed' }))
        throw new Error(err.detail || `HTTP ${response.status}`)
      }

      data.value = await response.json()
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Unknown error'
      console.error('{Feature} calculation failed:', e)
    } finally {
      loading.value = false
    }
  }

  function reset(): void {
    data.value = null
    error.value = null
    loading.value = false
  }

  // Cleanup (if needed for timers, subscriptions)
  onUnmounted(() => {
    // Cancel pending requests, clear timers
  })

  return {
    // State (readonly where possible)
    data: computed(() => data.value),
    loading: computed(() => loading.value),
    error: computed(() => error.value),
    hasData,
    // Methods
    calculate,
    reset,
  }
}
```

## Usage in Page

```vue
<script setup lang="ts">
import { use{Feature} } from '@/composables/use{Feature}'

const { data, loading, error, calculate } = use{Feature}()
</script>
```

## Existing Composables (reference)

| File | Purpose |
|------|---------|
| `useHMMModel.ts` | HMM Forward-Backward, Viterbi |
| `useRegimeSpace3D.ts` | Three.js 3D renderer lifecycle |
| `useSecurityTools.ts` | Security utilities |
| `usePdfExport.ts` | PDF generation via html2pdf.js |

## Patterns

**Debounced input:**
```typescript
import { ref, watch } from 'vue'

export function useDebounce<T>(value: Ref<T>, delay = 300) {
  const debounced = ref(value.value) as Ref<T>
  let timeout: ReturnType<typeof setTimeout>

  watch(value, (newVal) => {
    clearTimeout(timeout)
    timeout = setTimeout(() => { debounced.value = newVal }, delay)
  })

  return debounced
}
```

**AbortController for cancellable requests:**
```typescript
let controller: AbortController | null = null

async function fetchData() {
  controller?.abort()
  controller = new AbortController()

  const response = await fetch(url, { signal: controller.signal })
  // ...
}

onUnmounted(() => controller?.abort())
```

## Checklist

- [ ] TypeScript interfaces for params and results
- [ ] `ref()` for primitives, return as `computed()` for readonly
- [ ] Loading + error + data state trio
- [ ] Error handling with user-friendly messages
- [ ] `onUnmounted` cleanup for timers/subscriptions/AbortController
- [ ] `getApiBaseUrl()` for API calls
- [ ] Exported function named `use{Feature}` (camelCase)
