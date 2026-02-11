<!-- PageHeader.vue - Brutalist Page Header Component -->
<template>
  <div class="page-header">
    <div class="header-content">
      <div class="header-left">
        <h1 class="header-title font-anton">{{ title }}</h1>
        <p v-if="subtitle" class="header-subtitle font-mono">{{ subtitle }}</p>
      </div>
      <div class="header-actions" v-if="$slots.actions">
        <slot name="actions"></slot>
      </div>
    </div>
    <div class="header-divider"></div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  subtitle?: string
}>()
</script>

<style scoped>
.page-header {
  margin-bottom: 32px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 24px;
  padding-bottom: 16px;
}

.header-left {
  flex: 1;
  min-width: 0;
}

.header-title {
  font-size: clamp(1.5rem, 4vw, 2.5rem);
  color: var(--text-primary);
  text-transform: uppercase;
  letter-spacing: -0.02em;
  line-height: 1;
  margin: 0;
}

.header-subtitle {
  font-size: 12px;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin: 8px 0 0 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.header-divider {
  height: 1px;
  background: var(--border-dark);
  width: 100%;
}

/* Responsive */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .header-actions {
    width: 100%;
    justify-content: flex-start;
    flex-wrap: wrap;
  }
}
</style>
