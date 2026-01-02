<!-- src/App.vue -->
<template>
  <!-- Глобальная Command Palette (вызывается Cmd+K) -->
  <CommandPalette />

  <!-- Основной роутер -->
  <router-view />
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useThemeStore } from '@/stores'
import CommandPalette from '@/components/common/CommandPalette.vue' // <-- Новый импорт
import TaskContainer from '@/components/common/TaskContainer.vue'

const themeStore = useThemeStore()

onMounted(() => {
  themeStore.initTheme()
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
  overflow: hidden;
  padding: 0; 
  margin: 0;
}

body {
  font-family:
    'FKGroteskNeue',
    -apple-system,
    BlinkMacSystemFont,
    'Segoe UI',
    'Roboto',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: #000000;
  color: #ffffff;
}
</style>

