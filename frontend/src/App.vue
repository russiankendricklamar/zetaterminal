<!-- src/App.vue -->
<template>
  <!-- Глобальная Command Palette (вызывается Cmd+K) - скрыта на странице терминала -->
  <CommandPalette v-if="!isTerminalPage" />

  <!-- Auto-updater banner (Tauri desktop only) -->
  <AppUpdater />

  <!-- Основной роутер -->
  <router-view />
</template>

<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useThemeStore } from '@/stores'
import CommandPalette from '@/components/common/CommandPalette.vue'
import AppUpdater from '@/components/common/AppUpdater.vue'
import { restoreSession } from '@/utils/sessionManager'
import { initPersistentStorage } from '@/utils/persistentStorage'

const route = useRoute()
const themeStore = useThemeStore()

// Скрываем глобальную Command Palette на странице терминала (там своя)
const isTerminalPage = computed(() => route.path === '/terminal')

onMounted(async () => {
  themeStore.initTheme()
  // Load tokens from Tauri Store into localStorage before session restore
  await initPersistentStorage()
  // Restore session using refresh token (also warms up Render backend)
  restoreSession()
})
</script>

<style>
/* Глобальный сброс */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html,
body,
#app {
  width: 100%;
  height: 100%;
  overflow-x: hidden;
  overflow-y: auto;
  padding: 0; 
  margin: 0;
  -webkit-overflow-scrolling: touch;
}

@media (max-width: 768px) {
  html,
  body,
  #app {
    overflow-y: auto;
    -webkit-overflow-scrolling: touch;
    height: auto;
    min-height: 100vh;
  }
}

body {
  font-family:
    -apple-system,
    BlinkMacSystemFont,
    'Segoe UI',
    'Roboto',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: var(--bg-primary);
  color: var(--text-primary);
}
</style>
