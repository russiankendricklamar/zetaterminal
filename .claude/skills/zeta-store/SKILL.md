---
name: zeta-store
description: Create Pinia stores for zetaterminal with Composition API pattern, persistence, and type safety. Use when adding shared state management.
---

# Zeta Terminal — Pinia Store

## When to Use a Store

- State shared between **2+ pages** (not just parent-child)
- User preferences / settings
- Cached data that survives navigation
- Global UI state (sidebar, modals)

Do NOT use for page-local state — use `ref()` in the page.

## Template

`frontend/src/stores/{domain}.ts`:

```typescript
import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

interface {Domain}State {
  items: {Item}[]
  selectedId: string | null
}

export const use{Domain}Store = defineStore('{domain}', () => {
  // State
  const items = ref<{Item}[]>([])
  const selectedId = ref<string | null>(null)
  const loading = ref(false)

  // Getters (computed)
  const selectedItem = computed(() =>
    items.value.find(item => item.id === selectedId.value) ?? null
  )

  const count = computed(() => items.value.length)

  // Actions (functions) — IMMUTABLE patterns
  function setItems(newItems: {Item}[]) {
    items.value = [...newItems]  // New array, no mutation
  }

  function selectItem(id: string | null) {
    selectedId.value = id
  }

  function addItem(item: {Item}) {
    items.value = [...items.value, item]  // Immutable add
  }

  function updateItem(id: string, updates: Partial<{Item}>) {
    items.value = items.value.map(item =>
      item.id === id ? { ...item, ...updates } : item
    )
  }

  function removeItem(id: string) {
    items.value = items.value.filter(item => item.id !== id)
  }

  function reset() {
    items.value = []
    selectedId.value = null
    loading.value = false
  }

  return {
    // State
    items: computed(() => items.value),
    selectedId: computed(() => selectedId.value),
    loading: computed(() => loading.value),
    // Getters
    selectedItem,
    count,
    // Actions
    setItems,
    selectItem,
    addItem,
    updateItem,
    removeItem,
    reset,
  }
})
```

## Existing Stores (reference)

| Store | Purpose |
|-------|---------|
| `stores/theme.ts` | Dark theme (single theme, brutalist) |
| `stores/portfolio.ts` | Portfolio positions and metrics |
| `stores/riskMetrics.ts` | Risk calculations cache |
| `stores/swapRegistry.ts` | Swap instrument registry |
| `stores/forwardRegistry.ts` | Forward instrument registry |
| `stores/tasks.ts` | Background task tracking |

## localStorage Persistence

```typescript
// Save to localStorage on change
watch(items, (newItems) => {
  localStorage.setItem('{domain}_items', JSON.stringify(newItems))
}, { deep: true })

// Restore on init
function init() {
  const saved = localStorage.getItem('{domain}_items')
  if (saved) {
    try {
      items.value = JSON.parse(saved)
    } catch {
      localStorage.removeItem('{domain}_items')
    }
  }
}
```

## Rules

- [ ] Composition API (`defineStore` with setup function), NOT Options API
- [ ] **Immutable updates** — spread operator, map/filter, never `push`/`splice`
- [ ] Return state as `computed()` for readonly access
- [ ] TypeScript interface for state shape
- [ ] Store name matches filename: `use{Domain}Store` in `stores/{domain}.ts`
- [ ] `reset()` function for cleanup
- [ ] No API calls in stores — use composables for that, stores just hold state
