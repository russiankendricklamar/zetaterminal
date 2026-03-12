<template>
  <div v-if="updateInfo.available" class="updater-banner">
    <div class="updater-content">
      <span class="updater-text font-oswald">
        UPDATE {{ updateInfo.version }}
      </span>
      <span v-if="updateInfo.body" class="updater-notes font-mono">
        {{ updateInfo.body.slice(0, 120) }}
      </span>
    </div>
    <div class="updater-actions">
      <button
        v-if="!updateInfo.downloading"
        class="updater-btn font-oswald"
        @click="downloadAndInstall"
      >
        INSTALL →
      </button>
      <span v-else class="updater-progress font-mono">
        {{ updateInfo.progress }}%
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAutoUpdater } from '@/composables/useAutoUpdater'

const { updateInfo, downloadAndInstall } = useAutoUpdater()
</script>

<style scoped>
.updater-banner {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 16px;
  background: var(--bg-secondary);
  border-top: 1px solid var(--accent-red);
}

.updater-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.updater-text {
  color: var(--accent-red);
  font-size: 12px;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.updater-notes {
  color: var(--text-secondary);
  font-size: 11px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 400px;
}

.updater-btn {
  background: var(--accent-red);
  color: var(--text-primary);
  border: none;
  padding: 4px 12px;
  font-size: 11px;
  letter-spacing: 0.05em;
  cursor: pointer;
  border-radius: 3px;
  transition: background 0.15s;
}

.updater-btn:hover {
  background: var(--accent-red-hover);
}

.updater-progress {
  color: var(--accent-red);
  font-size: 12px;
}
</style>
