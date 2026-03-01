import { defineStore } from 'pinia'
import http from '@/api/http'

export interface MyEnrollment {
  id: number
  name: string
  phone: string
  comment?: string | null
}

export const useMyEnrollmentsStore = defineStore('myEnrollments', {
  state: () => ({
    enrollments: [] as MyEnrollment[],
    loading: false as boolean,
    error: null as string | null,
  }),

  actions: {
    async fetchMyEnrollments() {
      this.loading = true
      this.error = null
      try {
        const res = await http.get<MyEnrollment[]>('/enrollments/my')
        this.enrollments = res.data
      } catch (e) {
        this.error = 'Не удалось загрузить заявки'
      } finally {
        this.loading = false
      }
    },
  },
})
