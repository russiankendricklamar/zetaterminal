<!-- StatCard.vue - Brutalist KPI/Metric Card -->
<template>
  <div class="stat-card" :class="[`stat-card--${variant}`, { 'stat-card--glow': glow }]">
    <div class="stat-header">
      <span class="stat-label font-mono">{{ label }}</span>
      <div v-if="trend !== undefined" class="stat-trend" :class="trendClass">
        <svg v-if="trend >= 0" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
          <path d="M18 15l-6-6-6 6"/>
        </svg>
        <svg v-else width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
          <path d="M6 9l6 6 6-6"/>
        </svg>
        <span class="font-mono">{{ formatTrend(trend) }}</span>
      </div>
    </div>
    <div class="stat-content">
      <div class="stat-value font-oswald" :class="valueClass">
        {{ formattedValue }}
        <small v-if="unit" class="stat-unit">{{ unit }}</small>
      </div>
      <div v-if="subtext" class="stat-subtext font-mono">{{ subtext }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  label: string
  value: number | string
  unit?: string
  trend?: number
  subtext?: string
  variant?: 'default' | 'positive' | 'negative' | 'warning'
  glow?: boolean
  format?: 'number' | 'currency' | 'percent'
}>(), {
  variant: 'default',
  glow: false,
  format: 'number'
})

const formattedValue = computed(() => {
  if (typeof props.value === 'string') return props.value

  switch (props.format) {
    case 'currency':
      return props.value.toLocaleString('ru-RU', { maximumFractionDigits: 0 })
    case 'percent':
      return `${(props.value * 100).toFixed(2)}%`
    default:
      return props.value.toLocaleString('ru-RU', { maximumFractionDigits: 2 })
  }
})

const trendClass = computed(() => ({
  'trend-positive': props.trend !== undefined && props.trend >= 0,
  'trend-negative': props.trend !== undefined && props.trend < 0
}))

const valueClass = computed(() => ({
  'value-positive': props.variant === 'positive',
  'value-negative': props.variant === 'negative',
  'value-warning': props.variant === 'warning'
}))

function formatTrend(value: number): string {
  const sign = value >= 0 ? '+' : ''
  return `${sign}${(value * 100).toFixed(1)}%`
}
</script>

<style scoped>
.stat-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-dark);
  border-radius: var(--radius-sm);
  padding: 20px;
  transition: border-color 0.2s ease;
}

.stat-card:hover {
  border-color: var(--border-medium);
}

/* Glow variants */
.stat-card--glow.stat-card--positive {
  border-color: rgba(34, 197, 94, 0.3);
  box-shadow: 0 0 20px rgba(34, 197, 94, 0.1);
}

.stat-card--glow.stat-card--negative {
  border-color: rgba(220, 38, 38, 0.3);
  box-shadow: 0 0 20px rgba(220, 38, 38, 0.1);
}

/* Header */
.stat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.stat-label {
  font-size: 10px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 2px;
}

.trend-positive {
  color: #22c55e;
  background: rgba(34, 197, 94, 0.1);
}

.trend-negative {
  color: var(--accent-red);
  background: rgba(220, 38, 38, 0.1);
}

/* Content */
.stat-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-value {
  font-size: 28px;
  font-weight: 400;
  color: var(--text-primary);
  line-height: 1;
  display: flex;
  align-items: baseline;
  gap: 6px;
}

.stat-unit {
  font-size: 14px;
  color: var(--text-tertiary);
  font-weight: 400;
}

.value-positive {
  color: #22c55e;
}

.value-negative {
  color: var(--accent-red);
}

.value-warning {
  color: #f59e0b;
}

.stat-subtext {
  font-size: 11px;
  color: var(--text-tertiary);
}

/* Responsive */
@media (max-width: 768px) {
  .stat-card {
    padding: 16px;
  }

  .stat-value {
    font-size: 24px;
  }
}
</style>
