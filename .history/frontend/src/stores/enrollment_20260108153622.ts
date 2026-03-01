import { defineStore } from 'pinia'

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

      // имитация API-запроса
      await new Promise(resolve => setTimeout(resolve, 1000))

      this.loading = false
      this.success = true
    },
  },
})
