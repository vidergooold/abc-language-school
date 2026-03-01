import { defineStore } from 'pinia'
import http from '@/api/http'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') as string | null,
  }),

  actions: {
    async login(email: string, password: string) {
      const res = await http.post('/auth/login', { email, password })
      this.token = res.data.access_token
      localStorage.setItem('token', this.token!)
    },
    logout() {
      this.token = null
      localStorage.removeItem('token')
    },
  },
})
