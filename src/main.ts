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

app.mount('#app')
