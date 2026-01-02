import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  // Всегда используем dark
  const theme = ref<'dark'>('dark')

  // Палитра "Glass Dark"
  const glassVars = {
    // Основные фоны
    '--color-bg-primary': '#050505', // Почти черный фон страницы
    '--color-bg-secondary': '#0a0a0a',
    '--color-bg-tertiary': '#141414',
    
    // Переменные для стекла (карточки, сайдбары)
    '--color-bg-glass': 'rgba(20, 20, 20, 0.65)', 
    '--color-bg-glass-light': 'rgba(255, 255, 255, 0.05)',
    
    // Акценты
    '--color-accent-primary': '#ffffff',
    '--color-accent-secondary': '#737373', // Neutral gray
    '--color-accent-success': '#22c55e', // Green 500
    '--color-accent-warning': '#f59e0b', // Amber 500
    '--color-accent-danger': '#ef4444', // Red 500
    
    // Текст
    '--color-text-primary': '#fafafa', // Almost white
    '--color-text-secondary': '#a3a3a3', // Neutral 400
    '--color-text-tertiary': '#525252', // Neutral 600
    
    // Границы
    '--color-border': 'rgba(255, 255, 255, 0.08)',
    '--color-border-hover': 'rgba(255, 255, 255, 0.15)',
    
    // Тени (мягкое свечение вместо жестких теней)
    '--shadow-sm': '0 0 0 1px rgba(255,255,255,0.05)',
    '--shadow-md': '0 4px 6px -1px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255,255,255,0.05)',
    '--shadow-lg': '0 20px 25px -5px rgba(0, 0, 0, 0.6), 0 0 0 1px rgba(255,255,255,0.05)',
  }

  const applyTheme = () => {
    const html = document.documentElement
    // Применяем переменные
    Object.entries(glassVars).forEach(([key, value]) => {
      html.style.setProperty(key, value)
    })
    // Ставим класс dark для Tailwind (если используется)
    html.classList.add('dark')
    html.style.colorScheme = 'dark'
  }

  const initTheme = () => {
    theme.value = 'dark'
    applyTheme()
  }

  // Заглушка, чтобы не ломать компоненты, которые вызывают toggle
  const toggleTheme = () => {
    initTheme() 
  }

  return { theme, initTheme, toggleTheme }
})

