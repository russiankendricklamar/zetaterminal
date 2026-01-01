import { createApp } from 'vue'
import { createPinia } from 'pinia'
import PrimeVue from 'primevue/config'
import 'primevue/resources/themes/bootstrap4-dark-blue/theme.css'
import 'primeicons/primeicons.css'
import '@/assets/styles/main.css'

import App from '@/App.vue'

const app = createApp(App)
app.use(createPinia())
app.use(PrimeVue)
app.mount('#app')
