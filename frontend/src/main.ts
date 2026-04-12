import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { setupRouterGuards } from './router/guards'
import './styles/theme.css'

const app = createApp(App)
const pinia = createPinia()

// Pinia MUST be registered before router guards (guards use useAuthStore)
app.use(pinia)
app.use(router)

// Global navigation guards (run after pinia is ready)
setupRouterGuards(router)

app.mount('#app')
