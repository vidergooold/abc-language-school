import axios from 'axios'

const http = axios.create({
    baseURL: (import.meta.env.VITE_API_URL || 'https://abc-language-school-production.up.railway.app') + '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
})

// читаем токен напрямую из localStorage — надёжнее чем через Pinia при инициализации модуля
http.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
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
