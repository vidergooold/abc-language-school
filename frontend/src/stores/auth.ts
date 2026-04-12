import { defineStore } from 'pinia'
import http from '@/api/http'

interface AuthUser {
  id: number
  email: string
  full_name: string | null
  role: 'admin' | 'teacher' | 'student'
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') as string | null,
    user: JSON.parse(localStorage.getItem('user') || 'null') as AuthUser | null,
  }),

  getters: {
    isLoggedIn:  (state) => !!state.token,
    isAdmin:     (state) => state.user?.role === 'admin',
    isTeacher:   (state) => state.user?.role === 'teacher',
    isStudent:   (state) => state.user?.role === 'student',
    isStaff:     (state) => state.user?.role === 'admin' || state.user?.role === 'teacher',
  },

  actions: {
    async login(email: string, password: string) {
      const res = await http.post('/auth/login', { email, password })
      this.token = res.data.access_token
      this.user = res.data.user as AuthUser
      localStorage.setItem('token', this.token!)
      localStorage.setItem('user', JSON.stringify(this.user))
    },
    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    },
  },
})
