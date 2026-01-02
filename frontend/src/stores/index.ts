import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const theme = ref<'light' | 'dark'>('dark')

  const applyTheme = (themeValue: 'light' | 'dark') => {
    const html = document.documentElement
    html.style.colorScheme = themeValue
    
    if (themeValue === 'light') {
      html.classList.add('light-theme')
      html.classList.remove('dark-theme')
    } else {
      html.classList.add('dark-theme')
      html.classList.remove('light-theme')
    }
  }

  const initTheme = () => {
    const saved = (localStorage.getItem('theme') || 'dark') as 'light' | 'dark'
    theme.value = saved
    applyTheme(saved)
  }

  const toggleTheme = () => {
    theme.value = theme.value === 'dark' ? 'light' : 'dark'
    localStorage.setItem('theme', theme.value)
    console.log('🎨 Theme changed to:', theme.value)
    applyTheme(theme.value)
  }

  return { theme, initTheme, toggleTheme }
})


