<!-- BrutalistCard.vue - Brutalist Card Component -->
<template>
  <div
    class="brutalist-card"
    :class="[
      `brutalist-card--${variant}`,
      { 'brutalist-card--hoverable': hoverable }
    ]"
  >
    <div v-if="title || $slots.header" class="card-header">
      <slot name="header">
        <h3 class="card-title font-oswald">{{ title }}</h3>
        <span v-if="badge" class="card-badge font-mono">{{ badge }}</span>
      </slot>
    </div>
    <div class="card-body">
      <slot></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  variant?: 'default' | 'accent' | 'dark'
  title?: string
  badge?: string
  hoverable?: boolean
}>(), {
  variant: 'default',
  hoverable: false
})
</script>

<style scoped>
.brutalist-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-dark);
  border-radius: var(--radius-sm);
  transition: border-color 0.2s ease, transform 0.2s ease;
}

.brutalist-card--hoverable:hover {
  border-color: var(--border-medium);
}

/* Variants */
.brutalist-card--accent {
  border-color: rgba(220, 38, 38, 0.2);
}

.brutalist-card--accent:hover {
  border-color: var(--accent-red);
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(220, 38, 38, 0.1);
}

.brutalist-card--dark {
  background: var(--bg-primary);
}

/* Header */
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-dark);
  background: var(--bg-primary);
}

.card-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0;
}

.card-badge {
  font-size: 10px;
  color: var(--accent-red);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  padding: 2px 8px;
  border: 1px solid var(--accent-red);
}

/* Body */
.card-body {
  padding: 20px;
}

/* Responsive */
@media (max-width: 768px) {
  .card-header {
    padding: 12px 16px;
  }

  .card-body {
    padding: 16px;
  }
}
</style>
