import { defineStore } from 'pinia'
import http from '@/api/http'

export const useEnrollmentStore = defineStore('enrollment', {
  state: () => ({
    loading: false,
    success: false,
    error: null as string | null,
  }),

  actions: {
    async submitEnrollment(payload: {
      name: string
      phone: string
      comment: string
    }) {
      this.loading = true
      this.error = null
      this.success = false

      try {
        await http.post('/enrollments', payload)
        this.success = true
      } catch (e) {
        this.error = 'Ошибка отправки заявки'
      } finally {
        this.loading = false
      }
    },
  },
})
