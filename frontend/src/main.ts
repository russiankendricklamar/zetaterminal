import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from '@/router'
import '@/assets/styles/main.css'
import App from '@/App.vue'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// Initialize theme
import { useThemeStore } from '@/stores/theme'
const themeStore = useThemeStore()
themeStore.initTheme()

// Enhanced smooth scrolling for better performance
if ('scrollBehavior' in document.documentElement.style) {
  // Native smooth scrolling is supported
  document.documentElement.style.scrollBehavior = 'smooth'
} else {
  // Polyfill for browsers that don't support smooth scrolling
  const smoothScrollPolyfill = () => {
    const elements = document.querySelectorAll('[data-smooth-scroll]')
    elements.forEach((el) => {
      el.addEventListener('click', (e) => {
        const target = (e.target as HTMLElement).getAttribute('href')
        if (target && target.startsWith('#')) {
          e.preventDefault()
          const targetElement = document.querySelector(target)
          if (targetElement) {
            targetElement.scrollIntoView({
              behavior: 'smooth',
              block: 'start'
            })
          }
        }
      })
    })
  }
  smoothScrollPolyfill()
}

app.mount('#app')


