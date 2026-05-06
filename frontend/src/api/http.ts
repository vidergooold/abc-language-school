import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const http = axios.create({
  baseURL: (import.meta.env.VITE_API_URL || 'http://localhost:8000') + '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Read token from in-memory auth store instead of localStorage
http.interceptors.request.use((config) => {
  const authStore = useAuthStore()
  const token = authStore.token
  if (token) {
    config.headers = config.headers || {}
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// автоматически добавляем trailing slash, чтобы избежать 307 redirect с потерей токена
http.interceptors.request.use((config) => {
  if (config.url && !config.url.endsWith('/') && !config.url.includes('?')) {
    config.url = config.url + '/'
  }
  return config
})

export default http
